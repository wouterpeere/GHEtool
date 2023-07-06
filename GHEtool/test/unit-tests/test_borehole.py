import copy

import pygfunction as gt
import numpy as np
import pytest

from GHEtool import FluidData, PipeData
from GHEtool.VariableClasses import Borehole

import matplotlib.pyplot as plt

fluid_data = FluidData(0.2, 0.568, 998, 4180, 1e-3)
pipe_data = PipeData(1, 0.015, 0.02, 0.4, 0.05, 2)


def test_fluid_data_without_pipe():
    borehole = Borehole()
    assert borehole.fluid_data == FluidData()
    borehole.fluid_data = fluid_data
    assert borehole.fluid_data == fluid_data
    del borehole.fluid_data
    assert borehole.fluid_data == FluidData()


def test_fluid_data_with_pipe_later_added():
    borehole = Borehole()
    borehole.fluid_data = fluid_data
    assert borehole.fluid_data.R_f == 0
    assert borehole.fluid_data.h_f == 0
    borehole.pipe_data = pipe_data
    assert np.isclose(0.01663038005086118, borehole.fluid_data.R_f)
    assert np.isclose(638.0088432741649, borehole.fluid_data.h_f)


def test_fluid_data_with_pipe_first():
    borehole = Borehole()
    borehole.pipe_data = pipe_data
    borehole.fluid_data = fluid_data
    assert np.isclose(0.01663038005086118, borehole.fluid_data.R_f)
    assert np.isclose(638.0088432741649, borehole.fluid_data.h_f)


def test_pipe_data():
    borehole = Borehole()
    assert borehole.pipe_data == PipeData()
    assert borehole.pipe_data.R_p == 0
    borehole.pipe_data = pipe_data
    assert borehole.pipe_data == pipe_data
    assert np.isclose(0.11446505967405429, borehole.pipe_data.R_p)
    del borehole.pipe_data
    assert borehole.pipe_data == PipeData()


def test_equivalent_loading():
    borehole1 = Borehole()
    borehole2 = Borehole()

    borehole1.fluid_data = fluid_data
    borehole1.pipe_data = pipe_data

    borehole2.pipe_data = copy.copy(pipe_data)
    borehole2.fluid_data = fluid_data

    assert borehole2 == borehole1
    assert not borehole1 == fluid_data
    borehole1._pipe_data.k_g = 3
    assert not borehole1 == borehole2


def test_calculate_Rb():
    borehole = Borehole()
    borehole.pipe_data = pipe_data
    borehole.fluid_data = fluid_data

    assert np.isclose(0.09483159131195469, borehole.calculate_Rb(100, 1, 0.075, 3))


def test_calculate_Rb_no_data():
    borehole = Borehole()

    try:
        borehole.calculate_Rb(100, 1, 0.075, 3)
        assert False  # pragma: no cover
    except ValueError:
        assert True
