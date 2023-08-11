import copy

import pygfunction as gt
import numpy as np
import pytest

from GHEtool import FluidData, DoubleUTube, SingleUTube, MultipleUTube
from GHEtool.VariableClasses import Borehole

fluid_data = FluidData(0.2, 0.568, 998, 4180, 1e-3)
pipe_data = DoubleUTube(1, 0.015, 0.02, 0.4, 0.05)


def test_fluid_data_without_pipe():
    borehole = Borehole()
    assert borehole.fluid_data == FluidData()
    borehole.fluid_data = fluid_data
    assert borehole.fluid_data == fluid_data
    del borehole.fluid_data
    assert borehole.fluid_data == FluidData()


def test_fluid_data_with_pipe_first_added():
    borehole = Borehole()
    borehole.pipe_data = pipe_data
    assert borehole.pipe_data.R_f == 0
    borehole.fluid_data = fluid_data
    assert np.isclose(0.01663038005086118, borehole.pipe_data.R_f)


def test_fluid_data_with_pipe_later_added():
    borehole = Borehole()
    borehole.pipe_data = pipe_data
    borehole.fluid_data = fluid_data
    assert np.isclose(0.01663038005086118, borehole.pipe_data.R_f)


def test_pipe_data():
    borehole = Borehole()
    assert borehole.pipe_data == MultipleUTube()
    assert borehole.pipe_data.R_p == 0
    borehole.pipe_data = pipe_data
    assert borehole.pipe_data == pipe_data
    assert np.isclose(0.11446505967405429, borehole.pipe_data.R_p)
    del borehole.pipe_data
    assert borehole.pipe_data == MultipleUTube()


def test_equivalent_loading():
    borehole1 = Borehole()
    borehole2 = Borehole()

    borehole1.fluid_data = fluid_data
    borehole1.pipe_data = copy.copy(pipe_data)

    borehole2.pipe_data = copy.copy(pipe_data)
    borehole2.fluid_data = fluid_data

    assert borehole2 == borehole1
    assert not borehole1 == fluid_data
    borehole1._pipe_data.k_g = 3
    assert not borehole1 == borehole2


def test_calculate_Rb():
    borehole = Borehole()
    borehole.pipe_data = MultipleUTube(1, 0.015, 0.02, 0.4, 0.05, 2)
    borehole.fluid_data = FluidData(0.2, 0.568, 998, 4180, 1e-3)

    assert np.isclose(borehole.calculate_Rb(100, 1, 0.075, 3), 0.09483159131195469)


def test_Rb():
    borehole = Borehole()
    assert borehole.get_Rb(100, 1, 0.07, 2) == 0.12

    # set pipe and fluid data
    borehole.fluid_data = fluid_data
    borehole.pipe_data = pipe_data

    assert np.isclose(borehole.calculate_Rb(100, 1, 0.075, 3), 0.09483159131195469)

    # set Rb
    borehole.Rb = 0.12
    assert borehole.get_Rb(100, 1, 0.07, 2) == 0.12

    # set pipe and fluid data
    borehole.fluid_data = fluid_data
    borehole.pipe_data = pipe_data

    assert np.isclose(borehole.calculate_Rb(100, 1, 0.075, 3), 0.09483159131195469)
    del borehole.pipe_data
    assert borehole.get_Rb(100, 1, 0.07, 2) == 0.12
    borehole.pipe_data = pipe_data
    assert np.isclose(borehole.calculate_Rb(100, 1, 0.075, 3), 0.09483159131195469)
    del borehole.fluid_data
    assert borehole.get_Rb(100, 1, 0.07, 2) == 0.12
    borehole.fluid_data = fluid_data
    assert np.isclose(borehole.calculate_Rb(100, 1, 0.075, 3), 0.09483159131195469)


def test_calculate_Rb_no_data():
    borehole = Borehole()

    try:
        borehole.calculate_Rb(100, 1, 0.075, 3)
        assert False  # pragma: no cover
    except ValueError:
        assert True

def test_Rb_values():
    borehole = Borehole()
    mfr_range = np.arange(0.05, 0.55, 0.05)
    pipe_data = MultipleUTube(1, 0.015, 0.02, 0.4, 0.05, number_of_pipes=2, epsilon=1e-6)
    borehole.pipe_data = pipe_data
    Rb_list = []
    for mfr in mfr_range:
        fluid_data = FluidData(mfr, 0.568, 998, 4180, 1e-3)
        borehole.fluid_data = fluid_data
        Rb_list.append(borehole.get_Rb(100, 1, 0.075, 3))

    assert np.allclose(Rb_list, [0.2696064888020322, 0.16229265041543758, 0.11073836048982678, 0.09483159131195469, 0.08742765267449451, 0.08315828854931047, 0.08046372254501538, 0.07864703705590415, 0.07735912210040842, 0.07640933344353783])


def test_assign_by_initiation():
    borehole = Borehole(fluid_data, pipe_data)
    assert np.isclose(borehole.calculate_Rb(100, 1, 0.075, 3), 0.09483159131195469)
    assert not borehole.use_constant_Rb