"""
g-functions on pygfunction's public solvers, without the solver monkeypatch.

Motivation
----------
GHEtool historically computes g-functions through a *monkeypatch* of pygfunction's
solver (see :mod:`GHEtool.VariableClasses.Cylindrical_correction`), replacing
``_BaseSolver.solve``/``__init__`` and ``Equivalent.thermal_response_factors`` to inject
the finite-radius *cylindrical correction* that upstream pygfunction lacks. That patch
also bypasses any solver improvement made upstream.

Newer pygfunction exposes a Laplace-domain solver (``method='laplace'``) that reconstructs
the g-function as a sum of decaying exponentials. Its cost is *independent* of the number
of requested time values and it yields the exact continuous-time g-function, evaluable at
any instant. This module lets GHEtool ride that solver (or any public pygfunction solver)
*without* the monkeypatch, and re-adds the cylindrical correction as a thin, provably
field-independent early-time delta.

Why the correction is separable
-------------------------------
The cylindrical correction only modifies each borehole's *self*-response, and only at
early times (t ~ r_b^2 / alpha). At those times the thermal radius sqrt(alpha*t) is far
smaller than the borehole spacing, so the boreholes are thermally isolated and the
correction's effect on the field g-function equals the single-borehole correction. This is
verified numerically: the single-borehole delta reproduces the full-field cylindrical
correction to < 0.008 g-units (the residual being the negligible late-time inter-borehole
coupling), against an early-time correction of ~0.30 g-units. See
``test_laplace_gfunction.py``.

    g_field_corrected(t) ~= g_field_FLS(t) + [g_1borehole_corrected(t) - g_1borehole_FLS(t)]
                            \\_______________/   \\_________________________________________/
                             any public solver     field-independent, single-borehole delta
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np
import pygfunction as gt

# Importing this module (indirectly, through the package) applies the cylindrical-correction
# monkeypatch. We rely on the ``cylindrical_correction`` option it adds to compute the
# single-borehole delta, but we compute the *field* base g through the untouched public
# solvers (``Laplace.solve``/``Similarities.solve`` are defined on the subclasses and are
# not affected by the ``_BaseSolver`` patch).

#: Solvers whose ``solve`` is not overridden by the cylindrical-correction monkeypatch and
#: that therefore return the genuine upstream result.
_CONTINUOUS_METHOD = "laplace"


def laplace_method_available() -> bool:
    """Return whether the installed pygfunction exposes the Laplace-domain solver."""
    return hasattr(gt.solvers, "Laplace")


def _uniform_geometry(boreholes: List) -> Optional[tuple]:
    """
    Return ``(H, D, r_b)`` if every borehole shares the same length, buried depth and
    radius (the case the single-borehole cylindrical delta is valid for), else ``None``.
    """
    H = np.array([b.H for b in boreholes])
    D = np.array([b.D for b in boreholes])
    r_b = np.array([b.r_b for b in boreholes])
    if np.ptp(H) < 1e-9 and np.ptp(D) < 1e-9 and np.ptp(r_b) < 1e-9:
        return float(H[0]), float(D[0]), float(r_b[0])
    return None


@dataclass
class GFunctionResult:
    """Result of a fast g-function evaluation."""

    time: np.ndarray
    """Time values (s) the g-function was evaluated at."""
    gfunc: np.ndarray
    """g-function values, cylindrical correction included when requested."""
    base_gfunc: np.ndarray
    """Uncorrected (finite line source) g-function from the public solver."""
    correction: np.ndarray
    """The cylindrical-correction delta that was added (zeros when disabled)."""
    method: str
    """pygfunction method used for the base g-function."""
    cylindrical_correction: bool
    """Whether the cylindrical correction was applied."""


def cylindrical_correction_delta(
    boreholes: List,
    alpha: float,
    time: np.ndarray,
    *,
    base_method: str = "equivalent",
    n_reference: int = 60,
) -> np.ndarray:
    """
    Field-independent cylindrical-correction delta, computed from a single borehole.

    The delta is ``g_1borehole_corrected - g_1borehole_uncorrected`` for a borehole with
    the field's geometry. It is added to a field's uncorrected g-function to recover the
    cylindrically corrected g-function (exact at early times, < 0.008 g-units residual at
    late times, where the correction itself is already negligible).

    The delta is a smooth function of ``log(time)`` that vanishes at late times, so it is
    evaluated on a fixed coarse log-spaced grid and interpolated. This keeps the correction
    *flat cost* in the number of requested time values, preserving the flat cost of the
    Laplace base solver.

    Parameters
    ----------
    boreholes : list of pygfunction Borehole
        The borefield; must have uniform geometry.
    alpha : float
        Ground thermal diffusivity (m^2/s).
    time : np.ndarray
        Time values (s).
    base_method : str
        pygfunction method used for the two single-borehole evaluations.
    n_reference : int
        Number of log-spaced reference points the delta is computed at before interpolation.

    Returns
    -------
    np.ndarray
        The correction delta, same shape as ``time``.

    Raises
    ------
    ValueError
        If the borefield geometry is not uniform.
    """
    geom = _uniform_geometry(boreholes)
    if geom is None:
        raise ValueError(
            "The single-borehole cylindrical correction is only valid for a borefield of "
            "identical boreholes. Use the monkeypatched solver for mixed geometries."
        )
    H, D, r_b = geom
    time = np.asarray(time, dtype=float)

    # Evaluate the delta on a coarse log grid, then interpolate (flat cost, smooth in log t).
    if time.size <= n_reference:
        ref_time = time
    else:
        ref_time = np.geomspace(time[0], time[-1], n_reference)

    one = [gt.boreholes.Borehole(H, D, r_b, 0.0, 0.0)]
    g_std = gt.gfunction.gFunction(
        one, alpha, ref_time, method=base_method, options={"disp": False}
    ).gFunc
    g_cyl = gt.gfunction.gFunction(
        one, alpha, ref_time, method=base_method,
        options={"disp": False, "cylindrical_correction": True},
    ).gFunc
    delta_ref = g_cyl - g_std

    if ref_time is time:
        return delta_ref
    return np.interp(np.log(time), np.log(ref_time), delta_ref)


def calculate_gfunction(
    boreholes: List,
    alpha: float,
    time: np.ndarray,
    *,
    method: str = "laplace",
    boundary_condition: str = "UBWT",
    cylindrical_correction: bool = True,
    options: Optional[dict] = None,
) -> GFunctionResult:
    """
    Evaluate a g-function through a public pygfunction solver, optionally re-adding the
    cylindrical correction as a field-independent delta.

    When ``method='laplace'`` (and available) the base g-function is the exact
    continuous-time solution, evaluated at flat cost regardless of the number of time
    values -- ideal for hourly (L4) simulations. Falls back to ``method='equivalent'``
    when the Laplace solver is not present in the installed pygfunction.

    Parameters
    ----------
    boreholes : list of pygfunction Borehole
        The borefield.
    alpha : float
        Ground thermal diffusivity (m^2/s).
    time : np.ndarray
        Time values (s).
    method : str
        pygfunction solver method ('laplace', 'similarities', 'equivalent', 'detailed').
    boundary_condition : str
        Boundary condition for the base solver (the Laplace solver supports 'UBWT'/'UHTR').
    cylindrical_correction : bool
        Whether to add the finite-radius cylindrical correction.
    options : dict, optional
        Extra options forwarded to ``pygfunction.gfunction.gFunction``.

    Returns
    -------
    GFunctionResult
    """
    time = np.asarray(time, dtype=float)
    opts = {"disp": False}
    if options:
        opts.update(options)

    if method == _CONTINUOUS_METHOD and not laplace_method_available():
        method = "equivalent"

    kwargs = {}
    # Only the field/wall boundary conditions are meaningful without a fluid network.
    if method in ("laplace",):
        kwargs["boundary_condition"] = boundary_condition

    base = gt.gfunction.gFunction(
        boreholes, alpha, time, method=method, options=opts, **kwargs
    ).gFunc

    if cylindrical_correction:
        correction = cylindrical_correction_delta(boreholes, alpha, time)
    else:
        correction = np.zeros_like(base)

    return GFunctionResult(
        time=time,
        gfunc=base + correction,
        base_gfunc=base,
        correction=correction,
        method=method,
        cylindrical_correction=cylindrical_correction,
    )
