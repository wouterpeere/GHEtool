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


def test_COP_error():
    with pytest.raises(ValueError):
        COP(np.array([-3, 4, 6]), np.array([5, 15, 6]))
    with pytest.raises(ValueError):
        COP(np.array([3, 4, 6]), np.array([5, 10]))
    with pytest.raises(ValueError):  # no efficiencies equal or smaller than 0
        COP(np.array([0, 4, 6]), np.array([5, 10, 15]), part_load=True)


def test_COP_basic():
    cop_basic = COP(np.array([3, 4, 6]), np.array([5, 10, 15]))
    assert not cop_basic._has_secondary
    assert not cop_basic._has_part_load

    assert cop_basic.get_COP(5) == 3
    assert np.array_equal(cop_basic.get_COP(np.array([7.5, 10])), np.array([3.5, 4]))
    assert np.array_equal(cop_basic.get_COP(np.array([7.5, 10, 0])), np.array([3.5, 4, 3]))

    assert np.array_equal(cop_basic.get_COP(np.array([7.5, 10]), secondary_temperature=5), np.array([3.5, 4]))
    assert np.array_equal(cop_basic.get_COP(np.array([7.5, 10, 0]), secondary_temperature=np.array([5, 6])),
                          np.array([3.5, 4, 3]))

    assert np.array_equal(cop_basic.get_COP(np.array([7.5, 10]), power=5), np.array([3.5, 4]))
    assert np.array_equal(cop_basic.get_COP(np.array([7.5, 10, 0]), power=np.array([5, 6])),
                          np.array([3.5, 4, 3]))


def test_COP_secondary():
    cop_sec = COP(np.array([1, 2, 2, 4]), np.array([[1.5, 2.5], [2.5, 2.5], [1.5, 4.5], [2.5, 4.5]]), secondary=True)
    assert cop_sec._has_secondary
    assert not cop_sec._has_part_load

    with pytest.raises(ValueError):
        assert cop_sec.get_COP(5) == 3

    assert cop_sec.get_COP(1.5, 3.5) == 1.5
    assert np.array_equal(cop_sec.get_COP(np.array([1.5, 2]), np.array([3, 4])), np.array([1.25, 2.625]))
    assert np.array_equal(cop_sec.get_COP(np.array([1.5, 3]), np.array([3, 4])), np.array([1.25, 3.5]))

    assert cop_sec.get_COP(1.5, 3.5, 1) == 1.5
    assert np.array_equal(cop_sec.get_COP(np.array([1.5, 2]), np.array([3, 4]), 1), np.array([1.25, 2.625]))
    assert np.array_equal(cop_sec.get_COP(np.array([1.5, 3]), np.array([3, 4]), np.array([1, 2])),
                          np.array([1.25, 3.5]))
    assert np.array_equal(cop_sec.get_COP(1.5, np.array([2.5, 4.5])), np.array([1, 2]))


def test_COP_part_load():
    cop_part = COP(np.array([1, 2, 2, 4]), np.array([[1.5, 2.5], [2.5, 2.5], [1.5, 4.5], [2.5, 4.5]]), part_load=True)
    assert cop_part._has_part_load
    assert not cop_part._has_secondary

    with pytest.raises(ValueError):
        assert cop_part.get_COP(5) == 3

    assert cop_part.get_COP(1.5, power=3.5) == 1.5
    assert np.array_equal(cop_part.get_COP(np.array([1.5, 2]), power=np.array([3, 4])), np.array([1.25, 2.625]))
    assert np.array_equal(cop_part.get_COP(np.array([1.5, 3]), power=np.array([3, 4])), np.array([1.25, 3.5]))

    assert cop_part.get_COP(1.5, secondary_temperature=1, power=3.5) == 1.5
    assert np.array_equal(cop_part.get_COP(np.array([1.5, 2]), power=np.array([3, 4]), secondary_temperature=1),
                          np.array([1.25, 2.625]))
    assert np.array_equal(
        cop_part.get_COP(np.array([1.5, 3]), power=np.array([3, 4]), secondary_temperature=np.array([1, 2])),
        np.array([1.25, 3.5]))
    assert np.array_equal(cop_part.get_COP(1.5, power=np.array([2.5, 4.5])), np.array([1, 2]))


def test_COP_full():
    cop_full = COP(np.array([1, 2, 2, 4, 2, 4, 4, 8]),
                   np.array([[1.5, 2.5, 4.5], [2.5, 2.5, 4.5], [1.5, 4.5, 4.5], [2.5, 4.5, 4.5],
                             [1.5, 2.5, 8.5], [2.5, 2.5, 8.5], [1.5, 4.5, 8.5], [2.5, 4.5, 8.5]]),
                   secondary=True, part_load=True)

    assert cop_full._has_part_load
    assert cop_full._has_secondary

    with pytest.raises(ValueError):
        assert cop_full.get_COP(5, 3) == 3

    assert cop_full.get_COP(2, 2.5, 4.5) == 1.5
    assert np.array_equal(cop_full.get_COP(np.array([2, 2.5]), np.array([3.5, 3.5]), np.array([6.5, 8])),
                          np.array([3.375, 5.625]))
    assert np.array_equal(cop_full.get_COP(np.array([2, 2.5, 5]), np.array([3.5, 3.5, 3.5]), np.array([6.5, 8, 8])),
                          np.array([3.375, 5.625, 5.625]))
    assert np.array_equal(cop_full.get_COP(1.5, secondary_temperature=np.array([2.5, 4.5]), power=4.5),
                          np.array([1, 2]))


def test_COP_get_SCOP():
    cop_full = COP(np.array([1, 2, 2, 4, 2, 4, 4, 8]),
                   np.array([[1.5, 2.5, 0], [2.5, 2.5, 0], [1.5, 4.5, 0], [2.5, 4.5, 0],
                             [1.5, 2.5, 10], [2.5, 2.5, 10], [1.5, 4.5, 10], [2.5, 4.5, 10]]),
                   secondary=True, part_load=True)

    with pytest.raises(ValueError):
        cop_full.get_SCOP([10, 5], [2, 3, 4])

    assert np.isclose(cop_full.get_SCOP([10, 10], [1.5, 2.5], [2.5, 2.5]), 16 / 6)
    assert np.isclose(cop_full.get_SCOP([10, 5], [1.5, 2.5], [2.5, 2.5]), 45 / 20)


def test_error_EER():
    with pytest.raises(ValueError):
        EER(np.array([3, 4, 6]), np.array([5, 15]))
    with pytest.raises(ValueError):
        EER(np.array([3, 4, 6]), np.array([5, 10, 15]), True, True)
    with pytest.raises(ValueError):  # no efficiencies equal or smaller than 0
        EER(np.array([0, 4, 6]), np.array([5, 10, 15]))


def test_EER_basic():
    eer_basic = EER(np.array([3, 4, 6]), np.array([5, 10, 15]))
    assert not eer_basic._has_secondary
    assert not eer_basic._has_part_load

    assert eer_basic.get_EER(5) == 3
    assert np.array_equal(eer_basic.get_EER(np.array([7.5, 10])), np.array([3.5, 4]))
    assert np.array_equal(eer_basic.get_EER(np.array([7.5, 10, 0])), np.array([3.5, 4, 3]))

    assert np.array_equal(eer_basic.get_EER(np.array([7.5, 10]), secondary_temperature=5), np.array([3.5, 4]))
    assert np.array_equal(eer_basic.get_EER(np.array([7.5, 10, 0]), secondary_temperature=np.array([5, 6])),
                          np.array([3.5, 4, 3]))

    assert np.array_equal(eer_basic.get_EER(np.array([7.5, 10]), power=5), np.array([3.5, 4]))
    assert np.array_equal(eer_basic.get_EER(np.array([7.5, 10, 0]), power=np.array([5, 6])),
                          np.array([3.5, 4, 3]))


def test_EER_secondary():
    eer_sec = EER(np.array([1, 2, 2, 4]), np.array([[1.5, 2.5], [2.5, 2.5], [1.5, 4.5], [2.5, 4.5]]), secondary=True)
    assert eer_sec._has_secondary
    assert not eer_sec._has_part_load

    with pytest.raises(ValueError):
        assert eer_sec.get_EER(5) == 3

    assert eer_sec.get_EER(1.5, 3.5) == 1.5
    assert np.array_equal(eer_sec.get_EER(np.array([1.5, 2]), np.array([3, 4])), np.array([1.25, 2.625]))
    assert np.array_equal(eer_sec.get_EER(np.array([1.5, 3]), np.array([3, 4])), np.array([1.25, 3.5]))

    assert eer_sec.get_EER(1.5, 3.5, 1) == 1.5
    assert np.array_equal(eer_sec.get_EER(np.array([1.5, 2]), np.array([3, 4]), 1), np.array([1.25, 2.625]))
    assert np.array_equal(eer_sec.get_EER(np.array([1.5, 3]), np.array([3, 4]), np.array([1, 2])),
                          np.array([1.25, 3.5]))
    assert np.array_equal(eer_sec.get_EER(1.5, np.array([2.5, 4.5])), np.array([1, 2]))


def test_EER_part_load():
    eer_part = EER(np.array([1, 2, 2, 4]), np.array([[1.5, 2.5], [2.5, 2.5], [1.5, 4.5], [2.5, 4.5]]), part_load=True)
    assert eer_part._has_part_load
    assert not eer_part._has_secondary

    with pytest.raises(ValueError):
        assert eer_part.get_EER(5) == 3

    assert eer_part.get_EER(1.5, power=3.5) == 1.5
    assert np.array_equal(eer_part.get_EER(np.array([1.5, 2]), power=np.array([3, 4])), np.array([1.25, 2.625]))
    assert np.array_equal(eer_part.get_EER(np.array([1.5, 3]), power=np.array([3, 4])), np.array([1.25, 3.5]))

    assert eer_part.get_EER(1.5, secondary_temperature=1, power=3.5) == 1.5
    assert np.array_equal(eer_part.get_EER(np.array([1.5, 2]), power=np.array([3, 4]), secondary_temperature=1),
                          np.array([1.25, 2.625]))
    assert np.array_equal(
        eer_part.get_EER(np.array([1.5, 3]), power=np.array([3, 4]), secondary_temperature=np.array([1, 2])),
        np.array([1.25, 3.5]))
    assert np.array_equal(eer_part.get_EER(1.5, power=np.array([2.5, 4.5])), np.array([1, 2]))


def test_EER_full():
    eer_full = EER(np.array([1, 2, 2, 4, 2, 4, 4, 8]),
                   np.array([[1.5, 2.5, 4.5], [2.5, 2.5, 4.5], [1.5, 4.5, 4.5], [2.5, 4.5, 4.5],
                             [1.5, 2.5, 8.5], [2.5, 2.5, 8.5], [1.5, 4.5, 8.5], [2.5, 4.5, 8.5]]),
                   secondary=True, part_load=True)
    assert eer_full._has_part_load
    assert eer_full._has_secondary

    with pytest.raises(ValueError):
        assert eer_full.get_EER(5, 3) == 3

    assert eer_full.get_EER(2, 2.5, 4.5) == 1.5
    assert np.array_equal(eer_full.get_EER(np.array([2, 2.5]), np.array([3.5, 3.5]), np.array([6.5, 8])),
                          np.array([3.375, 5.625]))
    assert np.array_equal(eer_full.get_EER(np.array([2, 2.5, 5]), np.array([3.5, 3.5, 3.5]), np.array([6.5, 8, 8])),
                          np.array([3.375, 5.625, 5.625]))
    assert np.array_equal(eer_full.get_EER(1.5, secondary_temperature=np.array([2.5, 4.5]), power=4.5),
                          np.array([1, 2]))


def test_EER_get_SEER():
    eer_full = EER(np.array([1, 2, 2, 4, 2, 4, 4, 8]),
                   np.array([[1.5, 2.5, 0], [2.5, 2.5, 0], [1.5, 4.5, 0], [2.5, 4.5, 0],
                             [1.5, 2.5, 10], [2.5, 2.5, 10], [1.5, 4.5, 10], [2.5, 4.5, 10]]),
                   secondary=True, part_load=True)

    with pytest.raises(ValueError):
        eer_full.get_SEER([10, 5], [2, 3, 4])

    assert np.isclose(eer_full.get_SEER([10, 10], [1.5, 2.5], [2.5, 2.5]), 16 / 6)
    assert np.isclose(eer_full.get_SEER([10, 5], [1.5, 2.5], [2.5, 2.5]), 45 / 20)


def test_eq():
    scop1 = SCOP(5)
    scop2 = SCOP(6)
    scop3 = SCOP(6)
    seer1 = SEER(5)
    seer2 = SEER(6)
    seer3 = SEER(6)

    assert scop1 != scop2
    assert seer1 != seer2
    assert scop1 != seer1
    assert seer1 != scop1
    assert scop2 == scop3
    assert seer2 == seer3

    cop_basic1 = COP(np.array([1, 10]), np.array([1, 10]))
    eer_basic1 = EER(np.array([1, 10]), np.array([1, 10]))
    cop_pl1 = COP(np.array([1, 10, 2, 20]), np.array([[1, 0.5], [10, 0.5], [1, 1], [10, 1]]), part_load=True)
    eer_pl1 = EER(np.array([1, 10, 2, 20]), np.array([[1, 0.5], [10, 0.5], [1, 1], [10, 1]]), part_load=True)
    cop_basic2 = COP(np.array([2, 10]), np.array([1, 10]))
    eer_basic2 = EER(np.array([2, 10]), np.array([1, 10]))
    cop_pl2 = COP(np.array([2, 10, 2, 20]), np.array([[1, 0.5], [10, 0.5], [1, 1], [10, 1]]), part_load=True)
    eer_pl2 = EER(np.array([2, 10, 2, 20]), np.array([[1, 0.5], [10, 0.5], [1, 1], [10, 1]]), part_load=True)
    cop_basic3 = COP(np.array([1, 10]), np.array([1, 10]))
    eer_basic3 = EER(np.array([1, 10]), np.array([1, 10]))
    cop_pl3 = COP(np.array([1, 10, 2, 20]), np.array([[1, 0.5], [10, 0.5], [1, 1], [10, 1]]), part_load=True)
    eer_pl3 = EER(np.array([1, 10, 2, 20]), np.array([[1, 0.5], [10, 0.5], [1, 1], [10, 1]]), part_load=True)

    assert cop_basic1 != cop_basic2
    assert eer_basic1 != eer_basic2
    assert cop_basic1 != eer_basic1
    assert eer_basic1 != cop_basic1
    assert cop_basic1 == cop_basic3
    assert eer_basic1 == eer_basic3
    assert cop_pl1 != cop_pl2
    assert eer_pl1 != eer_pl2
    assert cop_pl1 != eer_pl1
    assert eer_pl1 != cop_pl1
    assert cop_pl1 == cop_pl3
    assert eer_pl1 == eer_pl3


def test_scale_EER():
    with pytest.raises(ValueError):
        eer_full = EER(np.array([1, 2, 2, 4, 2, 4, 4, 8]),
                       np.array([[1.5, 2.5, 0], [2.5, 2.5, 0], [1.5, 4.5, 0], [2.5, 4.5, 0],
                                 [1.5, 2.5, 10], [2.5, 2.5, 10], [1.5, 4.5, 10], [2.5, 4.5, 10]]),
                       secondary=True, part_load=True, nominal_power=8)
    eer_full = EER(np.array([1, 2, 2, 4, 2, 4, 4, 8]),
                   np.array([[1.5, 2.5, 0], [2.5, 2.5, 0], [1.5, 4.5, 0], [2.5, 4.5, 0],
                             [1.5, 2.5, 10], [2.5, 2.5, 10], [1.5, 4.5, 10], [2.5, 4.5, 10]]),
                   secondary=True, part_load=True, nominal_power=1, reference_nominal_power=10)
    assert np.array_equal(eer_full._range_part_load, np.array([0, 1]))
    assert np.array_equal(eer_full._points[-1], np.array([0, 1]))


def test_scale_COP():
    with pytest.raises(ValueError):
        cop_full = COP(np.array([1, 2, 2, 4, 2, 4, 4, 8]),
                       np.array([[1.5, 2.5, 0], [2.5, 2.5, 0], [1.5, 4.5, 0], [2.5, 4.5, 0],
                                 [1.5, 2.5, 10], [2.5, 2.5, 10], [1.5, 4.5, 10], [2.5, 4.5, 10]]),
                       secondary=True, part_load=True, nominal_power=8)
    cop_full = COP(np.array([1, 2, 2, 4, 2, 4, 4, 8]),
                   np.array([[1.5, 2.5, 0], [2.5, 2.5, 0], [1.5, 4.5, 0], [2.5, 4.5, 0],
                             [1.5, 2.5, 10], [2.5, 2.5, 10], [1.5, 4.5, 10], [2.5, 4.5, 10]]),
                   secondary=True, part_load=True, nominal_power=1, reference_nominal_power=10)
    assert np.array_equal(cop_full._range_part_load, np.array([0, 1]))
    assert np.array_equal(cop_full._points[-1], np.array([0, 1]))


def test_interpolation():
    cop = COP(np.array([1, 2, 2, 3]), np.array([[1, 1], [1, 3], [2, 1], [2, 2]]), part_load=True)
    assert np.array_equal(cop._range_part_load, np.array([1, 2, 3]))
    assert np.array_equal(cop._data, np.array([[1, 1.5, 2], [2, 3, 3]]))

    cop = COP(np.array([1, 2, 2, 3, 1, 2, 2, 3]),
              np.array([[1, 1, 1], [1, 1, 3], [2, 1, 1], [2, 1, 2], [1, 2, 1], [1, 2, 3], [2, 2, 1], [2, 2, 2]]),
              part_load=True, secondary=True)
    assert np.array_equal(cop._range_part_load, np.array([1, 2, 3]))
    assert np.array_equal(cop._data, np.array([[[1, 1.5, 2], [1, 1.5, 2]], [[2, 3, 3], [2, 3, 3]]]))


def test_EERCombined():
    with pytest.raises(ValueError):
        EERCombined(20, 5)

    # with threshold
    eer = EERCombined(20, 5, 10)
    assert eer.get_EER(1, 0, 0, 0) == 20
    assert eer.get_EER(10, 0, 0, 0) == 20
    assert eer.get_EER(20, 0, 0, 0) == 5
    assert np.allclose(eer.get_EER(np.array([1, 10, 20])), np.array([20, 20, 5]))
    assert np.allclose(eer.get_time_series_active_cooling(np.array([1, 10, 20]), month_indices=np.array([5, 6, 7])),
                       np.array([False, False, True]))
    # with month array
    eer = EERCombined(20, 5, months_active_cooling=np.array([7, 8, 9]))
    with pytest.raises(ValueError):
        eer.get_EER(1)
    with pytest.raises(ValueError):
        eer.get_EER(np.array([1, 10, 20]))
    assert eer.get_EER(1, 0, 0, month_indices=1) == 20
    assert eer.get_EER(15, 0, 0, month_indices=1) == 20
    assert eer.get_EER(20, 0, 0, month_indices=7) == 5
    assert np.allclose(eer.get_EER(np.array([1, 15, 20]), month_indices=np.array([5, 6, 7])), np.array([20, 20, 5]))
    assert np.allclose(eer.get_time_series_active_cooling(np.array([1, 10, 20]), month_indices=np.array([5, 6, 7])),
                       np.array([False, False, True]))
    # with threshold and month array
    eer = EERCombined(20, 5, 10, months_active_cooling=np.array([7, 8, 9]))
    with pytest.raises(ValueError):
        eer.get_EER(1)
    with pytest.raises(ValueError):
        eer.get_EER(np.array([1, 10, 20]))
    assert eer.get_EER(1, 0, 0, month_indices=1) == 20
    assert eer.get_EER(15, 0, 0, month_indices=1) == 5
    assert eer.get_EER(20, 0, 0, month_indices=7) == 5
    assert np.allclose(eer.get_EER(np.array([1, 15, 20]), month_indices=np.array([5, 6, 7])), np.array([20, 5, 5]))
    assert np.allclose(eer.get_EER(1, month_indices=np.array([5, 6, 7])), np.array([20, 20, 5]))

    assert np.allclose(eer.get_time_series_active_cooling(np.array([1, 15, 20]), month_indices=np.array([5, 6, 7])),
                       np.array([False, True, True]))

    with pytest.raises(ValueError):
        eer.get_SEER(np.array([10, 10, 10]), np.array([1, 15, 20]), month_indices=np.array([6, 7]))
    assert np.isclose(eer.get_SEER(np.array([10, 10, 10]), np.array([1, 15, 20]), month_indices=np.array([5, 6, 7])),
                      30 / 4.5)


def test_eq_eer_combined():
    eer_combined = EERCombined(20, 5, 10)
    eer_combined2 = EERCombined(20, 50, 10)
    eer_combined3 = EERCombined(20, 50, 10)

    seer = SEER(20)

    assert eer_combined != seer
    assert eer_combined2 != eer_combined
    assert eer_combined2 == eer_combined3


def test_repr_():
    scop = SCOP(5)
    seer = SEER(5)
    assert 'SCOP [-]: 5' == scop.__repr__()
    assert 'SEER [-]: 5' == seer.__repr__()
    cop_basic = COP(np.array([3, 4, 6]), np.array([5, 10, 15]))
    eer_basic = EER(np.array([3, 4, 6]), np.array([5, 10, 15]))
    cop_sec = COP(np.array([1, 2, 2, 4]), np.array([[1.5, 2.5], [2.5, 2.5], [1.5, 4.5], [2.5, 4.5]]), secondary=True)
    cop_part = COP(np.array([1, 2, 2, 4]), np.array([[1.5, 2.5], [2.5, 2.5], [1.5, 4.5], [2.5, 4.5]]), part_load=True)
    cop_full = COP(np.array([1, 2, 2, 4, 2, 4, 4, 8]),
                   np.array([[1.5, 2.5, 4.5], [2.5, 2.5, 4.5], [1.5, 4.5, 4.5], [2.5, 4.5, 4.5],
                             [1.5, 2.5, 8.5], [2.5, 2.5, 8.5], [1.5, 4.5, 8.5], [2.5, 4.5, 8.5]]),
                   secondary=True, part_load=True)
    eer_sec = EER(np.array([1, 2, 2, 4]), np.array([[1.5, 2.5], [2.5, 2.5], [1.5, 4.5], [2.5, 4.5]]), secondary=True)
    eer_part = EER(np.array([1, 2, 2, 4]), np.array([[1.5, 2.5], [2.5, 2.5], [1.5, 4.5], [2.5, 4.5]]), part_load=True)
    eer_full = EER(np.array([1, 2, 2, 4, 2, 4, 4, 8]),
                   np.array([[1.5, 2.5, 4.5], [2.5, 2.5, 4.5], [1.5, 4.5, 4.5], [2.5, 4.5, 4.5],
                             [1.5, 2.5, 8.5], [2.5, 2.5, 8.5], [1.5, 4.5, 8.5], [2.5, 4.5, 8.5]]),
                   secondary=True, part_load=True)
    assert 'Temperature dependent COP' == cop_basic.__repr__()
    assert 'Temperature dependent EER' == eer_basic.__repr__()
    assert 'Temperature dependent COP' == cop_sec.__repr__()
    assert 'Temperature and part-load dependent COP' == cop_part.__repr__()
    assert 'Temperature and part-load dependent COP' == cop_full.__repr__()
    assert 'Temperature dependent EER' == eer_sec.__repr__()
    assert 'Temperature and part-load dependent EER' == eer_part.__repr__()
    assert 'Temperature and part-load dependent EER' == eer_full.__repr__()

    eer_combined = EERCombined(20, 5, 10)
    assert '\n' \
           'Active cooling:\n' \
           '\tSEER [-]: 5\n' \
           'Passive cooling:\n' \
           '\tSEER [-]: 20\n' \
           'With active cooling above [°C]: 10' == eer_combined.__repr__()

    eer_combined = EERCombined(20, 5, months_active_cooling=[5, 6])
    assert '\n' \
           'Active cooling:\n' \
           '\tSEER [-]: 5\n' \
           'Passive cooling:\n' \
           '\tSEER [-]: 20\n' \
           'With active cooling in months [-]: [5 6]' == eer_combined.__repr__()
