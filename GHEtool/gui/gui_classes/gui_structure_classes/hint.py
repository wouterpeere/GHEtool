"""
float box option class
"""
from __future__ import annotations

import abc
from functools import partial as ft_partial
from os.path import exists
from typing import Callable, List, Optional, Tuple, Union, Protocol
from pathlib import Path

import matplotlib.pyplot as plt
import PySide6.QtCore as QtC  # type: ignore
import PySide6.QtGui as QtG  # type: ignore
import PySide6.QtWidgets as QtW  # type: ignore

from GHEtool.gui.gui_classes.gui_base_class import DARK, GREY, LIGHT, LIGHT_SELECT, WARNING, WHITE, set_graph_layout

class Option(Protocol):
    label_text: str
    default_value: Union[bool, int, float, str]
    widget: Optional[QtW.QWidget]
    frame: QtW.QFrame
    label:  QtW.QLabel
    linked_options: List[(Option, int)]
    limit_size: bool

class Category(Protocol):
    list_of_options: List[Option]

class Hint:
    """
    This class contains all the functionalities of the Hint option in the GUI.
    Hints can be used to show text (for information or warnings) inside the category.
    """

    default_parent: Optional[QtW.QWidget] = None

    def __init__(self, hint: str, category: Category, warning: bool = False):
        """

        Parameters
        ----------
        hint : str
            Text of the hint
        category : Category
            Category in which the Hint should be placed
        warning : bool
            True if the Hint should be shown

        Examples
        --------
        >>> hint_example = Hint(hint='This is a hint to something important.',
        >>>                     category=category_example,
        >>>                     warning=True)

        Gives:

        .. figure:: _static/Example_Hint.PNG

        """
        self.hint: str = hint
        self.label: QtW.QLabel = QtW.QLabel(self.default_parent)
        self.warning = warning
        category.list_of_options.append(self)

    def create_widget(self, frame: QtW.QFrame, layout_parent: QtW.QLayout, row: int = None, column: int = None) -> None:
        """
        This functions creates the ButtonBox widget in the frame.

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
        self.label.setParent(frame)
        self.label.setText(self.hint)
        if self.warning:
            self.label.setStyleSheet(f"color: {WARNING};")
        self.label.setWordWrap(True)
        if row is not None and isinstance(layout_parent, QtW.QGridLayout):
            layout_parent.addWidget(self.label, column, row)
            return
        layout_parent.addWidget(self.label)

    def hide(self) -> None:
        """
        This function makes the Hint invisible.

        Returns
        -------
        None
        """
        self.label.hide()

    def show(self) -> None:
        """
        This function makes the current Hint visible.

        Returns
        -------
        None
        """
        self.label.show()

    def is_hidden(self) -> bool:
        """
        This function returns a boolean value related to whether or not the Hint is hidden.

        Returns
        -------
        Bool
            True if the option is hidden
        """
        return self.label.isHidden()

    def set_text(self, name: str):
        """
        This function sets the text of the Hint.

        Parameters
        ----------
        name : str
            Text of the Hint

        Returns
        -------
        None
        """
        self.hint: str = name
        self.label.setText(self.hint)

    def __repr__(self):
        return f'{type(self).__name__}; Hint: {self.hint}; Warning: {self.warning}'