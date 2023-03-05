import copy

import pygfunction as gt
import pytest

from GHEtool import GroundData, FluidData, PipeData
from GHEtool.VariableClasses import Borehole

import matplotlib.pyplot as plt

fluid_data = FluidData(0.2, 0.568, 998, 4180, 1e-3)
pipe_data = PipeData(1, 0.015, 0.02, 0.4, 0.05, 2)


def test_fluid_data():
    borehole = Borehole()
    assert borehole.fluid_data == FluidData()
    borehole.fluid_data = fluid_data
    assert borehole.fluid_data == fluid_data
    del borehole.fluid_data
    assert borehole.fluid_data == FluidData()


def test_pipe_data():
    borehole = Borehole()
    assert borehole.pipe_data == PipeData()
    borehole.pipe_data = pipe_data
    assert borehole.pipe_data == pipe_data
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
    borehole.fluid_data = fluid_data
    borehole.pipe_data = pipe_data

    borehole.calculate_Rb(100, 1, 0.075, 3)


def test_calculate_Rb_no_data():
    borehole = Borehole()

    try:
        borehole.calculate_Rb(100, 1, 0.075, 3)
    except ValueError:
        assert True
