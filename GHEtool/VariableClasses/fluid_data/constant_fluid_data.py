import numpy as np
from numpy.typing import NDArray

from .base_class import FluidData


class ConstantFluidData(FluidData):
    """
    Contains information regarding the fluid data of the borefield.
    """

    __slots__ = '_k_f', '_rho', '_c_p', '_mu', 'mfr', 'h_f', 'R_f'

    def __init__(self, mfr: float = None,
                 k_f: float = None,
                 rho: float = None,
                 c_p: float = None,
                 mu: float = None):
        """

        Parameters
        ----------
        mfr : float
            Mass flow rate per borehole [kg/s]
        k_f : float
            Thermal Conductivity of the fluid [W/mK]
        rho : float
            Density of the fluid [kg/m3]
        c_p : float
            Thermal capacity of the fluid [J/kgK]
        mu : float
            Dynamic viscosity of the fluid [Pa/s]
        """
        super().__init__(mfr, k_f, rho, c_p, mu)

    def k_f(self, temps: NDArray[np.float64]) -> NDArray[np.float64]:
        """
        determines the conductivity for the input temperatures

        Parameters
        ----------
        temps: NDArray[np.float64]
            temperatures to calculate conductivity for

        Returns
        -------
            conductivity as an NDArray[np.float64]
        """
        return self._k_f * np.ones_like(temps)

    def rho(self, temps: NDArray[np.float64]) -> NDArray[np.float64]:
        """
        determines the density for the input temperatures

        Parameters
        ----------
        temps: NDArray[np.float64]
            temperatures to calculate density for

        Returns
        -------
            density as an NDArray[np.float64]
        """
        return self._rho * np.ones_like(temps)

    def c_p(self, temps: NDArray[np.float64]) -> NDArray[np.float64]:
        """
        determines the thermal capacity for the input temperatures

        Parameters
        ----------
        temps: NDArray[np.float64]
            temperatures to calculate thermal capacity for

        Returns
        -------
            thermal capacity as an NDArray[np.float64]
        """
        return self._c_p * np.ones_like(temps)

    def mu(self, temps: NDArray[np.float64]) -> NDArray[np.float64]:
        """
        determines the viscosity for the input temperatures

        Parameters
        ----------
        temps: NDArray[np.float64]
            temperatures to calculate viscosity for

        Returns
        -------
            viscosity as an NDArray[np.float64]
        """
        return self._mu * np.ones_like(temps)


