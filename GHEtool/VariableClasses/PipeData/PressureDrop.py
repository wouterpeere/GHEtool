import copy

import numpy as np
import pygfunction as gt

from GHEtool.VariableClasses.PipeData._PipeData import _PipeData
from GHEtool.VariableClasses.FluidData._FluidData import _FluidData
from GHEtool.VariableClasses.FlowData.ConstantFlowRate import ConstantFlowRate
from GHEtool.VariableClasses.FlowData._FlowData import _FlowData
from math import pi


class PressureDrop:

    def __init__(self, pipe_data: _PipeData, fluid_data: _FluidData, flow_data: _FlowData, minor_losses_borehole: float,
                 borehole_length: float, r_in_lateral: float, distance_lateral: float, minor_losses_lateral: float,
                 r_in_main: float, distance_main: float, minor_losses_main: float,
                 nb_of_boreholes: int, series_factor: int, tichelmann_factor: int, **kwargs):
        """

        Parameters
        ----------
        pipe_data : Pipe data
            Pipe data class
        fluid_data : Fluid data
            Fluid data class
        flow_data : Flow data
            Flow data class
        minor_losses_borehole : float
            Minor losses in the borehole (e.g. connections to the horizontal pipe) [-]
        borehole_length : float
            Length of the borehole [m]
        r_in_lateral : float
            Inner radius of the lateral connection between the borehole and the manifold [m]
        distance_lateral : float
            Distance between the borehole to the manifold [m]
        minor_losses_lateral : float
            Minor losses in the lateral connection between the borehole and the manifold (e.g. the connection
             to the manifold) [-]
        r_in_main : float
            Inner radius of the main header between the manifold and the plant room [m]
        distance_main : float
            Distance between the manifold and the plant room [m]
        minor_losses_main : float
            Minor losses in the main header [-]
        nb_of_boreholes : int
            Number of boreholes in the borefield [-]
        series_factor : int
            Number of boreholes in series [-]
        tichelmann_factor : int
            Number of boreholes in Tichelmann [-]
        """
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
            self.flow_data.mfr(fluid_data=self.fluid_data, **kwargs) * self.tichelmann_factor,
            self.r_in_lateral,
            self.fluid_data.mu(**kwargs),
            self.fluid_data.rho(**kwargs),
            1e-6)
        A = pi * self.r_in_lateral ** 2
        V = (self.flow_data.vfr(fluid_data=self.fluid_data,
                                **kwargs) / 1000) / A * self.tichelmann_factor

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
            self.flow_data.mfr(fluid_data=self.fluid_data, **kwargs) * self.nb_of_boreholes / self.series_factor,
            self.r_in_main,
            self.fluid_data.mu(**kwargs),
            self.fluid_data.rho(**kwargs),
            1e-6)
        A = pi * self.r_in_main ** 2
        V = (self.flow_data.vfr(fluid_data=self.fluid_data,
                                **kwargs) / 1000) / A * self.nb_of_boreholes / self.series_factor

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
        pressure drop in the borehole, pressure drop in the lateral pipes, pressure drop in the main header, flow rates : np.ndarray, np.ndarray, np.ndarray, np.ndarray
            Array with the pressure drops in the borehole [kPa], Array with the pressure drops in the lateral pipe [kPa], Array with the pressure drops in the main header [kPa], Array with the flow rates per borehole [l/s]
        """
        # backup
        flow_backup = copy.copy(self.flow_data)

        flow_rates = np.linspace(0, range * self.flow_data.vfr(fluid_data=self.fluid_data, **kwargs), datapoints)
        pressure_drops_pipe = np.zeros(flow_rates.shape)
        pressure_drops_lateral = np.zeros(flow_rates.shape)
        pressure_drops_main = np.zeros(flow_rates.shape)

        for i, val in enumerate(flow_rates):
            self.flow_data = ConstantFlowRate(vfr=val)
            pressure_drops_pipe[i] = self.calculate_pressure_drop_borehole(**kwargs)
            pressure_drops_lateral[i] = self.calculate_pressure_drop_lateral(**kwargs)
            pressure_drops_main[i] = self.calculate_pressure_drop_main(**kwargs)

        # reset backup
        self.flow_data = flow_backup
        return np.nan_to_num(pressure_drops_pipe), np.nan_to_num(pressure_drops_lateral), \
            np.nan_to_num(pressure_drops_main), flow_rates
