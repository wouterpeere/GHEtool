import pytest

import numpy as np
from GHEtool import MonthlyGeothermalLoadMultiYear

# Initialize test data
baseload_heating = np.array([1000] * 12)  # 1000 kWh/month for each month
baseload_cooling = np.array([500] * 12)  # 500 kWh/month for each month
peak_heating = np.array([50] * 12)  # 50 kW/month for each month
peak_cooling = np.array([30] * 12)  # 30 kW/month for each month

# Initialize the MonthlyGeothermalLoadMultiYear object with test data
load_data = MonthlyGeothermalLoadMultiYear(
    baseload_heating=baseload_heating,
    baseload_cooling=baseload_cooling,
    peak_heating=peak_heating,
    peak_cooling=peak_cooling
)


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
    assert np.array_equal(load_data.baseload_heating_simulation_period, expected_output)


def test_baseload_cooling_simulation_period():
    expected_output = np.array([500] * 12)  # Average cooling load for the simulation period
    assert np.array_equal(load_data.baseload_cooling_simulation_period, expected_output)


def test_peak_heating_simulation_period():
    expected_output = np.array([50] * 12)  # Average peak heating load for the simulation period
    assert np.array_equal(load_data.peak_heating_simulation_period, expected_output)


def test_peak_cooling_simulation_period():
    expected_output = np.array([30] * 12)  # Average peak cooling load for the simulation period
    assert np.array_equal(load_data.peak_cooling_simulation_period, expected_output)


def test_baseload_heating_power_simulation_period():
    expected_output = baseload_heating / load_data.UPM
    assert np.array_equal(load_data.baseload_heating_power_simulation_period, expected_output)


def test_baseload_cooling_power_simulation_period():
    expected_output = baseload_cooling / load_data.UPM
    assert np.array_equal(load_data.baseload_cooling_power_simulation_period, expected_output)


def test_monthly_average_load_simulation_period():
    expected_output = (baseload_cooling / load_data.UPM) - (baseload_heating / load_data.UPM)
    assert np.array_equal(load_data.monthly_average_load_simulation_period, expected_output)


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
