import numpy as np
import pygfunction as gt
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from GHEtool import FOLDER
from GHEtool.utils.calculate_friction_factor import *
from GHEtool.VariableClasses.PipeData._PipeData import _PipeData
from GHEtool.VariableClasses.FluidData import _FluidData
from GHEtool.VariableClasses.FlowData import _FlowData


def _predict_rb_ra_numpy(ann: dict, X: np.ndarray) -> np.ndarray:
    """5→64→64→32→2 Tanh MLP + StandardScaler, no torch."""
    Xs = (X - ann["x_mean"]) / ann["x_scale"]
    h = np.tanh(Xs @ ann["w0"].T + ann["b0"])
    h = np.tanh(h @ ann["w1"].T + ann["b1"])
    h = np.tanh(h @ ann["w2"].T + ann["b2"])
    ys = h @ ann["w3"].T + ann["b3"]
    return ys * ann["y_scale"] + ann["y_mean"]


class SeparatusNew(_PipeData):
    """
    This class contains the model for the Separatus probe from separatus. The borehole internals are calculated
    using an ANN trained with 20k simulations from a Boundary Element Method model. The heat transfer inside the pipe,
    is calculated using the equivalent hydraulic diameter.

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
        self.diameter = 51.9 * 1e-3
        self.wall_thickness = 3.05e-3
        self.r_in = (self.diameter / 2) - self.wall_thickness
        self.r_out = (self.diameter / 2)
        self.k_p = 0.4
        self.epsilon = 1e-6
        self.pipe_inner_wall = 2.7 * 1e-3
        self.d_hydraulic = 26.5e-3

        self._ann = None
        self._model_path = FOLDER.joinpath("VariableClasses/PipeData/ANN/separatus/separatus.npz")

    def calculate_conductive_resistance(self, **kwargs) -> tuple[float, float]:
        """
        This function calculates the pipe thermal conductive resistance for both the inner pipe wall and the outer wall.

        Returns
        -------
        tuple
            Conductive resistance for the separation wall [mK/W], Conductive resistance for the outer wall [mK/W]
        """
        return (self.pipe_inner_wall / (self.k_p * self.r_in * 2),
                # multiplied by two since only half the pipe circumference is present
                gt.pipes.conduction_thermal_resistance_circular_pipe(self.r_in, self.r_out, self.k_p) * 2)

    def calculate_convective_resistance(self, flow_rate_data, fluid_data, **kwargs) -> tuple[float, float]:
        """
            This function calculates the convective resistance for both the inner pipe wall and the outer wall
            based on the hydraulic diameter.

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
            .. [#Niklas] Niklas Hidman. (2026). Thermohydraulic performance evaluation of internally finned elliptical geothermal collector pipes
            """
        wetted_perimeter = np.pi * self.r_in + 2 * self.r_in
        conv_circle = calculate_convective_resistance(
            flow_rate_data, fluid_data, r_in=self.hydraulic_diameter / 2, nb_of_pipes=1, area=self.cross_sectional_area,
            epsilon=self.epsilon,
            wetted_perimeter=wetted_perimeter,  # include entire wetted perimeter in calculation
            **kwargs)

        # convert back to Nusselt number
        nu = self.hydraulic_diameter / conv_circle / wetted_perimeter / fluid_data.k_f(**kwargs)
        conv_circle = self.hydraulic_diameter / (nu * fluid_data.k_f(**kwargs) * self.r_in * np.pi)
        # Rconv = 1/(hP) = Dh/(Nu*kf*P) with P wetted area (separation wall)
        plate = self.hydraulic_diameter / (nu * fluid_data.k_f(**kwargs) * self.r_in * 2)
        return plate * 2, conv_circle

    def _load_ann(self) -> dict:
        """Load and cache weights + scalers from the .npz file."""
        if self._ann is None:
            with np.load(self._model_path) as data:
                self._ann = {key: np.asarray(data[key]) for key in data.files}
        return self._ann

    def predict_split_pipe_Rb_Ra_series(self, r_b, R_fp_pipe, R_fp_center, k_b, k_s, **kwargs):
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

        y = _predict_rb_ra_numpy(self._load_ann(), X)

        # Reshape back
        R_b = y[:, 0].reshape(shape)
        R_a = y[:, 1].reshape(shape)

        return R_b, R_a

    def explicit_model_borehole_resistance(self, fluid_data: _FluidData, flow_rate_data: _FlowData, k_s: float,
                                           borehole: gt.boreholes.Borehole, R_p: float = None, **kwargs) -> float:
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
            R_b, R_a = self.predict_split_pipe_Rb_Ra_series(borehole.r_b, r_fp_pipe, r_fp_center, self.k_g, k_s,
                                                            **kwargs)
            r_v = borehole.H / (flow_rate_data.mfr_borehole(**kwargs, fluid_data=fluid_data) * fluid_data.cp(
                **kwargs))
            n = r_v / (R_b * R_a) ** 0.5
            self._Ra = R_a
            self._Rb = R_b
            return R_b * n * np.cosh(n) / np.sinh(n)

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
        raise NotImplementedError('The separatus can only be simulated with the explicit methods.')

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

        raise NotImplementedError('The separatus can only be simulated with the explicit methods.')

    def Re(self, fluid_data: _FluidData, flow_rate_data: _FlowData, **kwargs) -> float:
        """
        Reynolds number.
        This model uses the hydraulic diameter of 26.5 mm.

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
        u = flow_rate_data.vfr_borehole(fluid_data=fluid_data, **kwargs) / self.cross_sectional_area / 1000
        return fluid_data.rho(**kwargs) * u * self.hydraulic_diameter / fluid_data.mu(**kwargs)

    def pressure_drop(self, fluid_data: _FluidData, flow_rate_data: _FlowData, borehole_length: float,
                      **kwargs) -> float:
        """
        Calculates the pressure drop across the entire borehole.
        This model uses the hydraulic diameter of 26.5 mm.

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

        # calculate flow velocity
        v = flow_rate_data.vfr_borehole(fluid_data=fluid_data, **kwargs) / self.cross_sectional_area / 1000

        # Darcy fluid factor
        if kwargs.get('haaland', False):
            fd = friction_factor_Haaland(
                self.Re(fluid_data, flow_rate_data, **kwargs), self.hydraulic_diameter / 2, self.epsilon, **kwargs)
        else:
            fd = friction_factor_darcy_weisbach(
                self.Re(fluid_data, flow_rate_data, **kwargs), self.hydraulic_diameter / 2, self.epsilon, **kwargs)

        # add 0.75 for the local losses, according to simulations by OST
        return ((fd * (borehole_length * 2) / self.hydraulic_diameter + 0.75) * fluid_data.rho(
            **kwargs) * v ** 2 / 2) / 1000

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

        COLOR_SECONDARY = '#2196F3'  # left inner ellipse (flow in)
        COLOR_RED = '#E53935'  # right inner ellipse (flow out)

        # ── Derived values ───────────────────────────────────────────────────────────
        borehole_radius = r_b
        a_inner = self.a / 2 - self.wall_thickness
        b_inner = self.b / 2 - self.wall_thickness

        # Ellipse centers: left at (-spacing, 0), right at (+spacing, 0)
        centers = [(-self.D_s, 0), (self.D_s, 0)]
        inner_colors = [COLOR_SECONDARY, COLOR_RED]

        # ── Plot ─────────────────────────────────────────────────────────────────────
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.set_aspect('equal')
        ax.axis('off')

        # Borehole circle (black outline, no fill)
        borehole = plt.Circle((0, 0), borehole_radius, fill=False, edgecolor='black', linewidth=2, zorder=1)
        ax.add_patch(borehole)

        # Ellipses
        for i, (cx, cy) in enumerate(centers):
            # Outer ellipse (black pipe wall)
            outer = patches.Ellipse(
                (cx, cy),
                width=self.b, height=self.a,
                facecolor='black',
                zorder=2
            )
            ax.add_patch(outer)

            # Inner ellipse (fluid channel)
            inner = patches.Ellipse(
                (cx, cy),
                width=2 * b_inner, height=2 * a_inner,
                facecolor=inner_colors[i],
                zorder=3
            )
            ax.add_patch(inner)

        # Axis limits with a small margin
        margin = borehole_radius * 1.1
        ax.set_xlim(-margin, margin)
        ax.set_ylim(-margin, margin)

        plt.tight_layout()
        plt.show()

    def __export__(self):
        return {'type': 'Separatus',
                'k_g [W/(m·K)]': self.k_g}
