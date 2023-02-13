"""
This file contains the class of ground data with a flux temperature.
"""

from GHEtool.VariableClasses.GroundData import GroundDataBaseClass


class GroundFluxTemperature(GroundDataBaseClass):

    __slots__ = 'flux', 'Tg', 'k_s', 'volumetric_heat_capacity'

    def __init__(self, k_s: float = None,
                 T_g: float = None,
                 volumetric_heat_capacity: float = 2.4 * 10**6,
                 flux: float = 0.06):
        """

        Parameters
        ----------
        k_s : float
            Ground thermal conductivity [W/mK]
        T_g : float
            Surface ground temperature [deg C]
        volumetric_heat_capacity : float
            The volumetric heat capacity of the ground [J/m3K]
        flux : float
            The geothermal heat flux [W/m2]
        """
        super().__init__(k_s=k_s, volumetric_heat_capacity=volumetric_heat_capacity)
        self.flux = flux
        self.Tg = T_g

    def calculate_Tg(self, H: float) -> float:
        """
        This function gives back the ground temperature at a depth H.

        Parameters
        ----------
        H : float
            Depth at which the temperature should be calculated [m]

        Returns
        -------
        Tg : float
            Ground temperature [deg C]
        """
        # geothermal gradient is equal to the geothermal heat flux divided by the thermal conductivity
        # avg ground temperature is (Tg + gradient + Tg) / 2 = Tg + gradient / 2
        return self.Tg + H * self.flux / self.k_s / 2
