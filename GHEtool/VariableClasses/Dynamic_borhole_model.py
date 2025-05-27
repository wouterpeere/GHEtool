import warnings
from enum import auto, IntEnum
from math import exp, log, pi, sqrt

from collections import namedtuple
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.linalg.lapack import dgtsv

import pygfunction as gt
from GHEtool.logger.ghe_logger import ghe_logger

class CellProps(IntEnum):
    R_IN = 0
    R_CENTER = auto()
    R_OUT = auto()
    K = auto()
    RHO_CP = auto()
    TEMP = auto()
    VOL = auto()


class DynamicsBH(object):
    """
    X. Xu and Jeffrey D. Spitler. 2006. 'Modeling of Vertical Ground Loop Heat
    Exchangers with Variable Convective Resistance and Thermal Mass of the
    Fluid.' in Proceedings of the 10th International Conference on Thermal
    Energy Storage-EcoStock. Pomona, NJ, May 31-June 2.
    """

    def __init__(self, time, gFunc, boreholes, alpha, ground_data, fluid_data, pipe_data, borefield, short_term_effects_parameters):

        print('in dynamic model')

        #loading all necessary variables and adding to self

        self.boreholes = boreholes
        self.ground_ghe = ground_data
        self.fluid_ghe = fluid_data
        self.pipes_ghe = pipe_data
        self.pipes_gt = gt.pipes
        self.short_term_effects_parameters = short_term_effects_parameters
        self.borefield = borefield
        self.gFunc = gFunc
        self.time = time

        self.g_lt = interp1d(self.time, self.gFunc)

        # The number of boreholes here is calculated for two things: (1) For a single borehole the fluid_factor should be set 
        # to 1, since no connections (except if the distance to the collector is very far and know) between boreholes are present
        # and therefore the only fluid capacity is the one in the borehole itself (2) To calculate the far field radius of the 
        # 1D numerical model. For a single borehole the far field radius is set to 10m, for a field the far field radius is
        # set to half of the distance between two boreholes. 

        # To do: Future development on above topics should include: (1) Calculating the length of the piping connection from the coordinates
        # maybe also include an option to give the piping from the closest borehole to the collector, or option to give coordinates 
        # of collector and function calculated al the piping including the pipes going to the collector (2) for not trivial (fixed)
        # distance between boreholes an 'average' borehole-to-borehole distance should be calculated to decide on the far field radius


        number_of_boreholes = len(self.boreholes)

        # Definition: Fluid factor takes into account the fluid inside of the system but outside of the boreholes
        if number_of_boreholes == 1:
            self.fluid_factor = 1
        else:
            self.fluid_factor = 2

        # Definition: number of pipes refers to single or double U pipe. Depending on this value a different equivalent borehole 
        # model (different equivalent radia and number of cells) is choosen to represent the borehole. 1 for single U tube, 2 for dubble U tube 
        # To do: extend method to coaxial pipes
        self.u_tube = self.pipes_ghe.number_of_pipes

        # Calculate the far field radius, which influences the number of ground cells
        # To do: only works for rectangular field, adjust for more general approaches (as discussed above)
        if number_of_boreholes == 0:
            ghe_logger.warning(f"Borefield should consist of at least one borehole")
        elif number_of_boreholes < 4:
            far_field_radius = 10
        else: 
            distance_between_boreholes = np.sqrt((self.boreholes[1].x - self.boreholes[0].x)**2 + (self.boreholes[1].y - self.boreholes[0].y)**2)
            far_field_radius = distance_between_boreholes/2

        print(f"far field radius used: {far_field_radius}")

        # Number of ground cells for 10m is set to 500 (Xu&Spitler 2006), scaling is introduced for far field radia smaller 
        # then 10m
        self.num_soil_cells = int(far_field_radius/10*500)

        # Reference temperature is now taken di
        #self.init_temp = self.ground_ghe.Tg
        self.init_temp = 0

        # Create a namedtuple type
        ShortTermEffectsParameters = namedtuple('ShortTermEffectsParameters', short_term_effects_parameters.keys())
        # Create an instance of the namedtuple
        short_term_parameters = ShortTermEffectsParameters(**short_term_effects_parameters)
        self.short_term_parameters = short_term_parameters

        self.factor_time = 50 # parameter to modify default final time 
        self.rho_cp_grout = self.short_term_parameters.rho_cp_grout  
        self.rho_cp_pipe = self.short_term_parameters.rho_cp_pipe  
        
        # Starting Rb, needs to be updated every iteration
        self.resist_bh_effective = self.borefield.Rb
               
        # "The one dimensional model has a fluid core, an equivalent convective
        # resistance layer, a tube layer, a grout layer and is surrounded by the
        # ground."
        if self.u_tube == 1:
        # cell numbers
            self.num_fluid_cells = 3
            self.num_conv_cells = 1
            self.num_pipe_cells = 4
            self.num_grout_cells = 27

        elif self.u_tube == 2:
            self.num_fluid_cells = 12
            self.num_conv_cells = 4
            self.num_pipe_cells = 16
            self.num_grout_cells = 18 #20
        else:
            ghe_logger.warning(f"Choose for single or double U-tube")


        self.num_cells = self.num_fluid_cells + self.num_conv_cells + self.num_pipe_cells
        self.num_cells += self.num_grout_cells + self.num_soil_cells

        self.bh_wall_idx = self.num_fluid_cells + self.num_conv_cells + self.num_pipe_cells + self.num_grout_cells

        # Geometry and grid procedure

        # far-field radius is set to half of the distance between two boreholes or 10m when a single borehole is used;
        # the soil region is represented by (500/10 * far-field radius) cells
      
        self.r_far_field = far_field_radius - self.boreholes[0].r_b

        # borehole radius is set to the actual radius of the borehole
        self.r_borehole = self.boreholes[0].r_b

        # pipe thickness
        self.thickness_pipe_actual = self.pipes_ghe.r_out - self.pipes_ghe.r_in

        # outer tube radius is set to sqrt(2) * r_p_o, tube region has 4 cells
        if self.u_tube == 1:
            # outer tube radius is set to sqrt(2) * r_p_o, tube region has 4 cells
            self.r_out_tube = sqrt(2) * self.pipes_ghe.r_out
            # inner tube radius is set to r_out_tube-t_p
            self.r_in_tube = self.r_out_tube - self.thickness_pipe_actual
            # r_in_convection is set to r_in_tube - 1/4 * t
            self.r_in_convection = self.r_in_tube - self.thickness_pipe_actual / 4.0
            # r_fluid is set to r_in_convection - 3/4 * t
            self.r_fluid = self.r_in_convection - (3.0 / 4.0 * self.thickness_pipe_actual)
            # Thicknesses of the grid regions
            self.thickness_soil_cell = (self.r_far_field - self.r_borehole) / self.num_soil_cells
            self.thickness_grout_cell = (self.r_borehole - self.r_out_tube) / self.num_grout_cells
            # pipe thickness is equivalent to original tube thickness
            self.thickness_conv_cell = (self.r_in_tube - self.r_in_convection) / self.num_conv_cells
            self.thickness_fluid_cell = (self.r_in_convection - self.r_fluid) / self.num_fluid_cells
            # Fixing error of thickness pipe cells, divide by number of pipe cells
            self.thickness_pipe_cell = self.thickness_pipe_actual / self.num_pipe_cells
            ghe_logger.info(f"Single U-tube cells defined for numerical model")

        else:
            # outer tube radius is set to sqrt(2) * r_p_o, tube region has 4 cells
            #self.r_out_tube = sqrt(2) * self.pipes_ghe.r_out + 2*self.thickness_pipe_actual
            self.r_out_tube = 2 * self.pipes_ghe.r_out 
            # inner tube radius is set to r_out_tube-t_p
            self.r_in_tube = self.r_out_tube - 2.0 * self.thickness_pipe_actual
            # r_in_convection is set to r_in_tube - 1/4 * t
            self.r_in_convection = self.r_in_tube - self.thickness_pipe_actual / 2.0
            # r_fluid is set to r_in_convection - 3/4 * t
            self.r_fluid = self.r_in_convection - (3.0 / 2.0 * self.thickness_pipe_actual)
            # Thicknesses of the grid regions
            self.thickness_soil_cell = (self.r_far_field - self.r_borehole) / self.num_soil_cells
            self.thickness_grout_cell = (self.r_borehole - self.r_out_tube) / self.num_grout_cells
            # pipe thickness is equivalent to original tube thickness
            self.thickness_conv_cell = (self.r_in_tube - self.r_in_convection) / self.num_conv_cells
            self.thickness_fluid_cell = (self.r_in_convection - self.r_fluid) / self.num_fluid_cells
            self.thickness_pipe_cell = (2*self.thickness_pipe_actual) / self.num_pipe_cells
            ghe_logger.info(f"Double U-tube cells defined for numerical model")

        # other
        self.g = np.array([], dtype=np.double)
        self.Tf = np.array([], dtype=np.double)
        self.Tb = np.array([], dtype=np.double)
        self.diff = np.array([], dtype=np.double)
        self.g_bhw = np.array([], dtype=np.double)
        self.lntts = np.array([], dtype=np.double)
        self.c_0 = 2.0 * pi * self.ground_ghe.k_s()
        self.t_s = self.boreholes[0].H ** 2 / (9 * self.ground_ghe.alpha())
        self.t_b = 5 * (self.boreholes[0].r_b) ** 2 / self.ground_ghe.alpha()  
        self.final_time = self.factor_time * self.t_b
        self.g_sts = None

    def partial_init(self):
        # TODO: unravel how to eliminate this.
        # - It was calling the full class ctor "self.__init__()" which is just plain wrong...
        # - Now we're calling a stripped down version with only the most essential
        #   variables which are required.
        # - This is here partially because equivalent boreholes are generated.

        soil_diffusivity = self.ground_ghe.k_s() / self.ground_ghe.volumetric_heat_capacity()  # kon k_s niet terugvinden dus soil.k genomen
        self.t_s = self.boreholes[0].H ** 2 / (
                    9 * self.ground_ghe.alpha())  # self.t_s = single_u_tube.b.H ** 2 / (9 * soil_diffusivity)
        self.calc_time_in_sec = max([self.t_s * exp(-8.6), 49.0 * 3600.0])

    def fill_radial_cell(self, radial_cell, resist_f_eq, resist_tg_eq):

        num_fluid_cells = self.num_fluid_cells
        num_conv_cells = self.num_conv_cells
        num_pipe_cells = self.num_pipe_cells
        num_grout_cells = self.num_grout_cells
        num_soil_cells = self.num_soil_cells

        cell_summation = 0

        # load fluid cells
        for idx in range(cell_summation, num_fluid_cells + cell_summation):
           
            inner_radius = self.r_fluid + idx * self.thickness_fluid_cell
            center_radius = inner_radius + self.thickness_fluid_cell / 2.0
            outer_radius = inner_radius + self.thickness_fluid_cell

            # The equivalent thermal mass of the fluid can be calculated from
            # equation (2)
            # pi (r_in_conv ** 2 - r_f **2) C_eq_f = 2pi r_p_in**2 * C_f
            rho_cp_eq = (self.fluid_factor * self.u_tube * 2.0
                         * (self.pipes_ghe.r_in ** 2)
                         * self.fluid_ghe.Cp * self.fluid_ghe.rho
                         ) / ((self.r_in_convection ** 2) - (self.r_fluid ** 2))

            k_eq = rho_cp_eq / self.fluid_ghe.Cp

            volume = pi * (outer_radius ** 2 - inner_radius ** 2)
            radial_cell[:, idx] = np.array(
                [
                    inner_radius,
                    center_radius,
                    outer_radius,
                    k_eq,
                    rho_cp_eq,
                    self.init_temp,
                    volume,
                ],
                dtype=np.double,
            )
        cell_summation += num_fluid_cells

        # TODO: verify whether errors are possible here and raise exception if needed
        # assert cell_summation == num_fluid_cells

        # load convection cells
        for idx in range(cell_summation, num_conv_cells + cell_summation):
            j = idx - cell_summation
            inner_radius = self.r_in_convection + j * self.thickness_conv_cell
            center_radius = inner_radius + self.thickness_conv_cell / 2.0
            outer_radius = inner_radius + self.thickness_conv_cell
            k_eq = log(self.r_in_tube / self.r_in_convection) / (2.0 * pi * resist_f_eq)
            rho_cp = 1.0
            volume = pi * (outer_radius ** 2 - inner_radius ** 2)
            radial_cell[:, idx] = np.array(
                [
                    inner_radius,
                    center_radius,
                    outer_radius,
                    k_eq,
                    rho_cp,
                    self.init_temp,
                    volume,
                ],
                dtype=np.double,
            )
        cell_summation += num_conv_cells

        # TODO: verify whether errors are possible here and raise exception if needed
        # assert cell_summation == (num_fluid_cells + num_conv_cells)

        # load pipe cells
        for idx in range(cell_summation, num_pipe_cells + cell_summation):
            j = idx - cell_summation
            inner_radius = self.r_in_tube + j * self.thickness_pipe_cell
            center_radius = inner_radius + self.thickness_pipe_cell / 2.0
            outer_radius = inner_radius + self.thickness_pipe_cell
            conductivity = log(self.r_borehole / self.r_in_tube) / (2.0 * pi * resist_tg_eq)
            # rho_cp = self.single_u_tube.pipe.rhoCp
            rho_cp = self.rho_cp_pipe
            volume = pi * (outer_radius ** 2 - inner_radius ** 2)
            radial_cell[:, idx] = np.array(
                [
                    inner_radius,
                    center_radius,
                    outer_radius,
                    conductivity,
                    rho_cp,
                    self.init_temp,
                    volume,
                ],
                dtype=np.double,
            )
        cell_summation += num_pipe_cells

        # TODO: verify whether errors are possible here and raise exception if needed
        # assert cell_summation == (num_fluid_cells + num_conv_cells + num_pipe_cells)

        # load grout cells
        for idx in range(cell_summation, num_grout_cells + cell_summation):
            j = idx - cell_summation
            inner_radius = self.r_out_tube + j * self.thickness_grout_cell
            center_radius = inner_radius + self.thickness_grout_cell / 2.0
            outer_radius = inner_radius + self.thickness_grout_cell
            conductivity = log(self.r_borehole / self.r_in_tube) / (2.0 * pi * resist_tg_eq)
            # rho_cp = self.single_u_tube.grout.rhoCp
            rho_cp = self.rho_cp_grout
            volume = pi * (outer_radius ** 2 - inner_radius ** 2)
            radial_cell[:, idx] = np.array(
                [
                    inner_radius,
                    center_radius,
                    outer_radius,
                    conductivity,
                    rho_cp,
                    self.init_temp,
                    volume,
                ],
                dtype=np.double,
            )
        cell_summation += num_grout_cells

        # TODO: verify whether errors are possible here and raise exception if needed
        # assert cell_summation == (num_fluid_cells + num_conv_cells + num_pipe_cells + num_grout_cells)

        # load soil cells
        for idx in range(cell_summation, num_soil_cells + cell_summation):
            j = idx - cell_summation
            inner_radius = self.r_borehole + j * self.thickness_soil_cell
            center_radius = inner_radius + self.thickness_soil_cell / 2.0
            outer_radius = inner_radius + self.thickness_soil_cell
            conductivity = self.ground_ghe.k_s()
            rho_cp = self.ground_ghe.volumetric_heat_capacity()
            volume = pi * (outer_radius ** 2 - inner_radius ** 2)
            radial_cell[:, idx] = np.array(
                [
                    inner_radius,
                    center_radius,
                    outer_radius,
                    conductivity,
                    rho_cp,
                    self.init_temp,
                    volume,
                ],
                dtype=np.double,
            )
        cell_summation += num_soil_cells

    def calc_sts_g_functions(self, final_time=None) -> tuple:
        """
        Compute short-term g-functions using a finite difference approach for radial heat conduction
        in the borehole.

        This method simulates transient heat transfer from the circulating fluid to the surrounding ground 
        through pipe walls and the borehole. It implements the cylindrical heat source model (Xu & Spitler)
        and solves a tri-diagonal matrix system at each time step to simulate the radial temperature distribution.

        Parameters:
            final_time (float, optional): The final simulation time in seconds. If not provided, uses `self.final_time`.

        Returns:
            tuple: Contains the following arrays/interpolators:
                - lntts (np.ndarray): Log time steps [s]
                - g (np.ndarray): Short-term g-function values
                - g_sts (interp1d): Interpolated short-term g-function
                - g_plot (np.ndarray): Alternative g-function used for plotting
                - qb (np.ndarray): Normalized heat flux to the ground
        """

        # === Initialization and geometry setup ===
        self.partial_init()
        self.m_flow_borehole = self.fluid_ghe.mfr
        final_time = self.final_time if final_time is None else final_time
        self.pipe_roughness = 1e-6
        self.bh = gt.boreholes
        self.H = self.boreholes[0].H
        print(f"Borehole length of current iteration is {self.H} m")
        self.r_b = self.r_borehole
        self.D = self.boreholes[0].D

        # === Convective heat transfer coefficient and resistances ===
        self.h_f = self.pipes_gt.convective_heat_transfer_coefficient_circular_pipe(
            self.m_flow_borehole,
            self.pipes_ghe.r_in,
            self.fluid_ghe.mu,
            self.fluid_ghe.rho,
            self.fluid_ghe.k_f,
            self.fluid_ghe.Cp,
            self.pipe_roughness
        )

        # Convective resistance inside pipe
        R_f = 1 / (self.h_f * 2 * pi * self.pipes_ghe.r_in)

        # Conduction resistance through the pipe wall
        R_p = self.pipes_gt.conduction_thermal_resistance_circular_pipe(
            self.pipes_ghe.r_in,
            self.pipes_ghe.r_out,
            self.pipes_ghe.k_p
        )

        # Borehole effective resistance (includes ground)
        self.resist_bh_effective = self.borefield.Rb

        # === Apply Xu & Spitler framework for equivalent resistances ===
        # Requiv,TG = RBH - Rf/2*u_tube
        resist_f_eq = R_f / 2 * self.u_tube
        resist_tg_eq = self.resist_bh_effective - resist_f_eq

        # === Build radial cell structure ===
        radial_cell = np.zeros((len(CellProps), self.num_cells), dtype=np.double)
        self.fill_radial_cell(radial_cell, resist_f_eq, resist_tg_eq)

        # === Characteristic time definitions ===
        self.t_b = 5 * (self.boreholes[0].r_b)**2 / self.ground_ghe.alpha()
        self.t_s = self.boreholes[0].H**2 / (9 * self.ground_ghe.alpha())

        # === Time loop variables ===
        g, g_plot, lntts, plottime = [], [], [], [2e-12]
        Tf, Tb, diff, qb, gFunc_CHS = [self.init_temp], [self.init_temp], [0], [], []
        time, time_step = 1e-12 - 120, 120
        heat_flux, init_temp = 1.0, self.init_temp

        # === Matrix setup for finite difference solver ===
        _dl = np.zeros(self.num_cells - 1)
        _d = np.zeros(self.num_cells)
        _du = np.zeros(self.num_cells - 1)
        _b = np.zeros(self.num_cells)

        _fe_1, _fe_2 = np.zeros(self.num_cells - 2), np.zeros(self.num_cells - 2)
        _ae = np.zeros_like(_fe_1)
        _fw_1, _fw_2, _aw, _ad = map(np.zeros_like, (_ae, _ae, _ae, _ae))

        _west_cell = radial_cell[:, 0:self.num_cells - 2]
        _center_cell = radial_cell[:, 1:self.num_cells - 1]
        _east_cell = radial_cell[:, 2:self.num_cells]

        # === Boundary condition coefficients ===
        fe_1 = log(radial_cell[CellProps.R_OUT, 0] / radial_cell[CellProps.R_CENTER, 0]) / (2 * pi * radial_cell[CellProps.K, 0])
        fe_2 = log(radial_cell[CellProps.R_CENTER, 1] / radial_cell[CellProps.R_IN, 1]) / (2 * pi * radial_cell[CellProps.K, 1])
        ae = 1 / (fe_1 + fe_2)
        ad = radial_cell[CellProps.RHO_CP, 0] * radial_cell[CellProps.VOL, 0] / time_step
        _d[0] = -ae / ad - 1
        _du[0] = ae / ad

        # === Define helper fill functions ===
        def fill_f1(fx_1, cell):
            fx_1[:] = np.log(cell[CellProps.R_OUT, :] / cell[CellProps.R_CENTER, :]) / (2 * pi * cell[CellProps.K, :])

        def fill_f2(fx_2, cell):
            fx_2[:] = np.log(cell[CellProps.R_CENTER, :] / cell[CellProps.R_IN, :]) / (2 * pi * cell[CellProps.K, :])

        # === Fill matrix coefficients ===
        fill_f1(_fe_1, _center_cell)
        fill_f2(_fe_2, _east_cell)
        _ae[:] = 1 / (_fe_1 + _fe_2)

        fill_f1(_fw_1, _west_cell)
        fill_f2(_fw_2, _center_cell)
        _aw[:] = -1 / (_fw_1 + _fw_2)

        _ad[:] = (_center_cell[CellProps.RHO_CP, :] * _center_cell[CellProps.VOL, :]) / time_step
        _dl[:self.num_cells - 2] = -_aw / _ad
        _d[1:self.num_cells - 1] = _aw / _ad - _ae / _ad - 1
        _du[1:self.num_cells - 1] = _ae / _ad

        # === Time loop ===
        while True:
            time += time_step

            _b[0] = -radial_cell[CellProps.TEMP, 0] - heat_flux / ad
            _dl[-1] = 0
            _d[-1] = 1
            _b[-1] = radial_cell[CellProps.TEMP, -1]
            _b[1:self.num_cells - 1] = -radial_cell[CellProps.TEMP, 1:self.num_cells - 1]

            dgtsv(_dl, _d, _du, _b, overwrite_b=1)
            radial_cell[CellProps.TEMP, :] = _b

            # g-function calculation
            g_val = self.c_0 * ((radial_cell[CellProps.TEMP, 0] - init_temp) / heat_flux - self.resist_bh_effective)
            g_plot_val = self.c_0 * ((radial_cell[CellProps.TEMP, 0] - init_temp) / heat_flux)
            q_val = 1 - (self.resist_bh_effective - (radial_cell[CellProps.TEMP, 0] - radial_cell[CellProps.TEMP, self.bh_wall_idx]))

            g.append(g_val)
            g_plot.append(g_plot_val)
            qb.append(q_val)
            gFunc_CHS.append(
                2 * pi * gt.heat_transfer.cylindrical_heat_source(
                    time, self.ground_ghe.alpha(), self.boreholes[0].r_b, self.boreholes[0].r_b
                )
            )

            if time > 3600:
                stop_crit = self.g_lt(time) - g_val
            else:
                stop_crit = 1

            Tf.append(radial_cell[CellProps.TEMP, 0])
            Tb.append(radial_cell[CellProps.TEMP, self.bh_wall_idx])
            diff.append(Tf[-1] - Tb[-1])
            lntts.append(time)
            plottime.append(time)

            if stop_crit < 0 or time >= (final_time - time_step):
                if stop_crit < 0:
                    ghe_logger.info(f"Perfect convergence with long-term g-function after {time / 3600:.1f} hours")
                else:
                    ghe_logger.info(
                        f"No perfect convergence; switch after {time / 3600:.1f} hours "
                        f"with g-function difference of {stop_crit:.5f}"
                    )
                break

        # === Plot g-functions ===
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        plt.tight_layout()
        ax1.plot(self.time, self.gFunc, c='b', marker='s', label='g_lt')
        ax1.plot(lntts, g, c='r', label='g_st')
        plt.legend(loc='upper left')

        # === Interpolation and downsampling ===
        num_intervals = 1000
        uniform_lntts_vals = np.linspace(lntts[0], lntts[-1], num_intervals)
        self.lntts = np.array(uniform_lntts_vals)

        g_tmp = interp1d(lntts, g)
        qb_tmp = interp1d(lntts, qb)
        g_plot_tmp = interp1d(lntts, g_plot)

        self.g = g_tmp(self.lntts)
        self.qb = qb_tmp(self.lntts)
        self.g_plot = g_plot_tmp(self.lntts)
        self.g_sts = interp1d(self.lntts, self.g)

        return self.lntts, self.g, self.g_sts, self.g_plot, self.qb
