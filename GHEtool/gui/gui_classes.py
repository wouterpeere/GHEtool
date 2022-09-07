from __future__ import annotations
from typing import List, Optional, Union

from functools import partial as ft_partial
from dataclasses import dataclass

import abc

import PySide6.QtWidgets as qt_w
import PySide6.QtCore as qt_c
import PySide6.QtGui as qt_g


class Option(metaclass=abc.ABCMeta):

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


class DoubleValue(Option):

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


class IntValue(Option):

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


class ListBox(Option):

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


class Category:

    def __init__(self, obj_name: str, label: str, list_of_options: List[Option]):
        self.obj_name: str = obj_name
        self.label_text: str = label
        self.label: qt_w.QLabel = qt_w.QLabel()
        self.list_of_options: List[Option] = list_of_options
        self.layout: qt_w.QVBoxLayout = qt_w.QVBoxLayout()
        self.frame: qt_w.QFrame = qt_w.QFrame()
        """
        self.category: category = category
        self.object: GuiObject = object
        """

    def create_widget(self, page: qt_w.QWidget, layout: qt_w.QLayout):
        label = qt_w.QLabel(page)
        self.label = label
        label.setText(self.label_text)
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
        spacer_label = qt_w.QLabel(page)
        spacer_label.setMinimumHeight(6)
        spacer_label.setMaximumHeight(6)
        layout.addWidget(spacer_label)
        self.layout = qt_w.QVBoxLayout(self.frame)
        for option in self.list_of_options:
            option.create_widget(self.frame, self.layout)

    def hide(self) -> None:
        self.frame.hide()
        self.label.hide()

    def show(self) -> None:
        self.frame.show()
        self.label.show()


class Page:

    def __init__(self, obj_name: str, name: str, button_name: str, icon: str, list_categories: List[Category]):
        self.obj_name: str = obj_name
        self.name: str = name
        self.button_name: str = button_name
        self.icon: str = icon
        self.list_categories: List[Category] = list_categories
        self.button: qt_w.QPushButton = qt_w.QPushButton()
        self.previous_page: Optional[Page] = None
        self.next_page: Optional[Page] = None

    def set_previous_page(self, previous_page: Page):
        self.previous_page = previous_page

    def set_next_page(self, next_page: Page):
        self.next_page = next_page
        
    def create_page(self, central_widget: qt_w.QWidget, stacked_widget: qt_w.QStackedWidget, vertical_layout_menu: qt_w.QVBoxLayout):
        page = qt_w.QWidget(central_widget)
        page.setObjectName(f"page_{self.obj_name}")
        layout = qt_w.QVBoxLayout(page)
        layout.setSpacing(0)
        label: qt_w.QLabel = qt_w.QLabel(central_widget)
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
        self.button = qt_w.QPushButton(central_widget)
        self.button.setObjectName(f"pushButton_General_{self.obj_name}")
        self.button.setMinimumSize(qt_c.QSize(100, 100))
        icon23 = qt_g.QIcon()
        icon23.addFile(self.icon, qt_c.QSize(), qt_g.QIcon.Normal, qt_g.QIcon.Off)
        self.button.setIcon(icon23)
        self.button.setIconSize(qt_c.QSize(24, 24))
        self.button.setText(self.button_name)
        label_gap = qt_w.QLabel(central_widget)
        label_gap.setMinimumSize(qt_c.QSize(0, 6))
        label_gap.setMaximumSize(qt_c.QSize(16777215, 6))

        vertical_layout_menu.addWidget(self.button)
        vertical_layout_menu.addWidget(label_gap)

        for category in self.list_categories:
            category.create_widget(scroll_area_content, scroll_area_layout)

        spacer = qt_w.QSpacerItem(1, 1, qt_w.QSizePolicy.Minimum, qt_w.QSizePolicy.Expanding)
        layout.addItem(spacer)

        self.create_links_to_other_pages(central_widget, layout)

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
        
        
        

@dataclass
class aim:
    obj_name: str
    label: str
    icon: str
    options: List[Category]


