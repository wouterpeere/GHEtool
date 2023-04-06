"""
This file contains the base class for the load classes.
"""
import abc
from abc import ABC

import numpy as np

from GHEtool.VariableClasses.BaseClass import BaseClass


class _LoadData(BaseClass, ABC):
    """
    This class contains information w.r.t. load data for the borefield sizing.
    """
    __slots__ = "hourly_resolution"

    def __init__(self, hourly_resolution: bool):
        self.hourly_resolution: bool = hourly_resolution

    @abc.abstractmethod
    def _check_input(self, input) -> bool:
        """

        Parameters
        ----------
        input

        Returns
        -------

        """

    @abc.abstractmethod
    def peak_heating(self) -> np.array:
        """

        Returns
        -------

        """

    @abc.abstractmethod
    def peak_cooling(self) -> np.array:
        """

        Returns
        -------

        """

    @abc.abstractmethod
    def baseload_heating(self) -> np.array:
        """

        Returns
        -------

        """

    @abc.abstractmethod
    def baseload_cooling(self) -> np.array:
        """

        Returns
        -------

        """

    @property
    def imbalance(self) -> float:
        """

        Returns
        -------
        imbalance : float
        """
        return np.sum(self.baseload_cooling() - self.baseload_heating())