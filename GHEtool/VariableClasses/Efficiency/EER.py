import numpy as np

from scipy import interpolate
from typing import Union

from GHEtool.VariableClasses.Efficiency._Efficiency import _EER


class EER(_EER):
    """
    Class for EER efficiency, with dependencies on main average inlet temperature, main average outlet temperature (optional)
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
        self._data = data
        self._range_secondary: bool = range_avg_secondary_temperature is not None
        self._range_part_load: bool = range_part_load is not None
        self.__range_primary_ = range_avg_primary_temperature
        self.__range_secondary_ = range_avg_secondary_temperature
        self.__range_part_load_ = range_part_load

        # set points
        self._points = [range_avg_primary_temperature]

        if range_avg_secondary_temperature is not None:
            self._points.append(range_avg_secondary_temperature)
        if range_part_load is not None:
            self._points.append(range_part_load)

        # test if data is correct provided

        if range_avg_secondary_temperature is None and range_part_load is None:
            if np.shape(self._points[0]) != np.shape(self._data):
                raise ValueError('Please make sure the dimensions of the dataset are correct!')
            return
        if self._range_part_load and self._range_secondary:
            try:
                interpolate.interpn(self._points, self._data, (1, 1, 1), bounds_error=False)
                return
            except ValueError:
                raise ValueError('Please make sure the dimensions of the dataset are correct!')
        if np.shape(self._points) != np.shape(self._data):
            raise ValueError('Please make sure the dimensions of the dataset are correct!')

    def get_EER(self,
                primary_temperature: Union[float, np.ndarray],
                secondary_temperature: Union[float, np.ndarray] = None,
                part_load: Union[float, np.ndarray] = None) -> np.ndarray:
        """
        This function calculates the EER. This function uses a linear interpolation and sets the out-of-bound values
        to the nearest value in the dataset. This function does hence not extrapolate.

        Parameters
        ----------
        primary_temperature : np.ndarray or float
            Value(s) for the average primary temperature of the heat pump for the EER calculation.
        secondary_temperature : np.ndarray or float
            Value(s) for the average secondary temperature of the heat pump for the EER calculation.
        part_load : np.ndarray or float
            Value(s) for the part load data of the heat pump for the EER calculation.

        Raises
        ------
        ValueError
            When secondary_temperature is in the dataset, and it is not provided. Same for part_load.

        Returns
        -------
        EER
            np.ndarray
        """
        # check if all the required values are present
        if self._range_secondary != (secondary_temperature is not None):
            if self._range_secondary:
                raise ValueError('The EER class requires a value for the secondary temperature.')
        if self._range_part_load != (part_load is not None):
            if self._range_part_load:
                raise ValueError('The EER class requires a value for the part-load.')

        # convert to arrays
        primary_temperature = np.array(
            [primary_temperature] if isinstance(primary_temperature, (float, int)) else primary_temperature)
        secondary_temperature = np.array(
            [secondary_temperature] if isinstance(secondary_temperature, (float, int)) else secondary_temperature)
        part_load = np.array([part_load] if isinstance(part_load, (float, int)) else part_load)

        # clip
        primary_temperature_clipped = np.clip(primary_temperature,
                                              np.min(self.__range_primary_),
                                              np.max(self.__range_primary_))
        secondary_temperature_clipped = None
        part_load_clipped = None
        if self._range_secondary:
            secondary_temperature_clipped = np.clip(secondary_temperature, np.min(self.__range_secondary_),
                                                    np.max(self.__range_secondary_))
        if self._range_part_load:
            part_load_clipped = np.clip(part_load, np.min(self.__range_part_load_), np.max(self.__range_part_load_))

        xi = primary_temperature_clipped
        if self._range_part_load and self._range_secondary:
            xi = list(zip(primary_temperature_clipped, secondary_temperature_clipped, part_load_clipped))
        elif self._range_secondary:
            xi = list(zip(primary_temperature_clipped, secondary_temperature_clipped))
        elif self._range_part_load:
            xi = list(zip(primary_temperature_clipped, part_load_clipped))

        interp = interpolate.interpn(self._points, self._data, xi, bounds_error=False, fill_value=np.nan)
        if not np.isnan(interp).any():
            return interp

        # replace with nearest value
        nearest = interpolate.interpn(self._points, self._data, xi,
                                      method='nearest',
                                      bounds_error=False,
                                      fill_value=None)
        interp[np.isnan(interp)] = nearest[np.isnan(interp)]
        return interp

    def get_SEER(self,
                 power: np.ndarray,
                 nom_power: float,
                 primary_temperature: np.ndarray,
                 secondary_temperature: np.ndarray = None
                 ) -> float:
        """
        This function calculates and returns the SEER.

        Parameters
        ----------
        power : np.ndarray
            Array with the hourly secondary power of the heat pump [kW]
        nom_power : float
            Nominal power of the heat pump [kW]
        primary_temperature : np.ndarray
            Values for the average primary temperature of the heat pump for the EER calculation.
        secondary_temperature : np.ndarray
            Values for the average secondary temperature of the heat pump for the EER calculation.

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

        part_load = np.array(power) / nom_power
        cop_array = self.get_EER(primary_temperature, secondary_temperature, part_load)

        # SEER = sum(Q)/sum(W)
        w_array = np.array(power) / cop_array

        return np.sum(power) / np.sum(w_array)
