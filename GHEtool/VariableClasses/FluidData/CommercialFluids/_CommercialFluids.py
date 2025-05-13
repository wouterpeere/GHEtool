"""
This document contains the framework for all the commercial fluids.
"""

import numpy as np
import scipy as sc


class _CommercialFluids:

    def __init__(self):
        self._temperatures = np.array([])
        self._volume_ratio_array = np.array([])
        self._volume_ratio = 0

        self._freezing_array = np.array([])
        self._k_f_array = np.array([])
        self._mu_array = np.array([])
        self._rho_array = np.array([])
        self._cp_array = np.array([])

    def check_volume_ratio(self, volume_ratio: float) -> bool:
        """
        Checks if there is data for the volume ratio. If not a ValueError is raised.

        Parameters
        ----------
        volume_ratio : float
            Volume ratio (0-1)

        Returns
        -------
        bool
            True if there is data

        Raises
        ------
        ValueError
            If the requested percentage is outside the data range
        """
        if min(self._volume_ratio_array) <= volume_ratio <= max(self._volume_ratio_array):
            return True
        raise ValueError(
            f'The volume ratio {volume_ratio} is outside the data range of {min(self._volume_ratio_array)} - {max(self._volume_ratio_array)}.')

    def freeze_point(self, volume_ratio: float) -> float:
        if self.check_volume_ratio(volume_ratio):
            return np.interp(volume_ratio, self._volume_ratio_array, self._freezing_array)

    def conductivity(self, temperature: float, volume_ratio: float = None):
        return sc.interpolate.interpn((self._temperatures, self._volume_ratio_array), self._k_f_array,
                                      (temperature, self._volume_ratio if volume_ratio is None else volume_ratio))

    def viscosity(self, temperature: float, percentage: float = None):
        return sc.interpolate.interpn((self._volume_ratio, self._temperatures), self._mu_array,
                                      (temperature, self._percentage if percentage is None else percentage))

    def density(self, temperature: float, percentage: float = None):
        return sc.interpolate.interpn((self._volume_ratio, self._temperatures), self._rho_array,
                                      (temperature, self._percentage if percentage is None else percentage))

    def specific_heat(self, temperature: float, percentage: float = None):
        return sc.interpolate.interpn((self._volume_ratio, self._temperatures), self._cp_array,
                                      (temperature, self._percentage if percentage is None else percentage))
