from __future__ import annotations
from typing import List, Optional, Union

from functools import partial as ft_partial
from dataclasses import dataclass
from .gui_Main_new import WHITE, LIGHT, DARK, GREY, WARNING

import abc

import PySide6.QtWidgets as qt_w
import PySide6.QtCore as qt_c
import PySide6.QtGui as qt_g


def update_opponent(button: qt_w.QPushButton, button_opponent: qt_w.QPushButton, false_button_list: List[qt_w.QPushButton] = None):
    button_opponent.setChecked(not button.isChecked())
    if false_button_list is not None:
        for false_button in false_button_list:
            false_button.setChecked(False)


class Option(metaclass=abc.ABCMeta):

    def __init__(self, default_parent: qt_w.QWidget, widget_name: str, label: str, default_value: Union[bool, int, float, str]):

        self.widget_name: str = widget_name
        self.label: str = label
        self.default_value: Union[bool, int, float, str] = default_value
        self.widget: Optional[qt_w.QWidget] = None
        self.frame: qt_w.QFrame = qt_w.QFrame(default_parent)
        self.linked_options: List[(Option, int)] = []
        self.limit_size: bool = True

    @abc.abstractmethod
    def get_value(self) -> Union[bool, int, float, str]:
        pass

    @abc.abstractmethod
    def set_value(self, value: Union[bool, int, float, str]) -> None:
        pass

    @abc.abstractmethod
    def create_widget(self, frame: qt_w.QFrame, layout: qt_w.QLayout, row: int = None, column: int = None) -> None:
        pass

    def deactivate_size_limit(self):
        self.limit_size = False

    def create_frame(self, frame: qt_w.QFrame, layout_parent: qt_w.QLayout, create_spacer: bool = True) -> qt_w.QHBoxLayout:
        if self.label == '':
            self.frame.setParent(None)
            self.frame = frame
            return frame.layout()
        self.frame.setParent(frame)
        self.frame.setObjectName(f"frame_{self.widget_name}")
        self.frame.setFrameShape(qt_w.QFrame.StyledPanel)
        self.frame.setFrameShadow(qt_w.QFrame.Raised)
        self.frame.setStyleSheet("QFrame {\n"
                                 f"	border: 0px solid {WHITE};\n"
                                 "	border-radius: 0px;\n"
                                 "  }\n")
        layout = qt_w.QHBoxLayout(self.frame)
        layout.setSpacing(6)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setObjectName(f"verticalLayout_{self.widget_name}")
        label = qt_w.QLabel(self.label)
        layout.addWidget(label)
        if create_spacer:
            spacer = qt_w.QSpacerItem(1, 1, qt_w.QSizePolicy.Expanding, qt_w.QSizePolicy.Minimum)
            layout.addItem(spacer)
        layout_parent.addWidget(self.frame)
        return layout

    def hide(self) -> None:
        self.frame.hide()

    def show(self) -> None:
        self.frame.show()


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


class DoubleValue(Option):

    def __init__(self, default_parent: qt_w.QWidget, widget_name: str, label: str, default_value: float, decimal_number: int = 0, minimal_value: float = 0.,
                 maximal_value: float = 100., step: float = 1.):
        super().__init__(default_parent, widget_name, label, default_value)
        self.decimal_number: int = decimal_number
        self.minimal_value: float = minimal_value
        self.maximal_value: float = maximal_value
        self.step: float = step
        self.widget: qt_w.QDoubleSpinBox = qt_w.QDoubleSpinBox(default_parent)

    def get_value(self) -> float:
        return self.widget.value()

    def set_value(self, value: float) -> None:
        self.widget.setValue(value)

    def create_widget(self, frame: qt_w.QFrame, layout_parent: qt_w.QLayout, row: int = None, column: int = None) -> None:
        layout = self.create_frame(frame, layout_parent)
        self.widget.setParent(self.frame)
        self.widget.setObjectName(self.widget_name)
        self.widget.setStyleSheet(f"QDoubleSpinBox{'{'}selection-color: {WHITE};\n"
                                  f"selection-background-color: {LIGHT};\n"
                                  f"border: 1px solid {WHITE};\n"
                                  "font: 11pt \"Lexend Deca Light\";}\n")
        self.widget.setAlignment(qt_c.Qt.AlignRight | qt_c.Qt.AlignTrailing | qt_c.Qt.AlignVCenter)
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
        setattr(frame.window(), self.widget_name, self.widget)
        if row is not None and isinstance(layout_parent, qt_w.QGridLayout):
            layout_parent.addWidget(self.widget, column, row)
            return
        layout.addWidget(self.widget)


class IntValue(Option):

    def __init__(self, default_parent: qt_w.QWidget, widget_name: str, label: str, default_value: int, minimal_value: int = 0, maximal_value: int = 100,
                 step: int = 1):
        super().__init__(default_parent, widget_name, label, default_value)
        self.minimal_value: int = minimal_value
        self.maximal_value: int = maximal_value
        self.step: int = step
        self.widget: qt_w.QSpinBox = qt_w.QSpinBox(default_parent)

    def get_value(self) -> float:
        return self.widget.value()

    def set_value(self, value: int) -> None:
        self.widget.setValue(value)

    def create_widget(self, frame: qt_w.QFrame, layout_parent: qt_w.QLayout, row: int = None, column: int = None) -> None:
        layout = self.create_frame(frame, layout_parent)
        self.widget.setParent(self.frame)
        self.widget.setObjectName(self.widget_name)
        self.widget.setStyleSheet("QSpinBox{\n"
                                    f"selection-color: {WHITE};\n"
                                  f"selection-background-color: {LIGHT};\n"
                                  f"border: 1px solid {WHITE};\n"
                                  "font: 11pt \"Lexend Deca Light\";}\n")
        self.widget.setAlignment(qt_c.Qt.AlignRight | qt_c.Qt.AlignTrailing | qt_c.Qt.AlignVCenter)
        self.widget.setMinimum(self.minimal_value)
        self.widget.setMaximum(self.maximal_value)
        self.widget.setValue(self.default_value)
        self.widget.setSingleStep(self.step)
        self.widget.setMaximumWidth(100)
        self.widget.setMinimumWidth(100)
        self.widget.setMinimumHeight(28)
        setattr(frame.window(), self.widget_name, self.widget)
        if row is not None and isinstance(layout_parent, qt_w.QGridLayout):
            layout_parent.addWidget(self.widget, column, row)
            return
        layout.addWidget(self.widget)


class ButtonBox(Option):

    def __init__(self, default_parent: qt_w.QWidget, widget_name: str, label: str, default_index: int, entries: List[str]):
        super().__init__(default_parent, widget_name, label, default_index)
        self.entries: List[str] = entries
        self.widget: List[qt_w.QPushButton] = [qt_w.QPushButton(default_parent) for _ in self.entries]

    def get_value(self) -> int:
        for idx, button in enumerate(self.widget):
            if button.isChecked():
                return idx
        return -1

    def set_value(self, index: int) -> None:
        for idx, button in enumerate(self.widget):
            if idx == index:
                button.click()
                break

    def create_widget(self, frame: qt_w.QFrame, layout_parent: qt_w.QLayout, row: int = None, column: int = None) -> None:
        layout = self.create_frame(frame, layout_parent)
        for idx, (entry, widget) in enumerate(zip(self.entries, self.widget)):
            widget.setParent(self.frame)
            widget.setObjectName(f'{self.widget_name}_{idx}')
            widget.setText(f' {entry} ')
            widget.setStyleSheet("QPushButton{\n"
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
                                 "}")
            widget.setCheckable(True)
            widget.setChecked(idx == self.default_value)
            widget.setMinimumHeight(30)
            # self.widget.currentIndexChanged.connect(ft_partial(check, self.linked_options))
            setattr(frame.window(), self.widget_name, self.widget)
            layout.addWidget(widget)
        for idx, button in enumerate(self.widget):
            default_value = self.default_value if idx != self.default_value else idx - 1 if idx > 0 else 1
            button.clicked.connect(ft_partial(update_opponent, button, self.widget[default_value],
                                              [but for i, but in enumerate(self.widget) if i not in [idx, default_value]]))
            button.clicked.connect(ft_partial(check, self.linked_options, self, self.get_value()))


class ListBox(Option):

    def __init__(self, default_parent: qt_w.QWidget, widget_name: str, label: str, default_index: int, entries: List[str]):
        super().__init__(default_parent, widget_name, label, default_index)
        self.entries: List[str] = entries
        self.widget: qt_w.QComboBox = qt_w.QComboBox(default_parent)

    def get_value(self) -> float:
        return self.widget.currentIndex()

    def set_value(self, index: int) -> None:
        self.widget.setCurrentIndex(index)

    def create_widget(self, frame: qt_w.QFrame, layout_parent: qt_w.QLayout, row: int = None, column: int = None) -> None:
        layout = self.create_frame(frame, layout_parent)
        self.widget.setParent(self.frame)
        self.widget.setObjectName(self.widget_name)
        self.widget.setStyleSheet("QFrame {\n"
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
        setattr(frame.window(), self.widget_name, self.widget)
        if row is not None and isinstance(layout_parent, qt_w.QGridLayout):
            layout_parent.addWidget(self.widget, column, row)
            return
        layout.addWidget(self.widget)


class FileName(Option):

    def __init__(self, default_parent: qt_w.QWidget, widget_name: str, label: str, default_value: str, dialog_text: str, error_text: str,
                 status_bar: qt_w.QStatusBar):
        super().__init__(default_parent, widget_name, label, default_value)
        self.widget: qt_w.QLineEdit = qt_w.QLineEdit(default_parent)
        self.dialog_text: str = dialog_text
        self.error_text: str = error_text
        self.status_bar: qt_w.QStatusBar = status_bar

    def get_value(self) -> str:
        return self.widget.text()

    def set_value(self, filename: str) -> None:
        self.widget.setText(filename)

    def create_widget(self, frame: qt_w.QFrame, layout_parent: qt_w.QLayout, row: int = None, column: int = None) -> None:
        layout = self.create_frame(frame, layout_parent, False)
        self.widget.setParent(self.frame)
        self.widget.setObjectName(self.widget_name)
        self.widget.setStyleSheet(u"QLineEdit{border: 3px solid rgb(84, 188, 235);\n"
                                  "border-radius: 5px;\n"
                                  f"color: {WHITE};\n"
                                  "gridline-color: rgb(84, 188, 235);\n"
                                  "background-color: rgb(84, 188, 235);\n"
                                  "font-weight:500;\n"
                                  "selection-background-color: rgb(42, 126, 179);}\n"
                                  "QLineEdit:hover{background-color: rgb(0, 64, 122);}")
        layout.addWidget(self.widget)
        button = qt_w.QPushButton(self.frame)
        button.setMinimumSize(qt_c.QSize(30, 30))
        button.setMaximumSize(qt_c.QSize(30, 30))
        button.setText('...')
        button.clicked.connect(self.fun_choose_file)
        layout.addWidget(button)
        setattr(frame.window(), self.widget_name, self.widget)

    def fun_choose_file(self) -> None:
        """
        function to choose data file Import
        :return: None
        """
        # try to ask for a file otherwise show message in status bar
        try:
            filename = qt_w.QFileDialog.getOpenFileName(self.frame, caption=self.dialog_text, filter='(*.csv)')
            self.widget.setText(filename[0])
        # show warning if no file is selected in status bar for 5 seconds
        except FileNotFoundError:
            self.status_bar.showMessage(self.error_text, 5000)


class Hint:

    def __init__(self, default_parent: qt_w.QWidget, widget_name: str, hint: str, warning: bool = False):
        self.hint: str = hint
        self.obj_name: str = widget_name
        self.label: qt_w.QLabel = qt_w.QLabel(default_parent)
        self.warning = warning

    def create_widget(self, frame: qt_w.QFrame, layout_parent: qt_w.QLayout, row: int = None, column: int = None) -> None:
        self.label.setParent(frame)
        self.label.setText(self.hint)
        if self.warning:
            self.label.setStyleSheet(f"color: {WARNING};")
        self.label.setWordWrap(True)
        if row is not None and isinstance(layout_parent, qt_w.QGridLayout):
            layout_parent.addWidget(self.label, column, row)
            return
        layout_parent.addWidget(self.label)

    def hide(self) -> None:
        self.label.hide()

    def show(self) -> None:
        self.label.show()

class FunctionButton:

    def __init__(self, default_parent: qt_w.QWidget, widget_name: str, button_text: str, icon: str):
        self.button_text: str = button_text
        self.widget_name: str = widget_name
        self.icon: str = icon
        self.frame: qt_w.QFrame = qt_w.QFrame(default_parent)
        self.button: qt_w.QPushButton = qt_w.QPushButton(default_parent)

    def create_widget(self, frame: qt_w.QFrame, layout_parent: qt_w.QLayout):
        self.button.setParent(frame)
        self.button.setObjectName(f"button_{self.widget_name}")
        self.button.setText(f'  {self.button_text}  ')
        icon = qt_g.QIcon()
        # icon11.addPixmap(QtGui_QPixmap(icon), QtGui_QIcon.Normal, QtGui_QIcon.Off)
        icon.addFile(self.icon)
        self.button.setIcon(icon)
        self.button.setIconSize(qt_c.QSize(20, 20))
        self.button.setMinimumWidth(100)
        self.button.setMinimumHeight(35)
        self.frame.setParent(frame)
        self.frame.setObjectName(f"frame_{self.widget_name}")
        self.frame.setFrameShape(qt_w.QFrame.StyledPanel)
        self.frame.setFrameShadow(qt_w.QFrame.Raised)
        self.frame.setStyleSheet("QFrame {\n"
                                 f"	border: 0px solid {WHITE};\n"
                                 "	border-radius: 0px;\n"
                                 "  }\n")
        layout = qt_w.QHBoxLayout(self.frame)
        layout.setSpacing(6)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setObjectName(f"verticalLayout_{self.widget_name}")
        spacer1 = qt_w.QSpacerItem(1, 1, qt_w.QSizePolicy.Expanding, qt_w.QSizePolicy.Minimum)
        layout.addItem(spacer1)

        layout.addWidget(self.button)
        spacer1 = qt_w.QSpacerItem(1, 1, qt_w.QSizePolicy.Expanding, qt_w.QSizePolicy.Minimum)
        layout.addItem(spacer1)

        layout_parent.addWidget(self.frame)

    def hide(self) -> None:
        self.frame.hide()

    def show(self) -> None:
        self.frame.show()


class Category:

    def __init__(self, default_parent: qt_w.QWidget, obj_name: str, label: str, list_of_options: List[Union[Option, Hint, FunctionButton]]):
        self.obj_name: str = obj_name
        self.label_text: str = label
        self.label: qt_w.QLabel = qt_w.QLabel(default_parent)
        self.list_of_options: List[Union[Option, Hint, FunctionButton]] = list_of_options
        self.frame: qt_w.QFrame = qt_w.QFrame(default_parent)
        self.graphic_left: Optional[Union[qt_w.QGraphicsView, bool]] = None
        self.graphic_right: Optional[Union[qt_w.QGraphicsView, bool]] = None
        self.grid_layout: int = 0

    def activate_graphic_left(self):
        self.graphic_left = True

    def activate_graphic_right(self):
        self.graphic_right = True

    def activate_grid_layout(self, column: int):
        self.grid_layout = column

    def create_widget(self, page: qt_w.QWidget, layout: qt_w.QLayout):
        self.label.setParent(page)
        self.label.setText(self.label_text)
        self.label.setObjectName(f'label_{self.obj_name}')
        self.label.setStyleSheet("QLabel {\n"
                                            f"	border: 1px solid  {LIGHT};\n"
                                            "	border-top-left-radius: 15px;\n"
                                            "	border-top-right-radius: 15px;\n"
                                            f"	background-color:  {LIGHT};\n"
                                            "	padding: 5px 0px;\n"
                                            f"	color:  {WHITE};\n"
                                            "font-weight:500;\n"
                                            "}")
        self.label.setAlignment(qt_c.Qt.AlignCenter | qt_c.Qt.AlignVCenter)
        layout.addWidget(self.label)
        self.frame.setParent(page)
        self.frame.setObjectName(f'frame_{self.obj_name}')
        self.frame.setStyleSheet("QFrame {\n"
                                            f"	border: 1px solid {LIGHT};\n"
                                            "	border-bottom-left-radius: 15px;\n"
                                            "	border-bottom-right-radius: 15px;\n"
                                            "}\n"
                                            "QLabel{\n"
                                 f"border: 0px solid {WHITE};"
                                 "\n}")
        self.frame.setFrameShape(qt_w.QFrame.StyledPanel)
        self.frame.setFrameShadow(qt_w.QFrame.Raised)
        layout.addWidget(self.frame)
        spacer_label = qt_w.QLabel(page)
        spacer_label.setMinimumHeight(6)
        spacer_label.setMaximumHeight(6)
        layout.addWidget(spacer_label)
        layout_frame_horizontal = qt_w.QHBoxLayout(self.frame)
        if self.graphic_left is not None:
            self.graphic_left = self.create_graphic_view(layout_frame_horizontal)
        if self.grid_layout > 0:
            layout_frane = qt_w.QGridLayout(self.frame)
            row = 0
            column = 0
            for option in self.list_of_options:
                if isinstance(option, Hint):
                    option.create_widget(self.frame, layout_frane, row, column)
                else:
                    option.deactivate_size_limit() if option.label == '' else None
                    option.create_widget(self.frame, layout_frane, row, column)
                if row == self.grid_layout - 1:
                    row = 0
                    column += 1
                    continue
                row += 1
        else:
            layout_frane = qt_w.QVBoxLayout(self.frame)
            for option in self.list_of_options:
                option.create_widget(self.frame, layout_frane)

        layout_frame_horizontal.addLayout(layout_frane)

        if self.graphic_right is not None:
            self.graphic_right = self.create_graphic_view(layout_frame_horizontal)

    def create_graphic_view(self, layout: qt_w.QLayout) -> qt_w.QGraphicsView:
        graphic_view = qt_w.QGraphicsView(self.frame)
        graphic_view.setObjectName(f"graphicsView_left_{self.obj_name}")
        graphic_view.setMinimumSize(qt_c.QSize(0, 0))
        graphic_view.setMaximumSize(qt_c.QSize(100, 16777215))
        graphic_view.setStyleSheet(u"QFrame {\n"
                                        "	border: 1px solid #54bceb;\n"
                                        "	border-bottom-left-radius: 0px;\n"
                                        "	border-bottom-right-radius: 0px;\n"
                                        "}\n"
                                        "QLabel{border: 0px solid rgb(255,255,255);}")

        layout.addWidget(graphic_view)
        return graphic_view

    def hide(self) -> None:
        self.frame.hide()
        self.label.hide()

    def show(self) -> None:
        self.frame.show()
        self.label.show()


class Aim:

    def __init__(self, default_parent: qt_w.QWidget, obj_name: str, label: str, icon: str, list_options: List[Union[Option, Category]]):
        self.obj_name: str = obj_name
        self.label: str = label
        self.icon: str = icon
        self.widget: qt_w.QPushButton = qt_w.QPushButton(default_parent)
        self.list_options: List[Union[Option, Category]] = list_options

    def create_widget(self, frame: qt_w.QFrame, layout: qt_w.QGridLayout, idx: int) -> None:
        icon11 = qt_g.QIcon()
        # icon11.addPixmap(QtGui_QPixmap(icon), QtGui_QIcon.Normal, QtGui_QIcon.Off)
        icon11.addFile(self.icon)
        self.widget.setParent(frame)
        push_button = self.widget
        push_button.setIcon(icon11)
        push_button.setMinimumSize(qt_c.QSize(0, 60))
        push_button.setMaximumSize(qt_c.QSize(16777215, 60))
        push_button.setStyleSheet("QPushButton{border: 3px solid rgb(0, 64, 122);\n"
                                  "border-radius: 15px;\n"
                                  "color: rgb(255, 255, 255);\n"
                                  "gridline-color: rgb(84, 188, 235);\n"
                                  "background-color: rgb(100, 100, 100);\n"
                                  "font-weight:500;}\n"
                                  "QPushButton:hover{border: 3px solid rgb(0, 64, 122);\n"
                                  "background-color:rgb(84, 188, 235);}\n"
                                  "QPushButton:checked{border:3px solid rgb(84, 188, 235);\n"
                                  "background-color:rgb(84, 188, 235);}\n"
                                  "QPushButton:disabled{border: 3px solid rgb(100, 100, 100);\n"
                                  "border-radius: 5px;\n"
                                  "color: rgb(255, 255, 255);\n"
                                  "gridline-color: rgb(100, 100, 100);\n"
                                  "background-color: rgb(100, 100, 100);}\n"
                                  "QPushButton:disabled:hover{background-color: rgb(0, 64, 122);}")
        # push_button.setIcon(icon11)
        # push_button.setIcon(QtGui_QIcon(QtGui_QPixmap(icon)))
        push_button.setIconSize(qt_c.QSize(30, 30))
        push_button.setCheckable(True)
        push_button.setObjectName(self.obj_name)
        push_button.setText(self.label)
        setattr(self, self.obj_name, push_button)
        layout.addWidget(push_button, int(idx/2), 0 if divmod(idx, 2)[1] == 0 else 1, 1, 1)


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

    def __init__(self, default_parent: qt_w.QWidget, obj_name: str, name: str, button_name: str, icon: str, list_categories: List[Category]):
        self.obj_name: str = obj_name
        self.name: str = name
        self.button_name: str = button_name
        self.icon: str = icon
        self.list_categories: List[Category] = list_categories
        self.button: qt_w.QPushButton = qt_w.QPushButton(default_parent)
        self.label: qt_w.QLabel = qt_w.QLabel(default_parent)
        self.label_gap: qt_w.QLabel = qt_w.QLabel(default_parent)
        self.previous_page: Optional[Page] = None
        self.next_page: Optional[Page] = None
        self.upper_frame: Optional[List[Union[Aim, Option, Category]]] = None

    def set_text(self, name: str, button_name: str):
        self.name = name
        self.button_name = button_name
        self.label.setText(self.name)
        self.button.setText(self.button_name)

    def set_previous_page(self, previous_page: Page):
        self.previous_page = previous_page

    def set_next_page(self, next_page: Page):
        self.next_page = next_page

    def set_upper_frame(self, options: List[Union[Aim, Option, Category]]):
        self.upper_frame: List[Union[Aim, Option, Category]] = options

    def create_page(self, central_widget: qt_w.QWidget, stacked_widget: qt_w.QStackedWidget, vertical_layout_menu: qt_w.QVBoxLayout):
        page = qt_w.QWidget(central_widget)
        page.setObjectName(f"page_{self.obj_name}")
        layout = qt_w.QVBoxLayout(page)
        layout.setSpacing(0)
        self.label.setParent(central_widget)
        label: qt_w.QLabel = self.label
        label.setObjectName(f"label_{self.obj_name}")
        label.setStyleSheet("font: 63 16pt \"Lexend SemiBold\";")
        label.setText(self.name)
        layout.addWidget(label)
        spacer_label = qt_w.QLabel(page)
        spacer_label.setMinimumHeight(6)
        spacer_label.setMaximumHeight(6)
        layout.addWidget(spacer_label)
        scroll_area = qt_w.QScrollArea(page)
        scroll_area.setObjectName(f"scrollArea_{self.obj_name}")
        scroll_area.setFrameShape(qt_w.QFrame.NoFrame)
        scroll_area.setLineWidth(0)
        scroll_area.setWidgetResizable(True)
        scroll_area_content = qt_w.QWidget()
        scroll_area_content.setObjectName(f"scrollAreaWidgetContents_{self.obj_name}")
        scroll_area_content.setGeometry(qt_c.QRect(0, 0, 864, 695))
        scroll_area.setWidget(scroll_area_content)
        layout.addWidget(scroll_area)
        scroll_area_layout = qt_w.QVBoxLayout(scroll_area_content)
        scroll_area_layout.setSpacing(0)
        scroll_area_layout.setObjectName(f"scroll_area_layout_{self.obj_name}")
        scroll_area_layout.setContentsMargins(0, 0, 0, 0)
        stacked_widget.addWidget(page)
        if self.upper_frame is not None:
            upper_frame = qt_w.QFrame(scroll_area_content)
            upper_frame.setStyleSheet("QFrame {\n"
                                          f"	border: 1px solid {LIGHT};\n"
                                          "	border-top-left-radius: 15px;\n"
                                          "	border-top-right-radius: 15px;\n"
                                          "	border-bottom-left-radius: 15px;\n"
                                          "	border-bottom-right-radius: 15px;\n"
                                          "}\n"
                                          f"QLabel{'{'}border: 0px solid {WHITE};{'}'}")
            upper_frame.setFrameShape(qt_w.QFrame.StyledPanel)
            upper_frame.setFrameShadow(qt_w.QFrame.Raised)
            upper_frame.setSizePolicy(qt_w.QSizePolicy.Minimum, qt_w.QSizePolicy.Minimum)
            grid_layout = qt_w.QGridLayout(upper_frame)
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
                    aim.widget.clicked.connect(ft_partial(update_opponent, aim.widget, list_aims[default_value].widget,
                                                          [wid.widget for i, wid in enumerate(list_aims) if i not in [idx, default_value]]))
                    aim.widget.clicked.connect(ft_partial(check_aim_options, list_aims))
                list_aims[0].widget.click()

        for category in self.list_categories:
            category.create_widget(scroll_area_content, scroll_area_layout)

        spacer = qt_w.QSpacerItem(1, 1, qt_w.QSizePolicy.Minimum, qt_w.QSizePolicy.Expanding)
        scroll_area_layout.addItem(spacer)

        self.create_links_to_other_pages(central_widget, layout)

        self.button.setParent(central_widget)
        self.button.setObjectName(f"pushButton_General_{self.obj_name}")
        self.button.setMinimumSize(qt_c.QSize(100, 100))
        icon23 = qt_g.QIcon()
        icon23.addFile(self.icon, qt_c.QSize(), qt_g.QIcon.Normal, qt_g.QIcon.Off)
        self.button.setIcon(icon23)
        self.button.setIconSize(qt_c.QSize(24, 24))
        self.button.setText(self.button_name)
        self.label_gap.setParent(central_widget)
        self.label_gap.setMinimumSize(qt_c.QSize(0, 6))
        self.label_gap.setMaximumSize(qt_c.QSize(16777215, 6))

        vertical_layout_menu.addWidget(self.button)
        vertical_layout_menu.addWidget(self.label_gap)
        self.button.clicked.connect(ft_partial(stacked_widget.setCurrentWidget, page))

    def create_links_to_other_pages(self, central_widget: qt_w.QWidget, scroll_area_layout: qt_w.QVBoxLayout):
        if self.previous_page is None and self.next_page is None:
            return

        horizontal_layout = qt_w.QHBoxLayout(central_widget)

        if self.previous_page is not None:
            push_button_previous = qt_w.QPushButton(central_widget)
            push_button_previous.setMinimumSize(qt_c.QSize(0, 30))
            push_button_previous.setMaximumSize(qt_c.QSize(16777215, 30))
            icon = qt_g.QIcon()
            icon.addFile(u":/icons/icons/ArrowLeft2.svg", qt_c.QSize(), qt_g.QIcon.Normal, qt_g.QIcon.Off)
            push_button_previous.setIcon(icon)
            push_button_previous.setIconSize(qt_c.QSize(20, 20))
            push_button_previous.setText('  previous  ')

            horizontal_layout.addWidget(push_button_previous)
            push_button_previous.clicked.connect(self.previous_page.button.click)

        horizontal_spacer = qt_w.QSpacerItem(1, 1, qt_w.QSizePolicy.Expanding, qt_w.QSizePolicy.Minimum)

        horizontal_layout.addItem(horizontal_spacer)
        if self.next_page is not None:
            push_button_next = qt_w.QPushButton(central_widget)
            push_button_next.setMinimumSize(qt_c.QSize(0, 30))
            push_button_next.setMaximumSize(qt_c.QSize(16777215, 30))
            push_button_next.setLayoutDirection(qt_c.Qt.RightToLeft)
            icon = qt_g.QIcon()
            icon.addFile(u":/icons/icons/ArrowRight2.svg", qt_c.QSize(), qt_g.QIcon.Normal, qt_g.QIcon.Off)
            push_button_next.setIcon(icon)
            push_button_next.setIconSize(qt_c.QSize(20, 20))
            push_button_next.setText('  next  ')

            horizontal_layout.addWidget(push_button_next)
            push_button_next.clicked.connect(self.next_page.button.click)

        scroll_area_layout.addLayout(horizontal_layout)




