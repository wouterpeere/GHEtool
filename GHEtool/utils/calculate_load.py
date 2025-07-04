"""
This file contains the code to calculate the borefield load from a building load if there are other technologies
available. Based on a temperature threshold with the environment, these hybrid solutions will be used first after which
the borefield load is computed.
"""
import copy

import numpy as np
import pandas as pd

from GHEtool.VariableClasses.LoadData import HourlyBuildingLoad, HourlyBuildingLoadMultiYear
from typing import Union


def calculate_load(weather_file, load_data: Union[HourlyBuildingLoad, HourlyBuildingLoadMultiYear],
                   max_peak_heating_borefield: float = None, max_peak_cooling_borefield: float = None,
                   max_peak_heating_top: float = None, max_peak_heating_bottom: float = None,
                   max_peak_cooling_top: float = None, max_peak_cooling_bottom: float = None,
                   threshold_heating_top: float = None, threshold_heating_bottom: float = None,
                   threshold_cooling_top: float = None, threshold_cooling_bottom: float = None):
    """
    This function calculates the resulting borefield load given hybrid solutions that take away part of the heating
    and cooling demand based on temperature thresholds.

    Parameters
    ----------
    weather_file : epw file
        EnergyPlus weather file
    load_data : HourlyBuildingLoad or HourlyBuildingLoadMultiYear
        GHEtool hourly building load data
    max_peak_heating_borefield : float
        Maximum peak heating power of the ground source heat pump [kW]
    max_peak_cooling_borefield : float
        Maximum cooling power of the borefield [kW]
    max_peak_heating_top : float
        Maximum power for the hybrid top heating system [kW]
    max_peak_heating_bottom : float
        Maximum power for the hybrid bottom heating system [kW]
    max_peak_cooling_top : float
        Maximum power for the hybrid top cooling system [kW]
    max_peak_cooling_bottom : float
        Maximum power for the hybrid bottom cooling system [kW]
    threshold_heating_top : float
        Threshold temperature for the hybrid top heating system [kW]
    threshold_heating_bottom : float
        Threshold temperature for the hybrid bottom heating system [kW]
    threshold_cooling_top : float
        Threshold temperature for the hybrid top cooling system [kW]
    threshold_cooling_bottom : float
        Threshold temperature for the hybrid bottom cooling system [kW]

    Returns
    -------

    Raises
    ------
    ValueError
        If a max power for either heating/cooling top/bottom is supplied but not the corresponding threshold.
        If the threshold temperature for the bottom load is higher than that of the top load.
        If the load_data is not of the required format.
    """

    # check if inputs are correct
    def xor(a, b):
        if a and b:
            return True
        if not a and not b:
            return True
        return False

    if not xor(max_peak_heating_top is None, threshold_heating_top is None) or \
            not xor(max_peak_heating_bottom is None, threshold_heating_bottom is None) or \
            not xor(max_peak_cooling_top is None, threshold_cooling_top is None) \
            or not xor(max_peak_cooling_bottom is None, threshold_cooling_bottom is None):
        raise ValueError('Please make sure both threshold and peak powers are supplied.')

    if threshold_heating_bottom is not None and threshold_heating_top is not None \
            and threshold_heating_top < threshold_heating_bottom:
        raise ValueError(
            'Make sure the temperature threshold for peak heating top is higher than for peak heating bottom.')

    if threshold_cooling_top is not None and threshold_cooling_bottom is not None \
            and threshold_cooling_top < threshold_cooling_bottom:
        raise ValueError(
            'Make sure the temperature threshold for peak cooling top is higher than for peak cooling bottom.')

    if not isinstance(load_data, (HourlyBuildingLoad, HourlyBuildingLoadMultiYear)):
        raise ValueError('Make sure the load data is either the HourlyBuildingLoad or HourlyBuildingLoadMultiYear.')

    if max_peak_cooling_borefield is None:
        max_peak_cooling_borefield = 10 ** 9
    if max_peak_heating_borefield is None:
        max_peak_heating_borefield = 10 ** 9

    # read weather file
    temperature = np.array([])
    try:
        TMY: pd.DataFrame = pd.read_csv(weather_file, sep=",", header=None, skiprows=8)

        # drop first 6 columns
        TMY.drop(columns=TMY.columns[:5], axis=1, inplace=True)

        # set dry bulb temperature
        temperature: np.ndarray = np.array(TMY.iloc[:, 1])
        assert len(temperature) == 8760
    except:
        raise ValueError('There is something wrong with the epw-file.')

    heating_demand = copy.copy(load_data._hourly_heating_load)
    cooling_demand = copy.copy(load_data._hourly_cooling_load)

    if isinstance(load_data, HourlyBuildingLoadMultiYear):
        # we need to tile the temperature data
        temperature = np.tile(temperature, load_data.simulation_period)
        heating_demand = copy.copy(load_data.hourly_heating_load_simulation_period)
        cooling_demand = copy.copy(load_data.hourly_cooling_load_simulation_period)

    # define parameters
    top_heating = np.zeros(temperature.shape)
    top_cooling = np.zeros(temperature.shape)
    bottom_heating = np.zeros(temperature.shape)
    bottom_cooling = np.zeros(temperature.shape)

    # calculate the loads
    if threshold_heating_top is not None:
        top_heating = np.minimum((temperature >= threshold_heating_top) * max_peak_heating_top, heating_demand)
    if threshold_cooling_top is not None:
        top_cooling = np.minimum((temperature >= threshold_cooling_top) * max_peak_cooling_top, cooling_demand)
    if threshold_heating_bottom is not None:
        bottom_heating = np.minimum((temperature <= threshold_heating_bottom) * max_peak_heating_bottom,
                                    heating_demand - top_heating)
    if threshold_cooling_bottom is not None:
        bottom_cooling = np.minimum((temperature <= threshold_cooling_bottom) * max_peak_cooling_bottom,
                                    cooling_demand - top_cooling)
    borefield_heating = np.minimum(max_peak_heating_borefield, heating_demand - top_heating - bottom_heating)
    borefield_cooling = np.minimum(max_peak_cooling_borefield, cooling_demand - top_cooling - bottom_cooling)
    excess_heating = heating_demand - top_heating - bottom_heating - borefield_heating
    excess_cooling = cooling_demand - top_cooling - bottom_cooling - borefield_cooling

    new_load = copy.deepcopy(load_data)
    new_load.hourly_heating_load = borefield_heating
    new_load.hourly_cooling_load = borefield_cooling

    return new_load, {'borefield cooling': borefield_cooling,
                      'borefield heating': borefield_heating,
                      'excess cooling': excess_cooling,
                      'excess heating': excess_heating,
                      'top heating': top_heating,
                      'top cooling': top_cooling,
                      'bottom heating': bottom_heating,
                      'bottom cooling': bottom_cooling}
