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
