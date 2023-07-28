from GHEtool.VariableClasses.GroundData._GroundData import _GroundData


class GroundConstantTemperature(_GroundData):

    __slots__ = _GroundData.__slots__ + ('Tg',)

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

    def calculate_Tg(self, H: float = None) -> float:
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


    def max_depth(self, max_temp) -> float:
        return self.Tg

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
        return (calculated_old_temperature - self.Tg) / (limiting_temperature - self.Tg) * perv_depth