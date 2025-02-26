import copy

import numpy as np
import pygfunction as gt

from GHEtool import *
from GHEtool.VariableClasses.PipeData import _PipeData
from math import pi


def calculate_pressure_drop_horizontal(fluid_data: FluidData, r_in: float, length: float, minor_losses: float) -> float:
    """
    This function calculates the pressure drop in the horizontal pipe.

    Parameters
    ----------
    fluid_data : FluidData
        Fluid data
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
        fluid_data.mfr,
        r_in,
        fluid_data.mu,
        fluid_data.rho,
        1e-6)
    A = pi * r_in ** 2
    V = (fluid_data.vfr / 1000) / A

    return ((fd * length / (2 * r_in) + minor_losses) * fluid_data.rho * V ** 2 / 2) / 1000


def calculate_total_pressure_drop(pipe_data: _PipeData, fluid_data: FluidData, borehole_length: float,
                                  r_in: float, distance: float, minor_losses: float) -> float:
    """
    This function calculates the total pressure drop of your system, assuming every borehole is brought individually
    to the main collector.

    Parameters
    ----------
    pipe_data : PipeData
        Pipe data
    fluid_data : FluidData
        Fluid data
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

    return pipe_data.pressure_drop(fluid_data, borehole_length) + \
        calculate_pressure_drop_horizontal(fluid_data, r_in, distance * 2, minor_losses)


def create_pressure_drop_curve(pipe_data: _PipeData, fluid_data: FluidData, borehole_length: float,
                               r_in: float, distance: float, minor_losses: float, range: float = 2,
                               datapoints: int = 30) -> tuple:
    """
    This function calculates the pressure drop for different flow rates.

    Parameters
    ----------
    pipe_data : PipeData
        Pipe data
    fluid_data : FluidData
        Fluid data
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

    flow_rates = np.linspace(0, range * fluid_data.vfr, datapoints)
    pressure_drops = np.zeros(flow_rates.shape)

    new_fluid = copy.copy(fluid_data)

    for i, val in enumerate(flow_rates):
        new_fluid.vfr = val
        pressure_drops[i] = calculate_total_pressure_drop(pipe_data, new_fluid, borehole_length, r_in, distance,
                                                          minor_losses)

    return np.nan_to_num(pressure_drops), flow_rates
