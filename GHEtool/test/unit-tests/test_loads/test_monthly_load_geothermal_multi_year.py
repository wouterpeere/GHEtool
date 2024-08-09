import pytest

import numpy as np
from GHEtool import MonthlyGeothermalLoadMultiYear

# Initialize test data
baseload_extraction = np.array([1000] * 12)  # 1000 kWh/month for each month
baseload_injection = np.array([500] * 12)  # 500 kWh/month for each month
peak_extraction = np.array([50] * 12)  # 50 kW/month for each month
peak_injection = np.array([30] * 12)  # 30 kW/month for each month

# Initialize the MonthlyGeothermalLoadMultiYear object with test data
load_data = MonthlyGeothermalLoadMultiYear(
    baseload_extraction=baseload_extraction,
    baseload_injection=baseload_injection,
    peak_extraction=peak_extraction,
    peak_injection=peak_injection
)


def test_checks_multiyear_monthly():
    load = MonthlyGeothermalLoadMultiYear()
    assert not load._check_input(2)
    assert not load._check_input(np.ones(11))
    assert not load._check_input(-1 * np.ones(12 * 2))
    assert load._check_input([1] * 12 * 2)
    assert load._check_input(np.ones(12))
    assert load._check_input(np.ones(12 * 3))
    assert not load._check_input(np.ones(30))
    with pytest.raises(ValueError):
        load.baseload_extraction = np.ones(13)
    with pytest.raises(ValueError):
        load.baseload_injection = np.ones(13)


def test_baseload_extraction():
    assert np.array_equal(load_data.baseload_extraction, baseload_extraction)


def test_baseload_injection():
    assert np.array_equal(load_data.baseload_injection, baseload_injection)


def test_peak_extraction():
    assert np.array_equal(load_data.peak_extraction, peak_extraction)


def test_peak_injection():
    assert np.array_equal(load_data.peak_injection, peak_injection)


def test_baseload_extraction_simulation_period():
    expected_output = np.array([1000] * 12)  # Average heating load for the simulation period
    assert np.array_equal(load_data.monthly_baseload_extraction_simulation_period, expected_output)


def test_baseload_injection_simulation_period():
    expected_output = np.array([500] * 12)  # Average cooling load for the simulation period
    assert np.array_equal(load_data.monthly_baseload_injection_simulation_period, expected_output)


def test_peak_extraction_simulation_period():
    expected_output = np.array([50] * 12)  # Average peak heating load for the simulation period
    assert np.array_equal(load_data.monthly_peak_extraction_simulation_period, expected_output)


def test_peak_injection_simulation_period():
    expected_output = np.array([30] * 12)  # Average peak cooling load for the simulation period
    assert np.array_equal(load_data.monthly_peak_injection_simulation_period, expected_output)


def test_baseload_extraction_power_simulation_period():
    expected_output = baseload_extraction / load_data.UPM
    assert np.array_equal(load_data.monthly_baseload_extraction_power_simulation_period, expected_output)


def test_baseload_injection_power_simulation_period():
    expected_output = baseload_injection / load_data.UPM
    assert np.array_equal(load_data.monthly_baseload_injection_power_simulation_period, expected_output)


def test_monthly_average_load_simulation_period():
    expected_output = (baseload_injection / load_data.UPM) - (baseload_extraction / load_data.UPM)
    assert np.array_equal(load_data.monthly_average_injection_power_simulation_period, expected_output)


def test_baseload_extraction_setter():
    new_baseload_extraction = np.array([800] * 12)  # New baseload heating values
    load_data.baseload_extraction = new_baseload_extraction
    assert np.array_equal(load_data.baseload_extraction, new_baseload_extraction)


def test_baseload_injection_setter():
    new_baseload_injection = np.array([400] * 12)  # New baseload cooling values
    load_data.baseload_injection = new_baseload_injection
    assert np.array_equal(load_data.baseload_injection, new_baseload_injection)


def test_peak_extraction_setter():
    new_peak_extraction = np.array([60] * 12)  # New peak heating values
    load_data.peak_extraction = new_peak_extraction
    assert np.array_equal(load_data.peak_extraction, new_peak_extraction)


def test_peak_injection_setter():
    new_peak_injection = np.array([35] * 12)  # New peak cooling values
    load_data.peak_injection = new_peak_injection
    assert np.array_equal(load_data.peak_injection, new_peak_injection)


def test_input_validation():
    # Test input validation for non-array input
    with pytest.raises(ValueError):
        load_data.baseload_extraction = 1000

    # Test input validation for negative values
    with pytest.raises(ValueError):
        load_data.peak_injection = np.array([-30] * 12)

    # Test input validation for incorrect length
    with pytest.raises(ValueError):
        load_data.peak_extraction = np.array([40] * 15)


def test_yearly_loads():
    baseload_extraction = np.array([1000] * 12)  # 1000 kWh/month for each month
    baseload_injection = np.array([500] * 12)  # 500 kWh/month for each month
    peak_extraction = np.array([50] * 12)  # 50 kW/month for each month
    peak_injection = np.array([30] * 12)  # 30 kW/month for each month

    # Initialize the MonthlyGeothermalLoadMultiYear object with test data
    load_data = MonthlyGeothermalLoadMultiYear(
        baseload_extraction=baseload_extraction,
        baseload_injection=baseload_injection,
        peak_extraction=peak_extraction,
        peak_injection=peak_injection
    )

    assert np.array_equal(load_data.yearly_injection_load_simulation_period, [6000])
    assert np.array_equal(load_data.yearly_extraction_load_simulation_period, [12000])
    assert np.array_equal(load_data.yearly_injection_peak_simulation_period, [30])
    assert np.array_equal(load_data.yearly_extraction_peak_simulation_period, [50])


def test_depreciation_warning():
    with pytest.raises(DeprecationWarning):
        MonthlyGeothermalLoadMultiYear(baseload_heating=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
