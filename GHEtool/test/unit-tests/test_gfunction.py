import copy
import time

import numpy as np
import pandas as pd
import pygfunction as gt
import pytest
from pytest import raises

from GHEtool import Borefield, FOLDER
from GHEtool.VariableClasses import FIFO, GFunction

borehole_length_array = np.array([1, 5, 6])
borehole_length_array_empty = np.array([])
borehole_length_array_threshold = np.array([30, 60, 100])
time_value_array_empty = np.array([])
time_value_array = np.array([1, 100, 1000, 10000])

borefield = gt.borefield.Borefield.rectangle_field(5, 5, 5, 5, 100, 1, 0.075)
borefield_less_deep = gt.borefield.Borefield.rectangle_field(5, 5, 5, 5, 80, 1, 0.075)
borefield_more_deep = gt.borefield.Borefield.rectangle_field(5, 5, 5, 5, 110, 1, 0.075)
borefield_ghe = Borefield()


def test_equal_borefields():
    borefield1 = gt.borefield.Borefield.rectangle_field(1, 1, 5, 5, 100, 4, 0.075)
    borefield2 = gt.borefield.Borefield.rectangle_field(1, 1, 5, 5, 100, 4, 0.075)

    gfunc = GFunction()
    gfunc.borefield = borefield1
    assert gfunc._check_borefield(borefield2)


def test_unequal_borefields():
    borefield1 = gt.borefield.Borefield.rectangle_field(1, 1, 5, 5, 100, 4, 0.075)
    borefield2 = gt.borefield.Borefield.rectangle_field(2, 1, 5, 5, 100, 4, 0.075)

    gfunc = GFunction()
    gfunc.borefield = borefield1
    assert not gfunc._check_borefield(borefield2)


def test_equal_borefields2():
    borefield1 = gt.borefield.Borefield.rectangle_field(10, 10, 5, 5, 100, 4, 0.075)
    borefield2 = gt.borefield.Borefield.rectangle_field(10, 10, 5, 5, 100, 4, 0.075)

    gfunc = GFunction()
    gfunc.borefield = borefield1
    assert gfunc._check_borefield(borefield2)


def test_unequal_borefields2():
    borefield1 = gt.borefield.Borefield.rectangle_field(10, 10, 5, 5, 100, 4, 0.075)
    borefield2 = gt.borefield.Borefield.rectangle_field(10, 10, 6, 5, 100, 4, 0.075)

    gfunc = GFunction()
    gfunc.borefield = borefield1
    assert not gfunc._check_borefield(borefield2)


def test_store_previous_values():
    gfunc = GFunction()
    assert gfunc.store_previous_values
    assert gfunc._store_previous_values_backup

    gfunc.store_previous_values = False
    assert not gfunc.store_previous_values
    assert not gfunc._store_previous_values_backup

    gfunc._store_previous_values = True
    assert gfunc.store_previous_values
    assert not gfunc._store_previous_values_backup


def test_equal_alpha():
    gfunc = GFunction()
    gfunc.alpha = 2

    assert gfunc._check_alpha(2)


def test_unequal_alpha():
    gfunc = GFunction()
    gfunc.alpha = 2

    assert not gfunc._check_alpha(3)

    assert not gfunc._check_alpha(0)


def test_nearest_value_empty():
    gfunc = GFunction()
    assert False == gfunc._nearest_value(borehole_length_array_empty, 5)


def test_nearest_value_index():
    gfunc = GFunction()
    assert 1, 0 == gfunc._nearest_value(borehole_length_array, 0)
    assert 1, 0 == gfunc._nearest_value(borehole_length_array, 1)
    assert 1, 0 == gfunc._nearest_value(borehole_length_array, 2)
    assert 5, 1 == gfunc._nearest_value(borehole_length_array, 4)
    assert 5, 1 == gfunc._nearest_value(borehole_length_array, 5)
    assert 6, 2 == gfunc._nearest_value(borehole_length_array, 100)


def test_nearest_borehole_length_index():
    gfunc = GFunction()
    gfunc.borehole_length_array = np.array([1, 5, 6])
    assert (None, 0) == gfunc._get_nearest_borehole_length_index(0.9)
    assert (None, None) == gfunc._get_nearest_borehole_length_index(100)
    assert (None, None) == gfunc._get_nearest_borehole_length_index(3)
    assert (1, 1) == gfunc._get_nearest_borehole_length_index(5)
    assert (2, None) == gfunc._get_nearest_borehole_length_index(7)
    gfunc.borehole_length_array = np.array([4, 5, 6])
    assert (0, 1) == gfunc._get_nearest_borehole_length_index(4.8)

    with raises(ValueError):
        gfunc._get_nearest_borehole_length_index(-100)


def test_nearest_borehole_length_index_threshold():
    gfunc = GFunction()
    gfunc.borehole_length_array = borehole_length_array_threshold
    assert (None, None) == gfunc._get_nearest_borehole_length_index(5)
    assert (None, None) == gfunc._get_nearest_borehole_length_index(50)
    assert (None, None) == gfunc._get_nearest_borehole_length_index(95)
    assert (None, None) == gfunc._get_nearest_borehole_length_index(40)


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
    test = {"method": "similarities", "linear_threshold": 24 * 3600}
    gfunc.set_options_gfunction_calculation(test)
    assert gfunc.options == test
    gfunc.set_options_gfunction_calculation({"method": "similarities"})
    assert gfunc.options == test
    gfunc.set_options_gfunction_calculation({"method": "similarities"}, add=False)
    assert gfunc.options == {"method": "similarities"}


def test_calculate_gfunctions_speed_test():
    gfunc = GFunction()
    alpha = 0.00005
    time_values = borefield_ghe.load.time_L3

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
    time_values = borefield_ghe.load.time_L4

    gfunc.calculate(time_values, borefield, alpha)
    gfunc_val = copy.copy(gfunc.previous_gfunctions)

    assert np.array_equal(gfunc.previous_gfunctions,
                          gt.gfunction.gFunction(borefield, alpha, gfunc.time_array).gFunc)
    assert not np.array_equal(gfunc.calculate(borefield_ghe.load.time_L3, borefield, alpha),
                              gt.gfunction.gFunction(borefield, alpha, borefield_ghe.load.time_L3).gFunc)
    assert np.array_equal(gfunc_val, gfunc.previous_gfunctions)
    assert not np.array_equal(gfunc.calculate(borefield_ghe.load.time_L3[20:], borefield, alpha),
                              gt.gfunction.gFunction(borefield, alpha, borefield_ghe.load.time_L3[20:]).gFunc)
    assert np.array_equal(gfunc_val, gfunc.previous_gfunctions)

    gfunc.remove_previous_data()
    gfunc.calculate(borefield_ghe.load.time_L3[-12:], borefield, alpha)
    gfunc_val = copy.copy(gfunc.previous_gfunctions)
    # check if values are correctly calculated
    assert np.array_equal(gfunc.previous_gfunctions,
                          gt.gfunction.gFunction(borefield, alpha, gfunc.time_array).gFunc)

    # gvalues should be calculated, not interpolated
    gfunc_cal = gfunc.calculate(borefield_ghe.load.time_L3[:12], borefield, alpha)
    gfunc_pyg = gt.gfunction.gFunction(borefield, alpha, borefield_ghe.load.time_L3[:12]).gFunc
    assert np.array_equal(gfunc_cal, gfunc_pyg)
    # saved values should not have been overwritten
    assert not np.array_equal(gfunc_val, gfunc.previous_gfunctions)
    assert np.array_equal(gfunc_cal, gfunc.previous_gfunctions)

    # check if data will be overwritten
    gfunc_cal = gfunc.calculate(borefield_ghe.load.time_L3[:13], borefield, alpha)
    gfunc_pyg = gt.gfunction.gFunction(borefield, alpha, borefield_ghe.load.time_L3[:13]).gFunc
    # check if values are correctly calculated
    assert np.array_equal(gfunc_cal, gfunc_pyg)
    # values should have been overwritten
    assert not np.array_equal(gfunc_val, gfunc.previous_gfunctions)
    gfunc_val = copy.copy(gfunc.previous_gfunctions)

    # check if data will be overwritten
    gfunc.calculate(borefield_ghe.load.time_L4, borefield, alpha)
    gfunc_pyg = gt.gfunction.gFunction(borefield, alpha, gfunc.time_array).gFunc
    # check if values are correctly calculated
    assert np.array_equal(gfunc.previous_gfunctions, gfunc_pyg)
    # values should have been overwritten
    assert not np.array_equal(gfunc_val, gfunc.previous_gfunctions)
    gfunc_val = copy.copy(gfunc.previous_gfunctions)

    # test with smaller field, should not be interpolated
    gfunc_cal = gfunc.calculate(borefield_ghe.load.time_L3[:20], borefield_less_deep, alpha)
    gfunc_pyg = gt.gfunction.gFunction(borefield_less_deep, alpha, borefield_ghe.load.time_L3[:20]).gFunc
    # check if values are correctly calculated
    assert np.array_equal(gfunc_cal, gfunc_pyg)
    # values should not have been overwritten
    assert np.array_equal(gfunc_val, gfunc.previous_gfunctions)

    # run again to unittest that the data will not be overwritten
    gfunc.previous_gfunctions[0] = 100
    test = copy.copy(gfunc.previous_gfunctions)
    gfunc.calculate(borefield_ghe.load.time_L4, borefield, alpha)
    assert np.array_equal(test, gfunc.previous_gfunctions)


def _change_borefield_borehole_length(borefield, borehole_length):
    borefield.H = np.full(borefield.nBoreholes, borehole_length)


def test_store_2D_data():
    gfunc = GFunction()
    alpha = 0.00005
    time_values = borefield_ghe.load.time_L4

    gfunc.calculate(time_values, borefield, alpha)
    gfunc_val = copy.copy(gfunc.previous_gfunctions)

    _change_borefield_borehole_length(borefield, 120)
    gfunc.calculate(time_values, borefield, alpha)

    assert gfunc.borehole_length_array.shape[0] == 2
    assert np.array_equal(gfunc.previous_gfunctions[0], gfunc_val)

    _change_borefield_borehole_length(borefield, 80)
    gfunc.calculate(time_values, borefield, alpha)

    assert gfunc.borehole_length_array.shape[0] == 3
    assert np.array_equal(gfunc.previous_gfunctions[1], gfunc_val)

    gfunc.remove_previous_data()

    # do the same but now first with other sequence of 100, 80, 120m
    _change_borefield_borehole_length(borefield, 100)
    gfunc.calculate(time_values, borefield, alpha)
    gfunc_val = copy.copy(gfunc.previous_gfunctions)

    _change_borefield_borehole_length(borefield, 80)
    gfunc.calculate(time_values, borefield, alpha)

    assert gfunc.borehole_length_array.shape[0] == 2
    assert np.array_equal(gfunc.previous_gfunctions[1], gfunc_val)

    _change_borefield_borehole_length(borefield, 120)
    gfunc.calculate(time_values, borefield, alpha)

    assert gfunc.borehole_length_array.shape[0] == 3
    assert np.array_equal(gfunc.previous_gfunctions[1], gfunc_val)

    # test if data is removed
    _change_borefield_borehole_length(borefield, 130)
    gfunc.calculate(time_values, borefield, alpha * 1.01)
    assert gfunc.borehole_length_array.size == 1

    _change_borefield_borehole_length(borefield, 110)
    gfunc.calculate(time_values, borefield, alpha * 1.01)
    assert gfunc.borehole_length_array.shape[0] == 2

    # test if data is removed
    borefield_2 = gt.borefield.Borefield.rectangle_field(5, 6, 5, 5, 100, 1, 0.075)
    gfunc.calculate(time_values, borefield_2, alpha * 1.01)
    assert gfunc.borehole_length_array.size == 1


def test_interpolate_2D():
    gfunc = GFunction()
    alpha = 0.00005
    time_values = borefield_ghe.load.time_L4

    # populate data
    _change_borefield_borehole_length(borefield, 100)
    gfunc.calculate(time_values, borefield, alpha)

    _change_borefield_borehole_length(borefield, 120)
    gfunc.calculate(time_values, borefield, alpha)

    _change_borefield_borehole_length(borefield, 80)
    gfunc.calculate(time_values, borefield, alpha)

    _change_borefield_borehole_length(borefield, 110)
    gfunc_calc = gfunc.calculate(gfunc.time_array, borefield, alpha)
    gfunc_pyg = gt.gfunction.gFunction(borefield, alpha, gfunc.time_array).gFunc

    assert np.array_equal(gfunc.borehole_length_array, np.array([80, 100, 120]))
    assert gfunc_calc.shape == gfunc_pyg.shape
    assert not np.array_equal(gfunc_calc, gfunc_pyg)

    _change_borefield_borehole_length(borefield, 100)
    gfunc_calc = gfunc.calculate(borefield_ghe.load.time_L3[:20], borefield, alpha)
    gfunc_pyg = gt.gfunction.gFunction(borefield, alpha, borefield_ghe.load.time_L3[:20]).gFunc

    assert np.array_equal(gfunc.borehole_length_array, np.array([80, 100, 120]))
    assert gfunc_pyg.size == gfunc_calc.size
    assert not np.array_equal(gfunc_calc, gfunc_pyg)

    time_double = borefield_ghe.load.time_L3[:20]
    time_double = np.insert(time_double, -1, time_double[-1])

    gfunc_calc = gfunc.calculate(time_double, borefield, alpha)
    gfunc_pyg = gt.gfunction.gFunction(borefield, alpha, time_double[:-1]).gFunc

    assert np.array_equal(gfunc.borehole_length_array, np.array([80, 100, 120]))
    assert gfunc_pyg.size + 1 == gfunc_calc.size
    assert not np.array_equal(gfunc_calc[:-1], gfunc_pyg)
    assert gfunc_calc[-1] == gfunc_calc[-2]

    # calculate anyhow
    gfunc.store_previous_values = False
    gfunc_calc = gfunc.calculate(borefield_ghe.load.time_L3[:20], borefield, alpha)
    assert np.allclose(gfunc_calc, [14.89758799, 19.00729376, 21.25068071, 22.6936062, 23.70823959, 24.4633899,
                                    25.04810995, 25.51433124, 25.89459298, 26.21041712, 26.47665307, 26.70390003,
                                    26.89993724, 27.07060881, 27.22039279, 27.35277941, 27.47052956, 27.57585579,
                                    27.67055182, 27.75608682])
    gfunc.store_previous_values = True
    gfunc_calc = gfunc.calculate(borefield_ghe.load.time_L3[:20], borefield, alpha)
    assert np.allclose(gfunc_calc, [15.21723783, 19.21174728, 21.39698711, 22.78389769, 23.78126837, 24.51443669,
                                    25.09618046, 25.5292184, 25.90238329, 26.22140026, 26.48339286, 26.70550955,
                                    26.90228268, 27.07574976, 27.20792103, 27.33922595, 27.46457098, 27.56161827,
                                    27.65866557, 27.74718794])

    # now with argument
    gfunc_calc = gfunc.calculate(borefield_ghe.load.time_L3[:20], borefield, alpha, interpolate=False)
    assert np.allclose(gfunc_calc, [14.89758799, 19.00729376, 21.25068071, 22.6936062, 23.70823959, 24.4633899,
                                    25.04810995, 25.51433124, 25.89459298, 26.21041712, 26.47665307, 26.70390003,
                                    26.89993724, 27.07060881, 27.22039279, 27.35277941, 27.47052956, 27.57585579,
                                    27.67055182, 27.75608682])

    gfunc_calc = gfunc.calculate(borefield_ghe.load.time_L3[:20], borefield, alpha, interpolate=True)
    assert np.allclose(gfunc_calc, [15.21723783, 19.21174728, 21.39698711, 22.78389769, 23.78126837, 24.51443669,
                                    25.09618046, 25.5292184, 25.90238329, 26.22140026, 26.48339286, 26.70550955,
                                    26.90228268, 27.07574976, 27.20792103, 27.33922595, 27.46457098, 27.56161827,
                                    27.65866557, 27.74718794])
    # default is still interpolate is True
    gfunc_calc = gfunc.calculate(borefield_ghe.load.time_L3[:20], borefield, alpha)
    assert np.allclose(gfunc_calc, [15.21723783, 19.21174728, 21.39698711, 22.78389769, 23.78126837, 24.51443669,
                                    25.09618046, 25.5292184, 25.90238329, 26.22140026, 26.48339286, 26.70550955,
                                    26.90228268, 27.07574976, 27.20792103, 27.33922595, 27.46457098, 27.56161827,
                                    27.65866557, 27.74718794])


def test_no_extrapolation():
    gfunc = GFunction()
    alpha = 0.00005
    time_values = borefield_ghe.load.time_L4
    gfunc.no_extrapolation = False
    gfunc.calculate(time_values, borefield, alpha)

    assert np.array_equal(gfunc.previous_gfunctions,
                          gt.gfunction.gFunction(borefield, alpha, gfunc.time_array).gFunc)
    # these should equal since there is no extrapolation
    assert np.array_equal(gfunc.calculate(borefield_ghe.load.time_L3[:20], borefield, alpha),
                          gt.gfunction.gFunction(borefield, alpha, borefield_ghe.load.time_L3[:20]).gFunc)


def test_floating_number():
    gfunc = GFunction()
    alpha = 0.00005
    time_values = borefield_ghe.load.time_L4

    # populate data
    _change_borefield_borehole_length(borefield, 100)
    gfunc.calculate(time_values, borefield, alpha)

    _change_borefield_borehole_length(borefield, 120)
    gfunc.calculate(time_values, borefield, alpha)

    _change_borefield_borehole_length(borefield, 80)
    gfunc.calculate(time_values, borefield, alpha)

    _change_borefield_borehole_length(borefield, 100)
    assert gfunc.calculate(7500., borefield, alpha) != gt.gfunction.gFunction(borefield, alpha, 7500.).gFunc
    assert gfunc.calculate(gfunc.time_array[0], borefield, alpha) == \
           gt.gfunction.gFunction(borefield, alpha, gfunc.time_array[0]).gFunc


def test_fifo():
    fifo = FIFO()
    assert fifo.fifo_list == []
    fifo.add(84)
    assert not fifo.in_fifo_list(84)
    assert fifo.fifo_list == [84]
    fifo.add(46)
    assert fifo.fifo_list == [84, 46]
    assert fifo.in_fifo_list(84)
    assert not fifo.in_fifo_list(46)
    fifo.add(30)
    assert fifo.fifo_list == [46, 30]
    assert not fifo.in_fifo_list(84)
    fifo.clear()
    assert fifo.fifo_list == []


def test_stuck_in_loop():
    gfunc = GFunction()
    alpha = 0.00005
    time_values = borefield_ghe.load.time_L3
    for bor in borefield:
        bor.H = 100
    gfunc.calculate(time_values, borefield, alpha)
    for bor in borefield:
        bor.H = 120
    gfunc.calculate(time_values, borefield, alpha)
    for bor in borefield:
        bor.H = 110
    temp = gfunc.calculate(time_values, borefield, alpha)
    for bor in borefield:
        bor.H = 111
    gfunc.calculate(time_values, borefield, alpha)
    for bor in borefield:
        bor.H = 110
    temp = gfunc.calculate(time_values, borefield, alpha)
    assert np.allclose(temp, gfunc.calculate(time_values, borefield, alpha))
    for bor in borefield:
        bor.H = 110.5
    assert np.allclose(temp, gfunc.calculate(time_values, borefield, alpha))


def test_negative_values():
    gfunc = GFunction()
    gfunc.use_cyl_correction_when_negative = False
    field = gt.borefield.Borefield.rectangle_field(10, 7, 2, 2, 150, 2, 0.2)
    time = gt.load_aggregation.ClaessonJaved(3600, 3600 * 8760 * 20).get_times_for_simulation()
    g_func = gfunc.calculate(time, field, 1 / 5000 / 1000, interpolate=False)
    assert not np.all(g_func > 0)
    assert np.isclose(np.min(g_func), -519964.66315776133)

    gfunc.use_cyl_correction_when_negative = True
    g_func = gfunc.calculate(time, field, 1 / 5000 / 1000, interpolate=False)
    assert np.all(g_func > 0)
    assert np.isclose(np.min(g_func), 0.14299471464245733)


def test_ann_boundaries():
    gfunc = GFunction()
    time_steps = np.arange(3600, 3600 * 24 * 365 * 100, 3600)
    with pytest.warns():
        borefield = gt.borefield.Borefield.rectangle_field(5, 1, 4, 6, 20, 0.5, 0.1)
        gfunc.borefield = borefield
        gfunc.calculate(time_steps, borefield, 1.1249999999999998e-06, use_neural_network=True,
                        borefield_description={"type": 3, "N_1": 2, "N_2": 1,
                                               "B_1": 4, "B_2": 6})
    with pytest.warns():
        borefield = gt.borefield.Borefield.rectangle_field(5, 1, 4, 6, 500, 0.5, 0.1)
        gfunc.borefield = borefield
        gfunc.calculate(time_steps, borefield, 1.1249999999999998e-06, use_neural_network=True,
                        borefield_description={"type": 3, "N_1": 2, "N_2": 1,
                                               "B_1": 4, "B_2": 6})
    with pytest.warns():
        borefield = gt.borefield.Borefield.rectangle_field(5, 1, 4, 6, 100, 8, 0.1)
        gfunc.borefield = borefield
        gfunc.calculate(time_steps, borefield, 1.1249999999999998e-06, use_neural_network=True,
                        borefield_description={"type": 3, "N_1": 2, "N_2": 1,
                                               "B_1": 4, "B_2": 6})
    with pytest.warns():
        borefield = gt.borefield.Borefield.rectangle_field(5, 1, 4, 6, 100, -2, 0.1)
        gfunc.borefield = borefield
        gfunc.calculate(time_steps, borefield, 1.1249999999999998e-06, use_neural_network=True,
                        borefield_description={"type": 3, "N_1": 2, "N_2": 1,
                                               "B_1": 4, "B_2": 6})
    with pytest.warns():
        borefield = gt.borefield.Borefield.rectangle_field(5, 1, 4, 6, 100, 0.5, 0.1)
        gfunc.borefield = borefield
        gfunc.calculate(time_steps, borefield, 1.1249999999999998e-06, use_neural_network=True,
                        borefield_description={"type": 3, "N_1": 31, "N_2": 1,
                                               "B_1": 4, "B_2": 6})
    with pytest.warns():
        borefield = gt.borefield.Borefield.rectangle_field(5, 1, 4, 6, 100, 0.5, 0.1)
        gfunc.borefield = borefield
        gfunc.calculate(time_steps, borefield, 1.1249999999999998e-06, use_neural_network=True,
                        borefield_description={"type": 3, "N_1": 0, "N_2": 1,
                                               "B_1": 4, "B_2": 6})
    with pytest.warns():
        borefield = gt.borefield.Borefield.rectangle_field(5, 1, 4, 6, 100, 0.5, 0.1)
        gfunc.borefield = borefield
        gfunc.calculate(time_steps, borefield, 1.1249999999999998e-06, use_neural_network=True,
                        borefield_description={"type": 3, "N_1": 2, "N_2": 31,
                                               "B_1": 4, "B_2": 6})
    with pytest.warns():
        borefield = gt.borefield.Borefield.rectangle_field(5, 1, 4, 6, 100, 0.5, 0.1)
        gfunc.borefield = borefield
        gfunc.calculate(time_steps, borefield, 1.1249999999999998e-06, use_neural_network=True,
                        borefield_description={"type": 3, "N_1": 1, "N_2": 0,
                                               "B_1": 4, "B_2": 6})

    with pytest.warns():
        borefield = gt.borefield.Borefield.rectangle_field(5, 1, 4, 6, 100, 0.5, 0.1)
        gfunc.borefield = borefield
        gfunc.calculate(time_steps, borefield, 1.1249999999999998e-06, use_neural_network=True,
                        borefield_description={"type": 3, "N_1": 1, "N_2": 2,
                                               "B_1": 1, "B_2": 6})
    with pytest.warns():
        borefield = gt.borefield.Borefield.rectangle_field(5, 1, 4, 6, 100, 0.5, 0.1)
        gfunc.borefield = borefield
        gfunc.calculate(time_steps, borefield, 1.1249999999999998e-06, use_neural_network=True,
                        borefield_description={"type": 3, "N_1": 1, "N_2": 2,
                                               "B_1": 11, "B_2": 6})
    with pytest.warns():
        borefield = gt.borefield.Borefield.rectangle_field(5, 1, 4, 6, 100, 0.5, 0.1)
        gfunc.borefield = borefield
        gfunc.calculate(time_steps, borefield, 1.1249999999999998e-06, use_neural_network=True,
                        borefield_description={"type": 3, "N_1": 1, "N_2": 2,
                                               "B_1": 2, "B_2": 1})
    with pytest.warns():
        borefield = gt.borefield.Borefield.rectangle_field(5, 1, 4, 6, 100, 0.5, 0.1)
        gfunc.borefield = borefield
        gfunc.calculate(time_steps, borefield, 1.1249999999999998e-06, use_neural_network=True,
                        borefield_description={"type": 3, "N_1": 1, "N_2": 2,
                                               "B_1": 2, "B_2": 11})
    with pytest.warns():
        borefield = gt.borefield.Borefield.rectangle_field(5, 1, 4, 6, 100, 0.5, 0.01)
        gfunc.borefield = borefield
        gfunc.calculate(time_steps, borefield, 1.1249999999999998e-06, use_neural_network=True,
                        borefield_description={"type": 3, "N_1": 1, "N_2": 2,
                                               "B_1": 2, "B_2": 2})
    with pytest.warns():
        borefield = gt.borefield.Borefield.rectangle_field(5, 1, 4, 6, 100, 0.5, 0.2)
        gfunc.borefield = borefield
        gfunc.calculate(time_steps, borefield, 1.1249999999999998e-06, use_neural_network=True,
                        borefield_description={"type": 3, "N_1": 1, "N_2": 2,
                                               "B_1": 2, "B_2": 2})
    with pytest.warns():
        borefield = gt.borefield.Borefield.rectangle_field(5, 1, 4, 6, 100, 0.5, 0.1)
        gfunc.borefield = borefield
        gfunc.calculate(time_steps, borefield, 1e-8, use_neural_network=True,
                        borefield_description={"type": 3, "N_1": 1, "N_2": 2,
                                               "B_1": 2, "B_2": 2})
    with pytest.warns():
        borefield = gt.borefield.Borefield.rectangle_field(5, 1, 4, 6, 100, 0.5, 0.1)
        gfunc.borefield = borefield
        gfunc.calculate(time_steps, borefield, 1e-5, use_neural_network=True,
                        borefield_description={"type": 3, "N_1": 1, "N_2": 2,
                                               "B_1": 2, "B_2": 2})
    with pytest.raises(ValueError):
        borefield = gt.borefield.Borefield.rectangle_field(5, 1, 4, 6, 100, 0.5, 0.1)
        gfunc.borefield = borefield
        gfunc.calculate(time_steps, borefield, 1e-6, use_neural_network=True,
                        borefield_description={"type": -1, "N_1": 1, "N_2": 2,
                                               "B_1": 2, "B_2": 2})
    with pytest.raises(ValueError):
        borefield = gt.borefield.Borefield.rectangle_field(5, 1, 4, 6, 100, 0.5, 0.1)
        gfunc.borefield = borefield
        gfunc.calculate(time_steps, borefield, 1e-6, use_neural_network=True,
                        borefield_description={"type": 7, "N_1": 1, "N_2": 2,
                                               "B_1": 2, "B_2": 2})

# def test_ann_borefield_result_TB():
#     borefield1 = gt.borefield.Borefield.U_shaped_field(12, 10, 10, 8, 100, 2, 0.13)
#
#     time_steps_default = gt.load_aggregation.ClaessonJaved(3600, 3600 * 8760 * 100).get_times_for_simulation()
#     time_steps = np.arange(3600, 3600 * 24, 3600)
#
#     gfunc = GFunction()
#     gfunc.borefield = borefield1
#     g_func_regular = gfunc.calculate(time_steps, borefield1, 1.1249999999999998e-06, use_neural_network=False)
#     g_func_ann = gfunc.calculate(time_steps, borefield1, 1.1249999999999998e-06, use_neural_network=True,
#                                  borefield_description={"type": 1, "N_1": 12, "N_2": 10,
#                                                         "B_1": 10, "B_2": 8})
#     import matplotlib.pyplot as plt
#     plt.plot(g_func_ann, label="With ANN")
#     plt.plot(g_func_regular, label="Regular, without ANN")
#     plt.legend()
#     plt.show()
#
#     assert np.allclose(g_func_regular, g_func_ann, rtol=0.05)
#
#
# def test_ann_borefield_result_WP():
#     borefield1 = gt.borefield.Borefield.rectangle_field(4, 7, 5, 6, 100, 0.7, 0.075)
#
#     gfunc = GFunction()
#     gfunc.borefield = borefield1
#     time_steps = np.arange(3600, 3600 * 24 * 365 * 100, 3600)
#     g_func_regular = gfunc.calculate(time_steps, borefield1, 0.75 / 1000000, use_neural_network=False,
#                                      borefield_description={"type": 3, "N_1": 4, "N_2": 7,
#                                                             "B_1": 5, "B_2": 6})
#     g_func_ann = gfunc.calculate(time_steps, borefield1, 0.75 / 1000000, use_neural_network=True,
#                                  borefield_description={"type": 3, "N_1": 4, "N_2": 7,
#                                                         "B_1": 5, "B_2": 6})
#     import matplotlib.pyplot as plt
#     plt.figure()
#     plt.plot(g_func_ann, label="With ANN")
#     plt.plot(g_func_regular, label="Regular, without ANN")
#     plt.legend()
#
#     plt.figure()
#     plt.plot(time_steps, (g_func_ann - g_func_regular) / g_func_regular * 100, label="Rel diff [%]")
#     plt.legend()
#     plt.show()
