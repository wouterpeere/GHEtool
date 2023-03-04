"""
This document contains all the information of the borehole class.
"""

from GHEtool.VariableClasses.BaseClass import BaseClass
from GHEtool.VariableClasses.VariableClasses import FluidData, PipeData
from math import pi

import matplotlib.pyplot as plt
import pygfunction as gt


class Borehole(BaseClass):

    """
    The borehole class contains all the functionalities related to the calculation of the equivalent
    borehole thermal resistance and contains a fluid and pipe class object.
    """

    __slots__ = '_fluid_data', '_pipe_data', '_Rb'

    def __init__(self):
        self._fluid_data = FluidData()
        self._pipe_data = PipeData()
        self._Rb = 0.12

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

        Parameters
        ----------
        fluid_data : FluidData

        Returns
        -------
        None
        """
        self._fluid_data = fluid_data
        if self.pipe_data.check_values():
            self.calculate_fluid_thermal_resistance()

    @fluid_data.deleter
    def fluid_data(self) -> None:
        """
        This function resets the fluid data object.

        Returns
        -------
        None
        """
        self._fluid_data = FluidData()

    @property
    def pipe_data(self) -> PipeData:
        """
        This function returns the pipe data object.

        Returns
        -------
        PipeData
        """
        return self._pipe_data

    @pipe_data.setter
    def pipe_data(self, pipe_data: PipeData) -> None:
        """
        This function sets the pipe data.

        Parameters
        ----------
        pipe_data : PipeData

        Returns
        -------
        None
        """
        self._pipe_data = pipe_data
        self.pipe_data.calculate_pipe_thermal_resistance()
        if self.fluid_data.check_values():
            self.calculate_fluid_thermal_resistance()

    @pipe_data.deleter
    def pipe_data(self) -> None:
        """
        This function resets the fluid data object.

        Returns
        -------
        None
        """
        self._pipe_data = PipeData()

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
        pipe = gt.pipes.MultipleUTube(self.pipe_data.pos, self.pipe_data.r_in, self.pipe_data.r_out,
                                      borehole, k_s, self.pipe_data.k_g,
                                      self.pipe_data.R_p + self.fluid_data.R_f, self.pipe_data.number_of_pipes, J=2)

        return pipe.effective_borehole_thermal_resistance(self.fluid_data.mfr, self.fluid_data.Cp)

    def calculate_fluid_thermal_resistance(self) -> None:
        """
        This function calculates and sets the fluid thermal resistance R_f.

        Returns
        -------
        None
        """
        self.fluid_data.h_f: float =\
            gt.pipes.convective_heat_transfer_coefficient_circular_pipe(self.fluid_data.mfr /
                                                                        self.pipe_data.number_of_pipes,
                                                                        self.pipe_data.r_in,
                                                                        self.fluid_data.mu,
                                                                        self.fluid_data.rho,
                                                                        self.fluid_data.k_f,
                                                                        self.fluid_data.Cp,
                                                                        self.pipe_data.epsilon)
        self.fluid_data.R_f: float = 1. / (self.fluid_data.h_f * 2 * pi * self.pipe_data.r_in)

    def __eq__(self, other):
        if not isinstance(other, Borehole):
            return False
        for i in self.__slots__:
            if getattr(self, i) != getattr(other, i):
                return False
        return True