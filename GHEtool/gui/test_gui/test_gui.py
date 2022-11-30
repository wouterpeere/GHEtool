from GHEtool.gui.gui_classes import FloatBox, IntBox, ListBox, ButtonBox, FileNameBox, FigureOption
from GHEtool.main_class import FOLDER
from typing import List, Union
from math import isclose


def test_gui_values(qtbot):
    import sys
    sys.setrecursionlimit(1500)

    from PySide6.QtWidgets import QMainWindow as QtWidgets_QMainWindow

    from GHEtool.gui.gui_combine_window import MainWindow

    # init gui window
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.delete_backup()
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)

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
    print(main_window.list_ds[0].borefield.H)
    #main_window.gui_structure.aim_size_length.widget.click()
    #main_window.start_current_scenario_calculation()

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

