"""
Test to see if the advanced options work as expected
"""
import sys
from pathlib import Path

import PySide6.QtWidgets as QtW

from GHEtool import Borefield
from GHEtool.gui.data_2_borefield_func import data_2_borefield
from GHEtool.gui.gui_classes.gui_combine_window import MainWindow
from GHEtool.gui.gui_classes.translation_class import Translations
from GHEtool.gui.gui_structure import GUI
from ScenarioGUI import load_config

load_config(Path(__file__).parent.joinpath("gui_config.ini"))

sys.setrecursionlimit(1500)


def test_advanced_options(qtbot):
    main_window = MainWindow(QtW.QMainWindow(), qtbot, GUI, Translations, result_creating_class=Borefield,
                             data_2_results_function=data_2_borefield)
    main_window.delete_backup()
    main_window = MainWindow(QtW.QMainWindow(), qtbot, GUI, Translations, result_creating_class=Borefield,
                             data_2_results_function=data_2_borefield)
    main_window.save_scenario()

    gs = main_window.gui_structure
    gs.option_method_rb_calc.set_value(0)

    assert gs.category_advanced_options.is_hidden()
    gs.option_advanced_options.set_value(1)
    assert not gs.category_advanced_options.is_hidden()
    gs.aim_req_depth.widget.click()

    main_window.start_current_scenario_calculation()
    thread = main_window.threads[-1]
    thread.run()
    assert thread.calculated

    main_window.display_results()
    assert gs.result_text_depth.label.text() == 'Depth: 115.13 m'

    gs.option_atol.set_value(25)
    gs.option_rtol.set_value(20)
    main_window.start_current_scenario_calculation()
    thread = main_window.threads[-1]
    thread.run()
    assert thread.calculated

    main_window.display_results()
    assert gs.result_text_depth.label.text() == 'Depth: 115.15 m'
