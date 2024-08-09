import pytest

import numpy as np

from GHEtool.VariableClasses import MonthlyBuildingLoadAbsolute, ResultsMonthly, ResultsHourly
from GHEtool.VariableClasses.Efficiency import *
from GHEtool.Validation.cases import load_case

scop = SCOP(6)
seer = SEER(5)
cop_basic = COP(np.array([1, 10]), np.array([1, 10]))
eer_basic = EER(np.array([1, 10]), np.array([1, 10]))
cop_pl = COP(np.array([[1, 10], [2, 20]]), np.array([1, 10]), range_part_load=np.array([0.5, 1]))
eer_pl = EER(np.array([[1, 10], [2, 20]]), np.array([1, 10]), range_part_load=np.array([0.5, 1]))

results_monthly = ResultsMonthly(np.linspace(0, 120 - 1, 120),
                                 np.linspace(0, 120 - 1, 120) * 2,
                                 np.linspace(0, 120 - 1, 120) * 3,
                                 np.linspace(0, 120 - 1, 120) * 4,
                                 np.linspace(0, 120 - 1, 120) * 5)
results_hourly = ResultsHourly(np.linspace(0, 87600 - 1, 87600),
                               np.linspace(0, 87600 - 1, 87600) * 2)


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


def test_monthly_baseload_heating():
    load = MonthlyBuildingLoadAbsolute(np.full(12, 0), np.full(12, 0), np.full(12, 0), np.full(12, 0), 10, 5, 5)
    assert np.allclose(load.monthly_baseload_heating, np.full(12, 0))
    load.baseload_heating = np.linspace(0, 11, 12)
    assert np.allclose(load.monthly_baseload_heating, np.linspace(0, 11, 12))
    load.set_baseload_heating(np.linspace(1, 12, 12))
    assert np.allclose(load.monthly_baseload_heating, np.linspace(1, 12, 12))
    assert np.allclose(load.monthly_baseload_heating / 730, load.monthly_baseload_heating_power)


def test_monthly_baseload_cooling():
    load = MonthlyBuildingLoadAbsolute(np.full(12, 0), np.full(12, 0), np.full(12, 0), np.full(12, 0), 10, 5, 5)
    assert np.allclose(load.monthly_baseload_cooling, np.full(12, 0))
    load.baseload_cooling = np.linspace(0, 11, 12)
    assert np.allclose(load.monthly_baseload_cooling, np.linspace(0, 11, 12))
    load.set_baseload_cooling(np.linspace(1, 12, 12))
    assert np.allclose(load.monthly_baseload_cooling, np.linspace(1, 12, 12))
    assert np.allclose(load.monthly_baseload_cooling / 730, load.monthly_baseload_cooling_power)


def test_monthly_peak_heating():
    load = MonthlyBuildingLoadAbsolute(np.full(12, 0), np.full(12, 0), np.full(12, 0), np.full(12, 0), 10, 5, 5)
    assert np.allclose(load.monthly_peak_heating, np.full(12, 0))
    load.peak_heating = np.linspace(0, 11, 12)
    assert np.allclose(load.monthly_peak_heating, np.linspace(0, 11, 12))
    load.set_peak_heating(np.linspace(1, 12, 12))
    assert np.allclose(load.monthly_peak_heating, np.linspace(1, 12, 12))
    load.set_baseload_heating(np.ones(12) * 730 * 5)
    assert np.allclose(load.monthly_peak_heating, np.array([5., 5., 5., 5., 5., 6., 7., 8., 9., 10., 11., 12.]))


def test_monthly_peak_cooling():
    load = MonthlyBuildingLoadAbsolute(np.full(12, 0), np.full(12, 0), np.full(12, 0), np.full(12, 0), 10, 5, 5)
    assert np.allclose(load.monthly_peak_cooling, np.full(12, 0))
    load.peak_cooling = np.linspace(0, 11, 12)
    assert np.allclose(load.monthly_peak_cooling, np.linspace(0, 11, 12))
    load.set_peak_cooling(np.linspace(1, 12, 12))
    assert np.allclose(load.monthly_peak_cooling, np.linspace(1, 12, 12))
    load.set_baseload_cooling(np.ones(12) * 730 * 5)
    assert np.allclose(load.monthly_peak_cooling, np.array([5., 5., 5., 5., 5., 6., 7., 8., 9., 10., 11., 12.]))
    with pytest.raises(ValueError):
        load.set_peak_cooling(np.ones(11))


def test_cop():
    load = MonthlyBuildingLoadAbsolute(*load_case(1), 10, scop, seer, 0, scop)
    assert load.cop == scop
    assert load.cop_dhw == scop
    assert load.eer == seer
    load.cop = SCOP(10)
    load.cop_dhw = SCOP(11)
    load.eer = SEER(1)
    assert load.cop == SCOP(10)
    assert load.cop_dhw == SCOP(11)
    assert load.eer == SEER(1)
    load.cop = 5
    load.cop_dhw = 6
    load.eer = 4
    assert load.cop == SCOP(5)
    assert load.cop_dhw == SCOP(6)
    assert load.eer == SEER(4)
    load.cop = cop_basic
    load.cop_dhw = cop_pl
    load.eer = eer_basic
    assert load.cop == cop_basic
    assert load.cop_dhw == cop_pl
    assert load.eer == eer_basic


def test_results():
    load10 = MonthlyBuildingLoadAbsolute(*load_case(1), 10, scop, seer)
    load9 = MonthlyBuildingLoadAbsolute(*load_case(1), 9, scop, seer)

    assert load10.results == (0, 17)
    assert load9.results == (0, 17)

    with pytest.raises(ValueError):
        load10.set_results(results_hourly)
    with pytest.raises(ValueError):
        load9.set_results(results_monthly)

    load10.set_results(results_monthly)
    assert load10.results == results_monthly


def test_reset_results():
    load = MonthlyBuildingLoadAbsolute(*load_case(1), 10, scop, seer)
    load.set_results(results_monthly)
    assert load.results == results_monthly
    load.reset_results(5, 10)
    assert load.results == (5, 10)


def test_times():
    load = MonthlyBuildingLoadAbsolute()
    load.peak_cooling_duration = 6
    load.peak_heating_duration = 7
    assert load.peak_heating_duration == 7 * 3600
    assert load.peak_cooling_duration == 6 * 3600
    assert load.peak_extraction_duration == 7 * 3600
    assert load.peak_injection_duration == 6 * 3600
    load.peak_duration = 8
    assert load.peak_heating_duration == 8 * 3600
    assert load.peak_cooling_duration == 8 * 3600
    assert load.peak_extraction_duration == 8 * 3600
    assert load.peak_injection_duration == 8 * 3600
    load.simulation_period = 20
    assert load.time_L3[-1] == 20 * 3600 * 8760
    assert load.time_L4[-1] == 20 * 3600 * 8760

    load.simulation_period = 100
    assert not np.isinf(load.time_L4.any())
    assert load.ty == 100 * 8760 * 3600
