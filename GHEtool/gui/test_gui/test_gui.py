import os
import pathlib
from math import isclose
from sys import setrecursionlimit
from typing import List

import keyboard
import PySide6.QtCore as QtC
import PySide6.QtWidgets as QtW
import numpy as np
from PySide6.QtWidgets import QMainWindow as QtWidgets_QMainWindow
from pytest import raises

from GHEtool import FOLDER
from GHEtool.gui.data_2_borefield_func import data_2_borefield
from GHEtool.gui.gui_classes.gui_combine_window import MainWindow
from GHEtool.gui.gui_classes.gui_structure_classes import ButtonBox, FigureOption, FloatBox, IntBox, ListBox
from GHEtool.gui.test_gui.test_results import create_borefield

setrecursionlimit(1500)


def test_language(qtbot):
    """
    test if the language is changed correctly

    Parameters
    ----------
    qtbot: qtbot
        bot for the GUI
    """
    from GHEtool.gui.translation_csv_to_py import main

    main()

    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.delete_backup()

    for idx, action in enumerate(main_window.menuLanguage.actions()):
        action.trigger()
        assert main_window.gui_structure.option_language.get_value() == idx

    main_window.menuLanguage.actions()[0].trigger()


def test_gui_values(qtbot):
    """
    test if all gui values are set and get correctly.

    Parameters
    ----------
    qtbot: qtbot
        bot for the GUI
    """
    # init gui window
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.remove_previous_calculated_results()
    main_window.delete_backup()
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.remove_previous_calculated_results()

    main_window.gui_structure.option_filename.set_value(f'{FOLDER}/Examples/hourly_profile.csv')

    for option, _ in main_window.gui_structure.list_of_options:
        # check if option is hidden and disabled
        option.hide()
        assert option.is_hidden()
        if isinstance(option.widget, list):
            for widget in option.widget:
                assert not widget.isEnabled()
        else:
            assert not option.widget.isEnabled()
        # show option and check values
        option.show()
        if isinstance(option, FloatBox) or isinstance(option, IntBox):
            if option.linked_options:  # pragma: no cover
                option.set_value(option.maximal_value)
                assert isclose(option.get_value(), option.maximal_value)

                option.set_value(option.minimal_value)
                assert isclose(option.get_value(), option.minimal_value)
                continue
            val = option.get_value() + option.step
            val = val - 2 * option.step if option.widget.maximum() > val else val
            if val < option.widget.minimum():
                continue
            option.set_value(val)
            assert isclose(option.get_value(), val)
            option.set_value(option.default_value)
            continue
        if (isinstance(option, ButtonBox) or isinstance(option, ListBox)) and not isinstance(option, FigureOption):
            option.set_value(0)
            assert option.get_value() == 0
            option.set_value(1)
            assert option.get_value() == 1

    for idx, action in enumerate(main_window.menuLanguage.actions()):
        action.trigger()
        assert main_window.gui_structure.option_language.get_value() == idx

    list_columns: List[str] = ['Heating', 'Cooling']

    main_window.gui_structure.option_decimal_csv.set_value(0)
    main_window.gui_structure.option_seperator_csv.set_value(0)
    main_window.gui_structure.option_filename.set_value(f'{FOLDER}/Examples/hourly_profile.csv')
    for idx, column in enumerate(list_columns):
        assert main_window.gui_structure.option_heating_column.widget.itemText(idx) == column
        assert main_window.gui_structure.option_cooling_column.widget.itemText(idx) == column
        assert main_window.gui_structure.option_single_column.widget.itemText(idx) == column

    main_window.gui_structure.option_decimal_csv.set_value(0)
    main_window.gui_structure.option_seperator_csv.set_value(1)
    main_window.gui_structure.option_filename.set_value(f'{FOLDER}/Examples/hourly_profile_comma_as_sep.csv')

    for idx, column in enumerate(list_columns):
        assert main_window.gui_structure.option_heating_column.widget.itemText(idx) == column
        assert main_window.gui_structure.option_cooling_column.widget.itemText(idx) == column
        assert main_window.gui_structure.option_single_column.widget.itemText(idx) == column

    main_window.gui_structure.aim_temp_profile.widget.click() if not main_window.gui_structure.aim_temp_profile.widget.isChecked() else None
    main_window.save_scenario()
    main_window.start_current_scenario_calculation(False)
    with qtbot.waitSignal(main_window.threads[0].any_signal, raising=False) as blocker:
        main_window.threads[0].run()
        main_window.threads[0].any_signal.connect(main_window.thread_function)

    main_window.gui_structure.aim_req_depth.widget.click()
    main_window.save_scenario()
    main_window.start_current_scenario_calculation(True)
    with qtbot.waitSignal(main_window.threads[0].any_signal, raising=False) as blocker:
        main_window.threads[0].run()
        main_window.threads[0].any_signal.connect(main_window.thread_function)

    main_window.remove_previous_calculated_results()
    main_window.gui_structure.aim_optimize.widget.click()
    main_window.save_scenario()
    main_window.start_current_scenario_calculation(True)
    with qtbot.waitSignal(main_window.threads[0].any_signal, raising=False) as blocker:
        main_window.threads[0].run()
        main_window.threads[0].any_signal.connect(main_window.thread_function)
    # check if no calculation runs
    assert main_window.list_ds[0].borefield is not None
    main_window.start_current_scenario_calculation()
    assert len(main_window.threads) == 0
    assert all([ds.borefield is not None for ds in main_window.list_ds])
    main_window.start_multiple_scenarios_calculation()
    assert len(main_window.threads) == 0

    main_window.gui_structure.option_column.set_value(0)
    main_window.gui_structure.option_single_column.set_value(0)
    main_window.gui_structure.button_load_csv.button.click()

    main_window.gui_structure.option_column.set_value(1)
    main_window.gui_structure.option_heating_column.set_value(0)
    main_window.gui_structure.option_cooling_column.set_value(1)
    main_window.gui_structure.button_load_csv.button.click()

    print('end')


def test_gui_scenario_properties(qtbot):
    """
    test if gui scenario properties like adding and deleting are working correctly.

    Parameters
    ----------
    qtbot: qtbot
        bot for the GUI
    """
    # init gui window
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.delete_backup()
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    # check if at start no scenario exists
    assert len(main_window.list_ds) == 0
    assert main_window.list_widget_scenario.count() == 0
    # check if saving of a scenario if an empty list create one
    main_window.save_scenario()
    assert len(main_window.list_ds) == 1
    assert main_window.list_widget_scenario.count() == 1
    # check if adding a scenario is adding one
    for i in range(10):
        main_window.add_scenario()
        assert len(main_window.list_ds) == 2 + i
        assert main_window.list_widget_scenario.count() == 2 + i
    # check if deleting a scenario is removing a scenario
    for i in range(10):
        main_window.delete_scenario()
        assert len(main_window.list_ds) == 10 - i
        assert main_window.list_widget_scenario.count() == 10 - i
    # check if deleting the last scenario is ignored so at least one exists
    main_window.delete_scenario()
    assert len(main_window.list_ds) == 1
    assert main_window.list_widget_scenario.count() == 1


def test_gui_scenario_double_naming(qtbot):
    """
    test if two scenarios can have the same name.

    Parameters
    ----------
    qtbot: qtbot
        bot for the GUI
    """
    # init gui window
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.delete_backup()
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    # create two scenarios
    main_window.add_scenario()
    main_window.add_scenario()
    assert ["Scenario: 1", "Scenario: 2"] == [main_window.list_widget_scenario.item(x).text().split("*")[0]
                                                 for x in range(main_window.list_widget_scenario.count())]
    main_window.list_widget_scenario.setCurrentRow(0)
    main_window.delete_scenario()
    # scenarios are renamed
    assert ["Scenario: 2"] == [main_window.list_widget_scenario.item(x).text().split("*")[0]
                              for x in range(main_window.list_widget_scenario.count())]
    # add two scenarios and check if the second one is named correctly
    main_window.add_scenario()
    main_window.add_scenario()
    assert ["Scenario: 2", "Scenario: 2(2)", "Scenario: 3"] == [main_window.list_widget_scenario.item(x).text().split("*")[0]
                                              for x in range(main_window.list_widget_scenario.count())]
    # check if this also works with renaming a scenario
    main_window.list_widget_scenario.setCurrentRow(1)
    main_window.fun_rename_scenario("Scenario: 3")
    assert ["Scenario: 2", "Scenario: 3(2)", "Scenario: 3"] == [main_window.list_widget_scenario.item(x).text().split("*")[0]
                                              for x in range(main_window.list_widget_scenario.count())]


def test_wrong_results_shown(qtbot):
    """
    test if results are shown correctly.

    Parameters
    ----------
    qtbot: qtbot
        bot for the GUI
    """
    # init gui window
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.delete_backup()
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.gui_structure.option_decimal_csv.set_value(0)
    main_window.gui_structure.option_seperator_csv.set_value(0)

    main_window.gui_structure.option_filename.set_value(f'{FOLDER}/Examples/hourly_profile.csv')
    main_window.gui_structure.fun_update_combo_box_data_file(f'{FOLDER}/Examples/hourly_profile.csv')
    main_window.gui_structure.option_column.set_value(1)
    main_window.gui_structure.option_cooling_column.set_value(1)

    main_window.gui_structure.aim_optimize.widget.click()
    main_window.save_scenario()
    main_window.start_current_scenario_calculation(True)
    with qtbot.waitSignal(main_window.threads[0].any_signal, raising=False) as blocker:
        main_window.threads[0].run()
        main_window.threads[0].any_signal.connect(main_window.thread_function)

    main_window.display_results()
    assert not main_window.gui_structure.hourly_figure_temperature_profile.is_hidden()
    assert main_window.gui_structure.result_Rb_calculated.is_hidden()
    assert not main_window.gui_structure.figure_load_duration.is_hidden()

    main_window.gui_structure.option_method_rb_calc.set_value(1)
    main_window.save_scenario()
    main_window.start_current_scenario_calculation(True)
    with qtbot.waitSignal(main_window.threads[0].any_signal, raising=False) as blocker:
        main_window.threads[0].run()
        main_window.threads[0].any_signal.connect(main_window.thread_function)

    main_window.display_results()
    assert not main_window.gui_structure.hourly_figure_temperature_profile.is_hidden()
    assert not main_window.gui_structure.result_Rb_calculated.is_hidden()

    main_window.add_scenario()
    main_window.save_scenario()
    main_window.start_current_scenario_calculation(True)
    with qtbot.waitSignal(main_window.threads[0].any_signal, raising=False) as blocker:
        main_window.threads[0].run()
        main_window.threads[0].any_signal.connect(main_window.thread_function)

    main_window.display_results()
    assert not main_window.gui_structure.hourly_figure_temperature_profile.is_hidden()
    assert not main_window.gui_structure.result_Rb_calculated.is_hidden()
    main_window.list_widget_scenario.setCurrentRow(0)
    assert not main_window.gui_structure.hourly_figure_temperature_profile.is_hidden()
    assert not main_window.gui_structure.result_Rb_calculated.is_hidden()
    main_window.list_widget_scenario.setCurrentRow(1)
    assert not main_window.gui_structure.hourly_figure_temperature_profile.is_hidden()
    assert not main_window.gui_structure.result_Rb_calculated.is_hidden()
    main_window.add_scenario()
    main_window.gui_structure.aim_temp_profile.widget.click()
    main_window.save_scenario()
    main_window.start_current_scenario_calculation(True)
    with qtbot.waitSignal(main_window.threads[0].any_signal, raising=False) as blocker:
        main_window.threads[0].run()
        main_window.threads[0].any_signal.connect(main_window.thread_function)
    assert main_window.gui_structure.hourly_figure_temperature_profile.is_hidden()


def test_move_scenario(qtbot):
    """
    test if the change of a scenario works correctly.\n

    Parameters
    ----------
    qtbot: qtbot
        bot for the GUI
    """
    # init gui window
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.delete_backup()
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    # add three scenarios
    main_window.add_scenario()
    main_window.add_scenario()
    main_window.gui_structure.aim_req_depth.widget.click()
    main_window.save_scenario()
    main_window.add_scenario()
    main_window.gui_structure.option_method_size_depth.set_value(1)
    main_window.save_scenario()
    # save old lists of data storages and names
    li_before = main_window.list_ds.copy()
    li_names_before = [main_window.list_widget_scenario.item(idx).text() for idx in range(main_window.list_widget_scenario.count())]
    # change the items
    main_window.list_widget_scenario.model().moveRow(QtC.QModelIndex(), 2, QtC.QModelIndex(), 0)
    # get new lists of data storages and names
    li_after = main_window.list_ds
    li_names_after = [main_window.list_widget_scenario.item(idx).text() for idx in range(main_window.list_widget_scenario.count())]
    # create check lists by hand from before lists
    li_check = [li_before[2], li_before[0], li_before[1]]
    li_names_check = [li_names_before[2], li_names_before[0], li_names_before[1]]
    # check if names and data storages have been changed correctly
    assert li_after == li_check
    assert li_names_after == li_names_check


def test_wrong_options_are_shown(qtbot):
    """
    test if the options are shown correctly.

    Parameters
    ----------
    qtbot: qtbot
        bot for the GUI
    """
    # first case
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.delete_backup()
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.gui_structure.aim_req_depth.widget.click()
    main_window.gui_structure.option_method_size_depth.set_value(2)
    main_window.gui_structure.aim_temp_profile.widget.click()
    assert not main_window.gui_structure.option_len_peak_heating.is_hidden()
    # second case
    main_window.delete_backup()
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.pushButton_start_single.click()
    main_window.add_scenario()
    main_window.pushButton_start_single.click()
    assert not main_window.gui_structure.max_temp.is_hidden()


def test_rename_scenario(qtbot):
    """
    test renaming of scenario by button and double click.

    Parameters
    ----------
    qtbot: qtbot
        bot for the GUI
    """
    # init gui window
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.delete_backup()
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.add_scenario()
    # set scenario names
    scenario_name = 'test_name'
    scenario_name_2 = 'test_name_2'
    # create functions to handle pop up dialog windows to change names, close and reject the dialog
    def change_name():
        while main_window.dialog is None:  # pragma: no cover
            QtW.QApplication.processEvents()
        # handle dialog now
        if isinstance(main_window.dialog, QtW.QInputDialog):
            main_window.dialog.setTextValue(scenario_name)
            main_window.dialog.accept()

    def change_name_2():
        while main_window.dialog is None:  # pragma: no cover
            QtW.QApplication.processEvents()
        # handle dialog now
        if isinstance(main_window.dialog, QtW.QInputDialog):
            main_window.dialog.setTextValue(scenario_name_2)
            main_window.dialog.accept()

    def not_change_name():
        while main_window.dialog is None:  # pragma: no cover
            QtW.QApplication.processEvents()
        # handle dialog now
        if isinstance(main_window.dialog, QtW.QInputDialog):
            main_window.dialog.setTextValue('')
            main_window.dialog.accept()

    def close_dialog():
        while main_window.dialog is None:  # pragma: no cover
            QtW.QApplication.processEvents()
        # handle dialog now
        if isinstance(main_window.dialog, QtW.QInputDialog):
            main_window.dialog.close()

    def reject_dialog():
        while main_window.dialog is None:  # pragma: no cover
            QtW.QApplication.processEvents()
        # handle dialog now
        if isinstance(main_window.dialog, QtW.QInputDialog):
            main_window.dialog.reject()
    # get old item name
    old_name = main_window.list_widget_scenario.item(0).text()
    # enter nothing in the text box and not change the name
    QtC.QTimer.singleShot(100, not_change_name)
    qtbot.mouseClick(main_window.button_rename_scenario, QtC.Qt.MouseButton.LeftButton, delay=1)
    # check if the name stays the old one
    assert main_window.list_widget_scenario.item(0).text() == old_name
    # just close the dialog window
    QtC.QTimer.singleShot(100, close_dialog)
    qtbot.mouseClick(main_window.button_rename_scenario, QtC.Qt.MouseButton.LeftButton, delay=1)
    # check if the name stays the old one
    assert main_window.list_widget_scenario.item(0).text() == old_name
    # abort the dialog window by button
    QtC.QTimer.singleShot(100, reject_dialog)
    qtbot.mouseClick(main_window.button_rename_scenario, QtC.Qt.MouseButton.LeftButton, delay=1)
    # check if the name stays the old one
    assert main_window.list_widget_scenario.item(0).text() == old_name
    # change the name
    QtC.QTimer.singleShot(100, change_name)
    qtbot.mouseClick(main_window.button_rename_scenario, QtC.Qt.MouseButton.LeftButton, delay=1)
    # check the name has been changed correctly
    assert main_window.list_widget_scenario.item(0).text() == scenario_name
    # check if the name can be changed by double click
    QtC.QTimer.singleShot(100, change_name_2)
    main_window.list_widget_scenario.doubleClicked.emit(main_window.list_widget_scenario.model().index(0, 0))
    # check the name has been changed correctly
    assert main_window.list_widget_scenario.item(0).text() == scenario_name_2


def test_push_button_layout_change(qtbot):
    """
    test if the button layout is changed while overing over it

    Parameters
    ----------
    qtbot: qtbot
        bot for the GUI
    """
    # init gui window
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.delete_backup()
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.add_scenario()
    # check if the layout is the small one at the beginning
    for page_i in main_window.gui_structure.list_of_pages:
        assert page_i.button.iconSize() == main_window.sizeB
        assert page_i.button.size() == main_window.sizePushS
    # enter and leave all buttons and check if they all have the correct size
    for page in main_window.gui_structure.list_of_pages:
        main_window.eventFilter(page.button, QtC.QEvent(QtC.QEvent.Enter))
        for page_i in main_window.gui_structure.list_of_pages:
            assert page_i.button.size() == main_window.sizePushB
            assert page_i.button.iconSize() == main_window.sizeS
        qtbot.wait(50)
        main_window.eventFilter(page.button, QtC.QEvent(QtC.QEvent.Leave))
        for page_i in main_window.gui_structure.list_of_pages:
            assert page_i.button.iconSize() == main_window.sizeB
            assert page_i.button.size() == main_window.sizePushS


def test_save_load_new(qtbot):
    """
    test if load, save and create a new scenario works

    Parameters
    ----------
    qtbot: qtbot
        bot for the GUI
    """
    # init gui window
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.delete_backup()
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.add_scenario()
    # set filenames
    filename_1 = 'test_1.GHEtool'
    filename_2 = 'test_2.GHEtool'
    filename_3 = 'test_3.GHEtool'
    # delete files if they already exists
    if os.path.exists(main_window.default_path.joinpath(filename_1)):  # pragma: no cover
        os.remove(main_window.default_path.joinpath(filename_1))
    if os.path.exists(main_window.default_path.joinpath(filename_2)):  # pragma: no cover
        os.remove(main_window.default_path.joinpath(filename_2))
    if os.path.exists(main_window.default_path.joinpath(filename_3)):  # pragma: no cover
        os.remove(main_window.default_path.joinpath(filename_3))
    # trigger save action and add filename
    QtC.QTimer.singleShot(100, lambda: keyboard.press('Esc'))
    main_window.actionSave.trigger()
    assert (pathlib.Path(main_window.filename[0]), main_window.filename[1]) == (pathlib.Path(main_window.filenameDefault[0]), main_window.filenameDefault[1])
    # trigger save action and add filename
    QtC.QTimer.singleShot(1000, lambda: keyboard.write(filename_1))
    QtC.QTimer.singleShot(1200, lambda: keyboard.press('enter'))
    main_window.actionSave.trigger()
    # check if filename is set correctly
    assert (pathlib.Path(main_window.filename[0]), main_window.filename[1]) == (main_window.default_path.joinpath(filename_1), 'GHEtool (*.GHEtool)')
    # check if filename is set correctly
    assert (pathlib.Path(main_window.filename[0]), main_window.filename[1]) == (main_window.default_path.joinpath(filename_1), 'GHEtool (*.GHEtool)')
    # get old list and add a new scenario
    list_old = main_window.list_ds.copy()
    main_window.add_scenario()
    # check that they differ
    assert list_old != main_window.list_ds
    # set a different filename and test save as action
    QtC.QTimer.singleShot(1000, lambda: keyboard.write(filename_2))
    QtC.QTimer.singleShot(1200, lambda: keyboard.press('enter'))
    main_window.actionSave_As.trigger()
    # check if filename is set correctly
    assert (pathlib.Path(main_window.filename[0]), main_window.filename[1]) == (main_window.default_path.joinpath(filename_2), 'GHEtool (*.GHEtool)')
    # trigger open function and set filename 1
    QtC.QTimer.singleShot(1000, lambda: keyboard.write(filename_1))
    QtC.QTimer.singleShot(1200, lambda: keyboard.press('enter'))
    main_window.actionOpen.trigger()
    # check if filename is imported correctly and the data storages as well
    assert (pathlib.Path(main_window.filename[0]), main_window.filename[1]) == (main_window.default_path.joinpath(filename_1), 'GHEtool (*.GHEtool)')
    assert list_old == main_window.list_ds
    # set a different filename and test new action
    QtC.QTimer.singleShot(1000, lambda: keyboard.write(filename_3))
    QtC.QTimer.singleShot(1200, lambda: keyboard.press('enter'))
    main_window.actionNew.trigger()
    assert (pathlib.Path(main_window.filename[0]), main_window.filename[1]) == (main_window.default_path.joinpath(filename_3), 'GHEtool (*.GHEtool)')
    assert len(main_window.list_ds) < 1


def test_close(qtbot):
    """
    test if the close dialog works correctly

    Parameters
    ----------
    qtbot: qtbot
        bot for the GUI
    """

    # init gui window
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.delete_backup()
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.add_scenario()
    main_window.gui_structure.option_conductivity.set_value(2.1)
    # set filenames
    filename_1 = 'test_1.GHEtool'
    # delete files if they already exists
    if os.path.exists(main_window.default_path.joinpath(filename_1)):
        os.remove(main_window.default_path.joinpath(filename_1))

    def close():
        while main_window.dialog is None:  # pragma: no cover
            QtW.QApplication.processEvents()
        # handle dialog now
        if isinstance(main_window.dialog, QtW.QMessageBox):
            main_window.dialog.close()

    def cancel():
        while main_window.dialog is None:  # pragma: no cover
            QtW.QApplication.processEvents()
        # handle dialog now
        if isinstance(main_window.dialog, QtW.QMessageBox):
            main_window.dialog.buttons()[2].click()

    def exit_window():
        while main_window.dialog is None:  # pragma: no cover
            QtW.QApplication.processEvents()
        # handle dialog now
        if isinstance(main_window.dialog, QtW.QMessageBox):
            main_window.dialog.buttons()[1].click()

    def save():
        while main_window.dialog is None:  # pragma: no cover
            QtW.QApplication.processEvents()
        # handle dialog now
        if isinstance(main_window.dialog, QtW.QMessageBox):
            main_window.dialog.buttons()[0].click()

    QtC.QTimer.singleShot(100, close)
    main_window.close()

    QtC.QTimer.singleShot(100, cancel)
    main_window.close()

    QtC.QTimer.singleShot(100, save)
    QtC.QTimer.singleShot(120, lambda: keyboard.write(filename_1))
    QtC.QTimer.singleShot(150, lambda: keyboard.press('enter'))
    main_window.close()

    QtC.QTimer.singleShot(100, exit_window)
    main_window.close()


def test_auto_save(qtbot):
    """
    test if the auto save function works

    Parameters
    ----------
    qtbot: qtbot
        bot for the GUI
    """
    # init gui window
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.delete_backup()
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    # set auto save function and create new backup file
    main_window.gui_structure.option_auto_saving.set_value(1)
    main_window.fun_save_auto()
    # add a new scenario and change conductivity
    main_window.add_scenario()
    main_window.gui_structure.option_conductivity.set_value(2.1)
    # add a new scenario and change conductivity
    main_window.add_scenario()
    main_window.gui_structure.option_conductivity.set_value(1.1)
    # run calculations
    main_window.action_start_multiple.trigger()
    # check if options has been stored correctly
    assert main_window.list_ds[1].option_conductivity == 2.1
    assert main_window.list_ds[2].option_conductivity == 1.1


def test_no_load_save_file(qtbot):
    """
    test if the GUI handles wrong load and save inputs correctly

    Parameters
    ----------
    qtbot: qtbot
        bot for the GUI
    """
    from pytest import raises

    # init gui window
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.delete_backup()
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    # check if an import error has been raises with a wrong load file
    with raises(ImportError):
        main_window._load_from_data('not_there.GHEtool')
    # check if the current error message is shown with a wrong save file/folder
    main_window._save_to_data('hello/not_there.GHEtool')
    assert main_window.status_bar.currentMessage() == main_window.translations.NoFileSelected[main_window.gui_structure.option_language.get_value()]


def test_change_scenario(qtbot):
    """
    test if the scenario changing is handled correctly

    Parameters
    ----------
    qtbot: qtbot
        bot for the GUI
    """
    # init gui window
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.delete_backup()
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    # add two scenarios and set different conductivity
    main_window.add_scenario()
    main_window.gui_structure.option_conductivity.set_value(2.1)
    main_window.save_scenario()
    main_window.add_scenario()
    main_window.gui_structure.option_conductivity.set_value(1.1)
    main_window.save_scenario()
    # change scenario to first one and check for the correct value
    assert main_window.list_widget_scenario.currentRow() == 1
    main_window.list_widget_scenario.setCurrentItem(main_window.list_widget_scenario.item(0))
    assert 2.1 == main_window.gui_structure.option_conductivity.get_value()
    assert main_window.list_widget_scenario.currentRow() == 0
    # change a value to trigger pop up window
    main_window.gui_structure.option_conductivity.set_value(2.3)
    # create functions to handle pop up window
    def close():
        while main_window.dialog is None:  # pragma: no cover
            QtW.QApplication.processEvents()
        # handle dialog now
        if isinstance(main_window.dialog, QtW.QMessageBox):
            main_window.dialog.close()

    def abort():
        while main_window.dialog is None:  # pragma: no cover
            QtW.QApplication.processEvents()
        # handle dialog now
        if isinstance(main_window.dialog, QtW.QMessageBox):
            main_window.dialog.buttons()[2].click()

    def exit_window():
        while main_window.dialog is None:  # pragma: no cover
            QtW.QApplication.processEvents()
        # handle dialog now
        if isinstance(main_window.dialog, QtW.QMessageBox):
            main_window.dialog.buttons()[1].click()

    def save():
        while main_window.dialog is None:  # pragma: no cover
            QtW.QApplication.processEvents()
        # handle dialog now
        if isinstance(main_window.dialog, QtW.QMessageBox):
            main_window.dialog.buttons()[0].click()
    # test if closing the window is not changing the value and scenario
    QtC.QTimer.singleShot(100, close)
    main_window.list_widget_scenario.setCurrentItem(main_window.list_widget_scenario.item(1))
    assert 2.3 == main_window.gui_structure.option_conductivity.get_value()
    qtbot.wait(100)
    assert main_window.list_widget_scenario.currentRow() == 0
    # test if canceling the window is not changing the value and scenario
    QtC.QTimer.singleShot(100, abort)
    main_window.list_widget_scenario.setCurrentItem(main_window.list_widget_scenario.item(1))
    assert 2.3 == main_window.gui_structure.option_conductivity.get_value()
    qtbot.wait(100)
    assert main_window.list_widget_scenario.currentRow() == 0
    # test if exiting the window is rejecting the changed the value and changing the scenario
    QtC.QTimer.singleShot(100, exit_window)
    main_window.list_widget_scenario.setCurrentItem(main_window.list_widget_scenario.item(1))
    qtbot.wait(100)
    assert main_window.gui_structure.option_conductivity.get_value() == 1.1
    assert main_window.list_ds[0].option_conductivity == 2.1
    assert main_window.list_widget_scenario.currentRow() == 1
    # change a value to trigger pop up window
    main_window.gui_structure.option_conductivity.set_value(3)
    # test if saving is saving the changed the value and changing the scenario
    QtC.QTimer.singleShot(100, save)
    main_window.list_widget_scenario.setCurrentItem(main_window.list_widget_scenario.item(0))
    qtbot.wait(100)
    assert main_window.list_ds[1].option_conductivity == 3
    assert main_window.list_widget_scenario.currentRow() == 0
    # check if the * is removed when it is changed to old values
    old_value = main_window.gui_structure.option_conductivity.get_value()
    main_window.gui_structure.option_conductivity.set_value(4)
    assert main_window.list_widget_scenario.currentItem().text()[-1] == '*'
    main_window.gui_structure.option_conductivity.set_value(old_value)
    assert main_window.list_widget_scenario.currentItem().text()[-1] != '*'
    # check if just one * is added if multiple options are changed
    main_window.gui_structure.option_conductivity.set_value(4)
    main_window.gui_structure.option_spacing.set_value(4)
    assert main_window.list_widget_scenario.currentItem().text()[-1] == '*'
    assert main_window.list_widget_scenario.currentItem().text()[-2] != '**'
    # activate auto saving option
    main_window.gui_structure.option_auto_saving.set_value(1)
    # check if the value is stored and the scenario is changed
    main_window.gui_structure.option_conductivity.set_value(4)
    main_window.list_widget_scenario.setCurrentItem(main_window.list_widget_scenario.item(1))
    qtbot.wait(100)
    assert main_window.list_ds[0].option_conductivity == 4
    assert main_window.list_widget_scenario.currentRow() == 1
    # check if nothing is changed when scenarios are switched
    main_window.list_widget_scenario.setCurrentItem(main_window.list_widget_scenario.item(0))
    main_window.list_widget_scenario.setCurrentItem(main_window.list_widget_scenario.item(1))
    assert main_window.list_ds[0].option_conductivity == 4
    assert main_window.list_ds[1].option_conductivity == 3


def test_repr(qtbot):
    # init gui window
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    assert main_window.gui_structure.figure_temperature_profile.__repr__() == "ResultFigure; Label: Temperature evolution"
    assert main_window.gui_structure.category_language.__repr__() == "Category; Label: Language: "
    assert main_window.gui_structure.option_toggle_buttons.__repr__() == "ButtonBox; Label: Use toggle buttons?:; Value: 1"
    assert main_window.gui_structure.hint_peak_heating.__repr__() == "Hint; Hint: Heating peak; Warning: False"
    assert main_window.gui_structure.option_conductivity.__repr__() == "FloatBox; Label: Conductivity of the soil [W/mK]: ; Value: 4.0"
    assert main_window.gui_structure.option_width.__repr__() == "IntBox; Label: Width of rectangular field [#]: ; Value: 9"
    assert main_window.gui_structure.legend_figure_temperature_profile.__repr__() == "FigureOption; Label: Show legend?; Value: ('legend', False)"


def test_backward_compatibility(qtbot):
    """
    test if the GUI is importing old files correctly

    Parameters
    ----------
    qtbot: qtbot
        bot for the GUI
    """
    import numpy as np

    from GHEtool import FOLDER

    # init gui window
    main_window_old = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window_old._load_from_data(f'{FOLDER}/gui/test_gui/test_file_version_2_1_0.GHEtool')
    # init gui window
    main_window_new = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window_new._load_from_data(f'{FOLDER}/gui/test_gui/test_file_version_2_1_1.GHEtool')
    # check if the imported values are the same
    for ds_old, ds_new in zip(main_window_old.list_ds, main_window_new.list_ds):
        for option in ds_new.list_options_aims:
            if isinstance(getattr(ds_old, option), (int, float)):
                assert np.isclose(getattr(ds_old, option), getattr(ds_new, option))
                continue
            if isinstance(getattr(ds_old, option), (str, bool)):
                assert getattr(ds_old, option) == getattr(ds_new, option)
                continue


def test_datastorage(qtbot):
    """
    tests the datastorage
    """
    # init gui window
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.delete_backup()
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.save_scenario()
    main_window.add_scenario()
    assert not main_window.list_ds[0] == 2
    assert main_window.list_ds[0] == main_window.list_ds[1]
    val_old = main_window.list_ds[1].option_depth
    main_window.list_ds[1].option_depth = 1
    assert not main_window.list_ds[1] == main_window.list_ds[0]
    main_window.list_ds[1].option_depth = val_old
    assert main_window.list_ds[0] == main_window.list_ds[1]
    main_window.list_ds[1].list_options_aims.append('no_real_option')
    assert not main_window.list_ds[1] == main_window.list_ds[0]


def test_float_box(qtbot):
    """
    test float box functions

    Parameters
    ----------
    qtbot: qtbot
        bot for the GUI
    """
    # init gui window
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.delete_backup()
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    option_depth = main_window.gui_structure.option_depth
    assert np.isclose(option_depth.get_value(), option_depth.default_value)
    option_depth.set_value(option_depth.default_value + 50)
    assert np.isclose(option_depth.default_value + 50, option_depth.get_value())
    option_depth._init_links()
    assert option_depth.check_linked_value((200, None))
    assert option_depth.check_linked_value((None, 50))
    assert not option_depth.check_linked_value((50, 200))
    option_depth.show_option(main_window.gui_structure.option_width, 50, 200)
    main_window.gui_structure.page_borehole.button.click()
    assert main_window.gui_structure.option_width.is_hidden()
    option_depth.set_value(20)
    option_depth.show_option(main_window.gui_structure.option_width, 50, 200)
    assert not main_window.gui_structure.option_width.is_hidden()
    option_depth.set_value(220)
    option_depth.show_option(main_window.gui_structure.option_width, 50, 200)
    assert not main_window.gui_structure.option_width.is_hidden()
    option_depth.add_link_2_show(main_window.gui_structure.option_width, 50, 200)
    option_depth.set_value(110)
    assert main_window.gui_structure.option_width.is_hidden()
    option_depth.set_value(20)
    assert not main_window.gui_structure.option_width.is_hidden()
    option_depth.set_value(220)
    assert not main_window.gui_structure.option_width.is_hidden()


def test_int_box(qtbot):
    """
    test float box functions

    Parameters
    ----------
    qtbot: qtbot
        bot for the GUI
    """
    # init gui window
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.delete_backup()
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    option_width = main_window.gui_structure.option_width
    assert np.isclose(option_width.get_value(), option_width.default_value)
    option_width.set_value(option_width.default_value + 5)
    assert np.isclose(option_width.default_value + 5, option_width.get_value())
    option_width._init_links()
    assert option_width.check_linked_value((20, None))
    assert option_width.check_linked_value((None, 2))
    assert not option_width.check_linked_value((5, 20))
    option_width.show_option(main_window.gui_structure.option_depth, 5, 20)
    main_window.gui_structure.page_borehole.button.click()
    assert main_window.gui_structure.option_depth.is_hidden()
    option_width.set_value(4)
    option_width.show_option(main_window.gui_structure.option_depth, 5, 20)
    assert not main_window.gui_structure.option_depth.is_hidden()
    option_width.set_value(22)
    option_width.show_option(main_window.gui_structure.option_depth, 5, 20)
    assert not main_window.gui_structure.option_depth.is_hidden()
    option_width.add_link_2_show(main_window.gui_structure.option_depth, below=5, above=20)
    option_width.set_value(10)
    assert main_window.gui_structure.option_depth.is_hidden()
    option_width.set_value(4)
    assert not main_window.gui_structure.option_depth.is_hidden()
    option_width.set_value(22)
    assert not main_window.gui_structure.option_depth.is_hidden()


def test_filename_read(qtbot) -> None:
    """
    test filename reading function

    Parameters
    ----------
    qtbot: qtbot
        qtbot
    """
    # init gui window
    main_window = MainWindow(QtW.QMainWindow(), qtbot)
    main_window.save_scenario()
    main_window.gui_structure.option_filename._init_links()
    from GHEtool import FOLDER
    import pandas as pd
    file = f'{FOLDER.joinpath("Examples/hourly_profile.csv")}'
    # check if no file is passed
    QtC.QTimer.singleShot(1000, lambda: keyboard.press('Esc'))
    main_window.gui_structure.option_filename.button.click()
    assert main_window.gui_structure.option_filename.status_bar.currentMessage() == main_window.gui_structure.option_filename.error_text
    # check file import and calculation
    QtC.QTimer.singleShot(1000, lambda: keyboard.write(file))
    QtC.QTimer.singleShot(1500, lambda: keyboard.press('enter'))
    main_window.gui_structure.option_filename.button.click()
    assert main_window.gui_structure.option_filename.get_value() == file.replace('\\', '/')
    assert main_window.gui_structure.option_filename.check_linked_value(file.replace('\\', '/'))
    main_window.gui_structure.option_column.set_value(1)
    main_window.gui_structure.option_heating_column.set_value(0)
    main_window.gui_structure.option_cooling_column.set_value(1)
    main_window.gui_structure.button_load_csv.button.click()
    main_window.save_scenario()
    borefield, _ = data_2_borefield(main_window.list_ds[-1])
    # check that the borefield baseload is different from main class base load
    g_s = main_window.gui_structure
    borefield_new = create_borefield(g_s)
    borefield_new.load_hourly_profile(file)
    borefield_new.calculate_monthly_load()
    assert not np.allclose(borefield_new.baseload_cooling, borefield.baseload_cooling)
    assert not np.allclose(borefield_new.baseload_heating, borefield.baseload_heating)
    # manually read and calculate load
    d_f = pd.read_csv(file, sep=';', decimal='.')
    heat = d_f[d_f.columns[0]].to_numpy()
    cool = d_f[d_f.columns[1]].to_numpy()
    idx = np.array([0, 31,28,31,30,31,30,31,31,30,31,30,31]).cumsum() * 24
    baseload_heating = [np.sum(heat[idx[i]:idx[i+1]]).astype(np.int64) for i in range(12)]
    baseload_cooling = [np.sum(cool[idx[i]:idx[i+1]]).astype(np.int64) for i in range(12)]
    peak_heating = [np.max(heat[idx[i]:idx[i+1]]).astype(np.int64) for i in range(12)]
    peak_cooling = [np.max(cool[idx[i]:idx[i+1]]).astype(np.int64) for i in range(12)]
    assert np.allclose(baseload_heating, borefield.baseload_heating, atol=1)
    assert np.allclose(baseload_cooling, borefield.baseload_cooling, atol=1)
    assert np.allclose(peak_heating, borefield.peak_heating, atol=1)
    assert np.allclose(peak_cooling, borefield.peak_cooling, atol=1)
    main_window.delete_backup()


def test_no_valid_value(qtbot) -> None:
    """
    test no valid value

    Parameters
    ----------
    qtbot: qtbot
        qtbot
    """
    # init gui window
    main_window = MainWindow(QtW.QMainWindow(), qtbot)
    main_window.save_scenario()
    gs = main_window.gui_structure
    gs.aim_req_depth.widget.click() if not gs.aim_req_depth.widget.isChecked() else None
    gs.option_method_size_depth.set_value(2)
    gs.option_filename.widget.setText("")
    assert not main_window.save_scenario()
    main_window.start_current_scenario_calculation()
    main_window.start_multiple_scenarios_calculation()


def test_value_error(qtbot) -> None:
    """
    test value error caption

    Parameters
    ----------
    qtbot: qtbot
        qtbot
    """
    # init gui window
    main_window = MainWindow(QtW.QMainWindow(), qtbot)
    main_window.save_scenario()
    main_window.delete_backup()
    main_window = MainWindow(QtW.QMainWindow(), qtbot)
    gs = main_window.gui_structure
    main_window.save_scenario()

    gs.aim_temp_profile.widget.click() if not gs.aim_temp_profile.widget.isChecked() else None
    main_window.gui_structure.option_depth.widget.setMinimum(-500)
    main_window.gui_structure.option_depth.minimal_value = -500
    main_window.gui_structure.option_depth.set_value(-100)
    main_window.save_scenario()
    borefield, func = data_2_borefield(main_window.list_ds[-1])
    with raises(ValueError) as err:
        func()
    main_window.start_current_scenario_calculation(True)
    with qtbot.waitSignal(main_window.threads[0].any_signal, raising=False) as blocker:
        main_window.threads[0].run()
        main_window.threads[0].any_signal.connect(main_window.thread_function)

    main_window.check_results()
    assert f'{main_window.list_ds[-1].debug_message}' == f'{err.value}'
    main_window.delete_backup()


def test_start_gui():
    """
    tests start gui import
    """
    from GHEtool.gui.start_gui import run
