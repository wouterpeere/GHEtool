"""
This document contains the information for the BaseClass.
This class is used as a super class for different variable classes.
"""
from __future__ import annotations

import warnings
from typing import List

import numpy as np
from numpy import ndarray
from pygfunction.boreholes import Borehole
from importlib import import_module


class BaseClass:
    """
    This class contains basic functionality of different classes within GHEtool.

    This class should only be altered whenever a highly general method should be implemented.
    """

    __allow_none__ = []

    def check_values(self) -> bool:
        """
        This functions checks if the class attributes differ from None.

        Returns
        -------
        bool
            True if all values are correct. False otherwise
        """
        # get all variables in class
        if hasattr(self, "__slots__"):
            variables: List[str] = list(self.__slots__)
        else:
            variables: List[str] = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]

        temp = [getattr(self, var) is not None for var in variables if var not in self.__class__.__allow_none__]
        if all(temp):
            return True
        else:
            return False


class UnsolvableDueToTemperatureGradient(Exception):
    """
    This Exception occurs when there is an unsizeble borefield due to incompatibility between 1) peak cooling,
    which requires a deeper borefield and 2) a temperature gradient, which causes a higher ground temperature when
    the field is drilled deeper. This leads to unsizeble solutions.
    """
    def __init__(self):
        super().__init__('No solution can be found due to the temperature gradient. Please increase the field size.')


class MaximumNumberOfIterations(RuntimeError):
    """
    This Error occurs when the maximum number of interation is reacted.
    """
    def __init__(self, iter: int):
        super().__init__(f'The maximum number of iterations {iter} is crossed. There is no size convergence.')
