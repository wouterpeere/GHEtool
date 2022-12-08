import pygfunction as gt
import numpy as np
from typing import Union
import copy

from .CustomGFunction import _timeValues


class GFunction:

    # TODO check whether there is more time needed to calculate 3 than 100 timesteps,
    # if not, it can be useful to only calculate the default number so that it can be saved
    # for interpolation
    DEFAULT_NUMBER_OF_TIMESTEPS: int = 100

    def __init__(self):
        self.store_previous_values: bool = True
        self.options: dict = {"method": "equivalent"}
        self.alpha: float = None
        self.borefield: list = []
        self.depth_array: np.ndarray = np.array([])
        self.time_array: np.ndarray = np.array([])
        self.previous_gfunctions: np.ndarray = np.array([])

    def calculate(self, time_value: Union[list, float, np.ndarray], borefield, alpha: float):
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

    def _check_prev_calculated(self) -> bool:

        # return false when
        if not self.store_previous_values:
            return False,

        # check if there is data saved

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

    def remove_previous_data(self):
        self.depth_array = np.array([])
        self.time_array = np.array([])
        self.previous_gfunctions = np.array([])

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

        keys = borefield[0].__dict__.keys()
        keys.pop("H")

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
