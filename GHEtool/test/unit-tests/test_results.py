import pytest

import numpy as np

from GHEtool import ResultsHourly


def test_hourly():
    results = ResultsHourly(np.array([1, 2, 3]), np.array([1, 5, 6]))
    assert np.array_equal(results.Tf, np.array([1, 5, 6]))
    assert np.array_equal(results.peak_extraction, np.array([1, 5, 6]))
    assert np.array_equal(results.peak_injection, np.array([1, 5, 6]))
