import pytest

import numpy as np

from GHEtool.VariableClasses import MonthlyGeothermalLoadAbsolute
from GHEtool.test.test_GHEtool_two import load_case


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
    assert load.ty == 100 * 8760 * 3600


def test_monthly_average_load():
    load = MonthlyGeothermalLoadAbsolute()
    load.baseload_cooling = np.ones(12) * 400
    load.baseload_heating = np.ones(12) * 500

    assert np.isclose(np.average(load.baseload_cooling_power) * 8760, 400 * 12)
    assert np.isclose(np.average(load.baseload_heating_power) * 8760, 500 * 12)
    assert np.array_equal(load.baseload_cooling_power, load.peak_cooling)
    assert np.array_equal(load.baseload_heating_power, load.peak_heating)

    assert np.array_equal(load.baseload_cooling_power_simulation_period,
                          np.tile(load.baseload_cooling_power, 20))
    assert np.array_equal(load.baseload_heating_power_simulation_period,
                          np.tile(load.baseload_heating_power, 20))
    assert np.array_equal(load.peak_heating_simulation_period,
                          np.tile(load.peak_heating, 20))
    assert np.array_equal(load.peak_cooling_simulation_period,
                          np.tile(load.peak_cooling, 20))
    assert np.array_equal(load.baseload_cooling_simulation_period,
                   np.tile(load.baseload_cooling, 20))
    assert np.array_equal(load.baseload_heating_simulation_period,
                          np.tile(load.baseload_heating, 20))

    assert np.array_equal(load.monthly_average_load, load.baseload_cooling_power-load.baseload_heating_power)
    assert np.array_equal(load.monthly_average_load_simulation_period,
                          load.baseload_cooling_power_simulation_period-load.baseload_heating_power_simulation_period)

    # test now with different month loads
    temp_cooling = load.baseload_cooling_power
    temp_heating = load.baseload_heating_power

    load.all_months_equal = False
    assert not np.array_equal(load.baseload_cooling_power, temp_cooling)
    assert not np.array_equal(load.baseload_heating_power, temp_heating)

    assert np.isclose(np.sum(np.multiply(load.baseload_cooling_power, load.UPM)), 400 * 12)
    assert np.isclose(np.sum(np.multiply(load.baseload_heating_power, load.UPM)), 500 * 12)


def test_params_last_year():
    monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(2)
    load = MonthlyGeothermalLoadAbsolute(monthly_load_heating, monthly_load_cooling, peak_heating, peak_cooling)
    assert np.array_equal(load._calculate_last_year_params(False),
                          (21600.0, 240000.0, 65753.42465753425, 9132.420091324202))
    assert np.array_equal(load._calculate_last_year_params(True),
                          (21600.0, 160000.0, 25753.424657534248, -9132.420091324202))
    load.peak_heating = np.ones(12) * 160
    load.peak_cooling = np.ones(12) * 240
    assert np.array_equal(load._calculate_last_year_params(False),
                          (21600.0, 240000.0, 65753.42465753425, 9132.420091324202))
    assert np.array_equal(load._calculate_last_year_params(True),
                          (21600.0, 160000.0, 25753.424657534248, -9132.420091324202))


def test_params_first_year():
    monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(2)
    load = MonthlyGeothermalLoadAbsolute(monthly_load_heating, monthly_load_cooling, peak_heating, peak_cooling)
    assert np.array_equal(load._calculate_first_year_params(False),
                          (21600.0, 18396000.0, 21024000.0, 240000.0, 6410.9589041095915, 65753.42465753425))
    assert np.array_equal(load._calculate_first_year_params(True),
                          (21600.0, 0, 2628000.0, 160000.0, 0, 25753.424657534248))
    load.peak_heating = np.ones(12) * 160
    load.peak_cooling = np.ones(12) * 240

    assert np.array_equal(load._calculate_first_year_params(False),
                          (21600.0, 15768000.0, 18396000.0, 240000.0, -2066.536203522503, 65753.42465753425))
    assert np.array_equal(load._calculate_first_year_params(True),
                          (21600.0, 0, 2628000.0, 160000.0, 0, 25753.424657534248))
