import joblib
import torch
import torch.nn as nn

import pygfunction as gt
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from GHEtool.utils.calculate_friction_factor import *
from GHEtool.VariableClasses.PipeData._PipeData import _PipeData
from GHEtool.VariableClasses.FluidData import _FluidData
from GHEtool.VariableClasses.FlowData import _FlowData


class MultiUTubeANN(nn.Module):
    """
    Small MLP: 6 inputs → 2 outputs.

    Inputs:  r_b, r_outer_pos, R_fp_center, R_fp_outer, k_b, k_s
    Outputs: R_b, R_a
    """

    def __init__(self, n_inputs: int = 6, n_outputs: int = 2):
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


class MultiUTube(_PipeData):
    """
    This class contains the model for the Multi-U-Tube probe from BLZ Geotechnik. This probe consists of a central, DN40
    PN16 probe going down and 10 DN16 PN16 satellite probes at the outside.

    More information on this technology and its advantages can be found here: https://www.blz-geotherm.de/en/
    """

    def __init__(self, k_g: float, position_satellites: float, groundwater_filled: bool = False):
        """

        Parameters
        ----------
        k_g : float
            Grout thermal conductivity [W/(mK)]
        position_satellites : float
            Distance of the center of the satellites and the borehole center [m]
        groundwater_filled : bool
            Filled with groundwater (overwrites the grout conductivity)
        """
        super().__init__(k_g, 0.4)

        # check configuration
        if position_satellites < 20e-3:
            raise ValueError(f'The distance of the pipe until the center should at least be 20 mm.')

        # load correct ANN model
        self._load_model()

        self._r_sat_out = 0.5 * 16e-3
        self._r_sat_in = 0.5 * 16e-3 - 1.5e-3
        self._r_cen_out = 0.5 * 40e-3
        self._r_cen_in = 0.5 * 40e-3 - 3.7e-3
        self._pos_sat = position_satellites
        self._n_satellites = 10

        self._groundwater_filled = groundwater_filled

    def _load_model(self) -> None:
        """
        This function loads the trained ANN models for the Multi-U-Tube.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When the a and b do not match the product specifics
        """
        from GHEtool import FOLDER
        self._model_path = FOLDER.joinpath("VariableClasses/PipeData/ANN/MultiUTube/borehole_ann.pt")
        self._x_scaler_path = FOLDER.joinpath("VariableClasses/PipeData/ANN/MultiUTube/x_scaler.joblib")
        self._y_scaler_path = FOLDER.joinpath("VariableClasses/PipeData/ANN/MultiUTube/y_scaler.joblib")

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
        raise NotImplementedError('The Multi-U-Tube can only be simulated with the explicit methods.')

    def calculate_conductive_resistance(self, **kwargs) -> tuple:
        """
        This function calculates the pipe thermal conductive resistance for both the central and satellite pipes.

        Returns
        -------
        tuple
            Conductive resistance of central pipe [mK/W], Conductive resistance of satellite pipes [mK/W]
        """
        R_p_sat = gt.pipes.conduction_thermal_resistance_circular_pipe(self._r_sat_in, self._r_sat_out, self.k_p)
        R_p_cen = gt.pipes.conduction_thermal_resistance_circular_pipe(self._r_cen_in, self._r_cen_out, self.k_p)

        return R_p_cen, R_p_sat

    def calculate_convective_resistance(self, flow_data: _FlowData, fluid_data: _FluidData, **kwargs):
        """
        This function calculates the convective resistance for both the central and satellite pipes.

        Parameters
        ----------
        flow_data : _FlowData
            Flow data object
        fluid_data : _FluidData
            Fluid data object

        Returns
        -------
         tuple
            Conductive resistance of central pipe [mK/W], Conductive resistance of satellite pipes [mK/W]
        """

        # Convective resistance
        R_conv_sat = calculate_convective_resistance(
            flow_data, fluid_data, r_in=self._r_sat_in, nb_of_pipes=self._n_satellites, epsilon=self.epsilon, **kwargs)
        R_conv_cen = calculate_convective_resistance(
            flow_data, fluid_data, r_in=self._r_cen_in, nb_of_pipes=1, epsilon=self.epsilon, **kwargs)

        return R_conv_cen, R_conv_sat

    def calculate_resistances(self, fluid_data: _FluidData, flow_rate_data: _FlowData, **kwargs) -> None:
        """
        This function calculates the conductive and convective resistances, which are constant.
        For the convective heat transfer coefficient, the correlation by (H. Niklas, 2026) is used.

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

        raise NotImplementedError('The Multi-U-Tube can only be simulated with the explicit methods.')

    def predict_Rb_Ra_series(self, r_b, r_outer_pos, R_fp_center, R_fp_sat, k_b, k_s):
        """
        Vectorized prediction of R_b and R_a based on the ANN-model.

        Parameters
        ----------
        Inputs can be float or array-like:
            r_b
            r_outer_pos
            R_fp_center
            R_fp_sat
            k_b
            k_s

        Returns
        -------
        R_b, R_a : np.ndarray
            Same shape as broadcasted inputs.
        """
        model = MultiUTubeANN()
        model.load_state_dict(torch.load(self._model_path, map_location="cpu"))
        model.eval()

        X_scaler = joblib.load(self._x_scaler_path)
        y_scaler = joblib.load(self._y_scaler_path)

        # Convert to arrays
        r_b = np.asarray(r_b)
        r_outer_pos = np.asarray(r_outer_pos)
        R_fp_center = np.asarray(R_fp_center)
        R_fp_sat = np.asarray(R_fp_sat)
        k_b = np.asarray(k_b)
        k_s = np.asarray(k_s)

        # Broadcast to common shape
        r_b, r_outer_pos, R_fp_center, R_fp_sat, k_b, k_s = np.broadcast_arrays(
            r_b, r_outer_pos, R_fp_center, R_fp_sat, k_b, k_s
        )

        shape = r_b.shape

        # Build ANN input matrix
        X = np.column_stack(
            [
                r_b.ravel(),
                r_outer_pos.ravel(),
                R_fp_center.ravel(),
                R_fp_sat.ravel(),
                k_b.ravel(),
                k_s.ravel(),
            ]
        )

        # Scale inputs
        X_s = X_scaler.transform(X)

        # Predict
        with torch.no_grad():
            y_s = model(torch.tensor(X_s, dtype=torch.float32)).numpy()

        y = y_scaler.inverse_transform(y_s)

        # Restore original shape
        R_b = y[:, 0].reshape(shape)
        R_a = y[:, 1].reshape(shape)

        return R_b, R_a

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
            Which Reynolds number should be calculated, either 'avg' for the entire pipe, 'cen' for the center pipe or 'sat' for the satellite pipes.

        Returns
        -------
        Reynolds number : float
        """

        u_cen = flow_rate_data.vfr_borehole(fluid_data=fluid_data, **kwargs) / \
                (np.pi * self._r_cen_in ** 2) / 1000
        re_cen = fluid_data.rho(**kwargs) * u_cen * self._r_cen_in * 2 / fluid_data.mu(**kwargs)

        u_sat = flow_rate_data.vfr_borehole(fluid_data=fluid_data, **kwargs) / \
                (np.pi * self._r_sat_in ** 2) / 1000 / self._n_satellites
        re_sat = fluid_data.rho(**kwargs) * u_sat * self._r_sat_in * 2 / fluid_data.mu(**kwargs)

        if type == "avg":
            return 0.5 * (re_sat + re_cen)
        if type == "cen":
            return re_cen
        return re_sat

    def explicit_model_borehole_resistance(self, fluid_data: _FluidData, flow_rate_data: _FlowData, k_s: float,
                                           borehole: gt.boreholes.Borehole, order: int = 1, R_p: float = None,
                                           **kwargs) -> float:
        """
        This function returns the effective borehole thermal resistance for the Multi-U-Tube based on an explicit
        model (always second order). The borehole resistance is based on an artificial neural network that was
        trained on 20.000 different simulations for each design of the Multi-U-Tube.

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
        R_p : float
            Pipe thermal resistance [mK/W], when this is not given, it is calculated explicitly.

        Returns
        -------
        float or list
            Effective borehole thermal resistance [mK/W]
        """
        R_cond_cen, R_cond_sat = self.calculate_conductive_resistance(**kwargs)
        R_conv_cen, R_conv_sat = self.calculate_convective_resistance(flow_rate_data, fluid_data, **kwargs)

        if self._pos_sat > borehole.r_b - self._r_sat_out:
            raise ValueError('The satellites are outside of the probe.')

        r_max = borehole.r_b - self._r_sat_out
        r_min = self._r_sat_out + self._r_cen_out
        rel_pos_sat = (self._pos_sat - r_min) / (r_max - r_min)

        R_b, R_a = self.predict_Rb_Ra_series(borehole.r_b, rel_pos_sat, R_cond_cen + R_conv_cen,
                                             R_cond_sat + R_conv_sat, self.k_g, k_s)
        r_v = borehole.H / (flow_rate_data.mfr_borehole(**kwargs, fluid_data=fluid_data) * fluid_data.cp(
            **kwargs))
        n = r_v / (R_b * R_a) ** 0.5
        return R_b * n * np.cosh(n) / np.sinh(n)

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

        # Darcy fluid factor
        if kwargs.get('haaland', False):
            fd_cen = friction_factor_Haaland(self.Re(fluid_data, flow_rate_data, type="cen", **kwargs), self._r_cen_in,
                                             self.epsilon,
                                             **kwargs)
            fd_sat = friction_factor_Haaland(self.Re(fluid_data, flow_rate_data, type="sat", **kwargs), self._r_sat_in,
                                             self.epsilon, **kwargs)
        else:
            fd_cen = friction_factor_darcy_weisbach(self.Re(fluid_data, flow_rate_data, type="cen", **kwargs),
                                                    self._r_cen_in,
                                                    self.epsilon,
                                                    **kwargs)
            fd_sat = friction_factor_darcy_weisbach(self.Re(fluid_data, flow_rate_data, type="sat", **kwargs),
                                                    self._r_sat_in,
                                                    self.epsilon, **kwargs)

        A_cen = np.pi * self._r_cen_in ** 2
        V_cen = (flow_rate_data.vfr_borehole(fluid_data=fluid_data, **kwargs) / 1000) / A_cen
        A_sat = np.pi * self._r_sat_in ** 2
        V_sat = (flow_rate_data.vfr_borehole(fluid_data=fluid_data, **kwargs) / 1000) / A_sat / self._n_satellites

        return (((fd_cen * borehole_length / (2 * self._r_cen_in) + 0.2) * fluid_data.rho(
            **kwargs) * V_cen ** 2 / 2) / 1000 +
                ((fd_sat * borehole_length / (2 * self._r_sat_in) + 0.2) * fluid_data.rho(
                    **kwargs) * V_sat ** 2 / 2) / 1000)

    def draw_borehole_internal(self, r_b: float) -> None:
        """
        This function draws the internal structure of a Multi-U-Tube borehole: a single central DN40 pipe
        at the borehole center, surrounded by 10 DN16 satellite pipes evenly distributed on a circle at
        radius ``self.pos_sat`` from the center.

        Parameters
        ----------
        r_b : float
            Borehole radius [m]

        Returns
        -------
        None
        """

        COLOR_CENTER = '#2196F3'  # central pipe (flow in)
        COLOR_SATELLITE = '#E53935'  # satellite pipes (flow out)

        borehole_radius = r_b

        # ── Plot ─────────────────────────────────────────────────────────────────────
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.set_aspect('equal')
        ax.axis('off')

        # Borehole circle (black outline, no fill)
        borehole = plt.Circle((0, 0), borehole_radius, fill=False, edgecolor='black', linewidth=2, zorder=1)
        ax.add_patch(borehole)

        # Central DN40 pipe, at the borehole center
        center_outer = plt.Circle((0, 0), self._r_cen_out, facecolor='black', zorder=2)
        center_inner = plt.Circle((0, 0), self._r_cen_in, facecolor=COLOR_CENTER, zorder=3)
        ax.add_patch(center_outer)
        ax.add_patch(center_inner)

        # 10 satellite DN16 pipes, evenly distributed on a circle of radius self.pos_sat
        angles = np.linspace(0, 2 * np.pi, self._n_satellites, endpoint=False)
        for angle in angles:
            cx = self._pos_sat * np.cos(angle)
            cy = self._pos_sat * np.sin(angle)

            sat_outer = plt.Circle((cx, cy), self._r_sat_out, facecolor='black', zorder=2)
            sat_inner = plt.Circle((cx, cy), self._r_sat_in, facecolor=COLOR_SATELLITE, zorder=3)
            ax.add_patch(sat_outer)
            ax.add_patch(sat_inner)

        # Axis limits with a small margin
        margin = borehole_radius * 1.1
        ax.set_xlim(-margin, margin)
        ax.set_ylim(-margin, margin)

        plt.tight_layout()
        plt.show()

    def __export__(self):
        return {
            'type': 'Multi-U-Tube',
            'satellite position [mm]': self._pos_sat * 1000,
            'k_g [W/(m·K)]': self.k_g,
        }
