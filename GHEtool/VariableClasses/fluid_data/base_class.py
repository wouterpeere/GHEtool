import numpy as np
from numpy.typing import NDArray

from GHEtool.VariableClasses.BaseClass import BaseClass
from abc import ABC, abstractmethod


class FluidData(BaseClass, ABC):
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
        self._k_f = k_f  # Thermal conductivity W/mK
        self.mfr = mfr  # Mass flow rate per borehole kg/s
        self._rho = rho  # Density kg/m3
        self._c_p = c_p    # Thermal capacity J/kgK
        self._mu = mu    # Dynamic viscosity Pa/s
        self.h_f: NDArray[np.float64] = np.empty(0)  # convective heat transfer coefficient
        self.R_f: NDArray[np.float64] = np.empty(0)  # fluid thermal resistance

    @abstractmethod
    def k_f(self, temps: NDArray[np.float64]) -> NDArray[np.float64]:
        """"""

    @abstractmethod
    def rho(self, temps: NDArray[np.float64]) -> NDArray[np.float64]:
        """"""

    @abstractmethod
    def c_p(self, temps: NDArray[np.float64]) -> NDArray[np.float64]:
        """"""

    @abstractmethod
    def mu(self, temps: NDArray[np.float64]) -> NDArray[np.float64]:
        """"""

    def set_mass_flow_rate(self, mfr: float) -> None:
        """
        This function sets the mass flow rate per borehole.

        Parameters
        ----------
        mfr : fluid
            Mass flow rate per borehole [kg/s]

        Returns
        -------
        None
        """
        self.mfr = mfr

    def __eq__(self, other):
        if not isinstance(other, FluidData):
            return False
        for i in self.__slots__:
            if getattr(self, i) != getattr(other, i):
                return False
        return True
