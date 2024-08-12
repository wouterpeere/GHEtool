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
                 coordinates: np.ndarray,
                 nb_of_points_primary_temperature: int,
                 nb_of_points_secondary_temperature: int = 0,
                 nb_of_points_part_load: int = 0):
        """

        Parameters
        ----------
        data : np.ndarray
            1D-array with all efficiency values.
        coordinates : np.ndarray
            1D array with all the coordinates at which the efficiency values can be found. These coordinates can be
            1D up to 3D, depending on whether secondary temperature and/or part load is taken into account.
        nb_of_points_primary_temperature : np.ndarray
            The resolution for the interpolation grid for primary temperature.
        nb_of_points_secondary_temperature : np.ndarray
            The resolution for the interpolation grid for primary temperature. 0 if there are no secondary temperatures
            in the data.
        nb_of_points_part_load : np.ndarray
            The resolution for the interpolation grid for primary temperature. 0 if there are no part loads
            in the data.

        Raises
        ------
        ValueError
            When the shape of the data does not equal the provided ranges.
        ValueError
            When there is a datapoint smaller or equal to zero.

        """
        self._data = data
        self._has_secondary: bool = nb_of_points_secondary_temperature > 0
        self._has_part_load: bool = nb_of_points_part_load > 0
        self._range_primary = ()
        self._range_secondary = ()
        self._range_part_load = ()

        # check if all data points are higher than 0
        if not np.all(self._data > 0):
            raise ValueError('The efficiencies should all be above zero!')

        # check if the data has the same length as the coordinates
        if len(data) != len(coordinates):
            raise ValueError('The provided data and coordinates array are not of the same length!')

        # check dimension
        dimensions = len(coordinates[0])
        if dimensions != 1 + self._has_secondary + self._has_part_load:
            raise ValueError(f'The provided coordinate data has {dimensions} dimensions whereas '
                             f'{1 + self._has_secondary + self._has_part_load} dimensions where provided.'
                             'Please check the nb_of_points for both secondary temperature and part load.')

        # set range
        self._range_primary = (np.min(coordinates[:, 0]), np.max(coordinates[:, 0]))
        if self._has_secondary and self._has_part_load:
            self._range_secondary = (np.min(coordinates[:, 1]), np.max(coordinates[:, 1]))
            self._range_part_load = (np.min(coordinates[:, 2]), np.max(coordinates[:, 2]))
            # make rectangular interpolation grid
            self._points = np.mgrid(
                np.linspace(self._range_primary[0], self._range_primary[1], nb_of_points_primary_temperature),
                np.linspace(self._range_secondary[0], self._range_secondary[1], nb_of_points_secondary_temperature),
                np.linspace(self._range_part_load[0], self._range_part_load[1], nb_of_points_primary_temperature))
        elif self._has_secondary:
            self._range_secondary = (np.min(coordinates[:, 1]), np.max(coordinates[:, 1]))
            # make rectangular interpolation grid
            self._points = np.mgrid(
                np.linspace(self._range_primary[0], self._range_primary[1], nb_of_points_primary_temperature),
                np.linspace(self._range_secondary[0], self._range_secondary[1], nb_of_points_secondary_temperature))
        elif self._has_part_load:
            self._range_part_load = (np.min(coordinates[:, 1]), np.max(coordinates[:, 1]))
            # make rectangular interpolation grid
            self._points = np.mgrid(
                np.linspace(self._range_primary[0], self._range_primary[1], nb_of_points_primary_temperature),
                np.linspace(self._range_part_load[0], self._range_part_load[1], nb_of_points_primary_temperature))
        else:
            self._points = np.mgrid(
                np.linspace(self._range_primary[0], self._range_primary[1], nb_of_points_primary_temperature))

        # create data grid for later interpolation
        self._data = interpolate.griddata(coordinates, data, self._points, fill_value=np.nan)

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
        if self._has_secondary != (secondary_temperature is not None):
            if self._has_secondary:
                raise ValueError('The EER class requires a value for the secondary temperature.')
        if self._has_part_load != (part_load is not None):
            if self._has_part_load:
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
        if self._has_secondary:
            secondary_temperature_clipped = np.clip(secondary_temperature, np.min(self.__range_secondary_),
                                                    np.max(self.__range_secondary_))
        if self._has_part_load:
            part_load_clipped = np.clip(part_load, np.min(self.__range_part_load_), np.max(self.__range_part_load_))

        xi = primary_temperature_clipped
        if self._has_part_load and self._has_secondary:
            xi = list(zip(primary_temperature_clipped, secondary_temperature_clipped, part_load_clipped))
        elif self._has_secondary:
            xi = list(zip(primary_temperature_clipped, secondary_temperature_clipped))
        elif self._has_part_load:
            xi = list(zip(primary_temperature_clipped, part_load_clipped))

        interp = interpolate.interpn(self._points, self._data, xi, bounds_error=False, fill_value=np.nan)
        if not np.isnan(interp).any():
            return interp
