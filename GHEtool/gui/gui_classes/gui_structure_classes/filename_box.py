"""
filename box
"""
from __future__ import annotations

from os.path import exists
from pathlib import Path
from typing import TYPE_CHECKING, Callable

import PySide6.QtCore as QtC  # type: ignore
import PySide6.QtWidgets as QtW  # type: ignore

from GHEtool.gui.gui_classes.gui_base_class import DARK, LIGHT, LIGHT_SELECT, WHITE
from GHEtool.gui.gui_classes.gui_structure_classes.option import Option

if TYPE_CHECKING:  # pragma: no cover
    from GHEtool.gui.gui_classes.gui_structure_classes.category import Category


class FileNameBox(Option):
    """
    This class contains all the functionalities of the FileNameBox (filename input box) option in the GUI.
    The FileNameBox can be used to import a datafile.
    """
    def __init__(self, label: str, default_value: str, dialog_text: str, error_text: str, status_bar: QtW.QStatusBar, category: Category):
        """

        Parameters
        ----------
        label : str
            The label of the FileNameBox
        default_value : int
            The default value of the FileNameBox
        dialog_text : str
            Text to be displayed in the top bar of the dialog box
        error_text : str
            Error text be be shown in the status_bar
        status_bar : QtW.QStatusBar
            Status bar to put in an error message related to the file import
        category : Category
            Category in which the FileNameBox should be placed

        Examples
        --------
        >>> option_file = FileNameBox(label='File name box label text',
        >>>                           default_value='example_file.XX',
        >>>                           dialog_text='Choose *.XX file',
        >>>                           error_text='no file found',
        >>>                           status_bar=status_bar,
        >>>                           category=category_example)

        Gives:

        .. figure:: _static/Example_Filename.PNG

        """
        super().__init__(label, default_value, category)
        self.widget: QtW.QLineEdit = QtW.QLineEdit(self.default_parent)
        self.dialog_text: str = dialog_text
        self.error_text: str = error_text
        self.status_bar: QtW.QStatusBar = status_bar
        self.button: QtW.QPushButton = QtW.QPushButton(self.default_parent)

    def get_value(self) -> str:
        """
        This function returns the filename (with path) which is put into the FileNameBox.

        Returns
        -------
        str
            Filename (with path)
        """
        return self.widget.text()

    def set_value(self, value: str) -> None:
        """
        This function sets the value of the FileNameBox.

        Parameters
        ----------
        value : int
            Value to which the the FileNameBox should be set.

        Returns
        -------
        None
        """
        self.widget.setText(value)

    def _init_links(self) -> None:
        """
        Function on how the links for the FileNameBox should be set.

        Returns
        -------
        None
        """
        current_value: str = self.get_value()
        self.set_value('test')
        self.set_value(current_value)

    def _check_value(self) -> bool:
        """
        This function checks whether or not a value is given in the FileNameBox.

        Returns
        -------
        bool
            True if a value is given in the FileNameBox. False otherwise
        """
        return exists(self.widget.text())

    def check_linked_value(self, value: str) -> bool:
        """
        This function checks if the linked "option" should be shown.

        Parameters
        ----------
        value : str
            str on which the option should be shown

        Returns
        -------
        bool
            True if the linked "option" should be shown
        """
        return self.get_value() == value

    def change_event(self, function_to_be_called: Callable) -> None:
        """
        This function calls the function_to_be_called whenever the FileNameBox is changed.

        Parameters
        ----------
        function_to_be_called : callable
            Function which should be called

        Returns
        -------
        None

        Examples
        --------
        >>> self.option_filename.change_event(self.fun_update_combo_box_data_file)

        The code above is used in gui_structure.py to update the information related to the input of hourly data,
        whenever a new file is selected.

        """
        self.widget.textChanged.connect(function_to_be_called)  # pylint: disable=E1101

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
        layout = self.create_frame(frame, layout_parent, False)
        self.widget.setParent(self.frame)
        self.widget.setStyleSheet(
            f"QLineEdit{'{'}border: 3px solid {LIGHT};border-radius: 5px;color: {WHITE};gridline-color: {LIGHT};background-color: {LIGHT};font-weight:500;\n"
            f"selection-background-color: {LIGHT_SELECT};{'}'}\n"
            f"QLineEdit:hover{'{'}background-color: {DARK};{'}'}"
        )
        self.widget.setText(self.default_value)
        layout.addWidget(self.widget)
        self.button.setParent(self.frame)
        self.button.setMinimumSize(QtC.QSize(30, 30))
        self.button.setMaximumSize(QtC.QSize(30, 30))
        self.button.setText("...")
        self.button.clicked.connect(self.fun_choose_file)  # pylint: disable=E1101
        layout.addWidget(self.button)

    def fun_choose_file(self) -> None:
        """
        This function opens a file selector, with which the filename path can be selected.
        This is automatically added to the FileNameBox.

        Returns
        -------
        None
        """
        # try to ask for a file otherwise show message in status bar
        filename = QtW.QFileDialog.getOpenFileName(self.frame, caption=self.dialog_text, filter="(*.csv)", dir=str(Path.home()))
        if filename[0] == "":
            self.status_bar.showMessage(self.error_text, 5000)
        self.widget.setText(filename[0])
