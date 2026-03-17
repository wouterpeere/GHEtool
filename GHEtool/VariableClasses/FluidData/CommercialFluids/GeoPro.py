"""
This file contains the data of the GeoPro antifreeze from InnoGreenChem.
Visit https://innogreenchem.com/product/geopro/ for more information.
"""

import numpy as np

from GHEtool.VariableClasses.FluidData.CommercialFluids._CommercialFluids import _CommercialFluids


class GeoPro(_CommercialFluids):

    def __init__(self, volume_ratio: float):
        super().__init__(volume_ratio)

        self._temperatures = np.array([50, 40, 30, 20, 10, 0, -10, -15])
        self._volume_ratio_array = np.array([25, 30, 40]) / 100

        self._freezing_array = np.array([-10, -15, -20])
        self._k_f_array = np.array([
            [0.559, 0.525, 0.481],  # 50°C
            [0.549, 0.519, 0.478],  # 40°C
            [0.539, 0.513, 0.475],  # 30°C
            [0.529, 0.507, 0.472],  # 20°C
            [0.519, 0.501, 0.469],  # 10°C
            [0.509, 0.495, 0.466],  # 0°C
            [np.nan, 0.489, 0.463],  # -10°C
            [np.nan, np.nan, 0.461],  # -15°C
        ])  # W/(mK)

        self._rho_array = np.array([
            [1.109, 1.115, 1.165],  # 50°C
            [1.113, 1.121, 1.168],  # 40°C
            [1.117, 1.127, 1.171],  # 30°C
            [1.121, 1.133, 1.174],  # 20°C
            [1.125, 1.139, 1.177],  # 10°C
            [1.129, 1.145, 1.180],  # 0°C
            [np.nan, 1.151, 1.183],  # -10°C
            [np.nan, np.nan, 1.185],  # -15°C
        ]) * 1000  # kg/m³

        self._mu_array = np.array([
            [1.493, 1.510, 2.377],  # 50°C
            [1.420, 1.520, 2.129],  # 40°C
            [1.459, 1.528, 2.173],  # 30°C
            [1.658, 1.879, 2.437],  # 20°C
            [2.017, 2.430, 3.041],  # 10°C
            [2.788, 3.241, 4.297],  # 0°C
            [np.nan, 4.372, 6.709],  # -10°C
            [np.nan, np.nan, 8.559],  # -15°C
        ]) * 1e-6 * self._rho_array  # convert from kinematic viscosity in mm²/s to dynamic viscosity in Pa.s

        self._cp_array = np.array([
            [3.36, 3.32, 3.12],  # 50°C
            [3.34, 3.28, 3.11],  # 40°C
            [3.32, 3.25, 3.09],  # 30°C
            [3.30, 3.22, 3.08],  # 20°C
            [3.29, 3.20, 3.07],  # 10°C
            [3.28, 3.19, 3.05],  # 0°C
            [np.nan, 3.18, 3.04],  # -10°C
            [np.nan, np.nan, 3.03],  # -15°C
        ]) * 1000  # J/(kgK)

        if self.check_volume_ratio(volume_ratio):
            self._volume_ratio = volume_ratio

        # update nan values
        self._fill_nan_values_vertically()
