"""
This document contains the variable classes for the fluid data.
"""
import abc
import warnings

import numpy as np

from abc import ABC
from GHEtool.VariableClasses.BaseClass import BaseClass
from typing import Union


class _FluidData(ABC, BaseClass):
    """
    Contains information regarding the fluid data of the borefield.
    """

    def __init__(self, freezing_point: float):
        """

        Parameters
        ----------
        freezing_point : float
            Freezing point of the fluid °C
        """
        self._freezing_point = freezing_point

    @abc.abstractmethod
    def k_f(self, **kwargs) -> float:
        """
        This function returns the conductivity of the fluid in W/(mK).

        Returns
        -------
        float
            Fluid thermal conductivity [W/(mK)]
        """

    @abc.abstractmethod
    def rho(self, **kwargs) -> float:
        """
        This function returns the density of the fluid in kg/m^3.

        Returns
        -------
        float
            Density [kg/m^3]
        """

    @abc.abstractmethod
    def cp(self, **kwargs) -> float:
        """
        This function returns the heat capacity of the fluid in J/(kgK).

        Returns
        -------
        float
            Heat capacity of the fluid [J/(kgK)]
        """

    @abc.abstractmethod
    def mu(self, **kwargs) -> float:
        """
        This function returns the dynamic viscosity of the fluid in Pa.s.

        Returns
        -------
        float
            Dynamic viscosity [Pa.s]
        """

    @property
    def freezing_point(self) -> float:
        """
        This function returns the freezing point of the fluid in °C.

        Returns
        -------
        float
            Freezing point °C
        """
        return self._freezing_point

    def nu(self, **kwargs) -> float:
        """
        This function returns the kinematic viscosity of the fluid in m^2/s.

        Returns
        -------
        float
            Kinematic viscosity [m^2/s]
        """
        return self.mu(**kwargs) / self.rho(**kwargs)

    def Pr(self, **kwargs) -> float:
        """
        This function returns the Prandtl number which is defined as the ratio of momentum diffusivity
        to thermal diffusivity.

        Returns
        -------
        float
            Prandtl number
        """
        return self.cp(**kwargs) * self.mu(**kwargs) / self.k_f(**kwargs)

    def test_freezing(self, temperature: Union[float, int, np.ndarray]) -> bool:
        """
        This function returns false if all the temperatures are above the freezing point and true otherwise.
        If no freezing point is set, a ValueError is raised.

        Parameters
        ----------
        temperature : int, float, np.ndarray
            Fluid temperatures

        Returns
        -------
        bool
            False if all temperatures are above the freezing point, true otherwise.

        Raises
        ------
        ValueError
            When no freezing point was given
        """

        if self.freezing_point is None:
            raise ValueError('No freezing point was given.')

        if np.all(np.array(temperature) > self.freezing_point):
            return False
        return True
