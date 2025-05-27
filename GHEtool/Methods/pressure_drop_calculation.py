import copy

import numpy as np
import pygfunction as gt

from GHEtool import *
from GHEtool.VariableClasses.PipeData import _PipeData
from GHEtool.VariableClasses.FluidData import _FluidData
from GHEtool.VariableClasses.FlowData import _FlowData
from math import pi


class PressureDrop:

    def __init__(self, pipe_data: _PipeData, fluid_data: _FluidData, flow_data: _FlowData, minor_losses_borehole: float,
                 borehole_length: float, r_in_lateral: float, distance_lateral: float, minor_losses_lateral: float,
                 r_in_main: float, distance_main: float, minor_losses_main: float,
                 nb_of_boreholes: int, series_factor: int, tichelmann_factor: int):
        self.pipe_data = pipe_data
        self.fluid_data = fluid_data
        self.flow_data = flow_data
        self.borehole_length = borehole_length
        self.minor_losses_borehole = minor_losses_borehole
        self.r_in_lateral = r_in_lateral
        self.distance_lateral = distance_lateral
        self.minor_losses_lateral = minor_losses_lateral
        self.r_in_main = r_in_main
        self.distance_main = distance_main
        self.minor_losses_main = minor_losses_main
        self.nb_of_boreholes = nb_of_boreholes
        self.series_factor = series_factor
        self.tichelmann_factor = tichelmann_factor

    def calculate_pressure_drop_borehole(self, **kwargs) -> float:
        """
        This function calculates the pressure drop inside the borehole.

        Returns
        -------
        Pressure drop in kPa
        """
        return self.pipe_data.pressure_drop(self.fluid_data, self.flow_data, self.borehole_length, **kwargs)

    def calculate_pressure_drop_lateral(self, **kwargs) -> float:
        """
        This function calculates the pressure drop in the lateral pipes, i.e. the pipes between the borehole and
        the manifold.

        Returns
        -------
        Pressure drop in kPa
        """

        # Darcy fluid factor
        fd = gt.pipes.fluid_friction_factor_circular_pipe(
            self.flow_data.mfr(fluid_data=self.fluid_data, **kwargs) * self.series_factor * self.tichelmann_factor,
            self.r_in_lateral,
            self.fluid_data.mu(**kwargs),
            self.fluid_data.rho(**kwargs),
            1e-6)
        A = pi * self.r_in_lateral ** 2
        V = (self.flow_data.vfr(fluid_data=self.fluid_data,
                                **kwargs) / 1000) / A * self.series_factor * self.tichelmann_factor

        # distance_later * 2 for back and forth
        return ((fd * self.distance_lateral * 2 / (
                2 * self.r_in_lateral) + self.minor_losses_lateral) * self.fluid_data.rho(
            **kwargs) * V ** 2 / 2) / 1000

    def calculate_pressure_drop_main(self, **kwargs) -> float:
        """
        This function calculates the pressure drop in the main header, i.e. between the manifold and the plant room.

        Returns
        -------
        Pressure drop in kPa
        """
        # Darcy fluid factor
        fd = gt.pipes.fluid_friction_factor_circular_pipe(
            self.flow_data.mfr(fluid_data=self.fluid_data, **kwargs) * self.nb_of_boreholes,
            self.r_in_main,
            self.fluid_data.mu(**kwargs),
            self.fluid_data.rho(**kwargs),
            1e-6)
        A = pi * self.r_in_main ** 2
        V = (self.flow_data.vfr(fluid_data=self.fluid_data, **kwargs) / 1000) / A * self.nb_of_boreholes

        # distance_later * 2 for back and forth
        return ((fd * self.distance_main * 2 / (
                2 * self.r_in_main) + self.minor_losses_main) * self.fluid_data.rho(
            **kwargs) * V ** 2 / 2) / 1000

    def calculate_total_pressure_drop(self, **kwargs) -> float:
        """
        This function calculates the total pressure drop of the borefield.

        Returns
        -------
        Pressure drop in kPa
        """
        return self.calculate_pressure_drop_borehole(**kwargs) + \
            self.calculate_pressure_drop_lateral(**kwargs) + \
            self.calculate_pressure_drop_main(**kwargs)

    def create_pressure_drop_curve(self, range: float = 2, datapoints: int = 30, **kwargs):
        """
        This function calculates the total pressure drop for different flow rates.

        Parameters
        ----------
        range : float
            Multiplier of the flow rate for the range of the data.
        datapoints : int
            Number of datapoints.

        Returns
        -------
        pressure drop, flow rates : np.ndarray, np.ndarray
            Array with the pressure drops [kPa], Array with the flow rates per borehole [l/s]
        """
        flow_rates = np.linspace(0, range * self.flow_data.vfr(fluid_data=self.fluid_data, **kwargs), datapoints)
        pressure_drops = np.zeros(flow_rates.shape)

        for i, val in enumerate(flow_rates):
            self.flow_data = ConstantFlowRate(vfr=val)
            pressure_drops[i] = self.calculate_total_pressure_drop(**kwargs)

        return np.nan_to_num(pressure_drops), flow_rates


def calculate_pressure_drop_horizontal(fluid_data: _FluidData, flow_data: _FlowData, r_in: float,
                                       length: float, minor_losses: float, **kwargs) -> float:
    """
    This function calculates the pressure drop in the horizontal pipe.

    Parameters
    ----------
    fluid_data : FluidData
        Fluid data
    flow_data : FlowData
        Flow rate data
    r_in : float
        Inner pipe diameter [m]
    length : float
        Length of the pipe [m]
    minor_losses : float
        Coefficient for minor losses [-]

    Returns
    -------
    Pressure drop : float
        Pressure drop [kPa]
    """
    # Darcy fluid factor
    fd = gt.pipes.fluid_friction_factor_circular_pipe(
        flow_data.mfr(fluid_data=fluid_data, **kwargs),
        r_in,
        fluid_data.mu(**kwargs),
        fluid_data.rho(**kwargs),
        1e-6)
    A = pi * r_in ** 2
    V = (flow_data.vfr(fluid_data=fluid_data, **kwargs) / 1000) / A

    return ((fd * length / (2 * r_in) + minor_losses) * fluid_data.rho(**kwargs) * V ** 2 / 2) / 1000


def calculate_total_pressure_drop(pipe_data: _PipeData, fluid_data: _FluidData, flow_data: _FlowData,
                                  borehole_length: float,
                                  r_in: float, distance: float, minor_losses: float, **kwargs) -> float:
    """
    This function calculates the total pressure drop of your system, assuming every borehole is brought individually
    to the main collector.

    Parameters
    ----------
    pipe_data : PipeData
        Pipe data
    fluid_data : FluidData
        Fluid data
    flow_data : FlowData
        Flow rate data
    borehole_length : float
        Borehole length [m]
    r_in : float
        Inner pipe diameter [m]
    distance : float
        distance from the borehole to the collector [m]
    minor_losses : float
        Coefficient for minor losses [-]

    Returns
    -------
    Pressure drop : float
        Pressure drop [kPa]
    """

    return pipe_data.pressure_drop(fluid_data, flow_data, borehole_length, **kwargs) + \
        calculate_pressure_drop_horizontal(fluid_data, flow_data, r_in, distance * 2, minor_losses, **kwargs)


def create_pressure_drop_curve(pipe_data: _PipeData, fluid_data: _FluidData, flow_data: _FlowData,
                               borehole_length: float,
                               r_in: float, distance: float, minor_losses: float, range: float = 2,
                               datapoints: int = 30, **kwargs) -> tuple:
    """
    This function calculates the pressure drop for different flow rates.

    Parameters
    ----------
    pipe_data : PipeData
        Pipe data
    fluid_data : FluidData
        Fluid data
    flow_data : FlowData
        Flow rate data
    borehole_length : float
        Borehole length [m]
    r_in : float
        Inner pipe diameter [m]
    distance : float
        distance from the borehole to the collector [m]
    minor_losses : float
        Coefficient for minor losses [-]
    range : float
        Multiplier of the flow rate for the range of the data.
    datapoints : int
        Number of datapoints.

    Returns
    -------
    pressure drop, flow rates : np.ndarray, np.ndarray
        Array with the pressure drops [kPa], Array with the flow rates per borehole [l/s]
    """

    flow_rates = np.linspace(0, range * flow_data.vfr(fluid_data=fluid_data, **kwargs), datapoints)
    pressure_drops = np.zeros(flow_rates.shape)

    for i, val in enumerate(flow_rates):
        new_flow_data = ConstantFlowRate(vfr=val)
        pressure_drops[i] = calculate_total_pressure_drop(pipe_data, fluid_data, new_flow_data, borehole_length,
                                                          r_in, distance,
                                                          minor_losses, **kwargs)

    return np.nan_to_num(pressure_drops), flow_rates
