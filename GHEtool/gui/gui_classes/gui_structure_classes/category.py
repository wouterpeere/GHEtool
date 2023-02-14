"""
category class script
"""
from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING, Union

import PySide6.QtCore as QtC  # type: ignore
import PySide6.QtWidgets as QtW  # type: ignore

from GHEtool.gui.gui_classes.gui_base_class import LIGHT, WHITE
from GHEtool.gui.gui_classes.gui_structure_classes.hint import Hint
from GHEtool.gui.gui_classes.gui_structure_classes.result_text import ResultText

if TYPE_CHECKING:  # pragma: no cover
    from GHEtool.gui.gui_classes.gui_structure_classes.function_button import FunctionButton
    from GHEtool.gui.gui_classes.gui_structure_classes.page import Page
    from GHEtool.gui.gui_classes.gui_structure_classes.option import Option


class Category:
    """
    This class contains all the information for categories - the place where
    options are put.
    """

    default_parent: Optional[QtW.QWidget] = None

    def __init__(self, label: str, page: Page):
        """

        Parameters
        ----------
        label : str
            Label of the category
        page : Page
            Page on which the category should be placed

        Examples
        --------
        >>> category_example = Category(label='Example category',
        >>>                             page=page_example)

        Gives:

        .. figure:: _static/Example_Category.PNG
        """
        self.label_text: str = label
        self.label: QtW.QLabel = QtW.QLabel(self.default_parent)
        self.list_of_options: List[Union[Option, Hint, FunctionButton]] = []
        self.frame: QtW.QFrame = QtW.QFrame(self.default_parent)
        self.graphic_left: Optional[Union[QtW.QGraphicsView, bool]] = None
        self.graphic_right: Optional[Union[QtW.QGraphicsView, bool]] = None
        self.grid_layout: int = 0
        self.layout_frame: Optional[QtW.QVBoxLayout] = None
        page.list_categories.append(self)
        self.options_hidden = []

    def activate_graphic_left(self) -> None:
        """
        This function activates the possibility to show a figure next to the options in
        the category. The figure is shown on the left side of the options.

        Returns
        -------
        None

        Examples
        --------

        >>> self.category_pipe_data.activate_graphic_left()

        The code above makes sure that the plot of the pipe internals is on the left
        of the options within the catgory.
        """
        self.graphic_left = True

    def activate_graphic_right(self) -> None:
        """
        This function activates the possibility to show a figure next to the options in
        the category. The figure is shown on the right side of the options.

        Returns
        -------
        None

        Examples
        --------

        >>> self.category_pipe_data.activate_graphic_right()

        The code above makes sure that the plot of the pipe internals is on the right
        of the options within the catgory.
        """
        self.graphic_right = True

    def activate_grid_layout(self, column: int) -> None:
        """
        This function activates the grid layout of the Category.

        Parameters
        ----------
        column : int
            Number of columns in the grid layout.

        Returns
        -------
        None

        Examples
        --------
        The code below is used to create a grid layout with 5 columns for the monthly
        thermal demands.

        >>> self.category_th_demand.activate_grid_layout(5)
        """
        self.grid_layout = column

    def set_text(self, name: str) -> None:
        """
        This function sets the text in the Category label.

        Parameters
        ----------
        name : str
            Name of the Category

        Returns
        -------
        None
        """
        self.label_text = name
        self.label.setText(name)

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
        self.label.setParent(page)
        self.label.setText(self.label_text)
        self.label.setStyleSheet(
            f"QLabel {'{'}border: 1px solid  {LIGHT};border-top-left-radius: 15px;border-top-right-radius: 15px;background-color:  {LIGHT};padding: 5px 0px;\n"
            f"	color:  {WHITE};font-weight:500;{'}'}"
        )
        self.label.setAlignment(QtC.Qt.AlignCenter | QtC.Qt.AlignVCenter)
        layout.addWidget(self.label)
        self.frame.setParent(page)
        self.frame.setStyleSheet(
            f"QFrame{'{'}border: 1px solid {LIGHT};border-bottom-left-radius: 15px;border-bottom-right-radius: 15px;{'}'}\n"
            f"QLabel{'{'}border: 0px solid {WHITE};{'}'}"
        )
        self.frame.setFrameShape(QtW.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtW.QFrame.Raised)
        layout.addWidget(self.frame)
        spacer_label = QtW.QLabel(page)
        spacer_label.setMinimumHeight(6)
        spacer_label.setMaximumHeight(6)
        layout.addWidget(spacer_label)
        layout_frame_horizontal = QtW.QHBoxLayout(self.frame)
        if self.graphic_left is not None:
            self.graphic_left = self.create_graphic_view(layout_frame_horizontal)

        # check if the category should be made with a grid layout
        if self.grid_layout > 0:
            self.layout_frame = QtW.QGridLayout(self.frame)
            row = 0
            column = 0
            for option in self.list_of_options:
                if isinstance(option, Hint):
                    option.create_widget(self.frame, self.layout_frame, row=row, column=column)
                else:
                    if option.label_text == "":
                        option.deactivate_size_limit()
                    option.create_widget(self.frame, self.layout_frame, row=row, column=column)
                if row == self.grid_layout - 1:
                    row = 0
                    column += 1
                    continue
                row += 1
        else:
            # create category with grid layout
            self.layout_frame = QtW.QVBoxLayout(self.frame)
            for option in self.list_of_options:
                option.create_widget(self.frame, self.layout_frame)

        layout_frame_horizontal.addLayout(self.layout_frame)

        if self.graphic_right is not None:
            self.graphic_right = self.create_graphic_view(layout_frame_horizontal)

    def create_graphic_view(self, layout: QtW.QLayout) -> QtW.QGraphicsView:
        """
        This function creates a graphic view for the case a figure will be shown in the
        Category.

        Parameters
        ----------
        layout : QtW.QLayout
            The layout element where the graphic view should be created in

        Returns
        -------
        QtW.QGraphicsView
            The box where the graphical element will be drawn into
        """
        graphic_view = QtW.QGraphicsView(self.frame)
        graphic_view.setMinimumSize(QtC.QSize(0, 0))
        graphic_view.setMaximumSize(QtC.QSize(100, 16777215))
        graphic_view.setStyleSheet(
            f"QFrame{'{'}border: 1px solid {LIGHT};border-bottom-left-radius: 0px;border-bottom-right-radius: 0px;{'}'}\n"
            f"QLabel{'{'}border: 0px solid {WHITE};{'}'}"
        )

        layout.addWidget(graphic_view)
        return graphic_view

    def hide(self, **kwargs) -> None:
        """
        This function makes the current category invisible and everything on them.
        It makes sure that it only hides the objects that were not already hidden
        due to some links with other options.

        Returns
        -------
        None
        """
        self.frame.hide()
        self.label.hide()
        for option in self.list_of_options:
            # only hide the options that were not already hidden
            # this since otherwise there can be problems with options at the results page
            if option.is_hidden():
                continue
            self.options_hidden.append(option)
            option.hide()

        # when results is given as an argument, the current category is on the result page
        # all ResultTexts should be out of the options_hidden list
        if kwargs.get("results"):
            self.options_hidden = [i for i in self.options_hidden if not isinstance(i, ResultText)]

    def show(self, **kwargs) -> None:
        """
        This function makes the current category visible.

        Returns
        -------
        None
        """
        self.frame.show()
        self.label.show()
        for option in self.options_hidden:
            option.show()
        self.options_hidden = []

    def is_hidden(self) -> bool:
        """
        This function returns a boolean value related to whether or not the category is hidden.

        Returns
        -------
        Bool
            True if the option is hidden
        """
        return self.frame.isHidden()

    def __repr__(self):
        return f'{type(self).__name__}; Label: {self.label_text}'