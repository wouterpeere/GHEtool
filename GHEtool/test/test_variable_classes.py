from GHEtool import GroundData, PipeData
from GHEtool.VariableClasses.fluid_data import ConstantFluidData, LinearFluidData
import numpy as np


def test_ground_data():
    data = GroundData(3, 10, 0.2)

    assert data.k_s == 3
    assert data.Tg == 10
    assert data.Rb == 0.2


def test_constant_fluid_data():
    data = ConstantFluidData(0.2, 0.568, 998, 4180, 1e-3)
    assert data.mfr == 0.2
    assert data._k_f == 0.568
    assert data._rho == 998
    assert data._c_p == 4180
    assert data._mu == 1e-3
    assert np.allclose(data.rho(np.arange(0, 20, 0.5)), 998 * np.ones(40))
    assert np.allclose(data.k_f(np.arange(0, 20, 0.5)), 0.568 * np.ones(40))
    assert np.allclose(data.c_p(np.arange(0, 20, 0.5)), 4180 * np.ones(40))
    assert np.allclose(data.mu(np.arange(0, 20, 0.5)), 1e-3 * np.ones(40))


def test_linear_fluid_data():
    data = LinearFluidData(0.2, 0.568, 998, 4180, 1e-3)
    assert data.mfr == 0.2
    assert data._k_f == 0.568
    assert data._rho == 998
    assert data._c_p == 4180
    assert data._mu == 1e-3
    data.set_linear_factor(.012, 2.3, 0.000_024, 3.12)
    assert np.allclose(data.rho(np.arange(0, 20, 0.5)), 998 + 2.3 * np.arange(0, 20, 0.5))
    assert np.allclose(data.k_f(np.arange(0, 20, 0.5)), 0.568 + .012 * np.arange(0, 20, 0.5))
    assert np.allclose(data.c_p(np.arange(0, 20, 0.5)), 4180 + 3.12 * np.arange(0, 20, 0.5))
    assert np.allclose(data.mu(np.arange(0, 20, 0.5)), 1e-3 + 0.000_024 * np.arange(0, 20, 0.5))


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
    data = ConstantFluidData(0.2, 0.568, 998, 4180, 1e-3)
    data2 = ConstantFluidData(0.2, 0.568, 998, 4180, 1e-3)
    assert data == data2


def test_fluid_data_unequal():
    data = ConstantFluidData(0.2, 0.568, 998, 4180, 1e-3)
    data2 = ConstantFluidData(0.2, 0.567, 998, 4180, 1e-3)
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
    data_fluid = ConstantFluidData(0.2, 0.568, 998, 4180, 1e-3)
    data_ground = GroundData(3, 10, 0.2)

    assert data_ground != data_pipe
    assert data_fluid != data_pipe
    assert data_pipe != data_fluid


def test_empty_variable_classes():
    ground_data = GroundData()
    fluid_data = ConstantFluidData()
    pipe_data = PipeData()
    assert not ground_data.check_values()
    assert not pipe_data.check_values()
    assert not fluid_data.check_values()


def test_set_mfr():
    data_fluid = ConstantFluidData(0.2, 0.568, 998, 4180, 1e-3)
    data_fluid.set_mass_flow_rate(10)
    assert data_fluid.mfr == 10
