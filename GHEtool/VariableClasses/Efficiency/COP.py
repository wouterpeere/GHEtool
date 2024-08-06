import numpy as np

from typing import Union

from GHEtool.VariableClasses.Efficiency._Efficiency import _Efficiency


class COP(_Efficiency):
    """
    Class for COP efficiency, with dependencies on main average inlet temperature, main average outlet temperature (optional)
    and part-load (optional) conditions.
    """

    def __init__(self,
                 data: np.ndarray,
                 range_avg_primary_temperature: np.ndarray,
                 range_avg_secondary_temperature: np.ndarray = None,
                 range_part_load: np.ndarray = None):
        """

        Parameters
        ----------
         data : np.ndarray
            Array with all the interpolation data, at least 1D, but up to 3D depending on whether the range for
            average secondary temperatures or the part load data is provided.
        range_avg_primary_temperature : np.ndarray
            Array with all the values for the average primary temperature of the heat pump that are present
            in the data.
        range_avg_secondary_temperature : np.ndarray
            Array with all the values for the average secondary temperature of the heat pump that are present
            in the data. (Optional)
        range_part_load : np.ndarray
            Array with all the values for the part-load data of the heat pump that are present in the data.
            All these values have to be between 0-1. (Optional).

        Raises
        ------
        ValueError
            When the shape of the data does not equal the provided ranges.

        """
        super().__init__(data, range_avg_primary_temperature, range_avg_secondary_temperature, range_part_load)

    def get_COP(self,
                primary_temperature: Union[float, np.ndarray],
                secondary_temperature: Union[float, np.ndarray] = None,
                part_load: Union[float, np.ndarray] = None) -> np.ndarray:
        """
        This function calculates the COP. This function uses a linear interpolation and sets the out-of-bound values
        to the nearest value in the dataset. This function does hence not extrapolate.

        Parameters
        ----------
        primary_temperature : np.ndarray or float
            Value(s) for the average primary temperature of the heat pump for the COP calculation.
        secondary_temperature : np.ndarray or float
            Value(s) for the average secondary temperature of the heat pump for the COP calculation.
        part_load : np.ndarray or float
            Value(s) for the part load data of the heat pump for the COP calculation.

        Raises
        ------
        ValueError
            When secondary_temperature is in the dataset, and it is not provided. Same for part_load.

        Returns
        -------
        COP
            np.ndarray
        """
        return self._get_efficiency(primary_temperature, secondary_temperature, part_load)

    def get_SCOP(self,
                 power: np.ndarray,
                 nom_power: float,
                 primary_temperature: np.ndarray,
                 secondary_temperature: np.ndarray = None
                 ) -> float:
        """
        This function calculates and returns the SCOP.

        Parameters
        ----------
        power : np.ndarray
            Array with the hourly secondary power of the heat pump [kW]
        nom_power : float
            Nominal power of the heat pump [kW]
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

        part_load = np.array(power) / nom_power
        cop_array = self.get_COP(primary_temperature, secondary_temperature, part_load)

        # SCOP = sum(Q)/sum(W)
        w_array = np.array(power) / cop_array

        return np.sum(power) / np.sum(w_array)
