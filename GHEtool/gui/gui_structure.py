"""
This document contains all the information relevant for the GUI.
It contains all the options, categories etc. that should appear on the GUI.
"""
import logging
from functools import partial
from math import cos, pi, sin
from pathlib import Path
from typing import List, Optional, Tuple, TYPE_CHECKING

import PySide6.QtGui as QtG
import PySide6.QtWidgets as QtW
import PySide6.QtCore as QtC
import pandas as pd

from GHEtool import FOLDER
from GHEtool.gui.gui_classes.translation_class import Translations
from numpy import array, cos, int64, round, sin, sum
from pandas import DataFrame as pd_DataFrame
from pandas import read_csv as pd_read_csv
import ScenarioGUI.global_settings as globs
from ScenarioGUI import GuiStructure
from ScenarioGUI import elements as els
from ScenarioGUI.gui_classes.gui_structure_classes import (
    Aim,
    ButtonBox,
    Category,
    FigureOption,
    FileNameBox,
    FloatBox,
    FunctionButton,
    Hint,
    IntBox,
    ListBox,
    Option,
    Page,
    ResultFigure,
    ResultText,
)

if TYPE_CHECKING:  # pragma: no cover
    from GHEtool.gui.gui_classes.translation_class import Translations


def load_data_GUI(filename: str, thermal_demand: int, heating_load_column: str, cooling_load_column: str, combined: str, sep: str,
                  dec: str, fac: float, hourly: bool = False):
    """
    This function loads hourly thermal data from a given file.
    This data can have one or two columns, can be in W, kW or MW.

    Parameters
    ----------
    filename : str
        Location of the file which should be loaded
    thermal_demand : int
        1 if the thermal demand has two columns, 0 if it has one
    heating_load_column : str
        Name of the column that has the heating values
    cooling_load_column : str
        Name of the column that has the cooling values
    combined : str
        Name of the column that has both heating and cooling values
    sep : str
        Character used for the separation of values in the vile
    dec : str
        Character used for decimal separator in the file
    fac : float
        A factor to convert the data to [kW]
    hourly : bool
        True if hourly data should be returned

    Returns
    -------
    peak_heating, peak_cooling, heating_load, cooling_load : array, array, array, array
        It returns the peak heating and peak cooling load per month [kW] and the monthly heating and cooling load in [kWh]
        If hourly is True, it only returns the peak heating and peak cooling load [kW]

    Raises
    ------
    FileNotFoundError
        If the filename is empty or it cannot be found

    """
    # raise error if no filename exists
    if filename == "":
        raise FileNotFoundError

    # Generate list of columns that have to be imported
    cols: list = []
    if len(heating_load_column) >= 1:
        cols.append(heating_load_column)
    if len(cooling_load_column) >= 1:
        cols.append(cooling_load_column)
    if len(combined) >= 1:
        cols.append(combined)
    date: str = "Date"
    try:
        df2: pd_DataFrame = pd_read_csv(filename, usecols=cols, sep=sep, decimal=dec)
    except:
        raise FileNotFoundError

    # not the correct decimal seperator
    if isinstance(df2.iloc[1, 1], str):
        logging.error("Please select the correct decimal point seperator.")
        raise ValueError

    # ---------------------- Time Step Section  ----------------------
    # import pandas here to save start up time
    from pandas import Series as pd_Series
    from pandas import date_range as pd_date_range
    from pandas import to_datetime as pd_to_datetime

    # Define start and end date
    start = pd_to_datetime("2019-01-01 00:00:00")
    end = pd_to_datetime("2019-12-31 23:59:00")
    # add date column
    df2[date] = pd_Series(pd_date_range(start, end, freq="1H"))
    # Create no dict to create mean values for
    dict_agg: Optional[None, dict] = None

    # set date to index
    df2 = df2.set_index(date)
    # resample data to hourly resolution if necessary
    df2 = df2 if dict_agg is None else df2.resample("H").agg(dict_agg)
    # ------------------- Calculate Section --------------------
    # Choose path between Single or Combined Column and create new columns
    if thermal_demand == 1:
        # Resample the Data for peakHeating and peakCooling
        df2 = df2.rename(columns={heating_load_column: "Heating Load", cooling_load_column: "Cooling Load"})
        df2["peak Heating"] = df2["Heating Load"]
        df2["peak Cooling"] = df2["Cooling Load"]
    # by single column split by 0 to heating (>0) and cooling (<0)
    elif thermal_demand == 0:
        # Create Filter for heating and cooling load ( Heating Load +, Cooling Load -)
        heating_load = df2[combined].apply(lambda x: x >= 0)
        cooling_load = df2[combined].apply(lambda x: x < 0)
        df2["Heating Load"] = df2.loc[heating_load, combined]
        df2["Cooling Load"] = df2.loc[cooling_load, combined] * -1
        df2["peak Heating"] = df2["Heating Load"]
        df2["peak Cooling"] = df2["Cooling Load"]

    # ----------------------- Data Unit Section --------------------------
    # multiply dataframe with unit factor and collect data
    df2 = df2 * fac
    df2 = df2.fillna(0)

    if hourly:
        return df2["peak Heating"], df2["peak Cooling"]

    # resample to a monthly resolution as sum and maximal load
    df3: pd_DataFrame = df2.resample("M").agg(
        {"Heating Load": "sum", "Cooling Load": "sum", "peak Heating": "max", "peak Cooling": "max"})
    # replace nan with 0
    df3 = df3.fillna(0)

    peak_heating = df3["peak Heating"]
    peak_cooling = df3["peak Cooling"]
    heating_load = df3["Heating Load"]
    cooling_load = df3["Cooling Load"]

    return peak_heating, peak_cooling, heating_load, cooling_load


class GUI(GuiStructure):
    """
    This class contains all the elements that are relevant for the GUI.
    """
    def __init__(self, default_parent: QtW.QWidget, translations: Translations):
        """
        All the elements that should be placed on the GUI, should be written in
        chronologial order, in this __init__ function.
        """
        # set default parent for the class variables to avoid widgets creation not in the main window
        super().__init__(default_parent, translations)

        #################################################################################################################
        #                                                                                                               #
        # GUI STRUCTURE                                                                                                 #
        #                                                                                                               #
        #################################################################################################################


        #def create_page_aim():
        # create page
        self.page_aim = Page(name=translations.page_aim, button_name="Aim", icon="Aim_Inv.svg")

        self.aim_temp_profile = Aim(page=self.page_aim, label=translations.aim_temp_profile, icon="Temp_Profile.svg")
        self.aim_req_depth = Aim(page=self.page_aim, label=translations.aim_req_depth, icon="depth_determination.svg")
        # self.aim_size_length = Aim(page=self.page_aim, label="Size borefield by length and width", icon="Size_Length.svg")
        self.aim_optimize = Aim(page=self.page_aim, label=translations.aim_optimize, icon="Optimize_Profile.svg")

        #def create_page_options():
        # create page
        self.page_options = Page(translations.page_options, "Options", "Options.svg")
        self.page_aim.set_next_page(self.page_options)
        self.page_options.set_previous_page(self.page_aim)

        #def create_category_calculation():
        self.category_calculation = Category(page=self.page_options, label=translations.category_calculation)

        self.option_method_size_depth = ButtonBox(label=translations.option_method_size_depth, default_index=0,
                                                  entries=[" L2 ", " L3 ", "  L4  "],
                                                  category=self.category_calculation)
        # self.option_method_size_length = ButtonBox(label="Method for size width and length:", default_index=0,
        #                                            entries=[" L2 ", " L3 "], category=self.category_calculation)
        self.option_method_temp_gradient = ButtonBox(
            label=translations.option_method_temp_gradient, default_index=0,
            entries=[" no ", " yes  "], category=self.category_calculation)
        self.option_method_rb_calc = ButtonBox(label=translations.option_method_rb_calc, default_index=0,
                                               entries=[" constant ", " dynamic "],
                                               category=self.category_calculation)
        self.option_temperature_profile_hourly = ButtonBox(
            label=translations.option_temperature_profile_hourly, default_index=0,
            entries=[" no ", " yes "], category=self.category_calculation)
        # add dependencies
        # self.aim_size_length.add_link_2_show(self.option_method_size_length)
        self.aim_req_depth.add_link_2_show(self.option_method_size_depth)
        self.aim_temp_profile.add_link_2_show(self.option_temperature_profile_hourly)

        # create categories
        #create_category_calculation()

        # def create_page_borehole():
        # create page
        self.page_borefield = Page(translations.page_borefield, "Borehole\nand earth", "RectField")
        self.page_options.set_next_page(self.page_borefield)
        self.page_borefield.set_previous_page(self.page_options)

        self.aim_rect = Aim(page=self.page_borefield, label="Rectangular borefield", icon="RectField.svg")
        self.aim_Box_shaped = Aim(page=self.page_borefield, label="Box shaped borefield", icon="BoxField.svg")
        self.aim_L_shaped = Aim(page=self.page_borefield, label="L-shaped borefield", icon="LField.svg")
        self.aim_U_shaped = Aim(page=self.page_borefield, label="U-shaped borefield", icon="UField.svg")
        self.aim_circle = Aim(page=self.page_borefield, label="Circle borefield", icon="CircleField.svg")
        self.aim_custom = Aim(page=self.page_borefield, label="Customized borefield", icon="FlexField.svg")

        # def create_category_borehole():
        self.category_borefield = Category(
            page=self.page_borefield,
            label=translations.category_borehole,
        )
        self.category_borefield.activate_graphic_left()

        self.option_depth = FloatBox(
            category=self.category_borefield,
            label=translations.option_depth,
            default_value=100,
            decimal_number=2,
            minimal_value=0,
            maximal_value=5_000,
            step=1,
        )
        # self.option_max_depth = FloatBox(
        #     category=self.category_borehole,
        #     label="Maximal borehole depth [m]: ",
        #     default_value=150,
        #     decimal_number=2,
        #     minimal_value=0,
        #     maximal_value=500,
        #     step=1,
        # )
        self.option_spacing = FloatBox(
            category=self.category_borefield,
            label=translations.option_spacing,
            default_value=6,
            decimal_number=2,
            minimal_value=1,
            maximal_value=99,
            step=0.1,
        )
        self.option_spacing.change_event(self.update_borefield)
        self.option_spacing_length = FloatBox(
            category=self.category_borefield,
            label=translations.option_spacing_length,
            default_value=6,
            decimal_number=2,
            minimal_value=1,
            maximal_value=99,
            step=0.1,
        )
        self.option_spacing_length.change_event(self.update_borefield)
        self.option_borefield_radius = els.FloatBox(category=self.category_borefield, label=translations.option_borefield_radius,
                                                    minimal_value=0, maximal_value=1_000_000, default_value=12.5, step=0.1, decimal_number=2)

        self.option_borefield_radius.change_event(self.update_borefield)
        self.option_number_circle_boreholes = els.IntBox(category=self.category_borefield, label=translations.option_number_circle_boreholes,
                                                    minimal_value=2, maximal_value=1_000_000, default_value=12, step=1)
        self.option_number_circle_boreholes.change_event(self.update_borefield)
        # self.option_min_spacing = FloatBox(
        #     category=self.category_borehole,
        #     label="Minimal borehole spacing [m]: ",
        #     default_value=3,
        #     decimal_number=2,
        #     minimal_value=1,
        #     maximal_value=99,
        #     step=0.1,
        # )
        # self.option_max_spacing = FloatBox(
        #     category=self.category_borehole,
        #     label="Maximal borehole spacing [m]: ",
        #     default_value=9,
        #     decimal_number=2,
        #     minimal_value=1,
        #     maximal_value=99,
        #     step=0.1,
        # )
        self.option_width = IntBox(
            category=self.category_borefield, label=translations.option_width, default_value=9, minimal_value=1, maximal_value=40
        )
        self.option_width.change_event(self.update_borefield)
        self.option_length = IntBox(
            category=self.category_borefield, label=translations.option_length, default_value=12, minimal_value=1, maximal_value=40
        )
        self.option_length.change_event(self.update_borefield)
        # self.option_max_width = FloatBox(
        #     category=self.category_borehole,
        #     label="Maximal width of rectangular field [m]: ",
        #     default_value=160,
        #     decimal_number=2,
        #     minimal_value=1,
        #     maximal_value=1000,
        #     step=1,
        # )
        # self.option_max_length = FloatBox(
        #     category=self.category_borehole,
        #     label="Maximal length of rectangular field [m]: ",
        #     default_value=150,
        #     decimal_number=2,
        #     minimal_value=1,
        #     maximal_value=1000,
        #     step=1,
        # )
        self.option_pipe_depth = FloatBox(
            category=self.category_borefield,
            label=translations.option_pipe_depth,
            default_value=1,
            decimal_number=1,
            minimal_value=0,
            maximal_value=10000,
            step=0.1,
        )

        self.option_pipe_borehole_radius = FloatBox(
            category=self.category_borefield,
            label=translations.option_pipe_borehole_radius,
            default_value=0.075,
            decimal_number=4,
            minimal_value=0,
            maximal_value=10000,
            step=0.001,
        )

        self.option_tilted = FloatBox(
            category=self.category_borefield,
            label="Tilt [Â°] (0Â° = vertical, 90Â° horizontal directed to exterior)",
            default_value=0.0,
            decimal_number=2,
            minimal_value=-90,
            maximal_value=90,
            step=0.001,
        )
        self.option_tilted.hide()


        self.option_seperator_borefield = ButtonBox(label=translations.option_seperator_borefield, default_index=0,
                                              entries=['Semicolon ";"', 'Comma ","', 'Tab "   "'],
                                              category=self.category_borefield)
        self.option_decimal_borefield = ButtonBox(label=translations.option_decimal_borefield, default_index=0,
                                            entries=['Point "."', 'Comma ","'],
                                            category=self.category_borefield)

        file = f"{FOLDER.joinpath('gui/test_gui/borefield_data.csv')}"
        self.borefield_file = els.FileNameBox(label=translations.borefield_file, category=self.category_borefield, default_value=file, file_extension=["csv", "txt"])
        self.import_borefield = els.FunctionButton(button_text=translations.import_borefield, icon="Download", category=self.category_borefield)
        self.import_borefield.change_event(self.fun_import_borefield)

        self.custom_borefield = els.FlexibleAmount(label=translations.custom_borefield, default_length=1, entry_mame="Borehole", category=self.category_borefield,
                                                   min_length=1)
        self.custom_borefield.add_option(els.FloatBox, name="x [m]", default_value=0, minimal_value=-1_000_000, maximal_value=1_000_000,  decimal_number=2)
        self.custom_borefield.add_option(els.FloatBox, name="y [m]", default_value=0, minimal_value=-1_000_000, maximal_value=1_000_000,  decimal_number=2)
        self.custom_borefield.add_option(els.FloatBox, name="depth [m]", default_value=100, minimal_value=0, maximal_value=1_000_000)
        self.custom_borefield.add_option(els.FloatBox, name="buried depth [m]", default_value=2, minimal_value=0, maximal_value=1_000_000,  decimal_number=2)
        self.custom_borefield.add_option(els.FloatBox, name="Borehole radius [m]", default_value=0.075, minimal_value=0, maximal_value=1_000,
                                         decimal_number=4, step=0.01)
        # self.custom_borefield.add_option(els.FloatBox, name="tilt [Â°]", default_value=0, minimal_value=-90, maximal_value=90)
        self.custom_borefield.change_event(self.update_borefield)

        # add dependencies
        #self.aim_temp_profile.add_link_2_show(self.option_depth)
        #self.aim_optimize.add_link_2_show(self.option_depth)
        li_aim = [self.aim_optimize, self.aim_temp_profile, self.aim_req_depth, self.aim_rect, self.aim_Box_shaped, self.aim_L_shaped, self.aim_U_shaped,
                  self.aim_circle, self.aim_custom]
        _ = [aim.change_event(partial(show_option_on_multiple_aims,
                                      [self.aim_optimize, self.aim_temp_profile],
                                      [self.aim_rect, self.aim_Box_shaped, self.aim_L_shaped, self.aim_U_shaped, self.aim_circle],
                                      self.option_depth)) for aim in li_aim]
        # self.aim_size_length.add_link_2_show(self.option_max_depth)

        _ = [aim.change_event(partial(show_option_on_multiple_aims,
                                      [self.aim_optimize, self.aim_temp_profile, self.aim_req_depth],
                                      [self.aim_rect,self.aim_Box_shaped, self.aim_L_shaped,self.aim_U_shaped],
                                      self.option_spacing)) for aim in li_aim]
        _ = [aim.change_event(partial(show_option_on_multiple_aims,
                                      [self.aim_optimize, self.aim_temp_profile, self.aim_req_depth],
                                      [self.aim_rect,self.aim_Box_shaped, self.aim_L_shaped,self.aim_U_shaped],
                                      self.option_spacing_length)) for aim in li_aim]

        # self.aim_size_length.add_link_2_show(self.option_min_spacing)
        # self.aim_size_length.add_link_2_show(self.option_max_spacing)

        _ = [aim.change_event(partial(show_option_on_multiple_aims,
                                      [self.aim_optimize, self.aim_temp_profile, self.aim_req_depth],
                                      [self.aim_rect,self.aim_Box_shaped, self.aim_L_shaped,self.aim_U_shaped],
                                      self.option_width)) for aim in li_aim]

        _ = [aim.change_event(partial(show_option_on_multiple_aims,
                                      [self.aim_optimize, self.aim_temp_profile, self.aim_req_depth],
                                      [self.aim_rect,self.aim_Box_shaped, self.aim_L_shaped,self.aim_U_shaped],
                                      self.option_length)) for aim in li_aim]

        _ = [aim.change_event(partial(show_option_on_multiple_aims,
                                      [self.aim_optimize, self.aim_temp_profile, self.aim_req_depth],
                                      [self.aim_rect,self.aim_Box_shaped, self.aim_L_shaped,self.aim_U_shaped, self.aim_circle],
                                      self.option_pipe_depth)) for aim in li_aim]

        _ = [aim.change_event(partial(show_option_on_multiple_aims,
                                      [self.aim_optimize, self.aim_temp_profile, self.aim_req_depth],
                                      [self.aim_rect, self.aim_Box_shaped, self.aim_L_shaped, self.aim_U_shaped, self.aim_circle],
                                      self.option_pipe_borehole_radius)) for aim in li_aim]

        _ = [aim.change_event(partial(show_option_on_multiple_aims,
                                      [self.aim_optimize, self.aim_temp_profile, self.aim_req_depth],
                                      [self.aim_circle],
                                      self.option_number_circle_boreholes)) for aim in li_aim]

        _ = [aim.change_event(partial(show_option_on_multiple_aims,
                                      [self.aim_optimize, self.aim_temp_profile, self.aim_req_depth],
                                      [self.aim_circle],
                                      self.option_borefield_radius)) for aim in li_aim]

        _ = [aim.change_event(partial(show_option_on_multiple_aims,
                                      [self.aim_optimize, self.aim_temp_profile, self.aim_req_depth],
                                      [self.aim_custom],
                                      self.custom_borefield)) for aim in li_aim]

        _ = [aim.change_event(partial(show_option_on_multiple_aims,
                                      [self.aim_optimize, self.aim_temp_profile, self.aim_req_depth],
                                      [self.aim_custom],
                                      self.import_borefield)) for aim in li_aim]

        _ = [aim.change_event(partial(show_option_on_multiple_aims,
                                      [self.aim_optimize, self.aim_temp_profile, self.aim_req_depth],
                                      [self.aim_custom],
                                      self.borefield_file)) for aim in li_aim]

        _ = [aim.change_event(partial(show_option_on_multiple_aims,
                                      [self.aim_optimize, self.aim_temp_profile, self.aim_req_depth],
                                      [self.aim_custom],
                                      self.option_seperator_borefield)) for aim in li_aim]

        _ = [aim.change_event(partial(show_option_on_multiple_aims,
                                      [self.aim_optimize, self.aim_temp_profile, self.aim_req_depth],
                                      [self.aim_custom],
                                      self.option_decimal_borefield)) for aim in li_aim]

        [aim.change_event(self.update_borefield) for aim in li_aim]

        self.page_borefield.add_function_called_if_button_clicked(self.update_borefield)

        self.page_earth = Page(translations.page_earth, "earth", "Borehole.png")
        self.page_borefield.set_next_page(self.page_earth)
        self.page_earth.set_previous_page(self.page_borefield)

        # def create_category_earth():
        self.category_earth = Category(
            page=self.page_earth,
            label=translations.category_earth,
        )

        self.option_conductivity = FloatBox(
            category=self.category_earth,
            label=translations.option_conductivity,
            default_value=1.5,
            decimal_number=3,
            minimal_value=0.1,
            maximal_value=10,
            step=0.1,
        )

        self.option_heat_capacity = FloatBox(
            category=self.category_earth,
            label=translations.option_heat_capacity,
            default_value=2400,
            decimal_number=1,
            minimal_value=1,
            maximal_value=100_000,
            step=100,
        )
        self.option_ground_temp = FloatBox(
            category=self.category_earth,
            label=translations.option_ground_temp,
            default_value=12,
            decimal_number=2,
            minimal_value=-273.15,
            maximal_value=100,
            step=0.1,
        )
        self.option_ground_temp_gradient = FloatBox(
            category=self.category_earth,
            label=translations.option_ground_temp_gradient,
            default_value=10,
            decimal_number=2,
            minimal_value=-273.15,
            maximal_value=100,
            step=0.1,
        )
        self.option_temp_gradient = FloatBox(
            category=self.category_earth,
            label=translations.option_temp_gradient,
            default_value=2,
            decimal_number=3,
            minimal_value=-273.15,
            maximal_value=100,
            step=0.1,
        )

        # add dependencies
        self.option_method_temp_gradient.add_link_2_show(self.option_ground_temp_gradient, on_index=1)
        self.option_method_temp_gradient.add_link_2_show(self.option_temp_gradient, on_index=1)
        self.option_method_temp_gradient.add_link_2_show(self.option_ground_temp, on_index=0)

        # self.aim_size_length.add_link_2_show(self.option_max_width)
        # self.aim_size_length.add_link_2_show(self.option_max_length)

        # def create_category_temperatures():
        self.category_temperatures = Category(page=self.page_earth, label=translations.category_temperatures)

        self.option_min_temp = FloatBox(
            category=self.category_temperatures,
            label=translations.option_min_temp,
            default_value=0,
            decimal_number=2,
            minimal_value=-273.15,
            maximal_value=100,
            step=0.1,
        )
        self.option_max_temp = FloatBox(
            category=self.category_temperatures,
            label=translations.option_max_temp,
            default_value=16,
            decimal_number=2,
            minimal_value=-273.15,
            maximal_value=100,
            step=0.1,
        )
        self.option_simu_period = IntBox(
            category=self.category_temperatures, label=translations.option_simu_period, default_value=40, minimal_value=1, maximal_value=100
        )

        self.option_len_peak_heating = FloatBox(
            category=self.category_temperatures, label=translations.option_len_peak_heating,
            default_value=6, minimal_value=1, maximal_value=8760, step=1,
            decimal_number=2
        )
        self.option_len_peak_cooling = FloatBox(
            category=self.category_temperatures, label=translations.option_len_peak_cooling,
            default_value=6, minimal_value=1, maximal_value=8760, step=1,
            decimal_number=2
        )

        # add dependencies
        self.option_temperature_profile_hourly.add_link_2_show(self.option_len_peak_heating, on_index=0)
        self.option_method_size_depth.add_link_2_show(self.option_len_peak_heating, on_index=0)
        self.option_method_size_depth.add_link_2_show(self.option_len_peak_heating, on_index=1)
        self.aim_optimize.add_link_2_show(self.option_len_peak_heating)

        self.option_temperature_profile_hourly.add_link_2_show(self.option_len_peak_cooling, on_index=0)
        self.option_method_size_depth.add_link_2_show(self.option_len_peak_cooling, on_index=0)
        self.option_method_size_depth.add_link_2_show(self.option_len_peak_cooling, on_index=1)
        self.aim_optimize.add_link_2_show(self.option_len_peak_cooling)

        # create categories
        #create_category_earth()
        #create_category_borehole()
        #create_category_temperatures()

        #def create_page_borehole_resistance():
        # create page
        self.page_borehole_resistance = Page(translations.page_borehole_resistance, "Borehole\nresistance", "Resistance.png")
        self.page_borefield.set_next_page(self.page_borehole_resistance)
        self.page_borehole_resistance.set_previous_page(self.page_borefield)

        #def create_category_constant_rb():
        self.category_constant_rb = Category(page=self.page_borehole_resistance, label=translations.category_constant_rb)

        self.option_constant_rb = FloatBox(
            category=self.category_constant_rb,
            label=translations.option_constant_rb,
            default_value=0.08,
            decimal_number=4,
            minimal_value=0,
            maximal_value=100,
            step=0.01,
        )

        # add dependency
        self.option_method_rb_calc.add_link_2_show(self.category_constant_rb, on_index=0)

        #def create_category_fluid_data():
        self.category_fluid_data = Category(page=self.page_borehole_resistance, label=translations.category_fluid_data)

        self.option_fluid_conductivity = FloatBox(
            category=self.category_fluid_data,
            label=translations.option_fluid_conductivity,
            default_value=0.5,
            decimal_number=3,
            minimal_value=0,
            maximal_value=100,
            step=0.1,
        )
        self.option_fluid_density = FloatBox(
            category=self.category_fluid_data,
            label=translations.option_fluid_density,
            default_value=1000,
            decimal_number=1,
            minimal_value=0,
            maximal_value=10000000,
            step=100,
        )
        self.option_fluid_capacity = FloatBox(
            category=self.category_fluid_data,
            label=translations.option_fluid_capacity,
            default_value=4182,
            decimal_number=1,
            minimal_value=0,
            maximal_value=10000000,
            step=100,
        )
        self.option_fluid_viscosity = FloatBox(
            category=self.category_fluid_data,
            label=translations.option_fluid_viscosity,
            default_value=0.001,
            decimal_number=6,
            minimal_value=0,
            maximal_value=1,
            step=0.0001,
        )

        self.option_fluid_mass_flow = FloatBox(
            category=self.category_fluid_data,
            label=translations.option_fluid_mass_flow,
            default_value=0.5,
            decimal_number=3,
            minimal_value=0,
            maximal_value=100000,
            step=0.1,
        )

        # add dependencies
        self.option_method_rb_calc.add_link_2_show(self.category_fluid_data, on_index=1)

        # def create_category_pipe_data():
        self.category_pipe_data = Category(page=self.page_borehole_resistance, label=translations.category_pipe_data)
        self.category_pipe_data.activate_graphic_left()

        self.option_pipe_number = IntBox(
            category=self.category_pipe_data, label=translations.option_pipe_number, default_value=2, minimal_value=1, maximal_value=99
        )
        self.option_pipe_grout_conductivity = FloatBox(
            category=self.category_pipe_data,
            label=translations.option_pipe_grout_conductivity,
            default_value=1.5,
            decimal_number=3,
            minimal_value=0,
            maximal_value=10000,
            step=0.1,
        )
        self.option_pipe_conductivity = FloatBox(
            category=self.category_pipe_data,
            label=translations.option_pipe_conductivity,
            default_value=0.42,
            decimal_number=3,
            minimal_value=0,
            maximal_value=10000,
            step=0.1,
        )
        self.option_pipe_inner_radius = FloatBox(
            category=self.category_pipe_data,
            label=translations.option_pipe_inner_radius,
            default_value=0.02,
            decimal_number=4,
            minimal_value=0,
            maximal_value=10000,
            step=0.001,
        )
        self.option_pipe_outer_radius = FloatBox(
            category=self.category_pipe_data,
            label=translations.option_pipe_outer_radius,
            default_value=0.022,
            decimal_number=4,
            minimal_value=0,
            maximal_value=10000,
            step=0.001,
        )
        self.option_pipe_outer_radius.change_event(self.option_pipe_inner_radius.widget.setMaximum)
        self.option_pipe_inner_radius.change_event(self.option_pipe_outer_radius.widget.setMinimum)

        self.option_pipe_borehole_radius_2 = FloatBox(
            category=self.category_pipe_data,
            label=translations.option_pipe_borehole_radius_2,
            default_value=0.075,
            decimal_number=4,
            minimal_value=0,
            maximal_value=10000,
            step=0.001,
        )
        self.option_pipe_borehole_radius_2.change_event(self.check_distance_between_pipes)
        self.option_pipe_borehole_radius_2.change_event(self.option_pipe_borehole_radius.set_value)
        self.option_pipe_borehole_radius.change_event(self.option_pipe_borehole_radius_2.set_value)

        self.option_pipe_distance = FloatBox(
            category=self.category_pipe_data,
            label=translations.option_pipe_distance,
            default_value=0.04,
            decimal_number=4,
            minimal_value=0,
            maximal_value=10000,
            step=0.001,
        )
        self.option_pipe_roughness = FloatBox(
            category=self.category_pipe_data,
            label=translations.option_pipe_roughness,
            default_value=0.000_001,
            decimal_number=7,
            minimal_value=0,
            maximal_value=10000,
            step=0.000001,
        )

        # add dependency
        self.option_method_rb_calc.add_link_2_show(self.category_pipe_data, on_index=1)

        # set update events
        self.option_pipe_number.change_event(self.check_distance_between_pipes)
        self.option_pipe_outer_radius.change_event(self.check_distance_between_pipes)
        self.option_pipe_distance.change_event(self.check_distance_between_pipes)

        self.option_pipe_number.change_event(self.update_borehole)
        self.option_pipe_outer_radius.change_event(self.update_borehole)
        self.option_pipe_inner_radius.change_event(self.update_borehole)
        self.option_pipe_borehole_radius.change_event(self.update_borehole)
        self.option_pipe_distance.change_event(self.update_borehole)

        self.page_borehole_resistance.add_function_called_if_button_clicked(self.update_borehole)

        # create categories
        #create_category_constant_rb()
        #create_category_fluid_data()
        #create_category_pipe_data()

        # def create_page_thermal_demands():
        # create page
        self.page_thermal = Page(translations.page_thermal, "Thermal\ndemands", "Thermal.svg")
        self.page_borehole_resistance.set_next_page(self.page_thermal)
        self.page_thermal.set_previous_page(self.page_borefield)

        def create_category_select_datafile():
            self.category_select_file = Category(page=self.page_thermal, label=translations.category_select_file)

            self.option_seperator_csv = ButtonBox(label=translations.option_seperator_csv, default_index=0,
                                                  entries=['Semicolon ";"', 'Comma ","'],
                                                  category=self.category_select_file)
            self.option_decimal_csv = ButtonBox(label=translations.option_decimal_csv, default_index=0,
                                                entries=['Point "."', 'Comma ","'],
                                                category=self.category_select_file)
            self.option_filename = FileNameBox(
                category=self.category_select_file,
                label=translations.option_filename,
                default_value=f'{FOLDER.joinpath("Examples/hourly_profile.csv")}',
                dialog_text="Choose csv file",
                error_text="no file selected",
            )
            self.option_filename.check_active = True
            self.option_column = ButtonBox(label=translations.option_column, default_index=0,
                                           entries=["1 column", "2 columns"], category=self.category_select_file)
            self.option_heating_column = ListBox(category=self.category_select_file, label=translations.option_heating_column, default_index=0, entries=[])
            self.option_cooling_column = ListBox(category=self.category_select_file, label=translations.option_cooling_column, default_index=0, entries=[])
            self.option_single_column = ListBox(category=self.category_select_file, label=translations.option_single_column, default_index=0, entries=[])

            self.option_unit_data = ButtonBox(label=translations.option_unit_data, default_index=1, entries=["W", "kW", "MW"],
                                              category=self.category_select_file)

            self.hint_press_load = Hint(hint=self.translations.hint_press_load,
                                        category=self.category_select_file,
                                        warning=True)

            self.button_load_csv = FunctionButton(category=self.category_select_file, button_text=translations.button_load_csv, icon="Download.svg")

            # add dependencies
            self.option_filename.add_aim_option_2_be_set_for_check(self.aim_optimize)
            self.option_filename.add_aim_option_2_be_set_for_check((self.option_method_size_depth, 2))

            self.option_column.add_link_2_show(self.option_heating_column, on_index=1)
            self.option_heating_column.add_aim_option_2_be_set_for_check(self.aim_optimize)
            self.option_heating_column.add_aim_option_2_be_set_for_check((self.option_method_size_depth, 2))
            self.option_heating_column.add_aim_option_2_be_set_for_check((self.option_temperature_profile_hourly, 1))

            self.option_column.add_link_2_show(self.option_cooling_column, on_index=1)
            self.option_cooling_column.add_aim_option_2_be_set_for_check(self.aim_optimize)
            self.option_cooling_column.add_aim_option_2_be_set_for_check((self.option_method_size_depth, 2))
            self.option_cooling_column.add_aim_option_2_be_set_for_check((self.option_temperature_profile_hourly, 1))

            self.option_column.add_link_2_show(self.option_single_column, on_index=0)
            self.option_single_column.add_aim_option_2_be_set_for_check(self.aim_optimize)
            self.option_single_column.add_aim_option_2_be_set_for_check((self.option_method_size_depth, 2))
            self.option_single_column.add_aim_option_2_be_set_for_check((self.option_temperature_profile_hourly, 1))

            self.option_method_size_depth.add_link_2_show(self.button_load_csv, on_index=0)
            self.option_method_size_depth.add_link_2_show(self.button_load_csv, on_index=1)
            self.aim_temp_profile.add_link_2_show(self.button_load_csv)
            self.option_temperature_profile_hourly.add_link_2_show(self.button_load_csv, on_index=0)
            self.aim_req_depth.add_link_2_show(self.button_load_csv)

            self.option_method_size_depth.add_link_2_show(self.hint_press_load, on_index=0)
            self.option_method_size_depth.add_link_2_show(self.hint_press_load, on_index=1)
            self.aim_temp_profile.add_link_2_show(self.hint_press_load)
            self.option_temperature_profile_hourly.add_link_2_show(self.hint_press_load, on_index=0)
            self.aim_req_depth.add_link_2_show(self.hint_press_load)
            # self.aim_size_length.add_link_2_show(self.button_load_csv)

            # add change events
            self.option_seperator_csv.change_event(self.fun_update_combo_box_data_file)
            self.option_decimal_csv.change_event(self.fun_update_combo_box_data_file)
            self.option_filename.change_event(self.fun_update_combo_box_data_file)

            self.button_load_csv.change_event(self.fun_display_data)

        def create_category_th_demand():
            self.category_th_demand = Category(page=self.page_thermal, label=translations.category_th_demand)
            self.category_th_demand.activate_grid_layout(5)

            self.hint_none_1 = Hint(category=self.category_th_demand, hint="  ")
            self.hint_peak_heating = Hint(category=self.category_th_demand, hint=translations.hint_peak_heating)
            self.hint_peak_cooling = Hint(category=self.category_th_demand, hint=translations.hint_peak_cooling)
            self.hint_load_heating = Hint(category=self.category_th_demand, hint=translations.hint_load_heating)
            self.hint_load_cooling = Hint(category=self.category_th_demand, hint=translations.hint_load_cooling)

            self.hint_none_2 = Hint(category=self.category_th_demand, hint="  ")
            self.hint_peak_heating_unit = Hint(category=self.category_th_demand, hint="[kW]")
            self.hint_peak_cooling_unit = Hint(category=self.category_th_demand, hint="[kW]")
            self.hint_load_heating_unit = Hint(category=self.category_th_demand, hint="[kWh]")
            self.hint_load_cooling_unit = Hint(category=self.category_th_demand, hint="[kWh]")

            self.hint_jan = Hint(category=self.category_th_demand, hint=translations.hint_jan)
            self.option_hp_jan = FloatBox(
                category=self.category_th_demand, label="", default_value=160, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
            )
            self.option_cp_jan = FloatBox(
                category=self.category_th_demand, label="", default_value=0, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
            )
            self.option_hl_jan = FloatBox(
                category=self.category_th_demand,
                label="",
                default_value=46500,
                decimal_number=0,
                minimal_value=0,
                maximal_value=1_000_000_000,
                step=1,
            )
            self.option_cl_jan = FloatBox(
                category=self.category_th_demand,
                label="",
                default_value=4000,
                decimal_number=0,
                minimal_value=0,
                maximal_value=1_000_000_000,
                step=1,
            )
            self.hint_feb = Hint(category=self.category_th_demand, hint=translations.hint_feb)
            self.option_hp_feb = FloatBox(
                category=self.category_th_demand, label="", default_value=142, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
            )
            self.option_cp_feb = FloatBox(
                category=self.category_th_demand, label="", default_value=0, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
            )
            self.option_hl_feb = FloatBox(
                category=self.category_th_demand,
                label="",
                default_value=44400,
                decimal_number=0,
                minimal_value=0,
                maximal_value=1_000_000_000,
                step=1,
            )
            self.option_cl_feb = FloatBox(
                category=self.category_th_demand,
                label="",
                default_value=8000,
                decimal_number=0,
                minimal_value=0,
                maximal_value=1_000_000_000,
                step=1,
            )
            self.hint_mar = Hint(category=self.category_th_demand, hint=translations.hint_mar)
            self.option_hp_mar = FloatBox(
                category=self.category_th_demand, label="", default_value=102, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
            )
            self.option_cp_mar = FloatBox(
                category=self.category_th_demand, label="", default_value=34, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
            )
            self.option_hl_mar = FloatBox(
                category=self.category_th_demand,
                label="",
                default_value=37500,
                decimal_number=0,
                minimal_value=0,
                maximal_value=1_000_000_000,
                step=1,
            )
            self.option_cl_mar = FloatBox(
                category=self.category_th_demand,
                label="",
                default_value=8000,
                decimal_number=0,
                minimal_value=0,
                maximal_value=1_000_000_000,
                step=1,
            )
            self.hint_apr = Hint(category=self.category_th_demand, hint=translations.hint_apr)
            self.option_hp_apr = FloatBox(
                category=self.category_th_demand, label="", default_value=55, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
            )
            self.option_cp_apr = FloatBox(
                category=self.category_th_demand, label="", default_value=69, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
            )
            self.option_hl_apr = FloatBox(
                category=self.category_th_demand,
                label="",
                default_value=29700,
                decimal_number=0,
                minimal_value=0,
                maximal_value=1_000_000_000,
                step=1,
            )
            self.option_cl_apr = FloatBox(
                category=self.category_th_demand,
                label="",
                default_value=8000,
                decimal_number=0,
                minimal_value=0,
                maximal_value=1_000_000_000,
                step=1,
            )
            self.hint_may = Hint(category=self.category_th_demand, hint=translations.hint_may)
            self.option_hp_may = FloatBox(
                category=self.category_th_demand, label="", default_value=0, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
            )
            self.option_cp_may = FloatBox(
                category=self.category_th_demand, label="", default_value=133, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
            )
            self.option_hl_may = FloatBox(
                category=self.category_th_demand,
                label="",
                default_value=19200,
                decimal_number=0,
                minimal_value=0,
                maximal_value=1_000_000_000,
                step=1,
            )
            self.option_cl_may = FloatBox(
                category=self.category_th_demand,
                label="",
                default_value=12000,
                decimal_number=0,
                minimal_value=0,
                maximal_value=1_000_000_000,
                step=1,
            )
            self.hint_jun = Hint(category=self.category_th_demand, hint=translations.hint_jun)
            self.option_hp_jun = FloatBox(
                category=self.category_th_demand, label="", default_value=0, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
            )
            self.option_cp_jun = FloatBox(
                category=self.category_th_demand, label="", default_value=187, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
            )
            self.option_hl_jun = FloatBox(
                category=self.category_th_demand, label="", default_value=0, decimal_number=0, minimal_value=0, maximal_value=1_000_000_000, step=1
            )
            self.option_cl_jun = FloatBox(
                category=self.category_th_demand,
                label="",
                default_value=16000,
                decimal_number=0,
                minimal_value=0,
                maximal_value=1_000_000_000,
                step=1,
            )
            self.hint_jul = Hint(category=self.category_th_demand, hint=translations.hint_jul)
            self.option_hp_jul = FloatBox(
                category=self.category_th_demand, label="", default_value=0, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
            )
            self.option_cp_jul = FloatBox(
                category=self.category_th_demand, label="", default_value=213, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
            )
            self.option_hl_jul = FloatBox(
                category=self.category_th_demand, label="", default_value=0, decimal_number=0, minimal_value=0, maximal_value=1_000_000_000, step=1
            )
            self.option_cl_jul = FloatBox(
                category=self.category_th_demand,
                label="",
                default_value=32000,
                decimal_number=0,
                minimal_value=0,
                maximal_value=1_000_000_000,
                step=1,
            )
            self.hint_aug = Hint(category=self.category_th_demand, hint=translations.hint_aug)
            self.option_hp_aug = FloatBox(
                category=self.category_th_demand, label="", default_value=0, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
            )
            self.option_cp_aug = FloatBox(
                category=self.category_th_demand, label="", default_value=240, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
            )
            self.option_hl_aug = FloatBox(
                category=self.category_th_demand, label="", default_value=0, decimal_number=0, minimal_value=0, maximal_value=1_000_000_000, step=1
            )
            self.option_cl_aug = FloatBox(
                category=self.category_th_demand,
                label="",
                default_value=32000,
                decimal_number=0,
                minimal_value=0,
                maximal_value=1_000_000_000,
                step=1,
            )
            self.hint_sep = Hint(category=self.category_th_demand, hint=translations.hint_sep)
            self.option_hp_sep = FloatBox(
                category=self.category_th_demand, label="", default_value=40.4, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
            )
            self.option_cp_sep = FloatBox(
                category=self.category_th_demand, label="", default_value=160, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
            )
            self.option_hl_sep = FloatBox(
                category=self.category_th_demand,
                label="",
                default_value=18300,
                decimal_number=0,
                minimal_value=0,
                maximal_value=1_000_000_000,
                step=1,
            )
            self.option_cl_sep = FloatBox(
                category=self.category_th_demand,
                label="",
                default_value=16000,
                decimal_number=0,
                minimal_value=0,
                maximal_value=1_000_000_000,
                step=1,
            )
            self.hint_oct = Hint(category=self.category_th_demand, hint=translations.hint_oct)
            self.option_hp_oct = FloatBox(
                category=self.category_th_demand, label="", default_value=85, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
            )
            self.option_cp_oct = FloatBox(
                category=self.category_th_demand, label="", default_value=37, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
            )
            self.option_hl_oct = FloatBox(
                category=self.category_th_demand,
                label="",
                default_value=26100,
                decimal_number=0,
                minimal_value=0,
                maximal_value=1_000_000_000,
                step=1,
            )
            self.option_cl_oct = FloatBox(
                category=self.category_th_demand,
                label="",
                default_value=12000,
                decimal_number=0,
                minimal_value=0,
                maximal_value=1_000_000_000,
                step=1,
            )
            self.hint_nov = Hint(category=self.category_th_demand, hint=translations.hint_nov)
            self.option_hp_nov = FloatBox(
                category=self.category_th_demand, label="", default_value=119, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
            )
            self.option_cp_nov = FloatBox(
                category=self.category_th_demand, label="", default_value=0, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
            )
            self.option_hl_nov = FloatBox(
                category=self.category_th_demand,
                label="",
                default_value=35100,
                decimal_number=0,
                minimal_value=0,
                maximal_value=1_000_000_000,
                step=1,
            )
            self.option_cl_nov = FloatBox(
                category=self.category_th_demand,
                label="",
                default_value=8000,
                decimal_number=0,
                minimal_value=0,
                maximal_value=1_000_000_000,
                step=1,
            )
            self.hint_dec = Hint(category=self.category_th_demand, hint=translations.hint_dec)
            self.option_hp_dec = FloatBox(
                category=self.category_th_demand, label="", default_value=136, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
            )
            self.option_cp_dec = FloatBox(
                category=self.category_th_demand, label="", default_value=0, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
            )
            self.option_hl_dec = FloatBox(
                category=self.category_th_demand,
                label="",
                default_value=43200,
                decimal_number=0,
                minimal_value=0,
                maximal_value=1_000_000_000,
                step=1,
            )
            self.option_cl_dec = FloatBox(
                category=self.category_th_demand,
                label="",
                default_value=4000,
                decimal_number=0,
                minimal_value=0,
                maximal_value=1_000_000_000,
                step=1,
            )

            # add dependencies
            self.option_method_size_depth.add_link_2_show(self.category_th_demand, on_index=0)
            self.option_method_size_depth.add_link_2_show(self.category_th_demand, on_index=1)
            self.option_temperature_profile_hourly.add_link_2_show(self.category_th_demand, on_index=0)

            self.aim_temp_profile.add_link_2_show(self.category_th_demand)
            self.aim_req_depth.add_link_2_show(self.category_th_demand)
            # self.aim_size_length.add_link_2_show(self.category_th_demand)

        def create_category_building_demand():
            self.category_demand_building_or_geo =\
                Category(page=self.page_thermal, label=self.translations.category_demand_building_or_geo)
            self.geo_load = ButtonBox(label=self.translations.geo_load, default_index=0,
                                      entries=[" goethermal ", " building "],
                                      category=self.category_demand_building_or_geo)
            self.SCOP = FloatBox(
                category=self.category_demand_building_or_geo,
                label=self.translations.SCOP,
                default_value=4,
                decimal_number=2,
                minimal_value=1,
                maximal_value=50,
                step=0.1,
            )
            self.SEER = FloatBox(
                category=self.category_demand_building_or_geo,
                label=self.translations.SEER,
                default_value=3,
                decimal_number=2,
                minimal_value=1,
                maximal_value=50,
                step=0.1,
            )

            # add dependencies
            self.aim_optimize.add_link_2_show(self.SCOP)
            self.aim_optimize.add_link_2_show(self.SEER)
            self.geo_load.add_link_2_show(self.SCOP, 1)
            self.geo_load.add_link_2_show(self.SEER, 1)
            self.aim_req_depth.add_link_2_show(self.geo_load)
            self.aim_temp_profile.add_link_2_show(self.geo_load)

        # create categories
        create_category_select_datafile()
        create_category_building_demand()
        create_category_th_demand()

        def create_page_results():

            self.create_results_page()

            def create_category_numerical_results():
                self.numerical_results = Category(page=self.page_result, label=translations.numerical_results)

                self.result_text_depth = ResultText(translations.result_text_depth, category=self.numerical_results, prefix="Depth: ", suffix="m")
                self.result_text_depth.text_to_be_shown("Borefield", "H")
                self.result_text_depth.function_to_convert_to_text(lambda x: round(x, 2))

                self.result_Rb_calculated = ResultText(translations.result_Rb_calculated, category=self.numerical_results,
                                                       prefix="Equivalent borehole thermal resistance: ", suffix="Wm/K")
                self.result_Rb_calculated.text_to_be_shown("Borefield", "Rb")
                self.result_Rb_calculated.function_to_convert_to_text(lambda x: round(x, 4))

                self.result_Reynolds = ResultText(self.translations.result_Reynolds,
                                                       category=self.numerical_results,
                                                       prefix="Reynolds number: ", suffix="")
                self.result_Reynolds.text_to_be_shown("Borefield", "Re")
                self.result_Reynolds.function_to_convert_to_text(lambda x: round(x, 0))

                self.results_ground_temperature = ResultText(translations.results_ground_temperature, category=self.numerical_results,
                                                             prefix="Average ground temperature: ", suffix=" deg C")
                self.results_ground_temperature.text_to_be_shown("Borefield", "_Tg")
                self.results_ground_temperature.function_to_convert_to_text(lambda x: round(x, 2))

                self.results_heating_load = ResultText(translations.results_heating_load, category=self.numerical_results,
                                                       prefix="Heating load on the borefield: ", suffix=" kWh")
                self.results_heating_peak_geo = ResultText(self.translations.results_heating_peak_geo,
                                                       category=self.numerical_results,
                                                       prefix="with a peak of: ", suffix=" kW")
                self.results_heating_peak_geo.text_to_be_shown("Borefield", "hourly_heating_load_building")
                self.results_heating_peak_geo.function_to_convert_to_text(lambda x: round(max(x), 2))
                self.results_heating_load.text_to_be_shown("Borefield", "hourly_heating_load_building")
                self.results_heating_load.function_to_convert_to_text(lambda x: round(sum(x), 0))
                self.results_heating_load_percentage = ResultText(translations.results_heating_load_percentage, category=self.numerical_results,
                                                                  prefix="This is ", suffix="% of the heating load")
                self.results_heating_load_percentage.text_to_be_shown("Borefield", "_percentage_heating")
                self.results_heating_load_percentage.function_to_convert_to_text(lambda x: round(x, 2))
                self.results_heating_ext = ResultText(translations.results_heating_ext, category=self.numerical_results,
                                                      prefix="heating load external: ", suffix=" kWh")
                self.results_heating_ext.text_to_be_shown("Borefield", "hourly_heating_load_external")
                self.results_heating_ext.function_to_convert_to_text(lambda x: round(sum(x), 0))
                self.results_heating_peak = ResultText(translations.results_heating_peak, category=self.numerical_results,
                                                       prefix="with a peak of: ", suffix=" kW")
                self.results_heating_peak.text_to_be_shown("Borefield", "peak_heating_external")
                self.results_heating_peak.function_to_convert_to_text(lambda x: round(max(x), 2))

                self.results_cooling_load = ResultText(translations.results_cooling_load, category=self.numerical_results,
                                                       prefix="Cooling load on the borefield: ", suffix=" kWh")
                self.results_cooling_peak_geo = ResultText(self.translations.results_cooling_peak_geo,
                                                       category=self.numerical_results,
                                                       prefix="with a peak of: ", suffix=" kW")
                self.results_cooling_peak_geo.text_to_be_shown("Borefield", "hourly_cooling_load_building")
                self.results_cooling_peak_geo.function_to_convert_to_text(lambda x: round(max(x), 2))
                self.results_cooling_load.text_to_be_shown("Borefield", "hourly_cooling_load_building")
                self.results_cooling_load.function_to_convert_to_text(lambda x: round(sum(x), 0))
                self.results_cooling_load_percentage = ResultText(translations.results_cooling_load_percentage, category=self.numerical_results,
                                                                  prefix="This is ", suffix="% of the cooling load")
                self.results_cooling_load_percentage.text_to_be_shown("Borefield", "_percentage_cooling")
                self.results_cooling_load_percentage.function_to_convert_to_text(lambda x: round(x, 2))
                self.results_cooling_ext = ResultText(translations.results_cooling_ext, category=self.numerical_results,
                                                      prefix="cooling load external: ", suffix=" kWh")
                self.results_cooling_ext.text_to_be_shown("Borefield", "hourly_cooling_load_external")
                self.results_cooling_ext.function_to_convert_to_text(lambda x: round(sum(x), 0))
                self.results_cooling_peak = ResultText(translations.results_cooling_peak, category=self.numerical_results,
                                                       prefix="with a peak of: ", suffix=" kW")
                self.results_cooling_peak.text_to_be_shown("Borefield", "peak_cooling_external")
                self.results_cooling_peak.function_to_convert_to_text(lambda x: round(max(x), 2))

                self.max_temp = ResultText(translations.max_temp, category=self.numerical_results,
                                           prefix="The maximum average fluid temperature is ", suffix=" deg C")
                self.max_temp.text_to_be_shown("Borefield", "results_peak_cooling")
                self.max_temp.function_to_convert_to_text(lambda x: round(max(x), 2))
                self.min_temp = ResultText(translations.min_temp, category=self.numerical_results,
                                           prefix="The minimum average fluid temperature is ", suffix=" deg C")
                self.min_temp.text_to_be_shown("Borefield", "results_peak_heating")
                self.min_temp.function_to_convert_to_text(lambda x: round(min(x), 2))

                # add dependency
                self.option_method_temp_gradient.add_link_2_show(self.results_ground_temperature, on_index=1)
                self.option_method_rb_calc.add_link_2_show(self.result_Rb_calculated, on_index=1)
                self.option_method_rb_calc.add_link_2_show(self.result_Reynolds, on_index=1)
                self.aim_req_depth.add_link_2_show(self.result_text_depth)

                self.aim_optimize.add_link_2_show(self.results_heating_ext)
                self.aim_optimize.add_link_2_show(self.results_heating_peak_geo)
                self.aim_optimize.add_link_2_show(self.results_heating_load_percentage)
                self.aim_optimize.add_link_2_show(self.results_heating_load)
                self.aim_optimize.add_link_2_show(self.results_heating_peak)
                self.aim_optimize.add_link_2_show(self.results_cooling_ext)
                self.aim_optimize.add_link_2_show(self.results_cooling_load_percentage)
                self.aim_optimize.add_link_2_show(self.results_cooling_load)
                self.aim_optimize.add_link_2_show(self.results_cooling_peak)
                self.aim_optimize.add_link_2_show(self.results_cooling_peak_geo)

                self.aim_temp_profile.add_link_2_show(self.max_temp)
                self.aim_temp_profile.add_link_2_show(self.min_temp)

            def create_figure_temperature_profile():
                self.figure_temperature_profile = ResultFigure(label=translations.figure_temperature_profile,
                                                               page=self.page_result)

                self.figure_temperature_profile.fig_to_be_shown(class_name="Borefield",
                                                                function_name="print_temperature_profile")

                self.legend_figure_temperature_profile = FigureOption(category=self.figure_temperature_profile,
                                                                      label=translations.legend_figure_temperature_profile,
                                                                      param="legend",
                                                                      default=0,
                                                                      entries=["No", "Yes"],
                                                                      entries_values=[False, True])

                self.hourly_figure_temperature_profile = FigureOption(category=self.figure_temperature_profile,
                                                                      label=translations.hourly_figure_temperature_profile,
                                                                      param="plot_hourly",
                                                                      default=0,
                                                                      entries=["No", "Yes"],
                                                                      entries_values=[False, True])

                # add dependencies
                self.option_temperature_profile_hourly.add_link_2_show(self.hourly_figure_temperature_profile, on_index=1)
                self.aim_optimize.add_link_2_show(self.hourly_figure_temperature_profile)
                self.option_method_size_depth.add_link_2_show(self.hourly_figure_temperature_profile, on_index=2)

            def create_figure_load_duration():
                self.figure_load_duration = ResultFigure(label=translations.figure_load_duration,
                                                         page=self.page_result)

                self.figure_load_duration.fig_to_be_shown(class_name="Borefield",
                                                          function_name="plot_load_duration")

                self.legend_figure_load_duration = FigureOption(category=self.figure_load_duration,
                                                                label=translations.legend_figure_load_duration,
                                                                param="legend",
                                                                default=0,
                                                                entries=["No", "Yes"],
                                                                entries_values=[False, True])

                # add dependencies
                self.option_method_size_depth.add_link_2_show(self.figure_load_duration, on_index=2)
                self.option_temperature_profile_hourly.add_link_2_show(self.figure_load_duration, on_index=1)
                self.aim_optimize.add_link_2_show(self.figure_load_duration)

            # create categories
            create_category_numerical_results()
            create_figure_temperature_profile()
            create_figure_load_duration()



        #################################################################################################################
        #                                                                                                               #
        # CREATE PAGES                                                                                                  #
        #                                                                                                               #
        #################################################################################################################

        #create_page_aim()
        #create_page_options()
        #create_page_borehole()
        #create_page_borehole_resistance()
        #create_page_thermal_demands()
        create_page_results()
        self.create_settings_page()

        # general settings
        self.create_lists()

    def check_distance_between_pipes(self) -> None:
        """
        This function calculates and sets the minimal and maximal distance between the U pipes
        and the center of the borehole.

        Returns
        -------
        None
        """
        if self.option_pipe_distance.is_hidden():
            return
        n_u: int = self.option_pipe_number.get_value()  # get number of U pipes
        if n_u == 0:
            return
        r_borehole: float = self.option_pipe_borehole_radius.get_value()  # get borehole radius
        r_outer_pipe: float = self.option_pipe_outer_radius.get_value()  # get outer pipe radius
        distance_max: float = r_borehole - r_outer_pipe  # calculate maximal distance between pipe and center
        alpha: float = pi / n_u  # determine equal angle between pipes
        # determine minimal distance between pipe and center if number of pipes is bigger than one else set to half
        # borehole radius
        distance_min: float = r_outer_pipe / sin(alpha / 2) + 0.001  # add 1mm for safety
        # set minimal and maximal value for pipe distance
        self.option_pipe_distance.widget.blockSignals(True)
        self.option_pipe_distance.widget.setMinimum(distance_min)
        self.option_pipe_distance.widget.setMaximum(distance_max)
        self.option_pipe_distance.widget.blockSignals(False)

    def update_borehole(self) -> None:
        """
        This function plots the position of the pipe in the borehole.
        This figure can be either left or right of the options in the category

        Returns
        -------
        None
        """
        frame = self.category_pipe_data.graphic_left if self.category_pipe_data.graphic_left is not None else \
            self.category_pipe_data.graphic_right
        if isinstance(frame, QtW.QGraphicsView):
            # import all that is needed
            # get variables from gui
            number_of_pipes = self.option_pipe_number.get_value()
            r_out = self.option_pipe_outer_radius.get_value() * 10
            r_in = self.option_pipe_inner_radius.get_value() * 10
            r_bore = max(self.option_pipe_borehole_radius.get_value() * 10, 0.001)
            dis = self.option_pipe_distance.get_value() * 10
            # calculate scale from graphic view size
            max_l = min(frame.width(), frame.height())
            scale = max_l / r_bore / 1.25  # leave 25 % space
            # set colors
            dark_color = array(globs.DARK.replace('rgb(', '').replace(')', '').split(','), dtype=int64)
            white_color = array(globs.WHITE.replace('rgb(', '').replace(')', '').split(','), dtype=int64)
            light_color = array(globs.LIGHT.replace('rgb(', '').replace(')', '').split(','), dtype=int64)
            grey_color = array(globs.GREY.replace('rgb(', '').replace(')', '').split(','), dtype=int64)
            blue_color = QtG.QColor(dark_color[0], dark_color[1], dark_color[2])
            blue_light = QtG.QColor(light_color[0], light_color[1], light_color[2])
            white_color = QtG.QColor(white_color[0], white_color[1], white_color[2])
            grey = QtG.QColor(grey_color[0], grey_color[1], grey_color[2])
            brown = QtG.QColor(145, 124, 111)
            # create graphic scene if not exits otherwise get scene and delete items
            if frame.scene() is None:
                scene = QtW.QGraphicsScene()  # parent=self.central_widget)
                frame.setScene(scene)
                frame.setBackgroundBrush(brown)
            else:
                scene = frame.scene()
                scene.clear()
            # create borehole circle in grey wih no border
            circle = QtW.QGraphicsEllipseItem(-r_bore * scale / 2, -r_bore * scale / 2, r_bore * scale, r_bore * scale)
            circle.setPen(QtG.QPen(grey, 0))
            circle.setBrush(grey)
            scene.addItem(circle)
            # calculate pipe position and draw circle (white for outer pipe and blue for inner pipe)
            dt: float = pi / float(number_of_pipes)
            for i in range(number_of_pipes):
                pos_1 = dis * cos(2.0 * i * dt + pi) / 2
                pos_2 = dis * sin(2.0 * i * dt + pi) / 2
                circle = QtW.QGraphicsEllipseItem((pos_1 - r_out / 2) * scale, (pos_2 - r_out / 2) * scale, r_out * scale, r_out * scale)
                circle.setPen(white_color)
                circle.setBrush(white_color)
                scene.addItem(circle)
                circle = QtW.QGraphicsEllipseItem((pos_1 - r_in / 2) * scale, (pos_2 - r_in / 2) * scale, r_in * scale, r_in * scale)
                circle.setPen(blue_color)
                circle.setBrush(blue_color)
                scene.addItem(circle)
                pos_1 = dis * cos(2.0 * i * dt + pi + dt) / 2
                pos_2 = dis * sin(2.0 * i * dt + pi + dt) / 2
                circle = QtW.QGraphicsEllipseItem((pos_1 - r_out / 2) * scale, (pos_2 - r_out / 2) * scale, r_out * scale, r_out * scale)
                circle.setPen(white_color)
                circle.setBrush(white_color)
                scene.addItem(circle)
                circle = QtW.QGraphicsEllipseItem((pos_1 - r_in / 2) * scale, (pos_2 - r_in / 2) * scale, r_in * scale, r_in * scale)
                circle.setPen(blue_light)
                circle.setBrush(blue_light)
                scene.addItem(circle)

    def update_borefield(self) -> None:
        """
        This function plots the position of the pipe in the borehole.
        This figure can be either left or right of the options in the category

        Returns
        -------
        None
        """
        frame = self.category_borefield.graphic_left if self.category_borefield.graphic_left is not None else self.category_borefield.graphic_right
        if not isinstance(frame, QtW.QGraphicsView):
            return
        def draw_borefield():
            # import all that is needed
            # get variables from gui
            spacing_width = self.option_spacing.get_value()
            spacing_length = self.option_spacing_length.get_value()
            r_bore = min(spacing_length, spacing_width) / 4
            width = self.option_width.get_value()
            length = self.option_length.get_value()
            # calculate scale from graphic view size
            max_l = min(frame.width(), frame.height())
            max_size = max(spacing_length * length, spacing_width * width, 1)
            scale = max_l / max_size / 1.25  # leave 25 % space
            # set colors
            white_color = array(globs.WHITE.replace('rgb(', '').replace(')', '').split(','), dtype=int64)
            white_color = QtG.QColor(white_color[0], white_color[1], white_color[2])
            brown = QtG.QColor(145, 124, 111)
            # create graphic scene if not exits otherwise get scene and delete items
            if frame.scene() is None:
                scene = QtW.QGraphicsScene()  # parent=self.central_widget)
                frame.setScene(scene)
                frame.setBackgroundBrush(brown)
            else:
                scene = frame.scene()
                scene.clear()
            # create borehole circle in grey wih no border
            width = (width - 1) * spacing_width * scale / 2 + r_bore * scale / 2
            length = (length - 1) * spacing_length * scale / 2 + r_bore * scale / 2

            if self.aim_rect.widget.isChecked():
                coordinates = [(w * spacing_width * scale - width, l * spacing_length * scale - length) for w in range(self.option_width.get_value()) for l in range(self.option_length.get_value())]
            elif self.aim_Box_shaped.widget.isChecked():
                coordinates = [(w * spacing_width * scale - width, l * spacing_length * scale - length) for w in range(self.option_width.get_value()) if not(
                        0 < w < self.option_width.get_value() - 1) for l in range(self.option_length.get_value())]
                coordinates += [(w * spacing_width * scale - width, l * spacing_length * scale - length) for w in range(self.option_width.get_value()) for l
                                in range(self.option_length.get_value())  if not (0 < l < self.option_length.get_value() - 1) ]
            elif self.aim_L_shaped.widget.isChecked():
                l = self.option_length.get_value() - 1
                coordinates = [(w * spacing_width * scale - width, l * spacing_length * scale - length) for w in range(self.option_width.get_value())]
                w = 0
                coordinates += [(w * spacing_width * scale - width, l * spacing_length * scale - length) for l in range(self.option_length.get_value())]
            elif self.aim_U_shaped.widget.isChecked():
                l = self.option_length.get_value() - 1
                coordinates = [(w * spacing_width * scale - width, l * spacing_length * scale - length) for w in range(self.option_width.get_value())]
                w = 0
                coordinates += [(w * spacing_width * scale - width, l * spacing_length * scale - length) for l in range(self.option_length.get_value())]
                w = self.option_width.get_value() - 1
                coordinates += [(w * spacing_width * scale - width, l * spacing_length * scale - length) for l in range(self.option_length.get_value())]
            elif self.aim_circle.widget.isChecked():
                r_bore = 2 * self.option_borefield_radius.get_value() * pi / self.option_number_circle_boreholes.get_value() / 4
                scale = max_l / (2 * self.option_borefield_radius.get_value() + r_bore) / 1.25  # leave 25 % space
                angle = 2 * pi / self.option_number_circle_boreholes.get_value()
                radius = self.option_borefield_radius.get_value()*scale
                coordinates = [(sin(angle * n) * radius - r_bore * scale / 2, cos(angle * n) * radius - r_bore * scale / 2) for n in range(self.option_number_circle_boreholes.get_value())]

            else:
                coordinates = [(x,y) for x,y,_,_,_ in self.custom_borefield.get_value()]
                min_x = min(x for x, _ in coordinates)
                max_x = max(x for x, _ in coordinates)
                min_y = min(y for _, y in coordinates)
                max_y = max(y for _, y in coordinates)
                r_bore = max(min(max_x - min_x, max_y - min_y), 1) / len(coordinates)
                dist_x = max_x + min_x
                dist_y = max_y + min_y
                scale = max_l / (max(max_x - min_x, max_y - min_y, 5) + r_bore) / 1.25
                coordinates = [((x - dist_x / 2 - r_bore / 2) * scale, (y - dist_y /2 - r_bore / 2) * scale) for x, y in coordinates]

            for x, y in coordinates:
                circle = QtW.QGraphicsEllipseItem(x, y, r_bore * scale, r_bore * scale)
                circle.setPen(QtG.QPen(white_color, 0))
                circle.setBrush(white_color)
                scene.addItem(circle)

        QtC.QTimer.singleShot(5, draw_borefield)

    def fun_update_combo_box_data_file(self, filename: str) -> None:
        """
        This function updates the combo box of the file selector when a new file is selected.

        Parameters
        ----------
        filename : str
            Location of the file

        Returns
        -------
        None
        """
        filename = (self.option_filename.get_value() if not isinstance(filename, str) else filename) if filename is not None else self.option_filename.get_value()

        # get decimal and column seperator
        sep: str = ";" if self.option_seperator_csv.get_value() == 0 else ","
        dec: str = "." if self.option_decimal_csv.get_value() == 0 else ","

        # raise error if seperator is decimal point
        if dec == sep:
            logging.warning("Please make sure the seperator and decimal point are different.")
            return

        if filename == "":
            logging.info(self.translations.no_file_selected[self.option_language.get_value()[0]])
            return
        # try to read CSV-File
        try:
            data: pd_DataFrame = pd_read_csv(filename, sep=sep, decimal=dec)
        except FileNotFoundError:
            logging.warning(self.translations.no_file_selected[self.option_language.get_value()[0]])
            return
        except PermissionError:  # pragma: no cover
            logging.warning(self.translations.no_file_selected[self.option_language.get_value()[0]])
            return
        # get data column names to set them to comboBoxes
        columns = data.columns
        # clear comboBoxes and add column names
        self.option_heating_column.widget.clear()
        self.option_cooling_column.widget.clear()
        self.option_single_column.widget.clear()
        self.option_heating_column.widget.addItems(columns)
        self.option_cooling_column.widget.addItems(columns)
        self.option_single_column.widget.addItems(columns)
        # set column selection mode to 2 columns if more than one line exists
        self.option_column.set_value(1 if len(columns) > 0 else 0)
        self.option_cooling_column.widget.setCurrentIndex(len(columns) - 1)

    def fun_display_data(self) -> None:
        """
        This function loads the data and displays it (in a monthly format) in the GUI.

        Returns
        -------
        None
        """
        try:
            data_unit = self.option_unit_data.get_value()

            loaded_data = load_data_GUI(filename=self.option_filename.get_value(),
                                        thermal_demand=self.option_column.get_value(),
                                        heating_load_column=self.option_heating_column.get_value()[1],
                                        cooling_load_column=self.option_cooling_column.get_value()[1],
                                        combined=self.option_single_column.get_value()[1],
                                        sep=";" if self.option_seperator_csv.get_value() == 0 else ",",
                                        dec="." if self.option_decimal_csv.get_value() == 0 else ",",
                                        fac=0.001 if data_unit == 0 else 1 if data_unit == 1 else 1000)

            peak_heating, peak_cooling, heating_load, cooling_load = loaded_data
            # set heating loads to double spinBoxes
            self.option_hl_jan.set_value(heating_load[0])
            self.option_hl_feb.set_value(heating_load[1])
            self.option_hl_mar.set_value(heating_load[2])
            self.option_hl_apr.set_value(heating_load[3])
            self.option_hl_may.set_value(heating_load[4])
            self.option_hl_jun.set_value(heating_load[5])
            self.option_hl_jul.set_value(heating_load[6])
            self.option_hl_aug.set_value(heating_load[7])
            self.option_hl_sep.set_value(heating_load[8])
            self.option_hl_oct.set_value(heating_load[9])
            self.option_hl_nov.set_value(heating_load[10])
            self.option_hl_dec.set_value(heating_load[11])
            # set cooling loads to double spinBoxes
            self.option_cl_jan.set_value(cooling_load[0])
            self.option_cl_feb.set_value(cooling_load[1])
            self.option_cl_mar.set_value(cooling_load[2])
            self.option_cl_apr.set_value(cooling_load[3])
            self.option_cl_may.set_value(cooling_load[4])
            self.option_cl_jun.set_value(cooling_load[5])
            self.option_cl_jul.set_value(cooling_load[6])
            self.option_cl_aug.set_value(cooling_load[7])
            self.option_cl_sep.set_value(cooling_load[8])
            self.option_cl_oct.set_value(cooling_load[9])
            self.option_cl_nov.set_value(cooling_load[10])
            self.option_cl_dec.set_value(cooling_load[11])
            # set peak heating load to double spinBoxes
            self.option_hp_jan.set_value(peak_heating[0])
            self.option_hp_feb.set_value(peak_heating[1])
            self.option_hp_mar.set_value(peak_heating[2])
            self.option_hp_apr.set_value(peak_heating[3])
            self.option_hp_may.set_value(peak_heating[4])
            self.option_hp_jun.set_value(peak_heating[5])
            self.option_hp_jul.set_value(peak_heating[6])
            self.option_hp_aug.set_value(peak_heating[7])
            self.option_hp_sep.set_value(peak_heating[8])
            self.option_hp_oct.set_value(peak_heating[9])
            self.option_hp_nov.set_value(peak_heating[10])
            self.option_hp_dec.set_value(peak_heating[11])
            # set peak cooling load to double spinBoxes
            self.option_cp_jan.set_value(peak_cooling[0])
            self.option_cp_feb.set_value(peak_cooling[1])
            self.option_cp_mar.set_value(peak_cooling[2])
            self.option_cp_apr.set_value(peak_cooling[3])
            self.option_cp_may.set_value(peak_cooling[4])
            self.option_cp_jun.set_value(peak_cooling[5])
            self.option_cp_jul.set_value(peak_cooling[6])
            self.option_cp_aug.set_value(peak_cooling[7])
            self.option_cp_sep.set_value(peak_cooling[8])
            self.option_cp_oct.set_value(peak_cooling[9])
            self.option_cp_nov.set_value(peak_cooling[10])
            self.option_cp_dec.set_value(peak_cooling[11])
        # raise error and display error massage in status bar
        except FileNotFoundError:
            logging.error(self.translations.no_file_selected[self.option_language.get_value()[0]])
            return
        except IndexError:
            logging.error(self.translations.ValueError[self.option_language.get_value()[0]])
            return
        except KeyError:
            logging.error(self.translations.ColumnError[self.option_language.get_value()[0]])
            return

    def fun_import_borefield(self):
        filename = self.borefield_file.get_value()
        if not Path(filename).exists() or filename == "":
            logging.error(self.translations.no_file_selected[self.option_language.get_value()[0]])
            return
        sep = "," if self.option_seperator_borefield.get_value() == 1 else ";" if self.option_seperator_borefield.get_value() == 0 else "\t"
        dec = "." if self.option_decimal_borefield.get_value() == 0 else ','
        if filename.endswith(".csv"):
            data = pd.read_csv(filename, sep=sep, decimal=dec)
            self.custom_borefield.set_value(data.values)
            return
        with open(filename, "r") as f:
            data = f.readlines()
        data = [[float(val.replace(dec, ".")) for val in line.split(sep)] for line in data[1:]]
        self.custom_borefield.set_value(data)


def show_option_on_multiple_aims(first_aims: list[Aim], second_aims: list[Aim], option: Option):
    def show_hide():
        first = any(aim.widget.isChecked() for aim in first_aims)
        second = any(aim.widget.isChecked() for aim in second_aims)
        if first and second:
            option.show()
            return
        option.hide()

    QtC.QTimer.singleShot(5, show_hide)
