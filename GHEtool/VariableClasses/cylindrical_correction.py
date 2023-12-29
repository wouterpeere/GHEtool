"""
This document contains the code to add the cylindrical correction to the pygfunction package,
as was documented here: https://github.com/MassimoCimmino/pygfunction/issues/269.
Note that this is a temporary solution, until issue #44 of pygfunction is solved.
"""

import pygfunction as gt
import numpy as np

from pygfunction.boreholes import Borehole, _EquivalentBorehole, find_duplicates
from pygfunction.heat_transfer import finite_line_source, finite_line_source_vectorized, \
    finite_line_source_equivalent_boreholes_vectorized
from pygfunction.networks import network_thermal_resistance

from scipy.integrate import quad_vec
from scipy.special import j0, j1, y0, y1

from scipy.interpolate import interp1d as interp1d
from time import perf_counter

# update pygfunction
def cylindrical_heat_source(
        time, alpha, r, r_b):
    """
    Evaluate the Cylindrical Heat Source (CHS) solution.
    This function uses a numerical quadrature to evaluate the CHS solution, as
    proposed by Carslaw and Jaeger [#CarslawJaeger1946]_. The CHS solution
    is given by:
        .. math::
            G(r,t) =
            \\frac{1}{\pi^2}
            \\int_{0}^{\\infty}
            \\frac{1}{s^2}
            \\frac{e^{-Fo s^2} - 1}{J_1^2(s) + Y_1^2(s)}
            [J_0(ps)Y_1(s) - J_1(s)Y_0(ps)]ds
    Parameters
    ----------
    time : float
        Value of time (in seconds) for which the FLS solution is evaluated.
    alpha : float
        Soil thermal diffusivity (in m2/s).
    r : float
        Radial distance from the borehole axis (in m).
    r_b : float
        Borehole radius (in m).
    Returns
    -------
    G : float
        Value of the CHS solution. The temperature at a distance r from
        borehole is:
        .. math:: \\Delta T(r,t) = T_g - \\frac{Q}{k_s H} G(r,t)
    Examples
    --------
    >>> G = gt.heat_transfer.cylindrical_heat_source(4*168*3600., 1.0e-6, 0.1, 0.075)
    G =
    References
    ----------
    .. [#CarslawJaeger1946] Carslaw, H.S., & Jaeger, J.C. (1946). The Laplace
       transformation: Problems on the cylinder and sphere, in: OU Press (Ed.),
       Conduction of heat in solids, Oxford University, Oxford, pp. 327-352.
    """
    # def _CHS(u, Fo, p):
    #     # Function to integrate
    #     CHS_integrand = ( 1. / (u**2 * np.pi**2) * (np.exp(-u**2 * Fo) - 1.0)
    #         / (j1(u)**2 + y1(u)**2) * (j0(p * u) * y1(u) - j1(u) * y0(p * u)) )
    #     return CHS_integrand
    CHS_integrand = lambda u: ( 1. / (u**2 * np.pi**2) * (np.exp(-u**2 * Fo) - 1.0)
        / (j1(u)**2 + y1(u)**2) * (j0(p * u) * y1(u) - j1(u) * y0(p * u)) )

    # Fourier number
    Fo = alpha * time / r_b**2
    # Normalized distance from borehole axis
    p = r / r_b
    # Lower bound of integration
    a = 0.
    # Upper bound of integration
    b = np.inf
    # Evaluate integral using Gauss-Kronrod
    G = quad_vec(CHS_integrand, a, b)[0]
    return G


def infinite_line_source(
        time, alpha, r):
    """
    Evaluate the Infinit Line Source (ILS) solution.
    This function uses the exponential integral to evaluate the ILS solution.
    The ILS solution is given by:
        .. math::
            I(r,t) = E_1(\\frac{r^2}{4 \\alpha t})
    Parameters
    ----------
    time : float
        Value of time (in seconds) for which the FLS solution is evaluated.
    alpha : float
        Soil thermal diffusivity (in m2/s).
    r : float
        Radial distance from the borehole axis (in m).
    borehole : Borehole object
        Borehole object of the borehole extracting heat.
    Returns
    -------
    I : float
        Value of the ILS solution. The temperature at a distance r from
        borehole is:
        .. math:: \\Delta T(r,t) = T_g - \\frac{Q}{4 \\pi k_s H} I(r,t)
    Examples
    --------
    >>> b = gt.boreholes.Borehole(H=150., D=4., r_b=0.075, x=0., y=0.)
    >>> G = gt.heat_transfer.infinite_line_source(4*168*3600., 1.0e-6, 0.1, b)
    I =
    """
    I = gt.utilities.exp1(r**2 / (4 * alpha * time))

    return I

def thermal_response_factors(self, time, alpha, kind='linear'):
    """
    Evaluate the segment-to-segment thermal response factors for all pairs
    of segments in the borefield at all time steps using the finite line
    source solution.
    This method returns a scipy.interpolate.interp1d object of the matrix
    of thermal response factors, containing a copy of the matrix accessible
    by h_ij.y[:nSources,:nSources,:nt+1]. The first index along the
    third axis corresponds to time t=0. The interp1d object can be used to
    obtain thermal response factors at any intermediate time by
    h_ij(t)[:nSources,:nSources].
    Parameters
    ----------
    time : float or array
        Values of time (in seconds) for which the g-function is evaluated.
    alpha : float
        Soil thermal diffusivity (in m2/s).
    kind : string, optional
        Interpolation method used for segment-to-segment thermal response
        factors. See documentation for scipy.interpolate.interp1d.
        Default is linear.
    Returns
    -------
    h_ij : interp1d
        interp1d object (scipy.interpolate) of the matrix of
        segment-to-segment thermal response factors.
    """
    if self.disp:
        print('Calculating segment to segment response factors ...',
              end='')
    # Number of time values
    nt = len(np.atleast_1d(time))
    # Initialize chrono
    tic = perf_counter()
    # Initialize segment-to-segment response factors
    h_ij = np.zeros((self.nSources, self.nSources, nt+1), dtype=self.dtype)
    segment_lengths = self.segment_lengths()
    # ---------------------------------------------------------------------
    # Segment-to-segment thermal response factors for borehole-to-borehole
    # thermal interactions
    # ---------------------------------------------------------------------
    # Groups correspond to unique pairs of borehole dimensions
    for pairs in self.borehole_to_borehole:
        i, j = pairs[0]
        # Prepare inputs to the FLS function
        dis, wDis = self._find_unique_distances(self.dis, pairs)
        H1, D1, H2, D2, i_pair, j_pair, k_pair = \
            self._map_axial_segment_pairs(i, j)
        H1 = H1.reshape(1, -1)
        H2 = H2.reshape(1, -1)
        D1 = D1.reshape(1, -1)
        D2 = D2.reshape(1, -1)
        N2 = np.array(
            [[self.boreholes[j].nBoreholes for (i, j) in pairs]]).T
        # Evaluate FLS at all time steps
        h = finite_line_source_equivalent_boreholes_vectorized(
            time, alpha, dis, wDis, H1, D1, H2, D2, N2)
        # Broadcast values to h_ij matrix
        for k, (i, j) in enumerate(pairs):
            i_segment = self._i0Segments[i] + i_pair
            j_segment = self._i0Segments[j] + j_pair
            h_ij[j_segment, i_segment, 1:] = h[k, k_pair, :]
            if not i == j:
                h_ij[i_segment, j_segment, 1:] = (h[k, k_pair, :].T \
                    * segment_lengths[j_segment]/segment_lengths[i_segment]).T
    # ---------------------------------------------------------------------
    # Segment-to-segment thermal response factors for same-borehole thermal
    # interactions
    # ---------------------------------------------------------------------
    # Groups correspond to unique borehole dimensions
    for group in self.borehole_to_self:
        # Index of first borehole in group
        i = group[0]
        # Find segment-to-segment similarities
        H1, D1, H2, D2, i_pair, j_pair, k_pair = \
            self._map_axial_segment_pairs(i, i)
        # Evaluate FLS at all time steps
        H1 = H1.reshape(1, -1)
        H2 = H2.reshape(1, -1)
        D1 = D1.reshape(1, -1)
        D2 = D2.reshape(1, -1)
        if self.cylindrical_correction:
            dis = 0.0005 * self.boreholes[i].H
        else:
            dis = self.boreholes[i].r_b
        h = finite_line_source_vectorized(
            time, alpha, dis, H1, D1, H2, D2,
            approximation=self.approximate_FLS, N=self.nFLS)
        # Broadcast values to h_ij matrix
        for i in group:
            i_segment = self._i0Segments[i] + i_pair
            j_segment = self._i0Segments[i] + j_pair
            h_ij[j_segment, i_segment, 1:] = \
                h_ij[j_segment, i_segment, 1:] + h[0, k_pair, :]

            if self.cylindrical_correction:
                r_b = self.boreholes[i].r_b
                ii_segment = j_segment[j_segment==i_segment]
                h_ils = infinite_line_source(time, alpha, dis)
                h_chs = cylindrical_heat_source(time, alpha, r_b, r_b)
                h_ij[ii_segment, ii_segment, 1:] = (
                    h_ij[ii_segment, ii_segment, 1:] + 2 * np.pi * h_chs - 0.5 * h_ils)
    # Return 2d array if time is a scalar
    if np.isscalar(time):
        h_ij = h_ij[:,:,1]
    # Interp1d object for thermal response factors
    h_ij = interp1d(np.hstack((0., time)), h_ij,
                    kind=kind, copy=True, axis=2)
    toc = perf_counter()
    if self.disp: print(f' {toc - tic:.3f} sec')
    return h_ij

def solve(self, time, alpha):
    """
    Build and solve the system of equations.
    Parameters
    ----------
    time : float or array
        Values of time (in seconds) for which the g-function is evaluated.
    alpha : float
        Soil thermal diffusivity (in m2/s).
    Returns
    -------
    gFunc : float or array
        Values of the g-function
    """
    # Number of time values
    self.time = time
    nt = len(self.time)
    # Evaluate threshold time for g-function linearization
    if self.linear_threshold is None:
        if self.cylindrical_correction:
            time_threshold = 0.
        else:
            time_threshold = self.r_b_max ** 2 / (25 * alpha)
    else:
        time_threshold = self.linear_threshold
    # Find the number of g-function values to be linearized
    p_long = np.searchsorted(self.time, time_threshold, side='right')
    if p_long > 0:
        time_long = np.concatenate([[time_threshold], self.time[p_long:]])
    else:
        time_long = self.time
    nt_long = len(time_long)
    # Initialize g-function
    gFunc = np.zeros(nt)
    # Initialize segment heat extraction rates
    if self.boundary_condition == 'UHTR':
        Q_b = 1
    else:
        Q_b = np.zeros((self.nSources, nt), dtype=self.dtype)
    if self.boundary_condition == 'UBWT':
        T_b = np.zeros(nt, dtype=self.dtype)
    else:
        T_b = np.zeros((self.nSources, nt), dtype=self.dtype)
    # Calculate segment to segment thermal response factors
    h_ij = self.thermal_response_factors(time_long, alpha, kind=self.kind)
    # Segment lengths
    H_b = self.segment_lengths()
    if self.boundary_condition == 'MIFT':
        Hb_individual = np.array([b.H for b in self.boreSegments], dtype=self.dtype)
    H_tot = np.sum(H_b)
    if self.disp: print('Building and solving the system of equations ...',
                        end='')
    # Initialize chrono
    tic = perf_counter()
    # Build and solve the system of equations at all times
    p0 = max(0, p_long - 1)
    for p in range(nt_long):
        if self.boundary_condition == 'UHTR':
            # Evaluate the g-function with uniform heat extraction along
            # boreholes
            # Thermal response factors evaluated at time t[p]
            h_dt = h_ij.y[:, :, p + 1]
            # Borehole wall temperatures are calculated by the sum of
            # contributions of all segments
            T_b[:, p + p0] = np.sum(h_dt, axis=1)
            # The g-function is the average of all borehole wall
            # temperatures
            gFunc[p + p0] = np.sum(T_b[:, p + p0] * H_b) / H_tot
        else:
            # Current thermal response factor matrix
            if p > 0:
                dt = time_long[p] - time_long[p - 1]
            else:
                dt = time_long[p]
            # Thermal response factors evaluated at t=dt
            h_dt = h_ij(dt)
            # Reconstructed load history
            Q_reconstructed = self.load_history_reconstruction(
                time_long[0:p + 1], Q_b[:, p0:p + p0 + 1])
            # Borehole wall temperature for zero heat extraction at
            # current step
            T_b0 = self.temporal_superposition(
                h_ij.y[:, :, 1:], Q_reconstructed)
            if self.boundary_condition == 'UBWT':
                # Evaluate the g-function with uniform borehole wall
                # temperature
                # ---------------------------------------------------------
                # Build a system of equation [A]*[X] = [B] for the
                # evaluation of the g-function. [A] is a coefficient
                # matrix, [X] = [Q_b,T_b] is a state space vector of the
                # borehole heat extraction rates and borehole wall
                # temperature (equal for all segments), [B] is a
                # coefficient vector.
                #
                # Spatial superposition: [T_b] = [T_b0] + [h_ij_dt]*[Q_b]
                # Energy conservation: sum([Q_b*Hb]) = sum([Hb])
                # ---------------------------------------------------------
                A = np.block([[h_dt, -np.ones((self.nSources, 1),
                                              dtype=self.dtype)],
                              [H_b, 0.]])
                B = np.hstack((-T_b0, H_tot))
                # Solve the system of equations
                X = np.linalg.solve(A, B)
                # Store calculated heat extraction rates
                Q_b[:, p + p0] = X[0:self.nSources]
                # The borehole wall temperatures are equal for all segments
                T_b[p + p0] = X[-1]
                gFunc[p + p0] = T_b[p + p0]
            elif self.boundary_condition == 'MIFT':
                # Evaluate the g-function with mixed inlet fluid
                # temperatures
                # ---------------------------------------------------------
                # Build a system of equation [A]*[X] = [B] for the
                # evaluation of the g-function. [A] is a coefficient
                # matrix, [X] = [Q_b,T_b,Tf_in] is a state space vector of
                # the borehole heat extraction rates, borehole wall
                # temperatures and inlet fluid temperature (into the bore
                # field), [B] is a coefficient vector.
                #
                # Spatial superposition: [T_b] = [T_b0] + [h_ij_dt]*[Q_b]
                # Heat transfer inside boreholes:
                # [Q_{b,i}] = [a_in]*[T_{f,in}] + [a_{b,i}]*[T_{b,i}]
                # Energy conservation: sum([Q_b*H_b]) = sum([H_b])
                # ---------------------------------------------------------
                a_in, a_b = self.network.coefficients_borehole_heat_extraction_rate(
                    self.network.m_flow_network,
                    self.network.cp_f,
                    self.nBoreSegments,
                    segment_ratios=self.segment_ratios)
                k_s = self.network.p[0].k_s
                A = np.block(
                    [[h_dt,
                      -np.eye(self.nSources, dtype=self.dtype),
                      np.zeros((self.nSources, 1), dtype=self.dtype)],
                     [np.eye(self.nSources, dtype=self.dtype),
                      a_b / (2.0 * np.pi * k_s * np.atleast_2d(Hb_individual).T),
                      a_in / (2.0 * np.pi * k_s * np.atleast_2d(Hb_individual).T)],
                     [H_b, np.zeros(self.nSources + 1, dtype=self.dtype)]])
                B = np.hstack(
                    (-T_b0,
                     np.zeros(self.nSources, dtype=self.dtype),
                     H_tot))
                # Solve the system of equations
                X = np.linalg.solve(A, B)
                # Store calculated heat extraction rates
                Q_b[:, p + p0] = X[0:self.nSources]
                T_b[:, p + p0] = X[self.nSources:2 * self.nSources]
                T_f_in = X[-1]
                # The gFunction is equal to the effective borehole wall
                # temperature
                # Outlet fluid temperature
                T_f_out = T_f_in - 2 * np.pi * self.network.p[0].k_s * H_tot / (
                    np.sum(self.network.m_flow_network * self.network.cp_f))
                # Average fluid temperature
                T_f = 0.5 * (T_f_in + T_f_out)
                # Borefield thermal resistance
                R_field = network_thermal_resistance(
                    self.network, self.network.m_flow_network,
                    self.network.cp_f)
                # Effective borehole wall temperature
                T_b_eff = T_f - 2 * np.pi * self.network.p[0].k_s * R_field
                gFunc[p + p0] = T_b_eff
    # Linearize g-function for times under threshold
    if p_long > 0:
        gFunc[:p_long] = gFunc[p_long - 1] * self.time[:p_long] / time_threshold
        if not self.boundary_condition == 'UHTR':
            Q_b[:, :p_long] = 1 + (Q_b[:, p_long - 1:p_long] - 1) * self.time[:p_long] / time_threshold
        if self.boundary_condition == 'UBWT':
            T_b[:p_long] = T_b[p_long - 1] * self.time[:p_long] / time_threshold
        else:
            T_b[:, :p_long] = T_b[:, p_long - 1:p_long] * self.time[:p_long] / time_threshold
    # Store temperature and heat extraction rate profiles
    if self.profiles:
        self.Q_b = Q_b
        self.T_b = T_b
    toc = perf_counter()
    if self.disp: print(f' {toc - tic:.3f} sec')
    return gFunc

def __init__(self, boreholes, network, time, boundary_condition,
             nSegments=8, segment_ratios=gt.utilities.segment_ratios,
             approximate_FLS=False, mQuad=11, nFLS=10,
             linear_threshold=None, cylindrical_correction=False,
             disp=False, profiles=False, kind='linear', dtype=np.double,
             **other_options):
    self.boreholes = boreholes
    self.network = network
    # Convert time to a 1d array
    self.time = np.atleast_1d(time).flatten()
    self.linear_threshold = linear_threshold
    self.cylindrical_correction = cylindrical_correction
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


def update_pygfunction() -> None:
    """
    This function updates pygfunction by adding the cylindrical correction methods to it.

    Returns
    -------
    None
    """
    gt.heat_transfer.cylindrical_heat_source = cylindrical_heat_source
    gt.heat_transfer.infinite_line_source = infinite_line_source
    gt.gfunction._Equivalent.thermal_response_factors = thermal_response_factors
    gt.gfunction._BaseSolver.solve = solve
    gt.gfunction._BaseSolver.__init__ = __init__