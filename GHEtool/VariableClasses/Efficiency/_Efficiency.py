import numpy as np

from scipy.interpolate import interpn, interp1d
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
                 part_load: bool = False,
                 secondary: bool = False,
                 reference_nominal_power: float = None,
                 nominal_power: float = None):
        """

        Parameters
        ----------
        data : np.ndarray
            1D-array with all efficiency values.
        coordinates : np.ndarray
            1D array with all the coordinates at which the efficiency values can be found. These coordinates can be
            1D up to 3D, depending on whether secondary temperature and/or part load is taken into account.
        part_load : bool
            True if the data contains part load information.
        secondary : bool
            True if the data contains secondary temperature information
        reference_nominal_power : float
            If you want to use the efficiency class as a reference of different heat pumps, you need to define a reference
            for the nominal power, at which the data is defined. This is only relevant when part load data is available.
        nominal_power : float
            The nominal power at which to define the current efficiency class. This converts the provided efficiency data
            from the reference_nominal_power to the nominal_power. This is only relevant when part load data is available
            and the reference_nominal_power is provided.

        Raises
        ------
        ValueError
            When the shape of the data does not equal the provided ranges.
        ValueError
            When there is a datapoint smaller or equal to zero.

        """
        self._interp = None
        self._nearestp = None
        self._has_secondary: bool = secondary
        self._has_part_load: bool = part_load
        self._data_: np.ndarray = data
        self._coordinates_: np.ndarray = coordinates      
        self._reference_nominal_power: float = reference_nominal_power
        self._nominal_power: float = nominal_power
                     
        self._range_primary: np.ndarray = np.array([])
        self._range_secondary: np.ndarray = np.array([])
        self._range_part_load: np.ndarray = np.array([])

        # check if all data points are higher than 0
        if not np.all(data > 0):
            raise ValueError('The efficiencies should all be above zero!')

        # check if the data has the same length as the coordinates
        if len(data) != len(coordinates):
            raise ValueError('The provided data and coordinates array are not of the same length!')

        # check dimension
        dimensions = 1 if isinstance(coordinates[0], (int, float, np.int32, np.int64, np.float16, np.float32)) else len(
            coordinates[0])
        if dimensions != 1 + self._has_secondary + self._has_part_load:
            raise ValueError(f'The provided coordinate data has {dimensions} dimensions whereas '
                             f'{1 + self._has_secondary + self._has_part_load} dimensions where provided.'
                             'Please check the nb_of_points for both secondary temperature and part load.')

        # get ranges
        self._points = []
        if dimensions == 3:
            self._range_primary = np.sort(np.unique(coordinates[:, 0]))
            self._range_secondary = np.sort(np.unique(coordinates[:, 1]))
            self._range_part_load = np.sort(np.unique(coordinates[:, 2]))
            self._points.append(self._range_secondary)
            self._points.append(self._range_part_load)
        elif self._has_secondary:
            self._range_primary = np.sort(np.unique(coordinates[:, 0]))
            self._range_secondary = np.sort(np.unique(coordinates[:, 1]))
            self._points.append(self._range_secondary)
        elif self._has_part_load:
            self._range_primary = np.sort(np.unique(coordinates[:, 0]))
            self._range_part_load = np.sort(np.unique(coordinates[:, 1]))
            self._points.append(self._range_part_load)
        else:
            self._range_primary = np.sort(coordinates)
        self._points.insert(0, self._range_primary)

        def find_value(x, y, z=None):
            if z is None:
                index = np.nonzero(np.all(coordinates == (x, y), axis=1))[0]
            else:
                index = np.nonzero(np.all(coordinates == (x, y, z), axis=1))[0]

            # the data point exists
            if len(index) > 0:
                return data[index[0]]

            # the data point does not exist, so we have to interpolate to get it
            x_array = []
            y_array = []
            if z is None:
                # only one dimension to check
                for idx, val in enumerate(coordinates):
                    if val[0] == x:
                        x_array.append(val[1])
                        y_array.append(data[idx])
            else:
                # two dimensions to check
                for idx, val in enumerate(coordinates):
                    if val[0] == x and val[1] == y:
                        x_array.append(val[2])
                        y_array.append(data[idx])
            # as array
            x_array = np.array(x_array)
            y_array = np.array(y_array)

            # sort array
            p = x_array.argsort()
            x_array = x_array[p]
            y_array = y_array[p]

            temp = np.interp(y if z is None else z, x_array, y_array)
            return temp

        # populate data matrix
        if dimensions == 3:
            self._data = np.empty((len(self._range_primary), len(self._range_secondary), len(self._range_part_load)))
            for i in range(self._data.shape[0]):
                for j in range(self._data.shape[1]):
                    for k in range(self._data.shape[2]):
                        self._data[i, j, k] = find_value(self._range_primary[i],
                                                         self._range_secondary[j],
                                                         self._range_part_load[k])
        elif dimensions == 2:
            self._data = np.empty(
                (len(self._range_primary), max(len(self._range_secondary), len(self._range_part_load))))
            if self._has_secondary:
                for i in range(self._data.shape[0]):
                    for j in range(self._data.shape[1]):
                        self._data[i, j] = find_value(self._range_primary[i],
                                                      self._range_secondary[j])
            else:
                for i in range(self._data.shape[0]):
                    for j in range(self._data.shape[1]):
                        self._data[i, j] = find_value(self._range_primary[i],
                                                      self._range_part_load[j])
        else:
            p = self._range_primary.argsort()
            self._data = data[p]

        # correct for nominal power
        if nominal_power is not None and reference_nominal_power is None:
            raise ValueError('Please enter a reference nominal power.')

        if self._has_part_load and nominal_power is not None:
            self._range_part_load *= nominal_power / reference_nominal_power

    def _get_efficiency(self,
                        primary_temperature: Union[float, np.ndarray],
                        secondary_temperature: Union[float, np.ndarray] = None,
                        power: Union[float, np.ndarray] = None) -> np.ndarray:
        """
        This function calculates the efficiency. This function uses interpolation and sets the out-of-bound values
        to the nearest value in the dataset. This function does hence not extrapolate.

        Parameters
        ----------
        primary_temperature : np.ndarray or float
            Value(s) for the average primary temperature of the heat pump for the efficiency calculation.
        secondary_temperature : np.ndarray or float
            Value(s) for the average secondary temperature of the heat pump for the efficiency calculation.
        power : np.ndarray or float
            Value(s) for the part load data of the heat pump for the efficiency calculation.

        Raises
        ------
        ValueError
            When secondary_temperature is in the dataset, and it is not provided. Same for power.

        Returns
        -------
        Efficiency
            np.ndarray
        """
        # check if all the required values are present
        if self._has_secondary != (secondary_temperature is not None):
            if self._has_secondary:
                raise ValueError('The EER class requires a value for the secondary temperature.')
        if self._has_part_load != (power is not None):
            if self._has_part_load:
                raise ValueError('The EER class requires a value for the part-load.')

        # get maximum length
        _max_length = np.max([len(i) if i is not None and not isinstance(i, (float, int)) else 1 for i in
                              (primary_temperature, secondary_temperature, power)])

        # convert to arrays
        primary_temperature = np.array(
            np.full(_max_length, primary_temperature) if isinstance(primary_temperature,
                                                                    (float, int)) else primary_temperature)
        secondary_temperature = np.array(
            np.full(_max_length, secondary_temperature) if isinstance(secondary_temperature,
                                                                      (float, int)) else secondary_temperature)
        power = np.array(np.full(_max_length, power) if isinstance(power, (float, int)) else power)

        # clip, so that no values fall outside the provided values
        primary_temperature_clipped = np.clip(primary_temperature,
                                              np.min(self._range_primary),
                                              np.max(self._range_primary))
        secondary_temperature_clipped = None
        part_load_clipped = None
        if self._has_secondary:
            secondary_temperature_clipped = np.clip(secondary_temperature, np.min(self._range_secondary),
                                                    np.max(self._range_secondary))
        if self._has_part_load:
            part_load_clipped = np.clip(power, np.min(self._range_part_load), np.max(self._range_part_load))

        xi = primary_temperature_clipped
        if self._has_part_load and self._has_secondary:
            xi = list(zip(primary_temperature_clipped, secondary_temperature_clipped, part_load_clipped))
        elif self._has_secondary:
            xi = list(zip(primary_temperature_clipped, secondary_temperature_clipped))
        elif self._has_part_load:
            xi = list(zip(primary_temperature_clipped, part_load_clipped))

        interp = interpn(self._points, self._data, xi, bounds_error=False, fill_value=np.nan)
        if not np.isnan(interp).any():
            return interp
