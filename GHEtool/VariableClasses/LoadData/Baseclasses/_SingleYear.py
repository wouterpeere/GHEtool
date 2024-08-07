import abc

import numpy as np

from abc import ABC


class _SingleYear(ABC):

    def __init__(self, simulation_period: int = 20, start_month: int = 1):

        self._simulation_period = None
        self._start_month = None

    @property
    def start_month(self) -> int:
        """
        This function returns the start month.

        Returns
        -------
        float
            Start month
        """
        return self._start_month

    @start_month.setter
    def start_month(self, month: int) -> None:
        """
        This function sets the start month.

        Parameters
        ----------
        month : int
            Start month (jan: 1, feb: 2 ...)

        Returns
        -------
        None

        Raises
        ----------
        ValueError
            When the start month is smaller than 1, larger than 12 or non-integer
        """

        if not isinstance(month, int) or month < 1 or month > 12:
            raise ValueError(f'The value for month is: {month} which is not an integer in [1,12].')

        self._start_month = month

    @property
    def simulation_period(self) -> int:
        return self._simulation_period

    @simulation_period.setter
    def simulation_period(self, simulation_period: int) -> None:
        if not isinstance(simulation_period, int) or simulation_period < 1:
            raise ValueError(
                f'The value for the simulation period is: {simulation_period} which is not an integer above 1.')
        self._simulation_period = simulation_period

    @abc.abstractmethod
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
