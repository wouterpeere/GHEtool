from GHEtool.VariableClasses.TemperatureLimits._TemperatureLimits import _TemperatureLimits

import numpy as np


class ConstantTemperatureLimit(_TemperatureLimits):

    def __init__(self, min_temp: float = 0, max_temp: float = 16):
        super().__init__()
        self.set_max_temperature(max_temp)
        self.set_min_temperature(min_temp)

    def check_input(self, temperature_limit: float) -> bool:
        """
        Checks if the input is a constant.

        Parameters
        ----------
        temperature_limit : float
            Temperature limit

        Returns
        -------
        bool
            True if the input is correct, False otherwise
        """
        return isinstance(temperature_limit, (float, int))

    def set_max_temperature(self, max_temperature: float) -> None:
        """
        Sets the maximum temperature limit of the borefield.

        Parameters
        ----------
        max_temperature : float
            Maximum temperature limit of the borefield

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If the max temperature is not a number
        """
        if not self.check_input(max_temperature):
            raise ValueError('Max temperature is not a number!')
        self._max_temperature = max_temperature
        self.check_max_not_below_min()

    def set_min_temperature(self, min_temperature: float) -> None:
        """
        Sets the minimum temperature limit of the borefield.

        Parameters
        ----------
        min_temperature : float
            Minimum temperature limit of the borefield

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If the max temperature is not a number
        """

        if not self.check_input(min_temperature):
            raise ValueError('Min temperature is not a number!')
        self._min_temperature = min_temperature
        self.check_max_not_below_min()

    def get_min_temperature_monthly(self, simulation_period: int) -> np.ndarray:
        """
        Get the monthly minimum temperature limit for the whole simulation period.

        Parameters
        ----------
        simulation_period : int
            Simulation period in years

        Returns
        -------
        Monthly minimum temperature limit : np.ndarray
        """
        return np.full(simulation_period * 12, self._min_temperature)

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
        return np.full(simulation_period * 8760, self._min_temperature)

    def get_max_temperature_monthly(self, simulation_period: int) -> np.ndarray:
        """
        Get the monthly maximum temperature limit for the whole simulation period.

        Parameters
        ----------
        simulation_period : int
            Simulation period in years

        Returns
        -------
        Monthly maximum temperature limit : np.ndarray
        """
        return np.full(simulation_period * 12, self._max_temperature)

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
        return np.full(simulation_period * 8760, self._max_temperature)
