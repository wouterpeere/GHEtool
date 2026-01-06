import copy
import math

import numpy as np
import pygfunction as gt
import matplotlib.pyplot as plt

from math import pi
from GHEtool.utils.calculate_friction_factor import *
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
            Grout thermal conductivity [W/(mK)]
        r_in : float
            Inner pipe radius [m]
        r_out : float
            Outer pipe radius [m]
        k_p : float
            Pipe thermal conductivity [W/(mK)]
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

        # Film thermal resistance [m.K/W]
        self.R_f = self.calculate_convective_resistance(flow_rate_data, fluid_data, **kwargs)

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
        u = flow_rate_data.vfr_borehole(fluid_data=fluid_data, **kwargs) / self.number_of_pipes / \
            (pi * self.r_in ** 2) / 1000
        return fluid_data.rho(**kwargs) * u * self.r_in * 2 / fluid_data.mu(**kwargs)

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

        # Darcy fluid factor
        fd = gt.pipes.fluid_friction_factor_circular_pipe(
            flow_rate_data.mfr_borehole(fluid_data=fluid_data, **kwargs) / self.number_of_pipes,
            self.r_in,
            fluid_data.mu(**kwargs),
            fluid_data.rho(**kwargs),
            self.epsilon)
        A = pi * self.r_in ** 2
        V = (flow_rate_data.vfr_borehole(fluid_data=fluid_data, **kwargs) / 1000) / A / self.number_of_pipes

        bend = 0
        if include_bend:
            # add 0.2 for the local losses
            # (source: https://www.engineeringtoolbox.com/minor-loss-coefficients-pipes-d_626.html)
            bend = 0.2
        return ((fd * (borehole_length * 2) / (2 * self.r_in) + bend) * fluid_data.rho(**kwargs) * V ** 2 / 2) / 1000

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

    def calculate_convective_resistance(self, flow_data: _FlowData, fluid_data: _FluidData, **kwargs):
        """
        This function calculates the convective resistance.
        For the laminar flow, a fixed Nusselt number of 3.66 is used, for the turbulent flow, the Gnielinski
        equation is used. The Reynolds numbers between 2300-4000 are linearly interpolated.

        Parameters
        ----------
        flow_data : _FlowData
            Flow data object
        fluid_data : _FluidData
            Fluid data object

        Returns
        -------
        float or np.ndarray
            Convective resistances
        """
        low_re = 2300.0
        high_re = 4000.0

        m_dot = np.atleast_1d(np.asarray(flow_data.mfr_borehole(**kwargs, fluid_data=fluid_data), dtype=np.float64))

        # Reynolds number
        re = 4.0 * m_dot / (fluid_data.mu(**kwargs) * np.pi * self.r_in * 2) / self.number_of_pipes

        # Allocate Nusselt array
        nu = np.empty_like(re)

        # Laminar
        laminar = re < low_re
        nu[laminar] = 3.66

        # Turbulent
        turbulent = re > high_re
        if np.any(turbulent):
            if kwargs.get('haaland', False):
                f = friction_factor_Haaland(re[turbulent], self.r_in, self.epsilon, **kwargs)
            else:
                f = friction_factor_darcy_weisbach(re[turbulent], self.r_in, self.epsilon, **kwargs)
            nu[turbulent] = turbulent_nusselt(fluid_data, re[turbulent], f, array=turbulent, **kwargs)

        # Transitional interpolation
        transitional = (~laminar) & (~turbulent)

        if np.any(transitional):
            nu_low = 3.66
            if kwargs.get('haaland', False):
                # no array here to get a better fit with pygfunction (see validation file)
                f = friction_factor_Haaland(high_re, self.r_in, self.epsilon, **kwargs)
            else:
                f = friction_factor_darcy_weisbach(re[transitional], self.r_in, self.epsilon, **kwargs)
            nu_high = turbulent_nusselt(fluid_data, high_re, f, array=transitional, **kwargs)

            re_t = re[transitional]
            nu[transitional] = (nu_low + (re_t - low_re) * (nu_high - nu_low) / (high_re - low_re))

        # Convective resistance
        R_conv = 1.0 / (nu * np.pi * fluid_data.k_f(**kwargs))
        if R_conv.size == 1:
            return R_conv.item()
        return R_conv

    def explicit_model_borehole_resistance(self, fluid_data: _FluidData, flow_rate_data: _FlowData, k_s: float,
                                           borehole: gt.boreholes.Borehole, order: int = 1, **kwargs) -> None:
        """
        This function calculates the conductive and convective resistances, which are constant.
        For the single U case, the formulas from (Claesson & Javed, 2018) are taken [#CJ2018]_.
        For double U probes, this is based on (Claesson & Javed, 2019) [#CJ2019]_.

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
        order : int
            Order of the model. For the single U, a zeroth, first and second order explicit model is implemented,
            for the double U, only a zeroth and first order.

        Returns
        -------
        None

        References
        ----------
        .. [#CJ2018] Claesson, J., & Javed, S. (2018). Explicit Multipole Formulas for Calculating Thermal Resistance of Single U-Tube Ground Heat Exchangers. Energies, 11(1), 214. https://doi.org/10.3390/en11010214
        .. [#CJ2019] Claesson, J., & Javed, S. (2019). Explicit multipole formulas and thermal network models for calculating thermal resistances of double U-pipe borehole heat exchangers. Science and Technology for the Built Environment, 25(8), 980–992. https://doi.org/10.1080/23744731.2019.1620565
        """
        if self.number_of_pipes > 2:
            raise NotImplementedError('Explicit models are only implemented for the single and double probes.')

        # Pipe resistance [m.K/W]
        R_p_cond = gt.pipes.conduction_thermal_resistance_circular_pipe(self.r_in, self.r_out, self.k_p)
        R_p_conv = self.calculate_convective_resistance(flow_rate_data, fluid_data, **kwargs)

        R_p = R_p_cond + R_p_conv

        sigma = (self.k_g - k_s) / (self.k_g + k_s)

        if self.number_of_pipes == 1:
            # use solution from (Claesson & Javed, 2018)
            # calculate zeroth order
            R_plus = R_p + 1 / (2 * np.pi * self.k_g) * (
                    np.log(borehole.r_b ** 2 / (2 * self.r_out * self.D_s)) + sigma * np.log(
                borehole.r_b ** 4 / (borehole.r_b ** 4 - self.D_s ** 4)))
            R_min = R_p + 1 / (2 * np.pi * self.k_g) * (np.log(2 * self.D_s / (self.r_out)) + sigma * np.log(
                (borehole.r_b ** 2 + self.D_s ** 2) / (borehole.r_b ** 2 - self.D_s ** 2)))
            if order == 0:
                # calculate internal resistance and local borehole resistance
                R_a = 2 * R_min
                R_b = R_plus / 2
            elif order == 1:
                beta = R_p * 2 * np.pi * self.k_g
                p0 = self.r_out / (2 * self.D_s)
                p1 = self.r_out * self.D_s / (borehole.r_b ** 2 - self.D_s ** 2)
                p2 = self.r_out * self.D_s / (borehole.r_b ** 2 + self.D_s ** 2)
                b1 = (1 - beta) / (1 + beta)

                B1_plus = 1 / (2 * np.pi * self.k_g) * ((b1 * (-p0 + sigma * p1 - sigma * p2) ** 2) / (
                        1 + b1 * (p0 ** 2 + sigma * (p1 * (p1 + 2 * p0) + p2 * (p2 - 2 * p0)))))
                B1_min = 1 / (2 * np.pi * self.k_g) * ((b1 * (p0 + sigma * p1 + sigma * p2) ** 2) / (
                        1 + b1 * ((-1) * p0 ** 2 + sigma * (p1 * (p1 + 2 * p0) + p2 * (p2 - 2 * p0) * (-1)))))

                # calculate internal resistance and local borehole resistance
                R_a = 2 * R_min - 2 * B1_min
                R_b = R_plus / 2 - B1_plus / 2
            elif order == 2:
                beta = R_p * 2 * np.pi * self.k_g
                p0 = self.r_out / (2 * self.D_s)
                p1 = self.r_out * self.D_s / (borehole.r_b ** 2 - self.D_s ** 2)
                p2 = self.r_out * self.D_s / (borehole.r_b ** 2 + self.D_s ** 2)
                b1 = (1 - beta) / (1 + beta)
                b2 = (1 - 2 * beta) / (1 + 2 * beta)

                A12_plus = -2 * p0 ** 3 + 2 * sigma * (p1 ** 2 * (p1 + 2 * p0) - p2 ** 2 * (p2 - 2 * p0))
                A12_min = +2 * p0 ** 3 + 2 * sigma * (p1 ** 2 * (p1 + 2 * p0) - p2 ** 2 * (p2 - 2 * p0) * (-1))
                A22_plus = 6 * p0 ** 4 + 2 * sigma * (p1 ** 2 * (3 * p1 ** 3 + 8 * p1 * p0 + 4 * p0 ** 2) + p2 ** 2 * (
                        3 * p2 ** 2 - 8 * p2 * p0 + 4 * p0 ** 2))
                A22_min = (-1) * 6 * p0 ** 4 + 2 * sigma * (
                        p1 ** 2 * (3 * p1 ** 3 + 8 * p1 * p0 + 4 * p0 ** 2) + p2 ** 2 * (
                        3 * p2 ** 2 - 8 * p2 * p0 + 4 * p0 ** 2) * (-1))
                V1_plus = -p0 + sigma * p1 - sigma * p2
                V1_min = p0 + sigma * p1 + sigma * p2
                A11_plus = p0 ** 2 + sigma * (p1 * (p1 + 2 * p0) + p2 * (p2 - 2 * p0))
                A11_min = -p0 ** 2 - sigma * (p1 * (p1 + 2 * p0) - p2 * (p2 - 2 * p0))
                V2_plus = p0 ** 2 + sigma * p1 ** 2 + sigma * p2 ** 2
                V2_min = (-1) * p0 ** 2 + sigma * p1 ** 2 + sigma * p2 ** 2 * (-1)

                B2_plus = 1 / (2 * np.pi * self.k_g) * ((b1 * V1_plus ** 2) * (
                        2 + b2 * A22_plus) - 2 * b1 * b2 * V1_plus * V2_plus * A12_plus + b2 * V2_plus ** 2 * (
                                                                1 + b1 * A11_plus)) / (
                                  (1 + b1 * A11_plus) * (2 + b2 * A22_plus) - b1 * b2 * A12_plus ** 2)

                B2_min = 1 / (2 * np.pi * self.k_g) * ((b1 * V1_min ** 2) * (
                        2 + b2 * A22_min) - 2 * b1 * b2 * V1_min * V2_min * A12_min + b2 * V2_min ** 2 * (
                                                               1 + b1 * A11_min)) / (
                                 (1 + b1 * A11_min) * (2 + b2 * A22_min) - b1 * b2 * A12_min ** 2)

                # calculate internal resistance and local borehole resistance
                R_a = 2 * R_min - 2 * B2_min
                R_b = R_plus / 2 - B2_plus / 2
            else:
                raise NotImplementedError(
                    'Explicit models are only implemented for single U probes are only implemented for orders 0 to 2.')
        else:
            # use solution from (Claesson & Javed, 2019)
            R_min = R_p + 1 / (2 * np.pi * self.k_g) * (np.log(self.D_s / (self.r_out)) + sigma * np.log(
                (borehole.r_b ** 4 + self.D_s ** 4) / (borehole.r_b ** 4 - self.D_s ** 4)))
            R_plus = R_p / 2 + 1 / (4 * np.pi * self.k_g) * (
                    np.log(borehole.r_b ** 4 / (4 * self.r_out * self.D_s ** 3)) + sigma * np.log(
                borehole.r_b ** 8 / (borehole.r_b ** 8 - self.D_s ** 8)))

            if order == 0:
                # calculate internal resistance and local borehole resistance
                R_a = 2 * R_min
                R_b = R_plus / 2
            elif order == 1:
                beta = R_p * 2 * np.pi * self.k_g
                ppc = self.r_out ** 2 / (4 * self.D_s ** 2)
                pc = self.D_s ** 2 / ((borehole.r_b ** 8 - self.D_s ** 8) ** (1 / 4))
                pb = borehole.r_b ** 2 / ((borehole.r_b ** 8 - self.D_s ** 8) ** (1 / 4))
                b1 = (1 - beta) / (1 + beta)

                B1_min = 1 / (2 * np.pi * self.k_g) * (b1 * ppc * (1 + 8 * sigma * pc ** 2 * pb ** 2) ** 2) / (
                        1 - b1 * ppc * (3 - 32 * sigma * (pc ** 2 * pb ** 6 + pc ** 6 * pb ** 2)))
                B1_plus = 1 / (4 * np.pi * self.k_g) * (b1 * ppc * (3 - 8 * sigma * pc ** 4) ** 2) / (
                        1 + b1 * ppc * (5 + 64 * sigma * pc ** 4 * pb ** 4))

                # calculate internal resistance and local borehole resistance
                R_a = 2 * R_min - 2 * B1_min
                R_b = R_plus / 2 - B1_plus / 2
            else:
                raise NotImplementedError(
                    'Explicit models are only implemented for double U probes are only implemented for orders 0 an 1.')
        r_v = borehole.H / (flow_rate_data.mfr_borehole(**kwargs, fluid_data=fluid_data) * fluid_data.cp(**kwargs))
        n = r_v / (R_b * R_a) ** 0.5
        return R_b * n * np.cosh(n) / np.sinh(n)

    def __export__(self):
        return {'type': 'U',
                'nb_of_tubes': self.number_of_pipes,
                'thickness [mm]': (self.r_out * 1000 - self.r_in * 1000),
                'diameter [mm]': self.r_out * 2 * 1000,
                'spacing [mm]': math.sqrt(self.pos[0][0] ** 2 + self.pos[0][1] ** 2) * 1000,
                'k_g [W/(m·K)]': self.k_g,
                'k_p [W/(m·K)]': self.k_p,
                'epsilon [mm]': self.epsilon * 1000
                }
