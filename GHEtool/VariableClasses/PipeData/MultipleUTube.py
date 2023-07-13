"""
This file contains the base class for the Multiple U-Tube borehole classes.
"""

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

    __slots__ = _PipeData.__slots__ + ('r_in', 'r_out', 'D_s', 'number_of_pipes', 'pos')

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

        self.r_in = r_in                    # inner pipe radius m
        self.r_out = r_out                  # outer pipe radius m
        self.D_s = D_s                      # distance of pipe until center m
        self.number_of_pipes = number_of_pipes  # number of pipes #
        self.pos = []
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
            pos[i + self.number_of_pipes] = (self.D_s * np.cos(2.0 * i * dt + pi + dt), self.D_s * np.sin(2.0 * i * dt + pi + dt))
        return pos

    def calculate_pipe_thermal_resistance(self) -> None:
        """
        This function calculates and sets the pipe thermal resistance R_p.

        Returns
        -------
        R_p : float
            The pipe thermal resistance [mK/W]
        """
        self.R_p: float = gt.pipes.conduction_thermal_resistance_circular_pipe(self.r_in, self.r_out, self.k_p)

    def calculate_convective_heat_transfer_coefficient(self, fluid_data: FluidData) -> float:
        """
        This function calculates the convective heat transfer coefficient h_f [W/m^2K].

        Parameters
        ----------
        fluid_data : FluidData
            FluidData object

        Returns
        -------
        h_f : float
            Convective heat transfer coefficient [W/m^2K]
        """

        return gt.pipes.convective_heat_transfer_coefficient_circular_pipe(fluid_data.mfr/self.number_of_pipes,
                                                                           self.r_in,
                                                                           fluid_data.mu,
                                                                           fluid_data.rho,
                                                                           fluid_data.k_f,
                                                                           fluid_data.Cp,
                                                                           self.epsilon)

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
                                      self.R_p + fluid_data.R_f, self.number_of_pipes, J=2)

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

        # calculate the pipe positions
        pos = self._axis_symmetrical_pipe

        # set figure
        figure, axes = plt.subplots()

        # initate circles
        circles_outer = []
        circles_inner = []

        # color inner circles and outer circles
        for i in range(self.number_of_pipes):
            circles_outer.append(plt.Circle(pos[i], self.r_out, color="black"))
            circles_inner.append(plt.Circle(pos[i], self.r_in, color="red"))
            circles_outer.append(plt.Circle(pos[i + self.number_of_pipes], self.r_out, color="black"))
            circles_inner.append(plt.Circle(pos[i + self.number_of_pipes], self.r_in, color="blue"))

        # set visual settings for figure
        axes.set_aspect('equal')
        axes.set_xlim([-r_b, r_b])
        axes.set_ylim([-r_b, r_b])
        axes.get_xaxis().set_visible(False)
        axes.get_yaxis().set_visible(False)
        plt.tight_layout()

        # define borehole circle
        borehole_circle = plt.Circle((0, 0), r_b, color="white")

        # add borehole circle to canvas
        axes.add_artist(borehole_circle)

        # add other circles to canvas
        for i in circles_outer:
            axes.add_artist(i)
        for i in circles_inner:
            axes.add_artist(i)

        # set background color
        axes.set_facecolor("grey")

        # show plot
        plt.show()