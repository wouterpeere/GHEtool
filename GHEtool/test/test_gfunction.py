import copy

import pygfunction as gt
import numpy as np
import pytest
import time

from GHEtool.VariableClasses import GFunction
from GHEtool import Borefield


depth_array = np.array([1, 5, 6])
depth_array_empty = np.array([])
depth_array_threshold = np.array([30, 60, 100])
time_value_array_empty = np.array([])
time_value_array = np.array([1, 100, 1000, 10000])

borefield = gt.boreholes.rectangle_field(5, 5, 5, 5, 100, 1, 0.075)
borefield_less_deep = gt.boreholes.rectangle_field(5, 5, 5, 5, 80, 1, 0.075)
borefield_more_deep = gt.boreholes.rectangle_field(5, 5, 5, 5, 110, 1, 0.075)
borefield_ghe = Borefield()


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

    gfunc.alpha = 0
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

    gfunc.time_array = time_value_array_empty
    assert not gfunc._check_time_values(np.array([]))
    assert not gfunc._check_time_values(np.array([1]))

    gfunc.time_array = time_value_array
    assert not gfunc._check_time_values(np.array([]))
    assert not gfunc._check_time_values(np.linspace(1, 5, 10))
    assert gfunc._check_time_values(time_value_array)
    assert gfunc._check_time_values(np.array([5]))
    assert not gfunc._check_time_values(np.array([0.5, 100]))
    assert not gfunc._check_time_values(np.array([100, 100000]))


def test_set_options():
    gfunc = GFunction()
    gfunc.set_options_gfunction_calculation({"Method": "similarities"})
    assert gfunc.options["Method"] == "similarities"


def test_calculate_gfunctions_speed_test():
    gfunc = GFunction()
    alpha = 0.00005
    time_values = borefield_ghe.time_L3_last_year

    time_init_start = time.time()
    gvalues = gfunc.calculate(time_values, borefield, alpha)
    time_init_end = time.time()

    time_inter_start = time.time()
    gvalues2 = gfunc.calculate(time_values, borefield, alpha)
    time_inter_end = time.time()
    assert np.array_equal(gvalues, gvalues2)
    assert time_init_end - time_init_start > time_inter_end - time_inter_start


def test_interpolation_1D():
    gfunc = GFunction()
    alpha = 0.00005
    time_values = borefield_ghe.time_L4

    gfunc.calculate(time_values, borefield, alpha)
    gfunc_val = copy.copy(gfunc.previous_gfunctions)

    assert np.array_equal(gfunc.previous_gfunctions,
                          gt.gfunction.gFunction(borefield, alpha, gfunc.time_array).gFunc)
    assert not np.array_equal(gfunc.calculate(borefield_ghe.time_L3_last_year, borefield, alpha),
                              gt.gfunction.gFunction(borefield, alpha, borefield_ghe.time_L3_last_year).gFunc)
    assert np.array_equal(gfunc_val, gfunc.previous_gfunctions)
    assert not np.array_equal(gfunc.calculate(borefield_ghe.time_L3_last_year[20:], borefield, alpha),
                              gt.gfunction.gFunction(borefield, alpha, borefield_ghe.time_L3_last_year[20:]).gFunc)
    assert np.array_equal(gfunc_val, gfunc.previous_gfunctions)

    gfunc.remove_previous_data()
    gfunc.calculate(borefield_ghe.time_L3_last_year[-12:], borefield, alpha)
    gfunc_val = copy.copy(gfunc.previous_gfunctions)
    # check if values are correctly calculated
    assert np.array_equal(gfunc.previous_gfunctions,
                          gt.gfunction.gFunction(borefield, alpha, gfunc.time_array).gFunc)

    # gvalues should be calculated, not interpolated
    gfunc_cal = gfunc.calculate(borefield_ghe.time_L3_last_year[:12], borefield, alpha)
    gfunc_pyg = gt.gfunction.gFunction(borefield, alpha, borefield_ghe.time_L3_last_year[:12]).gFunc
    assert np.array_equal(gfunc_cal, gfunc_pyg)
    # saved values should not have been overwritten
    assert np.array_equal(gfunc_val, gfunc.previous_gfunctions)

    # check if data will be overwritten
    gfunc_cal = gfunc.calculate(borefield_ghe.time_L3_last_year[:13], borefield, alpha)
    gfunc_pyg = gt.gfunction.gFunction(borefield, alpha, borefield_ghe.time_L3_last_year[:13]).gFunc
    # check if values are correctly calculated
    assert np.array_equal(gfunc_cal, gfunc_pyg)
    # values should have been overwritten
    assert not np.array_equal(gfunc_val, gfunc.previous_gfunctions)
    gfunc_val = copy.copy(gfunc.previous_gfunctions)

    # check if data will be overwritten
    gfunc.calculate(borefield_ghe.time_L4, borefield, alpha)
    gfunc_pyg = gt.gfunction.gFunction(borefield, alpha, gfunc.time_array).gFunc
    # check if values are correctly calculated
    assert np.array_equal(gfunc.previous_gfunctions, gfunc_pyg)
    # values should have been overwritten
    assert not np.array_equal(gfunc_val, gfunc.previous_gfunctions)
    gfunc_val = copy.copy(gfunc.previous_gfunctions)

    # test with smaller field, should not be interpolated
    gfunc_cal = gfunc.calculate(borefield_ghe.time_L3_last_year[:20], borefield_less_deep, alpha)
    gfunc_pyg = gt.gfunction.gFunction(borefield_less_deep, alpha, borefield_ghe.time_L3_last_year[:20]).gFunc
    # check if values are correctly calculated
    assert np.array_equal(gfunc_cal, gfunc_pyg)
    # values should not have been overwritten
    assert np.array_equal(gfunc_val, gfunc.previous_gfunctions)

    # run again to unittest that the data will not be overwritten
    gfunc.previous_gfunctions[0] = 100
    test = copy.copy(gfunc.previous_gfunctions)
    gfunc.calculate(borefield_ghe.time_L4, borefield, alpha)
    assert np.array_equal(test, gfunc.previous_gfunctions)


def test_no_extrapolation():
    gfunc = GFunction()
    alpha = 0.00005
    time_values = borefield_ghe.time_L4
    gfunc.no_extrapolation = False
    gfunc.calculate(time_values, borefield, alpha)

    assert np.array_equal(gfunc.previous_gfunctions,
                          gt.gfunction.gFunction(borefield, alpha, gfunc.time_array).gFunc)
    # these should equal since there is no extrapolation
    assert np.array_equal(gfunc.calculate(borefield_ghe.time_L3_last_year[:20], borefield, alpha),
                          gt.gfunction.gFunction(borefield, alpha, borefield_ghe.time_L3_last_year[:20]).gFunc)
