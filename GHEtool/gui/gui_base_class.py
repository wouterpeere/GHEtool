"""
This document contains some base functionality for the GUI.
It contains a function to reformat the graphs to a layout for the gui,
and it contains the main class that creates the framework for the GUI (top bar etc.)
"""
from PySide6.QtCore import QMetaObject, QRect, QSize, Qt
from PySide6.QtGui import QAction, QFont, QIcon
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QFrame,
                               QHBoxLayout, QLabel, QListWidget,
                               QListWidgetItem, QMenu, QMenuBar, QProgressBar,
                               QPushButton, QSizePolicy, QSpacerItem,
                               QStackedWidget, QStatusBar, QToolBar,
                               QVBoxLayout, QWidget)

import GHEtool.gui.icons_rc

WHITE: str = "rgb(255, 255, 255)"
LIGHT: str = "rgb(84, 188, 235)"
LIGHT_SELECT: str = "rgb(42, 126, 179)"
DARK: str = "rgb(0, 64, 122)"
GREY: str = "rgb(100, 100, 100)"
WARNING: str = "rgb(255, 200, 87)"
BLACK: str = "rgb(0, 0, 0)"


def set_graph_layout() -> None:
    """
    This function sets the graph layout to the correct format when the GUI is used.

    Returns
    -------
    None
    """
    from matplotlib.colors import to_rgb
    from numpy import array, float64
    import matplotlib.pyplot as plt
    background_color: str = to_rgb(
        array(DARK.replace('rgb(', '').replace(')', '').split(','), dtype=float64) / 255)
    white_color: str = to_rgb(
        array(WHITE.replace('rgb(', '').replace(')', '').split(','), dtype=float64) / 255)
    light_color: str = to_rgb(
        array(LIGHT.replace('rgb(', '').replace(')', '').split(','), dtype=float64) / 255)
    bright_color: str = to_rgb(
        array(WARNING.replace('rgb(', '').replace(')', '').split(','), dtype=float64) / 255)
    plt.rcParams["axes.labelcolor"] = white_color
    plt.rcParams["xtick.color"] = white_color
    plt.rcParams["ytick.color"] = white_color

    plt.rc('figure')
    plt.rcParams['figure.facecolor'] = background_color


class UiGhetool:
    """
    This class contains the framework of the GUI, with the top bar,
    the scenario/run/ ... buttons and the shortcuts.
    """

    menuLanguage: QMenu
    status_bar: QStatusBar
    toolBar: QToolBar
    menuScenario: QMenu
    menuSettings: QMenu
    menuCalculation: QMenu
    pushButton_Cancel: QPushButton
    menuFile: QMenu
    pushButton_start_multiple: QPushButton
    pushButton_start_single: QPushButton
    horizontalSpacer_2: QSpacerItem
    progressBar: QProgressBar
    horizontalLayout_2: QHBoxLayout
    label_Status: QLabel
    horizontalLayout_7: QHBoxLayout
    stackedWidget: QStackedWidget
    verticalLayout_21: QVBoxLayout
    verticalLayout_menu: QVBoxLayout
    list_widget_scenario: QListWidget
    button_rename_scenario: QPushButton
    pushButton_SaveScenario: QPushButton
    verticalLayout_scenario: QVBoxLayout
    horizontalLayout_23: QHBoxLayout
    central_widget: QWidget
    pushButton_DeleteScenario: QPushButton
    action_start_single: QAction
    actionRename_scenario: QAction
    actionSave_As: QAction
    actionDelete_scenario: QAction
    actionAdd_Scenario: QAction
    actionUpdate_Scenario: QAction
    menubar: QMenuBar
    pushButton_AddScenario: QPushButton
    action_start_multiple: QAction
    actionOpen: QAction
    actionSave: QAction
    actionNew: QAction

    def setup_ui(self, ghe_tool):
        if not ghe_tool.objectName():
            ghe_tool.setObjectName("GHEtool")
        ghe_tool.resize(1920, 1080)
        size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(ghe_tool.sizePolicy().hasHeightForWidth())
        ghe_tool.setSizePolicy(size_policy)
        ghe_tool.setMaximumSize(QSize(16777215, 16777215))
        font = QFont()
        font.setFamilies(["Lexend"])
        font.setPointSize(11)
        font.setBold(False)
        font.setItalic(False)
        ghe_tool.setFont(font)
        icon = QIcon()
        icon.addFile(":/icons/icons/icon_05.svg", QSize(), QIcon.Normal, QIcon.Off)
        ghe_tool.setWindowIcon(icon)
        ghe_tool.setStyleSheet(
            f"*{'{'}color: {WHITE};font: 11pt 'Lexend';background-color: {DARK};selection-background-color: {LIGHT};alternate-background-color: {LIGHT};{'}'}\n"
            f"QPushButton{'{'}border: 3px solid {LIGHT};border-radius: 5px;color:{WHITE};gridline-color:{LIGHT};background-color:{LIGHT};font-weight:500;{'}'}"
            f"QPushButton:hover{'{'}background-color: {DARK};{'}'}\n"
            f"QPushButton:disabled{'{'}border: 3px solid {GREY};border-radius: 5px;color: {WHITE};gridline-color: {GREY};background-color: {GREY};{'}'}\n"
            f"QPushButton:disabled:hover{'{'}background-color: {DARK};{'}'}\n"
            f"QComboBox{'{'}border: 1px solid {WHITE};border-bottom-left-radius: 0px;border-bottom-right-radius: 0px;{'}'}\n"
            f"QSpinBox{'{'}selection-color: {WHITE};selection-background-color: {LIGHT};border: 1px solid {WHITE};font: 11pt 'Lexend Deca Light';{'}'}\n"
            f"QLineEdit{'{'}border: 3px solid {LIGHT};border-radius: 5px;color: {WHITE};gridline-color: {LIGHT};background-color: {LIGHT};font-weight:500;\n"
            f"selection-background-color: {LIGHT_SELECT};{'}'}\n"
            f"QLineEdit:hover{'{'}background-color: {DARK};{'}'}"
        )
        self.actionNew = QAction(ghe_tool)
        self.actionNew.setObjectName("actionNew")
        self.actionNew.setCheckable(False)
        self.actionNew.setChecked(False)
        self.actionNew.setEnabled(True)
        icon1 = QIcon()
        icon1.addFile(":/icons/icons/New.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon1.addFile(":/icons/icons/New_Inv.svg", QSize(), QIcon.Active, QIcon.Off)
        self.actionNew.setIcon(icon1)
        self.actionSave = QAction(ghe_tool)
        self.actionSave.setObjectName("actionSave")
        self.actionSave.setEnabled(True)
        icon2 = QIcon()
        icon2.addFile(":/icons/icons/Save.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon2.addFile(":/icons/icons/Save_Inv.svg", QSize(), QIcon.Active, QIcon.Off)
        self.actionSave.setIcon(icon2)
        self.actionOpen = QAction(ghe_tool)
        self.actionOpen.setObjectName("actionOpen")
        self.actionOpen.setEnabled(True)
        icon3 = QIcon()
        icon3.addFile(":/icons/icons/Open.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon3.addFile(":/icons/icons/Open_Inv.svg", QSize(), QIcon.Active, QIcon.Off)
        self.actionOpen.setIcon(icon3)
        self.action_start_multiple = QAction(ghe_tool)
        self.action_start_multiple.setObjectName("action_start_multiple")
        self.action_start_multiple.setEnabled(True)
        icon4 = QIcon()
        icon4.addFile(":/icons/icons/Start_multiple_inv.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon4.addFile(":/icons/icons/Start_multiple.svg", QSize(), QIcon.Active, QIcon.Off)
        self.action_start_multiple.setIcon(icon4)
        self.actionUpdate_Scenario = QAction(ghe_tool)
        self.actionUpdate_Scenario.setObjectName("actionUpdate_Scenario")
        icon7 = QIcon()
        icon7.addFile(":/icons/icons/Update_Inv.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon7.addFile(":/icons/icons/Update.svg", QSize(), QIcon.Active, QIcon.Off)
        self.actionUpdate_Scenario.setIcon(icon7)
        self.actionAdd_Scenario = QAction(ghe_tool)
        self.actionAdd_Scenario.setObjectName("actionAdd_Scenario")
        icon8 = QIcon()
        icon8.addFile(":/icons/icons/Add_Inv.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon8.addFile(":/icons/icons/Add.svg", QSize(), QIcon.Active, QIcon.Off)
        self.actionAdd_Scenario.setIcon(icon8)
        self.actionDelete_scenario = QAction(ghe_tool)
        self.actionDelete_scenario.setObjectName("actionDelete_scenario")
        icon9 = QIcon()
        icon9.addFile(":/icons/icons/Delete_Inv.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon9.addFile(":/icons/icons/Delete.svg", QSize(), QIcon.Active, QIcon.Off)
        self.actionDelete_scenario.setIcon(icon9)
        self.actionSave_As = QAction(ghe_tool)
        self.actionSave_As.setObjectName("actionSave_As")
        icon10 = QIcon()
        icon10.addFile(":/icons/icons/SaveAs.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon10.addFile(":/icons/icons/Save_As_Inv.svg", QSize(), QIcon.Active, QIcon.Off)
        self.actionSave_As.setIcon(icon10)
        self.actionRename_scenario = QAction(ghe_tool)
        self.actionRename_scenario.setObjectName("actionRename_scenario")
        icon14 = QIcon()
        icon14.addFile(":/icons/icons/Rename_Inv.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon14.addFile(":/icons/icons/Rename.svg", QSize(), QIcon.Active, QIcon.Off)
        self.actionRename_scenario.setIcon(icon14)
        self.action_start_single = QAction(ghe_tool)
        self.action_start_single.setObjectName("action_start_single")
        icon15 = QIcon()
        icon15.addFile(":/icons/icons/Start_inv.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon15.addFile(":/icons/icons/Start.svg", QSize(), QIcon.Active, QIcon.Off)
        self.action_start_single.setIcon(icon15)
        self.central_widget = QWidget(ghe_tool)
        self.central_widget.setObjectName("central_widget")
        self.horizontalLayout_23 = QHBoxLayout(self.central_widget)
        self.horizontalLayout_23.setObjectName("horizontalLayout_23")
        self.verticalLayout_scenario = QVBoxLayout()
        self.verticalLayout_scenario.setObjectName("verticalLayout_scenario")
        self.pushButton_SaveScenario = QPushButton(self.central_widget)
        self.pushButton_SaveScenario.setObjectName("pushButton_SaveScenario")
        size_policy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        size_policy1.setHorizontalStretch(0)
        size_policy1.setVerticalStretch(0)
        size_policy1.setHeightForWidth(self.pushButton_SaveScenario.sizePolicy().hasHeightForWidth())
        self.pushButton_SaveScenario.setSizePolicy(size_policy1)
        self.pushButton_SaveScenario.setMinimumSize(QSize(180, 30))
        self.pushButton_SaveScenario.setMaximumSize(QSize(250, 30))
        self.pushButton_SaveScenario.setStyleSheet("text-align:left;")
        icon18 = QIcon()
        icon18.addFile(":/icons/icons/Update.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_SaveScenario.setIcon(icon18)
        self.pushButton_SaveScenario.setIconSize(QSize(20, 20))

        self.verticalLayout_scenario.addWidget(self.pushButton_SaveScenario)

        self.pushButton_AddScenario = QPushButton(self.central_widget)
        self.pushButton_AddScenario.setObjectName("pushButton_AddScenario")
        self.pushButton_AddScenario.setMinimumSize(QSize(180, 30))
        self.pushButton_AddScenario.setMaximumSize(QSize(250, 30))
        self.pushButton_AddScenario.setStyleSheet("text-align:left;")
        icon19 = QIcon()
        icon19.addFile(":/icons/icons/Add.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_AddScenario.setIcon(icon19)
        self.pushButton_AddScenario.setIconSize(QSize(20, 20))

        self.verticalLayout_scenario.addWidget(self.pushButton_AddScenario)

        self.pushButton_DeleteScenario = QPushButton(self.central_widget)
        self.pushButton_DeleteScenario.setObjectName("pushButton_DeleteScenario")
        self.pushButton_DeleteScenario.setMinimumSize(QSize(180, 30))
        self.pushButton_DeleteScenario.setMaximumSize(QSize(250, 30))
        self.pushButton_DeleteScenario.setStyleSheet("text-align:left;")
        icon20 = QIcon()
        icon20.addFile(":/icons/icons/Delete.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_DeleteScenario.setIcon(icon20)
        self.pushButton_DeleteScenario.setIconSize(QSize(20, 20))

        self.verticalLayout_scenario.addWidget(self.pushButton_DeleteScenario)

        self.button_rename_scenario = QPushButton(self.central_widget)
        self.button_rename_scenario.setObjectName("button_rename_scenario")
        self.button_rename_scenario.setMinimumSize(QSize(180, 30))
        self.button_rename_scenario.setMaximumSize(QSize(250, 30))
        self.button_rename_scenario.setStyleSheet("text-align:left;")
        icon21 = QIcon()
        icon21.addFile(":/icons/icons/Rename.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.button_rename_scenario.setIcon(icon21)
        self.button_rename_scenario.setIconSize(QSize(20, 20))

        self.verticalLayout_scenario.addWidget(self.button_rename_scenario)

        self.list_widget_scenario = QListWidget(self.central_widget)
        QListWidgetItem(self.list_widget_scenario)
        self.list_widget_scenario.setObjectName("list_widget_scenario")
        size_policy.setHeightForWidth(self.list_widget_scenario.sizePolicy().hasHeightForWidth())
        self.list_widget_scenario.setSizePolicy(size_policy)
        self.list_widget_scenario.setMaximumSize(QSize(16666711, 16666711))
        self.list_widget_scenario.setStyleSheet(
            f"*{'{'}border: 1px solid {WHITE};{'}'}\n"
            "QListWidget{outline: 0;}\n"
            f"QListWidget::item:selected{'{'}background:{LIGHT};color: {WHITE};border: 0px solid {WHITE};{'}'}\n"
            f"QListWidget::item:hover{'{'}border: 1px solid {WHITE};color: {WHITE};{'}'}QListWidget:disabled{'{'}background-color: {GREY};{'}'}"
        )
        self.list_widget_scenario.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.list_widget_scenario.setAutoScrollMargin(10)
        self.list_widget_scenario.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed | QAbstractItemView.SelectedClicked)
        self.list_widget_scenario.setDragDropMode(QAbstractItemView.DragDrop)
        self.list_widget_scenario.setDefaultDropAction(Qt.TargetMoveAction)
        self.list_widget_scenario.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.list_widget_scenario.setSelectionRectVisible(False)

        self.verticalLayout_scenario.addWidget(self.list_widget_scenario)

        self.horizontalLayout_23.addLayout(self.verticalLayout_scenario)

        self.verticalLayout_menu = QVBoxLayout()
        self.verticalLayout_menu.setSpacing(0)
        self.verticalLayout_menu.setObjectName("verticalLayout_menu")

        self.horizontalLayout_23.addLayout(self.verticalLayout_menu)

        self.verticalLayout_21 = QVBoxLayout()
        self.verticalLayout_21.setObjectName("verticalLayout_21")
        self.stackedWidget = QStackedWidget(self.central_widget)
        self.stackedWidget.setObjectName("stackedWidget")
        self.stackedWidget.setFrameShadow(QFrame.Plain)
        self.stackedWidget.setLineWidth(0)

        self.verticalLayout_21.addWidget(self.stackedWidget)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_Status = QLabel(self.central_widget)
        self.label_Status.setObjectName("label_Status")
        self.label_Status.setStyleSheet(f"*{'{'}background-color: {LIGHT};{'}'}")
        self.horizontalLayout_7.addWidget(self.label_Status)

        self.progressBar = QProgressBar(self.central_widget)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setStyleSheet(
            f"QProgressBar{'{'}border: 1px solid {WHITE};border-radius: 10px;text-align: center;color: {WHITE};{'}'}\n"
            f"QProgressBar::chunk{'{'}background-color: {LIGHT}; border-radius: 10px;{'}'}"
        )
        self.progressBar.setValue(24)

        self.horizontalLayout_7.addWidget(self.progressBar)

        self.verticalLayout_21.addLayout(self.horizontalLayout_7)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.pushButton_start_single = QPushButton(self.central_widget)
        self.pushButton_start_single.setObjectName("pushButton_start_single")
        self.pushButton_start_single.setMinimumSize(QSize(100, 40))
        self.pushButton_start_single.setMaximumSize(QSize(16777215, 40))
        icon32 = QIcon()
        icon32.addFile(":/icons/icons/Start.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_start_single.setIcon(icon32)
        self.pushButton_start_single.setIconSize(QSize(24, 24))

        self.horizontalLayout_2.addWidget(self.pushButton_start_single)

        self.pushButton_start_multiple = QPushButton(self.central_widget)
        self.pushButton_start_multiple.setObjectName("pushButton_start_multiple")
        self.pushButton_start_multiple.setMinimumSize(QSize(100, 40))
        self.pushButton_start_multiple.setMaximumSize(QSize(16777215, 40))
        icon33 = QIcon()
        icon33.addFile(":/icons/icons/Start_multiple.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_start_multiple.setIcon(icon33)
        self.pushButton_start_multiple.setIconSize(QSize(24, 24))

        self.horizontalLayout_2.addWidget(self.pushButton_start_multiple)

        self.pushButton_Cancel = QPushButton(self.central_widget)
        self.pushButton_Cancel.setObjectName("pushButton_Cancel")
        self.pushButton_Cancel.setMinimumSize(QSize(100, 40))
        self.pushButton_Cancel.setMaximumSize(QSize(16777215, 40))
        icon34 = QIcon()
        icon34.addFile(":/icons/icons/Exit.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_Cancel.setIcon(icon34)
        self.pushButton_Cancel.setIconSize(QSize(24, 24))

        self.horizontalLayout_2.addWidget(self.pushButton_Cancel)

        self.verticalLayout_21.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_23.addLayout(self.verticalLayout_21)

        ghe_tool.setCentralWidget(self.central_widget)
        self.menubar = QMenuBar(ghe_tool)
        self.menubar.setObjectName("menubar")
        self.menubar.setEnabled(True)
        self.menubar.setGeometry(QRect(0, 0, 1226, 30))
        self.menubar.setStyleSheet(
            f"QMenuBar::item{'{'}background-color: {DARK};{'}'}\n"
            f"QMenuBar::item:pressed{'{'}background-color: {LIGHT};{'}'}\n"
            f"QMenuBar::item:selected{'{'}background-color: {LIGHT};{'}'}\n"
            f"QToolTip{'{'} color: {WHITE}; background-color: {BLACK}; border: none; {'}'}"
        )
        self.menubar.setNativeMenuBar(True)
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuFile.setStyleSheet(
            f"QAction::icon {'{'} background-color:{LIGHT};selection-background-color: {LIGHT};{'}'}\n"
            f"*{'{'}	background-color: {DARK};{'}'}\n"
            f"*:hover{'{'}background-color: {LIGHT};{'}'}"
        )
        self.menuFile.setTearOffEnabled(False)
        self.menuCalculation = QMenu(self.menubar)
        self.menuCalculation.setObjectName("menuCalculation")
        self.menuSettings = QMenu(self.menubar)
        self.menuSettings.setObjectName("menuSettings")
        self.menuLanguage = QMenu(self.menuSettings)
        self.menuLanguage.setObjectName("menuLanguage")
        self.menuLanguage.setEnabled(True)
        icon35 = QIcon()
        icon35.addFile(":/icons/icons/Language.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon35.addFile(":/icons/icons/Language_Inv.svg", QSize(), QIcon.Active, QIcon.Off)
        self.menuLanguage.setIcon(icon35)
        self.menuScenario = QMenu(self.menubar)
        self.menuScenario.setObjectName("menuScenario")
        ghe_tool.setMenuBar(self.menubar)
        self.toolBar = QToolBar(ghe_tool)
        self.toolBar.setObjectName("toolBar")
        self.toolBar.setStyleSheet(
            f"QAction::icon {'{'} background-color:{LIGHT};selection-background-color: {LIGHT};{'}'}\n"
            f"*{'{'}	background-color: {DARK};{'}'}\n"
            f"*:hover{'{'}background-color: {LIGHT};{'}'}"
        )
        self.toolBar.setMovable(False)
        ghe_tool.addToolBar(Qt.TopToolBarArea, self.toolBar)
        self.status_bar = QStatusBar(ghe_tool)
        self.status_bar.setObjectName("status_bar")
        self.status_bar.setStyleSheet(f"QStatusBar::item{'{'}border:None;{'}'}QStatusBar{'{'}color:{BLACK};background-color: {LIGHT};{'}'}")
        ghe_tool.setStatusBar(self.status_bar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuCalculation.menuAction())
        self.menubar.addAction(self.menuScenario.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSave_As)
        self.menuFile.addAction(self.actionOpen)
        self.menuCalculation.addAction(self.action_start_multiple)
        self.menuCalculation.addAction(self.action_start_single)
        self.menuSettings.addAction(self.menuLanguage.menuAction())
        self.menuScenario.addAction(self.actionUpdate_Scenario)
        self.menuScenario.addAction(self.actionAdd_Scenario)
        self.menuScenario.addAction(self.actionDelete_scenario)
        self.menuScenario.addAction(self.actionRename_scenario)
        self.toolBar.addAction(self.actionNew)
        self.toolBar.addAction(self.actionSave)
        self.toolBar.addAction(self.actionSave_As)
        self.toolBar.addAction(self.actionOpen)
        self.toolBar.addAction(self.action_start_single)
        self.toolBar.addAction(self.action_start_multiple)
        self.toolBar.addAction(self.actionUpdate_Scenario)
        self.toolBar.addAction(self.actionAdd_Scenario)
        self.toolBar.addAction(self.actionDelete_scenario)
        self.toolBar.addAction(self.actionRename_scenario)

        self.button_rename_scenario.clicked.connect(self.actionRename_scenario.trigger)
        self.pushButton_Cancel.clicked.connect(ghe_tool.close)
        self.pushButton_start_multiple.clicked.connect(self.action_start_multiple.trigger)
        self.pushButton_AddScenario.clicked.connect(self.actionAdd_Scenario.trigger)
        self.pushButton_DeleteScenario.clicked.connect(self.actionDelete_scenario.trigger)
        self.pushButton_SaveScenario.clicked.connect(self.actionUpdate_Scenario.trigger)
        self.list_widget_scenario.itemDoubleClicked.connect(self.actionRename_scenario.trigger)
        self.pushButton_start_single.clicked.connect(self.action_start_single.trigger)

        self.stackedWidget.setCurrentIndex(0)
        QMetaObject.connectSlotsByName(ghe_tool)

        ghe_tool.setWindowTitle("GHEtool")
        self.actionNew.setText("New")
        # if QT_CONFIG(tooltip)
        self.actionNew.setToolTip("Create new project file")
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.actionNew.setShortcut("Ctrl+N")
        # endif // QT_CONFIG(shortcut)
        self.actionSave.setText("Save")
        # if QT_CONFIG(shortcut)
        self.actionSave.setShortcut("Ctrl+S")
        # endif // QT_CONFIG(shortcut)
        self.actionOpen.setText("Open")
        # if QT_CONFIG(shortcut)
        self.actionOpen.setShortcut("Ctrl+O")
        # endif // QT_CONFIG(shortcut)
        self.action_start_multiple.setText("Calculate all scenarios")
        # if QT_CONFIG(shortcut)
        self.action_start_multiple.setShortcut("Ctrl+R")
        # endif // QT_CONFIG(shortcut)
        self.actionUpdate_Scenario.setText("Update scenario")
        # if QT_CONFIG(shortcut)
        self.actionUpdate_Scenario.setShortcut("Ctrl+Shift+S")
        # endif // QT_CONFIG(shortcut)
        self.actionAdd_Scenario.setText("Add scenario")
        # if QT_CONFIG(shortcut)
        self.actionAdd_Scenario.setShortcut("Ctrl+Shift+A")
        # endif // QT_CONFIG(shortcut)
        self.actionDelete_scenario.setText("Delete scenario")
        # if QT_CONFIG(shortcut)
        self.actionDelete_scenario.setShortcut("Ctrl+Shift+D")
        # endif // QT_CONFIG(shortcut)
        self.actionSave_As.setText("Save As")
        # if QT_CONFIG(shortcut)
        self.actionSave_As.setShortcut("F12")
        # endif // QT_CONFIG(shortcut)
        self.actionRename_scenario.setText("Rename scenario")
        # if QT_CONFIG(shortcut)
        self.actionRename_scenario.setShortcut("Ctrl+Shift+R")
        # endif // QT_CONFIG(shortcut)
        self.action_start_single.setText("Calculate current scenario")
        # if QT_CONFIG(shortcut)
        self.action_start_single.setShortcut("Ctrl+Shift+R")
        # endif // QT_CONFIG(shortcut)
        self.pushButton_SaveScenario.setText("Update scenario")
        self.pushButton_AddScenario.setText("Add scenario")
        self.pushButton_DeleteScenario.setText("Delete scenario")
        self.button_rename_scenario.setText("Rename scenario")

        __sortingEnabled = self.list_widget_scenario.isSortingEnabled()
        self.list_widget_scenario.setSortingEnabled(False)
        ___qlistwidgetitem = self.list_widget_scenario.item(0)
        ___qlistwidgetitem.setText("Scenario: 1")
        self.list_widget_scenario.setSortingEnabled(__sortingEnabled)
        self.label_Status.setText("Progress: ")
        self.pushButton_start_single.setText("Calculate current scenario")
        self.pushButton_start_multiple.setText("Calculate all scenarios")
        self.pushButton_Cancel.setText("Exit")
        self.menuFile.setTitle("File")
        self.menuCalculation.setTitle("Calculation")
        self.menuSettings.setTitle("Settings")
        self.menuLanguage.setTitle("Language")
        self.menuScenario.setTitle("Scenario")
        self.toolBar.setWindowTitle("toolBar")
