import copy
import numpy as np

from typing import Tuple
from GHEtool.VariableClasses import HourlyGeothermalLoad, HourlyGeothermalLoadMultiYear, MonthlyGeothermalLoadMultiYear


def optimise_load_profile_power(
        borefield,
        building_load: HourlyGeothermalLoad,
        depth: float = None,
        SCOP: float = 10 ** 6,
        SEER: float = 10 ** 6,
        temperature_threshold: float = 0.05,
        use_hourly_resolution: bool = True,
        max_peak_heating: float = None,
        max_peak_cooling: float = None
) -> tuple[HourlyGeothermalLoad, HourlyGeothermalLoad, HourlyGeothermalLoad]:
    """
    This function optimises the load based on the given borefield and the given hourly load.
    (When the load is not geothermal, the SCOP and SEER are used to convert it to a geothermal load.)
    It does so based on a load-duration curve. The temperatures of the borefield are calculated on a monthly
    basis, even though we have hourly data, for an hourly calculation of the temperatures
    would take a very long time.

    Parameters
    ----------
    borefield : Borefield
        Borefield object
    building_load : _LoadData
        Load data used for the optimisation
    depth : float
        Depth of the boreholes in the borefield [m]
    SCOP : float
        SCOP of the geothermal system (needed to convert hourly building load to geothermal load)
    SEER : float
        SEER of the geothermal system (needed to convert hourly building load to geothermal load)
    temperature_threshold : float
        The maximum allowed temperature difference between the maximum and minimum fluid temperatures and their
        respective limits. The lower this threshold, the longer the convergence will take.
    use_hourly_resolution : bool
        If use_hourly_resolution is used, the hourly data will be used for this optimisation. This can take some
        more time than using the monthly resolution, but it will give more accurate results.
    max_peak_heating : float
        The maximum peak power for geothermal heating [kW]
    max_peak_cooling : float
        The maximum peak power for geothermal cooling [kW]

    Returns
    -------
    tuple [HourlyGeothermalLoad, HourlyGeothermalLoad, HourlyGeothermalLoad]
        borefield load (primary), borefield load (secundary), external load (secundary)

    Raises
    ------
    ValueError
        ValueError if no hourly load is given or the threshold is negative
    """
    # copy borefield
    borefield = copy.deepcopy(borefield)

    # check if hourly load is given
    if not building_load.hourly_resolution:
        raise ValueError("No hourly load was given!")

    # check if threshold is positive
    if temperature_threshold < 0:
        raise ValueError(f"The temperature threshold is {temperature_threshold}, but it cannot be below 0!")

    # set depth
    if depth is None:
        depth = borefield.H

    # since the depth does not change, the Rb* value is constant
    borefield.Rb = borefield.borehole.get_Rb(depth, borefield.D, borefield.r_b, borefield.ground_data.k_s(depth))

    # load hourly extraction and injection load and convert it to geothermal loads
    primary_geothermal_load = HourlyGeothermalLoad(simulation_period=building_load.simulation_period)
    primary_geothermal_load.set_hourly_injection_load(building_load.hourly_injection_load.copy() * (1 + 1 / SEER))
    primary_geothermal_load.set_hourly_extraction_load(building_load.hourly_extraction_load.copy() * (1 - 1 / SCOP))

    # set geothermal load
    borefield.load = copy.deepcopy(primary_geothermal_load)

    # set initial peak loads
    init_peak_extraction: float = borefield.load.max_peak_extraction
    init_peak_injection: float = borefield.load.max_peak_injection

    # correct for max peak powers
    if max_peak_heating is not None:
        init_peak_extraction = min(init_peak_extraction, max_peak_heating * (1 - 1 / SCOP))
    if max_peak_cooling is not None:
        init_peak_injection = min(init_peak_injection, max_peak_cooling * (1 + 1 / SEER))

    # peak loads for iteration
    peak_heat_load_geo: float = init_peak_extraction
    peak_cool_load_geo: float = init_peak_injection

    # set iteration criteria
    cool_ok, heat_ok = False, False
    while not cool_ok or not heat_ok:
        # limit the primary geothermal extraction and injection load to peak_heat_load_geo and peak_cool_load_geo
        borefield.load.set_hourly_injection_load(
            np.minimum(peak_cool_load_geo, primary_geothermal_load.hourly_injection_load))
        borefield.load.set_hourly_extraction_load(
            np.minimum(peak_heat_load_geo, primary_geothermal_load.hourly_extraction_load))

        # calculate temperature profile, just for the results
        borefield.calculate_temperatures(depth=depth, hourly=use_hourly_resolution)

        # deviation from minimum temperature
        if abs(min(borefield.results.peak_extraction) - borefield.Tf_min) > temperature_threshold:
            # check if it goes below the threshold
            if min(borefield.results.peak_extraction) < borefield.Tf_min:
                peak_heat_load_geo = max(0.1, peak_heat_load_geo - 1 * max(1, 10 * (
                        borefield.Tf_min - min(borefield.results.peak_extraction))))
            else:
                peak_heat_load_geo = min(init_peak_extraction, peak_heat_load_geo * 1.01)
                if peak_heat_load_geo == init_peak_extraction:
                    heat_ok = True
        else:
            heat_ok = True

        # deviation from maximum temperature
        if abs(np.max(borefield.results.peak_injection) - borefield.Tf_max) > temperature_threshold:
            # check if it goes above the threshold
            if np.max(borefield.results.peak_injection) > borefield.Tf_max:
                peak_cool_load_geo = max(0.1, peak_cool_load_geo - 1 * max(1, 10 * (
                        -borefield.Tf_max + np.max(borefield.results.peak_injection))))
            else:
                peak_cool_load_geo = min(init_peak_injection, peak_cool_load_geo * 1.01)
                if peak_cool_load_geo == init_peak_injection:
                    cool_ok = True
        else:
            cool_ok = True

    # calculate the resulting secundary hourly profile that can be put on the borefield
    secundary_borefield_load = HourlyGeothermalLoad(simulation_period=building_load.simulation_period)
    secundary_borefield_load.set_hourly_injection_load(borefield.load.hourly_injection_load / (1 + 1 / SEER))
    secundary_borefield_load.set_hourly_extraction_load(borefield.load.hourly_extraction_load / (1 - 1 / SCOP))

    # calculate external load
    external_load = HourlyGeothermalLoad(simulation_period=building_load.simulation_period)
    external_load.set_hourly_extraction_load(
        np.maximum(0, building_load.hourly_extraction_load - secundary_borefield_load.hourly_extraction_load))
    external_load.set_hourly_injection_load(
        np.maximum(0, building_load.hourly_injection_load - secundary_borefield_load.hourly_injection_load))

    return borefield.load, secundary_borefield_load, external_load


def optimise_load_profile_energy(
        borefield,
        building_load: HourlyGeothermalLoad,
        depth: float = None,
        SCOP: float = 10 ** 6,
        SEER: float = 10 ** 6,
        temperature_threshold: float = 0.05,
        max_peak_heating: float = None,
        max_peak_cooling: float = None
) -> tuple[HourlyGeothermalLoadMultiYear, HourlyGeothermalLoadMultiYear, HourlyGeothermalLoadMultiYear]:
    """
    This function optimises the load based on the given borefield and the given hourly load.
    (When the load is not geothermal, the SCOP and SEER are used to convert it to a geothermal load.)
    It does so based on a load-duration curve. The temperatures of the borefield are calculated on a monthly
    basis, even though we have hourly data, for an hourly calculation of the temperatures
    would take a very long time.

    Parameters
    ----------
    borefield : Borefield
        Borefield object
    building_load : _LoadData
        Load data used for the optimisation
    depth : float
        Depth of the boreholes in the borefield [m]
    SCOP : float
        SCOP of the geothermal system (needed to convert hourly building load to geothermal load)
    SEER : float
        SEER of the geothermal system (needed to convert hourly building load to geothermal load)
    temperature_threshold : float
        The maximum allowed temperature difference between the maximum and minimum fluid temperatures and their
        respective limits. The lower this threshold, the longer the convergence will take.
    max_peak_heating : float
        The maximum peak power for geothermal extraction [kW]
    max_peak_cooling : float
        The maximum peak power for geothermal injection [kW]

    Returns
    -------
    tuple [HourlyGeothermalLoad, HourlyGeothermalLoad, HourlyGeothermalLoad]
        borefield load (primary), borefield load (secundary), external load (secundary)

    Raises
    ------
    ValueError
        ValueError if no hourly load is given or the threshold is negative
    """
    # copy borefield
    borefield = copy.deepcopy(borefield)

    # check if hourly load is given
    if not building_load.hourly_resolution:
        raise ValueError("No hourly load was given!")

    # check if threshold is positive
    if temperature_threshold < 0:
        raise ValueError(f"The temperature threshold is {temperature_threshold}, but it cannot be below 0!")

    # set depth
    if depth is None:
        depth = borefield.H

    # since the depth does not change, the Rb* value is constant
    # set to use a constant Rb* value but save the initial parameters
    borefield.Rb = borefield.borehole.get_Rb(depth, borefield.D, borefield.r_b, borefield.ground_data.k_s)

    # set max peak values
    init_peak_extraction = building_load.hourly_extraction_load.copy() * (1 - 1 / SCOP)
    init_peak_injection = building_load.hourly_injection_load.copy() * (1 + 1 / SEER)

    # correct for max peak powers
    if max_peak_heating is not None:
        init_peak_extraction = np.clip(init_peak_extraction, None, max_peak_heating * (1 - 1 / SCOP))
    if max_peak_cooling is not None:
        init_peak_injection = np.clip(init_peak_injection, None, max_peak_cooling * (1 + 1 / SEER))

    # load hourly extraction and injection load and convert it to geothermal loads
    primary_geothermal_load = HourlyGeothermalLoad(simulation_period=building_load.simulation_period)
    primary_geothermal_load.set_hourly_extraction_load(init_peak_extraction)
    primary_geothermal_load.set_hourly_injection_load(init_peak_injection)

    # set relation qh-qm
    nb_points = 100

    power_extraction_range = np.linspace(0.001, primary_geothermal_load.max_peak_extraction, nb_points)
    power_injection_range = np.linspace(0.001, primary_geothermal_load.max_peak_injection, nb_points)

    # relationship between the peak load and the corresponding monthly load
    extraction_peak_bl = np.zeros((nb_points, 12))
    injection_peak_bl = np.zeros((nb_points, 12))

    for idx in range(nb_points):
        extraction_peak_bl[idx] = primary_geothermal_load.resample_to_monthly(
            np.minimum(power_extraction_range[idx], primary_geothermal_load.hourly_extraction_load))[1]
        injection_peak_bl[idx] = primary_geothermal_load.resample_to_monthly(
            np.minimum(power_injection_range[idx], primary_geothermal_load.hourly_injection_load))[1]

    # create monthly multi-load
    primary_monthly_load = \
        MonthlyGeothermalLoadMultiYear(
            baseload_extraction=primary_geothermal_load.monthly_baseload_extraction_simulation_period,
            baseload_injection=primary_geothermal_load.monthly_baseload_injection_simulation_period,
            peak_extraction=primary_geothermal_load.monthly_peak_extraction_simulation_period,
            peak_injection=primary_geothermal_load.monthly_peak_injection_simulation_period)

    borefield.load = primary_monthly_load

    # store initial monthly peak loads
    peak_extraction = primary_geothermal_load.monthly_peak_extraction
    peak_injection = primary_geothermal_load.monthly_peak_injection

    for i in range(12 * borefield.load.simulation_period):
        # set iteration criteria
        cool_ok, heat_ok = False, False

        while not cool_ok or not heat_ok:
            # calculate temperature profile, just for the results
            borefield.calculate_temperatures(depth)

            # deviation from minimum temperature
            if abs(borefield.results.peak_extraction[i] - borefield.Tf_min) > temperature_threshold:
                # check if it goes below the threshold
                curr_extraction_peak = borefield.load.monthly_peak_extraction_simulation_period[i]
                if borefield.results.peak_extraction[i] < borefield.Tf_min:
                    curr_extraction_peak = max(0.1, curr_extraction_peak - 1 * max(1, 10 * (
                            borefield.Tf_min - borefield.results.peak_extraction[i])))
                else:
                    curr_extraction_peak = min(peak_extraction[i % 12], curr_extraction_peak * 1.01)
                    if curr_extraction_peak == peak_extraction[i % 12]:
                        heat_ok = True
                borefield.load._peak_extraction[i], borefield.load._baseload_extraction[i] = \
                    curr_extraction_peak, np.interp(curr_extraction_peak, power_extraction_range,
                                                    extraction_peak_bl[:, i % 12])
            else:
                heat_ok = True

            # deviation from maximum temperature
            if abs(borefield.results.peak_injection[i] - borefield.Tf_max) > temperature_threshold:
                # check if it goes above the threshold
                curr_injection_peak = borefield.load.monthly_peak_injection_simulation_period[i]
                if borefield.results.peak_injection[i] > borefield.Tf_max:
                    curr_injection_peak = max(0.1, curr_injection_peak - 1 * max(1, 10 * (
                            -borefield.Tf_max + borefield.results.peak_injection[i])))
                else:
                    curr_injection_peak = min(peak_injection[i % 12], curr_injection_peak * 1.01)
                    if curr_injection_peak == peak_injection[i % 12]:
                        cool_ok = True
                borefield.load._peak_injection[i], borefield.load._baseload_injection[i] = \
                    curr_injection_peak, np.interp(curr_injection_peak, power_injection_range,
                                                   injection_peak_bl[:, i % 12])
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
    primary_borefield_load = HourlyGeothermalLoadMultiYear()
    primary_borefield_load.hourly_extraction_load = f(primary_geothermal_load.hourly_extraction_load_simulation_period,
                                                      borefield.load.monthly_peak_extraction_simulation_period)
    primary_borefield_load.hourly_injection_load = f(primary_geothermal_load.hourly_injection_load_simulation_period,
                                                     borefield.load.monthly_peak_injection_simulation_period)

    # calculate the corresponding geothermal load
    secundary_borefield_load = HourlyGeothermalLoadMultiYear()
    secundary_borefield_load.hourly_injection_load = primary_borefield_load.hourly_injection_load_simulation_period / (
            1 + 1 / SEER)
    secundary_borefield_load.hourly_extraction_load = primary_borefield_load.hourly_extraction_load_simulation_period / (
            1 - 1 / SCOP)

    # calculate external load
    external_load = HourlyGeothermalLoadMultiYear()
    external_load.hourly_extraction_load = np.maximum(0, building_load.hourly_extraction_load_simulation_period -
                                                      secundary_borefield_load.hourly_extraction_load_simulation_period)
    external_load.hourly_injection_load = np.maximum(0, building_load.hourly_injection_load_simulation_period -
                                                     secundary_borefield_load.hourly_injection_load_simulation_period)

    return primary_borefield_load, secundary_borefield_load, external_load
