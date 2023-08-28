from sys import setrecursionlimit

import numpy as np
from PySide6.QtWidgets import QMainWindow as QtWidgets_QMainWindow

import PySide6.QtWidgets as QtW
from GHEtool import FOLDER, Borefield
from GHEtool.gui.data_2_borefield_func import data_2_borefield, _create_monthly_loads_peaks
from GHEtool.gui.gui_classes.gui_combine_window import MainWindow
from GHEtool.gui.gui_classes.translation_class import Translations
from GHEtool.gui.gui_structure import GUI, load_data_GUI


setrecursionlimit(1500)


def test_building_load(qtbot):
    # init gui window
    main_window = MainWindow(QtW.QMainWindow(), qtbot, GUI, Translations, result_creating_class=Borefield, data_2_results_function=data_2_borefield)
    main_window.delete_backup()
    main_window = MainWindow(QtW.QMainWindow(), qtbot, GUI, Translations, result_creating_class=Borefield, data_2_results_function=data_2_borefield)
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
    main_window.start_current_scenario_calculation()
    thread = main_window.threads[-1]
    thread.run()
    assert thread.calculated

    # check if the data is the same, because optimize load profile needs the building, not the ground data
    assert np.allclose(main_window.list_ds[0].results._building_load.hourly_cooling_load, peak_cooling)
    assert np.allclose(main_window.list_ds[0].results._building_load.hourly_heating_load, peak_heating)

    # check if the resultTexts are correct
    gs = main_window.gui_structure
    main_window.display_results()

    assert gs.results_heating_load.label.text() == "Heating load on the borefield: 566750.0 kWh"
    assert gs.results_heating_peak_geo.label.text() == "with a peak of: 310.29 kW"
    assert gs.results_heating_load_percentage.label.text() == "This is 88.14 % of the heating load"
    assert gs.results_heating_ext.label.text() == "Heating load external: 76267.0 kWh"
    assert gs.results_heating_peak.label.text() == "with a peak of: 225.75 kW"
    assert gs.results_cooling_load.label.text() == "Cooling load on the borefield: 173773.0 kWh"
    assert gs.results_cooling_peak_geo.label.text() == "with a peak of: 121.57 kW"
    assert gs.results_cooling_load_percentage.label.text() == "This is 64.9 % of the cooling load"
    assert gs.results_cooling_ext.label.text() == "Cooling load external: 93971.0 kWh"
    assert gs.results_cooling_peak.label.text() == "with a peak of: 554.85 kW"

    # calculate with geothermal load
    main_window.gui_structure.aim_temp_profile.widget.click()
    main_window.gui_structure.geo_load.set_value(0)
    main_window.save_scenario()
    without_SCOP, without_SEER, without_SCOP_avg, without_SEER_avg = _create_monthly_loads_peaks(main_window.list_ds[-1])

    # calculate with building load
    main_window.gui_structure.geo_load.set_value(1)
    main_window.save_scenario()

    with_SCOP, with_SEER, with_SCOP_avg, with_SEER_avg = _create_monthly_loads_peaks(main_window.list_ds[-1])

    # check loads
    assert np.array_equal(with_SCOP, (1 - 1/4) * without_SCOP)
    assert np.array_equal(with_SEER, (1 + 1/3) * without_SEER)
    assert np.array_equal(with_SCOP_avg, (1 - 1 / 4) * without_SCOP_avg)
    assert np.array_equal(with_SEER_avg, (1 + 1 / 3) * without_SEER_avg)

    main_window.gui_structure.option_temperature_profile_hourly.set_value(1)
    main_window.save_scenario()
    main_window.start_current_scenario_calculation()
    thread = main_window.threads[-1]
    thread.run()
    assert thread.calculated

    # # check if the data is the same
    assert np.allclose(main_window.list_ds[0].results.load.hourly_cooling_load / (1 + 1/3), peak_cooling)
    assert np.allclose(main_window.list_ds[0].results.load.hourly_heating_load / (1 - 1/4), peak_heating)
