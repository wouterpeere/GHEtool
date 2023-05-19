import pytest

from GHEtool import *


def test_ground_data():
    data = GroundData(3, 10, 0.2)

    assert data.k_s == 3
    assert data.Tg == 10
    assert data.Rb == 0.2


def test_fluid_data():
    data = FluidData(0.2, 0.568, 998, 4180, 1e-3)
    assert data.mfr == 0.2
    assert data.k_f == 0.568
    assert data.rho == 998
    assert data.Cp == 4180
    assert data.mu == 1e-3


def test_pipe_data():
    data = PipeData(1, 0.015, 0.02, 0.4, 0.05, 2)
    assert data.k_g == 1
    assert data.r_in == 0.015
    assert data.r_out == 0.02
    assert data.k_p == 0.4
    assert data.D_s == 0.05
    assert data.number_of_pipes == 2


def test_ground_data_equal():
    data = GroundData(3, 10, 0.2)
    data2 = GroundData(3, 10, 0.2)
    assert data == data2


def test_ground_data_unequal():
    data = GroundData(3, 10, 0.2)
    data2 = GroundData(3, 11, 0.2)
    assert data != data2


def test_fluid_data_equal():
    data = FluidData(0.2, 0.568, 998, 4180, 1e-3)
    data2 = FluidData(0.2, 0.568, 998, 4180, 1e-3)
    assert data == data2


def test_fluid_data_unequal():
    data = FluidData(0.2, 0.568, 998, 4180, 1e-3)
    data2 = FluidData(0.2, 0.567, 998, 4180, 1e-3)
    assert data != data2


def test_pipe_data_equal():
    data = PipeData(1, 0.015, 0.02, 0.4, 0.05, 2)
    data2 = PipeData(1, 0.015, 0.02, 0.4, 0.05, 2)
    assert data == data2


def test_pipe_data_unequal():
    data = PipeData(1, 0.015, 0.02, 0.4, 0.05, 2)
    data2 = PipeData(1, 0.016, 0.02, 0.4, 0.05, 2)
    assert data != data2


def test_unequal_cross():
    data_pipe = PipeData(1, 0.015, 0.02, 0.4, 0.05, 2)
    data_fluid = FluidData(0.2, 0.568, 998, 4180, 1e-3)
    data_ground = GroundData(3, 10, 0.2)

    assert data_ground != data_pipe
    assert data_fluid != data_pipe
    assert data_pipe != data_fluid


def test_empty_variable_classes():
    ground_data = GroundData()
    fluid_data = FluidData()
    pipe_data = PipeData()
    assert not ground_data.check_values()
    assert not pipe_data.check_values()
    assert not fluid_data.check_values()

def test_set_mfr():
    data_fluid = FluidData(0.2, 0.568, 998, 4180, 1e-3)
    data_fluid.set_mass_flow_rate(10)
    assert data_fluid.mfr == 10
