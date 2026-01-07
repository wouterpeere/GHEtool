import numpy as np
import pygfunction as gt
import matplotlib.pyplot as plt
from math import pi

from GHEtool.utils.calculate_friction_factor import *
from GHEtool.VariableClasses.PipeData._PipeData import _PipeData
from GHEtool.VariableClasses.FluidData import _FluidData
from GHEtool.VariableClasses.FlowData import _FlowData


class CoaxialPipe(_PipeData):
    """
    Contains information regarding the Coaxial pipe class.
    """

    __slots__ = 'r_in_in', 'r_in_out', 'r_out_in', 'r_out_out', 'k_g', 'is_inner_inlet', 'R_ff', 'R_fp', 'k_p_out'

    def __init__(self, r_in_in: float = None, r_in_out: float = None,
                 r_out_in: float = None, r_out_out: float = None, k_p: float = None, k_g: float = None,
                 epsilon: float = 1e-6, is_inner_inlet: bool = True, k_p_out: float = None):
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
            Pipe thermal conductivity of the inner and outer pipe [W/mK]. If k_p_out is set, k_p is only used for
            the conductivity of the inner pipe.
        k_g : float
            Thermal conductivity of the grout [W/mK]
        epsilon : float
            Pipe roughness of the tube [m]
        is_inner_inlet : bool
            True if the inlet of the fluid is through the inner annulus
        k_p_out : float
            Pipe conductivity of the outer pipe [W/mK]. If None, it is assumed that the outer pipe has the same
            conductivity as the inner pipe (k_p).
        """
        super().__init__(epsilon=epsilon, k_g=k_g, k_p=k_p)
        self.r_in_in: float = r_in_in
        self.r_in_out: float = r_in_out
        self.r_out_in: float = r_out_in
        self.r_out_out: float = r_out_out
        self.is_inner_inlet: bool = is_inner_inlet
        self.R_ff: float = 0.
        self.R_fp: float = 0.
        self.k_p_out = k_p if k_p_out is None else k_p_out

    def calculate_convective_resistance(self, flow_data: _FlowData, fluid_data: _FluidData, **kwargs):
        """
        This function evaluates the inner and outer convective resistance for the annulus region of the concentric pipe.
        Grundmann (2016) [#Grundmann2016]_ referenced Hellström (1991) [#Hellstrom1991b]_ in the discussion about
        inner and outer convection coefficients in an annulus region of a concentric pipe arrangement.
        Cengel and Ghajar (2015) [#ConvCoeff-CengelGhajar2015]_ state that inner and outer Nusselt numbers
        are approximately equivalent for turbulent flow. They additionally state that Gnielinski can be used for turbulent
        flow. Linear interpolation is used over the range 2300 < Re < 4000 for the evaluation of the Nusselt number,
        as proposed by Gnielinski (2013) [#Gnielinksi2013]_.

        Parameters
        ----------
        flow_data : _FlowData
            Flow data object
        fluid_data : _FluidData
            Fluid data object

        Returns
        -------
        (float or np.ndarray, float or np.ndarray)
            Convective resistances for the inner pipe (circular and inner annular part),
            Convective resistance for the outer pipe (outer annular part)

        References
        ----------
        .. [#Hellstrom1991b] Hellstrom, G. (1991). Ground heat storage. Thermal
           Analyses of Duct Storage Systems I: Theory. PhD Thesis. University of
           Lund, Department of Mathematical Physics. Lund, Sweden.
        .. [#Grundmann2016] Grundmann, R. (2016) Improved design methods for ground
            heat exchangers. Oklahoma State University, M.S. Thesis.
        .. [#ConvCoeff-CengelGhajar2015] Çengel, Y.A., & Ghajar, A.J. (2015). Heat
            and mass transfer: fundamentals & applications (Fifth edition.).
            McGraw-Hill.
        .. [#Gnielinksi2013] Gnielinski, V. (2013). On heat transfer in tubes.
            International Journal of Heat and Mass Transfer, 63, 134–140.
            https://doi.org/10.1016/j.ijheatmasstransfer.2013.04.015

        """
        low_re = 2300.0
        high_re = 4000.0

        # Hydraulic diameter and radius for concentric tube annulus region
        D_h = 2 * (self.r_out_in - self.r_in_out)
        r_h = D_h / 2
        # Cross-sectional area of the annulus region
        A_c = pi * ((self.r_out_in ** 2) - (self.r_in_out ** 2))

        # Ratio of radii (Grundmann, 2016)
        r_star = self.r_in_out / self.r_out_in

        m_dot = np.atleast_1d(np.asarray(flow_data.mfr_borehole(**kwargs, fluid_data=fluid_data), dtype=np.float64))

        # Reynolds number

        V = m_dot / A_c / fluid_data.rho(**kwargs)

        re = fluid_data.rho(**kwargs) * V * D_h / fluid_data.mu(**kwargs)

        # Allocate Nusselt array
        nu_inner = np.empty_like(re)
        nu_outer = np.empty_like(re)

        # Laminar
        laminar = re < low_re
        nu_inner[laminar] = 3.66 + 1.2 * r_star ** (-0.8)
        nu_outer[laminar] = 3.66 + 1.2 * r_star ** 0.5

        # Turbulent
        turbulent = re > high_re
        if np.any(turbulent):
            if kwargs.get('haaland', False):
                f = friction_factor_Haaland(re[turbulent], r_h, self.epsilon, **kwargs)
            else:
                f = friction_factor_darcy_weisbach(re[turbulent], r_h, self.epsilon, **kwargs)
            nu_inner[turbulent] = turbulent_nusselt(fluid_data, re[turbulent], f, array=turbulent, **kwargs)
            nu_outer[turbulent] = nu_inner[turbulent]

        # Transitional interpolation
        transitional = (~laminar) & (~turbulent)

        if np.any(transitional):
            nu_low_inner = 3.66 + 1.2 * r_star ** (-0.8)
            nu_low_outer = 3.66 + 1.2 * r_star ** 0.5

            if kwargs.get('haaland', False):
                # no array here to get a better fit with pygfunction (see validation file)
                f = friction_factor_Haaland(high_re, r_h, self.epsilon, **kwargs)
            else:
                f = friction_factor_darcy_weisbach(re[transitional], r_h, self.epsilon, **kwargs)
            nu_high = turbulent_nusselt(fluid_data, high_re, f, array=transitional, **kwargs)

            re_t = re[transitional]
            nu_inner[transitional] = (nu_low_inner + (re_t - low_re) * (nu_high - nu_low_inner) / (high_re - low_re))
            nu_outer[transitional] = (nu_low_outer + (re_t - low_re) * (nu_high - nu_low_outer) / (high_re - low_re))

        # Convective resistance for the annular part of the coaxial probe
        R_conv_inner = D_h / (nu_inner * np.pi * fluid_data.k_f(**kwargs) * self.r_in_out * 2)
        R_conv_outer = D_h / (nu_outer * np.pi * fluid_data.k_f(**kwargs) * self.r_out_in * 2)

        # create inner pipe object for the convective resistance calculation of the inner pipe
        R_conv_inner_inner = calculate_convective_resistance(
            flow_data, fluid_data, r_in=self.r_in_in, nb_of_pipes=1, epsilon=self.epsilon, **kwargs)

        if R_conv_inner.size == 1:
            return R_conv_inner.item() + R_conv_inner_inner, R_conv_outer.item()
        return R_conv_inner + R_conv_inner_inner, R_conv_outer

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
        # Pipe thermal resistances [m.K/W]
        # Inner pipe
        R_p_in = gt.pipes.conduction_thermal_resistance_circular_pipe(
            self.r_in_in, self.r_in_out, self.k_p)
        # Outer pipe
        R_p_out = gt.pipes.conduction_thermal_resistance_circular_pipe(
            self.r_out_in, self.r_out_out, self.k_p_out)

        # Fluid-to-fluid thermal resistance [m.K/W]
        Rfin, Rfout = self.calculate_convective_resistance(flow_rate_data, fluid_data, **kwargs)
        self.R_ff = R_p_in + Rfin
        # Coaxial GHE in borehole
        self.R_fp = R_p_out + Rfout

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
        return gt.pipes.Coaxial(pos=(0., 0.),
                                r_in=np.array([self.r_out_in, self.r_in_in]) if self.is_inner_inlet else
                                np.array([self.r_in_in, self.r_out_in]),
                                r_out=np.array([self.r_out_out, self.r_in_out]) if self.is_inner_inlet else
                                np.array([self.r_in_out, self.r_out_out]),
                                borehole=borehole, k_s=k_s, k_g=self.k_g, R_ff=self.R_ff, R_fp=self.R_fp, J=2)

    def Re(self, fluid_data: _FluidData, flow_rate_data: _FlowData, **kwargs) -> float:
        """
        Reynolds number.
        Note: This code is based on pygfunction, 'convective_heat_transfer_coefficient_concentric_annulus' in the
        Pipes class.

        Parameters
        ----------
        fluid_data : FluidData
            Fluid data
        flow_rate_data : FlowData
            Flow rate data
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
        V_dot = flow_rate_data.vfr_borehole(fluid_data=fluid_data, **kwargs) / 1000
        # Average velocity
        V = V_dot / A_c
        # Reynolds number
        return fluid_data.rho(**kwargs) * V * D_h / fluid_data.mu(**kwargs)

    def pressure_drop(self, fluid_data: _FluidData, flow_rate_data: _FlowData, borehole_length: float,
                      include_bend: bool = True, **kwargs) -> float:
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
        include_bend : bool
            True if the losses in the bend should be included

        Returns
        -------
        Pressure drop : float
            Pressure drop [kPa]
        """

        r_h = (self.r_out_in - self.r_in_in)
        # Cross-sectional area of the annulus region
        A_c = pi * ((self.r_out_in ** 2) - (self.r_in_in ** 2))
        # Average velocity
        V = (flow_rate_data.vfr_borehole(fluid_data=fluid_data, **kwargs) / 1000) / A_c

        # Darcy-Wiesbach friction factor
        fd = gt.pipes.fluid_friction_factor_circular_pipe(
            flow_rate_data.mfr_borehole(fluid_data=fluid_data, **kwargs), r_h, fluid_data.mu(**kwargs),
            fluid_data.rho(**kwargs),
            self.epsilon)

        bend = 0
        if include_bend:
            # add 0.2 for the local losses
            # (source: https://www.engineeringtoolbox.com/minor-loss-coefficients-pipes-d_626.html)
            bend = 0.2
        return ((fd * (borehole_length * 2) / (2 * r_h) + bend) * fluid_data.rho(**kwargs) * V ** 2 / 2) / 1000

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
            pipe = self.pipe_model(2, borehole)
            self.R_fp, self.R_ff = 0, 0
        else:
            pipe = self.pipe_model(2, borehole)

        pipe.visualize_pipes()
        plt.show()

    def __export__(self):
        return {
            'type': 'Coaxial',
            'inner_diameter [mm]': self.r_in_out * 2 * 1000,
            'inner_thickness [mm]': (self.r_in_out * 1000 - self.r_in_in * 1000),
            'outer_diameter [mm]': self.r_out_out * 2 * 1000,
            'outer_thickness [mm]': (self.r_out_out * 1000 - self.r_out_in * 1000),
            'k_g [W/(m·K)]': self.k_g,
            'k_p_in [W/(m·K)]': self.k_p,
            'k_p_out [W/(m·K)]': self.k_p_out,
            'epsilon [mm]': self.epsilon
        }
