import pytest

import matplotlib.pyplot as plt
import numpy as np

from GHEtool import *


def test_main_functionalities(monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda: None)
    from GHEtool.Examples.main_functionalities import main_functionalities
    main_functionalities()


def test_custom_borefield_configuration(monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda: None)
    from GHEtool.Examples.custom_borefield_configuration import custom_borefield_configuration
    custom_borefield_configuration()


def test_effect_borehole_configuration(monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda: None)
    from GHEtool.Examples.effect_of_borehole_configuration import effect_borefield_configuration
    effect_borefield_configuration()


@pytest.mark.slow
def test_sizing_with_Rb(monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda: None)
    from GHEtool.Examples.sizing_with_Rb_calculation import sizing_with_Rb
    sizing_with_Rb()


@pytest.mark.slow
def test_active_passive(monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda: None)
    from GHEtool.Examples.active_passive_cooling import active_passive_cooling
    active_passive_cooling(FOLDER.joinpath('Examples/active_passive_example.csv'))


def test_start_in_different_month(monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda: None)
    from GHEtool.Examples.start_in_different_month import start_in_different_month
    start_in_different_month()


def test_multiple_ground_layers():
    from GHEtool.Examples.multiple_ground_layers import multiple_ground_layers
    multiple_ground_layers()


def test_sizing_with_building_load(monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda: None)
    from GHEtool.Examples.sizing_with_building_load import size_with_scop, \
        size_with_variable_ground_temperature, \
        size_with_part_load_data
    assert np.allclose(size_with_scop(), (96.5589765783911, 4.072466974615784))
    assert np.allclose(size_with_variable_ground_temperature(), (95.64066844079264, 4.17665670561309))
    assert np.allclose(size_with_part_load_data(), (98.1273127062551, 4.685121612513776))


def test_sizing_with_building_load_hourly(monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda: None)
    from GHEtool.Examples.sizing_with_building_load_hourly import L3_sizing, L4_sizing
    assert np.allclose(L3_sizing(), (127.05154931011464, 6.131588043404349))
    assert np.allclose(L4_sizing(), (153.26361812264668, 6.237959315069309))


def test_separatus(monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda: None)
    from GHEtool.Examples.separatus import design_with_single_U, design_with_double_U, design_with_separatus
    design_with_single_U()
    design_with_double_U()
    design_with_separatus()
