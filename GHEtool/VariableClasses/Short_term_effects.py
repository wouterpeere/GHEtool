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
        self.gFunc = self.solver.solve(time, self.alpha)

        print('in new evaluat g function')

        print('self.short_term_effects', self.solver.short_term_effects)

        if self.solver.short_term_effects:
            self.gFunc = _ShortTermEffects(self, self.time, self.gFunc, self.boreholes, self.alpha, self.solver.ground_data,
                                           self.solver.fluid_data, self.solver.pipe_data, self.solver.borefield, self.solver.short_term_effects_parameters)
            toc = perf_counter()
        else:
            toc = perf_counter()

        if self.solver.disp:
            print(f'Total time for g-function evaluation: '
                  f'{toc - tic:.3f} sec')
            print(60*'-')
        return self.gFunc



def __init__(self, boreholes, network, time, boundary_condition,
             nSegments=8, segment_ratios=gt.utilities.segment_ratios,
             approximate_FLS=False, mQuad=11, nFLS=10,
             linear_threshold=None, cylindrical_correction=False, short_term_effects=True,
             ground_data=None, fluid_data=None, pipe_data=None, borefield=None, 
             short_term_effects_parameters=None,
             disp=False, profiles=False, kind='linear', dtype=np.double,
             **other_options):
    self.boreholes = boreholes
    self.network = network
    # Convert time to a 1d array

    print('new init is used in pygfunction')

    self.time = np.atleast_1d(time).flatten()
    self.linear_threshold = linear_threshold
    self.cylindrical_correction = cylindrical_correction
    self.short_term_effects = short_term_effects
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
    
    print('gFunc pygfunction', gFunc)

    print('in def _ShortTermEffects')

    from .Dynamic_borhole_model import DynamicsBH

    print('Dynamic_borehole_model imported')

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
    print('in combine sts lts')
    print('time sts', log_time_sts)
    print(' size log time sts', len(log_time_sts))
    print('time lst', log_time_lts)
    print('size log time lts', len(log_time_lts))
    print('g_lts', g_lts)
    print('g_sts', g_sts)
    print('stop')

    # log_time_sts: [-48.95425508 -47.6269381  -46.29962112 -44.972304 --> 30 FOUT!! STAAT NU OOK IN s
    # log_time_lts: [3.600000e+03 7.200000e+03 1.080000e+04 1.440000e+04 --> 76

    t_sts_in_s = []
    for k in range(0, len(log_time_sts)):
        t_sts_in_s.append(log_time_sts[k])

    print('time sts in s', t_sts_in_s)

    """
    dummy_list =[]
    for b in range(0,len(log_time_lts)):
        dummy_list.append(np.log(log_time_lts[b] / ts))
    log_time_lts = dummy_list

    dummy_list = []
    for b in range(0, len(g_lts)):
        dummy_list.append(g_lts[b])
    g_lts = dummy_list

    print('log time sts', log_time_sts)
    print(' size log time sts', len(log_time_sts))
    print('log time lst', log_time_lts)
    print('size log time lts', len(log_time_lts))
    """
    print('make sure the short time step does not overlap with the long time step, MAKING ONE LIST NOW')

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

        print('log time dat van sts', log_time_lts[0:i])

        print('uniform g sts', uniform_g_sts)
        log_time = log_time_lts
        print('log time', log_time)
        print(len(log_time))

        dummy = []
        for b in range(0, len(uniform_g_sts)):
            dummy.append(uniform_g_sts[b])

        uniform_g_sts = dummy
        print('uniform g sts na dummy list', uniform_g_sts)

        dummy = []
        for b in range(0, len(uniform_g_plot)):
            dummy.append(uniform_g_plot[b])

        uniform_g_plot = dummy

        dummy = []
        for b in range(0, len(g_lts)):
            dummy.append(g_lts[b])

        g_lts = dummy
        print('g_lts na dummy list', g_lts)

        g = uniform_g_sts + g_lts[i:]

        g_lst_plot = []
        g_lst_plot = [x + 0.165*2*pi*2.88 for x in g_lts]

        print('g totaal klaar', g)
        print(len(g))
        print('lekker bezig')

    print('log time ', log_time)
    print('size log time', len(log_time))
    print('g voor interp1d', g)
    print('size g voor interp1d', len(g))

    """
    # plot de short term and long term g function
    plt.rc('font', size=9)
    plt.rc('xtick', labelsize=9)
    plt.rc('ytick', labelsize=9)
    plt.rc('lines', lw=1.5, markersize=5.0)
    plt.rc('savefig', dpi=500)
    fig = plt.figure()

    ax = fig.add_subplot(111)
    ax.set_xlabel(r'$tijd$ [s] ', fontsize=18)
    ax.set_ylabel(r'$g$-functie', fontsize=18)

    plt.tight_layout()

    ax.plot(log_time_lts[0:i], uniform_g_plot)
    ax.plot(log_time_lts[0:25], g_lst_plot[0:25])
    #ax.plot(log_time_lts[0:11], g[0:11], '^')

    ax.legend([f'Numeriek model ',
               f'ELB model ',
               f'Gecombineerd model met 76 tijdstappen (voor interpolatie)'], fontsize=10)
    # ax.set_title(f'Field of {nBoreholes} boreholes')

    """
    """
    x = log_time_lts[0:i]
    y = uniform_g_sts
    print(x,y)
    plt.plot(x, y)

    x = log_time_lts
    y = g_lts
    print(x,y)
    plt.plot(x, y)
    plt.show()
    """
    return g

def update_pygfunction_short_term_effects() -> None:
    """
    This function updates pygfunction by adding the cylindrical correction methods to it.

    Returns
    -------
    None
    """
    print('IN update_pygfunctions_short_term_effects')
       
    gt.gfunction._ShortTermEffects = _ShortTermEffects
    print('short_term_effects succesfully added to pygfunction')
    gt.gfunction.gFunction.evaluate_g_function = evaluate_g_function
    print('evaluate gfunction succesfully replaced')
    gt.gfunction._BaseSolver.__init__ = __init__
    print('__init__ succesfully replaced')
    

