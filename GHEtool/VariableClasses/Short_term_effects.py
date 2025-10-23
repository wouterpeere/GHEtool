"""
This document contains the code to add the short-term dynamic effects to the pygfunction package,
as was descripted by Meertens (2024).
Note that this is a temporary solution, until the code will move to pygfunction.
"""

import pygfunction as gt
import numpy as np

from math import pi
import matplotlib.pyplot as plt

from pygfunction.boreholes import Borehole, _EquivalentBorehole, find_duplicates
from pygfunction.heat_transfer import finite_line_source, finite_line_source_vectorized, \
    finite_line_source_equivalent_boreholes_vectorized
from pygfunction.networks import network_thermal_resistance

from scipy.integrate import quad_vec
from scipy.special import j0, j1, y0, y1

from scipy.interpolate import interp1d as interp1d
from time import perf_counter
from .Dynamic_borhole_model import DynamicsBH


# update pygfunction
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
        print(60 * '-')
        print(f"Calculating g-function for boundary condition : "
              f"'{self.boundary_condition}'".center(60))
        print(60 * '-')
    # Initialize chrono
    tic = perf_counter()

    # Evaluate g-function
    # When cylindrical correction is True, this correction on the g-function is done in the next line
    self.gFunc = self.solver.solve(time, self.alpha)

    if self.solver.short_term_effects:
        self.gFunc = _ShortTermEffects(self, self.time, self.gFunc, self.boreholes, self.alpha, self.solver.ground_data,
                                       self.solver.fluid_data, self.solver.pipe_data, self.solver.borefield,
                                       self.solver.short_term_effects_parameters)
        toc = perf_counter()

    else:
        toc = perf_counter()

    if self.solver.disp:
        print(f'Total time for g-function evaluation: '
              f'{toc - tic:.3f} sec')
        print(60 * '-')
    return self.gFunc


def __init__(self, boreholes, network, time, boundary_condition,
             m_flow_borehole=None, m_flow_network=None, cp_f=None,
             nSegments=8, segment_ratios=gt.utilities.segment_ratios,
             approximate_FLS=False, mQuad=11, nFLS=10,
             linear_threshold=None, cylindrical_correction=False, short_term_effects=False,
             ground_data=None, fluid_data=None, pipe_data=None, borefield=None,
             short_term_effects_parameters=None,
             disp=False, profiles=False, kind='linear', dtype=np.double,
             **other_options
             ):
    self.boreholes = boreholes
    self.network = network
    # Convert time to a 1d array
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
        segment_ratios = [np.full(n, 1. / n) for n in self.nBoreSegments]
    elif callable(segment_ratios):
        segment_ratios = [segment_ratios(n) for n in self.nBoreSegments]
    self.segment_ratios = segment_ratios
    # Shortcut for segment_ratios comparisons
    self._equal_segment_ratios = \
        (np.all(np.array(self.nBoreSegments, dtype=np.uint) == self.nBoreSegments[0])
         and np.all([np.allclose(segment_ratios, self.segment_ratios[0]) for segment_ratios in
                     self.segment_ratios]))
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
    self.nMassFlow = 0
    self.m_flow_borehole = m_flow_borehole
    if self.m_flow_borehole is not None:
        if not self.m_flow_borehole.ndim == 1:
            self.nMassFlow = np.size(self.m_flow_borehole, axis=0)
        self.m_flow_borehole = np.atleast_2d(self.m_flow_borehole)
        self.m_flow = self.m_flow_borehole
    self.m_flow_network = m_flow_network
    if self.m_flow_network is not None:
        if not isinstance(self.m_flow_network, (np.floating, float)):
            self.nMassFlow = len(self.m_flow_network)
        self.m_flow_network = np.atleast_1d(self.m_flow_network)
        self.m_flow = self.m_flow_network
    self.cp_f = cp_f
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


def _ShortTermEffects(self, time, gFunc, boreholes, alpha, ground_data, fluid_data, pipe_data, borefield,
                      short_term_parameters):
    dynamic_numerical = DynamicsBH(time, gFunc, boreholes, alpha, ground_data, fluid_data, pipe_data, borefield,
                                   short_term_parameters)
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


def combine_sts_lts(time_lts: list, g_lts: list,
                    time_sts: list, g_sts: list,
                    g_plot: list, boreholes, alpha) -> list:
    """
    Combine short-term and long-term g-functions by aligning and merging time and g-values.

    Parameters
    ----------
    time_lts : list
        Time values (in seconds) for long-term simulation.
    g_lts : list
        g-function values corresponding to time_lts.
    time_sts : list
        Time values (in seconds) for short-term simulation.
    g_sts : list
        g-function values corresponding to time_sts.
    g_plot : list
        g-function values for plotting (same time points as time_sts).
    boreholes : list
        List of borehole objects. Assumes all have the same height `H`.
    alpha : float
        Ground thermal diffusivity (m²/s).

    Returns
    -------
    g : list
        Combined g-function values, aligned in time.
    """

    max_time_sts = max(time_sts)
    min_time_lts = min(time_lts)

    if max_time_sts < min_time_lts:
        # No overlap: simply concatenate
        return list(g_sts) + list(g_lts)

    # Overlap exists: find where to cut STS data
    i = 0
    while i < len(time_lts) and time_lts[i] <= max_time_sts:
        i += 1

    # Interpolate STS to match LTS time resolution up to index i
    g_sts_interp = interp1d(time_sts, g_sts, fill_value="extrapolate")
    g_sts_interp_vals = g_sts_interp(time_lts[:i])

    # Combine interpolated STS part with remaining LTS values
    combined_g = list(g_sts_interp_vals) + list(g_lts[i:])
    return combined_g


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
