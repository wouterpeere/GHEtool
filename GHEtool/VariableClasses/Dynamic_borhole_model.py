import warnings
from enum import auto, IntEnum
from math import exp, log, pi, sqrt

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.linalg.lapack import dgtsv

import pygfunction as gt

print('test import done')

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

    """
    def foo(self):
        from GHEtool import PipeData
        bar()
        """

    def __init__(self, time, gFunc, boreholes, alpha, ground_data, fluid_data, pipe_data, borefield):

        print('initialize Numerical model')


        data_ground = None
        data_fluid = None
        data_pipe = None
        self.resist_bh_effective = None
        self.Rb_cst = None
        self.x = None
        self.u_tube = None
        self.fluid_factor = None
        self.rho_cp_grout = None
        self.rho_cp_pipe = None
        far_field_radius = None
        self.num_soil_cells = None
        

        from GHEtool.VariableClasses import GroundFluxTemperature, FluidData, PipeData, GroundData
        
        print('gFunc in RM', gFunc, len(gFunc))

        self.boreholes = boreholes
        self.ground_ghe = ground_data
        self.fluid_ghe = fluid_data
        self.pipes_ghe = pipe_data
        self.borefield = borefield
        self.pipes_gt = gt.pipes

        # borefield not ok

        # make function based on number of boreholes (1 or more) and half of the distance between boreholes
        distance_between_boreholes = 20  #aanpassen!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        far_field_radius = distance_between_boreholes/2
        self.num_soil_cells = int(far_field_radius/10*500)

        self.init_temp = self.ground_ghe.Tg

        self.fluid_factor = 2 # 2 by default, make function to calculate this
        self.x = 1 # parameter to modify final time 
        self.u_tube = 1 # 1 for single U tube, 2 for dubble U tube (not possible yet) 
        self.rho_cp_grout = 3800000.0  # Sandbox
        self.rho_cp_pipe = 1800000.0  # not aan te passen voor sandbox

        self.Rb_cst = 1 # 0 for false, 1 for true (rewrite such that get_Rb takes right Rb)
        self.resist_bh_effective = 0.165 # get this value with get_Rb
           
        print('data is loaded')

        # "The one dimensional model has a fluid core, an equivalent convective
        # resistance layer, a tube layer, a grout layer and is surrounded by the
        # ground."

        # cell numbers
        self.num_fluid_cells = 3
        self.num_conv_cells = 1
        self.num_pipe_cells = 4
        self.num_grout_cells = 27

        self.num_cells = self.num_fluid_cells + self.num_conv_cells + self.num_pipe_cells
        self.num_cells += self.num_grout_cells + self.num_soil_cells

        self.bh_wall_idx = self.num_fluid_cells + self.num_conv_cells + self.num_pipe_cells + self.num_grout_cells

        # Geometry and grid procedure

        # far-field radius is set to half of the distance between two boreholes or 10m when a single borehole is used;
        # the soil region is represented by (500/10 * far-field radius) cells
      
        self.r_far_field = far_field_radius - self.boreholes[0].r_b

        # borehole radius is set to the actual radius of the borehole
        self.r_borehole = self.boreholes[0].r_b

        # outer tube radius is set to sqrt(2) * r_p_o, tube region has 4 cells
        self.r_out_tube = sqrt(2 * self.u_tube) * self.pipes_ghe.r_out

        # inner tube radius is set to r_out_tube-t_p
        self.thickness_pipe = self.pipes_ghe.r_out - self.pipes_ghe.r_in
        self.r_in_tube = self.r_out_tube - self.thickness_pipe

        # r_in_convection is set to r_in_tube - 1/4 * t
        self.r_in_convection = self.r_in_tube - self.thickness_pipe / 4.0

        # r_fluid is set to r_in_convection - 3/4 * t
        self.r_fluid = self.r_in_convection - (3.0 / 4.0 * self.thickness_pipe)

        # Thicknesses of the grid regions
        self.thickness_soil = (self.r_far_field - self.r_borehole) / self.num_soil_cells
        self.thickness_grout = (self.r_borehole - self.r_out_tube) / self.num_grout_cells
        # pipe thickness is equivalent to original tube thickness
        self.thickness_conv = (self.r_in_tube - self.r_in_convection) / self.num_conv_cells
        self.thickness_fluid = (self.r_in_convection - self.r_fluid) / self.num_fluid_cells


        print('all parameters are set')

        # other
        self.g = np.array([], dtype=np.double)
        self.Tf = np.array([], dtype=np.double)
        self.Tb = np.array([], dtype=np.double)
        self.diff = np.array([], dtype=np.double)
        self.g_bhw = np.array([], dtype=np.double)
        self.lntts = np.array([], dtype=np.double)
        self.c_0 = 2.0 * pi * self.ground_ghe.k_s()
        soil_diffusivity = self.ground_ghe.k_s() / (self.ground_ghe.volumetric_heat_capacity())  # = alpha
        self.t_s = self.boreholes[0].H ** 2 / (9 * self.ground_ghe.alpha())
        # default is at least 49 hours, or up to -8.6 log time
        self.calc_time_in_sec = max([self.t_s * exp(-8.6), 49.0 * 3600.0])

        print('ts charact time', self.t_s)
        print('ts * exp ', self.t_s * exp(-8.6))

        self.t_b = 5 * (self.boreholes[0].r_b) ** 2 / self.ground_ghe.alpha()
        print('t_b time vanaf wanneer stationaire benadering mag', self.t_b)
        self.final_time = self.x * self.t_b
        #self.final_time = 3601
        print('final time', self.final_time)
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

    def fill_radial_cell(self, radial_cell, resist_p_eq, resist_f_eq, resist_tg_eq):

        num_fluid_cells = self.num_fluid_cells
        num_conv_cells = self.num_conv_cells
        num_pipe_cells = self.num_pipe_cells
        num_grout_cells = self.num_grout_cells
        num_soil_cells = self.num_soil_cells

        cell_summation = 0

        # load fluid cells
        for idx in range(cell_summation, num_fluid_cells + cell_summation):
            center_radius = self.r_fluid + idx * self.thickness_fluid

            if idx == 0:
                inner_radius = center_radius
            else:
                inner_radius = center_radius - self.thickness_fluid / 2.0

            outer_radius = center_radius + self.thickness_fluid / 2.0

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
            inner_radius = self.r_in_convection + j * self.thickness_conv
            center_radius = inner_radius + self.thickness_conv / 2.0
            outer_radius = inner_radius + self.thickness_conv
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
            inner_radius = self.r_in_tube + j * self.thickness_pipe
            center_radius = inner_radius + self.thickness_pipe / 2.0
            outer_radius = inner_radius + self.thickness_pipe
            conductivity = log(self.r_borehole / self.r_in_tube) / (2.0 * pi * resist_p_eq)
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
            inner_radius = self.r_out_tube + j * self.thickness_grout
            center_radius = inner_radius + self.thickness_grout / 2.0
            outer_radius = inner_radius + self.thickness_grout
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
            inner_radius = self.r_borehole + j * self.thickness_soil
            center_radius = inner_radius + self.thickness_soil / 2.0
            outer_radius = inner_radius + self.thickness_soil
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
        print('in calc sts g functions')

        self.partial_init()
        self.m_flow_borehole = self.fluid_ghe.mfr
        final_time = self.final_time

        self.pipe_roughness = 1e-06
        self.bh = gt.boreholes
        self.H = self.boreholes[0].H
        self.r_b = self.r_borehole
        self.D = self.boreholes[0].D
        borehole = self.bh.Borehole(self.H, self.D, self.r_b, 0, 0)
        self.h_f = self.pipes_gt.convective_heat_transfer_coefficient_circular_pipe(self.m_flow_borehole,
                                                                                    self.pipes_ghe.r_in,
                                                                                    self.fluid_ghe.mu,
                                                                                    self.fluid_ghe.rho,
                                                                                    self.fluid_ghe.k_f,
                                                                                    self.fluid_ghe.Cp,
                                                                                    self.pipe_roughness)
        R_f = 1 / (self.h_f * 2 * pi * self.pipes_ghe.r_in)
        R_p = self.pipes_gt.conduction_thermal_resistance_circular_pipe(self.pipes_ghe.r_in, self.pipes_ghe.r_out,
                                                                        self.pipes_ghe.k_p)

        # wanneer Rb niet gekend is, maar dan moet je dit model niet gebruiken eigenlijk
        if self.Rb_cst == 0:

            if self.u_tube == 2:
                pipe = self.tubes_ghe.MultipleUTube(self.pipes_ghe.pos, self.pipes_ghe.r_in, self.pipes_ghe.r_out,
                                         borehole, self.ground_ghe.k_s(), self.pipes_ghe.k_g,
                                         R_p + R_f, 2)

                self.resist_bh_effective = pipe.effective_borehole_thermal_resistance(self.m_flow_borehole, self.fluid_ghe.Cp)

            elif self.u_tube == 1:
                pipe = self.tubes_ghe.SingleUTube(self.pipes_ghe.pos, self.pipes_ghe.r_in, self.pipes_ghe.r_out,
                                         borehole, self.ground_ghe.k_s(), self.pipes_ghe.k_g,
                                         R_p + R_f, 2)

                self.resist_bh_effective = pipe.effective_borehole_thermal_resistance(self.m_flow_borehole, self.fluid_ghe.Cp)

        else:
            #self.resist_bh_effective = self.ground_ghe.Rb
            lone = 22

        print('Rb* in NM',self.resist_bh_effective)

        resist_f_eq = R_f / 2
        resist_p_eq = R_p / 2
        resist_tg_eq = self.resist_bh_effective - resist_f_eq

        print('resist_f_eq', resist_f_eq)
        print('resist_p_eq', resist_p_eq)
        print('resist_tg_eq', resist_tg_eq)

        # Pass radial cell by reference and fill here so that it can be
        # destroyed when this method returns
        radial_cell = np.zeros(shape=(len(CellProps), self.num_cells), dtype=np.double)
        self.fill_radial_cell(radial_cell, resist_p_eq, resist_f_eq, resist_tg_eq)

        self.t_b = 5 * (self.boreholes[0].r_b) ** 2 / self.ground_ghe.alpha()

        final_time = self.final_time
        print('final time t_b in s', final_time)

        self.t_s = self.boreholes[0].H ** 2 / (9 * self.ground_ghe.alpha())
        print('final time lntts', log(final_time / self.t_s))

        g = []
        g_bhw = []
        g_comb = []
        g_plot = []
        lntts = []
        plottime = [2e-12]
        Tf = [self.init_temp]
        Tb = [self.init_temp]
        diff = [0]
        qb=[]

        _dl = np.zeros(self.num_cells - 1)
        _d = np.zeros(self.num_cells)
        _du = np.zeros(self.num_cells - 1)
        _b = np.zeros(self.num_cells)

        heat_flux = 1.0
        init_temp = self.init_temp

        time = 1e-12 - 120
        time_step = 120

        _fe_1 = np.zeros(shape=(self.num_cells - 2), dtype=np.double)
        _fe_2 = np.zeros_like(_fe_1)
        _ae = np.zeros_like(_fe_2)
        _fw_1 = np.zeros_like(_ae)
        _fw_2 = np.zeros_like(_fw_1)
        _aw = np.zeros_like(_fw_2)
        _ad = np.zeros_like(_aw)

        _west_cell = radial_cell[:, 0: self.num_cells - 2]
        _center_cell = radial_cell[:, 1: self.num_cells - 1]
        _east_cell = radial_cell[:, 2: self.num_cells - 0]

        fe_1 = log(radial_cell[CellProps.R_OUT, 0] / radial_cell[CellProps.R_CENTER, 0])
        fe_1 /= (2.0 * pi * radial_cell[CellProps.K, 0])

        fe_2 = log(radial_cell[CellProps.R_CENTER, 1] / radial_cell[CellProps.R_IN, 1])
        fe_2 /= (2.0 * pi * radial_cell[CellProps.K, 1])

        ae = 1 / (fe_1 + fe_2)
        ad = radial_cell[CellProps.RHO_CP, 0] * radial_cell[CellProps.VOL, 0] / time_step
        _d[0] = -ae / ad - 1
        _du[0] = ae / ad

        def fill_f1(fx_1, cell):
            fx_1[:] = np.log(cell[CellProps.R_OUT, :] / cell[CellProps.R_CENTER, :]) / (2.0 * pi * cell[CellProps.K, :])

        def fill_f2(fx_2, cell):
            fx_2[:] = np.log(cell[CellProps.R_CENTER, :] / cell[CellProps.R_IN, :]) / (2.0 * pi * cell[CellProps.K, :])

        fill_f1(_fe_1, _center_cell)
        fill_f2(_fe_2, _east_cell)
        _ae[:] = 1.0 / (_fe_1 + _fe_2)

        fill_f1(_fw_1, _west_cell)
        fill_f2(_fw_2, _center_cell)
        _aw[:] = -1.0 / (_fw_1 + _fw_2)

        _ad[:] = (_center_cell[CellProps.RHO_CP, :] * _center_cell[CellProps.VOL, :] / time_step)
        _dl[0: self.num_cells - 2] = -_aw / _ad
        _d[1: self.num_cells - 1] = _aw / _ad - _ae / _ad - 1.0
        _du[1: self.num_cells - 1] = _ae / _ad

        while True:

            time += time_step

            # For the idx == 0 case:

            _b[0] = -radial_cell[CellProps.TEMP, 0] - heat_flux / ad

            # For the idx == n-1 case

            _dl[self.num_cells - 2] = 0.0
            _d[self.num_cells - 1] = 1.0
            _b[self.num_cells - 1] = radial_cell[CellProps.TEMP, self.num_cells - 1]

            # Now handle the 1 to n-2 cases with numpy slicing and vectorization
            _b[1: self.num_cells - 1] = -radial_cell[CellProps.TEMP, 1: self.num_cells - 1]

            # Tri-diagonal matrix solver
            # High level interface to LAPACK routine
            # https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.lapack.dgtsv.html#scipy.linalg.lapack.dgtsv
            dgtsv(_dl, _d, _du, _b, overwrite_b=1)  # TODO: Do we really need lapack just to do a TDMA solution?

            radial_cell[CellProps.TEMP, :] = _b

            # compute standard g-functions
            g.append(self.c_0 * ((radial_cell[CellProps.TEMP, 0] - init_temp) / heat_flux - self.resist_bh_effective))

            g_comb.append(self.c_0 * ((radial_cell[CellProps.TEMP, 0] - radial_cell[CellProps.TEMP, self.bh_wall_idx]) / heat_flux - self.resist_bh_effective))

            g_plot.append(self.c_0 * ((radial_cell[CellProps.TEMP, 0] - init_temp) / heat_flux))


            qb.append(1- (self.resist_bh_effective - (radial_cell[CellProps.TEMP, 0]-radial_cell[CellProps.TEMP, self.bh_wall_idx])))

            print(qb)

            print('f1', radial_cell[CellProps.TEMP, 0], 'f2', radial_cell[CellProps.TEMP, 1], 'f3', radial_cell[CellProps.TEMP, 2], 'c1', radial_cell[CellProps.TEMP, 3], 'time', time)
            #print('idx -1 ', radial_cell[CellProps.TEMP, self.bh_wall_idx - 1], 'idx bhw', radial_cell[CellProps.TEMP,self.bh_wall_idx], 'idx bhw + 1', radial_cell[CellProps.TEMP, self.bh_wall_idx + 1], 'time', time)

            T0 = radial_cell[CellProps.TEMP, 0]
            TBH = radial_cell[CellProps.TEMP, self.bh_wall_idx]
            d= T0-TBH

            Tf.append(T0)
            Tb.append(TBH)
            diff.append(d)

            # compute g-functions at bh wall
            bh_wall_temp = radial_cell[CellProps.TEMP, self.bh_wall_idx]

            #g_bhw.append(self.c_0 * ((bh_wall_temp - init_temp) / heat_flux))

            lntts.append(time)

            plottime.append(time)

            """
            if d >= resist_bh_effective:
                print('Tf - Tb heeft Rb* bereikt')
                break
            """
            if time >= final_time - time_step:
                print('in time if')
                print(final_time)
                break


        # plot de short term and long term g function
        plt.rc('font', size=9)
        plt.rc('xtick', labelsize=9)
        plt.rc('ytick', labelsize=9)
        plt.rc('lines', lw=1.5, markersize=5.0)
        plt.rc('savefig', dpi=500)
        fig = plt.figure()

        ax = fig.add_subplot(111)
        ax.set_xlabel(r'$tijd$ [s] ', fontsize=18)
        #ax.set_ylabel(r'$|T_f - T_b|$', fontsize=18)

        plt.tight_layout()

        dummy = []
        for i in range(0,len(plottime)):
            dummy.append(0.09)

        #ax.plot(plottime, Tf)
        #ax.plot(plottime, Tb)
        ax.plot(plottime, diff)
        ax.plot(plottime, dummy)

        """
        #ax.legend([f'$T_f$', f'$T_b$'], fontsize=10)
        ax.legend([ f'$|T_f - T_b|$', f'$R_b^*$'], fontsize=20)

        # plot de short term and long term g function
        plt.rc('font', size=9)
        plt.rc('xtick', labelsize=9)
        plt.rc('ytick', labelsize=9)
        plt.rc('lines', lw=1.5, markersize=5.0)
        plt.rc('savefig', dpi=500)
        fig = plt.figure()

        ax = fig.add_subplot(111)
        ax.set_xlabel(r'$tijd$ [s] ', fontsize=18)
        ax.set_ylabel(r'g-functie', fontsize=18)
        plt.tight_layout()
        ax.plot(lntts, g_plot)
        """

        # quickly chop down the total values to a more manageable set
        num_intervals = int(self.x * 30)
        g_tmp = interp1d(lntts, g)


        uniform_lntts_vals = np.linspace(lntts[0], lntts[-1], num_intervals)
        uniform_g_vals = g_tmp(uniform_lntts_vals)

        #g_bhw_tmp = interp1d(lntts, g_bhw)
        g_comb_tmp = interp1d(lntts,g_comb)
        qb_tmp =interp1d(lntts,qb)
        g_plot_tmp = interp1d(lntts, g_plot)

        #uniform_g_bhw_vals = g_bhw_tmp(uniform_lntts_vals)
        uniform_g_comb_vals = g_comb_tmp(uniform_lntts_vals)
        uniform_qb_vals = qb_tmp(uniform_lntts_vals)
        uniform_g_plot_vals = g_plot_tmp(uniform_lntts_vals)

        # set the final arrays and interpolator objects
        self.lntts = np.array(uniform_lntts_vals)
        self.g = np.array(uniform_g_vals)
        #self.g_bhw = np.array(uniform_g_bhw_vals)
        self.g_comb = np.array(uniform_g_comb_vals)
        self.qb = np.array(uniform_qb_vals)
        self.g_sts = interp1d(self.lntts, self.g)
        self.g_plot = np.array(uniform_g_plot_vals)

        print('lntts', self.lntts)
        print('g', self.g)
        print('g_bhw', self.g_bhw)
        print('g_sts', self.g_sts)
        print('g_comb',self.g_comb)
        print('qb', self.qb)

        return self.lntts, self.g, self.g_sts, self.g_comb, self.g_plot, self.qb