import numpy as np

from typing import Union

from sympy import discriminant


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
            Second order heat loss coefficient [W/K²]
        min_delta_T : float
            Minimum temperature difference between the average fluid temperature inside the regeneration object and
            the borefield [K]
        """
        self.power = power
        self.temperature = temperature
        self.a1 = a1
        self.a2 = a2
        self.min_delta_T = min_delta_T

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
        mfr : float
            Mass flow rate through the regeneration technology [kg/s]
        c_p : float
            Specific heat capacity of the fluid [J/(kgK)]

        Returns
        -------
        float
            Regeneration power [W]

        """

        power = 0

        # power due to constant power
        if self.power is not None:
            if isinstance(self.power, (int, float)):
                power += self.power
            else:
                power += self.power[index]
        if self.temperature is None:
            return power

        # power due to temperature difference
        if isinstance(self.temperature, (int, float)):
            ref_temp = self.temperature
        else:
            ref_temp = self.temperature[index]

        delta_T = ref_temp - inlet_temperature

        if abs(delta_T) <= self.min_delta_T and power == 0:
            return power

        effective_ref_temp = (ref_temp - np.sign(delta_T) * self.min_delta_T)

        effective_delta_T = effective_ref_temp - inlet_temperature

        if self.a2 is not None and self.a2 != 0:
            # second degree
            alpha = power + (self.a1 + self.a2 * effective_delta_T) * effective_delta_T
            beta = (-1) * self.a1 / (2 * mfr * c_p) - self.a2 / (mfr * c_p) * effective_delta_T - 1
            gamma = self.a2 / (4 * mfr ** 2 * c_p ** 2)
            D = beta ** 2 - 4 * alpha * gamma

            x1 = ((-1) * beta + np.sqrt(D)) / (2 * gamma)
            x2 = ((-1) * beta - np.sqrt(D)) / (2 * gamma)
            regeneration_power = min((x1, x2), key=abs)

            reference_power = mfr * c_p * effective_delta_T

            regeneration_power = np.clip(regeneration_power, min(power, reference_power), max(power, reference_power))

            return regeneration_power

        # positive when ref temperature (e.g. outside temperature) is higher than the fluid temperature, so injection
        regeneration_power = (power + self.a1 * effective_delta_T) / (1 + self.a1 / (2 * mfr * c_p))
        reference_power = mfr * c_p * effective_delta_T

        regeneration_power = np.clip(regeneration_power, min(power, reference_power), max(power, reference_power))

        return regeneration_power
