import copy
import numpy as np

from typing import Union
from scipy.signal import convolve, oaconvolve

from GHEtool import VariableHourlyFlowRate, VariableHourlyMultiyearFlowRate
from GHEtool.VariableClasses import HourlyBuildingLoad, HourlyBuildingLoadMultiYear, ConstantFluidData, \
    ConstantFlowRate, ConstantDeltaTFlowRate, SCOP, SEER


def _find_root_regula_falsi(error_function, x_violating: float, error_violating: float, x_safe: float,
                            error_safe: float, temperature_threshold: float, max_iterations: int = 50) -> float:
    """
    This function searches the value x for which the error function equals zero, with the Illinois variant of the
    regula falsi method. The error is positive when a temperature limit is crossed and negative when it is respected.
    The error function should be monotone between x_violating and x_safe.

    Parameters
    ----------
    error_function : Callable
        Function that returns the error for a given x [K]
    x_violating : float
        Value for which the limit is crossed (error > 0)
    error_violating : float
        Error at x_violating [K]
    x_safe : float
        Value for which the limit is respected (error < 0)
    error_safe : float
        Error at x_safe [K]
    temperature_threshold : float
        The search stops when the absolute error is below this threshold [K]
    max_iterations : int
        Maximum number of iterations

    Returns
    -------
    float
        Value of x for which the absolute error is below the threshold, or the last value that respects the limit
        if the threshold could not be reached (e.g. because of a jump in the error function)
    """
    last_side_updated = 0
    for _ in range(max_iterations):
        if abs(x_safe - x_violating) <= 1e-9 * max(1., abs(x_safe)):
            # bracket collapsed, so the error function has a jump here
            break  # pragma: no cover
        x = (x_violating * error_safe - x_safe * error_violating) / (error_safe - error_violating)
        error = error_function(x)
        if abs(error) <= temperature_threshold:
            return x
        if error < 0:
            # x respects the limit
            x_safe, error_safe = x, error
            if last_side_updated == -1:
                error_violating /= 2
            last_side_updated = -1
        else:
            x_violating, error_violating = x, error
            if last_side_updated == 1:
                error_safe /= 2
            last_side_updated = 1
    return x_safe  # pragma: no cover


def _get_hourly_building_loads(building_load: Union[HourlyBuildingLoad, HourlyBuildingLoadMultiYear]) -> tuple:
    """
    This function returns the hourly heating, dhw and cooling load in the format in which they are set on the
    building load (one year for an HourlyBuildingLoad, the whole simulation period for an
    HourlyBuildingLoadMultiYear).

    Parameters
    ----------
    building_load : HourlyBuildingLoad | HourlyBuildingLoadMultiYear
        Load data

    Returns
    -------
    tuple
        hourly heating load, hourly dhw load, hourly cooling load [kW] (np.ndarray)
    """
    if isinstance(building_load, HourlyBuildingLoad):
        return building_load._hourly_heating_load, building_load._hourly_dhw_load, building_load._hourly_cooling_load
    return building_load.hourly_heating_load_simulation_period, building_load.hourly_dhw_load_simulation_period, \
        building_load.hourly_cooling_load_simulation_period


def _set_peak_loads(borefield, building_load: Union[HourlyBuildingLoad, HourlyBuildingLoadMultiYear],
                    peak_heat_load: float, peak_dhw_load: float, peak_cool_load: float) -> None:
    """
    This function limits the primary geothermal extraction and injection load of the borefield to the given peaks.

    Parameters
    ----------
    borefield : Borefield
        Borefield object
    building_load : HourlyBuildingLoad | HourlyBuildingLoadMultiYear
        Original (unlimited) load data
    peak_heat_load : float
        Peak power for heating (building side) [kW]
    peak_dhw_load : float
        Peak power for domestic hot water (building side) [kW]
    peak_cool_load : float
        Peak power for cooling (building side) [kW]

    Returns
    -------
    None
    """
    hourly_heating_load, hourly_dhw_load, hourly_cooling_load = _get_hourly_building_loads(building_load)
    borefield.load.set_hourly_cooling_load(np.minimum(peak_cool_load, hourly_cooling_load))
    borefield.load.set_hourly_heating_load(np.minimum(peak_heat_load, hourly_heating_load))
    borefield.load.set_hourly_dhw_load(np.minimum(peak_dhw_load, hourly_dhw_load))


def _calculate_min_max_temperature(borefield, use_hourly_resolution: bool, index_mask: Union[np.ndarray, None]) \
        -> tuple[float, float]:
    """
    This function calculates the temperature profile of the borefield (with the load that is set) and returns the
    minimum and maximum fluid temperature that are compared with the temperature limits.

    Parameters
    ----------
    borefield : Borefield
        Borefield object
    use_hourly_resolution : bool
        True if the hourly temperature profile should be calculated
    index_mask : np.ndarray | None
        Indices of the hours that should be taken into account (None for all)

    Returns
    -------
    tuple [float, float]
        minimum temperature, maximum temperature [°C]
    """
    borefield._calculate_temperature_profile(length=borefield.H, hourly=use_hourly_resolution,
                                             g_values=borefield._temp_results.get('g_values'),  # always the same
                                             g_value_differences=borefield._temp_results.get(
                                                 'g_value_differences'),
                                             first_last_year=isinstance(borefield.load,
                                                                        HourlyBuildingLoad))  # always the same
    if borefield._calculation_setup.size_based_on == 'average':
        return np.min(borefield.results.peak_extraction[index_mask]), np.max(
            borefield.results.peak_injection[index_mask])
    elif borefield._calculation_setup.size_based_on == 'inlet':
        return np.min(borefield.results.peak_extraction_inlet[index_mask]), np.max(
            borefield.results.peak_injection_inlet[index_mask])
    return np.min(borefield.results.peak_extraction_outlet[index_mask]), np.max(
        borefield.results.peak_injection_outlet[index_mask])


def _calculate_external_load(building_load: Union[HourlyBuildingLoad, HourlyBuildingLoadMultiYear],
                             borefield_load: Union[HourlyBuildingLoad, HourlyBuildingLoadMultiYear]) \
        -> Union[HourlyBuildingLoad, HourlyBuildingLoadMultiYear]:
    """
    This function calculates the part of the building load that is not covered by the borefield.

    Parameters
    ----------
    building_load : HourlyBuildingLoad | HourlyBuildingLoadMultiYear
        Original load data
    borefield_load : HourlyBuildingLoad | HourlyBuildingLoadMultiYear
        Load that is covered by the borefield

    Returns
    -------
    HourlyBuildingLoad | HourlyBuildingLoadMultiYear
        External load
    """
    if isinstance(building_load, HourlyBuildingLoad):
        external_load = HourlyBuildingLoad(simulation_period=building_load.simulation_period)
        external_load.start_month = building_load.start_month

        external_load.set_hourly_heating_load(
            np.maximum(0, building_load._hourly_heating_load - borefield_load._hourly_heating_load))
        external_load.set_hourly_cooling_load(
            np.maximum(0, building_load._hourly_cooling_load - borefield_load._hourly_cooling_load))
        external_load.set_hourly_dhw_load(
            np.maximum(0, building_load._hourly_dhw_load - borefield_load._hourly_dhw_load))
        return external_load

    external_load = HourlyBuildingLoadMultiYear()
    external_load.set_hourly_heating_load(
        np.maximum(0,
                   building_load.hourly_heating_load_simulation_period - borefield_load.hourly_heating_load_simulation_period))
    external_load.set_hourly_cooling_load(
        np.maximum(0,
                   building_load.hourly_cooling_load_simulation_period - borefield_load.hourly_cooling_load_simulation_period))
    external_load.set_hourly_dhw_load(
        np.maximum(0,
                   building_load.hourly_dhw_load_simulation_period - borefield_load.hourly_dhw_load_simulation_period))
    return external_load


def optimise_load_profile_power(
        borefield,
        building_load: Union[HourlyBuildingLoad, HourlyBuildingLoadMultiYear],
        temperature_threshold: float = 0.05,
        use_hourly_resolution: bool = True,
        max_peak_heating: float = None,
        max_peak_cooling: float = None,
        max_peak_dhw: float = None,
        dhw_preferential: bool = None,
        max_nb_of_sweeps: int = 20
) -> tuple[
    Union[HourlyBuildingLoad, HourlyBuildingLoadMultiYear], Union[HourlyBuildingLoad, HourlyBuildingLoadMultiYear]]:
    """
    This function optimises the load for maximum power in extraction and injection based on the given borefield and
    the given hourly building load. It does so based on a load-duration curve.

    The minimum fluid temperature decreases monotonically with the heating (and dhw) peak and the maximum fluid
    temperature increases monotonically with the cooling peak. Therefore, the heating peak (for a fixed cooling peak)
    and the cooling peak (for a fixed heating peak) are each found with the Illinois variant of the regula falsi
    method. Since a lower heating peak increases the maximum temperature and a lower cooling peak decreases the
    minimum temperature, both peaks only decrease from one sweep to the next, so alternating between both converges
    to the largest peaks that respect both limits (typically in 2-3 sweeps).

    Heating and dhw are combined in a single heating reduction, which first lowers the peak of one of them and then
    the peak of the other one (depending on dhw_preferential).

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
    max_peak_dhw : float
        The maximum peak power for the domestic hot water (building side) [kW]
    dhw_preferential : bool
        True if heating should first be reduced only after which the dhw share is reduced.
        False if dhw should first be reduced only after which the heating share is reduced.
        If it is None, then the dhw profile is not optimised and kept constant.
    max_nb_of_sweeps : int
        Maximum number of times the heating and cooling peak are optimised one after the other.

    Returns
    -------
    tuple [HourlyBuildingLoad, HourlyBuildingLoad] or tuple [HourlyBuildingLoadMultiYear, HourlyBuildingLoadMultiYear]
        borefield load, external load

    Raises
    ------
    ValueError
        ValueError if no correct load data is given or the threshold is negative
    """
    # copy borefield
    borefield = copy.deepcopy(borefield)

    # check if hourly flow rate is given and the temperature profile is monthly
    if (not use_hourly_resolution and not borefield.borehole.use_constant_Rb and
            isinstance(borefield.borehole.flow_data, (VariableHourlyFlowRate, VariableHourlyMultiyearFlowRate))):
        raise ValueError('No monthly resolution can be used when working with an hourly flow rate.')

    # check if hourly load is given
    if not isinstance(building_load, (HourlyBuildingLoad, HourlyBuildingLoadMultiYear)):
        raise ValueError("The building load should be of the class HourlyBuildingLoad or HourlyBuildingLoadMultiYear!")

    # check if threshold is positive
    if temperature_threshold < 0:
        raise ValueError(f"The temperature threshold is {temperature_threshold}, but it cannot be below 0!")

    # since the depth does not change, the Rb* value is constant, if there is no temperature dependent fluid data
    if isinstance(borefield.borehole.fluid_data, ConstantFluidData) \
            and isinstance(borefield.borehole.flow_data,
                           ConstantFlowRate) and borefield._calculation_setup.size_based_on == 'average':
        borefield.Rb = borefield.borehole.get_Rb(borefield.H, borefield.D, borefield.r_b,
                                                 borefield.ground_data.k_s(borefield.depth, borefield.D),
                                                 nb_of_boreholes=borefield.number_of_boreholes)

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
    if max_peak_dhw is not None:
        init_peak_dhw = min(init_peak_dhw, max_peak_dhw)

    # lowest peak loads (0.1 kW, or less if the initial peak is already lower)
    min_peak_heating, min_peak_dhw, min_peak_cooling = \
        min(0.1, init_peak_heating), min(0.1, init_peak_dhw), min(0.1, init_peak_cooling)
    range_heating, range_dhw = init_peak_heating - min_peak_heating, init_peak_dhw - min_peak_dhw
    max_heating_reduction = range_heating if dhw_preferential is None else range_heating + range_dhw

    n_hours = borefield.load.simulation_period * 8760
    if isinstance(borefield.load, HourlyBuildingLoad) and use_hourly_resolution:
        index_mask = np.concatenate([np.arange(8760), np.arange(n_hours - 8760, n_hours)])
    else:
        index_mask = None

    def get_heating_peaks(heating_reduction: float) -> tuple[float, float]:
        """
        This function converts the heating reduction into the peak load for heating and for dhw.

        Parameters
        ----------
        heating_reduction : float
            Total reduction of the heating and dhw peak w.r.t. their initial peaks [kW]

        Returns
        -------
        tuple [float, float]
            peak heating load, peak dhw load [kW]
        """
        heating_reduction = min(max(heating_reduction, 0.), max_heating_reduction)
        if dhw_preferential is None:
            # dhw is not optimised
            return init_peak_heating - heating_reduction, init_peak_dhw
        if dhw_preferential:
            # first reduce the peak load in heating before touching the dhw load
            return max(min_peak_heating, init_peak_heating - heating_reduction), \
                max(min_peak_dhw, init_peak_dhw - max(0., heating_reduction - range_heating))
        # first reduce the peak load in dhw before touching the heating load
        return max(min_peak_heating, init_peak_heating - max(0., heating_reduction - range_dhw)), \
            max(min_peak_dhw, init_peak_dhw - heating_reduction)

    calculated_temperatures = {}

    def calculate_temperatures(heating_reduction: float, peak_cool_load: float) -> tuple[float, float]:
        """
        This function calculates the minimum and maximum fluid temperature for a given heating reduction and
        cooling peak. Results are stored, so a combination is never calculated twice.

        Parameters
        ----------
        heating_reduction : float
            Total reduction of the heating and dhw peak [kW]
        peak_cool_load : float
            Peak load for cooling [kW]

        Returns
        -------
        tuple [float, float]
            minimum temperature, maximum temperature [°C]
        """
        key = (heating_reduction, peak_cool_load)
        if key not in calculated_temperatures:
            _set_peak_loads(borefield, building_load, *get_heating_peaks(heating_reduction), peak_cool_load)
            calculated_temperatures[key] = _calculate_min_max_temperature(borefield, use_hourly_resolution,
                                                                          index_mask)
        return calculated_temperatures[key]

    def calculate_error_heating(heating_reduction: float, peak_cool_load: float) -> float:
        # positive if the minimum temperature is below its limit
        return borefield.Tf_min - calculate_temperatures(heating_reduction, peak_cool_load)[0]

    def calculate_error_cooling(peak_cool_load: float, heating_reduction: float) -> float:
        # positive if the maximum temperature is above its limit
        return calculate_temperatures(heating_reduction, peak_cool_load)[1] - borefield.Tf_max

    def optimise_heating(heating_reduction: float, peak_cool_load: float) -> float:
        """
        This function searches the smallest heating reduction (for a given cooling peak) for which the minimum
        temperature does not cross its limit. Since the cooling peak only decreases during the optimisation,
        the previous heating reduction is a lower bound.

        Parameters
        ----------
        heating_reduction : float
            Heating reduction from the previous sweep [kW]
        peak_cool_load : float
            Peak load for cooling [kW]

        Returns
        -------
        float
            Heating reduction [kW]
        """
        error = calculate_error_heating(heating_reduction, peak_cool_load)
        if error <= temperature_threshold:
            return heating_reduction
        error_max_reduction = calculate_error_heating(max_heating_reduction, peak_cool_load)
        if error_max_reduction >= -temperature_threshold:
            # the limit can only (or not even) be met with the lowest heating peak
            return max_heating_reduction  # pragma: no cover
        return _find_root_regula_falsi(lambda x: calculate_error_heating(x, peak_cool_load),
                                       heating_reduction, error, max_heating_reduction, error_max_reduction,
                                       temperature_threshold)

    def optimise_cooling(peak_cool_load: float, heating_reduction: float) -> float:
        """
        This function searches the largest cooling peak (for a given heating reduction) for which the maximum
        temperature does not cross its limit. Since the heating reduction only increases during the optimisation,
        the previous cooling peak is an upper bound.

        Parameters
        ----------
        peak_cool_load : float
            Cooling peak from the previous sweep [kW]
        heating_reduction : float
            Total reduction of the heating and dhw peak [kW]

        Returns
        -------
        float
            Peak load for cooling [kW]
        """
        error = calculate_error_cooling(peak_cool_load, heating_reduction)
        if error <= temperature_threshold:
            return peak_cool_load
        error_min_peak = calculate_error_cooling(min_peak_cooling, heating_reduction)
        if error_min_peak >= -temperature_threshold:
            # the limit can only (or not even) be met with the lowest cooling peak
            return min_peak_cooling  # pragma: no cover
        return _find_root_regula_falsi(lambda x: calculate_error_cooling(x, heating_reduction),
                                       peak_cool_load, error, min_peak_cooling, error_min_peak,
                                       temperature_threshold)

    # peak loads for iteration
    heating_reduction: float = 0.
    peak_cool_load: float = init_peak_cooling
    for _ in range(max_nb_of_sweeps):
        new_heating_reduction = optimise_heating(heating_reduction, peak_cool_load)
        new_peak_cool_load = optimise_cooling(peak_cool_load, new_heating_reduction)
        converged = new_heating_reduction == heating_reduction and new_peak_cool_load == peak_cool_load
        heating_reduction, peak_cool_load = new_heating_reduction, new_peak_cool_load
        if converged:
            break

    # set the final load
    peak_heat_load, peak_dhw_load = get_heating_peaks(heating_reduction)
    _set_peak_loads(borefield, building_load, peak_heat_load, peak_dhw_load, peak_cool_load)

    return borefield.load, _calculate_external_load(building_load, borefield.load)


def _create_load_duration_curve(hourly_load: np.ndarray) -> tuple:
    """
    This function creates two functions based on the load-duration curve of an hourly load: one that returns the
    energy of the load when it is limited to a certain peak, and one that returns the peak that corresponds to a
    certain energy. Both relations are piecewise linear, so the results are exact.

    Parameters
    ----------
    hourly_load : np.ndarray
        Hourly load [kW]

    Returns
    -------
    tuple
        calculate_energy(peak) [kWh], calculate_peak(energy) [kW]
    """
    sorted_load = np.sort(np.asarray(hourly_load, dtype=float))
    number_of_hours = len(sorted_load)
    if number_of_hours == 0 or sorted_load[-1] <= 0:
        return lambda peak: 0., lambda energy: 0.
    # energy at the peaks equal to the sorted hourly values (including the point (0, 0))
    peaks = np.concatenate(([0.], sorted_load))
    energies = np.concatenate(([0.], np.cumsum(sorted_load) - sorted_load
                               + sorted_load * (number_of_hours - np.arange(number_of_hours))))

    def calculate_energy(peak: float) -> float:
        return float(np.interp(peak, peaks, energies))

    def calculate_peak(energy: float) -> float:
        return float(np.interp(energy, energies, peaks))

    return calculate_energy, calculate_peak


def optimise_load_profile_balance(
        borefield,
        building_load: Union[HourlyBuildingLoad, HourlyBuildingLoadMultiYear],
        temperature_threshold: float = 0.05,
        use_hourly_resolution: bool = True,
        max_peak_heating: float = None,
        max_peak_cooling: float = None,
        max_peak_dhw: float = None,
        dhw_preferential: bool = None,
        imbalance_factor: float = 0.01,
        max_nb_of_iterations: int = 10
) -> tuple[
    Union[HourlyBuildingLoad, HourlyBuildingLoadMultiYear], Union[HourlyBuildingLoad, HourlyBuildingLoadMultiYear]]:
    """
    This function optimises the load for maximum power in extraction and injection based on the given borefield and
    the given hourly building load, by maintaining a zero imbalance. It does so based on a load-duration curve.

    The imbalance does not depend on the temperatures (for constant efficiencies), and the energy of a load that is
    limited to a certain peak follows exactly from its load-duration curve. Therefore, all combinations of peaks
    with the allowed imbalance lie on a single curve, which is described by one energy level: the side (injection
    or extraction) with the smallest initial energy gets this level and the other side gets this level divided by
    (1 - imbalance_factor), i.e. the edge of the allowed imbalance. Along this curve, the temperatures only get worse
    with a higher level, so the largest level for which both temperature limits are respected is found with the
    Illinois variant of the regula falsi method.

    With temperature dependent efficiencies, the conversion from the building load to the ground load is first
    estimated with the efficiencies of the previous calculation, after which the curve is updated and solved again
    until the imbalance is within the allowed range.

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
    max_peak_dhw : float
        The maximum peak power for the domestic hot water (building side) [kW]
    dhw_preferential : bool
        True if heating should first be reduced only after which the dhw share is reduced.
        False if dhw should first be reduced only after which the heating share is reduced.
        If it is None, then the dhw profile is not optimised and kept constant.
    imbalance_factor : float
        Maximum allowed imbalance w.r.t. to the maximum of either the heat injection or extraction.
        It should be given in a range of 0-1. At 1, it converges to the solution for optimise for power.
    max_nb_of_iterations : int
        Maximum number of times the curve is updated for temperature dependent efficiencies.

    Returns
    -------
    tuple [HourlyBuildingLoad, HourlyBuildingLoad] or tuple [HourlyBuildingLoadMultiYear, HourlyBuildingLoadMultiYear]
        borefield load, external load

    Raises
    ------
    ValueError
        ValueError if no correct load data is given or the threshold is negative
    """
    # check if hourly flow rate is given and the temperature profile is monthly
    if (not use_hourly_resolution and not borefield.borehole.use_constant_Rb and
            isinstance(borefield.borehole.flow_data, (VariableHourlyFlowRate, VariableHourlyMultiyearFlowRate))):
        raise ValueError('No monthly resolution can be used when working with an hourly flow rate.')

    # check if hourly load is given
    if not isinstance(building_load, (HourlyBuildingLoad, HourlyBuildingLoadMultiYear)):
        raise ValueError("The building load should be of the class HourlyBuildingLoad or HourlyBuildingLoadMultiYear!")

    # check if threshold is positive
    if temperature_threshold < 0:
        raise ValueError(f"The temperature threshold is {temperature_threshold}, but it cannot be below 0!")

    if imbalance_factor > 1 or imbalance_factor < 0:
        raise ValueError(f"The imbalance factor is {imbalance_factor}, but it should be between 0-1!")

    if imbalance_factor == 1:
        # no constraint on the imbalance, so this is the same as optimising for power
        return optimise_load_profile_power(borefield, building_load, temperature_threshold, use_hourly_resolution,
                                           max_peak_heating, max_peak_cooling, max_peak_dhw,
                                           dhw_preferential=dhw_preferential)

    # copy borefield
    borefield = copy.deepcopy(borefield)

    # since the depth does not change, the Rb* value is constant, if there is no temperature dependent fluid data
    if isinstance(borefield.borehole.fluid_data, ConstantFluidData) \
            and isinstance(borefield.borehole.flow_data,
                           ConstantFlowRate) and borefield._calculation_setup.size_based_on == 'average':
        borefield.Rb = borefield.borehole.get_Rb(borefield.H, borefield.D, borefield.r_b,
                                                 borefield.ground_data.k_s(borefield.depth, borefield.D),
                                                 nb_of_boreholes=borefield.number_of_boreholes)

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
    if max_peak_dhw is not None:
        init_peak_dhw = min(init_peak_dhw, max_peak_dhw)

    # lowest peak loads (0.1 kW, or less if the initial peak is already lower)
    min_peak_heating, min_peak_dhw, min_peak_cooling = \
        min(0.1, init_peak_heating), min(0.1, init_peak_dhw), min(0.1, init_peak_cooling)

    n_hours = borefield.load.simulation_period * 8760
    if isinstance(borefield.load, HourlyBuildingLoad) and use_hourly_resolution:
        index_mask = np.concatenate([np.arange(8760), np.arange(n_hours - 8760, n_hours)])
    else:
        index_mask = None

    # load-duration curves of the building load
    hourly_heating_load, hourly_dhw_load, hourly_cooling_load = _get_hourly_building_loads(building_load)
    calculate_energy_heating, calculate_peak_heating = _create_load_duration_curve(hourly_heating_load)
    calculate_energy_dhw, calculate_peak_dhw = _create_load_duration_curve(hourly_dhw_load)
    calculate_energy_cooling, calculate_peak_cooling = _create_load_duration_curve(hourly_cooling_load)

    # factors to convert the secondary (building) energy to the primary (ground) energy
    load = borefield.load
    constant_efficiency = isinstance(load.cop, SCOP) and isinstance(load.cop_dhw, SCOP) and isinstance(load.eer, SEER)
    if constant_efficiency:
        factor_heating = load.conversion_factor_secondary_to_primary_heating(load.cop.SCOP)
        factor_dhw = load.conversion_factor_secondary_to_primary_heating(load.cop_dhw.SCOP)
        factor_cooling = load.conversion_factor_secondary_to_primary_cooling(load.eer.SEER)
    else:
        # estimated after the first temperature calculation
        factor_heating, factor_dhw, factor_cooling = 1., 1., 1.

    calculated_temperatures = {}

    def calculate_temperatures(peak_heat_load: float, peak_dhw_load: float, peak_cool_load: float) -> tuple:
        """
        This function calculates the minimum and maximum fluid temperature for the given peaks, together with the
        relative imbalance and the conversion factors from building to ground energy (for temperature dependent
        efficiencies). Results are stored, so a combination is never calculated twice.

        Parameters
        ----------
        peak_heat_load : float
            Peak load for heating [kW]
        peak_dhw_load : float
            Peak load for dhw [kW]
        peak_cool_load : float
            Peak load for cooling [kW]

        Returns
        -------
        tuple
            minimum temperature [°C], maximum temperature [°C], relative imbalance [-],
            extraction factor [-], injection factor [-]
        """
        key = (peak_heat_load, peak_dhw_load, peak_cool_load)
        if key not in calculated_temperatures:
            _set_peak_loads(borefield, building_load, peak_heat_load, peak_dhw_load, peak_cool_load)
            min_temperature, max_temperature = _calculate_min_max_temperature(borefield, use_hourly_resolution,
                                                                              index_mask)
            # calculate relative imbalance
            imbalance = borefield.load.imbalance / max(np.maximum(borefield.load.yearly_average_injection_load,
                                                                  borefield.load.yearly_average_extraction_load),
                                                       1e-12)
            factor_extraction_effective, factor_injection_effective = None, None
            if not constant_efficiency:
                building_heating = np.sum(borefield.load.hourly_heating_load_simulation_period) \
                                   + np.sum(borefield.load.hourly_dhw_load_simulation_period)
                building_cooling = np.sum(borefield.load.hourly_cooling_load_simulation_period)
                if building_heating > 0:
                    factor_extraction_effective = np.sum(
                        borefield.load.hourly_extraction_load_simulation_period) / building_heating
                if building_cooling > 0:
                    factor_injection_effective = np.sum(
                        borefield.load.hourly_injection_load_simulation_period) / building_cooling
            calculated_temperatures[key] = (min_temperature, max_temperature, imbalance,
                                            factor_extraction_effective, factor_injection_effective)
        return calculated_temperatures[key]

    def calculate_extraction_energy(peak_heat_load: float, peak_dhw_load: float) -> float:
        # primary extraction energy [kWh]
        return factor_heating * calculate_energy_heating(peak_heat_load) \
            + factor_dhw * calculate_energy_dhw(peak_dhw_load)

    def calculate_injection_energy(peak_cool_load: float) -> float:
        # primary injection energy [kWh]
        return factor_cooling * calculate_energy_cooling(peak_cool_load)

    def get_heating_peaks(extraction_energy: float) -> tuple[float, float]:
        """
        This function calculates the peak load for heating and dhw that corresponds to a certain extraction energy,
        taking into account the order in which heating and dhw are reduced.

        Parameters
        ----------
        extraction_energy : float
            Primary extraction energy [kWh]

        Returns
        -------
        tuple [float, float]
            peak heating load, peak dhw load [kW]
        """
        if dhw_preferential is None:
            # dhw is not optimised
            energy_heating = (extraction_energy - factor_dhw * calculate_energy_dhw(init_peak_dhw)) \
                             / max(factor_heating, 1e-9)
            return min(init_peak_heating, max(min_peak_heating, calculate_peak_heating(energy_heating))), \
                init_peak_dhw
        if dhw_preferential:
            # first reduce the peak load in heating before touching the dhw load
            energy_dhw_full = factor_dhw * calculate_energy_dhw(init_peak_dhw)
            if extraction_energy >= factor_heating * calculate_energy_heating(min_peak_heating) + energy_dhw_full:
                energy_heating = (extraction_energy - energy_dhw_full) / max(factor_heating, 1e-9)
                return min(init_peak_heating, max(min_peak_heating, calculate_peak_heating(energy_heating))), \
                    init_peak_dhw
            energy_dhw = (extraction_energy - factor_heating * calculate_energy_heating(min_peak_heating)) \
                         / max(factor_dhw, 1e-9)
            return min_peak_heating, min(init_peak_dhw, max(min_peak_dhw, calculate_peak_dhw(energy_dhw)))
        # first reduce the peak load in dhw before touching the heating load
        energy_heating_full = factor_heating * calculate_energy_heating(init_peak_heating)
        if extraction_energy >= factor_dhw * calculate_energy_dhw(min_peak_dhw) + energy_heating_full:
            energy_dhw = (extraction_energy - energy_heating_full) / max(factor_dhw, 1e-9)
            return init_peak_heating, min(init_peak_dhw, max(min_peak_dhw, calculate_peak_dhw(energy_dhw)))
        energy_heating = (extraction_energy - factor_dhw * calculate_energy_dhw(min_peak_dhw)) \
                         / max(factor_heating, 1e-9)
        return min(init_peak_heating, max(min_peak_heating, calculate_peak_heating(energy_heating))), min_peak_dhw

    def get_cooling_peak(injection_energy: float) -> float:
        # peak load for cooling that corresponds to a certain injection energy [kW]
        return min(init_peak_cooling, max(min_peak_cooling,
                                          calculate_peak_cooling(injection_energy / max(factor_cooling, 1e-9))))

    def get_peaks_on_balance_curve(energy_level: float) -> tuple[float, float, float]:
        """
        This function returns the peaks on the curve with the allowed imbalance for a certain energy level.

        Parameters
        ----------
        energy_level : float
            Energy level, i.e. the primary energy of the side with the smallest initial energy [kWh]

        Returns
        -------
        tuple [float, float, float]
            peak heating load, peak dhw load, peak cooling load [kW]
        """
        if max_injection_energy >= max_extraction_energy:
            # injection dominated, so the injection can be slightly larger than the extraction
            injection_energy = min(max_injection_energy, energy_level / (1 - imbalance_factor))
            extraction_energy = min(max_extraction_energy, energy_level)
        else:
            injection_energy = min(max_injection_energy, energy_level)
            extraction_energy = min(max_extraction_energy, energy_level / (1 - imbalance_factor))
        return *get_heating_peaks(extraction_energy), get_cooling_peak(injection_energy)

    def calculate_error(energy_level: float) -> float:
        # positive if one of the temperature limits is crossed
        min_temperature, max_temperature, *_ = calculate_temperatures(*get_peaks_on_balance_curve(energy_level))
        return max(borefield.Tf_min - min_temperature, max_temperature - borefield.Tf_max)

    if not constant_efficiency:
        # estimate the conversion factors with the initial load
        _, _, _, factor_extraction_effective, factor_injection_effective = \
            calculate_temperatures(init_peak_heating, init_peak_dhw, init_peak_cooling)
        factor_heating = factor_dhw = factor_extraction_effective or factor_heating
        factor_cooling = factor_injection_effective or factor_cooling

    energy_level = 0.
    for _ in range(max_nb_of_iterations if not constant_efficiency else 1):
        max_extraction_energy = calculate_extraction_energy(init_peak_heating, init_peak_dhw)
        max_injection_energy = calculate_injection_energy(init_peak_cooling)
        max_energy_level = min(max_extraction_energy, max_injection_energy)

        error = calculate_error(max_energy_level)
        if error <= temperature_threshold:
            energy_level = max_energy_level
        else:
            error_min_level = calculate_error(0.)
            if error_min_level >= -temperature_threshold:
                # the limits can only (or not even) be met with the lowest peaks
                energy_level = 0.  # pragma: no cover
            else:
                energy_level = _find_root_regula_falsi(calculate_error, max_energy_level, error, 0.,
                                                       error_min_level, temperature_threshold)

        if constant_efficiency:
            break
        # check the imbalance with the temperature dependent efficiencies and update the conversion factors
        _, _, imbalance, factor_extraction_effective, factor_injection_effective = \
            calculate_temperatures(*get_peaks_on_balance_curve(energy_level))
        if abs(imbalance) <= imbalance_factor + 1e-6 or energy_level == 0.:
            break
        factor_heating = factor_dhw = factor_extraction_effective or factor_heating  # pragma: no cover
        factor_cooling = factor_injection_effective or factor_cooling  # pragma: no cover

    # set the final load
    peak_heat_load, peak_dhw_load, peak_cool_load = get_peaks_on_balance_curve(energy_level)
    _set_peak_loads(borefield, building_load, peak_heat_load, peak_dhw_load, peak_cool_load)

    return borefield.load, _calculate_external_load(building_load, borefield.load)


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
        if limit_to_max_heat_pump_power:  # pragma: no cover
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
                    error_violating /= 2  # pragma: no cover
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
