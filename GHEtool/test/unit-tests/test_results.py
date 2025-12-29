import pytest

import numpy as np

from GHEtool import ResultsMonthly, ResultsHourly


def test_empty():
    results = ResultsMonthly()
    assert results.min_temperature is None
    assert results.max_temperature is None
    with pytest.raises(ValueError):
        results.baseload_temperature_inlet
    with pytest.raises(ValueError):
        results.baseload_temperature_outlet
    with pytest.raises(ValueError):
        results.peak_extraction_outlet
    with pytest.raises(ValueError):
        results.peak_extraction_inlet
    with pytest.raises(ValueError):
        results.peak_injection_outlet
    with pytest.raises(ValueError):
        results.peak_injection_inlet
    results = ResultsHourly()
    assert results.min_temperature is None
    assert results.max_temperature is None

    results = ResultsHourly()
    with pytest.raises(ValueError):
        results.peak_injection_inlet
    with pytest.raises(ValueError):
        results.peak_injection_outlet


def test_delta():
    results = ResultsMonthly()
    results._peak_extraction_outlet = np.array([5, 5])
    results._peak_extraction_inlet = np.array([4, 4])
    assert np.allclose([1, 1], results.peak_extraction_delta)
    results._peak_injection_outlet = np.array([5, 5])
    results._peak_injection_inlet = np.array([4, 4])
    assert np.allclose([1, 1], results.peak_injection_delta)
    results._baseload_temp_outlet = np.array([5, 5])
    results._baseload_temp_inlet = np.array([4, 4])
    assert np.allclose([1, 1], results.baseload_temperature_delta)

    results = ResultsHourly()
    results._Tf_outlet = np.array([5, 5])
    results._Tf_inlet = np.array([4, 4])
    assert np.allclose([1, 1], results.Tf_delta)
    assert np.allclose([1, 1], results.peak_injection_delta)
    assert np.allclose([1, 1], results.peak_extraction_delta)


def test_monthly():
    results = ResultsMonthly(np.linspace(0, 120 - 1, 120),
                             np.linspace(0, 120 - 1, 120) * 2,
                             np.linspace(0, 120 - 1, 120) * 3,
                             np.linspace(0, 120 - 1, 120) * 4,
                             np.linspace(0, 120 - 1, 120) * 5,
                             np.linspace(0, 120 - 1, 120) * 6)
    assert np.array_equal(results.Tb, np.linspace(0, 120 - 1, 120))
    assert np.array_equal(results.peak_extraction, np.linspace(0, 120 - 1, 120) * 2)
    assert np.array_equal(results.peak_injection, np.linspace(0, 120 - 1, 120) * 3)
    assert np.array_equal(results.monthly_extraction, np.linspace(0, 120 - 1, 120) * 4)
    assert np.array_equal(results.monthly_injection, np.linspace(0, 120 - 1, 120) * 5)
    assert np.array_equal(results.baseload_temperature, np.linspace(0, 120 - 1, 120) * 6)
    assert np.isclose(np.min(results.peak_extraction), results.min_temperature)
    assert np.isclose(np.max(results.peak_injection), results.max_temperature)


def test_depreciation():
    results = ResultsMonthly(np.linspace(0, 120 - 1, 120),
                             np.linspace(0, 120 - 1, 120) * 2,
                             np.linspace(0, 120 - 1, 120) * 3,
                             np.linspace(0, 120 - 1, 120) * 4,
                             np.linspace(0, 120 - 1, 120) * 5)
    with pytest.warns(DeprecationWarning):
        assert np.array_equal(results.monthly_extraction, np.linspace(0, 120 - 1, 120) * 4)
    with pytest.warns(DeprecationWarning):
        assert np.array_equal(results.monthly_injection, np.linspace(0, 120 - 1, 120) * 5)


def test_hourly():
    results = ResultsHourly(np.array([1, 2, 3]), np.array([1, 5, 6]))
    assert np.array_equal(results.Tb, np.array([1, 2, 3]))
    assert np.array_equal(results.Tf, np.array([1, 5, 6]))
    assert np.array_equal(results.peak_extraction, np.array([1, 5, 6]))
    assert np.array_equal(results.peak_injection, np.array([1, 5, 6]))
    assert np.isclose(np.min(results.peak_extraction), results.min_temperature)
    assert np.isclose(np.max(results.peak_extraction), results.max_temperature)


def test_eq():
    monthly1 = ResultsMonthly(np.linspace(0, 120 - 1, 120),
                              np.linspace(0, 120 - 1, 120) * 2,
                              np.linspace(0, 120 - 1, 120) * 3,
                              np.linspace(0, 120 - 1, 120) * 4,
                              np.linspace(0, 120 - 1, 120) * 5)
    monthly2 = ResultsMonthly(np.linspace(1, 120 - 1, 120),
                              np.linspace(0, 120 - 1, 120) * 2,
                              np.linspace(0, 120 - 1, 120) * 3,
                              np.linspace(0, 120 - 1, 120) * 4,
                              np.linspace(0, 120 - 1, 120) * 5)
    monthly3 = ResultsMonthly(np.linspace(1, 120 - 1, 120),
                              np.linspace(0, 120 - 1, 120) * 2,
                              np.linspace(0, 120 - 1, 120) * 3,
                              np.linspace(0, 120 - 1, 120) * 4,
                              np.linspace(0, 120 - 1, 120) * 5)
    hourly1 = ResultsHourly(np.array([0, 2, 3]), np.array([1, 5, 6]))
    hourly2 = ResultsHourly(np.array([1, 2, 3]), np.array([1, 5, 6]))
    hourly3 = ResultsHourly(np.array([1, 2, 3]), np.array([1, 5, 6]))

    assert monthly1 != monthly2
    assert hourly1 != hourly2
    assert monthly1 != hourly1
    assert monthly2 == monthly3
    assert hourly2 == hourly3
