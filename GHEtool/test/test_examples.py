import pytest
from GHEtool import *
import matplotlib.pyplot as plt
import pygfunction as gt


def test_main_functionalities(monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda: None)
    import GHEtool.Examples.main_functionalities


def test_custom_borefield_configuration(monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda: None)
    import GHEtool.Examples.custom_borefield_configuration


def test_effect_borehole_configuration(monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda: None)
    import GHEtool.Examples.effect_of_borehole_configuration


@pytest.mark.slow
def test_sizing_with_Rb(monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda: None)
    import GHEtool.Examples.sizing_with_Rb_calculation


def test_optimise_load_profile(monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda: None)

    # initiate ground data
    data = GroundData(3, 10, 0.2)

    # initiate pygfunction borefield model
    borefield_gt = gt.boreholes.rectangle_field(10, 10, 6, 6, 110, 1, 0.075)

    # initiate borefield
    borefield = Borefield()

    # set ground data in borefield
    borefield.set_ground_parameters(data)

    # set pygfunction borefield
    borefield.set_borefield(borefield_gt)

    # load the hourly profile
    borefield.load_hourly_profile("GHEtool/Examples/hourly_profile.csv", header=True, separator=";", first_column_heating=True)

    # optimise the load for a 10x10 field (see data above) and a fixed depth of 150m.
    borefield.optimise_load_profile(depth=150, print_results=True)

    # print resulting external peak cooling profile
    print(borefield.peak_cooling_external)

    # print resulting monthly load for an external heating source
    print(borefield.monthly_load_heating_external)
