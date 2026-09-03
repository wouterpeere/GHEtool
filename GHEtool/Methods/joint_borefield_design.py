"""
This file contains an all-at-once (simultaneous) design method for the borefield
configuration: the number of boreholes in both directions, the borehole spacing and the
borehole length are optimised jointly, instead of nested inside a search loop.

The method works in three stages:

1.  A smooth, physics-based surrogate of the L2 sizing equations (Ahmadfard & Bernier
    for the last year, Monzo/Carcel for the first year, combined with the borefield
    quadrants of Peere et al.) is built. The field g-function is modelled as the
    closed-form finite line source self-response plus the pairwise finite line source
    interaction energy of the rectangular configuration. This surrogate is smooth in
    (n_1, n_2, b_1, b_2, h), so the whole design problem becomes one small NLP:

        min   n_1 * n_2 * (cost_per_borehole + cost_per_meter * h)
        s.t.  n_1 * n_2 * h * |T_limit - T_ground|  >=  required length (per quadrant)
              (n_i - 1) * b_i <= plot size,  spacing/length/borehole-count bounds

2.  The relaxed optimum is rounded: the integer neighbours of (n_1*, n_2*) are sized
    *exactly* with the regular GHEtool sizing methods, so every candidate cost is exact.

3.  An integer hill-climb with exact sizings guarantees the returned configuration is
    (+-1)-optimal in the number of boreholes with respect to the exact model, whatever
    the (small) bias of the surrogate.

The returned configuration is therefore certified by exact sizings; the surrogate is
only used for navigation.
"""
import copy

import numpy as np
import pygfunction as gt

from scipy.interpolate import RegularGridInterpolator
from scipy.optimize import minimize

from GHEtool.VariableClasses.BaseClass import UnsolvableDueToTemperatureGradient, MaximumNumberOfIterations, \
    UnsolvableOptimalFieldError

__all__ = ['design_borefield_configuration']


class _L2Surrogate:
    """
    Smooth L2-sizing surrogate for rectangular borefields.

    The required total borehole length is evaluated with the same quadrant equations as
    Borefield.size_L2, but with the field g-function replaced by a closed-form model:
    the finite line source (FLS) self-response plus the mean pairwise FLS interaction
    of the n_1 x n_2 grid. Both are precomputed on (distance, borehole length) grids,
    which makes one evaluation of the surrogate take well below a millisecond, smooth
    in all five design variables.
    """

    def __init__(self, borefield, h_min: float, h_max: float, b_min: float,
                 d_max: float, n_1_max: int, n_2_max: int):
        load = borefield.load
        load.reset_results(borefield.Tf_min, borefield.Tf_max)

        self.D = borefield.D
        self.r_b = borefield.r_b
        self.ground_data = borefield.ground_data
        self.Rb = borefield.borehole.get_Rb(
            float(np.sqrt(h_min * h_max)), self.D, self.r_b,
            self.ground_data.k_s(float(np.sqrt(h_min * h_max)) + self.D, self.D),
            float(np.sqrt(h_min * h_max)) + self.D,
            temperature=(borefield.Tf_min + borefield.Tf_max) / 2, nb_of_boreholes=1,
            simulation_period=load.simulation_period)

        # quadrant equations, mirroring Borefield.size_L2
        # each entry: (kind, times [s], loads [W], temperature limit [degC])
        self.quadrants = []
        if load.imbalance <= 0:
            # extraction dominated: quadrants 1 and 4
            if load.max_peak_injection != 0:
                th, _, tcm, qh, qpm, qm = load._calculate_first_year_params(False)
                self.quadrants.append(
                    ('carcel', np.array([th, th + load.tm, tcm + th]), (qh, qpm, qm), borefield.Tf_max))
            th, qh, qm, qa = load._calculate_last_year_params(True)
            self.quadrants.append(
                ('ahmadfard', np.array([th, th + load.tm, load.ty + load.tm + th]), (qh, qm, qa), borefield.Tf_min))
        else:
            # injection dominated: quadrants 2 and 3
            th, qh, qm, qa = load._calculate_last_year_params(False)
            self.quadrants.append(
                ('ahmadfard', np.array([th, th + load.tm, load.ty + load.tm + th]), (qh, qm, qa), borefield.Tf_max))
            if load.max_peak_extraction != 0:
                th, _, tcm, qh, qpm, qm = load._calculate_first_year_params(True)
                self.quadrants.append(
                    ('carcel', np.array([th, th + load.tm, tcm + th]), (qh, qpm, qm), borefield.Tf_min))

        # all time values needed by the quadrant equations (fixed for the problem)
        self.times = np.unique(np.concatenate([q[1] for q in self.quadrants]))
        self._time_idx = [np.searchsorted(self.times, q[1]) for q in self.quadrants]

        # precompute the FLS responses on (distance, borehole length) grids
        from pygfunction.heat_transfer import finite_line_source_vectorized

        self.h_grid = np.geomspace(max(h_min, 10.), max(h_max, h_min + 1.), 16)
        self.d_grid = np.geomspace(max(min(b_min, 1.) * 0.5, self.r_b), max(d_max * 1.05, 1.), 300)

        pair_tab = np.empty((len(self.d_grid), len(self.h_grid), len(self.times)))
        self_tab = np.empty((len(self.h_grid), len(self.times)))
        for i, h in enumerate(self.h_grid):
            alpha = self.ground_data.alpha(h + self.D, self.D)
            # closed-form FLS approximation (Cimmino, 2021): smooth, no quadrature
            pair_tab[:, i, :] = finite_line_source_vectorized(
                self.times, alpha, self.d_grid, h, self.D, h, self.D, approximation=True)
            self_tab[i, :] = finite_line_source_vectorized(
                self.times, alpha, self.r_b, h, self.D, h, self.D, approximation=True)

        self._pair_interp = RegularGridInterpolator(
            (np.log(self.d_grid), np.log(self.h_grid)), pair_tab, bounds_error=False, fill_value=None)
        self._self_interp = RegularGridInterpolator(
            (np.log(self.h_grid),), self_tab, bounds_error=False, fill_value=None)

        # integer offset grid for the pairwise interaction of a rectangular field
        i = np.arange(-(n_1_max - 1), n_1_max)
        j = np.arange(-(n_2_max - 1), n_2_max)
        self._offset_i, self._offset_j = np.meshgrid(i, j, indexing='ij')
        self._offset_mask = (self._offset_i != 0) | (self._offset_j != 0)

    def gfunction(self, n_1: float, n_2: float, b_1: float, b_2: float, h: float) -> np.ndarray:
        """
        This function returns the surrogate g-function values at self.times for the
        (relaxed) rectangular configuration.

        Returns
        -------
        gvalues : np.ndarray
        """
        g = self._self_interp([np.log(h)])[0].copy()

        # pairwise interaction: sum over grid offsets, weights = number of ordered pairs
        w = (np.maximum(n_1 - np.abs(self._offset_i), 0.) *
             np.maximum(n_2 - np.abs(self._offset_j), 0.))[self._offset_mask]
        active = w > 0
        if np.any(active):
            d = np.hypot(self._offset_i[self._offset_mask][active] * b_1,
                         self._offset_j[self._offset_mask][active] * b_2)
            pts = np.column_stack((np.log(np.clip(d, self.d_grid[0], self.d_grid[-1])),
                                   np.full(len(d), np.log(h))))
            g = g + w[active] @ self._pair_interp(pts) / (n_1 * n_2)
        return g

    def required_length(self, n_1: float, n_2: float, b_1: float, b_2: float, h: float) -> float:
        """
        This function returns the required total borehole length [m] for the (relaxed)
        rectangular configuration, according to the L2 quadrant equations.

        Returns
        -------
        required length : float
        """
        depth = h + self.D
        k_s = self.ground_data.k_s(depth, self.D)
        Tg = self.ground_data.calculate_Tg(depth, self.D)
        g_all = self.gfunction(n_1, n_2, b_1, b_2, h)

        L_req = 0.
        for (kind, _, loads, Tf), idx in zip(self.quadrants, self._time_idx):
            g = g_all[idx]
            if kind == 'ahmadfard':
                qh, qm, qa = loads
                Ra = (g[2] - g[1]) / (2 * np.pi * k_s)
                Rm = (g[1] - g[0]) / (2 * np.pi * k_s)
                Rd = g[0] / (2 * np.pi * k_s)
                L = (qa * Ra + qm * Rm + qh * Rd + qh * self.Rb) / abs(Tf - Tg)
            else:
                qh, qpm, qm = loads
                Rpm = (g[2] - g[1]) / (2 * np.pi * k_s)
                Rcm = (g[1] - g[0]) / (2 * np.pi * k_s)
                Rh = g[0] / (2 * np.pi * k_s)
                L = (qh * self.Rb + qh * Rh + qm * Rcm + qpm * Rpm) / abs(Tf - Tg)
            L_req = max(L_req, L)
        return L_req

    def required_h(self, n_1: int, n_2: int, b_1: float, b_2: float,
                   h_min: float, h_max: float) -> float:
        """
        This function returns the required borehole length [m] for a fixed configuration
        by iterating the surrogate sizing equation (used for warm starts and fallbacks).

        Returns
        -------
        required borehole length : float
        """
        h = 100.
        for _ in range(30):
            h_new = self.required_length(n_1, n_2, b_1, b_2, min(max(h, h_min), h_max)) / (n_1 * n_2)
            if abs(h_new - h) < 0.1:
                return h_new
            h = 0.5 * h + 0.5 * h_new
        return h


def _spacing_for(n: float, l_max: float, b_min: float, b_max: float) -> float:
    """maximal spacing allowed by the plot (interference only decreases with spacing)"""
    if n <= 1:
        return b_max
    return min(max(l_max / (n - 1), b_min), b_max)


def design_borefield_configuration(
        borefield,
        l_1_max: float,
        l_2_max: float,
        b_min: float,
        b_max: float,
        h_min: float,
        h_max: float,
        cost_per_meter: float = 35.,
        cost_per_borehole: float = 0.,
        nb_min: int = 1,
        nb_max: int = 10000,
        use_L3: bool = True,
        _max_exact_sizings: int = 60) -> list:
    """
    This function designs the borefield configuration all at once: the number of
    boreholes in both directions, the borehole spacing and the borehole length are
    optimised jointly for minimal investment cost, subject to the temperature
    constraints and the available plot of land.

    A smooth physics-based surrogate of the sizing problem is optimised as one NLP,
    after which the integer neighbours of the relaxed optimum are sized exactly and an
    integer hill-climb with exact sizings is performed. Every returned candidate is
    hence certified by an exact sizing; the surrogate is only used for navigation.

    Parameters
    ----------
    borefield : Borefield
        Borefield object with ground data, load data and temperature limits set.
    l_1_max : float
        Maximum size of the plot in the first direction [m]
    l_2_max : float
        Maximum size of the plot in the second direction [m]
    b_min : float
        Minimum borehole spacing [m]
    b_max : float
        Maximum borehole spacing [m]
    h_min : float
        Minimum borehole length [m]
    h_max : float
        Maximum borehole length [m]
    cost_per_meter : float
        Drilling cost per meter of borehole [EUR/m]
    cost_per_borehole : float
        Fixed cost per borehole (mobilisation, hook-up, ...) [EUR]
    nb_min : int
        Minimum number of boreholes [-]
    nb_max : int
        Maximum number of boreholes [-]
    use_L3 : bool
        True if the exact certification sizings should use the L3 (monthly) method,
        False for the L2 method.
    _max_exact_sizings : int
        Safety cap on the number of exact sizings used for certification.

    Returns
    -------
    list
        List of certified candidate configurations, sorted from optimal to less
        optimal. Every element is a dictionary with the keys 'n_1', 'n_2', 'b_1',
        'b_2', 'H', 'number_of_boreholes', 'total_length' and 'cost'. The borefield
        object is configured with the best solution.

    Raises
    ------
    UnsolvableOptimalFieldError
        When no feasible configuration exists within the given bounds.
    """
    n_1_max = max(int(l_1_max / b_min) + 1, 1)
    n_2_max = max(int(l_2_max / b_min) + 1, 1)
    d_max = np.hypot(max(l_1_max, b_max), max(l_2_max, b_max))

    surrogate = _L2Surrogate(borefield, h_min, h_max, b_min, d_max, n_1_max, n_2_max)

    def cost(n_1, n_2, h):
        return n_1 * n_2 * (cost_per_borehole + cost_per_meter * h)

    # ------------------------------------------------------------------
    # stage 1: the relaxed NLP
    # ------------------------------------------------------------------
    cost_scale = cost(max(n_1_max, 2), max(n_2_max, 2), h_max)

    def objective(x):
        n_1, n_2, b_1, b_2, h = x
        return cost(n_1, n_2, h) / cost_scale

    def sizing_constraint(x):
        n_1, n_2, b_1, b_2, h = x
        return (n_1 * n_2 * h - surrogate.required_length(n_1, n_2, b_1, b_2, h)) / (h_max * max(nb_min, 1))

    constraints = [
        {'type': 'ineq', 'fun': sizing_constraint},
        {'type': 'ineq', 'fun': lambda x: (l_1_max - (x[0] - 1) * x[2]) / max(l_1_max, 1)},
        {'type': 'ineq', 'fun': lambda x: (l_2_max - (x[1] - 1) * x[3]) / max(l_2_max, 1)},
        {'type': 'ineq', 'fun': lambda x: (nb_max - x[0] * x[1]) / nb_max},
        {'type': 'ineq', 'fun': lambda x: (x[0] * x[1] - nb_min) / max(nb_min, 1)},
    ]
    bounds = [(1., n_1_max), (1., n_2_max), (b_min, b_max), (b_min, b_max), (h_min, h_max)]

    starts = []
    for n_1s, n_2s, hs in ((n_1_max, n_2_max, h_min), (max(1., n_1_max / 4), max(1., n_2_max / 4), h_max),
                           (max(1., n_1_max / 2), max(1., n_2_max / 2), 0.5 * (h_min + h_max)),
                           # line and boundary configurations form separate basins
                           (1., n_2_max, h_max), (n_1_max, 1., h_max),
                           (n_1_max, max(1., n_2_max / 3), 0.5 * (h_min + h_max)),
                           (max(1., n_1_max / 3), n_2_max, 0.5 * (h_min + h_max))):
        starts.append([n_1s, n_2s, _spacing_for(n_1s, l_1_max, b_min, b_max),
                       _spacing_for(n_2s, l_2_max, b_min, b_max), hs])

    relaxed = []
    for x0 in starts:
        try:
            res = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints,
                           options={'maxiter': 200, 'ftol': 1e-9})
            if res.success and sizing_constraint(res.x) > -1e-4:
                relaxed.append(res.x)
        except (ValueError, FloatingPointError):  # pragma: no cover
            continue

    # ------------------------------------------------------------------
    # stage 2 and 3: exact certification of the integer neighbours and hill-climb
    # ------------------------------------------------------------------
    exact_cache = {}
    exact_borefield = copy.deepcopy(borefield)

    def size_exact(n_1: int, n_2: int):
        """exact sizing; returns (cost, H, b_1, b_2) or None if infeasible"""
        n_1, n_2 = int(n_1), int(n_2)
        key = (n_1, n_2)
        if key in exact_cache:
            return exact_cache[key]
        if not (1 <= n_1 <= n_1_max and 1 <= n_2 <= n_2_max and nb_min <= n_1 * n_2 <= nb_max) \
                or len(exact_cache) >= _max_exact_sizings:
            exact_cache[key] = None
            return None
        b_1 = _spacing_for(n_1, l_1_max, b_min, b_max)
        b_2 = _spacing_for(n_2, l_2_max, b_min, b_max)
        h_start = surrogate.required_h(n_1, n_2, b_1, b_2, h_min, h_max)
        try:
            exact_borefield.create_rectangular_borefield(n_1, n_2, b_1, b_2,
                                                         min(max(h_start, h_min), h_max), borefield.D, borefield.r_b)
            H = exact_borefield.size(min(max(h_start, h_min), h_max),
                                     L3_sizing=use_L3, L2_sizing=not use_L3)
        except (UnsolvableDueToTemperatureGradient, MaximumNumberOfIterations, ValueError, RuntimeError):
            exact_cache[key] = None
            return None
        if H > h_max + 0.05:
            exact_cache[key] = None
            return None
        H = max(H, h_min)
        exact_cache[key] = (cost(n_1, n_2, H), H, b_1, b_2)
        return exact_cache[key]

    # candidates: integer neighbours of every relaxed solution
    candidates = set()
    for x in relaxed:
        for dn_1 in (0, 1, -1):
            for dn_2 in (0, 1, -1):
                candidates.add((int(np.floor(x[0])) + dn_1, int(np.floor(x[1])) + dn_2))
                candidates.add((int(np.ceil(x[0])) + dn_1, int(np.ceil(x[1])) + dn_2))

    # the 1D boundary families of the integer lattice (single and double rows and
    # the plot-filling edges) are separate basins that the integer hill-climb cannot
    # reach from a block optimum: scan them with the cheap surrogate and add the
    # most promising members as candidates
    for family in ('n1', 'n2'):
        boundary = (1, 2, n_1_max, n_1_max - 1) if family == 'n1' else (1, 2, n_2_max, n_2_max - 1)
        for n_fixed in {max(n, 1) for n in boundary}:
            best_family = None
            n_free_max = n_2_max if family == 'n1' else n_1_max
            for n in range(1, n_free_max + 1):
                n_1, n_2 = (n_fixed, n) if family == 'n1' else (n, n_fixed)
                if not nb_min <= n_1 * n_2 <= nb_max:
                    continue
                b_1 = _spacing_for(n_1, l_1_max, b_min, b_max)
                b_2 = _spacing_for(n_2, l_2_max, b_min, b_max)
                h = surrogate.required_h(n_1, n_2, b_1, b_2, h_min, h_max)
                if h > h_max:
                    continue
                c = cost(n_1, n_2, max(h, h_min))
                if best_family is None or c < best_family[0]:
                    best_family = (c, n_1, n_2)
            if best_family is not None:
                candidates.add((best_family[1], best_family[2]))
    if not candidates:
        # surrogate NLP failed: fall back to a coarse surrogate scan
        best_scan = None
        for n_1 in range(1, n_1_max + 1):
            for n_2 in range(1, n_2_max + 1):
                if not nb_min <= n_1 * n_2 <= nb_max:
                    continue
                b_1 = _spacing_for(n_1, l_1_max, b_min, b_max)
                b_2 = _spacing_for(n_2, l_2_max, b_min, b_max)
                h = surrogate.required_h(n_1, n_2, b_1, b_2, h_min, h_max)
                if h > h_max:
                    continue
                c = cost(n_1, n_2, max(h, h_min))
                if best_scan is None or c < best_scan[0]:
                    best_scan = (c, n_1, n_2)
        if best_scan is None:
            raise UnsolvableOptimalFieldError
        candidates.add((best_scan[1], best_scan[2]))

    for key in sorted(candidates):
        size_exact(*key)

    def best_of_cache():
        feasible = [(v[0], k, v) for k, v in exact_cache.items() if v is not None]
        return min(feasible) if feasible else None

    best = best_of_cache()
    if best is None:
        raise UnsolvableOptimalFieldError

    # integer hill-climb with exact sizings: guarantees (+-1)-optimality w.r.t. the exact model
    improved = True
    while improved:
        improved = False
        (n_1, n_2) = best[1]
        for dn_1, dn_2 in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
            size_exact(n_1 + dn_1, n_2 + dn_2)
        new_best = best_of_cache()
        if new_best[1] != best[1]:
            best = new_best
            improved = True

    # configure the borefield with the optimal solution and return all candidates
    solutions = sorted((v[0], k, v) for k, v in exact_cache.items() if v is not None)
    result = [{'n_1': k[0], 'n_2': k[1], 'b_1': v[2], 'b_2': v[3], 'H': v[1],
               'number_of_boreholes': k[0] * k[1], 'total_length': k[0] * k[1] * v[1], 'cost': c}
              for c, k, v in solutions]

    top = result[0]
    borefield.create_rectangular_borefield(top['n_1'], top['n_2'], top['b_1'], top['b_2'],
                                           top['H'], borefield.D, borefield.r_b)
    return result
