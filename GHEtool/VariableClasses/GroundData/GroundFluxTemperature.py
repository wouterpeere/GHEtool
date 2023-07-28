from GHEtool.VariableClasses.GroundData._GroundData import _GroundData
from GHEtool.utils.solve_quadratic_equation import solve_quadratic


class GroundFluxTemperature(_GroundData):

    __slots__ = _GroundData.__slots__ + ('flux', 'Tg')

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
        self.variable_Tg = True

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

    def max_depth(self, max_temp) -> float:
        return (max_temp - self.Tg) * self.k_s / self.flux

    def delta_H(self, temp) -> float:
        return temp * 2 * self.k_s / self.flux

    def new_depth(self, limiting_temperature: float, perv_depth: float, calculated_old_temperature: float) -> float:
        """
        determines the new borehole depth based on old one

        Parameters
        ----------
        limiting_temperature: float
             temperature limit
        perv_depth: float
            previous depth
        calculated_old_temperature: float
            calculated temperature

        Returns
        -------
            new depth
        """
        t_max_l = (calculated_old_temperature - self.calculate_Tg(perv_depth)) * perv_depth
        root1, root2 = solve_quadratic(a=-self.flux / self.k_s / 2,b=(limiting_temperature - self.calculate_Tg(0)), c=-1*t_max_l)
        return min(root1, root2)