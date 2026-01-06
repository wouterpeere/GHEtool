import math

import numpy as np
import pygfunction as gt

from GHEtool.utils.calculate_friction_factor import *
from GHEtool.VariableClasses.PipeData.SingleUTube import MultipleUTube
from GHEtool.VariableClasses.FluidData import _FluidData
from GHEtool.VariableClasses.FlowData import _FlowData


class Turbocollector(MultipleUTube):
    """
    This class contains the model for the turbocollector probe from Muovitech. The correlations for the Nusselt number
    and the friction factor where obtained from the work of (H. Niklas, 2025).

    More information on this technology and its advantages can be found here: https://www.turbocollector.com/.
    """

    def __init__(self, k_g: float = None, r_in: float = None, r_out: float = None,
                 D_s: float = None, number_of_pipes: int = None):
        """

        Parameters
        ----------
        k_g : float
            Grout thermal conductivity [W/(mK)]
        r_in : float
            Inner pipe radius [m]
        r_out : float
            Outer pipe radius [m]
        D_s : float
            Distance of the pipe until center [m]
        number_of_pipes : int
            Number of pipes [#] (single U-tube: 1, double U-tube:2)
        """
        super().__init__(k_g=k_g, r_in=r_in, r_out=r_out, k_p=0.4, D_s=D_s, number_of_pipes=number_of_pipes)

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
        m_dot = np.asarray(flow_data.mfr_borehole(**kwargs, fluid_data=fluid_data), dtype=np.float64)

        # Reynolds number
        re = 4.0 * m_dot / (fluid_data.mu(**kwargs) * np.pi * self.r_in * 2) / self.number_of_pipes

        # Allocate Nusselt array
        nu = np.empty_like(re)

        nu_sl = 3.66

        pr = fluid_data.Pr(**kwargs)

        # Laminar turbo correlation (Re ≤ 1700)
        laminar = re <= 1700.0
        if np.any(laminar):
            nu[laminar] = np.sqrt(nu_sl ** 2 + ((5.5e-7) * re[laminar] ** 1.77 * pr ** 0.5) ** 2)

        # Transitional turbo correlation (1700 < Re ≤ 4000)
        transitional = (re > 1700.0) & (re <= 4000.0)
        if np.any(transitional):
            nu[transitional] = np.sqrt(nu_sl ** 2 + (0.86 * (re[transitional] - 1699.0) ** 0.39 * pr ** 0.32) ** 2)

        # Turbulent region (Re > 4000)
        turbulent = re > 4000.0
        if np.any(turbulent):
            # constant enhancement relative to smooth pipe correlation
            nu_4000 = np.sqrt(nu_sl ** 2 + (0.86 * (4000.0 - 1699.0) ** 0.39 * pr ** 0.32) ** 2)

            if kwargs.get('haaland', False):
                f = friction_factor_Haaland(4000.0, self.r_in, self.epsilon, **kwargs)
            else:
                f = friction_factor_darcy_weisbach(4000.0, self.r_in, self.epsilon, **kwargs)

            nu_base_4000 = turbulent_nusselt(fluid_data, 4000, f, **kwargs)
            diff = nu_4000 - nu_base_4000

            if kwargs.get('haaland', False):
                f = friction_factor_Haaland(re[turbulent], self.r_in, self.epsilon, **kwargs)
            else:
                f = friction_factor_darcy_weisbach(re[turbulent], self.r_in, self.epsilon, **kwargs)
            nu[turbulent] = turbulent_nusselt(fluid_data, re[turbulent], f, **kwargs) + diff

        # Convective resistance
        return 1.0 / (nu * np.pi * fluid_data.k_f(**kwargs))

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
        self.R_p = gt.pipes.conduction_thermal_resistance_circular_pipe(
            self.r_in, self.r_out, self.k_p)

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
                return 1 / (1 + np.exp(-5 * ((Re - 1700) / (2300 - 1700) - 0.5)))

            return (1 - w(Re)) * 64 / Re + w(Re) * (-1.8 * np.log10(6.9 / Re)) ** -2

        # Darcy fluid factor
        fd = f_turbo(self.Re(fluid_data, flow_rate_data, **kwargs))

        A = math.pi * self.r_in ** 2
        V = (flow_rate_data.vfr_borehole(fluid_data=fluid_data, **kwargs) / 1000) / A / self.number_of_pipes

        # add 0.2 for the local losses
        # (source: https://www.engineeringtoolbox.com/minor-loss-coefficients-pipes-d_626.html)
        return ((fd * (borehole_length * 2) / (2 * self.r_in) + 0.2) * fluid_data.rho(**kwargs) * V ** 2 / 2) / 1000

    def __export__(self):
        return {
            'type': 'Turbocollector',
            'nb_of_tubes': self.number_of_pipes,
            'thickness [mm]': (self.r_out * 1000 - self.r_in * 1000),
            'diameter [mm]': self.r_out * 2 * 1000,
            'spacing [mm]': math.sqrt(self.pos[0][0] ** 2 + self.pos[0][1] ** 2) * 1000,
            'k_g [W/(m·K)]': self.k_g,
        }
