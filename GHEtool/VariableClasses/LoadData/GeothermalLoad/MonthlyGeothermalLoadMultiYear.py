from __future__ import annotations

import numpy as np

from GHEtool.VariableClasses.LoadData.Baseclasses import _LoadData
from GHEtool.VariableClasses.LoadData.GeothermalLoad.MonthlyGeothermalLoadAbsolute import MonthlyGeothermalLoadAbsolute
from GHEtool.logger.ghe_logger import ghe_logger

from numpy.typing import ArrayLike


class MonthlyGeothermalLoadMultiYear(_LoadData):
    """
    This class contains all the information for geothermal load data with a monthly resolution and absolute input.
    This means that the inputs are both in kWh/month and kW/month.
    """

    def __init__(
            self,
            baseload_extraction: ArrayLike = None,
            baseload_injection: ArrayLike = None,
            peak_extraction: ArrayLike = None,
            peak_injection: ArrayLike = None,
            *args,
            **kwargs
    ):
        """

        Parameters
        ----------
        baseload_extraction : np.ndarray, list, tuple
            Baseload heating values [kWh/month]
        baseload_injection : np.ndarray, list, tuple
            Baseload cooling values [kWh/month]
        peak_extraction : np.ndarray, list, tuple
            Peak heating values [kW/month]
        peak_injection : np.ndarray, list, tuple
            Peak cooling values [kW/month]
        """
        # check legacy
        if len(args) > 0 or len(kwargs) > 0:
            raise DeprecationWarning(
                'The definition of the HourlyGeothermalLoad class has been changed to injection/extraction terminology instead of cooling/heating terminology. '
                'Support for DHW is also dropped. You can use the HourlyBuildingLoad class with the same definitions instead.')

        super().__init__()

        # set variables
        self.baseload_extraction = np.zeros(12) if baseload_extraction is None else baseload_extraction
        self.baseload_injection = np.zeros(12) if baseload_injection is None else baseload_injection
        self.peak_extraction = np.zeros(12) if peak_extraction is None else peak_extraction
        self.peak_injection = np.zeros(12) if peak_injection is None else peak_injection

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
    def monthly_baseload_injection_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly injection baseload in kWh/month for the whole simulation period.

        Returns
        -------
        baseload injection : np.ndarray
            baseload injection for the whole simulation period
        """
        return self.baseload_injection

    @property
    def monthly_baseload_extraction_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly extraction baseload in kWh/month for the whole simulation period.

        Returns
        -------
        baseload extraction : np.ndarray
            baseload extraction for the whole simulation period
        """
        return self._baseload_extraction

    @property
    def monthly_peak_injection_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly injection peak in kW/month for the whole simulation period.

        Returns
        -------
        peak injection : np.ndarray
            peak injection for the whole simulation period
        """
        return self._peak_injection

    @property
    def monthly_peak_extraction_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly extraction peak in kW/month for the whole simulation period.

        Returns
        -------
        peak extraction : np.ndarray
            peak extraction for the whole simulation period
        """
        return self._peak_extraction

    @property
    def baseload_injection(self) -> np.ndarray:
        """
        This function returns the baseload cooling in kWh/month for the whole simulation period.

        Returns
        -------
        baseload cooling : np.ndarray
            Baseload cooling values [kWh/month] for all years
        """
        return self._baseload_injection

    @baseload_injection.setter
    def baseload_injection(self, load: ArrayLike) -> None:
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
            self._baseload_injection = np.array(load)
            return
        raise ValueError

    @property
    def baseload_extraction(self) -> np.ndarray:
        """
        This function returns the baseload heating in kWh/month for the whole simulation period.

        Returns
        -------
        baseload heating : np.ndarray
            Baseload heating values [kWh/month] for all years
        """
        return self._baseload_extraction

    @baseload_extraction.setter
    def baseload_extraction(self, load: ArrayLike) -> None:
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
            self._baseload_extraction = np.array(load)
            return
        raise ValueError

    @property
    def peak_injection(self) -> np.ndarray:
        """
        This function returns the peak cooling load in kW/month for the whole simulation period.

        Returns
        -------
        peak cooling : np.ndarray
            Peak cooling values for all years
        """
        return self._peak_injection

    @peak_injection.setter
    def peak_injection(self, load) -> None:
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
            self._peak_injection = np.array(load)
            return
        raise ValueError

    @property
    def peak_extraction(self) -> np.ndarray:
        """
        This function returns the peak heating load in kW/month for the whole simulation period.

        Returns
        -------
        peak heating : np.ndarray
            Peak heating values for all years
        """
        return self._peak_extraction

    @peak_extraction.setter
    def peak_extraction(self, load: ArrayLike) -> None:
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
            self._peak_extraction = np.array(load)
            return
        raise ValueError
