import pytest

import matplotlib.pyplot as plt
import numpy as np

from GHEtool import FOLDER
from GHEtool.VariableClasses import HourlyBuildingLoad
from GHEtool.VariableClasses.Result import ResultsMonthly, ResultsHourly

from GHEtool.VariableClasses.Efficiency import *

scop = SCOP(6)
seer = SEER(5)
cop_basic = COP(np.array([2, 20]), np.array([1, 10]))
eer_basic = EER(np.array([2, 20]), np.array([1, 10]))
cop_pl = COP(np.array([[2, 20], [4, 40]]), np.array([1, 10]), range_part_load=np.array([0.5, 1]))
eer_pl = EER(np.array([[2, 20], [4, 40]]), np.array([1, 10]), range_part_load=np.array([0.5, 1]))

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


def test_peak_cooling():
    load = HourlyBuildingLoad()
    assert np.array_equal(load.monthly_peak_cooling, np.zeros(12))
    load.hourly_cooling_load = np.repeat(np.linspace(0, 11, 12), 730)
    assert np.array_equal(load.hourly_cooling_load, np.repeat(np.linspace(0, 11, 12), 730))
    assert np.array_equal(load.monthly_peak_cooling, np.linspace(0, 11, 12))
    load.hourly_cooling_load = np.repeat(np.linspace(1, 12, 12), 730)
    assert np.array_equal(load.monthly_peak_cooling, np.linspace(1, 12, 12))


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
