import copy
import time

import numpy as np
import pandas as pd
import pygfunction as gt
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


def test_ann_borefield():
    borefield1 = gt.borefield.Borefield.rectangle_field(1, 2, 5, 6, 100, 4, 0.075)

    gfunc = GFunction()
    gfunc.borefield = borefield1
    time_steps = np.arange(3600, 3600 * 24 * 365 * 100, 3600)
    g_func = gfunc.calculate(time_steps, borefield1, 1 / 5000 / 1000, use_neural_network=True,
                             borefield_description={"type": 3, "N_1": 1, "N_2": 2,
                                                    "B_1": 5, "B_2": 6})

    input_data = (np.array([1, 2, 5, 6, 100, 4, 0.075, 1 / 5000 / 1000, 3]) * np.array(
        [1 / 20, 1 / 20, 1 / 9, 1 / 9, 1 / 1000, 1 / 100, 1 / 0.4, 1 / (10 ** -6),
         1 / 6])).reshape(9, 1)

    model_weights = [
        pd.read_csv(FOLDER.joinpath(f"VariableClasses/Gfunctions/ANN layers/layer_{i}_weights_diff_fields.csv"),
                    sep=";").values
        for i in range(6)]
    res = np.maximum(0, model_weights[0].T.dot(input_data) + model_weights[1])
    res = np.maximum(0, model_weights[2].T.dot(res) + model_weights[3])
    res = np.maximum(0, model_weights[4].T.dot(res) + model_weights[5])
    g_func_numpy = np.cumsum(res, axis=0).reshape(87)
    time_steps_default = gt.load_aggregation.ClaessonJaved(3600, 3600 * 8760 * 100).get_times_for_simulation()
    g_func_numpy = np.interp(time_steps, time_steps_default, g_func_numpy)
    assert np.allclose(g_func, g_func_numpy)


def test_ann_borefield_result_TB():
    borefield1 = gt.borefield.Borefield.rectangle_field(2, 1, 4, 6, 100, 2, 0.1)
    # N_1,N_2,B_1,B_2,H,D,r_b,alpha,shape,dt,result_0,result_1,result_2,result_3,result_4,result_5,result_6,result_7,result_8,result_9,result_10,result_11,result_12,result_13,result_14,result_15,result_16,result_17,result_18,result_19,result_20,result_21,result_22,result_23,result_24,result_25,result_26,result_27,result_28,result_29,result_30,result_31,result_32,result_33,result_34,result_35,result_36,result_37,result_38,result_39,result_40,result_41,result_42,result_43,result_44,result_45,result_46,result_47,result_48,result_49,result_50,result_51,result_52,result_53,result_54,result_55,result_56,result_57,result_58,result_59,result_60,result_61,result_62,result_63,result_64,result_65,result_66,result_67,result_68,result_69,result_70,result_71,result_72,result_73,result_74,result_75,result_76,result_77,result_78,result_79,result_80,result_81,result_82,result_83,result_84,result_85,result_86
    data = [2.0, 1.0, 4.0, 6.0, 100.0, 2.0, 0.1, 1.1249999999999998e-06, 3.0, 1.0625, 0.5672204924892253,
            0.7418143649839172, 0.8599681237932364, 0.9509432497537744,
            1.0254940179524288, 1.1442333353793774, 1.2376299563538078, 1.3149168907894009, 1.3809856370427849,
            1.4387622806000016, 1.5364379194824347, 1.617267418516207, 1.686297730368118, 1.7465832527611276,
            1.800118533950547, 1.8920597063561049, 1.9692539094622776, 2.0358144507587395, 2.0943355267247843,
            2.1465608457817056, 2.2367120850623468, 2.312763462793607, 2.3785502072182614, 2.4365340467420578,
            2.4883939023461625, 2.578223297949685, 2.654452443879622, 2.7209145047630736, 2.7800714374806783,
            2.833584791169094, 2.928008927285981, 3.0102190195748184, 3.0836319603633964, 3.1503471308795334,
            3.2117410621176785, 3.322103651974315, 3.419717928580185, 3.5075337168012677, 3.5874893600748328,
            3.6609519593461766, 3.7921985978949304, 3.9070035636279323, 4.009040949458206, 4.100852706361405,
            4.184280262481978, 4.331152249137318, 4.457465036521126, 4.5681577778104625, 4.666582156034277,
            4.755117701289577, 4.9090330684593075, 5.0396132124475415, 5.152802915704555, 5.25254073160464,
            5.341570677118445, 5.494838551936754, 5.6235161316071585, 5.734095056091165, 5.830812557354395,
            5.916586690938819, 6.062952932225428, 6.184668005309358, 6.288384768815434, 6.378412809329068,
            6.457699711384523, 6.591653335031628, 6.701801581560768, 6.794684172305982, 6.874519298572667,
            6.944177695625422, 7.060273467816655, 7.15420201641207, 7.232176811232924, 7.2981913660108395,
            7.354951739016995, 7.447556601448396, 7.520501919148197, 7.579516910491351, 7.628264384707831,
            7.669206799838913, 7.733879962177762, 7.782818759246749, 7.820996537839091, 7.851509923842294,
            7.876383953329409, 7.9141949898225885, 7.941537301563505]
    time_steps_default = gt.load_aggregation.ClaessonJaved(3600, 3600 * 8760 * 100).get_times_for_simulation()

    time_steps = np.arange(3600, 3600 * 24 * 365 * 100, 3600)
    g_func_data = np.interp(time_steps, time_steps_default, data[10:])
    gfunc = GFunction()
    gfunc.borefield = borefield1
    time_steps = np.arange(3600, 3600 * 24 * 365 * 100, 3600)
    g_func_regular = gfunc.calculate(time_steps, borefield1, 1.1249999999999998e-06, use_neural_network=False,
                                     borefield_description={"type": 3, "N_1": 2, "N_2": 1,
                                                            "B_1": 4, "B_2": 6})
    g_func_ann = gfunc.calculate(time_steps, borefield1, 1.1249999999999998e-06, use_neural_network=True,
                                 borefield_description={"type": 3, "N_1": 2, "N_2": 1,
                                                        "B_1": 4, "B_2": 6})
    """import matplotlib.pyplot as plt
    plt.plot(g_func_ann, label="With ANN")
    plt.plot(g_func_data, label="Input ANN")
    plt.plot(g_func_regular, label="Regular, without ANN")
    plt.legend()
    plt.show()
    """
    assert np.allclose(g_func_data, g_func_ann, rtol=0.03)
    assert np.allclose(g_func_regular, g_func_ann, rtol=0.05, atol=0.5)


def test_ann_borefield_result_WP():
    borefield1 = gt.borefield.Borefield.rectangle_field(4, 7, 5, 6, 100, 0.7, 0.075)

    gfunc = GFunction()
    gfunc.borefield = borefield1
    time_steps = np.arange(3600, 3600 * 24 * 365 * 100, 3600)
    g_func_regular = gfunc.calculate(time_steps, borefield1, 0.75 / 1000000, use_neural_network=False,
                                     borefield_description={"type": 3, "N_1": 4, "N_2": 7,
                                                            "B_1": 5, "B_2": 6})
    g_func_ann = gfunc.calculate(time_steps, borefield1, 0.75 / 1000000, use_neural_network=True,
                                 borefield_description={"type": 3, "N_1": 4, "N_2": 7,
                                                        "B_1": 5, "B_2": 6})
    import matplotlib.pyplot as plt
    plt.figure()
    plt.plot(g_func_ann, label="With ANN")
    plt.plot(g_func_regular, label="Regular, without ANN")
    plt.legend()

    plt.figure()
    plt.plot((g_func_ann - g_func_regular) / g_func_regular * 100, label="Rel diff [%]")
    plt.legend()
    plt.show()
