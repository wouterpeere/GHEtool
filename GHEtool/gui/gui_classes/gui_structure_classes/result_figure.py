"""
result figure class script
"""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

import matplotlib.pyplot as plt
import PySide6.QtCore as QtC  # type: ignore
import PySide6.QtGui as QtG  # type: ignore
import PySide6.QtWidgets as QtW  # type: ignore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from GHEtool import FOLDER
from GHEtool.gui.gui_classes.gui_base_class import LIGHT, WHITE, set_graph_layout
from GHEtool.gui.gui_classes.gui_structure_classes.category import Category

if TYPE_CHECKING:  # pragma: no cover
    from GHEtool.gui.gui_classes.gui_structure_classes.page import Page

class ResultFigure(Category):
    """
    This class contains all the functionalities of the ResultFigure option in the GUI.
    The ResultFigure option can be used to show figurative results in the results page.
    It is a category showing a figure and optionally a couple of FigureOptions to alter this figure.
    """
    def __init__(self, label: str, page: Page):
        """

        Parameters
        ----------
        label : str
            Label text of the ResultFigure
        page : Page
            Page where the ResultFigure should be placed (the result page)

        Examples
        --------
        The code below generates a ResultFigure category named 'Temperature evolution'.

        >>> ResultFigure(label="Temperature evolution",
        >>>              page=self.page_result)

        Gives (note that the FigureOption for the legend is also included):

        .. figure:: _static/Example_ResultFigure.PNG
        """
        super().__init__(label, page)
        self.frame_canvas: QtW.QFrame = QtW.QFrame(self.frame)
        self.layout_frame_canvas: QtW.QVBoxLayout = QtW.QVBoxLayout(self.frame_canvas)
        set_graph_layout()
        self.fig: plt.Figure = plt.figure()
        self.ax: Optional[plt.Axes] = self.fig.add_subplot(111)
        self.canvas: FigureCanvas = FigureCanvas(self.fig)
        # create navigation toolbar and replace icons with white ones
        self.toolbar: NavigationToolbar = NavigationToolbar(self.canvas, None, True)
        for name, icon_name in [("save_figure", "Save_Inv"), ('home', 'Home'), ('zoom', 'Search'), ('back', 'Back'), ('forward', 'Forward'),
                                ('pan', 'Pen'), ('configure_subplots', 'Options'), ('edit_parameters', 'Parameters')]:
            icon = QtG.QIcon()
            icon.addFile(f"{FOLDER}/gui/icons/{icon_name}.svg", QtC.QSize(), QtG.QIcon.Normal, QtG.QIcon.Off)
            self.toolbar._actions[name].setIcon(icon)
        self._kwargs: dict = {}
        self.function_name: str = ""
        self.class_name: str = ""
        self.x_axes_text: str = ''
        self.y_axes_text: str = ''
        self.to_show: bool = True

    def replace_figure(self, fig: plt.Figure) -> None:
        """
        Replace figure in canvas and reset toolbar to new figure.

        Parameters
        ----------
        fig: plt.Figure
            matplotlib figure

        Returns
        -------
        None
        """
        self.fig = fig
        self.ax = fig.get_axes()[0]
        self.ax.set_xlabel(self.x_axes_text)
        self.ax.set_ylabel(self.y_axes_text)
        self.toolbar.home()
        self.canvas.hide()
        self.toolbar.hide()
        canvas = FigureCanvas(self.fig)
        # create navigation toolbar and replace icons with white ones
        toolbar: NavigationToolbar = NavigationToolbar(canvas, self.frame_canvas, True)
        for name, icon_name in [("save_figure", "Save_Inv"), ('home', 'Home'), ('zoom', 'Search'), ('back', 'Back'), ('forward', 'Forward'),
                                ('pan', 'Pen'), ('configure_subplots', 'Options'), ('edit_parameters', 'Parameters')]:
            icon = QtG.QIcon()
            icon.addFile(f"{FOLDER}/gui/icons/{icon_name}.svg", QtC.QSize(), QtG.QIcon.Normal, QtG.QIcon.Off)
            toolbar._actions[name].setIcon(icon)

        self.layout_frame_canvas.replaceWidget(self.canvas, canvas)
        self.layout_frame_canvas.replaceWidget(self.toolbar, toolbar)

        self.canvas = canvas
        self.toolbar = toolbar

    def create_widget(self, page: QtW.QWidget, layout: QtW.QLayout):
        """
        This function creates the frame for this Category on a given page.
        If the current label text is "", then the frame attribute is set to the given frame.
        It populates this category widget with all the options within this category.

        Parameters
        ----------
        page : QtW.QWidget
            Widget (i.e. page) in which this option should be created
        layout : QtW.QLayout
            The layout parent of the current frame

        Returns
        -------
        None
        """
        # create widget as from category
        super().create_widget(page, layout)
        # create frame with no border for the frames inside the NavigationToolbar
        self.frame_canvas.setParent(page)
        self.frame_canvas.setStyleSheet(
            f"QFrame{'{'}border: 0px solid {LIGHT};border-bottom-left-radius: 15px;border-bottom-right-radius: 15px;{'}'}\n"
            f"QLabel{'{'}border: 0px solid {WHITE};{'}'}"
        )
        self.frame_canvas.setFrameShape(QtW.QFrame.StyledPanel)
        self.frame_canvas.setFrameShadow(QtW.QFrame.Raised)
        self.layout_frame.addWidget(self.frame_canvas)
        # set minimal height to ensure a minimal height of the plots
        self.frame_canvas.setMinimumHeight(500)
        # add canvas and toolbar to local frame
        self.layout_frame_canvas.addWidget(self.canvas)
        self.layout_frame_canvas.addWidget(self.toolbar)

    def set_text(self, name: str) -> None:
        """
        This function sets the text in the Figure category label and function button (separated by comma).

        Parameters
        ----------
        name : str
            Name of the Figure category label and function button.\n
            These strings are separated by ","

        Returns
        -------
        None
        """
        entry_name: List[str, str] = name.split(',')
        self.label_text = entry_name[0]
        self.label.setText(self.label_text)
        self.y_axes_text: str = entry_name[1]
        self.x_axes_text: str = entry_name[2]
        self.ax.set_xlabel(self.x_axes_text)
        self.ax.set_ylabel(self.y_axes_text)

    def fig_to_be_shown(self, class_name: str = "Borefield", function_name: str = "print_temperature_profile", **kwargs) -> None:
        """
        This function sets the result that should be shown. It refers to a certain function (function_name) inside the class class_name.
        It is possible to pass through fixed arguments to this function by using **kwargs.
        Arguments that do change, have to be set using a FigureOption.

        Parameters
        ----------
        class_name : str
            The class which contains the variable that should be shown (currently only Borefield)
        function_name : str
            Function that creates the figure. This should be a function existing in the class_name Class.
        **kwargs : dict
            A dictionary with keys being the function arguments which have preset values and the corresponding value.

        Returns
        -------
        None

        Examples
        --------
        The example below shows the temperature profile by calling on the 'print_temperature_profile' function in the Borefield class.

        >>> self.figure_temperature_profile.fig_to_be_shown(class_name="Borefield",
        >>>                                                 function_name="print_temperature_profile")
        """
        self.class_name = class_name
        self.function_name = function_name
        self._kwargs = kwargs

    @property
    def kwargs(self) -> dict:
        """
        This function returns the argument-value pairs for the function that generates the figure
        for this ResultFigure.

        Returns
        -------
        dict
            Dictionary with all the argument names (as keys) and the corresponding values
        """
        kwargs_temp = {}
        for i in self.list_of_options:
            if not i.is_hidden():
                key, value = i.get_value()
                kwargs_temp[key] = value
        return {**self._kwargs, **kwargs_temp}

    def show(self, results: bool = False) -> None:
        """
        This function shows the ResultFigure option.
        It makes sure that the figure is not shown when loading the entire GUI,
        but only when the result page is opened.

        Parameters
        ----------
        results : bool
            True if this function is called w.r.t. result page

        Returns
        -------
        None
        """
        if self.to_show:
            super(ResultFigure, self).show()
        if results:
            return
        self.to_show = True

    def hide(self, results: bool = False) -> None:
        """
        This function hides the ResultFigure option.
        It also sets the to_show parameter to False, so the Figure is not randomly showed
        when the result page is opened.

        Parameters
        ----------
        results : bool
            True if the hide function is called w.r.t. result page

        Returns
        -------
        None
        """
        super(ResultFigure, self).hide()
        if results:
            return
        self.to_show = False