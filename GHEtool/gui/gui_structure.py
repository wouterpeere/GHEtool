from GHEtool.gui.gui_classes import DoubleValue, IntValue, ListBox, Category, Page, ButtonBox, Aim, qt_w, qt_c, Option, Hint, FileName
from typing import List, Tuple
import pandas as pd

class GuiStructure:

    def __init__(self, default_parent: qt_w.QWidget, status_bar: qt_w.QStatusBar):

        self.sizeB = qt_c.QSize(48, 48)  # size of big logo on push button
        self.sizeS = qt_c.QSize(24, 24)  # size of small logo on push button
        self.sizePushB = qt_c.QSize(150, 75)  # size of big push button
        self.sizePushS = qt_c.QSize(75, 75)  # size of small push button

        self.option_data = ButtonBox(default_parent, widget_name='import_format', label='Data format:', default_index=0, entries=[' monthly data ',
                                                                                                                                 ' hourly data '])
        self.category_import_data = Category(default_parent, obj_name='category_import_data', label='Import data format', list_of_options=[self.option_data])

        self.option_method_size_length = ButtonBox(default_parent, widget_name='method_size_length', label='Method for size width and length :', default_index=0,
                                                   entries=[' L2 ', ' L3 '])
        self.option_method_size_depth = ButtonBox(default_parent, widget_name='method_size_depth', label='Method for size borehole depth :', default_index=0,
                                                  entries=[' L2 ', ' L3 ', '  L4  '])
        self.option_method_temp_gradient = ButtonBox(default_parent, widget_name='use_temp_gradient', label='Should a temperature gradient over depth be considered?:',
                                                     default_index=0, entries=[' no ', ' yes  '])
        self.option_method_rb_calc = ButtonBox(default_parent, widget_name='method_rb_calc', label='Borehole resistance calculation method:',
                                               default_index=0, entries=[' constant ', ' constant but unknown ', ' flaxibel during calculation '])
        self.category_calculation = Category(default_parent, obj_name='category_calculation_options', label='Calculation options',
                                             list_of_options=[self.option_method_size_length, self.option_method_size_depth,
                                                              self.option_method_temp_gradient, self.option_method_rb_calc])

        self.option_depth = DoubleValue(default_parent, widget_name='double_depth', label='Borehole depth [m]: ', default_value=100, decimal_number=2, minimal_value=0,
                                        maximal_value=500, step=1)
        self.option_spacing = DoubleValue(default_parent, widget_name='double_spacing', label='Borehole spacing [m]: ', default_value=6, decimal_number=2, minimal_value=1,
                                          maximal_value=99, step=0.1)
        self.option_min_spacing = DoubleValue(default_parent, widget_name='double_min_spacing', label='Minimal borehole spacing [m]: ', default_value=3, decimal_number=2,
                                              minimal_value=1, maximal_value=99, step=0.1)
        self.option_max_spacing = DoubleValue(default_parent, widget_name='double_max_spacing', label='Maximal borehole spacing [m]: ', default_value=3, decimal_number=2,
                                              minimal_value=1, maximal_value=99, step=0.1)
        self.option_width = IntValue(default_parent, widget_name='int_width', label='Width of rectangular field [#]: ', default_value=9, minimal_value=1, maximal_value=40)
        self.option_length = IntValue(default_parent, widget_name='int_length', label='Length of rectangular field [#]: ', default_value=12, minimal_value=1, maximal_value=40)

        self.option_min_width = DoubleValue(default_parent, widget_name='double_min_width', label='Minimal width of rectangular field [m]: ', default_value=10,
                                            decimal_number=2,
                                            minimal_value=1, maximal_value=1000, step=1)
        self.option_max_width = DoubleValue(default_parent, widget_name='double_max_width', label='Maximal width of rectangular field [m]: ', default_value=100,
                                            decimal_number=2,
                                            minimal_value=1, maximal_value=1000, step=1)

        self.option_min_length = DoubleValue(default_parent, widget_name='double_min_length', label='Minimal length of rectangular field [m]: ', default_value=12,
                                             decimal_number=2,
                                             minimal_value=1, maximal_value=1000, step=1)
        self.option_max_length = DoubleValue(default_parent, widget_name='double_max_length', label='Maximal length of rectangular field [m]: ', default_value=110,
                                             decimal_number=2,
                                             minimal_value=1, maximal_value=1000, step=1)

        self.option_conductivity = DoubleValue(default_parent, widget_name='double_conductivity', label='Conductivity of the soil [W/mK]: ', default_value=1.5,
                                               decimal_number=3,
                                               minimal_value=0.1, maximal_value=10, step=0.1)
        self.option_heat_capacity = DoubleValue(default_parent, widget_name='double_conductivity', label='Ground volumetric heat capacity [kJ / m³ K]: ', default_value=2400,
                                                decimal_number=1, minimal_value=1, maximal_value=100000, step=100)

        self.category_borehole = Category(default_parent, obj_name='category_borehole_earth', label='Borehole and earth properties',
                                          list_of_options=[self.option_depth, self.option_spacing, self.option_min_spacing, self.option_max_spacing,
                                                           self.option_width, self.option_length,
                                                           self.option_min_width, self.option_max_width, self.option_min_length, self.option_max_length,
                                                           self.option_conductivity,
                                                           self.option_heat_capacity])

        self.option_ground_temp = DoubleValue(default_parent, widget_name='double_ground_temp', label='Ground temperature at infinity [°C]: ', default_value=10,
                                              decimal_number=2,
                                              minimal_value=-273.15, maximal_value=100, step=0.1)
        self.option_min_temp = DoubleValue(default_parent, widget_name='double_min_temp', label='Minimal temperature [°C]: ', default_value=0, decimal_number=2,
                                           minimal_value=-273.15, maximal_value=100, step=0.1)
        self.option_max_temp = DoubleValue(default_parent, widget_name='double_max_temp', label='Maximal temperature [°C]: ', default_value=16, decimal_number=2,
                                           minimal_value=-273.15, maximal_value=100, step=0.1)
        self.option_temp_gradient = DoubleValue(default_parent, widget_name='double_temp_gradient', label='Temperature gradient [K/100m]: ', default_value=2, decimal_number=3,
                                                minimal_value=-273.15, maximal_value=100, step=0.1)
        self.option_simu_period = IntValue(default_parent, widget_name='int_simu_period', label='Simulation period [yrs]: ', default_value=20, minimal_value=1,
                                           maximal_value=100)

        self.category_temperatures = Category(default_parent, obj_name='category_temperatures', label='Temperature constraints and simulation period',
                                              list_of_options=[self.option_ground_temp, self.option_min_temp, self.option_max_temp, self.option_temp_gradient,
                                                               self.option_simu_period])

        self.option_method_temp_gradient.linked_options.append((self.option_temp_gradient, 1))

        self.option_constant_rb = DoubleValue(default_parent, widget_name='double_constant_rb', label='Equivalent borehole resistance [mK/W]: ', default_value=0.0150,
                                              decimal_number=4, minimal_value=0, maximal_value=100, step=0.01)
        self.category_constant_rb = Category(default_parent, obj_name='category_constant_rb', label='Konstant equivalent borehole resistance',
                                             list_of_options=[self.option_constant_rb])
        self.option_method_rb_calc.linked_options.append((self.category_constant_rb, 0))

        self.option_fluid_conductivity = DoubleValue(default_parent, widget_name='double_fluid_conductivity', label='Thermal conductivity [W/mK]: ', default_value=0.5,
                                                     decimal_number=3, minimal_value=0, maximal_value=100, step=0.1)
        self.option_fluid_density = DoubleValue(default_parent, widget_name='double_fluid_density', label='Density [kg/m³]: ', default_value=1000, decimal_number=1,
                                                minimal_value=0, maximal_value=10000000, step=100)
        self.option_fluid_capacity = DoubleValue(default_parent, widget_name='double_fluid_capacity', label='Thermal capacity [J/kg K]: ', default_value=4182, decimal_number=1,
                                                 minimal_value=0, maximal_value=10000000, step=100)
        self.option_fluid_viscosity = DoubleValue(default_parent, widget_name='double_fluid_viscosity', label='Dynamic viscosity [Pa s]:', default_value=0.001,
                                                  decimal_number=6,
                                                  minimal_value=0, maximal_value=1, step=0.0001)

        self.option_fluid_mass_flow = DoubleValue(default_parent, widget_name='double_fluid_mass_flow', label='Mass flow rate [kg/s]: ', default_value=0.5,
                                                  decimal_number=3, minimal_value=0, maximal_value=100000, step=0.1)

        self.category_fluid_data = Category(default_parent, obj_name='category_fluid_data', label='Fluid data', list_of_options=[
            self.option_fluid_conductivity, self.option_fluid_density, self.option_fluid_capacity, self.option_fluid_viscosity, self.option_fluid_mass_flow,])
        self.option_method_rb_calc.linked_options.append((self.category_fluid_data, 1))
        self.option_method_rb_calc.linked_options.append((self.category_fluid_data, 2))

        self.option_pipe_number = IntValue(default_parent, widget_name='int_pipe_number', label='Number of pipes [#]: ', default_value=2, minimal_value=1,
                                           maximal_value=99)
        self.option_pipe_grout_conductivity = DoubleValue(default_parent, widget_name='Double_pipe_grout_conductivity',
                                                          label='Grout thermal conductivity [W/mK]: ', default_value=1.5, decimal_number=3, minimal_value=0,
                                                          maximal_value=10000, step=0.1)
        self.option_pipe_conductivity = DoubleValue(default_parent, widget_name='Double_pipe_conductivity', label='Pipe thermal conductivity [W/mK]: ',
                                                    default_value=0.42, decimal_number=3, minimal_value=0, maximal_value=10000, step=0.1)
        self.option_pipe_inner_radius = DoubleValue(default_parent, widget_name='Double_pipe_inner_radius', label='Inner pipe radius [m]: ',
                                                    default_value=0.02, decimal_number=4, minimal_value=0, maximal_value=10000, step=0.001)
        self.option_pipe_outer_radius = DoubleValue(default_parent, widget_name='Double_pipe_outer_radius', label='Outer pipe radius [m]: ',
                                                    default_value=0.022, decimal_number=4, minimal_value=0, maximal_value=10000, step=0.001)
        self.option_pipe_borehole_radius = DoubleValue(default_parent, widget_name='Double_pipe_borehole_radius', label='Borehole radius [m]: ',
                                                       default_value=0.075, decimal_number=4, minimal_value=0, maximal_value=10000, step=0.001)
        self.option_pipe_distance = DoubleValue(default_parent, widget_name='Double_pipe_distance', label='Distance of pipe until center [m]: ',
                                                default_value=0.04, decimal_number=4, minimal_value=0, maximal_value=10000, step=0.001)
        self.option_pipe_roughness = DoubleValue(default_parent, widget_name='Double_pipe_roughness', label='Pipe roughness [m]: ',
                                                 default_value=0.000_001, decimal_number=7, minimal_value=0, maximal_value=10000, step=0.000001)
        self.option_pipe_depth = DoubleValue(default_parent, widget_name='Double_pipe_depth', label='Burial depth [m]: ', default_value=4, decimal_number=1,
                                             minimal_value=0, maximal_value=10000, step=0.1)

        self.category_pipe_data = Category(default_parent, obj_name='category_pipe_data', label='Pipe data', list_of_options=[
            self.option_pipe_number, self.option_pipe_grout_conductivity, self.option_pipe_conductivity, self.option_pipe_inner_radius,
            self.option_pipe_outer_radius, self.option_pipe_borehole_radius, self.option_pipe_distance, self.option_pipe_roughness,
            self.option_pipe_depth])
        self.category_pipe_data.activate_graphic_left()
        self.option_method_rb_calc.linked_options.append((self.category_pipe_data, 1))
        self.option_method_rb_calc.linked_options.append((self.category_pipe_data, 2))

        self.option_seperator_csv = ButtonBox(default_parent, widget_name='button_seperator_csv', label='Seperator in CSV-file:', default_index=0,
                                              entries=['Semicolon ";"', 'Comma ","'])
        self.option_decimal_csv = ButtonBox(default_parent, widget_name='button_decimal_csv', label='Decimal sign in CSV-file:', default_index=0,
                                            entries=['Point "."', 'Comma ","'])
        self.filename = FileName(default_parent, 'filename', 'Filename: ', '', 'Choose csv file', 'error', status_bar)
        self.option_column = ButtonBox(default_parent, widget_name='button_column', label='Thermal demand in one or two columns: ', default_index=0,
                                       entries=['1 column', '2 columns'])
        self.option_heating_column = ListBox(default_parent, widget_name='button_heating_column', label='Heating load line: ', default_index=0, entries=[])
        self.option_cooling_column = ListBox(default_parent, widget_name='button_cooling_column', label='Cooling load line: ', default_index=0, entries=[])
        self.option_single_column = ListBox(default_parent, widget_name='button_single_column', label='Load line: ', default_index=0, entries=[])
        self.option_unit_data = ButtonBox(default_parent, widget_name='button_unit_data', label='Unit data: ', default_index=1, entries=['W', 'kW', 'MW'])

        self.option_column.linked_options.append((self.option_single_column, 0))
        self.option_column.linked_options.append((self.option_heating_column, 1))
        self.option_column.linked_options.append((self.option_cooling_column, 1))
        self.category_select_file = Category(default_parent, obj_name='select_data', label='Select data file', list_of_options=[
            self.option_seperator_csv, self.option_decimal_csv, self.filename, self.option_column, self.option_heating_column, self.option_cooling_column,
            self.option_single_column, self.option_unit_data])

        self.hint_none_1 = Hint(default_parent, 'hint_none_1', '  ')
        self.hint_peak_heating = Hint(default_parent, 'hint_pH', 'Heating peak')
        self.hint_peak_cooling = Hint(default_parent, 'hint_pC', 'Cooling peak')
        self.hint_load_heating = Hint(default_parent, 'hint_lH', 'Heating load')
        self.hint_load_cooling = Hint(default_parent, 'hint_lH', 'Cooling load')

        self.hint_none_2 = Hint(default_parent, 'hint_none_2', '  ')
        self.hint_peak_heating_unit = Hint(default_parent, 'hint_pH_unit', '[kW]')
        self.hint_peak_cooling_unit = Hint(default_parent, 'hint_pC_unit', '[kW]')
        self.hint_load_heating_unit = Hint(default_parent, 'hint_lH_unit', '[kWh]')
        self.hint_load_cooling_unit = Hint(default_parent, 'hint_lH_unit', '[kWh]')

        self.hint_jan = Hint(default_parent, 'hint_january', 'January')
        self.hint_feb = Hint(default_parent, 'hint_February', 'February')
        self.hint_mar = Hint(default_parent, 'hint_March', 'March')
        self.hint_apr = Hint(default_parent, 'hint_April', 'April')
        self.hint_may = Hint(default_parent, 'hint_May', 'May')
        self.hint_jun = Hint(default_parent, 'hint_June', 'June')
        self.hint_jul = Hint(default_parent, 'hint_July', 'July')
        self.hint_aug = Hint(default_parent, 'hint_August', 'August')
        self.hint_sep = Hint(default_parent, 'hint_September', 'September')
        self.hint_oct = Hint(default_parent, 'hint_October', 'October')
        self.hint_nov = Hint(default_parent, 'hint_November', 'November')
        self.hint_dec = Hint(default_parent, 'hint_December', 'December')

        self.option_hp_jan = DoubleValue(default_parent, widget_name='Double_hp_jan', label='', default_value=160, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_hp_feb = DoubleValue(default_parent, widget_name='Double_hp_feb', label='', default_value=142, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_hp_mar = DoubleValue(default_parent, widget_name='Double_hp_mar', label='', default_value=102, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_hp_apr = DoubleValue(default_parent, widget_name='Double_hp_apr', label='', default_value=55, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_hp_may = DoubleValue(default_parent, widget_name='Double_hp_may', label='', default_value=0, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_hp_jun = DoubleValue(default_parent, widget_name='Double_hp_jun', label='', default_value=0, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_hp_jul = DoubleValue(default_parent, widget_name='Double_hp_jul', label='', default_value=0, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_hp_aug = DoubleValue(default_parent, widget_name='Double_hp_aug', label='', default_value=0, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_hp_sep = DoubleValue(default_parent, widget_name='Double_hp_sep', label='', default_value=0, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_hp_oct = DoubleValue(default_parent, widget_name='Double_hp_oct', label='', default_value=0, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_hp_nov = DoubleValue(default_parent, widget_name='Double_hp_nov', label='', default_value=0, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_hp_dec = DoubleValue(default_parent, widget_name='Double_hp_dec', label='', default_value=0, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)

        self.option_cp_jan = DoubleValue(default_parent, widget_name='Double_cp_jan', label='', default_value=160, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_cp_feb = DoubleValue(default_parent, widget_name='Double_cp_feb', label='', default_value=142, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_cp_mar = DoubleValue(default_parent, widget_name='Double_cp_mar', label='', default_value=102, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_cp_apr = DoubleValue(default_parent, widget_name='Double_cp_apr', label='', default_value=55, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_cp_may = DoubleValue(default_parent, widget_name='Double_cp_may', label='', default_value=0, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_cp_jun = DoubleValue(default_parent, widget_name='Double_cp_jun', label='', default_value=0, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_cp_jul = DoubleValue(default_parent, widget_name='Double_cp_jul', label='', default_value=0, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_cp_aug = DoubleValue(default_parent, widget_name='Double_cp_aug', label='', default_value=0, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_cp_sep = DoubleValue(default_parent, widget_name='Double_cp_sep', label='', default_value=0, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_cp_oct = DoubleValue(default_parent, widget_name='Double_cp_oct', label='', default_value=0, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_cp_nov = DoubleValue(default_parent, widget_name='Double_cp_nov', label='', default_value=0, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_cp_dec = DoubleValue(default_parent, widget_name='Double_cp_dec', label='', default_value=0, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)

        self.option_hl_jan = DoubleValue(default_parent, widget_name='Double_hl_jan', label='', default_value=160, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_hl_feb = DoubleValue(default_parent, widget_name='Double_hl_feb', label='', default_value=142, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_hl_mar = DoubleValue(default_parent, widget_name='Double_hl_mar', label='', default_value=102, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_hl_apr = DoubleValue(default_parent, widget_name='Double_hl_apr', label='', default_value=55, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_hl_may = DoubleValue(default_parent, widget_name='Double_hl_may', label='', default_value=0, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_hl_jun = DoubleValue(default_parent, widget_name='Double_hl_jun', label='', default_value=0, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_hl_jul = DoubleValue(default_parent, widget_name='Double_hl_jul', label='', default_value=0, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_hl_aug = DoubleValue(default_parent, widget_name='Double_hl_aug', label='', default_value=0, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_hl_sep = DoubleValue(default_parent, widget_name='Double_hl_sep', label='', default_value=0, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_hl_oct = DoubleValue(default_parent, widget_name='Double_hl_oct', label='', default_value=0, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_hl_nov = DoubleValue(default_parent, widget_name='Double_hl_nov', label='', default_value=0, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_hl_dec = DoubleValue(default_parent, widget_name='Double_hl_dec', label='', default_value=0, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)

        self.option_cl_jan = DoubleValue(default_parent, widget_name='Double_cl_jan', label='', default_value=160, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_cl_feb = DoubleValue(default_parent, widget_name='Double_cl_feb', label='', default_value=142, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_cl_mar = DoubleValue(default_parent, widget_name='Double_cl_mar', label='', default_value=102, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_cl_apr = DoubleValue(default_parent, widget_name='Double_cl_apr', label='', default_value=55, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_cl_may = DoubleValue(default_parent, widget_name='Double_cl_may', label='', default_value=0, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_cl_jun = DoubleValue(default_parent, widget_name='Double_cl_jun', label='', default_value=0, decimal_number=3, minimal_value=0,
                                        maximal_value=1000000, step=1)
        self.option_cl_jul = DoubleValue(default_parent, widget_name='Double_cl_jul', label='', default_value=0, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_cl_aug = DoubleValue(default_parent, widget_name='Double_cl_aug', label='', default_value=0, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_cl_sep = DoubleValue(default_parent, widget_name='Double_cl_sep', label='', default_value=0, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_cl_oct = DoubleValue(default_parent, widget_name='Double_cl_oct', label='', default_value=0, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_cl_nov = DoubleValue(default_parent, widget_name='Double_cl_nov', label='', default_value=0, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)
        self.option_cl_dec = DoubleValue(default_parent, widget_name='Double_cl_dec', label='', default_value=0, decimal_number=3, minimal_value=0,
                                         maximal_value=1000000, step=1)

        self.category_th_demand = Category(default_parent, obj_name='th_demand', label='Thermal demands', list_of_options=[
            self.hint_none_1, self.hint_peak_heating, self.hint_peak_cooling, self.hint_load_heating, self.hint_load_cooling,
            self.hint_none_2, self.hint_peak_heating_unit, self.hint_peak_cooling_unit, self.hint_load_heating_unit, self.hint_load_cooling_unit,
            self.hint_jan, self.option_hp_jan, self.option_cp_jan, self.option_hl_jan, self.option_cl_jan,
            self.hint_feb, self.option_hp_feb, self.option_cp_feb, self.option_hl_feb, self.option_cl_feb,
            self.hint_mar, self.option_hp_mar, self.option_cp_mar, self.option_hl_mar, self.option_cl_mar,
            self.hint_apr, self.option_hp_apr, self.option_cp_apr, self.option_hl_apr, self.option_cl_apr,
            self.hint_may, self.option_hp_may, self.option_cp_may, self.option_hl_may, self.option_cl_may,
            self.hint_jun, self.option_hp_jun, self.option_cp_jun, self.option_hl_jun, self.option_cl_jun,
            self.hint_jul, self.option_hp_jul, self.option_cp_jul, self.option_hl_jul, self.option_cl_jul,
            self.hint_aug, self.option_hp_aug, self.option_cp_aug, self.option_hl_aug, self.option_cl_aug,
            self.hint_sep, self.option_hp_sep, self.option_cp_sep, self.option_hl_sep, self.option_cl_sep,
            self.hint_oct, self.option_hp_oct, self.option_cp_oct, self.option_hl_oct, self.option_cl_oct,
            self.hint_nov, self.option_hp_nov, self.option_cp_nov, self.option_hl_nov, self.option_cl_nov,
            self.hint_dec, self.option_hp_dec, self.option_cp_dec, self.option_hl_dec, self.option_cl_dec,
        ])
        self.category_th_demand.activate_grid_layout(5)
        self.option_data.linked_options.append((self.category_th_demand, 0))

        self.option_language = ListBox(default_parent, widget_name='list_language', label='Language: ', default_index=0, entries=['english', 'german'])
        self.category_language = Category(default_parent, obj_name='category_language', label='Language', list_of_options=[self.option_language])

        self.option_auto_saving = ButtonBox(default_parent, widget_name='option_auto_saving', label='Use automatic saving?:', default_index=0,
                                            entries=[' no ', ' yes '])
        self.hint_saving = Hint(default_parent, widget_name='hint_saving', hint='If Auto saving is selected the scenario will automatically saved if a scenario'
                                                                                ' is changed. Otherwise the scenario has to be saved with the Update scenario '
                                                                                'butten in the upper left corner if the changes should not be lost. ')

        self.category_save_scenario = Category(default_parent, obj_name='category_save_scenario', label='Scenario saving settings', list_of_options=[
            self.option_auto_saving, self.hint_saving])

        self.aim_temp_profile = Aim(default_parent, 'pushButton_temp_profile', 'Determine temperature profile', ':/icons/icons/Options.svg',
                                    [self.category_import_data, self.option_depth, self.option_spacing, self.option_width, self.option_length])
        self.aim_req_depth = Aim(default_parent, 'pushButton_req_depth', 'Determine required depth', ':/icons/icons/Depth_determination.svg',
                                 [self.category_import_data, self.option_method_size_depth, self.option_spacing, self.option_width, self.option_length])
        self.aim_size_length = Aim(default_parent, 'pushButton_size_length', 'Size borefield by length and width', ':/icons/icons/Size_Length.svg',
                                   [self.category_import_data, self.option_method_size_length, self.option_min_spacing, self.option_max_spacing,
                                    self.option_min_width, self.option_max_width,
                                    self.option_min_length, self.option_max_length])
        self.aim_optimize = Aim(default_parent, 'pushButton_optimize', 'Optimize load profile', ':/icons/icons/Optimize_Profile.svg',
                                [self.option_depth, self.option_spacing, self.option_width, self.option_length])

        self.page_aim = Page(default_parent, 'Aim', 'Aim of simulation', 'Aim', ':/icons/icons/Aim_Inv.svg', [])
        self.page_aim.set_upper_frame([self.aim_temp_profile, self.aim_req_depth, self.aim_size_length, self.aim_optimize])
        self.page_options = Page(default_parent, 'Options', 'Options', 'Options', ':/icons/icons/Options.svg', [self.category_import_data, self.category_calculation])
        self.page_borehole = Page(default_parent, 'Borehole', 'Borehole and earth', 'Borehole\nand earth', ':/icons/icons/Borehole.png',
                                  [self.category_borehole, self.category_temperatures])
        self.page_borehole_resistance = Page(default_parent, 'Borehole_resistance', 'Equivalent borehole resistance', 'Borehole\nresistance', ':/icons/icons/Resistance.png',
                                             [self.category_constant_rb, self.category_fluid_data, self.category_pipe_data])
        self.page_thermal = Page(default_parent, 'thermal_demands', 'Thermal demands', 'Thermal\ndemands', ':/icons/icons/Thermal.svg',
                                 [self.category_select_file, self.category_th_demand])
        self.page_settings = Page(default_parent, 'settings', 'Settings', 'Settings', ':/icons/icons/Settings.svg', [
            self.category_language, self.category_save_scenario])

        self.page_aim.set_next_page(self.page_options)
        self.page_options.set_previous_page(self.page_aim)
        self.page_options.set_next_page(self.page_borehole)
        self.page_borehole.set_previous_page(self.page_options)
        self.page_borehole.set_next_page(self.page_borehole_resistance)
        self.page_borehole_resistance.set_previous_page(self.page_borehole)
        self.page_borehole_resistance.set_next_page(self.page_thermal)
        self.page_thermal.set_previous_page(self.page_borehole)

        self.list_of_options: List[Tuple[Option, str]] = [(getattr(self, name), name) for name in self.__dict__ if isinstance(getattr(self, name), Option)]
        self.list_of_pages: List[Page] = [getattr(self, name) for name in self.__dict__ if isinstance(getattr(self, name), Page)]

    def translate(self, index: int):
        from GHEtool.main_class import FOLDER
        data = pd.read_csv(f'{FOLDER}/gui/Translations.csv', sep=';')
        column = data.columns[index+1]
        for i in range(len(data)):
            try:
                entry = getattr(self, data['name'][i])
            except AttributeError:
                continue
            if isinstance(entry, Page):
                name: Tuple[str, str] = data[column][i].split(',')
                entry.set_text(name[0], name[1])


    def event_filter(self, obj: qt_w.QPushButton, event) -> bool:
        """
        function to check mouse over event
        :param obj:
        PushButton obj
        :param event:
        event to check if mouse over event is entering or leaving
        :return:
        Boolean to check if the function worked
        """
        if event.type() == qt_c.QEvent.Enter:
            # Mouse is over the label
            self.set_push(True)
            return True
        elif event.type() == qt_c.QEvent.Leave:
            # Mouse is not over the label
            self.set_push(False)
            return True
        return False

    def set_push(self, mouse_over: bool) -> None:
        """
        function to Set PushButton Text if MouseOver
        :param mouse_over: bool true if Mouse is over PushButton
        :return: None
        """
        # if Mouse is over PushButton change size to big otherwise to small
        if mouse_over:
            for page in self.list_of_pages:
                self.set_push_button_icon_size(page.button, True, page.button.setText(page.button_name))
            return
        for page in self.list_of_pages:
            self.set_push_button_icon_size(page.button)

    def set_push_button_icon_size(self, button: qt_w.QPushButton, big: bool = False, name: str = '') -> None:
        """
        set button name and size
        :param button: QPushButton to set name and icon size for
        :param big: big or small icon size (True = big)
        :param name: name to set to QPushButton
        :return: None
        """
        button.setText(name)  # set name to button
        # size big or small QPushButton depending on input
        if big:
            button.setIconSize(self.sizeS)
            button.setMaximumSize(self.sizePushB)
            button.setMinimumSize(self.sizePushB)
            return
        button.setIconSize(self.sizeB)
        button.setMaximumSize(self.sizePushS)
        button.setMinimumSize(self.sizePushS)
