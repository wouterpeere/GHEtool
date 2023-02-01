"""
This document contains the variable classes for the ground data, fluid data and pipe data.
"""

from math import pi
from GHEtool.VariableClasses.BaseClass import BaseClass

import numpy as np
import pygfunction as gt

from typing import Callable

from abc import ABC, abstractmethod


class GroundData_Base(BaseClass, ABC):
    """
    Contains information regarding the ground data of the borefield.
    """

    __slots__ = 'k_s', 'Tg', 'Rb', 'volumetric_heat_capacity', 'alpha'

    def __init__(self, k_s: float = None,
                 T_g: float = None,
                 R_b: float = None,
                 volumetric_heat_capacity: float = 2.4 * 10**6):
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
        """

        self.k_s = k_s  # W/mK
        self.Tg = T_g  # °C
        self.Rb = R_b  # mK/W
        self.volumetric_heat_capacity = volumetric_heat_capacity  # J/m3K
        if self.volumetric_heat_capacity is None or self.k_s is None:
            self.alpha = None
        else:
            self.alpha = self.k_s / self.volumetric_heat_capacity  # m2/s

    @abstractmethod
    def calculate_Tg(self, H: float) -> float:
        """
        This function gives back the ground temperature
        When use_constant_Tg is False, the thermal heat flux is taken into account.

        Parameters
        ----------
        H : float
            Depth at which the temperature should be calculated [m]

        Returns
        -------
        Tg : float
            Ground temperature [deg C]
        """


    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        for i in self.__slots__:
            if getattr(self, i) != getattr(other, i):
                return False
        return True


class ConstantTempGround(GroundData_Base):
    """
    Contains information regarding the ground data of the borefield.
    """

    __slots__ = 'k_s', 'Tg', 'Rb', 'flux', 'volumetric_heat_capacity', 'alpha'

    def __init__(self, k_s: float = None, T_g: float = None, R_b: float = None, volumetric_heat_capacity: float = 2.4 * 10 ** 6):
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
        """

        super().__init__(k_s, T_g, R_b, volumetric_heat_capacity)

    def calculate_Tg(self, H: float) -> float:
        """
        This function gives back the ground temperature
        When use_constant_Tg is False, the thermal heat flux is taken into account.

        Parameters
        ----------
        H : float
            Depth at which the temperature should be calculated [m]

        Returns
        -------
        Tg : float
            Ground temperature [deg C]
        """
        return self.Tg


class RaisingTempGround(GroundData_Base):
    """
    Contains information regarding the ground data of the borefield.
    """

    __slots__ = 'flux'

    def __init__(self, k_s: float = None, T_g: float = None, R_b: float = None, volumetric_heat_capacity: float = 2.4 * 10 ** 6,
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

        super().__init__(k_s, T_g, R_b, volumetric_heat_capacity)
        self.flux = flux  # W/m2

    def calculate_Tg(self, H: float) -> float:
        """
        This function gives back the ground temperature
        When use_constant_Tg is False, the thermal heat flux is taken into account.

        Parameters
        ----------
        H : float
            Depth at which the temperature should be calculated [m]

        Returns
        -------
        Tg : float
            Ground temperature [deg C]
        """
        # geothermal gradient is equal to the geothermal heat flux divided by the thermal conductivity
        # avg ground temperature is (Tg + gradient + Tg) / 2 = Tg + gradient / 2
        return self.Tg + H * self.flux / self.k_s / 2


class TempProfileData(BaseClass):
    """Contains the data for temperature profile calculation"""

    __slots__ = 'd_t', 'phi', 'd', 'h_start'

    omega = 2 * pi / (3600 * 8760)

    def __init__(self, d_t: float, phi: float, h_start: float, k_s: float, heat_cap: float):
        self.d_t = d_t
        self.phi = phi
        self.d = np.sqrt(2*k_s/heat_cap/self.omega)
        self.h_start = h_start




class GroundData(BaseClass):
    """
    Contains information regarding the ground data of the borefield.
    """

    __slots__ = 'k_s', 'Tg', 'Rb', '_flux', 'volumetric_heat_capacity', 'alpha', 'determine_Tg'

    def __init__(self, k_s: float = None,
                 T_g: float = None,
                 R_b: float = None,
                 volumetric_heat_capacity: float = 2.4 * 10**6,
                 flux: float = 0.06,
                 phi: float = None,
                 d_t: float = None,
                 h_start: float = None):
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
        self._flux = flux  # W/m2
        self.temp_profile = TempProfileData(d_t, phi, h_start, self.k_s, self.volumetric_heat_capacity)
        self.determine_Tg: Callable[[float, np.ndarray], np.ndarray] = self._constant_Tg if np.isclose(flux, 0) else self._raising_Tg



    def get_flux(self) -> float:
        return self._flux

    def set_flux(self, flux: float):
        self._flux = flux
        self.determine_Tg = self._constant_Tg if np.isclose(flux, 0) else self._raising_Tg

    def del_flux(self):
        del self._flux

    flux = property(
        fget=get_flux,
        fset=set_flux,
        fdel=del_flux,
        doc="The radius property."
    )

    def calculate_Tg(self, H: float, time: np.ndarray) -> np.ndarray:
        """
        This function gives back the ground temperature
        When use_constant_Tg is False, the thermal heat flux is taken into account.

        Parameters
        ----------
        H : float
            Depth at which the temperature should be calculated [m]

        Returns
        -------
        Tg : np.ndarray
            Ground temperature [deg C]
        """
        return self.determine_Tg(H, time)

    def _constant_Tg(self, H: float, time: np.ndarray) -> np.ndarray:
        return self.Tg * np.ones_like(time)

    def _raising_Tg(self, H: float, time: np.ndarray) -> np.ndarray:
        # geothermal gradient is equal to the geothermal heat flux divided by the thermal conductivity
        # avg ground temperature is (Tg + gradient + Tg) / 2 = Tg + gradient / 2
        return (self.Tg + H * self.flux / self.k_s / 2) * np.ones_like(time)

    def _near_field_temperature(self, H: float, time: np.ndarray) -> np.ndarray:
        # T_new = self.Tg + self.dT * np.exp(-H/self.D) * np.sin(self.sigma * time + self.phi -H/self.D)
        time_long = np.insert(time, 0, 0)
        time_1 = time_long[:-1]
        time_2 = time_long[1:]
        T_new = self.Tg + self.temp_profile.d_t * self.temp_profile.d / 2 / (H - self.temp_profile.h_start) / (time_2 - time_1) / self.temp_profile.omega * (
                np.exp(-H / self.temp_profile.d) * (np.cos(H / self.temp_profile.d - self.temp_profile.omega * time_2 - self.temp_profile.phi) +
                                                    np.sin(H / self.temp_profile.d - self.temp_profile.omega * time_2 - self.temp_profile.phi))
                - np.exp(-self.temp_profile.h_start / self.temp_profile.d) * (
                        np.cos(self.temp_profile.h_start / self.temp_profile.d - self.temp_profile.omega * time_2 - self.temp_profile.phi) -
                        np.sin(self.temp_profile.h_start / self.temp_profile.d - self.temp_profile.omega * time_2 - self.temp_profile.phi)) - (
                        np.exp(-H / self.temp_profile.d) * (np.cos(H / self.temp_profile.d - self.temp_profile.omega * time_1 - self.temp_profile.phi) +
                                                            np.sin(H / self.temp_profile.d - self.temp_profile.omega * time_1 - self.temp_profile.phi))
                        - np.exp(-self.temp_profile.h_start / self.temp_profile.d) * (
                                np.cos(self.temp_profile.h_start / self.temp_profile.d - self.temp_profile.omega * time_1 - self.temp_profile.phi) -
                                np.sin(self.temp_profile.h_start / self.temp_profile.d - self.temp_profile.omega * time_1 - self.temp_profile.phi))))
        self.flux = self.k_s * self.temp_profile.d_t * self.temp_profile.d / (H - self.temp_profile.h_start) / (time_2 - time_1) / self.temp_profile.omega * (
                np.exp(-H / self.temp_profile.d) * np.cos(H / self.temp_profile.d - self.temp_profile.omega * time_2 - self.temp_profile.phi) -
                np.exp(-self.temp_profile.h_start / self.temp_profile.d) * (
                    np.cos(self.temp_profile.h_start / self.temp_profile.d - self.temp_profile.omega * time_2 - self.temp_profile.phi)) - (
                        np.exp(-H / self.temp_profile.d) * np.cos(H / self.temp_profile.d - self.temp_profile.omega * time_1 - self.temp_profile.phi) -
                        np.exp(-self.temp_profile.h_start / self.temp_profile.d) * (
                            np.cos(self.temp_profile.h_start / self.temp_profile.d - self.temp_profile.omega * time_1 - self.temp_profile.phi))))
        return T_new

    def __eq__(self, other):
        if not isinstance(other, GroundData):
            return False
        for i in self.__slots__:
            if getattr(self, i) != getattr(other, i):
                return False
        return True

if __name__ == "__main__":
    ground = GroundData(1.5,10,0.015,2.4*10**6,20)
    print(ground.determine_Tg)
    ground.flux = 0
    print(ground.determine_Tg)
