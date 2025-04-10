import pytest

import numpy as np

from GHEtool import ResultsMonthly, ResultsHourly


def test_monthly():
    results = ResultsMonthly(np.linspace(0, 120 - 1, 120),
                             np.linspace(0, 120 - 1, 120) * 2,
                             np.linspace(0, 120 - 1, 120) * 3,
                             np.linspace(0, 120 - 1, 120) * 4,
                             np.linspace(0, 120 - 1, 120) * 5)
    assert np.array_equal(results.Tb, np.linspace(0, 120 - 1, 120))
    assert np.array_equal(results.peak_extraction, np.linspace(0, 120 - 1, 120) * 2)
    assert np.array_equal(results.peak_injection, np.linspace(0, 120 - 1, 120) * 3)
    assert np.array_equal(results.monthly_extraction, np.linspace(0, 120 - 1, 120) * 4)
    assert np.array_equal(results.monthly_injection, np.linspace(0, 120 - 1, 120) * 5)
    assert np.isclose(np.min(results.peak_extraction), results.min_temperature)
    assert np.isclose(np.max(results.peak_injection), results.max_temperature)


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
