import copy
import numpy as np

from typing import Union
from GHEtool.VariableClasses import HourlyBuildingLoad, MonthlyBuildingLoadMultiYear, HourlyBuildingLoadMultiYear


def optimise_load_profile_power(
        borefield,
        building_load: Union[HourlyBuildingLoad, HourlyBuildingLoadMultiYear],
        temperature_threshold: float = 0.05,
        use_hourly_resolution: bool = True,
        max_peak_heating: float = None,
        max_peak_cooling: float = None,
) -> tuple[HourlyBuildingLoad, HourlyBuildingLoad]:
    """
    This function optimises the load for maximum power in extraction and injection based on the given borefield and
    the given hourly building load. It does so based on a load-duration curve.
    The temperatures of the borefield are calculated on a monthly basis, even though we have hourly data,
    for an hourly calculation of the temperatures would take a very long time.

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

    # since the depth does not change, the Rb* value is constant
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
                peak_heat_load = max(0.1, peak_heat_load - 1 * max(1, 10 * (
                        borefield.Tf_min - min(borefield.results.peak_extraction))))
            else:
                peak_heat_load = min(init_peak_heating, peak_heat_load * 1.01)
                if peak_heat_load == init_peak_heating:
                    heat_ok = True
        else:
            heat_ok = True

        # deviation from maximum temperature
        if abs(np.max(borefield.results.peak_injection) - borefield.Tf_max) > temperature_threshold:
            # check if it goes above the threshold
            if np.max(borefield.results.peak_injection) > borefield.Tf_max:
                peak_cool_load = max(0.1, peak_cool_load - 1 * max(1, 10 * (
                        -borefield.Tf_max + np.max(borefield.results.peak_injection))))
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


def optimise_load_profile_energy(
        borefield,
        building_load: Union[HourlyBuildingLoad, HourlyBuildingLoadMultiYear],
        temperature_threshold: float = 0.05,
        max_peak_heating: float = None,
        max_peak_cooling: float = None
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

    # since the depth does not change, the Rb* value is constant
    # set to use a constant Rb* value but save the initial parameters
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
