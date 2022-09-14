from __future__ import annotations

import abc
from functools import partial as ft_partial
from typing import Callable, List, Optional, Union

import PySide6.QtCore as QtC
import PySide6.QtGui as QtG
import PySide6.QtWidgets as QtW

from .gui_main import DARK, GREY, LIGHT, WARNING, WHITE, LIGHT_SELECT


def update_opponent(button: QtW.QPushButton, button_opponent: QtW.QPushButton, false_button_list: List[QtW.QPushButton] = None):
    button_opponent.setChecked(not button.isChecked())
    if false_button_list is not None:
        for false_button in false_button_list:
            false_button.setChecked(False)


class Option(metaclass=abc.ABCMeta):
    def __init__(self, default_parent: QtW.QWidget, label: str, default_value: Union[bool, int, float, str], category: Category):

        self.label_text: str = label
        self.default_value: Union[bool, int, float, str] = default_value
        self.widget: Optional[QtW.QWidget] = None
        self.frame: QtW.QFrame = QtW.QFrame(default_parent)
        self.label = QtW.QLabel(self.frame)
        self.linked_options: List[(Option, int)] = []
        self.limit_size: bool = True
        category.list_of_options.append(self)

    @abc.abstractmethod
    def get_value(self) -> Union[bool, int, float, str]:
        pass

    @abc.abstractmethod
    def set_value(self, value: Union[bool, int, float, str]) -> None:
        pass

    @abc.abstractmethod
    def create_widget(self, frame: QtW.QFrame, layout: QtW.QLayout, row: int = None, column: int = None) -> None:
        pass

    @abc.abstractmethod
    def _init_links(self) -> None:
        pass

    def init_links(self) -> None:
        if self.linked_options:
            self._init_links()

    def set_text(self, name: str):
        self.label_text = name
        self.label.setText(name)

    def deactivate_size_limit(self):
        self.limit_size = False

    def create_frame(self, frame: QtW.QFrame, layout_parent: QtW.QLayout, create_spacer: bool = True) -> QtW.QHBoxLayout:
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
        self.frame.hide()

    def show(self) -> None:
        self.frame.show()

    @abc.abstractmethod
    def change_event(self, function_to_be_called: Callable) -> None:
        pass


def check(linked_options: List[(Union[Option, List[Option]], int)], option: Option, index: int):
    index = index if option.get_value() == index else option.get_value()
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


class FloatBox(Option):
    def __init__(
        self,
        default_parent: QtW.QWidget,
        label: str,
        default_value: float,
        category: Category,
        decimal_number: int = 0,
        minimal_value: float = 0.0,
        maximal_value: float = 100.0,
        step: float = 1.0,
    ):
        super().__init__(default_parent, label, default_value, category)
        self.decimal_number: int = decimal_number
        self.minimal_value: float = minimal_value
        self.maximal_value: float = maximal_value
        self.step: float = step
        self.widget: QtW.QDoubleSpinBox = QtW.QDoubleSpinBox(default_parent)

    def get_value(self) -> float:
        return self.widget.value()

    def set_value(self, value: float) -> None:
        self.widget.setValue(value)

    def _init_links(self) -> None:
        current_value: float = self.get_value()
        self.set_value(current_value*1.1)
        self.set_value(current_value)

    def change_event(self, function_to_be_called: Callable) -> None:
        self.widget.valueChanged.connect(function_to_be_called)

    def create_widget(self, frame: QtW.QFrame, layout_parent: QtW.QLayout, row: int = None, column: int = None) -> None:
        layout = self.create_frame(frame, layout_parent)
        self.widget.setParent(self.frame)
        self.widget.setStyleSheet(
            f"QDoubleSpinBox{'{'}selection-color: {WHITE};\n"
            f"selection-background-color: {LIGHT};\n"
            f"border: 1px solid {WHITE};\n"
            'font: 11pt "Lexend Deca Light";}\n'
        )
        self.widget.setAlignment(QtC.Qt.AlignRight | QtC.Qt.AlignTrailing | QtC.Qt.AlignVCenter)
        self.widget.setProperty("showGroupSeparator", True)
        self.widget.setMinimum(self.minimal_value)
        self.widget.setMaximum(self.maximal_value)
        self.widget.setDecimals(self.decimal_number)
        self.widget.setValue(self.default_value)
        self.widget.setSingleStep(self.step)
        if self.limit_size:
            self.widget.setMaximumWidth(100)
            self.widget.setMinimumWidth(100)
        self.widget.setMinimumHeight(28)
        if row is not None and isinstance(layout_parent, QtW.QGridLayout):
            layout_parent.addWidget(self.widget, column, row)
            return
        layout.addWidget(self.widget)


class IntBox(Option):
    def __init__(
        self, default_parent: QtW.QWidget, label: str, default_value: int, category: Category, minimal_value: int = 0, maximal_value: int = 100, step: int = 1
    ):
        super().__init__(default_parent, label, default_value, category)
        self.minimal_value: int = minimal_value
        self.maximal_value: int = maximal_value
        self.step: int = step
        self.widget: QtW.QSpinBox = QtW.QSpinBox(default_parent)

    def get_value(self) -> int:
        return self.widget.value()

    def set_value(self, value: int) -> None:
        self.widget.setValue(value)

    def _init_links(self) -> None:
        current_value: int = self.get_value()
        self.set_value(self.minimal_value if current_value == self.minimal_value else self.minimal_value)
        self.set_value(current_value)

    def change_event(self, function_to_be_called: Callable) -> None:
        self.widget.valueChanged.connect(function_to_be_called)

    def create_widget(self, frame: QtW.QFrame, layout_parent: QtW.QLayout, row: int = None, column: int = None) -> None:
        layout = self.create_frame(frame, layout_parent)
        self.widget.setParent(self.frame)
        self.widget.setStyleSheet(
            "QSpinBox{\n"
            f"selection-color: {WHITE};\n"
            f"selection-background-color: {LIGHT};\n"
            f"border: 1px solid {WHITE};\n"
            'font: 11pt "Lexend Deca Light";}\n'
        )
        self.widget.setAlignment(QtC.Qt.AlignRight | QtC.Qt.AlignTrailing | QtC.Qt.AlignVCenter)
        self.widget.setMinimum(self.minimal_value)
        self.widget.setMaximum(self.maximal_value)
        self.widget.setValue(self.default_value)
        self.widget.setSingleStep(self.step)
        self.widget.setMaximumWidth(100)
        self.widget.setMinimumWidth(100)
        self.widget.setMinimumHeight(28)
        if row is not None and isinstance(layout_parent, QtW.QGridLayout):
            layout_parent.addWidget(self.widget, column, row)
            return
        layout.addWidget(self.widget)


class ButtonBox(Option):
    def __init__(self, default_parent: QtW.QWidget, label: str, default_index: int, entries: List[str], category: Category):
        super().__init__(default_parent, label, default_index, category)
        self.entries: List[str] = entries
        self.widget: List[QtW.QPushButton] = [QtW.QPushButton(default_parent) for _ in self.entries]

    def get_value(self) -> int:
        for idx, button in enumerate(self.widget):
            if button.isChecked():
                return idx
        return -1

    def set_value(self, index: int) -> None:
        for idx, button in enumerate(self.widget):
            if idx == index:
                if not button.isChecked():
                    button.click()
                break

    def _init_links(self) -> None:
        current_value: int = self.get_value()
        self.set_value(0 if current_value != 0 else 1)
        self.set_value(current_value)

    def add_linked_option(self, option: Union[Option, Category, FunctionButton], index: int):
        self.linked_options.append([option, index])

    def change_event(self, function_to_be_called: Callable) -> None:
        for button in self.widget:
            button.clicked.connect(function_to_be_called)

    def set_text(self, name: str):
        entry_name: List[str, str] = name.split(',')
        self.label_text = entry_name[0]
        self.label.setText(self.label_text)
        for button, button_name in zip(self.widget, entry_name[1:]):
            button.setText(f" {button_name.replace('++', ',')} ")

    def create_widget(self, frame: QtW.QFrame, layout_parent: QtW.QLayout, row: int = None, column: int = None) -> None:
        layout = self.create_frame(frame, layout_parent)
        for idx, (entry, widget) in enumerate(zip(self.entries, self.widget)):
            widget.setParent(self.frame)
            widget.setText(f" {entry} ")
            widget.setStyleSheet(
                "QPushButton{\n"
                f"border: 3px solid {DARK};\n"
                "border-radius: 5px;\n"
                f"gridline-color: {LIGHT};\n"
                f"background-color: {GREY};\n"
                "font-weight:500;}\n"
                "QPushButton:hover{\n"
                f"border: 3px solid {DARK};\n"
                f"background-color:{LIGHT};\n"
                "}\n"
                "QPushButton:checked{\n"
                f"border:3px solid {LIGHT};\n"
                f"background-color:{LIGHT};\n"
                "}\n"
                "QPushButton:disabled{\n"
                f"border: 3px solid {GREY};\n"
                "border-radius: 5px;\n"
                f"color: {WHITE};\n"
                f"gridline-color: {GREY};\n"
                f"background-color: {GREY};\n"
                "}\n"
                "QPushButton:disabled:hover{\n"
                f"background-color: {DARK};\n"
                "}"
            )
            widget.setCheckable(True)
            widget.setChecked(idx == self.default_value)
            widget.setMinimumHeight(30)
            layout.addWidget(widget)
        for idx, button in enumerate(self.widget):
            default_value = self.default_value if idx != self.default_value else idx - 1 if idx > 0 else 1
            button.clicked.connect(
                ft_partial(update_opponent, button, self.widget[default_value], [but for i, but in enumerate(self.widget) if i not in [idx, default_value]])
            )
            button.clicked.connect(ft_partial(check, self.linked_options, self, self.get_value()))


class ListBox(Option):
    def __init__(self, default_parent: QtW.QWidget, label: str, default_index: int, entries: List[str], category: Category):
        super().__init__(default_parent, label, default_index, category)
        self.entries: List[str] = entries
        self.widget: QtW.QComboBox = QtW.QComboBox(default_parent)

    def get_value(self) -> int:
        return self.widget.currentIndex()

    def set_value(self, index: int) -> None:
        self.widget.setCurrentIndex(index)

    def _init_links(self) -> None:
        current_value: int = self.get_value()
        self.set_value(0 if current_value != 0 else 1)
        self.set_value(current_value)

    def add_linked_option(self, option: Union[Option, Category, FunctionButton], index: int):
        self.linked_options.append([option, index])

    def change_event(self, function_to_be_called: Callable) -> None:
        self.widget.currentIndexChanged.connect(function_to_be_called)

    def create_widget(self, frame: QtW.QFrame, layout_parent: QtW.QLayout, row: int = None, column: int = None) -> None:
        layout = self.create_frame(frame, layout_parent)
        self.widget.setParent(self.frame)
        self.widget.setStyleSheet(
            "QFrame {\n"
            f"	border: 1px solid {WHITE};\n"
            "	border-bottom-left-radius: 0px;\n"
            "	border-bottom-right-radius: 0px;\n"
            "}"
            "QComboBox{\n"
            f"border: 1px solid {WHITE};\n"
            "border-bottom-left-radius: 0px;\n"
            "border-bottom-right-radius: 0px;\n"
            "}\n"
        )
        self.widget.addItems(self.entries)
        self.widget.setCurrentIndex(self.default_value)
        self.widget.setMaximumWidth(100)
        self.widget.setMinimumWidth(100)
        self.widget.currentIndexChanged.connect(ft_partial(check, self.linked_options, self))
        if row is not None and isinstance(layout_parent, QtW.QGridLayout):
            layout_parent.addWidget(self.widget, column, row)
            return
        layout.addWidget(self.widget)


class FileNameBox(Option):
    def __init__(
            self, default_parent: QtW.QWidget, label: str, default_value: str, dialog_text: str, error_text: str, status_bar: QtW.QStatusBar,
            category: Category
    ):
        super().__init__(default_parent, label, default_value, category)
        self.widget: QtW.QLineEdit = QtW.QLineEdit(default_parent)
        self.dialog_text: str = dialog_text
        self.error_text: str = error_text
        self.status_bar: QtW.QStatusBar = status_bar

    def get_value(self) -> str:
        return self.widget.text()

    def set_value(self, filename: str) -> None:
        self.widget.setText(filename)

    def _init_links(self) -> None:
        current_value: str = self.get_value()
        self.set_value('test')
        self.set_value(current_value)

    def change_event(self, function_to_be_called: Callable) -> None:
        self.widget.textChanged.connect(function_to_be_called)

    def create_widget(self, frame: QtW.QFrame, layout_parent: QtW.QLayout, row: int = None, column: int = None) -> None:
        layout = self.create_frame(frame, layout_parent, False)
        self.widget.setParent(self.frame)
        self.widget.setStyleSheet(
            f"QLineEdit{'{'}border: 3px solid {LIGHT};\n"
            "border-radius: 5px;\n"
            f"color: {WHITE};\n"
            f"gridline-color: {LIGHT};\n"
            f"background-color: {LIGHT};\n"
            "font-weight:500;\n"
            f"selection-background-color: {LIGHT_SELECT};{'}'}\n"
            f"QLineEdit:hover{'{'}background-color: {DARK};{'}'}"
        )
        layout.addWidget(self.widget)
        button = QtW.QPushButton(self.frame)
        button.setMinimumSize(QtC.QSize(30, 30))
        button.setMaximumSize(QtC.QSize(30, 30))
        button.setText("...")
        button.clicked.connect(self.fun_choose_file)
        layout.addWidget(button)

    def fun_choose_file(self) -> None:
        """
        function to choose data file Import
        :return: None
        """
        # try to ask for a file otherwise show message in status bar
        try:
            filename = QtW.QFileDialog.getOpenFileName(self.frame, caption=self.dialog_text, filter="(*.csv)")
            self.widget.setText(filename[0])
        # show warning if no file is selected in status bar for 5 seconds
        except FileNotFoundError:
            self.status_bar.showMessage(self.error_text, 5000)


class Hint:
    def __init__(self, default_parent: QtW.QWidget, hint: str, category: Category, warning: bool = False):
        self.hint: str = hint
        self.label: QtW.QLabel = QtW.QLabel(default_parent)
        self.warning = warning
        category.list_of_options.append(self)

    def create_widget(self, frame: QtW.QFrame, layout_parent: QtW.QLayout, row: int = None, column: int = None) -> None:
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
        self.label.hide()

    def show(self) -> None:
        self.label.show()

    def set_text(self, name: str):
        self.hint: str = name
        self.label.setText(self.hint)


class FunctionButton:
    def __init__(self, default_parent: QtW.QWidget, button_text: str, icon: str, category: Category):
        self.button_text: str = button_text
        self.icon: str = icon
        self.frame: QtW.QFrame = QtW.QFrame(default_parent)
        self.button: QtW.QPushButton = QtW.QPushButton(default_parent)
        category.list_of_options.append(self)

    def create_widget(self, frame: QtW.QFrame, layout_parent: QtW.QLayout):
        self.button.setParent(frame)
        self.button.setText(f"  {self.button_text}  ")
        icon = QtG.QIcon()
        # icon11.addPixmap(QtGui_QPixmap(icon), QtGui_QIcon.Normal, QtGui_QIcon.Off)
        icon.addFile(self.icon)
        self.button.setIcon(icon)
        self.button.setIconSize(QtC.QSize(20, 20))
        self.button.setMinimumWidth(100)
        self.button.setMinimumHeight(35)
        self.frame.setParent(frame)
        self.frame.setFrameShape(QtW.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtW.QFrame.Raised)
        self.frame.setStyleSheet("QFrame {\n" f"	border: 0px solid {WHITE};\n" "	border-radius: 0px;\n" "  }\n")
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
        self.frame.hide()

    def show(self) -> None:
        self.frame.show()

    def set_text(self, name: str):
        self.button_text: str = name
        self.button.setText(self.button_text)

    def change_event(self, function_to_be_called: Callable) -> None:
        self.button.clicked.connect(function_to_be_called)


class Category:
    def __init__(self, default_parent: QtW.QWidget, label: str, page: Page):
        self.label_text: str = label
        self.label: QtW.QLabel = QtW.QLabel(default_parent)
        self.list_of_options: List[Union[Option, Hint, FunctionButton]] = []
        self.frame: QtW.QFrame = QtW.QFrame(default_parent)
        self.graphic_left: Optional[Union[QtW.QGraphicsView, bool]] = None
        self.graphic_right: Optional[Union[QtW.QGraphicsView, bool]] = None
        self.grid_layout: int = 0
        page.list_categories.append(self)

    def activate_graphic_left(self):
        self.graphic_left = True

    def activate_graphic_right(self):
        self.graphic_right = True

    def activate_grid_layout(self, column: int):
        self.grid_layout = column

    def set_text(self, name: str):
        self.label_text = name
        self.label.setText(name)

    def create_widget(self, page: QtW.QWidget, layout: QtW.QLayout):
        self.label.setParent(page)
        self.label.setText(self.label_text)
        self.label.setStyleSheet(
            "QLabel {\n"
            f"	border: 1px solid  {LIGHT};\n"
            "	border-top-left-radius: 15px;\n"
            "	border-top-right-radius: 15px;\n"
            f"	background-color:  {LIGHT};\n"
            "	padding: 5px 0px;\n"
            f"	color:  {WHITE};\n"
            "font-weight:500;\n"
            "}"
        )
        self.label.setAlignment(QtC.Qt.AlignCenter | QtC.Qt.AlignVCenter)
        layout.addWidget(self.label)
        self.frame.setParent(page)
        self.frame.setStyleSheet(
            "QFrame {\n"
            f"	border: 1px solid {LIGHT};\n"
            "	border-bottom-left-radius: 15px;\n"
            "	border-bottom-right-radius: 15px;\n"
            "}\n"
            "QLabel{\n"
            f"border: 0px solid {WHITE};"
            "\n}"
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
        if self.grid_layout > 0:
            layout_frane = QtW.QGridLayout(self.frame)
            row = 0
            column = 0
            for option in self.list_of_options:
                if isinstance(option, Hint):
                    option.create_widget(self.frame, layout_frane, row, column)
                else:
                    option.deactivate_size_limit() if option.label_text == "" else None
                    option.create_widget(self.frame, layout_frane, row, column)
                if row == self.grid_layout - 1:
                    row = 0
                    column += 1
                    continue
                row += 1
        else:
            layout_frane = QtW.QVBoxLayout(self.frame)
            for option in self.list_of_options:
                option.create_widget(self.frame, layout_frane)

        layout_frame_horizontal.addLayout(layout_frane)

        if self.graphic_right is not None:
            self.graphic_right = self.create_graphic_view(layout_frame_horizontal)

    def create_graphic_view(self, layout: QtW.QLayout) -> QtW.QGraphicsView:
        graphic_view = QtW.QGraphicsView(self.frame)
        graphic_view.setMinimumSize(QtC.QSize(0, 0))
        graphic_view.setMaximumSize(QtC.QSize(100, 16777215))
        graphic_view.setStyleSheet(
            "QFrame {\n"
            f"	border: 1px solid {LIGHT};\n"
            "	border-bottom-left-radius: 0px;\n"
            "	border-bottom-right-radius: 0px;\n"
            "}\n"
            f"QLabel{'{'}border: 0px solid {WHITE};{'}'}"
        )

        layout.addWidget(graphic_view)
        return graphic_view

    def hide(self) -> None:
        self.frame.hide()
        self.label.hide()

    def show(self) -> None:
        self.frame.show()
        self.label.show()


class Aim:
    def __init__(self, default_parent: QtW.QWidget, label: str, icon: str, page: Page):
        self.label: str = label
        self.icon: str = icon
        self.widget: QtW.QPushButton = QtW.QPushButton(default_parent)
        self.list_options: List[Union[Option, Category, FunctionButton]] = []
        page.upper_frame.append(self)

    def change_event(self, function_to_be_called: Callable) -> None:
        self.widget.clicked.connect(function_to_be_called)

    def add_linked_option(self, option: Union[Option, Category, FunctionButton]):
        self.list_options.append(option)

    def create_widget(self, frame: QtW.QFrame, layout: QtW.QGridLayout, idx: int) -> None:
        icon11 = QtG.QIcon()
        # icon11.addPixmap(QtGui_QPixmap(icon), QtGui_QIcon.Normal, QtGui_QIcon.Off)
        icon11.addFile(self.icon)
        self.widget.setParent(frame)
        push_button = self.widget
        push_button.setIcon(icon11)
        push_button.setMinimumSize(QtC.QSize(0, 60))
        push_button.setMaximumSize(QtC.QSize(16777215, 60))
        push_button.setStyleSheet(
            f"QPushButton{'{'}border: 3px solid {DARK};\n"
            "border-radius: 15px;\n"
            f"color: {WHITE};\n"
            f"gridline-color: {LIGHT};\n"
            f"background-color: {GREY};\n"
            "font-weight:500;}\n"
            f"QPushButton:hover{'{'}border: 3px solid {DARK};\n"
            f"background-color:{LIGHT};{'}'}\n"
            f"QPushButton:checked{'{'}border:3px solid {LIGHT};\n"
            f"background-color:{LIGHT};{'}'}\n"
            f"QPushButton:disabled{'{'}border: 3px solid {GREY};\n"
            "border-radius: 5px;\n"
            f"color: {WHITE};\n"
            f"gridline-color: {GREY};\n"
            f"background-color: {GREY};{'}'}\n"
            f"QPushButton:disabled:hover{'{'}background-color: {DARK};{'}'}"
        )
        # push_button.setIcon(icon11)
        # push_button.setIcon(QtGui_QIcon(QtGui_QPixmap(icon)))
        push_button.setIconSize(QtC.QSize(30, 30))
        push_button.setCheckable(True)
        push_button.setText(self.label)
        layout.addWidget(push_button, int(idx / 2), 0 if divmod(idx, 2)[1] == 0 else 1, 1, 1)


def check_aim_options(list_aim: List[Aim]):
    list_false = [aim for aim in list_aim if not aim.widget.isChecked()]
    list_true = [aim for aim in list_aim if aim.widget.isChecked()]
    for aim in list_false:
        for option in aim.list_options:
            if isinstance(option, list):
                for opt in option:
                    opt.hide()
                continue
            option.hide()
    for aim in list_true:
        for option in aim.list_options:
            if isinstance(option, list):
                for opt in option:
                    opt.show()
                continue
            option.show()


class Page:
    def __init__(self, default_parent: QtW.QWidget, name: str, button_name: str, icon: str):
        self.name: str = name
        self.button_name: str = button_name
        self.icon: str = icon
        self.list_categories: List[Category] = []
        self.button: QtW.QPushButton = QtW.QPushButton(default_parent)
        self.label: QtW.QLabel = QtW.QLabel(default_parent)
        self.label_gap: QtW.QLabel = QtW.QLabel(default_parent)
        self.page: QtW.QWidget = QtW.QWidget(default_parent)
        self.previous_page: Optional[Page] = None
        self.next_page: Optional[Page] = None
        self.upper_frame: List[Union[Aim, Option, Category]] = []

    def set_text(self, name: str):
        entry_name: List[str, str] = name.split(',')
        self.name = entry_name[1]
        self.button_name = entry_name[0].replace('@', '\n')
        self.label.setText(self.name)
        self.button.setText(self.button_name)

    def set_previous_page(self, previous_page: Page):
        self.previous_page = previous_page

    def set_next_page(self, next_page: Page):
        self.next_page = next_page

    def set_upper_frame(self, options: List[Union[Aim, Option, Category]]):
        self.upper_frame: List[Union[Aim, Option, Category]] = options

    def create_page(self, central_widget: QtW.QWidget, stacked_widget: QtW.QStackedWidget, vertical_layout_menu: QtW.QVBoxLayout):
        self.page.setParent(central_widget)
        layout = QtW.QVBoxLayout(self.page)
        layout.setSpacing(0)
        self.label.setParent(central_widget)
        label: QtW.QLabel = self.label
        label.setStyleSheet('font: 63 16pt "Lexend SemiBold";')
        label.setText(self.name)
        layout.addWidget(label)
        spacer_label = QtW.QLabel(self.page)
        spacer_label.setMinimumHeight(6)
        spacer_label.setMaximumHeight(6)
        layout.addWidget(spacer_label)
        scroll_area = QtW.QScrollArea(self.page)
        scroll_area.setFrameShape(QtW.QFrame.NoFrame)
        scroll_area.setLineWidth(0)
        scroll_area.setWidgetResizable(True)
        scroll_area_content = QtW.QWidget()
        scroll_area_content.setGeometry(QtC.QRect(0, 0, 864, 695))
        scroll_area.setWidget(scroll_area_content)
        layout.addWidget(scroll_area)
        scroll_area_layout = QtW.QVBoxLayout(scroll_area_content)
        scroll_area_layout.setSpacing(0)
        scroll_area_layout.setContentsMargins(0, 0, 0, 0)
        stacked_widget.addWidget(self.page)
        if self.upper_frame:
            upper_frame = QtW.QFrame(scroll_area_content)
            upper_frame.setStyleSheet(
                "QFrame {\n"
                f"	border: 1px solid {LIGHT};\n"
                "	border-top-left-radius: 15px;\n"
                "	border-top-right-radius: 15px;\n"
                "	border-bottom-left-radius: 15px;\n"
                "	border-bottom-right-radius: 15px;\n"
                "}\n"
                f"QLabel{'{'}border: 0px solid {WHITE};{'}'}"
            )
            upper_frame.setFrameShape(QtW.QFrame.StyledPanel)
            upper_frame.setFrameShadow(QtW.QFrame.Raised)
            upper_frame.setSizePolicy(QtW.QSizePolicy.Minimum, QtW.QSizePolicy.Minimum)
            grid_layout = QtW.QGridLayout(upper_frame)
            grid_layout.setVerticalSpacing(6)
            grid_layout.setHorizontalSpacing(6)
            scroll_area_layout.addWidget(upper_frame)
            for idx, option in enumerate(self.upper_frame):
                if isinstance(option, Aim):
                    option.create_widget(upper_frame, grid_layout, idx)
                    continue
                option.create_widget(upper_frame, grid_layout)

            list_aims: List[Aim] = [aim for aim in self.upper_frame if isinstance(aim, Aim)]
            if list_aims:
                for idx, aim in enumerate(list_aims):
                    default_value = 1 if idx == 0 else 0
                    aim.widget.clicked.connect(
                        ft_partial(
                            update_opponent,
                            aim.widget,
                            list_aims[default_value].widget,
                            [wid.widget for i, wid in enumerate(list_aims) if i not in [idx, default_value]],
                        )
                    )
                    aim.widget.clicked.connect(ft_partial(check_aim_options, list_aims))
                list_aims[0].widget.click()

        for category in self.list_categories:
            category.create_widget(scroll_area_content, scroll_area_layout)

        spacer = QtW.QSpacerItem(1, 1, QtW.QSizePolicy.Minimum, QtW.QSizePolicy.Expanding)
        scroll_area_layout.addItem(spacer)

        self.create_links_to_other_pages(central_widget, layout)

        self.button.setParent(central_widget)
        self.button.setMinimumSize(QtC.QSize(100, 100))
        icon23 = QtG.QIcon()
        icon23.addFile(self.icon, QtC.QSize(), QtG.QIcon.Normal, QtG.QIcon.Off)
        self.button.setIcon(icon23)
        self.button.setIconSize(QtC.QSize(24, 24))
        self.button.setText(self.button_name)
        self.label_gap.setParent(central_widget)
        self.label_gap.setMinimumSize(QtC.QSize(0, 6))
        self.label_gap.setMaximumSize(QtC.QSize(16777215, 6))

        vertical_layout_menu.addWidget(self.button)
        vertical_layout_menu.addWidget(self.label_gap)
        self.button.clicked.connect(ft_partial(stacked_widget.setCurrentWidget, self.page))

    def create_links_to_other_pages(self, central_widget: QtW.QWidget, scroll_area_layout: QtW.QVBoxLayout):
        if self.previous_page is None and self.next_page is None:
            return

        horizontal_layout = QtW.QHBoxLayout(central_widget)

        if self.previous_page is not None:
            push_button_previous = QtW.QPushButton(central_widget)
            push_button_previous.setMinimumSize(QtC.QSize(0, 30))
            push_button_previous.setMaximumSize(QtC.QSize(16777215, 30))
            icon = QtG.QIcon()
            icon.addFile(":/icons/icons/ArrowLeft2.svg", QtC.QSize(), QtG.QIcon.Normal, QtG.QIcon.Off)
            push_button_previous.setIcon(icon)
            push_button_previous.setIconSize(QtC.QSize(20, 20))
            push_button_previous.setText("  previous  ")

            horizontal_layout.addWidget(push_button_previous)
            push_button_previous.clicked.connect(self.previous_page.button.click)

        horizontal_spacer = QtW.QSpacerItem(1, 1, QtW.QSizePolicy.Expanding, QtW.QSizePolicy.Minimum)

        horizontal_layout.addItem(horizontal_spacer)
        if self.next_page is not None:
            push_button_next = QtW.QPushButton(central_widget)
            push_button_next.setMinimumSize(QtC.QSize(0, 30))
            push_button_next.setMaximumSize(QtC.QSize(16777215, 30))
            push_button_next.setLayoutDirection(QtC.Qt.RightToLeft)
            icon = QtG.QIcon()
            icon.addFile(":/icons/icons/ArrowRight2.svg", QtC.QSize(), QtG.QIcon.Normal, QtG.QIcon.Off)
            push_button_next.setIcon(icon)
            push_button_next.setIconSize(QtC.QSize(20, 20))
            push_button_next.setText("  next  ")

            horizontal_layout.addWidget(push_button_next)
            push_button_next.clicked.connect(self.next_page.button.click)

        scroll_area_layout.addLayout(horizontal_layout)
