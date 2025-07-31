import copy
import numpy as np

from math import pi
from typing import Union
from GHEtool.VariableClasses import HourlyBuildingLoad, MonthlyBuildingLoadMultiYear, HourlyBuildingLoadMultiYear, \
    ConstantFluidData, ConstantFlowRate, TemperatureDependentFluidData, EERCombined
from GHEtool.VariableClasses.LoadData.Baseclasses import _LoadDataBuilding


def optimise_load_profile_power(
        borefield,
        building_load: Union[HourlyBuildingLoad, HourlyBuildingLoadMultiYear],
        temperature_threshold: float = 0.05,
        use_hourly_resolution: bool = True,
        max_peak_heating: float = None,
        max_peak_cooling: float = None,
        dhw_preferential: bool = None
) -> tuple[HourlyBuildingLoad, HourlyBuildingLoad]:
    """
    This function optimises the load for maximum power in extraction and injection based on the given borefield and
    the given hourly building load. It does so based on a load-duration curve.

    Parameters
    ----------
    borefield : Borefield
        Borefield object
    building_load : HourlyBuildingLoad | HourlyBuildingLoadMultiYear
        Load data used for the optimisation.
    temperature_threshold : float
        The maximum allowed temperature difference between the maximum and minimum fluid temperatures and their
        respective limits. The lower this threshold, the longer the convergence will take.
    use_hourly_resolution : bool
        If use_hourly_resolution is used, the hourly data will be used for this optimisation. This can take some
        more time than using the monthly resolution, but it will give more accurate results.
    max_peak_heating : float
        The maximum peak power for the heating (building side) [kW]
    max_peak_cooling : float
        The maximum peak power for the cooling (building side) [kW]
    dhw_preferential : bool
        True if heating should first be reduced only after which the dhw share is reduced.
        If it is None, then the dhw profile is not optimised and kept constant.

    Returns
    -------
    tuple [HourlyBuildingLoad, HourlyBuildingLoad]
        borefield load, external load

    Raises
    ------
    ValueError
        ValueError if no correct load data is given or the threshold is negative
    """
    # copy borefield
    borefield = copy.deepcopy(borefield)

    # check if hourly load is given
    if not isinstance(building_load, (HourlyBuildingLoad, HourlyBuildingLoadMultiYear)):
        raise ValueError("The building load should be of the class HourlyBuildingLoad or HourlyBuildingLoadMultiYear!")

    # check if threshold is positive
    if temperature_threshold < 0:
        raise ValueError(f"The temperature threshold is {temperature_threshold}, but it cannot be below 0!")

    # since the depth does not change, the Rb* value is constant, if there is no temperature dependent fluid data
    if isinstance(borefield.borehole.fluid_data, ConstantFluidData) \
            and isinstance(borefield.borehole.flow_data, ConstantFlowRate):
        borefield.Rb = borefield.borehole.get_Rb(borefield.H, borefield.D, borefield.r_b,
                                                 borefield.ground_data.k_s(borefield.depth, borefield.D))

    # set load
    borefield.load = copy.deepcopy(building_load)

    # set initial peak loads
    init_peak_heating: float = borefield.load.max_peak_heating
    init_peak_dhw: float = borefield.load.max_peak_dhw
    init_peak_cooling: float = borefield.load.max_peak_cooling

    # correct for max peak powers
    if max_peak_heating is not None:
        init_peak_heating = min(init_peak_heating, max_peak_heating)
    if max_peak_cooling is not None:
        init_peak_cooling = min(init_peak_cooling, max_peak_cooling)

    # peak loads for iteration
    peak_heat_load: float = init_peak_heating
    peak_dhw_load: float = init_peak_dhw
    peak_cool_load: float = init_peak_cooling

    # set iteration criteria
    cool_ok, heat_ok = False, False
    while not cool_ok or not heat_ok:
        # limit the primary geothermal extraction and injection load to peak_heat_load and peak_cool_load
        borefield.load.set_hourly_cooling_load(
            np.minimum(peak_cool_load, building_load.hourly_cooling_load
            if isinstance(borefield.load, HourlyBuildingLoad) else building_load.hourly_cooling_load_simulation_period))
        borefield.load.set_hourly_heating_load(
            np.minimum(peak_heat_load, building_load.hourly_heating_load
            if isinstance(borefield.load, HourlyBuildingLoad) else building_load.hourly_heating_load_simulation_period))
        borefield.load.set_hourly_dhw_load(
            np.minimum(peak_dhw_load, building_load.hourly_dhw_load
            if isinstance(borefield.load, HourlyBuildingLoad) else building_load.hourly_dhw_load_simulation_period))

        # calculate temperature profile, just for the results
        borefield.calculate_temperatures(length=borefield.H, hourly=use_hourly_resolution)

        # deviation from minimum temperature
        if abs(min(borefield.results.peak_extraction) - borefield.Tf_min) > temperature_threshold:
            # check if it goes below the threshold
            if min(borefield.results.peak_extraction) < borefield.Tf_min:
                if (dhw_preferential and peak_heat_load > 0.1) \
                        or (not dhw_preferential and peak_dhw_load <= 0.1) \
                        or dhw_preferential is None:
                    # first reduce the peak load in heating before touching the dhw load
                    # if dhw_preferential is None, it is not optimised and kept constant
                    peak_heat_load = max(0.1, peak_heat_load - 1 * max(1, 10 * (
                            borefield.Tf_min - min(borefield.results.peak_extraction))))
                else:
                    peak_dhw_load = max(0.1, peak_dhw_load - 1 * max(1, 10 * (
                            borefield.Tf_min - min(borefield.results.peak_extraction))))
                heat_ok = False
            else:
                if (dhw_preferential and peak_heat_load != init_peak_heating) or (
                        not dhw_preferential and 0.1 >= peak_dhw_load) or dhw_preferential is None:
                    peak_heat_load = min(init_peak_heating, peak_heat_load * 1.01)
                else:
                    peak_dhw_load = min(init_peak_dhw, peak_dhw_load * 1.01)
                if peak_heat_load == init_peak_heating and peak_dhw_load == init_peak_dhw:
                    heat_ok = True
        else:
            heat_ok = True

        # deviation from maximum temperature
        if abs(np.max(borefield.results.peak_injection) - borefield.Tf_max) > temperature_threshold:
            # check if it goes above the threshold
            if np.max(borefield.results.peak_injection) > borefield.Tf_max:
                peak_cool_load = max(0.1, peak_cool_load - 1 * max(1, 10 * (
                        -borefield.Tf_max + np.max(borefield.results.peak_injection))))
                cool_ok = False
            else:
                peak_cool_load = min(init_peak_cooling, peak_cool_load * 1.01)
                if peak_cool_load == init_peak_cooling:
                    cool_ok = True
        else:
            cool_ok = True

    # calculate external load
    external_load = HourlyBuildingLoad(simulation_period=building_load.simulation_period)
    external_load.set_hourly_heating_load(
        np.maximum(0, building_load.hourly_heating_load - borefield.load.hourly_heating_load))
    external_load.set_hourly_cooling_load(
        np.maximum(0, building_load.hourly_cooling_load - borefield.load.hourly_cooling_load))
    external_load.set_hourly_dhw_load(
        np.maximum(0, building_load.hourly_dhw_load - borefield.load.hourly_dhw_load))

    return borefield.load, external_load


def optimise_load_profile_energy_old(
        borefield,
        building_load: Union[HourlyBuildingLoad, HourlyBuildingLoadMultiYear],
        temperature_threshold: float = 0.05,
        max_peak_heating: float = None,
        max_peak_cooling: float = None,
) -> tuple[HourlyBuildingLoadMultiYear, HourlyBuildingLoadMultiYear]:
    """
    This function optimises the load for maximum energy extraction and injection based on the given borefield and
    the given hourly building load. It does so by iterating over every month of the simulation period and increasing or
    decreasing the amount of geothermal heating and cooling until it meets the temperature requirements.

    Parameters
    ----------
    borefield : Borefield
        Borefield object
    building_load : HourlyBuildingLoad | HourlyBuildingLoadMultiYear
        Load data used for the optimisation
    temperature_threshold : float
        The maximum allowed temperature difference between the maximum and minimum fluid temperatures and their
        respective limits. The lower this threshold, the longer the convergence will take.
    max_peak_heating : float
        The maximum peak power for heating (building side) [kW]
    max_peak_cooling : float
        The maximum peak power for cooling (building side) [kW]

    Returns
    -------
    tuple [HourlyBuildingLoadMultiYear, HourlyBuildingLoadMultiYear]
        borefield load, external load

    Raises
    ------
    ValueError
        ValueError if no correct load data is given or the threshold is negative
    """
    # copy borefield
    borefield = copy.deepcopy(borefield)

    # check if hourly load is given
    if not isinstance(building_load, (HourlyBuildingLoad, HourlyBuildingLoadMultiYear)):
        raise ValueError("The building load should be of the class HourlyBuildingLoad or HourlyBuildingLoadMultiYear!")

    # check if threshold is positive
    if temperature_threshold < 0:
        raise ValueError(f"The temperature threshold is {temperature_threshold}, but it cannot be below 0!")

    # since the depth does not change, the Rb* value is constant, if there is no temperature dependent fluid data
    if isinstance(borefield.borehole.fluid_data, ConstantFluidData) \
            and isinstance(borefield.borehole.flow_data, ConstantFlowRate):
        borefield.Rb = borefield.borehole.get_Rb(borefield.H, borefield.D, borefield.r_b,
                                                 borefield.ground_data.k_s(borefield.depth, borefield.D))

    building_load_copy = copy.deepcopy(building_load)

    # if building load is not a multi-year load, convert to multiyear
    if isinstance(building_load, HourlyBuildingLoad):
        building_load = HourlyBuildingLoadMultiYear(building_load.hourly_heating_load_simulation_period,
                                                    building_load.hourly_cooling_load_simulation_period,
                                                    building_load._cop,
                                                    building_load._eer,
                                                    building_load.hourly_dhw_load_simulation_period,
                                                    building_load._cop_dhw)

    # set max peak values
    init_peak_heating = building_load.hourly_heating_load_simulation_period.copy()
    init_peak_cooling = building_load.hourly_cooling_load_simulation_period.copy()

    # correct for max peak powers
    if max_peak_heating is not None:
        init_peak_heating = np.clip(init_peak_heating, None, max_peak_heating)
    if max_peak_cooling is not None:
        init_peak_cooling = np.clip(init_peak_cooling, None, max_peak_cooling)

    # update loads
    building_load.hourly_heating_load = init_peak_heating
    building_load.hourly_cooling_load = init_peak_cooling

    # set relation qh-qm
    nb_points = 100

    power_heating_range = np.linspace(0.001, building_load.max_peak_heating, nb_points)
    power_cooling_range = np.linspace(0.001, building_load.max_peak_cooling, nb_points)

    # relationship between the peak load and the corresponding monthly load
    heating_peak_bl = np.zeros((nb_points, 12 * building_load.simulation_period))
    cooling_peak_bl = np.zeros((nb_points, 12 * building_load.simulation_period))

    for idx in range(nb_points):
        heating_peak_bl[idx] = building_load.resample_to_monthly(
            np.minimum(power_heating_range[idx], building_load.hourly_heating_load_simulation_period))[1]
        cooling_peak_bl[idx] = building_load.resample_to_monthly(
            np.minimum(power_cooling_range[idx], building_load.hourly_cooling_load_simulation_period))[1]

    # create monthly multi-load
    monthly_load = \
        MonthlyBuildingLoadMultiYear(
            baseload_heating=building_load.monthly_baseload_heating_simulation_period,
            baseload_cooling=building_load.monthly_baseload_cooling_simulation_period,
            peak_heating=building_load.monthly_peak_heating_simulation_period,
            peak_cooling=building_load.monthly_peak_cooling_simulation_period,
            efficiency_heating=building_load._cop,
            efficiency_cooling=building_load._eer,
            dhw=building_load.monthly_baseload_dhw_simulation_period,
            efficiency_dhw=building_load._cop_dhw)

    monthly_load.exclude_DHW_from_peak = building_load.exclude_DHW_from_peak

    borefield.load = monthly_load

    # store initial monthly peak loads
    peak_heating = copy.copy(monthly_load.monthly_peak_heating_simulation_period)
    peak_cooling = copy.copy(monthly_load.monthly_peak_cooling_simulation_period)

    for i in range(12 * borefield.load.simulation_period):
        # set iteration criteria
        cool_ok, heat_ok = False, False

        while not cool_ok or not heat_ok:
            # calculate temperature profile, just for the results
            borefield.calculate_temperatures(borefield.H)

            # deviation from minimum temperature
            if abs(borefield.results.peak_extraction[i] - borefield.Tf_min) > temperature_threshold:
                # check if it goes below the threshold
                current_heating_peak = borefield.load.monthly_peak_heating_simulation_period[i]
                if borefield.results.peak_extraction[i] < borefield.Tf_min:
                    current_heating_peak = max(0.1, current_heating_peak - 1 * max(1, 10 * (
                            borefield.Tf_min - borefield.results.peak_extraction[i])))
                else:
                    current_heating_peak = min(peak_heating[i], current_heating_peak * 1.01)
                    if current_heating_peak == peak_heating[i]:
                        heat_ok = True
                borefield.load._peak_heating[i], borefield.load._baseload_heating[i] = \
                    current_heating_peak, np.interp(current_heating_peak, power_heating_range, heating_peak_bl[:, i])
            else:
                heat_ok = True

            # deviation from maximum temperature
            if abs(borefield.results.peak_injection[i] - borefield.Tf_max) > temperature_threshold:
                # check if it goes above the threshold
                current_cooling_peak = borefield.load.monthly_peak_cooling_simulation_period[i]
                if borefield.results.peak_injection[i] > borefield.Tf_max:
                    current_cooling_peak = max(0.1, current_cooling_peak - 1 * max(1, 10 * (
                            -borefield.Tf_max + borefield.results.peak_injection[i])))
                else:
                    current_cooling_peak = min(peak_cooling[i], current_cooling_peak * 1.01)
                    if current_cooling_peak == peak_cooling[i]:
                        cool_ok = True
                borefield.load._peak_cooling[i], borefield.load._baseload_cooling[i] = \
                    current_cooling_peak, np.interp(current_cooling_peak, power_cooling_range, cooling_peak_bl[:, i])
            else:
                cool_ok = True

    def f(hourly_load, monthly_peak) -> np.ndarray:
        """
        This function creates a new hourly load where the values are limited by the monthly peaks.

        Parameters
        ----------
        hourly_load : np.ndarray
            An array with hourly values
        monthly_peak : np.ndarray
            An array with monthly values

        Returns
        -------
        np.ndarray
            New array with hourly values where each value is the minimum of the monthly and hourly array
        """
        new_load = np.zeros_like(hourly_load)
        UPM = np.cumsum(np.tile(building_load.UPM, building_load.simulation_period))
        month_idx = 0
        for idx, val in enumerate(hourly_load):
            if idx == UPM[month_idx] and not month_idx == len(UPM) - 1:
                month_idx += 1
            new_load[idx] = min(val, monthly_peak[month_idx])
        return new_load

    # calculate hourly load
    borefield_load = copy.deepcopy(building_load)
    borefield_load.hourly_heating_load = f(building_load.hourly_heating_load_simulation_period,
                                           borefield.load.monthly_peak_heating_simulation_period)
    borefield_load.hourly_cooling_load = f(building_load.hourly_cooling_load_simulation_period,
                                           borefield.load.monthly_peak_cooling_simulation_period)

    # calculate external load
    external_load = HourlyBuildingLoadMultiYear()
    external_load.set_hourly_heating_load(
        np.maximum(0,
                   building_load_copy.hourly_heating_load_simulation_period - borefield_load.hourly_heating_load_simulation_period))
    external_load.set_hourly_cooling_load(
        np.maximum(0,
                   building_load_copy.hourly_cooling_load_simulation_period - borefield_load.hourly_cooling_load_simulation_period))

    return borefield_load, external_load


def optimise_load_profile_energy(
        borefield,
        building_load: Union[HourlyBuildingLoad, HourlyBuildingLoadMultiYear],
        temperature_threshold: float = 0.05,
        max_peak_heating: float = None,
        max_peak_cooling: float = None,
) -> tuple[HourlyBuildingLoadMultiYear, HourlyBuildingLoadMultiYear]:
    """
    This function optimises the load for maximum energy extraction and injection based on the given borefield and
    the given hourly building load. It does so by iterating over every month of the simulation period and increasing or
    decreasing the amount of geothermal heating and cooling until it meets the temperature requirements.

    Parameters
    ----------
    borefield : Borefield
        Borefield object
    building_load : HourlyBuildingLoad | HourlyBuildingLoadMultiYear
        Load data used for the optimisation
    temperature_threshold : float
        The maximum allowed temperature difference between the maximum and minimum fluid temperatures and their
        respective limits. The lower this threshold, the longer the convergence will take.
    max_peak_heating : float
        The maximum peak power for heating (building side) [kW]
    max_peak_cooling : float
        The maximum peak power for cooling (building side) [kW]

    Returns
    -------
    tuple [HourlyBuildingLoadMultiYear, HourlyBuildingLoadMultiYear]
        borefield load, external load

    Raises
    ------
    ValueError
        ValueError if no correct load data is given or the threshold is negative
    """
    # copy borefield
    borefield = copy.deepcopy(borefield)

    # check if hourly load is given
    if not isinstance(building_load, (HourlyBuildingLoad, HourlyBuildingLoadMultiYear)):
        raise ValueError("The building load should be of the class HourlyBuildingLoad or HourlyBuildingLoadMultiYear!")

    # check if threshold is positive
    if temperature_threshold < 0:
        raise ValueError(f"The temperature threshold is {temperature_threshold}, but it cannot be below 0!")

    # since the depth does not change, the Rb* value is constant, if there is no temperature dependent fluid data
    if isinstance(borefield.borehole.fluid_data, ConstantFluidData) \
            and isinstance(borefield.borehole.flow_data, ConstantFlowRate):
        borefield.Rb = borefield.borehole.get_Rb(borefield.H, borefield.D, borefield.r_b,
                                                 borefield.ground_data.k_s(borefield.depth, borefield.D))

    building_load_copy = copy.deepcopy(building_load)

    # if building load is not a multi-year load, convert to multiyear
    if isinstance(building_load, HourlyBuildingLoad):
        building_load = HourlyBuildingLoadMultiYear(building_load.hourly_heating_load_simulation_period,
                                                    building_load.hourly_cooling_load_simulation_period,
                                                    building_load._cop,
                                                    building_load._eer,
                                                    building_load.hourly_dhw_load_simulation_period,
                                                    building_load._cop_dhw)

    # set max peak values
    init_peak_heating = building_load.hourly_heating_load_simulation_period.copy()
    init_peak_cooling = building_load.hourly_cooling_load_simulation_period.copy()

    # correct for max peak powers
    if max_peak_heating is not None:
        init_peak_heating = np.clip(init_peak_heating, None, max_peak_heating)
    if max_peak_cooling is not None:
        init_peak_cooling = np.clip(init_peak_cooling, None, max_peak_cooling)

    # update loads
    building_load.hourly_heating_load = init_peak_heating
    building_load.hourly_cooling_load = init_peak_cooling

    # set relation qh-qm
    nb_points = 100

    power_heating_range = np.linspace(0.001, building_load.max_peak_heating, nb_points)
    power_cooling_range = np.linspace(0.001, building_load.max_peak_cooling, nb_points)

    # relationship between the peak load and the corresponding monthly load
    heating_peak_bl = np.zeros((nb_points, 12 * building_load.simulation_period))
    cooling_peak_bl = np.zeros((nb_points, 12 * building_load.simulation_period))

    for idx in range(nb_points):
        heating_peak_bl[idx] = building_load.resample_to_monthly(
            np.minimum(power_heating_range[idx], building_load.hourly_heating_load_simulation_period))[1]
        cooling_peak_bl[idx] = building_load.resample_to_monthly(
            np.minimum(power_cooling_range[idx], building_load.hourly_cooling_load_simulation_period))[1]

    # create monthly multi-load
    monthly_load = \
        MonthlyBuildingLoadMultiYear(
            baseload_heating=building_load.monthly_baseload_heating_simulation_period,
            baseload_cooling=building_load.monthly_baseload_cooling_simulation_period,
            peak_heating=building_load.monthly_peak_heating_simulation_period,
            peak_cooling=building_load.monthly_peak_cooling_simulation_period,
            efficiency_heating=building_load._cop,
            efficiency_cooling=building_load._eer,
            dhw=building_load.monthly_baseload_dhw_simulation_period,
            efficiency_dhw=building_load._cop_dhw)

    monthly_load.exclude_DHW_from_peak = building_load.exclude_DHW_from_peak

    borefield.load = monthly_load

    # store initial monthly peak loads
    peak_heating = copy.copy(monthly_load.monthly_peak_heating_simulation_period)
    peak_cooling = copy.copy(monthly_load.monthly_peak_cooling_simulation_period)

    # set constants for optimisation
    g_value_peak_injection = borefield.gfunction(borefield.load.peak_injection_duration, borefield.H)[0]
    if borefield.load.peak_injection_duration == borefield.load.peak_extraction_duration:
        g_value_peak_extraction = g_value_peak_injection
    else:
        g_value_peak_extraction = borefield.gfunction(borefield.load.peak_extraction_duration, borefield.H)[0]

    g_value = borefield.gfunction(borefield.load.time_L3, borefield.H)[0]
    k_s = borefield.ground_data.k_s(borefield.calculate_depth(borefield.H, borefield.D), borefield.D)

    def update_last_month(idx, init_load) -> (float, float):
        def calculate(Tmin: float = None, Tmax: float = None, *args):
            if Tmin is None:
                Tmin = borefield.Tf_min
                Tmax = borefield.Tf_max
            Tb = borefield.results.Tb[idx]

            # convert to result
            result = (Tb - borefield._Tg(borefield.H)) * (2 * pi * k_s) * borefield.H * borefield.number_of_boreholes

            # correct result for previous load
            result -= g_value * init_load * 1000

            # calculate new Tb
            result += g_value * borefield.load.monthly_average_injection_power_simulation_period[idx] * 1000
            Tb = result / (2 * pi * k_s) / (borefield.H * borefield.number_of_boreholes) + borefield._Tg(borefield.H)

            # calculate new temperature
            extraction = Tb + \
                         (-borefield.load.monthly_peak_extraction_simulation_period[idx] *
                          (g_value_peak_extraction / (k_s * 2 * pi) + borefield.borehole.get_Rb(borefield.H,
                                                                                                borefield.D,
                                                                                                borefield.r_b,
                                                                                                k_s, borefield.depth,
                                                                                                temperature=Tmin))
                          + borefield.load.monthly_baseload_extraction_power_simulation_period[idx] *
                          (g_value_peak_extraction / (
                                  k_s * 2 * pi))) * 1000 / borefield.number_of_boreholes / borefield.H

            injection = Tb + \
                        (borefield.load.monthly_peak_injection_simulation_period[idx] *
                         (g_value_peak_injection / (k_s * 2 * pi) + borefield.borehole.get_Rb(borefield.H, borefield.D,
                                                                                              borefield.r_b,
                                                                                              k_s, borefield.depth,
                                                                                              temperature=Tmax))
                         - borefield.load.monthly_baseload_injection_power_simulation_period[idx] *
                         (g_value_peak_injection / (k_s * 2 * pi))) * 1000 / borefield.number_of_boreholes / borefield.H
            return extraction, injection, Tb

        # add some iteration for convergence

        if isinstance(borefield.load, _LoadDataBuilding) or \
                isinstance(borefield.borehole.fluid_data, TemperatureDependentFluidData):
            # when building load is given, the load should be updated after each temperature calculation.
            # check if active_passive, because then, threshold should be taken
            if isinstance(borefield.load, _LoadDataBuilding) and \
                    isinstance(borefield.load.eer,
                               EERCombined) and borefield.load.eer.threshold_temperature is not None:
                borefield.load.reset_results(borefield.Tf_min, borefield.load.eer.threshold_temperature)
            else:
                borefield.load.reset_results(borefield.Tf_min, borefield.Tf_max)
            results_old = calculate()
            # set results, but manually
            if borefield.load._results is None:
                borefield.load.set_results(borefield.results)
            borefield.load._results._peak_extraction[idx] = results_old[0]
            borefield.load._results._peak_injection[idx] = results_old[1]
            results = calculate(*results_old)

            # safety
            i = 0

            def calculate_difference(results_old, result_new) -> float:
                return max(
                    np.max(result_new[0] - results_old[0]),
                    np.max(result_new[1] - results_old[1]))

            while calculate_difference(results_old, results) > borefield._calculation_setup.atol \
                    and i < borefield._calculation_setup.max_nb_of_iterations:
                results_old = results
                # set results, but manually
                borefield.load._results._peak_extraction[idx] = results_old[0]
                borefield.load._results._peak_injection[idx] = results_old[1]
                results = calculate(*results_old)
                i += 1
            return results

        return calculate()

    for i in range(12 * borefield.load.simulation_period):
        # set iteration criteria
        borefield.calculate_temperatures(borefield.H)
        # optimise month i
        init_load = borefield.load.monthly_average_injection_power_simulation_period[i]
        cool_ok, heat_ok = False, False

        while not cool_ok or not heat_ok:
            # calculate temperature profile, just for the results
            peak_extraction, peak_injection, _ = update_last_month(i, init_load)

            # deviation from minimum temperature
            if abs(peak_extraction - borefield.Tf_min) > temperature_threshold:
                # check if it goes below the threshold
                current_heating_peak = borefield.load.monthly_peak_heating_simulation_period[i]
                if peak_extraction < borefield.Tf_min:
                    current_heating_peak = max(0.1, current_heating_peak - 1 * max(1, 10 * (
                            borefield.Tf_min - peak_extraction)))
                else:
                    current_heating_peak = min(peak_heating[i], current_heating_peak * 1.01)
                    if current_heating_peak == peak_heating[i]:
                        heat_ok = True
                borefield.load._peak_heating[i], borefield.load._baseload_heating[i] = \
                    current_heating_peak, np.interp(current_heating_peak, power_heating_range, heating_peak_bl[:, i])
            else:
                heat_ok = True

            # deviation from maximum temperature
            if abs(peak_injection - borefield.Tf_max) > temperature_threshold:
                # check if it goes above the threshold
                current_cooling_peak = borefield.load.monthly_peak_cooling_simulation_period[i]
                if peak_injection > borefield.Tf_max:
                    current_cooling_peak = max(0.1, current_cooling_peak - 1 * max(1, 10 * (
                            -borefield.Tf_max + peak_injection)))
                else:
                    current_cooling_peak = min(peak_cooling[i], current_cooling_peak * 1.01)
                    if current_cooling_peak == peak_cooling[i]:
                        cool_ok = True
                borefield.load._peak_cooling[i], borefield.load._baseload_cooling[i] = \
                    current_cooling_peak, np.interp(current_cooling_peak, power_cooling_range, cooling_peak_bl[:, i])
            else:
                cool_ok = True

    def f(hourly_load, monthly_peak) -> np.ndarray:
        """
        This function creates a new hourly load where the values are limited by the monthly peaks.

        Parameters
        ----------
        hourly_load : np.ndarray
            An array with hourly values
        monthly_peak : np.ndarray
            An array with monthly values

        Returns
        -------
        np.ndarray
            New array with hourly values where each value is the minimum of the monthly and hourly array
        """
        new_load = np.zeros_like(hourly_load)
        UPM = np.cumsum(np.tile(building_load.UPM, building_load.simulation_period))
        month_idx = 0
        for idx, val in enumerate(hourly_load):
            if idx == UPM[month_idx] and not month_idx == len(UPM) - 1:
                month_idx += 1
            new_load[idx] = min(val, monthly_peak[month_idx])
        return new_load

    # calculate hourly load
    borefield_load = copy.deepcopy(building_load)
    borefield_load.hourly_heating_load = f(building_load.hourly_heating_load_simulation_period,
                                           borefield.load.monthly_peak_heating_simulation_period)
    borefield_load.hourly_cooling_load = f(building_load.hourly_cooling_load_simulation_period,
                                           borefield.load.monthly_peak_cooling_simulation_period)

    # calculate external load
    external_load = HourlyBuildingLoadMultiYear()
    external_load.set_hourly_heating_load(
        np.maximum(0,
                   building_load_copy.hourly_heating_load_simulation_period - borefield_load.hourly_heating_load_simulation_period))
    external_load.set_hourly_cooling_load(
        np.maximum(0,
                   building_load_copy.hourly_cooling_load_simulation_period - borefield_load.hourly_cooling_load_simulation_period))

    return borefield_load, external_load


def optimise_load_profile_balance(
        borefield,
        building_load: Union[HourlyBuildingLoad, HourlyBuildingLoadMultiYear],
        temperature_threshold: float = 0.05,
        use_hourly_resolution: bool = True,
        max_peak_heating: float = None,
        max_peak_cooling: float = None,
        dhw_preferential: bool = None,
        imbalance_factor: float = 0.01,
) -> tuple[HourlyBuildingLoad, HourlyBuildingLoad]:
    """
    This function optimises the load for maximum power in extraction and injection based on the given borefield and
    the given hourly building load, by maintaining a zero imbalance. It does so based on a load-duration curve.

    Parameters
    ----------
    borefield : Borefield
        Borefield object
    building_load : HourlyBuildingLoad | HourlyBuildingLoadMultiYear
        Load data used for the optimisation.
    temperature_threshold : float
        The maximum allowed temperature difference between the maximum and minimum fluid temperatures and their
        respective limits. The lower this threshold, the longer the convergence will take.
    use_hourly_resolution : bool
        If use_hourly_resolution is used, the hourly data will be used for this optimisation. This can take some
        more time than using the monthly resolution, but it will give more accurate results.
    max_peak_heating : float
        The maximum peak power for the heating (building side) [kW]
    max_peak_cooling : float
        The maximum peak power for the cooling (building side) [kW]
    dhw_preferential : bool
        True if heating should first be reduced only after which the dhw share is reduced.
        If it is None, then the dhw profile is not optimised and kept constant.
    imbalance_factor : float
        Maximum allowed imbalance w.r.t. to the maximum of either the heat injection or extraction.
        It should be given in a range of 0-1. At 1, it converges to the solution for optimise for power.
        
    Returns
    -------
    tuple [HourlyBuildingLoad, HourlyBuildingLoad]
        borefield load, external load

    Raises
    ------
    ValueError
        ValueError if no correct load data is given or the threshold is negative
    """
    # copy borefield
    borefield = copy.deepcopy(borefield)

    # check if hourly load is given
    if not isinstance(building_load, (HourlyBuildingLoad, HourlyBuildingLoadMultiYear)):
        raise ValueError("The building load should be of the class HourlyBuildingLoad or HourlyBuildingLoadMultiYear!")

    # check if threshold is positive
    if temperature_threshold < 0:
        raise ValueError(f"The temperature threshold is {temperature_threshold}, but it cannot be below 0!")

    if imbalance_factor > 1 or imbalance_factor < 0:
        raise ValueError(f"The imbalance factor is {imbalance_factor}, but it should be between 0-1!")

    # since the depth does not change, the Rb* value is constant, if there is no temperature dependent fluid data
    if isinstance(borefield.borehole.fluid_data, ConstantFluidData) \
            and isinstance(borefield.borehole.flow_data, ConstantFlowRate):
        borefield.Rb = borefield.borehole.get_Rb(borefield.H, borefield.D, borefield.r_b,
                                                 borefield.ground_data.k_s(borefield.depth, borefield.D))

    # set load
    borefield.load = copy.deepcopy(building_load)

    # set initial peak loads
    init_peak_heating: float = borefield.load.max_peak_heating
    init_peak_dhw: float = borefield.load.max_peak_dhw
    init_peak_cooling: float = borefield.load.max_peak_cooling

    # correct for max peak powers
    if max_peak_heating is not None:
        init_peak_heating = min(init_peak_heating, max_peak_heating)
    if max_peak_cooling is not None:
        init_peak_cooling = min(init_peak_cooling, max_peak_cooling)

    # peak loads for iteration
    peak_heat_load: float = init_peak_heating
    peak_dhw_load: float = init_peak_dhw
    peak_cool_load: float = init_peak_cooling

    # set iteration criteria
    cool_ok, heat_ok = False, False
    while not cool_ok or not heat_ok:
        # limit the primary geothermal extraction and injection load to peak_heat_load and peak_cool_load
        borefield.load.set_hourly_cooling_load(
            np.minimum(peak_cool_load, building_load.hourly_cooling_load
            if isinstance(borefield.load, HourlyBuildingLoad) else building_load.hourly_cooling_load_simulation_period))
        borefield.load.set_hourly_heating_load(
            np.minimum(peak_heat_load, building_load.hourly_heating_load
            if isinstance(borefield.load, HourlyBuildingLoad) else building_load.hourly_heating_load_simulation_period))
        borefield.load.set_hourly_dhw_load(
            np.minimum(peak_dhw_load, building_load.hourly_dhw_load
            if isinstance(borefield.load, HourlyBuildingLoad) else building_load.hourly_dhw_load_simulation_period))

        # calculate temperature profile, just for the results
        borefield.calculate_temperatures(length=borefield.H, hourly=use_hourly_resolution)

        # calculate relative imbalance
        imbalance = borefield.load.imbalance / np.maximum(borefield.load.yearly_average_injection_load,
                                                          borefield.load.yearly_average_extraction_load)

        # deviation from minimum temperature
        if abs(min(borefield.results.peak_extraction) - borefield.Tf_min) > temperature_threshold or \
                (abs(imbalance) > imbalance_factor and imbalance < 0):
            # check if it goes below the threshold
            if min(borefield.results.peak_extraction) < borefield.Tf_min:
                if (dhw_preferential and peak_heat_load > 0.1) \
                        or (not dhw_preferential and peak_dhw_load <= 0.1) \
                        or dhw_preferential is None:
                    # first reduce the peak load in heating before touching the dhw load
                    # if dhw_preferential is None, it is not optimised and kept constant
                    peak_heat_load = max(0.1, peak_heat_load - 1 * max(1, 10 * (
                            borefield.Tf_min - min(borefield.results.peak_extraction))))
                else:
                    peak_dhw_load = max(0.1, peak_dhw_load - 1 * max(1, 10 * (
                            borefield.Tf_min - min(borefield.results.peak_extraction))))
                heat_ok = False
            else:
                if abs(imbalance) > imbalance_factor and imbalance < 0:
                    # remove imbalance
                    if (dhw_preferential and peak_heat_load > 0.1) \
                            or (not dhw_preferential and peak_dhw_load <= 0.1) \
                            or dhw_preferential is None:
                        # first reduce the peak load in heating before touching the dhw load
                        # if dhw_preferential is None, it is not optimised and kept constant
                        peak_heat_load = peak_heat_load * 0.99
                    else:
                        peak_dhw_load = peak_dhw_load * 0.99
                elif abs(imbalance) > imbalance_factor and imbalance > 0:
                    if (dhw_preferential and peak_heat_load != init_peak_heating) or (
                            not dhw_preferential and 0.1 >= peak_dhw_load) or dhw_preferential is None:
                        peak_heat_load = min(init_peak_heating, peak_heat_load * 1.01)
                    else:
                        peak_dhw_load = min(init_peak_dhw, peak_dhw_load * 1.01)
                    if (peak_heat_load == init_peak_heating and peak_dhw_load == init_peak_dhw) or cool_ok:
                        heat_ok = True
                else:
                    # imbalance small enough
                    heat_ok = True
        else:
            heat_ok = True

        # deviation from maximum temperature
        if abs(np.max(borefield.results.peak_injection) - borefield.Tf_max) > temperature_threshold or \
                (abs(imbalance) > imbalance_factor and imbalance > 0):
            # check if it goes above the threshold
            if np.max(borefield.results.peak_injection) > borefield.Tf_max:
                peak_cool_load = max(0.1, peak_cool_load - 1 * max(1, 10 * (
                        -borefield.Tf_max + np.max(borefield.results.peak_injection))))
                cool_ok = False
            else:
                if abs(imbalance) > imbalance_factor and imbalance > 0:
                    # remove imbalance
                    peak_cool_load = peak_cool_load * 0.99
                elif abs(imbalance) > imbalance_factor and imbalance < 0:
                    peak_cool_load = min(init_peak_cooling, peak_cool_load * 1.01)
                    if peak_cool_load == init_peak_cooling or heat_ok:
                        cool_ok = True
                else:
                    # imbalance is small enough
                    cool_ok = True
        else:
            cool_ok = True

    # calculate external load
    external_load = HourlyBuildingLoad(simulation_period=building_load.simulation_period)
    external_load.set_hourly_heating_load(
        np.maximum(0, building_load.hourly_heating_load - borefield.load.hourly_heating_load))
    external_load.set_hourly_cooling_load(
        np.maximum(0, building_load.hourly_cooling_load - borefield.load.hourly_cooling_load))
    external_load.set_hourly_dhw_load(
        np.maximum(0, building_load.hourly_dhw_load - borefield.load.hourly_dhw_load))

    return borefield.load, external_load
