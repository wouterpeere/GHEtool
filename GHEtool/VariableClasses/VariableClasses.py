import warnings


class GroundData:
    __slots__ = 'k_s', 'Tg', 'Rb', 'flux', 'volumetric_heat_capacity', 'alpha'

    def __init__(self, k_s: float, T_g: float, R_b: float, volumetric_heat_capacity: float = 2.4 * 10**6, flux: float = 0.06) -> None:
        """
        Data for storage of ground data

        :param k_s: Ground thermal conductivity [W/m.K]
        :param T_g: Surface ground temperature [deg C]
        (this is equal to the ground temperature at infinity when no heat flux is given (default))
        :param R_b: Equivalent borehole resistance [m K/W]
        :param volumetric_heat_capacity: The volumetric heat capacity of the ground (J/m3K)
        :param flux: the geothermal heat flux (W/m2)
        :return: None
        """

        self.k_s = k_s  # W/mK
        self.Tg = T_g  # °C
        self.Rb = R_b  # mK/W
        self.volumetric_heat_capacity = volumetric_heat_capacity  # J/m3K
        self.alpha = self.k_s / self.volumetric_heat_capacity  # m2/s
        self.flux = flux  # W/m2

    def __eq__(self, other):
        if not isinstance(other, GroundData):
            return False
        for i in self.__slots__:
            if getattr(self, i) != getattr(other, i):
                return False
        return True


class FluidData:

    __slots__ = 'k_f', 'rho', 'Cp', 'mu', 'mfr'

    def __init__(self, mfr: float, k_f: float, rho: float, Cp: float, mu: float) -> None:
        """
        Data for storage of ground data

        :param mfr: Mass flow rate per borehole [kg/s]
        :param k_f: Thermal Conductivity [W/mK]
        :param rho: Density [kg/m3]
        :param Cp: Thermal capacity [J/kgK]
        :param mu: EDynamic viscosity [Pa/s]
        :return: None
        """

        self.k_f = k_f  # Thermal conductivity W/mK
        self.mfr = mfr  # Mass flow rate per borehole kg/s
        self.rho = rho  # Density kg/m3
        self.Cp = Cp    # Thermal capacity J/kgK
        self.mu = mu    # Dynamic viscosity Pa/s

    def __eq__(self, other):
        if not isinstance(other, FluidData):
            return False
        for i in self.__slots__:
            if getattr(self, i) != getattr(other, i):
                return False
        return True


class PipeData:

    __slots__ = 'r_in', 'r_out', 'k_p', 'D_s', 'number_of_pipes', 'epsilon', 'k_g'

    def __init__(self, k_g: float, r_in: float, r_out: float, k_p: float, D_s: float, number_of_pipes: int = 1,
                 epsilon: float = 1e-6) -> None:
        """
        Data for storage of ground data

        :param k_g: Grout thermal conductivity [W/mK]
        :param r_in: Inner pipe radius [m]
        :param r_out: Outer pipe radius [m]
        :param k_p: Pipe thermal conductivity [W/mK]
        :param D_s: Distance of the pipe until center [m]
        :param number_of_pipes: Number of pipes [#] (single U-tube: 1, double U-tube:2)
        :param epsilon: Pipe roughness [m]
        :return: None
        """

        self.k_g = k_g                      # grout thermal conductivity W/mK
        self.r_in = r_in                    # inner pipe radius m
        self.r_out = r_out                  # outer pipe radius m
        self.k_p = k_p                      # pipe thermal conductivity W/mK
        self.D_s = D_s                      # distance of pipe until center m
        self.number_of_pipes = number_of_pipes  # number of pipes #
        self.epsilon = epsilon              # pipe roughness m

    def __eq__(self, other):
        if not isinstance(other, PipeData):
            return False
        for i in self.__slots__:
            if getattr(self, i) != getattr(other, i):
                return False
        return True
