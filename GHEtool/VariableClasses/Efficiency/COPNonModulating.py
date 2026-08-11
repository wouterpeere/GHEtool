import copy

import numpy as np
import matplotlib.pyplot as plt

from GHEtool.VariableClasses.Efficiency.COP import COP
from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator
from scipy.spatial import QhullError
from typing import Union


def _cop_carnot(temp_eva: Union[float, np.ndarray], temp_cond: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    This function calculates the Carnot efficiency.

    Parameters
    ----------
    temp_eva : float, np.ndarray
        Average fluid temperature at the evaporator [°C]
    temp_cond : float, np.ndarray
        Average fluid temperature at the condenser [°C]

    Returns
    -------
    float, np.ndarray
        Carnot efficiency [-]

    Raises
    ------
    ValueError
        When the temperature at the condenser is lower than at the evaporator.
    """
    if np.all(temp_cond < temp_eva):
        raise ValueError('The temperature at the condenser should be higher than the evaporator.')
    return (temp_cond + 273.15) / (temp_cond - temp_eva)


class COPNonModulating:
    """
    Class for COP efficiency for non-modulating heat pumps.
    The efficiency is calculated based on at least three measuring points and use these points to correct
    the carnot efficiency of the entire working range.
    """

    def __init__(self, temp_cond: np.ndarray, temp_eva: np.ndarray, power: np.ndarray, efficiency: np.ndarray,
                 min_temperature_lift: float = 20, min_condenser_temperature: float = 20,
                 max_condenser_temperature: float = 60,
                 default_condenser_temperature: float = 33.5) -> None:
        """
        Create an efficiency correlation based on the temperature lift.

        Parameters
        ----------
        temp_cond : np.ndarray
            Condenser temperatures [°C]
        temp_eva : np.ndarray
            Evaporator temperatures [°C]
        power : np.ndarray
            Heat pump power values [kW]
        efficiency : np.ndarray
            Heat pump efficiency values [-]
        min_temperature_lift : float
            The minimum temperature lift between the evaporator and condenser side of the heat pump [°C]
        min_condenser_temperature : float
            The lowest (average) temperature the heat pump can deliver at the condenser [°C]
        max_condenser_temperature : float
            The highest (average) temperature the heat pump can deliver at the condenser [°C]
        default_condenser_temperature : float
            The default average condenser temperature [°C]

        Raises
        ------
        ValueError
            If the input arrays do not have equal lengths.
            If there are less than 3 different temperatures lifts defined.
            If not all condenser fluid temperatures are above the evaporator ones.
            Not all powers and efficiencies are above 0.
        """
        if not (temp_cond.size == temp_eva.size == power.size == efficiency.size):
            raise ValueError("All input arrays must have equal lengths.")

        if np.unique(temp_cond - temp_eva).size < 3:
            raise ValueError("At least three different temperature lifts should be defined.")

        if not np.all(temp_cond > temp_eva):
            raise ValueError("All condenser fluid temperatures should be above the evaporator ones.")

        if not (np.all(efficiency > 0) and np.all(power > 0)):
            raise ValueError('All efficiencies and powers should be larger than 0.')

        # store variables
        self._temp_cond = temp_cond
        self._temp_eva = temp_eva
        self._power = power
        self._efficiency = efficiency

        temperature_lift = temp_cond - temp_eva
        carnot_efficiency = _cop_carnot(temp_eva, temp_cond)

        relative_difference = efficiency / carnot_efficiency
        self._scatter = np.column_stack((temperature_lift, relative_difference))

        self.model = np.poly1d(np.polyfit(temperature_lift, relative_difference, deg=2))
        self._r_squared = 1 - np.sum((relative_difference - self.model(temperature_lift)) ** 2) / np.sum(
            (relative_difference - np.mean(relative_difference)) ** 2)

        self._power_points = np.column_stack((temp_eva, temp_cond))
        try:
            self._power_linear_interp = LinearNDInterpolator(self._power_points, power)
        except QhullError:  # pragma: no cover
            # degenerate/collinear point set — Delaunay can't triangulate;
            # fall back to nearest-neighbor everywhere
            self._power_linear_interp = None
        self._power_nearest_interp = NearestNDInterpolator(self._power_points, power)

        # defaults
        self._min_lift = min_temperature_lift
        self._min_temperature = min_condenser_temperature
        self._max_temperature = max_condenser_temperature
        self._secondary_temp = default_condenser_temperature

    def plot_efficiency_curve(self):
        """
        This function plots the given efficiency of the
        """
        plt.figure()
        plt.scatter([i[0] for i in self._scatter], [i[1] * 100 for i in self._scatter], label="Data points")

        polyline = np.linspace(35 - 10, 65, 100)
        plt.plot(polyline, self.model(polyline) * 100, label="Fit")
        plt.xlabel('Temperature lift [°C]')
        plt.ylabel('Real efficiency w.r.t. Carnot COP [%]')
        plt.legend()
        plt.show()

    def _fit_within_range(self, secondary_temperature: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        This function makes sure the secondary temperatures are within the minimum and maximum condenser temperatures
        and that the minimum lift is also ensured.

        Parameters
        ----------
        secondary_temperature : float, np.ndarray
            Average fluid temperatures at the condenser side of the heat pump [°C]

        Returns
        -------
        secondary_temperatures : float, np.ndarray
            Average fluid temperatures at the condenser side of the heat pump [°C]
        """

        # Make sure the secondary temperature is within the operating range
        secondary_temperature = np.maximum(secondary_temperature, self._min_temperature)
        secondary_temperature = np.minimum(secondary_temperature, self._max_temperature)

        return secondary_temperature

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

        # Make sure the temperatures are within the working range of the heat pump
        _secondary_temperature = self._fit_within_range(_secondary_temperature)

        # Calculate Carnot efficiency
        cop_carnot = _cop_carnot(primary_temperature, _secondary_temperature)

        return cop_carnot * self.model(_secondary_temperature - primary_temperature)

    def _get_max_power(self,
                       primary_temperature: Union[float, np.ndarray],
                       secondary_temperature: Union[float, np.ndarray] = None, **kwargs) -> np.ndarray:
        """
        This function returns the maximum available power for a certain primary and secondary temperature,
        using Delaunay-based linear interpolation over the raw (evaporator, condenser) scatter, with
        nearest-neighbor fallback outside the convex hull (no extrapolation).

        Parameters
        ----------
        primary_temperature : np.ndarray or float
            Value(s) for the average primary (evaporator) temperature of the heat pump.
        secondary_temperature : np.ndarray or float
            Value(s) for the average secondary (condenser) temperature of the heat pump.

        Returns
        -------
        Max power
            np.ndarray or float
        """
        if secondary_temperature is None:
            secondary_temperature = self._secondary_temp
        secondary_temperature = self._fit_within_range(copy.copy(secondary_temperature))

        primary_arr, secondary_arr = np.broadcast_arrays(
            np.asarray(primary_temperature, dtype=float),
            np.asarray(secondary_temperature, dtype=float)
        )
        scalar_input = primary_arr.ndim == 0

        query = np.column_stack((np.atleast_1d(primary_arr).ravel(), np.atleast_1d(secondary_arr).ravel()))

        if self._power_linear_interp is not None:
            result = self._power_linear_interp(query)
        else:  # pragma: no cover
            result = np.full(len(query), np.nan)

        nan_mask = np.isnan(result)
        if nan_mask.any():  # pragma: no cover
            result[nan_mask] = self._power_nearest_interp(query[nan_mask])

        result = result.reshape(primary_arr.shape)
        return result.item() if scalar_input else result

    def get_COP(self,
                primary_temperature: Union[float, np.ndarray],
                secondary_temperature: Union[float, np.ndarray] = None,
                power: Union[float, np.ndarray] = None) -> np.ndarray:
        """
        This function calculates the COP using the quadratic model and the Carnot efficiency.

        Parameters
        ----------
        primary_temperature : np.ndarray or float
            Value(s) for the average primary temperature of the heat pump for the COP calculation.
        secondary_temperature : np.ndarray or float
            Value(s) for the average secondary temperature of the heat pump for the COP calculation.
        power : np.ndarray or float
            Value(s) for the part load data of the heat pump for the COP calculation. (Not used)

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

    def get_SCOP(self, power: np.ndarray, primary_temperature: np.ndarray,
                 secondary_temperature: np.ndarray = None) -> float:
        """
        This function calculates and returns the SCOP.

        Parameters
        ----------
        power : np.ndarray
            Array with the hourly secondary power of the heat pump [kW] (not used)
        primary_temperature : np.ndarray
            Values for the average primary temperature of the heat pump for the COP calculation [°C].
        secondary_temperature : np.ndarray
            Values for the average secondary temperature of the heat pump for the COP calculation [°C].

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

    def convert_to_eer_non_modulating(self, default_evaporator_temperature: float = 12):
        """
        This function converts the current class to its equivalent EER class.

        Parameters
        ----------
        default_evaporator_temperature : float
            Default average fluid temperature in the evaporator during cooling [°C]

        Returns
        -------
        EERNonModulating
        """
        from GHEtool.VariableClasses.Efficiency.EERNonModulating import EERNonModulating

        eer = EERNonModulating(
            temp_cond=self._temp_cond,
            temp_eva=self._temp_eva,
            efficiency=self._efficiency - 1,  # EER = COP -1
            power=self._power * (1 - 1 / self._efficiency),  # Ql = Qh(1-1/COP)
            min_temperature_lift=self._min_lift,
            max_condenser_temperature=self._max_temperature,
            min_condenser_temperature=self._min_temperature,
            default_evaporator_temperature=default_evaporator_temperature
        )
        return eer

    def convert_to_regular_COP(self, min_evaporator_temperature: float, max_evaporator_temperature: float) -> COP:
        """
        This function converts the current class to an equivalent COP class by creating an interpolation grid.

        Parameters
        ----------
        min_evaporator_temperature : float
            Minimum evaporator temperature to consider [°C]
        max_evaporator_temperature : float
            Maximum evaporator temperature to consider [°C]

        Returns
        -------
        COP
            COP object with the efficiency of the heat pump
        """

        eva_temperatures = np.arange(min_evaporator_temperature, max_evaporator_temperature, 1)
        cond_temperatures = np.arange(self._min_temperature, self._max_temperature, 1)

        data = []
        eff = []
        for eva_temp in eva_temperatures:
            for cond_temp in cond_temperatures:
                data.append([eva_temp, cond_temp, self._get_max_power(eva_temp, cond_temp)])
                eff.append(self._get_efficiency(eva_temp, cond_temp))

        return COP(np.array(eff), np.array(data), True, True,
                   default_secondary_temperature=self._secondary_temp)

    def __export__(self):
        return {'type': 'Non-modulating COP'}
