"""
Test to see if the Rb* is calculated on the go
"""
import sys
from pathlib import Path
from typing import Tuple

import numpy as np
import PySide6.QtWidgets as QtW
import pandas as pd

from GHEtool import Borefield, FOLDER, FluidData, GroundConstantTemperature, GroundFluxTemperature, PipeData, GroundTemperatureGradient
from GHEtool.gui.data_2_borefield_func import data_2_borefield
from GHEtool.gui.gui_classes.gui_combine_window import MainWindow
from GHEtool.gui.gui_classes.translation_class import Translations
from GHEtool.gui.gui_structure import GUI, GuiStructure
from ScenarioGUI import load_config
import pygfunction as gt

load_config(Path(__file__).parent.parent.joinpath("gui_config.ini"))

sys.setrecursionlimit(1500)

def setup(qtbot):
    main_window = MainWindow(QtW.QMainWindow(), qtbot, GUI, Translations, result_creating_class=Borefield,
                             data_2_results_function=data_2_borefield)
    main_window.delete_backup()
    main_window = MainWindow(QtW.QMainWindow(), qtbot, GUI, Translations, result_creating_class=Borefield,
                             data_2_results_function=data_2_borefield)
    main_window.save_scenario()

    gs = main_window.gui_structure
    return main_window, gs


def test_visibility_hourly_profile(qtbot):

    main_window, gs = setup(qtbot)
    assert not gs.option_temperature_profile_hourly.is_hidden()
    assert gs.option_method_size_depth.is_hidden()
    main_window.save_scenario()

    main_window.add_scenario()
    assert not gs.option_temperature_profile_hourly.is_hidden()
    assert gs.option_method_size_depth.is_hidden()
    gs.aim_req_depth.widget.click()

    assert gs.option_temperature_profile_hourly.is_hidden()
    assert not gs.option_method_size_depth.is_hidden()
    main_window.save_scenario()
    main_window.change_scenario(0)
    assert not gs.option_temperature_profile_hourly.is_hidden()
    assert gs.option_method_size_depth.is_hidden()


def test_visibility_non_constant_temperature(qtbot):

    main_window, gs = setup(qtbot)
    assert not gs.option_ground_temp.is_hidden()
    assert gs.option_ground_temp_gradient.is_hidden()
    assert gs.option_ground_heat_flux.is_hidden()
    assert gs.option_temp_gradient.is_hidden()
    main_window.save_scenario()

    main_window.add_scenario()
    gs.option_method_temp_gradient.set_value(1)
    assert gs.option_ground_temp.is_hidden()
    assert not gs.option_ground_temp_gradient.is_hidden()
    assert not gs.option_ground_heat_flux.is_hidden()
    assert gs.option_temp_gradient.is_hidden()
    main_window.save_scenario()

    main_window.add_scenario()
    gs.option_method_temp_gradient.set_value(2)
    assert gs.option_ground_temp.is_hidden()
    assert not gs.option_ground_temp_gradient.is_hidden()
    assert gs.option_ground_heat_flux.is_hidden()
    assert not gs.option_temp_gradient.is_hidden()
    main_window.save_scenario()

    main_window.change_scenario(0)
    assert not gs.option_ground_temp.is_hidden()
    assert gs.option_ground_temp_gradient.is_hidden()
    assert gs.option_ground_heat_flux.is_hidden()
    assert gs.option_temp_gradient.is_hidden()


def test_visibility_peak_length(qtbot):

    main_window, gs = setup(qtbot)

    def visible():
        assert not gs.option_len_peak_heating.is_hidden()
        assert not gs.option_len_peak_cooling.is_hidden()

    def invisible():
        assert gs.option_len_peak_heating.is_hidden()
        assert gs.option_len_peak_cooling.is_hidden()

    visible()
    main_window.gui_structure.option_filename.set_value(f'{FOLDER}/Examples/hourly_profile.csv')

    gs.option_temperature_profile_hourly.set_value(1)
    invisible()
    gs.aim_req_depth.widget.click()
    visible()
    gs.option_method_size_depth.set_value(2)
    invisible()
    gs.aim_optimize.widget.click()
    visible()

    main_window.save_scenario()
    main_window.add_scenario()
    visible()
    gs.aim_temp_profile.widget.click()
    invisible()
    main_window.save_scenario()

    main_window.change_scenario(0)
    visible()
    main_window.change_scenario(1)
    invisible()
