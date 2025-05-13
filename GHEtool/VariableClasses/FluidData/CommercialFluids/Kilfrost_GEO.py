import numpy as np

from GHEtool.VariableClasses.FluidData.CommercialFluids._CommercialFluids import _CommercialFluids


class KilfrostGEO(_CommercialFluids):

    def __init__(self, volume_ratio: float):
        super().__init__()

        self._temperatures = np.arange(-35, 45, 5)
        self._volume_ratio_array = np.array([20, 24, 32, 35, 39, 50, 60]) / 100

        self._freezing_array = np.array([-8.3, -10, -15, -17.5, -20, -30, -40])
        self._k_f_array = np.array([
            [0.579, 0.570, 0.550, 0.541, 0.532, 0.503, 0.479],  # 40°C
            [0.572, 0.564, 0.544, 0.536, 0.527, 0.499, 0.475],  # 35°C
            [0.566, 0.558, 0.538, 0.530, 0.521, 0.494, 0.471],  # 30°C
            [0.559, 0.551, 0.532, 0.524, 0.516, 0.489, 0.466],  # 25°C
            [0.552, 0.544, 0.526, 0.518, 0.510, 0.483, 0.461],  # 20°C
            [0.544, 0.537, 0.519, 0.511, 0.503, 0.478, 0.456],  # 15°C
            [0.536, 0.529, 0.512, 0.504, 0.497, 0.472, 0.451],  # 10°C
            [0.528, 0.521, 0.504, 0.497, 0.490, 0.466, 0.446],  # 5°C
            [0.519, 0.512, 0.496, 0.489, 0.482, 0.459, 0.440],  # 0°C
            [0.510, 0.504, 0.488, 0.482, 0.475, 0.453, 0.435],  # -5°C
            [np.nan, np.nan, 0.480, 0.473, 0.467, 0.446, 0.429],  # -10°C
            [np.nan, np.nan, np.nan, 0.465, 0.459, 0.439, 0.422],  # -15°C
            [np.nan, np.nan, np.nan, np.nan, np.nan, 0.432, 0.416],  # -20°C
            [np.nan, np.nan, np.nan, np.nan, np.nan, 0.424, 0.409],  # -25°C
            [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 0.403],  # -30°C
            [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 0.396],  # -35°C
        ])
        self._mu_array = np.array([])
        self._rho_array = np.array([])
        self._cp_array = np.array([])

        if self.check_volume_ratio(volume_ratio):
            self._volume_ratio = volume_ratio
