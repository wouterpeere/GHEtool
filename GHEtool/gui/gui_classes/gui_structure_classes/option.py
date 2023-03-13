"""
option base class script
"""
from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Callable, List, Optional, Tuple, Union

import PySide6.QtWidgets as QtW  # type: ignore

from GHEtool.gui.gui_classes.gui_base_class import WHITE
from GHEtool.gui.gui_classes.gui_structure_classes.aim import Aim

if TYPE_CHECKING:  # pragma: no cover
    from GHEtool.gui.gui_classes.gui_structure_classes import Category



class Option(metaclass=abc.ABCMeta):
    """
    Abstract base class for a gui option.
    """

    default_parent: Optional[QtW.QWidget] = None

    def __init__(self, label: str, default_value: Union[bool, int, float, str], category: Category):
        """
        Parameters
        ----------
        label : str
            The label related to the option
        default_value : bool, int, float, str
            The default value of the option
        category : Category
            The category in which the option should be placed
        """
        self.label_text: str = label
        self.default_value: Union[bool, int, float, str] = default_value
        self.widget: Optional[QtW.QWidget] = None
        self.frame: QtW.QFrame = QtW.QFrame(self.default_parent)
        self.label = QtW.QLabel(self.frame)
        self.linked_options: List[(Option, int)] = []
        self.limit_size: bool = True
        category.list_of_options.append(self)
        self.list_2_check_before_value: List[Tuple[Option, int], Aim] = []

    @abc.abstractmethod
    def get_value(self) -> Union[bool, int, float, str]:
        """
        This function gets the value of the option.

        Returns
        -------
        The value of the option, either a bool, int, float or str
        """

    @abc.abstractmethod
    def set_value(self, value: Union[bool, int, float, str]) -> None:
        """
        This function sets the value of the option.

        Parameters
        ----------
        value : bool, int, float, str
            The value to which the option should be set.

        Returns
        -------
        None
        """

    @abc.abstractmethod
    def _check_value(self) -> bool:
        """
        Abstract function to check whether or not the current value of the option is a valid value.

        Returns
        -------
        bool
            True if the option value is valid
        """

    def add_aim_option_2_be_set_for_check(self, aim_or_option: Union[Tuple[Option, int], Aim]):
        """
        Sometimes, an option should not be check on its valid value. This can be the case when,
        for a specific aim or in a specific case, the current option is not needed. (e.g.,
        the FileNameBox should only be checked whenever an aim is chosen which requires a
        filename).
        This function adds a list of dependencies to the current object, which will be checked
        (meaning: it will be checked if their value is correct) before the value of the self-option
        will be checked.

        Parameters
        ----------
        aim_or_option : aim, (option, int)
            aim or option (with its corresponding index)

        Returns
        -------
        None
        """
        self.list_2_check_before_value.append(aim_or_option)

    def check_value(self) -> bool:
        """
        This function check whether the value of the option is valid.
        Before it checks the value, it makes sure to check all the dependencies in list_2_check_before_value.
        If the check of one of the aims or options in this list is True, True is returned.
        Otherwise the value of the current option is checked.

        Returns
        -------
        bool
            True if the value of the current option is valid.
        """
        if self.frame.isEnabled():
            if not self.list_2_check_before_value:
                return self._check_value()
            if any(aim.widget.isChecked() for aim in self.list_2_check_before_value if isinstance(aim, Aim)) or any(
                    value[0].get_value() == value[1] and not value[0].is_hidden() for value in self.list_2_check_before_value if isinstance(value, tuple)):
                return self._check_value()
        return True

    @abc.abstractmethod
    def create_widget(self, frame: QtW.QFrame, layout_parent: QtW.QLayout, row: int = None, column: int = None) -> None:
        """
        This functions creates the widget, related to the current object, in the frame.

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

    @abc.abstractmethod
    def _init_links(self) -> None:
        """
        Abstract function on how the links for this particular object should be set.

        Returns
        -------
        None
        """

    def init_links(self) -> None:
        """
        This function initiates the links.

        Returns
        -------
        None
        """
        if self.linked_options:
            self._init_links()

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
        self.label_text = name
        self.label.setText(name)

    def deactivate_size_limit(self) -> None:
        """
        This function sets the size limit to False.

        Returns
        -------
        None
        """
        self.limit_size = False

    def create_frame(self, frame: QtW.QFrame, layout_parent: QtW.QLayout, create_spacer: bool = True) -> QtW.QHBoxLayout:
        """
        This function creates the frame for this option in a given frame (can be a page or category).
        If the current label text is "", then the frame attribute is set to the given frame.

        Parameters
        ----------
        frame : QtW.QFrame
            Frame in which this option should be created
        layout_parent : QtW.QLayout
            The layout parent of the current frame
        create_spacer : bool
            True if a spacer should be made

        Returns
        -------
        QtW.QHBoxLayout
            The frame created for this option
        """

        if self.label_text == "":
            self.frame.setParent(None)
            self.frame = frame
            return frame.layout()
        self.frame.setParent(frame)
        self.frame.setFrameShape(QtW.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtW.QFrame.Raised)
        self.frame.setStyleSheet("QFrame {\n" f"	border: 0px solid {WHITE};\n" "	border-radius: 0px;\n" "  }\n")
        layout = QtW.QHBoxLayout(self.frame)
        layout.setSpacing(6)
        layout.setContentsMargins(0, 0, 0, 0)
        self.label.setParent(frame)
        self.label.setText(self.label_text)
        layout.addWidget(self.label)
        if create_spacer:
            spacer = QtW.QSpacerItem(1, 1, QtW.QSizePolicy.Expanding, QtW.QSizePolicy.Minimum)
            layout.addItem(spacer)
        layout_parent.addWidget(self.frame)
        return layout

    def hide(self) -> None:
        """
        This function makes the current frame invisible.

        Returns
        -------
        None
        """
        # if self.is_hidden():
        #     return
        self.frame.hide()
        self.frame.setEnabled(False)
        [option.hide() for option, value in self.linked_options]

    def is_hidden(self) -> bool:
        """
        This function returns a boolean value related to whether or not the option is hidden.

        Returns
        -------
        Bool
            True if the option is hidden
        """
        return self.frame.isHidden()

    def show(self) -> None:
        """
        This function makes the current frame visible.

        Returns
        -------
        None
        """
        # if not self.is_hidden():
        #     return
        self.frame.show()
        self.frame.setEnabled(True)
        [option.show() for option, value in self.linked_options if self.check_linked_value(value)]

    @abc.abstractmethod
    def check_linked_value(self, value: Union[int, Tuple[Optional[int], Optional[int]], Tuple[Optional[float], Optional[float]], str, bool]) -> bool:
        """
        Check if the linked value is the current one then return True

        Parameters
        ----------
        value : int, bool, str, tuple of ints or floats
            value to be checked

        Returns
        -------
        bool
            True if it is the current value
        """

    @abc.abstractmethod
    def change_event(self, function_to_be_called: Callable) -> None:
        """
        This function calls the function_to_be_called whenever the option is changed.

        Parameters
        ----------
        function_to_be_called : callable
            Function which should be called

        Returns
        -------
        None
        """

    def __repr__(self):
        return f'{type(self).__name__}; Label: {self.label_text}; Value: {self.get_value()}'