import copy
import math

import numpy as np
import pygfunction as gt
import matplotlib.pyplot as plt

from math import pi
from GHEtool.VariableClasses.PipeData._PipeData import _PipeData
from GHEtool.VariableClasses.FluidData import _FluidData
from GHEtool.VariableClasses.FlowData import _FlowData


class MultipleUTube(_PipeData):
    """
    Contains information regarding the Multiple U-Tube class.
    """

    __slots__ = _PipeData.__slots__ + ('r_in', 'r_out', 'D_s', 'number_of_pipes', 'pos', 'R_p', 'R_f')

    def __init__(self, k_g: float = None,
                 r_in: float = None,
                 r_out: float = None,
                 k_p: float = None,
                 D_s: float = None,
                 number_of_pipes: int = 1,
                 epsilon: float = 1e-6):
        """

        Parameters
        ----------
        k_g : float
            Grout thermal conductivity [W/mK]
        r_in : float
            Inner pipe radius [m]
        r_out : float
            Outer pipe radius [m]
        k_p : float
            Pipe thermal conductivity [W/mK]
        D_s : float
            Distance of the pipe until center [m]
        number_of_pipes : int
            Number of pipes [#] (single U-tube: 1, double U-tube:2)
        epsilon : float
            Pipe roughness [m]
        """

        super().__init__(k_g, k_p, epsilon)

        self.r_in = r_in  # inner pipe radius m
        self.r_out = r_out  # outer pipe radius m
        self.D_s = D_s  # distance of pipe until center m
        self.number_of_pipes = number_of_pipes  # number of pipes #
        self.pos = []
        self.R_p = 0  # pipe thermal resistance mK/W
        self.R_f = 0  # film (i.e. fluid) thermal resistance mK/W
        if self.check_values():
            self.pos = self._axis_symmetrical_pipe  # position of the pipes

    @property
    def _axis_symmetrical_pipe(self) -> list:
        """
        This function gives back the coordinates of the pipes in an axis-symmetrical pipe.

        Returns
        -------
        Positions : list
            List of coordinates tuples of the pipes in the borehole
        """
        dt: float = pi / float(self.number_of_pipes)
        pos: list = [(0., 0.)] * 2 * self.number_of_pipes
        for i in range(self.number_of_pipes):
            pos[i] = (self.D_s * np.cos(2.0 * i * dt + pi), self.D_s * np.sin(2.0 * i * dt + pi))
            pos[i + self.number_of_pipes] = (
                self.D_s * np.cos(2.0 * i * dt + pi + dt), self.D_s * np.sin(2.0 * i * dt + pi + dt))
        return pos

    def calculate_resistances(self, fluid_data: _FluidData, flow_rate_data: _FlowData, **kwargs) -> None:
        """
        This function calculates the conductive and convective resistances, which are constant.

        Parameters
        ----------
        fluid_data : FluidData
            Fluid data
        flow_rate_data : FlowData
            Flow rate data

        Returns
        -------
        None
        """
        # Pipe thermal resistance [m.K/W]
        self.R_p = gt.pipes.conduction_thermal_resistance_circular_pipe(
            self.r_in, self.r_out, self.k_p)

        # Convection heat transfer coefficient [W/(m^2.K)]
        h_f = gt.pipes.convective_heat_transfer_coefficient_circular_pipe(
            flow_rate_data.mfr(fluid_data=fluid_data, **kwargs) / self.number_of_pipes,
            self.r_in, fluid_data.mu(**kwargs), fluid_data.rho(**kwargs),
            fluid_data.k_f(**kwargs), fluid_data.cp(**kwargs), self.epsilon)
        # Film thermal resistance [m.K/W]
        self.R_f = 1.0 / (h_f * 2 * np.pi * self.r_in)

    def pipe_model(self, k_s: float, borehole: gt.boreholes.Borehole) -> gt.pipes._BasePipe:
        """
        This function returns the BasePipe model.

        Parameters
        ----------
        k_s : float
            Ground thermal conductivity
        borehole : Borehole
            Borehole object

        Returns
        -------
        BasePipe
        """
        return gt.pipes.MultipleUTube(self.pos, self.r_in, self.r_out, borehole, k_s, self.k_g,
                                      self.R_p + self.R_f, self.number_of_pipes, J=2)

    def Re(self, fluid_data: _FluidData, flow_rate_data: _FlowData, **kwargs) -> float:
        """
        Reynolds number.

        Parameters
        ----------
        fluid_data: FluidData
            Fluid data
        flow_rate_data : FlowData
            Flow rate data

        Returns
        -------
        Reynolds number : float
        """
        u = flow_rate_data.mfr(fluid_data=fluid_data, **kwargs) / self.number_of_pipes / fluid_data.rho(**kwargs) / \
            (pi * self.r_in ** 2)
        return fluid_data.rho(**kwargs) * u * self.r_in * 2 / fluid_data.mu(**kwargs)

    def pressure_drop(self, fluid_data: _FluidData, flow_rate_data: _FlowData, borehole_length: float,
                      **kwargs) -> float:
        """
        Calculates the pressure drop across the entire borehole.
        It assumed that the U-tubes are all connected in parallel.

        Parameters
        ----------
        fluid_data: FluidData
            Fluid data
        flow_rate_data : FlowData
            Flow rate data
        borehole_length : float
            Borehole length [m]

        Returns
        -------
        Pressure drop : float
            Pressure drop [kPa]
        """

        # Darcy fluid factor
        fd = gt.pipes.fluid_friction_factor_circular_pipe(
            flow_rate_data.mfr(fluid_data=fluid_data, **kwargs) / self.number_of_pipes,
            self.r_in,
            fluid_data.mu(**kwargs),
            fluid_data.rho(**kwargs),
            self.epsilon)
        A = pi * self.r_in ** 2
        V = (flow_rate_data.vfr(fluid_data=fluid_data, **kwargs) / 1000) / A / self.number_of_pipes

        # add 0.2 for the local losses
        # (source: https://www.engineeringtoolbox.com/minor-loss-coefficients-pipes-d_626.html)
        return ((fd * (borehole_length * 2) / (2 * self.r_in) + 0.2) * fluid_data.rho(**kwargs) * V ** 2 / 2) / 1000

    def draw_borehole_internal(self, r_b: float) -> None:
        """
        This function draws the internal structure of a borehole.
        This means, it draws the pipes inside the borehole.

        Parameters
        ----------
        r_b : float
            Borehole radius [m]

        Returns
        -------
        None
        """

        # borehole
        borehole = gt.boreholes.Borehole(100, 1, r_b, 0, 0)
        if self.R_p == 0:
            self.R_p = 0.1
            self.R_f = 0.1
            pipe = self.pipe_model(2, borehole)
            self.R_p, self.R_f = 0, 0
        else:
            pipe = self.pipe_model(2, borehole)

        pipe.visualize_pipes()
        plt.show()

    def __export__(self):
        return {'type': 'U',
                'nb_of_tubes': self.number_of_pipes,
                'thickness [mm]': (self.r_out * 1000 - self.r_in * 1000),
                'diameter [mm]': self.r_out * 2 * 100,
                'spacing [mm]': math.sqrt(self.pos[0][0] ** 2 + self.pos[0][1] ** 2) * 1000,
                'k_g [W/(m·K)]': self.k_g,
                'k_p [W/(m·K)]': self.k_p,
                'epsilon [mm]': self.epsilon * 1000}
