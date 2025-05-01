from GHEtool.VariableClasses.GroundData._GroundData import _GroundData


class GroundTemperatureGradient(_GroundData):
    __slots__ = _GroundData.__slots__ + ('gradient',)

    def __init__(self, k_s: float = None,
                 T_g: float = None,
                 volumetric_heat_capacity: float = 2.4 * 10 ** 6,
                 gradient: float = 3.0):
        """

        Parameters
        ----------
        k_s : float
            Ground thermal conductivity [W/mK]
        T_g : float
            Surface ground temperature [deg C]
        volumetric_heat_capacity : float
            The volumetric heat capacity of the ground [J/m3K]
        gradient : float
            The geothermal temperature gradient [K/100m]
        """
        super().__init__(k_s=k_s, volumetric_heat_capacity=volumetric_heat_capacity)
        self.gradient = gradient
        self.Tg = T_g

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
        # divide by 100 since the gradient is in K/100m
        # take the average between the depth and the start depth
        temperature_at_bottom_borehole = self.Tg + (depth * self.gradient / 2 / 100)
        temperature_at_start_borehole = self.Tg + (start_depth * self.gradient / 2 / 100)
        if depth == 0:
            return temperature_at_bottom_borehole
        return (temperature_at_bottom_borehole * depth - temperature_at_start_borehole * start_depth) / (
                depth - start_depth)

    def calculate_delta_H(self, temperature_diff: float) -> float:
        """
        This function calculates the difference in depth for a given difference in temperature.

        Parameters
        ----------
        temperature_diff : float
            Difference in temperature [deg C]

        Returns
        -------
        float
            Difference in depth [m]
        """
        return temperature_diff * 2 * 100 / self.gradient

    def __export__(self):
        temp = {
            'type': 'Ground gradient temperature',
            'Ground surface temperature [°C]': self.Tg,
            'Gradient [K/100m]': self.gradient
        }
        temp.update(super().__export__())
        return temp
