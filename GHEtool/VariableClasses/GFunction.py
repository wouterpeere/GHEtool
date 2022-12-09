import pygfunction as gt
import numpy as np
from typing import Union, Tuple
import copy

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
        self.alpha: float = None
        self.borefield: list = []
        self.depth_array: np.ndarray = np.array([])
        self.time_array: np.ndarray = np.array([])
        self.previous_gfunctions: np.ndarray = np.array([])
        self.nb_of_time_values: int = 0

        self.no_extrapolation: bool = True
        self.threshold_depth_interpolation: float = 25  # m

    def calculate(self, time_value: Union[list, float, np.ndarray], borefield, alpha: float):

        depth = borefield[0].H

        if self._check_alpha(alpha) and self._check_borefield(borefield):
            # see if data can be interpolated
            gvalues: np.ndarray = self.interpolate_gfunctions(time_value, depth)
        else:
            gvalues: np.ndarray = np.zeros(len(time_value))

        time_value_np = np.array(time_value)
        if not isinstance(time_value, (float, int)) and len(time_value_np) > GFunction.DEFAULT_NUMBER_OF_TIMESTEPS:
            # due to this many requested time values, the calculation will be slow.
            # there will be interpolation

            time_value_new = _timeValues(t_max=time_value[-1])
            # Calculate the g-function for uniform borehole wall temperature
            gfunc_uniform_T = gt.gfunction.gFunction(borefield, alpha, time_value_new,
                                                     options=self.options).gFunc

            # return interpolated values
            return np.interp(time_value, time_value_new, gfunc_uniform_T)

        # check if there are double values
        if not isinstance(time_value, (float, int)) and len(time_value_np) != len(np.unique(np.asarray(time_value))):
            gfunc_uniform_T = gt.gfunction.gFunction(borefield, alpha, np.unique(time_value_np),
                                                     options=self.options).gFunc

            return np.interp(time_value, np.unique(time_value_np), gfunc_uniform_T)

        # Calculate the g-function for uniform borehole wall temperature
        gfunc_uniform_T = gt.gfunction.gFunction(borefield, alpha, time_value_np,
                                                 options=self.options).gFunc

        return gfunc_uniform_T

    def interpolate_gfunctions(self, time_value: Union[list, float, np.ndarray], depth: float) -> np.ndarray:

        gvalues: np.ndarray = np.zeros(len(time_value))

        # find nearest depth indices
        idx_prev, idx_next = self._get_nearest_depth_index(depth)

        if self.no_extrapolation:
            # no interpolation can be made since depth is not in between values in the depth array
            if idx_prev is None or idx_next is None:
                return gvalues

            # # check if the time values for both indices are equal
            # if not self._check_time_values_are_equal_at_indices(idx_prev, idx_next):
            #     return gvalues

            # check if interpolation of all time values can be done based on the available time values
            if not self._check_time_values(self.time_array, time_value):
                return gvalues

            # do interpolation

        # when extrapolation is permitted
        # TODO implement extrapolation
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
        """
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
            else:
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

    def _check_time_values_are_equal_at_indices(self, depth_1: float, depth_2: float) -> bool:
        """
        This function checks whether or not the time values of the previous calculated data for both depths
        are equal.

        Parameters
        ----------
        depth_1 : float
            First depth [m] for which the time values should be checked
        depth_2 : float
            Second depth [m] for which the time values should be checked

        Returns
        -------
        bool
            True if the time values are equal, False otherwise
        """
        return np.array_equal(self.time_array[depth_1], self.time_array[depth_2])

    def _check_time_values(self, source: np.ndarray, target: np.ndarray) -> bool:
        pass

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
        self.nb_of_time_values = 0

    def set_new_calculated_data(self, time_values: np.ndarray, depth: float, gvalues: np.ndarray) -> None:
        pass

    def _check_borefield(self, borefield) -> bool:
        """
        This function checks whether the new borefield object is equal to the previous one.
        It does so by comparing all the parameters (neglecting the depth).
        If the borefield objects are unequal, the borefield variable is set to the new borefield
        and all the previously saved gfunctions are deleted.

        Parameters
        ----------
        borefield : pygfunction borefield object
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
            Thermal diffusivity of the ground of the borefield for which the gfunctions should be calculated.

        Returns
        -------
        True
            True if the alpha's are the same, False otherwise
        """
        if alpha != self.alpha:
            self.alpha = alpha
            self.remove_previous_data()
            return False

        return True
