import warnings

import numpy as np

from GHEtool.VariableClasses.LoadData.Baseclasses import _SingleYear, _LoadData
from GHEtool.VariableClasses.LoadData.GeothermalLoad import HourlyGeothermalLoad
from GHEtool.VariableClasses.LoadData.GeothermalLoad.HourlyGeothermalLoadMultiYear import HourlyGeothermalLoadMultiYear
from GHEtool.logger.ghe_logger import ghe_logger

from numpy.typing import ArrayLike


class MonthlyGeothermalLoadAbsolute(_SingleYear, _LoadData):
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
            simulation_period: int = 20,
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
        simulation_period : int
            Length of the simulation period in years
        """
        # check legacy
        if len(args) > 0 or len(kwargs) > 0:
            raise DeprecationWarning(
                'The definition of the HourlyGeothermalLoad class has been changed to injection/extraction terminology instead of cooling/heating terminology. '
                'Support for DHW is also dropped. You can use the HourlyBuildingLoad class with the same definitions instead.')
        _LoadData.__init__(self)
        _SingleYear.__init__(self, simulation_period)

        # set variables
        self.baseload_extraction = np.zeros(12) if baseload_extraction is None else baseload_extraction
        self.baseload_injection = np.zeros(12) if baseload_injection is None else baseload_injection
        self.peak_extraction = np.zeros(12) if peak_extraction is None else peak_extraction
        self.peak_injection = np.zeros(12) if peak_injection is None else peak_injection

    @property
    def baseload_injection(self) -> np.ndarray:
        """
        This function returns the baseload cooling in kWh/month.

        Returns
        -------
        baseload cooling : np.ndarray
            Baseload cooling values [kWh/month] for one year, so the length of the array is 12
        """
        return self.correct_for_start_month(self._baseload_injection)

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
            When either the length is not 12, the input is not of the correct type, or it contains negative
            values
        """
        if self._check_input(load):
            self._baseload_injection = np.array(load)
            return
        raise ValueError

    def set_baseload_injection(self, load: ArrayLike) -> None:
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
            When either the length is not 12, the input is not of the correct type, or it contains negative
            values
        """
        self.baseload_injection = load

    @property
    def baseload_extraction(self) -> np.ndarray:
        """
        This function returns the baseload heating in kWh/month (incl. DHW).

        Returns
        -------
        baseload heating : np.ndarray
            Baseload heating values (incl. DHW) [kWh/month] for one year, so the length of the array is 12
        """
        return self.correct_for_start_month(self._baseload_extraction)

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
            When either the length is not 12, the input is not of the correct type, or it contains negative
            values
        """
        if self._check_input(load):
            self._baseload_extraction = np.array(load)
            return
        raise ValueError

    def set_baseload_extraction(self, load: ArrayLike) -> None:
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
            When either the length is not 12, the input is not of the correct type, or it contains negative
            values
        """
        self.baseload_extraction = np.array(load)

    @property
    def peak_injection(self) -> np.ndarray:
        """
        This function returns the peak cooling load in kW/month.

        Returns
        -------
        peak cooling : np.ndarray
            Peak cooling values for one year, so the length of the array is 12
        """
        return np.maximum(self.correct_for_start_month(self._peak_injection), self.monthly_baseload_injection_power)

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
            When either the length is not 12, the input is not of the correct type, or it contains negative
            values
        """
        if self._check_input(load):
            self._peak_injection = np.array(load)
            return
        raise ValueError

    def set_peak_injection(self, load: ArrayLike) -> None:
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
            When either the length is not 12, the input is not of the correct type, or it contains negative
            values
        """
        self.peak_injection = np.array(load)

    @property
    def peak_extraction(self) -> np.ndarray:
        """
        This function returns the peak heating load in kW/month.

        Returns
        -------
        peak heating : np.ndarray
            Peak heating values for one year, so the length of the array is 12
        """
        return np.maximum(self.correct_for_start_month(self._peak_extraction), self.monthly_baseload_extraction_power)

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
            When either the length is not 12, the input is not of the correct type, or it contains negative
            values
        """
        if self._check_input(load):
            self._peak_extraction = np.array(load)
            return
        raise ValueError

    def set_peak_extraction(self, load: ArrayLike) -> None:
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
            When either the length is not 12, the input is not of the correct type, or it contains negative
            values
        """
        self.peak_extraction = np.array(load)

    @property
    def monthly_baseload_injection_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly injection baseload in kWh/month for the whole simulation period.

        Returns
        -------
        baseload injection : np.ndarray
            baseload injection for the whole simulation period
        """
        return np.tile(self.baseload_injection, self.simulation_period)

    @property
    def monthly_baseload_extraction_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly extraction baseload in kWh/month for the whole simulation period.

        Returns
        -------
        baseload extraction : np.ndarray
            baseload extraction for the whole simulation period
        """
        return np.tile(self.baseload_extraction, self.simulation_period)

    @property
    def monthly_peak_injection_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly injection peak in kW/month for the whole simulation period.

        Returns
        -------
        peak injection : np.ndarray
            peak injection for the whole simulation period
        """
        return np.tile(self.peak_injection, self.simulation_period)

    @property
    def monthly_peak_extraction_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly extraction peak in kW/month for the whole simulation period.

        Returns
        -------
        peak extraction : np.ndarray
            peak extraction for the whole simulation period
        """
        return np.tile(self.peak_extraction, self.simulation_period)

    def __eq__(self, other) -> bool:
        if not isinstance(other, MonthlyGeothermalLoadAbsolute):
            return False
        if not np.array_equal(self.baseload_extraction, other.baseload_extraction):
            return False
        if not np.array_equal(self.baseload_injection, other.baseload_injection):
            return False
        if not np.array_equal(self.peak_extraction, other.peak_extraction):
            return False
        if not np.array_equal(self.peak_injection, other.peak_injection):
            return False
        if not self.simulation_period == other.simulation_period:
            return False
        return True

    def __add__(self, other):
        if isinstance(other, MonthlyGeothermalLoadAbsolute):
            if self.simulation_period != other.simulation_period:
                warnings.warn(
                    f"The simulation period for both load classes are different. "
                    f"The maximum simulation period of "
                    f"{max(self.simulation_period, other.simulation_period)} years will be taken."
                )
            if self.peak_injection_duration != other.peak_injection_duration:
                warnings.warn(
                    f"The peak cooling duration for both load classes are different. "
                    f"The maximum peak cooling duration of "
                    f"{max(self.peak_injection_duration, other.peak_injection_duration)} hours will be taken."
                )
            if self.peak_extraction_duration != other.peak_extraction_duration:
                warnings.warn(
                    f"The peak heating duration for both load classes are different. "
                    f"The maximum peak heating duration of "
                    f"{max(self.peak_extraction_duration, other.peak_extraction_duration)} hours will be taken."
                )

            result = MonthlyGeothermalLoadAbsolute(
                self._baseload_extraction + other._baseload_extraction,
                self._baseload_injection + other._baseload_injection,
                self._peak_extraction + other._peak_extraction,
                self._peak_injection + other._peak_injection,
                max(self.simulation_period, other.simulation_period)
            )
            result.peak_injection_duration = max(self._peak_injection_duration, other._peak_injection_duration)
            result.peak_extraction_duration = max(self._peak_extraction_duration, other._peak_extraction_duration)

            return result

        # multiyear hourly
        if isinstance(other, HourlyGeothermalLoadMultiYear):
            raise TypeError("You cannot add an HourlyMultiYear input with a monthly based input.")

        # hourly load
        if isinstance(other, HourlyGeothermalLoad):
            warnings.warn("You add an hourly to a monthly load, the result will hence be a monthly load.")
            if self.simulation_period != other.simulation_period:
                warnings.warn(
                    f"The simulation period for both load classes are different. "
                    f"The maximum simulation period of "
                    f"{max(self.simulation_period, other.simulation_period)} years will be taken."
                )

            peak_extraction, baseload_extraction = other.resample_to_monthly(other._hourly_extraction_load)
            peak_injection, baseload_injection = other.resample_to_monthly(other._hourly_injection_load)

            result = MonthlyGeothermalLoadAbsolute(
                self._baseload_extraction + baseload_extraction,
                self._baseload_injection + baseload_injection,
                self._peak_extraction + peak_extraction,
                self._peak_injection + peak_injection,
                max(self.simulation_period, other.simulation_period)
            )
            result.peak_injection_duration = self._peak_injection_duration
            result.peak_extraction_duration = self._peak_extraction_duration

            return result

        raise TypeError("Cannot perform addition. Please check if you use correct classes.")

    def correct_for_start_month(self, array: np.ndarray) -> np.ndarray:
        """
        This function corrects the load for the correct start month.
        If the simulation starts in september, the start month is 9 and hence the array should start
        at index 9.

        Parameters
        ----------
        array : np.ndarray
            Load array

        Returns
        -------
        load : np.ndarray
        """
        if self.start_month == 1:
            return array
        return np.concatenate((array[self.start_month - 1:], array[: self.start_month - 1]))

    def __repr__(self):
        temp = f'Monthly geothermal load\n'
        temp += f'Month\tPeak extraction [kW]\tPeak injection [kW]\tBaseload extraction [kWh]\tBaseload injection [kWh]\n'
        for i in range(12):
            temp += f'{i + 1}\t{self.peak_extraction[i]:.2f}\t{self.peak_injection[i]:.2f}\t' \
                    f'{self.baseload_extraction[i]:.2f}\t{self.baseload_injection[i]:.2f}\n'
        temp += f'Peak injection duration [hour]: {self.peak_injection_duration / 3600:.1f}\n'
        temp += f'Peak extraction duration [hour]: {self.peak_extraction_duration / 3600:.1f}\n'
        temp += f'Simulation period [year]: {self.simulation_period}\n' \
                f'First month of simulation [-]: {self.start_month}'
        return temp
