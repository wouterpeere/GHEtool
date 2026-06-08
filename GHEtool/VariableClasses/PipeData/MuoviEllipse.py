import math

import numpy as np
import pygfunction as gt

from GHEtool.utils.calculate_friction_factor import *
from GHEtool.VariableClasses.PipeData.SingleUTube import SingleUTube
from GHEtool.VariableClasses.FluidData import _FluidData
from GHEtool.VariableClasses.FlowData import _FlowData


class MuoviEllipse(SingleUTube):
    """
    This class contains the model for the MuoviELLIPSE probe from Muovitech. The correlations for the Nusselt number
    and the friction factor where obtained from the work of (H. Niklas, 2026).

    More information on this technology and its advantages can be found here: https://www.muovitech.com/group/?page=MuoviELLIPSE.
    """

    def __init__(self, k_g: float, a: float, b: float, wall_thickness: float, D_s: float = None):
        """

        Parameters
        ----------
        k_g : float
            Grout thermal conductivity [W/(mK)]
        a : float
            Long axis diameter [m]
        b: float
            Short axis diameter [m]
        wall_thickness : float
            Wall thickness [m]
        D_s : float
            Distance of the pipe until center [m]
        """
        self.k_g = k_g
        self.a = a
        self.b = b
        self.wall_thickness = wall_thickness

        self.area_outer = np.pi * a * b
        h = (a - b) ** 2 / ((a + b) ** 2)
        perimeter_outer = np.pi * (a + b) * (1 + (3 * h) / (10 + np.sqrt(4 - 3 * h)))
        self.hydraulic_diameter_outer = 4 * self.area_outer / perimeter_outer

        self.area_inner = np.pi * (a - wall_thickness * 2) * (b - wall_thickness * 2)
        h = ((a - wall_thickness * 2) - (b - wall_thickness * 2)) ** 2 / (
                ((a - wall_thickness * 2) + (b - wall_thickness * 2)) ** 2)
        perimeter_inner = np.pi * ((a - wall_thickness * 2) + (b - wall_thickness * 2)) * (
                1 + (3 * h) / (10 + np.sqrt(4 - 3 * h)))
        self.hydraulic_diameter_inner = 4 * self.area_inner / perimeter_inner

        super().__init__(k_g, self.hydraulic_diameter_inner / 2, self.hydraulic_diameter_outer / 2, 0.4, D_s)

    def Re(self, fluid_data: _FluidData, flow_rate_data: _FlowData, borehole_length: float, **kwargs) -> float:
        """
        Reynolds number.

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
        Reynolds number : float
        """

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
        raise NotImplementedError('The MuoviELLIPSE can only be simulated with the explicit methods.')

    def calculate_convective_resistance(self, flow_data: _FlowData, fluid_data: _FluidData, **kwargs):
        """
        This function calculates the convective resistance based on the work of (Hidman, N) [#Niklas]_.

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

        References
        ----------
        .. [#Niklas] Niklas Hidman, Daniel Almgren, Kim Johansson, Eskil Nilsson, How internal fins enhance the thermohydraulic performance of geothermal pipes: A direct numerical simulation study, International Journal of Heat and Mass Transfer, Volume 256, Part 3, 2026, 128114, ISSN 0017-9310, https://doi.org/10.1016/j.ijheatmasstransfer.2025.128114.
        """
        m_dot = np.atleast_1d(np.asarray(flow_data.mfr_borehole(**kwargs, fluid_data=fluid_data), dtype=np.float64))

        # Reynolds number
        re = self.hydraulic_diameter_inner * m_dot / (fluid_data.mu(**kwargs) * self.area_inner)

        # Allocate Nusselt array
        nu = np.empty_like(re)

        nu_sl = 3.66

        pr = np.atleast_1d(np.asarray(fluid_data.Pr(**kwargs)))

        # Laminar turbo correlation (Re ≤ 1850)
        laminar = re <= 1850.0
        if np.any(laminar):
            pr_formula = pr[laminar] if len(pr) > 1 else pr[0]
            nu[laminar] = np.sqrt(nu_sl ** 2 + ((-0.321) * re[laminar] ** 0.2 * pr_formula ** 0.21) ** 2)

        # Transitional turbo correlation (1700 < Re ≤ 4000)
        transitional = (re > 1850.0) & (re <= 4000.0)
        if np.any(transitional):
            pr_formula = pr[transitional] if len(pr) > 1 else pr[0]
            nu[transitional] = np.sqrt(
                nu_sl ** 2 + (1.96 * (re[transitional] - 1849.9) ** 0.295 * pr_formula ** 0.29) ** 2)

        # Turbulent region (Re > 4000)
        turbulent = re > 4000.0
        if np.any(turbulent):
            # constant enhancement relative to smooth pipe correlation
            pr_formula = pr[turbulent] if len(pr) > 1 else pr[0]
            nu_4000 = np.sqrt(nu_sl ** 2 + (1.96 * (4000 - 1849.9) ** 0.295 * pr_formula ** 0.29) ** 2)

            if kwargs.get('haaland', False):
                f = friction_factor_Haaland(4000.0, self.hydraulic_diameter_inner / 2, self.epsilon, **kwargs)
            else:
                f = friction_factor_darcy_weisbach(4000.0, self.hydraulic_diameter_inner / 2, self.epsilon, **kwargs)

            nu_base_4000 = turbulent_nusselt(fluid_data, 4000, f, array=turbulent, **kwargs)
            diff = nu_4000 - nu_base_4000

            if kwargs.get('haaland', False):
                f = friction_factor_Haaland(re[turbulent], self.hydraulic_diameter_inner / 2, self.epsilon, **kwargs)
            else:
                f = friction_factor_darcy_weisbach(re[turbulent], self.hydraulic_diameter_inner / 2, self.epsilon,
                                                   **kwargs)
            nu[turbulent] = turbulent_nusselt(fluid_data, re[turbulent], f, array=turbulent, **kwargs) + diff

        # Convective resistance
        R_conv = 1.0 / (nu * np.pi * fluid_data.k_f(**kwargs))
        if R_conv.size == 1:
            return R_conv.item()
        return R_conv

    def calculate_resistances(self, fluid_data: _FluidData, flow_rate_data: _FlowData, **kwargs) -> None:
        """
        This function calculates the conductive and convective resistances, which are constant.
        For the convective heat transfer coefficient, the correlation by (H. Niklas, 2025) is used.

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
        self.R_p = gt.pipes.conduction_thermal_resistance_circular_pipe(self.r_in, self.r_out, self.k_p)

        self.R_f = self.calculate_convective_resistance(flow_data=flow_rate_data, fluid_data=fluid_data, **kwargs)

    def pressure_drop(self, fluid_data: _FluidData, flow_rate_data: _FlowData, borehole_length: float,
                      **kwargs) -> float:
        """
        Calculates the pressure drop across the entire borehole.
        The friction factor is taken from the work of (H. Niklas, 2025).

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

        def f_turbo(Re: float) -> float:
            """
            This function calculates the friction factor of the turbocollector.

            Parameters
            ----------
            Re : float
                Reynolds number [-]

            Returns
            -------
            Friction factor : float
                Friction factor of the turbocollector.
            """

            def w(Re) -> float:
                return 1 / (1 + np.exp(-5 * ((Re - 1850) / (2300 - 1850) - 0.5)))

            return (1 - w(Re)) * 65 / Re + w(Re) * (-1.8 * np.log10(6.9 / Re)) ** -2

        # Darcy fluid factor
        fd = f_turbo(self.Re(fluid_data, flow_rate_data, **kwargs))

        V = (flow_rate_data.vfr_borehole(fluid_data=fluid_data, **kwargs) / 1000) / self.area_inner

        # add 0.2 for the local losses
        # (source: https://www.engineeringtoolbox.com/minor-loss-coefficients-pipes-d_626.html)
        return ((fd * (borehole_length * 2) / self.hydraulic_diameter_inner + 0.2) * fluid_data.rho(
            **kwargs) * V ** 2 / 2) / 1000

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

        pass

    def __export__(self):
        return {
            'type': 'MuoviELLIPSE',
            'nb_of_tubes': self.number_of_pipes,
            'thickness [mm]': (self.r_out * 1000 - self.r_in * 1000),
            'diameter [mm]': self.r_out * 2 * 1000,
            'spacing [mm]': math.sqrt(self.pos[0][0] ** 2 + self.pos[0][1] ** 2) * 1000,
            'k_g [W/(m·K)]': self.k_g,
        }
