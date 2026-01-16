import pygfunction as gt
from math import pi

from GHEtool.utils.calculate_friction_factor import *
from GHEtool.VariableClasses.PipeData.SingleUTube import SingleUTube
from GHEtool.VariableClasses.FluidData import _FluidData
from GHEtool.VariableClasses.FlowData import _FlowData


class Separatus(SingleUTube):
    """
    This class contains the model for the Separatus probe. Separatus is a new player in the geothermal space and
    uses a unique 'splitpipe'-technology. This technology inserts a membrane in the middel of a pipe with DN50, so that
    the inlet and outlet flows are separated.

    The model in this class has been obtained in close collaboration between Separatus AG (Swiss) and Enead BV (Belgium)
    based on real-life measurements from projects. It was found that the Separatus probe can be modelled like
    a single U-tube with a specific set of design parameters and an extra contact resistance.

    The implemented model is the first step towards designing a system with the Separatus technology. In the future, this
    model will be updated when new research has been conducted.

    More information on this technology and its advantages can be found here: https://separatus.ch/en.
    """

    def __init__(self, k_g: float = None):
        """
        
        Parameters
        ----------
        k_g : float
            Grout thermal conductivity [W/mK]
        """
        super().__init__(k_g=k_g,
                         r_in=(35.74 / 2 - 3) * 0.001,
                         r_out=(35.74 / 2) * 0.001,
                         k_p=0.44,
                         D_s=36 / 2 * 0.001)

    def explicit_model_borehole_resistance(self, fluid_data: _FluidData, flow_rate_data: _FlowData, k_s: float,
                                           borehole: gt.boreholes.Borehole, order: int = 1, R_p: float = None,
                                           **kwargs) -> float:
        """
        This function returns the effective borehole thermal resistance for the Separatus probe based on an explicit
        model (always second order).
        A Separatus heat exchanger can be modelled by using the model of a single U tube, with an extra contact resistance
        of 0.03 W/(mK) to account for the intermediate wall inside the probe. This value of 0.03W/(mK) was obtained by
        the company based on real-life measurements.

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
        if R_p is None:
            R_p_cond = self.calculate_conductive_resistance(**kwargs)
            R_p_conv = self.calculate_convective_resistance(flow_rate_data, fluid_data, **kwargs)

            R_p = R_p_cond + R_p_conv + 0.03

        return super().explicit_model_borehole_resistance(fluid_data, flow_rate_data, k_s, borehole, 2, R_p,
                                                          **kwargs)

    def pipe_model(self, k_s: float, borehole: gt.boreholes.Borehole) -> gt.pipes._BasePipe:
        """
        This function returns the pipe model for the Separatus probe.
        A Separatus heat exchanger can be modelled by using the model of a single U tube, with an extra contact resistance
        of 0.03 W/(mK) to account for the intermediate wall inside the probe. This value of 0.03W/(mK) was obtained by
        the company based on real-life measurements.

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
        single_u: gt.pipes._BasePipe = super().pipe_model(k_s, borehole)

        # add 0.03 W/(mK) as a contact resistance
        single_u.R_fp += 0.03
        single_u.update_thermal_resistances(single_u.R_fp)

        return single_u

    def Re(self, fluid_data: _FluidData, flow_rate_data: _FlowData, **kwargs) -> float:
        """
        Reynolds number.
        This model uses the hydraulic diameter of 25.51 mm.

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
        u = flow_rate_data.vfr_borehole(fluid_data=fluid_data, **kwargs) / (705.27 * 1e-6) / 1000
        return fluid_data.rho(**kwargs) * u * 0.02551 / fluid_data.mu(**kwargs)

    def pressure_drop(self, fluid_data: _FluidData, flow_rate_data: _FlowData, borehole_length: float,
                      **kwargs) -> float:
        """
        Calculates the pressure drop across the entire borehole.
        This model uses the hydraulic diameter of 25.51 mm.

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

        v = flow_rate_data.vfr_borehole(fluid_data=fluid_data, **kwargs) / (np.pi * 0.02551 ** 2 / 4) / 1000
        Re = fluid_data.rho(**kwargs) * v * 0.02551 / fluid_data.mu(**kwargs)
        # Darcy fluid factor
        if kwargs.get('haaland', False):
            fd = friction_factor_Haaland(Re, 0.02551 / 2, self.epsilon, **kwargs)
        else:
            fd = friction_factor_darcy_weisbach(Re, 0.02551 / 2, self.epsilon, **kwargs)

        A = 705.27 * 1e-6  # cross-sectional area of the separatus
        V = (flow_rate_data.vfr_borehole(fluid_data=fluid_data, **kwargs) / 1000) / A

        # add 0.2 for the local losses
        # (source: https://www.engineeringtoolbox.com/minor-loss-coefficients-pipes-d_626.html)
        return ((fd * (borehole_length * 2) / 0.02551 + 0.2) * fluid_data.rho(**kwargs) * V ** 2 / 2) / 1000

    def __export__(self):
        return {'type': 'Separatus',
                'k_g [W/(m·K)]': self.k_g}
