import matplotlib.pyplot as plt
from matplotlib.pyplot import ylabel

from GHEtool import *
from GHEtool.VariableClasses.LoadData import _LoadDataBuilding
from scipy.signal import convolve

import numpy as np
import time

from GHEtool.test.general_tests.test_GHEtool import borefield_custom_data


def calculate_temperature_profile_with_regeneration(borefield: Borefield, regen_obj: Regeneration,
                                                    balanced_per_year: bool = True,
                                                    simulation_horizon: int = 8760,
                                                    rules=(1, 2, 3)) -> HourlyBuildingLoadMultiYear:
    if borefield.borehole.use_constant_Rb:
        raise ValueError()

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

    if balanced_per_year:
        # every year the imbalance should be compensated
        remaining_imbalance = borefield.load.imbalance * 1000
    else:
        # imbalance may be compensated sooner
        remaining_imbalance = borefield.load.imbalance * borefield.simulation_period * 1000

    # convert fluid properties
    _fluid_data_original = copy.deepcopy(borefield.borehole.fluid_data)

    if isinstance(borefield.borehole.fluid_data, TemperatureDependentFluidData):
        # if injection dominated, regeneration will cool down, so Tf_min is the most relevant
        _fluid_data_constant = borefield.borehole.fluid_data.create_constant(
            borefield.Tf_min if injection_dominated else borefield.Tf_max
        )
    else:
        _fluid_data_constant = _fluid_data_original

    _constant_resistance = None
    _resistances_value_range = None
    _resistances_input_range = None
    if isinstance(borefield.borehole.flow_data, ConstantFlowRate):
        _constant_resistance = borefield.borehole.get_Rb(
            borefield.H, borefield.D, borefield.r_b, borefield.ground_data.k_s(borefield.depth, borefield.D),
            borefield.depth,
            temperature=borefield.Tf_min if injection_dominated else borefield.Tf_max, use_explicit_models=True,
            nb_of_boreholes=borefield.number_of_boreholes
        )
    elif isinstance(borefield.borehole.flow_data, ConstantDeltaTFlowRate):
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
        _resistances_input_range = np.linspace(0, max_power, 1000)
        _resistances_value_range = borefield.borehole.get_Rb(
            borefield.H, borefield.D, borefield.r_b, borefield.ground_data.k_s(borefield.depth, borefield.D),
            borefield.depth,
            temperature=borefield.Tf_min if injection_dominated else borefield.Tf_max, use_explicit_models=True,
            nb_of_boreholes=borefield.number_of_boreholes, power=_resistances_input_range * (-1) * extraction_dominated
        )
    else:
        raise ValueError('Only constant flow rates or constant Delta T flow rates can be used.')

    from resistance import build_Rb_interpolator

    max_flow = max(
        borefield.flow_data.mfr_borehole(power=np.max(_resistances_input_range), fluid_data=borefield.fluid_data,
                                         nb_of_boreholes=borefield.number_of_boreholes, temperature=25),
        borefield.flow_data.mfr_borehole(power=(-1) * np.max(_resistances_input_range), fluid_data=borefield.fluid_data,
                                         nb_of_boreholes=borefield.number_of_boreholes, temperature=25))
    Rb_interp, temp_grid, power_grid = build_Rb_interpolator(
        borefield,
        (0, 1),
        (borefield.Tf_min - 2, borefield.Tf_max + 2))

    # rb = Rb_interp(np.column_stack([tf, flow]))

    def get_Rb(borefield, power, temp) -> np.ndarray:
        flow = borefield.flow_data.mfr_borehole(borefield.fluid_data, borefield.number_of_boreholes, temperature=temp,
                                                power=power / 1000)
        flow = np.minimum(max_flow * borefield.flow_data._min_flow_percentage, flow)
        return Rb_interp(np.column_stack([temp, flow]))

    def _get_rb(q: float) -> float:
        # q in W
        if _constant_resistance is not None:
            return _constant_resistance
        return np.interp(q, _resistances_input_range, _resistances_value_range)

    # START OF THE ACTUAL SIMULATION
    regeneration_array = np.zeros_like(borefield.load.hourly_net_resulting_injection_power)

    g_values = borefield.gfunction(borefield.load.time_L4, borefield.H)
    g_value_differences = np.diff(g_values, prepend=0)
    g_value_differences_horizon = g_value_differences[:simulation_horizon]

    recalculate = True

    hourly_load = borefield.load.hourly_net_resulting_injection_power
    load = copy.deepcopy(borefield.load)
    load.simulation_period = 1

    hourly_load = borefield.load.hourly_net_resulting_injection_power

    corr = 2 * np.pi * borefield.ground_data.k_s(borefield.calculate_depth(borefield.H, borefield.D), borefield.D) * (
            borefield.H * borefield.number_of_boreholes)
    import time

    start = time.time()
    year = 0
    offset = np.zeros_like(8760)
    Tb = np.zeros(8760)

    for i in range(8760 * borefield.load.simulation_period):

        if i % 8760 == 0 and i > 0:
            year += 1

        # change offset
        if year > 0 and i % 8760 == 0:
            load_prev = hourly_load[0:8670 * year] + regeneration_array[0:8670 * year] / 1000
            all_years = convolve(load_prev * 1000, g_value_differences)[:8760 * borefield.load.simulation_period]
            offset = all_years[year * 8760:(year + 1) * 8760]
            recalculate = True
            print(year)
            if balanced_per_year:
                # every year the imbalance should be compensated
                remaining_imbalance = borefield.load.imbalance * 1000

        if recalculate:
            # calculate borehole wall temperature
            Tf = np.full(simulation_horizon, borefield.Tf_min if injection_dominated else borefield.Tf_max)
            # start = time.time()
            load = (hourly_load[year * 8760:(year + 1) * 8760] * 1000 +
                    regeneration_array[year * 8760:(year + 1) * 8760])
            Tb = ((convolve(load, g_value_differences_horizon)[:8760] + offset) / corr + borefield._Tg(borefield.H))

            for _ in range(2):  # 3 more than enough to converge
                Tf_old = Tf
                Tf = Tb + load * (get_Rb(borefield, load, Tf) / borefield.number_of_boreholes / borefield.H)
                Tf_inlet = borefield.calculate_borefield_inlet_outlet_temperature(load, Tf, Tb)[0]
                # if variable_efficiency:
                #     Tb = convolve(
                #         hourly_load[i:min(8760 * borefield.load.simulation_period, i + simulation_horizon)] * 1000,
                #         g_value_differences[:8760])[:8760] / corr + borefield._Tg(borefield.H)
                #     borefield.load.set_results(ResultsHourly(np.tile(Tb, borefield.load.simulation_period),
                #                                              np.tile(Tf, borefield.load.simulation_period)))
                #     hourly_load = borefield.load.hourly_net_resulting_injection_power
            recalculate = False

        possible = regen_obj.get_regeneration_power_inlet(i, Tf_inlet[i % 8760],
                                                          min(max_flow * borefield.flow_data._min_flow_percentage,
                                                              borefield.flow_data.mfr_borefield(
                                                                  nb_of_boreholes=borefield.number_of_boreholes,
                                                                  power=load[i % 8760], temperature=Tf_inlet[i % 8760],
                                                                  fluid_data=borefield.fluid_data)),
                                                          borefield.fluid_data.cp(temperature=Tf_inlet[i % 8760]))
        if extraction_dominated and possible > 0 and (remaining_imbalance < 0 or 1 not in rules):
            new_load = load[i % 8760] + possible
            Tf_new = Tb[i % 8760] + new_load * (
                    get_Rb(borefield, new_load, Tf[i % 8760])[0] / borefield.number_of_boreholes / borefield.H)
            possible2 = regen_obj.get_regeneration_power_inlet(i, Tf_new,
                                                               min(max_flow * borefield.flow_data._min_flow_percentage,
                                                                   borefield.flow_data.mfr_borefield(
                                                                       nb_of_boreholes=borefield.number_of_boreholes,
                                                                       power=new_load, temperature=Tf_new,
                                                                       fluid_data=borefield.fluid_data)),
                                                               borefield.fluid_data.cp(temperature=Tf_new))

            ## RULES TO LIMIT THE REGENERATION
            max_reg = possible2
            # 1. Do not allow more regeneration than the imbalance
            if 1 in rules:
                max_reg = max(0, min((-1) * remaining_imbalance, possible2))

            # 2. Make sure current limit is not crossed
            if 2 in rules:
                resistance = get_Rb(borefield, new_load, borefield.Tf_max)[0]
                max_delta = borefield.Tf_max - Tb[i % 8760]
                max_power = max_delta / resistance * borefield.number_of_boreholes * borefield.H
                max_reg = min(max_power, max_reg)

            # 3. Make sure future limits are not crossed
            if 3 in rules:
                diff_array = borefield.Tf_max - Tf[i % 8760:]
                impact_array = diff_array / g_value_differences_horizon[:-i % 8760] * corr
                max_reg = min(min(impact_array), max_reg)

            # set regeneration
            remaining_imbalance += max_reg
            regeneration_array[i] = max_reg
            if max_reg != 0:
                recalculate = True
        if injection_dominated and possible < 0:
            pass

    # print('optie 1', time.time() - start)
    #
    # start = time.time()
    # borefield.load.simulation_period = 1
    # for i in range(8760):
    #
    #     if recalculate:
    #         # calculate borehole wall temperature
    #         Tf = np.full(simulation_horizon, borefield.Tf_min if injection_dominated else borefield.Tf_max)
    #         # start = time.time()
    #         Tb = convolve(
    #             hourly_load[i:min(8760 * borefield.load.simulation_period, i + simulation_horizon)] * 1000,
    #             g_value_differences_horizon)[:(8760 - i)] / corr + borefield._Tg(borefield.H)
    #         # print(time.time() - start)
    #         for _ in range(3):  # 3 more than enough to converge
    #             Tf_old = Tf
    #             Tf = Tb + hourly_load[i:min(8760 * borefield.load.simulation_period, i + simulation_horizon)] * 1000 * (
    #                     get_Rb(borefield,
    #                            hourly_load[i:min(8760 * borefield.load.simulation_period, i + simulation_horizon)],
    #                            Tf[:(8760 - i)]) / borefield.number_of_boreholes / borefield.H)
    #
    #             if variable_efficiency:
    #                 Tb = convolve(
    #                     hourly_load[i:min(8760 * borefield.load.simulation_period, i + simulation_horizon)] * 1000,
    #                     g_value_differences_horizon)[:8760] / corr + borefield._Tg(borefield.H)
    #                 borefield.load.set_results(ResultsHourly(np.tile(Tb, borefield.load.simulation_period),
    #                                                          np.tile(Tf, borefield.load.simulation_period)))
    #                 hourly_load = borefield.load.hourly_net_resulting_injection_power

    plt.figure()
    plt.plot(range(8760), borefield.load.hourly_net_resulting_injection_power[:8760], label='building demand')
    plt.plot(range(8760), regeneration_array[:8760] / 1000, label='regeneration')
    plt.ylabel('Ground load [kW]')
    plt.xlabel('Time [hours]')
    plt.xlim(0, 8760)
    plt.legend()
    plt.show()

    multiyear_load = HourlyBuildingLoadMultiYear(
        borefield.load.hourly_heating_load_simulation_period,
        borefield.load.hourly_cooling_load_simulation_period,
        borefield.load.cop,
        borefield.load.eer
    )
    multiyear_load.hourly_regeneration_load_simulation_period = regeneration_array / 1000
    return multiyear_load
    borefield.load = multiyear_load

    borefield.print_temperature_profile(plot_hourly=True)
    borefield.load.hourly_regeneration_load_simulation_period = regeneration_array / 1000
    borefield.print_temperature_profile(plot_hourly=True)

    # for i in range(8760):
    #
    #     if recalculate:
    #         # calculate borehole wall temperature
    #         Tf = np.full(simulation_horizon, borefield.Tf_min if injection_dominated else borefield.Tf_max)
    #         # start = time.time()
    #         Tb = convolve(
    #             hourly_load[i:min(8760 * borefield.load.simulation_period, i + simulation_horizon)] * 1000,
    #             g_value_differences[:8760])[:8760] / corr + borefield._Tg(borefield.H)
    #         # print(time.time() - start)
    #         for _ in range(3):  # 3 more than enough to converge
    #             Tf_old = Tf
    #             Tf = Tb + hourly_load[i:min(8760 * borefield.load.simulation_period, i + simulation_horizon)] * 1000 * (
    #                     get_Rb(borefield,
    #                            hourly_load[i:min(8760 * borefield.load.simulation_period, i + simulation_horizon)],
    #                            Tf) / borefield.number_of_boreholes / borefield.H)
    #
    #             if variable_efficiency:
    #                 Tb = convolve(
    #                     hourly_load[i:min(8760 * borefield.load.simulation_period, i + simulation_horizon)] * 1000,
    #                     g_value_differences[:8760])[:8760] / corr + borefield._Tg(borefield.H)
    #                 borefield.load.set_results(ResultsHourly(np.tile(Tb, borefield.load.simulation_period),
    #                                                          np.tile(Tf, borefield.load.simulation_period)))
    #                 hourly_load = borefield.load.hourly_net_resulting_injection_power
    # print('optie 1', time.time() - start)
    #
    # start = time.time()
    # borefield.load.simulation_period = 1
    # for i in range(8760):
    #
    #     if recalculate:
    #         # calculate borehole wall temperature
    #         Tf = np.full(simulation_horizon, borefield.Tf_min if injection_dominated else borefield.Tf_max)
    #         # start = time.time()
    #         Tb = convolve(
    #             hourly_load[i:min(8760 * borefield.load.simulation_period, i + simulation_horizon)] * 1000,
    #             g_value_differences[:8760])[:(8760 - i)] / corr + borefield._Tg(borefield.H)
    #         # print(time.time() - start)
    #         for _ in range(3):  # 3 more than enough to converge
    #             Tf_old = Tf
    #             Tf = Tb + hourly_load[i:min(8760 * borefield.load.simulation_period, i + simulation_horizon)] * 1000 * (
    #                     get_Rb(borefield,
    #                            hourly_load[i:min(8760 * borefield.load.simulation_period, i + simulation_horizon)],
    #                            Tf[:(8760 - i)]) / borefield.number_of_boreholes / borefield.H)
    #
    #             if variable_efficiency:
    #                 Tb = convolve(
    #                     hourly_load[i:min(8760 * borefield.load.simulation_period, i + simulation_horizon)] * 1000,
    #                     g_value_differences[:8760])[:8760] / corr + borefield._Tg(borefield.H)
    #                 borefield.load.set_results(ResultsHourly(np.tile(Tb, borefield.load.simulation_period),
    #                                                          np.tile(Tf, borefield.load.simulation_period)))
    #                 hourly_load = borefield.load.hourly_net_resulting_injection_power
    # print('optie 2', time.time() - start)


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
    borefield.set_max_fluid_temperature(25)
    borefield.set_min_fluid_temperature(5.5)
    hourly_load_building = HourlyBuildingLoad(efficiency_cooling=7, efficiency_heating=6)
    hourly_load_building.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\\auditorium.csv"), header=True,
                                             separator=";", col_cooling=0, col_heating=1)
    borefield.load = hourly_load_building
    borefield.print_temperature_profile(plot_hourly=True)
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

    surface = 50  # m²

    regeneration_object = Regeneration(power=solar * a0 * surface, temperature=temperature, a1=a1 * surface)
    # plt.figure()
    # plt.plot(borefield.load.hourly_net_resulting_injection_power)
    # ylabel('Regeneration [kW]')
    #
    # plt.show()
    # no_rules = calculate_temperature_profile_with_regeneration(borefield=borefield, regen_obj=regeneration_object,
    #                                                            rules=())
    # one_rule = calculate_temperature_profile_with_regeneration(borefield=borefield, regen_obj=regeneration_object,
    #                                                            rules=(1,))
    # two_rules = calculate_temperature_profile_with_regeneration(borefield=borefield, regen_obj=regeneration_object,
    #                                                             rules=(1, 2))
    three_rules = calculate_temperature_profile_with_regeneration(borefield=borefield, regen_obj=regeneration_object,
                                                                  rules=(1, 2, 3))
    borefield.load = three_rules
    borefield.print_temperature_profile(plot_hourly=True)

    data = {
        # 'No rules': no_rules,
        # 'Rule 1': one_rule,
        # 'Rule 2': two_rules,
        'Regeneration': three_rules,
        'Rule 3': three_rules,

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
