"""
data storage class script
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import matplotlib.pyplot as plt

from GHEtool import Borefield
from GHEtool.gui.gui_classes.gui_structure_classes import ListBox

if TYPE_CHECKING:  # pragma: no cover
    from GHEtool.gui.gui_structure import GuiStructure


class DataStorage:
    """
    An instance of this class contains all the information available in the GuiStructure.
    It also contains some extra information that is based on the direct inputs of the GuiStructure, given
    in the attributes below.

    Attributes
    ----------
    hourly_data : bool
        True if hourly data should be used
    """

    def __init__(self, gui_structure: GuiStructure) -> DataStorage:
        """
        This creates an instance of the DataStorage Class

        Parameters
        ----------
        gui_structure : GuiStructure or JSON dict
            GUI structure for which a data storage object should be created

        Returns
        -------
        DataStorage
        """
        for option, name in gui_structure.list_of_options:
            # for a listbox, not the value but the text is relevant
            if isinstance(option, ListBox):
                setattr(self, name+"_text", option.get_text())
            setattr(self, name, option.get_value())
        for aim, name in gui_structure.list_of_aims:
            setattr(self, name, aim.widget.isChecked())

        self.list_options_aims = [name for option, name in gui_structure.list_of_options] + [name for option, name in gui_structure.list_of_aims]
        self.list_of_figures = [i[1] for i in gui_structure.list_of_result_figures]

        for figure_name in self.list_of_figures:
            setattr(self, figure_name, None)

        self.borefield: Optional[Borefield] = None

        self.debug_message: str = ""

        # params for which hourly data should be loaded
        self.hourly_data: bool = self.option_method_size_depth == 2 or (
                self.option_temperature_profile_hourly == 1 and self.aim_temp_profile) or self.aim_optimize

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
        # run over options to hide or show the relevant ones
        [aim.widget.click() for aim, name in gui_structure.list_of_aims if getattr(self, name)]
        [option.set_value(getattr(self, name)) for option, name in gui_structure.list_of_options if hasattr(self, name)]
        gui_structure.change_toggle_button()

    def close_figures(self) -> None:
        """
        This function closes the figures and sets them to None.
        
        Returns
        -------
        None
        """
        for fig in self.list_of_figures:
            plt.close(getattr(self, fig))
            setattr(self, fig, None)

    def to_dict(self) -> dict:
        """
        Creates a dictionary from the class to be again imported later.

        Returns
        -------
        dict
            Dictionary with the values of the class
        """
        # get all normal values
        return {key: value for key, value in self.__dict__.items() if isinstance(value, (int, bool, float, str))}

    def from_dict(self, data: dict):
        """
        Set values from input dictionary to class

        Parameters
        ----------
        data : dict
            Dictionary with main class values created by to_dict function

        Returns
        -------
        None
        """
        # set all normal values if they exist within the DS object
        [setattr(self, key, value) for key, value in data.items() if hasattr(self, key)]

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
