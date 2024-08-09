import numpy as np

from scipy import interpolate
from typing import Union


class _EfficiencyBase:

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False

        for key in self.__dict__:
            value1 = self.__dict__[key]
            value2 = other.__dict__[key]

            if isinstance(value1, np.ndarray) and isinstance(value2, np.ndarray):
                if not np.array_equal(value1, value2):
                    return False
            else:
                if not np.array_equal(value1, value2):
                    return False

        return True


class _Efficiency(_EfficiencyBase):
    """
    Baseclass for all the efficiencies
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
        ValueError
            When there is a datapoint smaller or equal to zero.

        """
        self._data = data
        self._range_secondary: bool = range_avg_secondary_temperature is not None
        self._range_part_load: bool = range_part_load is not None
        self.__range_primary_ = range_avg_primary_temperature
        self.__range_secondary_ = range_avg_secondary_temperature
        self.__range_part_load_ = range_part_load

        # check if all data points are higher than 0
        if not np.all(self._data > 0):
            raise ValueError('The efficiencies should all be above zero!')

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
                # if
                interpolate.interpn(self._points, self._data, (1, 1, 1), bounds_error=False)

                return
            except ValueError:
                raise ValueError('Please make sure the dimensions of the dataset are correct!')
        # test incorrect shape
        try:
            np.shape(self._points)
        except ValueError:
            raise ValueError('Please make sure the dimensions of the dataset are correct!')

    def _get_efficiency(self,
                        primary_temperature: Union[float, np.ndarray],
                        secondary_temperature: Union[float, np.ndarray] = None,
                        part_load: Union[float, np.ndarray] = None) -> np.ndarray:
        """
        This function calculates the efficiency. This function uses a linear interpolation and sets the out-of-bound values
        to the nearest value in the dataset. This function does hence not extrapolate.

        Parameters
        ----------
        primary_temperature : np.ndarray or float
            Value(s) for the average primary temperature of the heat pump for the efficiency calculation.
        secondary_temperature : np.ndarray or float
            Value(s) for the average secondary temperature of the heat pump for the efficiency calculation.
        part_load : np.ndarray or float
            Value(s) for the part load data of the heat pump for the efficiency calculation.

        Raises
        ------
        ValueError
            When secondary_temperature is in the dataset, and it is not provided. Same for part_load.

        Returns
        -------
        Efficiency
            np.ndarray
        """
        # check if all the required values are present
        if self._range_secondary != (secondary_temperature is not None):
            if self._range_secondary:
                raise ValueError('The EER class requires a value for the secondary temperature.')
        if self._range_part_load != (part_load is not None):
            if self._range_part_load:
                raise ValueError('The EER class requires a value for the part-load.')

        # get maximum length
        _max_length = np.max([len(i) if i is not None and not isinstance(i, (float, int)) else 1 for i in
                              (primary_temperature, secondary_temperature, part_load)])

        # convert to arrays
        primary_temperature = np.array(
            np.full(_max_length, primary_temperature) if isinstance(primary_temperature,
                                                                    (float, int)) else primary_temperature)
        secondary_temperature = np.array(
            np.full(_max_length, secondary_temperature) if isinstance(secondary_temperature,
                                                                      (float, int)) else secondary_temperature)
        part_load = np.array(np.full(_max_length, part_load) if isinstance(part_load, (float, int)) else part_load)

        # clip, so that no values fall outside of the provided values
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
