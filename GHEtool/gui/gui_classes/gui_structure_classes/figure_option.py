"""
figure option class script
"""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Tuple

from GHEtool.gui.gui_classes.gui_structure_classes.button_box import ButtonBox

if TYPE_CHECKING:  # pragma: no cover
    from GHEtool.gui.gui_classes.gui_structure_classes.result_figure import ResultFigure


class FigureOption(ButtonBox):
    """
    This class contains all the functionalities of the FigureOption.
    Such an element is not placed in itself on the GUI, but is part of the ResultFigure category.
    It can be used to add an extra option to alter the figure shown.
    """
    def __init__(self, category: ResultFigure, label: str, param: str, default: int, entries: List[str], entries_values: List):
        """

        Parameters
        ----------
        category : ResultFigure
            Category in which the FigureOption should be placed
        label : str
            The label of the FigureOption
        param : str
            Name of the argument in the function that is used to generate the figure
        default : int
            The default index of the FigureOption
        entries : List[str]
            The list of all the different buttons in the FigureOption
        entries_values : List
            The list of all the corresponding values (w.r.t. entries) for the argument defined in param

        Examples
        --------
        The example below adds the legende on/off option to the temperature profile figure.

        >>> FigureOption(category=self.figure_temperature_profile,
        >>>              label="Legend on",
        >>>              param="legend",
        >>>              default=0,
        >>>              entries=["No", "Yes"],
        >>>              entries_values=[False, True])

        Gives:

        .. figure:: _static/Example_FigureOption.PNG

        """
        super(FigureOption, self).__init__(label=label, default_index=default, entries=entries, category=category)
        self.values = entries_values
        self.param = param

    def get_value(self) -> Tuple[str, int]:
        """
        This functions returns the value of the FigureOption.
        This is used to update the finale results figure.

        Returns
        -------
        key_name, key_value : str, int
            Name of the variable and its value as an argument for the function in the Borefield Class that creates the figure.
        """
        for idx, button in enumerate(self.widget):
            if button.isChecked():
                return self.param, self.values[idx]
        return "", -1

    def set_value(self, values: Tuple[str, int]) -> None:
        """
        This function sets the value of the FigureOption.

        Parameters
        ----------
        values : Tuple[str, int]
            Tuple containing the value of the FigureOption and its selected index.
            Only the index is used.

        Returns
        -------
        None
        """
        value = values[1]
        for idx, button in enumerate(self.widget):
            if self.values[idx] == value:
                if not button.isChecked():
                    button.click()
                break
        return