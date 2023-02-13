"""
script which contain basic gui structure functions
"""

from __future__ import annotations

from typing import List, Union, Protocol

import PySide6.QtWidgets as QtW  # type: ignore

def _update_opponent_not_change(button: QtW.QPushButton, false_button_list: List[QtW.QPushButton] = None):
    """
    This function controls the behaviour of the buttons.
    This function makes sure that whenever a button is active, all other buttons except the current one,
    are inactive. If the current button is already active, nothing changes.

    Parameters
    ----------
    button : QtW.QPushButton
        Button which is activated (or pressed on)
    false_button_list : List[QtW.QPushButton]
        List with other buttons which aren't active

    Returns
    -------
    None
    """
    if not button.isChecked():
        button.setChecked(True)
        return
    for but in false_button_list:
        if not but == button:
            but.setChecked(False)


def _update_opponent_toggle(button: QtW.QPushButton, button_opponent: QtW.QPushButton, false_button_list: List[QtW.QPushButton] = None):
    """
    This function controls the behaviour of the buttons, specifically the toggle behaviour.
    This function makes sure that whenever a button is pressed, all other buttons except the current one,
    are inactive. If the current button is already active and it is still pressed, the current button
    is turned inactive and the button_opponent is made active.

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
    button_opponent.setChecked(not button.isChecked())
    if false_button_list is not None:
        for false_button in false_button_list:
            false_button.setChecked(False)


class Option(Protocol):

    def get_value(self) -> any:
        """get the value"""

    def hide(self):
        """hides the option"""

    def show(self):
        """shows the option"""

    def is_hidden(self) -> bool:
        """checks if the option is hidden"""


class Aim(Protocol):
    widget: QtW.QPushButton
    list_options: List[Option]

def check(linked_options: List[(Union[Option, List[Option]], int)], option_input: Option, index: int):
    """
    This function makes sure that the linked_options will be hidden when the index of the option_input
    is different from the index provided per Option in the linked_options list.
    When it is equal, the linked_option is shown.

    Parameters
    ----------
    linked_options : List[(Options, int) or  (List[Options], int)]
        List with linked option, composed of either an Option-index pair or a list of options-index pair
    option_input : Option
        The option which determines the visibility of the linked_options
    index : int
        The index which determines the visibility of the linked_options

    Returns
    -------
    None
    """
    index = index if option_input.get_value() == index else option_input.get_value()
    list_false = [(option, idx) for option, idx in linked_options if idx != index]
    list_true = [(option, idx) for option, idx in linked_options if idx == index]
    for option, idx in list_false:
        if isinstance(option, list):
            for opt in option:
                opt.hide()
            continue
        option.hide()
    for option, idx in list_true:
        if isinstance(option, list):
            for opt in option:
                opt.show()
            continue
        option.show()




def check_aim_options(list_aim: List[Aim]) -> None:
    """
    This function makes sure that all the options, that are linked to the Aim, are made invisible
    when the aim is not selected and that the options, linked to the Aim, will be shown whenever this Aim
    is selected.

    Parameters
    ----------
    list_aim : List[Aim]
        List with all the aims in the GUI

    Returns
    -------
    None
    """
    list_false = [aim for aim in list_aim if not aim.widget.isChecked()]
    list_true = [aim for aim in list_aim if aim.widget.isChecked()]
    # hide all the options related to the not-checked aims
    for aim in list_false:
        for option in aim.list_options:
            if isinstance(option, list):
                for opt in option:
                    opt.hide()
                continue
            option.hide()
    # show all the options related to the checked aims
    for aim in list_true:
        for option in aim.list_options:
            if isinstance(option, list):
                for opt in option:
                    opt.show()
                continue
            option.show()


def show_linked_options(options_list: List[Option]) -> None:
    """
    This function makes sure that for a given list of options, all linked options are shown if the option
    itself is not hidden.

    Parameters
    ----------
    options_list : List(Option)
        A list of options which have linked options

    Returns
    -------
    None
    """
    for option in options_list:
        if option.is_hidden():
            continue
        # show already shown option to evoke linked options
        option.show()