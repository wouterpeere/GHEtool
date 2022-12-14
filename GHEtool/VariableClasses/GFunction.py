import pygfunction as gt
import numpy as np
from typing import Union, Tuple, List
import copy
from scipy import interpolate

from .CustomGFunction import _timeValues


class GFunction:

    """
    Class that contains the functionality to calculate gfunctions and to store
    previously calculated values that can potentially be used for interpolation to save time.
    This is done by storing all previous calculated gvalues as long as the length of the does not change.

    # TODO update this documentation
    """

    DEFAULT_TIMESTEPS: np.ndarray = _timeValues()
    DEFAULT_NUMBER_OF_TIMESTEPS: int = DEFAULT_TIMESTEPS.size

    def __init__(self):
        self.store_previous_values: bool = True
        self.options: dict = {"method": "equivalent"}
        self.alpha: float = 0.
        self.borefield: list = []
        self.depth_array: np.ndarray = np.array([])
        self.time_array: np.ndarray = np.array([])
        self.previous_gfunctions: np.ndarray = np.array([])

        self.no_extrapolation: bool = True
        self.threshold_depth_interpolation: float = 25  # m

    def calculate(self, time_value: Union[list, float, np.ndarray], borefield: List[gt.boreholes.Borehole], alpha: float):
        """
        This function returns the gvalues either by interpolation or by calculating them.
        It does so by calling the function gvalues which does this calculation.
        This calculate function also stores the previous calculated data and makes interpolations
        whenever the requested list of time_value are longer then DEFAULT_NUMBER_OF_TIMESTEPS.

        Parameters
        ----------
        time_value : list, float, np.ndarray
            Array with all the time values [s] for which gvalues should be calculated
        borefield : list[pygfunction.borehole]
            Borefield model for which the gvalues should be calculated
        alpha : float
            Thermal diffusivity of the ground [m2/s]

        Returns
        -------
        gvalues : np.ndarray
            1D array with all the requested gvalues
        """

        def gvalues(time_values: np.ndarray, borefield: List[gt.boreholes.Borehole], alpha: float, depth: float) -> np.ndarray:
            """
            This function returns the gvalues either by interpolation or by calculating them.

            Parameters
            ----------
            time_values : np.ndarray
                Array with all the time values [s] for which gvalues should be calculated
            borefield : list[pygfunction.borehole]
                Borefield model for which the gvalues should be calculated
            alpha : float
                Thermal diffusivity of the ground [m2/s]
            depth : float
                Depth of the borefield [m]

            Returns
            -------
            gvalues : np.ndarray
                1D array with all the requested gvalues
            """
            # do interpolation
            gfunc_interpolated = self.interpolate_gfunctions(time_values, depth, alpha, borefield)

            # if there are g-values calculated, return them
            if np.any(gfunc_interpolated):
                return gfunc_interpolated

            # calculate the g-values for uniform borehole wall temperature
            gfunc_calculated = gt.gfunction.gFunction(borefield, alpha, time_values, options=self.options).gFunc

            # store the calculated g-values
            self.set_new_calculated_data(time_values, depth, gfunc_calculated)

            return gfunc_calculated

        # get depth from borefield
        depth = borefield[0].H

        # make numpy array from time_values
        time_value_np = np.array(time_value)

        if not isinstance(time_value, (float, int)) and time_value_np.size > GFunction.DEFAULT_NUMBER_OF_TIMESTEPS:
            # due to this many requested time values, the calculation will be slow.
            # there will be interpolation

            time_value_new = _timeValues(t_max=time_value[-1])

            # calculate g-function values
            gfunc_uniform_T = gvalues(time_value_new, borefield, alpha, depth)

            # return interpolated values
            return np.interp(time_value, time_value_new, gfunc_uniform_T)

        # check if there are double values
        if not isinstance(time_value, (float, int)) and time_value_np.size != np.unique(np.asarray(time_value)).size:

            # calculate g-function values
            gfunc_uniform_T = gvalues(np.unique(time_value_np), borefield, alpha, depth)

            return np.interp(time_value, np.unique(time_value_np), gfunc_uniform_T)

        # calculate g-function values
        gfunc_uniform_T = gvalues(time_value_np, borefield, alpha, depth)

        return gfunc_uniform_T

    def interpolate_gfunctions(self, time_value: Union[list, float, np.ndarray], depth: float,
                               alpha: float, borefield: List[gt.boreholes.Borehole]) -> np.ndarray:

        gvalues: np.ndarray = np.zeros(len(time_value))

        # check if interpolation is possible:
        if not (self._check_alpha(alpha) and self._check_borefield(borefield)):
            # the alpha and/or borefield is not in line with the precalculated data
            return gvalues

        # find nearest depth indices
        idx_prev, idx_next = self._get_nearest_depth_index(depth)

        if self.no_extrapolation:
            # no interpolation can be made since depth is not in between values in the depth array
            if idx_prev is None or idx_next is None:
                return gvalues

            # check if interpolation of all time values can be done based on the available time values
            if not self._check_time_values(self.time_array, time_value):
                return gvalues

            # do interpolation

            if not time_value.size == 1:
                # multiple values are requested
                gvalues = interpolate.interpn((self.depth_array, self.time_array), self.previous_gfunctions,
                                              np.array([[depth, t] for t in time_value]))
            else:
                # only one value is requested
                gvalues = interpolate.interpn((self.depth_array, self.time_array), self.previous_gfunctions,
                                              np.array([depth, time_value]))
            return gvalues

        # when extrapolation is permitted
        # not yet implemented
        return gvalues

    @staticmethod
    def _nearest_value(array: np.ndarray, value: float) -> Tuple[int, int]:
        """
        This function searches the nearest value and index in an array.

        Parameters
        ----------
        array : np.ndarray
            Array in which the value should be searched
        value : float
            Value to be searched for

        Returns
        -------
        nearest_value, nearest_index : tuple(int, int)
        """
        if not np.any(array):
            return False
        idx = (np.abs(array - value)).argmin()
        return array[idx], idx

    def _get_nearest_depth_index(self, depth: float) -> Tuple[int, int]:
        """
        This function returns the nearest depth indices w.r.t. a specific depth.

        Parameters
        ----------
        depth : float
            Depth for which the nearest indices in the depth_array should be searched.

        Returns
        -------
        tuple(int, int)
            (None, None) if no indices exist that are closer than the threshold value
            (None, int) if the current depth is lower then the minimum in the depth array, but closer then the
            threshold value
            (int, None) if the current depth is higher then the maximum in the depth array, but closer then the
            threshold value
            (int, int) if the current depth is between two previous calculated depths which are closer together
            then the threshold value

        Raises
        ------
        ValueError
            When the depth is smaller or equal to zero
        """
        # raise error when value is negative
        if depth <= 0:
            raise ValueError("The depth is smaller then zero!")

        # get nearest depth index
        val_depth, idx_depth = self._nearest_value(self.depth_array, depth)

        # the exact depth is in the previous calculated data
        # two times the same index is returned
        if val_depth == depth:
            return idx_depth, idx_depth

        if depth > val_depth:
            # the nearest index is the first in the array and the depth is smaller than the smallest value in the array
            # but the difference is smaller than the threshold for interpolation
            if idx_depth == self.depth_array.size - 1 and depth - val_depth < self.threshold_depth_interpolation:
                return idx_depth, None
            elif idx_depth != self.depth_array.size - 1:
                idx_next = idx_depth + 1
                if self.depth_array[idx_next] - val_depth < self.threshold_depth_interpolation:
                    return idx_depth, idx_next
        else:
            # the nearest index is the last in the array and the depth is larger than the highest value in the array
            # but the difference is smaller than the threshold for interpolation
            if idx_depth == 0 and val_depth - depth < self.threshold_depth_interpolation:
                return None, idx_depth
            else:
                idx_prev = idx_depth - 1
                if val_depth - self.depth_array[idx_prev] < self.threshold_depth_interpolation:
                    return idx_prev, idx_depth

        # no correct interpolation indices are found
        # None, None is returned
        return None, None

    @staticmethod
    def _check_time_values(source: np.ndarray, target: np.ndarray) -> bool:
        """
        This function checks whether or not the time values are suitable for interpolation.
        This is done by two checks:

        1. Is the target array longer then the source array? If yes, False is returned.

        2. Is the smallest value of the target smaller then the smallest value in the source array
        (and vice versa for the largest value), False is returned.

        Parameters
        ----------
        source : np.array
            The source of time values [s] for the interpolation
        target : np.array
            The targeted array of time values [s] for interpolation

        Returns
        -------
        bool
            True if the time values are suitable for interpolation.
        """

        if source.size == 0 or target.size == 0:
            return False

        if source.size < target.size:
            return False

        if source[0] <= target[0] and source[-1] >= target[-1]:
            return True

        return False

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

    def remove_previous_data(self) -> None:
        """
        This function removes the previous calculated data by setting the depth_array, time_array and
        previous_gfunctions back to empty arrays.

        Returns
        -------
        None
        """
        self.depth_array = np.array([])
        self.time_array = np.array([])
        self.previous_gfunctions = np.array([])

    def set_new_calculated_data(self, time_values: np.ndarray, depth: float, gvalues: np.ndarray) -> None:

        # TODO check with time_values

        nearest_idx = self._nearest_value(self.depth_array, depth)
        if not nearest_idx:
            nearest_idx = 0
        else:
            if self.depth_array[nearest_idx] < depth:
                nearest_idx += 1

        # insert data in stored data
        self.depth_array = np.insert(self.depth_array, nearest_idx, depth)
        self.previous_gfunctions = np.insert(self.previous_gfunctions, nearest_idx, gvalues)

    def _check_borefield(self, borefield: List[gt.boreholes.Borehole]) -> bool:
        """
        This function checks whether the new borefield object is equal to the previous one.
        It does so by comparing all the parameters (neglecting the depth).
        If the borefield objects are unequal, the borefield variable is set to the new borefield
        and all the previously saved gfunctions are deleted.

        Parameters
        ----------
        borefield : list[pygfunction.Borehole]
            New borefield for which the gfunctions should be calculated

        Returns
        -------
        True
            True if the borefields are the same, False otherwise
        """
        # borefields are unequal if they have different number of boreholes
        if len(borefield) != len(self.borefield):
            self.borefield = copy.copy(borefield)
            self.remove_previous_data()
            return False

        keys = set(borefield[0].__dict__.keys())
        keys.remove("H")

        for idx, _ in enumerate(borefield):
            for key in keys:
                if getattr(borefield[idx], key) != getattr(self.borefield[idx], key):
                    self.borefield = copy.copy(borefield)
                    self.remove_previous_data()
                    return False

        return True

    def _check_alpha(self, alpha) -> bool:
        """
        This function checks whether the thermal diffusivity object is equal to the previous one.
        If the alpha's are unequal, the alpha variable is set to the new alpha value
        and all the previously saved gfunctions are deleted.

        Parameters
        ----------
        alpha : float
            Thermal diffusivity of the ground of the borefield for which the gfunctions should be calculated [m2/s].

        Returns
        -------
        True
            True if the alpha's are the same, False otherwise
        """
        if alpha == 0.:
            return False

        if alpha != self.alpha:
            self.alpha = alpha
            self.remove_previous_data()
            return False

        return True
