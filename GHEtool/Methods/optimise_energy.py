import copy
import numpy as np

from typing import Union
from scipy.signal import convolve, oaconvolve

from GHEtool import VariableHourlyFlowRate, VariableHourlyMultiyearFlowRate
from GHEtool.VariableClasses import HourlyBuildingLoad, HourlyBuildingLoadMultiYear, ConstantFlowRate, \
    ConstantDeltaTFlowRate, SCOP, SEER


def optimise_load_profile_energy(
        borefield,
        building_load: Union[HourlyBuildingLoad, HourlyBuildingLoadMultiYear],
        temperature_threshold: float = 0.05,
        max_peak_heating: float = None,
        max_peak_cooling: float = None,
        max_peak_dhw: float = None,
        dhw_preferential: bool = None,
        simulation_horizon: int = 8760
) -> tuple[HourlyBuildingLoadMultiYear, HourlyBuildingLoadMultiYear]:
    """
    This function optimises the load for maximum energy extraction and injection based on the given borefield and
    the given hourly building load. It walks through the simulation period hour by hour and, whenever the fluid
    temperature would cross one of its limits, it lowers the geothermal heating, domestic hot water (DHW) or cooling
    load of that hour just enough to stay on the limit. The part that cannot be delivered by the borefield is
    returned as the external load.

    Since the algorithm is causal (an hour is fixed before the next one is considered), the result is the
    hourly equivalent of the former month-by-month approach, but without the conversion to a monthly load.

    The borehole wall temperature is linear in the load, so a reduction at a certain hour is propagated exactly to
    the remaining hours of the current window by adding its step response. This means a window never has to be
    recalculated because of a reduction. After every window, its (final) load is convolved once with the g-function
    to obtain its effect on all later hours.

    Parameters
    ----------
    borefield : Borefield
        Borefield object
    building_load : HourlyBuildingLoad | HourlyBuildingLoadMultiYear
        Load data used for the optimisation
    temperature_threshold : float
        Temperature tolerance [K]. An hour is only limited when it crosses a limit by more than 1/5 of this value
        and the load is then reduced until the fluid temperature is within 1/10 of this value from the limit.
    max_peak_heating : float
        The maximum peak power for heating (building side) [kW]
    max_peak_cooling : float
        The maximum peak power for cooling (building side) [kW]
    max_peak_dhw : float
        The maximum peak power for domestic hot water (building side) [kW]
    dhw_preferential : bool
        True if heating should be reduced first, only after which the dhw share is reduced.
        False if dhw should be reduced first, only after which the heating is reduced.
        If it is None, then the dhw profile is not optimised and kept constant (so the limit can still be crossed
        in hours where the dhw demand alone is too large).
    simulation_horizon : int
        Length of the window [hours] in which reductions are propagated directly. This is a pure speed setting
        and does not change the result (for constant efficiencies): smaller windows make each reduction cheaper,
        but require more convolutions over the full simulation period.

    Returns
    -------
    tuple [HourlyBuildingLoadMultiYear, HourlyBuildingLoadMultiYear]
        borefield load, external load

    Raises
    ------
    ValueError
        ValueError if no correct load data is given or the threshold is negative
    """
    # checks
    if not isinstance(building_load, (HourlyBuildingLoad, HourlyBuildingLoadMultiYear)):
        raise ValueError("The building load should be of the class HourlyBuildingLoad or HourlyBuildingLoadMultiYear!")
    if temperature_threshold < 0:
        raise ValueError(f"The temperature threshold is {temperature_threshold}, but it cannot be below 0!")
    if not borefield.borehole.use_constant_Rb and \
            isinstance(borefield.borehole.flow_data, (VariableHourlyFlowRate, VariableHourlyMultiyearFlowRate)):
        raise ValueError('No hourly flow rate can be used when working with this method.')

    borefield = copy.deepcopy(borefield)
    size_based_on = borefield._calculation_setup.size_based_on
    if borefield.borehole.use_constant_Rb and size_based_on != 'average':
        raise ValueError('Sizing based on the inlet or outlet temperature requires a variable borehole resistance.')

    # building load (secondary side) over the whole simulation period [kW]
    heating_load_original = np.asarray(building_load.hourly_heating_load_simulation_period, dtype=float)
    cooling_load_original = np.asarray(building_load.hourly_cooling_load_simulation_period, dtype=float)
    dhw_load_original = np.asarray(building_load.hourly_dhw_load_simulation_period, dtype=float)

    # building load that is covered by the borefield [kW]. These arrays are reduced during the optimisation.
    heating_load = heating_load_original.copy() if max_peak_heating is None \
        else np.minimum(heating_load_original, max_peak_heating)
    cooling_load = cooling_load_original.copy() if max_peak_cooling is None \
        else np.minimum(cooling_load_original, max_peak_cooling)
    dhw_load = dhw_load_original.copy() if max_peak_dhw is None \
        else np.minimum(dhw_load_original, max_peak_dhw)

    def create_multiyear_load(heating: np.ndarray, cooling: np.ndarray,
                              dhw: np.ndarray) -> HourlyBuildingLoadMultiYear:
        """
        This function creates a multi-year hourly building load with the same settings (efficiencies, peak
        durations ...) as the original building load.

        Parameters
        ----------
        heating : np.ndarray
            Hourly heating load for the whole simulation period [kW]
        cooling : np.ndarray
            Hourly cooling load for the whole simulation period [kW]
        dhw : np.ndarray
            Hourly domestic hot water load for the whole simulation period [kW]

        Returns
        -------
        HourlyBuildingLoadMultiYear
            Multi-year hourly building load
        """
        multiyear_load = HourlyBuildingLoadMultiYear(heating, cooling, building_load._cop, building_load._eer, dhw,
                                                     building_load._cop_dhw)
        multiyear_load.exclude_DHW_from_peak = building_load.exclude_DHW_from_peak
        multiyear_load.peak_extraction_duration = building_load.peak_extraction_duration / 3600
        multiyear_load.peak_injection_duration = building_load.peak_injection_duration / 3600
        multiyear_load._limit_to_max_heat_pump_power = building_load._limit_to_max_heat_pump_power
        return multiyear_load

    borefield.load = create_multiyear_load(heating_load, cooling_load, dhw_load)
    load = borefield.load
    cop_heating, eer_cooling, cop_dhw = load.cop, load.eer, load.cop_dhw
    variable_efficiency = not (isinstance(cop_heating, SCOP) and isinstance(cop_dhw, SCOP)
                               and isinstance(eer_cooling, SEER))
    limit_to_max_heat_pump_power = load._limit_to_max_heat_pump_power
    month_indices = load.month_indices

    # borehole resistance
    borehole_length, number_of_boreholes = borefield.H, borefield.number_of_boreholes
    conductivity = borefield.ground_data.k_s(borefield.calculate_depth(borehole_length, borefield.D), borefield.D)
    if not borefield.borehole.use_constant_Rb:
        if not isinstance(borefield.borehole.flow_data, (ConstantFlowRate, ConstantDeltaTFlowRate)):
            raise ValueError('Only constant flow rates or constant Delta T flow rates can be used.')
        borefield.borehole.set_interpolator(borehole_length, borefield.D, borefield.r_b,
                                            borefield.ground_data.k_s(borefield.depth, borefield.D),
                                            borefield.depth, nb_of_boreholes=number_of_boreholes)

    flow_data, fluid_data = borefield.borehole.flow_data, borefield.borehole.fluid_data
    constant_delta_t = isinstance(flow_data, ConstantDeltaTFlowRate)
    minimum_mass_flow_borefield = 0.  # [kg/s], set below once the ground load is known

    def calculate_mass_flow_borefield(ground_power: Union[float, np.ndarray],
                                      temperature: Union[float, np.ndarray]) -> np.ndarray:
        """
        This function calculates the mass flow rate of the entire borefield. For a constant delta T flow rate, the
        minimum flow rate is a fixed value (based on the original peak load), so that a single hour gets the same
        flow rate as it would get in a call with the full array.

        Parameters
        ----------
        ground_power : float | np.ndarray
            Ground load, positive for injection and negative for extraction [W]
        temperature : float | np.ndarray
            Average fluid temperature [°C]

        Returns
        -------
        np.ndarray
            Mass flow rate of the entire borefield [kg/s]
        """
        power_kw = np.atleast_1d(np.asarray(ground_power, dtype=float)) / 1000
        if not constant_delta_t:
            return np.broadcast_to(flow_data.mfr_borefield(fluid_data=fluid_data, power=power_kw,
                                                           nb_of_boreholes=number_of_boreholes,
                                                           temperature=temperature), power_kw.shape)
        mass_flow = flow_data.mfr_borefield(fluid_data=fluid_data, power=power_kw, temperature=temperature,
                                            min_flow_percentage=0)
        return np.maximum(mass_flow, minimum_mass_flow_borefield)

    def calculate_borehole_resistance(ground_power: Union[float, np.ndarray],
                                      temperature: Union[float, np.ndarray]) -> np.ndarray:
        """
        This function calculates the effective borehole thermal resistance.

        Parameters
        ----------
        ground_power : float | np.ndarray
            Ground load, positive for injection and negative for extraction [W]
        temperature : float | np.ndarray
            Average fluid temperature [°C]

        Returns
        -------
        np.ndarray
            Effective borehole thermal resistance [mK/W]
        """
        ground_power = np.atleast_1d(np.asarray(ground_power, dtype=float))
        if borefield.borehole.use_constant_Rb:
            return np.full_like(ground_power, borefield.borehole.Rb)
        mass_flow_borehole = calculate_mass_flow_borefield(ground_power, temperature) / number_of_boreholes \
                             * getattr(flow_data, '_series_factor', 1)
        temperature = np.broadcast_to(np.asarray(temperature, dtype=float), ground_power.shape)
        return borefield.borehole._interp(np.column_stack([temperature, mass_flow_borehole]))

    def calculate_reference_fluid_temperature(ground_power: np.ndarray, fluid_temperature_average: np.ndarray,
                                              borehole_wall_temperature: np.ndarray) -> np.ndarray:
        """
        This function calculates the fluid temperature that is compared with the temperature limits. Depending on
        the calculation setup, this is the average, inlet or outlet fluid temperature. The calculation is the same
        as in Borehole._calculate_borefield_inlet_outlet_temperature, but with the fixed minimum flow rate.

        Parameters
        ----------
        ground_power : np.ndarray
            Ground load, positive for injection and negative for extraction [W]
        fluid_temperature_average : np.ndarray
            Average fluid temperature [°C]
        borehole_wall_temperature : np.ndarray
            Borehole wall temperature [°C]

        Returns
        -------
        np.ndarray
            Reference fluid temperature [°C]
        """
        if size_based_on == 'average':
            return fluid_temperature_average
        power_kw = np.asarray(ground_power, dtype=float) / 1000
        delta_temperature = np.nan_to_num(
            power_kw / (fluid_data.cp(temperature=fluid_temperature_average) / 1000 *
                        calculate_mass_flow_borefield(ground_power, fluid_temperature_average)))
        # limit the temperature difference to 2x the difference between the fluid and the borehole wall
        max_delta_temperature = 2 * (fluid_temperature_average - borehole_wall_temperature)
        delta_temperature = np.where(delta_temperature > 0,
                                     np.minimum(max_delta_temperature, delta_temperature),
                                     np.maximum(max_delta_temperature, delta_temperature))
        if size_based_on == 'inlet':
            return fluid_temperature_average + delta_temperature / 2
        return fluid_temperature_average - delta_temperature / 2

    def calculate_conversion_factors(hours: slice, fluid_temperature_average: np.ndarray) -> tuple:
        """
        This function calculates the factors to convert the secondary (building) load to the primary (ground) load
        for a range of hours, together with the building load that can actually be delivered by the heat pump.
        The logic mirrors the one in _HourlyDataBuilding.

        Parameters
        ----------
        hours : slice
            Hours of the simulation period for which the factors should be calculated
        fluid_temperature_average : np.ndarray
            Average fluid temperature for these hours [°C]

        Returns
        -------
        tuple
            factor_heating, factor_dhw, factor_cooling [-] (np.ndarray) and
            available_heating, available_dhw, available_cooling [kW] (np.ndarray)
        """
        heating, cooling, dhw = heating_load[hours], cooling_load[hours], dhw_load[hours]
        months = month_indices[hours]
        factor_heating = 1 - 1 / np.asarray(
            cop_heating.get_COP(fluid_temperature_average, power=np.nan_to_num(heating)))
        factor_dhw = 1 - 1 / np.asarray(cop_dhw.get_COP(fluid_temperature_average, power=np.nan_to_num(dhw)))
        factor_cooling = 1 + 1 / np.asarray(
            eer_cooling.get_EER(fluid_temperature_average, power=np.nan_to_num(cooling), month_indices=months))
        factor_heating, factor_dhw, factor_cooling = (np.broadcast_to(factor, heating.shape).astype(float)
                                                      for factor in (factor_heating, factor_dhw, factor_cooling))
        if limit_to_max_heat_pump_power:
            if not isinstance(cop_heating, SCOP):
                heating = np.minimum(heating, cop_heating._get_max_power(fluid_temperature_average))
            if not isinstance(cop_dhw, SCOP):
                dhw = np.minimum(dhw, cop_dhw._get_max_power(fluid_temperature_average))
            if not isinstance(eer_cooling, SEER):
                cooling = np.minimum(cooling, eer_cooling._get_max_power(fluid_temperature_average,
                                                                         month_indices=months))
        return factor_heating, factor_dhw, factor_cooling, heating, dhw, cooling

    ground_temperature = borefield._Tg(borehole_length)
    if constant_delta_t:
        # fix the minimum flow rate based on the peak of the original ground load
        factor_heating, factor_dhw, factor_cooling, available_heating, available_dhw, available_cooling = \
            calculate_conversion_factors(slice(None), np.full(len(heating_load), ground_temperature))
        ground_power_estimate = (available_cooling * factor_cooling - available_heating * factor_heating
                                 - available_dhw * factor_dhw) * 1000
        minimum_mass_flow_borefield = flow_data._min_flow_percentage / 100 * np.max(
            flow_data.mfr_borefield(fluid_data=fluid_data, power=ground_power_estimate / 1000,
                                    temperature=ground_temperature, min_flow_percentage=0))

    # g-function
    total_length = 8760 * load.simulation_period
    g_values = borefield.gfunction(load.time_L4, borehole_length)
    g_value_differences = np.diff(g_values, prepend=0)
    # factor to convert the convolution of the g-function with the load [W] into a temperature difference [K]
    g_function_to_temperature = 2 * np.pi * conductivity * borehole_length * number_of_boreholes
    first_hour_response = g_value_differences[0] / g_function_to_temperature  # [K/W]
    Tf_min, Tf_max = borefield.Tf_min, borefield.Tf_max

    # net ground load per hour, positive for injection and negative for extraction [W]
    ground_power = np.zeros(total_length)
    # convolution of the load of all finished windows with the g-function, for every hour [W]
    convolution_finished_windows = np.zeros(total_length)
    fluid_temperature_guess = ground_temperature

    # The hourly solver evaluates Rb at the temperature limits only, so Rb is a function of the power alone
    # (through the flow rate). Tabulate it once instead of calling get_Rb for every iteration.
    max_ground_power = 1000 * 1.5 * (np.max(heating_load_original) + np.max(dhw_load_original)
                                     + np.max(cooling_load_original)) + 1
    power_table = np.concatenate([-np.geomspace(max_ground_power, 1, 300), [0], np.geomspace(1, max_ground_power, 300)])
    borehole_resistance_table = {
        limit: np.broadcast_to(calculate_borehole_resistance(power_table, np.full_like(power_table, limit)),
                               power_table.shape)
        for limit in (Tf_min, Tf_max)}
    # temperature difference over the borefield [K] as a function of the power (only for inlet/outlet)
    delta_temperature_table = {
        limit: np.zeros_like(power_table) if size_based_on == 'average' else np.nan_to_num(
            power_table / (fluid_data.cp(temperature=limit) * calculate_mass_flow_borefield(power_table, limit)))
        for limit in (Tf_min, Tf_max)}

    def calculate_reference_fluid_temperature_single_hour(power: float, wall_temperature_without_current_hour: float,
                                                          limit: float) -> float:
        """
        This function calculates the reference fluid temperature of a single hour for a given ground load, with the
        fluid properties evaluated at the temperature limit.

        Parameters
        ----------
        power : float
            Ground load of the current hour, positive for injection and negative for extraction [W]
        wall_temperature_without_current_hour : float
            Borehole wall temperature without the contribution of the load of the current hour [°C]
        limit : float
            Temperature limit (Tf_min or Tf_max) at which the borehole resistance is evaluated [°C]

        Returns
        -------
        float
            Reference fluid temperature [°C]
        """
        wall_temperature = wall_temperature_without_current_hour + power * first_hour_response
        fluid_temperature_average = wall_temperature + power * np.interp(
            power, power_table, borehole_resistance_table[limit]) / number_of_boreholes / borehole_length
        if size_based_on == 'average':
            return fluid_temperature_average
        delta_temperature = np.interp(power, power_table, delta_temperature_table[limit])
        max_delta_temperature = 2 * (fluid_temperature_average - wall_temperature)
        delta_temperature = min(max_delta_temperature, delta_temperature) if delta_temperature > 0 \
            else max(max_delta_temperature, delta_temperature)
        if size_based_on == 'inlet':
            return fluid_temperature_average + delta_temperature / 2
        return fluid_temperature_average - delta_temperature / 2

    def find_power_on_limit(violating_power: float, wall_temperature_without_current_hour: float,
                            limit: float) -> Union[float, None]:
        """
        This function searches the ground load for which the reference fluid temperature equals the limit. It
        searches between the violating load and (almost) zero load with the Illinois variant of the regula falsi
        method.

        Parameters
        ----------
        violating_power : float
            Ground load of the current hour that crosses the limit [W]
        wall_temperature_without_current_hour : float
            Borehole wall temperature without the contribution of the load of the current hour [°C]
        limit : float
            Temperature limit that is crossed (Tf_min or Tf_max) [°C]

        Returns
        -------
        float | None
            Ground load on the limit [W], or None if even (almost) no load in that direction respects the limit
            (i.e. the ground itself is already beyond the limit)
        """
        # stay on the same side of zero, because of the jump in inlet/outlet temperature for a constant delta T
        power_violating = violating_power
        power_safe = -1. if violating_power < 0 else 1.
        error_violating = calculate_reference_fluid_temperature_single_hour(
            power_violating, wall_temperature_without_current_hour, limit) - limit
        error_safe = calculate_reference_fluid_temperature_single_hour(
            power_safe, wall_temperature_without_current_hour, limit) - limit
        if error_violating * error_safe > 0:
            return None
        last_side_updated = 0
        for _ in range(30):
            power = (power_violating * error_safe - power_safe * error_violating) / (error_safe - error_violating)
            error = calculate_reference_fluid_temperature_single_hour(
                power, wall_temperature_without_current_hour, limit) - limit
            if error * error_safe >= 0:
                # power respects the limit
                power_safe, error_safe = power, error
                if abs(error) < temperature_threshold / 10:
                    break
                if last_side_updated == -1:
                    error_violating /= 2
                last_side_updated = -1
            else:
                power_violating, error_violating = power, error
                if last_side_updated == 1:
                    error_safe /= 2
                last_side_updated = 1
        return power_safe

    tolerance = temperature_threshold / 5  # tolerance before an hour is considered to cross a limit
    max_passes = 10
    for window_start in range(0, total_length, simulation_horizon):
        window_end = min(window_start + simulation_horizon, total_length)
        window = slice(window_start, window_end)
        window_length = window_end - window_start

        # With temperature dependent efficiencies, the efficiencies of the hours after a reduction change as well
        # (the fluid gets warmer/colder). Therefore, the window is re-evaluated with its final loads and checked
        # again until no hour crosses a limit anymore. With constant efficiencies, a single pass suffices.
        fluid_temperature_average = np.full(window_length, fluid_temperature_guess, dtype=float)
        for _ in range(max_passes if variable_efficiency else 1):
            # temperatures for the window, iterate for temperature dependent efficiencies and Rb
            for _ in range(3 if variable_efficiency else 2):
                factor_heating, factor_dhw, factor_cooling, available_heating, available_dhw, available_cooling = \
                    calculate_conversion_factors(window, fluid_temperature_average)
                ground_power[window] = (available_cooling * factor_cooling - available_heating * factor_heating
                                        - available_dhw * factor_dhw) * 1000
                convolution_window = convolve(ground_power[window], g_value_differences[:window_length])[:window_length]
                borehole_wall_temperature = (convolution_window + convolution_finished_windows[window]) \
                                            / g_function_to_temperature + ground_temperature
                borehole_resistance = calculate_borehole_resistance(ground_power[window], fluid_temperature_average)
                fluid_temperature_average = borehole_wall_temperature + ground_power[window] * borehole_resistance \
                                            / number_of_boreholes / borehole_length
            # copy, so it is never a view on the average fluid temperature
            fluid_temperature_reference = np.array(calculate_reference_fluid_temperature(
                ground_power[window], fluid_temperature_average, borehole_wall_temperature), dtype=float)
            # make sure the limited heat pump power is also part of the borefield load
            heating_load[window], dhw_load[window], cooling_load[window] = \
                available_heating, available_dhw, available_cooling

            # go over all the hours that cross a limit
            hour_in_window = 0
            load_changed = False
            while hour_in_window < window_length:
                remaining = fluid_temperature_reference[hour_in_window:]
                crossing = np.flatnonzero((remaining < Tf_min - tolerance) | (remaining > Tf_max + tolerance))
                if crossing.size == 0:
                    break
                hour_in_window += crossing[0]
                load_changed = True
                hour = window_start + hour_in_window
                power_before = ground_power[hour]
                wall_temperature_without_current_hour = borehole_wall_temperature[hour_in_window] \
                                                        - power_before * first_hour_response
                limit = Tf_min if fluid_temperature_reference[hour_in_window] < Tf_min else Tf_max
                power_on_limit = find_power_on_limit(power_before, wall_temperature_without_current_hour, limit) \
                    if (power_before < 0) == (limit == Tf_min) else None

                # primary (ground) side powers of this hour [W]
                injection = cooling_load[hour] * factor_cooling[hour_in_window] * 1000
                extraction = (heating_load[hour] * factor_heating[hour_in_window]
                              + dhw_load[hour] * factor_dhw[hour_in_window]) * 1000

                if limit == Tf_min:
                    allowed_extraction = 0. if power_on_limit is None else max(0., injection - power_on_limit)
                    reduction_primary = max(0., extraction - allowed_extraction) / 1000  # [kW]
                    reduction_order = ('heating', 'dhw') if dhw_preferential in (True, None) else ('dhw', 'heating')
                    for load_type in reduction_order:
                        if reduction_primary <= 0 or (load_type == 'dhw' and dhw_preferential is None):
                            continue
                        if load_type == 'heating':
                            factor = max(factor_heating[hour_in_window], 1e-9)
                            reduction_secondary = min(heating_load[hour], reduction_primary / factor)
                            heating_load[hour] -= reduction_secondary
                        else:
                            factor = max(factor_dhw[hour_in_window], 1e-9)
                            reduction_secondary = min(dhw_load[hour], reduction_primary / factor)
                            dhw_load[hour] -= reduction_secondary
                        reduction_primary -= reduction_secondary * factor
                else:
                    allowed_injection = 0. if power_on_limit is None else max(0., extraction + power_on_limit)
                    cooling_load[hour] = max(0., cooling_load[hour] - max(0., injection - allowed_injection)
                                             / 1000 / factor_cooling[hour_in_window])

                power_after = (cooling_load[hour] * factor_cooling[hour_in_window]
                               - heating_load[hour] * factor_heating[hour_in_window]
                               - dhw_load[hour] * factor_dhw[hour_in_window]) * 1000
                ground_power[hour] = power_after

                # propagate the change to the remainder of the window (the wall temperature is linear in the load)
                temperature_step = (power_after - power_before) \
                                   * g_value_differences[:window_length - hour_in_window] / g_function_to_temperature
                borehole_wall_temperature[hour_in_window:] += temperature_step
                fluid_temperature_average[hour_in_window + 1:] += temperature_step[1:]
                fluid_temperature_reference[hour_in_window + 1:] += temperature_step[1:]
                fluid_temperature_average[hour_in_window] = borehole_wall_temperature[hour_in_window] + \
                                                            power_after * np.interp(power_after, power_table,
                                                                                    borehole_resistance_table[limit]) \
                                                            / number_of_boreholes / borehole_length
                fluid_temperature_reference[hour_in_window] = calculate_reference_fluid_temperature_single_hour(
                    power_after, borehole_wall_temperature[hour_in_window] - power_after * first_hour_response, limit)
                hour_in_window += 1
            if not load_changed:
                break

        # add the effect of this (now final) window on all later hours
        if window_end < total_length:
            convolution_full = oaconvolve(ground_power[window], g_value_differences[:total_length - window_start])
            convolution_finished_windows[window_end:] += convolution_full[window_length:total_length - window_start]
        fluid_temperature_guess = fluid_temperature_average[-1]

    borefield_load = create_multiyear_load(heating_load, cooling_load, dhw_load)
    external_load = HourlyBuildingLoadMultiYear()
    external_load.set_hourly_heating_load(np.maximum(0, heating_load_original - heating_load))
    external_load.set_hourly_cooling_load(np.maximum(0, cooling_load_original - cooling_load))
    external_load.set_hourly_dhw_load(np.maximum(0, dhw_load_original - dhw_load))

    return borefield_load, external_load
