import copy

import numpy as np
import matplotlib.pyplot as plt

from typing import Union

from GHEtool.VariableClasses.Efficiency._Efficiency import _Efficiency


def _cop_carnot(temp_eva, temp_cond):
    return (temp_cond + 273.15) / (temp_cond - temp_eva)


class COPSimplified():
    """
    Class for COP efficiency, with dependencies on main average inlet temperature, main average outlet temperature (optional)
    and part-load (optional) conditions.
    """

    def __init__(self, temp_cond: np.ndarray, temp_eva: np.ndarray, power: np.ndarray, efficiency: np.ndarray) -> None:
        """
        Create an efficiency correlation based on the temperature lift.

        Parameters
        ----------
        temp_cond : np.ndarray
            Condenser temperatures.
        temp_eva : np.ndarray
            Evaporator temperatures.
        power : np.ndarray
            Heat pump power values.
        efficiency : np.ndarray
            Heat pump efficiency values.

        Raises
        ------
        ValueError
            If the input arrays do not have equal lengths.
        """
        if not (temp_cond.size == temp_eva.size == power.size == efficiency.size):
            raise ValueError("All input arrays must have equal lengths.")

        temperature_lift = temp_cond - temp_eva
        carnot_efficiency = _cop_carnot(temp_eva, temp_cond)

        relative_difference = efficiency / carnot_efficiency
        self._scatter = np.column_stack((temperature_lift, relative_difference))

        self.model = np.poly1d(np.polyfit(temperature_lift, relative_difference, deg=2))

        order = np.argsort(temperature_lift)
        self._lift_sorted = temperature_lift[order]
        self._power_sorted = power[order]

        # defaults
        self._min_lift = 25
        self._secondary_temp = 35

    def plot_efficiency_curve(self):
        plt.figure()
        plt.scatter([i[0] for i in self._scatter], [i[1] * 100 for i in self._scatter], legend="Data points")

        polyline = np.linspace(35 - 10, 65, 100)
        plt.plot(polyline, self.model(polyline) * 100, legend="Fit")
        plt.xlabel('Temperature lift [°C]')
        plt.ylabel('Real efficiency w.r.t. Carnot COP[%]')
        plt.legend()
        plt.show()

    def _get_efficiency(self,
                        primary_temperature: Union[float, np.ndarray],
                        secondary_temperature: Union[float, np.ndarray] = None,
                        power: Union[float, np.ndarray] = None) -> np.ndarray:
        """
        This function calculates the efficiency, with the help of the correlations it created.

        Parameters
        ----------
        primary_temperature : np.ndarray or float
            Value(s) for the average primary temperature of the heat pump for the efficiency calculation.
        secondary_temperature : np.ndarray or float
            Value(s) for the average secondary temperature of the heat pump for the efficiency calculation.
        power : np.ndarray or float
            Value(s) for the part load data of the heat pump for the efficiency calculation.

        Returns
        -------
        Efficiency
            np.ndarray
        """
        _secondary_temperature = copy.copy(secondary_temperature)
        if secondary_temperature is None:
            _secondary_temperature = self._secondary_temp
        # Ensure a minimum temperature lift of 25 K
        _secondary_temperature = np.maximum(_secondary_temperature, primary_temperature + self._min_lift)
        cop_carnot = _cop_carnot(primary_temperature, _secondary_temperature)

        return cop_carnot * self.model(_secondary_temperature - primary_temperature)

    def _get_max_power(self,
                       primary_temperature: Union[float, np.ndarray],
                       secondary_temperature: Union[float, np.ndarray] = None, **kwargs) -> np.ndarray:
        """
        This function returns the maximum available power for a certain primary and secondary temperature.

        Parameters
        ----------
        primary_temperature : np.ndarray or float
            Value(s) for the average primary temperature of the heat pump for the efficiency calculation.
        secondary_temperature : np.ndarray or float
            Value(s) for the average secondary temperature of the heat pump for the efficiency calculation.

        Raises
        ------
        ValueError
            When secondary_temperature is in the dataset, and it is not provided. Same for power.

        Returns
        -------
        Efficiency
            np.ndarray
        """

        lift = secondary_temperature - primary_temperature

        return np.interp(lift, self._lift_sorted, self._power_sorted)

    def get_COP(self,
                primary_temperature: Union[float, np.ndarray],
                secondary_temperature: Union[float, np.ndarray] = None,
                power: Union[float, np.ndarray] = None) -> np.ndarray:
        """
        This function calculates the COP. This function uses a linear interpolation and sets the out-of-bound values
        to the nearest value in the dataset. This function does hence not extrapolate.

        Parameters
        ----------
        primary_temperature : np.ndarray or float
            Value(s) for the average primary temperature of the heat pump for the COP calculation.
        secondary_temperature : np.ndarray or float
            Value(s) for the average secondary temperature of the heat pump for the COP calculation.
        power : np.ndarray or float
            Value(s) for the part load data of the heat pump for the COP calculation.

        Raises
        ------
        ValueError
            When secondary_temperature is in the dataset, and it is not provided. Same for power.

        Returns
        -------
        COP
            np.ndarray
        """
        return self._get_efficiency(primary_temperature, secondary_temperature, power)

    def get_SCOP(self,
                 power: np.ndarray,
                 primary_temperature: np.ndarray,
                 secondary_temperature: np.ndarray = None
                 ) -> float:
        """
        This function calculates and returns the SCOP.

        Parameters
        ----------
        power : np.ndarray
            Array with the hourly secondary power of the heat pump [kW]
        primary_temperature : np.ndarray
            Values for the average primary temperature of the heat pump for the COP calculation.
        secondary_temperature : np.ndarray
            Values for the average secondary temperature of the heat pump for the COP calculation.

        Raises
        ------
        ValueError
            When the length of all the arrays are not equal

        Returns
        -------
        SCOP
            float
        """

        if len(primary_temperature) != len(power) and (
                secondary_temperature is None or len(secondary_temperature) == len(power)):
            raise ValueError('The hourly arrays should have equal length!')

        cop_array = self.get_COP(primary_temperature, secondary_temperature, power)

        # SCOP = sum(Q)/sum(W)
        w_array = np.array(power) / cop_array

        return np.sum(power) / np.sum(w_array)

    def __export__(self):
        if self._has_part_load:
            return {'type': 'Temperature and part-load dependent COP'}
        return {'type': 'Temperature dependent COP'}


if __name__ == '__main__':
    cop = COPSimplified(
        np.array([35, 45, 55, 60, 65] * 6),
        np.repeat([0, 2, 4, 6, 8, 10], 5),
        np.array(
            [3.52, 3.19, 2.86, 2.65, 2.44, 3.69, 3.36, 3.01, 2.8, 2.61, 3.86, 3.51, 3.16, 2.94, 2.76, 4.02, 3.67, 3.3,
             3.08, 2.88, 4.18, 3.88, 3.44, 3.2, 3.00, 4.33, 3.95, 3.57, 3.33, 3.11]),
        np.array(
            [3.52, 3.19, 2.86, 2.65, 2.44, 3.69, 3.36, 3.01, 2.8, 2.61, 3.86, 3.51, 3.16, 2.94, 2.76, 4.02, 3.67, 3.3,
             3.08, 2.88, 4.18, 3.88, 3.44, 3.2, 3.00, 4.33, 3.95, 3.57, 3.33, 3.11]),
    )
    print(cop.get_COP(10, 35))
    print(cop.get_COP(10, 45))
    print(cop.get_COP(10, 55))
    print(cop.get_COP(10, 60))
    print(cop._get_max_power(10, 60))

    cop.plot_efficiency_curve()
