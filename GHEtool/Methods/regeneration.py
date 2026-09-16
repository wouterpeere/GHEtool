import matplotlib.pyplot as plt
from matplotlib.pyplot import ylabel

from GHEtool import *
from GHEtool.VariableClasses.LoadData import _LoadDataBuilding
from scipy.signal import convolve

import numpy as np

from GHEtool.VariableClasses.LoadData.Baseclasses import _HourlyDataBuilding


class _RegenerationWindow:
    """
    Bookkeeping for the moving 'validity window' used by `calculate_regeneration`.

    The borehole wall / fluid temperatures for a block of `simulation_horizon` hours are only ever
    computed once, under the assumption that no regeneration will take place inside that block. As long
    as that assumption holds, the previously computed values remain valid and there is no need to redo
    any work. A window is recomputed when:

      * `simulation_horizon` hours have passed without any regeneration event inside it (the window
        simply expires and the next block is computed), or
      * a regeneration event happens inside the window. This invalidates every hour after it, since the
        energy is wrong

    Note that a smaller horizon comes at the cost of the "rule 3" look-ahead (see `calculate_regeneration`) only
    guarding against exceeding the fluid temperature limits within the current window, rather than the rest of the
    simulation period.
    """

    def __init__(self, simulation_horizon: int, total_length: int):
        self.simulation_horizon = simulation_horizon
        self.total_length = total_length
        self.window_start = 0
        self.window_end = 0
        self._next_recalculation = 0

    @property
    def length(self) -> int:
        """
        Returns the length of the simulation window.

        Returns
        -------
        int
            Length of the simulation window [hours]
        """
        return self.window_end - self.window_start

    def needs_recalculation(self, i: int) -> bool:
        """True if hour `i` falls outside the currently valid window."""
        return i >= self._next_recalculation

    def invalidate(self, i: int) -> None:
        """
        A regeneration event at hour `i` invalidates every hour after it. Force a recalculation starting
        at the very next hour.
        """
        self._next_recalculation = i + 1

    def recalculate(self, i: int) -> None:
        """Register a freshly computed window starting at hour `i`."""
        self.window_start = i
        self.window_end = min(i + self.simulation_horizon, self.total_length)
        self._next_recalculation = self.window_end


def calculate_regeneration(borefield: Borefield, regen_obj: Regeneration,
                           algorithm: str = 'yearly',
                           position_regeneration: str = "inlet",
                           rules=(1, 2, 3),
                           simulation_horizon: int = 4380,
                           **kwargs
                           ) -> tuple[HourlyBuildingLoadMultiYear, np.ndarray]:
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
        The three different rules for regeneration as explained in Peere (2027).
    simulation_horizon : int
        The maximum number of hours a computed window of temperatures is trusted for  before being refreshed,
        assuming no regeneration event invalidates it sooner (see `RegenerationWindow`).

    Returns
    -------
    tuple : HourlyBuildingLoadMultiYear, np.ndarray
        The multi-year hourly building load with the regeneration and the regeneration load [kW]

    References
    ----------
    .. [#Peere] Peere, W. (2027). Validated combined first and last year borefield sizing methodology. In Proceedings of GeoTHERM 2027. Offenburg (Germany), 25-26 February 2027. [abstract submitted]
    """
    borefield = copy.deepcopy(borefield)

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

    if position_regeneration not in ('inlet', 'outlet'):
        raise ValueError('Position_regeneration must be either "inlet" or "outlet"')

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
        print(max_power)
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
    total_length = 8760 * borefield.load.simulation_period
    regeneration_array = np.zeros_like(borefield.load.hourly_net_resulting_injection_power)

    g_values = borefield.gfunction(borefield.load.time_L4, borefield.H)
    g_value_differences = np.diff(g_values, prepend=0)

    hourly_load = borefield.load.hourly_net_resulting_injection_power

    # correction factor to convert the g-function values to the ground temperature
    corr = 2 * np.pi * borefield.ground_data.k_s(borefield.calculate_depth(borefield.H, borefield.D), borefield.D) * (
            borefield.H * borefield.number_of_boreholes)
    g0_corr = g_value_differences[0] / corr

    # initiate objects
    window = _RegenerationWindow(simulation_horizon, total_length)
    Tb = np.zeros(0)
    Tf_avg = np.zeros(0)
    Tf_to_regeneration = np.zeros(0)
    load = np.zeros(0)
    future_offset = np.zeros(total_length)

    year = 0

    if algorithm == 'yearly':
        # every year the imbalance should be compensated
        remaining_imbalance = np.sum(hourly_load[0:8760]) * 1000
    elif algorithm == 'total':
        # imbalance may be compensated sooner
        remaining_imbalance = np.sum(hourly_load) * 1000
    else:
        # both proceeding or proceeding_extra
        # only the imbalance that has already been should be accounted for
        remaining_imbalance = 0

    building_imbalance = remaining_imbalance

    for i in range(total_length):
        # start a new year. This is independent from the recalculation window below, since a year
        # boundary no longer necessarily coincides with a window boundary once simulation_horizon != 8760.
        if i % 8760 == 0 and i > 0:
            print(year)
            year += 1
            if algorithm == 'yearly':
                remaining_imbalance = np.sum(hourly_load[year * 8760:(year + 1) * 8760]) * 1000  # in Wh
                building_imbalance = remaining_imbalance

        # check if the (fluid) temperatures need recalculation
        if window.needs_recalculation(i):

            finalised_length = i - window.window_start
            if finalised_length > 0:
                finalised_load = (hourly_load[window.window_start:i] * 1000 + regeneration_array[window.window_start:i])
                contribution = convolve(finalised_load, g_value_differences)
                future_offset[i:total_length] += contribution[finalised_length:total_length - window.window_start]

            window.recalculate(i)

            # calculate borehole wall temperature for the new window
            Tf_avg = np.full(window.length, borefield.Tf_min if injection_dominated else borefield.Tf_max)
            load = (hourly_load[window.window_start:window.window_end] * 1000 +
                    regeneration_array[window.window_start:window.window_end])
            Tb = ((convolve(load, g_value_differences[:window.length])[:window.length]
                   + future_offset[window.window_start:window.window_end]) / corr + borefield._Tg(borefield.H))

            # iterate to converge for the fluid temperature
            for _ in range(2):  # 3 more than enough to converge
                Tf_avg = Tb + load * (get_Rb(borefield, load, Tf_avg) / borefield.number_of_boreholes / borefield.H)
                if position_regeneration == 'inlet':
                    Tf_to_regeneration = borefield.calculate_borefield_inlet_outlet_temperature(load, Tf_avg, Tb)[0]
                else:
                    Tf_to_regeneration = borefield.calculate_borefield_inlet_outlet_temperature(load, Tf_avg, Tb)[1]

                # calculate reference temperature
                if borefield._calculation_setup.size_based_on == 'average':
                    Tf_ref = Tf_avg
                else:
                    Tf_ref = Tf_to_regeneration

                # with variable efficiency, the ground load should be updated as well
                if variable_efficiency:
                    load = (hourly_load[window.window_start:window.window_end] * 1000 +
                            regeneration_array[window.window_start:window.window_end])
                    Tb = convolve(load, g_value_differences[:window.length])[:window.length] + future_offset[
                        window.window_start:window.window_end]
                    Tb = Tb / corr + borefield._Tg(borefield.H)

                    borefield.load.set_results(
                        ResultsHourly(np.resize(Tb, total_length), np.resize(Tf_avg, total_length)))
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

        # position of hour i inside the arrays of the currently valid window
        idx = i - window.window_start

        # calculate the imbalance from the previous hours until now
        if algorithm in ('proceeding', 'proceeding_extra'):
            remaining_imbalance += hourly_load[i % 8760] * 1000  # Wh

        # calculate possible regeneration power (W)
        possible_regen_power = regen_obj.get_regeneration_power_inlet(
            i, Tf_to_regeneration[idx],
            max(min_flow, borefield.flow_data.mfr_borefield(
                nb_of_boreholes=borefield.number_of_boreholes,
                power=load[idx] / 1000,
                temperature=Tf_to_regeneration[idx],
                fluid_data=borefield.fluid_data)),
            borefield.fluid_data.cp(
                temperature=Tf_to_regeneration[idx]))

        base_Tb = Tb[idx] - load[idx] * g0_corr

        if (extraction_dominated and algorithm != 'proceeding_extra' or algorithm == 'proceeding_extra') \
                and possible_regen_power > 0 and (remaining_imbalance < 0 or 1 not in rules):
            # calculate new load based on regeneration
            new_load = load[idx] + possible_regen_power  # W
            Tf_avg_new = Tb[idx] + new_load * (
                    get_Rb(borefield, new_load, Tf_avg[idx])[0] / borefield.number_of_boreholes / borefield.H +
                    g_value_differences[0] / corr)

            # calculate fluid temperature for regeneration based on if it is placed at the borefield inlet or outlet
            if position_regeneration == 'inlet':
                Tf_to_regeneration_temp = \
                    borefield.calculate_borefield_inlet_outlet_temperature(new_load, Tf_avg_new, Tb[idx])[0]
            else:
                Tf_to_regeneration_temp = \
                    borefield.calculate_borefield_inlet_outlet_temperature(new_load, Tf_avg_new, Tb[idx])[1]

            # update possible regeneration power
            max_reg = regen_obj.get_regeneration_power_inlet(
                i, Tf_to_regeneration_temp,
                max(min_flow, borefield.flow_data.mfr_borefield(
                    nb_of_boreholes=borefield.number_of_boreholes,
                    power=new_load / 1000, temperature=Tf_avg_new,
                    fluid_data=borefield.fluid_data)),
                borefield.fluid_data.cp(temperature=Tf_avg_new))

            ## RULES TO LIMIT THE REGENERATION
            # 1. Do not allow more regeneration than the imbalance
            if 1 in rules:
                max_reg = max(0, min((-1) * remaining_imbalance, max_reg))

            # 2. Make sure current limit is not crossed
            if 2 in rules:
                def calculate_max_power(power):
                    resistance = get_Rb(borefield, power, borefield.Tf_max)[0]
                    Tb_corrected = base_Tb + power * g0_corr
                    max_delta = borefield.Tf_max - Tb_corrected
                    if borefield._calculation_setup.size_based_on != 'average':
                        debiet = max(min_flow, borefield.flow_data.mfr_borefield(
                            nb_of_boreholes=borefield.number_of_boreholes,
                            power=power / 1000, temperature=borefield.Tf_max,
                            fluid_data=borefield.fluid_data))
                        cp = borefield.fluid_data.cp(temperature=borefield.Tf_max)
                        delta = power / (cp * debiet)
                        if borefield._calculation_setup.size_based_on == 'inlet':
                            max_delta -= delta / 2
                        else:
                            max_delta += delta / 2
                    return max_delta / resistance * borefield.number_of_boreholes * borefield.H - np.abs(load[idx])

                max_power = max_reg

                for _ in range(10):
                    max_power_prev = max_power
                    max_power = calculate_max_power(max_power)

                    if np.isclose(max_power, max_power_prev, rtol=1e-2):
                        break

                max_reg = min(max_power, max_reg)

            # 3. Make sure future limits are not crossed (within the current window - see simulation_horizon
            # docstring above)
            if 3 in rules:
                remaining_in_window = window.length - idx
                diff_array = borefield.Tf_max - Tf_ref[idx:]
                impact_array = diff_array / g_value_differences[:remaining_in_window] * corr
                max_reg = min(min(impact_array), max_reg)

            # make sure regeneration is positive
            max_reg = max(0, max_reg)

            # set regeneration
            remaining_imbalance += max_reg
            regeneration_array[i] = max_reg

            # When there was regeneration, the remainder of the window is no longer valid
            if max_reg != 0:
                window.invalidate(i)

        if (injection_dominated and algorithm != 'proceeding_extra' or algorithm == 'proceeding_extra') \
                and possible_regen_power < 0 and (remaining_imbalance > 0 or 1 not in rules):
            # calculate new load based on regeneration
            new_load = load[idx] + possible_regen_power  # W
            Tf_avg_new = Tb[idx] + new_load * (
                    get_Rb(borefield, new_load, Tf_avg[idx])[0] / borefield.number_of_boreholes / borefield.H)

            # calculate fluid temperature for regeneration based on if it is placed at the borefield inlet or outlet
            if position_regeneration == 'inlet':
                Tf_to_regeneration_temp = \
                    borefield.calculate_borefield_inlet_outlet_temperature(new_load, Tf_avg_new, Tb[idx])[0]
            else:
                Tf_to_regeneration_temp = \
                    borefield.calculate_borefield_inlet_outlet_temperature(new_load, Tf_avg_new, Tb[idx])[1]

            # update possible regeneration power
            max_reg = regen_obj.get_regeneration_power_inlet(
                i, Tf_to_regeneration_temp,
                max(min_flow, borefield.flow_data.mfr_borefield(
                    nb_of_boreholes=borefield.number_of_boreholes,
                    power=new_load / 1000, temperature=Tf_avg_new,
                    fluid_data=borefield.fluid_data)),
                borefield.fluid_data.cp(temperature=Tf_avg_new))

            max_reg = (-1) * max_reg
            ## RULES TO LIMIT THE REGENERATION
            # 1. Do not allow more regeneration than the imbalance
            if 1 in rules:
                max_reg = max(0, min(remaining_imbalance, max_reg), )

            # 2. Make sure current limit is not crossed
            if 2 in rules:
                def calculate_max_power(power):
                    resistance = get_Rb(borefield, power, borefield.Tf_min)[0]
                    Tb_corrected = base_Tb - power * g0_corr
                    max_delta = max(0, Tb_corrected - borefield.Tf_min)
                    if borefield._calculation_setup.size_based_on == 'inlet':
                        max_delta += borefield.calculate_borefield_inlet_outlet_temperature((-1) * power, 0,
                                                                                            Tb_corrected)[0]
                    elif borefield._calculation_setup.size_based_on == 'outlet':
                        max_delta += borefield.calculate_borefield_inlet_outlet_temperature((-1) * power, 0,
                                                                                            Tb_corrected)[1]

                    return max_delta / resistance * borefield.number_of_boreholes * borefield.H - np.abs(load[idx])

                max_power = max_reg

                for _ in range(10):
                    max_power_prev = max_power
                    max_power = calculate_max_power(max_power)

                    if np.isclose(max_power, max_power_prev, rtol=1e-2):
                        break

                max_reg = min(max_power, max_reg)

                # resistance = get_Rb(borefield, new_load, borefield.Tf_min)[0]
                # max_delta = Tf_avg[idx] - borefield.Tf_min
                # max_power = max_delta / resistance * borefield.number_of_boreholes * borefield.H
                # max_reg = min(max_power, max_reg)

            # 3. Make sure future limits are not crossed (within the current window)
            if 3 in rules:
                remaining_in_window = window.length - idx
                diff_array = Tf_ref[idx:] - borefield.Tf_min
                impact_array = diff_array / g_value_differences[:remaining_in_window] * corr
                max_reg = min(min(impact_array), max_reg)

            # make sure regeneration is positive
            max_reg = max(0, max_reg)

            # reset sign
            max_reg = (-1) * max_reg

            # set regeneration
            remaining_imbalance += max_reg
            regeneration_array[i] = max_reg

            # When there was regeneration, the remainder of the window is no longer valid
            if max_reg != 0:
                window.invalidate(i)

    if isinstance(borefield.load, (HourlyBuildingLoadMultiYear, HourlyBuildingLoad)):
        multiyear_load: HourlyBuildingLoadMultiYear = HourlyBuildingLoadMultiYear(
            borefield.load.hourly_heating_load_simulation_period,
            borefield.load.hourly_cooling_load_simulation_period,
            borefield.load.cop,
            borefield.load.eer,
            borefield.load.hourly_dhw_load_simulation_period,
            borefield.load.cop_dhw
        )
    else:
        multiyear_load: HourlyGeothermalLoadMultiYear = HourlyGeothermalLoadMultiYear(
            borefield.load.hourly_extraction_load_simulation_period,
            borefield.load.hourly_injection_load_simulation_period
        )
    multiyear_load.hourly_regeneration_load_simulation_period = regeneration_array / 1000  # convert to kWh

    return multiyear_load, regeneration_array / 1000
