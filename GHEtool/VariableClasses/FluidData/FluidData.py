"""
This document contains the variable classes for the fluid data.
"""
from __future__ import annotations

import pygfunction as gt
import warnings

from GHEtool.VariableClasses.BaseClass import BaseClass
from GHEtool.VariableClasses.FluidData import ConstantFluidData
from GHEtool.VariableClasses.FlowData import ConstantFlowRate


class FluidData(BaseClass):
    """
    Contains information regarding the fluid data of the borefield.
    """

    def __init__(self, mfr: float = None,
                 k_f: float = None,
                 rho: float = None,
                 Cp: float = None,
                 mu: float = None,
                 vfr: float = None):
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
        vfr : float
            Volume flow rate per borehole [l/s]
        """
        warnings.warn('This class will be depreciated in version 2.4.0. Please use the ConstantFluidData and '
                      'ConstantFlowRate class.', DeprecationWarning)

        self.flow_rate = ConstantFlowRate(mfr=mfr, vfr=vfr)
        self.fluid_data = ConstantFluidData(k_f, rho, Cp, mu)

    @property
    def vfr(self) -> float:
        """
        This function returns the volume flow rate.

        Returns
        -------
        float
            volume flow rate [l/s]
        """
        return self.flow_rate.vfr(self.fluid_data)

    @vfr.setter
    def vfr(self, vfr: float) -> None:
        """
        This function sets the volume flow rate.
        The mass flow rate will be set to 0

        Parameters
        ----------
        vfr : float
            Volume flow rate [l/s]

        Returns
        -------
        None
        """
        self.flow_rate._vfr = vfr
        self.flow_rate._mfr = None

    @property
    def k_f(self) -> float:
        return self.fluid_data.k_f()

    @property
    def rho(self) -> float:
        return self.fluid_data.rho()

    @property
    def Cp(self) -> float:
        return self.fluid_data.cp()

    @property
    def mu(self) -> float:
        return self.fluid_data.mu()

    @property
    def mfr(self) -> float:
        """
        This function returns the mass flow rate. Either based on a given mass flow rate,
        or calculated based on a volume flow rate.

        Returns
        -------
        float
            mass flow rate [kg/s]
        """
        return self.flow_rate.mfr(self.fluid_data)

    @mfr.setter
    def mfr(self, mfr: float) -> None:
        """
        This function sets the mass flow rate.
        The vfr will hence be set to 0.

        Parameters
        ----------
        mfr : float
            Mass flow rate [kg/s]

        Returns
        -------
        None
        """
        self.flow_rate._mfr = mfr
        self.flow_rate._vfr = None

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
        self.flow_rate._mfr = mfr

    def import_fluid_from_pygfunction(self, fluid_object: gt.media.Fluid) -> None:
        """
        This function loads a fluid object from pygfunction and imports it into GHEtool.
        Note that this object does not contain the mass flow rate!

        Parameters
        ----------
        fluid_object : Fluid object from pygfunction

        Returns
        -------
        None
        """
        self.fluid_data = ConstantFluidData(fluid_object.k, fluid_object.rho, fluid_object.cp, fluid_object.mu)

    @property
    def Pr(self) -> float:
        """
        This function returns the Prandtl number which is defined as the ratio of momentum diffusivity
        to thermal diffusivity.

        Returns
        -------
        float
            Prandtl number
        """
        return self.fluid_data.Pr()

    def check_values(self) -> bool:
        return self.fluid_data.check_values()

    def __eq__(self, other):
        if not isinstance(other, FluidData):
            return False
        if self.fluid_data == other.fluid_data and self.flow_rate == other.flow_rate:
            return True
        return False

    def __repr__(self):
        temp = f'Fluid parameters\n\tThermal conductivity of the fluid [W/(m·K)]: {self.fluid_data.k_f():.3f}\n\t' \
               f'Density of the fluid [kg/m³]: {self.fluid_data.rho():.3f}\n\t' \
               f'Thermal capacity of the fluid [J/(kg·K)]: {self.fluid_data.cp():.3f}\n\t' \
               f'Dynamic viscosity [Pa·s]: {self.fluid_data.mu():.3f}\n\t'
        if self.flow_rate._vfr is not None:
            temp += f'Volume flow rate [l/s]: {self.flow_rate.vfr()}'
        else:
            temp += f'Mass flow rate [kg/s] : {self.flow_rate.mfr()}'
        return temp
