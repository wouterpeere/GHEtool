import math

import numpy as np
import pygfunction as gt

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

        def colebrook_white(Re: float, Pr: float) -> float:
            """
            Traditional Colebrook-White equation for rough pipes.

            Parameters
            ----------
            Re : float
                Reynolds number [-]
            Pr : float
                Prandtl number [-]

            Returns
            -------
            Nussel number : float
                Nusselt number for tradition, rough pipes
            """
            # Colebrook-White equation for rough pipes
            fDarcy = 0.02
            df = 1.0e99
            while abs(df / fDarcy) > 1e-6:
                one_over_sqrt_f = -2.0 * np.log10(1e-4 / 3.7
                                                  + 2.51 / (Re * np.sqrt(fDarcy)))
                fDarcy_new = 1.0 / one_over_sqrt_f ** 2
                df = fDarcy_new - fDarcy
                fDarcy = fDarcy_new
            return 0.125 * fDarcy * (Re - 1.0e3) * Pr / \
                (1.0 + 12.7 * np.sqrt(0.125 * fDarcy) * (Pr ** (2.0 / 3.0) - 1.0))

        def nusselt_turbo(Re: float, Pr: float) -> float:
            """
            This function returns the Nusselt number for the turbocollector using the correlation defined by
            (H. Niklas, 2025).

            Parameters
            ----------
            Re : float
                Reynolds number [-]
            Pr : float
                Prandtl number [-]

            Returns
            -------
            Nussel number : float
                Nusselt number for the turbo collector
            """
            nu_sl = 3.66

            def nusselt_lam_turbo(Re, Pr):
                return np.sqrt(nu_sl ** 2 + ((5.5 * 1e-7) * Re ** 1.77 * Pr ** 0.5) ** 2)

            def nusselt_tur_turbo(Re, Pr):
                return np.sqrt(nu_sl ** 2 + (0.86 * (Re - 1699) ** .39 * Pr ** .32) ** 2)

            if Re <= 1700:
                return nusselt_lam_turbo(Re, Pr)
            if 1700 < Re <= 4000:
                return nusselt_tur_turbo(Re, Pr)

            # add a constant improvement to the traditional Nusselt number for Re > 4000
            diff = nusselt_turbo(4000, Pr) - colebrook_white(4000, Pr)
            return colebrook_white(Re, Pr) + diff

        # Pipe thermal resistance [m.K/W]
        self.R_p = gt.pipes.conduction_thermal_resistance_circular_pipe(
            self.r_in, self.r_out, self.k_p)

        Re = self.Re(fluid_data, flow_rate_data, **kwargs)
        Pr = fluid_data.Pr(**kwargs)

        nusselt_number = nusselt_turbo(Re, Pr)

        h_f = fluid_data.k_f(**kwargs) * nusselt_number / (self.r_in * 2)

        # Film thermal resistance [m.K/W]
        self.R_f = 1.0 / (h_f * 2 * np.pi * self.r_in)

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
