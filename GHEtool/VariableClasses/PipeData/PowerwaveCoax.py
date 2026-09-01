import numpy as np
import pygfunction as gt
import matplotlib.pyplot as plt
from math import pi

from GHEtool.VariableClasses.BaseClass import BaseClass
from GHEtool.utils.calculate_friction_factor import *
from GHEtool.VariableClasses.FluidData import _FluidData
from GHEtool.VariableClasses.FlowData import _FlowData


class PowerwaveCoax(BaseClass):
    """
    This class contains the model for the JANSEN powerwave coax. This is a coaxial heat exchanger with a DN32PN16 smooth
    inner pipe and a corrugated outer pipe .The correlations for the Nusselt number
    and the friction factor where obtained via a DNS simulation.

    More information about the modeling of this probe can be found in (Peere et al., 2026) [#PeereEtAl]_.

    References
    ----------
    .. [#PeereEtAl] Peere, W., Hidman, N., Hofstetter, R. (2026) Development of a thermohydraulic model for the JANSEN powerwave with direct numerical simulation and its impact on the thermal borehole resistance. In Proceedings of Der Geothermiekongress. Postdam (Germany), 20-22 October 2026.
    """

    def __init__(self, k_g: float = None):
        """

        Parameters
        ----------
        k_g : float
            Thermal conductivity of the grout [W/mK]
        """
        self.k_g = k_g
        self.r_in_in: float = 16e-3 - 2.9e-3
        self.r_in_out: float = 16e-3
        self.r_out_in: float = 31.5e-3 - 2.9e-3
        self.r_out_out: float = 31.5e-3
        self.k_p: float = 0.4
        self.r_eq: float = (57.2e-3 + 49.2e-3) / 2 / 2

    def calculate_convective_resistance(self, flow_data: _FlowData, fluid_data: _FluidData, **kwargs):
        """
        This function evaluates the inner and outer convective resistance for the annulus region of the concentric pipe,
        based on the work of Peere et al. (2026) [#PeereEtAl_].

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
        .. [#PeereEtAl] Peere, W., Hidman, N., Hofstetter, R. (2026) Development of a thermohydraulic model for the
        JANSEN powerwave with direct numerical simulation and its impact on the thermal borehole resistance.
        In Proceedings of Der Geothermiekongress. Postdam (Germany), 20-22 October 2026.
        """

        def Nu_i_lam(Re, Pr):
            """
            This function calculates the laminar Nusselt nummer at the outer wall of the inner pipe.
            """
            return np.sqrt(6.7 ** 2 + (4.80747200e-05 * (Re ** 1.5906) * (Pr ** 0.4184)) ** 2)

        def Nu_i_turb(Re, Pr):
            """
            This function calculates the turbulent Nusselt nummer at the outer wall of the inner pipe.
            """
            return np.sqrt(6.7 ** 2 + (0.25400 * ((Re - 1000) ** 0.593377) * (Pr ** 0.312665)) ** 2)

        def Nu_i_corr_comb(Re, Pr):
            """
            This function calculates the Nusselt nummer at the outer wall of the inner pipe.
            """
            s = (1 + np.exp(- (4 * (Re - 1100) / (1200 - 1100) + 0))) ** (-1)
            return (1 - s) * Nu_i_lam(Re, Pr) + s * np.where(Re < 1000, Nu_i_lam(Re, Pr), Nu_i_turb(Re, Pr))

        def Nu_o_lam(Re, Pr):
            """
            This function calculates the laminar Nusselt nummer at the inner wall of the corrugated pipe.
            """
            return np.sqrt(6.7 ** 2 + (7.06256718e-09 * (Re ** 3.025891) * (Pr ** 0.4292)) ** 2)

        def Nu_o_turb(Re, Pr):
            """
            This function calculates the turbulent Nusselt nummer at the inner wall of the corrugated pipe.
            """
            return np.sqrt(6.7 ** 2 + (4.85563 * ((Re - 1000) ** 0.34399) * (Pr ** 0.1793452)) ** 2)

        def Nu_o_corr_comb(Re, Pr):
            """
            This function calculates the Nusselt nummer at the inner wall of the corrugated pipe.
            """
            s = (1 + np.exp(- (4 * (Re - 1100) / (1200 - 1100) + 0))) ** (-1)
            return (1 - s) * Nu_o_lam(Re, Pr) + s * np.where(Re <= 1000, Nu_o_lam(Re, Pr), Nu_o_turb(Re, Pr))

        # create inner pipe object for the convective resistance calculation of the inner pipe using the
        # correlations developed by Peere et al. (2026)
        Nu_outer_inner = Nu_i_corr_comb(self.Re(fluid_data, flow_data, 'outer', **kwargs), fluid_data.Pr(**kwargs))
        Nu_outer_outer = Nu_o_corr_comb(self.Re(fluid_data, flow_data, 'outer', **kwargs), fluid_data.Pr(**kwargs))

        # convective resistance for the inner wall of the inner pipe is just a smooth pipe
        R_conv_inner = np.atleast_1d(calculate_convective_resistance(
            flow_data, fluid_data, r_in=self.r_in_in, nb_of_pipes=1, epsilon=1e-6, **kwargs))

        # convert Nusselt numbers to convective resistances
        R_conv_outer_inner = self.r_in_out * 2 / (Nu_outer_inner * np.pi * fluid_data.k_f(**kwargs) * self.r_in_out * 2)
        R_conv_outer = self.r_eq * 2 / (Nu_outer_outer * np.pi * fluid_data.k_f(**kwargs) * self.r_eq * 2)

        if R_conv_outer_inner.size == 1:
            return R_conv_inner.item() + R_conv_outer_inner, R_conv_outer.item()
        return R_conv_inner + R_conv_outer_inner, R_conv_outer

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

        Raises
        ------
        NotImplementedError

        """
        raise NotImplementedError('The JANSEN powerwave coax can only be simulated with the explicit methods.')

    def explicit_model_borehole_resistance(self, fluid_data: _FluidData, flow_rate_data: _FlowData, k_s: float,
                                           borehole: gt.boreholes.Borehole, R_p: float = None,
                                           **kwargs) -> float:
        """
        This function calculates the borehole thermal resistance for a coaxial pipe using a simplified 1D
        resistance network model [#Grundmann]_.

        Parameters
        ----------
        fluid_data : FluidData
            Fluid data
        flow_rate_data : FlowData
            Flow rate data
        k_s : float
            Ground thermal conductivity
        borehole : Borehole
            Borehole object
        R_p : float
            Pipe thermal resistance [mK/W], when this is not given, it is calculated explicitly.

        Returns
        -------
        float
            Effective borehole thermal resistance [mK/W]

        References
        ----------
        .. [#Grundmann] Grundmann, Rachel Marie. "Improved design methods for ground heat exchangers." Master's thesis, Oklahoma State University, 2016.
        """

        # Pipe thermal resistances [m.K/W]
        # Inner pipe
        R_p_in = gt.pipes.conduction_thermal_resistance_circular_pipe(
            self.r_in_in, self.r_in_out, self.k_p)
        # Outer pipe
        R_p_out = gt.pipes.conduction_thermal_resistance_circular_pipe(
            self.r_out_in, self.r_out_out, self.k_p)

        R_conv_inner, R_conv_outer = self.calculate_convective_resistance(flow_rate_data, fluid_data, **kwargs)

        R_cond_grout = np.log(borehole.r_b / self.r_out_out) / (2 * pi * self.k_g)

        r_a = R_conv_inner + R_p_in
        r_b = R_conv_outer + R_p_out + R_cond_grout

        rv = borehole.H / (flow_rate_data.mfr_borehole(**kwargs, fluid_data=fluid_data) * fluid_data.cp(**kwargs))
        n = rv / (2 * r_b) * (1 + 4 * r_b / r_a) ** (1 / 2)
        return r_b * n * np.cosh(n) / np.sinh(n)

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

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError('The JANSEN powerwave coax can only be simulated with the explicit methods.')

    def Re(self, fluid_data: _FluidData, flow_rate_data: _FlowData, type: str = "avg", **kwargs) -> float:
        """
        This function returns the Reynolds number

        Parameters
        ----------
        fluid_data: FluidData
            Fluid data
        flow_rate_data : FlowData
            Flow rate data
        type : str
            Which Reynolds number should be calculated, either 'avg' for the entire pipe, 'inner' for the central pipe
            or 'annulus' for the annulus.

        Returns
        -------
        Reynolds number : float
        """

        u_inner = flow_rate_data.vfr_borehole(fluid_data=fluid_data, **kwargs) / (np.pi * self.r_in_in ** 2) / 1000
        re_inner = fluid_data.rho(**kwargs) * u_inner * self.r_in_in * 2 / fluid_data.mu(**kwargs)

        u_annulus = flow_rate_data.vfr_borehole(fluid_data=fluid_data, **kwargs) / (np.pi * self.r_eq ** 2) / 1000
        re_annulus = fluid_data.rho(**kwargs) * u_annulus * self.r_eq * 2 / fluid_data.mu(**kwargs)

        if type == "avg":
            return 0.5 * (re_annulus + re_inner)
        if type == "inner":
            return re_inner
        return re_annulus

    def pressure_drop(self, fluid_data: _FluidData, flow_rate_data: _FlowData, borehole_length: float,
                      include_bend: bool = True, **kwargs) -> float:
        """
        Calculates the pressure drop across the entire borehole. The friction factors were obtained by direct
        numerical simulation [#PeereEtAl_].

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

        References
        ----------
        .. [#PeereEtAl] Peere, W., Hidman, N., Hofstetter, R. (2026) Development of a thermohydraulic model for the
        JANSEN powerwave with direct numerical simulation and its impact on the thermal borehole resistance.
        In Proceedings of Der Geothermiekongress. Postdam (Germany), 20-22 October 2026.
        """

        # Average velocity
        V_in = (flow_rate_data.vfr_borehole(fluid_data=fluid_data, **kwargs) / 1000) / (np.pi * self.r_in_in ** 2)
        V_an = (flow_rate_data.vfr_borehole(fluid_data=fluid_data, **kwargs) / 1000) / (np.pi * self.r_eq ** 2)

        def f_lam(Re):
            """
            This function calculates the friction factor in the laminar range for the annulas part of the powerwave coax.
            """
            a = 64 * 2.47
            return a / Re

        def f_turb(Re):
            """
            This function calculates the friction factor in the turbulent range for the annulas part of the powerwave coax.
            """
            return -71.65 + 71.68 * Re ** 0.000289

        def f_corr_comb(Re):
            """
            This function calculates the friction factor for the annulas part of the powerwave coax.
            """
            s = (1 + np.exp(- (2 * (Re - 1000) / (1400 - 1000) + 0))) ** (-1)
            return (1 - s) * f_lam(Re) + s * f_turb(Re)

        if kwargs.get('haaland', False):
            fd = friction_factor_Haaland(self.Re(fluid_data, flow_rate_data, "inner", **kwargs), self.r_in_in,
                                         1e-6, **kwargs)
        else:
            fd = friction_factor_darcy_weisbach(self.Re(fluid_data, flow_rate_data, "inner", **kwargs), self.r_in_in,
                                                1e-6, **kwargs)

        bend = 0
        if include_bend:
            # add 0.2 for the local losses
            # (source: https://www.engineeringtoolbox.com/minor-loss-coefficients-pipes-d_626.html)
            bend = 0.2
        return (((fd * borehole_length / (2 * self.r_in_in) + bend) * fluid_data.rho(**kwargs) * V_in ** 2 / 2) / 1000 +
                ((f_corr_comb(self.Re(fluid_data, flow_rate_data, "outer", **kwargs)) * borehole_length / (
                        2 * self.r_eq) + bend) * fluid_data.rho(**kwargs) * V_an ** 2 / 2) / 1000)

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
        pipe = self.pipe_model(2, borehole)

        pipe.visualize_pipes()
        plt.show()

    def __export__(self):
        return {
            'type': 'JANSEN powerwave coax',
            'k_g [W/(m·K)]': self.k_g,
        }
