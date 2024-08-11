import pytest

import numpy as np

from GHEtool.VariableClasses import HourlyBuildingLoad, HourlyBuildingLoadMultiYear, MonthlyBuildingLoadAbsolute
from GHEtool.Validation.cases import load_case


def test_checks_multiyear():
    load = HourlyBuildingLoadMultiYear()
    assert not load._check_input(2)
    assert not load._check_input(np.ones(8759))
    assert not load._check_input(-1 * np.ones(8760))
    assert load._check_input([1] * 8760)
    assert load._check_input(np.ones(8760))
    assert load._check_input(np.ones(8760 * 3))
    assert not load._check_input(np.ones(9000))


def test_set_hourly_load_multi_year():
    load = HourlyBuildingLoadMultiYear()
    load.hourly_heating_load = np.linspace(0, 8759 * 2 + 1, 8760 * 2)
    load.hourly_cooling_load = np.linspace(0, 8759 * 2 + 1, 8760 * 2)
    assert len(load._hourly_heating_load) == 8760 * 2
    assert len(load.hourly_heating_load) == 8760
    assert load.simulation_period == 2
    assert np.array_equal(load.hourly_heating_load, np.linspace(0 + 8760 / 2, 8759 + 8760 / 2, 8760))
    assert np.array_equal(load.hourly_heating_load_simulation_period, load._hourly_heating_load)
    assert len(load._hourly_cooling_load) == 8760 * 2
    assert len(load.hourly_cooling_load) == 8760
    assert load.simulation_period == 2
    assert np.array_equal(load.hourly_cooling_load, np.linspace(0 + 8760 / 2, 8759 + 8760 / 2, 8760))
    assert np.array_equal(load.hourly_cooling_load_simulation_period, load._hourly_cooling_load)
    load._hourly_cooling_load = load._hourly_cooling_load - 20
    assert np.array_equal(load.hourly_net_resulting_power,
                          load._hourly_cooling_load - load._hourly_heating_load)


def test_imbalance_multi_year():
    load = HourlyBuildingLoadMultiYear(np.ones(8760 * 2) * 10, np.ones(8760 * 2))
    assert load.imbalance == -60882 * 2
    load = HourlyBuildingLoad(np.ones(8760), np.ones(8760) * 10)
    assert load.imbalance == 78840


def test_set_hourly_values_multi_year():
    load = HourlyBuildingLoadMultiYear()
    with pytest.raises(ValueError):
        load.set_hourly_heating_load(np.ones(10))
    with pytest.raises(ValueError):
        load.set_hourly_cooling_load(np.ones(10))


def test_monthly_based_on_hourly_multi_year():
    load = HourlyBuildingLoadMultiYear(heating_load=np.arange(0, 8760 * 2, 1),
                                       cooling_load=np.arange(0, 8760 * 2, 1) * 2)
    heating = np.array([729, 1459, 2189, 2919, 3649, 4379, 5109, 5839, 6569, 7299, 8029, 8759, 9489,
                        10219, 10949, 11679, 12409, 13139, 13869, 14599, 15329, 16059, 16789, 17519])
    heating_bl = np.array([np.sum(np.arange(0, 8760 * 2, 1)[i - 730:i]) for i in range(730, 8760 * 2 + 1, 730)])
    assert np.allclose(load.monthly_peak_heating_simulation_period, heating)
    assert np.allclose(load.monthly_peak_cooling_simulation_period, heating * 2)
    assert np.allclose(load.monthly_baseload_heating_simulation_period, heating_bl)
    assert np.allclose(load.monthly_baseload_cooling_simulation_period, heating_bl * 2)
    assert np.allclose(load.monthly_baseload_heating_power_simulation_period, heating_bl / 730)
    assert np.allclose(load.monthly_baseload_cooling_power_simulation_period, heating_bl * 2 / 730)
    assert np.allclose(load.monthly_average_cooling_power_simulation_period, heating_bl / 730)


def test_resample_to_monthly_multiyear():
    load = HourlyBuildingLoadMultiYear()
    peak, baseload = load.resample_to_monthly(np.tile(np.linspace(0, 729, 730), 24))
    assert np.array_equal(peak, np.full(24, 729))
    assert np.array_equal(baseload, np.full(24, 266085))
    load.all_months_equal = False
    peak, baseload = load.resample_to_monthly(np.tile(np.linspace(0, 729, 730), 24))
    assert np.array_equal(peak,
                          np.tile(np.array([729., 685., 729., 729., 729., 729., 729., 729., 729., 729., 729., 729.]),
                                  2))
    assert np.array_equal(baseload, np.tile(np.array([266176., 234864., 275780., 259140., 275836., 259100.,
                                                      275892., 276088., 258920., 276144., 258880., 276200.]), 2))


def test_yearly_loads_multiyear():
    load = HourlyBuildingLoadMultiYear(heating_load=np.linspace(0, 8759 * 2 + 1, 8760 * 2),
                                       cooling_load=np.linspace(0, 8759 * 2 + 1, 8760 * 2) * 2)
    assert np.array_equal(load.yearly_cooling_load_simulation_period, [76728840, 115102020 * 2])
    assert np.array_equal(load.yearly_heating_load_simulation_period, [38364420, 115102020])
    assert np.array_equal(load.yearly_cooling_peak_simulation_period, [17518, 35038])
    assert np.array_equal(load.yearly_heating_peak_simulation_period, [8759, 17519])
