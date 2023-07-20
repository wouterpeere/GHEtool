import abc

import numpy as np

from GHEtool.VariableClasses.BaseClass import BaseClass


class _TemperatureLimits(BaseClass, abc.ABC):
    """
    Contains information regarding the temperature limits of the borefield.
    """

    def __init__(self):
        self.constant_limits = False
        # TODO check that L2 does not work with non-constant temperature limits

    @abc.abstractmethod
    def set_max_temperature(self, max_temperature):
        """

        Parameters
        ----------
        max_temperature

        Returns
        -------

        """

    @abc.abstractmethod
    def set_min_temperature(self, min_temperature):
        """

        Parameters
        ----------
        min_temperature

        Returns
        -------

        """

    @abc.abstractmethod
    def _min_temperature_monthly(self) -> np.ndarray:
        """

        Returns
        -------

        """

    @abc.abstractmethod
    def _min_temperature_hourly(self) -> np.ndarray:
        """

        Returns
        -------

        """

    @abc.abstractmethod
    def _max_temperature_monthly(self) -> np.ndarray:
        """

        Returns
        -------

        """

    @abc.abstractmethod
    def _max_temperature_hourly(self) -> np.ndarray:
        """

        Returns
        -------

        """

    def get_min_temperature_monthly(self, simulation_period: int) -> np.ndarray:
        """

        Returns
        -------

        """
        return np.tile(self._min_temperature_monthly, simulation_period)

    def get_min_temperature_hourly(self, simulation_period: int) -> np.ndarray:
        """

        Returns
        -------

        """
        return np.tile(self._min_temperature_hourly, simulation_period)

    def get_max_temperature_monthly(self, simulation_period: int) -> np.ndarray:
        """

        Returns
        -------

        """
        return np.tile(self._max_temperature_monthly, simulation_period)

    def get_max_temperature_hourly(self, simulation_period: int) -> np.ndarray:
        """

        Returns
        -------

        """
        return np.tile(self._max_temperature_hourly, simulation_period)

# TODO monthly can go to hourly, not vice versa!