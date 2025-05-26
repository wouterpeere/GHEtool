import numpy as np
from scipy.interpolate import interp1d
from scipy.linalg.lapack import dgtsv
from math import pi, log, exp
import matplotlib.pyplot as plt
from enum import IntEnum

# Assumes existence of a logging system
import logging
ghe_logger = logging.getLogger(__name__)

# Enum to represent indices in the radial_cell array for better readability
class CellProps(IntEnum):
    R_IN = 0
    R_CENTER = 1
    R_OUT = 2
    K = 3
    RHO_CP = 4
    TEMP = 5
    VOL = 6

class GFunctionCalculator:
    print(">>> GFunctionCalculator module loaded <<<")

    def __init__(self, time, gFunc, boreholes, alpha, ground_data, fluid_data, pipe_data, borefield, short_term_parameters):
        print("✅ GFunctionCalculator initialized")
        self.time = time
        self.gFunc = gFunc
        self.boreholes = boreholes
        self.alpha = alpha
        self.ground_data = ground_data
        self.fluid_data = fluid_data
        self.pipe_data = pipe_data
        self.borefield = borefield
        self.short_term_parameters = short_term_parameters

    def partial_init(self):
        soil_diffusivity = self.ground_ghe.k_s() / self.ground_ghe.volumetric_heat_capacity()
        self.t_s = self.boreholes[0].H ** 2 / (9 * self.ground_ghe.alpha())
        self.calc_time_in_sec = max([self.t_s * exp(-8.6), 49.0 * 3600.0])

    def _populate_cells(self, radial_cell, idx_range, props):
        for idx in idx_range:
            j = idx - idx_range.start
            inner_radius = props['r_start'] + j * props['thickness']
            center_radius = inner_radius + props['thickness'] / 2.0
            outer_radius = inner_radius + props['thickness']
            volume = pi * (outer_radius ** 2 - inner_radius ** 2)

            # Get k_eq and rho_cp: use function if provided, else constant
            k_eq_func = props.get('k_eq_func')
            rho_cp_func = props.get('rho_cp_func')

            k_eq = k_eq_func(j) if k_eq_func else props['k']
            rho_cp = rho_cp_func(j) if rho_cp_func else props['rho_cp']

            radial_cell[:, idx] = np.array([
                inner_radius,
                center_radius,
                outer_radius,
                k_eq,
                rho_cp,
                self.init_temp,
                volume,
            ], dtype=np.double)


    def fill_radial_cell(self, radial_cell, resist_f_eq, resist_tg_eq):
        c = 0
        defs = [
            ('fluid', self.num_fluid_cells, {
                'r_start': self.r_fluid,
                'thickness': self.thickness_fluid_cell,
                'k_eq_func': lambda i: (
                    (self.fluid_factor * self.u_tube * 2.0 * (self.pipes_ghe.r_in ** 2) * self.fluid_ghe.Cp * self.fluid_ghe.rho)
                    / ((self.r_in_convection ** 2) - (self.r_fluid ** 2)) / self.fluid_ghe.Cp
                ),
                'rho_cp': (
                    self.fluid_factor * self.u_tube * 2.0 * (self.pipes_ghe.r_in ** 2) * self.fluid_ghe.Cp * self.fluid_ghe.rho
                ) / ((self.r_in_convection ** 2) - (self.r_fluid ** 2))
            }),
            ('convection', self.num_conv_cells, {
                'r_start': self.r_in_convection,
                'thickness': self.thickness_conv_cell,
                'k_eq_func': lambda i: log(self.r_in_tube / self.r_in_convection) / (2.0 * pi * resist_f_eq),
                'rho_cp': 1.0
            }),
            ('pipe', self.num_pipe_cells, {
                'r_start': self.r_in_tube,
                'thickness': self.thickness_pipe_cell,
                'k_eq_func': lambda i: log(self.r_borehole / self.r_in_tube) / (2.0 * pi * resist_tg_eq),
                'rho_cp': self.rho_cp_pipe
            }),
            ('grout', self.num_grout_cells, {
                'r_start': self.r_out_tube,
                'thickness': self.thickness_grout_cell,
                'k_eq_func': lambda i: log(self.r_borehole / self.r_in_tube) / (2.0 * pi * resist_tg_eq),
                'rho_cp': self.rho_cp_grout
            }),
            ('soil', self.num_soil_cells, {
                'r_start': self.r_borehole,
                'thickness': self.thickness_soil_cell,
                'k': self.ground_ghe.k_s(),
                'rho_cp': self.ground_ghe.volumetric_heat_capacity()
            }),
        ]

        for label, count, props in defs:
            self._populate_cells(radial_cell, range(c, c + count), props)
            c += count


    def _prepare_solver_coefficients(self, radial_cell, time_step):
        nc = self.num_cells
        _dl = np.zeros(nc - 1)
        _d = np.zeros(nc)
        _du = np.zeros(nc - 1)
        _b = np.zeros(nc)

        # Prepare coefficients for tridiagonal matrix system
        _fe_1 = np.zeros(nc - 2)
        _fe_2 = np.zeros_like(_fe_1)
        _ae = np.zeros_like(_fe_2)
        _fw_1 = np.zeros_like(_ae)
        _fw_2 = np.zeros_like(_fw_1)
        _aw = np.zeros_like(_fw_2)
        _ad = np.zeros_like(_aw)

        def fill_f1(fx_1, cell):
            fx_1[:] = np.log(cell[CellProps.R_OUT, :] / cell[CellProps.R_CENTER, :]) / (2.0 * pi * cell[CellProps.K, :])

        def fill_f2(fx_2, cell):
            fx_2[:] = np.log(cell[CellProps.R_CENTER, :] / cell[CellProps.R_IN, :]) / (2.0 * pi * cell[CellProps.K, :])

        # Vectorized setup
        _west = radial_cell[:, 0:nc - 2]
        _center = radial_cell[:, 1:nc - 1]
        _east = radial_cell[:, 2:nc]

        fill_f1(_fe_1, _center)
        fill_f2(_fe_2, _east)
        _ae[:] = 1.0 / (_fe_1 + _fe_2)

        fill_f1(_fw_1, _west)
        fill_f2(_fw_2, _center)
        _aw[:] = -1.0 / (_fw_1 + _fw_2)

        _ad[:] = (_center[CellProps.RHO_CP, :] * _center[CellProps.VOL, :] / time_step)

        _dl[0: nc - 2] = -_aw / _ad
        _d[1: nc - 1] = _aw / _ad - _ae / _ad - 1.0
        _du[1: nc - 1] = _ae / _ad

        return _dl, _d, _du, _b, _ad

    def calc_sts_g_functions(self, final_time=None):
        self.partial_init()
        self.m_flow_borehole = self.fluid_ghe.mfr
        final_time = self.final_time

        self.pipe_roughness = 1e-06
        self.H = self.boreholes[0].H
        self.r_b = self.r_borehole
        self.D = self.boreholes[0].D
        self.h_f = self.pipes_gt.convective_heat_transfer_coefficient_circular_pipe(
            self.m_flow_borehole,
            self.pipes_ghe.r_in,
            self.fluid_ghe.mu,
            self.fluid_ghe.rho,
            self.fluid_ghe.k_f,
            self.fluid_ghe.Cp,
            self.pipe_roughness
        )
        R_f = 1 / (self.h_f * 2 * pi * self.pipes_ghe.r_in)
        R_p = self.pipes_gt.conduction_thermal_resistance_circular_pipe(
            self.pipes_ghe.r_in, self.pipes_ghe.r_out, self.pipes_ghe.k_p)

        self.resist_bh_effective = self.borefield.Rb
        resist_f_eq = R_f / 2 * self.u_tube
        resist_tg_eq = self.resist_bh_effective - resist_f_eq

        radial_cell = np.zeros(shape=(len(CellProps), self.num_cells), dtype=np.double)
        self.fill_radial_cell(radial_cell, resist_f_eq, resist_tg_eq)

        heat_flux = 1.0
        init_temp = self.init_temp
        time_step = 120
        time = 1e-12 - time_step

        g, lntts, g_plot, qb = [], [], [], []
        Tf, Tb, diff, plottime = [init_temp], [init_temp], [0], [2e-12]

        _dl, _d, _du, _b, ad = self._prepare_solver_coefficients(radial_cell, time_step)

        while True:
            time += time_step
            _b[0] = -radial_cell[CellProps.TEMP, 0] - heat_flux / ad[0]
            _dl[-1] = 0.0
            _d[-1] = 1.0
            _b[-1] = radial_cell[CellProps.TEMP, -1]
            _b[1:-1] = -radial_cell[CellProps.TEMP, 1:-1]

            dgtsv(_dl, _d, _du, _b, overwrite_b=1)
            radial_cell[CellProps.TEMP, :] = _b

            g_val = self.c_0 * ((radial_cell[CellProps.TEMP, 0] - init_temp) / heat_flux - self.resist_bh_effective)
            g.append(g_val)
            g_plot.append(self.c_0 * ((radial_cell[CellProps.TEMP, 0] - init_temp) / heat_flux))
            qb.append(1 - (self.resist_bh_effective - (
                radial_cell[CellProps.TEMP, 0] - radial_cell[CellProps.TEMP, self.bh_wall_idx])))

            stop_crit = 1 if time <= 3600 else self.g_lt(time) - g_val
            if stop_crit < 0 or time >= (final_time - time_step):
                msg = "Perfect convergence" if stop_crit < 0 else "No perfect convergence"
                ghe_logger.info(f"{msg} after {time/3600:.2f} hours with g-function difference {stop_crit:.6f}")
                break

            Tf.append(radial_cell[CellProps.TEMP, 0])
            Tb.append(radial_cell[CellProps.TEMP, self.bh_wall_idx])
            diff.append(Tf[-1] - Tb[-1])
            lntts.append(time)
            plottime.append(time)

        fig, ax1 = plt.subplots()
        ax1.plot(self.time, self.gFunc, c='b', marker='s', label='g_lt')
        ax1.plot(lntts, g, c='r', label='g_st')
        plt.legend(loc='upper left')
        plt.tight_layout()

        g_interp = interp1d(lntts, g)
        g_plot_interp = interp1d(lntts, g_plot)
        qb_interp = interp1d(lntts, qb)

        uniform_lntts_vals = np.linspace(lntts[0], lntts[-1], 1000)

        self.lntts = np.array(uniform_lntts_vals)
        self.g = g_interp(uniform_lntts_vals)
        self.qb = qb_interp(uniform_lntts_vals)
        self.g_plot = g_plot_interp(uniform_lntts_vals)
        self.g_sts = interp1d(self.lntts, self.g)

        return self.lntts, self.g, self.g_sts, self.g_plot, self.qb
