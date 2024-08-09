import pytest

import numpy as np
from GHEtool import MonthlyBuildingLoadMultiYear

# Initialize test data
baseload_heating = np.array([1000] * 12)  # 1000 kWh/month for each month
baseload_cooling = np.array([500] * 12)  # 500 kWh/month for each month
peak_heating = np.array([50] * 12)  # 50 kW/month for each month
peak_cooling = np.array([30] * 12)  # 30 kW/month for each month

# Initialize the MonthlyBuildingLoadMultiYear object with test data
load_data = MonthlyBuildingLoadMultiYear(
    baseload_heating=baseload_heating,
    baseload_cooling=baseload_cooling,
    peak_heating=peak_heating,
    peak_cooling=peak_cooling)


def test_checks_multiyear_monthly():
    load = MonthlyBuildingLoadMultiYear()
    assert not load._check_input(2)
    assert not load._check_input(np.ones(11))
    assert not load._check_input(-1 * np.ones(12 * 2))
    assert load._check_input([1] * 12 * 2)
    assert load._check_input(np.ones(12))
    assert load._check_input(np.ones(12 * 3))
    assert not load._check_input(np.ones(30))
    with pytest.raises(ValueError):
        load.baseload_heating = np.ones(13)
    with pytest.raises(ValueError):
        load.baseload_cooling = np.ones(13)


def test_baseload_heating():
    assert np.array_equal(load_data.baseload_heating, baseload_heating)


def test_baseload_cooling():
    assert np.array_equal(load_data.baseload_cooling, baseload_cooling)


def test_peak_heating():
    assert np.array_equal(load_data.peak_heating, peak_heating)


def test_peak_cooling():
    assert np.array_equal(load_data.peak_cooling, peak_cooling)


def test_baseload_heating_simulation_period():
    expected_output = np.array([1000] * 12)  # Average heating load for the simulation period
    assert np.array_equal(load_data.monthly_baseload_heating_simulation_period, expected_output)


def test_baseload_cooling_simulation_period():
    expected_output = np.array([500] * 12)  # Average cooling load for the simulation period
    assert np.array_equal(load_data.monthly_baseload_cooling_simulation_period, expected_output)


def test_peak_heating_simulation_period():
    expected_output = np.array([50] * 12)  # Average peak heating load for the simulation period
    assert np.array_equal(load_data.monthly_peak_heating_simulation_period, expected_output)


def test_peak_cooling_simulation_period():
    expected_output = np.array([30] * 12)  # Average peak cooling load for the simulation period
    assert np.array_equal(load_data.monthly_peak_cooling_simulation_period, expected_output)


def test_baseload_heating_setter():
    new_baseload_heating = np.array([800] * 12)  # New baseload heating values
    load_data.baseload_heating = new_baseload_heating
    assert np.array_equal(load_data.baseload_heating, new_baseload_heating)


def test_baseload_cooling_setter():
    new_baseload_cooling = np.array([400] * 12)  # New baseload cooling values
    load_data.baseload_cooling = new_baseload_cooling
    assert np.array_equal(load_data.baseload_cooling, new_baseload_cooling)


def test_peak_heating_setter():
    new_peak_heating = np.array([60] * 12)  # New peak heating values
    load_data.peak_heating = new_peak_heating
    assert np.array_equal(load_data.peak_heating, new_peak_heating)


def test_peak_cooling_setter():
    new_peak_cooling = np.array([35] * 12)  # New peak cooling values
    load_data.peak_cooling = new_peak_cooling
    assert np.array_equal(load_data.peak_cooling, new_peak_cooling)


def test_input_validation():
    # Test input validation for non-array input
    with pytest.raises(ValueError):
        load_data.baseload_heating = 1000

    # Test input validation for negative values
    with pytest.raises(ValueError):
        load_data.peak_cooling = np.array([-30] * 12)

    # Test input validation for incorrect length
    with pytest.raises(ValueError):
        load_data.peak_heating = np.array([40] * 15)


def test_yearly_loads():
    baseload_heating = np.array([1000] * 12)  # 1000 kWh/month for each month
    baseload_cooling = np.array([500] * 12)  # 500 kWh/month for each month
    peak_heating = np.array([50] * 12)  # 50 kW/month for each month
    peak_cooling = np.array([30] * 12)  # 30 kW/month for each month

    # Initialize the MonthlyBuildingLoadMultiYear object with test data
    load_data = MonthlyBuildingLoadMultiYear(
        baseload_heating=baseload_heating,
        baseload_cooling=baseload_cooling,
        peak_heating=peak_heating,
        peak_cooling=peak_cooling
    )

    assert np.array_equal(load_data.yearly_cooling_load_simulation_period, [6000])
    assert np.array_equal(load_data.yearly_heating_load_simulation_period, [12000])
    assert np.array_equal(load_data.yearly_cooling_peak_simulation_period, [30])
    assert np.array_equal(load_data.yearly_heating_peak_simulation_period, [50])


def test_dhw():
    load = MonthlyBuildingLoadMultiYear(
        baseload_heating=baseload_heating,
        baseload_cooling=baseload_cooling,
        peak_heating=peak_heating,
        peak_cooling=peak_cooling)

    load.peak_heating = np.zeros(12)
    load.baseload_heating = np.zeros(12)

    assert load.dhw == 0

    with pytest.raises(ValueError):
        load.add_dhw(100)
    with pytest.raises(ValueError):
        load.add_dhw('test')
    with pytest.raises(ValueError):
        load.dhw = 100
    with pytest.raises(ValueError):
        load.dhw = 'test'

    load.dhw = np.linspace(1, 12, 12) * 730
    assert np.allclose(load.dhw, np.linspace(1, 12, 12) * 730)
    assert np.allclose(load.monthly_baseload_dhw, np.linspace(1, 12, 12) * 730)
    assert np.allclose(load.monthly_peak_dhw, np.linspace(1, 12, 12))
    assert np.allclose(load.monthly_baseload_dhw_simulation_period, np.linspace(1, 12, 12) * 730)
    assert np.allclose(load.monthly_baseload_dhw_power_simulation_period, np.linspace(1, 12, 12))
    assert np.allclose(load.monthly_baseload_extraction_power_simulation_period,
                       np.linspace(1, 12, 12) / 4)
    assert np.allclose(load.monthly_peak_extraction_simulation_period, np.linspace(1, 12, 12) / 4)
    assert np.allclose(load.yearly_dhw_load_simulation_period, np.full(1, np.sum(np.linspace(1, 12, 12) * 730)))
    assert np.isclose(load.yearly_average_dhw_load, np.sum(np.linspace(1, 12, 12) * 730))
    load.exclude_DHW_from_peak = True
    assert np.allclose(load.monthly_peak_extraction_simulation_period, np.zeros(12))
