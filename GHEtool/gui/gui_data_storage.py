from typing import Optional

import pandas as pd

from GHEtool import Borefield, FluidData, GroundData, PipeData
from GHEtool.gui.gui_structure import GuiStructure


class DataStorage:

    def __init__(self, gui_structure: GuiStructure):
        for option, name in gui_structure.list_of_options:
            setattr(self, name, option.get_value())
        for aim, name in gui_structure.list_of_aims:
            setattr(self, name, aim.widget.isChecked())

        self.list_options_aims = [name for option, name in gui_structure.list_of_options] + [name for option, name in gui_structure.list_of_aims]

        self.borefield: Optional[Borefield] = None

        self.peakHeating: list = [self.option_hp_jan, self.option_hp_feb, self.option_hp_mar, self.option_hp_apr, self.option_hp_may, self.option_hp_jun,
                                  self.option_hp_jul, self.option_hp_aug, self.option_hp_sep, self.option_hp_oct, self.option_hp_nov, self.option_hp_dec]
        self.peakCooling: list = [self.option_cp_jan, self.option_cp_feb, self.option_cp_mar, self.option_cp_apr, self.option_cp_may, self.option_cp_jun,
                                  self.option_cp_jul, self.option_cp_aug, self.option_cp_sep, self.option_cp_oct, self.option_cp_nov, self.option_cp_dec]
        self.monthlyLoadHeating: list = [self.option_hl_jan, self.option_hl_feb, self.option_hl_mar, self.option_hp_apr, self.option_hl_may, self.option_hl_jun,
                                         self.option_hl_jul, self.option_hl_aug, self.option_hl_sep, self.option_hl_oct, self.option_hl_nov, self.option_hl_dec]
        self.monthlyLoadCooling: list = [self.option_cl_jan, self.option_cl_feb, self.option_cl_mar, self.option_cl_apr, self.option_cl_may, self.option_cl_jun,
                                         self.option_cl_jul, self.option_cl_aug, self.option_cl_sep, self.option_cl_oct, self.option_cl_nov, self.option_cl_dec]
        self.ground_data: GroundData = GroundData(self.option_depth, self.option_spacing, self.option_conductivity, self.option_ground_temp,
                                                  self.option_constant_rb, self.option_width, self.option_length, self.option_heat_capacity * 1000,
                                                  2 * self.option_temp_gradient * self.option_conductivity / 100 if self.option_method_temp_gradient == 1
                                                  else 0)
        self.fluid_data: FluidData = FluidData(self.option_fluid_mass_flow, self.option_fluid_conductivity, self.option_fluid_density,
                                               self.option_fluid_capacity, self.option_fluid_viscosity)
        self.pipe_data: PipeData = PipeData(self.option_pipe_grout_conductivity, self.option_pipe_inner_radius, self.option_pipe_outer_radius,
                                            self.option_pipe_conductivity, self.option_pipe_distance, self.option_pipe_borehole_radius,
                                            self.option_pipe_number, self.option_pipe_roughness, self.option_pipe_depth)
        # check if a file for optimizing the load profile has been selected
        self.fileSelected: bool = (self.aim_optimize and self.option_filename == '')

    def set_values(self, gui_structure: GuiStructure):
        [option.set_value(getattr(self, name)) for option, name in gui_structure.list_of_options]
        [aim.widget.setChecked(False) for aim, _ in gui_structure.list_of_aims]
        [aim.widget.click() for aim, name in gui_structure.list_of_aims if getattr(self, name)]

    def save(self):
        data = pd.DataFrame([(name, getattr(self, name)) for name in self.__dict__])
        data.to_csv('test.csv')

    def __eq__(self, other) -> bool:
        """
        equality function to check if values are equal
        :param other: to compare Datastorage
        :return: boolean which is true if self has the same values as other
        """
        # if not of same class return false
        if not isinstance(other, DataStorage):
            return False
        # compare all slot values if one not match return false
        for i in self.list_options_aims:
            if getattr(self, i) != getattr(other, i):
                return False
        # if all match return true
        return True
