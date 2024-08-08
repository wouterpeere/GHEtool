from __future__ import annotations

import warnings

import numpy as np

from GHEtool.logger import ghe_logger
from GHEtool.VariableClasses.LoadData.Baseclasses import _HourlyData
from GHEtool.VariableClasses.LoadData.GeothermalLoad.HourlyGeothermalLoad import HourlyGeothermalLoad

from numpy.typing import ArrayLike


class HourlyGeothermalLoadMultiYear(_HourlyData):
    """
    This class contains all the information for geothermal load data with a monthly resolution and absolute input.
    This means that the inputs are both in kWh/month and kW/month.
    """

    def __init__(self, extraction_load: ArrayLike = None, injection_load: ArrayLike = None, *args, **kwargs):
        """

        Parameters
        ----------
        extraction_load : np.ndarray, list, tuple
            Extraction load [kWh/h]
        injection_load : np.ndarray, list, tuple
            Injection load [kWh/h]
        """
        # check legacy
        if len(args) > 0 or len(kwargs) > 0:
            raise DeprecationWarning(
                'The definition of the HourlyGeothermalLoad class has been changed to injection/extraction terminology instead of cooling/heating terminology. '
                'Support for DHW is also dropped. You can use the HourlyBuildingLoad class with the same definitions instead.')

        super().__init__()
        self._multiyear = True
        self._hourly = True

        # set variables
        extraction_load = np.zeros(8760) if extraction_load is None and injection_load is None else extraction_load
        self.hourly_extraction_load = np.zeros_like(injection_load) if extraction_load is None else np.array(
            extraction_load)
        self.hourly_injection_load = np.zeros_like(extraction_load) if injection_load is None else np.array(
            injection_load)

    @_HourlyData.hourly_extraction_load.setter
    def hourly_extraction_load(self, load: ArrayLike) -> None:
        """
        This function sets the hourly extraction load [kWh/h] after it has been checked.

        Parameters
        ----------
        load : np.ndarray, list or tuple
            Hourly extraction [kWh/h]

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
            self._hourly_extraction_load = load
            return
        raise ValueError

    @_HourlyData.hourly_injection_load.setter
    def hourly_injection_load(self, load: ArrayLike) -> None:
        """
        This function sets the hourly injection load [kWh/h] after it has been checked.

        Parameters
        ----------
        load : np.ndarray, list or tuple
            Hourly injection load [kWh/h]

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
            self._hourly_injection_load = load
            return
        raise ValueError

    @property
    def hourly_injection_load_simulation_period(self) -> np.ndarray:
        """
        This function returns the hourly cooling in kWh/h for a whole simulation period.

        Returns
        -------
        hourly cooling : np.ndarray
            hourly cooling for the whole simulation period
        """
        return self._hourly_injection_load

    @property
    def hourly_extraction_load_simulation_period(self) -> np.ndarray:
        """
        This function returns the hourly heating in kWh/h for a whole simulation period.

        Returns
        -------
        hourly heating : np.ndarray
            hourly heating for the whole simulation period
        """
        return self._hourly_extraction_load

    def set_hourly_injection_load(self, load: ArrayLike) -> None:
        """
        This function sets the hourly injection load [kWh/h] after it has been checked.

        Parameters
        ----------
        load : np.ndarray, list or tuple
            Hourly injection [kWh/h]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When either the length is not a multiple of 8760, the input is not of the correct type, or it contains negative values
        """
        self.hourly_injection_load = load

    def set_hourly_extraction_load(self, load: ArrayLike) -> None:
        """
        This function sets the hourly extraction load [kWh/h] after it has been checked.

        Parameters
        ----------
        load : np.ndarray, list or tuple
            Hourly extraction [kWh/h]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When either the length is not a multiple of 8760, the input is not of the correct type, or it contains negative values
        """
        self.hourly_extraction_load = load

    def __eq__(self, other) -> bool:
        if not isinstance(other, HourlyGeothermalLoadMultiYear):
            return False
        if not np.array_equal(self._hourly_injection_load, other._hourly_injection_load):
            return False
        if not np.array_equal(self._hourly_extraction_load, other._hourly_extraction_load):
            return False
        return True

    def __add__(self, other):
        if isinstance(other, HourlyGeothermalLoadMultiYear):
            if self.simulation_period != other.simulation_period:
                raise ValueError(
                    "Cannot combine HourlyGeothermalLoadMultiYear classes with different simulation periods.")

            return HourlyGeothermalLoadMultiYear(self._hourly_extraction_load + other._hourly_extraction_load,
                                                 self._hourly_injection_load + other._hourly_injection_load)

        if isinstance(other, HourlyGeothermalLoad):
            warnings.warn(
                "You combine a hourly load with a multi-year load. The result will be a multi-year load with" " the same simulation period as before."
            )
            return HourlyGeothermalLoadMultiYear(
                self._hourly_extraction_load + np.tile(other.hourly_extraction_load, self.simulation_period),
                self._hourly_injection_load + np.tile(other.hourly_injection_load, self.simulation_period),
            )

        try:
            return other.__add__(self)
        except TypeError:  # pragma: no cover
            raise TypeError("Cannot perform addition. Please check if you use correct classes.")  # pragma: no cover
