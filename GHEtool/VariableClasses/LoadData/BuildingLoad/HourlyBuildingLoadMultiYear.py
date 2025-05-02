from __future__ import annotations

import numpy as np

from GHEtool.VariableClasses.LoadData.Baseclasses import _HourlyDataBuilding
from GHEtool.VariableClasses.Efficiency import *
from typing import Union
from numpy.typing import ArrayLike


class HourlyBuildingLoadMultiYear(_HourlyDataBuilding):
    """
    This class contains all the information for building multi-year load data with an hourly resolution.
    """

    def __init__(self, heating_load: ArrayLike = None,
                 cooling_load: ArrayLike = None,
                 efficiency_heating: Union[int, float, COP, SCOP] = 5,
                 efficiency_cooling: Union[int, float, EER, SEER, EERCombined] = 20,
                 dhw: Union[float, np.ndarray] = None,
                 efficiency_dhw: Union[int, float, COP, SCOP] = 4):
        """

        Parameters
        ----------
        heating_load : np.ndarray, list, tuple
            Extraction load [kWh/h]
        cooling_load : np.ndarray, list, tuple
            Injection load [kWh/h]
        efficiency_heating : int, float, COP, SCOP
            Efficiency in heating
        efficiency_cooling : int, float, EER, SEER
            Efficiency in cooling
        dhw : float, np.ndarray
            Yearly value of array with energy demand for domestic hot water (DHW) [kWh]
        efficiency_dhw : int, float, COP, SCOP,
            Efficiency in DHW
        """

        _HourlyDataBuilding.__init__(self, efficiency_heating, efficiency_cooling, dhw, efficiency_dhw, True)
        self._multiyear = True

        # set variables
        heating_load = np.zeros(8760) if heating_load is None and cooling_load is None else heating_load
        self.hourly_heating_load = np.zeros_like(cooling_load) if heating_load is None else np.array(heating_load)
        self.hourly_cooling_load = np.zeros_like(heating_load) if cooling_load is None else np.array(cooling_load)

    @_HourlyDataBuilding.hourly_heating_load.setter
    def hourly_heating_load(self, load: ArrayLike) -> None:
        """
        This function sets the hourly heating load [kWh/h] after it has been checked.

        Parameters
        ----------
        load : np.ndarray, list or tuple
            Hourly heating [kWh/h]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When either the length is not 8760, the input is not of the correct type, or it contains negative
            values
        """
        if self._check_input(load):
            self._hourly_heating_load = load
            return
        raise ValueError

    @_HourlyDataBuilding.hourly_cooling_load.setter
    def hourly_cooling_load(self, load: ArrayLike) -> None:
        """
        This function sets the hourly cooling load [kWh/h] after it has been checked.

        Parameters
        ----------
        load : np.ndarray, list or tuple
            Hourly cooling load [kWh/h]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When either the length is not 8760, the input is not of the correct type, or it contains negative
            values
        """
        if self._check_input(load):
            self._hourly_cooling_load = load
            return
        raise ValueError

    @property
    def hourly_cooling_load_simulation_period(self) -> np.ndarray:
        """
        This function returns the hourly cooling in kWh/h for a whole simulation period.

        Returns
        -------
        hourly cooling : np.ndarray
            hourly cooling for the whole simulation period
        """
        return self._hourly_cooling_load

    @property
    def hourly_heating_load_simulation_period(self) -> np.ndarray:
        """
        This function returns the hourly heating in kWh/h for a whole simulation period.

        Returns
        -------
        hourly heating : np.ndarray
            hourly heating for the whole simulation period
        """
        return self._hourly_heating_load

    def set_hourly_cooling_load(self, load: ArrayLike) -> None:
        """
        This function sets the hourly cooling load [kWh/h] after it has been checked.

        Parameters
        ----------
        load : np.ndarray, list or tuple
            Hourly cooling [kWh/h]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When either the length is not a multiple of 8760, the input is not of the correct type, or it contains negative values
        """
        self.hourly_cooling_load = load

    def set_hourly_heating_load(self, load: ArrayLike) -> None:
        """
        This function sets the hourly heating load [kWh/h] after it has been checked.

        Parameters
        ----------
        load : np.ndarray, list or tuple
            Hourly heating [kWh/h]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When either the length is not a multiple of 8760, the input is not of the correct type, or it contains negative values
        """
        self.hourly_heating_load = load

    def set_hourly_dhw_load(self, load: ArrayLike) -> None:
        """
        This function sets the hourly domestic hot water load [kWh/h] after it has been checked.

        Parameters
        ----------
        load : np.ndarray, list or tuple
            Hourly dhw load [kWh/h]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When either the length is not 8760, the input is not of the correct type, or it contains negative
            values
        """
        self.dhw = load

    @property
    def hourly_dhw_load_simulation_period(self) -> np.ndarray:
        """
        This function returns the hourly DHW load in kWh/h for the whole simulation period.

        Returns
        -------
        hourly DHW : np.ndarray
            Hourly DHW values [kWh/h] for the whole simulation period
        """
        if self._dhw is None:
            return np.zeros(8760 * self.simulation_period)
        return self._dhw

    def __export__(self):
        return {
            'type': 'Multiyear hourly building load',
            'Efficiency heating': self.cop.__export__(),
            'Efficiency cooling': self.eer.__export__(),
            'Peak cooling duration [hour]': self.peak_injection_duration / 3600,
            'Peak heating duration [hour]': self.peak_extraction_duration / 3600
        }
