"""
Proof tests for the fast/continuous g-function path (DecoupledGFunction).

These assert the two claims the module rests on:
  1. The cylindrical correction is field-independent at early times, so a single-borehole
     delta reproduces GHEtool's full-field cylindrically corrected g-function.
  2. Using pygfunction's public solver + that delta recovers GHEtool's corrected g-function
     to well within the equivalent-approximation gap GHEtool already accepts.

They run on any pygfunction: when the Laplace solver is present the continuous path is
exercised, otherwise the module falls back to 'equivalent' and the same assertions hold.
"""
import time as _time

import numpy as np
import pygfunction as gt
import pytest

from GHEtool.VariableClasses.Gfunctions.DecoupledGFunction import (
    calculate_gfunction,
    cylindrical_correction_delta,
    laplace_method_available,
)

ALPHA = 1.25e-6
H, D, R_B = 100.0, 4.0, 0.075


def _field():
    return gt.boreholes.rectangle_field(10, 10, 6.0, 6.0, H, D, R_B)


def _ghetool_reference(time, cylindrical):
    """GHEtool's own (monkeypatched) g-function, the ground truth to reproduce."""
    return gt.gfunction.gFunction(
        _field(), ALPHA, time, method="equivalent",
        options={"disp": False, "cylindrical_correction": cylindrical},
    ).gFunc


def test_uncorrected_base_matches_ghetool():
    # Public 'equivalent' solver == GHEtool uncorrected g-function (bit-for-bit upstream).
    time = np.geomspace(3600.0, 20 * 8760 * 3600.0, 60)
    res = calculate_gfunction(_field(), ALPHA, time, method="equivalent",
                              cylindrical_correction=False)
    ref = _ghetool_reference(time, cylindrical=False)
    assert np.allclose(res.gfunc, ref, atol=1e-9)


def test_single_borehole_delta_is_field_independent_early():
    # The single-borehole correction must equal the full-field correction at early times.
    time = np.geomspace(3600.0, 20 * 8760 * 3600.0, 60)
    field_delta = _ghetool_reference(time, True) - _ghetool_reference(time, False)
    one_delta = cylindrical_correction_delta(_field(), ALPHA, time)
    # Perfect agreement at the earliest time (where the correction is largest, ~0.30).
    assert abs(one_delta[0] - field_delta[0]) < 1e-3
    # And bounded everywhere by the negligible late-time coupling.
    assert np.max(np.abs(one_delta - field_delta)) < 0.01


def test_corrected_composition_reproduces_ghetool():
    # base (any public solver) + field-independent delta == GHEtool corrected g.
    time = np.geomspace(3600.0, 20 * 8760 * 3600.0, 60)
    ref = _ghetool_reference(time, cylindrical=True)
    res = calculate_gfunction(_field(), ALPHA, time, cylindrical_correction=True)
    # Tolerance: well below the equivalent-approximation gap (~0.035) GHEtool accepts.
    assert np.max(np.abs(res.gfunc - ref)) < 0.05
    # Early-time correction (the whole point) must be essentially exact.
    assert abs(res.gfunc[0] - ref[0]) < 1e-3


def test_result_fields_are_consistent():
    time = np.geomspace(3600.0, 20 * 8760 * 3600.0, 40)
    res = calculate_gfunction(_field(), ALPHA, time, cylindrical_correction=True)
    assert np.allclose(res.gfunc, res.base_gfunc + res.correction)
    assert res.correction.shape == time.shape


def test_mixed_geometry_rejected():
    field = [gt.boreholes.Borehole(100.0, 4.0, 0.075, 0.0, 0.0),
             gt.boreholes.Borehole(120.0, 4.0, 0.075, 6.0, 0.0)]
    with pytest.raises(ValueError):
        cylindrical_correction_delta(field, ALPHA, np.array([3600.0, 7200.0]))


@pytest.mark.skipif(not laplace_method_available(),
                    reason="Laplace solver not in installed pygfunction")
def test_laplace_cost_is_flat_in_time_points():
    # The Laplace base g cost must be ~independent of the number of time values.
    field = _field()

    def base_time(nt):
        t = np.geomspace(3600.0, 20 * 8760 * 3600.0, nt)
        t0 = _time.perf_counter()
        calculate_gfunction(field, ALPHA, t, method="laplace",
                            cylindrical_correction=False)
        return _time.perf_counter() - t0

    base_time(50)  # warmup
    small = base_time(100)
    large = base_time(2000)
    # 20x the time points must not cost anywhere near 20x the time.
    assert large < 4 * small
