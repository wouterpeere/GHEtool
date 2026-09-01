"""
This file contains a hybrid dispatch optimisation formulated as a linear program.

For a fixed borefield, the fluid temperature is a linear function of the dispatched
ground load (a convolution with the g-function increments). The question 'which part
of the building load should the borefield serve, hour by hour' therefore has a
polyhedral feasible set, and the optimal hybrid dispatch is a linear program that can
be solved globally and all at once, instead of with a load-duration-curve clipping
iteration:

    max   total energy served by the borefield        (objective='energy')
    min   external (backup) peak capacity needed      (objective='power')
    s.t.  Tf_min <= Tf(t) <= Tf_max     for every hour of the first and the last year
          0 <= served(t) <= demand(t)   for every hour

Only a handful of the temperature constraints bind at the optimum (the hours in which
the ground is exhausted), so the LP is solved with constraint-row generation: solve,
find the violated hours with an exact temperature evaluation, add those rows, repeat.
The multi-year temperature response of the periodic load is evaluated exactly with a
year-folded convolution kernel.

The 'power' objective is solved lexicographically: first the minimal backup capacity
is found, then, with that capacity fixed, the served energy is maximised, so the
returned dispatch is not needlessly conservative.

The returned solution is certified: the temperatures of the resulting borefield load
are recalculated with the regular hourly temperature calculation of GHEtool and
checked against the temperature limits.

The dual variables (shadow prices) of the binding temperature constraints are
returned as well: they quantify the marginal value of relaxing the temperature band,
and, through the 1/length scaling of the temperature response, the marginal value of
additional borehole length. This is the coupling quantity for a joint
configuration-and-dispatch (two-stage) design optimisation.
"""
import copy

import numpy as np

from scipy.optimize import linprog
from scipy.signal import fftconvolve

from GHEtool.VariableClasses import SCOP, SEER
from GHEtool.VariableClasses.LoadData import HourlyBuildingLoad

__all__ = ['optimise_load_profile_lp']


def optimise_load_profile_lp(
        borefield,
        building_load: HourlyBuildingLoad,
        objective: str = 'energy',
        temperature_threshold: float = 0.025,
        max_lp_rounds: int = 40,
        return_shadow_prices: bool = False):
    """
    This function optimises the hybrid dispatch (the split of the building load between
    the borefield and an external system) as a single linear program, which is globally
    optimal for the chosen objective. See the module documentation for the formulation.

    Parameters
    ----------
    borefield : Borefield
        Borefield object (with ground data and temperature limits set).
    building_load : HourlyBuildingLoad
        Building load to be split between the borefield and the external system.
        Constant efficiencies (SCOP/SEER) are required and the load should start in
        January without a DHW profile.
    objective : str
        'energy' to maximise the total energy served by the borefield, 'power' to
        minimise the external (backup) peak capacity (lexicographically followed by
        an energy maximisation at that capacity).
    temperature_threshold : float
        Maximum allowed violation of the temperature limits in the certification of
        the result [K].
    max_lp_rounds : int
        Maximum number of constraint-generation rounds.
    return_shadow_prices : bool
        True if a dictionary with the shadow prices of the binding temperature
        constraints (and the derived marginal value of borehole length) should be
        returned as a third element.

    Returns
    -------
    tuple(HourlyBuildingLoad, HourlyBuildingLoad) or tuple(..., ..., dict)
        Borefield load, external load (and optionally the shadow price information).

    Raises
    ------
    ValueError
        When the load is not an HourlyBuildingLoad with constant efficiencies starting
        in January, or when the certification of the result fails.
    """
    if not isinstance(building_load, HourlyBuildingLoad):
        raise ValueError('The LP dispatch optimisation requires an HourlyBuildingLoad.')
    if not (isinstance(building_load.cop, SCOP) and isinstance(building_load.eer, SEER)):
        raise ValueError('The LP dispatch optimisation requires constant efficiencies (SCOP/SEER). '
                         'For temperature-dependent efficiencies, please use the optimise_load_profile_power '
                         'or _energy methods, or iterate this method with updated efficiencies.')
    if building_load.start_month != 1:
        raise ValueError('The LP dispatch optimisation requires a load starting in January.')
    if building_load._hourly_dhw_load is not None and np.any(building_load._hourly_dhw_load):
        raise ValueError('The LP dispatch optimisation does not support DHW profiles.')
    if objective not in ('energy', 'power'):
        raise ValueError("The objective should be either 'energy' or 'power'.")

    borefield = copy.deepcopy(borefield)
    borefield.load = copy.deepcopy(building_load)

    P = 8760
    years = building_load.simulation_period
    dem_h = building_load.hourly_heating_load.copy()
    dem_c = building_load.hourly_cooling_load.copy()

    # building -> ground conversion factors (constant, since SCOP/SEER)
    f_h = 1. - 1. / building_load.cop.get_COP(0)
    f_c = 1. + 1. / building_load.eer.get_EER(0)

    # exact temperature response of the borefield
    H = borefield.H
    depth = borefield.calculate_depth(H, borefield.D)
    L_tot = borefield.number_of_boreholes * H
    k_s = borefield.ground_data.k_s(depth, borefield.D)
    Tg = borefield._Tg(H)
    Tf_min, Tf_max = borefield.Tf_min, borefield.Tf_max
    Rb = borefield.Rb

    g = borefield.gfunction(building_load.time_L4, H)
    dg = np.diff(g, prepend=0)
    scale = 1000. / (2 * np.pi * k_s * L_tot)   # K per kW of load in the convolution
    rb_term = 1000. * Rb / L_tot                # K per kW of load at the same hour

    # year-folded convolution kernel: exact multi-year response of a periodic load
    K = np.zeros(2 * P - 1)
    for j in range(years):
        lo, hi = j * P - (P - 1), j * P + P
        src = dg[max(lo, 0):min(hi, years * P)]
        K[max(lo, 0) - lo: max(lo, 0) - lo + len(src)] += src
    K_first = dg[:P]

    def temperatures(q):
        """fluid temperature in the first and the last year for a periodic load q [kW]"""
        T_first = Tg + scale * fftconvolve(q, K_first)[:P] + rb_term * q
        T_last = Tg + scale * fftconvolve(q, K)[P - 1:2 * P - 1] + rb_term * q
        return T_first, T_last

    def temperature_row(tau, last_year):
        """row a such that Tf(tau) = Tg + a . q"""
        a = np.zeros(P)
        if last_year:
            a[:] = scale * K[tau - np.arange(P) + P - 1]
        else:
            a[:tau + 1] = scale * K_first[tau::-1]
        a[tau] += rb_term
        return a

    # ------------------------------------------------------------------
    # LP with constraint-row generation
    # variables: x = [served heating (P), served cooling (P), (Cap_h, Cap_c)]
    # ------------------------------------------------------------------
    n_extra = 2 if objective == 'power' else 0
    nvar = 2 * P + n_extra
    bounds = [(0., d) for d in dem_h] + [(0., d) for d in dem_c] + [(0., None)] * n_extra
    if objective == 'energy':
        c = np.concatenate((-np.ones(2 * P), np.zeros(n_extra)))
    else:
        c = np.zeros(nvar)
        c[-2:] = 1.

    A_ub, b_ub, row_info = [], [], []
    added_T, added_cap = set(), set()

    def add_capacity_row(u, side):
        # dem - x <= Cap  ->  -x - Cap <= -dem
        r = np.zeros(nvar)
        r[u if side == 'h' else P + u] = -1.
        r[-2 if side == 'h' else -1] = -1.
        A_ub.append(r)
        b_ub.append(-(dem_h[u] if side == 'h' else dem_c[u]))
        row_info.append(None)
        added_cap.add((u, side))

    def add_temperature_row(tau, last_year, sign):
        a = temperature_row(tau, last_year)
        r = np.zeros(nvar)
        r[:P] = sign * (-f_h) * a
        r[P:2 * P] = sign * f_c * a
        A_ub.append(r)
        b_ub.append((Tf_max - Tg) if sign > 0 else (Tg - Tf_min))
        row_info.append((tau, last_year, sign))
        added_T.add((tau, last_year, sign))

    if objective == 'power':
        for u in np.argsort(dem_h)[-50:]:
            if dem_h[u] > 0:
                add_capacity_row(int(u), 'h')
        for u in np.argsort(dem_c)[-50:]:
            if dem_c[u] > 0:
                add_capacity_row(int(u), 'c')

    def solve_current(c_vec, extra_bounds=None):
        return linprog(c_vec, A_ub=np.asarray(A_ub) if A_ub else None, b_ub=np.asarray(b_ub) if b_ub else None,
                       bounds=extra_bounds if extra_bounds is not None else bounds, method='highs')

    res, x = None, None
    for _ in range(max_lp_rounds):
        res = solve_current(c)
        if not res.success:
            raise ValueError(f'The LP dispatch optimisation failed: {res.message}')
        x = res.x
        q = f_c * x[P:2 * P] - f_h * x[:P]
        T_first, T_last = temperatures(q)

        new_rows = 0
        for T, last_year in ((T_first, False), (T_last, True)):
            for sign in (1., -1.):
                v = sign * T - (Tf_max if sign > 0 else -Tf_min)
                for i in np.argsort(v)[-80:]:
                    if v[i] > 1e-7 and (int(i), last_year, sign) not in added_T:
                        add_temperature_row(int(i), last_year, sign)
                        new_rows += 1
        if objective == 'power':
            cap_h, cap_c = x[-2], x[-1]
            for u in np.where(dem_h - x[:P] > cap_h + 1e-7)[0]:
                if (int(u), 'h') not in added_cap:
                    add_capacity_row(int(u), 'h')
                    new_rows += 1
            for u in np.where(dem_c - x[P:2 * P] > cap_c + 1e-7)[0]:
                if (int(u), 'c') not in added_cap:
                    add_capacity_row(int(u), 'c')
                    new_rows += 1
        if new_rows == 0:
            break
    else:
        raise ValueError('The LP dispatch optimisation did not converge within the allowed number of rounds.')

    if objective == 'power':
        # lexicographic refinement: fix the optimal capacities, maximise the served energy
        cap_h, cap_c = x[-2], x[-1]
        c2 = np.concatenate((-np.ones(2 * P), np.zeros(2)))
        bounds2 = bounds[:2 * P] + [(0., cap_h + 1e-9), (0., cap_c + 1e-9)]
        for _ in range(max_lp_rounds):
            res = solve_current(c2, bounds2)
            if not res.success:  # pragma: no cover
                break
            x = res.x
            q = f_c * x[P:2 * P] - f_h * x[:P]
            T_first, T_last = temperatures(q)
            new_rows = 0
            for T, last_year in ((T_first, False), (T_last, True)):
                for sign in (1., -1.):
                    v = sign * T - (Tf_max if sign > 0 else -Tf_min)
                    for i in np.argsort(v)[-80:]:
                        if v[i] > 1e-7 and (int(i), last_year, sign) not in added_T:
                            add_temperature_row(int(i), last_year, sign)
                            new_rows += 1
            for u in np.where(dem_h - x[:P] > cap_h + 1e-6)[0]:
                if (int(u), 'h') not in added_cap:
                    add_capacity_row(int(u), 'h')
                    new_rows += 1
            for u in np.where(dem_c - x[P:2 * P] > cap_c + 1e-6)[0]:
                if (int(u), 'c') not in added_cap:
                    add_capacity_row(int(u), 'c')
                    new_rows += 1
            if new_rows == 0:
                break

    served_h, served_c = x[:P], x[P:2 * P]

    # ------------------------------------------------------------------
    # certification with the regular GHEtool temperature calculation
    # ------------------------------------------------------------------
    borefield_load = copy.deepcopy(building_load)
    borefield_load.hourly_heating_load = served_h
    borefield_load.hourly_cooling_load = served_c
    external_load = copy.deepcopy(building_load)
    external_load.hourly_heating_load = np.maximum(dem_h - served_h, 0.)
    external_load.hourly_cooling_load = np.maximum(dem_c - served_c, 0.)

    borefield.load = copy.deepcopy(borefield_load)
    borefield.calculate_temperatures(hourly=True)
    T_max_cert = float(np.max(borefield.results.peak_injection))
    T_min_cert = float(np.min(borefield.results.peak_injection))
    if T_max_cert > Tf_max + temperature_threshold or T_min_cert < Tf_min - temperature_threshold:
        raise ValueError(  # pragma: no cover
            f'The certification of the LP dispatch failed: the fluid temperature spans '
            f'[{T_min_cert:.3f}, {T_max_cert:.3f}] degC for limits [{Tf_min}, {Tf_max}] degC.')

    if not return_shadow_prices:
        return borefield_load, external_load

    # shadow prices of the binding temperature constraints; the marginal objective
    # value of extra borehole length follows from the 1/length scaling of the
    # temperature response: dTf/dL = -(Tf - Tg)/L at the binding hours
    marginals = res.ineqlin.marginals if row_info else np.array([])
    shadow = []
    marginal_value_length = 0.
    for i, info in enumerate(row_info):
        if info is None or abs(marginals[i]) < 1e-12:
            continue
        tau, last_year, sign = info
        lam = -marginals[i]  # positive shadow price of tightening the constraint
        limit = Tf_max if sign > 0 else Tf_min
        shadow.append({'hour': tau, 'year': years if last_year else 1,
                       'limit': limit, 'shadow_price': lam})
        marginal_value_length += lam * abs(limit - Tg) / L_tot
    info = {'temperature_constraints': shadow,
            'marginal_objective_value_per_meter': marginal_value_length,
            'certified_temperature_range': (T_min_cert, T_max_cert)}
    return borefield_load, external_load, info
