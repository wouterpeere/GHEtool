"""
Tests for the all-at-once borefield configuration design method.
The optimum returned by the method is checked against exhaustive enumeration.
"""
import copy

import numpy as np
import pytest

from GHEtool import Borefield, GroundConstantTemperature, MonthlyGeothermalLoadAbsolute
from GHEtool.Methods import design_borefield_configuration
from GHEtool.VariableClasses.BaseClass import UnsolvableOptimalFieldError


def _borefield(scale_extraction: float = 1., scale_injection: float = 1.) -> Borefield:
    extraction = np.array([46500., 44400., 37500., 29700., 19200., 0., 0., 0., 18300., 26100., 35100., 43200.])
    injection = np.array([4000., 8000., 8000., 8000., 12000., 16000., 32000., 32000., 16000., 12000., 8000., 4000.])
    peak_extraction = np.array([160., 142., 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.])
    peak_injection = np.array([0., 0., 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.])
    load = MonthlyGeothermalLoadAbsolute(extraction * scale_extraction, injection * scale_injection,
                                         peak_extraction * scale_extraction, peak_injection * scale_injection, 20)
    borefield = Borefield(load=load, ground_data=GroundConstantTemperature(3, 10))
    borefield.create_rectangular_borefield(5, 5, 6, 6, 110, 4, 0.075)
    borefield.Rb = 0.12
    borefield.set_max_fluid_temperature(16)
    borefield.set_min_fluid_temperature(0)
    return borefield


def _enumerate_optimum(borefield: Borefield, l_1_max, l_2_max, b_min, b_max, h_min, h_max,
                       cost_per_meter, cost_per_borehole, use_L3=False):
    """brute-force reference: exact sizing of every integer configuration"""
    best = None
    bf = copy.deepcopy(borefield)
    for n_1 in range(1, int(l_1_max / b_min) + 2):
        for n_2 in range(1, int(l_2_max / b_min) + 2):
            b_1 = b_max if n_1 == 1 else min(max(l_1_max / (n_1 - 1), b_min), b_max)
            b_2 = b_max if n_2 == 1 else min(max(l_2_max / (n_2 - 1), b_min), b_max)
            try:
                bf.create_rectangular_borefield(n_1, n_2, b_1, b_2, 100, borefield.D, borefield.r_b)
                H = bf.size(100, L3_sizing=use_L3, L2_sizing=not use_L3)
            except Exception:
                continue
            if H > h_max + 0.05:
                continue
            H = max(H, h_min)
            cost = n_1 * n_2 * (cost_per_borehole + cost_per_meter * H)
            if best is None or cost < best[0]:
                best = (cost, n_1, n_2, H)
    return best


def test_matches_enumeration_small_plot():
    borefield = _borefield(scale_extraction=0.35, scale_injection=0.2)
    args = dict(l_1_max=15., l_2_max=20., b_min=5., b_max=10., h_min=40., h_max=200.,
                cost_per_meter=35., cost_per_borehole=500.)
    result = design_borefield_configuration(borefield, use_L3=False, **args)
    reference = _enumerate_optimum(_borefield(scale_extraction=0.35, scale_injection=0.2), use_L3=False, **args)
    assert reference is not None
    assert result[0]['cost'] <= reference[0] * (1 + 1e-6)
    # the borefield object is configured with the optimum
    assert borefield.number_of_boreholes == result[0]['number_of_boreholes']


def test_cost_trade_off_changes_optimum():
    # expensive boreholes should push the design towards fewer, deeper boreholes
    args = dict(l_1_max=25., l_2_max=25., b_min=5., b_max=12., h_min=40., h_max=250., use_L3=False)
    cheap = design_borefield_configuration(_borefield(0.35, 0.2), cost_per_meter=35., cost_per_borehole=0., **args)
    pricey = design_borefield_configuration(_borefield(0.35, 0.2), cost_per_meter=35., cost_per_borehole=5000., **args)
    assert pricey[0]['number_of_boreholes'] <= cheap[0]['number_of_boreholes']
    # every certified candidate respects the geometric constraints
    for r in cheap + pricey:
        assert (r['n_1'] - 1) * r['b_1'] <= 25. + 1e-9
        assert (r['n_2'] - 1) * r['b_2'] <= 25. + 1e-9
        assert 40. - 1e-9 <= r['H'] <= 250. + 0.05


def test_unsolvable_raises():
    borefield = _borefield(5., 3.)  # very large load on a tiny plot
    with pytest.raises(UnsolvableOptimalFieldError):
        design_borefield_configuration(borefield, l_1_max=6., l_2_max=6., b_min=5., b_max=10.,
                                       h_min=40., h_max=60., cost_per_meter=35., use_L3=False)
