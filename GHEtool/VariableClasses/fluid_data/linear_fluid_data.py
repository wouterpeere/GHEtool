import numpy as np
from numpy.typing import NDArray

from .base_class import FluidData


class LinearFluidData(FluidData):
    """
    Contains information regarding the fluid data of the borefield.
    """
    __slots__ = '_k_f', '_rho', '_c_p', '_mu', 'mfr', 'h_f', 'R_f', '_k_f_factor', '_rho_factor', '_c_p_factor', '_mu_factor'

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
        self._k_f_factor: float = 0.
        self._rho_factor: float = 0.
        self._c_p_factor: float = 0.
        self._mu_factor: float = 0.

    def set_linear_factor(self, fac_k_f: float, fac_rho: float, fac_mu: float, fac_c_p: float):
        """
        set linear temperature factors
        Parameters
        ----------
        fac_k_f: float
            conductivity factor
        fac_rho: float
            density factor
        fac_mu:
            viscosity factor
        fac_c_p: float
            thermal capacity factor

        Returns
        -------
            None
        """
        self.set_linear_th_capacity_factor(fac_c_p)
        self.set_linear_conductivity_factor(fac_k_f)
        self.set_linear_viscosity_factor(fac_mu)
        self.set_linear_density_factor(fac_rho)

    def set_linear_conductivity_factor(self, factor: float):
        """
        set the linear temperature factor for the conductivity

        Parameters
        ----------
        factor: float
            linear factor (k_f(t) = k_f + factor * t

        """
        self._k_f_factor = factor

    def set_linear_viscosity_factor(self, factor: float):
        """
        set the linear temperature factor for the viscosity

        Parameters
        ----------
        factor: float
            linear factor (mu(t) = mu + factor * t

        """
        self._mu_factor = factor

    def set_linear_density_factor(self, factor: float):
        """
        set the linear temperature factor for the density

        Parameters
        ----------
        factor: float
            linear factor (rho(t) = rho + factor * t

        """
        self._rho_factor = factor

    def set_linear_th_capacity_factor(self, factor: float):
        """
        set the linear temperature factor for the thermal capacity

        Parameters
        ----------
        factor: float
            linear factor (c_p(t) = c_p + factor * t

        """
        self._c_p_factor = factor

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
        return self._k_f + self._k_f_factor * temps

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
        return self._rho + self._rho_factor * temps

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
        return self._c_p + self._c_p_factor * temps

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
        return self._mu + self._mu_factor * temps


