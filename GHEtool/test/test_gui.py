from GHEtool.gui.gui_classes import FloatBox, IntBox, ListBox, ButtonBox, FileNameBox
from GHEtool.gui.gui_calculation_thread import CalcProblem
from GHEtool.main_class import FOLDER
from typing import List, Union
from math import isclose

def test_gui(qtbot):
    import sys
    sys.setrecursionlimit(1500)

    from PySide6.QtWidgets import QMainWindow as QtWidgets_QMainWindow

    from GHEtool.gui.gui_window import MainWindow

    # init window
    # window =
    #qtbot.addWidget(window)
    # init gui window
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)
    main_window.delete_backup()
    main_window = MainWindow(QtWidgets_QMainWindow(), qtbot)

    main_window.gui_structure.option_filename.set_value(f'{FOLDER}/Examples/hourly_profile.csv')

    for option, _ in main_window.gui_structure.list_of_options:
        if isinstance(option, FloatBox) or isinstance(option, IntBox):
            if option.linked_options:
                option.set_value(option.maximal_value)
                assert isclose(option.get_value(), option.maximal_value)

                option.set_value(option.minimal_value)
                assert isclose(option.get_value(), option.minimal_value)
            else:
                val = option.get_value() + option.step
                option.set_value(val)
                assert isclose(option.get_value(), val)
        if isinstance(option, ListBox) or isinstance(option, ButtonBox):
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

    #main_window.gui_structure.aim_temp_profile.click() if not main_window.gui_structure.aim_temp_profile.widget.isChecked() else None
    #main_window.start_current_scenario_calculation()


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
    # close app
    # sys_exit(qtbot.exec())

