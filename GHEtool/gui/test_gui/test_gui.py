from sys import setrecursionlimit

import PySide6.QtWidgets as QtW
from GHEtool import FOLDER, Borefield
from GHEtool.gui.data_2_borefield_func import data_2_borefield
from GHEtool.gui.gui_classes.gui_combine_window import MainWindow
from GHEtool.gui.gui_classes.translation_class import Translations
from GHEtool.gui.gui_structure import GUI, load_data_GUI
from pytest import raises

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

    main_window = MainWindow(QtW.QMainWindow(), qtbot, GUI, Translations, result_creating_class=Borefield, data_2_results_function=data_2_borefield)
    main_window.delete_backup()

    for idx, action in enumerate(main_window.menu_language.actions()):
        action.trigger()
        assert main_window.gui_structure.option_language.get_value()[0] == idx

    main_window.menu_language.actions()[0].trigger()
    main_window.delete_backup()


def test_wrong_results_shown(qtbot):
    """
    test if results are shown correctly.

    Parameters
    ----------
    qtbot: qtbot
        bot for the GUI
    """
    # init gui window
    main_window = MainWindow(QtW.QMainWindow(), qtbot, GUI, Translations, result_creating_class=Borefield, data_2_results_function=data_2_borefield)
    main_window = MainWindow(QtW.QMainWindow(), qtbot, GUI, Translations, result_creating_class=Borefield, data_2_results_function=data_2_borefield)
    main_window.show()
    main_window.gui_structure.option_decimal_csv.set_value(0)
    main_window.gui_structure.option_seperator_csv.set_value(0)

    main_window.gui_structure.option_filename.set_value(f'{FOLDER}/Examples/hourly_profile.csv')
    main_window.gui_structure.fun_update_combo_box_data_file(f'{FOLDER}/Examples/hourly_profile.csv')
    main_window.gui_structure.option_column.set_value(1)
    main_window.gui_structure.option_cooling_column.set_value(1)

    main_window.gui_structure.aim_optimize.widget.click()
    main_window.save_scenario()
    main_window.start_current_scenario_calculation(True)
    with qtbot.waitSignal(main_window.threads[0].any_signal, raising=False):
        main_window.threads[0].run()
        main_window.threads[0].any_signal.connect(main_window.thread_function)

    main_window.display_results()
    assert not main_window.gui_structure.hourly_figure_temperature_profile.is_hidden()
    assert main_window.gui_structure.result_Rb_calculated.is_hidden()
    assert not main_window.gui_structure.figure_load_duration.is_hidden()
    main_window.gui_structure.page_aim.button.click()
    main_window.gui_structure.page_result.button.click()

    main_window.gui_structure.option_method_rb_calc.set_value(1)
    main_window.save_scenario()
    main_window.start_current_scenario_calculation(True)
    with qtbot.waitSignal(main_window.threads[0].any_signal, raising=False):
        main_window.threads[0].run()
        main_window.threads[0].any_signal.connect(main_window.thread_function)

    main_window.display_results()
    assert not main_window.gui_structure.hourly_figure_temperature_profile.is_hidden()
    assert not main_window.gui_structure.result_Rb_calculated.is_hidden()

    main_window.add_scenario()
    main_window.save_scenario()
    main_window.start_current_scenario_calculation(True)
    with qtbot.waitSignal(main_window.threads[0].any_signal, raising=False):
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
    with qtbot.waitSignal(main_window.threads[0].any_signal, raising=False):
        main_window.threads[0].run()
        main_window.threads[0].any_signal.connect(main_window.thread_function)
    assert main_window.gui_structure.hourly_figure_temperature_profile.is_hidden()


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
    main_window_old = MainWindow(QtW.QMainWindow(), qtbot, GUI, Translations, result_creating_class=Borefield, data_2_results_function=data_2_borefield)
    main_window_old._load_from_data(f'{FOLDER}/gui/test_gui/test_file_version_2_1_0.GHEtool')
    # init gui window
    main_window_new = MainWindow(QtW.QMainWindow(), qtbot, GUI, Translations, result_creating_class=Borefield, data_2_results_function=data_2_borefield)
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
    main_window = MainWindow(QtW.QMainWindow(), qtbot, GUI, Translations, result_creating_class=Borefield, data_2_results_function=data_2_borefield)
    main_window.delete_backup()
    main_window = MainWindow(QtW.QMainWindow(), qtbot, GUI, Translations, result_creating_class=Borefield, data_2_results_function=data_2_borefield)
    main_window.save_scenario()
    main_window.add_scenario()
    assert main_window.list_ds[0] != 2
    assert main_window.list_ds[0] == main_window.list_ds[1]
    val_old = main_window.list_ds[1].option_depth
    main_window.list_ds[1].option_depth = 1
    assert main_window.list_ds[1] != main_window.list_ds[0]
    main_window.list_ds[1].option_depth = val_old
    assert main_window.list_ds[0] == main_window.list_ds[1]
    main_window.list_ds[1].list_options_aims.append('no_real_option')
    assert main_window.list_ds[1] != main_window.list_ds[0]


def test_no_valid_value(qtbot) -> None:
    """
    test no valid value

    Parameters
    ----------
    qtbot: qtbot
        qtbot
    """
    # init gui window
    main_window = MainWindow(QtW.QMainWindow(), qtbot, GUI, Translations, result_creating_class=Borefield, data_2_results_function=data_2_borefield)
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
    main_window = MainWindow(QtW.QMainWindow(), qtbot, GUI, Translations, result_creating_class=Borefield, data_2_results_function=data_2_borefield)
    main_window.save_scenario()
    main_window.delete_backup()
    main_window = MainWindow(QtW.QMainWindow(), qtbot, GUI, Translations, result_creating_class=Borefield, data_2_results_function=data_2_borefield)
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
    with qtbot.waitSignal(main_window.threads[0].any_signal, raising=False):
        main_window.threads[0].run()
        main_window.threads[0].any_signal.connect(main_window.thread_function)

    main_window.display_results()
    for figure in main_window.gui_structure.list_of_result_figures:
        assert figure[0].is_hidden()

    main_window.check_results()
    assert f'{main_window.list_ds[-1].debug_message}' == f'{err.value}'
    main_window.delete_backup()


def test_load_data_gui_errors():
    """
    test the load gui errors.
    """
    with raises(FileNotFoundError):
        load_data_GUI("", 0, 'Heating', 'Cooling', 'Heating', ';', '.', 1)
    with raises(FileNotFoundError):
        load_data_GUI("no_existing_file.csv", 0, 'Heating', 'Cooling', 'Heating', ';', '.', 1)


def test_file_import_errors(qtbot):
    main_window = MainWindow(QtW.QMainWindow(), qtbot, GUI, Translations, result_creating_class=Borefield, data_2_results_function=data_2_borefield)
    main_window.delete_backup()
    main_window = MainWindow(QtW.QMainWindow(), qtbot, GUI, Translations, result_creating_class=Borefield, data_2_results_function=data_2_borefield)
    g_s = main_window.gui_structure
    g_s.option_filename.set_value("")
    main_window.gui_structure.fun_display_data()
    assert main_window.status_bar.widget.currentMessage() == main_window.translations.no_file_selected[0]

    g_s.option_filename.set_value(f'{FOLDER.joinpath("Examples/hourly_profile.csv")}')
    g_s.fun_update_combo_box_data_file(f'{FOLDER.joinpath("Examples/hourly_profile.csv")}')
    g_s.option_single_column.widget.addItem('No Existing Column')
    g_s.option_single_column.set_value(-1)
    main_window.gui_structure.fun_display_data()
    assert main_window.status_bar.widget.currentMessage() == main_window.translations.ColumnError[0]
    g_s.option_single_column.set_value(0)
    g_s.option_heating_column.set_value(0)
    g_s.option_cooling_column.set_value(1)
    g_s.option_filename.set_value(f'{FOLDER.joinpath("Examples/hourly_profile_wrong.csv")}')
    main_window.gui_structure.fun_display_data()
    assert main_window.status_bar.widget.currentMessage() == main_window.translations.ValueError[0]

