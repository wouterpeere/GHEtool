from typing import Optional

import pandas as pd
import pygfunction as gt

from GHEtool import Borefield, FluidData, GroundData, PipeData
from GHEtool.gui.gui_structure import GuiStructure
from GHEtool.gui.gui_classes import ListBox


class DataStorage:
    """
    An instance of this class contains all the information available in the GuiStructure.
    It also contains some extra information that is based on the direct inputs of the GuiStructure, given
    in the attributes below.

    Attributes
    ----------
    peakHeating : List
        List with monthly peak heating values [kW]
    peakCooling : List
        List with monthly peak cooling values [kW]
    monthlyLoadHeating : List
        List with monthly heating load values [kWh]
    monthlyLoadCooling : List
        List with monthly cooling load values [kWh]
    ground_data : GroundData
        Ground data object based on multiple inputs in the GUI
    fluid_data : FluidData
        Fluid data object based on multiple inputs in the GUI
    pipe_data : PipeData
        Pipe data object based on multiple inputs in the GUI
    borefield_pygfunction : pygfunction borefield object
        Borefield object based on multiple inputs in the GUI
    hourly_data : bool
        True if hourly data should be used
    """

    def __init__(self, gui_structure: GuiStructure):
        """
        This creates an instance of the DataStorage Class

        Parameters
        ----------
        gui_structure : GuiStructure
            GUI structure for which a data storage object should be created

        Returns
        -------
        None
        """
        for option, name in gui_structure.list_of_options:
            # for a listbox, not the value but the text is relevant
            if isinstance(option, ListBox):
                setattr(self, name+"_text", option.get_text())
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
        self.ground_data: GroundData = GroundData(self.option_conductivity, self.option_ground_temp if self.option_method_temp_gradient == 0 else self.option_ground_temp_gradient,
                                                  self.option_constant_rb, self.option_heat_capacity * 1000, self._calculate_flux())

        self.borefield_pygfunction = gt.boreholes.rectangle_field(self.option_width, self.option_length, self.option_spacing, self.option_spacing,
                                                      self.option_depth, self.option_pipe_depth, self.option_pipe_borehole_radius)

        self.fluid_data: FluidData = FluidData(self.option_fluid_mass_flow, self.option_fluid_conductivity, self.option_fluid_density,
                                               self.option_fluid_capacity, self.option_fluid_viscosity)
        self.pipe_data: PipeData = PipeData(self.option_pipe_grout_conductivity, self.option_pipe_inner_radius, self.option_pipe_outer_radius,
                                            self.option_pipe_conductivity, self.option_pipe_distance, self.option_pipe_number, self.option_pipe_roughness)

        self.debug_message: str = ""

        # params for which hourly data should be loaded
        self.hourly_data: bool = self.option_method_size_depth == 2 or (
                self.option_temperature_profile_hourly == 1 and self.aim_temp_profile) or self.aim_optimize

    def _calculate_flux(self) -> float:
        """
        This function calculates the geothermal flux.
        This is calculated based on:

        2 * temperature gradient * conductivity / 100

        Returns
        -------
        Geothermal flux : float
            Geothermal flux in [W/m2]
        """
        return 2 * self.option_temp_gradient * self.option_conductivity / 100

    def set_values(self, gui_structure: GuiStructure) -> None:
        """
        This function sets the values in the gui_structure according to the one stored in this class.

        Parameters
        ----------
        gui_structure : GuiStructure
            Gui structure for which the values in this DataStorage class should be set

        Returns
        -------
        None
        """
        [aim.widget.setChecked(False) for aim, _ in gui_structure.list_of_aims]
        [aim.widget.click() for aim, name in gui_structure.list_of_aims if getattr(self, name)]
        [option.set_value(getattr(self, name)) for option, name in gui_structure.list_of_options if hasattr(self, name)]
        gui_structure.change_toggle_button()

    def __eq__(self, other) -> bool:
        """
        This function checks whether or not the current DataStorage object is equal to another one.

        Parameters
        ----------
        other : DataStorage
            Other data storage object to which the current one should be compared to

        Returns
        -------
        bool
            True if the current object has the same values as another object
        """
        # if not of same class return false
        if not isinstance(other, DataStorage):
            return False
        # compare all slot values if one not match return false
        for i in self.list_options_aims:
            if not hasattr(self, i) or not hasattr(other, i):
                return False
            if getattr(self, i) != getattr(other, i):
                return False
        # if all match return true
        return True
