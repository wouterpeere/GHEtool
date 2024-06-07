"""
This document contains the code to add the short-term dynamic effects to the pygfunction package,
as was descripted by Meertens (2024).
Note that this is a temporary solution, until the code will move to pygfunction.
"""

import pygfunction as gt
import numpy as np

from math import pi

from pygfunction.boreholes import Borehole, _EquivalentBorehole, find_duplicates
from pygfunction.heat_transfer import finite_line_source, finite_line_source_vectorized, \
    finite_line_source_equivalent_boreholes_vectorized
from pygfunction.networks import network_thermal_resistance

from scipy.integrate import quad_vec
from scipy.special import j0, j1, y0, y1

from scipy.interpolate import interp1d as interp1d
from time import perf_counter

#update pygfunction
def evaluate_g_function(self, time):
        """
        Evaluate the g-function.

        Parameters
        ----------
        time : float or array
            Values of time (in seconds) for which the g-function is evaluated.

        Returns
        -------
        gFunction : float or array
            Values of the g-function

        """
        time = np.maximum(np.atleast_1d(time), 0.)
        assert len(time) == 1 or np.all(time[:-1] <= time[1:]), \
            "Time values must be provided in increasing order."
        # Save time values
        self.time = time
        if self.solver.disp:
            print(60*'-')
            print(f"Calculating g-function for boundary condition : "
                  f"'{self.boundary_condition}'".center(60))
            print(60*'-')
        # Initialize chrono
        tic = perf_counter()

        # Evaluate g-function
        # When cylindrical correction is True, this correction on the g-function is done in the next line

        self.gFunc = self.solver.solve(time, self.alpha)

        self.gFunc_CHS = gt.heat_transfer.cylindrical_heat_source(self.time, self.alpha, self.boreholes[0].r_b,self.boreholes[0].r_b)
        self.gFunc_CHS = 2*np.pi*self.gFunc_CHS

        self.gFunc_ILS = gt.heat_transfer.infinite_line_source(self.time, self.alpha, self.boreholes[0].r_b)
        self.gFunc_ILS = -0.5*self.gFunc_ILS

        print('FLS+CC', self.gFunc)
        print('CHS', self.gFunc_CHS)
        print('ILS', self.gFunc_ILS)

        if self.solver.short_term_effects:
            self.gFunc = _ShortTermEffects(self, self.time, self.gFunc, self.boreholes, self.alpha, self.solver.ground_data,
                                           self.solver.fluid_data, self.solver.pipe_data, self.solver.borefield, self.solver.short_term_effects_parameters)
            toc = perf_counter()
            print('STE', self.gFunc)

        elif self.solver.short_term_effects_fbw:
            self.gFunc = _ShortTermEffectsfbw(self, self.time, self.gFunc, self.boreholes, self.alpha, self.solver.ground_data,
                                           self.solver.fluid_data, self.solver.pipe_data, self.solver.borefield, self.solver.short_term_effects_parameters)
            toc = perf_counter()
            print('STE_fbw', self.gFunc)
        else:
            toc = perf_counter()

        print('g after short T E', self.gFunc)

        if self.solver.disp:
            print(f'Total time for g-function evaluation: '
                  f'{toc - tic:.3f} sec')
            print(60*'-')
        return self.gFunc



def __init__(self, boreholes, network, time, boundary_condition,
             nSegments=8, segment_ratios=gt.utilities.segment_ratios,
             approximate_FLS=False, mQuad=11, nFLS=10,
             linear_threshold=None, cylindrical_correction=False, short_term_effects=True,
             short_term_effects_fbw = False, ground_data=None, fluid_data=None, pipe_data=None, borefield=None, 
             short_term_effects_parameters=None,
             disp=False, profiles=False, kind='linear', dtype=np.double,
             **other_options):
    self.boreholes = boreholes
    self.network = network
    # Convert time to a 1d array
    self.time = np.atleast_1d(time).flatten()
    self.linear_threshold = linear_threshold
    self.cylindrical_correction = cylindrical_correction
    self.short_term_effects = short_term_effects
    self.short_term_effects_fbw = short_term_effects_fbw
    self.short_term_effects_parameters = short_term_effects_parameters
    self.ground_data = ground_data
    self.fluid_data = fluid_data
    self.pipe_data = pipe_data
    self.borefield = borefield
    self.r_b_max = np.max([b.r_b for b in self.boreholes])
    self.boundary_condition = boundary_condition
    nBoreholes = len(self.boreholes)
    # Format number of segments and segment ratios
    if type(nSegments) is int:
        self.nBoreSegments = [nSegments] * nBoreholes
    else:
        self.nBoreSegments = nSegments
    if isinstance(segment_ratios, np.ndarray):
        segment_ratios = [segment_ratios] * nBoreholes
    elif segment_ratios is None:
        segment_ratios = [np.full(n, 1./n) for n in self.nBoreSegments]
    elif callable(segment_ratios):
        segment_ratios = [segment_ratios(n) for n in self.nBoreSegments]
    self.segment_ratios = segment_ratios
    # Shortcut for segment_ratios comparisons
    self._equal_segment_ratios = \
        (np.all(np.array(self.nBoreSegments, dtype=np.uint) == self.nBoreSegments[0])
         and np.all([np.allclose(segment_ratios, self.segment_ratios[0]) for segment_ratios in self.segment_ratios]))
    # Boreholes with a uniform discretization
    self._uniform_segment_ratios = [
        np.allclose(segment_ratios,
                    segment_ratios[0:1],
                    rtol=1e-6)
        for segment_ratios in self.segment_ratios]
    # Find indices of first and last segments along boreholes
    self._i0Segments = [sum(self.nBoreSegments[0:i])
                        for i in range(nBoreholes)]
    self._i1Segments = [sum(self.nBoreSegments[0:(i + 1)])
                        for i in range(nBoreholes)]
    self.approximate_FLS = approximate_FLS
    self.mQuad = mQuad
    self.nFLS = nFLS
    self.disp = disp
    self.profiles = profiles
    self.kind = kind
    self.dtype = dtype
    # Check the validity of inputs
    self._check_inputs()
    # Initialize the solver with solver-specific options
    self.nSources = self.initialize(**other_options)
    return


def _ShortTermEffects(self, time, gFunc, boreholes, alpha, ground_data, fluid_data, pipe_data, borefield, short_term_parameters):

    from .Dynamic_borhole_model import DynamicsBH

    dynamic_numerical = DynamicsBH(time, gFunc, boreholes, alpha, ground_data, fluid_data, pipe_data, borefield, short_term_parameters)

    dynamic_numerical.calc_sts_g_functions()

    g = combine_sts_lts(
        time,
        gFunc,
        dynamic_numerical.lntts,
        dynamic_numerical.g,
        dynamic_numerical.g_plot,
        boreholes, alpha,
    )

    return g

def combine_sts_lts(log_time_lts: list, g_lts: list, log_time_sts: list, g_sts: list, g_plot: list, boreholes, alpha) -> interp1d:
    # make sure the short time step doesn't overlap with the long time step
    H = boreholes[0].H
    ts = H ** 2 / (9. * alpha)  # Bore field characteristic time

    # log_time_sts: [-48.95425508 -47.6269381  -46.29962112 -44.972304 --> 30 FOUT!! STAAT NU OOK IN s
    # log_time_lts: [3.600000e+03 7.200000e+03 1.080000e+04 1.440000e+04 --> 76

    t_sts_in_s = []
    for k in range(0, len(log_time_sts)):
        t_sts_in_s.append(log_time_sts[k])

    # het noemt wel allemaal log, maar alles staat in s (nodig als input voor GHEtool)
    log_time_sts = t_sts_in_s
    max_log_time_sts = max(log_time_sts)
    min_log_time_lts = min(log_time_lts)

    if max_log_time_sts < min_log_time_lts:

        log_time = log_time_sts + log_time_lts
        g = g_sts + g_lts
    else:
        # find where to stop in sts
        i = 0
        value = max_log_time_sts
        while value >= log_time_lts[i]:
            i += 1

        g_tmp = interp1d(log_time_sts, g_sts)
        g_plot_tmp = interp1d(log_time_sts, g_plot)
        uniform_g_sts = g_tmp(log_time_lts[0:i])
        uniform_g_plot = g_plot_tmp(log_time_lts[0:i])
        log_time = log_time_lts
    

        dummy = []
        for b in range(0, len(uniform_g_sts)):
            dummy.append(uniform_g_sts[b])

        uniform_g_sts = dummy
   
        dummy = []
        for b in range(0, len(uniform_g_plot)):
            dummy.append(uniform_g_plot[b])

        uniform_g_plot = dummy

        dummy = []
        for b in range(0, len(g_lts)):
            dummy.append(g_lts[b])

        g_lts = dummy
       
        g = uniform_g_sts + g_lts[i:]
     

    return g

def _ShortTermEffectsfbw(self, time, gFunc, boreholes, alpha, ground_data, fluid_data, pipe_data, borefield, short_term_parameters):

    from .Dynamic_borhole_model import DynamicsBH

    dynamic_numerical = DynamicsBH(time, gFunc, boreholes, alpha, ground_data, fluid_data, pipe_data, borefield, short_term_parameters)

    dynamic_numerical.calc_sts_g_functions()

    g = combine_sts_lts_fbw(
        time,
        gFunc,
        dynamic_numerical.lntts,
        dynamic_numerical.g_comb,
        dynamic_numerical.qb,
        boreholes, alpha,
    )

    return g

def combine_sts_lts_fbw(log_time_lts: list, g_lts: list, log_time_sts: list, g_comb: list, qb: list, boreholes, alpha) -> interp1d:
    # make sure the short time step doesn't overlap with the long time step
    H = boreholes[0].H
    ts = H ** 2 / (9. * alpha)  # Bore field characteristic time
    print('in set nm timesteps')
    print('gcomb in set',g_comb)

    # log_time_sts: [-48.95425508 -47.6269381  -46.29962112 -44.972304 --> 30 FOUT!! STAAT NU OOK IN s
    # log_time_lts: [3.600000e+03 7.200000e+03 1.080000e+04 1.440000e+04 --> 76

    t_sts_in_s = []
    for k in range(0, len(log_time_sts)):
        t_sts_in_s.append(log_time_sts[k])

    print('time sts in s', t_sts_in_s)

    # het noemt wel allemaal log, maar alles staat in s (nodig als input voor GHEtool)
    log_time_sts = t_sts_in_s
    max_log_time_sts = max(log_time_sts)
    min_log_time_lts = min(log_time_lts)


    # find where to stop in sts
    i = 0
    value = max_log_time_sts
    while value >= log_time_lts[i]:
        i += 1

    g_tmp = interp1d(log_time_sts, g_comb)
    qb_tmp = interp1d(log_time_sts, qb)
    uniform_g_comb = g_tmp(log_time_lts[0:i])
    uniform_qb = qb_tmp(log_time_lts[0:i])

    print('log time dat van sts', log_time_lts[0:i])

    print('uniform g comb', uniform_g_comb)
    log_time = log_time_lts
    print('log time', log_time)
    print(len(log_time))

    dummy = []
    dummy2 =[]
    for b in range(0, len(uniform_g_comb)):
        dummy.append(uniform_g_comb[b])
        dummy2.append(uniform_qb[b])

    uniform_g_comb = dummy
    uniform_qb = dummy2
    print('uniform g sts na dummy list', uniform_g_comb)
    print('uniform qb sts na dummy2', uniform_qb)

    q_1 = [1] * len(g_lts)
    qb_tot = uniform_qb + q_1[i:]

    g_lts_new = []

    for k in range(0, len(qb_tot)):
        item = qb_tot[k] * g_lts[k]
        g_lts_new.append(item)

    print('g_lts oud', g_lts)
    print('g_lts_new', g_lts_new)

    g_0 = [0] * len(g_lts)
    g_comb = uniform_g_comb + g_0[i:]

    #g = g_lts + g_comb

    g_lts_new = np.array(g_lts_new)
    g = g_lts_new + g_comb

    print('g totaal klaar', g)
    print(len(g))
    print('lekker bezig')

    return g

def update_pygfunction_short_term_effects() -> None:
    """
    This function updates pygfunction by adding the cylindrical correction methods to it.

    Returns
    -------
    None
    """       
    gt.gfunction._ShortTermEffects = _ShortTermEffects
    gt.gfunction.gFunction.evaluate_g_function = evaluate_g_function
    gt.gfunction._BaseSolver.__init__ = __init__

    

