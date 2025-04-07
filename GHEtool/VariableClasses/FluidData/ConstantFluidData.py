from GHEtool.VariableClasses.FluidData._FluidData import _FluidData
from GHEtool.VariableClasses.BaseClass import BaseClass


class ConstantFluidData(_FluidData, BaseClass):
    """
    Contains information regarding the fluid data of the borefield, assuming there is no temperature dependency.
    """

    __slots__ = '_k_f', '_rho', '_cp', '_mu', '_freezing_point'
    __allow_none__ = '_freezing_point'

    def __init__(self, k_f: float, rho: float, cp: float, mu: float, freezing_point: float = None):
        """

        Parameters
        ----------
        k_f : float
            Thermal Conductivity of the fluid [W/(mK)]
        rho : float
            Density of the fluid [kg/m3]
        cp : float
            Thermal capacity of the fluid [J/(kgK)]
        mu : float
            Dynamic viscosity of the fluid [Pa.s]
        freezing_point : float
            Freezing point of the fluid (optional) [°C]
        """
        self._k_f: float = k_f  # Thermal conductivity W/(mK)
        self._rho: float = rho  # Density kg/m^3
        self._cp: float = cp  # Thermal capacity J/(kgK)
        self._mu: float = mu  # Dynamic viscosity Pa.s
        super().__init__(freezing_point)

    def k_f(self, **kwargs) -> float:
        """
        This function returns the conductivity of the fluid in W/(mK).

        Returns
        -------
        float
            Fluid thermal conductivity [W/(mK)]
        """
        return self._k_f

    def rho(self, **kwargs) -> float:
        """
        This function returns the density of the fluid in kg/m^3.

        Returns
        -------
        float
            Density [kg/m^3]
        """
        return self._rho

    def cp(self, **kwargs) -> float:
        """
        This function returns the heat capacity of the fluid in J/(kgK).

        Returns
        -------
        float
            Heat capacity of the fluid [J/(kgK)]
        """
        return self._cp

    def mu(self, **kwargs) -> float:
        """
        This function returns the dynamic viscosity of the fluid in Pa.s.

        Returns
        -------
        float
            Dynamic viscosity [Pa.s]
        """
        return self._mu

    def __eq__(self, other):
        if not isinstance(other, ConstantFluidData):
            return False
        if self._k_f != other._k_f or self._mu != other._mu or self._rho != other._rho or self._cp != other._cp:
            return False
        return True

    def __repr__(self):
        return {
            'k_f [W/(m·K)]': self.k_f(),
            'rho [kg/m³]': self.rho(),
            'cp [J/(kg·K)]': self.cp(),
            'mu [Pa·s]': self.mu(),
            'nu [m²/s]': self.nu(),
            'Pr': self.Pr(),
            'freezing_point [°C]': self.freezing_point
        }
