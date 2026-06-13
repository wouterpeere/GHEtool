import pygfunction as gt
from math import pi
import torch
import torch.nn as nn
import joblib

from GHEtool import FOLDER
from GHEtool.utils.calculate_friction_factor import *
from GHEtool.VariableClasses.PipeData.SingleUTube import SingleUTube
from GHEtool.VariableClasses.FluidData import _FluidData
from GHEtool.VariableClasses.FlowData import _FlowData


class SplitPipeANN(nn.Module):
    """
    Small MLP for 5-input, 2-output regression.

    Inputs:
        r_b, R_fp_pipe, R_fp_center, k_b, k_s

    Outputs:
        R_b, R_a
    """

    def __init__(self, n_inputs: int = 5, n_outputs: int = 2):
        super().__init__()

        self.net = nn.Sequential(
            nn.Linear(n_inputs, 64),
            nn.Tanh(),
            nn.Linear(64, 64),
            nn.Tanh(),
            nn.Linear(64, 32),
            nn.Tanh(),
            nn.Linear(32, n_outputs),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class SeparatusNew():
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

    def check_values(self):
        return True

    def __init__(self, k_g: float = None):
        """
        
        Parameters
        ----------
        k_g : float
            Grout thermal conductivity [W/mK]
        """
        self.k_g = k_g
        self.diameter = 51 * 1e-3
        self.wall_thickness = 3e-3  # 3.1 * 1e-3
        self.r_in = (self.diameter / 2) - self.wall_thickness
        self.r_out = (self.diameter / 2)
        self.k_p = 0.44  # 2
        self.D_s = 4 * self.r_in / (3 * np.pi)
        self.epsilon = 1e-6
        self.number_of_pipes = 1
        self.pos = [(-self.D_s, 0), (self.D_s, 0)]
        self.pipe_inner_wall = 2.7 * 1e-3

    def calculate_conductive_resistance(self, **kwargs) -> tuple[float, float]:
        return (self.pipe_inner_wall / (self.k_p * self.r_in * 2),
                gt.pipes.conduction_thermal_resistance_circular_pipe(self.r_in, self.r_out, self.k_p) * 2)

    def calculate_convective_resistance(self, flow_rate_data, fluid_data, **kwargs) -> tuple[float, float]:
        hydraulic_diameter = 25.88 * 1e-3

        conv_circle = calculate_convective_resistance(
            flow_rate_data, fluid_data, r_in=hydraulic_diameter / 2, nb_of_pipes=1, epsilon=self.epsilon,
            wetted_perimeter=np.pi * self.r_in, **kwargs)
        nu = hydraulic_diameter / conv_circle / (np.pi * self.r_in) / fluid_data.k_f(**kwargs)

        plate = hydraulic_diameter / (nu * fluid_data.k_f(**kwargs) * self.r_in * 2)
        return plate * 2, conv_circle

    def predict_split_pipe_Rb_Ra_series(self, r_b, R_fp_pipe, R_fp_center, k_b, k_s):
        """
        Vectorized prediction of R_b and R_a for the split-pipe ANN.

        Parameters
        ----------
        Inputs can be float or array-like:
            r_b
            R_fp_pipe
            R_fp_center
            k_b
            k_s

        Returns
        -------
        R_b, R_a : np.ndarray
            Same shape as broadcasted inputs
        """
        model_path = FOLDER.joinpath(f"VariableClasses/PipeData/Model separatus/separatus.pt")
        x_scaler_path = FOLDER.joinpath(f"VariableClasses/PipeData/Model separatus/separatus_x.joblib")
        y_scaler_path = FOLDER.joinpath(f"VariableClasses/PipeData/Model separatus/separatus_y.joblib")
        model_path = FOLDER.joinpath(f"VariableClasses/PipeData/Model separatus/split_pipe_two_rfp_ann.pt")
        x_scaler_path = FOLDER.joinpath(f"VariableClasses/PipeData/Model separatus/split_pipe_two_rfp_X_scaler.joblib")
        y_scaler_path = FOLDER.joinpath(f"VariableClasses/PipeData/Model separatus/split_pipe_two_rfp_y_scaler.joblib")
        model = SplitPipeANN()
        model.load_state_dict(torch.load(model_path, map_location="cpu"))
        model.eval()

        X_scaler = joblib.load(x_scaler_path)
        y_scaler = joblib.load(y_scaler_path)

        # Convert to arrays
        r_b = np.asarray(r_b)
        R_fp_pipe = np.asarray(R_fp_pipe)
        R_fp_center = np.asarray(R_fp_center)
        k_b = np.asarray(k_b)
        k_s = np.asarray(k_s)

        # Broadcast to common shape
        r_b, R_fp_pipe, R_fp_center, k_b, k_s = np.broadcast_arrays(
            r_b, R_fp_pipe, R_fp_center, k_b, k_s
        )

        # Flatten
        shape = r_b.shape
        X = np.column_stack([
            r_b.ravel(),
            R_fp_pipe.ravel(),
            R_fp_center.ravel(),
            k_b.ravel(),
            k_s.ravel(),
        ])

        # Scale
        X_s = X_scaler.transform(X)

        # Predict
        with torch.no_grad():
            y_s = model(torch.tensor(X_s, dtype=torch.float32)).numpy()

        y = y_scaler.inverse_transform(y_s)

        # Reshape back
        R_b = y[:, 0].reshape(shape)
        R_a = y[:, 1].reshape(shape)

        return R_b, R_a

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
            R_p_cond_wall, R_p_cond_circle = self.calculate_conductive_resistance(**kwargs)
            R_p_conv_wall, R_p_conv_circle = self.calculate_convective_resistance(flow_rate_data, fluid_data, **kwargs)

            r_fp_pipe = R_p_cond_circle + R_p_conv_circle
            r_fp_center = R_p_cond_wall + R_p_conv_wall
            # print(R_p_cond_wall, R_p_cond_circle, R_p_conv_wall, R_p_conv_circle)
            R_b, R_a = self.predict_split_pipe_Rb_Ra_series(borehole.r_b, r_fp_pipe, r_fp_center, self.k_g, k_s)
            # print(f'New Rf pipe: {r_fp_pipe:.3f}, Rf center: {r_fp_center:.3f}, R_b: {R_b:.3f}, R_a= {R_a:.3f}')
            r_v = borehole.H / (flow_rate_data.mfr_borehole(**kwargs, fluid_data=fluid_data) * fluid_data.cp(
                **kwargs))
            n = r_v / (R_b * R_a) ** 0.5
            return R_b * n * np.cosh(n) / np.sinh(n)

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
