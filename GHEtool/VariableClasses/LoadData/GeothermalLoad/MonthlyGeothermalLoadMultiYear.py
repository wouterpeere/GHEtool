from __future__ import annotations

import numpy as np

from GHEtool.VariableClasses.LoadData.Baseclasses import _LoadData

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
            Baseload extraction values [kWh/month]
        baseload_injection : np.ndarray, list, tuple
            Baseload injection values [kWh/month]
        peak_extraction : np.ndarray, list, tuple
            Peak extraction values [kW/month]
        peak_injection : np.ndarray, list, tuple
            Peak injection values [kW/month]
        """
        # check legacy
        if len(args) > 0 or len(kwargs) > 0:
            raise DeprecationWarning(
                'The definition of the HourlyGeothermalLoad class has been changed to injection/extraction terminology instead of cooling/heating terminology. '
                'Support for DHW is also dropped. You can use the HourlyBuildingLoad class with the same definitions instead.')

        super().__init__()
        self._multiyear = True

        # set variables
        self.baseload_extraction = np.zeros(12) if baseload_extraction is None else baseload_extraction
        self.baseload_injection = np.zeros(12) if baseload_injection is None else baseload_injection
        self.peak_extraction = np.zeros(12) if peak_extraction is None else peak_extraction
        self.peak_injection = np.zeros(12) if peak_injection is None else peak_injection

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
        return self.baseload_extraction

    @property
    def monthly_peak_injection_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly injection peak in kW/month for the whole simulation period.

        Returns
        -------
        peak injection : np.ndarray
            peak injection for the whole simulation period
        """
        return self.peak_injection

    @property
    def monthly_peak_extraction_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly extraction peak in kW/month for the whole simulation period.

        Returns
        -------
        peak extraction : np.ndarray
            peak extraction for the whole simulation period
        """
        return self.peak_extraction

    @property
    def baseload_injection(self) -> np.ndarray:
        """
        This function returns the baseload injection in kWh/month for the whole simulation period.

        Returns
        -------
        baseload injection : np.ndarray
            Baseload injection values [kWh/month] for all years
        """
        return self._baseload_injection

    @baseload_injection.setter
    def baseload_injection(self, load: ArrayLike) -> None:
        """
        This function sets the baseload injection [kWh/month] after it has been checked.
        If the baseload injection gives a higher average power than the peak power,
        this is taken as the peak power in that month.

        Parameters
        ----------
        load : np.ndarray, list or tuple
            Baseload injection [kWh/month]

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
        This function returns the baseload extraction in kWh/month for the whole simulation period.

        Returns
        -------
        baseload extraction : np.ndarray
            Baseload extraction values [kWh/month] for all years
        """
        return self._baseload_extraction

    @baseload_extraction.setter
    def baseload_extraction(self, load: ArrayLike) -> None:
        """
        This function sets the baseload extraction [kWh/month] after it has been checked.
        If the baseload extraction gives a higher average power than the peak power,
        this is taken as the peak power in that month.

        Parameters
        ----------
        load : np.ndarray, list or tuple
            Baseload extraction [kWh/month]

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
        This function returns the peak injection load in kW/month for the whole simulation period.

        Returns
        -------
        peak injection : np.ndarray
            Peak injection values for all years
        """
        return self._peak_injection

    @peak_injection.setter
    def peak_injection(self, load) -> None:
        """
        This function sets the peak injection load [kW/month] after it has been checked.
        If the baseload injection gives a higher average power, this is taken as the peak power in that month.

        Parameters
        ----------
        load : np.ndarray, list or tuple
            Peak injection load [kW/month]

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
        This function returns the peak extraction load in kW/month for the whole simulation period.

        Returns
        -------
        peak extraction : np.ndarray
            Peak extraction values for all years
        """
        return self._peak_extraction

    @peak_extraction.setter
    def peak_extraction(self, load: ArrayLike) -> None:
        """
        This function sets the peak extraction load [kW/month] after it has been checked.
        If the baseload extraction gives a higher average power, this is taken as the peak power in that month.

        Parameters
        ----------
        load : np.ndarray, list or tuple
            Peak extraction load [kW/month]

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

    def __repr__(self):
        return f'Multiyear monthly geothermal load\n' \
               f'Peak injection duration [hour]: {self.peak_injection_duration / 3600:.1f}\n' \
               f'Peak extraction duration [hour]: {self.peak_extraction_duration / 3600:.1f}'
