import pytest
from GHEtool import *
import matplotlib.pyplot as plt


def test_main_functionalities(monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda: None)
    import GHEtool.Examples.main_functionalities


def test_custom_borefield_configuration(monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda: None)
    import GHEtool.Examples.custom_borefield_configuration


def test_effect_borehole_configuration(monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda: None)
    import GHEtool.Examples.effect_of_borehole_configuration


def test_size_length_and_width(monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda: None)
    import GHEtool.Examples.size_borefield_by_length_and_width