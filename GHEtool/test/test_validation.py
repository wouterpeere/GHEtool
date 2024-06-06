import matplotlib.pyplot as plt
import pytest


def test_validation_cases(monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda: None)
    from GHEtool.Validation.cases import check_cases, check_custom_datafile
    check_cases()
    check_custom_datafile()


@pytest.mark.slow
def test_sizing_method_comparison(monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda: None)
    from GHEtool.Validation.sizing_method_comparison import sizing_method_comparison
    sizing_method_comparison()


@pytest.mark.slow
def test_speed_comparison():
    from GHEtool.Validation.speed_comparison import test_10_boreholes, test_64_boreholes
    test_10_boreholes()
    test_64_boreholes()


@pytest.mark.slow
def test_compare_L2_L3_L4(monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda: None)
    from GHEtool.Validation.sizing_method_comparison_L2_L3_L4 import compare
    compare()


@pytest.mark.slow
def test_effective_borehole_thermal_resistance(monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda: None)
    from GHEtool.Validation.validation_effective_borehole_thermal_resistance import validate
    validate()


@pytest.mark.slow
def test_validate_deep_sizing(monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda: None)
    from GHEtool.Validation.validate_deep_sizing import validate
    validate()


def test_validation_ahmadfard():
    from GHEtool.Validation.comparison_with_other_sizing_tools.test1a.test1a import test_1a_1h, test_1a_6h
    from GHEtool.Validation.comparison_with_other_sizing_tools.test1b.test1b import test_1b
    from GHEtool.Validation.comparison_with_other_sizing_tools.test2.test2 import test_2_6h
    from GHEtool.Validation.comparison_with_other_sizing_tools.test3.test3 import test_3_6h
    from GHEtool.Validation.comparison_with_other_sizing_tools.test4.test4 import test_4
    from GHEtool.Validation.comparison_with_other_sizing_tools.test4.sensitivity_analysis import test_4_sensitivity
    test_1a_1h()
    test_1a_6h()
    test_1b()
    # test_2_6h()
    test_3_6h()
    test_4()
    test_4_sensitivity()
