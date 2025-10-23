from GHEtool.VariableClasses.GroundData._GroundData import _GroundData


class GroundFluxTemperature(_GroundData):
    __slots__ = _GroundData.__slots__ + ('flux',)

    def __init__(self, k_s: float = None,
                 T_g: float = None,
                 volumetric_heat_capacity: float = 2.4 * 10 ** 6,
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

    def calculate_Tg(self, depth: float = 100, start_depth: float = 0) -> float:
        """
        This function gives back the average ground temperature for the borehole.

        Parameters
        ----------
        depth : float
            Depth of the borehole [m]
        start_depth : float
            Depth at which the borehole starts [m]

        Returns
        -------
        Tg : float
            Ground temperature [deg C]
        """
        # geothermal gradient is equal to the geothermal heat flux divided by the thermal conductivity
        # avg ground temperature is (Tg + gradient + Tg) / 2 = Tg + gradient / 2
        # take the average between the depth and the start depth
        temperature_at_bottom_borehole = self.Tg + (depth * self.flux / self.k_s(depth)) / 2
        temperature_at_start_borehole = self.Tg + (start_depth * self.flux / self.k_s(start_depth)) / 2
        if depth == 0:
            return temperature_at_bottom_borehole
        return (temperature_at_bottom_borehole * depth - temperature_at_start_borehole * start_depth) / (
                depth - start_depth)

    def calculate_delta_H(self, temperature_diff: float, H: float = 100) -> float:
        """
        This function calculates the difference in depth for a given difference in temperature.

        Parameters
        ----------
        temperature_diff : float
            Difference in temperature [deg C]
        H : float
            Depth at which the average ground thermal conductivity should be taken [m]

        Returns
        -------
        float
            Difference in depth [m]
        """
        return temperature_diff * 2 * self.k_s(H) / self.flux

    def __export__(self):
        temp = {
            'type': 'Ground flux temperature',
            'Ground surface temperature [°C]': self.Tg,
            'Ground flux [W/m²]': self.flux
        }
        temp.update(super().__export__())
        return temp
