import pytest

import matplotlib.pyplot as plt
import numpy as np

from GHEtool import FOLDER
from GHEtool.VariableClasses import HourlyBuildingLoad, Cluster
from GHEtool.VariableClasses.Result import ResultsMonthly, ResultsHourly

from GHEtool.VariableClasses.Efficiency import *

scop = SCOP(6)
seer = SEER(5)
cop_basic = COP(np.array([2, 20]), np.array([1, 10]))
eer_basic = EER(np.array([2, 20]), np.array([1, 10]))
cop_pl = COP(np.array([2, 20, 4, 40]), np.array([[1, 0.5], [10, 0.5], [1, 1], [10, 1]]), part_load=True)
eer_pl = EER(np.array([2, 20, 4, 40]), np.array([[1, 0.5], [10, 0.5], [1, 1], [10, 1]]), part_load=True)

results_monthly1 = ResultsMonthly(np.linspace(0, 120 - 1, 12),
                                  np.linspace(0, 120 - 1, 12) * 2,
                                  np.linspace(0, 120 - 1, 12) * 3,
                                  np.linspace(0, 120 - 1, 12) * 4,
                                  np.linspace(0, 120 - 1, 12) * 5)
results_monthly2 = ResultsMonthly(np.linspace(0, 120 - 1, 24),
                                  np.linspace(0, 120 - 1, 24) * 2,
                                  np.linspace(0, 120 - 1, 24) * 3,
                                  np.linspace(0, 120 - 1, 24) * 4,
                                  np.linspace(0, 120 - 1, 24) * 5)
temp = np.concatenate((np.zeros(4380), np.full(4380, 5)))
results_hourly_test = ResultsHourly(np.tile(temp, 10), np.tile(temp, 10))
test_load = temp + 5
test_load_sim_per = np.tile(test_load, 10)

temp = np.array([0, 0, 0, 0, 0, 0, 5, 5, 5, 5, 5, 5])
results_monthly_test = ResultsMonthly(np.tile(temp, 10),
                                      np.tile(temp, 10),
                                      np.tile(temp, 10),
                                      np.tile(temp, 10),
                                      np.tile(temp, 10))

results_hourly1 = ResultsHourly(np.linspace(0, 8760 * 2 - 1, 8760),
                                np.linspace(0, 8760 * 2 - 1, 8760) * 2)
results_hourly2 = ResultsHourly(np.linspace(0, 8760 * 2 - 1, 8760 * 2),
                                np.linspace(0, 8760 * 2 - 1, 8760 * 2) * 2)


def test_load_hourly_data():
    load = HourlyBuildingLoad()
    load.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"))
    load1 = HourlyBuildingLoad()
    load1.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"), col_heating=1, col_cooling=0)
    assert np.array_equal(load.hourly_cooling_load, load1.hourly_heating_load)
    assert np.array_equal(load.hourly_heating_load, load1.hourly_cooling_load)
    load2 = HourlyBuildingLoad()
    load2.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/hourly_profile_without_header.csv"),
                              header=False)
    assert np.array_equal(load.hourly_cooling_load, load2.hourly_cooling_load)
    assert np.array_equal(load.hourly_heating_load, load2.hourly_heating_load)


def test_checks():
    load = HourlyBuildingLoad()
    assert not load._check_input(2)
    assert not load._check_input(np.ones(8759))
    assert not load._check_input(-1 * np.ones(8760))
    assert load._check_input([1] * 8760)
    assert load._check_input(np.ones(8760))


def test_imbalance():
    load = HourlyBuildingLoad(np.ones(8760) * 10, np.ones(8760))
    assert np.isclose(load.imbalance, -60882)
    load = HourlyBuildingLoad(np.ones(8760), np.ones(8760) * 10)
    assert np.isclose(load.imbalance, 84972)
    load.dhw = 8000
    assert np.isclose(load.imbalance, 84972 - 8000 * 3 / 4)


def test_load_duration(monkeypatch):
    monkeypatch.setattr(plt, "show", lambda: None)
    load = HourlyBuildingLoad(np.ones(8760) * 10, np.ones(8760))
    load.plot_load_duration(legend=True)


def test_resample_to_monthly():
    load = HourlyBuildingLoad()
    peak, baseload = load.resample_to_monthly(np.tile(np.linspace(0, 729, 730), 12))
    assert np.array_equal(peak, np.ones(12) * 729)
    assert np.array_equal(baseload, np.ones(12) * 266085)
    load.all_months_equal = False
    peak, baseload = load.resample_to_monthly(np.tile(np.linspace(0, 729, 730), 12))
    assert np.array_equal(peak, np.array([729., 685., 729., 729., 729., 729., 729., 729., 729., 729., 729., 729.]))
    assert np.array_equal(baseload, np.array([266176., 234864., 275780., 259140., 275836., 259100.,
                                              275892., 276088., 258920., 276144., 258880., 276200.]))


def test_yearly_loads():
    load = HourlyBuildingLoad(heating_load=np.linspace(0, 8759, 8760),
                              cooling_load=np.linspace(0, 8759, 8760) * 2,
                              simulation_period=10)
    assert np.array_equal(load.yearly_cooling_load_simulation_period, [76728840] * 10)
    assert np.array_equal(load.yearly_heating_load_simulation_period, [38364420] * 10)
    assert np.array_equal(load.yearly_cooling_peak_simulation_period, [17518] * 10)
    assert np.array_equal(load.yearly_heating_peak_simulation_period, [8759] * 10)
    assert np.array_equal(load.yearly_dhw_load_simulation_period, np.zeros(10))


def test_baseload_heating():
    load = HourlyBuildingLoad()
    assert np.array_equal(load.monthly_baseload_heating, np.zeros(12))
    load.hourly_heating_load = np.repeat(np.linspace(0, 11, 12), 730)
    assert np.array_equal(load.monthly_baseload_heating, np.linspace(0, 11, 12) * 730)
    assert np.array_equal(load.monthly_baseload_heating / 730, load.monthly_baseload_heating_power)
    assert np.array_equal(load.monthly_baseload_heating_power, load.monthly_peak_heating)


def test_baseload_cooling():
    load = HourlyBuildingLoad()
    assert np.array_equal(load.monthly_baseload_cooling, np.zeros(12))
    load.hourly_cooling_load = np.repeat(np.linspace(0, 11, 12), 730)
    assert np.array_equal(load.monthly_baseload_cooling, np.linspace(0, 11, 12) * 730)
    assert np.array_equal(load.monthly_baseload_cooling / 730, load.monthly_baseload_cooling_power)
    assert np.array_equal(load.monthly_baseload_cooling_power, load.monthly_peak_cooling)


def test_peak_heating():
    load = HourlyBuildingLoad()
    assert np.array_equal(load.monthly_peak_heating, np.zeros(12))
    load.hourly_heating_load = np.repeat(np.linspace(0, 11, 12), 730)
    assert np.array_equal(load.hourly_heating_load, np.repeat(np.linspace(0, 11, 12), 730))
    assert np.array_equal(load.monthly_peak_heating, np.linspace(0, 11, 12))
    load.hourly_heating_load = np.repeat(np.linspace(1, 12, 12), 730)
    assert np.array_equal(load.monthly_peak_heating, np.linspace(1, 12, 12))
    assert np.isclose(load.max_peak_heating, 12)


def test_peak_cooling():
    load = HourlyBuildingLoad()
    assert np.array_equal(load.monthly_peak_cooling, np.zeros(12))
    load.hourly_cooling_load = np.repeat(np.linspace(0, 11, 12), 730)
    assert np.array_equal(load.hourly_cooling_load, np.repeat(np.linspace(0, 11, 12), 730))
    assert np.array_equal(load.monthly_peak_cooling, np.linspace(0, 11, 12))
    load.hourly_cooling_load = np.repeat(np.linspace(1, 12, 12), 730)
    assert np.array_equal(load.monthly_peak_cooling, np.linspace(1, 12, 12))
    assert np.isclose(load.max_peak_cooling, 12)


def test_load_simulation_period():
    load = HourlyBuildingLoad()
    load.hourly_heating_load = np.linspace(0, 8759, 8760)
    assert np.array_equal(load.hourly_heating_load_simulation_period,
                          np.tile(np.linspace(0, 8759, 8760), load.simulation_period))
    load.hourly_cooling_load = np.linspace(50, 8759, 8760)
    assert np.array_equal(load.hourly_cooling_load_simulation_period,
                          np.tile(np.linspace(50, 8759, 8760), load.simulation_period))


def test_set_hourly_values():
    load = HourlyBuildingLoad()
    with pytest.raises(ValueError):
        load.set_hourly_heating_load(np.ones(10))
    with pytest.raises(ValueError):
        load.set_hourly_cooling_load(np.ones(10))


def test_start_month_general():
    load = HourlyBuildingLoad()
    assert load.start_month == 1
    with pytest.raises(ValueError):
        load.start_month = 1.5
    with pytest.raises(ValueError):
        load.start_month = 0
    with pytest.raises(ValueError):
        load.start_month = 13
    load.start_month = 12
    assert load.start_month == 12
    assert load._start_hour == 11 * 730
    load.start_month = 1
    assert load.start_month == 1
    assert load._start_hour == 0
    load.start_month = 3
    assert load.start_month == 3
    assert load._start_hour == 730 * 2

    load.all_months_equal = False
    assert load._start_hour == 1416


def test_different_start_month():
    load = HourlyBuildingLoad(np.arange(1, 8761, 1), np.arange(1, 8761, 1))
    load.start_month = 3
    assert load.start_month == 3
    assert load.hourly_cooling_load[0] == 731 * 2 - 1
    assert load.hourly_heating_load[0] == 731 * 2 - 1
    assert load.hourly_cooling_load_simulation_period[0] == 731 * 2 - 1
    assert load.hourly_heating_load_simulation_period[0] == 731 * 2 - 1
    load.all_months_equal = False
    assert load.hourly_cooling_load[0] == 1417
    assert load.hourly_heating_load[0] == 1417
    assert load.hourly_cooling_load_simulation_period[0] == 1417
    assert load.hourly_heating_load_simulation_period[0] == 1417


def test_results():
    load2 = HourlyBuildingLoad(np.linspace(1, 8760 - 1, 8760), np.linspace(1, 8760 - 1, 8760) * 2, 2, scop, seer)
    load1 = HourlyBuildingLoad(np.linspace(1, 8760 - 1, 8760), np.linspace(1, 8760 - 1, 8760) * 2, 1, scop, seer)

    assert load2.results == (0, 17)
    assert load1.results == (0, 17)

    with pytest.raises(ValueError):
        load2.set_results(results_monthly1)
    with pytest.raises(ValueError):
        load1.set_results(results_hourly2)

    load2.set_results(results_hourly2)
    assert load2.results == results_hourly2
    load2.set_results(results_monthly2)
    assert load2.results == results_monthly2


def test_reset_results():
    load = HourlyBuildingLoad(np.linspace(1, 8760 - 1, 8760), np.linspace(1, 8760 - 1, 8760) * 2, 2, scop, seer)
    load.set_results(results_hourly2)
    assert load.results == results_hourly2
    load.reset_results(5, 10)
    assert load.results == (5, 10)


def test_dhw():
    load = HourlyBuildingLoad(np.zeros(8760), np.linspace(1, 8760 - 1, 8760) * 2, 10, scop, seer)

    assert load.dhw == 0

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
    assert np.allclose(load.hourly_dhw_load_simulation_period, np.zeros(87600))
    assert np.allclose(load.hourly_dhw_load, np.zeros(8760))
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

    load.dhw = 8760
    assert load.dhw == 8760
    assert np.allclose(load.hourly_dhw_load_simulation_period, np.full(87600, 1))
    assert np.allclose(load.hourly_dhw_load, np.full(8760, 1))
    assert np.allclose(load.monthly_baseload_dhw, np.full(12, 730))
    assert np.allclose(load.monthly_peak_dhw, np.full(12, 1))
    assert np.allclose(load.monthly_baseload_dhw_simulation_period, np.full(120, 730))
    assert np.allclose(load.monthly_baseload_dhw_power_simulation_period, np.full(120, 1))
    assert np.allclose(load.hourly_extraction_load_simulation_period, np.full(87600, 1) * 3 / 4)
    assert np.allclose(load.monthly_baseload_extraction_power_simulation_period, np.full(120, 1) * 3 / 4)
    assert np.allclose(load.monthly_peak_extraction_simulation_period, np.full(120, 1) * 3 / 4)
    assert np.allclose(load.yearly_dhw_load_simulation_period, np.full(10, 730 * 12))
    assert load.max_peak_dhw == 1
    assert np.isclose(load.yearly_average_dhw_load, 730 * 12)
    load.exclude_DHW_from_peak = True
    assert np.allclose(load.monthly_peak_extraction_simulation_period, np.zeros(120))
    load.exclude_DHW_from_peak = False

    arr = np.linspace(1, 8760, 8760)
    load.dhw = arr
    assert np.allclose(load.dhw, np.linspace(1, 8760, 8760))
    assert np.allclose(load.monthly_baseload_dhw, np.sum(arr.reshape(-1, 730), axis=1))
    assert np.allclose(load.monthly_peak_dhw, np.sum(arr.reshape(-1, 730), axis=1) / 730)
    assert np.allclose(load.monthly_baseload_dhw_simulation_period,
                       np.tile(np.sum(arr.reshape(-1, 730), axis=1), 10))
    assert np.allclose(load.monthly_baseload_dhw_power_simulation_period,
                       np.tile(np.sum(arr.reshape(-1, 730), axis=1) / 730, 10))
    assert np.allclose(load.monthly_baseload_extraction_power_simulation_period,
                       np.tile(np.sum(arr.reshape(-1, 730), axis=1) / 730, 10) * 3 / 4)
    assert np.allclose(load.monthly_peak_extraction_simulation_period,
                       np.tile(np.max(arr.reshape(-1, 730), axis=1), 10) * 3 / 4)
    assert np.allclose(load.yearly_dhw_load_simulation_period, np.full(10, np.sum(arr)))
    assert np.isclose(load.yearly_average_dhw_load, np.sum(arr))
    assert load.max_peak_dhw == 8760
    load.exclude_DHW_from_peak = True
    # idem since we started with an hourly data resolution
    assert np.allclose(load.monthly_peak_extraction_simulation_period, np.zeros(120))


def test_get_monthly_cop():
    load = HourlyBuildingLoad(np.linspace(1, 8760 - 1, 8760), np.linspace(1, 8760 - 1, 8760) * 2, 2, scop, seer)
    load.reset_results(5, 10)
    assert load._get_hourly_cop() == 6
    assert load._get_hourly_cop() == 6
    load.set_results(results_hourly2)
    assert np.allclose(load._get_hourly_cop(), np.full(120, 6))
    assert np.allclose(load._get_hourly_cop(), np.full(120, 6))


def test_get_monthly_cop_dhw():
    load = HourlyBuildingLoad(np.linspace(1, 8760 - 1, 8760), np.linspace(1, 8760 - 1, 8760) * 2, 2, scop, seer)
    load.reset_results(5, 10)
    assert load._get_hourly_cop_dhw() == 4
    assert load._get_hourly_cop_dhw() == 4
    load.set_results(results_hourly2)
    assert np.allclose(load._get_hourly_cop_dhw(), np.full(120, 4))
    assert np.allclose(load._get_hourly_cop_dhw(), np.full(120, 4))


def test_get_monthly_eer():
    load = HourlyBuildingLoad(np.linspace(1, 8760 - 1, 8760), np.linspace(1, 8760 - 1, 8760) * 2, 2, scop, seer)
    load.reset_results(5, 10)
    assert load._get_hourly_eer() == 5
    assert load._get_hourly_eer() == 5
    load.set_results(results_hourly2)
    assert np.allclose(load._get_hourly_eer(), np.full(120, 5))
    assert np.allclose(load._get_hourly_eer(), np.full(120, 5))


def test_hourly_injection_load_simulation_period_hourly_data():
    load = HourlyBuildingLoad(np.zeros(8760), np.zeros(8760), 10, scop, seer)
    load.hourly_cooling_load = test_load
    assert np.allclose(load.hourly_injection_load_simulation_period, test_load_sim_per * 6 / 5)
    assert np.allclose(load.monthly_baseload_injection_simulation_period,
                       load.resample_to_monthly(test_load_sim_per * 6 / 5)[1])
    assert np.allclose(load.monthly_peak_injection_simulation_period,
                       load.resample_to_monthly(test_load_sim_per * 6 / 5)[0])
    load.eer = eer_basic
    load.reset_results(0, 1)
    assert np.allclose(load.hourly_injection_load_simulation_period, test_load_sim_per * 3 / 2)
    assert np.allclose(load.monthly_baseload_injection_simulation_period,
                       load.resample_to_monthly(test_load_sim_per * 3 / 2)[1])
    assert np.allclose(load.monthly_peak_injection_simulation_period,
                       load.resample_to_monthly(test_load_sim_per * 3 / 2)[0])
    load.reset_results(0, 10)
    assert np.allclose(load.hourly_injection_load_simulation_period, test_load_sim_per * 21 / 20)
    assert np.allclose(load.monthly_baseload_injection_simulation_period,
                       load.resample_to_monthly(test_load_sim_per * 21 / 20)[1])
    assert np.allclose(load.monthly_peak_injection_simulation_period,
                       load.resample_to_monthly(test_load_sim_per * 21 / 20)[0])
    load.set_results(results_hourly_test)
    assert np.allclose(load.hourly_injection_load_simulation_period,
                       np.tile(np.concatenate((np.full(4380, 7.5), np.full(4380, 11))), 10))
    assert np.allclose(load.monthly_baseload_injection_simulation_period,
                       load.resample_to_monthly(np.tile(np.concatenate((np.full(4380, 7.5), np.full(4380, 11))), 10))[
                           1])
    assert np.allclose(load.monthly_peak_injection_simulation_period,
                       load.resample_to_monthly(np.tile(np.concatenate((np.full(4380, 7.5), np.full(4380, 11))), 10))[
                           0])
    load.eer = eer_pl
    load.reset_results(0, 1)
    assert np.allclose(load.hourly_injection_load_simulation_period,
                       np.tile(np.concatenate((np.full(4380, 6.25), np.full(4380, 12.5))), 10))
    assert np.allclose(load.monthly_baseload_injection_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 6.25), np.full(4380, 12.5))), 10))[
                           1])
    assert np.allclose(load.monthly_peak_injection_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 6.25), np.full(4380, 12.5))), 10))[
                           0])
    load.reset_results(0, 10)
    assert np.allclose(load.hourly_injection_load_simulation_period,
                       np.tile(np.concatenate((np.full(4380, 5.125), np.full(4380, 10.25))), 10))
    assert np.allclose(load.monthly_baseload_injection_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 5.125), np.full(4380, 10.25))), 10))[1])
    assert np.allclose(load.monthly_peak_injection_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 5.125), np.full(4380, 10.25))), 10))[0])
    load.set_results(results_hourly_test)
    assert np.allclose(load.hourly_injection_load_simulation_period,
                       np.tile(np.concatenate((np.full(4380, 6.25), np.full(4380, 10.5))), 10))
    assert np.allclose(load.monthly_baseload_injection_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 6.25), np.full(4380, 10.5))), 10))[1])
    assert np.allclose(load.monthly_peak_injection_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 6.25), np.full(4380, 10.5))), 10))[0])


def test_hourly_extraction_load_simulation_period_hourly_data():
    load = HourlyBuildingLoad(np.zeros(8760), np.zeros(8760), 10, scop, seer)
    load.hourly_heating_load = test_load

    assert np.allclose(load.hourly_extraction_load_simulation_period, test_load_sim_per * 5 / 6)
    assert np.allclose(load.monthly_baseload_extraction_simulation_period,
                       load.resample_to_monthly(test_load_sim_per * 5 / 6)[1])
    assert np.allclose(load.monthly_peak_extraction_simulation_period,
                       load.resample_to_monthly(test_load_sim_per * 5 / 6)[0])
    load.cop = cop_basic
    load.reset_results(0, 1)
    assert np.allclose(load.hourly_extraction_load_simulation_period, test_load_sim_per * 1 / 2)
    assert np.allclose(load.monthly_baseload_extraction_simulation_period,
                       load.resample_to_monthly(test_load_sim_per * 1 / 2)[1])
    assert np.allclose(load.monthly_peak_extraction_simulation_period,
                       load.resample_to_monthly(test_load_sim_per * 1 / 2)[0])
    load.reset_results(0, 10)
    assert np.allclose(load.hourly_extraction_load_simulation_period, test_load_sim_per * 19 / 20)
    assert np.allclose(load.monthly_baseload_extraction_simulation_period,
                       load.resample_to_monthly(test_load_sim_per * 19 / 20)[1])
    assert np.allclose(load.monthly_peak_extraction_simulation_period,
                       load.resample_to_monthly(test_load_sim_per * 19 / 20)[0])
    load.set_results(results_hourly_test)
    assert np.allclose(load.hourly_extraction_load_simulation_period,
                       np.tile(np.concatenate((np.full(4380, 2.5), np.full(4380, 9))), 10))
    assert np.allclose(load.monthly_baseload_extraction_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 2.5), np.full(4380, 9))), 10))[
                           1])
    assert np.allclose(load.monthly_peak_extraction_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 2.5), np.full(4380, 9))), 10))[
                           0])
    load.cop = cop_pl
    load.reset_results(0, 1)
    assert np.allclose(load.hourly_extraction_load_simulation_period,
                       np.tile(np.concatenate((np.full(4380, 3.75), np.full(4380, 7.5))), 10))
    assert np.allclose(load.monthly_baseload_extraction_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 3.75), np.full(4380, 7.5))), 10))[
                           1])
    assert np.allclose(load.monthly_peak_extraction_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 3.75), np.full(4380, 7.5))), 10))[
                           0])
    load.reset_results(0, 10)
    assert np.allclose(load.hourly_extraction_load_simulation_period,
                       np.tile(np.concatenate((np.full(4380, 4.875), np.full(4380, 9.75))), 10))
    assert np.allclose(load.monthly_baseload_extraction_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 4.875), np.full(4380, 9.75))), 10))[1])
    assert np.allclose(load.monthly_peak_extraction_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 4.875), np.full(4380, 9.75))), 10))[0])
    load.set_results(results_hourly_test)
    assert np.allclose(load.hourly_extraction_load_simulation_period,
                       np.tile(np.concatenate((np.full(4380, 3.75), np.full(4380, 9.5))), 10))
    assert np.allclose(load._hourly_extraction_load_heating_simulation_period,
                       np.tile(np.concatenate((np.full(4380, 3.75), np.full(4380, 9.5))), 10))
    assert np.allclose(load._hourly_extraction_load_dhw_simulation_period, np.zeros(87600))
    assert np.allclose(load.monthly_baseload_extraction_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 3.75), np.full(4380, 9.5))), 10))[1])
    assert np.allclose(load.monthly_peak_extraction_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 3.75), np.full(4380, 9.5))), 10))[0])
    assert np.allclose(load._monthly_baseload_extraction_heating_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 3.75), np.full(4380, 9.5))), 10))[1])
    assert np.allclose(load._monthly_peak_extraction_heating_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 3.75), np.full(4380, 9.5))), 10))[0])
    assert np.allclose(load._monthly_baseload_extraction_dhw_simulation_period, np.zeros(120))
    assert np.allclose(load._monthly_peak_extraction_dhw_simulation_period, np.zeros(120))

    # now for only DHW
    load.hourly_heating_load = np.zeros(8760)
    load.dhw = test_load
    load.cop_dhw = scop
    assert np.allclose(load.hourly_extraction_load_simulation_period, test_load_sim_per * 5 / 6)
    assert np.allclose(load.monthly_baseload_extraction_simulation_period,
                       load.resample_to_monthly(test_load_sim_per * 5 / 6)[1])
    assert np.allclose(load.monthly_peak_extraction_simulation_period,
                       load.resample_to_monthly(test_load_sim_per * 5 / 6)[0])
    load.cop_dhw = cop_basic
    load.reset_results(0, 1)
    assert np.allclose(load.hourly_extraction_load_simulation_period, test_load_sim_per * 1 / 2)
    assert np.allclose(load.monthly_baseload_extraction_simulation_period,
                       load.resample_to_monthly(test_load_sim_per * 1 / 2)[1])
    assert np.allclose(load.monthly_peak_extraction_simulation_period,
                       load.resample_to_monthly(test_load_sim_per * 1 / 2)[0])
    load.reset_results(0, 10)
    assert np.allclose(load.hourly_extraction_load_simulation_period, test_load_sim_per * 19 / 20)
    assert np.allclose(load.monthly_baseload_extraction_simulation_period,
                       load.resample_to_monthly(test_load_sim_per * 19 / 20)[1])
    assert np.allclose(load.monthly_peak_extraction_simulation_period,
                       load.resample_to_monthly(test_load_sim_per * 19 / 20)[0])
    load.set_results(results_hourly_test)
    assert np.allclose(load.hourly_extraction_load_simulation_period,
                       np.tile(np.concatenate((np.full(4380, 2.5), np.full(4380, 9))), 10))
    assert np.allclose(load.monthly_baseload_extraction_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 2.5), np.full(4380, 9))), 10))[
                           1])
    assert np.allclose(load.monthly_peak_extraction_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 2.5), np.full(4380, 9))), 10))[
                           0])
    load.cop_dhw = cop_pl
    load.reset_results(0, 1)
    assert np.allclose(load.hourly_extraction_load_simulation_period,
                       np.tile(np.concatenate((np.full(4380, 3.75), np.full(4380, 7.5))), 10))
    assert np.allclose(load.monthly_baseload_extraction_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 3.75), np.full(4380, 7.5))), 10))[
                           1])
    assert np.allclose(load.monthly_peak_extraction_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 3.75), np.full(4380, 7.5))), 10))[
                           0])
    load.reset_results(0, 10)
    assert np.allclose(load.hourly_extraction_load_simulation_period,
                       np.tile(np.concatenate((np.full(4380, 4.875), np.full(4380, 9.75))), 10))
    assert np.allclose(load.monthly_baseload_extraction_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 4.875), np.full(4380, 9.75))), 10))[1])
    assert np.allclose(load.monthly_peak_extraction_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 4.875), np.full(4380, 9.75))), 10))[0])
    load.set_results(results_hourly_test)
    assert np.allclose(load.hourly_extraction_load_simulation_period,
                       np.tile(np.concatenate((np.full(4380, 3.75), np.full(4380, 9.5))), 10))
    assert np.allclose(load._hourly_extraction_load_dhw_simulation_period,
                       np.tile(np.concatenate((np.full(4380, 3.75), np.full(4380, 9.5))), 10))
    assert np.allclose(load._hourly_extraction_load_heating_simulation_period, np.zeros(87600))
    assert np.allclose(load.monthly_baseload_extraction_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 3.75), np.full(4380, 9.5))), 10))[1])
    assert np.allclose(load.monthly_peak_extraction_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 3.75), np.full(4380, 9.5))), 10))[0])
    assert np.allclose(load._monthly_baseload_extraction_dhw_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 3.75), np.full(4380, 9.5))), 10))[1])
    assert np.allclose(load._monthly_peak_extraction_dhw_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 3.75), np.full(4380, 9.5))), 10))[0])
    assert np.allclose(load._monthly_baseload_extraction_heating_simulation_period, np.zeros(120))
    assert np.allclose(load._monthly_peak_extraction_heating_simulation_period, np.zeros(120))


def test_hourly_injection_load_simulation_period_monthly_data():
    # these results are the same as with hourly resolution, since the baseload and the peak load have the same
    # temperature result and are also the same power, since the hourly load is a constant, so it reduces to the same
    # power for both the peak and baseload
    load = HourlyBuildingLoad(np.zeros(8760), np.zeros(8760), 10, scop, seer)
    load.hourly_cooling_load = test_load
    load.set_results(results_monthly_test)
    load.eer = eer_basic
    with pytest.raises(TypeError):
        load.hourly_injection_load_simulation_period

    assert np.allclose(load.monthly_baseload_injection_simulation_period,
                       load.resample_to_monthly(np.tile(np.concatenate((np.full(4380, 7.5),
                                                                        np.full(4380, 11))), 10))[1])
    assert np.allclose(load.monthly_peak_injection_simulation_period,
                       load.resample_to_monthly(np.tile(np.concatenate((np.full(4380, 7.5),
                                                                        np.full(4380, 11))), 10))[0])
    assert np.isclose(load.max_peak_injection, 11)
    load.eer = eer_pl
    assert np.allclose(load.monthly_baseload_injection_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 6.25), np.full(4380, 10.5))), 10))[1])
    assert np.allclose(load.monthly_peak_injection_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 6.25), np.full(4380, 10.5))), 10))[0])


def test_hourly_extraction_load_simulation_period_monthly_data():
    # these results are the same as with hourly resolution, since the baseload and the peak load have the same
    # temperature result and are also the same power, since the hourly load is a constant, so it reduces to the same
    # power for both the peak and baseload
    load = HourlyBuildingLoad(np.zeros(8760), np.zeros(8760), 10, scop, seer)
    load.hourly_heating_load = test_load

    load.cop = cop_basic
    load.set_results(results_monthly_test)
    with pytest.raises(TypeError):
        load.hourly_extraction_load_simulation_period
    assert np.allclose(load.monthly_baseload_extraction_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 2.5), np.full(4380, 9))), 10))[1])
    assert np.allclose(load.monthly_peak_extraction_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 2.5), np.full(4380, 9))), 10))[0])
    assert np.allclose(load._monthly_baseload_extraction_heating_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 2.5), np.full(4380, 9))), 10))[1])
    assert np.allclose(load._monthly_peak_extraction_heating_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 2.5), np.full(4380, 9))), 10))[0])
    assert np.allclose(load._monthly_baseload_extraction_dhw_simulation_period, np.zeros(120))
    assert np.allclose(load._monthly_peak_extraction_dhw_simulation_period, np.zeros(120))
    assert np.isclose(load.max_peak_extraction, 9)
    assert np.isclose(load.imbalance, -50370.0)

    load.cop = cop_pl
    assert np.allclose(load.monthly_baseload_extraction_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 3.75), np.full(4380, 9.5))), 10))[1])
    assert np.allclose(load.monthly_peak_extraction_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 3.75), np.full(4380, 9.5))), 10))[0])

    # now for only DHW
    load.hourly_heating_load = np.zeros(8760)
    load.dhw = test_load
    load.cop_dhw = cop_basic
    with pytest.raises(TypeError):
        load._get_hourly_cop_dhw()
    assert np.allclose(load.monthly_baseload_extraction_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 2.5), np.full(4380, 9))), 10))[
                           1])
    assert np.allclose(load.monthly_peak_extraction_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 2.5), np.full(4380, 9))), 10))[
                           0])
    load.cop_dhw = cop_pl
    assert np.allclose(load.monthly_baseload_extraction_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 3.75), np.full(4380, 9.5))), 10))[1])
    assert np.allclose(load.monthly_peak_extraction_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 3.75), np.full(4380, 9.5))), 10))[0])
    assert np.allclose(load._monthly_baseload_extraction_dhw_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 3.75), np.full(4380, 9.5))), 10))[1])
    assert np.allclose(load._monthly_peak_extraction_dhw_simulation_period,
                       load.resample_to_monthly(
                           np.tile(np.concatenate((np.full(4380, 3.75), np.full(4380, 9.5))), 10))[0])
    assert np.allclose(load._monthly_baseload_extraction_heating_simulation_period, np.zeros(120))
    assert np.allclose(load._monthly_peak_extraction_heating_simulation_period, np.zeros(120))


def test_time_array():
    load = HourlyBuildingLoad(np.zeros(8760), np.zeros(8760), 10, scop, seer)
    assert np.allclose(load.month_indices, np.tile(np.repeat(np.arange(1, 13), load.UPM), 10))

    load.start_month = 2
    assert np.allclose(load.month_indices, np.tile(np.concatenate((
        np.repeat(np.arange(1, 13), load.UPM)[730:], np.repeat(np.arange(1, 13), load.UPM)[:730])), 10))


def test_cluster():
    load1 = HourlyBuildingLoad(np.linspace(1, 2000, 8760), np.linspace(1, 8760 - 1, 8760) * 2, 10, cop_basic, eer_basic)
    load2 = HourlyBuildingLoad(np.linspace(1, 2000, 8760), np.linspace(1, 8760 - 1, 8760) * 2, 10, cop_basic, eer_basic)
    load = HourlyBuildingLoad(np.linspace(1, 2000, 8760) * 2, np.linspace(1, 8760 - 1, 8760) * 2 * 2, 10, cop_basic,
                              eer_basic)

    cluster = Cluster([load1, load2])

    assert np.allclose(load.monthly_baseload_extraction,
                       cluster.monthly_baseload_extraction)
    assert np.allclose(load.monthly_baseload_injection,
                       cluster.monthly_baseload_injection)
    assert np.allclose(load.monthly_peak_extraction,
                       cluster.monthly_peak_extraction)
    assert np.allclose(load.monthly_peak_injection,
                       cluster.monthly_peak_injection)
    assert np.allclose(load.hourly_extraction_load, cluster.hourly_extraction_load)
    assert np.allclose(load.hourly_injection_load, cluster.hourly_injection_load)

    load.reset_results(0, 10)
    cluster.reset_results(0, 10)
    assert np.allclose(load.hourly_extraction_load, cluster.hourly_extraction_load)
    assert np.allclose(load.hourly_injection_load, cluster.hourly_injection_load)

    load.set_results(results_hourly_test)
    cluster.set_results(results_hourly_test)
    assert np.allclose(load.hourly_extraction_load, cluster.hourly_extraction_load)
    assert np.allclose(load.hourly_injection_load, cluster.hourly_injection_load)


def test_repr_():
    load = HourlyBuildingLoad()
    load.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"))
    load.dhw = 10000

    assert 'Hourly building load\n' \
           'Efficiency heating: SCOP [-]: 5\n' \
           'Efficiency cooling: SEER [-]: 20\n' \
           'Peak cooling duration [hour]: 6.0\n' \
           'Peak heating duration [hour]: 6.0\n' \
           'Simulation period [year]: 20\n' \
           'First month of simulation [-]: 1\n' \
           'DHW demand [kWh/year]: 10000\n' \
           'Efficiency DHW: SCOP [-]: 4' == load.__repr__()
