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
    assert np.array_equal(load.monthly_peak_heating, np.linspace(0, 11, 12))
    load.hourly_heating_load = np.repeat(np.linspace(1, 12, 12), 730)
    assert np.array_equal(load.monthly_peak_heating, np.linspace(1, 12, 12))


def test_peak_cooling():
    load = HourlyBuildingLoad()
    assert np.array_equal(load.monthly_peak_cooling, np.zeros(12))
    load.hourly_cooling_load = np.repeat(np.linspace(0, 11, 12), 730)
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
    load.set_results(results_hourly1)
    assert load.results == results_hourly1
    load.reset_results(5, 10)
    assert load.results == (5, 10)
