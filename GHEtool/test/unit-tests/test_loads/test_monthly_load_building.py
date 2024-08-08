import pytest

import numpy as np

from GHEtool.VariableClasses import MonthlyBuildingLoadAbsolute
from GHEtool.VariableClasses.Efficiency import *
from GHEtool.Validation.cases import load_case


def test_checks():
    load = MonthlyBuildingLoadAbsolute(*load_case(1), 10, 5, 5)
    assert not load._check_input(2)
    assert not load._check_input(np.ones(11))
    assert not load._check_input(-1 * np.ones(12))
    assert load._check_input([1] * 12)
    assert load._check_input(np.ones(12))


def test_start_month_general():
    load = MonthlyBuildingLoadAbsolute(*load_case(1), 10, 5, 5)
    assert load.start_month == 1
    with pytest.raises(ValueError):
        load.start_month = 1.5
    with pytest.raises(ValueError):
        load.start_month = 0
    with pytest.raises(ValueError):
        load.start_month = 13
    load.start_month = 12
    assert load.start_month == 12
    load.start_month = 1
    assert load.start_month == 1


def test_monthly_baseload_heating_simulation_period():
    load = MonthlyBuildingLoadAbsolute(*load_case(1), 10, 5, 5)
    assert np.allclose(load.monthly_baseload_heating_simulation_period, np.tile(load_case(1)[0], 10))
    assert np.allclose(load.monthly_baseload_extraction_simulation_period, np.tile(load_case(1)[0] / 5, 10))


def test_monthly_baseload_cooling_simulation_period():
    load = MonthlyBuildingLoadAbsolute(*load_case(1), 10, 5, 5)
    assert np.allclose(load.monthly_baseload_cooling_simulation_period, np.tile(load_case(1)[1], 10))
    assert np.allclose(load.monthly_baseload_injection_simulation_period, np.tile(load_case(1)[1] / 5, 10))


def test_monthly_peak_heating_simulation_period():
    load = MonthlyBuildingLoadAbsolute(*load_case(1), 10, 5, 5)
    load.peak_heating = np.full(12, 240)
    assert np.allclose(load.monthly_peak_heating_simulation_period, np.tile(np.full(12, 240), 10))
    assert np.allclose(load.monthly_peak_extraction_simulation_period, np.tile(np.full(12, 240) / 5, 10))


def test_monthly_peak_cooling_simulation_period():
    load = MonthlyBuildingLoadAbsolute(*load_case(1), 10, 5, 5)
    load.peak_cooling = np.full(12, 240)
    assert np.allclose(load.monthly_peak_cooling_simulation_period, np.tile(np.full(12, 240), 10))
    assert np.allclose(load.monthly_peak_injection_simulation_period, np.tile(np.full(12, 240) / 5, 10))


def test_baseload_heating():
    load = MonthlyBuildingLoadAbsolute(np.full(12, 0), np.full(12, 0), np.full(12, 0), np.full(12, 0), 10, 5, 5)
    assert np.allclose(load.baseload_heating, np.full(12, 0))
    load.baseload_heating = np.linspace(0, 11, 12)
    assert np.allclose(load.baseload_heating, np.linspace(0, 11, 12))
    load.set_baseload_heating(np.linspace(1, 12, 12))
    assert np.allclose(load.baseload_heating, np.linspace(1, 12, 12))
    assert np.allclose(load.baseload_heating / 730, load.monthly_baseload_heating_power)
    assert np.allclose(load.monthly_baseload_heating_power, load.peak_heating)
    with pytest.raises(ValueError):
        load.set_baseload_heating(np.ones(11))


def test_baseload_cooling():
    load = MonthlyBuildingLoadAbsolute(np.full(12, 0), np.full(12, 0), np.full(12, 0), np.full(12, 0), 10, 5, 5)
    assert np.allclose(load.baseload_cooling, np.full(12, 0))
    load.baseload_cooling = np.linspace(0, 11, 12)
    assert np.allclose(load.baseload_cooling, np.linspace(0, 11, 12))
    load.set_baseload_cooling(np.linspace(1, 12, 12))
    assert np.allclose(load.baseload_cooling, np.linspace(1, 12, 12))
    assert np.allclose(load.baseload_cooling / 730, load.monthly_baseload_cooling_power)
    assert np.allclose(load.monthly_baseload_cooling_power, load.peak_cooling)

    with pytest.raises(ValueError):
        load.set_baseload_cooling(np.ones(11))


def test_peak_heating():
    load = MonthlyBuildingLoadAbsolute(np.full(12, 0), np.full(12, 0), np.full(12, 0), np.full(12, 0), 10, 5, 5)
    assert np.allclose(load.peak_heating, np.full(12, 0))
    load.peak_heating = np.linspace(0, 11, 12)
    assert np.allclose(load.peak_heating, np.linspace(0, 11, 12))
    load.set_peak_heating(np.linspace(1, 12, 12))
    assert np.allclose(load.peak_heating, np.linspace(1, 12, 12))
    load.set_baseload_heating(np.ones(12) * 730 * 5)
    assert np.allclose(load.peak_heating, np.array([5., 5., 5., 5., 5., 6., 7., 8., 9., 10., 11., 12.]))
    with pytest.raises(ValueError):
        load.set_peak_heating(np.ones(11))


def test_peak_cooling():
    load = MonthlyBuildingLoadAbsolute(np.full(12, 0), np.full(12, 0), np.full(12, 0), np.full(12, 0), 10, 5, 5)
    assert np.allclose(load.peak_cooling, np.full(12, 0))
    load.peak_cooling = np.linspace(0, 11, 12)
    assert np.allclose(load.peak_cooling, np.linspace(0, 11, 12))
    load.set_peak_cooling(np.linspace(1, 12, 12))
    assert np.allclose(load.peak_cooling, np.linspace(1, 12, 12))
    load.set_baseload_cooling(np.ones(12) * 730 * 5)
    assert np.allclose(load.peak_cooling, np.array([5., 5., 5., 5., 5., 6., 7., 8., 9., 10., 11., 12.]))
    with pytest.raises(ValueError):
        load.set_peak_cooling(np.ones(11))
