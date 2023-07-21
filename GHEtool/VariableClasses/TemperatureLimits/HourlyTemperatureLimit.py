from GHEtool.VariableClasses.TemperatureLimits._TemperatureLimits import _TemperatureLimits

import numpy as np
from typing import Union
from functools import partial

class HourlyTemperatureLimit(_TemperatureLimits):

    def __init__(self, min_temp: Union[list, np.ndarray], max_temp: Union[list, np.ndarray]):
        """

        Parameters
        ----------
        min_temp : list | np.ndarray
            Array with monthly minimum temperature limit values
        max_temp : list | np.ndarray
            Array with monthly maximum temperature limit values
        """
        super().__init__()
        self.set_min_temperature(min_temp)
        self.set_max_temperature(max_temp)
        self.test = partial(lambda x: print(x))

    def check_input(self, temperature_limit: Union[list, np.ndarray]) -> bool:
        """
        Checks if the input is a list or array with length 8760.

        Parameters
        ----------
        temperature_limit : list, np.ndarray
            Temperature limit

        Returns
        -------
        bool
            True if the input is correct, False otherwise
        """
        return isinstance(temperature_limit, (list, np.ndarray)) and np.size(temperature_limit) == 8760

    def set_max_temperature(self, max_temperature: Union[list, np.ndarray]) -> None:
        """
        Sets the maximum temperature limit of the borefield.

        Parameters
        ----------
        max_temperature : list, np.ndarray
            Maximum temperature limit of the borefield on a monthly basis

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If the max temperature is not a number
        """
        if not self.check_input(max_temperature):
            raise ValueError('Max temperature is not a correct array!')
        self._max_temperature = np.array(max_temperature)
        self.check_max_not_below_min()

    def set_min_temperature(self, min_temperature: Union[list, np.ndarray]) -> None:
        """
        Sets the minimum temperature limit of the borefield.

        Parameters
        ----------
        min_temperature : list, np.ndarray
            Minimum temperature limit of the borefield on a monthly basis

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If the max temperature is not a number
        """

        if not self.check_input(min_temperature):
            raise ValueError('Min temperature is not a correct array!')
        self._min_temperature = np.array(min_temperature)
        self.check_max_not_below_min()

    def get_min_temperature_monthly(self, simulation_period: int) -> np.ndarray:
        """
        Get the monthly minimum temperature limit for the whole simulation period.

        Parameters
        ----------
        simulation_period : int
            Simulation period in years

        Raises
        ------
        RuntimeError
            Error since it is impossible to get monthly temperature limits if they are given with an hourly resolution.
        """
        raise RuntimeError('It is impossible to get monthly temperature limits if they are given with an hourly resolution.')

    def get_min_temperature_hourly(self, simulation_period: int, UPM=None) -> np.ndarray:
        """
        Get the hourly minimum temperature limit for the whole simulation period.

        Parameters
        ----------
        simulation_period : int
            Simulation period in years
        UPM
            Ignored

        Returns
        -------
        Hourly minimum temperature limit : np.ndarray
        """
        return np.tile(self._min_temperature, simulation_period)

    def get_max_temperature_monthly(self, simulation_period: int) -> np.ndarray:
        """
        Get the monthly maximum temperature limit for the whole simulation period.

        Parameters
        ----------
        simulation_period : int
            Simulation period in years

        Raises
        ------
        RuntimeError
            Error since it is impossible to get monthly temperature limits if they are given with an hourly resolution.
        """
        raise RuntimeError('It is impossible to get monthly temperature limits if they are given with an hourly resolution.')

    def get_max_temperature_hourly(self, simulation_period: int, UPM=None) -> np.ndarray:
        """
        Get the hourly maximum temperature limit for the whole simulation period.

        Parameters
        ----------
        simulation_period : int
            Simulation period in years
        UPM
            Ignored

        Returns
        -------
        Hourly maximum temperature limit : np.ndarray
        """
        return np.tile(self._max_temperature, simulation_period)
