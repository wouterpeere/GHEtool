import matplotlib.pyplot as plt
from matplotlib.pyplot import ylabel

from GHEtool import *
from GHEtool.VariableClasses.LoadData import _LoadDataBuilding
from scipy.signal import convolve

import numpy as np
import time

from GHEtool.test.general_tests.test_GHEtool import borefield_custom_data


def calculate_regeneration(borefield: Borefield, regen_obj: Regeneration,
                           algorithm: str = 'yearly',
                           position_regeneration: str = "inlet",
                           rules=(1, 2, 3)) -> tuple[HourlyBuildingLoadMultiYear, np.ndarray]:
    """
    This function calculates the possible regeneration for a certain borefield a regeneration object.
    The updated hourly load profile as well as the regeneration array are returned.
    The methodology is described in Peere W. (2027) [#Peere]_)

    Parameters
    ----------
    borefield : Borefield
        GHEtool borefield object
    regen_obj : Regeneration
        GHEtool regeneration object
    algorithm : str
        'yearly' if the imbalance should be compensated for each year individually, leading to a balanced field every year.
        'total' if the total imbalance over the simulation period is relevant. This can cause an initial increase in imbalance.
        'proceeding' only consider the imbalance that has already taken place, without overcompensation.
        'proceeding_extra' only consider the imbalance that has already taken place, with overcompensation active.
    position_regeneration : str
        'inlet' if the regeneration happens before the borefield inlet, 'outlet' if it happens at the borefield outlet.
    rules : tuple

    Returns
    -------
    tuple : HourlyBuildingLoadMultiYear, np.ndarray
        The multi-year hourly building load with the regeneration and the regeneration load [kW]

    References
    ----------
    .. [#Peere] Peere, W. (2027) Validated combined first and last year borefield sizing methodology. In Proceedings of GeoTHERM 2027. Offenburg (Germany), 25-26 February 2027. [abstract submitted]
    """
    borefield = copy.deepcopy(borefield)

    simulation_horizon: int = 8760

    if borefield.borehole.use_constant_Rb:
        raise ValueError('This function does not work with a constant borehole resistance')

    # get imbalance
    variable_efficiency = isinstance(borefield.load, _LoadDataBuilding) and not (
            isinstance(borefield.load.cop, SCOP) and isinstance(borefield.load.cop_dhw, SCOP) and isinstance(
        borefield.load.eer, SEER))
    if not variable_efficiency:
        # for constant efficiency, this is known a priori
        injection_dominated = borefield.load.imbalance > 0
        extraction_dominated = not injection_dominated
    else:
        # variable efficiency so this has to be simulated first
        borefield._calculate_temperature_profile(hourly=True)
        injection_dominated = borefield.load.imbalance > 0
        extraction_dominated = not injection_dominated

    # calculate the maximum power based on the maximum temperature difference that can be achieved
    if isinstance(borefield.borehole.flow_data, ConstantDeltaTFlowRate):
        max_delta = borefield.Tf_max - borefield.Tf_min
        q_0 = 0
        q_1 = 30
        while np.abs(q_1 - q_0) > 0.1:
            power = q_1 * borefield.number_of_boreholes * borefield.H * (-1) * extraction_dominated / 1000
            resistance = borefield.borehole.get_Rb(
                borefield.H, borefield.D, borefield.r_b, borefield.ground_data.k_s(borefield.depth, borefield.D),
                borefield.depth,
                temperature=borefield.Tf_min if injection_dominated else borefield.Tf_max, use_explicit_models=True,
                nb_of_boreholes=borefield.number_of_boreholes, power=power
            )
            q_0 = q_1
            q_1 = max_delta / resistance

        # convert to array
        max_power = q_1 * borefield.number_of_boreholes * borefield.H / 1000  # convert to KW
    else:
        raise ValueError('Only constant flow rates or constant Delta T flow rates can be used.')

    # calculate the maximum and minimum flow rate
    max_flow = max(
        borefield.flow_data.mfr_borehole(power=max_power, fluid_data=borefield.fluid_data,
                                         nb_of_boreholes=borefield.number_of_boreholes, temperature=25),
        borefield.flow_data.mfr_borehole(power=(-1) * max_power, fluid_data=borefield.fluid_data,
                                         nb_of_boreholes=borefield.number_of_boreholes, temperature=25))
    min_flow = max_flow * (
        borefield.flow_data._min_flow_percentage / 100 if isinstance(borefield.flow_data,
                                                                     ConstantDeltaTFlowRate) else 1)

    # set the interpolation function for the borehole resistance
    borefield.borehole.set_interpolator(
        borefield.H, borefield.D, borefield.r_b, borefield.ground_data.k_s(borefield.depth, borefield.D),
        borefield.depth, nb_of_boreholes=borefield.number_of_boreholes)

    def get_Rb(borefield, power, temp) -> np.ndarray:
        return borefield.borehole.get_Rb(borefield.H, borefield.D, borefield.r_b,
                                         borefield.ground_data.k_s(borefield.depth, borefield.D),
                                         borefield.depth, temperature=temp, power=power / 1000,
                                         use_explicit_models=True,
                                         nb_of_boreholes=borefield.number_of_boreholes)

    # START OF THE ACTUAL SIMULATION
    regeneration_array = np.zeros_like(borefield.load.hourly_net_resulting_injection_power)

    # set the g-values
    g_values = borefield.gfunction(borefield.load.time_L4, borefield.H)
    g_value_differences = np.diff(g_values, prepend=0)
    g_value_differences_horizon = g_value_differences[:simulation_horizon]

    recalculate = True

    hourly_load = borefield.load.hourly_net_resulting_injection_power

    # correction factor to convert the g-function values to the ground temperature
    corr = 2 * np.pi * borefield.ground_data.k_s(borefield.calculate_depth(borefield.H, borefield.D), borefield.D) * (
            borefield.H * borefield.number_of_boreholes)

    year = 0
    offset = np.zeros_like(8760)
    Tb = np.zeros(8760)

    if algorithm == 'yearly':
        # every year the imbalance should be compensated
        remaining_imbalance = np.sum(hourly_load[0:8670]) * 1000
    elif algorithm == 'total':
        # imbalance may be compensated sooner
        remaining_imbalance = np.sum(hourly_load) * 1000
    else:
        # only the imbalance that has already been should be accounted for
        remaining_imbalance = 0

    building_imbalance = remaining_imbalance

    for i in range(8760 * borefield.load.simulation_period):

        # start a new year
        if i % 8760 == 0 and i > 0:
            year += 1

        # change offset
        if year > 0 and i % 8760 == 0:
            load_prev = hourly_load[0:8670 * year] + regeneration_array[0:8670 * year] / 1000
            all_years = convolve(load_prev * 1000, g_value_differences)[:8760 * borefield.load.simulation_period]
            offset = all_years[year * 8760:(year + 1) * 8760]
            recalculate = True
            print(year)

        if recalculate:
            # calculate borehole wall temperature
            Tf_avg = np.full(simulation_horizon, borefield.Tf_min if injection_dominated else borefield.Tf_max)
            load = (hourly_load[year * 8760:(year + 1) * 8760] * 1000 +
                    regeneration_array[year * 8760:(year + 1) * 8760])
            Tb = ((convolve(load, g_value_differences_horizon)[:8760] + offset) / corr + borefield._Tg(borefield.H))

            # iterate to converge for the fluid temperature
            for _ in range(2):  # 3 more than enough to converge
                Tf_avg = Tb + load * (get_Rb(borefield, load, Tf_avg) / borefield.number_of_boreholes / borefield.H)
                if position_regeneration == 'inlet':
                    Tf_to_regeneration = borefield.calculate_borefield_inlet_outlet_temperature(load, Tf_avg, Tb)[0]
                else:
                    Tf_to_regeneration = borefield.calculate_borefield_inlet_outlet_temperature(load, Tf_avg, Tb)[1]

                # with variable efficiency, the ground load should be updated as well
                if variable_efficiency:
                    Tb = convolve(
                        hourly_load[i:min(8760 * borefield.load.simulation_period, i + simulation_horizon)] * 1000,
                        g_value_differences_horizon)[:8760] / corr + borefield._Tg(borefield.H)
                    borefield.load.set_results(ResultsHourly(np.tile(Tb, borefield.load.simulation_period),
                                                             np.tile(Tf_avg, borefield.load.simulation_period)))
                    hourly_load = borefield.load.hourly_net_resulting_injection_power

            # update imbalance when there is a variable efficiency
            if algorithm in ('yearly', 'total') and variable_efficiency:
                remaining_imbalance -= building_imbalance
                if algorithm == 'yearly':
                    # every year the imbalance should be compensated
                    building_imbalance = np.sum(hourly_load[year * 8760:(year + 1) * 8760]) * 1000
                else:
                    # imbalance may be compensated sooner
                    building_imbalance = np.sum(hourly_load) * 1000
                remaining_imbalance += building_imbalance

            # update imbalance
            if algorithm == 'yearly' and i % 8760 == 0:
                remaining_imbalance = np.sum(hourly_load[year * 8760:(year + 1) * 8760]) * 1000
                building_imbalance = remaining_imbalance

            recalculate = False

        # calculate the imbalance from the previous hours until now
        if algorithm in ('proceeding', 'proceeding_extra'):
            remaining_imbalance += hourly_load[i % 8760] * 1000  # Wh

        # calculate possible regeneration power (W)
        possible_regen_power = regen_obj.get_regeneration_power_inlet(
            i, Tf_to_regeneration[i % 8760],
            min(min_flow, borefield.flow_data.mfr_borefield(
                nb_of_boreholes=borefield.number_of_boreholes,
                power=load[i % 8760],
                temperature=Tf_to_regeneration[i % 8760],
                fluid_data=borefield.fluid_data)),
            borefield.fluid_data.cp(
                temperature=Tf_to_regeneration[i % 8760]))
        if (extraction_dominated and algorithm != 'proceeding_extra' or algorithm == 'proceeding_extra') \
                and possible_regen_power > 0 and (remaining_imbalance < 0 or 1 not in rules):
            # calculate new load based on regeneration
            new_load = load[i % 8760] + possible_regen_power  # W
            Tf_avg_new = Tb[i % 8760] + new_load * (
                    get_Rb(borefield, new_load, Tf_avg[i % 8760])[0] / borefield.number_of_boreholes / borefield.H)

            # calculate fluid temperature for regeneration based on if it is placed at the borefield inlet or outlet
            if position_regeneration == 'inlet':
                Tf_to_regeneration_temp = \
                    borefield.calculate_borefield_inlet_outlet_temperature(new_load, Tf_avg_new, Tb[i % 8760])[0]
            else:
                Tf_to_regeneration_temp = \
                    borefield.calculate_borefield_inlet_outlet_temperature(new_load, Tf_avg_new, Tb[i % 8760])[1]

            # update possible regeneration power
            max_reg = regen_obj.get_regeneration_power_inlet(
                i, Tf_to_regeneration_temp,
                min(min_flow, borefield.flow_data.mfr_borefield(
                    nb_of_boreholes=borefield.number_of_boreholes,
                    power=new_load, temperature=Tf_avg_new,
                    fluid_data=borefield.fluid_data)),
                borefield.fluid_data.cp(temperature=Tf_avg_new))

            ## RULES TO LIMIT THE REGENERATION
            # 1. Do not allow more regeneration than the imbalance
            if 1 in rules:
                max_reg = max(0, min((-1) * remaining_imbalance, max_reg))

            # 2. Make sure current limit is not crossed
            if 2 in rules:
                resistance = get_Rb(borefield, new_load, borefield.Tf_max)[0]
                max_delta = borefield.Tf_max - Tf_avg[i % 8760]
                max_power = max_delta / resistance * borefield.number_of_boreholes * borefield.H
                # if max_power < max_reg:
                #     print('2', i % 8760, max_power, max_reg, remaining_imbalance)
                max_reg = min(max_power, max_reg)

            # 3. Make sure future limits are not crossed
            if 3 in rules and i % 8760 > 0:
                diff_array = borefield.Tf_max - Tf_avg[i % 8760:]
                impact_array = diff_array / g_value_differences_horizon[:-i % 8760] * corr
                # if min(impact_array) < max_reg:
                #     print('3', i % 8760, min(impact_array), max_reg, remaining_imbalance)
                max_reg = min(min(impact_array), max_reg)

            # set regeneration
            remaining_imbalance += max_reg
            regeneration_array[i] = max_reg

            # When there was regeneration, the borehole wall temperature should be recalculated
            if max_reg != 0:
                recalculate = True
        # print(f'{i % 8760}: {remaining_imbalance / 1000.:0f}, {np.sum(regeneration_array) / 1000.:0f}')
        if (injection_dominated and algorithm != 'proceeding_extra' or algorithm == 'proceeding_extra') \
                and possible_regen_power < 0 and (remaining_imbalance > 0 or 1 not in rules):
            # calculate new load based on regeneration
            new_load = load[i % 8760] + possible_regen_power  # W
            Tf_avg_new = Tb[i % 8760] + new_load * (
                    get_Rb(borefield, new_load, Tf_avg[i % 8760])[0] / borefield.number_of_boreholes / borefield.H)

            # calculate fluid temperature for regeneration based on if it is placed at the borefield inlet or outlet
            if position_regeneration == 'inlet':
                Tf_to_regeneration_temp = \
                    borefield.calculate_borefield_inlet_outlet_temperature(new_load, Tf_avg_new, Tb[i % 8760])[0]
            else:
                Tf_to_regeneration_temp = \
                    borefield.calculate_borefield_inlet_outlet_temperature(new_load, Tf_avg_new, Tb[i % 8760])[1]

            # update possible regeneration power
            max_reg = regen_obj.get_regeneration_power_inlet(
                i, Tf_to_regeneration_temp,
                min(min_flow, borefield.flow_data.mfr_borefield(
                    nb_of_boreholes=borefield.number_of_boreholes,
                    power=new_load, temperature=Tf_avg_new,
                    fluid_data=borefield.fluid_data)),
                borefield.fluid_data.cp(temperature=Tf_avg_new))

            max_reg = (-1) * max_reg
            ## RULES TO LIMIT THE REGENERATION
            # 1. Do not allow more regeneration than the imbalance
            if 1 in rules:
                max_reg = max(0, min(remaining_imbalance, max_reg), )

            # 2. Make sure current limit is not crossed
            if 2 in rules:
                resistance = get_Rb(borefield, new_load, borefield.Tf_min)[0]
                max_delta = Tf_avg[i % 8760] - borefield.Tf_min
                max_power = max_delta / resistance * borefield.number_of_boreholes * borefield.H
                max_reg = min(max_power, max_reg)

            # 3. Make sure future limits are not crossed
            if 3 in rules:
                diff_array = Tf_avg[i % 8760:] - borefield.Tf_min
                impact_array = diff_array / g_value_differences_horizon[:-i % 8760] * corr
                max_reg = min(min(impact_array), max_reg)

            # reset sign
            max_reg = (-1) * max_reg
            # set regeneration
            remaining_imbalance += max_reg
            regeneration_array[i] = max_reg

            # When there was regeneration, the borehole wall temperature should be recalculated
            if max_reg != 0:
                recalculate = True

    multiyear_load = HourlyBuildingLoadMultiYear(
        borefield.load.hourly_heating_load_simulation_period,
        borefield.load.hourly_cooling_load_simulation_period,
        borefield.load.cop,
        borefield.load.eer,
        borefield.load.hourly_dhw_load_simulation_period,
        borefield.load.cop_dhw
    )
    multiyear_load.hourly_regeneration_load_simulation_period = regeneration_array / 1000

    return multiyear_load, regeneration_array / 1000


if __name__ == "__main__":
    ground_data = GroundFluxTemperature(2, 10)
    fluid_data = TemperatureDependentFluidData('MPG', 0, mass_percentage=False)
    flow_data = ConstantDeltaTFlowRate(delta_temp_extraction=3, delta_temp_injection=3)
    pipe_data = DoubleUTube(1, 0.013, 0.016, 0.4, 0.035)
    borefield = Borefield()
    borefield.create_rectangular_borefield(4, 3, 6, 6, 105, 0.7, 0.07)
    borefield.ground_data = ground_data
    borefield.fluid_data = fluid_data
    borefield.flow_data = flow_data
    borefield.pipe_data = pipe_data
    borefield.calculation_setup(use_constant_Rb=False)
    borefield.set_max_fluid_temperature(30)
    borefield.set_min_fluid_temperature(5.5)
    hourly_load_building = HourlyBuildingLoad(efficiency_cooling=7, efficiency_heating=6)
    hourly_load_building.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\\auditorium.csv"), header=True,
                                             separator=";", col_cooling=0, col_heating=1)
    borefield.load = hourly_load_building
    borefield.load.simulation_period = 5
    # borefield.print_temperature_profile(plot_hourly=True)
    # get weather data
    weather_file = open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb')
    weather_file.seek(0)
    TMY: pd.DataFrame = pd.read_csv(weather_file, sep=",", header=None, skiprows=8)

    TMY.drop(columns=TMY.columns[:5], inplace=True)
    solar: np.ndarray = np.tile(np.array(TMY.iloc[:, 8]), 20)
    temperature: np.ndarray = np.tile(np.array(TMY.iloc[:, 1]), 20)

    # initiate regeneration object
    a0 = 0.45
    a1 = 24.76  # W/K/m²

    surface = 200  # m²

    regeneration_object = Regeneration(power=solar * a0 * surface * 2, temperature=temperature, a1=a1 * surface)

    # three_rules, regeneration_inlet = calculate_regeneration(
    #     borefield=copy.deepcopy(borefield),
    #     regen_obj=regeneration_object,
    #     rules=(1, 2, 3))
    # three_rules, regeneration_outlet = calculate_regeneration(
    #     borefield=copy.deepcopy(borefield),
    #     regen_obj=regeneration_object,
    #     rules=(1, 2, 3),
    #     position_regeneration="outlet")
    #
    # plt.figure()
    # plt.plot(regeneration_outlet, label='At borefield outlet')
    # plt.plot(regeneration_inlet, label='At borefield inlet')
    # plt.xlabel('Time [hours]')
    # plt.ylabel('Regeneration power [kW]')
    # plt.title('Different positions for regeneration technology')
    # plt.legend()
    # plt.show()

    yearly_my, yearly = calculate_regeneration(
        borefield=copy.deepcopy(borefield),
        regen_obj=regeneration_object,
        rules=(1, 2, 3),
        algorithm='yearly')
    total_my, total = calculate_regeneration(
        borefield=copy.deepcopy(borefield),
        regen_obj=regeneration_object,
        rules=(1, 2, 3),
        algorithm='total')
    proceeding_my, proceeding = calculate_regeneration(
        borefield=copy.deepcopy(borefield),
        regen_obj=regeneration_object,
        rules=(1, 2, 3),
        algorithm='proceeding')
    proceeding_extra_my, proceeding_extra = calculate_regeneration(
        borefield=copy.deepcopy(borefield),
        regen_obj=regeneration_object,
        rules=(1, 2, 3),
        algorithm='proceeding_extra')
    plt.figure()
    plt.plot(total, label='Total')
    plt.plot(yearly, label='Yearly')
    plt.plot(proceeding, label='Proceeding')
    plt.plot(proceeding_extra, label='Proceeding extra')

    plt.xlabel('Time [hours]')
    plt.ylabel('Regeneration power [kW]')
    plt.title('Different regeneration strategies')
    plt.legend()
    plt.show()
    #
    # borefield.load = proceeding_extra_my
    # borefield.print_temperature_profile(plot_hourly=True)

    data = {
        'Yearly': yearly_my,
        'Total': total_my,
        'Proceeding w/o': proceeding_my,
        'Proceeding': proceeding_extra_my
    }

    fig, axes = plt.subplots(
        nrows=len(data),
        ncols=1,
        figsize=(9, 10),
        sharex=True,
    )

    for ax, (key, value) in zip(axes, data.items()):
        borefield.load = value
        borefield.calculate_temperatures(hourly=True)
        tf = borefield.results.Tf
        time_array = borefield.load.time_L4 / 12 / 3600 / 730

        ax.plot(time_array, tf, linewidth=0.7)
        ax.set_title(key)
        ax.set_ylabel('Fluid temperature [°C]')

        ax.axhline(
            borefield.Tf_min,
            color='black',
            linestyle='dashed',
            linewidth=0.7,
        )
        ax.axhline(
            borefield.Tf_max,
            color='black',
            linestyle='dashed',
            linewidth=0.7,
        )

        ax.set_xlim(0, borefield.simulation_period)

    axes[-1].set_xlabel('Time [year]')
    axes[-1].set_xticks(range(0, borefield.simulation_period + 1, 2))

    fig.tight_layout()
    plt.show()
