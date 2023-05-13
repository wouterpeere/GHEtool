import pytest

import numpy as np

from GHEtool.VariableClasses import MonthlyGeothermalLoadAbsolute


def test_checks():
    load = MonthlyGeothermalLoadAbsolute()
    assert not load._check_input(2)
    assert not load._check_input(np.ones(11))
    assert not load._check_input(-1*np.ones(12))
    assert load._check_input([1]*12)
    assert load._check_input(np.ones(12))


def test_imbalance():
    load = MonthlyGeothermalLoadAbsolute(np.ones(12)*10, np.ones(12), np.ones(12), np.ones(12))
    assert load.imbalance == -108
    load = MonthlyGeothermalLoadAbsolute(np.ones(12), np.ones(12) * 10, np.ones(12), np.ones(12))
    assert load.imbalance == 108


def test_baseload_heating():
    load = MonthlyGeothermalLoadAbsolute()
    assert np.array_equal(load.baseload_heating, np.zeros(12))
    load.baseload_heating = np.linspace(0, 11, 12)
    assert np.array_equal(load.baseload_heating, np.linspace(0, 11, 12))
    load.set_baseload_heating(np.linspace(1, 12, 12))
    assert np.array_equal(load.baseload_heating, np.linspace(1, 12, 12))
    assert np.array_equal(load.baseload_heating / 730, load.baseload_heating_power)
    assert np.array_equal(load.baseload_heating_power, load.peak_heating)
    try:
        load.set_baseload_heating(np.ones(11))
    except ValueError:
        assert True


def test_baseload_cooling():
    load = MonthlyGeothermalLoadAbsolute()
    assert np.array_equal(load.baseload_cooling, np.zeros(12))
    load.baseload_cooling = np.linspace(0, 11, 12)
    assert np.array_equal(load.baseload_cooling, np.linspace(0, 11, 12))
    load.set_baseload_cooling(np.linspace(1, 12, 12))
    assert np.array_equal(load.baseload_cooling, np.linspace(1, 12, 12))
    assert np.array_equal(load.baseload_cooling / 730, load.baseload_cooling_power)
    assert np.array_equal(load.baseload_cooling_power, load.peak_cooling)

    try:
        load.set_baseload_cooling(np.ones(11))
    except ValueError:
        assert True


def test_peak_heating():
    load = MonthlyGeothermalLoadAbsolute()
    assert np.array_equal(load.peak_heating, np.zeros(12))
    load.peak_heating = np.linspace(0, 11, 12)
    assert np.array_equal(load.peak_heating, np.linspace(0, 11, 12))
    load.set_peak_heating(np.linspace(1, 12, 12))
    assert np.array_equal(load.peak_heating, np.linspace(1, 12, 12))
    load.set_baseload_heating(np.ones(12) * 730 * 5)
    assert np.array_equal(load.peak_heating, np.array([5., 5., 5., 5., 5., 6., 7., 8., 9., 10., 11., 12.]))
    try:
        load.set_peak_heating(np.ones(11))
    except ValueError:
        assert True


def test_peak_cooling():
    load = MonthlyGeothermalLoadAbsolute()
    assert np.array_equal(load.peak_cooling, np.zeros(12))
    load.peak_cooling = np.linspace(0, 11, 12)
    assert np.array_equal(load.peak_cooling, np.linspace(0, 11, 12))
    load.set_peak_cooling(np.linspace(1, 12, 12))
    assert np.array_equal(load.peak_cooling, np.linspace(1, 12, 12))
    load.set_baseload_cooling(np.ones(12) * 730 * 5)
    assert np.array_equal(load.peak_cooling, np.array([5.,  5.,  5.,  5.,  5.,  6.,  7.,  8.,  9., 10., 11., 12.]))
    try:
        load.set_peak_cooling(np.ones(11))
    except ValueError:
        assert True


def test_times():
    load = MonthlyGeothermalLoadAbsolute()
    load.peak_cooling_duration = 6
    load.peak_heating_duration = 7
    assert load.peak_heating_duration == 7 * 3600
    assert load.peak_cooling_duration == 6 * 3600
    load.peak_duration = 8
    assert load.peak_heating_duration == 8 * 3600
    assert load.peak_cooling_duration == 8 * 3600

    load.simulation_period = 20
    assert load.time_L3[-1] == 20 * 3600 * 8760
    assert load.time_L4[-1] == 20 * 3600 * 8760

    load.simulation_period = 100
    assert not np.isinf(load.time_L4.any())
