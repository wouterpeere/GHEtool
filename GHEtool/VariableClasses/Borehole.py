"""
This document contains all the information of the borehole class.
"""

from GHEtool.VariableClasses.BaseClass import BaseClass
from GHEtool.VariableClasses.FluidData import _FluidData, FluidData
from GHEtool.VariableClasses.FlowRateData import _FlowRateData
from GHEtool.VariableClasses.PipeData import _PipeData, MultipleUTube
from typing import Union

import matplotlib.pyplot as plt
import pygfunction as gt


class Borehole(BaseClass):
    """
    The borehole class contains all the functionalities related to the calculation of the equivalent
    borehole thermal resistance and contains a fluid and pipe class object.
    """

    __slots__ = '_fluid_data', '_pipe_data', '_Rb', 'use_constant_Rb', '_flow_data'

    def __init__(self, fluid_data: _FluidData = None,
                 pipe_data: _PipeData = None,
                 flow_data: _FlowRateData = None):
        """

        Parameters
        ----------
        fluid_data : FluidData
            Fluid data
        pipe_data : PipeData
            Pipe data
        flow_data : FlowRateData
            Flow rate data
        """
        self._Rb: float = 0.12
        self.use_constant_Rb: bool = True

        self._fluid_data = fluid_data
        self._pipe_data = pipe_data
        self._flow_data = flow_data

        if isinstance(fluid_data, FluidData):
            self._fluid_data = fluid_data.fluid_data
            self._flow_data = fluid_data.flow_rate

        if self.data_available:
            self.use_constant_Rb: bool = False

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
        Furthermore, it sets the use_constant_Rb to True.

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
    def Re(self, **kwargs) -> float:
        """
        Reynolds number.

        Returns
        -------
        float
            Reynolds number
        """
        return self.pipe_data.Re(self.fluid_data, self.flow_rate_data, **kwargs)

    @property
    def data_available(self) -> bool:
        """
        Checks if all the data is available for the Rb calculation.

        Returns
        -------
        bool
            True if all the data is available
        """
        if self._flow_data is None or self._fluid_data is None or self._pipe_data is None:
            return False
        if self.fluid_data.check_values() and self.pipe_data.check_values() and self._flow_data.check_values():
            return True
        return False

    @property
    def fluid_data(self) -> _FluidData:
        """
        This function returns the fluid data object.

        Returns
        -------
        FluidData
        """
        return self._fluid_data

    @fluid_data.setter
    def fluid_data(self, fluid_data: _FluidData) -> None:
        """
        This function sets the fluid data.
        Furthermore, it sets the use_constant_Rb to False (if the pipe data is available) so the next time the Rb*
        is calculated dynamically. If this is not wanted, set the use_constant_Rb attribute back to True.

        Parameters
        ----------
        fluid_data : FluidData
            Fluid data

        Returns
        -------
        None
        """
        if isinstance(fluid_data, FluidData):
            self._fluid_data = fluid_data.fluid_data
            self._flow_data = fluid_data.flow_rate
        else:
            self._fluid_data = fluid_data
        if self.data_available:
            self.use_constant_Rb = False

    @fluid_data.deleter
    def fluid_data(self) -> None:
        """
        This function resets the fluid data object and sets the use_constant_Rb to True.

        Returns
        -------
        None
        """
        self._fluid_data = None
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
        Furthermore, it sets the use_constant_Rb to False (if the pipe data is available) so the next time the Rb*
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
        if self.data_available:
            self.use_constant_Rb = False

    @pipe_data.deleter
    def pipe_data(self) -> None:
        """
        This function resets the pipe data object and sets the use_constant_Rb to True.

        Returns
        -------
        None
        """
        self._pipe_data = None
        self.use_constant_Rb = True

    @property
    def flow_rate_data(self) -> _FlowRateData:
        """
        This function returns the flow rate data object.

        Returns
        -------
        FlowRateData
        """
        return self._flow_data

    @flow_rate_data.setter
    def flow_rate_data(self, flow_rate_data: _FlowRateData) -> None:
        """
        This function sets the flow rate data.
        Furthermore, it sets the use_constant_Rb to False (if the pipe data is available) so the next time the Rb*
        is calculated dynamically. If this is not wanted, set the use_constant_Rb attribute back to True.

        Parameters
        ----------
        flow_rate_data : FlowRateData
            Flow rate Data

        Returns
        -------
        None
        """
        self._flow_data = flow_rate_data
        if self.data_available:
            self.use_constant_Rb = False

    @flow_rate_data.deleter
    def flow_rate_data(self) -> None:
        """
        This function resets the flow rate data object and sets the use_constant_Rb to True.

        Returns
        -------
        None
        """
        self._flow_data = None
        self.use_constant_Rb = True

    def calculate_Rb(self, H: float, D: float, r_b: float, k_s: Union[float, callable], depth: float = None,
                     **kwargs) -> float:
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
        k_s : float or callable
            (Function to calculate the) ground thermal conductivity [mk/W]
        depth : float
            Borehole depth [m] (only needed if k_s is a function, not a number)

        Returns
        -------
        Rb : float
            Equivalent borehole thermal resistance

        Raises
        ------
        ValueError
            ValueError when the pipe and/or fluid data is not set correctly.
        """
        if depth is None:
            # assume all vertical boreholes
            depth = D + H

        # check if all data is available
        if not self.data_available:
            print("Please make sure you set al the pipe and fluid data.")
            raise ValueError

        # initiate temporary borefield
        borehole = gt.boreholes.Borehole(H, D, r_b, 0, 0)
        self.pipe_data.calculate_resistances(self.fluid_data, self.flow_rate_data, **kwargs)

        # initiate pipe
        pipe = self.pipe_data.pipe_model(k_s if isinstance(k_s, (float, int)) else k_s(depth, D), borehole)

        return pipe.effective_borehole_thermal_resistance(self.flow_rate_data.mfr(**kwargs),
                                                          self.fluid_data.cp(**kwargs))

    def get_Rb(self, H: float, D: float, r_b: float, k_s: Union[callable, float], depth: float = None) -> float:
        """
        This function returns the equivalent borehole thermal resistance.
        If use_constant_Rb is True, self._Rb is returned, otherwise the resistance is calculated.

        Parameters
        ----------
        H : float
            Borehole length [m]
        D : float
            Borehole burial depth [m]
        r_b : float
            Borehole radius [m]
        k_s : float or callable
            (Function to calculate) ground thermal conductivity in function of the borehole depth [mk/W]
        depth : float
            Borehole depth [m] (only needed if k_s is a function, not a number)

        Returns
        -------
        Rb* : float
            Equivalent borehole thermal resistance [mK/W]
        """
        if depth is None:
            # assume all vertical boreholes
            depth = D + H

        if self.use_constant_Rb:
            return self.Rb

        return self.calculate_Rb(H, D, r_b, k_s if isinstance(k_s, (int, float)) else k_s(depth, D))

    def __eq__(self, other):
        if not isinstance(other, Borehole):
            return False
        for i in self.__slots__:
            if getattr(self, i) != getattr(other, i):
                return False
        return True

    def __repr__(self):
        if self.use_constant_Rb:
            return {'Rb': self.Rb}
        return {'fluid': self.fluid_data.__repr__(),
                'pipe': self.pipe_data.__repr__(),
                'flow': self.flow_rate_data.__repr__()}
