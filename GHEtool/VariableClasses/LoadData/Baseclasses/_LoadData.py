import abc

import numpy as np

from abc import ABC
from numpy.typing import ArrayLike
from GHEtool.VariableClasses.BaseClass import BaseClass


class _LoadData(ABC, BaseClass):
    """
    This class contains all the general functionalities for the load classes.
    """

    AVG_UPM: int = 730  # number of hours per month
    DEFAULT_LENGTH_PEAK: int = 6  # hours

    def __init__(self):
        self.tm: int = _LoadData.AVG_UPM * 3600  # time in a month in seconds
        self._all_months_equal: bool = True  # true if it is assumed that all months are of the same length
        self._peak_injection_duration: int = _LoadData.DEFAULT_LENGTH_PEAK
        self._peak_extraction_duration: int = _LoadData.DEFAULT_LENGTH_PEAK
        self._multiyear = False
        self._hourly = False

        # initiate variables
        self._baseload_extraction: np.ndarray = np.zeros(12)
        self._baseload_injection: np.ndarray = np.zeros(12)
        self._peak_extraction: np.ndarray = np.zeros(12)
        self._peak_injection: np.ndarray = np.zeros(12)

    @abc.abstractmethod
    def monthly_baseload_injection_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly injection baseload in kWh/month for the whole simulation period.

        Returns
        -------
        baseload injection : np.ndarray
            Baseload injection for the whole simulation period
        """

    @abc.abstractmethod
    def monthly_baseload_extraction_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly extraction baseload in kWh/month for the whole simulation period.

        Returns
        -------
        baseload extraction : np.ndarray
            Baseload extraction for the whole simulation period
        """

    @abc.abstractmethod
    def monthly_peak_injection_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly injection peak in kW/month for the whole simulation period.

        Returns
        -------
        peak injection : np.ndarray
            Peak injection for the whole simulation period
        """

    @abc.abstractmethod
    def monthly_peak_extraction_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly extraction peak in kW/month for the whole simulation period.

        Returns
        -------
        peak extraction : np.ndarray
            Peak extraction for the whole simulation period
        """

    @property
    def simulation_period(self) -> int:
        """
        This property returns the simulation period.

        Returns
        -------
        simulation period : int
        """
        return int(len(self.monthly_baseload_injection_simulation_period) / 12)

    @property
    def all_months_equal(self) -> bool:
        """
        Returns the attribute all months are equal

        Returns
        -------
        bool
            True if the months are assumed to be of equal length (i.e. 730 hours/month).
            False if the correct number of hours is used.
        """
        return self._all_months_equal

    @all_months_equal.setter
    def all_months_equal(self, bool: bool) -> None:
        """
        Sets the all_months_equal attribute.

        Parameters
        ----------
        bool : bool
            True if the months are assumed to be of equal length (i.e. 730 hours/month).
            False if the correct number of hours is used.

        Returns
        -------
        None
        """
        self._all_months_equal = bool

    @property
    def UPM(self) -> np.ndarray:
        """
        Depending on whether all months are assumed to have equal length, the UPM are either constant
        or vary during the year.

        Returns
        -------
        Hours per month : np.ndarray
        """
        if self.all_months_equal:
            # every month has equal length
            return np.full(12, _LoadData.AVG_UPM, dtype=np.int64)
        else:
            return np.array([744, 672, 744, 720, 744, 720, 744, 744, 720, 744, 720, 744], dtype=np.int64)

    @property
    def monthly_baseload_injection(self) -> np.ndarray:
        """
        This function returns the monthly baseload injection in kWh/month.

        Returns
        -------
        monthly baseload injection : np.ndarray
        """
        return np.mean(self.monthly_baseload_injection_simulation_period.reshape((self.simulation_period, 12)),
                       axis=0)

    @property
    def monthly_baseload_extraction(self) -> np.ndarray:
        """
        This function returns the monthly baseload extraction in kWh/month.

        Returns
        -------
        monthly baseload extraction : np.ndarray
        """
        return np.mean(self.monthly_baseload_extraction_simulation_period.reshape((self.simulation_period, 12)),
                       axis=0)

    @property
    def monthly_peak_injection(self) -> np.ndarray:
        """
        This function returns the monthly peak injection in kW/month.

        Returns
        -------
        monthly peak injection : np.ndarray
        """
        return np.mean(self.monthly_peak_injection_simulation_period.reshape((self.simulation_period, 12)),
                       axis=0)

    @property
    def monthly_peak_extraction(self) -> np.ndarray:
        """
        This function returns the monthly peak extraction in kW/month.

        Returns
        -------
        monthly peak extraction : np.ndarray
        """
        return np.mean(self.monthly_peak_extraction_simulation_period.reshape((self.simulation_period, 12)),
                       axis=0)

    @property
    def monthly_baseload_injection_power(self) -> np.ndarray:
        """
        This function returns the monthly injection power due to the baseload injection in kW/month.

        Returns
        -------
        monthly baseload injection power : np.ndarray
        """
        return np.divide(self.monthly_baseload_injection, self.UPM)

    @property
    def monthly_baseload_extraction_power(self) -> np.ndarray:
        """
        This function returns the monthly extraction power due to the baseload extraction in kW/month.

        Returns
        -------
        monthly baseload extraction power : np.ndarray
        """
        return np.divide(self.monthly_baseload_extraction, self.UPM)

    @property
    def monthly_baseload_injection_power_simulation_period(self) -> np.ndarray:
        """

        Returns
        -------

        """
        return np.divide(self.monthly_baseload_injection_simulation_period, np.tile(self.UPM, self.simulation_period))

    @property
    def monthly_baseload_extraction_power_simulation_period(self) -> np.ndarray:
        """

        Returns
        -------

        """
        return np.divide(self.monthly_baseload_extraction_simulation_period, np.tile(self.UPM, self.simulation_period))

    @property
    def yearly_average_injection_load(self) -> float:
        """
        This function returns the average yearly injection load in kWh.

        Returns
        -------
        float
            Yearly injection load kWh/year
        """
        return np.sum(self.monthly_baseload_injection)

    @property
    def yearly_average_extraction_load(self) -> float:
        """
        This function returns the average yearly extraction load in kWh.

        Returns
        -------
        float
            Yearly extraction load kWh/year
        """
        return np.sum(self.monthly_baseload_extraction)

    @property
    def yearly_extraction_load_simulation_period(self) -> np.array:
        """
        This function returns the yearly extraction demand in kWh/year for the whole simulation period.

        Returns
        -------
        yearly extraction : np.ndarray
            yearly extraction for the whole simulation period
        """
        return np.sum(np.reshape(self.monthly_baseload_extraction_simulation_period, (self.simulation_period, 12)),
                      axis=1)

    @property
    def yearly_injection_load_simulation_period(self) -> np.array:
        """
        This function returns the yearly injection demand in kWh/year for the whole simulation period.

        Returns
        -------
        yearly injection : np.ndarray
            yearly injection for the whole simulation period
        """
        return np.sum(np.reshape(self.monthly_baseload_injection_simulation_period, (self.simulation_period, 12)),
                      axis=1)

    @property
    def yearly_extraction_peak_simulation_period(self) -> np.array:
        """
        This function returns the yearly extraction peak in kW/year for the whole simulation period.

        Returns
        -------
        yearly extraction : np.ndarray
            yearly extraction for the whole simulation period
        """
        return np.max(np.reshape(self.monthly_peak_extraction_simulation_period, (self.simulation_period, 12)), axis=1)

    @property
    def yearly_injection_peak_simulation_period(self) -> np.array:
        """
        This function returns the yearly injection peak in kW/year for the whole simulation period.

        Returns
        -------
        yearly injection : np.ndarray
            yearly injection for the whole simulation period
        """
        return np.max(np.reshape(self.monthly_peak_injection_simulation_period, (self.simulation_period, 12)), axis=1)

    @property
    def imbalance(self) -> float:
        """
        This function calculates the average yearly ground imbalance.
        A positive imbalance means that the field is injection dominated, i.e. it heats up every year.

        Returns
        -------
        imbalance : float
        """
        return np.sum(
            self.monthly_baseload_injection_simulation_period - self.monthly_baseload_extraction_simulation_period) / self.simulation_period

    @property
    def monthly_average_injection_power(self) -> np.ndarray:
        """
        This function calculates the average monthly injection power in kW.
        A negative load means it is extraction dominated.

        Returns
        -------
        monthly average load : np.ndarray
        """
        return np.mean(self.monthly_average_injection_power_simulation_period.reshape((self.simulation_period, 12)),
                       axis=0)

    @property
    def monthly_average_injection_power_simulation_period(self) -> np.ndarray:
        """
        This function calculates the average monthly injection power in kW for the whole simulation period.
        A negative load means it is extraction dominated.

        Returns
        -------
        monthly average load : np.ndarray
        """
        return self.monthly_baseload_injection_power_simulation_period - self.monthly_baseload_extraction_power_simulation_period

    @property
    def peak_extraction_duration(self) -> float:
        """
        Length of the peak in extraction.

        Returns
        -------
        Length peak in extraction [s]
        """
        return self._peak_extraction_duration * 3600

    @peak_extraction_duration.setter
    def peak_extraction_duration(self, duration: float) -> None:
        """
        This function sets the duration of the peak in extraction.

        Parameters
        ----------
        duration : float
            Duration of the peak in hours

        Returns
        -------
        None
        """
        self._peak_extraction_duration = duration

    @property
    def peak_injection_duration(self) -> float:
        """
        Duration of the peak in injection.

        Returns
        -------
        Duration of the peak in injection [s]
        """
        return self._peak_injection_duration * 3600

    @peak_injection_duration.setter
    def peak_injection_duration(self, duration: float) -> None:
        """
        This function sets the duration of the peak in injection.

        Parameters
        ----------
        duration : float
            Duration of the peak in hours

        Returns
        -------
        None
        """
        self._peak_injection_duration = duration

    @property
    def peak_duration(self) -> None:
        """
        Dummy object to set the length peak for both extraction and injection.

        Returns
        -------
        None
        """
        return

    @peak_duration.setter
    def peak_duration(self, duration: float) -> None:
        """
        This sets the duration of both the extraction and injection peak.

        Parameters
        ----------
        duration : float
            Duration in hours

        Returns
        -------
        None
        """
        self.peak_extraction_duration = duration
        self.peak_injection_duration = duration

    @property
    def ty(self) -> float:
        """
        Simulation period in seconds.

        Returns
        -------
        Simulation period in seconds
        """
        return self.simulation_period * 8760 * 3600

    @property
    def time_L3(self) -> np.ndarray:
        """
        Time for L3 sizing, i.e. an array with monthly the cumulative seconds that have passed.
        [744, 1416 ...] * 3600

        Returns
        -------
        Times for the L3 sizing : np.ndarray
        """
        return np.cumsum(np.tile(self.UPM, self.simulation_period) * 3600)

    @property
    def time_L4(self) -> np.ndarray:
        """
        Times for the L4 sizing, i.e. an array with hourly the cumulative seconds that have passed.
        [1, 2, 3, 4 ...] * 3600

        Returns
        -------
        Times for the L4 sizing : np.ndarray
        """
        # set the time constant for the L4 sizing
        time_L4 = 3600 * np.arange(1, 8760 * self.simulation_period + 1, dtype=np.float16)
        if np.isinf(time_L4).any():
            # 16 bit is not enough, go to 32
            time_L4 = 3600 * np.arange(1, 8760 * self.simulation_period + 1, dtype=np.float32)
        return time_L4

    @staticmethod
    def get_month_index(peak_load, avg_load) -> int:
        """
        This function calculates and returns the month index (i.e. the index of the month
        in which the field should be sized). It does so by taking 1) the month with the highest peak load.
        2) if all the peak loads are the same, it takes the month with the highest average load
        3) if all average loads are the same, it takes the last month

        Parameters
        ----------
        peak_load : np.ndarray
            array with the peak loads [kW]
        avg_load : np.ndarray
            array with the monthly average loads [kW]

        Returns
        -------
        month_index : int
            0 = jan, 1 = feb ...
        """
        # check if all peak loads are equal
        if not np.all(peak_load == peak_load[0]):
            return np.where(peak_load == np.max(peak_load))[0][-1]

        # if the average load is not constant, the month with the highest average load is chosen
        # if it is constant, the last month is returned
        return np.where(avg_load == np.max(avg_load))[0][-1]

    @property
    def max_peak_injection(self) -> float:
        """
        This returns the max peak injection in kW.

        Returns
        -------
        max peak injection : float
        """
        return np.max(self.monthly_peak_injection_simulation_period)

    @property
    def max_peak_extraction(self) -> float:
        """
        This returns the max peak extraction in kW.

        Returns
        -------
        max peak extraction : float
        """
        return np.max(self.monthly_peak_extraction_simulation_period)

    def _calculate_last_year_params(self, HC: bool) -> tuple:
        """
        This function calculates the parameters for the sizing based on the last year of operation.
        This is needed for the L2 sizing.

        Parameters
        ----------
        HC : bool
            True if the borefield is limited by extraction load

        Returns
        -------
        th, qh, qm, qa : float
            Peak length [s], peak load [W], corresponding monthly load [W], yearly imbalance [W]
        """

        # convert imbalance to Watt
        qa = self.imbalance / 8760. * 1000

        if HC:
            # limited by extraction load

            # set length peak
            th = self.peak_extraction_duration

            # Select month with the highest peak load and take both the peak and average load from that month
            month_index = self.get_month_index(self.monthly_peak_extraction,
                                               self.monthly_baseload_extraction)
            qm = self.monthly_average_injection_power[month_index] * 1000.
            qh = self.max_peak_extraction * 1000.

            # correct signs
            qm = -qm
            qa = -qa

        else:
            # limited by injection load

            # set length peak
            th = self.peak_injection_duration

            # Select month with the highest peak load and take both the peak and average load from that month
            month_index = self.get_month_index(self.monthly_peak_injection,
                                               self.monthly_baseload_injection_power)
            qm = self.monthly_average_injection_power[month_index] * 1000.
            qh = self.max_peak_injection * 1000.

        return th, qh, qm, qa

    def _calculate_first_year_params(self, HC: bool) -> tuple:
        """
        This function calculates the parameters for the sizing based on the first year of operation.
        This is needed for the L2 sizing.

        Parameters
        ----------
        HC : bool
            True if the borefield is limited by extraction load

        Returns
        -------
        th, tpm, tcm, qh, qpm, qcm : float
            Peak duration [s], cumulative time passed at the start of the month [s],
            cumulative time passed at the end of the month [s], peak load [W],
            average cumulative load of the past months [W avg],
            average load of the current month [W avg]
        """

        if HC:
            # limited by extraction load

            # set peak length
            th = self.peak_extraction_duration

            # Select month with the highest peak load and take both the peak and average load from that month
            month_index = self.get_month_index(self.monthly_peak_extraction,
                                               self.monthly_baseload_extraction_power)
            qh = self.max_peak_extraction * 1000.

            qm = self.monthly_average_injection_power[month_index] * 1000.

            if month_index < 1:
                qpm = 0
            else:
                qpm = np.sum(self.monthly_average_injection_power[:month_index]) * 1000 / (month_index + 1)

            qm = -qm
        else:
            # limited by injection

            # set peak length
            th = self.peak_injection_duration

            # Select month with the highest peak load and take both the peak and average load from that month
            month_index = self.get_month_index(self.monthly_peak_injection,
                                               self.monthly_baseload_injection_power)
            qh = self.max_peak_injection * 1000.

            qm = self.monthly_average_injection_power[month_index] * 1000.
            if month_index < 1:
                qpm = 0
            else:
                qpm = np.sum(self.monthly_average_injection_power[:month_index]) * 1000 / (month_index + 1)

        tcm = self.time_L3[month_index]
        tpm = self.time_L3[month_index - 1] if month_index > 0 else 0

        return th, tpm, tcm, qh, qpm, qm

    def _check_input(self, load_array: ArrayLike) -> bool:
        """
        This function checks whether the input is valid or not.
        The input is correct if and only if:
        1) the input is a np.ndarray, list or tuple
        2) the length of the input is (a multiple of) 12 or 8760, depending on if it is an hourly load or not
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
            print("The load should be of type np.ndarray, list or tuple.")
            return False
        if self._multiyear:
            if self._hourly:
                if not len(load_array) % 8760 == 0:
                    print("The length of the load should be a multiple of 8760.")
                    return False
            else:
                if not len(load_array) % 12 == 0:
                    print("The length of the load should be a multiple of 12.")
                    return False
        else:
            if self._hourly:
                if not len(load_array) == 8760:
                    print("The length of the load should be 8760.")
                    return False
            else:
                if not len(load_array) == 12:
                    print("The length of the load should be 12.")
                    return False
        if np.min(load_array) < 0:
            print("No value in the load can be smaller than zero.")
            return False
        return True

    def set_results(self, results) -> None:  # pragma: no cover
        pass

    def reset_results(self, min_temperature: float, max_temperature: float) -> None:  # pragma: no cover
        pass

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not np.all(
                self.monthly_peak_injection_simulation_period == other.monthly_peak_injection_simulation_period) or \
                not np.all(
                    self.monthly_peak_extraction_simulation_period == other.monthly_peak_extraction_simulation_period) or \
                not np.all(
                    self.monthly_baseload_extraction_simulation_period == other.monthly_baseload_extraction_simulation_period) or \
                not np.all(
                    self.monthly_baseload_injection_simulation_period == other.monthly_baseload_injection_simulation_period):
            return False

        return True
