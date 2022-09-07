
from typing import List, Optional, Union

from dataclasses import dataclass

import abc

import PySide6.QtWidgets as qt_w
import PySide6.QtCore as qt_c

@dataclass
class category:
    obj_name: str
    label: str
    page: str


class GuiObject(metaclass=abc.ABCMeta):

    def __init__(self, widget_name: str, label: str, default_value: Union[bool, int, float, str]):
        self.widget_name: str = widget_name
        self.label: str = label
        self.default_value: Union[bool, int, float, str] = default_value
        self.widget: qt_w.QWidget = qt_w.QWidget()
        self.frame: qt_w.QFrame = qt_w.QFrame()

    @abc.abstractmethod
    def get_value(self) -> Union[bool, int, float, str]:
        pass

    @abc.abstractmethod
    def create_widget(self, frame: qt_w.QFrame, layout: qt_w.QLayout) -> None:
        pass

    def create_frame(self, frame: qt_w.QFrame, layout_parent: qt_w.QLayout) -> qt_w.QHBoxLayout:
        self.frame = qt_w.QFrame(frame)
        self.frame.setObjectName(f"frame_{self.widget_name}")
        self.frame.setFrameShape(qt_w.QFrame.StyledPanel)
        self.frame.setFrameShadow(qt_w.QFrame.Raised)
        self.frame.setStyleSheet("QFrame {\n"
                                 "	border: 0px solid #54bceb;\n"
                                 "	border-radius: 0px;\n"
                                   "}\n")
        layout = qt_w.QHBoxLayout(self.frame)
        layout.setSpacing(0)
        layout.setObjectName(f"verticalLayout_{self.widget_name}")
        label = qt_w.QLabel(self.label)
        layout.addWidget(label)
        spacer = qt_w.QSpacerItem(1, 1, qt_w.QSizePolicy.Expanding, qt_w.QSizePolicy.Minimum)
        layout.addItem(spacer)
        layout_parent.addWidget(self.frame)
        return layout

    def hide(self) -> None:
        self.frame.hide()

    def show(self) -> None:
        self.frame.show()


class DoubleValue(GuiObject):

    def __init__(self, widget_name: str, label: str, default_value: float, decimal_number: int = 0, minimal_value: float = 0., maximal_value: float = 100.,
                 step: float = 1.):
        super().__init__(widget_name, label, default_value)
        self.decimal_number: int = decimal_number
        self.minimal_value: float = minimal_value
        self.maximal_value: float = maximal_value
        self.step: float = step
        self.widget: qt_w.QDoubleSpinBox = qt_w.QDoubleSpinBox()

    def get_value(self) -> float:
        return self.widget.value()

    def create_widget(self, frame: qt_w.QFrame, layout_parent: qt_w.QLayout) -> None:
        layout = self.create_frame(frame, layout_parent)
        self.widget = qt_w.QDoubleSpinBox(self.frame)
        self.widget.setObjectName(self.widget_name)
        self.widget.setStyleSheet("QDoubleSpinBox{selection-color: rgb(255, 255, 255);\n"
                                  "selection-background-color: rgb(84, 188, 235);\n"
                                  "border: 1px solid rgb(255, 255, 255);\n"
                                  "font: 11pt \"Lexend Deca Light\";}\n")
        self.widget.setAlignment(qt_c.Qt.AlignRight | qt_c.Qt.AlignTrailing | qt_c.Qt.AlignVCenter)
        self.widget.setMinimum(self.minimal_value)
        self.widget.setMaximum(self.maximal_value)
        self.widget.setValue(self.default_value)
        self.widget.setDecimals(self.decimal_number)
        self.widget.setSingleStep(self.step)
        self.widget.setMaximumWidth(100)
        self.widget.setMinimumWidth(100)
        setattr(frame.window(), self.widget_name, self.widget)
        layout.addWidget(self.widget)


class IntValue(GuiObject):

    def __init__(self, widget_name: str, label: str, default_value: int, minimal_value: int = 0, maximal_value: int = 100, step: int = 1):
        super().__init__(widget_name, label, default_value)
        self.minimal_value: int = minimal_value
        self.maximal_value: int = maximal_value
        self.step: int = step
        self.widget: qt_w.QSpinBox = qt_w.QSpinBox()

    def get_value(self) -> float:
        return self.widget.value()

    def create_widget(self, frame: qt_w.QFrame, layout_parent: qt_w.QLayout) -> None:
        layout = self.create_frame(frame, layout_parent)
        self.widget = qt_w.QSpinBox(self.frame)
        self.widget.setObjectName(self.widget_name)
        self.widget.setStyleSheet("QSpinBox{selection-color: rgb(255, 255, 255);\n"
                                  "selection-background-color: rgb(84, 188, 235);\n"
                                  "border: 1px solid rgb(255, 255, 255);\n"
                                  "font: 11pt \"Lexend Deca Light\";}\n")
        self.widget.setAlignment(qt_c.Qt.AlignRight | qt_c.Qt.AlignTrailing | qt_c.Qt.AlignVCenter)
        self.widget.setMinimum(self.minimal_value)
        self.widget.setMaximum(self.maximal_value)
        self.widget.setValue(self.default_value)
        self.widget.setSingleStep(self.step)
        self.widget.setMaximumWidth(100)
        self.widget.setMinimumWidth(100)
        setattr(frame.window(), self.widget_name, self.widget)
        layout.addWidget(self.widget)


class ListBox(GuiObject):

    def __init__(self, widget_name: str, label: str, default_index: int, entries: List[str]):
        super().__init__(widget_name, label, default_index)
        self.entries: List[str] = entries
        self.widget: qt_w.QComboBox = qt_w.QComboBox()

    def get_value(self) -> float:
        return self.widget.currentIndex()

    def create_widget(self, frame: qt_w.QFrame, layout_parent: qt_w.QLayout) -> None:
        layout = self.create_frame(frame, layout_parent)
        self.widget = qt_w.QComboBox(self.frame)
        self.widget.setObjectName(self.widget_name)
        self.widget.setStyleSheet("QFrame {\n"
                                  "	border: 1px solid rgb(255, 255, 255);\n"
                                  "	border-bottom-left-radius: 0px;\n"
                                              "	border-bottom-right-radius: 0px;\n"
                                              "}"
                                              "QComboBox{border: 1px solid #ffffff;\n"
                                              "border-bottom-left-radius: 0px;\n"
                                              "border-bottom-right-radius: 0px;\n"
                                              "}\n"
                                              )
        self.widget.addItems(self.entries)
        self.widget.setCurrentIndex(self.default_value)
        self.widget.setMaximumWidth(100)
        self.widget.setMinimumWidth(100)
        setattr(frame.window(), self.widget_name, self.widget)
        layout.addWidget(self.widget)


class Option:

    def __init__(self, obj_name: str, label: str, list_of_options: List[GuiObject]):#, category: category, object: GuiObject):
        self.obj_name: str = obj_name
        self.label: str = label
        self.list_of_options: List[GuiObject] = list_of_options
        self.layout: qt_w.QVBoxLayout = qt_w.QVBoxLayout()
        self.frame: qt_w.QFrame = qt_w.QFrame()
        """
        self.category: category = category
        self.object: GuiObject = object
        """

    def create_widget(self, page: qt_w.QWidget, layout: qt_w.QLayout):
        label = qt_w.QLabel(page)
        label.setText(self.label)
        label.setObjectName(f'label_{self.obj_name}')
        label.setStyleSheet("QLabel {\n"
                                            "	border: 1px solid  rgb(84, 188, 235);\n"
                                            "	border-top-left-radius: 15px;\n"
                                            "	border-top-right-radius: 15px;\n"
                                            "	background-color:  rgb(84, 188, 235);\n"
                                            "	padding: 5px 0px;\n"
                                            "	color:  rgb(255, 255, 235);\n"
                                            "font-weight:500;\n"
                                            "}")
        label.setAlignment(qt_c.Qt.AlignCenter | qt_c.Qt.AlignVCenter)
        layout.addWidget(label)
        self.frame = qt_w.QFrame(page)
        self.frame.setObjectName(f'frame_{self.obj_name}')
        self.frame.setStyleSheet(u"QFrame {\n"
                                            "	border: 1px solid #54bceb;\n"
                                            "	border-bottom-left-radius: 15px;\n"
                                            "	border-bottom-right-radius: 15px;\n"
                                            "}\n"
                                            "QLabel{border: 0px solid rgb(255,255,255);}")
        self.frame.setFrameShape(qt_w.QFrame.StyledPanel)
        self.frame.setFrameShadow(qt_w.QFrame.Raised)
        layout.addWidget(self.frame)
        self.layout = qt_w.QVBoxLayout(self.frame)
        self.layout.setSpacing(0)
        for option in self.list_of_options:
            option.create_widget(self.frame, self.layout)


@dataclass
class aim:
    obj_name: str
    label: str
    icon: str
    options: List[Option]


