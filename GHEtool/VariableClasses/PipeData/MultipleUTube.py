import math

import numpy as np
import pygfunction as gt
import matplotlib.pyplot as plt
from math import pi

from GHEtool.VariableClasses.PipeData._PipeData import _PipeData
from GHEtool.VariableClasses.FluidData import FluidData


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

    def calculate_resistances(self, fluid_data: FluidData) -> None:
        """
        This function calculates the conductive and convective resistances, which are constant.

        Parameters
        ----------
        fluid_data : FluidData
            Fluid data

        Returns
        -------
        None
        """
        # Pipe thermal resistance [m.K/W]
        self.R_p = gt.pipes.conduction_thermal_resistance_circular_pipe(
            self.r_in, self.r_out, self.k_p)
        # Convection heat transfer coefficient [W/m2.K]
        h_f = gt.pipes.convective_heat_transfer_coefficient_circular_pipe(fluid_data.mfr / self.number_of_pipes,
                                                                          self.r_in, fluid_data.mu, fluid_data.rho,
                                                                          fluid_data.k_f, fluid_data.Cp, self.epsilon)
        # Film thermal resistance [m.K/W]
        self.R_f = 1.0 / (h_f * 2 * np.pi * self.r_in)

    def pipe_model(self, fluid_data: FluidData, k_s: float, borehole: gt.boreholes.Borehole) -> gt.pipes._BasePipe:
        """
        This function returns the BasePipe model.

        Parameters
        ----------
        fluid_data : FluidData
            Fluid data
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

    def Re(self, fluid_data: FluidData) -> float:
        """
        Reynolds number.

        Parameters
        ----------
        fluid_data: FluidData
            fluid data

        Returns
        -------
        Reynolds number : float
        """
        u = fluid_data.mfr / self.number_of_pipes / fluid_data.rho / \
            (pi * self.r_in ** 2)
        return fluid_data.rho * u * self.r_in * 2 / fluid_data.mu

    def pressure_drop(self, fluid_data: FluidData, borehole_depth: float) -> float:
        """
        Calculates the pressure drop across the entire borehole.
        It assumed that the U-tubes are all connected in parallel.

        Parameters
        ----------
        fluid_data: FluidData
            Fluid data
        borehole_depth : float
            Borehole depth [m]

        Returns
        -------
        Pressure drop : float
            Pressure drop [kPa]
        """

        # Darcy fluid factor
        fd = gt.pipes.fluid_friction_factor_circular_pipe(
            fluid_data.mfr / self.number_of_pipes,
            self.r_in,
            fluid_data.mu,
            fluid_data.rho,
            self.epsilon)
        A = pi * self.r_in ** 2
        V = (fluid_data.vfr / 1000) / A / self.number_of_pipes

        return (fd * (borehole_depth * 2) / (2 * self.r_in) * fluid_data.rho * V ** 2 / 2) / 1000

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
            pipe = self.pipe_model(FluidData(), 2, borehole)
            self.R_p, self.R_f = 0, 0
        else:
            pipe = self.pipe_model(FluidData(), 2, borehole)

        pipe.visualize_pipes()
        plt.show()

    def __repr__(self):
        return f'U tube' \
               f'\n\tNumber of U tubes [-]: {self.number_of_pipes}' \
               f'\n\tPipe wall thickness [mm]: {(self.r_out * 1000 - self.r_in * 1000):.1f}' \
               f'\n\tPipe diameter [mm]: {self.r_out * 2 * 1000}' \
               f'\n\tDistance from pipe to borehole center [mm]: {math.sqrt(self.pos[0][0] ** 2 + self.pos[0][1] ** 2) * 1000:.0f}' \
               f'\n\tGrout conductivity [W/(m·K)]: {self.k_g}' \
               f'\n\tPipe conductivity [W/(m·K)]: {self.k_p}' \
               f'\n\tPipe roughness [mm]: {self.epsilon * 1000}'
