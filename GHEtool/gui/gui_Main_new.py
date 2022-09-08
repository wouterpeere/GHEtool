# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'gui_Main.ui'
##
## Created by: Qt User Interface Compiler version 6.3.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QApplication, QCheckBox,
    QComboBox, QDoubleSpinBox, QFrame, QGraphicsView,
    QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QMainWindow, QMenu,
    QMenuBar, QProgressBar, QPushButton, QScrollArea,
    QSizePolicy, QSpacerItem, QSpinBox, QStackedWidget,
    QStatusBar, QToolBar, QToolBox, QVBoxLayout,
    QWidget)

import icons_rc

WHITE: str = "rgb(255, 255, 255)"
LIGHT: str = "rgb(84, 188, 235)"
LIGHT_SELECT: str = "rgb(42, 126, 179)"
DARK: str = "rgb(0, 64, 122)"
GREY: str = "rgb(100, 100, 100)"

class Ui_GHEtool(object):
    def setupUi(self, GHETool):
        if not GHETool.objectName():
            GHETool.setObjectName(u"GHEtool")
        GHETool.resize(1226, 869)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(GHETool.sizePolicy().hasHeightForWidth())
        GHETool.setSizePolicy(sizePolicy)
        GHETool.setMaximumSize(QSize(16777215, 16777215))
        font = QFont()
        font.setFamilies([u"Lexend"])
        font.setPointSize(11)
        font.setBold(False)
        font.setItalic(False)
        GHETool.setFont(font)
        icon = QIcon()
        icon.addFile(u":/icons/icons/icon_05.svg", QSize(), QIcon.Normal, QIcon.Off)
        GHETool.setWindowIcon(icon)
        GHETool.setStyleSheet("*{\n"
                              f"color: {WHITE};\n"
"font: 11pt \"Lexend\";\n"
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
"font: 11pt \"Lexend Deca Light\";}\n"
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
                              "}")
        self.actionNew = QAction(GHETool)
        self.actionNew.setObjectName(u"actionNew")
        self.actionNew.setCheckable(False)
        self.actionNew.setChecked(False)
        self.actionNew.setEnabled(True)
        icon1 = QIcon()
        icon1.addFile(u":/icons/icons/New.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon1.addFile(u":/icons/icons/New_Inv.svg", QSize(), QIcon.Active, QIcon.Off)
        self.actionNew.setIcon(icon1)
        font1 = QFont()
        font1.setFamilies([u"Arial"])
        font1.setPointSize(12)
        self.actionNew.setFont(font1)
        self.actionSave = QAction(GHETool)
        self.actionSave.setObjectName(u"actionSave")
        self.actionSave.setEnabled(True)
        icon2 = QIcon()
        icon2.addFile(u":/icons/icons/Save.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon2.addFile(u":/icons/icons/Save_Inv.svg", QSize(), QIcon.Active, QIcon.Off)
        self.actionSave.setIcon(icon2)
        self.actionSave.setFont(font1)
        self.actionOpen = QAction(GHETool)
        self.actionOpen.setObjectName(u"actionOpen")
        self.actionOpen.setEnabled(True)
        icon3 = QIcon()
        icon3.addFile(u":/icons/icons/Open.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon3.addFile(u":/icons/icons/Open_Inv.svg", QSize(), QIcon.Active, QIcon.Off)
        self.actionOpen.setIcon(icon3)
        self.actionOpen.setFont(font1)
        self.action_start_multiple = QAction(GHETool)
        self.action_start_multiple.setObjectName(u"action_start_multiple")
        self.action_start_multiple.setEnabled(True)
        icon4 = QIcon()
        icon4.addFile(u":/icons/icons/Start_multiple_inv.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon4.addFile(u":/icons/icons/Start_multiple.svg", QSize(), QIcon.Active, QIcon.Off)
        self.action_start_multiple.setIcon(icon4)
        self.actionGerman = QAction(GHETool)
        self.actionGerman.setObjectName(u"actionGerman")
        icon5 = QIcon()
        icon5.addFile(u":/icons/icons/Flag_German.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionGerman.setIcon(icon5)
        self.actionEnglish = QAction(GHETool)
        self.actionEnglish.setObjectName(u"actionEnglish")
        icon6 = QIcon()
        icon6.addFile(u":/icons/icons/Flag_English.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionEnglish.setIcon(icon6)
        self.actionUpdate_Scenario = QAction(GHETool)
        self.actionUpdate_Scenario.setObjectName(u"actionUpdate_Scenario")
        icon7 = QIcon()
        icon7.addFile(u":/icons/icons/Update_Inv.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon7.addFile(u":/icons/icons/Update.svg", QSize(), QIcon.Active, QIcon.Off)
        self.actionUpdate_Scenario.setIcon(icon7)
        self.actionAdd_Scenario = QAction(GHETool)
        self.actionAdd_Scenario.setObjectName(u"actionAdd_Scenario")
        icon8 = QIcon()
        icon8.addFile(u":/icons/icons/Add_Inv.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon8.addFile(u":/icons/icons/Add.svg", QSize(), QIcon.Active, QIcon.Off)
        self.actionAdd_Scenario.setIcon(icon8)
        self.actionDelete_scenario = QAction(GHETool)
        self.actionDelete_scenario.setObjectName(u"actionDelete_scenario")
        icon9 = QIcon()
        icon9.addFile(u":/icons/icons/Delete_Inv.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon9.addFile(u":/icons/icons/Delete.svg", QSize(), QIcon.Active, QIcon.Off)
        self.actionDelete_scenario.setIcon(icon9)
        self.actionSave_As = QAction(GHETool)
        self.actionSave_As.setObjectName(u"actionSave_As")
        icon10 = QIcon()
        icon10.addFile(u":/icons/icons/SaveAs.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon10.addFile(u":/icons/icons/Save_As_Inv.svg", QSize(), QIcon.Active, QIcon.Off)
        self.actionSave_As.setIcon(icon10)
        self.actionDutch = QAction(GHETool)
        self.actionDutch.setObjectName(u"actionDutch")
        icon11 = QIcon()
        icon11.addFile(u":/icons/icons/Flag_Dutch.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionDutch.setIcon(icon11)
        self.actionItalian = QAction(GHETool)
        self.actionItalian.setObjectName(u"actionItalian")
        icon12 = QIcon()
        icon12.addFile(u":/icons/icons/Flag_Italian.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionItalian.setIcon(icon12)
        self.actionFrench = QAction(GHETool)
        self.actionFrench.setObjectName(u"actionFrench")
        icon13 = QIcon()
        icon13.addFile(u":/icons/icons/Flag_French.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionFrench.setIcon(icon13)
        self.actionRename_scenario = QAction(GHETool)
        self.actionRename_scenario.setObjectName(u"actionRename_scenario")
        icon14 = QIcon()
        icon14.addFile(u":/icons/icons/Rename_Inv.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon14.addFile(u":/icons/icons/Rename.svg", QSize(), QIcon.Active, QIcon.Off)
        self.actionRename_scenario.setIcon(icon14)
        self.action_start_single = QAction(GHETool)
        self.action_start_single.setObjectName(u"action_start_single")
        icon15 = QIcon()
        icon15.addFile(u":/icons/icons/Start_inv.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon15.addFile(u":/icons/icons/Start.svg", QSize(), QIcon.Active, QIcon.Off)
        self.action_start_single.setIcon(icon15)
        self.actionSpanish = QAction(GHETool)
        self.actionSpanish.setObjectName(u"actionSpanish")
        icon16 = QIcon()
        icon16.addFile(u":/icons/icons/Flag_Spain.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionSpanish.setIcon(icon16)
        self.actionInputChanged = QAction(GHETool)
        self.actionInputChanged.setObjectName(u"actionInputChanged")
        self.actionCheckUDistance = QAction(GHETool)
        self.actionCheckUDistance.setObjectName(u"actionCheckUDistance")
        self.actionUpdateBoreholeGraph = QAction(GHETool)
        self.actionUpdateBoreholeGraph.setObjectName(u"actionUpdateBoreholeGraph")
        self.actionGalician = QAction(GHETool)
        self.actionGalician.setObjectName(u"actionGalician")
        icon17 = QIcon()
        icon17.addFile(u":/icons/icons/Flag_Galicia.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionGalician.setIcon(icon17)
        self.centralwidget = QWidget(GHETool)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setStyleSheet(u"")
        self.horizontalLayout_23 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_23.setObjectName(u"horizontalLayout_23")
        self.verticalLayout_scenario = QVBoxLayout()
        self.verticalLayout_scenario.setObjectName(u"verticalLayout_scenario")
        self.pushButton_SaveScenario = QPushButton(self.centralwidget)
        self.pushButton_SaveScenario.setObjectName(u"pushButton_SaveScenario")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.pushButton_SaveScenario.sizePolicy().hasHeightForWidth())
        self.pushButton_SaveScenario.setSizePolicy(sizePolicy1)
        self.pushButton_SaveScenario.setMinimumSize(QSize(180, 30))
        self.pushButton_SaveScenario.setMaximumSize(QSize(250, 30))
        self.pushButton_SaveScenario.setStyleSheet(u"text-align:left;")
        icon18 = QIcon()
        icon18.addFile(u":/icons/icons/Update.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_SaveScenario.setIcon(icon18)
        self.pushButton_SaveScenario.setIconSize(QSize(20, 20))

        self.verticalLayout_scenario.addWidget(self.pushButton_SaveScenario)

        self.pushButton_AddScenario = QPushButton(self.centralwidget)
        self.pushButton_AddScenario.setObjectName(u"pushButton_AddScenario")
        self.pushButton_AddScenario.setMinimumSize(QSize(180, 30))
        self.pushButton_AddScenario.setMaximumSize(QSize(250, 30))
        self.pushButton_AddScenario.setStyleSheet(u"text-align:left;")
        icon19 = QIcon()
        icon19.addFile(u":/icons/icons/Add.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_AddScenario.setIcon(icon19)
        self.pushButton_AddScenario.setIconSize(QSize(20, 20))

        self.verticalLayout_scenario.addWidget(self.pushButton_AddScenario)

        self.pushButton_DeleteScenario = QPushButton(self.centralwidget)
        self.pushButton_DeleteScenario.setObjectName(u"pushButton_DeleteScenario")
        self.pushButton_DeleteScenario.setMinimumSize(QSize(180, 30))
        self.pushButton_DeleteScenario.setMaximumSize(QSize(250, 30))
        self.pushButton_DeleteScenario.setStyleSheet(u"text-align:left;")
        icon20 = QIcon()
        icon20.addFile(u":/icons/icons/Delete.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_DeleteScenario.setIcon(icon20)
        self.pushButton_DeleteScenario.setIconSize(QSize(20, 20))

        self.verticalLayout_scenario.addWidget(self.pushButton_DeleteScenario)

        self.button_rename_scenario = QPushButton(self.centralwidget)
        self.button_rename_scenario.setObjectName(u"button_rename_scenario")
        self.button_rename_scenario.setMinimumSize(QSize(180, 30))
        self.button_rename_scenario.setMaximumSize(QSize(250, 30))
        self.button_rename_scenario.setStyleSheet(u"text-align:left;")
        icon21 = QIcon()
        icon21.addFile(u":/icons/icons/Rename.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.button_rename_scenario.setIcon(icon21)
        self.button_rename_scenario.setIconSize(QSize(20, 20))

        self.verticalLayout_scenario.addWidget(self.button_rename_scenario)

        self.list_widget_scenario = QListWidget(self.centralwidget)
        QListWidgetItem(self.list_widget_scenario)
        self.list_widget_scenario.setObjectName(u"list_widget_scenario")
        sizePolicy.setHeightForWidth(self.list_widget_scenario.sizePolicy().hasHeightForWidth())
        self.list_widget_scenario.setSizePolicy(sizePolicy)
        self.list_widget_scenario.setMaximumSize(QSize(16666711, 16666711))
        self.list_widget_scenario.setStyleSheet(u"*{border: 1px solid white;}\n"
"QListWidget{outline: 0;}\n"
"QListWidget::item:selected{\n"
                                                f"background:{LIGHT};color: {WHITE};border: 0px solid white;\n"
                                                "}\n"
"QListWidget::item:hover{border: 1px solid white;color: rgb(255, 255, 255);}")
        self.list_widget_scenario.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.list_widget_scenario.setAutoScrollMargin(10)
        self.list_widget_scenario.setEditTriggers(QAbstractItemView.DoubleClicked|QAbstractItemView.EditKeyPressed|QAbstractItemView.SelectedClicked)
        self.list_widget_scenario.setDragDropMode(QAbstractItemView.DragDrop)
        self.list_widget_scenario.setDefaultDropAction(Qt.TargetMoveAction)
        self.list_widget_scenario.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.list_widget_scenario.setSelectionRectVisible(False)

        self.verticalLayout_scenario.addWidget(self.list_widget_scenario)


        self.horizontalLayout_23.addLayout(self.verticalLayout_scenario)

        self.verticalLayout_menu = QVBoxLayout()
        self.verticalLayout_menu.setSpacing(0)
        self.verticalLayout_menu.setObjectName(u"verticalLayout_menu")

        self.label_Gap_Aim = QLabel(self.centralwidget)
        self.label_Gap_Aim.setObjectName(u"label_Gap_Aim")
        self.label_Gap_Aim.setMinimumSize(QSize(0, 6))
        self.label_Gap_Aim.setMaximumSize(QSize(16777215, 6))

        self.verticalLayout_menu.addWidget(self.label_Gap_Aim)

        self.pushButton_General = QPushButton(self.centralwidget)
        self.pushButton_General.setObjectName(u"pushButton_General")
        self.pushButton_General.setMinimumSize(QSize(100, 100))
        self.pushButton_General.setStyleSheet(u"")
        icon23 = QIcon()
        icon23.addFile(u":/icons/icons/Borehole.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_General.setIcon(icon23)
        self.pushButton_General.setIconSize(QSize(24, 24))

        self.verticalLayout_menu.addWidget(self.pushButton_General)

        self.label_GapBR_Res = QLabel(self.centralwidget)
        self.label_GapBR_Res.setObjectName(u"label_GapBR_Res")
        self.label_GapBR_Res.setMinimumSize(QSize(0, 6))
        self.label_GapBR_Res.setMaximumSize(QSize(16777215, 6))

        self.verticalLayout_menu.addWidget(self.label_GapBR_Res)

        self.pushButton_borehole_resistance = QPushButton(self.centralwidget)
        self.pushButton_borehole_resistance.setObjectName(u"pushButton_borehole_resistance")
        self.pushButton_borehole_resistance.setMinimumSize(QSize(100, 100))
        self.pushButton_borehole_resistance.setStyleSheet(u"")
        icon24 = QIcon()
        icon24.addFile(u":/icons/icons/Resistance.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_borehole_resistance.setIcon(icon24)
        self.pushButton_borehole_resistance.setIconSize(QSize(24, 24))

        self.verticalLayout_menu.addWidget(self.pushButton_borehole_resistance)

        self.label_GapGenTh = QLabel(self.centralwidget)
        self.label_GapGenTh.setObjectName(u"label_GapGenTh")
        self.label_GapGenTh.setMinimumSize(QSize(0, 6))
        self.label_GapGenTh.setMaximumSize(QSize(16777215, 6))

        self.verticalLayout_menu.addWidget(self.label_GapGenTh)

        self.pushButton_thermalDemands = QPushButton(self.centralwidget)
        self.pushButton_thermalDemands.setObjectName(u"pushButton_thermalDemands")
        self.pushButton_thermalDemands.setMinimumSize(QSize(100, 100))
        self.pushButton_thermalDemands.setStyleSheet(u"")
        icon25 = QIcon()
        icon25.addFile(u":/icons/icons/Thermal.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_thermalDemands.setIcon(icon25)
        self.pushButton_thermalDemands.setIconSize(QSize(24, 24))

        self.verticalLayout_menu.addWidget(self.pushButton_thermalDemands)

        self.label_GapThRes = QLabel(self.centralwidget)
        self.label_GapThRes.setObjectName(u"label_GapThRes")
        self.label_GapThRes.setMinimumSize(QSize(0, 6))
        self.label_GapThRes.setMaximumSize(QSize(16777215, 6))

        self.verticalLayout_menu.addWidget(self.label_GapThRes)

        self.pushButton_Results = QPushButton(self.centralwidget)
        self.pushButton_Results.setObjectName(u"pushButton_Results")
        self.pushButton_Results.setMinimumSize(QSize(100, 100))
        self.pushButton_Results.setStyleSheet(u"")
        icon26 = QIcon()
        icon26.addFile(u":/icons/icons/Result.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_Results.setIcon(icon26)
        self.pushButton_Results.setIconSize(QSize(24, 24))

        self.verticalLayout_menu.addWidget(self.pushButton_Results)

        self.label_GapResSet = QLabel(self.centralwidget)
        self.label_GapResSet.setObjectName(u"label_GapResSet")
        self.label_GapResSet.setMinimumSize(QSize(0, 6))
        self.label_GapResSet.setMaximumSize(QSize(16777215, 6))

        self.verticalLayout_menu.addWidget(self.label_GapResSet)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_menu.addItem(self.verticalSpacer)


        self.horizontalLayout_23.addLayout(self.verticalLayout_menu)

        self.verticalLayout_21 = QVBoxLayout()
        self.verticalLayout_21.setObjectName(u"verticalLayout_21")
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setStyleSheet(u"")
        self.stackedWidget.setFrameShadow(QFrame.Plain)
        self.stackedWidget.setLineWidth(0)
        self.page_aim = QWidget()
        self.page_aim.setObjectName(u"page_aim")
        self.verticalLayout_22 = QVBoxLayout(self.page_aim)
        self.verticalLayout_22.setObjectName(u"verticalLayout_22")
        self.label = QLabel(self.page_aim)
        self.label.setObjectName(u"label")
        self.label.setStyleSheet(u"font: 63 16pt \"Lexend SemiBold\";")

        self.verticalLayout_22.addWidget(self.label)

        self.scrollArea_3 = QScrollArea(self.page_aim)
        self.scrollArea_3.setObjectName(u"scrollArea_3")
        self.scrollArea_3.setFrameShape(QFrame.NoFrame)
        self.scrollArea_3.setLineWidth(0)
        self.scrollArea_3.setWidgetResizable(True)
        self.scrollAreaWidgetContents_6 = QWidget()
        self.scrollAreaWidgetContents_6.setObjectName(u"scrollAreaWidgetContents_6")
        self.scrollAreaWidgetContents_6.setGeometry(QRect(0, 0, 881, 606))
        self.verticalLayout_24 = QVBoxLayout(self.scrollAreaWidgetContents_6)
        self.verticalLayout_24.setSpacing(0)
        self.verticalLayout_24.setObjectName(u"verticalLayout_24")
        self.frame_aims = QFrame(self.scrollAreaWidgetContents_6)
        self.frame_aims.setObjectName(u"frame_aims")
        self.frame_aims.setStyleSheet(u"QFrame {\n"
"	border: 1px solid #54bceb;\n"
"	border-top-left-radius: 15px;\n"
"	border-top-right-radius: 15px;\n"
"	border-bottom-left-radius: 15px;\n"
"	border-bottom-right-radius: 15px;\n"
"}\n"
"QLabel{border: 0px solid rgb(255,255,255);}")
        self.frame_aims.setFrameShape(QFrame.StyledPanel)
        self.frame_aims.setFrameShadow(QFrame.Raised)
        self.gridLayout_14 = QGridLayout(self.frame_aims)
        self.gridLayout_14.setObjectName(u"gridLayout_14")
        self.gridLayout_14.setVerticalSpacing(6)

        self.verticalLayout_24.addWidget(self.frame_aims)

        self.label_4 = QLabel(self.scrollAreaWidgetContents_6)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setMinimumSize(QSize(0, 6))
        self.label_4.setMaximumSize(QSize(16777215, 6))

        self.verticalLayout_24.addWidget(self.label_4)

        self.label_Earth_Properties_7 = QLabel(self.scrollAreaWidgetContents_6)
        self.label_Earth_Properties_7.setObjectName(u"label_Earth_Properties_7")
        self.label_Earth_Properties_7.setStyleSheet(u"QLabel {\n"
"        qproperty-alignment: AlignCenter;\n"
f"	border: 1px solid  {LIGHT};\n"
"	border-top-left-radius: 15px;\n"
"	border-top-right-radius: 15px;\n"
f"	background-color:  {LIGHT};\n"
"	padding: 5px 0px;\n"
"	color:  rgb(255, 255, 235);\n"
"font-weight:500;\n"
"}")

        self.verticalLayout_24.addWidget(self.label_Earth_Properties_7)

        self.frame_7 = QFrame(self.scrollAreaWidgetContents_6)
        self.frame_7.setObjectName(u"frame_7")
        self.frame_7.setStyleSheet(u"QFrame {\n"
"	border: 1px solid #54bceb;\n"
"	border-bottom-left-radius: 15px;\n"
"	border-bottom-right-radius: 15px;\n"
"}\n"
"QLabel{border: 0px solid rgb(255,255,255);}")
        self.frame_7.setFrameShape(QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QFrame.Raised)
        self.gridLayout_13 = QGridLayout(self.frame_7)
        self.gridLayout_13.setObjectName(u"gridLayout_13")
        self.gridLayout_13.setVerticalSpacing(0)
        self.pushButton_hourly_data = QPushButton(self.frame_7)
        self.pushButton_hourly_data.setObjectName(u"pushButton_hourly_data")
        self.pushButton_hourly_data.setStyleSheet(u"QPushButton{\n"
                                                  f"border: 3px solid {LIGHT};\n"
"border-radius: 5px;\n"
f"color: {WHITE};\n"
f"gridline-color: {LIGHT};\n"
"background-color: rgb(0, 64, 122);\n"
"font-weight:500;}\n"
"QPushButton:hover{\n"
"border: 3px solid  rgb(0, 64, 122);\n"
f"background-color:{LIGHT};\n"
                                                  "}\n"
"QPushButton:checked{\n"
                                                  f"background-color:{LIGHT};"
                                                  "}\n"
"QPushButton:disabled{border: 3px solid rgb(100, 100, 100);\n"
"border-radius: 5px;\n"
f"color: {WHITE};\n"
f"gridline-color: {GREY};\n"
"background-color: rgb(100, 100, 100);}\n"
"QPushButton:disabled:hover{background-color: rgb(0, 64, 122);}")
        self.pushButton_hourly_data.setCheckable(True)

        self.gridLayout_13.addWidget(self.pushButton_hourly_data, 0, 1, 1, 1)

        self.pushButton_hourly_data2 = QPushButton(self.frame_7)
        self.pushButton_hourly_data2.setObjectName(u"pushButton_hourly_data2")
        self.pushButton_hourly_data2.setStyleSheet(u"QPushButton{border: 3px solid {LIGHT};\n"
                                                  "border-radius: 5px;\n"
                                                  f"color: {WHITE};\n"
                                                  f"gridline-color: {LIGHT};\n"
                                                  "background-color: rgb(0, 64, 122);\n"
                                                  "font-weight:500;}\n"
                                                  "QPushButton:hover{\n"
                                                  "border: 3px solid  rgb(0, 64, 122);\n"
                                                  f"background-color:{LIGHT};\n"
                                                   "}\n"
                                                  "QPushButton:checked{\n"
                                                   f"background-color:{LIGHT};\n"
                                                   "}\n"
                                                  "QPushButton:disabled{border: 3px solid rgb(100, 100, 100);\n"
                                                  "border-radius: 5px;\n"
                                                  f"color: {WHITE};\n"
                                                  f"gridline-color: {GREY};\n"
                                                  "background-color: rgb(100, 100, 100);}\n"
                                                  "QPushButton:disabled:hover{background-color: rgb(0, 64, 122);}")
        self.pushButton_hourly_data2.setCheckable(True)

        self.gridLayout_13.addWidget(self.pushButton_hourly_data2, 0, 2, 1, 1)

        self.label_Gap_Aim_5 = QLabel(self.frame_7)
        self.label_Gap_Aim_5.setObjectName(u"label_Gap_Aim_5")
        self.label_Gap_Aim_5.setMinimumSize(QSize(0, 6))
        self.label_Gap_Aim_5.setMaximumSize(QSize(16777215, 6))

        self.gridLayout_13.addWidget(self.label_Gap_Aim_5, 1, 0, 1, 1)

        self.pushButton_monthly_data = QPushButton(self.frame_7)
        self.pushButton_monthly_data.setObjectName(u"pushButton_monthly_data")
        self.pushButton_monthly_data.setStyleSheet("QPushButton{\n"
                                                   "border: 3px solid {LIGHT};\n"
"border-radius: 5px;\n"
f"color: {WHITE};\n"
f"gridline-color: {LIGHT};\n"
"background-color: rgb(0, 64, 122);\n"
"font-weight:500;}\n"
"QPushButton:hover{\n"
"border: 3px solid  rgb(0, 64, 122);\n"
f"background-color:{LIGHT};\n"
                                                   "}\n"
"QPushButton:checked{\n"
                                                   f"background-color:{LIGHT};\n"
                                                   "}\n"
"QPushButton:disabled{border: 3px solid rgb(100, 100, 100);\n"
"border-radius: 5px;\n"
f"color: {WHITE};\n"
f"gridline-color: {GREY};\n"
"background-color: rgb(100, 100, 100);}\n"
"QPushButton:disabled:hover{background-color: rgb(0, 64, 122);}")
        self.pushButton_monthly_data.setCheckable(True)
        self.pushButton_monthly_data.setChecked(True)

        self.gridLayout_13.addWidget(self.pushButton_monthly_data, 0, 0, 1, 1)


        self.verticalLayout_24.addWidget(self.frame_7)

        self.label_3 = QLabel(self.scrollAreaWidgetContents_6)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMinimumSize(QSize(0, 6))
        self.label_3.setMaximumSize(QSize(16777215, 6))

        self.verticalLayout_24.addWidget(self.label_3)

        self.label_Options = QLabel(self.scrollAreaWidgetContents_6)
        self.label_Options.setObjectName(u"label_Options")
        self.label_Options.setStyleSheet(u"QLabel {\n"
"        qproperty-alignment: AlignCenter;\n"
"	border: 1px solid  rgb(84, 188, 235);\n"
"	border-top-left-radius: 15px;\n"
"	border-top-right-radius: 15px;\n"
"	background-color:  rgb(84, 188, 235);\n"
"	padding: 5px 0px;\n"
"	color:  rgb(255, 255, 235);\n"
"font-weight:500;\n"
"}")

        self.verticalLayout_24.addWidget(self.label_Options)

        self.frame_Options = QFrame(self.scrollAreaWidgetContents_6)
        self.frame_Options.setObjectName(u"frame_Options")
        self.frame_Options.setStyleSheet(u"QFrame {\n"
"	border: 1px solid #54bceb;\n"
"	border-bottom-left-radius: 15px;\n"
"	border-bottom-right-radius: 15px;\n"
"}\n"
"QLabel{border: 0px solid rgb(255,255,255);}")
        self.frame_Options.setFrameShape(QFrame.StyledPanel)
        self.frame_Options.setFrameShadow(QFrame.Raised)
        self.verticalLayout_23 = QVBoxLayout(self.frame_Options)
        self.verticalLayout_23.setSpacing(0)
        self.verticalLayout_23.setObjectName(u"verticalLayout_23")
        self.label_calc_method_depth_sizing = QLabel(self.frame_Options)
        self.label_calc_method_depth_sizing.setObjectName(u"label_calc_method_depth_sizing")
        self.label_calc_method_depth_sizing.setStyleSheet(u"QLabel {\n"
"        qproperty-alignment: AlignCenter;\n"
"	border: 1px solid  rgb(84, 188, 235);\n"
"	border-top-left-radius: 15px;\n"
"	border-top-right-radius: 15px;\n"
"	border-bottom-left-radius: 0px;\n"
"	border-bottom-right-radius: 0px;\n"
"	border-bottom: 0px solid  rgb(84, 188, 235);\n"
"	background-color:  rgb(0, 64, 122);\n"
"	padding: 5px 0px;\n"
"	color:  rgb(255, 255, 235);\n"
"font-weight:500;\n"
"}")

        self.verticalLayout_23.addWidget(self.label_calc_method_depth_sizing)

        self.frame_calc_method_depth_sizing = QFrame(self.frame_Options)
        self.frame_calc_method_depth_sizing.setObjectName(u"frame_calc_method_depth_sizing")
        self.frame_calc_method_depth_sizing.setStyleSheet(u"QFrame {\n"
"	border: 1px solid #54bceb;\n"
"	border-top: 0px solid #54bceb;\n"
"	border-bottom-left-radius: 15px;\n"
"	border-bottom-right-radius: 15px;\n"
"}\n"
"QLabel{border: 0px solid rgb(255,255,255);}")
        self.frame_calc_method_depth_sizing.setFrameShape(QFrame.StyledPanel)
        self.frame_calc_method_depth_sizing.setFrameShadow(QFrame.Raised)
        self.gridLayout_11 = QGridLayout(self.frame_calc_method_depth_sizing)
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.pushButton_9 = QPushButton(self.frame_calc_method_depth_sizing)
        self.pushButton_9.setObjectName(u"pushButton_9")
        self.pushButton_9.setStyleSheet(u"QPushButton{border: 3px solid rgb(84, 188, 235);\n"
"border-radius: 5px;\n"
f"color: {WHITE};\n"
"gridline-color: rgb(84, 188, 235);\n"
"background-color: rgb(0, 64, 122);\n"
"font-weight:500;}\n"
"QPushButton:hover{\n"
"border: 3px solid  rgb(0, 64, 122);\n"
"background-color:rgb(84, 188, 235);}\n"
"QPushButton:checked{background-color:rgb(84, 188, 235);}\n"
"QPushButton:disabled{border: 3px solid rgb(100, 100, 100);\n"
"border-radius: 5px;\n"
f"color: {WHITE};\n"
f"gridline-color: {GREY};\n"
"background-color: rgb(100, 100, 100);}\n"
"QPushButton:disabled:hover{background-color: rgb(0, 64, 122);}")
        self.pushButton_9.setCheckable(True)

        self.gridLayout_11.addWidget(self.pushButton_9, 0, 0, 1, 1)

        self.pushButton_11 = QPushButton(self.frame_calc_method_depth_sizing)
        self.pushButton_11.setObjectName(u"pushButton_11")
        self.pushButton_11.setStyleSheet(u"QPushButton{border: 3px solid rgb(84, 188, 235);\n"
"border-radius: 5px;\n"
f"color: {WHITE};\n"
"gridline-color: rgb(84, 188, 235);\n"
"background-color: rgb(0, 64, 122);\n"
"font-weight:500;}\n"
"QPushButton:hover{\n"
"border: 3px solid  rgb(0, 64, 122);\n"
"background-color:rgb(84, 188, 235);}\n"
"QPushButton:checked{background-color:rgb(84, 188, 235);}\n"
"QPushButton:disabled{border: 3px solid rgb(100, 100, 100);\n"
"border-radius: 5px;\n"
f"color: {WHITE};\n"
f"gridline-color: {GREY};\n"
"background-color: rgb(100, 100, 100);}\n"
"QPushButton:disabled:hover{background-color: rgb(0, 64, 122);}")
        self.pushButton_11.setCheckable(True)

        self.gridLayout_11.addWidget(self.pushButton_11, 0, 1, 1, 1)


        self.verticalLayout_23.addWidget(self.frame_calc_method_depth_sizing)

        self.label_Gap_Aim_2 = QLabel(self.frame_Options)
        self.label_Gap_Aim_2.setObjectName(u"label_Gap_Aim_2")
        self.label_Gap_Aim_2.setMinimumSize(QSize(0, 6))
        self.label_Gap_Aim_2.setMaximumSize(QSize(16777215, 6))

        self.verticalLayout_23.addWidget(self.label_Gap_Aim_2)

        self.label_calc_method_length_sizing = QLabel(self.frame_Options)
        self.label_calc_method_length_sizing.setObjectName(u"label_calc_method_length_sizing")
        self.label_calc_method_length_sizing.setStyleSheet(u"QLabel {\n"
"        qproperty-alignment: AlignCenter;\n"
"	border: 1px solid  rgb(84, 188, 235);\n"
"	border-top-left-radius: 15px;\n"
"	border-top-right-radius: 15px;\n"
"	border-bottom-left-radius: 0px;\n"
"	border-bottom-right-radius: 0px;\n"
"	border-bottom: 0px solid  rgb(84, 188, 235);\n"
"	background-color:  rgb(0, 64, 122);\n"
"	padding: 5px 0px;\n"
"	color:  rgb(255, 255, 235);\n"
"font-weight:500;\n"
"}")

        self.verticalLayout_23.addWidget(self.label_calc_method_length_sizing)

        self.frame_calc_method_length_sizing = QFrame(self.frame_Options)
        self.frame_calc_method_length_sizing.setObjectName(u"frame_calc_method_length_sizing")
        self.frame_calc_method_length_sizing.setStyleSheet(u"QFrame {\n"
"	border: 1px solid #54bceb;\n"
"	border-top: 0px solid #54bceb;\n"
"	border-bottom-left-radius: 15px;\n"
"	border-bottom-right-radius: 15px;\n"
"}\n"
"QLabel{border: 0px solid rgb(255,255,255);}")
        self.frame_calc_method_length_sizing.setFrameShape(QFrame.StyledPanel)
        self.frame_calc_method_length_sizing.setFrameShadow(QFrame.Raised)
        self.gridLayout_12 = QGridLayout(self.frame_calc_method_length_sizing)
        self.gridLayout_12.setObjectName(u"gridLayout_12")
        self.pushButton_10 = QPushButton(self.frame_calc_method_length_sizing)
        self.pushButton_10.setObjectName(u"pushButton_10")
        self.pushButton_10.setStyleSheet(u"QPushButton{border: 3px solid rgb(84, 188, 235);\n"
"border-radius: 5px;\n"
f"color: {WHITE};\n"
"gridline-color: rgb(84, 188, 235);\n"
"background-color: rgb(0, 64, 122);\n"
"font-weight:500;}\n"
"QPushButton:hover{\n"
"border: 3px solid  rgb(0, 64, 122);\n"
"background-color:rgb(84, 188, 235);}\n"
"QPushButton:checked{background-color:rgb(84, 188, 235);}\n"
"QPushButton:disabled{border: 3px solid rgb(100, 100, 100);\n"
"border-radius: 5px;\n"
f"color: {WHITE};\n"
f"gridline-color: {GREY};\n"
"background-color: rgb(100, 100, 100);}\n"
"QPushButton:disabled:hover{background-color: rgb(0, 64, 122);}")
        self.pushButton_10.setCheckable(True)

        self.gridLayout_12.addWidget(self.pushButton_10, 0, 0, 1, 1)

        self.pushButton_12 = QPushButton(self.frame_calc_method_length_sizing)
        self.pushButton_12.setObjectName(u"pushButton_12")
        self.pushButton_12.setStyleSheet(u"QPushButton{border: 3px solid rgb(84, 188, 235);\n"
"border-radius: 5px;\n"
f"color: {WHITE};\n"
"gridline-color: rgb(84, 188, 235);\n"
"background-color: rgb(0, 64, 122);\n"
"font-weight:500;}\n"
"QPushButton:hover{\n"
"border: 3px solid  rgb(0, 64, 122);\n"
"background-color:rgb(84, 188, 235);}\n"
"QPushButton:checked{background-color:rgb(84, 188, 235);}\n"
"QPushButton:disabled{border: 3px solid rgb(100, 100, 100);\n"
"border-radius: 5px;\n"
f"color: {WHITE};\n"
f"gridline-color: {GREY};\n"
"background-color: rgb(100, 100, 100);}\n"
"QPushButton:disabled:hover{background-color: rgb(0, 64, 122);}")
        self.pushButton_12.setCheckable(True)

        self.gridLayout_12.addWidget(self.pushButton_12, 0, 1, 1, 1)


        self.verticalLayout_23.addWidget(self.frame_calc_method_length_sizing)

        self.label_Gap_Aim_3 = QLabel(self.frame_Options)
        self.label_Gap_Aim_3.setObjectName(u"label_Gap_Aim_3")
        self.label_Gap_Aim_3.setMinimumSize(QSize(0, 6))
        self.label_Gap_Aim_3.setMaximumSize(QSize(16777215, 6))

        self.verticalLayout_23.addWidget(self.label_Gap_Aim_3)

        self.frame_calc_method_length_sizing_2 = QFrame(self.frame_Options)
        self.frame_calc_method_length_sizing_2.setObjectName(u"frame_calc_method_length_sizing_2")
        self.frame_calc_method_length_sizing_2.setStyleSheet(u"QFrame {\n"
"	border: 1px solid #54bceb;\n"
"border-top-left-radius: 15px;\n"
"	border-top-right-radius: 15px;\n"
"	border-bottom-left-radius: 15px;\n"
"	border-bottom-right-radius: 15px;\n"
"}\n"
"QLabel{border: 0px solid rgb(255,255,255);}")
        self.frame_calc_method_length_sizing_2.setFrameShape(QFrame.StyledPanel)
        self.frame_calc_method_length_sizing_2.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_calc_method_length_sizing_2)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_calc_method_length_sizing_2 = QLabel(self.frame_calc_method_length_sizing_2)
        self.label_calc_method_length_sizing_2.setObjectName(u"label_calc_method_length_sizing_2")
        self.label_calc_method_length_sizing_2.setMinimumSize(QSize(0, 30))
        self.label_calc_method_length_sizing_2.setStyleSheet(u"")

        self.horizontalLayout_3.addWidget(self.label_calc_method_length_sizing_2)

        self.horizontalSpacer_9 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_9)

        self.pushButton_13 = QPushButton(self.frame_calc_method_length_sizing_2)
        self.pushButton_13.setObjectName(u"pushButton_13")
        self.pushButton_13.setMinimumSize(QSize(100, 30))
        self.pushButton_13.setStyleSheet(u"QPushButton{border: 3px solid rgb(84, 188, 235);\n"
"border-radius: 5px;\n"
f"color: {WHITE};\n"
"gridline-color: rgb(84, 188, 235);\n"
"background-color: rgb(0, 64, 122);\n"
"font-weight:500;}\n"
"QPushButton:hover{\n"
"border: 3px solid  rgb(0, 64, 122);\n"
"background-color:rgb(84, 188, 235);}\n"
"QPushButton:checked{background-color:rgb(84, 188, 235);}\n"
"QPushButton:disabled{border: 3px solid rgb(100, 100, 100);\n"
"border-radius: 5px;\n"
f"color: {WHITE};\n"
f"gridline-color: {GREY};\n"
"background-color: rgb(100, 100, 100);}\n"
"QPushButton:disabled:hover{background-color: rgb(0, 64, 122);}")
        self.pushButton_13.setCheckable(True)

        self.horizontalLayout_3.addWidget(self.pushButton_13)

        self.pushButton_14 = QPushButton(self.frame_calc_method_length_sizing_2)
        self.pushButton_14.setObjectName(u"pushButton_14")
        self.pushButton_14.setMinimumSize(QSize(100, 30))
        self.pushButton_14.setStyleSheet(u"QPushButton{border: 3px solid rgb(84, 188, 235);\n"
"border-radius: 5px;\n"
f"color: {WHITE};\n"
"gridline-color: rgb(84, 188, 235);\n"
"background-color: rgb(0, 64, 122);\n"
"font-weight:500;}\n"
"QPushButton:hover{\n"
"border: 3px solid  rgb(0, 64, 122);\n"
"background-color:rgb(84, 188, 235);}\n"
"QPushButton:checked{background-color:rgb(84, 188, 235);}\n"
"QPushButton:disabled{border: 3px solid rgb(100, 100, 100);\n"
"border-radius: 5px;\n"
f"color: {WHITE};\n"
f"gridline-color: {GREY};\n"
"background-color: rgb(100, 100, 100);}\n"
"QPushButton:disabled:hover{background-color: rgb(0, 64, 122);}")
        self.pushButton_14.setCheckable(True)

        self.horizontalLayout_3.addWidget(self.pushButton_14)


        self.verticalLayout_23.addWidget(self.frame_calc_method_length_sizing_2)


        self.verticalLayout_24.addWidget(self.frame_Options)

        self.label_5 = QLabel(self.scrollAreaWidgetContents_6)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMinimumSize(QSize(0, 6))
        self.label_5.setMaximumSize(QSize(16777215, 6))

        self.verticalLayout_24.addWidget(self.label_5)

        self.verticalSpacer_7 = QSpacerItem(20, 137, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_24.addItem(self.verticalSpacer_7)

        self.horizontalLayout_37 = QHBoxLayout()
        self.horizontalLayout_37.setObjectName(u"horizontalLayout_37")
        self.horizontalSpacer_22 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_37.addItem(self.horizontalSpacer_22)

        self.pushButton_NextAim = QPushButton(self.scrollAreaWidgetContents_6)
        self.pushButton_NextAim.setObjectName(u"pushButton_NextAim")
        self.pushButton_NextAim.setMinimumSize(QSize(0, 30))
        self.pushButton_NextAim.setMaximumSize(QSize(16777215, 30))
        self.pushButton_NextAim.setLayoutDirection(Qt.RightToLeft)
        self.pushButton_NextAim.setStyleSheet(u"")
        icon28 = QIcon()
        icon28.addFile(u":/icons/icons/ArrowRight2.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_NextAim.setIcon(icon28)
        self.pushButton_NextAim.setIconSize(QSize(20, 20))

        self.horizontalLayout_37.addWidget(self.pushButton_NextAim)


        self.verticalLayout_24.addLayout(self.horizontalLayout_37)

        self.scrollArea_3.setWidget(self.scrollAreaWidgetContents_6)

        self.verticalLayout_22.addWidget(self.scrollArea_3)

        self.stackedWidget.addWidget(self.page_aim)
        self.page_General = QWidget()
        self.page_General.setObjectName(u"page_General")
        self.verticalLayout_7 = QVBoxLayout(self.page_General)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.scrollArea_General = QScrollArea(self.page_General)
        self.scrollArea_General.setObjectName(u"scrollArea_General")
        self.scrollArea_General.setFrameShape(QFrame.NoFrame)
        self.scrollArea_General.setLineWidth(0)
        self.scrollArea_General.setWidgetResizable(True)
        self.scrollAreaWidgetContents_3 = QWidget()
        self.scrollAreaWidgetContents_3.setObjectName(u"scrollAreaWidgetContents_3")
        self.scrollAreaWidgetContents_3.setGeometry(QRect(0, 0, 864, 695))
        self.verticalLayout_8 = QVBoxLayout(self.scrollAreaWidgetContents_3)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.label_Borehole_earth = QLabel(self.scrollAreaWidgetContents_3)
        self.label_Borehole_earth.setObjectName(u"label_Borehole_earth")
        self.label_Borehole_earth.setStyleSheet(u"font: 63 16pt \"Lexend SemiBold\";")

        self.verticalLayout_8.addWidget(self.label_Borehole_earth)

        self.label_46 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_46.setObjectName(u"label_46")
        self.label_46.setMinimumSize(QSize(0, 6))
        self.label_46.setMaximumSize(QSize(16777215, 6))

        self.verticalLayout_8.addWidget(self.label_46)

        self.label_Earth_Properties = QLabel(self.scrollAreaWidgetContents_3)
        self.label_Earth_Properties.setObjectName(u"label_Earth_Properties")
        self.label_Earth_Properties.setStyleSheet(u"QLabel {\n"
"        qproperty-alignment: AlignCenter;\n"
"	border: 1px solid  rgb(84, 188, 235);\n"
"	border-top-left-radius: 15px;\n"
"	border-top-right-radius: 15px;\n"
"	background-color:  rgb(84, 188, 235);\n"
"	padding: 5px 0px;\n"
"	color:  rgb(255, 255, 235);\n"
"font-weight:500;\n"
"}")

        self.verticalLayout_8.addWidget(self.label_Earth_Properties)

        self.frame_2 = QFrame(self.scrollAreaWidgetContents_3)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setStyleSheet(u"QFrame {\n"
"	border: 1px solid #54bceb;\n"
"	border-bottom-left-radius: 15px;\n"
"	border-bottom-right-radius: 15px;\n"
"}\n"
"QLabel{border: 0px solid rgb(255,255,255);}")
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.gridLayout_4 = QGridLayout(self.frame_2)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.label_H = QLabel(self.frame_2)
        self.label_H.setObjectName(u"label_H")
        self.label_H.setStyleSheet(u"")

        self.gridLayout_4.addWidget(self.label_H, 0, 0, 1, 1)

        self.doubleSpinBox_H = QDoubleSpinBox(self.frame_2)
        self.doubleSpinBox_H.setObjectName(u"doubleSpinBox_H")
        self.doubleSpinBox_H.setStyleSheet(u"")
        self.doubleSpinBox_H.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_H.setMinimum(15.000000000000000)
        self.doubleSpinBox_H.setMaximum(500.000000000000000)
        self.doubleSpinBox_H.setValue(100.000000000000000)

        self.gridLayout_4.addWidget(self.doubleSpinBox_H, 0, 2, 1, 1)

        self.label_BS = QLabel(self.frame_2)
        self.label_BS.setObjectName(u"label_BS")

        self.gridLayout_4.addWidget(self.label_BS, 1, 0, 1, 1)

        self.doubleSpinBox_B = QDoubleSpinBox(self.frame_2)
        self.doubleSpinBox_B.setObjectName(u"doubleSpinBox_B")
        self.doubleSpinBox_B.setStyleSheet(u"")
        self.doubleSpinBox_B.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_B.setMinimum(1.000000000000000)
        self.doubleSpinBox_B.setMaximum(99.000000000000000)
        self.doubleSpinBox_B.setSingleStep(0.100000000000000)
        self.doubleSpinBox_B.setValue(6.000000000000000)

        self.gridLayout_4.addWidget(self.doubleSpinBox_B, 1, 2, 1, 1)

        self.label_B_max = QLabel(self.frame_2)
        self.label_B_max.setObjectName(u"label_B_max")

        self.gridLayout_4.addWidget(self.label_B_max, 2, 0, 1, 1)

        self.doubleSpinBox_B_max = QDoubleSpinBox(self.frame_2)
        self.doubleSpinBox_B_max.setObjectName(u"doubleSpinBox_B_max")
        self.doubleSpinBox_B_max.setStyleSheet(u"")
        self.doubleSpinBox_B_max.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_B_max.setMinimum(3.000000000000000)
        self.doubleSpinBox_B_max.setMaximum(9.000000000000000)
        self.doubleSpinBox_B_max.setSingleStep(0.100000000000000)
        self.doubleSpinBox_B_max.setValue(9.000000000000000)

        self.gridLayout_4.addWidget(self.doubleSpinBox_B_max, 2, 2, 1, 1)

        self.doubleSpinBox_k_s = QDoubleSpinBox(self.frame_2)
        self.doubleSpinBox_k_s.setObjectName(u"doubleSpinBox_k_s")
        self.doubleSpinBox_k_s.setStyleSheet(u"")
        self.doubleSpinBox_k_s.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_k_s.setDecimals(3)
        self.doubleSpinBox_k_s.setMinimum(0.100000000000000)
        self.doubleSpinBox_k_s.setMaximum(10.000000000000000)
        self.doubleSpinBox_k_s.setSingleStep(0.100000000000000)
        self.doubleSpinBox_k_s.setValue(1.500000000000000)

        self.gridLayout_4.addWidget(self.doubleSpinBox_k_s, 3, 2, 1, 1)

        self.label_lambdaEarth = QLabel(self.frame_2)
        self.label_lambdaEarth.setObjectName(u"label_lambdaEarth")

        self.gridLayout_4.addWidget(self.label_lambdaEarth, 3, 0, 1, 1)

        self.label_GroundTemp = QLabel(self.frame_2)
        self.label_GroundTemp.setObjectName(u"label_GroundTemp")

        self.gridLayout_4.addWidget(self.label_GroundTemp, 4, 0, 1, 1)

        self.doubleSpinBox_Tg = QDoubleSpinBox(self.frame_2)
        self.doubleSpinBox_Tg.setObjectName(u"doubleSpinBox_Tg")
        self.doubleSpinBox_Tg.setStyleSheet(u"")
        self.doubleSpinBox_Tg.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_Tg.setDecimals(2)
        self.doubleSpinBox_Tg.setMinimum(-273.149999999999977)
        self.doubleSpinBox_Tg.setMaximum(100.000000000000000)
        self.doubleSpinBox_Tg.setSingleStep(0.100000000000000)
        self.doubleSpinBox_Tg.setValue(10.000000000000000)

        self.gridLayout_4.addWidget(self.doubleSpinBox_Tg, 4, 2, 1, 1)

        self.label_LengthField = QLabel(self.frame_2)
        self.label_LengthField.setObjectName(u"label_LengthField")

        self.gridLayout_4.addWidget(self.label_LengthField, 7, 0, 1, 1)

        self.spinBox_N_1 = QSpinBox(self.frame_2)
        self.spinBox_N_1.setObjectName(u"spinBox_N_1")
        self.spinBox_N_1.setStyleSheet(u"")
        self.spinBox_N_1.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.spinBox_N_1.setMinimum(1)
        self.spinBox_N_1.setMaximum(40)
        self.spinBox_N_1.setValue(12)

        self.gridLayout_4.addWidget(self.spinBox_N_1, 5, 2, 1, 1)

        self.label_WidthField = QLabel(self.frame_2)
        self.label_WidthField.setObjectName(u"label_WidthField")

        self.gridLayout_4.addWidget(self.label_WidthField, 5, 0, 1, 1)

        self.spinBox_N_2 = QSpinBox(self.frame_2)
        self.spinBox_N_2.setObjectName(u"spinBox_N_2")
        self.spinBox_N_2.setStyleSheet(u"")
        self.spinBox_N_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.spinBox_N_2.setMinimum(1)
        self.spinBox_N_2.setMaximum(40)
        self.spinBox_N_2.setValue(8)

        self.gridLayout_4.addWidget(self.spinBox_N_2, 7, 2, 1, 1)

        self.label_MaxWidthField = QLabel(self.frame_2)
        self.label_MaxWidthField.setObjectName(u"label_MaxWidthField")

        self.gridLayout_4.addWidget(self.label_MaxWidthField, 6, 0, 1, 1)

        self.doubleSpinBox_W_max = QDoubleSpinBox(self.frame_2)
        self.doubleSpinBox_W_max.setObjectName(u"doubleSpinBox_W_max")
        self.doubleSpinBox_W_max.setStyleSheet(u"")
        self.doubleSpinBox_W_max.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_W_max.setMinimum(10.000000000000000)
        self.doubleSpinBox_W_max.setMaximum(500.000000000000000)
        self.doubleSpinBox_W_max.setValue(100.000000000000000)

        self.gridLayout_4.addWidget(self.doubleSpinBox_W_max, 6, 2, 1, 1)

        self.label_MaxLengthField = QLabel(self.frame_2)
        self.label_MaxLengthField.setObjectName(u"label_MaxLengthField")

        self.gridLayout_4.addWidget(self.label_MaxLengthField, 8, 0, 1, 1)

        self.doubleSpinBox_L_max = QDoubleSpinBox(self.frame_2)
        self.doubleSpinBox_L_max.setObjectName(u"doubleSpinBox_L_max")
        self.doubleSpinBox_L_max.setStyleSheet(u"")
        self.doubleSpinBox_L_max.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_L_max.setMinimum(10.000000000000000)
        self.doubleSpinBox_L_max.setMaximum(500.000000000000000)
        self.doubleSpinBox_L_max.setValue(100.000000000000000)

        self.gridLayout_4.addWidget(self.doubleSpinBox_L_max, 8, 2, 1, 1)

        self.label_calc_method_depth = QLabel(self.frame_2)
        self.label_calc_method_depth.setObjectName(u"label_calc_method_depth")

        self.gridLayout_4.addWidget(self.label_calc_method_depth, 9, 0, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer, 3, 1, 1, 1)

        self.label_calc_method_sizing = QLabel(self.frame_2)
        self.label_calc_method_sizing.setObjectName(u"label_calc_method_sizing")

        self.gridLayout_4.addWidget(self.label_calc_method_sizing, 11, 0, 1, 1)

        self.comboBox_Size_Method = QComboBox(self.frame_2)
        self.comboBox_Size_Method.addItem("")
        self.comboBox_Size_Method.addItem("")
        self.comboBox_Size_Method.setObjectName(u"comboBox_Size_Method")
        self.comboBox_Size_Method.setMinimumSize(QSize(100, 0))
        self.comboBox_Size_Method.setStyleSheet(u"QFrame {\n"
"	border: 1px solid rgb(255, 255, 255);\n"
"	border-bottom-left-radius: 0px;\n"
"	border-bottom-right-radius: 0px;\n"
"}")

        self.gridLayout_4.addWidget(self.comboBox_Size_Method, 11, 2, 1, 1)

        self.comboBox_depth_Method = QComboBox(self.frame_2)
        self.comboBox_depth_Method.addItem("")
        self.comboBox_depth_Method.addItem("")
        self.comboBox_depth_Method.setObjectName(u"comboBox_depth_Method")
        self.comboBox_depth_Method.setStyleSheet(u"QFrame {\n"
"	border: 1px solid rgb(255, 255, 255);\n"
"	border-bottom-left-radius: 0px;\n"
"	border-bottom-right-radius: 0px;\n"
"}")

        self.gridLayout_4.addWidget(self.comboBox_depth_Method, 9, 2, 1, 1)


        self.verticalLayout_8.addWidget(self.frame_2)

        self.label_45 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_45.setObjectName(u"label_45")
        self.label_45.setMinimumSize(QSize(0, 6))
        self.label_45.setMaximumSize(QSize(16777215, 6))

        self.verticalLayout_8.addWidget(self.label_45)

        self.label_37 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_37.setObjectName(u"label_37")
        self.label_37.setMinimumSize(QSize(0, 10))
        self.label_37.setMaximumSize(QSize(16777215, 10))

        self.verticalLayout_8.addWidget(self.label_37)

        self.pushButton_simulation_period = QPushButton(self.scrollAreaWidgetContents_3)
        self.pushButton_simulation_period.setObjectName(u"pushButton_simulation_period")
        self.pushButton_simulation_period.setMinimumSize(QSize(0, 30))
        self.pushButton_simulation_period.setMaximumSize(QSize(16777215, 30))
        self.pushButton_simulation_period.setStyleSheet(u"QPushButton{border: 3px solid rgb(84, 188, 235);\n"
"	border-top-right-radius: 10px;\n"
"	border-top-left-radius: 10px;\n"
"	border-bottom-left-radius: 10px;\n"
"	border-bottom-right-radius: 10px;\n"
f"color: {WHITE};\n"
"gridline-color: rgb(84, 188, 235);\n"
"background-color: rgb(0, 64, 122);\n"
"font-weight:500;}\n"
"QPushButton:hover{background-color:rgb(84, 188, 235);}\n"
"QPushButton:checked{background-color:rgb(84, 188, 235);\n"
"	border-top-right-radius: 10px;\n"
"	border-top-left-radius: 10px;\n"
"	border-bottom-left-radius: 0px;\n"
"	border-bottom-right-radius: 0px;}\n"
"QPushButton:disabled{border: 3px solid rgb(100, 100, 100);\n"
f"color: {WHITE};\n"
f"gridline-color: {GREY};\n"
"background-color: rgb(100, 100, 100);}\n"
"QPushButton:disabled:hover{background-color: rgb(0, 64, 122);}")
        self.pushButton_simulation_period.setCheckable(True)

        self.verticalLayout_8.addWidget(self.pushButton_simulation_period)

        self.frame_simulation_period = QFrame(self.scrollAreaWidgetContents_3)
        self.frame_simulation_period.setObjectName(u"frame_simulation_period")
        self.frame_simulation_period.setStyleSheet(u"QFrame {\n"
"	border: 1px solid #54bceb;\n"
"	border-bottom-left-radius: 15px;\n"
"	border-bottom-right-radius: 15px;\n"
"}\n"
"QLabel{border: 0px solid rgb(255,255,255);}")
        self.frame_simulation_period.setFrameShape(QFrame.StyledPanel)
        self.frame_simulation_period.setFrameShadow(QFrame.Raised)
        self.frame_simulation_period.setLineWidth(1)
        self.verticalLayout_5 = QVBoxLayout(self.frame_simulation_period)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.gridLayout_7 = QGridLayout()
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.label_TempMin = QLabel(self.frame_simulation_period)
        self.label_TempMin.setObjectName(u"label_TempMin")

        self.gridLayout_7.addWidget(self.label_TempMin, 0, 0, 1, 1)

        self.label_TempMax = QLabel(self.frame_simulation_period)
        self.label_TempMax.setObjectName(u"label_TempMax")

        self.gridLayout_7.addWidget(self.label_TempMax, 1, 0, 1, 1)

        self.doubleSpinBox_TMax = QDoubleSpinBox(self.frame_simulation_period)
        self.doubleSpinBox_TMax.setObjectName(u"doubleSpinBox_TMax")
        self.doubleSpinBox_TMax.setMinimumSize(QSize(100, 0))
        self.doubleSpinBox_TMax.setMaximumSize(QSize(100, 16777215))
        self.doubleSpinBox_TMax.setStyleSheet(u"")
        self.doubleSpinBox_TMax.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_TMax.setMinimum(-273.000000000000000)
        self.doubleSpinBox_TMax.setMaximum(1000.000000000000000)
        self.doubleSpinBox_TMax.setSingleStep(0.100000000000000)
        self.doubleSpinBox_TMax.setValue(16.000000000000000)

        self.gridLayout_7.addWidget(self.doubleSpinBox_TMax, 1, 2, 1, 1)

        self.label_SimulationTime = QLabel(self.frame_simulation_period)
        self.label_SimulationTime.setObjectName(u"label_SimulationTime")

        self.gridLayout_7.addWidget(self.label_SimulationTime, 2, 0, 1, 1)

        self.doubleSpinBox_TMin = QDoubleSpinBox(self.frame_simulation_period)
        self.doubleSpinBox_TMin.setObjectName(u"doubleSpinBox_TMin")
        self.doubleSpinBox_TMin.setMinimumSize(QSize(100, 0))
        self.doubleSpinBox_TMin.setMaximumSize(QSize(100, 16777215))
        self.doubleSpinBox_TMin.setStyleSheet(u"")
        self.doubleSpinBox_TMin.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_TMin.setMinimum(-273.000000000000000)
        self.doubleSpinBox_TMin.setMaximum(1000.000000000000000)
        self.doubleSpinBox_TMin.setSingleStep(0.100000000000000)

        self.gridLayout_7.addWidget(self.doubleSpinBox_TMin, 0, 2, 1, 1)

        self.spinBox_Years = QSpinBox(self.frame_simulation_period)
        self.spinBox_Years.setObjectName(u"spinBox_Years")
        self.spinBox_Years.setMinimumSize(QSize(100, 0))
        self.spinBox_Years.setMaximumSize(QSize(100, 16777215))
        self.spinBox_Years.setStyleSheet(u"")
        self.spinBox_Years.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.spinBox_Years.setMinimum(1)
        self.spinBox_Years.setMaximum(100)
        self.spinBox_Years.setValue(20)

        self.gridLayout_7.addWidget(self.spinBox_Years, 2, 2, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(445, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_7.addItem(self.horizontalSpacer_3, 2, 1, 1, 1)


        self.verticalLayout_5.addLayout(self.gridLayout_7)


        self.verticalLayout_8.addWidget(self.frame_simulation_period)

        self.label_38 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_38.setObjectName(u"label_38")
        self.label_38.setMinimumSize(QSize(0, 10))
        self.label_38.setMaximumSize(QSize(16777215, 10))

        self.verticalLayout_8.addWidget(self.label_38)

        self.label_WarningCustomBorefield = QLabel(self.scrollAreaWidgetContents_3)
        self.label_WarningCustomBorefield.setObjectName(u"label_WarningCustomBorefield")
        self.label_WarningCustomBorefield.setFont(font)
        self.label_WarningCustomBorefield.setStyleSheet(u"color: rgb(255, 200, 87);")
        self.label_WarningCustomBorefield.setWordWrap(True)

        self.verticalLayout_8.addWidget(self.label_WarningCustomBorefield)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_8.addItem(self.verticalSpacer_2)

        self.label_44 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_44.setObjectName(u"label_44")
        self.label_44.setMinimumSize(QSize(0, 10))
        self.label_44.setMaximumSize(QSize(16777215, 10))

        self.verticalLayout_8.addWidget(self.label_44)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.pushButton_PreviousGeneral = QPushButton(self.scrollAreaWidgetContents_3)
        self.pushButton_PreviousGeneral.setObjectName(u"pushButton_PreviousGeneral")
        self.pushButton_PreviousGeneral.setMinimumSize(QSize(0, 30))
        self.pushButton_PreviousGeneral.setMaximumSize(QSize(16777215, 30))
        self.pushButton_PreviousGeneral.setStyleSheet(u"")
        icon29 = QIcon()
        icon29.addFile(u":/icons/icons/ArrowLeft2.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_PreviousGeneral.setIcon(icon29)
        self.pushButton_PreviousGeneral.setIconSize(QSize(20, 20))
        self.pushButton_PreviousGeneral.setCheckable(False)

        self.horizontalLayout_4.addWidget(self.pushButton_PreviousGeneral)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_4)

        self.pushButton_NextGeneral = QPushButton(self.scrollAreaWidgetContents_3)
        self.pushButton_NextGeneral.setObjectName(u"pushButton_NextGeneral")
        self.pushButton_NextGeneral.setMinimumSize(QSize(0, 30))
        self.pushButton_NextGeneral.setMaximumSize(QSize(16777215, 30))
        self.pushButton_NextGeneral.setLayoutDirection(Qt.RightToLeft)
        self.pushButton_NextGeneral.setStyleSheet(u"")
        self.pushButton_NextGeneral.setIcon(icon28)
        self.pushButton_NextGeneral.setIconSize(QSize(20, 20))

        self.horizontalLayout_4.addWidget(self.pushButton_NextGeneral)


        self.verticalLayout_8.addLayout(self.horizontalLayout_4)

        self.scrollArea_General.setWidget(self.scrollAreaWidgetContents_3)

        self.verticalLayout_7.addWidget(self.scrollArea_General)

        self.stackedWidget.addWidget(self.page_General)
        self.page_borehole_resistance = QWidget()
        self.page_borehole_resistance.setObjectName(u"page_borehole_resistance")
        self.verticalLayout_33 = QVBoxLayout(self.page_borehole_resistance)
        self.verticalLayout_33.setObjectName(u"verticalLayout_33")
        self.scrollArea_2 = QScrollArea(self.page_borehole_resistance)
        self.scrollArea_2.setObjectName(u"scrollArea_2")
        self.scrollArea_2.setFrameShape(QFrame.NoFrame)
        self.scrollArea_2.setLineWidth(0)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollAreaWidgetContents_5 = QWidget()
        self.scrollAreaWidgetContents_5.setObjectName(u"scrollAreaWidgetContents_5")
        self.scrollAreaWidgetContents_5.setGeometry(QRect(0, 0, 540, 735))
        self.verticalLayout_17 = QVBoxLayout(self.scrollAreaWidgetContents_5)
        self.verticalLayout_17.setSpacing(0)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.verticalLayout_17.setContentsMargins(0, 0, 0, 0)
        self.label_Borehole_Resistance = QLabel(self.scrollAreaWidgetContents_5)
        self.label_Borehole_Resistance.setObjectName(u"label_Borehole_Resistance")
        self.label_Borehole_Resistance.setStyleSheet(u"font: 63 16pt \"Lexend SemiBold\";")

        self.verticalLayout_17.addWidget(self.label_Borehole_Resistance)

        self.label_49 = QLabel(self.scrollAreaWidgetContents_5)
        self.label_49.setObjectName(u"label_49")
        sizePolicy.setHeightForWidth(self.label_49.sizePolicy().hasHeightForWidth())
        self.label_49.setSizePolicy(sizePolicy)
        self.label_49.setMinimumSize(QSize(0, 10))
        self.label_49.setMaximumSize(QSize(16777215, 10))

        self.verticalLayout_17.addWidget(self.label_49)

        self.label_Borehole_Resistance_Head = QLabel(self.scrollAreaWidgetContents_5)
        self.label_Borehole_Resistance_Head.setObjectName(u"label_Borehole_Resistance_Head")
        self.label_Borehole_Resistance_Head.setStyleSheet(u"QLabel {\n"
"        qproperty-alignment: AlignCenter;\n"
"	border: 1px solid  rgb(84, 188, 235);\n"
"	border-top-left-radius: 15px;\n"
"	border-top-right-radius: 15px;\n"
"	background-color:  rgb(84, 188, 235);\n"
"	padding: 5px 0px;\n"
"	color:  rgb(255, 255, 235);\n"
"font-weight:500;\n"
"}")

        self.verticalLayout_17.addWidget(self.label_Borehole_Resistance_Head)

        self.frame_9 = QFrame(self.scrollAreaWidgetContents_5)
        self.frame_9.setObjectName(u"frame_9")
        self.frame_9.setStyleSheet(u"QFrame {\n"
"	border: 1px solid #54bceb;\n"
"	border-bottom-left-radius: 15px;\n"
"	border-bottom-right-radius: 15px;\n"
"}\n"
"QLabel{border: 0px solid rgb(255,255,255);}")
        self.frame_9.setFrameShape(QFrame.StyledPanel)
        self.frame_9.setFrameShadow(QFrame.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.frame_9)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.gridLayout_9 = QGridLayout()
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.gridLayout_9.setHorizontalSpacing(6)
        self.gridLayout_9.setVerticalSpacing(0)
        self.label_Rb_calculation_method = QLabel(self.frame_9)
        self.label_Rb_calculation_method.setObjectName(u"label_Rb_calculation_method")
        self.label_Rb_calculation_method.setStyleSheet(u"")

        self.gridLayout_9.addWidget(self.label_Rb_calculation_method, 0, 0, 1, 1)

        self.label_BoreholeResistance = QLabel(self.frame_9)
        self.label_BoreholeResistance.setObjectName(u"label_BoreholeResistance")
        self.label_BoreholeResistance.setStyleSheet(u"")

        self.gridLayout_9.addWidget(self.label_BoreholeResistance, 2, 0, 1, 1)

        self.comboBox_Rb_method = QComboBox(self.frame_9)
        self.comboBox_Rb_method.addItem("")
        self.comboBox_Rb_method.addItem("")
        self.comboBox_Rb_method.addItem("")
        self.comboBox_Rb_method.setObjectName(u"comboBox_Rb_method")
        self.comboBox_Rb_method.setMinimumSize(QSize(220, 0))
        self.comboBox_Rb_method.setStyleSheet(u"QFrame {\n"
"	border: 1px solid rgb(255, 255, 255);\n"
"	border-bottom-left-radius: 0px;\n"
"	border-bottom-right-radius: 0px;\n"
"}")
        self.comboBox_Rb_method.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.comboBox_Rb_method.setMinimumContentsLength(0)

        self.gridLayout_9.addWidget(self.comboBox_Rb_method, 0, 2, 1, 1)

        self.doubleSpinBox_Rb = QDoubleSpinBox(self.frame_9)
        self.doubleSpinBox_Rb.setObjectName(u"doubleSpinBox_Rb")
        self.doubleSpinBox_Rb.setStyleSheet(u"")
        self.doubleSpinBox_Rb.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_Rb.setDecimals(4)
        self.doubleSpinBox_Rb.setMinimum(0.000000000000000)
        self.doubleSpinBox_Rb.setMaximum(100.000000000000000)
        self.doubleSpinBox_Rb.setSingleStep(0.010000000000000)
        self.doubleSpinBox_Rb.setValue(0.015000000000000)

        self.gridLayout_9.addWidget(self.doubleSpinBox_Rb, 2, 2, 1, 1)

        self.label_2 = QLabel(self.frame_9)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(0, 6))
        self.label_2.setMaximumSize(QSize(16777215, 6))

        self.gridLayout_9.addWidget(self.label_2, 1, 0, 1, 1)

        self.horizontalSpacer_6 = QSpacerItem(551, 9, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_9.addItem(self.horizontalSpacer_6, 0, 1, 1, 1)


        self.verticalLayout_4.addLayout(self.gridLayout_9)


        self.verticalLayout_17.addWidget(self.frame_9)

        self.label_47 = QLabel(self.scrollAreaWidgetContents_5)
        self.label_47.setObjectName(u"label_47")
        self.label_47.setMinimumSize(QSize(0, 6))
        self.label_47.setMaximumSize(QSize(16777215, 6))

        self.verticalLayout_17.addWidget(self.label_47)

        self.label_fluid_data = QLabel(self.scrollAreaWidgetContents_5)
        self.label_fluid_data.setObjectName(u"label_fluid_data")
        self.label_fluid_data.setStyleSheet(u"QLabel {\n"
"        qproperty-alignment: AlignCenter;\n"
"	border: 1px solid  rgb(84, 188, 235);\n"
"	border-top-left-radius: 15px;\n"
"	border-top-right-radius: 15px;\n"
"	background-color:  rgb(84, 188, 235);\n"
"	padding: 5px 0px;\n"
"	color:  rgb(255, 255, 235);\n"
"font-weight:500;\n"
"}")

        self.verticalLayout_17.addWidget(self.label_fluid_data)

        self.frame_fluid_data = QFrame(self.scrollAreaWidgetContents_5)
        self.frame_fluid_data.setObjectName(u"frame_fluid_data")
        self.frame_fluid_data.setStyleSheet(u"QFrame {\n"
"	border: 1px solid #54bceb;\n"
"	border-bottom-left-radius: 15px;\n"
"	border-bottom-right-radius: 15px;\n"
"}\n"
"QLabel{border: 0px solid rgb(255,255,255);}")
        self.frame_fluid_data.setFrameShape(QFrame.StyledPanel)
        self.frame_fluid_data.setFrameShadow(QFrame.Raised)
        self.gridLayout_5 = QGridLayout(self.frame_fluid_data)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.label_fluid_thermal_capacity = QLabel(self.frame_fluid_data)
        self.label_fluid_thermal_capacity.setObjectName(u"label_fluid_thermal_capacity")

        self.gridLayout_5.addWidget(self.label_fluid_thermal_capacity, 3, 0, 1, 1)

        self.doubleSpinBox_fluid_thermal_capacity = QDoubleSpinBox(self.frame_fluid_data)
        self.doubleSpinBox_fluid_thermal_capacity.setObjectName(u"doubleSpinBox_fluid_thermal_capacity")
        self.doubleSpinBox_fluid_thermal_capacity.setStyleSheet(u"")
        self.doubleSpinBox_fluid_thermal_capacity.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_fluid_thermal_capacity.setDecimals(1)
        self.doubleSpinBox_fluid_thermal_capacity.setMinimum(0.000000000000000)
        self.doubleSpinBox_fluid_thermal_capacity.setMaximum(100000000.000000000000000)
        self.doubleSpinBox_fluid_thermal_capacity.setSingleStep(100.000000000000000)
        self.doubleSpinBox_fluid_thermal_capacity.setValue(4182.000000000000000)

        self.gridLayout_5.addWidget(self.doubleSpinBox_fluid_thermal_capacity, 3, 2, 1, 1)

        self.label_fluid_mass_flow_rate = QLabel(self.frame_fluid_data)
        self.label_fluid_mass_flow_rate.setObjectName(u"label_fluid_mass_flow_rate")

        self.gridLayout_5.addWidget(self.label_fluid_mass_flow_rate, 1, 0, 1, 1)

        self.horizontalSpacer_18 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_5.addItem(self.horizontalSpacer_18, 0, 1, 1, 1)

        self.label_fluid_lambda = QLabel(self.frame_fluid_data)
        self.label_fluid_lambda.setObjectName(u"label_fluid_lambda")

        self.gridLayout_5.addWidget(self.label_fluid_lambda, 0, 0, 1, 1)

        self.doubleSpinBox_fluid_lambda = QDoubleSpinBox(self.frame_fluid_data)
        self.doubleSpinBox_fluid_lambda.setObjectName(u"doubleSpinBox_fluid_lambda")
        self.doubleSpinBox_fluid_lambda.setStyleSheet(u"")
        self.doubleSpinBox_fluid_lambda.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_fluid_lambda.setDecimals(3)
        self.doubleSpinBox_fluid_lambda.setMinimum(0.000000000000000)
        self.doubleSpinBox_fluid_lambda.setMaximum(100.000000000000000)
        self.doubleSpinBox_fluid_lambda.setSingleStep(0.100000000000000)
        self.doubleSpinBox_fluid_lambda.setValue(0.500000000000000)

        self.gridLayout_5.addWidget(self.doubleSpinBox_fluid_lambda, 0, 2, 1, 1)

        self.label_fluid_density = QLabel(self.frame_fluid_data)
        self.label_fluid_density.setObjectName(u"label_fluid_density")

        self.gridLayout_5.addWidget(self.label_fluid_density, 2, 0, 1, 1)

        self.doubleSpinBox_fluid_mass_flow_rate = QDoubleSpinBox(self.frame_fluid_data)
        self.doubleSpinBox_fluid_mass_flow_rate.setObjectName(u"doubleSpinBox_fluid_mass_flow_rate")
        self.doubleSpinBox_fluid_mass_flow_rate.setStyleSheet(u"")
        self.doubleSpinBox_fluid_mass_flow_rate.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_fluid_mass_flow_rate.setDecimals(3)
        self.doubleSpinBox_fluid_mass_flow_rate.setMinimum(0.000000000000000)
        self.doubleSpinBox_fluid_mass_flow_rate.setMaximum(10000000.000000000000000)
        self.doubleSpinBox_fluid_mass_flow_rate.setSingleStep(0.100000000000000)
        self.doubleSpinBox_fluid_mass_flow_rate.setValue(0.500000000000000)

        self.gridLayout_5.addWidget(self.doubleSpinBox_fluid_mass_flow_rate, 1, 2, 1, 1)

        self.doubleSpinBox_fluid_density = QDoubleSpinBox(self.frame_fluid_data)
        self.doubleSpinBox_fluid_density.setObjectName(u"doubleSpinBox_fluid_density")
        self.doubleSpinBox_fluid_density.setStyleSheet(u"")
        self.doubleSpinBox_fluid_density.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_fluid_density.setDecimals(1)
        self.doubleSpinBox_fluid_density.setMinimum(0.000000000000000)
        self.doubleSpinBox_fluid_density.setMaximum(10000000.000000000000000)
        self.doubleSpinBox_fluid_density.setSingleStep(100.000000000000000)
        self.doubleSpinBox_fluid_density.setValue(1000.000000000000000)

        self.gridLayout_5.addWidget(self.doubleSpinBox_fluid_density, 2, 2, 1, 1)

        self.label_fluid_viscosity = QLabel(self.frame_fluid_data)
        self.label_fluid_viscosity.setObjectName(u"label_fluid_viscosity")

        self.gridLayout_5.addWidget(self.label_fluid_viscosity, 4, 0, 1, 1)

        self.doubleSpinBox_fluid_viscosity = QDoubleSpinBox(self.frame_fluid_data)
        self.doubleSpinBox_fluid_viscosity.setObjectName(u"doubleSpinBox_fluid_viscosity")
        self.doubleSpinBox_fluid_viscosity.setStyleSheet(u"")
        self.doubleSpinBox_fluid_viscosity.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_fluid_viscosity.setDecimals(6)
        self.doubleSpinBox_fluid_viscosity.setMinimum(0.000000000000000)
        self.doubleSpinBox_fluid_viscosity.setMaximum(1000.000000000000000)
        self.doubleSpinBox_fluid_viscosity.setSingleStep(0.000100000000000)
        self.doubleSpinBox_fluid_viscosity.setValue(0.001000000000000)

        self.gridLayout_5.addWidget(self.doubleSpinBox_fluid_viscosity, 4, 2, 1, 1)


        self.verticalLayout_17.addWidget(self.frame_fluid_data)

        self.label_48 = QLabel(self.scrollAreaWidgetContents_5)
        self.label_48.setObjectName(u"label_48")
        self.label_48.setMinimumSize(QSize(0, 6))
        self.label_48.setMaximumSize(QSize(16777215, 6))

        self.verticalLayout_17.addWidget(self.label_48)

        self.label_pipe_data = QLabel(self.scrollAreaWidgetContents_5)
        self.label_pipe_data.setObjectName(u"label_pipe_data")
        self.label_pipe_data.setStyleSheet(u"QLabel {\n"
"        qproperty-alignment: AlignCenter;\n"
"	border: 1px solid  rgb(84, 188, 235);\n"
"	border-top-left-radius: 15px;\n"
"	border-top-right-radius: 15px;\n"
"	background-color:  rgb(84, 188, 235);\n"
"	padding: 5px 0px;\n"
"	color:  rgb(255, 255, 235);\n"
"font-weight:500;\n"
"}")

        self.verticalLayout_17.addWidget(self.label_pipe_data)

        self.frame_pipe_data = QFrame(self.scrollAreaWidgetContents_5)
        self.frame_pipe_data.setObjectName(u"frame_pipe_data")
        self.frame_pipe_data.setStyleSheet(u"QFrame {\n"
"	border: 1px solid #54bceb;\n"
"	border-bottom-left-radius: 15px;\n"
"	border-bottom-right-radius: 15px;\n"
"}\n"
"QLabel{border: 0px solid rgb(255,255,255);}")
        self.frame_pipe_data.setFrameShape(QFrame.StyledPanel)
        self.frame_pipe_data.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_35 = QHBoxLayout(self.frame_pipe_data)
        self.horizontalLayout_35.setObjectName(u"horizontalLayout_35")
        self.graphicsView = QGraphicsView(self.frame_pipe_data)
        self.graphicsView.setObjectName(u"graphicsView")
        self.graphicsView.setMinimumSize(QSize(0, 0))
        self.graphicsView.setMaximumSize(QSize(100, 16777215))
        self.graphicsView.setStyleSheet(u"QFrame {\n"
"	border: 1px solid #54bceb;\n"
"	border-bottom-left-radius: 0px;\n"
"	border-bottom-right-radius: 0px;\n"
"}\n"
"QLabel{border: 0px solid rgb(255,255,255);}")

        self.horizontalLayout_35.addWidget(self.graphicsView)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_NumberOfPipes = QLabel(self.frame_pipe_data)
        self.label_NumberOfPipes.setObjectName(u"label_NumberOfPipes")

        self.gridLayout.addWidget(self.label_NumberOfPipes, 0, 0, 1, 1)

        self.doubleSpinBox_pipe_roughness = QDoubleSpinBox(self.frame_pipe_data)
        self.doubleSpinBox_pipe_roughness.setObjectName(u"doubleSpinBox_pipe_roughness")
        self.doubleSpinBox_pipe_roughness.setStyleSheet(u"")
        self.doubleSpinBox_pipe_roughness.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_pipe_roughness.setDecimals(7)
        self.doubleSpinBox_pipe_roughness.setMinimum(0.000000000000000)
        self.doubleSpinBox_pipe_roughness.setMaximum(1000.000000000000000)
        self.doubleSpinBox_pipe_roughness.setSingleStep(0.000001000000000)
        self.doubleSpinBox_pipe_roughness.setValue(0.000001000000000)

        self.gridLayout.addWidget(self.doubleSpinBox_pipe_roughness, 7, 2, 1, 1)

        self.doubleSpinBox_pipe_distance = QDoubleSpinBox(self.frame_pipe_data)
        self.doubleSpinBox_pipe_distance.setObjectName(u"doubleSpinBox_pipe_distance")
        self.doubleSpinBox_pipe_distance.setStyleSheet(u"")
        self.doubleSpinBox_pipe_distance.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_pipe_distance.setDecimals(4)
        self.doubleSpinBox_pipe_distance.setMinimum(0.000000000000000)
        self.doubleSpinBox_pipe_distance.setMaximum(1000.000000000000000)
        self.doubleSpinBox_pipe_distance.setSingleStep(0.001000000000000)
        self.doubleSpinBox_pipe_distance.setValue(0.040000000000000)

        self.gridLayout.addWidget(self.doubleSpinBox_pipe_distance, 6, 2, 1, 1)

        self.doubleSpinBox_pipe_inner_radius = QDoubleSpinBox(self.frame_pipe_data)
        self.doubleSpinBox_pipe_inner_radius.setObjectName(u"doubleSpinBox_pipe_inner_radius")
        self.doubleSpinBox_pipe_inner_radius.setStyleSheet(u"")
        self.doubleSpinBox_pipe_inner_radius.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_pipe_inner_radius.setDecimals(4)
        self.doubleSpinBox_pipe_inner_radius.setMinimum(0.000000000000000)
        self.doubleSpinBox_pipe_inner_radius.setMaximum(10000000.000000000000000)
        self.doubleSpinBox_pipe_inner_radius.setSingleStep(0.001000000000000)
        self.doubleSpinBox_pipe_inner_radius.setValue(0.020000000000000)

        self.gridLayout.addWidget(self.doubleSpinBox_pipe_inner_radius, 4, 2, 1, 1)

        self.doubleSpinBox_borehole_radius = QDoubleSpinBox(self.frame_pipe_data)
        self.doubleSpinBox_borehole_radius.setObjectName(u"doubleSpinBox_borehole_radius")
        self.doubleSpinBox_borehole_radius.setStyleSheet(u"")
        self.doubleSpinBox_borehole_radius.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_borehole_radius.setDecimals(4)
        self.doubleSpinBox_borehole_radius.setMinimum(0.000000000000000)
        self.doubleSpinBox_borehole_radius.setMaximum(1000.000000000000000)
        self.doubleSpinBox_borehole_radius.setSingleStep(0.001000000000000)
        self.doubleSpinBox_borehole_radius.setValue(0.075000000000000)

        self.gridLayout.addWidget(self.doubleSpinBox_borehole_radius, 5, 2, 1, 1)

        self.spinBox_number_pipes = QSpinBox(self.frame_pipe_data)
        self.spinBox_number_pipes.setObjectName(u"spinBox_number_pipes")
        self.spinBox_number_pipes.setLayoutDirection(Qt.LeftToRight)
        self.spinBox_number_pipes.setStyleSheet(u"")
        self.spinBox_number_pipes.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.spinBox_number_pipes.setMinimum(1)
        self.spinBox_number_pipes.setValue(2)

        self.gridLayout.addWidget(self.spinBox_number_pipes, 0, 2, 1, 1)

        self.label_grout_conductivity = QLabel(self.frame_pipe_data)
        self.label_grout_conductivity.setObjectName(u"label_grout_conductivity")

        self.gridLayout.addWidget(self.label_grout_conductivity, 1, 0, 1, 1)

        self.horizontalSpacer_19 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_19, 0, 1, 1, 1)

        self.doubleSpinBox_pipe_conductivity = QDoubleSpinBox(self.frame_pipe_data)
        self.doubleSpinBox_pipe_conductivity.setObjectName(u"doubleSpinBox_pipe_conductivity")
        self.doubleSpinBox_pipe_conductivity.setStyleSheet(u"")
        self.doubleSpinBox_pipe_conductivity.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_pipe_conductivity.setDecimals(3)
        self.doubleSpinBox_pipe_conductivity.setMinimum(0.000000000000000)
        self.doubleSpinBox_pipe_conductivity.setMaximum(100000.000000000000000)
        self.doubleSpinBox_pipe_conductivity.setSingleStep(0.100000000000000)
        self.doubleSpinBox_pipe_conductivity.setValue(0.420000000000000)

        self.gridLayout.addWidget(self.doubleSpinBox_pipe_conductivity, 2, 2, 1, 1)

        self.doubleSpinBox_grout_conductivity = QDoubleSpinBox(self.frame_pipe_data)
        self.doubleSpinBox_grout_conductivity.setObjectName(u"doubleSpinBox_grout_conductivity")
        self.doubleSpinBox_grout_conductivity.setStyleSheet(u"")
        self.doubleSpinBox_grout_conductivity.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_grout_conductivity.setDecimals(3)
        self.doubleSpinBox_grout_conductivity.setMinimum(0.000000000000000)
        self.doubleSpinBox_grout_conductivity.setMaximum(100000.000000000000000)
        self.doubleSpinBox_grout_conductivity.setSingleStep(0.100000000000000)
        self.doubleSpinBox_grout_conductivity.setValue(1.500000000000000)

        self.gridLayout.addWidget(self.doubleSpinBox_grout_conductivity, 1, 2, 1, 1)

        self.doubleSpinBox_pipe_outer_radius = QDoubleSpinBox(self.frame_pipe_data)
        self.doubleSpinBox_pipe_outer_radius.setObjectName(u"doubleSpinBox_pipe_outer_radius")
        self.doubleSpinBox_pipe_outer_radius.setStyleSheet(u"")
        self.doubleSpinBox_pipe_outer_radius.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_pipe_outer_radius.setDecimals(4)
        self.doubleSpinBox_pipe_outer_radius.setMinimum(0.000000000000000)
        self.doubleSpinBox_pipe_outer_radius.setMaximum(1000.000000000000000)
        self.doubleSpinBox_pipe_outer_radius.setSingleStep(0.001000000000000)
        self.doubleSpinBox_pipe_outer_radius.setValue(0.022000000000000)

        self.gridLayout.addWidget(self.doubleSpinBox_pipe_outer_radius, 3, 2, 1, 1)

        self.doubleSpinBox_borehole_burial_depth = QDoubleSpinBox(self.frame_pipe_data)
        self.doubleSpinBox_borehole_burial_depth.setObjectName(u"doubleSpinBox_borehole_burial_depth")
        self.doubleSpinBox_borehole_burial_depth.setStyleSheet(u"")
        self.doubleSpinBox_borehole_burial_depth.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_borehole_burial_depth.setDecimals(1)
        self.doubleSpinBox_borehole_burial_depth.setMinimum(0.000000000000000)
        self.doubleSpinBox_borehole_burial_depth.setMaximum(1000.000000000000000)
        self.doubleSpinBox_borehole_burial_depth.setSingleStep(0.500000000000000)
        self.doubleSpinBox_borehole_burial_depth.setValue(4.000000000000000)

        self.gridLayout.addWidget(self.doubleSpinBox_borehole_burial_depth, 8, 2, 1, 1)

        self.label_pipe_conductivity = QLabel(self.frame_pipe_data)
        self.label_pipe_conductivity.setObjectName(u"label_pipe_conductivity")

        self.gridLayout.addWidget(self.label_pipe_conductivity, 2, 0, 1, 1)

        self.label_pipe_outer_radius = QLabel(self.frame_pipe_data)
        self.label_pipe_outer_radius.setObjectName(u"label_pipe_outer_radius")

        self.gridLayout.addWidget(self.label_pipe_outer_radius, 3, 0, 1, 1)

        self.label_pipe_inner_radius = QLabel(self.frame_pipe_data)
        self.label_pipe_inner_radius.setObjectName(u"label_pipe_inner_radius")

        self.gridLayout.addWidget(self.label_pipe_inner_radius, 4, 0, 1, 1)

        self.label_borehole_radius = QLabel(self.frame_pipe_data)
        self.label_borehole_radius.setObjectName(u"label_borehole_radius")

        self.gridLayout.addWidget(self.label_borehole_radius, 5, 0, 1, 1)

        self.label_pipe_distance = QLabel(self.frame_pipe_data)
        self.label_pipe_distance.setObjectName(u"label_pipe_distance")

        self.gridLayout.addWidget(self.label_pipe_distance, 6, 0, 1, 1)

        self.label_pipe_roughness = QLabel(self.frame_pipe_data)
        self.label_pipe_roughness.setObjectName(u"label_pipe_roughness")

        self.gridLayout.addWidget(self.label_pipe_roughness, 7, 0, 1, 1)

        self.label_borehole_burial_depth = QLabel(self.frame_pipe_data)
        self.label_borehole_burial_depth.setObjectName(u"label_borehole_burial_depth")

        self.gridLayout.addWidget(self.label_borehole_burial_depth, 8, 0, 1, 1)


        self.horizontalLayout_35.addLayout(self.gridLayout)


        self.verticalLayout_17.addWidget(self.frame_pipe_data)

        self.verticalSpacer_12 = QSpacerItem(20, 442, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_17.addItem(self.verticalSpacer_12)

        self.label_63 = QLabel(self.scrollAreaWidgetContents_5)
        self.label_63.setObjectName(u"label_63")
        self.label_63.setMinimumSize(QSize(0, 10))
        self.label_63.setMaximumSize(QSize(16777215, 10))

        self.verticalLayout_17.addWidget(self.label_63)

        self.horizontalLayout_45 = QHBoxLayout()
        self.horizontalLayout_45.setObjectName(u"horizontalLayout_45")
        self.pushButton_PreviousResistance = QPushButton(self.scrollAreaWidgetContents_5)
        self.pushButton_PreviousResistance.setObjectName(u"pushButton_PreviousResistance")
        self.pushButton_PreviousResistance.setMinimumSize(QSize(0, 30))
        self.pushButton_PreviousResistance.setMaximumSize(QSize(16777215, 30))
        self.pushButton_PreviousResistance.setStyleSheet(u"")
        self.pushButton_PreviousResistance.setIcon(icon29)
        self.pushButton_PreviousResistance.setIconSize(QSize(20, 20))
        self.pushButton_PreviousResistance.setCheckable(False)

        self.horizontalLayout_45.addWidget(self.pushButton_PreviousResistance)

        self.horizontalSpacer_38 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_45.addItem(self.horizontalSpacer_38)

        self.pushButton_NextResistance = QPushButton(self.scrollAreaWidgetContents_5)
        self.pushButton_NextResistance.setObjectName(u"pushButton_NextResistance")
        self.pushButton_NextResistance.setMinimumSize(QSize(0, 30))
        self.pushButton_NextResistance.setMaximumSize(QSize(16777215, 30))
        self.pushButton_NextResistance.setLayoutDirection(Qt.RightToLeft)
        self.pushButton_NextResistance.setStyleSheet(u"")
        self.pushButton_NextResistance.setIcon(icon28)
        self.pushButton_NextResistance.setIconSize(QSize(20, 20))

        self.horizontalLayout_45.addWidget(self.pushButton_NextResistance)


        self.verticalLayout_17.addLayout(self.horizontalLayout_45)

        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_5)

        self.verticalLayout_33.addWidget(self.scrollArea_2)

        self.stackedWidget.addWidget(self.page_borehole_resistance)
        self.page_thermal = QWidget()
        self.page_thermal.setObjectName(u"page_thermal")
        self.verticalLayout_2 = QVBoxLayout(self.page_thermal)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.scrollArea_thermal = QScrollArea(self.page_thermal)
        self.scrollArea_thermal.setObjectName(u"scrollArea_thermal")
        self.scrollArea_thermal.setFrameShape(QFrame.NoFrame)
        self.scrollArea_thermal.setLineWidth(0)
        self.scrollArea_thermal.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 884, 1191))
        self.verticalLayout_20 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_20.setSpacing(0)
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.verticalLayout_20.setContentsMargins(0, 0, 0, 0)
        self.label_ThermalDemandsTitle = QLabel(self.scrollAreaWidgetContents)
        self.label_ThermalDemandsTitle.setObjectName(u"label_ThermalDemandsTitle")
        self.label_ThermalDemandsTitle.setStyleSheet(u"font: 63 16pt \"Lexend SemiBold\";")

        self.verticalLayout_20.addWidget(self.label_ThermalDemandsTitle)

        self.label_40 = QLabel(self.scrollAreaWidgetContents)
        self.label_40.setObjectName(u"label_40")
        self.label_40.setMinimumSize(QSize(0, 10))
        self.label_40.setMaximumSize(QSize(16777215, 10))

        self.verticalLayout_20.addWidget(self.label_40)

        self.label_Import = QLabel(self.scrollAreaWidgetContents)
        self.label_Import.setObjectName(u"label_Import")
        self.label_Import.setStyleSheet(u"QLabel {\n"
"        qproperty-alignment: AlignCenter;\n"
"	border: 1px solid  rgb(84, 188, 235);\n"
"	border-top-left-radius: 15px;\n"
"	border-top-right-radius: 15px;\n"
"	background-color:  rgb(84, 188, 235);\n"
"	padding: 5px 0px;\n"
"	color:  rgb(255, 255, 235);\n"
"font-weight:500;\n"
"}")

        self.verticalLayout_20.addWidget(self.label_Import)

        self.frame_import = QFrame(self.scrollAreaWidgetContents)
        self.frame_import.setObjectName(u"frame_import")
        self.frame_import.setStyleSheet(u"QFrame {\n"
"	border: 1px solid #54bceb;\n"
"	border-bottom-left-radius: 15px;\n"
"	border-bottom-right-radius: 15px;\n"
"}\n"
"QLabel{border: 0px solid rgb(255,255,255);font: 12pt;}\n"
"")
        self.frame_import.setFrameShape(QFrame.StyledPanel)
        self.frame_import.setFrameShadow(QFrame.Raised)
        self.verticalLayout_9 = QVBoxLayout(self.frame_import)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(9, 9, 9, 9)
        self.checkBox_Import = QCheckBox(self.frame_import)
        self.checkBox_Import.setObjectName(u"checkBox_Import")

        self.verticalLayout_9.addWidget(self.checkBox_Import)

        self.toolBox = QToolBox(self.frame_import)
        self.toolBox.setObjectName(u"toolBox")
        self.toolBox.setMinimumSize(QSize(0, 250))
        self.toolBox.setStyleSheet(u"QWidget{border: 0px solid rgb(255,255,255);}\n"
"QToolBox::tab {\n"
"    background: transparent;\n"
"	font-weight: 500;\n"
"}\n"
"QToolBox::tab:first {\n"
"	border-bottom: 1px solid #eee;\n"
"}\n"
"\n"
"QToolBox::tab:last {\n"
"	border-bottom: 1px solid #eee;\n"
"}\n"
"\n"
"QToolBox{\n"
"	border: 0px solid  rgb(255, 255, 255);\n"
"border-radius: 5px;\n"
"}\n"
"QComboBox{border: 1px solid #ffffff;\n"
"border-bottom-left-radius: 0px;\n"
"border-bottom-right-radius: 0px;}")
        self.page_File = QWidget()
        self.page_File.setObjectName(u"page_File")
        self.page_File.setGeometry(QRect(0, 0, 331, 241))
        self.verticalLayout = QVBoxLayout(self.page_File)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_DataType = QLabel(self.page_File)
        self.label_DataType.setObjectName(u"label_DataType")
        self.label_DataType.setStyleSheet(u"")
        self.label_DataType.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.horizontalLayout.addWidget(self.label_DataType)

        self.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_10)

        self.comboBox_Datentyp = QComboBox(self.page_File)
        self.comboBox_Datentyp.addItem("")
        self.comboBox_Datentyp.addItem("")
        self.comboBox_Datentyp.addItem("")
        self.comboBox_Datentyp.setObjectName(u"comboBox_Datentyp")
        self.comboBox_Datentyp.setMinimumSize(QSize(60, 30))
        self.comboBox_Datentyp.setMaximumSize(QSize(200, 30))
        self.comboBox_Datentyp.setSizeIncrement(QSize(0, 0))
        self.comboBox_Datentyp.setBaseSize(QSize(0, 0))
        self.comboBox_Datentyp.setStyleSheet(u"QFrame {\n"
"	border: 1px solid rgb(255, 255, 255);\n"
"	border-bottom-left-radius: 0px;\n"
"	border-bottom-right-radius: 0px;\n"
"}")
        self.comboBox_Datentyp.setEditable(False)
        self.comboBox_Datentyp.setFrame(True)

        self.horizontalLayout.addWidget(self.comboBox_Datentyp)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.label_Filename = QLabel(self.page_File)
        self.label_Filename.setObjectName(u"label_Filename")
        self.label_Filename.setStyleSheet(u"")

        self.horizontalLayout_11.addWidget(self.label_Filename)

        self.lineEdit_displayCsv = QLineEdit(self.page_File)
        self.lineEdit_displayCsv.setObjectName(u"lineEdit_displayCsv")
        self.lineEdit_displayCsv.setMaximumSize(QSize(10000000, 25))
        self.lineEdit_displayCsv.setStyleSheet(u"QLineEdit{border: 3px solid rgb(84, 188, 235);\n"
"border-radius: 5px;\n"
f"color: {WHITE};\n"
"gridline-color: rgb(84, 188, 235);\n"
"background-color: rgb(84, 188, 235);\n"
"font-weight:500;\n"
"selection-background-color: rgb(42, 126, 179);}\n"
"QLineEdit:hover{background-color: rgb(0, 64, 122);}")

        self.horizontalLayout_11.addWidget(self.lineEdit_displayCsv)

        self.pushButton_loadCsv = QPushButton(self.page_File)
        self.pushButton_loadCsv.setObjectName(u"pushButton_loadCsv")
        self.pushButton_loadCsv.setMinimumSize(QSize(30, 30))
        self.pushButton_loadCsv.setMaximumSize(QSize(30, 30))
        self.pushButton_loadCsv.setStyleSheet(u"*{border: 3px solid rgb(84, 188, 235);\n"
"border-radius: 5px;\n"
f"color: {WHITE};\n"
"gridline-color: rgb(84, 188, 235);\n"
"background-color: rgb(84, 188, 235);\n"
"font: 75;}\n"
"*:hover{background-color: rgb(0, 64, 122);}")

        self.horizontalLayout_11.addWidget(self.pushButton_loadCsv)


        self.verticalLayout.addLayout(self.horizontalLayout_11)

        self.frame_Seperator = QFrame(self.page_File)
        self.frame_Seperator.setObjectName(u"frame_Seperator")
        self.frame_Seperator.setFrameShape(QFrame.NoFrame)
        self.frame_Seperator.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_26 = QHBoxLayout(self.frame_Seperator)
        self.horizontalLayout_26.setObjectName(u"horizontalLayout_26")
        self.horizontalLayout_26.setContentsMargins(0, 0, 0, 0)
        self.label_Seperator = QLabel(self.frame_Seperator)
        self.label_Seperator.setObjectName(u"label_Seperator")

        self.horizontalLayout_26.addWidget(self.label_Seperator)

        self.horizontalSpacer_23 = QSpacerItem(477, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_26.addItem(self.horizontalSpacer_23)

        self.comboBox_Seperator = QComboBox(self.frame_Seperator)
        self.comboBox_Seperator.addItem("")
        self.comboBox_Seperator.addItem("")
        self.comboBox_Seperator.setObjectName(u"comboBox_Seperator")
        self.comboBox_Seperator.setMinimumSize(QSize(120, 0))
        self.comboBox_Seperator.setStyleSheet(u"QFrame {\n"
"	border: 1px solid rgb(255, 255, 255);\n"
"	border-bottom-left-radius: 0px;\n"
"	border-bottom-right-radius: 0px;\n"
"}")
        self.comboBox_Seperator.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.horizontalLayout_26.addWidget(self.comboBox_Seperator)


        self.verticalLayout.addWidget(self.frame_Seperator)

        self.frame_decimal = QFrame(self.page_File)
        self.frame_decimal.setObjectName(u"frame_decimal")
        self.frame_decimal.setFrameShape(QFrame.NoFrame)
        self.frame_decimal.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_27 = QHBoxLayout(self.frame_decimal)
        self.horizontalLayout_27.setObjectName(u"horizontalLayout_27")
        self.horizontalLayout_27.setContentsMargins(0, 0, 0, 0)
        self.label_decimal = QLabel(self.frame_decimal)
        self.label_decimal.setObjectName(u"label_decimal")

        self.horizontalLayout_27.addWidget(self.label_decimal)

        self.horizontalSpacer_24 = QSpacerItem(477, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_27.addItem(self.horizontalSpacer_24)

        self.comboBox_decimal = QComboBox(self.frame_decimal)
        self.comboBox_decimal.addItem("")
        self.comboBox_decimal.addItem("")
        self.comboBox_decimal.setObjectName(u"comboBox_decimal")
        self.comboBox_decimal.setMinimumSize(QSize(120, 0))
        self.comboBox_decimal.setStyleSheet(u"QFrame {\n"
"	border: 1px solid rgb(255, 255, 255);\n"
"	border-bottom-left-radius: 0px;\n"
"	border-bottom-right-radius: 0px;\n"
"}")
        self.comboBox_decimal.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.horizontalLayout_27.addWidget(self.comboBox_decimal)


        self.verticalLayout.addWidget(self.frame_decimal)

        self.frame_sheetName = QFrame(self.page_File)
        self.frame_sheetName.setObjectName(u"frame_sheetName")
        self.frame_sheetName.setFrameShape(QFrame.NoFrame)
        self.frame_sheetName.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_19 = QHBoxLayout(self.frame_sheetName)
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.horizontalLayout_19.setContentsMargins(0, 0, 0, 0)
        self.label_SheetName = QLabel(self.frame_sheetName)
        self.label_SheetName.setObjectName(u"label_SheetName")
        self.label_SheetName.setMinimumSize(QSize(0, 25))
        self.label_SheetName.setMaximumSize(QSize(16777215, 25))
        self.label_SheetName.setStyleSheet(u"")

        self.horizontalLayout_19.addWidget(self.label_SheetName)

        self.horizontalSpacer_11 = QSpacerItem(477, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_19.addItem(self.horizontalSpacer_11)

        self.comboBox_sheetName = QComboBox(self.frame_sheetName)
        self.comboBox_sheetName.setObjectName(u"comboBox_sheetName")
        self.comboBox_sheetName.setMinimumSize(QSize(120, 30))
        self.comboBox_sheetName.setMaximumSize(QSize(300, 300))
        self.comboBox_sheetName.setStyleSheet(u"QFrame {\n"
"	border: 1px solid rgb(255, 255, 255);\n"
"	border-bottom-left-radius: 0px;\n"
"	border-bottom-right-radius: 0px;\n"
"}")
        self.comboBox_sheetName.setEditable(True)
        self.comboBox_sheetName.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.comboBox_sheetName.setFrame(True)

        self.horizontalLayout_19.addWidget(self.comboBox_sheetName)


        self.verticalLayout.addWidget(self.frame_sheetName)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_4)

        self.horizontalLayout_16 = QHBoxLayout()
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.horizontalSpacer_15 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_16.addItem(self.horizontalSpacer_15)

        self.pushButton_load = QPushButton(self.page_File)
        self.pushButton_load.setObjectName(u"pushButton_load")
        sizePolicy1.setHeightForWidth(self.pushButton_load.sizePolicy().hasHeightForWidth())
        self.pushButton_load.setSizePolicy(sizePolicy1)
        self.pushButton_load.setMinimumSize(QSize(100, 35))
        self.pushButton_load.setMaximumSize(QSize(100, 35))
        self.pushButton_load.setStyleSheet(u"QPushButton{border: 3px solid rgb(84, 188, 235);\n"
"border-radius: 5px;\n"
f"color: {WHITE};\n"
"gridline-color: rgb(84, 188, 235);\n"
"background-color: rgb(84, 188, 235);\n"
"font-weight:500;}\n"
"QPushButton:hover{background-color: rgb(0, 64, 122);}")
        icon30 = QIcon()
        icon30.addFile(u":/icons/icons/Download.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_load.setIcon(icon30)

        self.horizontalLayout_16.addWidget(self.pushButton_load)

        self.horizontalSpacer_16 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_16.addItem(self.horizontalSpacer_16)


        self.verticalLayout.addLayout(self.horizontalLayout_16)

        self.toolBox.addItem(self.page_File, u"Data file")
        self.page_DataLocation = QWidget()
        self.page_DataLocation.setObjectName(u"page_DataLocation")
        self.page_DataLocation.setGeometry(QRect(0, 0, 882, 188))
        self.verticalLayout_10 = QVBoxLayout(self.page_DataLocation)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.horizontalLayout_29 = QHBoxLayout()
        self.horizontalLayout_29.setObjectName(u"horizontalLayout_29")
        self.frame_thermalDemands = QFrame(self.page_DataLocation)
        self.frame_thermalDemands.setObjectName(u"frame_thermalDemands")
        self.frame_thermalDemands.setFrameShape(QFrame.NoFrame)
        self.frame_thermalDemands.setFrameShadow(QFrame.Raised)
        self.verticalLayout_15 = QVBoxLayout(self.frame_thermalDemands)
        self.verticalLayout_15.setSpacing(0)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.verticalLayout_15.setContentsMargins(0, 0, 0, 0)
        self.frame_8 = QFrame(self.frame_thermalDemands)
        self.frame_8.setObjectName(u"frame_8")
        self.frame_8.setFrameShape(QFrame.NoFrame)
        self.frame_8.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_15 = QHBoxLayout(self.frame_8)
        self.horizontalLayout_15.setSpacing(6)
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.horizontalLayout_15.setContentsMargins(0, 0, 0, 0)
        self.label_dataColumn = QLabel(self.frame_8)
        self.label_dataColumn.setObjectName(u"label_dataColumn")
        self.label_dataColumn.setMinimumSize(QSize(0, 25))
        self.label_dataColumn.setMaximumSize(QSize(16777215, 40))
        self.label_dataColumn.setStyleSheet(u"")
        self.label_dataColumn.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_15.addWidget(self.label_dataColumn, 0, Qt.AlignLeft)

        self.comboBox_dataColumn = QComboBox(self.frame_8)
        self.comboBox_dataColumn.addItem("")
        self.comboBox_dataColumn.addItem("")
        self.comboBox_dataColumn.setObjectName(u"comboBox_dataColumn")
        self.comboBox_dataColumn.setMinimumSize(QSize(100, 30))
        self.comboBox_dataColumn.setMaximumSize(QSize(150, 40))
        self.comboBox_dataColumn.setStyleSheet(u"")
        self.comboBox_dataColumn.setEditable(False)
        self.comboBox_dataColumn.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)

        self.horizontalLayout_15.addWidget(self.comboBox_dataColumn)


        self.verticalLayout_15.addWidget(self.frame_8)


        self.horizontalLayout_29.addWidget(self.frame_thermalDemands)

        self.frame_heatingLoad = QFrame(self.page_DataLocation)
        self.frame_heatingLoad.setObjectName(u"frame_heatingLoad")
        self.frame_heatingLoad.setMinimumSize(QSize(0, 25))
        self.frame_heatingLoad.setMaximumSize(QSize(1672341, 35))
        self.frame_heatingLoad.setFrameShape(QFrame.NoFrame)
        self.frame_heatingLoad.setFrameShadow(QFrame.Raised)
        self.frame_heatingLoad.setLineWidth(0)
        self.horizontalLayout_13 = QHBoxLayout(self.frame_heatingLoad)
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.horizontalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.label_HeatingLoadLine = QLabel(self.frame_heatingLoad)
        self.label_HeatingLoadLine.setObjectName(u"label_HeatingLoadLine")
        self.label_HeatingLoadLine.setMinimumSize(QSize(0, 30))
        self.label_HeatingLoadLine.setMaximumSize(QSize(1672341, 30))
        self.label_HeatingLoadLine.setStyleSheet(u"")
        self.label_HeatingLoadLine.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.horizontalLayout_13.addWidget(self.label_HeatingLoadLine, 0, Qt.AlignRight)

        self.comboBox_heatingLoad = QComboBox(self.frame_heatingLoad)
        self.comboBox_heatingLoad.setObjectName(u"comboBox_heatingLoad")
        self.comboBox_heatingLoad.setMinimumSize(QSize(0, 30))
        self.comboBox_heatingLoad.setMaximumSize(QSize(150, 16777215))
        self.comboBox_heatingLoad.setStyleSheet(u"")

        self.horizontalLayout_13.addWidget(self.comboBox_heatingLoad)


        self.horizontalLayout_29.addWidget(self.frame_heatingLoad)

        self.frame_coolingLoad = QFrame(self.page_DataLocation)
        self.frame_coolingLoad.setObjectName(u"frame_coolingLoad")
        self.frame_coolingLoad.setMinimumSize(QSize(0, 25))
        self.frame_coolingLoad.setMaximumSize(QSize(1672341, 35))
        self.frame_coolingLoad.setFrameShape(QFrame.NoFrame)
        self.frame_coolingLoad.setFrameShadow(QFrame.Raised)
        self.frame_coolingLoad.setLineWidth(0)
        self.horizontalLayout_24 = QHBoxLayout(self.frame_coolingLoad)
        self.horizontalLayout_24.setObjectName(u"horizontalLayout_24")
        self.horizontalLayout_24.setContentsMargins(0, 0, 0, 0)
        self.label_CoolingLoadLine = QLabel(self.frame_coolingLoad)
        self.label_CoolingLoadLine.setObjectName(u"label_CoolingLoadLine")
        self.label_CoolingLoadLine.setMinimumSize(QSize(0, 30))
        self.label_CoolingLoadLine.setMaximumSize(QSize(1672341, 30))
        self.label_CoolingLoadLine.setStyleSheet(u"")
        self.label_CoolingLoadLine.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.horizontalLayout_24.addWidget(self.label_CoolingLoadLine)

        self.comboBox_coolingLoad = QComboBox(self.frame_coolingLoad)
        self.comboBox_coolingLoad.setObjectName(u"comboBox_coolingLoad")
        self.comboBox_coolingLoad.setMinimumSize(QSize(0, 30))
        self.comboBox_coolingLoad.setMaximumSize(QSize(150, 16777215))
        self.comboBox_coolingLoad.setStyleSheet(u"")

        self.horizontalLayout_24.addWidget(self.comboBox_coolingLoad)


        self.horizontalLayout_29.addWidget(self.frame_coolingLoad)

        self.frame_combined = QFrame(self.page_DataLocation)
        self.frame_combined.setObjectName(u"frame_combined")
        self.frame_combined.setMinimumSize(QSize(0, 25))
        self.frame_combined.setMaximumSize(QSize(1672341, 35))
        self.frame_combined.setFrameShape(QFrame.NoFrame)
        self.frame_combined.setFrameShadow(QFrame.Raised)
        self.frame_combined.setLineWidth(0)
        self.horizontalLayout_32 = QHBoxLayout(self.frame_combined)
        self.horizontalLayout_32.setObjectName(u"horizontalLayout_32")
        self.horizontalLayout_32.setContentsMargins(0, 0, 0, 0)
        self.label_combined = QLabel(self.frame_combined)
        self.label_combined.setObjectName(u"label_combined")
        self.label_combined.setMinimumSize(QSize(0, 30))
        self.label_combined.setMaximumSize(QSize(1672341, 30))
        self.label_combined.setStyleSheet(u"")
        self.label_combined.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.horizontalLayout_32.addWidget(self.label_combined)

        self.comboBox_combined = QComboBox(self.frame_combined)
        self.comboBox_combined.setObjectName(u"comboBox_combined")
        self.comboBox_combined.setMinimumSize(QSize(0, 30))
        self.comboBox_combined.setMaximumSize(QSize(150, 16777215))
        self.comboBox_combined.setStyleSheet(u"")

        self.horizontalLayout_32.addWidget(self.comboBox_combined)


        self.horizontalLayout_29.addWidget(self.frame_combined)


        self.verticalLayout_10.addLayout(self.horizontalLayout_29)

        self.horizontalLayout_31 = QHBoxLayout()
        self.horizontalLayout_31.setObjectName(u"horizontalLayout_31")
        self.horizontalLayout_31.setContentsMargins(-1, 6, -1, 9)
        self.frame_timeStep = QFrame(self.page_DataLocation)
        self.frame_timeStep.setObjectName(u"frame_timeStep")
        self.frame_timeStep.setMinimumSize(QSize(0, 30))
        self.frame_timeStep.setMaximumSize(QSize(1672341, 35))
        self.frame_timeStep.setFrameShape(QFrame.NoFrame)
        self.frame_timeStep.setFrameShadow(QFrame.Raised)
        self.frame_timeStep.setLineWidth(0)
        self.horizontalLayout_28 = QHBoxLayout(self.frame_timeStep)
        self.horizontalLayout_28.setObjectName(u"horizontalLayout_28")
        self.horizontalLayout_28.setContentsMargins(0, 0, 0, 0)
        self.label_TimeStep = QLabel(self.frame_timeStep)
        self.label_TimeStep.setObjectName(u"label_TimeStep")
        self.label_TimeStep.setMinimumSize(QSize(0, 30))
        self.label_TimeStep.setMaximumSize(QSize(1672341, 30))
        self.label_TimeStep.setStyleSheet(u"")
        self.label_TimeStep.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.horizontalLayout_28.addWidget(self.label_TimeStep)

        self.comboBox_timeStep = QComboBox(self.frame_timeStep)
        self.comboBox_timeStep.addItem("")
        self.comboBox_timeStep.addItem("")
        self.comboBox_timeStep.addItem("")
        self.comboBox_timeStep.setObjectName(u"comboBox_timeStep")
        self.comboBox_timeStep.setMinimumSize(QSize(0, 30))
        self.comboBox_timeStep.setMaximumSize(QSize(150, 16777215))
        self.comboBox_timeStep.setStyleSheet(u"")

        self.horizontalLayout_28.addWidget(self.comboBox_timeStep)


        self.horizontalLayout_31.addWidget(self.frame_timeStep)

        self.frame_date = QFrame(self.page_DataLocation)
        self.frame_date.setObjectName(u"frame_date")
        self.frame_date.setMinimumSize(QSize(0, 30))
        self.frame_date.setMaximumSize(QSize(1672341, 35))
        self.frame_date.setFrameShape(QFrame.NoFrame)
        self.frame_date.setFrameShadow(QFrame.Raised)
        self.frame_date.setLineWidth(0)
        self.horizontalLayout_30 = QHBoxLayout(self.frame_date)
        self.horizontalLayout_30.setObjectName(u"horizontalLayout_30")
        self.horizontalLayout_30.setContentsMargins(0, 0, 0, 0)
        self.label_DateLine = QLabel(self.frame_date)
        self.label_DateLine.setObjectName(u"label_DateLine")
        self.label_DateLine.setMinimumSize(QSize(0, 30))
        self.label_DateLine.setMaximumSize(QSize(1672341, 30))
        self.label_DateLine.setStyleSheet(u"")
        self.label_DateLine.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.horizontalLayout_30.addWidget(self.label_DateLine, 0, Qt.AlignRight)

        self.comboBox_date = QComboBox(self.frame_date)
        self.comboBox_date.setObjectName(u"comboBox_date")
        self.comboBox_date.setMinimumSize(QSize(0, 30))
        self.comboBox_date.setMaximumSize(QSize(150, 16777215))
        self.comboBox_date.setStyleSheet(u"")

        self.horizontalLayout_30.addWidget(self.comboBox_date)


        self.horizontalLayout_31.addWidget(self.frame_date)


        self.verticalLayout_10.addLayout(self.horizontalLayout_31)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label_DataUnit = QLabel(self.page_DataLocation)
        self.label_DataUnit.setObjectName(u"label_DataUnit")
        self.label_DataUnit.setStyleSheet(u"")

        self.horizontalLayout_8.addWidget(self.label_DataUnit)

        self.horizontalSpacer_12 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_12)

        self.comboBox_dataUnit = QComboBox(self.page_DataLocation)
        self.comboBox_dataUnit.addItem("")
        self.comboBox_dataUnit.addItem("")
        self.comboBox_dataUnit.addItem("")
        self.comboBox_dataUnit.setObjectName(u"comboBox_dataUnit")
        self.comboBox_dataUnit.setEnabled(True)
        self.comboBox_dataUnit.setMinimumSize(QSize(60, 30))
        self.comboBox_dataUnit.setMaximumSize(QSize(150, 16777215))
        self.comboBox_dataUnit.setStyleSheet(u"")
        self.comboBox_dataUnit.setEditable(False)
        self.comboBox_dataUnit.setSizeAdjustPolicy(QComboBox.AdjustToContentsOnFirstShow)
        self.comboBox_dataUnit.setFrame(True)

        self.horizontalLayout_8.addWidget(self.comboBox_dataUnit)


        self.verticalLayout_10.addLayout(self.horizontalLayout_8)

        self.verticalSpacer_6 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_10.addItem(self.verticalSpacer_6)

        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.horizontalSpacer_13 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_14.addItem(self.horizontalSpacer_13)

        self.pushButton_calculate = QPushButton(self.page_DataLocation)
        self.pushButton_calculate.setObjectName(u"pushButton_calculate")
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.pushButton_calculate.sizePolicy().hasHeightForWidth())
        self.pushButton_calculate.setSizePolicy(sizePolicy2)
        self.pushButton_calculate.setMinimumSize(QSize(100, 35))
        self.pushButton_calculate.setMaximumSize(QSize(100, 35))
        self.pushButton_calculate.setLayoutDirection(Qt.LeftToRight)
        self.pushButton_calculate.setStyleSheet(u"QPushButton{border: 3px solid rgb(84, 188, 235);\n"
"border-radius: 5px;\n"
f"color: {WHITE};\n"
"gridline-color: rgb(84, 188, 235);\n"
"background-color: rgb(84, 188, 235);\n"
"font-weight:500;}\n"
"QPushButton:hover{background-color: rgb(0, 64, 122);}")
        self.pushButton_calculate.setIcon(icon26)
        self.pushButton_calculate.setFlat(False)

        self.horizontalLayout_14.addWidget(self.pushButton_calculate)

        self.horizontalSpacer_14 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_14.addItem(self.horizontalSpacer_14)


        self.verticalLayout_10.addLayout(self.horizontalLayout_14)

        self.toolBox.addItem(self.page_DataLocation, u"Data location in file")

        self.verticalLayout_9.addWidget(self.toolBox)


        self.verticalLayout_20.addWidget(self.frame_import)

        self.label_39 = QLabel(self.scrollAreaWidgetContents)
        self.label_39.setObjectName(u"label_39")
        self.label_39.setMinimumSize(QSize(0, 10))
        self.label_39.setMaximumSize(QSize(16777215, 10))

        self.verticalLayout_20.addWidget(self.label_39)

        self.label_ThermalDemands = QLabel(self.scrollAreaWidgetContents)
        self.label_ThermalDemands.setObjectName(u"label_ThermalDemands")
        self.label_ThermalDemands.setStyleSheet(u"QLabel {\n"
"        qproperty-alignment: AlignCenter;\n"
"	border: 1px solid  rgb(84, 188, 235);\n"
"	border-top-left-radius: 15px;\n"
"	border-top-right-radius: 15px;\n"
"	background-color:  rgb(84, 188, 235);\n"
"	padding: 5px 0px;\n"
"	color:  rgb(255, 255, 235);\n"
"font-weight:500;\n"
"}")

        self.verticalLayout_20.addWidget(self.label_ThermalDemands)

        self.frame_thermal_demand = QFrame(self.scrollAreaWidgetContents)
        self.frame_thermal_demand.setObjectName(u"frame_thermal_demand")
        self.frame_thermal_demand.setStyleSheet(u"QFrame {\n"
"	border: 1px solid #54bceb;\n"
"	border-bottom-left-radius: 15px;\n"
"	border-bottom-right-radius: 15px;\n"
"}\n"
"QLabel{border: 0px solid rgb(255,255,255);}")
        self.frame_thermal_demand.setFrameShape(QFrame.StyledPanel)
        self.frame_thermal_demand.setFrameShadow(QFrame.Raised)
        self.verticalLayout_11 = QVBoxLayout(self.frame_thermal_demand)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(9, 9, 9, 9)
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_Oct = QLabel(self.frame_thermal_demand)
        self.label_Oct.setObjectName(u"label_Oct")

        self.gridLayout_2.addWidget(self.label_Oct, 11, 0, 1, 1)

        self.label_Aug = QLabel(self.frame_thermal_demand)
        self.label_Aug.setObjectName(u"label_Aug")

        self.gridLayout_2.addWidget(self.label_Aug, 9, 0, 1, 1)

        self.label_pH = QLabel(self.frame_thermal_demand)
        self.label_pH.setObjectName(u"label_pH")

        self.gridLayout_2.addWidget(self.label_pH, 0, 1, 1, 1)

        self.label_Unit_pH = QLabel(self.frame_thermal_demand)
        self.label_Unit_pH.setObjectName(u"label_Unit_pH")

        self.gridLayout_2.addWidget(self.label_Unit_pH, 1, 1, 1, 1)

        self.label_Jan = QLabel(self.frame_thermal_demand)
        self.label_Jan.setObjectName(u"label_Jan")

        self.gridLayout_2.addWidget(self.label_Jan, 2, 0, 1, 1)

        self.label_pC = QLabel(self.frame_thermal_demand)
        self.label_pC.setObjectName(u"label_pC")

        self.gridLayout_2.addWidget(self.label_pC, 0, 2, 1, 1)

        self.doubleSpinBox_Hp_Jan = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_Hp_Jan.setObjectName(u"doubleSpinBox_Hp_Jan")
        self.doubleSpinBox_Hp_Jan.setStyleSheet(u"")
        self.doubleSpinBox_Hp_Jan.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_Hp_Jan.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_Hp_Jan.setMinimum(0.000000000000000)
        self.doubleSpinBox_Hp_Jan.setMaximum(1000000.000000000000000)
        self.doubleSpinBox_Hp_Jan.setValue(160.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_Hp_Jan, 2, 1, 1, 1)

        self.label_Sep = QLabel(self.frame_thermal_demand)
        self.label_Sep.setObjectName(u"label_Sep")

        self.gridLayout_2.addWidget(self.label_Sep, 10, 0, 1, 1)

        self.label_Unit_HL = QLabel(self.frame_thermal_demand)
        self.label_Unit_HL.setObjectName(u"label_Unit_HL")

        self.gridLayout_2.addWidget(self.label_Unit_HL, 1, 3, 1, 1)

        self.label_Apr = QLabel(self.frame_thermal_demand)
        self.label_Apr.setObjectName(u"label_Apr")

        self.gridLayout_2.addWidget(self.label_Apr, 5, 0, 1, 1)

        self.doubleSpinBox_Cp_Jan = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_Cp_Jan.setObjectName(u"doubleSpinBox_Cp_Jan")
        self.doubleSpinBox_Cp_Jan.setStyleSheet(u"")
        self.doubleSpinBox_Cp_Jan.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_Cp_Jan.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_Cp_Jan.setMinimum(0.000000000000000)
        self.doubleSpinBox_Cp_Jan.setMaximum(1000000.000000000000000)
        self.doubleSpinBox_Cp_Jan.setValue(0.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_Cp_Jan, 2, 2, 1, 1)

        self.doubleSpinBox_Hp_Feb = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_Hp_Feb.setObjectName(u"doubleSpinBox_Hp_Feb")
        self.doubleSpinBox_Hp_Feb.setStyleSheet(u"")
        self.doubleSpinBox_Hp_Feb.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_Hp_Feb.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_Hp_Feb.setMinimum(0.000000000000000)
        self.doubleSpinBox_Hp_Feb.setMaximum(1000000.000000000000000)
        self.doubleSpinBox_Hp_Feb.setValue(142.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_Hp_Feb, 3, 1, 1, 1)

        self.label_Unit_pC = QLabel(self.frame_thermal_demand)
        self.label_Unit_pC.setObjectName(u"label_Unit_pC")

        self.gridLayout_2.addWidget(self.label_Unit_pC, 1, 2, 1, 1)

        self.doubleSpinBox_Hp_May = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_Hp_May.setObjectName(u"doubleSpinBox_Hp_May")
        self.doubleSpinBox_Hp_May.setStyleSheet(u"")
        self.doubleSpinBox_Hp_May.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_Hp_May.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_Hp_May.setMinimum(0.000000000000000)
        self.doubleSpinBox_Hp_May.setMaximum(1000000.000000000000000)
        self.doubleSpinBox_Hp_May.setValue(0.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_Hp_May, 6, 1, 1, 1)

        self.label_Jul = QLabel(self.frame_thermal_demand)
        self.label_Jul.setObjectName(u"label_Jul")

        self.gridLayout_2.addWidget(self.label_Jul, 8, 0, 1, 1)

        self.label_Mar = QLabel(self.frame_thermal_demand)
        self.label_Mar.setObjectName(u"label_Mar")

        self.gridLayout_2.addWidget(self.label_Mar, 4, 0, 1, 1)

        self.label_Feb = QLabel(self.frame_thermal_demand)
        self.label_Feb.setObjectName(u"label_Feb")
        self.label_Feb.setMinimumSize(QSize(50, 0))

        self.gridLayout_2.addWidget(self.label_Feb, 3, 0, 1, 1)

        self.doubleSpinBox_Hp_Mar = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_Hp_Mar.setObjectName(u"doubleSpinBox_Hp_Mar")
        self.doubleSpinBox_Hp_Mar.setStyleSheet(u"")
        self.doubleSpinBox_Hp_Mar.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_Hp_Mar.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_Hp_Mar.setMinimum(0.000000000000000)
        self.doubleSpinBox_Hp_Mar.setMaximum(1000000.000000000000000)
        self.doubleSpinBox_Hp_Mar.setValue(102.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_Hp_Mar, 4, 1, 1, 1)

        self.doubleSpinBox_Cp_Feb = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_Cp_Feb.setObjectName(u"doubleSpinBox_Cp_Feb")
        self.doubleSpinBox_Cp_Feb.setStyleSheet(u"")
        self.doubleSpinBox_Cp_Feb.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_Cp_Feb.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_Cp_Feb.setMinimum(0.000000000000000)
        self.doubleSpinBox_Cp_Feb.setMaximum(1000000.000000000000000)
        self.doubleSpinBox_Cp_Feb.setValue(0.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_Cp_Feb, 3, 2, 1, 1)

        self.doubleSpinBox_Hp_Apr = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_Hp_Apr.setObjectName(u"doubleSpinBox_Hp_Apr")
        self.doubleSpinBox_Hp_Apr.setStyleSheet(u"")
        self.doubleSpinBox_Hp_Apr.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_Hp_Apr.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_Hp_Apr.setMinimum(0.000000000000000)
        self.doubleSpinBox_Hp_Apr.setMaximum(1000000.000000000000000)
        self.doubleSpinBox_Hp_Apr.setValue(55.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_Hp_Apr, 5, 1, 1, 1)

        self.label_Dec = QLabel(self.frame_thermal_demand)
        self.label_Dec.setObjectName(u"label_Dec")

        self.gridLayout_2.addWidget(self.label_Dec, 13, 0, 1, 1)

        self.doubleSpinBox_Cp_May = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_Cp_May.setObjectName(u"doubleSpinBox_Cp_May")
        self.doubleSpinBox_Cp_May.setStyleSheet(u"")
        self.doubleSpinBox_Cp_May.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_Cp_May.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_Cp_May.setMinimum(0.000000000000000)
        self.doubleSpinBox_Cp_May.setMaximum(1000000.000000000000000)
        self.doubleSpinBox_Cp_May.setValue(133.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_Cp_May, 6, 2, 1, 1)

        self.label_HL = QLabel(self.frame_thermal_demand)
        self.label_HL.setObjectName(u"label_HL")

        self.gridLayout_2.addWidget(self.label_HL, 0, 3, 1, 1)

        self.doubleSpinBox_Cp_Apr = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_Cp_Apr.setObjectName(u"doubleSpinBox_Cp_Apr")
        self.doubleSpinBox_Cp_Apr.setStyleSheet(u"")
        self.doubleSpinBox_Cp_Apr.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_Cp_Apr.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_Cp_Apr.setMinimum(0.000000000000000)
        self.doubleSpinBox_Cp_Apr.setMaximum(1000000.000000000000000)
        self.doubleSpinBox_Cp_Apr.setValue(69.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_Cp_Apr, 5, 2, 1, 1)

        self.doubleSpinBox_CL_Mar = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_CL_Mar.setObjectName(u"doubleSpinBox_CL_Mar")
        self.doubleSpinBox_CL_Mar.setStyleSheet(u"")
        self.doubleSpinBox_CL_Mar.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_CL_Mar.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_CL_Mar.setDecimals(0)
        self.doubleSpinBox_CL_Mar.setMinimum(0.000000000000000)
        self.doubleSpinBox_CL_Mar.setMaximum(10000000000.000000000000000)
        self.doubleSpinBox_CL_Mar.setValue(8000.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_CL_Mar, 4, 4, 1, 1)

        self.doubleSpinBox_CL_May = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_CL_May.setObjectName(u"doubleSpinBox_CL_May")
        self.doubleSpinBox_CL_May.setStyleSheet(u"")
        self.doubleSpinBox_CL_May.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_CL_May.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_CL_May.setDecimals(0)
        self.doubleSpinBox_CL_May.setMinimum(0.000000000000000)
        self.doubleSpinBox_CL_May.setMaximum(10000000000.000000000000000)
        self.doubleSpinBox_CL_May.setValue(12000.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_CL_May, 6, 4, 1, 1)

        self.doubleSpinBox_HL_Jun = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_HL_Jun.setObjectName(u"doubleSpinBox_HL_Jun")
        self.doubleSpinBox_HL_Jun.setStyleSheet(u"")
        self.doubleSpinBox_HL_Jun.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_HL_Jun.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_HL_Jun.setDecimals(0)
        self.doubleSpinBox_HL_Jun.setMinimum(0.000000000000000)
        self.doubleSpinBox_HL_Jun.setMaximum(10000000000.000000000000000)
        self.doubleSpinBox_HL_Jun.setValue(0.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_HL_Jun, 7, 3, 1, 1)

        self.label_Jun = QLabel(self.frame_thermal_demand)
        self.label_Jun.setObjectName(u"label_Jun")

        self.gridLayout_2.addWidget(self.label_Jun, 7, 0, 1, 1)

        self.label_CL = QLabel(self.frame_thermal_demand)
        self.label_CL.setObjectName(u"label_CL")

        self.gridLayout_2.addWidget(self.label_CL, 0, 4, 1, 1)

        self.label_May = QLabel(self.frame_thermal_demand)
        self.label_May.setObjectName(u"label_May")

        self.gridLayout_2.addWidget(self.label_May, 6, 0, 1, 1)

        self.label_Unit_CL = QLabel(self.frame_thermal_demand)
        self.label_Unit_CL.setObjectName(u"label_Unit_CL")

        self.gridLayout_2.addWidget(self.label_Unit_CL, 1, 4, 1, 1)

        self.doubleSpinBox_Cp_Mar = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_Cp_Mar.setObjectName(u"doubleSpinBox_Cp_Mar")
        self.doubleSpinBox_Cp_Mar.setStyleSheet(u"")
        self.doubleSpinBox_Cp_Mar.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_Cp_Mar.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_Cp_Mar.setMinimum(0.000000000000000)
        self.doubleSpinBox_Cp_Mar.setMaximum(1000000.000000000000000)
        self.doubleSpinBox_Cp_Mar.setValue(34.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_Cp_Mar, 4, 2, 1, 1)

        self.label_Nov = QLabel(self.frame_thermal_demand)
        self.label_Nov.setObjectName(u"label_Nov")

        self.gridLayout_2.addWidget(self.label_Nov, 12, 0, 1, 1)

        self.doubleSpinBox_HL_Jan = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_HL_Jan.setObjectName(u"doubleSpinBox_HL_Jan")
        self.doubleSpinBox_HL_Jan.setStyleSheet(u"")
        self.doubleSpinBox_HL_Jan.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_HL_Jan.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_HL_Jan.setDecimals(0)
        self.doubleSpinBox_HL_Jan.setMinimum(0.000000000000000)
        self.doubleSpinBox_HL_Jan.setMaximum(10000000000.000000000000000)
        self.doubleSpinBox_HL_Jan.setValue(46500.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_HL_Jan, 2, 3, 1, 1)

        self.doubleSpinBox_HL_Mar = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_HL_Mar.setObjectName(u"doubleSpinBox_HL_Mar")
        self.doubleSpinBox_HL_Mar.setStyleSheet(u"")
        self.doubleSpinBox_HL_Mar.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_HL_Mar.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_HL_Mar.setDecimals(0)
        self.doubleSpinBox_HL_Mar.setMinimum(0.000000000000000)
        self.doubleSpinBox_HL_Mar.setMaximum(10000000000.000000000000000)
        self.doubleSpinBox_HL_Mar.setValue(37500.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_HL_Mar, 4, 3, 1, 1)

        self.doubleSpinBox_HL_May = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_HL_May.setObjectName(u"doubleSpinBox_HL_May")
        self.doubleSpinBox_HL_May.setStyleSheet(u"")
        self.doubleSpinBox_HL_May.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_HL_May.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_HL_May.setDecimals(0)
        self.doubleSpinBox_HL_May.setMinimum(0.000000000000000)
        self.doubleSpinBox_HL_May.setMaximum(10000000000.000000000000000)
        self.doubleSpinBox_HL_May.setValue(19200.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_HL_May, 6, 3, 1, 1)

        self.doubleSpinBox_CL_Jan = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_CL_Jan.setObjectName(u"doubleSpinBox_CL_Jan")
        self.doubleSpinBox_CL_Jan.setStyleSheet(u"")
        self.doubleSpinBox_CL_Jan.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_CL_Jan.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_CL_Jan.setDecimals(0)
        self.doubleSpinBox_CL_Jan.setMinimum(0.000000000000000)
        self.doubleSpinBox_CL_Jan.setMaximum(10000000000.000000000000000)
        self.doubleSpinBox_CL_Jan.setValue(4000.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_CL_Jan, 2, 4, 1, 1)

        self.doubleSpinBox_HL_Feb = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_HL_Feb.setObjectName(u"doubleSpinBox_HL_Feb")
        self.doubleSpinBox_HL_Feb.setStyleSheet(u"")
        self.doubleSpinBox_HL_Feb.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_HL_Feb.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_HL_Feb.setDecimals(0)
        self.doubleSpinBox_HL_Feb.setMinimum(0.000000000000000)
        self.doubleSpinBox_HL_Feb.setMaximum(10000000000.000000000000000)
        self.doubleSpinBox_HL_Feb.setValue(44400.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_HL_Feb, 3, 3, 1, 1)

        self.doubleSpinBox_CL_Apr = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_CL_Apr.setObjectName(u"doubleSpinBox_CL_Apr")
        self.doubleSpinBox_CL_Apr.setStyleSheet(u"")
        self.doubleSpinBox_CL_Apr.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_CL_Apr.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_CL_Apr.setDecimals(0)
        self.doubleSpinBox_CL_Apr.setMinimum(0.000000000000000)
        self.doubleSpinBox_CL_Apr.setMaximum(10000000000.000000000000000)
        self.doubleSpinBox_CL_Apr.setValue(8000.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_CL_Apr, 5, 4, 1, 1)

        self.doubleSpinBox_HL_Apr = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_HL_Apr.setObjectName(u"doubleSpinBox_HL_Apr")
        self.doubleSpinBox_HL_Apr.setStyleSheet(u"")
        self.doubleSpinBox_HL_Apr.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_HL_Apr.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_HL_Apr.setDecimals(0)
        self.doubleSpinBox_HL_Apr.setMinimum(0.000000000000000)
        self.doubleSpinBox_HL_Apr.setMaximum(10000000000.000000000000000)
        self.doubleSpinBox_HL_Apr.setValue(29700.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_HL_Apr, 5, 3, 1, 1)

        self.doubleSpinBox_CL_Feb = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_CL_Feb.setObjectName(u"doubleSpinBox_CL_Feb")
        self.doubleSpinBox_CL_Feb.setStyleSheet(u"")
        self.doubleSpinBox_CL_Feb.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_CL_Feb.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_CL_Feb.setDecimals(0)
        self.doubleSpinBox_CL_Feb.setMinimum(0.000000000000000)
        self.doubleSpinBox_CL_Feb.setMaximum(10000000000.000000000000000)
        self.doubleSpinBox_CL_Feb.setValue(8000.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_CL_Feb, 3, 4, 1, 1)

        self.doubleSpinBox_HL_Jul = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_HL_Jul.setObjectName(u"doubleSpinBox_HL_Jul")
        self.doubleSpinBox_HL_Jul.setStyleSheet(u"")
        self.doubleSpinBox_HL_Jul.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_HL_Jul.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_HL_Jul.setDecimals(0)
        self.doubleSpinBox_HL_Jul.setMinimum(0.000000000000000)
        self.doubleSpinBox_HL_Jul.setMaximum(10000000000.000000000000000)
        self.doubleSpinBox_HL_Jul.setValue(0.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_HL_Jul, 8, 3, 1, 1)

        self.doubleSpinBox_CL_Jun = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_CL_Jun.setObjectName(u"doubleSpinBox_CL_Jun")
        self.doubleSpinBox_CL_Jun.setStyleSheet(u"")
        self.doubleSpinBox_CL_Jun.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_CL_Jun.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_CL_Jun.setDecimals(0)
        self.doubleSpinBox_CL_Jun.setMinimum(0.000000000000000)
        self.doubleSpinBox_CL_Jun.setMaximum(10000000000.000000000000000)
        self.doubleSpinBox_CL_Jun.setValue(16000.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_CL_Jun, 7, 4, 1, 1)

        self.doubleSpinBox_CL_Aug = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_CL_Aug.setObjectName(u"doubleSpinBox_CL_Aug")
        self.doubleSpinBox_CL_Aug.setStyleSheet(u"")
        self.doubleSpinBox_CL_Aug.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_CL_Aug.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_CL_Aug.setDecimals(0)
        self.doubleSpinBox_CL_Aug.setMinimum(0.000000000000000)
        self.doubleSpinBox_CL_Aug.setMaximum(10000000000.000000000000000)
        self.doubleSpinBox_CL_Aug.setValue(32000.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_CL_Aug, 9, 4, 1, 1)

        self.doubleSpinBox_HL_Aug = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_HL_Aug.setObjectName(u"doubleSpinBox_HL_Aug")
        self.doubleSpinBox_HL_Aug.setStyleSheet(u"")
        self.doubleSpinBox_HL_Aug.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_HL_Aug.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_HL_Aug.setDecimals(0)
        self.doubleSpinBox_HL_Aug.setMinimum(0.000000000000000)
        self.doubleSpinBox_HL_Aug.setMaximum(10000000000.000000000000000)
        self.doubleSpinBox_HL_Aug.setValue(0.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_HL_Aug, 9, 3, 1, 1)

        self.doubleSpinBox_CL_Jul = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_CL_Jul.setObjectName(u"doubleSpinBox_CL_Jul")
        self.doubleSpinBox_CL_Jul.setStyleSheet(u"")
        self.doubleSpinBox_CL_Jul.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_CL_Jul.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_CL_Jul.setDecimals(0)
        self.doubleSpinBox_CL_Jul.setMinimum(0.000000000000000)
        self.doubleSpinBox_CL_Jul.setMaximum(10000000000.000000000000000)
        self.doubleSpinBox_CL_Jul.setValue(32000.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_CL_Jul, 8, 4, 1, 1)

        self.doubleSpinBox_CL_Sep = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_CL_Sep.setObjectName(u"doubleSpinBox_CL_Sep")
        self.doubleSpinBox_CL_Sep.setStyleSheet(u"")
        self.doubleSpinBox_CL_Sep.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_CL_Sep.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_CL_Sep.setDecimals(0)
        self.doubleSpinBox_CL_Sep.setMinimum(0.000000000000000)
        self.doubleSpinBox_CL_Sep.setMaximum(10000000000.000000000000000)
        self.doubleSpinBox_CL_Sep.setValue(16000.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_CL_Sep, 10, 4, 1, 1)

        self.doubleSpinBox_HL_Sep = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_HL_Sep.setObjectName(u"doubleSpinBox_HL_Sep")
        self.doubleSpinBox_HL_Sep.setStyleSheet(u"")
        self.doubleSpinBox_HL_Sep.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_HL_Sep.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_HL_Sep.setDecimals(0)
        self.doubleSpinBox_HL_Sep.setMinimum(0.000000000000000)
        self.doubleSpinBox_HL_Sep.setMaximum(10000000000.000000000000000)
        self.doubleSpinBox_HL_Sep.setValue(18300.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_HL_Sep, 10, 3, 1, 1)

        self.doubleSpinBox_HL_Oct = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_HL_Oct.setObjectName(u"doubleSpinBox_HL_Oct")
        self.doubleSpinBox_HL_Oct.setStyleSheet(u"")
        self.doubleSpinBox_HL_Oct.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_HL_Oct.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_HL_Oct.setDecimals(0)
        self.doubleSpinBox_HL_Oct.setMinimum(0.000000000000000)
        self.doubleSpinBox_HL_Oct.setMaximum(10000000000.000000000000000)
        self.doubleSpinBox_HL_Oct.setValue(26100.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_HL_Oct, 11, 3, 1, 1)

        self.doubleSpinBox_CL_Oct = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_CL_Oct.setObjectName(u"doubleSpinBox_CL_Oct")
        self.doubleSpinBox_CL_Oct.setStyleSheet(u"")
        self.doubleSpinBox_CL_Oct.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_CL_Oct.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_CL_Oct.setDecimals(0)
        self.doubleSpinBox_CL_Oct.setMinimum(0.000000000000000)
        self.doubleSpinBox_CL_Oct.setMaximum(10000000000.000000000000000)
        self.doubleSpinBox_CL_Oct.setValue(12000.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_CL_Oct, 11, 4, 1, 1)

        self.doubleSpinBox_CL_Nov = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_CL_Nov.setObjectName(u"doubleSpinBox_CL_Nov")
        self.doubleSpinBox_CL_Nov.setStyleSheet(u"")
        self.doubleSpinBox_CL_Nov.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_CL_Nov.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_CL_Nov.setDecimals(0)
        self.doubleSpinBox_CL_Nov.setMinimum(0.000000000000000)
        self.doubleSpinBox_CL_Nov.setMaximum(10000000000.000000000000000)
        self.doubleSpinBox_CL_Nov.setValue(8000.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_CL_Nov, 12, 4, 1, 1)

        self.doubleSpinBox_HL_Dec = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_HL_Dec.setObjectName(u"doubleSpinBox_HL_Dec")
        self.doubleSpinBox_HL_Dec.setStyleSheet(u"")
        self.doubleSpinBox_HL_Dec.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_HL_Dec.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_HL_Dec.setDecimals(0)
        self.doubleSpinBox_HL_Dec.setMinimum(0.000000000000000)
        self.doubleSpinBox_HL_Dec.setMaximum(10000000000.000000000000000)
        self.doubleSpinBox_HL_Dec.setValue(43200.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_HL_Dec, 13, 3, 1, 1)

        self.doubleSpinBox_HL_Nov = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_HL_Nov.setObjectName(u"doubleSpinBox_HL_Nov")
        self.doubleSpinBox_HL_Nov.setStyleSheet(u"")
        self.doubleSpinBox_HL_Nov.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_HL_Nov.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_HL_Nov.setDecimals(0)
        self.doubleSpinBox_HL_Nov.setMinimum(0.000000000000000)
        self.doubleSpinBox_HL_Nov.setMaximum(10000000000.000000000000000)
        self.doubleSpinBox_HL_Nov.setValue(35100.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_HL_Nov, 12, 3, 1, 1)

        self.doubleSpinBox_Cp_Jun = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_Cp_Jun.setObjectName(u"doubleSpinBox_Cp_Jun")
        self.doubleSpinBox_Cp_Jun.setStyleSheet(u"")
        self.doubleSpinBox_Cp_Jun.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_Cp_Jun.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_Cp_Jun.setMinimum(0.000000000000000)
        self.doubleSpinBox_Cp_Jun.setMaximum(1000000.000000000000000)
        self.doubleSpinBox_Cp_Jun.setValue(187.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_Cp_Jun, 7, 2, 1, 1)

        self.doubleSpinBox_CL_Dec = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_CL_Dec.setObjectName(u"doubleSpinBox_CL_Dec")
        self.doubleSpinBox_CL_Dec.setStyleSheet(u"")
        self.doubleSpinBox_CL_Dec.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_CL_Dec.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_CL_Dec.setDecimals(0)
        self.doubleSpinBox_CL_Dec.setMinimum(0.000000000000000)
        self.doubleSpinBox_CL_Dec.setMaximum(10000000000.000000000000000)
        self.doubleSpinBox_CL_Dec.setValue(4000.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_CL_Dec, 13, 4, 1, 1)

        self.doubleSpinBox_Hp_Jul = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_Hp_Jul.setObjectName(u"doubleSpinBox_Hp_Jul")
        self.doubleSpinBox_Hp_Jul.setStyleSheet(u"")
        self.doubleSpinBox_Hp_Jul.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_Hp_Jul.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_Hp_Jul.setMinimum(0.000000000000000)
        self.doubleSpinBox_Hp_Jul.setMaximum(1000000.000000000000000)
        self.doubleSpinBox_Hp_Jul.setValue(0.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_Hp_Jul, 8, 1, 1, 1)

        self.doubleSpinBox_Hp_Jun = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_Hp_Jun.setObjectName(u"doubleSpinBox_Hp_Jun")
        self.doubleSpinBox_Hp_Jun.setStyleSheet(u"")
        self.doubleSpinBox_Hp_Jun.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_Hp_Jun.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_Hp_Jun.setMinimum(0.000000000000000)
        self.doubleSpinBox_Hp_Jun.setMaximum(1000000.000000000000000)
        self.doubleSpinBox_Hp_Jun.setValue(0.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_Hp_Jun, 7, 1, 1, 1)

        self.doubleSpinBox_Cp_Jul = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_Cp_Jul.setObjectName(u"doubleSpinBox_Cp_Jul")
        self.doubleSpinBox_Cp_Jul.setStyleSheet(u"")
        self.doubleSpinBox_Cp_Jul.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_Cp_Jul.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_Cp_Jul.setMinimum(0.000000000000000)
        self.doubleSpinBox_Cp_Jul.setMaximum(1000000.000000000000000)
        self.doubleSpinBox_Cp_Jul.setValue(213.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_Cp_Jul, 8, 2, 1, 1)

        self.doubleSpinBox_Hp_Sep = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_Hp_Sep.setObjectName(u"doubleSpinBox_Hp_Sep")
        self.doubleSpinBox_Hp_Sep.setStyleSheet(u"")
        self.doubleSpinBox_Hp_Sep.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_Hp_Sep.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_Hp_Sep.setMinimum(0.000000000000000)
        self.doubleSpinBox_Hp_Sep.setMaximum(1000000.000000000000000)
        self.doubleSpinBox_Hp_Sep.setValue(40.399999999999999)

        self.gridLayout_2.addWidget(self.doubleSpinBox_Hp_Sep, 10, 1, 1, 1)

        self.doubleSpinBox_Hp_Aug = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_Hp_Aug.setObjectName(u"doubleSpinBox_Hp_Aug")
        self.doubleSpinBox_Hp_Aug.setStyleSheet(u"")
        self.doubleSpinBox_Hp_Aug.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_Hp_Aug.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_Hp_Aug.setMinimum(0.000000000000000)
        self.doubleSpinBox_Hp_Aug.setMaximum(1000000.000000000000000)
        self.doubleSpinBox_Hp_Aug.setValue(0.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_Hp_Aug, 9, 1, 1, 1)

        self.doubleSpinBox_Cp_Sep = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_Cp_Sep.setObjectName(u"doubleSpinBox_Cp_Sep")
        self.doubleSpinBox_Cp_Sep.setStyleSheet(u"")
        self.doubleSpinBox_Cp_Sep.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_Cp_Sep.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_Cp_Sep.setMinimum(0.000000000000000)
        self.doubleSpinBox_Cp_Sep.setMaximum(1000000.000000000000000)
        self.doubleSpinBox_Cp_Sep.setValue(160.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_Cp_Sep, 10, 2, 1, 1)

        self.doubleSpinBox_Hp_Oct = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_Hp_Oct.setObjectName(u"doubleSpinBox_Hp_Oct")
        self.doubleSpinBox_Hp_Oct.setStyleSheet(u"")
        self.doubleSpinBox_Hp_Oct.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_Hp_Oct.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_Hp_Oct.setMinimum(0.000000000000000)
        self.doubleSpinBox_Hp_Oct.setMaximum(1000000.000000000000000)
        self.doubleSpinBox_Hp_Oct.setValue(85.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_Hp_Oct, 11, 1, 1, 1)

        self.doubleSpinBox_Cp_Aug = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_Cp_Aug.setObjectName(u"doubleSpinBox_Cp_Aug")
        self.doubleSpinBox_Cp_Aug.setStyleSheet(u"")
        self.doubleSpinBox_Cp_Aug.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_Cp_Aug.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_Cp_Aug.setMinimum(0.000000000000000)
        self.doubleSpinBox_Cp_Aug.setMaximum(1000000.000000000000000)
        self.doubleSpinBox_Cp_Aug.setValue(240.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_Cp_Aug, 9, 2, 1, 1)

        self.doubleSpinBox_Hp_Nov = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_Hp_Nov.setObjectName(u"doubleSpinBox_Hp_Nov")
        self.doubleSpinBox_Hp_Nov.setStyleSheet(u"")
        self.doubleSpinBox_Hp_Nov.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_Hp_Nov.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_Hp_Nov.setMinimum(0.000000000000000)
        self.doubleSpinBox_Hp_Nov.setMaximum(1000000.000000000000000)
        self.doubleSpinBox_Hp_Nov.setValue(119.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_Hp_Nov, 12, 1, 1, 1)

        self.doubleSpinBox_Cp_Oct = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_Cp_Oct.setObjectName(u"doubleSpinBox_Cp_Oct")
        self.doubleSpinBox_Cp_Oct.setStyleSheet(u"")
        self.doubleSpinBox_Cp_Oct.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_Cp_Oct.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_Cp_Oct.setMinimum(0.000000000000000)
        self.doubleSpinBox_Cp_Oct.setMaximum(1000000.000000000000000)
        self.doubleSpinBox_Cp_Oct.setValue(37.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_Cp_Oct, 11, 2, 1, 1)

        self.doubleSpinBox_Hp_Dec = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_Hp_Dec.setObjectName(u"doubleSpinBox_Hp_Dec")
        self.doubleSpinBox_Hp_Dec.setStyleSheet(u"")
        self.doubleSpinBox_Hp_Dec.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_Hp_Dec.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_Hp_Dec.setMinimum(0.000000000000000)
        self.doubleSpinBox_Hp_Dec.setMaximum(1000000.000000000000000)
        self.doubleSpinBox_Hp_Dec.setValue(136.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_Hp_Dec, 13, 1, 1, 1)

        self.doubleSpinBox_Cp_Nov = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_Cp_Nov.setObjectName(u"doubleSpinBox_Cp_Nov")
        self.doubleSpinBox_Cp_Nov.setStyleSheet(u"")
        self.doubleSpinBox_Cp_Nov.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_Cp_Nov.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_Cp_Nov.setMinimum(0.000000000000000)
        self.doubleSpinBox_Cp_Nov.setMaximum(1000000.000000000000000)
        self.doubleSpinBox_Cp_Nov.setValue(0.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_Cp_Nov, 12, 2, 1, 1)

        self.doubleSpinBox_Cp_Dec = QDoubleSpinBox(self.frame_thermal_demand)
        self.doubleSpinBox_Cp_Dec.setObjectName(u"doubleSpinBox_Cp_Dec")
        self.doubleSpinBox_Cp_Dec.setStyleSheet(u"")
        self.doubleSpinBox_Cp_Dec.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_Cp_Dec.setProperty("showGroupSeparator", True)
        self.doubleSpinBox_Cp_Dec.setMinimum(0.000000000000000)
        self.doubleSpinBox_Cp_Dec.setMaximum(1000000.000000000000000)
        self.doubleSpinBox_Cp_Dec.setValue(0.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_Cp_Dec, 13, 2, 1, 1)


        self.verticalLayout_11.addLayout(self.gridLayout_2)

        self.horizontalLayout_21 = QHBoxLayout()
        self.horizontalLayout_21.setObjectName(u"horizontalLayout_21")
        self.horizontalLayout_17 = QHBoxLayout()
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.label_UnitPeak = QLabel(self.frame_thermal_demand)
        self.label_UnitPeak.setObjectName(u"label_UnitPeak")
        self.label_UnitPeak.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_17.addWidget(self.label_UnitPeak)

        self.comboBox_Unit_peak = QComboBox(self.frame_thermal_demand)
        self.comboBox_Unit_peak.addItem("")
        self.comboBox_Unit_peak.addItem("")
        self.comboBox_Unit_peak.addItem("")
        self.comboBox_Unit_peak.setObjectName(u"comboBox_Unit_peak")
        self.comboBox_Unit_peak.setEnabled(True)
        self.comboBox_Unit_peak.setMinimumSize(QSize(60, 0))
        self.comboBox_Unit_peak.setMaximumSize(QSize(120, 16777215))
        self.comboBox_Unit_peak.setStyleSheet(u"QFrame {\n"
"	border: 1px solid rgb(255, 255, 255);\n"
"	border-bottom-left-radius: 0px;\n"
"	border-bottom-right-radius: 0px;\n"
"}")
        self.comboBox_Unit_peak.setEditable(False)
        self.comboBox_Unit_peak.setSizeAdjustPolicy(QComboBox.AdjustToContentsOnFirstShow)
        self.comboBox_Unit_peak.setFrame(True)

        self.horizontalLayout_17.addWidget(self.comboBox_Unit_peak)


        self.horizontalLayout_21.addLayout(self.horizontalLayout_17)

        self.horizontalLayout_18 = QHBoxLayout()
        self.horizontalLayout_18.setSpacing(10)
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.label_UnitLoad = QLabel(self.frame_thermal_demand)
        self.label_UnitLoad.setObjectName(u"label_UnitLoad")
        self.label_UnitLoad.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_18.addWidget(self.label_UnitLoad)

        self.comboBox_Unit_Load = QComboBox(self.frame_thermal_demand)
        self.comboBox_Unit_Load.addItem("")
        self.comboBox_Unit_Load.addItem("")
        self.comboBox_Unit_Load.addItem("")
        self.comboBox_Unit_Load.setObjectName(u"comboBox_Unit_Load")
        self.comboBox_Unit_Load.setEnabled(True)
        self.comboBox_Unit_Load.setMinimumSize(QSize(80, 0))
        self.comboBox_Unit_Load.setMaximumSize(QSize(120, 16777215))
        self.comboBox_Unit_Load.setStyleSheet(u"QFrame {\n"
"	border: 1px solid rgb(255, 255, 255);\n"
"	border-bottom-left-radius: 0px;\n"
"	border-bottom-right-radius: 0px;\n"
"}")
        self.comboBox_Unit_Load.setEditable(False)
        self.comboBox_Unit_Load.setMaxVisibleItems(10)
        self.comboBox_Unit_Load.setSizeAdjustPolicy(QComboBox.AdjustToContentsOnFirstShow)
        self.comboBox_Unit_Load.setFrame(True)

        self.horizontalLayout_18.addWidget(self.comboBox_Unit_Load)


        self.horizontalLayout_21.addLayout(self.horizontalLayout_18)

        self.horizontalSpacer_17 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_21.addItem(self.horizontalSpacer_17)

        self.pushButton_Unit = QPushButton(self.frame_thermal_demand)
        self.pushButton_Unit.setObjectName(u"pushButton_Unit")
        self.pushButton_Unit.setMinimumSize(QSize(40, 30))
        self.pushButton_Unit.setMaximumSize(QSize(40, 30))
        self.pushButton_Unit.setLayoutDirection(Qt.LeftToRight)
        self.pushButton_Unit.setStyleSheet(u"")

        self.horizontalLayout_21.addWidget(self.pushButton_Unit)


        self.verticalLayout_11.addLayout(self.horizontalLayout_21)


        self.verticalLayout_20.addWidget(self.frame_thermal_demand)

        self.label_51 = QLabel(self.scrollAreaWidgetContents)
        self.label_51.setObjectName(u"label_51")
        self.label_51.setMinimumSize(QSize(0, 10))
        self.label_51.setMaximumSize(QSize(16777215, 10))

        self.verticalLayout_20.addWidget(self.label_51)

        self.label_data_file = QLabel(self.scrollAreaWidgetContents)
        self.label_data_file.setObjectName(u"label_data_file")
        self.label_data_file.setStyleSheet(u"QLabel {\n"
"        qproperty-alignment: AlignCenter;\n"
"	border: 1px solid  rgb(84, 188, 235);\n"
"	border-top-left-radius: 15px;\n"
"	border-top-right-radius: 15px;\n"
"	background-color:  rgb(84, 188, 235);\n"
"	padding: 5px 0px;\n"
"	color:  rgb(255, 255, 235);\n"
"font-weight:500;\n"
"}")

        self.verticalLayout_20.addWidget(self.label_data_file)

        self.frame_data_file = QFrame(self.scrollAreaWidgetContents)
        self.frame_data_file.setObjectName(u"frame_data_file")
        self.frame_data_file.setStyleSheet(u"QFrame {\n"
"	border: 1px solid #54bceb;\n"
"	border-bottom-left-radius: 15px;\n"
"	border-bottom-right-radius: 15px;\n"
"}\n"
"QLabel{border: 0px solid rgb(255,255,255);font: 12pt;}\n"
"")
        self.frame_data_file.setFrameShape(QFrame.StyledPanel)
        self.frame_data_file.setFrameShadow(QFrame.Raised)
        self.verticalLayout_12 = QVBoxLayout(self.frame_data_file)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.label_SeperatorDataFile = QLabel(self.frame_data_file)
        self.label_SeperatorDataFile.setObjectName(u"label_SeperatorDataFile")

        self.horizontalLayout_10.addWidget(self.label_SeperatorDataFile)

        self.horizontalSpacer_21 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_10.addItem(self.horizontalSpacer_21)

        self.comboBox_SeperatorDataFile = QComboBox(self.frame_data_file)
        self.comboBox_SeperatorDataFile.addItem("")
        self.comboBox_SeperatorDataFile.addItem("")
        self.comboBox_SeperatorDataFile.setObjectName(u"comboBox_SeperatorDataFile")
        self.comboBox_SeperatorDataFile.setMinimumSize(QSize(120, 0))
        self.comboBox_SeperatorDataFile.setStyleSheet(u"QFrame {\n"
"	border: 1px solid rgb(255, 255, 255);\n"
"	border-bottom-left-radius: 0px;\n"
"	border-bottom-right-radius: 0px;\n"
"}")
        self.comboBox_SeperatorDataFile.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.horizontalLayout_10.addWidget(self.comboBox_SeperatorDataFile)


        self.verticalLayout_12.addLayout(self.horizontalLayout_10)

        self.horizontalLayout_36 = QHBoxLayout()
        self.horizontalLayout_36.setObjectName(u"horizontalLayout_36")
        self.label_decimalDataFile = QLabel(self.frame_data_file)
        self.label_decimalDataFile.setObjectName(u"label_decimalDataFile")

        self.horizontalLayout_36.addWidget(self.label_decimalDataFile)

        self.horizontalSpacer_25 = QSpacerItem(477, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_36.addItem(self.horizontalSpacer_25)

        self.comboBox_decimalDataFile = QComboBox(self.frame_data_file)
        self.comboBox_decimalDataFile.addItem("")
        self.comboBox_decimalDataFile.addItem("")
        self.comboBox_decimalDataFile.setObjectName(u"comboBox_decimalDataFile")
        self.comboBox_decimalDataFile.setMinimumSize(QSize(120, 0))
        self.comboBox_decimalDataFile.setStyleSheet(u"QFrame {\n"
"	border: 1px solid rgb(255, 255, 255);\n"
"	border-bottom-left-radius: 0px;\n"
"	border-bottom-right-radius: 0px;\n"
"}")
        self.comboBox_decimalDataFile.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.horizontalLayout_36.addWidget(self.comboBox_decimalDataFile)


        self.verticalLayout_12.addLayout(self.horizontalLayout_36)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.label_Filename_2 = QLabel(self.frame_data_file)
        self.label_Filename_2.setObjectName(u"label_Filename_2")
        self.label_Filename_2.setStyleSheet(u"")

        self.horizontalLayout_12.addWidget(self.label_Filename_2)

        self.lineEdit_filename_data_file = QLineEdit(self.frame_data_file)
        self.lineEdit_filename_data_file.setObjectName(u"lineEdit_filename_data_file")
        self.lineEdit_filename_data_file.setMaximumSize(QSize(10000000, 25))
        self.lineEdit_filename_data_file.setStyleSheet(u"")

        self.horizontalLayout_12.addWidget(self.lineEdit_filename_data_file)

        self.pushButton_data_file_select = QPushButton(self.frame_data_file)
        self.pushButton_data_file_select.setObjectName(u"pushButton_data_file_select")
        self.pushButton_data_file_select.setMinimumSize(QSize(30, 30))
        self.pushButton_data_file_select.setMaximumSize(QSize(30, 30))
        self.pushButton_data_file_select.setStyleSheet(u"")

        self.horizontalLayout_12.addWidget(self.pushButton_data_file_select)


        self.verticalLayout_12.addLayout(self.horizontalLayout_12)

        self.horizontalLayout_33 = QHBoxLayout()
        self.horizontalLayout_33.setObjectName(u"horizontalLayout_33")
        self.frame_thermalDemands_2 = QFrame(self.frame_data_file)
        self.frame_thermalDemands_2.setObjectName(u"frame_thermalDemands_2")
        self.frame_thermalDemands_2.setStyleSheet(u"QFrame {\n"
"	border: 0px solid #54bceb;\n"
"	border-bottom-left-radius: 15px;\n"
"	border-bottom-right-radius: 15px;\n"
"}\n"
"QLabel{border: 0px solid rgb(255,255,255);font: 12pt;}\n"
"")
        self.frame_thermalDemands_2.setFrameShape(QFrame.NoFrame)
        self.frame_thermalDemands_2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_19 = QVBoxLayout(self.frame_thermalDemands_2)
        self.verticalLayout_19.setSpacing(0)
        self.verticalLayout_19.setObjectName(u"verticalLayout_19")
        self.verticalLayout_19.setContentsMargins(0, 0, 0, 0)
        self.frame_12 = QFrame(self.frame_thermalDemands_2)
        self.frame_12.setObjectName(u"frame_12")
        self.frame_12.setStyleSheet(u"QFrame {\n"
"	border: 0px solid #54bceb;\n"
"	border-bottom-left-radius: 15px;\n"
"	border-bottom-right-radius: 15px;\n"
"}\n"
"QLabel{border: 0px solid rgb(255,255,255);}\n"
"")
        self.frame_12.setFrameShape(QFrame.NoFrame)
        self.frame_12.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_20 = QHBoxLayout(self.frame_12)
        self.horizontalLayout_20.setSpacing(6)
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.horizontalLayout_20.setContentsMargins(0, 0, 0, 0)
        self.label_dataColumn_2 = QLabel(self.frame_12)
        self.label_dataColumn_2.setObjectName(u"label_dataColumn_2")
        self.label_dataColumn_2.setMinimumSize(QSize(0, 25))
        self.label_dataColumn_2.setMaximumSize(QSize(16777215, 40))
        self.label_dataColumn_2.setStyleSheet(u"")
        self.label_dataColumn_2.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_20.addWidget(self.label_dataColumn_2, 0, Qt.AlignLeft)

        self.comboBox_dataColumn_data_file = QComboBox(self.frame_12)
        self.comboBox_dataColumn_data_file.addItem("")
        self.comboBox_dataColumn_data_file.addItem("")
        self.comboBox_dataColumn_data_file.setObjectName(u"comboBox_dataColumn_data_file")
        self.comboBox_dataColumn_data_file.setMinimumSize(QSize(100, 30))
        self.comboBox_dataColumn_data_file.setMaximumSize(QSize(150, 40))
        self.comboBox_dataColumn_data_file.setStyleSheet(u"QFrame {\n"
"	border: 1px solid rgb(255, 255, 255);\n"
"	border-bottom-left-radius: 0px;\n"
"	border-bottom-right-radius: 0px;\n"
"}")
        self.comboBox_dataColumn_data_file.setEditable(False)
        self.comboBox_dataColumn_data_file.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)

        self.horizontalLayout_20.addWidget(self.comboBox_dataColumn_data_file)


        self.verticalLayout_19.addWidget(self.frame_12)


        self.horizontalLayout_33.addWidget(self.frame_thermalDemands_2)

        self.frame_heatingLoad_data_File = QFrame(self.frame_data_file)
        self.frame_heatingLoad_data_File.setObjectName(u"frame_heatingLoad_data_File")
        self.frame_heatingLoad_data_File.setMinimumSize(QSize(0, 25))
        self.frame_heatingLoad_data_File.setMaximumSize(QSize(1672341, 35))
        self.frame_heatingLoad_data_File.setStyleSheet(u"QFrame {\n"
"	border: 0px solid #54bceb;\n"
"	border-bottom-left-radius: 15px;\n"
"	border-bottom-right-radius: 15px;\n"
"}\n"
"QLabel{border: 0px solid rgb(255,255,255);}\n"
"")
        self.frame_heatingLoad_data_File.setFrameShape(QFrame.NoFrame)
        self.frame_heatingLoad_data_File.setFrameShadow(QFrame.Raised)
        self.frame_heatingLoad_data_File.setLineWidth(0)
        self.horizontalLayout_22 = QHBoxLayout(self.frame_heatingLoad_data_File)
        self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
        self.horizontalLayout_22.setContentsMargins(0, 0, 0, 0)
        self.label_HeatingLoadLine_2 = QLabel(self.frame_heatingLoad_data_File)
        self.label_HeatingLoadLine_2.setObjectName(u"label_HeatingLoadLine_2")
        self.label_HeatingLoadLine_2.setMinimumSize(QSize(0, 30))
        self.label_HeatingLoadLine_2.setMaximumSize(QSize(1672341, 30))
        self.label_HeatingLoadLine_2.setStyleSheet(u"")
        self.label_HeatingLoadLine_2.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.horizontalLayout_22.addWidget(self.label_HeatingLoadLine_2, 0, Qt.AlignRight)

        self.comboBox_heatingLoad_data_file = QComboBox(self.frame_heatingLoad_data_File)
        self.comboBox_heatingLoad_data_file.setObjectName(u"comboBox_heatingLoad_data_file")
        self.comboBox_heatingLoad_data_file.setMinimumSize(QSize(0, 30))
        self.comboBox_heatingLoad_data_file.setMaximumSize(QSize(150, 16777215))
        self.comboBox_heatingLoad_data_file.setStyleSheet(u"QFrame {\n"
"	border: 1px solid rgb(255, 255, 255);\n"
"	border-bottom-left-radius: 0px;\n"
"	border-bottom-right-radius: 0px;\n"
"}")

        self.horizontalLayout_22.addWidget(self.comboBox_heatingLoad_data_file)


        self.horizontalLayout_33.addWidget(self.frame_heatingLoad_data_File)

        self.frame_coolingLoad_data_file = QFrame(self.frame_data_file)
        self.frame_coolingLoad_data_file.setObjectName(u"frame_coolingLoad_data_file")
        self.frame_coolingLoad_data_file.setMinimumSize(QSize(0, 25))
        self.frame_coolingLoad_data_file.setMaximumSize(QSize(1672341, 35))
        self.frame_coolingLoad_data_file.setStyleSheet(u"QFrame {\n"
"	border: 0px solid #54bceb;\n"
"	border-bottom-left-radius: 15px;\n"
"	border-bottom-right-radius: 15px;\n"
"}\n"
"QLabel{border: 0px solid rgb(255,255,255);}\n"
"")
        self.frame_coolingLoad_data_file.setFrameShape(QFrame.NoFrame)
        self.frame_coolingLoad_data_file.setFrameShadow(QFrame.Raised)
        self.frame_coolingLoad_data_file.setLineWidth(0)
        self.horizontalLayout_25 = QHBoxLayout(self.frame_coolingLoad_data_file)
        self.horizontalLayout_25.setObjectName(u"horizontalLayout_25")
        self.horizontalLayout_25.setContentsMargins(0, 0, 0, 0)
        self.label_CoolingLoadLine_2 = QLabel(self.frame_coolingLoad_data_file)
        self.label_CoolingLoadLine_2.setObjectName(u"label_CoolingLoadLine_2")
        self.label_CoolingLoadLine_2.setMinimumSize(QSize(0, 30))
        self.label_CoolingLoadLine_2.setMaximumSize(QSize(1672341, 30))
        self.label_CoolingLoadLine_2.setStyleSheet(u"")
        self.label_CoolingLoadLine_2.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.horizontalLayout_25.addWidget(self.label_CoolingLoadLine_2)

        self.comboBox_coolingLoad_data_file = QComboBox(self.frame_coolingLoad_data_file)
        self.comboBox_coolingLoad_data_file.setObjectName(u"comboBox_coolingLoad_data_file")
        self.comboBox_coolingLoad_data_file.setMinimumSize(QSize(0, 30))
        self.comboBox_coolingLoad_data_file.setMaximumSize(QSize(150, 16777215))
        self.comboBox_coolingLoad_data_file.setStyleSheet(u"QFrame {\n"
"	border: 1px solid rgb(255, 255, 255);\n"
"	border-bottom-left-radius: 0px;\n"
"	border-bottom-right-radius: 0px;\n"
"}")

        self.horizontalLayout_25.addWidget(self.comboBox_coolingLoad_data_file)


        self.horizontalLayout_33.addWidget(self.frame_coolingLoad_data_file)

        self.frame_combined_data_file = QFrame(self.frame_data_file)
        self.frame_combined_data_file.setObjectName(u"frame_combined_data_file")
        self.frame_combined_data_file.setMinimumSize(QSize(0, 25))
        self.frame_combined_data_file.setMaximumSize(QSize(1672341, 35))
        self.frame_combined_data_file.setStyleSheet(u"QFrame {\n"
"	border: 0px solid #54bceb;\n"
"	border-bottom-left-radius: 15px;\n"
"	border-bottom-right-radius: 15px;\n"
"}\n"
"QLabel{border: 0px solid rgb(255,255,255);}\n"
"")
        self.frame_combined_data_file.setFrameShape(QFrame.NoFrame)
        self.frame_combined_data_file.setFrameShadow(QFrame.Raised)
        self.frame_combined_data_file.setLineWidth(0)
        self.horizontalLayout_34 = QHBoxLayout(self.frame_combined_data_file)
        self.horizontalLayout_34.setObjectName(u"horizontalLayout_34")
        self.horizontalLayout_34.setContentsMargins(0, 0, 0, 0)
        self.label_combined_2 = QLabel(self.frame_combined_data_file)
        self.label_combined_2.setObjectName(u"label_combined_2")
        self.label_combined_2.setMinimumSize(QSize(0, 30))
        self.label_combined_2.setMaximumSize(QSize(1672341, 30))
        self.label_combined_2.setStyleSheet(u"")
        self.label_combined_2.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.horizontalLayout_34.addWidget(self.label_combined_2)

        self.comboBox_combined_data_file = QComboBox(self.frame_combined_data_file)
        self.comboBox_combined_data_file.setObjectName(u"comboBox_combined_data_file")
        self.comboBox_combined_data_file.setMinimumSize(QSize(0, 30))
        self.comboBox_combined_data_file.setMaximumSize(QSize(150, 16777215))
        self.comboBox_combined_data_file.setStyleSheet(u"QFrame {\n"
"	border: 1px solid rgb(255, 255, 255);\n"
"	border-bottom-left-radius: 0px;\n"
"	border-bottom-right-radius: 0px;\n"
"}")

        self.horizontalLayout_34.addWidget(self.comboBox_combined_data_file)


        self.horizontalLayout_33.addWidget(self.frame_combined_data_file)


        self.verticalLayout_12.addLayout(self.horizontalLayout_33)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.label_DataUnit_2 = QLabel(self.frame_data_file)
        self.label_DataUnit_2.setObjectName(u"label_DataUnit_2")
        self.label_DataUnit_2.setStyleSheet(u"")

        self.horizontalLayout_9.addWidget(self.label_DataUnit_2)

        self.horizontalSpacer_20 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer_20)

        self.comboBox_dataUnit_data_file = QComboBox(self.frame_data_file)
        self.comboBox_dataUnit_data_file.addItem("")
        self.comboBox_dataUnit_data_file.addItem("")
        self.comboBox_dataUnit_data_file.addItem("")
        self.comboBox_dataUnit_data_file.setObjectName(u"comboBox_dataUnit_data_file")
        self.comboBox_dataUnit_data_file.setEnabled(True)
        self.comboBox_dataUnit_data_file.setMinimumSize(QSize(60, 30))
        self.comboBox_dataUnit_data_file.setMaximumSize(QSize(150, 16777215))
        self.comboBox_dataUnit_data_file.setStyleSheet(u"QFrame {\n"
"	border: 1px solid rgb(255, 255, 255);\n"
"	border-bottom-left-radius: 0px;\n"
"	border-bottom-right-radius: 0px;\n"
"}")
        self.comboBox_dataUnit_data_file.setEditable(False)
        self.comboBox_dataUnit_data_file.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.comboBox_dataUnit_data_file.setFrame(True)

        self.horizontalLayout_9.addWidget(self.comboBox_dataUnit_data_file)


        self.verticalLayout_12.addLayout(self.horizontalLayout_9)


        self.verticalLayout_20.addWidget(self.frame_data_file)

        self.label_43 = QLabel(self.scrollAreaWidgetContents)
        self.label_43.setObjectName(u"label_43")
        self.label_43.setMinimumSize(QSize(0, 10))
        self.label_43.setMaximumSize(QSize(16777215, 10))

        self.verticalLayout_20.addWidget(self.label_43)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_20.addItem(self.verticalSpacer_3)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.pushButton_PreviousThermal = QPushButton(self.scrollAreaWidgetContents)
        self.pushButton_PreviousThermal.setObjectName(u"pushButton_PreviousThermal")
        self.pushButton_PreviousThermal.setMinimumSize(QSize(0, 30))
        self.pushButton_PreviousThermal.setMaximumSize(QSize(16777215, 30))
        self.pushButton_PreviousThermal.setStyleSheet(u"")
        self.pushButton_PreviousThermal.setIcon(icon29)
        self.pushButton_PreviousThermal.setIconSize(QSize(20, 20))
        self.pushButton_PreviousThermal.setCheckable(False)

        self.horizontalLayout_5.addWidget(self.pushButton_PreviousThermal)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_5)


        self.verticalLayout_20.addLayout(self.horizontalLayout_5)

        self.scrollArea_thermal.setWidget(self.scrollAreaWidgetContents)
        self.label_ThermalDemandsTitle.raise_()
        self.label_Import.raise_()
        self.label_ThermalDemands.raise_()
        self.frame_thermal_demand.raise_()
        self.label_39.raise_()
        self.label_40.raise_()
        self.frame_import.raise_()
        self.label_43.raise_()
        self.frame_data_file.raise_()
        self.label_51.raise_()
        self.label_data_file.raise_()

        self.verticalLayout_2.addWidget(self.scrollArea_thermal)

        self.stackedWidget.addWidget(self.page_thermal)
        self.page_Results = QWidget()
        self.page_Results.setObjectName(u"page_Results")
        self.verticalLayout_6 = QVBoxLayout(self.page_Results)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.scrollArea_Res = QScrollArea(self.page_Results)
        self.scrollArea_Res.setObjectName(u"scrollArea_Res")
        self.scrollArea_Res.setFrameShape(QFrame.NoFrame)
        self.scrollArea_Res.setLineWidth(0)
        self.scrollArea_Res.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 367, 312))
        self.gridLayout_8 = QGridLayout(self.scrollAreaWidgetContents_2)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.gridLayout_8.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_6 = QGridLayout()
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.checkBox_Legend = QCheckBox(self.scrollAreaWidgetContents_2)
        self.checkBox_Legend.setObjectName(u"checkBox_Legend")
        self.checkBox_Legend.setMaximumSize(QSize(16777215, 20))
        self.checkBox_Legend.setChecked(True)
        self.checkBox_Legend.setTristate(False)

        self.gridLayout_6.addWidget(self.checkBox_Legend, 1, 0, 1, 1)

        self.label_Size = QLabel(self.scrollAreaWidgetContents_2)
        self.label_Size.setObjectName(u"label_Size")
        sizePolicy2.setHeightForWidth(self.label_Size.sizePolicy().hasHeightForWidth())
        self.label_Size.setSizePolicy(sizePolicy2)
        self.label_Size.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout_6.addWidget(self.label_Size, 0, 0, 1, 1)

        self.pushButton_SaveData = QPushButton(self.scrollAreaWidgetContents_2)
        self.pushButton_SaveData.setObjectName(u"pushButton_SaveData")
        self.pushButton_SaveData.setMinimumSize(QSize(150, 40))
        self.pushButton_SaveData.setMaximumSize(QSize(16777215, 40))
        icon31 = QIcon()
        icon31.addFile(u":/icons/icons/Save_Inv.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_SaveData.setIcon(icon31)
        self.pushButton_SaveData.setIconSize(QSize(24, 24))

        self.gridLayout_6.addWidget(self.pushButton_SaveData, 0, 2, 1, 1)

        self.pushButton_SaveFigure = QPushButton(self.scrollAreaWidgetContents_2)
        self.pushButton_SaveFigure.setObjectName(u"pushButton_SaveFigure")
        self.pushButton_SaveFigure.setMinimumSize(QSize(150, 40))
        self.pushButton_SaveFigure.setMaximumSize(QSize(16777215, 40))
        self.pushButton_SaveFigure.setStyleSheet(u"")
        self.pushButton_SaveFigure.setIcon(icon31)
        self.pushButton_SaveFigure.setIconSize(QSize(24, 24))

        self.gridLayout_6.addWidget(self.pushButton_SaveFigure, 1, 2, 1, 1)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_6.addItem(self.horizontalSpacer_8, 1, 1, 1, 1)

        self.label_WarningDepth = QLabel(self.scrollAreaWidgetContents_2)
        self.label_WarningDepth.setObjectName(u"label_WarningDepth")
        self.label_WarningDepth.setStyleSheet(u"color: rgb(255, 200, 87);")
        self.label_WarningDepth.setWordWrap(True)

        self.gridLayout_6.addWidget(self.label_WarningDepth, 0, 1, 1, 1)


        self.gridLayout_8.addLayout(self.gridLayout_6, 0, 0, 1, 1)

        self.scrollArea_Res.setWidget(self.scrollAreaWidgetContents_2)

        self.verticalLayout_6.addWidget(self.scrollArea_Res)

        self.stackedWidget.addWidget(self.page_Results)
        self.page_Settings = QWidget()
        self.page_Settings.setObjectName(u"page_Settings")
        self.verticalLayout_14 = QVBoxLayout(self.page_Settings)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.scrollArea = QScrollArea(self.page_Settings)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setLineWidth(0)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents_4 = QWidget()
        self.scrollAreaWidgetContents_4.setObjectName(u"scrollAreaWidgetContents_4")
        self.scrollAreaWidgetContents_4.setGeometry(QRect(0, 0, 881, 645))
        self.verticalLayout_18 = QVBoxLayout(self.scrollAreaWidgetContents_4)
        self.verticalLayout_18.setSpacing(0)
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.verticalLayout_18.setContentsMargins(0, 0, 0, 0)
        self.label_Settings = QLabel(self.scrollAreaWidgetContents_4)
        self.label_Settings.setObjectName(u"label_Settings")
        self.label_Settings.setStyleSheet(u"font: 63 16pt \"Lexend SemiBold\";")

        self.verticalLayout_18.addWidget(self.label_Settings)

        self.label_42 = QLabel(self.scrollAreaWidgetContents_4)
        self.label_42.setObjectName(u"label_42")
        self.label_42.setMinimumSize(QSize(0, 10))
        self.label_42.setMaximumSize(QSize(16777215, 10))

        self.verticalLayout_18.addWidget(self.label_42)

        self.label_Language_Head = QLabel(self.scrollAreaWidgetContents_4)
        self.label_Language_Head.setObjectName(u"label_Language_Head")
        self.label_Language_Head.setStyleSheet(u"QLabel {\n"
"        qproperty-alignment: AlignCenter;\n"
"	border: 1px solid  rgb(84, 188, 235);\n"
"	border-top-left-radius: 15px;\n"
"	border-top-right-radius: 15px;\n"
"	background-color:  rgb(84, 188, 235);\n"
"	padding: 5px 0px;\n"
"	color:  rgb(255, 255, 235);\n"
"font-weight:500;\n"
"}")

        self.verticalLayout_18.addWidget(self.label_Language_Head)

        self.frame_6 = QFrame(self.scrollAreaWidgetContents_4)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setStyleSheet(u"QFrame {\n"
"	border: 1px solid #54bceb;\n"
"	border-bottom-left-radius: 15px;\n"
"	border-bottom-right-radius: 15px;\n"
"}\n"
"QLabel{border: 0px solid rgb(255,255,255);}")
        self.frame_6.setFrameShape(QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_6 = QHBoxLayout(self.frame_6)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_Language = QLabel(self.frame_6)
        self.label_Language.setObjectName(u"label_Language")

        self.horizontalLayout_6.addWidget(self.label_Language)

        self.horizontalSpacer_7 = QSpacerItem(433, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_7)

        self.comboBox_Language = QComboBox(self.frame_6)
        self.comboBox_Language.setObjectName(u"comboBox_Language")
        self.comboBox_Language.setMinimumSize(QSize(150, 30))
        self.comboBox_Language.setStyleSheet(u"QFrame {\n"
"	border: 1px solid rgb(255, 255, 255);\n"
"	border-bottom-left-radius: 0px;\n"
"	border-bottom-right-radius: 0px;\n"
"}")

        self.horizontalLayout_6.addWidget(self.comboBox_Language)


        self.verticalLayout_18.addWidget(self.frame_6)

        self.label_50 = QLabel(self.scrollAreaWidgetContents_4)
        self.label_50.setObjectName(u"label_50")
        self.label_50.setMinimumSize(QSize(0, 6))
        self.label_50.setMaximumSize(QSize(16777215, 6))

        self.verticalLayout_18.addWidget(self.label_50)

        self.label_Scenario_Head = QLabel(self.scrollAreaWidgetContents_4)
        self.label_Scenario_Head.setObjectName(u"label_Scenario_Head")
        self.label_Scenario_Head.setStyleSheet(u"QLabel {\n"
"        qproperty-alignment: AlignCenter;\n"
"	border: 1px solid  rgb(84, 188, 235);\n"
"	border-top-left-radius: 15px;\n"
"	border-top-right-radius: 15px;\n"
"	background-color:  rgb(84, 188, 235);\n"
"	padding: 5px 0px;\n"
"	color:  rgb(255, 255, 235);\n"
"font-weight:500;\n"
"}")

        self.verticalLayout_18.addWidget(self.label_Scenario_Head)

        self.frame_10 = QFrame(self.scrollAreaWidgetContents_4)
        self.frame_10.setObjectName(u"frame_10")
        self.frame_10.setStyleSheet(u"QFrame {\n"
"	border: 1px solid #54bceb;\n"
"	border-bottom-left-radius: 15px;\n"
"	border-bottom-right-radius: 15px;\n"
"}\n"
"QLabel{border: 0px solid rgb(255,255,255);}")
        self.frame_10.setFrameShape(QFrame.StyledPanel)
        self.frame_10.setFrameShadow(QFrame.Raised)
        self.verticalLayout_16 = QVBoxLayout(self.frame_10)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.checkBox_AutoSaving = QCheckBox(self.frame_10)
        self.checkBox_AutoSaving.setObjectName(u"checkBox_AutoSaving")

        self.verticalLayout_16.addWidget(self.checkBox_AutoSaving)

        self.label_Scenario_Hint = QLabel(self.frame_10)
        self.label_Scenario_Hint.setObjectName(u"label_Scenario_Hint")
        self.label_Scenario_Hint.setWordWrap(True)

        self.verticalLayout_16.addWidget(self.label_Scenario_Hint)


        self.verticalLayout_18.addWidget(self.frame_10)

        self.verticalSpacer_5 = QSpacerItem(20, 341, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_18.addItem(self.verticalSpacer_5)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents_4)

        self.verticalLayout_14.addWidget(self.scrollArea)

        self.stackedWidget.addWidget(self.page_Settings)

        self.verticalLayout_21.addWidget(self.stackedWidget)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_Status = QLabel(self.centralwidget)
        self.label_Status.setObjectName(u"label_Status")

        self.horizontalLayout_7.addWidget(self.label_Status)

        self.progressBar = QProgressBar(self.centralwidget)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setStyleSheet(u"QProgressBar{border: 1px solid white;\n"
" border-radius: 10px;\n"
"text-align: center;\n"
" color: #ffffff;\n"
"}QProgressBar::chunk{background-color: #54bceb; border-radius: 10px;}")
        self.progressBar.setValue(24)

        self.horizontalLayout_7.addWidget(self.progressBar)


        self.verticalLayout_21.addLayout(self.horizontalLayout_7)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.pushButton_start_single = QPushButton(self.centralwidget)
        self.pushButton_start_single.setObjectName(u"pushButton_start_single")
        self.pushButton_start_single.setMinimumSize(QSize(100, 40))
        self.pushButton_start_single.setMaximumSize(QSize(16777215, 40))
        self.pushButton_start_single.setStyleSheet(u"")
        icon32 = QIcon()
        icon32.addFile(u":/icons/icons/Start.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_start_single.setIcon(icon32)
        self.pushButton_start_single.setIconSize(QSize(24, 24))

        self.horizontalLayout_2.addWidget(self.pushButton_start_single)

        self.pushButton_start_multiple = QPushButton(self.centralwidget)
        self.pushButton_start_multiple.setObjectName(u"pushButton_start_multiple")
        self.pushButton_start_multiple.setMinimumSize(QSize(100, 40))
        self.pushButton_start_multiple.setMaximumSize(QSize(16777215, 40))
        self.pushButton_start_multiple.setStyleSheet(u"")
        icon33 = QIcon()
        icon33.addFile(u":/icons/icons/Start_multiple.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_start_multiple.setIcon(icon33)
        self.pushButton_start_multiple.setIconSize(QSize(24, 24))

        self.horizontalLayout_2.addWidget(self.pushButton_start_multiple)

        self.pushButton_Cancel = QPushButton(self.centralwidget)
        self.pushButton_Cancel.setObjectName(u"pushButton_Cancel")
        self.pushButton_Cancel.setMinimumSize(QSize(100, 40))
        self.pushButton_Cancel.setMaximumSize(QSize(16777215, 40))
        self.pushButton_Cancel.setStyleSheet(u"")
        icon34 = QIcon()
        icon34.addFile(u":/icons/icons/Exit.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_Cancel.setIcon(icon34)
        self.pushButton_Cancel.setIconSize(QSize(24, 24))

        self.horizontalLayout_2.addWidget(self.pushButton_Cancel)


        self.verticalLayout_21.addLayout(self.horizontalLayout_2)


        self.horizontalLayout_23.addLayout(self.verticalLayout_21)

        GHETool.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(GHETool)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setEnabled(True)
        self.menubar.setGeometry(QRect(0, 0, 1226, 30))
        self.menubar.setStyleSheet(u"QMenuBar::item{\n"
"    background-color: rgb(0, 64, 122);\n"
"}\n"
"QMenuBar::item:pressed {	background-color:rgb(84, 188, 235);}\n"
"QMenuBar::item:selected{	background-color:rgb(84, 188, 235);}\n"
"QToolTip { color: #fff; background-color: #000; border: none; }")
        self.menubar.setNativeMenuBar(True)
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuFile.setStyleSheet(u"QAction::icon { background-color:rgb(84, 188, 235);\n"
"selection-background-color: rgb(84, 188, 235);}\n"
"*{	background-color: rgb(0, 64, 122);}\n"
"*:hover{background-color: rgb(84, 188, 235);}")
        self.menuFile.setTearOffEnabled(False)
        self.menuCalculation = QMenu(self.menubar)
        self.menuCalculation.setObjectName(u"menuCalculation")
        self.menuSettings = QMenu(self.menubar)
        self.menuSettings.setObjectName(u"menuSettings")
        self.menuLanguage = QMenu(self.menuSettings)
        self.menuLanguage.setObjectName(u"menuLanguage")
        self.menuLanguage.setEnabled(True)
        icon35 = QIcon()
        icon35.addFile(u":/icons/icons/Language.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon35.addFile(u":/icons/icons/Language_Inv.svg", QSize(), QIcon.Active, QIcon.Off)
        self.menuLanguage.setIcon(icon35)
        self.menuScenario = QMenu(self.menubar)
        self.menuScenario.setObjectName(u"menuScenario")
        GHETool.setMenuBar(self.menubar)
        self.toolBar = QToolBar(GHETool)
        self.toolBar.setObjectName(u"toolBar")
        self.toolBar.setStyleSheet(u"*{\n"
"	background-color: rgb(0, 64, 122);\n"
"}\n"
"*:hover{background-color: rgb(84, 188, 235);}\n"
"QToolTip { color: rgb(0, 0, 0); background-color: rgb(255, 255, 255);border: 1px solid rgb(84, 188, 235); }")
        self.toolBar.setMovable(False)
        GHETool.addToolBar(Qt.TopToolBarArea, self.toolBar)
        self.status_bar = QStatusBar(GHETool)
        self.status_bar.setObjectName(u"status_bar")
        self.status_bar.setStyleSheet(u"QStatusBar::item{border:None;}")
        GHETool.setStatusBar(self.status_bar)
        QWidget.setTabOrder(self.doubleSpinBox_H, self.doubleSpinBox_B)
        QWidget.setTabOrder(self.doubleSpinBox_B, self.doubleSpinBox_B_max)
        QWidget.setTabOrder(self.doubleSpinBox_B_max, self.doubleSpinBox_k_s)
        QWidget.setTabOrder(self.doubleSpinBox_k_s, self.doubleSpinBox_Tg)
        QWidget.setTabOrder(self.doubleSpinBox_Tg, self.spinBox_N_1)
        QWidget.setTabOrder(self.spinBox_N_1, self.doubleSpinBox_W_max)
        QWidget.setTabOrder(self.doubleSpinBox_W_max, self.spinBox_N_2)
        QWidget.setTabOrder(self.spinBox_N_2, self.doubleSpinBox_L_max)
        QWidget.setTabOrder(self.doubleSpinBox_L_max, self.comboBox_depth_Method)
        QWidget.setTabOrder(self.comboBox_depth_Method, self.comboBox_Size_Method)
        QWidget.setTabOrder(self.comboBox_Size_Method, self.doubleSpinBox_TMin)
        QWidget.setTabOrder(self.doubleSpinBox_TMin, self.doubleSpinBox_TMax)
        QWidget.setTabOrder(self.doubleSpinBox_TMax, self.spinBox_Years)
        QWidget.setTabOrder(self.spinBox_Years, self.comboBox_Rb_method)
        QWidget.setTabOrder(self.comboBox_Rb_method, self.doubleSpinBox_Rb)
        QWidget.setTabOrder(self.doubleSpinBox_Rb, self.doubleSpinBox_fluid_lambda)
        QWidget.setTabOrder(self.doubleSpinBox_fluid_lambda, self.doubleSpinBox_fluid_mass_flow_rate)
        QWidget.setTabOrder(self.doubleSpinBox_fluid_mass_flow_rate, self.doubleSpinBox_fluid_density)
        QWidget.setTabOrder(self.doubleSpinBox_fluid_density, self.doubleSpinBox_fluid_thermal_capacity)
        QWidget.setTabOrder(self.doubleSpinBox_fluid_thermal_capacity, self.doubleSpinBox_fluid_viscosity)
        QWidget.setTabOrder(self.doubleSpinBox_fluid_viscosity, self.spinBox_number_pipes)
        QWidget.setTabOrder(self.spinBox_number_pipes, self.doubleSpinBox_grout_conductivity)
        QWidget.setTabOrder(self.doubleSpinBox_grout_conductivity, self.doubleSpinBox_pipe_conductivity)
        QWidget.setTabOrder(self.doubleSpinBox_pipe_conductivity, self.doubleSpinBox_pipe_outer_radius)
        QWidget.setTabOrder(self.doubleSpinBox_pipe_outer_radius, self.doubleSpinBox_pipe_inner_radius)
        QWidget.setTabOrder(self.doubleSpinBox_pipe_inner_radius, self.doubleSpinBox_borehole_radius)
        QWidget.setTabOrder(self.doubleSpinBox_borehole_radius, self.doubleSpinBox_pipe_distance)
        QWidget.setTabOrder(self.doubleSpinBox_pipe_distance, self.doubleSpinBox_pipe_roughness)
        QWidget.setTabOrder(self.doubleSpinBox_pipe_roughness, self.doubleSpinBox_borehole_burial_depth)
        QWidget.setTabOrder(self.doubleSpinBox_borehole_burial_depth, self.pushButton_NextResistance)
        QWidget.setTabOrder(self.pushButton_NextResistance, self.checkBox_Import)
        QWidget.setTabOrder(self.checkBox_Import, self.comboBox_Datentyp)
        QWidget.setTabOrder(self.comboBox_Datentyp, self.lineEdit_displayCsv)
        QWidget.setTabOrder(self.lineEdit_displayCsv, self.pushButton_loadCsv)
        QWidget.setTabOrder(self.pushButton_loadCsv, self.comboBox_Seperator)
        QWidget.setTabOrder(self.comboBox_Seperator, self.comboBox_decimal)
        QWidget.setTabOrder(self.comboBox_decimal, self.comboBox_sheetName)
        QWidget.setTabOrder(self.comboBox_sheetName, self.pushButton_load)
        QWidget.setTabOrder(self.pushButton_load, self.comboBox_dataColumn)
        QWidget.setTabOrder(self.comboBox_dataColumn, self.comboBox_heatingLoad)
        QWidget.setTabOrder(self.comboBox_heatingLoad, self.comboBox_coolingLoad)
        QWidget.setTabOrder(self.comboBox_coolingLoad, self.comboBox_combined)
        QWidget.setTabOrder(self.comboBox_combined, self.comboBox_timeStep)
        QWidget.setTabOrder(self.comboBox_timeStep, self.comboBox_date)
        QWidget.setTabOrder(self.comboBox_date, self.comboBox_dataUnit)
        QWidget.setTabOrder(self.comboBox_dataUnit, self.pushButton_calculate)
        QWidget.setTabOrder(self.pushButton_calculate, self.doubleSpinBox_Hp_Jan)
        QWidget.setTabOrder(self.doubleSpinBox_Hp_Jan, self.doubleSpinBox_Hp_Feb)
        QWidget.setTabOrder(self.doubleSpinBox_Hp_Feb, self.doubleSpinBox_Hp_Mar)
        QWidget.setTabOrder(self.doubleSpinBox_Hp_Mar, self.doubleSpinBox_Hp_Apr)
        QWidget.setTabOrder(self.doubleSpinBox_Hp_Apr, self.doubleSpinBox_Hp_May)
        QWidget.setTabOrder(self.doubleSpinBox_Hp_May, self.doubleSpinBox_Hp_Jun)
        QWidget.setTabOrder(self.doubleSpinBox_Hp_Jun, self.doubleSpinBox_Hp_Jul)
        QWidget.setTabOrder(self.doubleSpinBox_Hp_Jul, self.doubleSpinBox_Hp_Aug)
        QWidget.setTabOrder(self.doubleSpinBox_Hp_Aug, self.doubleSpinBox_Hp_Sep)
        QWidget.setTabOrder(self.doubleSpinBox_Hp_Sep, self.doubleSpinBox_Hp_Oct)
        QWidget.setTabOrder(self.doubleSpinBox_Hp_Oct, self.doubleSpinBox_Hp_Nov)
        QWidget.setTabOrder(self.doubleSpinBox_Hp_Nov, self.doubleSpinBox_Hp_Dec)
        QWidget.setTabOrder(self.doubleSpinBox_Hp_Dec, self.doubleSpinBox_Cp_Jan)
        QWidget.setTabOrder(self.doubleSpinBox_Cp_Jan, self.doubleSpinBox_Cp_Feb)
        QWidget.setTabOrder(self.doubleSpinBox_Cp_Feb, self.doubleSpinBox_Cp_Mar)
        QWidget.setTabOrder(self.doubleSpinBox_Cp_Mar, self.doubleSpinBox_Cp_Apr)
        QWidget.setTabOrder(self.doubleSpinBox_Cp_Apr, self.doubleSpinBox_Cp_May)
        QWidget.setTabOrder(self.doubleSpinBox_Cp_May, self.doubleSpinBox_Cp_Jun)
        QWidget.setTabOrder(self.doubleSpinBox_Cp_Jun, self.doubleSpinBox_Cp_Jul)
        QWidget.setTabOrder(self.doubleSpinBox_Cp_Jul, self.doubleSpinBox_Cp_Aug)
        QWidget.setTabOrder(self.doubleSpinBox_Cp_Aug, self.doubleSpinBox_Cp_Sep)
        QWidget.setTabOrder(self.doubleSpinBox_Cp_Sep, self.doubleSpinBox_Cp_Oct)
        QWidget.setTabOrder(self.doubleSpinBox_Cp_Oct, self.doubleSpinBox_Cp_Nov)
        QWidget.setTabOrder(self.doubleSpinBox_Cp_Nov, self.doubleSpinBox_Cp_Dec)
        QWidget.setTabOrder(self.doubleSpinBox_Cp_Dec, self.doubleSpinBox_HL_Jan)
        QWidget.setTabOrder(self.doubleSpinBox_HL_Jan, self.doubleSpinBox_HL_Feb)
        QWidget.setTabOrder(self.doubleSpinBox_HL_Feb, self.doubleSpinBox_HL_Mar)
        QWidget.setTabOrder(self.doubleSpinBox_HL_Mar, self.doubleSpinBox_HL_Apr)
        QWidget.setTabOrder(self.doubleSpinBox_HL_Apr, self.doubleSpinBox_HL_May)
        QWidget.setTabOrder(self.doubleSpinBox_HL_May, self.doubleSpinBox_HL_Jun)
        QWidget.setTabOrder(self.doubleSpinBox_HL_Jun, self.doubleSpinBox_HL_Jul)
        QWidget.setTabOrder(self.doubleSpinBox_HL_Jul, self.doubleSpinBox_HL_Aug)
        QWidget.setTabOrder(self.doubleSpinBox_HL_Aug, self.doubleSpinBox_HL_Sep)
        QWidget.setTabOrder(self.doubleSpinBox_HL_Sep, self.doubleSpinBox_HL_Oct)
        QWidget.setTabOrder(self.doubleSpinBox_HL_Oct, self.doubleSpinBox_HL_Nov)
        QWidget.setTabOrder(self.doubleSpinBox_HL_Nov, self.doubleSpinBox_HL_Dec)
        QWidget.setTabOrder(self.doubleSpinBox_HL_Dec, self.doubleSpinBox_CL_Jan)
        QWidget.setTabOrder(self.doubleSpinBox_CL_Jan, self.doubleSpinBox_CL_Feb)
        QWidget.setTabOrder(self.doubleSpinBox_CL_Feb, self.doubleSpinBox_CL_Mar)
        QWidget.setTabOrder(self.doubleSpinBox_CL_Mar, self.doubleSpinBox_CL_Apr)
        QWidget.setTabOrder(self.doubleSpinBox_CL_Apr, self.doubleSpinBox_CL_May)
        QWidget.setTabOrder(self.doubleSpinBox_CL_May, self.doubleSpinBox_CL_Jun)
        QWidget.setTabOrder(self.doubleSpinBox_CL_Jun, self.doubleSpinBox_CL_Jul)
        QWidget.setTabOrder(self.doubleSpinBox_CL_Jul, self.doubleSpinBox_CL_Aug)
        QWidget.setTabOrder(self.doubleSpinBox_CL_Aug, self.doubleSpinBox_CL_Sep)
        QWidget.setTabOrder(self.doubleSpinBox_CL_Sep, self.doubleSpinBox_CL_Oct)
        QWidget.setTabOrder(self.doubleSpinBox_CL_Oct, self.doubleSpinBox_CL_Nov)
        QWidget.setTabOrder(self.doubleSpinBox_CL_Nov, self.doubleSpinBox_CL_Dec)
        QWidget.setTabOrder(self.doubleSpinBox_CL_Dec, self.comboBox_Unit_peak)
        QWidget.setTabOrder(self.comboBox_Unit_peak, self.comboBox_Unit_Load)
        QWidget.setTabOrder(self.comboBox_Unit_Load, self.pushButton_Unit)
        QWidget.setTabOrder(self.pushButton_Unit, self.comboBox_SeperatorDataFile)
        QWidget.setTabOrder(self.comboBox_SeperatorDataFile, self.comboBox_decimalDataFile)
        QWidget.setTabOrder(self.comboBox_decimalDataFile, self.lineEdit_filename_data_file)
        QWidget.setTabOrder(self.lineEdit_filename_data_file, self.pushButton_data_file_select)
        QWidget.setTabOrder(self.pushButton_data_file_select, self.comboBox_dataColumn_data_file)
        QWidget.setTabOrder(self.comboBox_dataColumn_data_file, self.comboBox_heatingLoad_data_file)
        QWidget.setTabOrder(self.comboBox_heatingLoad_data_file, self.comboBox_coolingLoad_data_file)
        QWidget.setTabOrder(self.comboBox_coolingLoad_data_file, self.comboBox_combined_data_file)
        QWidget.setTabOrder(self.comboBox_combined_data_file, self.comboBox_dataUnit_data_file)
        QWidget.setTabOrder(self.comboBox_dataUnit_data_file, self.pushButton_start_single)
        QWidget.setTabOrder(self.pushButton_start_single, self.pushButton_start_multiple)
        QWidget.setTabOrder(self.pushButton_start_multiple, self.pushButton_Cancel)
        QWidget.setTabOrder(self.pushButton_Cancel, self.pushButton_PreviousThermal)
        QWidget.setTabOrder(self.pushButton_PreviousThermal, self.pushButton_PreviousResistance)
        QWidget.setTabOrder(self.pushButton_PreviousResistance, self.pushButton_General)
        QWidget.setTabOrder(self.pushButton_General, self.pushButton_borehole_resistance)
        QWidget.setTabOrder(self.pushButton_borehole_resistance, self.pushButton_thermalDemands)
        QWidget.setTabOrder(self.pushButton_thermalDemands, self.pushButton_Results)
        QWidget.setTabOrder(self.pushButton_Results, self.pushButton_SaveScenario)
        QWidget.setTabOrder(self.pushButton_SaveScenario, self.pushButton_AddScenario)
        QWidget.setTabOrder(self.pushButton_AddScenario, self.pushButton_DeleteScenario)
        QWidget.setTabOrder(self.pushButton_DeleteScenario, self.button_rename_scenario)
        QWidget.setTabOrder(self.button_rename_scenario, self.list_widget_scenario)
        QWidget.setTabOrder(self.list_widget_scenario, self.pushButton_SaveData)
        QWidget.setTabOrder(self.pushButton_SaveData, self.checkBox_Legend)
        QWidget.setTabOrder(self.checkBox_Legend, self.pushButton_SaveFigure)
        QWidget.setTabOrder(self.pushButton_SaveFigure, self.comboBox_Language)
        QWidget.setTabOrder(self.comboBox_Language, self.checkBox_AutoSaving)
        QWidget.setTabOrder(self.checkBox_AutoSaving, self.scrollArea_Res)
        QWidget.setTabOrder(self.scrollArea_Res, self.scrollArea)
        QWidget.setTabOrder(self.scrollArea, self.scrollArea_2)
        QWidget.setTabOrder(self.scrollArea_2, self.pushButton_NextGeneral)
        QWidget.setTabOrder(self.pushButton_NextGeneral, self.scrollArea_thermal)
        QWidget.setTabOrder(self.scrollArea_thermal, self.scrollArea_General)
        QWidget.setTabOrder(self.scrollArea_General, self.graphicsView)

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
        self.checkBox_Import.toggled.connect(self.toolBox.setVisible)
        self.checkBox_Import.stateChanged.connect(self.toolBox.setCurrentIndex)
        self.pushButton_start_single.clicked.connect(self.action_start_single.trigger)
        self.checkBox_AutoSaving.toggled.connect(self.pushButton_SaveScenario.setHidden)
        self.comboBox_Rb_method.currentIndexChanged.connect(self.actionInputChanged.trigger)
        self.comboBox_depth_Method.currentIndexChanged.connect(self.actionInputChanged.trigger)
        self.comboBox_Size_Method.currentIndexChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_H.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_B.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_B_max.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_k_s.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_Tg.valueChanged.connect(self.actionInputChanged.trigger)
        self.spinBox_N_1.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_W_max.valueChanged.connect(self.actionInputChanged.trigger)
        self.spinBox_N_2.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_L_max.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_TMin.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_TMax.valueChanged.connect(self.actionInputChanged.trigger)
        self.spinBox_Years.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_Rb.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_fluid_lambda.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_fluid_mass_flow_rate.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_fluid_density.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_fluid_thermal_capacity.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_fluid_viscosity.valueChanged.connect(self.actionInputChanged.trigger)
        self.spinBox_number_pipes.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_grout_conductivity.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_pipe_conductivity.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_pipe_inner_radius.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_pipe_outer_radius.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_pipe_distance.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_borehole_radius.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_pipe_roughness.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_borehole_burial_depth.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_Hp_Jan.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_Hp_Feb.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_Hp_Mar.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_Hp_Apr.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_Hp_May.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_Hp_Jun.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_Hp_Jul.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_Hp_Aug.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_Hp_Sep.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_Hp_Oct.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_Hp_Nov.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_Hp_Dec.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_Cp_Jan.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_Cp_Feb.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_Cp_Mar.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_Cp_Apr.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_Cp_May.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_Cp_Jun.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_Cp_Jul.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_Cp_Aug.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_Cp_Sep.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_Cp_Oct.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_Cp_Nov.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_Cp_Dec.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_HL_Jan.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_HL_Feb.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_HL_Mar.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_HL_Apr.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_HL_May.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_HL_Jun.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_HL_Jul.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_HL_Aug.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_HL_Sep.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_HL_Oct.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_HL_Nov.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_HL_Dec.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_CL_Jan.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_CL_Feb.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_CL_Mar.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_CL_Apr.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_CL_May.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_CL_Jun.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_CL_Jul.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_CL_Aug.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_CL_Sep.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_CL_Oct.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_CL_Nov.valueChanged.connect(self.actionInputChanged.trigger)
        self.doubleSpinBox_CL_Dec.valueChanged.connect(self.actionInputChanged.trigger)
        self.pushButton_Unit.toggled.connect(self.actionInputChanged.trigger)
        self.spinBox_number_pipes.valueChanged.connect(self.actionCheckUDistance.trigger)
        self.doubleSpinBox_pipe_outer_radius.valueChanged.connect(self.actionCheckUDistance.trigger)
        self.doubleSpinBox_borehole_radius.valueChanged.connect(self.actionCheckUDistance.trigger)
        self.comboBox_SeperatorDataFile.currentIndexChanged.connect(self.actionInputChanged.trigger)
        self.lineEdit_filename_data_file.textChanged.connect(self.actionInputChanged.trigger)
        self.comboBox_heatingLoad_data_file.currentIndexChanged.connect(self.actionInputChanged.trigger)
        self.comboBox_coolingLoad_data_file.currentIndexChanged.connect(self.actionInputChanged.trigger)
        self.comboBox_combined_data_file.currentIndexChanged.connect(self.actionInputChanged.trigger)
        self.comboBox_dataUnit_data_file.currentIndexChanged.connect(self.actionInputChanged.trigger)
        self.comboBox_dataColumn_data_file.currentIndexChanged.connect(self.actionInputChanged.trigger)
        self.comboBox_decimalDataFile.currentIndexChanged.connect(self.actionInputChanged.trigger)
        self.spinBox_number_pipes.valueChanged.connect(self.actionUpdateBoreholeGraph.trigger)
        self.doubleSpinBox_pipe_inner_radius.valueChanged.connect(self.actionUpdate_Scenario.trigger)
        self.doubleSpinBox_pipe_outer_radius.valueChanged.connect(self.actionUpdateBoreholeGraph.trigger)
        self.doubleSpinBox_borehole_radius.valueChanged.connect(self.actionUpdateBoreholeGraph.trigger)
        self.doubleSpinBox_pipe_distance.valueChanged.connect(self.actionUpdateBoreholeGraph.trigger)
        self.doubleSpinBox_pipe_inner_radius.valueChanged.connect(self.actionUpdateBoreholeGraph.trigger)
        self.pushButton_simulation_period.toggled.connect(self.frame_simulation_period.setVisible)

        self.stackedWidget.setCurrentIndex(0)
        self.toolBox.setCurrentIndex(1)
        self.comboBox_dataColumn.setCurrentIndex(0)
        self.comboBox_timeStep.setCurrentIndex(0)
        self.comboBox_dataColumn_data_file.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(GHETool)
    # setupUi

    def retranslateUi(self, GHEtool):
        GHEtool.setWindowTitle(QCoreApplication.translate("GHEtool", u"GHEtool", None))
        self.actionNew.setText(QCoreApplication.translate("GHEtool", u"New", None))
#if QT_CONFIG(tooltip)
        self.actionNew.setToolTip(QCoreApplication.translate("GHEtool", u"Create new project file", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.actionNew.setShortcut(QCoreApplication.translate("GHEtool", u"Ctrl+N", None))
#endif // QT_CONFIG(shortcut)
        self.actionSave.setText(QCoreApplication.translate("GHEtool", u"Save", None))
#if QT_CONFIG(shortcut)
        self.actionSave.setShortcut(QCoreApplication.translate("GHEtool", u"Ctrl+S", None))
#endif // QT_CONFIG(shortcut)
        self.actionOpen.setText(QCoreApplication.translate("GHEtool", u"Open", None))
#if QT_CONFIG(shortcut)
        self.actionOpen.setShortcut(QCoreApplication.translate("GHEtool", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.action_start_multiple.setText(QCoreApplication.translate("GHEtool", u"Calculate all scenarios", None))
#if QT_CONFIG(shortcut)
        self.action_start_multiple.setShortcut(QCoreApplication.translate("GHEtool", u"Ctrl+R", None))
#endif // QT_CONFIG(shortcut)
        self.actionGerman.setText(QCoreApplication.translate("GHEtool", u"German", None))
#if QT_CONFIG(shortcut)
        self.actionGerman.setShortcut(QCoreApplication.translate("GHEtool", u"Ctrl+Alt+G", None))
#endif // QT_CONFIG(shortcut)
        self.actionEnglish.setText(QCoreApplication.translate("GHEtool", u"English", None))
#if QT_CONFIG(shortcut)
        self.actionEnglish.setShortcut(QCoreApplication.translate("GHEtool", u"Ctrl+Alt+\u20ac", None))
#endif // QT_CONFIG(shortcut)
        self.actionUpdate_Scenario.setText(QCoreApplication.translate("GHEtool", u"Update scenario", None))
#if QT_CONFIG(shortcut)
        self.actionUpdate_Scenario.setShortcut(QCoreApplication.translate("GHEtool", u"Ctrl+Shift+S", None))
#endif // QT_CONFIG(shortcut)
        self.actionAdd_Scenario.setText(QCoreApplication.translate("GHEtool", u"Add scenario", None))
#if QT_CONFIG(shortcut)
        self.actionAdd_Scenario.setShortcut(QCoreApplication.translate("GHEtool", u"Ctrl+Shift+A", None))
#endif // QT_CONFIG(shortcut)
        self.actionDelete_scenario.setText(QCoreApplication.translate("GHEtool", u"Delete scenario", None))
#if QT_CONFIG(shortcut)
        self.actionDelete_scenario.setShortcut(QCoreApplication.translate("GHEtool", u"Ctrl+Shift+D", None))
#endif // QT_CONFIG(shortcut)
        self.actionSave_As.setText(QCoreApplication.translate("GHEtool", u"Save As", None))
#if QT_CONFIG(shortcut)
        self.actionSave_As.setShortcut(QCoreApplication.translate("GHEtool", u"F12", None))
#endif // QT_CONFIG(shortcut)
        self.actionDutch.setText(QCoreApplication.translate("GHEtool", u"Dutch", None))
#if QT_CONFIG(shortcut)
        self.actionDutch.setShortcut(QCoreApplication.translate("GHEtool", u"Ctrl+Alt+D", None))
#endif // QT_CONFIG(shortcut)
        self.actionItalian.setText(QCoreApplication.translate("GHEtool", u"Italian", None))
#if QT_CONFIG(shortcut)
        self.actionItalian.setShortcut(QCoreApplication.translate("GHEtool", u"Ctrl+Alt+I", None))
#endif // QT_CONFIG(shortcut)
        self.actionFrench.setText(QCoreApplication.translate("GHEtool", u"French", None))
#if QT_CONFIG(shortcut)
        self.actionFrench.setShortcut(QCoreApplication.translate("GHEtool", u"Ctrl+Alt+F", None))
#endif // QT_CONFIG(shortcut)
        self.actionRename_scenario.setText(QCoreApplication.translate("GHEtool", u"Rename scenario", None))
#if QT_CONFIG(shortcut)
        self.actionRename_scenario.setShortcut(QCoreApplication.translate("GHEtool", u"Ctrl+Shift+R", None))
#endif // QT_CONFIG(shortcut)
        self.action_start_single.setText(QCoreApplication.translate("GHEtool", u"Calculate current scenario", None))
#if QT_CONFIG(shortcut)
        self.action_start_single.setShortcut(QCoreApplication.translate("GHEtool", u"Ctrl+Shift+R", None))
#endif // QT_CONFIG(shortcut)
        self.actionSpanish.setText(QCoreApplication.translate("GHEtool", u"Spanish", None))
#if QT_CONFIG(shortcut)
        self.actionSpanish.setShortcut(QCoreApplication.translate("GHEtool", u"Ctrl+Alt+S", None))
#endif // QT_CONFIG(shortcut)
        self.actionInputChanged.setText(QCoreApplication.translate("GHEtool", u"InputChanged", None))
        self.actionCheckUDistance.setText(QCoreApplication.translate("GHEtool", u"CheckUDistance", None))
        self.actionUpdateBoreholeGraph.setText(QCoreApplication.translate("GHEtool", u"UpdateBoreholeGraph", None))
        self.actionGalician.setText(QCoreApplication.translate("GHEtool", u"Galician", None))
#if QT_CONFIG(shortcut)
        self.actionGalician.setShortcut(QCoreApplication.translate("GHEtool", u"Ctrl+Alt+A", None))
#endif // QT_CONFIG(shortcut)
        self.pushButton_SaveScenario.setText(QCoreApplication.translate("GHEtool", u"Update scenario", None))
        self.pushButton_AddScenario.setText(QCoreApplication.translate("GHEtool", u"Add scenario", None))
        self.pushButton_DeleteScenario.setText(QCoreApplication.translate("GHEtool", u"Delete scenario", None))
        self.button_rename_scenario.setText(QCoreApplication.translate("GHEtool", u"Rename scenario", None))

        __sortingEnabled = self.list_widget_scenario.isSortingEnabled()
        self.list_widget_scenario.setSortingEnabled(False)
        ___qlistwidgetitem = self.list_widget_scenario.item(0)
        ___qlistwidgetitem.setText(QCoreApplication.translate("GHEtool", u"Scenario: 1", None));
        self.list_widget_scenario.setSortingEnabled(__sortingEnabled)

        self.label_Gap_Aim.setText("")
        self.pushButton_General.setText(QCoreApplication.translate("GHEtool", u"Borehole \n"
"and earth", None))
        self.label_GapBR_Res.setText("")
        self.pushButton_borehole_resistance.setText(QCoreApplication.translate("GHEtool", u"Borehole\n"
"resistance", None))
        self.label_GapGenTh.setText("")
        self.pushButton_thermalDemands.setText(QCoreApplication.translate("GHEtool", u"Thermal \n"
"demands", None))
        self.label_GapThRes.setText("")
        self.pushButton_Results.setText(QCoreApplication.translate("GHEtool", u"Results", None))
        self.label_GapResSet.setText("")
        self.label.setText(QCoreApplication.translate("GHEtool", u"Aim of simulation", None))
        self.label_4.setText("")
        self.label_Earth_Properties_7.setText(QCoreApplication.translate("GHEtool", u"Thermal data format", None))
        self.pushButton_hourly_data.setText(QCoreApplication.translate("GHEtool", u"hourly data", None))
        self.pushButton_hourly_data2.setText(QCoreApplication.translate("GHEtool", u"hourly data2", None))
        self.label_Gap_Aim_5.setText("")
        self.pushButton_monthly_data.setText(QCoreApplication.translate("GHEtool", u"monthly data", None))
        self.label_3.setText("")
        self.label_Options.setText(QCoreApplication.translate("GHEtool", u"Options", None))
        self.label_calc_method_depth_sizing.setText(QCoreApplication.translate("GHEtool", u"calculation method for depth sizing", None))
        self.pushButton_9.setText(QCoreApplication.translate("GHEtool", u"simple", None))
        self.pushButton_11.setText(QCoreApplication.translate("GHEtool", u"complex", None))
        self.label_Gap_Aim_2.setText("")
        self.label_calc_method_length_sizing.setText(QCoreApplication.translate("GHEtool", u"calculation method for length and width sizing", None))
        self.pushButton_10.setText(QCoreApplication.translate("GHEtool", u"simple", None))
        self.pushButton_12.setText(QCoreApplication.translate("GHEtool", u"complex", None))
        self.label_Gap_Aim_3.setText("")
        self.label_calc_method_length_sizing_2.setText(QCoreApplication.translate("GHEtool", u"calculation method for length and width sizing", None))
        self.pushButton_13.setText(QCoreApplication.translate("GHEtool", u"simple", None))
        self.pushButton_14.setText(QCoreApplication.translate("GHEtool", u"complex", None))
        self.label_5.setText("")
        self.pushButton_NextAim.setText(QCoreApplication.translate("GHEtool", u"  next  ", None))
        self.label_Borehole_earth.setText(QCoreApplication.translate("GHEtool", u"Borehole and earth", None))
        self.label_46.setText("")
        self.label_Earth_Properties.setText(QCoreApplication.translate("GHEtool", u"Borehole and earth properties", None))
        self.label_H.setText(QCoreApplication.translate("GHEtool", u"Borehole depth [m]: ", None))
        self.label_BS.setText(QCoreApplication.translate("GHEtool", u"Borehole spacing [m]: ", None))
        self.label_B_max.setText(QCoreApplication.translate("GHEtool", u"Maximal borehole spacing [m]: ", None))
        self.label_lambdaEarth.setText(QCoreApplication.translate("GHEtool", u"Conductivity of the soil [W/mK]: ", None))
        self.label_GroundTemp.setText(QCoreApplication.translate("GHEtool", u"Ground temperature at infinity [\u00b0C]: ", None))
        self.label_LengthField.setText(QCoreApplication.translate("GHEtool", u"Length of rectangular field [#]: ", None))
        self.label_WidthField.setText(QCoreApplication.translate("GHEtool", u"Width of rectangular field [#]: ", None))
        self.label_MaxWidthField.setText(QCoreApplication.translate("GHEtool", u"Maximal width of rectangular field [m]: ", None))
        self.label_MaxLengthField.setText(QCoreApplication.translate("GHEtool", u"Maximal length of rectangular field [m]: ", None))
        self.label_calc_method_depth.setText(QCoreApplication.translate("GHEtool", u"Calculation method for depth sizing [-]:", None))
        self.label_calc_method_sizing.setText(QCoreApplication.translate("GHEtool", u"Calculation method for borehole sizing [-]:", None))
        self.comboBox_Size_Method.setItemText(0, QCoreApplication.translate("GHEtool", u"Fast", None))
        self.comboBox_Size_Method.setItemText(1, QCoreApplication.translate("GHEtool", u"Robust", None))

        self.comboBox_depth_Method.setItemText(0, QCoreApplication.translate("GHEtool", u"Fast", None))
        self.comboBox_depth_Method.setItemText(1, QCoreApplication.translate("GHEtool", u"Robust", None))

        self.label_45.setText("")
        self.label_37.setText("")
        self.pushButton_simulation_period.setText(QCoreApplication.translate("GHEtool", u"Temperature constraints and simulation period", None))
        self.label_TempMin.setText(QCoreApplication.translate("GHEtool", u"Minimal temperature [\u00b0C]: ", None))
        self.label_TempMax.setText(QCoreApplication.translate("GHEtool", u"Maximal temperature [\u00b0C]: ", None))
        self.label_SimulationTime.setText(QCoreApplication.translate("GHEtool", u"Simulation period [yrs]: ", None))
        self.label_38.setText("")
        self.label_WarningCustomBorefield.setText(QCoreApplication.translate("GHEtool", u"With the selected values a customized bore field will be calculated. This will dramatically increase the calculation time.", None))
        self.label_44.setText("")
        self.pushButton_PreviousGeneral.setText(QCoreApplication.translate("GHEtool", u"  previous  ", None))
        self.pushButton_NextGeneral.setText(QCoreApplication.translate("GHEtool", u"  next  ", None))
        self.label_Borehole_Resistance.setText(QCoreApplication.translate("GHEtool", u"Equivalent borehole resistance", None))
        self.label_49.setText("")
        self.label_Borehole_Resistance_Head.setText(QCoreApplication.translate("GHEtool", u"Equivalent borehole resistance", None))
        self.label_Rb_calculation_method.setText(QCoreApplication.translate("GHEtool", u"Calculation method:", None))
        self.label_BoreholeResistance.setText(QCoreApplication.translate("GHEtool", u"Equivalent borehole resistance [mK/W]: ", None))
        self.comboBox_Rb_method.setItemText(0, QCoreApplication.translate("GHEtool", u"Known constant value", None))
        self.comboBox_Rb_method.setItemText(1, QCoreApplication.translate("GHEtool", u"Unknown constant value", None))
        self.comboBox_Rb_method.setItemText(2, QCoreApplication.translate("GHEtool", u"During calculation updating value", None))

#if QT_CONFIG(tooltip)
        self.comboBox_Rb_method.setToolTip(QCoreApplication.translate("GHEtool", u"Profile meanss .....\n"
"depth means ....\n"
"sizing means ....", None))
#endif // QT_CONFIG(tooltip)
        self.label_2.setText("")
        self.label_47.setText("")
        self.label_fluid_data.setText(QCoreApplication.translate("GHEtool", u"Fluid data", None))
        self.label_fluid_thermal_capacity.setText(QCoreApplication.translate("GHEtool", u"Thermal capacity [J/kg K]:", None))
        self.label_fluid_mass_flow_rate.setText(QCoreApplication.translate("GHEtool", u"Mass flow rate [kg/s]: ", None))
        self.label_fluid_lambda.setText(QCoreApplication.translate("GHEtool", u"Thermal conductivity [W/mK]: ", None))
        self.label_fluid_density.setText(QCoreApplication.translate("GHEtool", u"Density [kg/m\u00b3]:", None))
        self.label_fluid_viscosity.setText(QCoreApplication.translate("GHEtool", u"Dynamic viscosity [Pa s]:", None))
        self.label_48.setText("")
        self.label_pipe_data.setText(QCoreApplication.translate("GHEtool", u"Pipe data", None))
        self.label_NumberOfPipes.setText(QCoreApplication.translate("GHEtool", u"Number of pipes [#]:", None))
        self.label_grout_conductivity.setText(QCoreApplication.translate("GHEtool", u"Grout thermal conductivity [W/mK]: ", None))
        self.label_pipe_conductivity.setText(QCoreApplication.translate("GHEtool", u"Pipe thermal conductivity [W/mK]: ", None))
        self.label_pipe_outer_radius.setText(QCoreApplication.translate("GHEtool", u"Outer pipe radius [m]: ", None))
        self.label_pipe_inner_radius.setText(QCoreApplication.translate("GHEtool", u"Inner pipe radius [m]: ", None))
        self.label_borehole_radius.setText(QCoreApplication.translate("GHEtool", u"Borehole radius [m]:", None))
        self.label_pipe_distance.setText(QCoreApplication.translate("GHEtool", u"Distance of pipe until center [m]:", None))
        self.label_pipe_roughness.setText(QCoreApplication.translate("GHEtool", u"Pipe roughness [m]:", None))
        self.label_borehole_burial_depth.setText(QCoreApplication.translate("GHEtool", u"Burial depth [m]:", None))
        self.label_63.setText("")
        self.pushButton_PreviousResistance.setText(QCoreApplication.translate("GHEtool", u"  previous  ", None))
        self.pushButton_NextResistance.setText(QCoreApplication.translate("GHEtool", u"  next  ", None))
        self.label_ThermalDemandsTitle.setText(QCoreApplication.translate("GHEtool", u"Thermal demands", None))
        self.label_40.setText("")
        self.label_Import.setText(QCoreApplication.translate("GHEtool", u"Import", None))
        self.checkBox_Import.setText(QCoreApplication.translate("GHEtool", u"Import Demands?", None))
        self.label_DataType.setText(QCoreApplication.translate("GHEtool", u"File type: ", None))
        self.comboBox_Datentyp.setItemText(0, QCoreApplication.translate("GHEtool", u".csv", None))
        self.comboBox_Datentyp.setItemText(1, QCoreApplication.translate("GHEtool", u".xlsx", None))
        self.comboBox_Datentyp.setItemText(2, QCoreApplication.translate("GHEtool", u".xls", None))

        self.comboBox_Datentyp.setCurrentText(QCoreApplication.translate("GHEtool", u".csv", None))
        self.comboBox_Datentyp.setProperty("placeholderText", QCoreApplication.translate("GHEtool", u"choose your file ...", None))
        self.label_Filename.setText(QCoreApplication.translate("GHEtool", u"Filename: ", None))
        self.lineEdit_displayCsv.setText("")
        self.pushButton_loadCsv.setText(QCoreApplication.translate("GHEtool", u"...", None))
        self.label_Seperator.setText(QCoreApplication.translate("GHEtool", u"Seperator in CSV-file:", None))
        self.comboBox_Seperator.setItemText(0, QCoreApplication.translate("GHEtool", u"Semicolon ';'", None))
        self.comboBox_Seperator.setItemText(1, QCoreApplication.translate("GHEtool", u"Comma ','", None))

        self.label_decimal.setText(QCoreApplication.translate("GHEtool", u"Decimal sign in CSV-file:", None))
        self.comboBox_decimal.setItemText(0, QCoreApplication.translate("GHEtool", u"Point '.'", None))
        self.comboBox_decimal.setItemText(1, QCoreApplication.translate("GHEtool", u"Comma ','", None))

        self.label_SheetName.setText(QCoreApplication.translate("GHEtool", u"Sheet Name", None))
        self.comboBox_sheetName.setProperty("placeholderText", QCoreApplication.translate("GHEtool", u"choose your excel sheet name ", None))
        self.pushButton_load.setText(QCoreApplication.translate("GHEtool", u"Load", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_File), QCoreApplication.translate("GHEtool", u"Data file", None))
        self.label_dataColumn.setText(QCoreApplication.translate("GHEtool", u"Thermal demands: ", None))
        self.comboBox_dataColumn.setItemText(0, QCoreApplication.translate("GHEtool", u"2 columns", None))
        self.comboBox_dataColumn.setItemText(1, QCoreApplication.translate("GHEtool", u"1 column", None))

        self.comboBox_dataColumn.setCurrentText(QCoreApplication.translate("GHEtool", u"2 columns", None))
        self.label_HeatingLoadLine.setText(QCoreApplication.translate("GHEtool", u"Heating load line: ", None))
        self.label_CoolingLoadLine.setText(QCoreApplication.translate("GHEtool", u"Cooling load line: ", None))
        self.label_combined.setText(QCoreApplication.translate("GHEtool", u"Load line: ", None))
        self.label_TimeStep.setText(QCoreApplication.translate("GHEtool", u"Time step: ", None))
        self.comboBox_timeStep.setItemText(0, QCoreApplication.translate("GHEtool", u"1 hr.", None))
        self.comboBox_timeStep.setItemText(1, QCoreApplication.translate("GHEtool", u"15 Min.", None))
        self.comboBox_timeStep.setItemText(2, QCoreApplication.translate("GHEtool", u"Auto", None))

        self.comboBox_timeStep.setCurrentText(QCoreApplication.translate("GHEtool", u"1 hr.", None))
        self.label_DateLine.setText(QCoreApplication.translate("GHEtool", u"Date line: ", None))
        self.label_DataUnit.setText(QCoreApplication.translate("GHEtool", u"Unit data: ", None))
        self.comboBox_dataUnit.setItemText(0, QCoreApplication.translate("GHEtool", u"W", None))
        self.comboBox_dataUnit.setItemText(1, QCoreApplication.translate("GHEtool", u"kW", None))
        self.comboBox_dataUnit.setItemText(2, QCoreApplication.translate("GHEtool", u"MW", None))

        self.comboBox_dataUnit.setCurrentText(QCoreApplication.translate("GHEtool", u"W", None))
        self.pushButton_calculate.setText(QCoreApplication.translate("GHEtool", u"Calculate", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_DataLocation), QCoreApplication.translate("GHEtool", u"Data location in file", None))
        self.label_39.setText("")
        self.label_ThermalDemands.setText(QCoreApplication.translate("GHEtool", u"Thermal demands", None))
        self.label_Oct.setText(QCoreApplication.translate("GHEtool", u"October", None))
        self.label_Aug.setText(QCoreApplication.translate("GHEtool", u"August", None))
        self.label_pH.setText(QCoreApplication.translate("GHEtool", u"Heating peak", None))
        self.label_Unit_pH.setText(QCoreApplication.translate("GHEtool", u"[kW]", None))
        self.label_Jan.setText(QCoreApplication.translate("GHEtool", u"January", None))
        self.label_pC.setText(QCoreApplication.translate("GHEtool", u"Cooling peak", None))
        self.doubleSpinBox_Hp_Jan.setPrefix("")
        self.doubleSpinBox_Hp_Jan.setSuffix("")
        self.label_Sep.setText(QCoreApplication.translate("GHEtool", u"September", None))
        self.label_Unit_HL.setText(QCoreApplication.translate("GHEtool", u"[kWh]", None))
        self.label_Apr.setText(QCoreApplication.translate("GHEtool", u"April", None))
        self.label_Unit_pC.setText(QCoreApplication.translate("GHEtool", u"[kW]", None))
        self.label_Jul.setText(QCoreApplication.translate("GHEtool", u"July", None))
        self.label_Mar.setText(QCoreApplication.translate("GHEtool", u"March", None))
        self.label_Feb.setText(QCoreApplication.translate("GHEtool", u"February", None))
        self.label_Dec.setText(QCoreApplication.translate("GHEtool", u"December", None))
        self.label_HL.setText(QCoreApplication.translate("GHEtool", u"Heating load", None))
        self.label_Jun.setText(QCoreApplication.translate("GHEtool", u"June", None))
        self.label_CL.setText(QCoreApplication.translate("GHEtool", u"Cooling load", None))
        self.label_May.setText(QCoreApplication.translate("GHEtool", u"May", None))
        self.label_Unit_CL.setText(QCoreApplication.translate("GHEtool", u"[kWh]", None))
        self.label_Nov.setText(QCoreApplication.translate("GHEtool", u"November", None))
        self.label_UnitPeak.setText(QCoreApplication.translate("GHEtool", u"Peak unit: ", None))
        self.comboBox_Unit_peak.setItemText(0, QCoreApplication.translate("GHEtool", u"W", None))
        self.comboBox_Unit_peak.setItemText(1, QCoreApplication.translate("GHEtool", u"kW", None))
        self.comboBox_Unit_peak.setItemText(2, QCoreApplication.translate("GHEtool", u"MW", None))

        self.comboBox_Unit_peak.setCurrentText(QCoreApplication.translate("GHEtool", u"W", None))
        self.label_UnitLoad.setText(QCoreApplication.translate("GHEtool", u"Load unit: ", None))
        self.comboBox_Unit_Load.setItemText(0, QCoreApplication.translate("GHEtool", u"Wh", None))
        self.comboBox_Unit_Load.setItemText(1, QCoreApplication.translate("GHEtool", u"kWh", None))
        self.comboBox_Unit_Load.setItemText(2, QCoreApplication.translate("GHEtool", u"MWh", None))

        self.comboBox_Unit_Load.setCurrentText(QCoreApplication.translate("GHEtool", u"Wh", None))
        self.pushButton_Unit.setText(QCoreApplication.translate("GHEtool", u"OK", None))
        self.label_51.setText("")
        self.label_data_file.setText(QCoreApplication.translate("GHEtool", u"Select data file", None))
        self.label_SeperatorDataFile.setText(QCoreApplication.translate("GHEtool", u"Seperator in CSV-file:", None))
        self.comboBox_SeperatorDataFile.setItemText(0, QCoreApplication.translate("GHEtool", u"Semicolon ';'", None))
        self.comboBox_SeperatorDataFile.setItemText(1, QCoreApplication.translate("GHEtool", u"Comma ','", None))

        self.label_decimalDataFile.setText(QCoreApplication.translate("GHEtool", u"Decimal sign in CSV-file:", None))
        self.comboBox_decimalDataFile.setItemText(0, QCoreApplication.translate("GHEtool", u"Point '.'", None))
        self.comboBox_decimalDataFile.setItemText(1, QCoreApplication.translate("GHEtool", u"Comma ','", None))

        self.label_Filename_2.setText(QCoreApplication.translate("GHEtool", u"Filename: ", None))
        self.lineEdit_filename_data_file.setText("")
        self.pushButton_data_file_select.setText(QCoreApplication.translate("GHEtool", u"...", None))
        self.label_dataColumn_2.setText(QCoreApplication.translate("GHEtool", u"Thermal demands: ", None))
        self.comboBox_dataColumn_data_file.setItemText(0, QCoreApplication.translate("GHEtool", u"2 columns", None))
        self.comboBox_dataColumn_data_file.setItemText(1, QCoreApplication.translate("GHEtool", u"1 column", None))

        self.comboBox_dataColumn_data_file.setCurrentText(QCoreApplication.translate("GHEtool", u"2 columns", None))
        self.label_HeatingLoadLine_2.setText(QCoreApplication.translate("GHEtool", u"Heating load line: ", None))
        self.label_CoolingLoadLine_2.setText(QCoreApplication.translate("GHEtool", u"Cooling load line: ", None))
        self.label_combined_2.setText(QCoreApplication.translate("GHEtool", u"Load line: ", None))
        self.label_DataUnit_2.setText(QCoreApplication.translate("GHEtool", u"Unit data: ", None))
        self.comboBox_dataUnit_data_file.setItemText(0, QCoreApplication.translate("GHEtool", u"W", None))
        self.comboBox_dataUnit_data_file.setItemText(1, QCoreApplication.translate("GHEtool", u"kW", None))
        self.comboBox_dataUnit_data_file.setItemText(2, QCoreApplication.translate("GHEtool", u"MW", None))

        self.comboBox_dataUnit_data_file.setCurrentText(QCoreApplication.translate("GHEtool", u"W", None))
        self.label_43.setText("")
        self.pushButton_PreviousThermal.setText(QCoreApplication.translate("GHEtool", u"  previous  ", None))
        self.checkBox_Legend.setText(QCoreApplication.translate("GHEtool", u"Show Legend?", None))
        self.label_Size.setText(QCoreApplication.translate("GHEtool", u"Size", None))
        self.pushButton_SaveData.setText(QCoreApplication.translate("GHEtool", u"Save results", None))
        self.pushButton_SaveFigure.setText(QCoreApplication.translate("GHEtool", u"Save figure", None))
        self.label_WarningDepth.setText(QCoreApplication.translate("GHEtool", u"The calculated size is below the suggested minimum of 15 m. The calculation may be incorrect.", None))
        self.label_Settings.setText(QCoreApplication.translate("GHEtool", u"Settings", None))
        self.label_42.setText("")
        self.label_Language_Head.setText(QCoreApplication.translate("GHEtool", u"Language", None))
        self.label_Language.setText(QCoreApplication.translate("GHEtool", u"Language", None))
        self.label_50.setText("")
        self.label_Scenario_Head.setText(QCoreApplication.translate("GHEtool", u"Scenario saving settings", None))
        self.checkBox_AutoSaving.setText(QCoreApplication.translate("GHEtool", u"Automatic saving", None))
        self.label_Scenario_Hint.setText(QCoreApplication.translate("GHEtool", u"If Auto saving is selected the scenario will automatically saved if a scenario is changed. Otherwise the scenario has to be saved with the Update scenario butten in the upper left corner if the changes should not be lost. ", None))
        self.label_Status.setText(QCoreApplication.translate("GHEtool", u"Progress: ", None))
        self.pushButton_start_single.setText(QCoreApplication.translate("GHEtool", u"Calculate current scenario", None))
        self.pushButton_start_multiple.setText(QCoreApplication.translate("GHEtool", u"Calculate all scenarios", None))
        self.pushButton_Cancel.setText(QCoreApplication.translate("GHEtool", u"Exit", None))
        self.menuFile.setTitle(QCoreApplication.translate("GHEtool", u"File", None))
        self.menuCalculation.setTitle(QCoreApplication.translate("GHEtool", u"Calculation", None))
        self.menuSettings.setTitle(QCoreApplication.translate("GHEtool", u"Settings", None))
        self.menuLanguage.setTitle(QCoreApplication.translate("GHEtool", u"Language", None))
        self.menuScenario.setTitle(QCoreApplication.translate("GHEtool", u"Scenario", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("GHEtool", u"toolBar", None))
    # retranslateUi

