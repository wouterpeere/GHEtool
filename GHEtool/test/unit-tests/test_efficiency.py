"""
This file contains the test for the efficiency data
"""
import pytest

import numpy as np

from GHEtool.VariableClasses.Efficiency import *


def test_SCOP():
    scop = SCOP(50)
    assert scop.get_SCOP(12, test=5) == 50
    assert scop.get_COP(12, test=5) == 50
    with pytest.raises(ValueError):
        SCOP(0)


def test_SEER():
    seer = SEER(50)
    assert seer.get_SEER(12, test=5) == 50
    assert seer.get_EER(12, test=5) == 50
    with pytest.raises(ValueError):
        SEER(0)


def test_COP_basic():
    with pytest.raises(ValueError):
        COP(np.array([3, 4, 6]), np.array([5, 15]))
    with pytest.raises(ValueError):
        COP(np.array([3, 4, 6]), np.array([5, 10, 15]), np.array([5, 6]))

    cop_basic = COP(np.array([3, 4, 6]), np.array([5, 10, 15]))
    assert not cop_basic._range_secondary
    assert not cop_basic._range_part_load

    assert cop_basic.get_COP(5) == 3
    assert np.array_equal(cop_basic.get_COP(np.array([7.5, 10])), np.array([3.5, 4]))
    assert np.array_equal(cop_basic.get_COP(np.array([7.5, 10, 0])), np.array([3.5, 4, 3]))

    assert np.array_equal(cop_basic.get_COP(np.array([7.5, 10]), secondary_temperature=5), np.array([3.5, 4]))
    assert np.array_equal(cop_basic.get_COP(np.array([7.5, 10, 0]), secondary_temperature=np.array([5, 6])),
                          np.array([3.5, 4, 3]))

    assert np.array_equal(cop_basic.get_COP(np.array([7.5, 10]), part_load=5), np.array([3.5, 4]))
    assert np.array_equal(cop_basic.get_COP(np.array([7.5, 10, 0]), part_load=np.array([5, 6])),
                          np.array([3.5, 4, 3]))


def test_COP_secondary():
    with pytest.raises(ValueError):
        COP(np.array([[1, 2], [2, 4]]), np.array([5, 15]))
    with pytest.raises(ValueError):
        COP(np.array([[1, 2], [2, 4]]), np.array([1.5, 2.5]), np.array([2.5, 4.5]), np.array([2.5, 4.5]))

    cop_sec = COP(np.array([[1, 2], [2, 4]]), np.array([1.5, 2.5]), np.array([2.5, 4.5]))
    assert cop_sec._range_secondary
    assert not cop_sec._range_part_load

    with pytest.raises(ValueError):
        assert cop_sec.get_COP(5) == 3

    assert cop_sec.get_COP(1.5, 3.5) == 1.5
    assert np.array_equal(cop_sec.get_COP(np.array([1.5, 2]), np.array([3, 4])), np.array([1.25, 2.625]))
    assert np.array_equal(cop_sec.get_COP(np.array([1.5, 3]), np.array([3, 4])), np.array([1.25, 3.5]))

    assert cop_sec.get_COP(1.5, 3.5, 1) == 1.5
    assert np.array_equal(cop_sec.get_COP(np.array([1.5, 2]), np.array([3, 4]), 1), np.array([1.25, 2.625]))
    assert np.array_equal(cop_sec.get_COP(np.array([1.5, 3]), np.array([3, 4]), np.array([1, 2])),
                          np.array([1.25, 3.5]))


def test_COP_part_load():
    with pytest.raises(ValueError):
        COP(np.array([[1, 2], [2, 4]]), np.array([5, 15]))
    with pytest.raises(ValueError):
        COP(np.array([[1, 2], [2, 4]]), np.array([1.5, 2.5]), np.array([2.5, 4.5]), np.array([2.5, 4.5]))

    cop_part = COP(np.array([[1, 2], [2, 4]]), np.array([1.5, 2.5]), range_part_load=np.array([2.5, 4.5]))
    assert cop_part._range_part_load
    assert not cop_part._range_secondary

    with pytest.raises(ValueError):
        assert cop_part.get_COP(5) == 3

    assert cop_part.get_COP(1.5, part_load=3.5) == 1.5
    assert np.array_equal(cop_part.get_COP(np.array([1.5, 2]), part_load=np.array([3, 4])), np.array([1.25, 2.625]))
    assert np.array_equal(cop_part.get_COP(np.array([1.5, 3]), part_load=np.array([3, 4])), np.array([1.25, 3.5]))

    assert cop_part.get_COP(1.5, secondary_temperature=1, part_load=3.5) == 1.5
    assert np.array_equal(cop_part.get_COP(np.array([1.5, 2]), part_load=np.array([3, 4]), secondary_temperature=1),
                          np.array([1.25, 2.625]))
    assert np.array_equal(
        cop_part.get_COP(np.array([1.5, 3]), part_load=np.array([3, 4]), secondary_temperature=np.array([1, 2])),
        np.array([1.25, 3.5]))


def test_COP_full():
    with pytest.raises(ValueError):
        COP(np.array([[1, 2], [2, 4]]), np.array([5, 15]))
    with pytest.raises(ValueError):
        COP(np.array([[1, 2], [2, 4]]), np.array([1.5, 2.5]), np.array([2.5, 4.5]), np.array([2.5, 4.5]))
    with pytest.raises(ValueError):
        COP(np.array([[[1, 2], [2, 4]], [[1, 2], [2, 4]]]), np.array([1.5, 2.5]), np.array([2.5, 4.5, 4.5]),
            np.array([2.5, 4.5]))
    cop_full = COP(np.array([[[1, 2], [2, 4]], [[2, 4], [4, 8]]]), np.array([1.5, 2.5]), np.array([2.5, 4.5]),
                   np.array([4.5, 8.5]))
    assert cop_full._range_part_load
    assert cop_full._range_secondary

    with pytest.raises(ValueError):
        assert cop_full.get_COP(5, 3) == 3

    assert cop_full.get_COP(2, 2.5, 4.5) == 1.5
    assert np.array_equal(cop_full.get_COP(np.array([2, 2.5]), np.array([3.5, 3.5]), np.array([6.5, 8])),
                          np.array([3.375, 5.625]))
    assert np.array_equal(cop_full.get_COP(np.array([2, 2.5, 5]), np.array([3.5, 3.5, 3.5]), np.array([6.5, 8, 8])),
                          np.array([3.375, 5.625, 5.625]))
