import pygfunction as gt
import numpy as np
import pytest

from GHEtool.VariableClasses import GFunction


depth_array = np.array([1, 5, 6])
depth_array_empty = np.array([])
depth_array_threshold = np.array([30, 60, 100])
time_value_array_empty = np.array([])
time_value_array = np.array([1, 100, 1000, 10000])


def test_equal_borefields():
    borefield1 = gt.boreholes.rectangle_field(1, 1, 5, 5, 100, 4, 0.075)
    borefield2 = gt.boreholes.rectangle_field(1, 1, 5, 5, 100, 4, 0.075)

    gfunc = GFunction()
    gfunc.borefield = borefield1
    assert gfunc._check_borefield(borefield2)


def test_unequal_borefields():
    borefield1 = gt.boreholes.rectangle_field(1, 1, 5, 5, 100, 4, 0.075)
    borefield2 = gt.boreholes.rectangle_field(2, 1, 5, 5, 100, 4, 0.075)

    gfunc = GFunction()
    gfunc.borefield = borefield1
    assert not gfunc._check_borefield(borefield2)


def test_equal_borefields2():
    borefield1 = gt.boreholes.rectangle_field(10, 10, 5, 5, 100, 4, 0.075)
    borefield2 = gt.boreholes.rectangle_field(10, 10, 5, 5, 100, 4, 0.075)
    
    gfunc = GFunction()
    gfunc.borefield = borefield1
    assert gfunc._check_borefield(borefield2)


def test_unequal_borefields2():
    borefield1 = gt.boreholes.rectangle_field(10, 10, 5, 5, 100, 4, 0.075)
    borefield2 = gt.boreholes.rectangle_field(10, 10, 6, 5, 100, 4, 0.075)

    gfunc = GFunction()
    gfunc.borefield = borefield1
    assert not gfunc._check_borefield(borefield2)


def test_equal_alpha():
    gfunc = GFunction()
    gfunc.alpha = 2

    assert gfunc._check_alpha(2)


def test_unequal_alpha():
    gfunc = GFunction()
    gfunc.alpha = 2

    assert not gfunc._check_alpha(3)


def test_nearest_value_empty():
    gfunc = GFunction()
    assert False == gfunc._nearest_value(depth_array_empty, 5)


def test_nearest_value_index():
    gfunc = GFunction()
    assert 1, 0 == gfunc._nearest_value(depth_array, 0)
    assert 1, 0 == gfunc._nearest_value(depth_array, 1)
    assert 1, 0 == gfunc._nearest_value(depth_array, 2)
    assert 5, 1 == gfunc._nearest_value(depth_array, 4)
    assert 5, 1 == gfunc._nearest_value(depth_array, 5)
    assert 6, 2 == gfunc._nearest_value(depth_array, 100)


def test_nearest_depth_index():
    gfunc = GFunction()
    gfunc.depth_array = depth_array
    assert (None, 0) == gfunc._get_nearest_depth_index(0.1)
    assert (None, None) == gfunc._get_nearest_depth_index(100)
    assert (0, 1) == gfunc._get_nearest_depth_index(3)
    assert (1, 1) == gfunc._get_nearest_depth_index(5)
    assert (2, None) == gfunc._get_nearest_depth_index(20)
    assert (0, 1) == gfunc._get_nearest_depth_index(4)

    try:
        gfunc._get_nearest_depth_index(-100)
    except ValueError:
        assert True


def test_nearest_depth_index_threshold():
    gfunc = GFunction()
    gfunc.depth_array = depth_array_threshold
    assert (None, None) == gfunc._get_nearest_depth_index(5)
    assert (None, None) == gfunc._get_nearest_depth_index(50)
    assert (None, None) == gfunc._get_nearest_depth_index(95)
    assert (None, None) == gfunc._get_nearest_depth_index(40)



def test_check_time_values():
    gfunc = GFunction()

    assert not gfunc._check_time_values(time_value_array_empty, np.array([]))
    assert not gfunc._check_time_values(time_value_array_empty, np.array([1]))
    assert not gfunc._check_time_values(time_value_array, np.array([]))
    assert not gfunc._check_time_values(time_value_array, np.linspace(1, 5, 10))
    assert gfunc._check_time_values(time_value_array, time_value_array)
    assert gfunc._check_time_values(time_value_array, np.array([5]))
    assert not gfunc._check_time_values(time_value_array, np.array([0.5, 100]))
    assert not gfunc._check_time_values(time_value_array, np.array([100, 100000]))


def test_set_options():
    gfunc = GFunction()
    gfunc.set_options_gfunction_calculation({"Method": "similarities"})
    assert gfunc.options["Method"] == "similarities"

