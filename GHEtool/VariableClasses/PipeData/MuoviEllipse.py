import joblib
import torch
import torch.nn as nn

import pygfunction as gt
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from GHEtool.utils.calculate_friction_factor import *
from GHEtool.VariableClasses.PipeData.SingleUTube import SingleUTube
from GHEtool.VariableClasses.FluidData import _FluidData
from GHEtool.VariableClasses.FlowData import _FlowData


class EllipseANN(nn.Module):
    """
    Small MLP for 5-input, 2-output regression.

    Inputs:
        r_b, spacing, R_fp, k_b, k_s

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

        # check configuration
        if D_s < b / 2:
            raise ValueError(f'The distance of the pipe until the center should at least be {b / 2} m.')

        # load correct ANN model
        self._load_model(a, b)

        self.area_outer = np.pi * a * b / 4
        h = (a / 2 - b / 2) ** 2 / ((a / 2 + b / 2) ** 2)
        perimeter_outer = np.pi * (a / 2 + b / 2) * (1 + (3 * h) / (10 + np.sqrt(4 - 3 * h)))
        self.hydraulic_diameter_outer = 4 * self.area_outer / perimeter_outer

        self.area_inner = np.pi * (a - wall_thickness * 2) * (b - wall_thickness * 2) / 4
        h = (((a - wall_thickness * 2) / 2 - (b - wall_thickness * 2) / 2) ** 2 /
             (((a - wall_thickness * 2) / 2 + (b - wall_thickness * 2) / 2) ** 2))
        perimeter_inner = np.pi * ((a - wall_thickness * 2) / 2 + (b - wall_thickness * 2) / 2) * (
                1 + (3 * h) / (10 + np.sqrt(4 - 3 * h)))
        self.hydraulic_diameter_inner = 4 * self.area_inner / perimeter_inner

        super().__init__(k_g, self.hydraulic_diameter_inner / 2, self.hydraulic_diameter_outer / 2, 0.4, D_s)

    def _load_model(self, a, b) -> None:
        """
        This function loads the trained ANN models for the MuoviELLIPSE.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When the a and b do not match the product specifics
        """
        from GHEtool import FOLDER

        if np.isclose(a, 37e-3) and np.isclose(b, 26e-3):
            self._model_path = FOLDER.joinpath("VariableClasses/PipeData/ANN/MuoviELLIPSE32/borehole_ann.pt")
            self._x_scaler_path = FOLDER.joinpath("VariableClasses/PipeData/ANN/MuoviELLIPSE32/X_scaler.joblib")
            self._y_scaler_path = FOLDER.joinpath("VariableClasses/PipeData/ANN/MuoviELLIPSE32/y_scaler.joblib")

        elif np.isclose(a, 46e-3) and np.isclose(b, 33e-3):
            self._model_path = FOLDER.joinpath("VariableClasses/PipeData/ANN/MuoviELLIPSE40/borehole_ann.pt")
            self._x_scaler_path = FOLDER.joinpath("VariableClasses/PipeData/ANN/MuoviELLIPSE40/X_scaler.joblib")
            self._y_scaler_path = FOLDER.joinpath("VariableClasses/PipeData/ANN/MuoviELLIPSE40/y_scaler.joblib")

        elif np.isclose(a, 51e-3) and np.isclose(b, 37e-3):
            self._model_path = FOLDER.joinpath("VariableClasses/PipeData/ANN/MuoviELLIPSE45/borehole_ann.pt")
            self._x_scaler_path = FOLDER.joinpath("VariableClasses/PipeData/ANN/MuoviELLIPSE45/X_scaler.joblib")
            self._y_scaler_path = FOLDER.joinpath("VariableClasses/PipeData/ANN/MuoviELLIPSE45/y_scaler.joblib")

        elif np.isclose(a, 58e-3) and np.isclose(b, 41e-3):
            self._model_path = FOLDER.joinpath("VariableClasses/PipeData/ANN/MuoviELLIPSE50/borehole_ann.pt")
            self._x_scaler_path = FOLDER.joinpath("VariableClasses/PipeData/ANN/MuoviELLIPSE50/X_scaler.joblib")
            self._y_scaler_path = FOLDER.joinpath("VariableClasses/PipeData/ANN/MuoviELLIPSE50/y_scaler.joblib")

        elif np.isclose(a, 64e-3) and np.isclose(b, 45e-3):
            self._model_path = FOLDER.joinpath("VariableClasses/PipeData/ANN/MuoviELLIPSE55/borehole_ann.pt")
            self._x_scaler_path = FOLDER.joinpath("VariableClasses/PipeData/ANN/MuoviELLIPSE55/X_scaler.joblib")
            self._y_scaler_path = FOLDER.joinpath("VariableClasses/PipeData/ANN/MuoviELLIPSE55/y_scaler.joblib")

        elif np.isclose(a, 73e-3) and np.isclose(b, 52e-3):
            self._model_path = FOLDER.joinpath("VariableClasses/PipeData/ANN/MuoviELLIPSE63/borehole_ann.pt")
            self._x_scaler_path = FOLDER.joinpath("VariableClasses/PipeData/ANN/MuoviELLIPSE63/X_scaler.joblib")
            self._y_scaler_path = FOLDER.joinpath("VariableClasses/PipeData/ANN/MuoviELLIPSE63/y_scaler.joblib")

        else:
            raise ValueError(
                f"No ANN model available for ellipse dimensions a={a * 1000:.1f} mm, "
                f"b={b * 1000:.1f} mm."
            )

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

    def calculate_conductive_resistance(self, **kwargs) -> float:
        """
        This function calculates the pipe thermal conductive resistance.

        Returns
        -------
        float
            Conductive resistance [mK/W]

        Notes
        -----
        Assumes confocal inner and outer ellipses. Analogous to the circular
        ln(r_out/r_in)/(2*pi*k) formula, with r -> (a+b)/2.

        References
        ----------
        Ecsedi & Baksa (2023), "Steady-state heat conduction problems for
        non-homogeneous hollow elliptical two-dimensional domain",
        Annals of Faculty Engineering Hunedoara, Vol. XXI, Fasc. 1, pp. 129-134.
        Eq. (24).
        """
        R_p = np.log((self.a + self.b) / ((self.a - self.wall_thickness * 2) + (self.b - self.wall_thickness * 2))) / (
                2 * np.pi * self.k_p)
        return R_p

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
        .. [#Niklas] Niklas Hidman. (2026). Thermohydraulic performance evaluation of internally finned elliptical geothermal collector pipes
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

        raise NotImplementedError('The MuoviELLIPSE can only be simulated with the explicit methods.')

    def predict_Rb_Ra_series(self, r_b, spacing, R_fp, k_b, k_s):
        """
        Vectorized prediction of R_b and R_a based on the ANN-model.

        Parameters
        ----------
        Inputs can be float or array-like:
            r_b
            spacing
            R_fp
            k_b
            k_s

        Returns
        -------
        R_b, R_a : np.ndarray
            Same shape as broadcasted inputs.
        """
        model = EllipseANN()
        model.load_state_dict(torch.load(self._model_path, map_location="cpu"))
        model.eval()

        X_scaler = joblib.load(self._x_scaler_path)
        y_scaler = joblib.load(self._y_scaler_path)

        # Convert to arrays
        r_b = np.asarray(r_b)
        spacing = np.asarray(spacing)
        R_fp = np.asarray(R_fp)
        k_b = np.asarray(k_b)
        k_s = np.asarray(k_s)

        # Broadcast to common shape
        r_b, spacing, R_fp, k_b, k_s = np.broadcast_arrays(
            r_b, spacing, R_fp, k_b, k_s
        )

        shape = r_b.shape

        # Build ANN input matrix
        X = np.column_stack(
            [
                r_b.ravel(),
                spacing.ravel(),
                R_fp.ravel(),
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

    def explicit_model_borehole_resistance(self, fluid_data: _FluidData, flow_rate_data: _FlowData, k_s: float,
                                           borehole: gt.boreholes.Borehole, order: int = 1, R_p: float = None,
                                           **kwargs) -> float:
        """
        This function returns the effective borehole thermal resistance for the MuoviELLIPSE based on an explicit
        model (always second order). The borehole resistance is based on an artificial neural network that was
        trained on 10.000 different simulations for each design of the MuoviELLIPSE.

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
        if R_p is None:
            R_cond = self.calculate_conductive_resistance(**kwargs)
            R_conv = self.calculate_convective_resistance(flow_rate_data, fluid_data, **kwargs)

            R_p = R_cond + R_conv

        R_b, R_a = self.predict_Rb_Ra_series(borehole.r_b, self.D_s, R_p, self.k_g, k_s)

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

        def f_turbo(Re: float) -> float:
            """
            This function calculates the friction factor of the MuoviELLIPSE.

            Parameters
            ----------
            Re : float
                Reynolds number [-]

            Returns
            -------
            Friction factor : float
                Friction factor of the MuoviELLIPSE.
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
        return {
            'type': 'MuoviELLIPSE',
            'thickness [mm]': self.wall_thickness * 1000,
            'a [mm]': self.a * 1000,
            'b [mm]': self.b * 1000,
            'spacing [mm]': self.D_s * 1000,
            'k_g [W/(m·K)]': self.k_g,
        }
