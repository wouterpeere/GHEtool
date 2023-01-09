from math import isclose
from typing import List, Union

from GHEtool import FOLDER
from GHEtool.gui.gui_classes import ButtonBox, FigureOption, FileNameBox, FloatBox, IntBox, ListBox


def test_language(qtbot):
    from GHEtool.gui.translation_csv_to_py import main

    main()

    from PySide6.QtWidgets import QMainWindow as QtWidgets_QMainWindow

    from GHEtool.gui.gui_combine_window import MainWindow

    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.delete_backup()

    for idx, action in enumerate(main_window.menuLanguage.actions()):
        action.trigger()
        assert main_window.gui_structure.option_language.get_value() == idx

    main_window.menuLanguage.actions()[0].trigger()


def test_gui_values(qtbot):
    import sys
    sys.setrecursionlimit(1500)

    from PySide6.QtWidgets import QMainWindow as QtWidgets_QMainWindow

    from GHEtool.gui.gui_combine_window import MainWindow

    # init gui window
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.update_graph()
    main_window.delete_backup()
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.update_graph()

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
            if option.linked_options:
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

    main_window.update_graph()
    main_window.gui_structure.aim_optimize.widget.click()
    main_window.save_scenario()
    main_window.start_current_scenario_calculation(True)
    with qtbot.waitSignal(main_window.threads[0].any_signal, raising=False) as blocker:
        main_window.threads[0].run()
        main_window.threads[0].any_signal.connect(main_window.thread_function)

    main_window.gui_structure.option_column.set_value(0)
    main_window.gui_structure.option_single_column.set_value(0)
    main_window.gui_structure.button_load_csv.button.click()

    main_window.gui_structure.option_column.set_value(1)
    main_window.gui_structure.option_heating_column.set_value(0)
    main_window.gui_structure.option_cooling_column.set_value(1)
    main_window.gui_structure.button_load_csv.button.click()
    #main_window.close()

    print('end')


def test_gui_scenario_properties(qtbot):
    import sys
    sys.setrecursionlimit(1500)

    from PySide6.QtWidgets import QMainWindow as QtWidgets_QMainWindow

    from GHEtool.gui.gui_combine_window import MainWindow

    # init gui window
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.delete_backup()
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)

    assert len(main_window.list_ds) == 0

    main_window.save_scenario()
    assert len(main_window.list_ds) == 1

    for i in range(10):
        main_window.add_scenario()
        assert len(main_window.list_ds) == 2 + i

    for i in range(10):
        main_window.delete_scenario()
        assert len(main_window.list_ds) == 10 - i

    main_window.delete_scenario()
    assert len(main_window.list_ds) == 1


def test_wrong_options_are_shown(qtbot):
    import sys
    sys.setrecursionlimit(1500)

    from PySide6.QtWidgets import QMainWindow as QtWidgets_QMainWindow

    from GHEtool.gui.gui_combine_window import MainWindow

    # init gui window
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.delete_backup()
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.gui_structure.aim_req_depth.widget.click()
    main_window.gui_structure.option_method_size_depth.set_value(2)
    main_window.gui_structure.aim_temp_profile.widget.click()
    assert not main_window.gui_structure.option_len_peak_heating.is_hidden()

    main_window.delete_backup()
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.pushButton_start_single.click()
    main_window.add_scenario()
    main_window.pushButton_start_single.click()
    assert not main_window.gui_structure.max_temp.is_hidden()


def test_backward_compatibility(qtbot):
    import sys
    sys.setrecursionlimit(1500)
    import numpy as np

    from PySide6.QtWidgets import QMainWindow as QtWidgets_QMainWindow

    from GHEtool.gui.gui_combine_window import MainWindow

    from GHEtool import FOLDER
    # init gui window
    main_window_old = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window_old._load_from_data(f'{FOLDER}/gui/test_gui/test_file_version_2_1_0.GHEtool')

    # init gui window
    main_window_new = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window_new._load_from_data(f'{FOLDER}/gui/test_gui/test_file_version_2_1_1.GHEtool')

    for ds_old, ds_new in zip(main_window_old.list_ds, main_window_new.list_ds):
        for option in ds_new.list_options_aims:
            if isinstance(getattr(ds_old, option), (int, float)):
                assert np.isclose(getattr(ds_old, option), getattr(ds_new, option))
                continue
            if isinstance(getattr(ds_old, option), (str, bool)):
                assert getattr(ds_old, option) == getattr(ds_new, option)
                continue

