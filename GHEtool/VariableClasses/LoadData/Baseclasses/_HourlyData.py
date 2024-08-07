import abc

import numpy as np

from ._MonthlyData import _MonthlyData
from abc import ABC
from typing import Tuple


class _HourlyData(_MonthlyData, ABC):

    def __init__(self):
        _MonthlyData.__init__(self)
        self.hourly_resolution = True

    @abc.abstractmethod
    def hourly_injection_load_simulation_period(self) -> np.ndarray:
        """

        Returns
        -------

        """

    @abc.abstractmethod
    def hourly_extraction_load_simulation_period(self) -> np.ndarray:
        """

        Returns
        -------

        """

    @property
    def hourly_injection_load(self) -> np.ndarray:
        """
        This function returns the hourly injection load in kWh/h.

        Returns
        -------
        hourly injection : np.ndarray
            Hourly injection values [kWh/h] for one year, so the length of the array is 8760
        """
        return np.mean(self.hourly_injection_load_simulation_period.reshape((self.simulation_period, 8760)), axis=0)

    @property
    def hourly_extraction_load(self) -> np.ndarray:
        """
        This function returns the hourly extraction load in kWh/h.

        Returns
        -------
        hourly extraction : np.ndarray
            Hourly extraction values [kWh/h] for one year, so the length of the array is 8760
        """
        return np.mean(self.hourly_extraction_load_simulation_period.reshape((self.simulation_period, 8760)), axis=0)

    @property
    def hourly_load_simulation_period(self) -> np.ndarray:
        """
        This function calculates the resulting hourly load in kW for the whole simulation period.
        A negative values means the borefield is extraction dominated.

        Returns
        -------
        resulting hourly load : np.ndarray
        """
        return self.hourly_injection_load_simulation_period - self.hourly_extraction_load_simulation_period

    @property
    def monthly_baseload_injection_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly injection baseload in kWh/month for the whole simulation period.

        Returns
        -------
        baseload injection : np.ndarray
            baseload injection for the whole simulation period
        """
        return self.resample_to_monthly(self.hourly_injection_load_simulation_period)[1]

    @property
    def monthly_baseload_extraction_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly extraction baseload in kWh/month for the whole simulation period.

        Returns
        -------
        baseload extraction : np.ndarray
            baseload extraction for the whole simulation period
        """
        return self.resample_to_monthly(self.hourly_extraction_load_simulation_period)[1]

    @property
    def monthly_peak_injection_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly injection peak in kW/month for the whole simulation period.

        Returns
        -------
        peak injection : np.ndarray
            peak injection for the whole simulation period
        """
        return self.resample_to_monthly(self.hourly_injection_load_simulation_period)[0]

    @property
    def monthly_peak_extraction_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly extraction peak in kW/month for the whole simulation period.

        Returns
        -------
        peak extraction : np.ndarray
            peak extraction for the whole simulation period
        """
        return self.resample_to_monthly(self.hourly_extraction_load_simulation_period)[0]

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
            self.hourly_injection_load_simulation_period - self.hourly_extraction_load_simulation_period) / self.simulation_period

    @property
    def max_peak_injection(self) -> float:
        """
        This returns the max peak injection in kW.

        Returns
        -------
        max peak injection : float
        """
        return np.max(self.hourly_injection_load_simulation_period)

    @property
    def max_peak_extraction(self) -> float:
        """
        This returns the max peak extraction in kW.

        Returns
        -------
        max peak extraction : float
        """
        return np.max(self.hourly_extraction_load_simulation_period)

    def resample_to_monthly(self, hourly_load: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        This function resamples an hourly_load to monthly peaks (kW/month) and baseloads (kWh/month).

        Parameters
        ----------
        hourly_load : np.ndarray
            Hourly loads in kWh/h

        Returns
        -------
        peak loads [kW], monthly average loads [kWh/month] : np.ndarray, np.ndarray
        """

        data = np.array_split(hourly_load, np.cumsum(np.tile(self.UPM, self.simulation_period))[:-1])

        if self.all_months_equal:
            return np.max(data, axis=1), np.sum(data, axis=1)

        return np.array([np.max(i) for i in data]), np.array([np.sum(i) for i in data])
