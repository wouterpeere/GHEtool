"""
This file contains the code for the ground data with a constant temperature.
"""

from GHEtool.VariableClasses.GroundData import GroundDataBaseClass


class GroundConstantTemperature(GroundDataBaseClass):

    __slots__ = 'Tg', 'k_s', 'volumetric_heat_capacity'

    def __init__(self, k_s: float = None,
                 T_g: float = None,
                 volumetric_heat_capacity: float = 2.4 * 10**6):
        """

        Parameters
        ----------
        k_s : float
            Ground thermal conductivity [W/mK]
        T_g : float
            Ground temperature at infinity [deg C]
        volumetric_heat_capacity : float
            The volumetric heat capacity of the ground [J/m3K]
        """

        super().__init__(k_s=k_s, volumetric_heat_capacity=volumetric_heat_capacity)
        self.Tg = T_g

    def calculate_Tg(self, H: float) -> float:
        """
        This function gives back the ground temperature.

        Parameters
        ----------
        H : float
            Depth of the borefield [m] (not used)

        Returns
        -------
        Tg : float
            Ground temperature [deg C]
        """
        return self.Tg
