"""
button box class script
"""
from __future__ import annotations

from functools import partial as ft_partial
from typing import TYPE_CHECKING, Callable, List, Union

import PySide6.QtWidgets as QtW  # type: ignore

from GHEtool.gui.gui_classes.gui_base_class import DARK, GREY, LIGHT, WHITE
from GHEtool.gui.gui_classes.gui_structure_classes.functions import _update_opponent_not_change, _update_opponent_toggle, check
from GHEtool.gui.gui_classes.gui_structure_classes.option import Option

if TYPE_CHECKING:  # pragma: no cover
    from GHEtool.gui.gui_classes.gui_structure_classes.category import Category
    from GHEtool.gui.gui_classes.gui_structure_classes.function_button import FunctionButton
    from GHEtool.gui.gui_classes.gui_structure_classes.hint import Hint


class ButtonBox(Option):
    """
    This class contains all the functionalities of the ButtonBox option in the GUI.
    The ButtonBox can be used to input floating point numbers.
    """

    TOGGLE: bool = True

    def __init__(self, label: str, default_index: int, entries: List[str], category: Category):
        """

        Parameters
        ----------
        label : str
            The label of the ButtonBox
        default_index : int
            The default index of the ButtonBox
        entries : List[str]
            The list of all the different buttons in the ButtonBox
        category : Category
            Category in which the ButtonBox should be placed

        Examples
        --------
        >>> option_buttons = ButtonBox(label='Button box label text',
        >>>                            default_index=0,
        >>>                            entries=['option 1', 'option 2'],
        >>>                            category=category_example)

        Gives:

        .. figure:: _static/Example_Button_Box.PNG

        """
        super().__init__(label, default_index, category)
        self.entries: List[str] = entries
        self.widget: List[QtW.QPushButton] = [QtW.QPushButton(self.default_parent) for _ in self.entries]
        for idx, button in enumerate(self.widget):
            default_value = self.default_value if idx != self.default_value else idx - 1 if idx > 0 else 1
            button.clicked.connect(
                ft_partial(self.update_function, *(button, self.widget[default_value], [but for but in self.widget if but not in [
                    button, self.widget[default_value]]]))
            )
            button.clicked.connect(ft_partial(check, self.linked_options, self, self.get_value()))

    def get_value(self) -> int:
        """
        This function gets the value of the ButtonBox.

        Returns
        -------
        int
            Value of the ButtonBox
        """
        for idx, button in enumerate(self.widget):
            if button.isChecked():
                return idx
        return -1

    def set_value(self, value: int) -> None:
        """
        This function sets the value of the ButtonBox.

        Parameters
        ----------
        value : int
            Value to which the ButtonBox should be set.

        Returns
        -------
        None
        """
        button = self.widget[value]
        if not button.isChecked():
            button.click()

    def _init_links(self) -> None:
        """
        Function on how the links for the ButtonBox should be set.

        Returns
        -------
        None
        """
        current_value: int = self.get_value()
        self.set_value(0 if current_value != 0 else 1)
        self.set_value(current_value)

    def _check_value(self) -> bool:
        """
        This function checks whether or not at least one button is checked.

        Returns
        -------
        bool
            True if at least one button is checked. False otherwise
        """
        return any(button.isChecked() for button in self.widget)

    def add_link_2_show(self, option: Union[Option, Category, FunctionButton, Hint], on_index: int):
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
        In the example below, 'option linked' will be shown if the first ('0') option is selected in the ButtonBox.

        >>> option_buttons.add_link_2_show(option=option_linked, on_index=0)
        """

        self.linked_options.append([option, on_index])

    def change_event(self, function_to_be_called: Callable) -> None:
        """
        This function calls the function_to_be_called whenever the ButtonBox is changed.

        Parameters
        ----------
        function_to_be_called : callable
            Function which should be called

        Returns
        -------
        None
        """
        for button in self.widget:
            button.clicked.connect(function_to_be_called)  # pylint: disable=E1101

    def set_text(self, name: str) -> None:
        """
        This function sets the text of the label and of the different buttons in the ButtonBox.

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
        for button, button_name in zip(self.widget, entry_name[1:]):
            button.setText(f" {button_name.replace('++', ',')} ")

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
        layout = self.create_frame(frame, layout_parent)
        for idx, (entry, widget) in enumerate(zip(self.entries, self.widget)):
            widget.setParent(self.frame)
            widget.setText(f" {entry} ")
            widget.setStyleSheet(
                f"QPushButton{'{'}border: 3px solid {DARK};border-radius: 5px;gridline-color: {LIGHT};background-color: {GREY};font-weight:500;{'}'}"
                f"QPushButton:hover{'{'}border: 3px solid {DARK};background-color:{LIGHT};{'}'}"
                f"QPushButton:checked{'{'}border:3px solid {LIGHT};background-color:{LIGHT};{'}'}\n"
                f"QPushButton:disabled{'{'}border: 3px solid {GREY};border-radius: 5px;color: {WHITE};gridline-color: {GREY};background-color: {GREY};{'}'}\n"
                f"QPushButton:disabled:hover{'{'}background-color: {DARK};{'}'}"
            )
            widget.setCheckable(True)
            widget.setChecked(idx == self.default_value)
            widget.setMinimumHeight(30)
            layout.addWidget(widget)

    def update_function(self, button: QtW.QPushButton, button_opponent: QtW.QPushButton, false_button_list: List[QtW.QPushButton] = None) -> None:
        """
        This function updates which button should be checked/activated or unchecked/deactivated
        This can be done by either the toggle behaviour or not-change behaviour.

        Parameters
        ----------
        button : QtW.QPushButton
            Button which is activated (iff it was not already), and which is deactivated if it was active and is pressed on
        button_opponent : QtW.QPushButton
            Button which is activated if the current button was active and is pressed on
        false_button_list : List[QtW.QPushButton]
            List with other buttons which aren't active

        Returns
        -------
        None
        """
        if self.TOGGLE:
            _update_opponent_toggle(button, button_opponent, false_button_list)
            return
        _update_opponent_not_change(button, false_button_list + [button_opponent])