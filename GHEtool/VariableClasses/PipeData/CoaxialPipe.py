import numpy as np
import pygfunction as gt
import matplotlib.pyplot as plt
from math import pi

from GHEtool.VariableClasses.PipeData._PipeData import _PipeData
from GHEtool.VariableClasses.FluidData import FluidData


class CoaxialPipe(_PipeData):
    """
    Contains information regarding the Multiple U-Tube class.
    """

    __slots__ = 'r_in_in', 'r_in_out', 'r_out_in', 'r_out_out', 'k_g', 'is_inner_inlet', 'R_ff', 'R_fp'

    def __init__(self, r_in_in: float = None, r_in_out: float = None,
                 r_out_in: float = None, r_out_out: float = None, k_p: float = None, k_g: float = None,
                 epsilon: float = 1e-6, is_inner_inlet: bool = True):
        """

        Parameters
        ----------
        r_in_in : float
            Inner radius of the inner annulus [m]
        r_in_out : float
            Outer radius of the inner annulus [m]
        r_out_in : float
            Inner radius of the outer annulus [m]
        r_out_out : float
            Outer radius of the outer annulus [m]
        k_p : float
            Pipe thermal conductivity  [W/mK]
        k_g : float
            Thermal conductivity of the grout [W/mK]
        epsilon : float
            Pipe roughness of the tube [m]
        is_inner_inlet : bool
            True if the inlet of the fluid is through the inner annulus
        """
        super().__init__(epsilon=epsilon, k_g=k_g, k_p=k_p)
        self.r_in_in: float = r_in_in
        self.r_in_out: float = r_in_out
        self.r_out_in: float = r_out_in
        self.r_out_out: float = r_out_out
        self.is_inner_inlet: bool = is_inner_inlet
        self.R_ff: float = 0.
        self.R_fp: float = 0.

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
        # Pipe thermal resistances [m.K/W]
        # Inner pipe
        R_p_in = gt.pipes.conduction_thermal_resistance_circular_pipe(
            self.r_in_in, self.r_in_out, self.k_p)
        # Outer pipe
        R_p_out = gt.pipes.conduction_thermal_resistance_circular_pipe(
            self.r_out_in, self.r_out_out, self.k_p)
        # Fluid-to-fluid thermal resistance [m.K/W]
        # Inner pipe
        h_f_in = gt.pipes.convective_heat_transfer_coefficient_circular_pipe(
            fluid_data.mfr, self.r_in_in, fluid_data.mu, fluid_data.rho, fluid_data.k_f, fluid_data.Cp, self.epsilon)
        R_f_in = 1.0 / (h_f_in * 2 * np.pi * self.r_in_in)
        # Outer pipe
        h_f_a_in, h_f_a_out = \
            gt.pipes.convective_heat_transfer_coefficient_concentric_annulus(
                fluid_data.mfr, self.r_in_out, self.r_out_in, fluid_data.mu, fluid_data.rho, fluid_data.k_f,
                fluid_data.Cp, self.epsilon)
        R_f_out_in = 1.0 / (h_f_a_in * 2 * np.pi * self.r_in_out)
        self.R_ff = R_f_in + R_p_in + R_f_out_in
        # Coaxial GHE in borehole
        R_f_out_out = 1.0 / (h_f_a_out * 2 * np.pi * self.r_out_in)
        self.R_fp = R_p_out + R_f_out_out

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
        return gt.pipes.Coaxial(pos=(0., 0.),
                                r_in=np.array([self.r_out_in, self.r_in_in]) if self.is_inner_inlet else
                                np.array([self.r_in_in, self.r_out_in]),
                                r_out=np.array([self.r_out_out, self.r_in_out]) if self.is_inner_inlet else
                                np.array([self.r_in_out, self.r_out_out]),
                                borehole=borehole, k_s=k_s, k_g=self.k_g, R_ff=self.R_ff, R_fp=self.R_fp, J=2)

    def Re(self, fluid_data: FluidData) -> float:
        """
        Reynolds number.
        Note: This code is based on pygfunction, 'convective_heat_transfer_coefficient_concentric_annulus' in the
        Pipes class.

        Parameters
        ----------
        fluid_data: FluidData
            fluid data

        Returns
        -------
        Reynolds number : float
        """
        # Hydraulic diameter and radius for concentric tube annulus region
        D_h = 2 * (self.r_out_in - self.r_in_out)
        r_h = D_h / 2
        # Cross-sectional area of the annulus region
        A_c = pi * ((self.r_out_in ** 2) - (self.r_in_out ** 2))
        # Volume flow rate
        V_dot = fluid_data.mfr / fluid_data.rho
        # Average velocity
        V = V_dot / A_c
        # Reynolds number
        return fluid_data.rho * V * D_h / fluid_data.mu

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
        if self.R_ff == 0:
            self.R_fp = 0.1
            self.R_ff = 0.1
            pipe = self.pipe_model(FluidData(), 2, borehole)
            self.R_fp, self.R_ff = 0, 0
        else:
            pipe = self.pipe_model(FluidData(), 2, borehole)

        pipe.visualize_pipes()
        plt.show()
