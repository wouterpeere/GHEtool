"""
This document contains all the information of the borehole class.
"""

from GHEtool.VariableClasses.BaseClass import BaseClass
from GHEtool.VariableClasses.FluidData import FluidData
from GHEtool.VariableClasses.PipeData import _PipeData, MultipleUTube
from math import pi

import matplotlib.pyplot as plt
import pygfunction as gt


class Borehole(BaseClass):

    """
    The borehole class contains all the functionalities related to the calculation of the equivalent
    borehole thermal resistance and contains a fluid and pipe class object.
    """

    __slots__ = '_fluid_data', '_pipe_data', '_Rb', 'use_constant_Rb', 'borehole_internal_model'

    def __init__(self, fluid_data: FluidData = None, pipe_data: _PipeData = None):
        """

        Parameters
        ----------
        fluid_data : FluidData
            Fluid data
        pipe_data : PipeData
            Pipe data
        """
        self._fluid_data = FluidData()
        self._pipe_data = MultipleUTube()
        self._Rb: float = 0.12
        self.use_constant_Rb: bool = True
        self.borehole_internal_model: gt.pipes._BasePipe = None
        if not fluid_data is None:
            self.fluid_data = fluid_data
        if not pipe_data is None:
            self.pipe_data = pipe_data

    @property
    def Rb(self) -> float:
        """
        This returns the constant, equivalent borehole thermal resistance [mK/W].

        Returns
        -------
        Rb* : float
            Equivalent borehole thermal resistance [mK/W]
        """
        return self._Rb

    @Rb.setter
    def Rb(self, Rb: float) -> None:
        """
        This function sets the constant equivalent borehole thermal resistance [mK/W].
        Futhermore it sets the use_constant_Rb to True.

        Parameters
        ----------
        Rb : float
            Equivalent borehole thermal resistance [mK/W]

        Returns
        -------
        None
        """
        self._Rb = Rb
        self.use_constant_Rb = True

    @property
    def Re(self) -> float:
        """
        Reynolds number.

        Returns
        -------
        Reynolds number : float
        """
        return self.pipe_data.Re(self.fluid_data)

    @property
    def fluid_data(self) -> FluidData:
        """
        This function returns the fluid data object.

        Returns
        -------
        FluidData
        """
        return self._fluid_data

    @fluid_data.setter
    def fluid_data(self, fluid_data: FluidData) -> None:
        """
        This function sets the fluid data.
        Futhermore it sets the use_constant_Rb to False (if the pipe data is available) so the next time the Rb*
        is calculated dynamically. If this is not wanted, set the use_constant_Rb attribute back to True.

        Parameters
        ----------
        fluid_data : FluidData
            Fluid data

        Returns
        -------
        None
        """
        self._fluid_data = fluid_data
        if self.pipe_data.check_values():
            self.pipe_data.calculate_resistances(self.fluid_data)
            self.use_constant_Rb = False

    @fluid_data.deleter
    def fluid_data(self) -> None:
        """
        This function resets the fluid data object and sets the use_constant_Rb to True.

        Returns
        -------
        None
        """
        self._fluid_data = FluidData()
        self.use_constant_Rb = True

    @property
    def pipe_data(self) -> _PipeData:
        """
        This function returns the pipe data object.

        Returns
        -------
        PipeData
        """
        return self._pipe_data

    @pipe_data.setter
    def pipe_data(self, pipe_data: _PipeData) -> None:
        """
        This function sets the pipe data.
        Futhermore it sets the use_constant_Rb to False (if the pipe data is available) so the next time the Rb*
        is calculated dynamically. If this is not wanted, set the use_constant_Rb attribute back to True.

        Parameters
        ----------
        pipe_data : PipeData
            Pipe data

        Returns
        -------
        None
        """
        self._pipe_data = pipe_data
        if self.fluid_data.check_values():
            self.pipe_data.calculate_resistances(self.fluid_data)
            self.use_constant_Rb = False

    @pipe_data.deleter
    def pipe_data(self) -> None:
        """
        This function resets the pipe data object and sets the use_constant_Rb to True.

        Returns
        -------
        None
        """
        self._pipe_data = MultipleUTube()
        self.use_constant_Rb = True

    def calculate_Rb(self, H: float, D: float, r_b: float, k_s: float) -> float:
        """
        This function calculates the equivalent borehole thermal resistance.

        Parameters
        ----------
        H : float
            Borehole depth [m]
        D : float
            Borehole burial depth [m]
        r_b : float
            Borehole radius [m]
        k_s : float
            Ground thermal conductivity [mk/W]

        Returns
        -------
        Rb : float
            Equivalent borehole thermal resistance

        Raises
        ------
        ValueError
            ValueError when the pipe and/or fluid data is not set correctly.
        """
        # check if all data is available
        if not self.pipe_data.check_values() or not self.fluid_data.check_values():
            print("Please make sure you set al the pipe and fluid data.")
            raise ValueError

        # initiate temporary borefield
        borehole = gt.boreholes.Borehole(H, D, r_b, 0, 0)
        # initiate pipe
        pipe = self.pipe_data.pipe_model(self.fluid_data, k_s, borehole)

        return pipe.effective_borehole_thermal_resistance(self.fluid_data.mfr, self.fluid_data.Cp)

    def get_Rb(self, H: float, D: float, r_b: float, k_s: float) -> float:
        """
        This function returns the equivalent borehole thermal resistance.
        If use_constant_Rb is True, self._Rb is returned, otherwise the resistance is calculated.

        Parameters
        ----------
        H : float
            Borehole depth [m]
        D : float
            Borehole burial depth [m]
        r_b : float
            Borehole radius [m]
        k_s : float
            Ground thermal conductivity [mk/W]

        Returns
        -------
        Rb* : float
            Equivalent borehole thermal resistance [mK/W]
        """
        if self.use_constant_Rb:
            return self.Rb

        return self.calculate_Rb(H, D, r_b, k_s)

    def __eq__(self, other):
        if not isinstance(other, Borehole):
            return False
        for i in self.__slots__:
            if getattr(self, i) != getattr(other, i):
                return False
        return True
