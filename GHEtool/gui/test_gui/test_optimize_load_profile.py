from sys import setrecursionlimit

import numpy as np
from PySide6.QtWidgets import QMainWindow as QtWidgets_QMainWindow

from GHEtool import FOLDER
from GHEtool.gui.gui_combine_window import MainWindow
from GHEtool.gui.gui_structure import load_data_GUI

setrecursionlimit(1500)


def test_building_load(qtbot):
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

    # load data
    main_window.save_scenario()
    peak_heating, peak_cooling = load_data_GUI(
        filename=main_window.list_ds[0].option_filename,
        thermal_demand=main_window.list_ds[0].option_column,
        heating_load_column=main_window.list_ds[0].option_heating_column_text,
        cooling_load_column=main_window.list_ds[0].option_cooling_column_text,
        combined=main_window.list_ds[0].option_single_column_text,
        sep=";" if main_window.list_ds[0].option_seperator_csv == 0 else ",",
        dec="." if main_window.list_ds[0].option_decimal_csv == 0 else ",",
        fac=1, hourly=True)

    # set optimize load profile
    main_window.gui_structure.aim_optimize.widget.click()
    main_window.save_scenario()
    main_window.start_current_scenario_calculation(True)
    with qtbot.waitSignal(main_window.threads[0].any_signal, raising=False) as blocker:
        main_window.threads[0].run()
        main_window.threads[0].any_signal.connect(main_window.thread_function)

    # check if the data is the same
    assert np.allclose(main_window.list_ds[0].borefield.hourly_cooling_load, peak_cooling)
    assert np.allclose(main_window.list_ds[0].borefield.hourly_heating_load, peak_heating)

    # calculate with geothermal load
    main_window.gui_structure.aim_temp_profile.widget.click()
    main_window.save_scenario()
    without_SCOP = main_window.list_ds[0].peakHeating
    without_SEER = main_window.list_ds[0].peakCooling
    without_SCOP_avg = main_window.list_ds[0].monthlyLoadHeating
    without_SEER_avg = main_window.list_ds[0].monthlyLoadCooling

    # calculate with building load
    main_window.gui_structure.geo_load.set_value(1)
    main_window.save_scenario()

    # check loads
    assert main_window.list_ds[0].peakHeating == [i * (1 - 1/4) for i in without_SCOP]
    assert main_window.list_ds[0].peakCooling == [i * (1 + 1/3) for i in without_SEER]
    assert main_window.list_ds[0].monthlyLoadHeating == [i * (1 - 1 / 4) for i in without_SCOP_avg]
    assert main_window.list_ds[0].monthlyLoadCooling == [i * (1 + 1 / 3) for i in without_SEER_avg]

    main_window.gui_structure.option_temperature_profile_hourly.set_value(1)
    main_window.save_scenario()
    main_window.start_current_scenario_calculation(True)
    with qtbot.waitSignal(main_window.threads[0].any_signal, raising=False) as blocker:
        main_window.threads[0].run()
        main_window.threads[0].any_signal.connect(main_window.thread_function)

    # # check if the data is the same
    assert np.allclose(main_window.list_ds[0].borefield.hourly_cooling_load / (1 + 1/3), peak_cooling)
    assert np.allclose(main_window.list_ds[0].borefield.hourly_heating_load / (1 - 1/4), peak_heating)

