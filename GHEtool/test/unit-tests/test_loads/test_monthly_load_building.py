import pytest

import numpy as np

from GHEtool.VariableClasses import MonthlyBuildingLoadAbsolute, ResultsMonthly, ResultsHourly
from GHEtool.VariableClasses.Efficiency import *
from GHEtool.Validation.cases import load_case

scop = SCOP(6)
seer = SEER(5)
cop_basic = COP(np.array([2, 20]), np.array([1, 10]))
eer_basic = EER(np.array([2, 20]), np.array([1, 10]))
cop_pl = COP(np.array([2, 20, 4, 40]), np.array([[1, 0.5], [10, 0.5], [1, 1], [10, 1]]), part_load=True)
eer_pl = EER(np.array([2, 20, 4, 40]), np.array([[1, 0.5], [10, 0.5], [1, 1], [10, 1]]), part_load=True)
results_monthly = ResultsMonthly(np.linspace(0, 120 - 1, 120),
                                 np.linspace(0, 120 - 1, 120) * 2,
                                 np.linspace(0, 120 - 1, 120) * 3,
                                 np.linspace(0, 120 - 1, 120) * 4,
                                 np.linspace(0, 120 - 1, 120) * 5)
temp = np.array([0, 0, 0, 0, 0, 0, 5, 5, 5, 5, 5, 5])
results_monthly_test = ResultsMonthly(np.tile(temp, 10),
                                      np.tile(temp, 10),
                                      np.tile(temp, 10),
                                      np.tile(temp, 10),
                                      np.tile(temp, 10))
results_hourly = ResultsHourly(np.linspace(0, 87600 - 1, 87600),
                               np.linspace(0, 87600 - 1, 87600) * 2)

test_load = np.array([5, 5, 5, 5, 5, 5, 10, 10, 10, 10, 10, 10])
test_load_sim_per = np.tile(test_load, 10)


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


def test_different_start_month():
    load = MonthlyBuildingLoadAbsolute(baseload_heating=np.arange(1, 13, 1),
                                       baseload_cooling=np.arange(1, 13, 1),
                                       peak_cooling=np.arange(1, 13, 1),
                                       peak_heating=np.arange(1, 13, 1))
    load.start_month = 2
    result = np.array([2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1])
    assert np.allclose(load.baseload_heating, result)
    assert np.allclose(load.baseload_cooling, result)
    assert np.allclose(load.peak_heating, result)
    assert np.allclose(load.peak_cooling, result)
    assert np.allclose(load.monthly_baseload_heating_simulation_period, np.tile(result, 20))
    assert np.allclose(load.monthly_baseload_cooling_simulation_period, np.tile(result, 20))
    assert np.allclose(load.monthly_peak_heating_simulation_period, np.tile(result, 20))
    assert np.allclose(load.monthly_peak_cooling_simulation_period, np.tile(result, 20))

    load.peak_cooling = np.zeros(12)
    load.peak_heating = np.zeros(12)
    assert np.allclose(load.monthly_peak_heating_simulation_period, np.tile(result, 20) / 730)
    assert np.allclose(load.monthly_peak_cooling_simulation_period, np.tile(result, 20) / 730)


def test_monthly_baseload_heating_simulation_period():
    load = MonthlyBuildingLoadAbsolute(*load_case(1), 10, 5, 5)
    assert np.allclose(load.monthly_baseload_heating_simulation_period, np.tile(load_case(1)[0], 10))
    assert np.allclose(load.monthly_baseload_extraction_simulation_period, np.tile(load_case(1)[0] * 4 / 5, 10))
    load.peak_heating = np.zeros(12)
    assert np.allclose(load.monthly_peak_extraction_simulation_period,
                       load.monthly_baseload_extraction_power_simulation_period)


def test_monthly_baseload_cooling_simulation_period():
    load = MonthlyBuildingLoadAbsolute(*load_case(1), 10, 5, 5)
    assert np.allclose(load.monthly_baseload_cooling_simulation_period, np.tile(load_case(1)[1], 10))
    assert np.allclose(load.monthly_baseload_injection_simulation_period, np.tile(load_case(1)[1] * 6 / 5, 10))
    load.peak_cooling = np.zeros(12)
    assert np.allclose(load.monthly_peak_injection_simulation_period,
                       load.monthly_baseload_injection_power_simulation_period)


def test_monthly_peak_heating_simulation_period():
    load = MonthlyBuildingLoadAbsolute(*load_case(1), 10, 5, 5)
    load.peak_heating = np.full(12, 240)
    assert np.allclose(load.monthly_peak_heating_simulation_period, np.tile(np.full(12, 240), 10))
    assert np.allclose(load.monthly_peak_extraction_simulation_period, np.tile(np.full(12, 240) * 4 / 5, 10))


def test_monthly_peak_cooling_simulation_period():
    load = MonthlyBuildingLoadAbsolute(*load_case(1), 10, 5, 5)
    load.peak_cooling = np.full(12, 240)
    assert np.allclose(load.monthly_peak_cooling_simulation_period, np.tile(np.full(12, 240), 10))
    assert np.allclose(load.monthly_peak_injection_simulation_period, np.tile(np.full(12, 240) * 6 / 5, 10))


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


def test_dhw_simulation_period():
    load = MonthlyBuildingLoadAbsolute(np.full(12, 0), np.full(12, 0), np.full(12, 0), np.full(12, 0), 10, 5, 5)
    assert np.array_equal(load.monthly_baseload_dhw_simulation_period, np.zeros(120))
    assert np.array_equal(load.monthly_baseload_dhw_power_simulation_period, np.zeros(120))
    assert np.array_equal(load.yearly_dhw_load_simulation_period, np.zeros(10))
    load.dhw = 8760
    assert np.array_equal(load.monthly_baseload_dhw_simulation_period, np.full(120, 730))
    assert np.array_equal(load.monthly_baseload_dhw_power_simulation_period, np.ones(120))
    assert np.array_equal(load.yearly_dhw_load_simulation_period, np.full(10, 8760))


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


def test_get_monthly_cop():
    load = MonthlyBuildingLoadAbsolute(*load_case(1), 10, scop, seer)
    load.reset_results(5, 10)
    assert load._get_monthly_cop(False) == 6
    assert load._get_monthly_cop(True) == 6
    load.set_results(results_monthly)
    assert np.allclose(load._get_monthly_cop(False), np.full(120, 6))
    assert np.allclose(load._get_monthly_cop(True), np.full(120, 6))


def test_get_monthly_cop_dhw():
    load = MonthlyBuildingLoadAbsolute(*load_case(1), 10, 4, seer, 0, scop)
    load.reset_results(5, 10)
    assert load._get_monthly_cop_dhw(False) == 6
    assert load._get_monthly_cop_dhw(True) == 6
    load.set_results(results_monthly)
    assert np.allclose(load._get_monthly_cop_dhw(False), np.full(120, 6))
    assert np.allclose(load._get_monthly_cop_dhw(True), np.full(120, 6))


def test_get_monthly_eer():
    load = MonthlyBuildingLoadAbsolute(*load_case(1), 10, scop, seer)
    load.reset_results(5, 10)
    assert load._get_monthly_eer(False) == 5
    assert load._get_monthly_eer(True) == 5
    load.set_results(results_monthly)
    assert np.allclose(load._get_monthly_eer(False), np.full(120, 5))
    assert np.allclose(load._get_monthly_eer(True), np.full(120, 5))


def test_conversion():
    load = MonthlyBuildingLoadAbsolute()
    assert load.conversion_factor_secondary_to_primary_cooling(5) == 1 + 1 / 5
    assert load.conversion_factor_secondary_to_primary_heating(5) == 1 - 1 / 5


def test_monthly_baseload_injection_simulation_period():
    load = MonthlyBuildingLoadAbsolute(*load_case(2), 10, scop, seer)
    load.baseload_cooling = test_load
    load.peak_cooling = np.full(12, 10)
    assert np.allclose(load.monthly_baseload_injection_simulation_period, test_load_sim_per * 6 / 5)
    load.eer = eer_basic
    load.reset_results(0, 1)
    assert np.allclose(load.monthly_baseload_injection_simulation_period, test_load_sim_per * 3 / 2)
    load.reset_results(0, 10)
    assert np.allclose(load.monthly_baseload_injection_simulation_period, test_load_sim_per * 21 / 20)
    load.set_results(results_monthly_test)
    assert np.allclose(load.monthly_baseload_injection_simulation_period,
                       np.tile(np.array([7.5, 7.5, 7.5, 7.5, 7.5, 7.5, 11, 11, 11, 11, 11, 11]), 10))
    load.eer = eer_pl
    load.reset_results(0, 1)
    assert np.allclose(load.monthly_baseload_injection_simulation_period,
                       np.tile(np.array([7.5, 7.5, 7.5, 7.5, 7.5, 7.5, 15, 15, 15, 15, 15, 15]), 10))
    load.reset_results(0, 10)
    assert np.allclose(load.monthly_baseload_injection_simulation_period,
                       np.tile(np.array([6.25, 6.25, 6.25, 6.25, 6.25, 6.25, 12.5, 12.5, 12.5, 12.5, 12.5, 12.5]), 10))
    load.set_results(results_monthly_test)
    assert np.allclose(load.monthly_baseload_injection_simulation_period,
                       np.tile(np.array(
                           [7.5, 7.5, 7.5, 7.5, 7.5, 7.5, 13.46153846, 13.46153846, 13.46153846, 13.46153846,
                            13.46153846, 13.46153846]), 10))


def test_monthly_baseload_extraction_simulation_period():
    load = MonthlyBuildingLoadAbsolute(*load_case(2), 10, scop, seer)
    load.baseload_heating = test_load
    load.peak_heating = np.full(12, 10)
    assert np.allclose(load.monthly_baseload_extraction_simulation_period, test_load_sim_per * 5 / 6)
    load.cop = cop_basic
    load.reset_results(1, 11)
    assert np.allclose(load.monthly_baseload_extraction_simulation_period, test_load_sim_per * 1 / 2)
    load.reset_results(10, 110)
    assert np.allclose(load.monthly_baseload_extraction_simulation_period, test_load_sim_per * 19 / 20)
    load.set_results(results_monthly_test)
    assert np.allclose(load.monthly_baseload_extraction_simulation_period,
                       np.tile(np.array([2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 9, 9, 9, 9, 9, 9]), 10))
    load.cop = cop_pl
    load.reset_results(1, 11)
    assert np.allclose(load.monthly_baseload_extraction_simulation_period,
                       np.tile(np.array([2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 5., 5., 5., 5., 5., 5.]), 10))
    load.reset_results(10, 110)
    assert np.allclose(load.monthly_baseload_extraction_simulation_period,
                       np.tile(np.array([3.75, 3.75, 3.75, 3.75, 3.75, 3.75, 7.5, 7.5, 7.5, 7.5, 7.5, 7.5]), 10))
    load.set_results(results_monthly_test)
    assert np.allclose(load.monthly_baseload_extraction_simulation_period,
                       np.tile(np.array(
                           [2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 6.53846154, 6.53846154, 6.53846154, 6.53846154, 6.53846154,
                            6.53846154]), 10))

    # now with only DHW
    load.cop_dhw = scop
    load.baseload_heating = np.zeros(12)
    load.dhw = test_load
    assert np.allclose(load.monthly_baseload_extraction_simulation_period, test_load_sim_per * 5 / 6)
    load.cop_dhw = cop_basic
    load.reset_results(1, 11)
    assert np.allclose(load.monthly_baseload_extraction_simulation_period, test_load_sim_per * 1 / 2)
    load.reset_results(10, 110)
    assert np.allclose(load.monthly_baseload_extraction_simulation_period, test_load_sim_per * 19 / 20)
    load.set_results(results_monthly_test)
    assert np.allclose(load.monthly_baseload_extraction_simulation_period,
                       np.tile(np.array([2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 9, 9, 9, 9, 9, 9]), 10))
    # this will follow the data for the baseload, since the part load data is the same, because peak_heating is not
    # relevant for the dhw power
    load.cop_dhw = cop_pl
    load.reset_results(1, 11)
    assert np.allclose(load.monthly_baseload_extraction_simulation_period,
                       np.tile(np.array([2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 9.5, 9.5, 9.5, 9.5, 9.5, 9.5]), 10))
    load.reset_results(10, 110)
    assert np.allclose(load.monthly_baseload_extraction_simulation_period,
                       np.tile(np.array([3.75, 3.75, 3.75, 3.75, 3.75, 3.75, 9.75, 9.75, 9.75, 9.75, 9.75, 9.75]), 10))
    load.set_results(results_monthly_test)
    assert np.allclose(load.monthly_baseload_extraction_simulation_period,
                       np.tile(np.array(
                           [2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 9.65384615, 9.65384615, 9.65384615, 9.65384615, 9.65384615,
                            9.65384615]), 10))


def test_monthly_peak_injection_simulation_period():
    load = MonthlyBuildingLoadAbsolute(*load_case(2), 10, scop, seer)
    load.peak_cooling = test_load
    load.baseload_cooling = np.full(12, 10)
    assert np.allclose(load.monthly_peak_injection_simulation_period, test_load_sim_per * 6 / 5)
    load.eer = eer_basic
    load.reset_results(0, 1)
    assert np.allclose(load.monthly_peak_injection_simulation_period, test_load_sim_per * 3 / 2)
    load.reset_results(0, 10)
    assert np.allclose(load.monthly_peak_injection_simulation_period, test_load_sim_per * 21 / 20)
    load.set_results(results_monthly_test)
    assert np.allclose(load.monthly_peak_injection_simulation_period,
                       np.tile(np.array([7.5, 7.5, 7.5, 7.5, 7.5, 7.5, 11, 11, 11, 11, 11, 11]), 10))
    load.eer = eer_pl
    load.reset_results(0, 1)
    assert np.allclose(load.monthly_peak_injection_simulation_period,
                       np.tile(np.array([7.5, 7.5, 7.5, 7.5, 7.5, 7.5, 10.5, 10.5, 10.5, 10.5, 10.5, 10.5]), 10))
    load.reset_results(0, 10)
    assert np.allclose(load.monthly_peak_injection_simulation_period,
                       np.tile(
                           np.array([6.25, 6.25, 6.25, 6.25, 6.25, 6.25, 10.25, 10.25, 10.25, 10.25, 10.25, 10.25]),
                           10))
    load.set_results(results_monthly_test)
    assert np.allclose(load.monthly_peak_injection_simulation_period,
                       np.tile(np.array(
                           [7.5, 7.5, 7.5, 7.5, 7.5, 7.5, 10.34615385, 10.34615385, 10.34615385, 10.34615385,
                            10.34615385, 10.34615385]), 10))


def test_monthly_peak_extraction_simulation_period():
    load = MonthlyBuildingLoadAbsolute(*load_case(2), 10, scop, seer)
    load.peak_heating = test_load
    load.baseload_heating = np.full(12, 10)
    assert np.allclose(load.monthly_peak_extraction_simulation_period, test_load_sim_per * 5 / 6)
    load.cop = cop_basic
    load.reset_results(1, 11)
    assert np.allclose(load.monthly_peak_extraction_simulation_period, test_load_sim_per * 1 / 2)
    load.reset_results(10, 110)
    assert np.allclose(load.monthly_peak_extraction_simulation_period, test_load_sim_per * 19 / 20)
    load.set_results(results_monthly_test)
    assert np.allclose(load.monthly_peak_extraction_simulation_period,
                       np.tile(np.array([2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 9, 9, 9, 9, 9, 9]), 10))
    load.cop = cop_pl
    load.reset_results(1, 11)
    assert np.allclose(load.monthly_peak_extraction_simulation_period,
                       np.tile(np.array([2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 9.5, 9.5, 9.5, 9.5, 9.5, 9.5]), 10))
    load.reset_results(10, 110)
    assert np.allclose(load.monthly_peak_extraction_simulation_period,
                       np.tile(np.array([3.75, 3.75, 3.75, 3.75, 3.75, 3.75, 9.75, 9.75, 9.75, 9.75, 9.75, 9.75]),
                               10))
    load.set_results(results_monthly_test)
    assert np.allclose(load.monthly_peak_extraction_simulation_period,
                       np.tile(np.array(
                           [2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 9.65384615, 9.65384615, 9.65384615, 9.65384615, 9.65384615,
                            9.65384615]), 10))

    # now with only DHW
    load.cop_dhw = scop
    load.peak_heating = np.zeros(12)
    load.baseload_heating = np.zeros(12)
    load.dhw = test_load * 730
    assert np.allclose(load.monthly_peak_extraction_simulation_period, test_load_sim_per * 5 / 6)
    load.cop_dhw = cop_basic
    load.reset_results(1, 11)
    assert np.allclose(load.monthly_peak_extraction_simulation_period, test_load_sim_per * 1 / 2)
    load.reset_results(10, 110)
    assert np.allclose(load.monthly_peak_extraction_simulation_period, test_load_sim_per * 19 / 20)
    load.set_results(results_monthly_test)
    assert np.allclose(load.monthly_peak_extraction_simulation_period,
                       np.tile(np.array([2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 9, 9, 9, 9, 9, 9]), 10))
    load.cop_dhw = cop_pl
    load.reset_results(1, 11)
    assert np.allclose(load.monthly_peak_extraction_simulation_period,
                       np.tile(np.array([2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 9.5, 9.5, 9.5, 9.5, 9.5, 9.5]), 10))
    load.reset_results(10, 110)
    assert np.allclose(load.monthly_peak_extraction_simulation_period,
                       np.tile(np.array([3.75, 3.75, 3.75, 3.75, 3.75, 3.75, 9.75, 9.75, 9.75, 9.75, 9.75, 9.75]),
                               10))
    load.set_results(results_monthly_test)
    assert np.allclose(load.monthly_peak_extraction_simulation_period,
                       np.tile(np.array(
                           [2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 9.65384615, 9.65384615, 9.65384615, 9.65384615, 9.65384615,
                            9.65384615]), 10))


def test_max_loads():
    load = MonthlyBuildingLoadAbsolute(*load_case(2), 10, scop, seer)
    assert load.max_peak_heating == 160
    assert load.max_peak_cooling == 240
    assert load.max_peak_injection == 240 / 5 * 6
    assert load.max_peak_extraction == 160 / 6 * 5


def test_yearly_loads():
    baseload_heating = np.array([1000] * 12)  # 1000 kWh/month for each month
    baseload_cooling = np.array([500] * 12)  # 500 kWh/month for each month
    peak_heating = np.array([50] * 12)  # 50 kW/month for each month
    peak_cooling = np.array([30] * 12)  # 30 kW/month for each month

    # Initialize the MonthlyGeothermalLoadMultiYear object with test data
    load_data = MonthlyBuildingLoadAbsolute(
        baseload_heating=baseload_heating,
        baseload_cooling=baseload_cooling,
        peak_heating=peak_heating,
        peak_cooling=peak_cooling,
        simulation_period=2,
        dhw=8760
    )

    assert np.array_equal(load_data.yearly_cooling_load_simulation_period, [6000, 6000])
    assert np.array_equal(load_data.yearly_heating_load_simulation_period, [12000, 12000])
    assert np.array_equal(load_data.yearly_cooling_peak_simulation_period, [30, 30])
    assert np.array_equal(load_data.yearly_heating_peak_simulation_period, [50, 50])
    assert np.array_equal(load_data.yearly_dhw_load_simulation_period, [8760, 8760])
    assert np.isclose(load_data.yearly_average_cooling_load, 500 * 12)
    assert np.isclose(load_data.yearly_average_heating_load, 1000 * 12)
    assert np.isclose(load_data.yearly_average_dhw_load, 8760)


def test_dhw():
    load = MonthlyBuildingLoadAbsolute(*load_case(1), simulation_period=10)
    load.peak_heating = np.zeros(12)
    load.baseload_heating = np.zeros(12)

    assert load.dhw == 0
    assert np.allclose(load.baseload_cooling, load_case(1)[1])
    assert np.allclose(load.peak_cooling, np.array(
        [5.1369863, 10.2739726, 22., 44., 83., 117., 134., 150., 100., 23., 10.2739726, 5.1369863]))

    with pytest.raises(ValueError):
        load.add_dhw(-100)
    with pytest.raises(ValueError):
        load.add_dhw('test')
    with pytest.raises(ValueError):
        load.add_dhw(np.full(120, 10))
    with pytest.raises(ValueError):
        load.dhw = -100
    with pytest.raises(ValueError):
        load.dhw = 'test'
    with pytest.raises(ValueError):
        load.dhw = np.full(120, 10)

    assert np.allclose(load.dhw, 0)
    assert np.allclose(load.monthly_baseload_dhw, np.zeros(12))
    assert np.allclose(load.monthly_peak_dhw, np.zeros(12))
    assert np.allclose(load.monthly_baseload_dhw_simulation_period, np.zeros(120))
    assert np.allclose(load.monthly_baseload_dhw_power_simulation_period, np.zeros(120))
    assert np.allclose(load.monthly_peak_dhw_simulation_period, np.zeros(120))
    assert np.allclose(load.monthly_baseload_extraction_power_simulation_period, np.zeros(120))
    assert np.allclose(load.monthly_peak_extraction_simulation_period, np.zeros(120))
    assert np.allclose(load.yearly_dhw_load_simulation_period, np.zeros(10))
    assert np.isclose(load.yearly_average_dhw_load, 0)
    assert load.max_peak_dhw == 0
    load.exclude_DHW_from_peak = True
    assert np.allclose(load.monthly_peak_extraction_simulation_period, np.zeros(120))
    load.exclude_DHW_from_peak = False

    load.dhw = 730 * 12
    assert load.dhw == 730 * 12
    assert np.allclose(load.monthly_baseload_dhw, np.full(12, 730))
    assert np.allclose(load.monthly_peak_dhw, np.full(12, 1))
    assert np.allclose(load.monthly_baseload_dhw_simulation_period, np.full(120, 730))
    assert np.allclose(load.monthly_baseload_dhw_power_simulation_period, np.full(120, 1))
    assert np.allclose(load.monthly_peak_dhw_simulation_period, np.full(120, 1))
    assert np.allclose(load.monthly_baseload_extraction_power_simulation_period, np.full(120, 1) * 3 / 4)
    assert np.allclose(load.monthly_peak_extraction_simulation_period, np.full(120, 1) * 3 / 4)
    assert np.allclose(load.yearly_dhw_load_simulation_period, np.full(10, 730 * 12))
    assert load.max_peak_dhw == 1
    assert np.isclose(load.yearly_average_dhw_load, 730 * 12)
    load.exclude_DHW_from_peak = True
    assert np.allclose(load.monthly_peak_extraction_simulation_period, np.zeros(120))
    load.exclude_DHW_from_peak = False

    load.dhw = np.linspace(1, 12, 12) * 730
    assert np.allclose(load.dhw, np.linspace(1, 12, 12) * 730)
    assert np.allclose(load.monthly_baseload_dhw, np.linspace(1, 12, 12) * 730)
    assert np.allclose(load.monthly_peak_dhw, np.linspace(1, 12, 12))
    assert np.allclose(load.monthly_baseload_dhw_simulation_period, np.tile(np.linspace(1, 12, 12) * 730, 10))
    assert np.allclose(load.monthly_baseload_dhw_power_simulation_period, np.tile(np.linspace(1, 12, 12), 10))
    assert np.allclose(load.monthly_peak_dhw_simulation_period, np.tile(np.linspace(1, 12, 12), 10))
    assert np.allclose(load.monthly_baseload_extraction_power_simulation_period,
                       np.tile(np.linspace(1, 12, 12), 10) * 3 / 4)
    assert np.allclose(load.monthly_peak_extraction_simulation_period, np.tile(np.linspace(1, 12, 12), 10) * 3 / 4)
    assert np.allclose(load.yearly_dhw_load_simulation_period, np.full(10, np.sum(np.linspace(1, 12, 12) * 730)))
    assert np.isclose(load.yearly_average_dhw_load, np.sum(np.linspace(1, 12, 12) * 730))
    assert load.max_peak_dhw == 12
    load.exclude_DHW_from_peak = True
    assert np.allclose(load.monthly_peak_extraction_simulation_period, np.zeros(120))
