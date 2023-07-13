"""
This file contains the test for the pipedata
"""

from GHEtool.VariableClasses.PipeData import *
from GHEtool.VariableClasses import FluidData
import matplotlib.pyplot as plt
import numpy as np
import pygfunction as gt


### Test U-pipes
def test_empty_class():
    assert not SingleUPipe().check_values()
    assert not DoubleUPipe().check_values()
    assert not MultipleUTube().check_values()


def test_axissym():
    single = SingleUPipe(1, 0.016, 0.02, 2, 0.02)
    double = DoubleUPipe(1, 0.016, 0.02, 2, 0.02)
    assert np.array_equal(single._axis_symmetrical_pipe, [(-0.02, 2.4492935982947064e-18), (0.02, -4.898587196589413e-18)])
    assert np.array_equal(double._axis_symmetrical_pipe, [(-0.02, 2.4492935982947064e-18), (0.02, -4.898587196589413e-18), (-3.673940397442059e-18, -0.02), (6.123233995736766e-18, 0.02)])
    assert np.array_equal(single._axis_symmetrical_pipe, MultipleUTube(1, 0.16, 0.02, 2, 0.02, 1)._axis_symmetrical_pipe)
    assert np.array_equal(double._axis_symmetrical_pipe, MultipleUTube(1, 0.16, 0.02, 2, 0.02, 2)._axis_symmetrical_pipe)


def test_pipe_thermal_resistance():
    single = SingleUPipe(1, 0.016, 0.02, 2, 0.02)
    double = DoubleUPipe(1, 0.016, 0.02, 2, 0.02)
    U = MultipleUTube(1, 0.016, 0.02, 2, 0.02)
    single.calculate_pipe_thermal_resistance()
    double.calculate_pipe_thermal_resistance()
    U.calculate_pipe_thermal_resistance()
    assert np.isclose(single.R_p, double.R_p)
    assert np.isclose(single.R_p, U.R_p)
    assert np.isclose(single.R_p, 0.017757199605368243)


def test_calculate_convective_heat_transfer_coefficient():
    fluid_data = FluidData(0.2, 0.568, 998, 4180, 1e-3)
    single = SingleUPipe(1, 0.016, 0.02, 2, 0.02)
    double = DoubleUPipe(1, 0.016, 0.02, 2, 0.02)
    Us = MultipleUTube(1, 0.016, 0.02, 2, 0.02, 1)
    Ud = MultipleUTube(1, 0.016, 0.02, 2, 0.02, 2)
    assert np.isclose(single.calculate_convective_heat_transfer_coefficient(fluid_data), 1143.6170532222986)
    assert np.isclose(Us.calculate_convective_heat_transfer_coefficient(fluid_data), 1143.6170532222986)
    assert np.isclose(double.calculate_convective_heat_transfer_coefficient(fluid_data), 553.7476734615789)
    assert np.isclose(Ud.calculate_convective_heat_transfer_coefficient(fluid_data), 553.7476734615789)


def test_draw_internals(monkeypatch):
    pipe = MultipleUTube(1, 0.015, 0.02, 0.4, 0.05)
    monkeypatch.setattr(plt, 'show', lambda: None)
    pipe.draw_borehole_internal(0.075)


def test_pipe_data():
    data = MultipleUTube(1, 0.015, 0.02, 0.4, 0.05, 2)
    assert data.k_g == 1
    assert data.r_in == 0.015
    assert data.r_out == 0.02
    assert data.k_p == 0.4
    assert data.D_s == 0.05
    assert data.number_of_pipes == 2


def test_pipe_data_equal():
    data = MultipleUTube(1, 0.015, 0.02, 0.4, 0.05, 2)
    data2 = MultipleUTube(1, 0.015, 0.02, 0.4, 0.05, 2)
    assert data == data2


def test_pipe_data_unequal():
    data = MultipleUTube(1, 0.015, 0.02, 0.4, 0.05, 2)
    data2 = MultipleUTube(1, 0.016, 0.02, 0.4, 0.05, 2)
    assert data != data2