"""
This document contains the framework for all the commercial fluids.
"""

import numpy as np
import pandas as pd
import scipy as sc


class _CommercialFluids:

    def __init__(self, _volume_ratio):
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
            return float(np.interp(volume_ratio, self._volume_ratio_array, self._freezing_array))

    def conductivity(self, temp: float, volume_ratio: float = None):
        temp = sc.interpolate.interpn((self._temperatures, self._volume_ratio_array), self._k_f_array,
                                      (temp, self._volume_ratio if volume_ratio is None else volume_ratio),
                                      bounds_error=False)
        if len(temp) == 1:
            return temp[0]
        return temp

    def viscosity(self, temp: float, volume_ratio: float = None):
        temp = sc.interpolate.interpn((self._temperatures, self._volume_ratio_array), self._mu_array,
                                      (temp, self._volume_ratio if volume_ratio is None else volume_ratio),
                                      bounds_error=False)
        if len(temp) == 1:
            return temp[0]
        return temp

    def density(self, temp: float, volume_ratio: float = None):
        temp = sc.interpolate.interpn((self._temperatures, self._volume_ratio_array), self._rho_array,
                                      (temp, self._volume_ratio if volume_ratio is None else volume_ratio),
                                      bounds_error=False)
        if len(temp) == 1:
            return temp[0]
        return temp

    def specific_heat(self, temp: float, volume_ratio: float = None):
        temp = sc.interpolate.interpn((self._temperatures, self._volume_ratio_array), self._cp_array,
                                      (temp, self._volume_ratio if volume_ratio is None else volume_ratio),
                                      bounds_error=False)
        if len(temp) == 1:
            return temp[0]
        return temp

    def _fill_nan_values_vertically(self) -> None:
        """
        Fill NaN values in a 2D array by interpolating vertically (column-wise).

        Returns
        -------
        None
        """
        self._k_f_array = pd.DataFrame(self._k_f_array).interpolate(axis=0, limit_direction='both').to_numpy()
        self._rho_array = pd.DataFrame(self._rho_array).interpolate(axis=0, limit_direction='both').to_numpy()
        self._mu_array = pd.DataFrame(self._mu_array).interpolate(axis=0, limit_direction='both').to_numpy()
        self._cp_array = pd.DataFrame(self._cp_array).interpolate(axis=0, limit_direction='both').to_numpy()
