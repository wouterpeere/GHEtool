import numpy as np

from typing import Union

from GHEtool.VariableClasses.Efficiency.EER import EER
from GHEtool.VariableClasses.Efficiency.SEER import SEER


class EERCombined:
    """
    Class for EER efficiency of combined active and passive cooling, with dependencies on main average inlet temperature,
    main average outlet temperature (optional) and part-load (optional) conditions.
    """

    def __init__(self,
                 efficiency_passive_cooling: Union[EER, SEER, float],
                 efficiency_active_cooling: Union[EER, SEER, float],
                 threshold_temperature: float = None,
                 months_active_cooling: np.ndarray = None):
        """

        Parameters
        ----------
        efficiency_passive_cooling : EER, SEER or float
            The efficiency class for the passive cooling. Floats will be converted to SEER.
        efficiency_active_cooling : EER, SEER or float
            The efficiency class for the active cooling. Floats will be converted to SEER.
        threshold_temperature : float
            Temperature threshold above which active cooling is chosen.
        months_active_cooling : np.ndarray
            Months at which by default there is active cooling (jan:1, feb:2 etc.).

        Raises
        ------
        ValueError
            If neither a threshold_temperature nor months_active_cooling is provided.
        """

        self.efficiency_passive_cooling = efficiency_passive_cooling
        self.efficiency_active_cooling = efficiency_active_cooling
        self.threshold_temperature = threshold_temperature
        self.time_active_cooling = months_active_cooling

        if isinstance(efficiency_active_cooling, (float, int)):
            self.efficiency_active_cooling = SEER(efficiency_active_cooling)

        if isinstance(efficiency_passive_cooling, (float, int)):
            self.efficiency_passive_cooling = SEER(efficiency_passive_cooling)

        if threshold_temperature is None and months_active_cooling is None:
            raise ValueError('Please set either a threshold temperature or the months for active cooling.')

    def _get_EER_active(self, primary_temperature: Union[float, np.ndarray],
                        secondary_temperature: Union[float, np.ndarray] = None,
                        power: Union[float, np.ndarray] = None):
        """
        This function calculates the EER for active cooling.
        This function uses a linear interpolation and sets the out-of-bound values
        to the nearest value in the dataset. This function does hence not extrapolate.

        Parameters
        ----------
        primary_temperature : np.ndarray or float
            Value(s) for the average primary temperature of the heat pump for the EER calculation.
        secondary_temperature : np.ndarray or float
            Value(s) for the average secondary temperature of the heat pump for the EER calculation.
        power : np.ndarray or float
            Value(s) for the part load data of the heat pump for the EER calculation.

        Raises
        ------
        ValueError
            When secondary_temperature is in the dataset, and it is not provided. Same for power.

        Returns
        -------
        EER
            np.ndarray
        """
        return self.efficiency_active_cooling.get_EER(primary_temperature, secondary_temperature, power)

    def _get_EER_passive(self, primary_temperature: Union[float, np.ndarray],
                         secondary_temperature: Union[float, np.ndarray] = None,
                         power: Union[float, np.ndarray] = None):
        """
        This function calculates the EER for passive cooling.
        This function uses a linear interpolation and sets the out-of-bound values
        to the nearest value in the dataset. This function does hence not extrapolate.

        Parameters
        ----------
        primary_temperature : np.ndarray or float
            Value(s) for the average primary temperature of the heat pump for the EER calculation.
        secondary_temperature : np.ndarray or float
            Value(s) for the average secondary temperature of the heat pump for the EER calculation.
        power : np.ndarray or float
            Value(s) for the part load data of the heat pump for the EER calculation.

        Raises
        ------
        ValueError
            When secondary_temperature is in the dataset, and it is not provided. Same for power.

        Returns
        -------
        EER
            np.ndarray
        """
        return self.efficiency_passive_cooling.get_EER(primary_temperature, secondary_temperature, power)

    def get_EER(self,
                primary_temperature: Union[float, np.ndarray],
                secondary_temperature: Union[float, np.ndarray] = None,
                power: Union[float, np.ndarray] = None,
                month_indices: Union[float, np.ndarray] = None) -> EER | float:
        """
        This function calculates the EER. This function uses a linear interpolation and sets the out-of-bound values
        to the nearest value in the dataset. This function does hence not extrapolate.

        Parameters
        ----------
        primary_temperature : np.ndarray or float
            Value(s) for the average primary temperature of the heat pump for the EER calculation.
        secondary_temperature : np.ndarray or float
            Value(s) for the average secondary temperature of the heat pump for the EER calculation.
        power : np.ndarray or float
            Value(s) for the part load data of the heat pump for the EER calculation.
        month_indices : np.ndarray or float
            Array with all the monthly indices, after correction for the start month. Should be the same length as the
            other input parameters

        Raises
        ------
        ValueError
            When secondary_temperature is in the dataset, and it is not provided. Same for power.

        Returns
        -------
        EER
            np.ndarray
        """

        if isinstance(primary_temperature, (float, int)):
            # check temperature threshold
            active_cooling_bool = False
            if self.threshold_temperature is not None and primary_temperature > self.threshold_temperature:
                active_cooling_bool = True

            if not active_cooling_bool and self.time_active_cooling is not None:
                if month_indices is None:
                    raise ValueError('Please provide a month value, for otherwise the system cannot decide if it is '
                                     'active or passive cooling.')
                active_cooling_bool = month_indices in self.time_active_cooling

            if active_cooling_bool:
                return self.efficiency_active_cooling.get_EER(primary_temperature, secondary_temperature, power)
            return self.efficiency_passive_cooling.get_EER(primary_temperature, secondary_temperature, power)

        # now for monthly loads
        active_cooling_eer = self.efficiency_active_cooling.get_EER(primary_temperature, secondary_temperature, power)
        passive_cooling_eer = self.efficiency_passive_cooling.get_EER(primary_temperature, secondary_temperature, power)

        active_cooling_bool = np.full(primary_temperature.shape, False)

        if self.threshold_temperature is not None:
            active_cooling_bool = primary_temperature > self.threshold_temperature

        if self.time_active_cooling is not None:
            if month_indices is None:
                raise ValueError('Please provide a month value, for otherwise the system cannot decide if it is '
                                 'active or passive cooling.')
            active_cooling_bool = np.add(active_cooling_bool, np.isin(month_indices, self.time_active_cooling))

        # select correct data
        return active_cooling_eer * active_cooling_bool + passive_cooling_eer * np.invert(active_cooling_bool)

    def get_SEER(self,
                 power: np.ndarray,
                 primary_temperature: np.ndarray,
                 secondary_temperature: np.ndarray = None,
                 month_indices: Union[float, np.ndarray] = None) -> float:
        """
        This function calculates and returns the SEER.

        Parameters
        ----------
        power : np.ndarray
            Array with the hourly secondary power of the heat pump [kW]
        primary_temperature : np.ndarray
            Values for the average primary temperature of the heat pump for the EER calculation.
        secondary_temperature : np.ndarray
            Values for the average secondary temperature of the heat pump for the EER calculation.
        month_indices : np.ndarray or float
            Array with all the monthly indices, after correction for the start month. Should be the same length as the
            other input parameters
        Raises
        ------
        ValueError
            When the length of all the arrays are not equal

        Returns
        -------
        SEER
            float
        """

        if len(primary_temperature) != len(power) and (
                secondary_temperature is None or len(secondary_temperature) == len(power)):
            raise ValueError('The hourly arrays should have equal length!')

        eer_array = self.get_EER(primary_temperature, secondary_temperature, power, month_indices)

        # SEER = sum(Q)/sum(W)
        w_array = np.array(power) / eer_array

        return np.sum(power) / np.sum(w_array)
