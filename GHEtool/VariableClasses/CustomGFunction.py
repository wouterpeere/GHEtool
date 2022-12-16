"""
This file contains both the CustomGFunction class and all the relevant information w.r.t. custom gfunctions.
"""
import pygfunction as gt
import numpy as np
from typing import Union, List
import pickle
import warnings
from scipy import interpolate


def _timeValues(dt=3600., t_max=100. * 8760 * 3600.) -> np.array:
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
    dt: float = dt  # Time step (s)
    t_max: float = t_max  # Maximum time (s)

    # Load aggregation scheme
    load_agg = gt.load_aggregation.ClaessonJaved(dt, t_max)

    return load_agg.get_times_for_simulation()


class CustomGFunction:

    """
    This class contains all the functionalities related to custom gfunctions.
    """

    DEFAULT_DEPTH_ARRAY: np.ndarray = np.arange(0, 351, 25)  # m
    DEFAULT_DEPTH_ARRAY[0] = 10  # m
    DEFAULT_TIME_ARRAY: np.ndarray = _timeValues()  # sec

    def __init__(self, time_array: np.ndarray = None, depth_array: np.ndarray = None, options: dict = None):
        """

        Parameters
        ----------
        time_array : np.ndarray
            Time value(s) in seconds at which the gfunctions should be calculated
        depth_array : np.ndarray
            Depths [m] for which the gfunctions should be calculated
        options : dict
            Dictionary with options for the gFunction class of pygfunction
        """
        self._time_array: np.ndarray = np.array([])
        self._depth_array: np.ndarray = np.array([])

        self.max_H: float = 0.
        self.min_H: float = 0.
        self.max_t: float = 0.
        self.min_t: float = 0.

        self.time_array = CustomGFunction.DEFAULT_TIME_ARRAY
        self.depth_array = CustomGFunction.DEFAULT_DEPTH_ARRAY

        self._gvalues_array: np.ndarray = np.zeros((self.depth_array.size, self.time_array.size))
        self.options: dict = {"method": "equivalent", "display": True}

        # set values
        if time_array is not None:
            self.time_array = time_array
        if depth_array is not None:
            self.depth_array = depth_array
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
        self._gvalues_array = np.zeros((self.depth_array.size, self.time_array.size))

    @property
    def depth_array(self) -> np.ndarray:
        return self._depth_array

    @depth_array.setter
    def depth_array(self, depth_array) -> None:
        self._depth_array = np.sort(depth_array)
        self.max_H = self._depth_array[-1]
        self.min_H = self._depth_array[0]
        # initialise gvalue array
        self._gvalues_array = np.zeros((self.depth_array.size, self.time_array.size))

    def calculate_gfunction(self, time_value: Union[list, float, np.ndarray], H: float, check: bool = False) -> np.ndarray:
        """
        This function returns the gfunction value, based on interpolation between precalculated values.

        Parameters
        ----------
        time_value : list, float, np.ndarray
            Time value(s) in seconds at which the gfunctions should be calculated
        H : float
            Depth [m] at which the gfunctions should be calculated.
            If no depth is given, the current depth is taken.
        check : bool
            True if it should be check whether or not the requested gvalues can be interpolated based on the
            precalculated values

        Returns
        -------
        gvalues : np.ndarray
            1D array with all the requested gvalues. False is returned if the check is True and the requested values
            are out of range for interpolation
        """

        # check if the requested value is within the range
        if check and not self.within_range(time_value, H):
            return False

        if not isinstance(time_value, (float, int)):
            # multiple values are requested
            g_value = interpolate.interpn((self.depth_array, self.time_array), self._gvalues_array, np.array([[H, t] for t in time_value]))
        else:
            # only one value is requested
            g_value = interpolate.interpn((self.depth_array, self.time_array), self._gvalues_array, np.array([H, time_value]))
        return g_value

    def within_range(self, time_value: Union[list, float, np.ndarray], H: float) -> bool:
        """
        This function checks whether or not the requested data can be calculated using the custom dataset.

        Parameters
        ----------
        time_value : list, float, np.ndarray
            Time value(s) in seconds at which the gfunctions should be calculated
        H : float
            Depth [m] at which the gfunctions should be calculated.
            If no depth is given, the current depth is taken.

        Returns
        -------
        bool
            True if the requested values are within the range of the precalculated data, False otherwise
        """

        # check if the custom gfunctions are calculated
        if not np.any(self._gvalues_array):
            return False

        max_time_value = time_value if isinstance(time_value, (float, int)) else max(time_value)
        min_time_value = time_value if isinstance(time_value, (float, int)) else min(time_value)

        # check if H in precalculated data range
        if H > self.max_H or H < self.min_H:
            warnings.warn("The requested depth of " + str(H) + "m is outside the bounds of " + str(self.min_H) +
                          " and " + str(self.max_H) +
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

    def create_custom_dataset(self, borefield: List[gt.boreholes.Borehole], alpha: float) -> None:
        """
        This function creates the custom dataset.

        Parameters
        ----------
        borefield : list[pygfunction.boreholes.Borehole]
            Borefield object for which the custom dataset should be created
        alpha : float
            Ground thermal diffusivity [m2/s]

        Returns
        -------
        None
        """
        # chek if there is a method in options
        if not "method" in self.options:
            self.options["method"] = "equivalent"

        for idx, H in enumerate(self.depth_array):
            print("Start H: ", H)

            # Calculate the g-function for uniform borehole wall temperature

            # set borehole depth in borefield
            for borehole in borefield:
                borehole.H = H

            gfunc_uniform_T = gt.gfunction.gFunction(borefield, alpha,
                                                     self.time_array, options=self.options,
                                                     method=self.options["method"])

            self._gvalues_array[idx] = gfunc_uniform_T.gFunc

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
        self._gvalues_array = np.array([])

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
