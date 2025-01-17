from GHEtool.VariableClasses.GroundData._GroundData import _GroundData


class GroundConstantTemperature(_GroundData):
    __slots__ = _GroundData.__slots__

    def __init__(self, k_s: float = None,
                 T_g: float = None,
                 volumetric_heat_capacity: float = 2.4 * 10 ** 6):
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
        return self.Tg

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
        return 0

    def __repr__(self):
        return f'Constant ground temperature\n\tGround temperature at infinity [°C]: {self.Tg}\n\t' + super().__repr__()
