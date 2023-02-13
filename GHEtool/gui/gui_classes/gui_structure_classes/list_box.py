from __future__ import annotations

import abc
from functools import partial as ft_partial
from os.path import exists
from typing import Callable, List, Optional, Tuple, Union
from pathlib import Path

import matplotlib.pyplot as plt
import PySide6.QtCore as QtC  # type: ignore
import PySide6.QtGui as QtG  # type: ignore
import PySide6.QtWidgets as QtW  # type: ignore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from GHEtool.gui.gui_classes.gui_structure_classes.option import Option, Category
from GHEtool.gui.gui_classes.gui_structure_classes.hint import Hint
from GHEtool.gui.gui_classes.gui_structure_classes.function_button import FunctionButton

from GHEtool.gui.gui_classes.gui_base_class import DARK, GREY, LIGHT, LIGHT_SELECT, WARNING, WHITE, set_graph_layout

from GHEtool.gui.gui_classes.gui_structure_classes.functions import check



class ListBox(Option):
    """
    This class contains all the functionalities of the ListBox option in the GUI.
    The ListBox can be used to select one option out of many (sort of like the ButtonBox)
    """
    def __init__(self, label: str, default_index: int, entries: List[str], category: Category):
        """

        Parameters
        ----------
        label : str
            The label of the ListBox
        default_index : int
            The default index of the ListBox
        entries : List[str]
            The list of all the different buttons in the ListBox
        category : Category
            Category in which the ButtonBox should be placed

        Examples
        --------
        >>> option_list = ListBox(label='List box label text',
        >>>                       default_index=0,
        >>>                       entries=['Option 1', 'Option 2'],
        >>>                       category=category_example)

        Gives:

        .. figure:: _static/Example_List_Box.PNG

        """
        super().__init__(label, default_index, category)
        self.entries: List[str] = entries
        self.widget: QtW.QComboBox = QtW.QComboBox(self.default_parent)

    def get_text(self) -> str:
        """
        This function returns the current text of the ListBox.

        Returns
        -------
        str
            Current text on the ListBox
        """
        return self.widget.currentText()

    def get_value(self) -> int:
        """
        This function gets the value (i.e. index) of the ListBox.

        Returns
        -------
        int
            Value/index of the ListBox
        """
        return self.widget.currentIndex()

    def set_value(self, value: int) -> None:
        """
        This function sets the value/index of the ListBox.

        Parameters
        ----------
        value : int
            Index of the ListBox

        Returns
        -------
        None
        """
        self.widget.setCurrentIndex(value)

    def _init_links(self) -> None:
        """
        Function on how the links for the ListBox should be set.

        Returns
        -------
        None
        """
        current_value: int = self.get_value()
        self.set_value(0 if current_value != 0 else 1)
        self.set_value(current_value)

    def _check_value(self) -> bool:
        """
        This function checks whether a correct value is selected.

        Returns
        -------
        bool
            True if the current index of the ListBox is larger than zero. False otherwise
        """
        return self.widget.currentIndex() >= 0

    def set_text(self, name: str):
        """
        This function sets the text of the label and of the different buttons in the ListBox.

        Parameters
        ----------
        name: str
            String with the names of all the buttons (in order) and the label name at position 0.
            These strings are separated by ","

        Returns
        -------
        None
        """
        entry_name: List[str, str] = name.split(',')
        self.label_text = entry_name[0]
        self.label.setText(self.label_text)
        for idx, name in enumerate(entry_name[1:]):
            self.widget.setItemText(idx, name)

    def add_link_2_show(self, option: Union[Option, Category, FunctionButton, Hint], *, on_index: int):
        """
        This function couples the visibility of an option to the value of the ButtonBox object.

        Parameters
        ----------
        option : Option, Category, FunctionButton, Hint
            Option which visibility should be linked to the value of the FloatBox.
        on_index : int
            The index on which the linked options should be made visible.

        Returns
        -------
        None

        Examples
        --------
        This function can be used to couple the ButtonBox value to other options, hints, function buttons or categories.
        In the example below, 'option linked' will be shown if the first ('0') option is selected in the ListBox.

        >>> option_list.add_link_2_show(option=option_linked, on_index=0)

        """
        self.linked_options.append([option, on_index])

    def check_linked_value(self, value: int) -> bool:
        """
        This function checks if the linked "option" should be shown.

        Parameters
        ----------
        value : int
            int of index on which the option should be shown

        Returns
        -------
        bool
            True if the linked "option" should be shown
        """
        return self.get_value() == value

    def change_event(self, function_to_be_called: Callable) -> None:
        """
        This function calls the function_to_be_called whenever the index of the ListBox is changed.

        Parameters
        ----------
        function_to_be_called : callable
            Function which should be called

        Returns
        -------
        None
        """
        self.widget.currentIndexChanged.connect(function_to_be_called)  # pylint: disable=E1101

    def create_widget(self, frame: QtW.QFrame, layout_parent: QtW.QLayout, row: int = None, column: int = None) -> None:
        """
        This functions creates the ListBox widget in the frame.

        Parameters
        ----------
        frame : QtW.QFrame
            The frame object in which the widget should be created
        layout_parent : QtW.QLayout
            The parent layout of the current widget
        row : int
            The index of the row in which the widget should be created
            (only needed when there is a grid layout)
        column : int
            The index of the column in which the widget should be created
            (only needed when there is a grid layout)

        Returns
        -------
        None
        """
        layout = self.create_frame(frame, layout_parent)
        self.widget.setParent(self.frame)
        self.widget.setStyleSheet(
            f"QFrame {'{'}border: 1px solid {WHITE};border-bottom-left-radius: 0px;border-bottom-right-radius: 0px;{'}'}"
            f"QComboBox{'{'}border: 1px solid {WHITE};border-bottom-left-radius: 0px;border-bottom-right-radius: 0px;{'}'}"
        )
        self.widget.addItems(self.entries)
        self.widget.setCurrentIndex(self.default_value)
        self.widget.setMaximumWidth(100)
        self.widget.setMinimumWidth(100)
        self.widget.currentIndexChanged.connect(ft_partial(check, self.linked_options, self))  # pylint: disable=E1101
        if row is not None and isinstance(layout_parent, QtW.QGridLayout):
            layout_parent.addWidget(self.widget, column, row)
            return
        layout.addWidget(self.widget)