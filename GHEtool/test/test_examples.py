import matplotlib.pyplot as plt
import pygfunction as gt
import pytest

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

def test_short_term_effects():
    from GHEtool.Examples.short_term_effects import short_term_effects
    short_term_effects()
