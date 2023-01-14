"""
This document contains the variable classes for the ground data, fluid data and pipe data.
"""

from math import pi
from GHEtool.VariableClasses.BaseClass import BaseClass

import numpy as np
import pygfunction as gt


class GroundData(BaseClass):
    """
    Contains information regarding the ground data of the borefield.
    """

    __slots__ = 'k_s', 'Tg', 'Rb', 'flux', 'volumetric_heat_capacity', 'alpha'

    def __init__(self, k_s: float = None,
                 T_g: float = None,
                 R_b: float = None,
                 volumetric_heat_capacity: float = 2.4 * 10**6,
                 flux: float = 0.06):
        """

        Parameters
        ----------
        k_s : float
            Ground thermal conductivity [W/mK]
        T_g : float
            Surface ground temperature [deg C]
            (this is equal to the ground temperature at infinity when no heat flux is given (default))
        R_b : float
            Equivalent borehole resistance [mK/W]
        volumetric_heat_capacity : float
            The volumetric heat capacity of the ground [J/m3K]
        flux : float
            The geothermal heat flux [W/m2]
        """

        self.k_s = k_s  # W/mK
        self.Tg = T_g  # °C
        self.Rb = R_b  # mK/W
        self.volumetric_heat_capacity = volumetric_heat_capacity  # J/m3K
        if self.volumetric_heat_capacity is None or self.k_s is None:
            self.alpha = None
        else:
            self.alpha = self.k_s / self.volumetric_heat_capacity  # m2/s
        self.flux = flux  # W/m2

    def calculate_Tg(self, H: float, use_constant_Tg: bool) -> float:
        """
        This function gives back the ground temperature
        When use_constant_Tg is False, the thermal heat flux is taken into account.

        Parameters
        ----------
        H : float
            Depth at which the temperature should be calculated [m]
        use_constant_Tg : bool
            True if a constant ground temperature should be used

        Returns
        -------
        Tg : float
            Ground temperature [deg C]
        """
        if use_constant_Tg:
            return self.Tg

        # geothermal gradient is equal to the geothermal heat flux divided by the thermal conductivity
        # avg ground temperature is (Tg + gradient + Tg) / 2 = Tg + gradient / 2
        return self.Tg + H * self.flux / self.k_s / 2

    def __eq__(self, other):
        if not isinstance(other, GroundData):
            return False
        for i in self.__slots__:
            if getattr(self, i) != getattr(other, i):
                return False
        return True


class FluidData(BaseClass):
    """
    Contains information regarding the fluid data of the borefield.
    """

    __slots__ = 'k_f', 'rho', 'Cp', 'mu', 'mfr', 'h_f', 'R_f'

    def __init__(self, mfr: float = None,
                 k_f: float = None,
                 rho: float = None,
                 Cp: float = None,
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
        Cp : float
            Thermal capacity of the fluid [J/kgK]
        mu : float
            Dynamic viscosity of the fluid [Pa/s]
        """
        self.k_f = k_f  # Thermal conductivity W/mK
        self.mfr = mfr  # Mass flow rate per borehole kg/s
        self.rho = rho  # Density kg/m3
        self.Cp = Cp    # Thermal capacity J/kgK
        self.mu = mu    # Dynamic viscosity Pa/s
        self.h_f: float = 0.  # convective heat transfer coefficient
        self.R_f: float = 0.  # fluid thermal resistance

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


class PipeData(BaseClass):
    """
    Contains information regarding the pipe data of the borefield.
    """

    __slots__ = 'r_in', 'r_out', 'k_p', 'D_s', 'number_of_pipes', 'epsilon', 'k_g', 'R_p', 'pos'

    def __init__(self, k_g: float = None,
                 r_in: float = None,
                 r_out: float = None,
                 k_p: float = None,
                 D_s: float = None,
                 number_of_pipes: int = 1,
                 epsilon: float = 1e-6):
        """

        Parameters
        ----------
        k_g : float
            Grout thermal conductivity [W/mK]
        r_in : float
            Inner pipe radius [m]
        r_out : float
            Outer pipe radius [m]
        k_p : float
            Pipe thermal conductivity [W/mK]
        D_s : float
            Distance of the pipe until center [m]
        number_of_pipes : int
            Number of pipes [#] (single U-tube: 1, double U-tube:2)
        epsilon : float
            Pipe roughness [m]
        """

        self.k_g = k_g                      # grout thermal conductivity W/mK
        self.r_in = r_in                    # inner pipe radius m
        self.r_out = r_out                  # outer pipe radius m
        self.k_p = k_p                      # pipe thermal conductivity W/mK
        self.D_s = D_s                      # distance of pipe until center m
        self.number_of_pipes = number_of_pipes  # number of pipes #
        self.epsilon = epsilon              # pipe roughness m
        self.R_p: float = 0.
        self.pos = []
        if self.check_values():
            self.pos = self._axis_symmetrical_pipe  # position of the pipes

    @property
    def _axis_symmetrical_pipe(self) -> list:
        """
        This function gives back the coordinates of the pipes in an axis-symmetrical pipe.

        Returns
        -------
        Positions : list
            List of coordinates tuples of the pipes in the borehole
        """
        dt: float = pi / float(self.number_of_pipes)
        pos: list = [(0., 0.)] * 2 * self.number_of_pipes
        for i in range(self.number_of_pipes):
            pos[i] = (self.D_s * np.cos(2.0 * i * dt + pi), self.D_s * np.sin(2.0 * i * dt + pi))
            pos[i + self.number_of_pipes] = (self.D_s * np.cos(2.0 * i * dt + pi + dt), self.D_s * np.sin(2.0 * i * dt + pi + dt))
        return pos

    def calculate_pipe_thermal_resistance(self) -> None:
        """
        This function calculates and sets the pipe thermal resistance R_p.

        Returns
        -------
        R_p : float
            The pipe thermal resistance [mK/W]
        """
        self.R_p: float = gt.pipes.conduction_thermal_resistance_circular_pipe(self.r_in, self.r_out, self.k_p)

    def __eq__(self, other):
        if not isinstance(other, PipeData):
            return False
        for i in self.__slots__:
            if getattr(self, i) != getattr(other, i):
                return False
        return True
