from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSize, Qt
from PySide6.QtGui import QAction, QFont, QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QAbstractScrollArea,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMenuBar,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QStackedWidget,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

import GHEtool.gui.icons_rc

WHITE: str = "rgb(255, 255, 255)"
LIGHT: str = "rgb(84, 188, 235)"
LIGHT_SELECT: str = "rgb(42, 126, 179)"
DARK: str = "rgb(0, 64, 122)"
GREY: str = "rgb(100, 100, 100)"
WARNING: str = "rgb(255, 200, 87)"


class Ui_GHEtool:
    def setupUi(self, GHETool):
        if not GHETool.objectName():
            GHETool.setObjectName("GHEtool")
        GHETool.resize(1226, 869)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(GHETool.sizePolicy().hasHeightForWidth())
        GHETool.setSizePolicy(sizePolicy)
        GHETool.setMaximumSize(QSize(16777215, 16777215))
        font = QFont()
        font.setFamilies(["Lexend"])
        font.setPointSize(11)
        font.setBold(False)
        font.setItalic(False)
        GHETool.setFont(font)
        icon = QIcon()
        icon.addFile(":/icons/icons/icon_05.svg", QSize(), QIcon.Normal, QIcon.Off)
        GHETool.setWindowIcon(icon)
        GHETool.setStyleSheet(
            "*{\n"
            f"color: {WHITE};\n"
            'font: 11pt "Lexend";\n'
            f"background-color: {DARK};\n"
            f"selection-background-color: {LIGHT};\n"
            f"alternate-background-color: {LIGHT};\n"
            "}\n"
            "QPushButton{\n"
            f"border: 3px solid {LIGHT};\n"
            "border-radius: 5px;\n"
            f"color: {WHITE};\n"
            f"gridline-color: {LIGHT};\n"
            f"background-color: {LIGHT};\n"
            "font-weight:500;}\n"
            "QPushButton:hover{\n"
            f"background-color: {DARK};\n"
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
            "}\n"
            "QComboBox{\n"
            f"border: 1px solid {WHITE};\n"
            "border-bottom-left-radius: 0px;\n"
            "border-bottom-right-radius: 0px;\n"
            "}\n"
            "QSpinBox{\n"
            f"selection-color: {WHITE};\n"
            f"selection-background-color: {LIGHT};\n"
            f"border: 1px solid {WHITE};\n"
            'font: 11pt "Lexend Deca Light";}\n'
            "QLineEdit{\n"
            f"border: 3px solid {LIGHT};\n"
            "border-radius: 5px;\n"
            f"color: {WHITE};\n"
            f"gridline-color: {LIGHT};\n"
            f"background-color: {LIGHT};\n"
            "font-weight:500;\n"
            f"selection-background-color: {LIGHT_SELECT};\n"
            "}\n"
            "QLineEdit:hover{\n"
            f"background-color: {DARK};\n"
            "}"
        )
        self.actionNew = QAction(GHETool)
        self.actionNew.setObjectName("actionNew")
        self.actionNew.setCheckable(False)
        self.actionNew.setChecked(False)
        self.actionNew.setEnabled(True)
        icon1 = QIcon()
        icon1.addFile(":/icons/icons/New.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon1.addFile(":/icons/icons/New_Inv.svg", QSize(), QIcon.Active, QIcon.Off)
        self.actionNew.setIcon(icon1)
        self.actionSave = QAction(GHETool)
        self.actionSave.setObjectName("actionSave")
        self.actionSave.setEnabled(True)
        icon2 = QIcon()
        icon2.addFile(":/icons/icons/Save.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon2.addFile(":/icons/icons/Save_Inv.svg", QSize(), QIcon.Active, QIcon.Off)
        self.actionSave.setIcon(icon2)
        self.actionOpen = QAction(GHETool)
        self.actionOpen.setObjectName("actionOpen")
        self.actionOpen.setEnabled(True)
        icon3 = QIcon()
        icon3.addFile(":/icons/icons/Open.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon3.addFile(":/icons/icons/Open_Inv.svg", QSize(), QIcon.Active, QIcon.Off)
        self.actionOpen.setIcon(icon3)
        self.action_start_multiple = QAction(GHETool)
        self.action_start_multiple.setObjectName("action_start_multiple")
        self.action_start_multiple.setEnabled(True)
        icon4 = QIcon()
        icon4.addFile(":/icons/icons/Start_multiple_inv.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon4.addFile(":/icons/icons/Start_multiple.svg", QSize(), QIcon.Active, QIcon.Off)
        self.action_start_multiple.setIcon(icon4)
        self.actionGerman = QAction(GHETool)
        self.actionGerman.setObjectName("actionGerman")
        icon5 = QIcon()
        icon5.addFile(":/icons/icons/Flag_German.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionGerman.setIcon(icon5)
        self.actionEnglish = QAction(GHETool)
        self.actionEnglish.setObjectName("actionEnglish")
        icon6 = QIcon()
        icon6.addFile(":/icons/icons/Flag_English.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionEnglish.setIcon(icon6)
        self.actionUpdate_Scenario = QAction(GHETool)
        self.actionUpdate_Scenario.setObjectName("actionUpdate_Scenario")
        icon7 = QIcon()
        icon7.addFile(":/icons/icons/Update_Inv.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon7.addFile(":/icons/icons/Update.svg", QSize(), QIcon.Active, QIcon.Off)
        self.actionUpdate_Scenario.setIcon(icon7)
        self.actionAdd_Scenario = QAction(GHETool)
        self.actionAdd_Scenario.setObjectName("actionAdd_Scenario")
        icon8 = QIcon()
        icon8.addFile(":/icons/icons/Add_Inv.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon8.addFile(":/icons/icons/Add.svg", QSize(), QIcon.Active, QIcon.Off)
        self.actionAdd_Scenario.setIcon(icon8)
        self.actionDelete_scenario = QAction(GHETool)
        self.actionDelete_scenario.setObjectName("actionDelete_scenario")
        icon9 = QIcon()
        icon9.addFile(":/icons/icons/Delete_Inv.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon9.addFile(":/icons/icons/Delete.svg", QSize(), QIcon.Active, QIcon.Off)
        self.actionDelete_scenario.setIcon(icon9)
        self.actionSave_As = QAction(GHETool)
        self.actionSave_As.setObjectName("actionSave_As")
        icon10 = QIcon()
        icon10.addFile(":/icons/icons/SaveAs.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon10.addFile(":/icons/icons/Save_As_Inv.svg", QSize(), QIcon.Active, QIcon.Off)
        self.actionSave_As.setIcon(icon10)
        self.actionDutch = QAction(GHETool)
        self.actionDutch.setObjectName("actionDutch")
        icon11 = QIcon()
        icon11.addFile(":/icons/icons/Flag_Dutch.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionDutch.setIcon(icon11)
        self.actionItalian = QAction(GHETool)
        self.actionItalian.setObjectName("actionItalian")
        icon12 = QIcon()
        icon12.addFile(":/icons/icons/Flag_Italian.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionItalian.setIcon(icon12)
        self.actionFrench = QAction(GHETool)
        self.actionFrench.setObjectName("actionFrench")
        icon13 = QIcon()
        icon13.addFile(":/icons/icons/Flag_French.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionFrench.setIcon(icon13)
        self.actionRename_scenario = QAction(GHETool)
        self.actionRename_scenario.setObjectName("actionRename_scenario")
        icon14 = QIcon()
        icon14.addFile(":/icons/icons/Rename_Inv.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon14.addFile(":/icons/icons/Rename.svg", QSize(), QIcon.Active, QIcon.Off)
        self.actionRename_scenario.setIcon(icon14)
        self.action_start_single = QAction(GHETool)
        self.action_start_single.setObjectName("action_start_single")
        icon15 = QIcon()
        icon15.addFile(":/icons/icons/Start_inv.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon15.addFile(":/icons/icons/Start.svg", QSize(), QIcon.Active, QIcon.Off)
        self.action_start_single.setIcon(icon15)
        self.actionSpanish = QAction(GHETool)
        self.actionSpanish.setObjectName("actionSpanish")
        icon16 = QIcon()
        icon16.addFile(":/icons/icons/Flag_Spain.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionSpanish.setIcon(icon16)
        self.actionInputChanged = QAction(GHETool)
        self.actionInputChanged.setObjectName("actionInputChanged")
        self.actionCheckUDistance = QAction(GHETool)
        self.actionCheckUDistance.setObjectName("actionCheckUDistance")
        self.actionUpdateBoreholeGraph = QAction(GHETool)
        self.actionUpdateBoreholeGraph.setObjectName("actionUpdateBoreholeGraph")
        self.actionGalician = QAction(GHETool)
        self.actionGalician.setObjectName("actionGalician")
        icon17 = QIcon()
        icon17.addFile(":/icons/icons/Flag_Galicia.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionGalician.setIcon(icon17)
        self.centralwidget = QWidget(GHETool)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("")
        self.horizontalLayout_23 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_23.setObjectName("horizontalLayout_23")
        self.verticalLayout_scenario = QVBoxLayout()
        self.verticalLayout_scenario.setObjectName("verticalLayout_scenario")
        self.pushButton_SaveScenario = QPushButton(self.centralwidget)
        self.pushButton_SaveScenario.setObjectName("pushButton_SaveScenario")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.pushButton_SaveScenario.sizePolicy().hasHeightForWidth())
        self.pushButton_SaveScenario.setSizePolicy(sizePolicy1)
        self.pushButton_SaveScenario.setMinimumSize(QSize(180, 30))
        self.pushButton_SaveScenario.setMaximumSize(QSize(250, 30))
        self.pushButton_SaveScenario.setStyleSheet("text-align:left;")
        icon18 = QIcon()
        icon18.addFile(":/icons/icons/Update.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_SaveScenario.setIcon(icon18)
        self.pushButton_SaveScenario.setIconSize(QSize(20, 20))

        self.verticalLayout_scenario.addWidget(self.pushButton_SaveScenario)

        self.pushButton_AddScenario = QPushButton(self.centralwidget)
        self.pushButton_AddScenario.setObjectName("pushButton_AddScenario")
        self.pushButton_AddScenario.setMinimumSize(QSize(180, 30))
        self.pushButton_AddScenario.setMaximumSize(QSize(250, 30))
        self.pushButton_AddScenario.setStyleSheet("text-align:left;")
        icon19 = QIcon()
        icon19.addFile(":/icons/icons/Add.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_AddScenario.setIcon(icon19)
        self.pushButton_AddScenario.setIconSize(QSize(20, 20))

        self.verticalLayout_scenario.addWidget(self.pushButton_AddScenario)

        self.pushButton_DeleteScenario = QPushButton(self.centralwidget)
        self.pushButton_DeleteScenario.setObjectName("pushButton_DeleteScenario")
        self.pushButton_DeleteScenario.setMinimumSize(QSize(180, 30))
        self.pushButton_DeleteScenario.setMaximumSize(QSize(250, 30))
        self.pushButton_DeleteScenario.setStyleSheet("text-align:left;")
        icon20 = QIcon()
        icon20.addFile(":/icons/icons/Delete.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_DeleteScenario.setIcon(icon20)
        self.pushButton_DeleteScenario.setIconSize(QSize(20, 20))

        self.verticalLayout_scenario.addWidget(self.pushButton_DeleteScenario)

        self.button_rename_scenario = QPushButton(self.centralwidget)
        self.button_rename_scenario.setObjectName("button_rename_scenario")
        self.button_rename_scenario.setMinimumSize(QSize(180, 30))
        self.button_rename_scenario.setMaximumSize(QSize(250, 30))
        self.button_rename_scenario.setStyleSheet("text-align:left;")
        icon21 = QIcon()
        icon21.addFile(":/icons/icons/Rename.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.button_rename_scenario.setIcon(icon21)
        self.button_rename_scenario.setIconSize(QSize(20, 20))

        self.verticalLayout_scenario.addWidget(self.button_rename_scenario)

        self.list_widget_scenario = QListWidget(self.centralwidget)
        QListWidgetItem(self.list_widget_scenario)
        self.list_widget_scenario.setObjectName("list_widget_scenario")
        sizePolicy.setHeightForWidth(self.list_widget_scenario.sizePolicy().hasHeightForWidth())
        self.list_widget_scenario.setSizePolicy(sizePolicy)
        self.list_widget_scenario.setMaximumSize(QSize(16666711, 16666711))
        self.list_widget_scenario.setStyleSheet(
            "*{border: 1px solid white;}\n"
            "QListWidget{outline: 0;}\n"
            "QListWidget::item:selected{\n"
            f"background:{LIGHT};color: {WHITE};border: 0px solid white;\n"
            "}\n"
            "QListWidget::item:hover{border: 1px solid white;color: rgb(255, 255, 255);}"
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
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName("stackedWidget")
        self.stackedWidget.setStyleSheet("")
        self.stackedWidget.setFrameShadow(QFrame.Plain)
        self.stackedWidget.setLineWidth(0)

        self.verticalLayout_21.addWidget(self.stackedWidget)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_Status = QLabel(self.centralwidget)
        self.label_Status.setObjectName("label_Status")

        self.horizontalLayout_7.addWidget(self.label_Status)

        self.progressBar = QProgressBar(self.centralwidget)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setStyleSheet(
            "QProgressBar{border: 1px solid white;\n"
            " border-radius: 10px;\n"
            "text-align: center;\n"
            " color: #ffffff;\n"
            "}QProgressBar::chunk{background-color: #54bceb; border-radius: 10px;}"
        )
        self.progressBar.setValue(24)

        self.horizontalLayout_7.addWidget(self.progressBar)

        self.verticalLayout_21.addLayout(self.horizontalLayout_7)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.pushButton_start_single = QPushButton(self.centralwidget)
        self.pushButton_start_single.setObjectName("pushButton_start_single")
        self.pushButton_start_single.setMinimumSize(QSize(100, 40))
        self.pushButton_start_single.setMaximumSize(QSize(16777215, 40))
        self.pushButton_start_single.setStyleSheet("")
        icon32 = QIcon()
        icon32.addFile(":/icons/icons/Start.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_start_single.setIcon(icon32)
        self.pushButton_start_single.setIconSize(QSize(24, 24))

        self.horizontalLayout_2.addWidget(self.pushButton_start_single)

        self.pushButton_start_multiple = QPushButton(self.centralwidget)
        self.pushButton_start_multiple.setObjectName("pushButton_start_multiple")
        self.pushButton_start_multiple.setMinimumSize(QSize(100, 40))
        self.pushButton_start_multiple.setMaximumSize(QSize(16777215, 40))
        self.pushButton_start_multiple.setStyleSheet("")
        icon33 = QIcon()
        icon33.addFile(":/icons/icons/Start_multiple.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_start_multiple.setIcon(icon33)
        self.pushButton_start_multiple.setIconSize(QSize(24, 24))

        self.horizontalLayout_2.addWidget(self.pushButton_start_multiple)

        self.pushButton_Cancel = QPushButton(self.centralwidget)
        self.pushButton_Cancel.setObjectName("pushButton_Cancel")
        self.pushButton_Cancel.setMinimumSize(QSize(100, 40))
        self.pushButton_Cancel.setMaximumSize(QSize(16777215, 40))
        self.pushButton_Cancel.setStyleSheet("")
        icon34 = QIcon()
        icon34.addFile(":/icons/icons/Exit.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_Cancel.setIcon(icon34)
        self.pushButton_Cancel.setIconSize(QSize(24, 24))

        self.horizontalLayout_2.addWidget(self.pushButton_Cancel)

        self.verticalLayout_21.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_23.addLayout(self.verticalLayout_21)

        GHETool.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(GHETool)
        self.menubar.setObjectName("menubar")
        self.menubar.setEnabled(True)
        self.menubar.setGeometry(QRect(0, 0, 1226, 30))
        self.menubar.setStyleSheet(
            "QMenuBar::item{\n"
            "    background-color: rgb(0, 64, 122);\n"
            "}\n"
            "QMenuBar::item:pressed {	background-color:rgb(84, 188, 235);}\n"
            "QMenuBar::item:selected{	background-color:rgb(84, 188, 235);}\n"
            "QToolTip { color: #fff; background-color: #000; border: none; }"
        )
        self.menubar.setNativeMenuBar(True)
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuFile.setStyleSheet(
            "QAction::icon { background-color:rgb(84, 188, 235);\n"
            "selection-background-color: rgb(84, 188, 235);}\n"
            "*{	background-color: rgb(0, 64, 122);}\n"
            "*:hover{background-color: rgb(84, 188, 235);}"
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
        GHETool.setMenuBar(self.menubar)
        self.toolBar = QToolBar(GHETool)
        self.toolBar.setObjectName("toolBar")
        self.toolBar.setStyleSheet(
            "*{\n"
            "	background-color: rgb(0, 64, 122);\n"
            "}\n"
            "*:hover{background-color: rgb(84, 188, 235);}\n"
            "QToolTip { color: rgb(0, 0, 0); background-color: rgb(255, 255, 255);border: 1px solid rgb(84, 188, 235); }"
        )
        self.toolBar.setMovable(False)
        GHETool.addToolBar(Qt.TopToolBarArea, self.toolBar)
        self.status_bar = QStatusBar(GHETool)
        self.status_bar.setObjectName("status_bar")
        self.status_bar.setStyleSheet("QStatusBar::item{border:None;}")
        GHETool.setStatusBar(self.status_bar)

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
        self.menuLanguage.addAction(self.actionEnglish)
        self.menuLanguage.addAction(self.actionGerman)
        self.menuLanguage.addAction(self.actionDutch)
        self.menuLanguage.addAction(self.actionItalian)
        self.menuLanguage.addAction(self.actionFrench)
        self.menuLanguage.addAction(self.actionSpanish)
        self.menuLanguage.addAction(self.actionGalician)
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

        self.retranslateUi(GHETool)
        self.button_rename_scenario.clicked.connect(self.actionRename_scenario.trigger)
        self.pushButton_Cancel.clicked.connect(GHETool.close)
        self.pushButton_start_multiple.clicked.connect(self.action_start_multiple.trigger)
        self.pushButton_AddScenario.clicked.connect(self.actionAdd_Scenario.trigger)
        self.pushButton_DeleteScenario.clicked.connect(self.actionDelete_scenario.trigger)
        self.pushButton_SaveScenario.clicked.connect(self.actionUpdate_Scenario.trigger)
        self.list_widget_scenario.itemDoubleClicked.connect(self.actionRename_scenario.trigger)
        self.pushButton_start_single.clicked.connect(self.action_start_single.trigger)

        self.stackedWidget.setCurrentIndex(0)
        QMetaObject.connectSlotsByName(GHETool)

    # setupUi

    def retranslateUi(self, GHEtool):
        GHEtool.setWindowTitle(QCoreApplication.translate("GHEtool", "GHEtool", None))
        self.actionNew.setText(QCoreApplication.translate("GHEtool", "New", None))
        # if QT_CONFIG(tooltip)
        self.actionNew.setToolTip(QCoreApplication.translate("GHEtool", "Create new project file", None))
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.actionNew.setShortcut(QCoreApplication.translate("GHEtool", "Ctrl+N", None))
        # endif // QT_CONFIG(shortcut)
        self.actionSave.setText(QCoreApplication.translate("GHEtool", "Save", None))
        # if QT_CONFIG(shortcut)
        self.actionSave.setShortcut(QCoreApplication.translate("GHEtool", "Ctrl+S", None))
        # endif // QT_CONFIG(shortcut)
        self.actionOpen.setText(QCoreApplication.translate("GHEtool", "Open", None))
        # if QT_CONFIG(shortcut)
        self.actionOpen.setShortcut(QCoreApplication.translate("GHEtool", "Ctrl+O", None))
        # endif // QT_CONFIG(shortcut)
        self.action_start_multiple.setText(QCoreApplication.translate("GHEtool", "Calculate all scenarios", None))
        # if QT_CONFIG(shortcut)
        self.action_start_multiple.setShortcut(QCoreApplication.translate("GHEtool", "Ctrl+R", None))
        # endif // QT_CONFIG(shortcut)
        self.actionGerman.setText(QCoreApplication.translate("GHEtool", "German", None))
        # if QT_CONFIG(shortcut)
        self.actionGerman.setShortcut(QCoreApplication.translate("GHEtool", "Ctrl+Alt+G", None))
        # endif // QT_CONFIG(shortcut)
        self.actionEnglish.setText(QCoreApplication.translate("GHEtool", "English", None))
        # if QT_CONFIG(shortcut)
        self.actionEnglish.setShortcut(QCoreApplication.translate("GHEtool", "Ctrl+Alt+\u20ac", None))
        # endif // QT_CONFIG(shortcut)
        self.actionUpdate_Scenario.setText(QCoreApplication.translate("GHEtool", "Update scenario", None))
        # if QT_CONFIG(shortcut)
        self.actionUpdate_Scenario.setShortcut(QCoreApplication.translate("GHEtool", "Ctrl+Shift+S", None))
        # endif // QT_CONFIG(shortcut)
        self.actionAdd_Scenario.setText(QCoreApplication.translate("GHEtool", "Add scenario", None))
        # if QT_CONFIG(shortcut)
        self.actionAdd_Scenario.setShortcut(QCoreApplication.translate("GHEtool", "Ctrl+Shift+A", None))
        # endif // QT_CONFIG(shortcut)
        self.actionDelete_scenario.setText(QCoreApplication.translate("GHEtool", "Delete scenario", None))
        # if QT_CONFIG(shortcut)
        self.actionDelete_scenario.setShortcut(QCoreApplication.translate("GHEtool", "Ctrl+Shift+D", None))
        # endif // QT_CONFIG(shortcut)
        self.actionSave_As.setText(QCoreApplication.translate("GHEtool", "Save As", None))
        # if QT_CONFIG(shortcut)
        self.actionSave_As.setShortcut(QCoreApplication.translate("GHEtool", "F12", None))
        # endif // QT_CONFIG(shortcut)
        self.actionDutch.setText(QCoreApplication.translate("GHEtool", "Dutch", None))
        # if QT_CONFIG(shortcut)
        self.actionDutch.setShortcut(QCoreApplication.translate("GHEtool", "Ctrl+Alt+D", None))
        # endif // QT_CONFIG(shortcut)
        self.actionItalian.setText(QCoreApplication.translate("GHEtool", "Italian", None))
        # if QT_CONFIG(shortcut)
        self.actionItalian.setShortcut(QCoreApplication.translate("GHEtool", "Ctrl+Alt+I", None))
        # endif // QT_CONFIG(shortcut)
        self.actionFrench.setText(QCoreApplication.translate("GHEtool", "French", None))
        # if QT_CONFIG(shortcut)
        self.actionFrench.setShortcut(QCoreApplication.translate("GHEtool", "Ctrl+Alt+F", None))
        # endif // QT_CONFIG(shortcut)
        self.actionRename_scenario.setText(QCoreApplication.translate("GHEtool", "Rename scenario", None))
        # if QT_CONFIG(shortcut)
        self.actionRename_scenario.setShortcut(QCoreApplication.translate("GHEtool", "Ctrl+Shift+R", None))
        # endif // QT_CONFIG(shortcut)
        self.action_start_single.setText(QCoreApplication.translate("GHEtool", "Calculate current scenario", None))
        # if QT_CONFIG(shortcut)
        self.action_start_single.setShortcut(QCoreApplication.translate("GHEtool", "Ctrl+Shift+R", None))
        # endif // QT_CONFIG(shortcut)
        self.actionSpanish.setText(QCoreApplication.translate("GHEtool", "Spanish", None))
        # if QT_CONFIG(shortcut)
        self.actionSpanish.setShortcut(QCoreApplication.translate("GHEtool", "Ctrl+Alt+S", None))
        # endif // QT_CONFIG(shortcut)
        self.actionInputChanged.setText(QCoreApplication.translate("GHEtool", "InputChanged", None))
        self.actionCheckUDistance.setText(QCoreApplication.translate("GHEtool", "CheckUDistance", None))
        self.actionUpdateBoreholeGraph.setText(QCoreApplication.translate("GHEtool", "UpdateBoreholeGraph", None))
        self.actionGalician.setText(QCoreApplication.translate("GHEtool", "Galician", None))
        # if QT_CONFIG(shortcut)
        self.actionGalician.setShortcut(QCoreApplication.translate("GHEtool", "Ctrl+Alt+A", None))
        # endif // QT_CONFIG(shortcut)
        self.pushButton_SaveScenario.setText(QCoreApplication.translate("GHEtool", "Update scenario", None))
        self.pushButton_AddScenario.setText(QCoreApplication.translate("GHEtool", "Add scenario", None))
        self.pushButton_DeleteScenario.setText(QCoreApplication.translate("GHEtool", "Delete scenario", None))
        self.button_rename_scenario.setText(QCoreApplication.translate("GHEtool", "Rename scenario", None))

        __sortingEnabled = self.list_widget_scenario.isSortingEnabled()
        self.list_widget_scenario.setSortingEnabled(False)
        ___qlistwidgetitem = self.list_widget_scenario.item(0)
        ___qlistwidgetitem.setText(QCoreApplication.translate("GHEtool", "Scenario: 1", None))
        self.list_widget_scenario.setSortingEnabled(__sortingEnabled)
        self.label_Status.setText(QCoreApplication.translate("GHEtool", "Progress: ", None))
        self.pushButton_start_single.setText(QCoreApplication.translate("GHEtool", "Calculate current scenario", None))
        self.pushButton_start_multiple.setText(QCoreApplication.translate("GHEtool", "Calculate all scenarios", None))
        self.pushButton_Cancel.setText(QCoreApplication.translate("GHEtool", "Exit", None))
        self.menuFile.setTitle(QCoreApplication.translate("GHEtool", "File", None))
        self.menuCalculation.setTitle(QCoreApplication.translate("GHEtool", "Calculation", None))
        self.menuSettings.setTitle(QCoreApplication.translate("GHEtool", "Settings", None))
        self.menuLanguage.setTitle(QCoreApplication.translate("GHEtool", "Language", None))
        self.menuScenario.setTitle(QCoreApplication.translate("GHEtool", "Scenario", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("GHEtool", "toolBar", None))

