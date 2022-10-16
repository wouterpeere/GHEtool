from typing import List, Optional, Tuple, Union

from PySide6.QtWidgets import QStatusBar, QWidget
from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsScene
from PySide6.QtWidgets import QGraphicsView as QtWidgets_QGraphicsView
from PySide6.QtGui import QPen
from PySide6.QtGui import QColor
from numpy import cos, sin, array, int64, float64

from GHEtool.gui.gui_classes import (Aim, ButtonBox, Category, FloatBox, FileNameBox, FunctionButton, Hint, IntBox, ListBox, Option, Page)
from GHEtool.gui.translation_class import Translations
from GHEtool.gui.gui_base_class import DARK, GREY, LIGHT, WHITE

from math import cos, pi, sin, tan

from pandas import DataFrame as pd_DataFrame, read_csv as pd_read_csv


class GuiStructure:
    def __init__(self, default_parent: QWidget, status_bar: QStatusBar):
        # set default parent for the class variables to avoid widgets creation not in the main window
        Page.default_parent = default_parent
        Aim.default_parent = default_parent
        Category.default_parent = default_parent
        Option.default_parent = default_parent
        Hint.default_parent = default_parent
        FunctionButton.default_parent = default_parent
        self.status_bar = status_bar
        self.no_file_selected = 'No file Selected'
        # start coding of structure
        self.page_aim = Page(name="Aim of simulation", button_name="Aim", icon=":/icons/icons/Aim_Inv.svg")

        self.aim_temp_profile = Aim(page=self.page_aim, label="Determine temperature profile", icon=":/icons/icons/Temp_Profile.svg")
        self.aim_req_depth = Aim(page=self.page_aim, label="Determine required depth", icon=":/icons/icons/Depth_determination.svg")
        self.aim_size_length = Aim(page=self.page_aim, label="Size borefield by length and width", icon=":/icons/icons/Size_Length.svg")
        self.aim_optimize = Aim(page=self.page_aim, label="Optimize load profile", icon=":/icons/icons/Optimize_Profile.svg")

        self.page_options = Page("Options", "Options", ":/icons/icons/Options.svg")
        self.page_aim.set_next_page(self.page_options)
        self.page_options.set_previous_page(self.page_aim)

        # self.category_import_data = Category(page=self.page_options, label="Import data format")
        # self.aim_temp_profile.add_link_2_show(self.category_import_data)
        # self.aim_req_depth.add_link_2_show(self.category_import_data)
        # self.aim_size_length.add_link_2_show(self.category_import_data)
        #
        # self.option_data = ButtonBox(
        #     category=self.category_import_data, label="Data format:", default_index=0, entries=["monthly data", "hourly data"]
        # )

        self.category_calculation = Category(page=self.page_options, label="Calculation options")

        self.option_method_size_depth = ButtonBox(
            category=self.category_calculation, label="Method for size borehole depth :", default_index=0, entries=[" L2 ", " L3 ", "  L4  "]
        )
        self.aim_req_depth.add_link_2_show(self.option_method_size_depth)
        self.option_method_size_length = ButtonBox(
            category=self.category_calculation, label="Method for size width and length :", default_index=0, entries=[" L2 ", " L3 "]
        )
        self.aim_size_length.add_link_2_show(self.option_method_size_length)
        self.option_method_temp_gradient = ButtonBox(
            category=self.category_calculation,
            label="Should a temperature gradient over depth be considered?:",
            default_index=0,
            entries=[" no ", " yes  "],
        )
        self.option_method_rb_calc = ButtonBox(
            category=self.category_calculation,
            label="Borehole resistance calculation method:",
            default_index=0,
            entries=[" constant ", " dynamic "],
        )

        self.page_borehole = Page("Borehole and earth", "Borehole\nand earth", ":/icons/icons/Borehole.png")
        self.page_options.set_next_page(self.page_borehole)
        self.page_borehole.set_previous_page(self.page_options)

        self.category_earth = Category(
            page=self.page_borehole,
            label="Earth properties",
        )

        self.option_conductivity = FloatBox(
            category=self.category_earth,
            label="Conductivity of the soil [W/mK]: ",
            default_value=1.5,
            decimal_number=3,
            minimal_value=0.1,
            maximal_value=10,
            step=0.1,
        )

        self.option_heat_capacity = FloatBox(
            category=self.category_earth,
            label="Ground volumetric heat capacity [kJ / m³ K]: ",
            default_value=2400,
            decimal_number=1,
            minimal_value=1,
            maximal_value=100000,
            step=100,
        )
        self.option_ground_temp = FloatBox(
            category=self.category_earth,
            label="Ground temperature at infinity [°C]: ",
            default_value=12,
            decimal_number=2,
            minimal_value=-273.15,
            maximal_value=100,
            step=0.1,
        )
        self.option_ground_temp_gradient = FloatBox(
            category=self.category_earth,
            label="Ground surface temperature [°C]: ",
            default_value=10,
            decimal_number=2,
            minimal_value=-273.15,
            maximal_value=100,
            step=0.1,
        )
        self.option_temp_gradient = FloatBox(
            category=self.category_earth,
            label="Temperature gradient [K/100m]: ",
            default_value=2,
            decimal_number=3,
            minimal_value=-273.15,
            maximal_value=100,
            step=0.1,
        )
        self.option_method_temp_gradient.add_link_2_show(self.option_ground_temp_gradient, on_index=1)
        self.option_method_temp_gradient.add_link_2_show(self.option_temp_gradient, on_index=1)
        self.option_method_temp_gradient.add_link_2_show(self.option_ground_temp, on_index=0)

        self.category_borehole = Category(
            page=self.page_borehole,
            label="Borehole properties",
        )

        self.option_depth = FloatBox(
            category=self.category_borehole,
            label="Borehole depth [m]: ",
            default_value=100,
            decimal_number=2,
            minimal_value=0,
            maximal_value=500,
            step=1,
        )

        self.aim_temp_profile.add_link_2_show(self.option_depth)
        self.aim_optimize.add_link_2_show(self.option_depth)
        self.option_max_depth = FloatBox(
            category=self.category_borehole,
            label="Maximal borehole depth [m]: ",
            default_value=150,
            decimal_number=2,
            minimal_value=0,
            maximal_value=500,
            step=1,
        )
        self.aim_size_length.add_link_2_show(self.option_max_depth)
        self.option_spacing = FloatBox(
            category=self.category_borehole,
            label="Borehole spacing [m]: ",
            default_value=6,
            decimal_number=2,
            minimal_value=1,
            maximal_value=99,
            step=0.1,
        )

        self.aim_temp_profile.add_link_2_show(self.option_spacing)
        self.aim_req_depth.add_link_2_show(self.option_spacing)
        self.aim_optimize.add_link_2_show(self.option_spacing)
        self.option_min_spacing = FloatBox(
            category=self.category_borehole,
            label="Minimal borehole spacing [m]: ",
            default_value=3,
            decimal_number=2,
            minimal_value=1,
            maximal_value=99,
            step=0.1,
        )

        self.aim_size_length.add_link_2_show(self.option_min_spacing)
        self.option_max_spacing = FloatBox(
            category=self.category_borehole,
            label="Maximal borehole spacing [m]: ",
            default_value=9,
            decimal_number=2,
            minimal_value=1,
            maximal_value=99,
            step=0.1,
        )

        self.aim_size_length.add_link_2_show(self.option_max_spacing)
        self.option_width = IntBox(
            category=self.category_borehole, label="Width of rectangular field [#]: ", default_value=9, minimal_value=1, maximal_value=40
        )

        self.aim_temp_profile.add_link_2_show(self.option_width)
        self.aim_req_depth.add_link_2_show(self.option_width)
        self.aim_optimize.add_link_2_show(self.option_width)
        self.option_length = IntBox(
            category=self.category_borehole, label="Length of rectangular field [#]: ", default_value=12, minimal_value=1, maximal_value=40
        )

        self.aim_temp_profile.add_link_2_show(self.option_length)
        self.aim_req_depth.add_link_2_show(self.option_length)
        self.aim_optimize.add_link_2_show(self.option_length)
        self.option_max_width = FloatBox(
            category=self.category_borehole,
            label="Maximal width of rectangular field [m]: ",
            default_value=160,
            decimal_number=2,
            minimal_value=1,
            maximal_value=1000,
            step=1,
        )
        self.aim_size_length.add_link_2_show(self.option_max_width)
        self.option_max_length = FloatBox(
            category=self.category_borehole,
            label="Maximal length of rectangular field [m]: ",
            default_value=150,
            decimal_number=2,
            minimal_value=1,
            maximal_value=1000,
            step=1,
        )
        self.aim_size_length.add_link_2_show(self.option_max_length)

        self.option_pipe_depth = FloatBox(
            category=self.category_borehole,
            label="Burial depth [m]: ",
            default_value=1,
            decimal_number=1,
            minimal_value=0,
            maximal_value=10000,
            step=0.1,
        )

        self.option_pipe_borehole_radius = FloatBox(
            category=self.category_borehole,
            label="Borehole radius [m]: ",
            default_value=0.075,
            decimal_number=4,
            minimal_value=0,
            maximal_value=10000,
            step=0.001,
        )
        self.option_pipe_borehole_radius.change_event(self.check_distance_between_pipes)

        self.category_temperatures = Category(page=self.page_borehole, label="Temperature constraints and simulation period")

        self.option_min_temp = FloatBox(
            category=self.category_temperatures,
            label="Minimal temperature [°C]: ",
            default_value=0,
            decimal_number=2,
            minimal_value=-273.15,
            maximal_value=100,
            step=0.1,
        )
        self.option_max_temp = FloatBox(
            category=self.category_temperatures,
            label="Maximal temperature [°C]: ",
            default_value=16,
            decimal_number=2,
            minimal_value=-273.15,
            maximal_value=100,
            step=0.1,
        )

        self.option_simu_period = IntBox(
            category=self.category_temperatures, label="Simulation period [yrs]: ", default_value=20, minimal_value=1, maximal_value=100
        )


        self.page_borehole_resistance = Page("Equivalent borehole resistance", "Borehole\nresistance", ":/icons/icons/Resistance.png")
        self.page_borehole.set_next_page(self.page_borehole_resistance)
        self.page_borehole_resistance.set_previous_page(self.page_borehole)

        self.category_constant_rb = Category(page=self.page_borehole_resistance, label="Constant equivalent borehole resistance")

        self.option_constant_rb = FloatBox(
            category=self.category_constant_rb,
            label="Equivalent borehole resistance [mK/W]: ",
            default_value=0.0150,
            decimal_number=4,
            minimal_value=0,
            maximal_value=100,
            step=0.01,
        )
        self.option_method_rb_calc.add_link_2_show(self.category_constant_rb, on_index=0)

        self.category_fluid_data = Category(page=self.page_borehole_resistance, label="Fluid data")
        self.option_method_rb_calc.add_link_2_show(self.category_fluid_data, on_index=1)
        self.option_method_rb_calc.add_link_2_show(self.category_fluid_data, on_index=2)

        self.option_fluid_conductivity = FloatBox(
            category=self.category_fluid_data,
            label="Thermal conductivity [W/mK]: ",
            default_value=0.5,
            decimal_number=3,
            minimal_value=0,
            maximal_value=100,
            step=0.1,
        )
        self.option_fluid_density = FloatBox(
            category=self.category_fluid_data,
            label="Density [kg/m³]: ",
            default_value=1000,
            decimal_number=1,
            minimal_value=0,
            maximal_value=10000000,
            step=100,
        )
        self.option_fluid_capacity = FloatBox(
            category=self.category_fluid_data,
            label="Thermal capacity [J/kg K]: ",
            default_value=4182,
            decimal_number=1,
            minimal_value=0,
            maximal_value=10000000,
            step=100,
        )
        self.option_fluid_viscosity = FloatBox(
            category=self.category_fluid_data,
            label="Dynamic viscosity [Pa s]:",
            default_value=0.001,
            decimal_number=6,
            minimal_value=0,
            maximal_value=1,
            step=0.0001,
        )

        self.option_fluid_mass_flow = FloatBox(
            category=self.category_fluid_data,
            label="Mass flow rate [kg/s]: ",
            default_value=0.5,
            decimal_number=3,
            minimal_value=0,
            maximal_value=100000,
            step=0.1,
        )

        self.category_pipe_data = Category(page=self.page_borehole_resistance, label="Pipe data")
        self.category_pipe_data.activate_graphic_left()
        self.option_method_rb_calc.add_link_2_show(self.category_pipe_data, on_index=1)

        self.option_pipe_number = IntBox(
            category=self.category_pipe_data, label="Number of pipes [#]: ", default_value=2, minimal_value=1, maximal_value=99
        )
        self.option_pipe_grout_conductivity = FloatBox(
            category=self.category_pipe_data,
            label="Grout thermal conductivity [W/mK]: ",
            default_value=1.5,
            decimal_number=3,
            minimal_value=0,
            maximal_value=10000,
            step=0.1,
        )
        self.option_pipe_conductivity = FloatBox(
            category=self.category_pipe_data,
            label="Pipe thermal conductivity [W/mK]: ",
            default_value=0.42,
            decimal_number=3,
            minimal_value=0,
            maximal_value=10000,
            step=0.1,
        )
        self.option_pipe_inner_radius = FloatBox(
            category=self.category_pipe_data,
            label="Inner pipe radius [m]: ",
            default_value=0.02,
            decimal_number=4,
            minimal_value=0,
            maximal_value=10000,
            step=0.001,
        )
        self.option_pipe_outer_radius = FloatBox(
            category=self.category_pipe_data,
            label="Outer pipe radius [m]: ",
            default_value=0.022,
            decimal_number=4,
            minimal_value=0,
            maximal_value=10000,
            step=0.001,
        )
        self.option_pipe_outer_radius.change_event(self.option_pipe_inner_radius.widget.setMaximum)
        self.option_pipe_inner_radius.change_event(self.option_pipe_outer_radius.widget.setMinimum)

        self.option_pipe_distance = FloatBox(
            category=self.category_pipe_data,
            label="Distance of pipe until center [m]: ",
            default_value=0.04,
            decimal_number=4,
            minimal_value=0,
            maximal_value=10000,
            step=0.001,
        )
        self.option_pipe_roughness = FloatBox(
            category=self.category_pipe_data,
            label="Pipe roughness [m]: ",
            default_value=0.000_001,
            decimal_number=7,
            minimal_value=0,
            maximal_value=10000,
            step=0.000001,
        )

        self.option_pipe_number.change_event(self.check_distance_between_pipes)
        self.option_pipe_outer_radius.change_event(self.check_distance_between_pipes)
        self.option_pipe_distance.change_event(self.check_distance_between_pipes)

        self.option_pipe_number.change_event(self.update_borehole)
        self.option_pipe_outer_radius.change_event(self.update_borehole)
        self.option_pipe_inner_radius.change_event(self.update_borehole)
        self.option_pipe_borehole_radius.change_event(self.update_borehole)
        self.option_pipe_distance.change_event(self.update_borehole)

        self.page_borehole_resistance.add_function_called_if_button_clicked(self.update_borehole)

        self.page_thermal = Page("Thermal demands", "Thermal\ndemands", ":/icons/icons/Thermal.svg")
        self.page_borehole_resistance.set_next_page(self.page_thermal)
        self.page_thermal.set_previous_page(self.page_borehole)

        self.category_select_file = Category(page=self.page_thermal, label="Select data file")

        self.option_seperator_csv = ButtonBox(
            category=self.category_select_file, label="Seperator in CSV-file:", default_index=0, entries=['Semicolon ";"', 'Comma ","']
        )
        self.option_decimal_csv = ButtonBox(
            category=self.category_select_file, label="Decimal sign in CSV-file:", default_index=0, entries=['Point "."', 'Comma ","']
        )
        self.option_filename = FileNameBox(
            
            category=self.category_select_file,
            label="Filename: ",
            default_value="",
            dialog_text="Choose csv file",
            error_text="error",
            status_bar=status_bar,
        )
        self.option_filename.add_aim_option_2_be_set_for_check(self.aim_optimize)
        self.option_filename.add_aim_option_2_be_set_for_check((self.option_method_size_depth, 2))
        self.option_column = ButtonBox(
            category=self.category_select_file,
            label="Thermal demand in one or two columns: ",
            default_index=0,
            entries=["1 column", "2 columns"],
        )
        self.option_heating_column = ListBox(category=self.category_select_file, label="Heating load line: ", default_index=0, entries=[])
        self.option_column.add_link_2_show(self.option_heating_column, on_index=1)
        self.option_heating_column.add_aim_option_2_be_set_for_check(self.aim_optimize)
        self.option_heating_column.add_aim_option_2_be_set_for_check((self.option_method_size_depth, 2))
        self.option_cooling_column = ListBox(category=self.category_select_file, label="Cooling load line: ", default_index=0, entries=[])
        self.option_column.add_link_2_show(self.option_cooling_column, on_index=1)
        self.option_cooling_column.add_aim_option_2_be_set_for_check(self.aim_optimize)
        self.option_cooling_column.add_aim_option_2_be_set_for_check((self.option_method_size_depth, 2))
        self.option_single_column = ListBox(category=self.category_select_file, label="Load line: ", default_index=0, entries=[])
        self.option_column.add_link_2_show(self.option_single_column, on_index=0)
        self.option_single_column.add_aim_option_2_be_set_for_check(self.aim_optimize)
        self.option_single_column.add_aim_option_2_be_set_for_check((self.option_method_size_depth, 2))

        self.option_unit_data = ButtonBox(category=self.category_select_file, label="Unit data: ", default_index=1, entries=["W", "kW", "MW"])

        self.button_load_csv = FunctionButton(category=self.category_select_file, button_text="Load", icon=":/icons/icons/Download.svg")
        self.option_method_size_depth.add_link_2_show(self.button_load_csv, on_index=0)
        self.option_method_size_depth.add_link_2_show(self.button_load_csv, on_index=1)
        self.aim_temp_profile.add_link_2_show(self.button_load_csv)
        self.aim_req_depth.add_link_2_show(self.button_load_csv)
        self.aim_size_length.add_link_2_show(self.button_load_csv)

        self.option_seperator_csv.change_event(self.fun_update_combo_box_data_file)
        self.option_decimal_csv.change_event(self.fun_update_combo_box_data_file)
        self.option_filename.change_event(self.fun_update_combo_box_data_file)

        self.button_load_csv.change_event(self.fun_display_data)

        self.category_th_demand = Category(page=self.page_thermal, label="Thermal demands")
        self.category_th_demand.activate_grid_layout(5)

        # visible when L2 or L3
        self.option_method_size_depth.add_link_2_show(self.category_th_demand, on_index=0)
        self.option_method_size_depth.add_link_2_show(self.category_th_demand, on_index=1)

        self.aim_temp_profile.add_link_2_show(self.category_th_demand)
        self.aim_req_depth.add_link_2_show(self.category_th_demand)
        self.aim_size_length.add_link_2_show(self.category_th_demand)

        self.hint_none_1 = Hint(category=self.category_th_demand, hint="  ")
        self.hint_peak_heating = Hint(category=self.category_th_demand, hint="Heating peak")
        self.hint_peak_cooling = Hint(category=self.category_th_demand, hint="Cooling peak")
        self.hint_load_heating = Hint(category=self.category_th_demand, hint="Heating load")
        self.hint_load_cooling = Hint(category=self.category_th_demand, hint="Cooling load")

        self.hint_none_2 = Hint(category=self.category_th_demand, hint="  ")
        self.hint_peak_heating_unit = Hint(category=self.category_th_demand, hint="[kW]")
        self.hint_peak_cooling_unit = Hint(category=self.category_th_demand, hint="[kW]")
        self.hint_load_heating_unit = Hint(category=self.category_th_demand, hint="[kWh]")
        self.hint_load_cooling_unit = Hint(category=self.category_th_demand, hint="[kWh]")

        self.hint_jan = Hint(category=self.category_th_demand, hint="January")
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
        self.hint_feb = Hint(category=self.category_th_demand, hint="February")
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
        self.hint_mar = Hint(category=self.category_th_demand, hint="March")
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
        self.hint_apr = Hint(category=self.category_th_demand, hint="April")
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
        self.hint_may = Hint(category=self.category_th_demand, hint="May")
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
        self.hint_jun = Hint(category=self.category_th_demand, hint="June")
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
        self.hint_jul = Hint(category=self.category_th_demand, hint="July")
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
        self.hint_aug = Hint(category=self.category_th_demand, hint="August")
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
        self.hint_sep = Hint(category=self.category_th_demand, hint="September")
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
        self.hint_oct = Hint(category=self.category_th_demand, hint="October")
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
        self.hint_nov = Hint(category=self.category_th_demand, hint="November")
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
        self.hint_dec = Hint(category=self.category_th_demand, hint="December")
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

        self.page_result = Page("Results", "Results", ":/icons/icons/Result.svg")

        self.category_options_result = Category(page=self.page_result, label="Options results")

        self.hint_depth = Hint(category=self.category_options_result, hint="Size")
        self.function_save_results = FunctionButton(
            category=self.category_options_result, button_text="Save results", icon=":/icons/icons/Save_Inv.svg"
        )
        self.function_save_figure = FunctionButton(
            category=self.category_options_result, button_text="Save figure", icon=":/icons/icons/Save_Inv.svg"
        )

        self.category_result_figure = Category(page=self.page_result, label="Figure")

        self.option_show_legend = ButtonBox(category=self.category_result_figure, label="Show legend?", default_index=0, entries=["no", "yes"])
        self.option_plot_hourly = ButtonBox(category=self.category_result_figure, label="plot hourly?", default_index=0, entries=["no", "yes"])

        self.option_method_size_depth.add_link_2_show(self.option_plot_hourly, on_index=2)

        self.page_settings = Page("Settings", "Settings", ":/icons/icons/Settings.svg")

        self.category_language = Category(page=self.page_settings, label="Language")

        self.option_language = ListBox(category=self.category_language, label="Language: ", default_index=0, entries=[])

        self.category_save_scenario = Category(page=self.page_settings, label="Scenario saving settings")

        self.option_auto_saving = ButtonBox(
            category=self.category_save_scenario, label="Use automatic saving?:", default_index=0, entries=[" no ", " yes "]
        )
        self.hint_saving = Hint(
            category=self.category_save_scenario,
            hint="If Auto saving is selected the scenario will automatically saved if a scenario"
            " is changed. Otherwise the scenario has to be saved with the Update scenario "
            "button in the upper left corner if the changes should not be lost. ",
        )

        self.list_of_aims: List[Tuple[Aim, str]] = [(getattr(self, name), name) for name in self.__dict__ if isinstance(getattr(self, name), Aim)]
        self.list_of_options: List[Tuple[Option, str]] = [(getattr(self, name), name) for name in self.__dict__ if isinstance(getattr(self, name), Option)]
        self.list_of_pages: List[Page] = [getattr(self, name) for name in self.__dict__ if isinstance(getattr(self, name), Page)]

        self.list_of_result_plot_options: List[Tuple[Union[Option, FunctionButton], str]] = [(self.option_show_legend, 'show_legend'),
                                                                                             (self.option_plot_hourly, 'change_plot_hourly')]

    def check_distance_between_pipes(self, *args) -> None:
        """
        calculate and set minimal and maximal distance between U pipes and center
        :return: None
        """
        if self.option_pipe_distance.is_hidden():
            return
        n_u: int = self.option_pipe_number.get_value()  # get number of U pipes
        if n_u == 0:
            return
        r_borehole: float = self.option_pipe_borehole_radius.get_value()  # get borehole radius
        r_outer_pipe: float = self.option_pipe_outer_radius.get_value()  # get outer pipe radius
        r_outer_pipe_max: float = r_borehole / (1 + 1 / sin(pi / (2 * n_u)))  # calculate maximal outer pipe radius(see Circle packing)
        distance_max: float = r_borehole - r_outer_pipe_max  # calculate maximal distance between pipe and center
        alpha: float = pi / n_u  # determine equal angle between pipes
        # determine minimal distance between pipe and center if number of pipes is bigger than one else set to half
        # borehole radius
        distance_min: float = 2 * r_outer_pipe * (cos((pi - alpha) / 2) + sin((pi - alpha) / 2) / tan(alpha)) if n_u > 1 else r_borehole / 2
        # set minimal and maximal value for pipe distance
        self.option_pipe_distance.widget.blockSignals(True)
        self.option_pipe_distance.widget.setMinimum(distance_min)
        self.option_pipe_distance.widget.setMaximum(distance_max)
        self.option_pipe_distance.widget.blockSignals(False)

    def update_borehole(self) -> None:
        """
        plots the position of the pipes in the borehole
        :return: None
        """
        if isinstance(self.category_pipe_data.graphic_left, QtWidgets_QGraphicsView):
            # import all that is needed
            # get variables from gui
            number_of_pipes = self.option_pipe_number.get_value()
            r_out = self.option_pipe_outer_radius.get_value() * 10
            r_in = self.option_pipe_inner_radius.get_value() * 10
            r_bore = max(self.option_pipe_borehole_radius.get_value() * 10, 0.001)
            dis = self.option_pipe_distance.get_value() * 10
            # calculate scale from graphic view size
            max_l = min(self.category_pipe_data.graphic_left.width(), self.category_pipe_data.graphic_left.height())
            scale = max_l / r_bore / 1.25  # leave 25 % space
            # set colors
            dark_color = array(DARK.replace('rgb(', '').replace(')', '').split(','), dtype=int64)
            white_color = array(WHITE.replace('rgb(', '').replace(')', '').split(','), dtype=int64)
            light_color = array(LIGHT.replace('rgb(', '').replace(')', '').split(','), dtype=int64)
            grey_color = array(GREY.replace('rgb(', '').replace(')', '').split(','), dtype=int64)
            blue_color = QColor(dark_color[0], dark_color[1], dark_color[2])
            blue_light = QColor(light_color[0], light_color[1], light_color[2])
            white_color = QColor(white_color[0], white_color[1], white_color[2])
            grey = QColor(grey_color[0], grey_color[1], grey_color[2])
            brown = QColor(145, 124, 111)
            # create graphic scene if not exits otherwise get scene and delete items
            if self.category_pipe_data.graphic_left.scene() is None:
                scene = QGraphicsScene()  # parent=self.central_widget)
                self.category_pipe_data.graphic_left.setScene(scene)
                self.category_pipe_data.graphic_left.setBackgroundBrush(brown)
            else:
                scene = self.category_pipe_data.graphic_left.scene()
                scene.clear()
            # create borehole circle in grey wih no border
            circle = QGraphicsEllipseItem(-r_bore * scale / 2, -r_bore * scale / 2, r_bore * scale, r_bore * scale)
            circle.setPen(QPen(grey, 0))
            circle.setBrush(grey)
            scene.addItem(circle)
            # calculate pipe position and draw circle (white for outer pipe and blue for inner pipe)
            dt: float = pi / float(number_of_pipes)
            for i in range(number_of_pipes):
                pos_1 = dis * cos(2.0 * i * dt + pi) / 2
                pos_2 = dis * sin(2.0 * i * dt + pi) / 2
                circle = QGraphicsEllipseItem((pos_1 - r_out / 2) * scale, (pos_2 - r_out / 2) * scale, r_out * scale, r_out * scale)
                circle.setPen(white_color)
                circle.setBrush(white_color)
                scene.addItem(circle)
                circle = QGraphicsEllipseItem((pos_1 - r_in / 2) * scale, (pos_2 - r_in / 2) * scale, r_in * scale, r_in * scale)
                circle.setPen(blue_color)
                circle.setBrush(blue_color)
                scene.addItem(circle)
                pos_1 = dis * cos(2.0 * i * dt + pi + dt) / 2
                pos_2 = dis * sin(2.0 * i * dt + pi + dt) / 2
                circle = QGraphicsEllipseItem((pos_1 - r_out / 2) * scale, (pos_2 - r_out / 2) * scale, r_out * scale, r_out * scale)
                circle.setPen(white_color)
                circle.setBrush(white_color)
                scene.addItem(circle)
                circle = QGraphicsEllipseItem((pos_1 - r_in / 2) * scale, (pos_2 - r_in / 2) * scale, r_in * scale, r_in * scale)
                circle.setPen(blue_light)
                circle.setBrush(blue_light)
                scene.addItem(circle)

    # TODO, one (or both) of the functions beneath should run if L4 is selected / or 
    def fun_update_combo_box_data_file(self, filename: str) -> None:
        """
        update comboBox if new data file is selected
        :param filename: filename of data file
        :return: None
        """
        if not isinstance(filename, str):
            return

        # get decimal and column seperator
        sep: str = ";" if self.option_seperator_csv.get_value() == 0 else ","
        dec: str = "." if self.option_decimal_csv.get_value() == 0 else ","
        # try to read CSV-File
        try:
            data: pd_DataFrame = pd_read_csv(filename, sep=sep, decimal=dec)
        except FileNotFoundError:
            self.status_bar.showMessage(self.no_file_selected[self.option_language.get_value()], 5000)
            return
        except PermissionError:
            self.status_bar.showMessage(self.no_file_selected[self.option_language.get_value()], 5000)
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
        self.option_column.set_value(0 if len(columns) > 0 else 1)

    def fun_display_data(self) -> None:
        """
        Load the Data to Display in the GUI
        :return: None
        """
        try:
            # get filename from line edit
            filename: str = self.option_filename.get_value()
            # raise error if no filename exists
            if filename == "":
                raise FileNotFoundError
            # get thermal demands index (1 = 2 columns, 2 = 1 column)
            thermal_demand: int = self.option_column.get_value()
            # Generate list of columns that have to be imported
            cols: list = []
            heating_load_column: str = self.option_heating_column.widget.currentText()
            if len(heating_load_column) >= 1:
                cols.append(heating_load_column)
            cooling_load_column: str = self.option_cooling_column.widget.currentText()
            if len(cooling_load_column) >= 1:
                cols.append(cooling_load_column)
            combined: str = self.option_single_column.widget.currentText()
            if len(combined) >= 1:
                cols.append(combined)
            date: str = "Date"

            sep: str = ";" if self.option_seperator_csv.get_value() == 0 else ","
            dec: str = "." if self.option_decimal_csv.get_value() == 0 else ","
            df2: pd_DataFrame = pd_read_csv(filename, usecols=cols, sep=sep, decimal=dec)
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
            df2.set_index(date, inplace=True)
            # resample data to hourly resolution if necessary
            df2 = df2 if dict_agg is None else df2.resample("H").agg(dict_agg)
            # ------------------- Calculate Section --------------------
            # Choose path between Single or Combined Column and create new columns
            if thermal_demand == 1:
                # Resample the Data for peakHeating and peakCooling
                df2.rename(columns={heating_load_column: "Heating Load", cooling_load_column: "Cooling Load"}, inplace=True)
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
            # resample to a monthly resolution as sum and maximal load
            df3: pd_DataFrame = df2.resample("M").agg({"Heating Load": "sum", "Cooling Load": "sum", "peak Heating": "max", "peak Cooling": "max"})
            # replace nan with 0
            df3 = df3.fillna(0)
            # ----------------------- Data Unit Section --------------------------
            # Get the Data Unit and set the label in the thermal Demand Box to follow
            data_unit = self.option_unit_data.get_value()
            # define unit factors
            fac = 0.001 if data_unit == 0 else 1 if data_unit == 1 else 1000
            # multiply dataframe with unit factor and collect data
            df3 = df3 * fac
            peak_heating = df3["peak Heating"]
            peak_cooling = df3["peak Cooling"]
            heating_load = df3["Heating Load"]
            cooling_load = df3["Cooling Load"]
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
            self.status_bar.showMessage(self.no_file_selected[self.option_language.get_value()], 5000)
        except IndexError:
            self.status_bar.showMessage(self.translations.ValueError[self.option_language.get_value()], 5000)
        except KeyError:
            self.status_bar.showMessage(self.translations.ColumnError[self.option_language.get_value()], 5000)

    def translate(self, index: int, translation: Translations):
        Page.next_label = translation.label_next[index]
        Page.previous_label = translation.label_previous[index]
        self.no_file_selected = translation.NoFileSelected[index]
        for name in [j for j in translation.__slots__ if hasattr(self, j)]:
            entry: Optional[Option, Hint, FunctionButton, Page, Category] = getattr(self, name)
            entry.set_text(getattr(translation, name)[index])
