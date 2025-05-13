"""
This document contains the framework for all the commercial fluids.
"""

import numpy as np
import scipy as sc


class _CommercialFluids:

    def __init__(self):
        self._temperatures = np.array([])
        self._volume_percentages = np.array([])
        self._percentage = 0

        self._freezing_array = np.array([])
        self._k_f_array = np.array([])
        self._mu_array = np.array([])
        self._rho_array = np.array([])
        self._cp_array = np.array([])

    def check_percentage(self, percentage: float) -> bool:
        """
        Checks if there is data for the percentage. If not a ValueError is raised.

        Parameters
        ----------
        percentage : float
            Volume percentage

        Returns
        -------
        bool
            True if there is data

        Raises
        ------
        ValueError
            If the requested percentage is outside the data range
        """
        if min(self._volume_percentages) <= percentage <= max(self._volume_percentages):
            return True
        raise ValueError(
            f'The percentage {percentage} is outside the data range of {min(self._volume_percentages)} - {max(self._volume_percentages)}.')

    def freeze_point(self, percentage: float) -> float:
        if self.check_percentage(percentage):
            return np.interp(percentage, self._volume_percentages, self._freezing_array)

    def conductivity(self, temperature: float, percentage: float = None):
        return sc.interpolate.interpn((self._volume_percentages, self._temperatures), self._k_f_array,
                                      (temperature, self._percentage if percentage is None else percentage))

    def viscosity(self, temperature: float, percentage: float = None):
        return sc.interpolate.interpn((self._volume_percentages, self._temperatures), self._mu_array,
                                      (temperature, self._percentage if percentage is None else percentage))

    def density(self, temperature: float, percentage: float = None):
        return sc.interpolate.interpn((self._volume_percentages, self._temperatures), self._rho_array,
                                      (temperature, self._percentage if percentage is None else percentage))

    def specific_heat(self, temperature: float, percentage: float = None):
        return sc.interpolate.interpn((self._volume_percentages, self._temperatures), self._cp_array,
                                      (temperature, self._percentage if percentage is None else percentage))
