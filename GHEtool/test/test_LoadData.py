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
    try:
        load.set_peak_cooling(np.ones(11))
    except ValueError:
        assert True
