import numpy as np

from typing import Union


class Regeneration:

    def __init__(self, power: Union[float, np.ndarray] = None, temperature: Union[float, np.ndarray] = None,
                 a1: float = 0, a2: float = 0, min_delta_T: float = 0):
        """
        This defines the regeneration object.

        Parameters
        ----------
        power : Union[float, np.ndarray]
            Constant power or array of power available for regeneration [W] (Injection is positive)
        temperature : Union[float, np.ndarray]
            Reference temperature for regeneration w.r.t. temperature (eg. dry coolers) [K]
        a1 : float
            First order heat loss coefficient [W/K]
        a2 : float
            Second order heat loss coefficient [W/K]
        min_delta_T : float
            Minimum temperature difference between the average fluid temperature inside the regeneration object and
            the borefield [K]
        """
        self.power = power
        self.temperature = temperature
        self.a1 = a1
        self.a2 = a2
        self.min_delta_T = min_delta_T

    def get_regeneration_power(self, index: int, fluid_temperature: float) -> float:
        """
        This function returns the regeneration power at index index for a given temperature.
        The regeneration power is positive for injection.

        Parameters
        ----------
        index : int
            Index for the power and temperature array
        fluid_temperature : float
            Average fluid temperature [°C]

        Returns
        -------
        float
            Regeneration power [W]

        """

        power = 0

        # power due to constant power
        if self.power is not None:
            if isinstance(self.power, (int, float)):
                power += power
            else:
                power += self.power[index]
        if self.temperature is None:
            return power

        # power due to temperature difference
        if isinstance(self.temperature, (int, float)):
            ref_temp = self.temperature
        else:
            ref_temp = self.temperature[index]

        if np.abs(ref_temp - fluid_temperature) < self.min_delta_T:
            return power

        # positive when ref temperature (eg. outside temperature) is higher than the fluid temperature, so injection
        power += (ref_temp - fluid_temperature) * self.a1 + (ref_temp - fluid_temperature) ** 2 * self.a2

        return power

    def get_regeneration_power_inlet(self, index: int, inlet_temperature: float, mfr: float, c_p: float) -> float:
        """
        This function returns the regeneration power at index index for a given temperature.
        The regeneration power is positive for injection.

        Parameters
        ----------
        index : int
            Index for the power and temperature array
        inlet_temperature : float
            Inlet fluid temperature [°C]

        Returns
        -------
        float
            Regeneration power [W]

        """

        power = 0

        # power due to constant power
        if self.power is not None:
            if isinstance(self.power, (int, float)):
                power += power
            else:
                power += self.power[index]
        if self.temperature is None:
            return power

        # power due to temperature difference
        if isinstance(self.temperature, (int, float)):
            ref_temp = self.temperature
        else:
            ref_temp = self.temperature[index]

        if np.abs(ref_temp - inlet_temperature) < self.min_delta_T:
            return power

        # positive when ref temperature (eg. outside temperature) is higher than the fluid temperature, so injection
        power = (self.power[index] + self.a1 * (ref_temp - inlet_temperature)) / (1 + self.a1 / (2 * mfr * c_p))

        return power
