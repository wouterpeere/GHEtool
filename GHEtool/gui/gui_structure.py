from typing import List, Optional, Tuple

from PySide6.QtWidgets import QStatusBar, QWidget

from GHEtool.gui.gui_classes import (Aim, ButtonBox, Category, FloatBox, FileNameBox, FunctionButton, Hint, IntBox, ListBox, Option, Page)
from GHEtool.gui.translation_class import Translations


class GuiStructure:
    def __init__(self, default_parent: QWidget, status_bar: QStatusBar):

        self.page_aim = Page(default_parent, "Aim of simulation", "Aim", ":/icons/icons/Aim_Inv.svg")

        self.aim_temp_profile = Aim(default_parent, page=self.page_aim, label="Determine temperature profile", icon=":/icons/icons/Options.svg")
        self.aim_req_depth = Aim(default_parent, page=self.page_aim, label="Determine required depth", icon=":/icons/icons/Depth_determination.svg")
        self.aim_size_length = Aim(default_parent, page=self.page_aim, label="Size borefield by length and width", icon=":/icons/icons/Size_Length.svg")
        self.aim_optimize = Aim(default_parent, page=self.page_aim, label="Optimize load profile", icon=":/icons/icons/Optimize_Profile.svg")

        self.page_options = Page(default_parent, "Options", "Options", ":/icons/icons/Options.svg")
        self.page_aim.set_next_page(self.page_options)
        self.page_options.set_previous_page(self.page_aim)

        self.category_import_data = Category(default_parent, page=self.page_options, label="Import data format")
        self.aim_temp_profile.add_linked_option(self.category_import_data)
        self.aim_req_depth.add_linked_option(self.category_import_data)
        self.aim_size_length.add_linked_option(self.category_import_data)

        self.option_data = ButtonBox(
            default_parent, category=self.category_import_data, label="Data format:", default_index=0, entries=[" monthly data ", " hourly data "]
        )

        self.category_calculation = Category(default_parent, page=self.page_options, label="Calculation options")

        self.option_method_size_depth = ButtonBox(
            default_parent, category=self.category_calculation, label="Method for size borehole depth :", default_index=0, entries=[" L2 ", " L3 ", "  L4  "]
        )
        self.aim_req_depth.add_linked_option(self.option_method_size_depth)
        self.option_method_size_length = ButtonBox(
            default_parent, category=self.category_calculation, label="Method for size width and length :", default_index=0, entries=[" L2 ", " L3 "]
        )
        self.aim_size_length.add_linked_option(self.option_method_size_length)
        self.option_method_temp_gradient = ButtonBox(
            default_parent,
            category=self.category_calculation,
            label="Should a temperature gradient over depth be considered?:",
            default_index=0,
            entries=[" no ", " yes  "],
        )
        self.option_method_rb_calc = ButtonBox(
            default_parent,
            category=self.category_calculation,
            label="Borehole resistance calculation method:",
            default_index=0,
            entries=[" constant ", " constant but unknown ", " flexibel during calculation "],
        )

        self.page_borehole = Page(default_parent, "Borehole and earth", "Borehole\nand earth", ":/icons/icons/Borehole.png")
        self.page_options.set_next_page(self.page_borehole)
        self.page_borehole.set_previous_page(self.page_options)

        self.category_borehole = Category(
            default_parent,
            page=self.page_borehole,
            label="Borehole and earth properties",
        )

        self.option_depth = FloatBox(
            default_parent,
            category=self.category_borehole,
            label="Borehole depth [m]: ",
            default_value=100,
            decimal_number=2,
            minimal_value=0,
            maximal_value=500,
            step=1,
        )
        self.aim_temp_profile.add_linked_option(self.option_depth)
        self.aim_optimize.add_linked_option(self.option_depth)
        self.option_max_depth = FloatBox(
            default_parent,
            category=self.category_borehole,
            label="Maximal borehole depth [m]: ",
            default_value=150,
            decimal_number=2,
            minimal_value=0,
            maximal_value=500,
            step=1,
        )
        self.aim_size_length.add_linked_option(self.option_max_depth)
        self.option_spacing = FloatBox(
            default_parent,
            category=self.category_borehole,
            label="Borehole spacing [m]: ",
            default_value=6,
            decimal_number=2,
            minimal_value=1,
            maximal_value=99,
            step=0.1,
        )
        self.aim_temp_profile.add_linked_option(self.option_spacing)
        self.aim_req_depth.add_linked_option(self.option_spacing)
        self.aim_optimize.add_linked_option(self.option_spacing)
        self.option_min_spacing = FloatBox(
            default_parent,
            category=self.category_borehole,
            label="Minimal borehole spacing [m]: ",
            default_value=3,
            decimal_number=2,
            minimal_value=1,
            maximal_value=99,
            step=0.1,
        )
        self.aim_size_length.add_linked_option(self.option_min_spacing)
        self.option_max_spacing = FloatBox(
            default_parent,
            category=self.category_borehole,
            label="Maximal borehole spacing [m]: ",
            default_value=9,
            decimal_number=2,
            minimal_value=1,
            maximal_value=99,
            step=0.1,
        )
        self.aim_size_length.add_linked_option(self.option_max_spacing)
        self.option_width = IntBox(
            default_parent, category=self.category_borehole, label="Width of rectangular field [#]: ", default_value=9, minimal_value=1, maximal_value=40
        )
        self.aim_temp_profile.add_linked_option(self.option_width)
        self.aim_req_depth.add_linked_option(self.option_width)
        self.aim_optimize.add_linked_option(self.option_width)
        self.option_length = IntBox(
            default_parent, category=self.category_borehole, label="Length of rectangular field [#]: ", default_value=12, minimal_value=1, maximal_value=40
        )
        self.aim_temp_profile.add_linked_option(self.option_width)
        self.aim_req_depth.add_linked_option(self.option_width)
        self.aim_optimize.add_linked_option(self.option_width)
        self.option_max_width = FloatBox(
            default_parent,
            category=self.category_borehole,
            label="Maximal width of rectangular field [m]: ",
            default_value=160,
            decimal_number=2,
            minimal_value=1,
            maximal_value=1000,
            step=1,
        )
        self.aim_size_length.add_linked_option(self.option_max_width)
        self.option_max_length = FloatBox(
            default_parent,
            category=self.category_borehole,
            label="Maximal length of rectangular field [m]: ",
            default_value=150,
            decimal_number=2,
            minimal_value=1,
            maximal_value=1000,
            step=1,
        )
        self.aim_size_length.add_linked_option(self.option_max_length)
        self.option_conductivity = FloatBox(
            default_parent,
            category=self.category_borehole,
            label="Conductivity of the soil [W/mK]: ",
            default_value=1.5,
            decimal_number=3,
            minimal_value=0.1,
            maximal_value=10,
            step=0.1,
        )
        self.option_heat_capacity = FloatBox(
            default_parent,
            category=self.category_borehole,
            label="Ground volumetric heat capacity [kJ / m³ K]: ",
            default_value=2400,
            decimal_number=1,
            minimal_value=1,
            maximal_value=100000,
            step=100,
        )

        self.hint_calc_time = Hint(
            default_parent,
            category=self.category_borehole,
            hint="With the selected values a customized bore field will be calculated. " "This will dramatically increase the calculation time.",
            warning=True,
        )

        self.category_temperatures = Category(default_parent, page=self.page_borehole, label="Temperature constraints and simulation period")

        self.option_ground_temp = FloatBox(
            default_parent,
            category=self.category_temperatures,
            label="Ground temperature at infinity [°C]: ",
            default_value=10,
            decimal_number=2,
            minimal_value=-273.15,
            maximal_value=100,
            step=0.1,
        )
        self.option_min_temp = FloatBox(
            default_parent,
            category=self.category_temperatures,
            label="Minimal temperature [°C]: ",
            default_value=0,
            decimal_number=2,
            minimal_value=-273.15,
            maximal_value=100,
            step=0.1,
        )
        self.option_max_temp = FloatBox(
            default_parent,
            category=self.category_temperatures,
            label="Maximal temperature [°C]: ",
            default_value=16,
            decimal_number=2,
            minimal_value=-273.15,
            maximal_value=100,
            step=0.1,
        )
        self.option_temp_gradient = FloatBox(
            default_parent,
            category=self.category_temperatures,
            label="Temperature gradient [K/100m]: ",
            default_value=2,
            decimal_number=3,
            minimal_value=-273.15,
            maximal_value=100,
            step=0.1,
        )
        self.option_simu_period = IntBox(
            default_parent, category=self.category_temperatures, label="Simulation period [yrs]: ", default_value=20, minimal_value=1, maximal_value=100
        )

        self.option_method_temp_gradient.add_linked_option(self.option_temp_gradient, 1)

        self.page_borehole_resistance = Page(default_parent, "Equivalent borehole resistance", "Borehole\nresistance", ":/icons/icons/Resistance.png")
        self.page_borehole.set_next_page(self.page_borehole_resistance)
        self.page_borehole_resistance.set_previous_page(self.page_borehole)

        self.category_constant_rb = Category(default_parent, page=self.page_borehole_resistance, label="Konstant equivalent borehole resistance")

        self.option_constant_rb = FloatBox(
            default_parent,
            category=self.category_constant_rb,
            label="Equivalent borehole resistance [mK/W]: ",
            default_value=0.0150,
            decimal_number=4,
            minimal_value=0,
            maximal_value=100,
            step=0.01,
        )
        self.option_method_rb_calc.add_linked_option(self.category_constant_rb, 0)

        self.category_fluid_data = Category(default_parent, page=self.page_borehole_resistance, label="Fluid data")
        self.option_method_rb_calc.add_linked_option(self.category_fluid_data, 1)
        self.option_method_rb_calc.add_linked_option(self.category_fluid_data, 2)

        self.option_fluid_conductivity = FloatBox(
            default_parent,
            category=self.category_fluid_data,
            label="Thermal conductivity [W/mK]: ",
            default_value=0.5,
            decimal_number=3,
            minimal_value=0,
            maximal_value=100,
            step=0.1,
        )
        self.option_fluid_density = FloatBox(
            default_parent,
            category=self.category_fluid_data,
            label="Density [kg/m³]: ",
            default_value=1000,
            decimal_number=1,
            minimal_value=0,
            maximal_value=10000000,
            step=100,
        )
        self.option_fluid_capacity = FloatBox(
            default_parent,
            category=self.category_fluid_data,
            label="Thermal capacity [J/kg K]: ",
            default_value=4182,
            decimal_number=1,
            minimal_value=0,
            maximal_value=10000000,
            step=100,
        )
        self.option_fluid_viscosity = FloatBox(
            default_parent,
            category=self.category_fluid_data,
            label="Dynamic viscosity [Pa s]:",
            default_value=0.001,
            decimal_number=6,
            minimal_value=0,
            maximal_value=1,
            step=0.0001,
        )

        self.option_fluid_mass_flow = FloatBox(
            default_parent,
            category=self.category_fluid_data,
            label="Mass flow rate [kg/s]: ",
            default_value=0.5,
            decimal_number=3,
            minimal_value=0,
            maximal_value=100000,
            step=0.1,
        )

        self.category_pipe_data = Category(default_parent, page=self.page_borehole_resistance, label="Pipe data")
        self.category_pipe_data.activate_graphic_left()
        self.option_method_rb_calc.add_linked_option(self.category_pipe_data, 1)
        self.option_method_rb_calc.add_linked_option(self.category_pipe_data, 2)

        self.option_pipe_number = IntBox(
            default_parent, category=self.category_pipe_data, label="Number of pipes [#]: ", default_value=2, minimal_value=1, maximal_value=99
        )
        self.option_pipe_grout_conductivity = FloatBox(
            default_parent,
            category=self.category_pipe_data,
            label="Grout thermal conductivity [W/mK]: ",
            default_value=1.5,
            decimal_number=3,
            minimal_value=0,
            maximal_value=10000,
            step=0.1,
        )
        self.option_pipe_conductivity = FloatBox(
            default_parent,
            category=self.category_pipe_data,
            label="Pipe thermal conductivity [W/mK]: ",
            default_value=0.42,
            decimal_number=3,
            minimal_value=0,
            maximal_value=10000,
            step=0.1,
        )
        self.option_pipe_inner_radius = FloatBox(
            default_parent,
            category=self.category_pipe_data,
            label="Inner pipe radius [m]: ",
            default_value=0.02,
            decimal_number=4,
            minimal_value=0,
            maximal_value=10000,
            step=0.001,
        )
        self.option_pipe_outer_radius = FloatBox(
            default_parent,
            category=self.category_pipe_data,
            label="Outer pipe radius [m]: ",
            default_value=0.022,
            decimal_number=4,
            minimal_value=0,
            maximal_value=10000,
            step=0.001,
        )
        self.option_pipe_borehole_radius = FloatBox(
            default_parent,
            category=self.category_pipe_data,
            label="Borehole radius [m]: ",
            default_value=0.075,
            decimal_number=4,
            minimal_value=0,
            maximal_value=10000,
            step=0.001,
        )
        self.option_pipe_distance = FloatBox(
            default_parent,
            category=self.category_pipe_data,
            label="Distance of pipe until center [m]: ",
            default_value=0.04,
            decimal_number=4,
            minimal_value=0,
            maximal_value=10000,
            step=0.001,
        )
        self.option_pipe_roughness = FloatBox(
            default_parent,
            category=self.category_pipe_data,
            label="Pipe roughness [m]: ",
            default_value=0.000_001,
            decimal_number=7,
            minimal_value=0,
            maximal_value=10000,
            step=0.000001,
        )
        self.option_pipe_depth = FloatBox(
            default_parent,
            category=self.category_pipe_data,
            label="Burial depth [m]: ",
            default_value=4,
            decimal_number=1,
            minimal_value=0,
            maximal_value=10000,
            step=0.1,
        )
        self.page_thermal = Page(default_parent, "Thermal demands", "Thermal\ndemands", ":/icons/icons/Thermal.svg")
        self.page_borehole_resistance.set_next_page(self.page_thermal)
        self.page_thermal.set_previous_page(self.page_borehole)

        self.category_select_file = Category(default_parent, page=self.page_thermal, label="Select data file")

        self.option_seperator_csv = ButtonBox(
            default_parent, category=self.category_select_file, label="Seperator in CSV-file:", default_index=0, entries=['Semicolon ";"', 'Comma ","']
        )
        self.option_decimal_csv = ButtonBox(
            default_parent, category=self.category_select_file, label="Decimal sign in CSV-file:", default_index=0, entries=['Point "."', 'Comma ","']
        )
        self.option_filename = FileNameBox(
            default_parent,
            category=self.category_select_file,
            label="Filename: ",
            default_value="",
            dialog_text="Choose csv file",
            error_text="error",
            status_bar=status_bar,
        )
        self.option_column = ButtonBox(
            default_parent,
            category=self.category_select_file,
            label="Thermal demand in one or two columns: ",
            default_index=0,
            entries=["1 column", "2 columns"],
        )
        self.option_heating_column = ListBox(default_parent, category=self.category_select_file, label="Heating load line: ", default_index=0, entries=[])
        self.option_cooling_column = ListBox(default_parent, category=self.category_select_file, label="Cooling load line: ", default_index=0, entries=[])
        self.option_single_column = ListBox(default_parent, category=self.category_select_file, label="Load line: ", default_index=0, entries=[])
        self.option_column.add_linked_option(self.option_single_column, 0)
        self.option_column.add_linked_option(self.option_heating_column, 1)
        self.option_column.add_linked_option(self.option_cooling_column, 1)
        self.option_unit_data = ButtonBox(default_parent, category=self.category_select_file, label="Unit data: ", default_index=1, entries=["W", "kW", "MW"])

        self.button_load_csv = FunctionButton(default_parent, category=self.category_select_file, button_text="Load", icon=":/icons/icons/Download.svg")
        self.option_data.add_linked_option(self.button_load_csv, 0)
        self.aim_temp_profile.add_linked_option(self.button_load_csv)
        self.aim_req_depth.add_linked_option(self.button_load_csv)
        self.aim_size_length.add_linked_option(self.button_load_csv)

        self.category_th_demand = Category(default_parent, page=self.page_thermal, label="Thermal demands")
        self.category_th_demand.activate_grid_layout(5)
        self.option_data.add_linked_option(self.category_th_demand, 0)
        self.aim_temp_profile.add_linked_option(self.category_th_demand)
        self.aim_req_depth.add_linked_option(self.category_th_demand)
        self.aim_size_length.add_linked_option(self.category_th_demand)

        self.hint_none_1 = Hint(default_parent, category=self.category_th_demand, hint="  ")
        self.hint_peak_heating = Hint(default_parent, category=self.category_th_demand, hint="Heating peak")
        self.hint_peak_cooling = Hint(default_parent, category=self.category_th_demand, hint="Cooling peak")
        self.hint_load_heating = Hint(default_parent, category=self.category_th_demand, hint="Heating load")
        self.hint_load_cooling = Hint(default_parent, category=self.category_th_demand, hint="Cooling load")

        self.hint_none_2 = Hint(default_parent, category=self.category_th_demand, hint="  ")
        self.hint_peak_heating_unit = Hint(default_parent, category=self.category_th_demand, hint="[kW]")
        self.hint_peak_cooling_unit = Hint(default_parent, category=self.category_th_demand, hint="[kW]")
        self.hint_load_heating_unit = Hint(default_parent, category=self.category_th_demand, hint="[kWh]")
        self.hint_load_cooling_unit = Hint(default_parent, category=self.category_th_demand, hint="[kWh]")

        self.hint_jan = Hint(default_parent, category=self.category_th_demand, hint="January")
        self.option_hp_jan = FloatBox(
            default_parent, category=self.category_th_demand, label="", default_value=160, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
        )
        self.option_cp_jan = FloatBox(
            default_parent, category=self.category_th_demand, label="", default_value=0, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
        )
        self.option_hl_jan = FloatBox(
            default_parent,
            category=self.category_th_demand,
            label="",
            default_value=46500,
            decimal_number=0,
            minimal_value=0,
            maximal_value=1_000_000_000,
            step=1,
        )
        self.option_cl_jan = FloatBox(
            default_parent,
            category=self.category_th_demand,
            label="",
            default_value=4000,
            decimal_number=0,
            minimal_value=0,
            maximal_value=1_000_000_000,
            step=1,
        )
        self.hint_feb = Hint(default_parent, category=self.category_th_demand, hint="February")
        self.option_hp_feb = FloatBox(
            default_parent, category=self.category_th_demand, label="", default_value=142, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
        )
        self.option_cp_feb = FloatBox(
            default_parent, category=self.category_th_demand, label="", default_value=0, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
        )
        self.option_hl_feb = FloatBox(
            default_parent,
            category=self.category_th_demand,
            label="",
            default_value=44400,
            decimal_number=0,
            minimal_value=0,
            maximal_value=1_000_000_000,
            step=1,
        )
        self.option_cl_feb = FloatBox(
            default_parent,
            category=self.category_th_demand,
            label="",
            default_value=8000,
            decimal_number=0,
            minimal_value=0,
            maximal_value=1_000_000_000,
            step=1,
        )
        self.hint_mar = Hint(default_parent, category=self.category_th_demand, hint="March")
        self.option_hp_mar = FloatBox(
            default_parent, category=self.category_th_demand, label="", default_value=102, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
        )
        self.option_cp_mar = FloatBox(
            default_parent, category=self.category_th_demand, label="", default_value=34, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
        )
        self.option_hl_mar = FloatBox(
            default_parent,
            category=self.category_th_demand,
            label="",
            default_value=37500,
            decimal_number=0,
            minimal_value=0,
            maximal_value=1_000_000_000,
            step=1,
        )
        self.option_cl_mar = FloatBox(
            default_parent,
            category=self.category_th_demand,
            label="",
            default_value=8000,
            decimal_number=0,
            minimal_value=0,
            maximal_value=1_000_000_000,
            step=1,
        )
        self.hint_apr = Hint(default_parent, category=self.category_th_demand, hint="April")
        self.option_hp_apr = FloatBox(
            default_parent, category=self.category_th_demand, label="", default_value=55, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
        )
        self.option_cp_apr = FloatBox(
            default_parent, category=self.category_th_demand, label="", default_value=69, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
        )
        self.option_hl_apr = FloatBox(
            default_parent,
            category=self.category_th_demand,
            label="",
            default_value=29700,
            decimal_number=0,
            minimal_value=0,
            maximal_value=1_000_000_000,
            step=1,
        )
        self.option_cl_apr = FloatBox(
            default_parent,
            category=self.category_th_demand,
            label="",
            default_value=8000,
            decimal_number=0,
            minimal_value=0,
            maximal_value=1_000_000_000,
            step=1,
        )
        self.hint_may = Hint(default_parent, category=self.category_th_demand, hint="May")
        self.option_hp_may = FloatBox(
            default_parent, category=self.category_th_demand, label="", default_value=0, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
        )
        self.option_cp_may = FloatBox(
            default_parent, category=self.category_th_demand, label="", default_value=133, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
        )
        self.option_hl_may = FloatBox(
            default_parent,
            category=self.category_th_demand,
            label="",
            default_value=19200,
            decimal_number=0,
            minimal_value=0,
            maximal_value=1_000_000_000,
            step=1,
        )
        self.option_cl_may = FloatBox(
            default_parent,
            category=self.category_th_demand,
            label="",
            default_value=12000,
            decimal_number=0,
            minimal_value=0,
            maximal_value=1_000_000_000,
            step=1,
        )
        self.hint_jun = Hint(default_parent, category=self.category_th_demand, hint="June")
        self.option_hp_jun = FloatBox(
            default_parent, category=self.category_th_demand, label="", default_value=0, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
        )
        self.option_cp_jun = FloatBox(
            default_parent, category=self.category_th_demand, label="", default_value=187, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
        )
        self.option_hl_jun = FloatBox(
            default_parent, category=self.category_th_demand, label="", default_value=0, decimal_number=0, minimal_value=0, maximal_value=1_000_000_000, step=1
        )
        self.option_cl_jun = FloatBox(
            default_parent,
            category=self.category_th_demand,
            label="",
            default_value=16000,
            decimal_number=0,
            minimal_value=0,
            maximal_value=1_000_000_000,
            step=1,
        )
        self.hint_jul = Hint(default_parent, category=self.category_th_demand, hint="July")
        self.option_hp_jul = FloatBox(
            default_parent, category=self.category_th_demand, label="", default_value=0, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
        )
        self.option_cp_jul = FloatBox(
            default_parent, category=self.category_th_demand, label="", default_value=213, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
        )
        self.option_hl_jul = FloatBox(
            default_parent, category=self.category_th_demand, label="", default_value=0, decimal_number=0, minimal_value=0, maximal_value=1_000_000_000, step=1
        )
        self.option_cl_jul = FloatBox(
            default_parent,
            category=self.category_th_demand,
            label="",
            default_value=32000,
            decimal_number=0,
            minimal_value=0,
            maximal_value=1_000_000_000,
            step=1,
        )
        self.hint_aug = Hint(default_parent, category=self.category_th_demand, hint="August")
        self.option_hp_aug = FloatBox(
            default_parent, category=self.category_th_demand, label="", default_value=0, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
        )
        self.option_cp_aug = FloatBox(
            default_parent, category=self.category_th_demand, label="", default_value=240, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
        )
        self.option_hl_aug = FloatBox(
            default_parent, category=self.category_th_demand, label="", default_value=0, decimal_number=0, minimal_value=0, maximal_value=1_000_000_000, step=1
        )
        self.option_cl_aug = FloatBox(
            default_parent,
            category=self.category_th_demand,
            label="",
            default_value=32000,
            decimal_number=0,
            minimal_value=0,
            maximal_value=1_000_000_000,
            step=1,
        )
        self.hint_sep = Hint(default_parent, category=self.category_th_demand, hint="September")
        self.option_hp_sep = FloatBox(
            default_parent, category=self.category_th_demand, label="", default_value=40.4, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
        )
        self.option_cp_sep = FloatBox(
            default_parent, category=self.category_th_demand, label="", default_value=160, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
        )
        self.option_hl_sep = FloatBox(
            default_parent,
            category=self.category_th_demand,
            label="",
            default_value=18300,
            decimal_number=0,
            minimal_value=0,
            maximal_value=1_000_000_000,
            step=1,
        )
        self.option_cl_sep = FloatBox(
            default_parent,
            category=self.category_th_demand,
            label="",
            default_value=16000,
            decimal_number=0,
            minimal_value=0,
            maximal_value=1_000_000_000,
            step=1,
        )
        self.hint_oct = Hint(default_parent, category=self.category_th_demand, hint="October")
        self.option_hp_oct = FloatBox(
            default_parent, category=self.category_th_demand, label="", default_value=85, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
        )
        self.option_cp_oct = FloatBox(
            default_parent, category=self.category_th_demand, label="", default_value=37, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
        )
        self.option_hl_oct = FloatBox(
            default_parent,
            category=self.category_th_demand,
            label="",
            default_value=26100,
            decimal_number=0,
            minimal_value=0,
            maximal_value=1_000_000_000,
            step=1,
        )
        self.option_cl_oct = FloatBox(
            default_parent,
            category=self.category_th_demand,
            label="",
            default_value=12000,
            decimal_number=0,
            minimal_value=0,
            maximal_value=1_000_000_000,
            step=1,
        )
        self.hint_nov = Hint(default_parent, category=self.category_th_demand, hint="November")
        self.option_hp_nov = FloatBox(
            default_parent, category=self.category_th_demand, label="", default_value=119, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
        )
        self.option_cp_nov = FloatBox(
            default_parent, category=self.category_th_demand, label="", default_value=0, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
        )
        self.option_hl_nov = FloatBox(
            default_parent,
            category=self.category_th_demand,
            label="",
            default_value=35100,
            decimal_number=0,
            minimal_value=0,
            maximal_value=1_000_000_000,
            step=1,
        )
        self.option_cl_nov = FloatBox(
            default_parent,
            category=self.category_th_demand,
            label="",
            default_value=8000,
            decimal_number=0,
            minimal_value=0,
            maximal_value=1_000_000_000,
            step=1,
        )
        self.hint_dec = Hint(default_parent, category=self.category_th_demand, hint="December")
        self.option_hp_dec = FloatBox(
            default_parent, category=self.category_th_demand, label="", default_value=136, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
        )
        self.option_cp_dec = FloatBox(
            default_parent, category=self.category_th_demand, label="", default_value=0, decimal_number=3, minimal_value=0, maximal_value=1000000, step=1
        )
        self.option_hl_dec = FloatBox(
            default_parent,
            category=self.category_th_demand,
            label="",
            default_value=43200,
            decimal_number=0,
            minimal_value=0,
            maximal_value=1_000_000_000,
            step=1,
        )
        self.option_cl_dec = FloatBox(
            default_parent,
            category=self.category_th_demand,
            label="",
            default_value=4000,
            decimal_number=0,
            minimal_value=0,
            maximal_value=1_000_000_000,
            step=1,
        )

        self.page_result = Page(default_parent, "Results", "Results", ":/icons/icons/Result.svg")

        self.category_options_result = Category(default_parent, page=self.page_result, label="Options results")

        self.hint_depth = Hint(default_parent, category=self.category_options_result, hint="Size")
        self.option_show_legend = ButtonBox(default_parent, category=self.category_options_result, label="Show legend?", default_index=0, entries=["yes", "no"])
        self.function_save_results = FunctionButton(
            default_parent, category=self.category_options_result, button_text="Save results", icon=":/icons/icons/Save_Inv.svg"
        )
        self.function_save_figure = FunctionButton(
            default_parent, category=self.category_options_result, button_text="Save figure", icon=":/icons/icons/Save_Inv.svg"
        )

        self.category_result_figure = Category(default_parent, page=self.page_result, label="Figure")

        self.page_settings = Page(default_parent, "Settings", "Settings", ":/icons/icons/Settings.svg")

        self.category_language = Category(default_parent, page=self.page_settings, label="Language")

        self.option_language = ListBox(default_parent, category=self.category_language, label="Language: ", default_index=0, entries=[])

        self.category_save_scenario = Category(default_parent, page=self.page_settings, label="Scenario saving settings")

        self.option_auto_saving = ButtonBox(
            default_parent, category=self.category_save_scenario, label="Use automatic saving?:", default_index=0, entries=[" no ", " yes "]
        )
        self.hint_saving = Hint(
            default_parent,
            category=self.category_save_scenario,
            hint="If Auto saving is selected the scenario will automatically saved if a scenario"
            " is changed. Otherwise the scenario has to be saved with the Update scenario "
            "button in the upper left corner if the changes should not be lost. ",
        )

        self.list_of_aims: List[Tuple[Aim, str]] = [(getattr(self, name), name) for name in self.__dict__ if isinstance(getattr(self, name), Aim)]
        self.list_of_options: List[Tuple[Option, str]] = [(getattr(self, name), name) for name in self.__dict__ if isinstance(getattr(self, name), Option)]
        self.list_of_pages: List[Page] = [getattr(self, name) for name in self.__dict__ if isinstance(getattr(self, name), Page)]

    def translate(self, index: int, translation: Translations):
        Page.next_label = translation.label_next[index]
        Page.previous_label = translation.label_previous[index]
        for name in [j for j in translation.__slots__ if hasattr(self, j)]:
            entry: Optional[Option, Hint, FunctionButton, Page, Category] = getattr(self, name)
            entry.set_text(getattr(translation, name)[index])
