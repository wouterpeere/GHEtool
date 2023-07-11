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


# @pytest.mark.slow
# def test_active_passive(monkeypatch):
#     monkeypatch.setattr(plt, 'show', lambda: None)
#     from GHEtool.Examples.active_passive_cooling import active_passive_cooling
#     active_passive_cooling(FOLDER.joinpath('Examples/active_passive_example.csv'))

def test_optimise_load_profile(monkeypatch):
    from GHEtool import FOLDER
    monkeypatch.setattr(plt, 'show', lambda: None)

    # initiate ground data
    data = GroundConstantTemperature(3, 10)

    # initiate pygfunction borefield model
    borefield_gt = gt.boreholes.rectangle_field(10, 10, 6, 6, 110, 1, 0.075)

    # initiate borefield
    borefield = Borefield()

    # set ground data in borefield
    borefield.set_ground_parameters(data)

    # set Rb
    borefield.set_Rb(0.2)

    # set pygfunction borefield
    borefield.set_borefield(borefield_gt)

    # load the hourly profile
    load = HourlyGeothermalLoad()
    load.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"), header=True, separator=";")

    # optimise the load for a 10x10 field (see data above) and a fixed depth of 150m.
    borefield.optimise_load_profile(load, depth=150, print_results=True)
