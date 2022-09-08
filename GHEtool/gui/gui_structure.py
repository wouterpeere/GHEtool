from GHEtool.gui.gui_classes import DoubleValue, IntValue, ListBox, Category, Page, ButtonBox, Aim, qt_w, Option
from typing import List, Tuple
import pandas as pd

class GuiStructure:

    def __init__(self, default_parent: qt_w.QWidget):
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
            self.option_fluid_conductivity, self.option_fluid_density, self.option_fluid_capacity, self.option_fluid_viscosity, self.option_fluid_mass_flow])
        self.option_method_rb_calc.linked_options.append((self.category_fluid_data, 1))
        self.option_method_rb_calc.linked_options.append((self.category_fluid_data, 2))

        self.option_pipe_number = IntValue(default_parent, widget_name='int_pipe_number', label='Number of pipes [#]: ', default_value=2, minimal_value=1,
                                           maximal_value=99)
        self.option_pipe_grout_conductivity = DoubleValue(default_parent, widget_name='Double_pipe_grout_conductivity',
                                                          label='Grout thermal conductivity [W/mK]: ', default_value=1.5, decimal_number=3, minimal_value=0,
                                                          maximal_value=10000, step=0.1)

        self.category_pipe_data = Category(default_parent, obj_name='category_pipe_data', label='Pipe data', list_of_options=[
            self.option_pipe_number, self.option_pipe_grout_conductivity])
        self.option_method_rb_calc.linked_options.append((self.category_pipe_data, 1))
        self.option_method_rb_calc.linked_options.append((self.category_pipe_data, 2))

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

        self.page_aim.set_next_page(self.page_options)
        self.page_options.set_previous_page(self.page_aim)
        self.page_options.set_next_page(self.page_borehole)
        self.page_borehole.set_previous_page(self.page_options)
        self.page_borehole.set_next_page(self.page_borehole_resistance)
        self.page_borehole_resistance.set_previous_page(self.page_borehole)

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
