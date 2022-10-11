import pytest
import matplotlib.pyplot as plt


def test_validation_cases(monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda: None)
    import GHEtool.Validation.cases


def test_sizing_method_comparison(monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda: None)
    import GHEtool.Validation.sizing_method_comparison


def test_sizing_with_Rb(monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda: None)
    import GHEtool.Validation.sizing_with_Rb_calculation


def test_speed_comparison():
    from GHEtool.Validation.speed_comparison import test_10_boreholes, test_64_boreholes
    test_10_boreholes()
    test_64_boreholes()
