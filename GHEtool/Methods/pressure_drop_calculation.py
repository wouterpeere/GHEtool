import copy

import numpy as np
import pygfunction as gt

from GHEtool import *
from GHEtool.VariableClasses.PipeData import _PipeData
from GHEtool.VariableClasses.FluidData import _FluidData
from GHEtool.VariableClasses.FlowRateData import _FlowRateData
from math import pi


def calculate_pressure_drop_horizontal(fluid_data: _FluidData, flow_rate_data: _FlowRateData, r_in: float,
                                       length: float, minor_losses: float, **kwargs) -> float:
    """
    This function calculates the pressure drop in the horizontal pipe.

    Parameters
    ----------
    fluid_data : FluidData
        Fluid data
    flow_rate_data : FlowRateData
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
        flow_rate_data.mfr(fluid_data=fluid_data, **kwargs),
        r_in,
        fluid_data.mu(**kwargs),
        fluid_data.rho(**kwargs),
        1e-6)
    A = pi * r_in ** 2
    V = (flow_rate_data.vfr(fluid_data=fluid_data, **kwargs) / 1000) / A

    return ((fd * length / (2 * r_in) + minor_losses) * fluid_data.rho(**kwargs) * V ** 2 / 2) / 1000


def calculate_total_pressure_drop(pipe_data: _PipeData, fluid_data: _FluidData, flow_rate_data: _FlowRateData,
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
    flow_rate_data : FlowRateData
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

    return pipe_data.pressure_drop(fluid_data, flow_rate_data, borehole_length, **kwargs) + \
        calculate_pressure_drop_horizontal(fluid_data, flow_rate_data, r_in, distance * 2, minor_losses, **kwargs)


def create_pressure_drop_curve(pipe_data: _PipeData, fluid_data: _FluidData, flow_rate_data: _FlowRateData,
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
    flow_rate_data : FlowRateData
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

    flow_rates = np.linspace(0, range * flow_rate_data.vfr(fluid_data=fluid_data, **kwargs), datapoints)
    pressure_drops = np.zeros(flow_rates.shape)

    for i, val in enumerate(flow_rates):
        new_flow_rate_data = ConstantFlowRate(vfr=val)
        pressure_drops[i] = calculate_total_pressure_drop(pipe_data, fluid_data, new_flow_rate_data, borehole_length,
                                                          r_in, distance,
                                                          minor_losses, **kwargs)

    return np.nan_to_num(pressure_drops), flow_rates
