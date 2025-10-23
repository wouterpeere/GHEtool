"""
This file contains both the CustomGFunction class and all the relevant information w.r.t. custom gfunctions.
"""
import copy
import math
import pickle
import warnings
from typing import List, Union

import numpy as np
import pygfunction as gt
from scipy import interpolate


def _time_values(dt=3600., t_max=100. * 8760 * 3600.) -> np.array:
    """
    This function calculates the default time values for the g-function.
    This is based on the Load aggregation algorithm of Claesson and Javed [#ClaessonJaved2012]_.

    Attributes
    ----------
    dt : float
        time step in seconds
    t_max : float
        maximum time in seconds

    Returns
    -------
    timevalues : numpy array
        array with the time values for the simulation

    References
    ----------
    .. [#ClaessonJaved2012] Claesson, J., & Javed, S. (2012). A
       load-aggregation method to calculate extraction temperatures of
       borehole heat exchangers. ASHRAE Transactions, 118 (1): 530–539.
    """
    # Load aggregation scheme
    return gt.load_aggregation.ClaessonJaved(dt, t_max).get_times_for_simulation()


class CustomGFunction:
    """
    This class contains all the functionalities related to custom gfunctions.
    """

    DEFAULT_LENGTH_ARRAY: np.ndarray = np.arange(0, 351, 25)  # m
    DEFAULT_LENGTH_ARRAY[0] = 10  # m
    DEFAULT_TIME_ARRAY: np.ndarray = _time_values()  # sec

    def __init__(self, time_array: np.ndarray = None, borehole_length_array: np.ndarray = None, options: dict = None):
        """

        Parameters
        ----------
        time_array : np.ndarray
            Time value(s) in seconds at which the gfunctions should be calculated
        borehole_length_array : np.ndarray
            Borehole lengths [m] for which the gfunctions should be calculated
        options : dict
            Dictionary with options for the gFunction class of pygfunction
        """
        self._time_array: np.ndarray = np.array([])
        self._borehole_length_array: np.ndarray = np.array([])

        self.max_borehole_length: float = 0.
        self.min_borehole_length: float = 0.
        self.max_t: float = 0.
        self.min_t: float = 0.

        self.time_array = CustomGFunction.DEFAULT_TIME_ARRAY
        self.borehole_length_array = CustomGFunction.DEFAULT_LENGTH_ARRAY

        self.gvalues_array: np.ndarray = np.zeros((self.borehole_length_array.size, self.time_array.size))
        self.options: dict = {"method": "equivalent", "display": True}

        # set values
        if time_array is not None:
            self.time_array = time_array
        if borehole_length_array is not None:
            self.borehole_length_array = borehole_length_array
        if options is not None:
            self.options = options

    @property
    def time_array(self) -> np.ndarray:
        return self._time_array

    @time_array.setter
    def time_array(self, time_array: np.ndarray) -> None:
        self._time_array = np.sort(time_array)
        self.max_t = time_array[-1]
        self.min_t = time_array[0]
        # initialise gvalue array
        self.gvalues_array = np.zeros((self.borehole_length_array.size, self.time_array.size))

    @property
    def borehole_length_array(self) -> np.ndarray:
        return self._borehole_length_array

    @borehole_length_array.setter
    def borehole_length_array(self, borehole_length_array) -> None:
        self._borehole_length_array = np.sort(borehole_length_array)
        self.max_borehole_length = self._borehole_length_array[-1]
        self.min_borehole_length = self._borehole_length_array[0]
        # initialise gvalue array
        self.gvalues_array = np.zeros((self.borehole_length_array.size, self.time_array.size))

    def calculate_gfunction(self, time_value: Union[list, float, np.ndarray], borehole_length: float,
                            check: bool = False) -> np.ndarray:
        """
        This function returns the gfunction value, based on interpolation between precalculated values.

        Parameters
        ----------
        time_value : list, float, np.ndarray
            Time value(s) in seconds at which the gfunctions should be calculated
        borehole_length : float
            Borehole lengths [m] at which the gfunctions should be calculated.
            If no borehole length is given, the current borehole length is taken.
        check : bool
            True if it should be checked whether the requested gvalues can be interpolated based on the
            precalculated values

        Returns
        -------
        gvalues : np.ndarray
            1D array with all the requested gvalues. False is returned if the check is True and the requested values
            are out of range for interpolation
        """

        # check if the requested value is within the range
        if check and not self.within_range(time_value, borehole_length):
            return False

        if not isinstance(time_value, (float, int)):
            # multiple values are requested
            g_value = interpolate.interpn((self.borehole_length_array, self.time_array), self.gvalues_array,
                                          np.array([[borehole_length, t] for t in time_value]))
        else:
            # only one value is requested
            g_value = interpolate.interpn((self.borehole_length_array, self.time_array), self.gvalues_array,
                                          np.array([borehole_length, time_value]))
        return g_value

    def within_range(self, time_value: Union[list, float, np.ndarray], borehole_length: float) -> bool:
        """
        This function checks whether or not the requested data can be calculated using the custom dataset.

        Parameters
        ----------
        time_value : list, float, np.ndarray
            Time value(s) in seconds at which the gfunctions should be calculated
        borehole_length : float
            Borehole lengths [m] at which the gfunctions should be calculated.
            If no borehole length is given, the current borehole length is taken.

        Returns
        -------
        bool
            True if the requested values are within the range of the precalculated data, False otherwise
        """

        # check if the custom gfunctions are calculated
        if not np.any(self.gvalues_array):
            return False

        max_time_value = time_value if isinstance(time_value, (float, int)) else max(time_value)
        min_time_value = time_value if isinstance(time_value, (float, int)) else min(time_value)

        # check if borehole_length in precalculated data range
        if borehole_length > self.max_borehole_length or borehole_length < self.min_borehole_length:
            warnings.warn(
                "The requested borehole length of " + str(borehole_length) + "m is outside the bounds of " + str(
                    self.min_borehole_length) +
                " and " + str(self.max_borehole_length) +
                " of the precalculated data. The gfunctions will be calculated jit.", UserWarning)
            return False

        # check if max time in precalculated data range
        if max_time_value > self.max_t:
            warnings.warn(
                "The requested time of " + str(max_time_value) + "s is outside the bounds of " + str(self.min_t) +
                " and " + str(self.max_t) + " of the precalculated data. The gfunctions will be calculated jit.",
                UserWarning)
            return False

        # check if min time in precalculated data range
        if min_time_value < self.min_t:
            warnings.warn(
                "The requested time of " + str(min_time_value) + "s is outside the bounds of " + str(self.min_t) +
                " and " + str(self.max_t) + " of the precalculated data. The gfunctions will be calculated jit.",
                UserWarning)
            return False

        return True

    def create_custom_dataset(self, borefield: gt.borefield.Borefield, alpha: Union[float, callable]) -> None:
        """
        This function creates the custom dataset.

        Parameters
        ----------
        borefield : pygfunction.borefield.Borefield
            Borefield object for which the custom dataset should be created
        alpha : float or callable
            Ground thermal diffusivity [m2/s] or function to calculate it at a certain borehole length

        Returns
        -------
        None
        """
        # chek if there is a method in options
        if not "method" in self.options:
            self.options["method"] = "equivalent"

        for idx, borehole_length in enumerate(self.borehole_length_array):
            print(f'Start length: {borehole_length} m')

            # Calculate the g-function for uniform borehole wall temperature
            borefield = copy.deepcopy(borefield)
            # set borehole borehole length in borefield
            borefield.H = np.full(borefield.nBoreholes, borehole_length)

            # calculate borehole buried depth
            D = np.average(borefield.D)
            tilt = np.average(borefield.tilt)

            depth = borehole_length * math.cos(tilt) + D
            gfunc_uniform_T = gt.gfunction.gFunction(borefield,
                                                     alpha if isinstance(alpha, float) else alpha(depth, D),
                                                     self.time_array, options=self.options,
                                                     method=self.options["method"])

            self.gvalues_array[idx] = gfunc_uniform_T.gFunc

    def dump_custom_dataset(self, path: str, name: str) -> None:
        """
        This function dumps the current custom dataset.

        Parameters
        ----------
        path : str
            Location where the dataset should be saved
        name : str
            Name under which the dataset should be saved

        Returns
        -------
        None
        """
        with open(path + name + '.gvalues', 'wb') as f:
            pickle.dump(self, f)

    def set_options_gfunction_calculation(self, options: dict) -> None:
        """
        This function sets the options for the gfunction calculation of pygfunction.
        This dictionary is directly passed through to the gFunction class of pygfunction.
        For more information, please visit the documentation of pygfunction.

        Parameters
        ----------
        options : dict
            Dictionary with options for the gFunction class of pygfunction

        Returns
        -------
        None
        """
        self.options = options

    def delete_custom_gfunction(self) -> None:
        """
        This function deletes the custom gfunction.

        Returns
        -------
        None
        """
        self.gvalues_array = np.array([])

    def __eq__(self, other):
        if not isinstance(other, CustomGFunction):
            return False
        for i in iter(self.__dict__):
            if isinstance(getattr(self, i), np.ndarray) or isinstance(getattr(self, i), list):
                if not np.array_equal(getattr(self, i), getattr(other, i)):
                    return False
                continue
            if getattr(self, i) != getattr(other, i):
                return False
        return True


def load_custom_gfunction(path: str) -> CustomGFunction:
    """
    This function loads a custom gfunction dataset.

    Parameters
    ----------
    path : str
        Location of the dataset

    Returns
    -------
    CustomGFunction
        Dataset with the custom gfunction data
    """
    return pickle.load(open(path, 'rb'))
