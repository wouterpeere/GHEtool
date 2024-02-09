from __future__ import annotations

import numpy as np

from GHEtool.VariableClasses.LoadData.GeothermalLoad.MonthlyGeothermalLoadAbsolute import MonthlyGeothermalLoadAbsolute
from GHEtool.logger.ghe_logger import ghe_logger

from numpy.typing import ArrayLike


class MonthlyGeothermalLoadMultiYear(MonthlyGeothermalLoadAbsolute):
    """
    This class contains all the information for geothermal load data with a monthly resolution and absolute input.
    This means that the inputs are both in kWh/month and kW/month.
    """

    def __init__(
        self,
        baseload_heating: ArrayLike = None,
        baseload_cooling: ArrayLike  = None,
        peak_heating: ArrayLike = None,
        peak_cooling: ArrayLike = None,
    ):
        """

        Parameters
        ----------
        baseload_heating : np.ndarray, list, tuple
            Baseload heating values [kWh/month]
        baseload_cooling : np.ndarray, list, tuple
            Baseload cooling values [kWh/month]
        peak_heating : np.ndarray, list, tuple
            Peak heating values [kW/month]
        peak_cooling : np.ndarray, list, tuple
            Peak cooling values [kW/month]
        """

        super().__init__()

        # set variables
        self.baseload_heating = np.zeros(12) if baseload_heating is None else baseload_heating
        self.baseload_cooling = np.zeros(12) if baseload_cooling is None else baseload_cooling
        self.peak_heating = np.zeros(12) if peak_heating is None else peak_heating
        self.peak_cooling = np.zeros(12) if peak_cooling is None else peak_cooling

    def _check_input(self, load_array: ArrayLike) -> bool:
        """
        This function checks whether the input is valid or not.
        The input is correct if and only if:
        1) the input is a np.ndarray, list or tuple
        2) the length of the input is 12
        3) the input does not contain any negative values.

        Parameters
        ----------
        load_array : np.ndarray, list or tuple

        Returns
        -------
        bool
            True if the inputs are valid
        """
        if not isinstance(load_array, (np.ndarray, list, tuple)):
            ghe_logger.error("The load should be of type np.ndarray, list or tuple.")
            return False
        if not len(load_array) % 12 == 0:
            ghe_logger.error("The length of the load should be multiples of 12.")
            return False
        if np.min(load_array) < 0:
            ghe_logger.error("No value in the load can be smaller than zero.")
            return False
        return True

    @property
    def baseload_heating_simulation_period(self) -> np.ndarray:
        """
        This function returns the baseload heating in kWh/month for a whole simulation period.

        Returns
        -------
        baseload heating : np.ndarray
            baseload heating for the whole simulation period
        """
        return self._baseload_heating

    @property
    def baseload_cooling_simulation_period(self) -> np.ndarray:
        """
        This function returns the baseload cooling in kWh/month for a whole simulation period.

        Returns
        -------
        baseload cooling : np.ndarray
            baseload cooling for the whole simulation period
        """
        return self._baseload_cooling

    @property
    def peak_heating_simulation_period(self) -> np.ndarray:
        """
        This function returns the peak heating in kW/month for a whole simulation period.

        Returns
        -------
        peak heating : np.ndarray
            peak heating for the whole simulation period
        """
        return self._peak_heating

    @property
    def peak_cooling_simulation_period(self) -> np.ndarray:
        """
        This function returns the peak cooling in kW/month for a whole simulation period.

        Returns
        -------
        peak cooling : np.ndarray
            peak cooling for the whole simulation period
        """
        return self._peak_cooling

    @property
    def baseload_heating_power_simulation_period(self) -> np.ndarray:
        """
        This function returns the average heating power in kW avg/month for a whole simulation period.

        Returns
        -------
        average heating power : np.ndarray
            average heating power for the whole simulation period
        """
        return np.divide(self.baseload_heating_simulation_period, np.tile(self.UPM, self.simulation_period))

    @property
    def baseload_cooling_power_simulation_period(self) -> np.ndarray:
        """
        This function returns the average cooling power in kW avg/month for a whole simulation period.

        Returns
        -------
        average cooling power : np.ndarray
            average cooling for the whole simulation period
        """
        return np.divide(self.baseload_cooling_simulation_period, np.tile(self.UPM, self.simulation_period))

    @property
    def monthly_average_load_simulation_period(self) -> np.ndarray:
        """
        This function calculates the average monthly load in kW for the whole simulation period.

        Returns
        -------
        monthly average load : np.ndarray
        """
        return self.baseload_cooling_power_simulation_period - self.baseload_heating_power_simulation_period

    @property
    def baseload_cooling(self) -> np.ndarray:
        """
        This function returns the baseload cooling in kWh/month.

        Returns
        -------
        baseload cooling : np.ndarray
            Baseload cooling values [kWh/month] for one year, so the length of the array is 12
        """
        return np.mean(self.baseload_cooling_simulation_period.reshape((self.simulation_period, 12)), axis=0)

    @baseload_cooling.setter
    def baseload_cooling(self, load: ArrayLike) -> None:
        """
        This function sets the baseload cooling [kWh/month] after it has been checked.
        If the baseload cooling gives a higher average power than the peak power,
        this is taken as the peak power in that month.

        Parameters
        ----------
        load : np.ndarray, list or tuple
            Baseload cooling [kWh/month]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When either the length is not a multiple of 12 , the input is not of the correct type, or it contains negative
            values
        """
        if self._check_input(load):
            self._baseload_cooling = np.array(load)
            self.simulation_period = int(len(load) / 12)
            return
        raise ValueError

    @property
    def baseload_heating(self) -> np.ndarray:
        """
        This function returns the baseload heating in kWh/month (incl. DHW).

        Returns
        -------
        baseload heating : np.ndarray
            Baseload heating values (incl. DHW) [kWh/month] for one year, so the length of the array is 12
        """
        return np.mean(self.baseload_heating_simulation_period.reshape((self.simulation_period, 12)), axis=0)

    @baseload_heating.setter
    def baseload_heating(self, load: ArrayLike) -> None:
        """
        This function sets the baseload heating [kWh/month] after it has been checked.
        If the baseload heating gives a higher average power than the peak power,
        this is taken as the peak power in that month.

        Parameters
        ----------
        load : np.ndarray, list or tuple
            Baseload heating [kWh/month]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When either the length is not a multiple of 12, the input is not of the correct type, or it contains
            negative values
        """
        if self._check_input(load):
            self._baseload_heating = np.array(load)
            self.simulation_period = int(len(load) / 12)
            return
        raise ValueError

    @property
    def peak_cooling(self) -> np.ndarray:
        """
        This function returns the peak cooling load in kW/month.

        Returns
        -------
        peak cooling : np.ndarray
            Peak cooling values for one year, so the length of the array is 12
        """
        return np.mean(np.maximum(self.peak_cooling_simulation_period, self.baseload_cooling_power_simulation_period).
                       reshape((self.simulation_period, 12)), axis=0)

    @peak_cooling.setter
    def peak_cooling(self, load) -> None:
        """
        This function sets the peak cooling load [kW/month] after it has been checked.
        If the baseload cooling gives a higher average power, this is taken as the peak power in that month.

        Parameters
        ----------
        load : np.ndarray, list or tuple
            Peak cooling load [kW/month]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When either the length is not a multiple of 12, the input is not of the correct type, or it contains
            negative values
        """
        if self._check_input(load):
            self._peak_cooling = np.array(load)
            self.simulation_period = int(len(load) / 12)
            return
        raise ValueError

    @property
    def peak_heating(self) -> np.ndarray:
        """
        This function returns the peak heating load in kW/month.

        Returns
        -------
        peak heating : np.ndarray
            Peak heating values for one year, so the length of the array is 12
        """
        return np.mean(np.maximum(self.peak_heating_simulation_period, self.baseload_heating_power_simulation_period).
                       reshape((self.simulation_period, 12)), axis=0)

    @peak_heating.setter
    def peak_heating(self, load: ArrayLike) -> None:
        """
        This function sets the peak heating load [kW/month] after it has been checked.
        If the baseload heating gives a higher average power, this is taken as the peak power in that month.

        Parameters
        ----------
        load : np.ndarray, list or tuple
            Peak heating load [kW/month]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When either the length is not a multiple of 12, the input is not of the correct type, or it contains
            negative values
        """
        if self._check_input(load):
            self._peak_heating = np.array(load)
            self.simulation_period = int(len(load) / 12)
            return
        raise ValueError
