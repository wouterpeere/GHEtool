
class GroundData:
    __slots__ = 'H', 'B', 'k_s', 'Tg', 'Rb', 'N_1', 'N_2'

    def __init__(self, h: float, b: float, k_s: float, t_g: float, r_b: float, n_1: int, n_2: int) -> None:
        """
        Data for storage of ground data
        :param h: Depth of boreholes [m]
        :param b: Borehole spacing [m]
        :param k_s: Ground thermal conductivity [W/m.K]
        :param t_g: Ground temperature at infinity [°C]
        :param r_b: Equivalent borehole resistance [m K/W]
        :param n_1: Width of rectangular field [#]
        :param n_2: Length of rectangular field [#]
        """
        self.H = h  # m
        self.B = b  # m
        self.k_s = k_s  # W/mK
        self.Tg = t_g  # °C
        self.Rb = r_b  # mK/W
        self.N_1 = n_1  # #
        self.N_2 = n_2  # #

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

    __slots__ = 'r_in', 'r_out', 'k_p', 'D_s', 'r_b', 'numberOfPipes', 'epsilon', 'k_g', 'D'

    def __init__(self, k_g: float, r_in: float, r_out: float, k_p: float, D_s: float, r_b: float, numberOfPipes: int,
                 epsilon: float = 1e-6, D: float = 4) -> None:
        """
        Data for storage of ground data
        :param k_g: Grout thermal conductivity [W/mK]
        :param r_in: Inner pipe radius [m]
        :param r_out: Outer pipe radius [m]
        :param k_p: Pipe thermal conductivity [W/mK]
        :param D_s: Distance of the pipe until center [m]
        :param r_b: Borehole radius [m]
        :param numberOfPipes: Number of pipes [#] (single U-tube: 1, double U-tube:2)
        :param epsilon: Pipe roughness [m]
        :param D: Burrial depth [m]
        """

        self.k_g = k_g                      # grout thermal conductivity W/mK
        self.r_in = r_in                    # inner pipe radius m
        self.r_out = r_out                  # outer pipe radius m
        self.k_p = k_p                      # pipe thermal conductivity W/mK
        self.D_s = D_s                      # distance of pipe until center m
        self.r_b = r_b                      # borehole radius m
        self.numberOfPipes = numberOfPipes  # number of pipes #
        self.epsilon = epsilon              # pipe roughness m
        self.D = D                          # burial depth m

    def __eq__(self, other):
        if not isinstance(other, FluidData):
            return False
        for i in self.__slots__:
            if getattr(self, i) != getattr(other, i):
                return False
        return True
