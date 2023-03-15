"""
aim class script
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable, List, Optional, Protocol, Tuple, Union

import PySide6.QtCore as QtC  # type: ignore
import PySide6.QtGui as QtG  # type: ignore
import PySide6.QtWidgets as QtW  # type: ignore

from GHEtool import FOLDER
from GHEtool.gui.gui_classes.gui_base_class import DARK, GREY, LIGHT, LIGHT_SELECT, WARNING, WHITE, set_graph_layout

if TYPE_CHECKING:  # pragma: no cover
    from GHEtool.gui.gui_classes.gui_structure_classes.function_button import FunctionButton
    from GHEtool.gui.gui_classes.gui_structure_classes.hint import Hint


class Option(Protocol):
    label_text: str
    default_value: Union[bool, int, float, str]
    widget: Optional[QtW.QWidget]
    frame: QtW.QFrame
    label:  QtW.QLabel
    linked_options: List[(Option, int)]
    limit_size: bool
    list_2_check_before_value: List[Tuple[Option, int], Aim]


class Category(Protocol):
    list_of_options: List[Option]

class Page(Protocol):
    upper_frame: List[Union[Aim, Option, Category]]

class Aim:
    """
    This class contains all the functionalities of the Aim option in the GUI.
    The Aim option is central in the GHEtool GUI for it determines the possible 'things' one can do with the tool.
    """

    default_parent: Optional[QtW.QWidget] = None

    def __init__(self, label: str, icon: str, page: Page):
        """

        Parameters
        ----------
        label : str
            Name of the Aim
        icon : str
            Path to the icon for the Aim
        page : Page
            Page on which the Aim should be shown (normally, this is the first page)

        Examples
        --------
        >>> aim_example = Aim(label='Example aim',
        >>>                   icon="example_icon.svg",
        >>>                   page=page_aim)

        Gives:

        .. figure:: _static/Example_Aim.PNG

        """
        self.label: str = label
        self.icon: str = icon
        self.widget: QtW.QPushButton = QtW.QPushButton(self.default_parent)
        self.list_options: List[Union[Option, Category, FunctionButton]] = []
        page.upper_frame.append(self)

    def set_text(self, name: str) -> None:
        """
        This function sets the label text.

        Parameters
        ----------
        name : str
            Label name of the object

        Returns
        -------
        None
        """
        self.label = name
        self.widget.setText(name)

    def change_event(self, function_to_be_called: Callable, *args) -> None:
        """
        This function calls the function_to_be_called whenever the Aim is changed.

        Parameters
        ----------
        function_to_be_called : callable
            Function which should be called
        *args
            Arguments which are passed through to the function_to_be_called

        Returns
        -------
        None
        """
        self.widget.clicked.connect(lambda: function_to_be_called(*args))  # pylint: disable=E1101

    def add_link_2_show(self, option: Union[Option, Category, FunctionButton, Hint]):
        """
        This function couples the visibility of an option to the value of the Aim object.

        Parameters
        ----------
        option : Option, Category, FunctionButton, Hint
            Option which visibility should be linked to the value of the FloatBox.

        Returns
        -------
        None

        Examples
        --------
        This function can be used to couple the Aim value to other options, hints, function buttons or categories.
        In the example below, 'option_example' will be shown if the Aim is selected.

        >>> aim_example.add_link_2_show(option=option_example)
        """
        self.list_options.append(option)

    def create_widget(self, frame: QtW.QFrame, layout: QtW.QGridLayout, idx: int) -> None:
        """
        This functions creates the Aim widget in the grid layout.

        Parameters
        ----------
        frame : QtW.QFrame
            The frame object in which is the parent of the current widget
        layout : QtW.QGridLayout
            The grid layout in which the widget should be created
        idx : int
            Index of the current Aim

        Returns
        -------
        None
        """
        icon11 = QtG.QIcon()
        icon11.addFile(f"{FOLDER}/gui/icons/{self.icon}")
        self.widget.setParent(frame)
        push_button = self.widget
        push_button.setIcon(icon11)
        push_button.setMinimumSize(QtC.QSize(0, 60))
        push_button.setMaximumSize(QtC.QSize(16777215, 60))
        push_button.setStyleSheet(
            f"QPushButton{'{'}border: 3px solid {DARK};border-radius: 15px;color:{WHITE};gridline-color: {LIGHT};background-color: {GREY};font-weight:700;{'}'}"
            f"QPushButton:hover{'{'}border: 3px solid {DARK};background-color:{LIGHT};{'}'}"
            f"QPushButton:checked{'{'}border:3px solid {LIGHT};background-color:{LIGHT};{'}'}\n"
            f"QPushButton:disabled{'{'}border: 3px solid {GREY};border-radius: 5px;color: {WHITE};gridline-color: {GREY};background-color: {GREY};{'}'}\n"
            f"QPushButton:disabled:hover{'{'}background-color: {DARK};{'}'}"
        )
        push_button.setIconSize(QtC.QSize(30, 30))
        push_button.setCheckable(True)
        push_button.setText(self.label)
        layout.addWidget(push_button, int(idx / 2), 0 if divmod(idx, 2)[1] == 0 else 1, 1, 1)
