"""
function button class
"""

from __future__ import annotations

import abc
from typing import Callable, List, Optional, Union, Protocol
import PySide6.QtCore as QtC  # type: ignore
import PySide6.QtGui as QtG  # type: ignore
import PySide6.QtWidgets as QtW  # type: ignore
from GHEtool import FOLDER

from GHEtool.gui.gui_classes.gui_base_class import  WHITE

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


class FunctionButton:
    """
    This class contains all the functionalities of the FunctionButton option in the GUI.
    The FunctionButton can be used to couple a button press to a function call.
    """
    default_parent: Optional[QtW.QWidget] = None

    def __init__(self, button_text: str, icon: str, category: Category):
        """

        Parameters
        ----------
        button_text : str
            The label of the FunctionButton
        icon : str
            Location of the icon for the FunctionButton
        category : Category
            Category in which the FunctionButton should be placed

        Examples
        --------
        >>> function_example = FunctionButton(button_text='Press Here to activate function',
        >>>                                   icon=':/icons/icons/example_icon.svg',
        >>>                                   category=category_example)

        Gives:

        .. figure:: _static/Example_Function_Button.PNG

        """
        self.button_text: str = button_text
        self.icon: str = icon
        self.frame: QtW.QFrame = QtW.QFrame(self.default_parent)
        self.button: QtW.QPushButton = QtW.QPushButton(self.default_parent)
        category.list_of_options.append(self)

    def create_widget(self, frame: QtW.QFrame, layout_parent: QtW.QLayout):
        """
        This functions creates the FunctionButton in the frame.

        Parameters
        ----------
        frame : QtW.QFrame
            The frame object in which the widget should be created
        layout_parent : QtW.QLayout
            The parent layout of the current widget

        Returns
        -------
        None
        """
        self.button.setParent(frame)
        self.button.setText(f"  {self.button_text}  ")
        icon = QtG.QIcon()
        # icon11.addPixmap(QtGui_QPixmap(icon), QtGui_QIcon.Normal, QtGui_QIcon.Off)
        icon.addFile(f'{FOLDER}/gui/icons/{self.icon}')
        self.button.setIcon(icon)
        self.button.setIconSize(QtC.QSize(20, 20))
        self.button.setMinimumWidth(100)
        self.button.setMinimumHeight(35)
        self.frame.setParent(frame)
        self.frame.setFrameShape(QtW.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtW.QFrame.Raised)
        self.frame.setStyleSheet(f"QFrame{'{'}border: 0px solid {WHITE};border-radius: 0px;{'}'}")
        layout = QtW.QHBoxLayout(self.frame)
        layout.setSpacing(6)
        layout.setContentsMargins(0, 0, 0, 0)
        spacer1 = QtW.QSpacerItem(1, 1, QtW.QSizePolicy.Expanding, QtW.QSizePolicy.Minimum)
        layout.addItem(spacer1)

        layout.addWidget(self.button)
        spacer2 = QtW.QSpacerItem(1, 1, QtW.QSizePolicy.Expanding, QtW.QSizePolicy.Minimum)
        layout.addItem(spacer2)

        layout_parent.addWidget(self.frame)

    def hide(self) -> None:
        """
        This function makes the FunctionButton invisible.

        Returns
        -------
        None
        """
        self.frame.hide()

    def show(self) -> None:
        """
        This function makes the current FunctionButton visible.

        Returns
        -------
        None
        """
        self.frame.show()

    def is_hidden(self) -> bool:
        """
        This function returns a boolean value related to whether or not the FunctionButton is hidden.

        Returns
        -------
        Bool
            True if the option is hidden
        """
        return self.frame.isHidden()

    def set_text(self, name: str):
        """
        This function sets the text of the FunctionButton.

        Parameters
        ----------
        name : str
            Text of the FunctionButton

        Returns
        -------
        None
        """
        self.button_text: str = name
        self.button.setText(self.button_text)

    def change_event(self, function_to_be_called: Callable, *args) -> None:
        """
        This function calls the function_to_be_called whenever the FunctionButton is pressed.

        Parameters
        ----------
        function_to_be_called : callable
            Function which should be called
        args
            Arguments to be passed through to the function_to_be_called

        Returns
        -------
        None
        """
        self.button.clicked.connect(lambda: function_to_be_called(*args))