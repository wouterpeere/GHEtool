from sys import exit as sys_exit
from typing import Optional
from Translation_class import TrClass
from PyQt5.QtWidgets import QWidget as QtWidgets_QWidget, QApplication as QtWidgets_QApplication, \
    QMainWindow as QtWidgets_QMainWindow, QPushButton as QtWidgets_QPushButton,\
    QDoubleSpinBox as QtWidgets_QDoubleSpinBox, QMessageBox as QtWidgets_QMessageBox, \
    QFileDialog as QtWidgets_QFileDialog
from PyQt5.QtGui import QIcon as QtGui_QIcon
from PyQt5.QtCore import QSize as QtCore_QSize, QEvent as QtCore_QEvent, QThread as QtCore_QThread, \
    pyqtSignal as QtCore_pyqtSignal
from ui.gui import Ui_GHEtool


# Create Data storage class to store the input and output variables
class DataStorage:
    __slots__ = 'H', 'B', 'k_s', 'Tg', 'Rb', 'N_1', 'N_2', 'T_max', 'T_min', 'simulationPeriod', 'peakHeating', \
                'peakCooling', 'monthlyLoadHeating', 'monthlyLoadHeating', 'monthlyLoadCooling', 'borefield', 'ui',\
                'DetermineDepth', 'unitDemand', 'unitPeak', 'FactorDemand', 'FactorPeak'

    # init class and store input data
    def __init__(self, ui: int):
        from ctypes import cast as ctypes_cast, py_object as ctypes_py_object
        from GHEtool import Borefield
        # get ui
        self.ui = ui
        obj = ctypes_cast(self.ui, ctypes_py_object).value
        # get values from GUI

        self.H: float = getattr(obj, 'doubleSpinBox_H').value()  # m
        self.B: float = getattr(obj, 'doubleSpinBox_B').value()  # m
        self.k_s: float = getattr(obj, 'doubleSpinBox_k_s').value()  # W/mK
        self.Tg: float = getattr(obj, 'doubleSpinBox_Tg').value()  # °C
        self.Rb: float = getattr(obj, 'doubleSpinBox_Rb').value()  # mK/W
        self.N_1: int = getattr(obj, 'spinBox_N_1').value()  # #
        self.N_2: int = getattr(obj, 'spinBox_N_2').value()  # #
        self.T_max: float = getattr(obj, 'doubleSpinBox_TMax').value()  # °C
        self.T_min: float = getattr(obj, 'doubleSpinBox_TMin').value()  # °C
        self.simulationPeriod: int = getattr(obj, 'spinBox_Years').value()  # years
        self.DetermineDepth: bool = getattr(obj, 'checkBox_CalcDepth').isChecked()  # boolean
        self.unitPeak: str = getattr(obj, 'label_Unit_pH').text()
        self.unitDemand: str = getattr(obj, 'label_Unit_HL').text()
        uP = self.unitPeak[1:-1]
        uD = self.unitDemand[1:-1]
        self.FactorPeak: float = 1 if uP == 'kW' else 0.001 if uP == 'W' else 1000
        self.FactorDemand: float = 1 if uD == 'kWh' else 0.001 if uD == 'Wh' else 1000

        # Monthly loading values
        self.peakHeating: list = [getattr(obj, 'doubleSpinBox_Hp_Jan').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Hp_Feb').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Hp_Mar').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Hp_Apr').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Hp_May').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Hp_Jun').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Hp_Jul').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Hp_Aug').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Hp_Sep').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Hp_Oct').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Hp_Nov').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Hp_Dec').value() * self.FactorPeak]  # kW

        self.peakCooling: list = [getattr(obj, 'doubleSpinBox_Cp_Jan').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Cp_Feb').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Cp_Mar').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Cp_Apr').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Cp_May').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Cp_Jun').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Cp_Jul').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Cp_Aug').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Cp_Sep').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Cp_Oct').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Cp_Nov').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Cp_Dec').value() * self.FactorPeak]  # kW

        # percentage of annual load per month (15.5% for January ...)
        self.monthlyLoadHeating: list = [getattr(obj, 'doubleSpinBox_HL_Jan').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_HL_Feb').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_HL_Mar').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_HL_Apr').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_HL_May').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_HL_Jun').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_HL_Jul').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_HL_Aug').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_HL_Sep').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_HL_Oct').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_HL_Nov').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_HL_Dec').value() * self.FactorDemand]  # kWh

        self.monthlyLoadCooling: list = [getattr(obj, 'doubleSpinBox_CL_Jan').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_CL_Feb').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_CL_Mar').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_CL_Apr').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_CL_May').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_CL_Jun').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_CL_Jul').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_CL_Aug').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_CL_Sep').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_CL_Oct').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_CL_Nov').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_CL_Dec').value() * self.FactorDemand]  # kWh

        self.borefield: Optional[Borefield, None] = None

    # set stored data to gui fields
    def setValues(self):
        from ctypes import cast as ctypes_cast, py_object as ctypes_py_object
        obj = ctypes_cast(self.ui, ctypes_py_object).value
        getattr(obj, 'doubleSpinBox_H').setValue(self.H)  # m
        getattr(obj, 'doubleSpinBox_B').setValue(self.B)  # m
        getattr(obj, 'doubleSpinBox_k_s').setValue(self.k_s)  # W/mK
        getattr(obj, 'doubleSpinBox_Tg').setValue(self.Tg)  # °C
        getattr(obj, 'doubleSpinBox_Rb').setValue(self.Rb)  # mK/W
        getattr(obj, 'spinBox_N_1').setValue(self.N_1)  # #
        getattr(obj, 'spinBox_N_2').setValue(self.N_2)  # #
        getattr(obj, 'doubleSpinBox_TMax').setValue(self.T_max)  # °C
        getattr(obj, 'doubleSpinBox_TMin').setValue(self.T_min)  # °C
        getattr(obj, 'spinBox_Years').setValue(self.simulationPeriod)  # years
        getattr(obj, 'checkBox_CalcDepth').setChecked(self.DetermineDepth)  # boolean
        getattr(obj, 'label_Unit_pH').setText(self.unitPeak)
        getattr(obj, 'label_Unit_pC').setText(self.unitPeak)
        getattr(obj, 'label_Unit_HL').setText(self.unitDemand)
        getattr(obj, 'label_Unit_CL').setText(self.unitDemand)

        # Monthly loading values
        getattr(obj, 'doubleSpinBox_Hp_Jan').setValue(self.peakHeating[0] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Hp_Feb').setValue(self.peakHeating[1] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Hp_Mar').setValue(self.peakHeating[2] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Hp_Apr').setValue(self.peakHeating[3] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Hp_May').setValue(self.peakHeating[4] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Hp_Jun').setValue(self.peakHeating[5] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Hp_Jul').setValue(self.peakHeating[6] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Hp_Aug').setValue(self.peakHeating[7] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Hp_Sep').setValue(self.peakHeating[8] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Hp_Oct').setValue(self.peakHeating[9] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Hp_Nov').setValue(self.peakHeating[10] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Hp_Dec').setValue(self.peakHeating[11] / self.FactorPeak)

        getattr(obj, 'doubleSpinBox_Cp_Jan').setValue(self.peakCooling[0] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Cp_Feb').setValue(self.peakCooling[1] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Cp_Mar').setValue(self.peakCooling[2] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Cp_Apr').setValue(self.peakCooling[3] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Cp_May').setValue(self.peakCooling[4] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Cp_Jun').setValue(self.peakCooling[5] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Cp_Jul').setValue(self.peakCooling[6] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Cp_Aug').setValue(self.peakCooling[7] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Cp_Sep').setValue(self.peakCooling[8] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Cp_Oct').setValue(self.peakCooling[9] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Cp_Nov').setValue(self.peakCooling[10] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Cp_Dec').setValue(self.peakCooling[11] / self.FactorPeak)

        # percentage of annual load per month (15.5% for January ...)
        getattr(obj, 'doubleSpinBox_HL_Jan').setValue(self.monthlyLoadHeating[0] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_HL_Feb').setValue(self.monthlyLoadHeating[1] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_HL_Mar').setValue(self.monthlyLoadHeating[2] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_HL_Apr').setValue(self.monthlyLoadHeating[3] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_HL_May').setValue(self.monthlyLoadHeating[4] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_HL_Jun').setValue(self.monthlyLoadHeating[5] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_HL_Jul').setValue(self.monthlyLoadHeating[6] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_HL_Aug').setValue(self.monthlyLoadHeating[7] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_HL_Sep').setValue(self.monthlyLoadHeating[8] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_HL_Oct').setValue(self.monthlyLoadHeating[9] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_HL_Nov').setValue(self.monthlyLoadHeating[10] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_HL_Dec').setValue(self.monthlyLoadHeating[11] / self.FactorDemand)

        getattr(obj, 'doubleSpinBox_CL_Jan').setValue(self.monthlyLoadCooling[0] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_CL_Feb').setValue(self.monthlyLoadCooling[1] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_CL_Mar').setValue(self.monthlyLoadCooling[2] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_CL_Apr').setValue(self.monthlyLoadCooling[3] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_CL_May').setValue(self.monthlyLoadCooling[4] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_CL_Jun').setValue(self.monthlyLoadCooling[5] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_CL_Jul').setValue(self.monthlyLoadCooling[6] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_CL_Aug').setValue(self.monthlyLoadCooling[7] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_CL_Sep').setValue(self.monthlyLoadCooling[8] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_CL_Oct').setValue(self.monthlyLoadCooling[9] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_CL_Nov').setValue(self.monthlyLoadCooling[10] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_CL_Dec').setValue(self.monthlyLoadCooling[11] / self.FactorDemand)


# main GUI class
class MainWindow(QtWidgets_QMainWindow, Ui_GHEtool):

    # initialize window
    def __init__(self, Dialog: QtWidgets_QWidget, app: QtWidgets_QApplication):
        # init windows
        super(MainWindow, self).__init__()
        super().setupUi(Dialog)
        self.app: QtWidgets_QApplication = app
        self.Dia = Dialog
        self.translations: TrClass = TrClass()
        self.file = None
        # init links from buttons to functions
        self.pushButton_Start.clicked.connect(self.checkStart)
        self.pushButton_Cancel.clicked.connect(self.checkCancel)
        self.pushButton_thermalDemands.clicked.connect(self.changeToThermalPage)
        self.pushButton_Results.clicked.connect(self.changeToResultsPage)
        self.checkBox_CalcDepth.clicked.connect(self.checkDetermineDepth)
        self.pushButton_General.clicked.connect(self.changeToGeneralPage)
        self.pushButton_SaveFigure.clicked.connect(self.SaveFigure)
        self.pushButton_SaveData.clicked.connect(self.SaveData)
        self.comboBox_Scenario.currentIndexChanged.connect(self.ChangeScenario)
        self.pushButton_AddScenario.clicked.connect(self.AddScenario)
        self.pushButton_SaveScenario.clicked.connect(self.SaveScenario)
        self.pushButton_DeleteScenario.clicked.connect(self.DeleteScenario)
        self.pushButton_SaveScenariosExternal.clicked.connect(self.funSave)
        self.pushButton_LoadScenarios.clicked.connect(self.funLoad)
        self.checkBox_Legend.clicked.connect(self.checkLegend)
        self.pushButton_NextGeneral.clicked.connect(self.changeToThermalPage)
        self.pushButton_PreviousThermal.clicked.connect(self.changeToGeneralPage)
        self.comboBox_Language.currentIndexChanged.connect(self.change_Language)
        self.comboBox_Datentyp.currentIndexChanged.connect(self.dataType)
        self.pushButton_loadCsv.clicked.connect(self.funChooseFile)
        # TODO: Connecting Load Push Button to New Function that create Excel Object and display the sheet name
        self.pushButton_load.clicked.connect(self.funLoadFile)
        # TODO: 1. Create New funChooseColumn() function
        self.comboBox_dataColumn.currentIndexChanged.connect(self.funChooseColumnDemand)
        self.comboBox_timeStep.currentIndexChanged.connect(self.funChooseColumnTimeStep)
        # TODO: New Calculate Button
        self.pushButton_calculate.clicked.connect(self.funDisplayData)
        self.pushButton_Einheit.clicked.connect(self.funChangeUnit)
        self.checkBox_Import.clicked.connect(self.HideImport)
        # hide results buttons
        self.pushButton_Results.hide()
        self.pushButton_SaveFigure.hide()
        self.pushButton_SaveData.hide()
        # initialize so far unused variables
        self.ax = None  # axes of figure
        self.canvas = None  # canvas class of figure
        self.fig = None  # figure
        self.NumberOfScenarios: int = 1  # number of scenarios
        self.finished: int = 1  # number of finished scenarios
        self.threads: list = []  # list of calculation threads
        self.ListDS: list = []  # list of data storages
        # set start page to settings page
        self.stackedWidget.setCurrentWidget(self.page_General)
        # reset progress bar
        self.updateBar(0, False)
        # set language options and link them to the comboBox
        options = ([('English', ''), ('Deutsch', 'eng-de')])  # , ('Russian', 'en-ru'), ('Spanish', 'en-es'),
        # ('Chinese', 'en-zh'), ('French', 'en-fr'), ('Bahasa Indonesia', 'en-id')])
        for i, (text, lang) in enumerate(options):
            self.comboBox_Language.addItem(text)
            self.comboBox_Language.setItemData(i, lang)
        from IconClass import IconClass
        IC = IconClass()

        self.pushButton_NextGeneral.setIcon(IC.ArrowRight2)
        self.pushButton_PreviousThermal.setIcon(IC.ArrowLeft2)
        self.pushButton_Cancel.setIcon(IC.Exit)
        self.pushButton_Start.setIcon(IC.Start)
        self.pushButton_SaveScenariosExternal.setIcon(IC.Save)
        self.pushButton_LoadScenarios.setIcon(IC.Load)
        self.pushButton_thermalDemands.setIcon(IC.Thermal)
        self.pushButton_General.setIcon(IC.Earth)
        self.pushButton_Results.setIcon(IC.Result)
        self.pushButton_AddScenario.setIcon(IC.Adder)
        self.pushButton_SaveScenario.setIcon(IC.Update)
        self.pushButton_DeleteScenario.setIcon(IC.Delete)
        self.pushButton_SaveData.setIcon(IC.Save)
        self.pushButton_SaveFigure.setIcon(IC.Save)
        self.pushButton_load.setIcon(IC.Download)
        self.pushButton_calculate.setIcon(IC.Result)

        self.pushButton_General.installEventFilter(self)
        self.pushButton_thermalDemands.installEventFilter(self)
        self.pushButton_Results.installEventFilter(self)
        self.label_GapGenTh.installEventFilter(self)
        self.label_GapThRes.installEventFilter(self)
        # size
        self.sizeB = QtCore_QSize(48, 48)
        self.sizeS = QtCore_QSize(24, 24)
        self.sizePushB = QtCore_QSize(150, 75)
        self.sizePushS = QtCore_QSize(75, 75)

        self.pushButton_Start.setIconSize(self.sizeS)
        self.pushButton_Cancel.setIconSize(self.sizeS)
        self.pushButton_SaveScenariosExternal.setIconSize(self.sizeS)
        self.pushButton_LoadScenarios.setIconSize(self.sizeS)

        self.scenarioStr: str = 'Scenario'
        app_icon = IC.logo
        self.app.setWindowIcon(app_icon)
        self.Dia.setWindowIcon(app_icon)
        self.HideImport()
        self.dataType()
        self.frame_heatingLoad.hide()
        self.frame_coolingLoad.hide()
        self.frame_combined.hide()
        self.SetPush(False)

    def eventFilter(self, object: QtWidgets_QPushButton, event):
        if event.type() == QtCore_QEvent.Enter:
            # Mouse is over the label
            self.SetPush(True)
            return True
        elif event.type() == QtCore_QEvent.Leave:
            # Mouse is not over the label
            self.SetPush(False)
            return True
        return False

    def SetPush(self, MouseOver: bool):
        if MouseOver:
            self.pushButton_General.setText(self.translations.pushButton_General)
            self.pushButton_thermalDemands.setText(self.translations.pushButton_thermalDemands)
            self.pushButton_Results.setText(self.translations.pushButton_Results)
            # setting icon size
            self.pushButton_General.setIconSize(self.sizeS)
            self.pushButton_thermalDemands.setIconSize(self.sizeS)
            self.pushButton_Results.setIconSize(self.sizeS)
            self.pushButton_General.setMaximumSize(self.sizePushB)
            self.pushButton_General.setMinimumSize(self.sizePushB)
            self.pushButton_thermalDemands.setMaximumSize(self.sizePushB)
            self.pushButton_thermalDemands.setMinimumSize(self.sizePushB)
            self.pushButton_Results.setMaximumSize(self.sizePushB)
            self.pushButton_Results.setMinimumSize(self.sizePushB)
            return
        self.pushButton_General.setText('')
        self.pushButton_thermalDemands.setText('')
        self.pushButton_Results.setText('')
        # setting icon size
        self.pushButton_General.setIconSize(self.sizeB)
        self.pushButton_thermalDemands.setIconSize(self.sizeB)
        self.pushButton_Results.setIconSize(self.sizeB)
        self.pushButton_General.setMaximumSize(self.sizePushS)
        self.pushButton_General.setMinimumSize(self.sizePushS)
        self.pushButton_thermalDemands.setMaximumSize(self.sizePushS)
        self.pushButton_thermalDemands.setMinimumSize(self.sizePushS)
        self.pushButton_Results.setMaximumSize(self.sizePushS)
        self.pushButton_Results.setMinimumSize(self.sizePushS)

    @staticmethod
    def DisplayValuesWithFloatingDecimal(spinbox: QtWidgets_QDoubleSpinBox, factor: float):
        value = spinbox.value() * factor
        decimalLoc = 0 if value >= 1_000 else 1 if value >= 100 else 2 if value >= 10 else 3 if value >= 1 else 4
        spinbox.setDecimals(decimalLoc)
        spinbox.setMaximum(max(value*10, 1_000_000))
        spinbox.setValue(value)

    def HideImport(self):
        if self.checkBox_Import.isChecked():
            self.toolBox.show()
            self.toolBox.setCurrentWidget(self.page_File)
            return
        self.toolBox.hide()

    # function to change language on labels and push buttons
    def change_Language(self):
        index = self.comboBox_Language.currentIndex()
        self.translations.ChangeLanguage(index)
        self.label_Language.setText(self.translations.label_Language)
        self.pushButton_SaveScenario.setText(self.translations.pushButton_SaveScenario)
        self.pushButton_AddScenario.setText(self.translations.pushButton_AddScenario)
        self.pushButton_DeleteScenario.setText(self.translations.pushButton_DeleteScenario)
        self.pushButton_Start.setText(self.translations.pushButton_Start)
        self.pushButton_Cancel.setText(self.translations.pushButton_Cancel)
        self.label_Status.setText(self.translations.label_Status)
        self.pushButton_SaveScenariosExternal.setText(self.translations.pushButton_SaveScenariosExternal)
        self.pushButton_LoadScenarios.setText(self.translations.pushButton_LoadScenarios)
        self.label_Borehole_earth.setText(self.translations.label_Borehole_earth)
        self.label_Earth_Properties.setText(self.translations.label_Earth_Properties)
        self.checkBox_CalcDepth.setText(self.translations.checkBox_CalcDepth)
        self.label_H.setText(self.translations.label_H)
        self.label_BS.setText(self.translations.label_BS)
        self.label_lambdaEarth.setText(self.translations.label_lambdaEarth)
        self.label_GroundTemp.setText(self.translations.label_GroundTemp)
        self.label_BoreholeResistance.setText(self.translations.label_BoreholeResistance)
        self.label_WidthField.setText(self.translations.label_WidthField)
        self.label_LengthField.setText(self.translations.label_LengthField)
        self.label_TempConstraints.setText(self.translations.label_TempConstraints)
        self.label_TempMin.setText(self.translations.label_TempMin)
        self.label_TempMax.setText(self.translations.label_TempMax)
        self.label_SimulationTime.setText(self.translations.label_SimulationTime)
        self.pushButton_NextGeneral.setText(self.translations.pushButton_NextGeneral)
        self.pushButton_PreviousThermal.setText(self.translations.pushButton_PreviousThermal)
        self.checkBox_Legend.setText(self.translations.checkBox_Legend)
        self.pushButton_SaveData.setText(self.translations.pushButton_SaveData)
        self.pushButton_SaveFigure.setText(self.translations.pushButton_SaveFigure)
        self.label_ThermalDemandsTitle.setText(self.translations.label_ThermalDemandsTitle)
        self.label_Import.setText(self.translations.label_Import)
        self.checkBox_Import.setText(self.translations.checkBox_Import)
        self.label_ThermalDemands.setText(self.translations.label_ThermalDemands)
        self.label_pH.setText(self.translations.label_pH)
        self.label_pC.setText(self.translations.label_pC)
        self.label_HL.setText(self.translations.label_HL)
        self.label_CL.setText(self.translations.label_CL)
        self.label_UnitPeak.setText(self.translations.label_UnitPeak)
        self.label_UnitLoad.setText(self.translations.label_UnitLoad)
        self.label_Jan.setText(self.translations.label_Jan)
        self.label_Feb.setText(self.translations.label_Feb)
        self.label_Mar.setText(self.translations.label_Mar)
        self.label_Apr.setText(self.translations.label_Apr)
        self.label_May.setText(self.translations.label_May)
        self.label_Jun.setText(self.translations.label_Jun)
        self.label_Jul.setText(self.translations.label_Jul)
        self.label_Aug.setText(self.translations.label_Aug)
        self.label_Sep.setText(self.translations.label_Sep)
        self.label_Oct.setText(self.translations.label_Oct)
        self.label_Nov.setText(self.translations.label_Nov)
        self.label_Dec.setText(self.translations.label_Dec)
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_File), self.translations.page_File)
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_DataLocation), self.translations.page_DataLocation)
        self.label_DataType.setText(self.translations.label_DataType)
        self.label_Filename.setText(self.translations.label_Filename)
        self.label_SheetName.setText(self.translations.label_SheetName)
        self.pushButton_load.setText(self.translations.pushButton_load)
        self.label_dataColumn.setText(self.translations.label_dataColumn)
        self.label_DataUnit.setText(self.translations.label_DataUnit)
        self.label_HeatingLoadLine.setText(self.translations.label_HeatingLoadLine)
        self.label_CoolingLoadLine.setText(self.translations.label_CoolingLoadLine)
        self.label_combined.setText(self.translations.label_combined)
        self.label_TimeStep.setText(self.translations.label_TimeStep)
        self.label_DateLine.setText(self.translations.label_DateLine)
        self.pushButton_calculate.setText(self.translations.pushButton_calculate)
        self.comboBox_dataColumn.clear()
        self.comboBox_dataColumn.addItems(self.translations.comboBox_dataColumn)
        self.comboBox_timeStep.clear()
        self.comboBox_timeStep.addItems(self.translations.comboBox_timeStep)
        self.scenarioStr = self.translations.scenarioStr
        amount: int = self.comboBox_Scenario.count()
        scenarios: list = [f'{self.scenarioStr}: {i}' for i in range(1, amount + 1)]
        self.comboBox_Scenario.clear()
        self.comboBox_Scenario.addItems(scenarios)

    # function to choose Datatype
    def dataType(self):
        index = self.comboBox_Datentyp.currentText()
        # hide labels
        self.lineEdit_displayCsv.setText("")
        self.frame_sheetName.hide()
        self.frame_heatingLoad.hide()
        self.frame_coolingLoad.hide()
        self.frame_date.hide()
        # clear all comboBox
        self.comboBox_sheetName.clear()
        self.comboBox_dataColumn.setCurrentIndex(-1)
        self.comboBox_coolingLoad.clear()
        self.comboBox_heatingLoad.clear()
        self.comboBox_combined.clear()
        self.comboBox_timeStep.setCurrentIndex(-1)

        if index == '.csv':
            pass
        elif index == '.xlsx' or index == '.xls':
            self.frame_sheetName.show()
        else:
            error_dialog = QtWidgets_QMessageBox(QtWidgets_QMessageBox.Warning, self.translations.ErrorMassage,
                                                 self.translations.UnableDataFormat, QtWidgets_QMessageBox.Ok, self.Dia)
            error_dialog.show()
        return index

    # function to choose data file
    def funChooseFile(self):
        try:
            fileIndex = self.comboBox_Datentyp.currentText()
            if fileIndex == '.csv':
                filename = QtWidgets_QFileDialog.getOpenFileName(caption=self.translations.ChooseCSV,
                                                                 filter='(*.csv)')
                self.lineEdit_displayCsv.setText(filename[0])

            elif fileIndex == '.xlsx' or fileIndex == '.xls':
                if fileIndex == '.xlsx':
                    filename = QtWidgets_QFileDialog.getOpenFileName(caption=self.translations.ChooseXLSX,
                                                                     filter='(*.xlsx)')
                else:
                    filename = QtWidgets_QFileDialog.getOpenFileName(caption=self.translations.ChooseXLS,
                                                                     filter='(*.xls)')
                self.lineEdit_displayCsv.setText(filename[0])
                from pandas import ExcelFile as pd_ExcelFile
                # Retrieve the filename
                file = pd_ExcelFile(filename[0])

                # Get the sheet name and let the user choose in the comboBox
                sheet_name = file.sheet_names
                self.comboBox_sheetName.clear()
                self.comboBox_sheetName.addItems(sheet_name)
            else:
                pass
        except FileNotFoundError:
            error_dialog = QtWidgets_QMessageBox(QtWidgets_QMessageBox.Warning, self.translations.ErrorMassage,
                                                 self.translations.NoFileSelected, QtWidgets_QMessageBox.Ok, self.Dia)
            error_dialog.show()

    # function to load data file
    def funLoadFile(self):
        try:
            filename = self.lineEdit_displayCsv.text()
            self.frame_heatingLoad.hide()
            self.frame_coolingLoad.hide()
            self.frame_date.hide()
            # clear all comboBox
            self.comboBox_dataColumn.setCurrentIndex(-1)
            self.comboBox_coolingLoad.clear()
            self.comboBox_heatingLoad.clear()
            self.comboBox_combined.clear()
            self.comboBox_timeStep.setCurrentIndex(-1)
            import time
            dt1 = time.process_time()
            if ".xlsx" in filename:
                sheet_name = self.comboBox_sheetName.currentText()
                from pandas import read_excel as pd_read_excel
                df = pd_read_excel(filename, sheet_name=sheet_name, nrows=1)

            elif ".csv" in filename:
                from pandas import read_csv as pd_read_csv
                df = pd_read_csv(filename, nrows=1)
            else:
                df = None
            dt2 = time.process_time()
            print(dt2-dt1)
            self.toolBox.setCurrentWidget(self.page_DataLocation)
            # Make the filename a Global variable so that it only load once
            self.file = df
        except FileNotFoundError:
            error_dialog = QtWidgets_QMessageBox(QtWidgets_QMessageBox.Warning, self.translations.ErrorMassage,
                                                 self.translations.NoFileSelected, QtWidgets_QMessageBox.Ok, self.Dia)
            error_dialog.show()

    # Choose Column which includes the demand
    def funChooseColumnDemand(self):
        df = self.file
        columns: list = [''] if df is None else df.columns

        self.frame_heatingLoad.hide()
        self.frame_coolingLoad.hide()
        self.frame_combined.hide()
        self.comboBox_heatingLoad.clear()
        self.comboBox_coolingLoad.clear()
        self.comboBox_combined.clear()
        text: int = self.comboBox_dataColumn.currentIndex()

        if text == 0:
            self.frame_heatingLoad.show()
            self.frame_coolingLoad.show()
            self.comboBox_heatingLoad.addItems(columns)
            self.comboBox_coolingLoad.addItems(columns)
        elif text == 1:
            self.frame_combined.show()
            self.comboBox_combined.addItems(columns)

    # Choose Column which includes the time step
    def funChooseColumnTimeStep(self):
        df = self.file
        columns = [''] if df is None else df.columns

        self.frame_date.hide()
        self.comboBox_date.clear()

        idx: int = self.comboBox_timeStep.currentIndex()

        if idx == 2:
            self.comboBox_date.addItems(columns)
            self.frame_date.show()

    # Load the Data to Display in the GUI
    def funDisplayData(self):
        try:
            # Alle eingegebene Daten auffassen
            filename: str = self.lineEdit_displayCsv.text()
            if filename == '':
                raise FileNotFoundError
            thermaldemand: int = self.comboBox_dataColumn.currentIndex()

            # Generate the column that have to be imported
            cols: list = []
            heatingLoad: str = self.comboBox_heatingLoad.currentText()
            if len(heatingLoad) >= 1:
                cols.append(heatingLoad)
            coolingLoad: str = self.comboBox_coolingLoad.currentText()
            if len(coolingLoad) >= 1:
                cols.append(coolingLoad)
            combined: str = self.comboBox_combined.currentText()
            if len(combined) >= 1:
                cols.append(combined)
            date: str = self.comboBox_date.currentText()
            if len(date) >= 1:
                cols.append(date)
            else:
                date: str = 'Date'

            if ".xlsx" in filename:
                from pandas import read_excel as pd_read_excel
                sheet_name = self.comboBox_sheetName.currentText()
                df2 = pd_read_excel(filename, sheet_name=sheet_name, usecols=cols)

            elif ".csv" in filename:
                from pandas import read_csv as pd_read_csv
                df2 = pd_read_csv(filename, usecols=cols)
            else:
                df2 = None

            # ---------------------- Time Step Section  ----------------------
            timeStepIdx = self.comboBox_timeStep.currentIndex()

            if timeStepIdx == 0:  # 1 hour
                # Define start and end date
                from pandas import to_datetime as pd_to_datetime, Series as pd_Series, date_range as pd_date_range
                start = pd_to_datetime("2019-01-01 00:00:00")
                end = pd_to_datetime("2019-12-31 23:59:00")
                df2[date] = pd_Series(pd_date_range(start, end, freq="1H"))
                dictAgg: Optional[None, dict] = None
            elif timeStepIdx == 1:  # 15 minute timestep
                from pandas import to_datetime as pd_to_datetime, Series as pd_Series, date_range as pd_date_range
                start = pd_to_datetime("2019-01-01 00:00:00")
                end = pd_to_datetime("2019-12-31 23:59:00")
                df2[date] = pd_Series(pd_date_range(start, end, freq="15T"))
                dictAgg: Optional[None, dict] = {combined: 'mean'} if thermaldemand == 1 else {heatingLoad: 'mean',
                                                                                               coolingLoad: 'mean'}
            else:
                from pandas import to_datetime as pd_to_datetime
                df2[date] = pd_to_datetime(df2[date])
                dictAgg: Optional[None, dict] = {combined: 'mean'} if thermaldemand == 1 else {heatingLoad: 'mean',
                                                                                               coolingLoad: 'mean'}
            df2.set_index(date, inplace=True)
            df2 = df2 if dictAgg is None else df2.resample("H").agg(dictAgg)

            # ------------------- Calculate Section --------------------
            # Choose path between Single or Combined Column
            if thermaldemand == 0:
                # Resample the Data for peakHeating and peakCooling
                df2.rename(columns={heatingLoad: "Heating Load", coolingLoad: "Cooling Load"}, inplace=True)
                df2["peak Heating"] = df2["Heating Load"]
                df2["peak Cooling"] = df2["Cooling Load"]
                # self.write_filename = "single_output.csv"

            elif thermaldemand == 1:
                # Create Filter for heating and cooling load ( Heating Load +, Cooling Load -)
                heatingLoad = df2[combined].apply(lambda x: x >= 0)
                coolingLoad = df2[combined].apply(lambda x: x < 0)
                df2["Heating Load"] = df2.loc[heatingLoad, combined]
                df2["Cooling Load"] = df2.loc[coolingLoad, combined] * -1
                df2["peak Heating"] = df2["Heating Load"]
                df2["peak Cooling"] = df2["Cooling Load"]
                # self.write_filename = "combi_output.csv"

            df3 = df2.resample("M").agg({"Heating Load": "sum", "Cooling Load": "sum",
                                         "peak Heating": "max", "peak Cooling": "max"})
            # TODO: https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects
            #       https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior

            # ----------------------- Data Unit Section --------------------------
            # Get the Data Unit and set the label in the thermal Demand Box to follow
            dataUnit = self.comboBox_dataUnit.currentText()

            # Faktor ertsmal definieren
            if dataUnit == 'W':
                fac = 1
            elif dataUnit == 'kW':
                fac = 0.001
            elif dataUnit == 'MW':
                fac = 0.000001
            else:
                fac = 0

            self.label_Unit_pH.setText(f'[kW]')
            self.label_Unit_pC.setText(f'[kW]')
            self.label_Unit_HL.setText(f'[kWh]')
            self.label_Unit_CL.setText(f'[kWh]')

            df3 = df3 * fac
            peakHeating = df3["peak Heating"]
            peakCooling = df3["peak Cooling"]
            heatingLoad = df3["Heating Load"]
            coolingLoad = df3["Cooling Load"]

            self.doubleSpinBox_HL_Jan.setValue(heatingLoad[0])
            self.doubleSpinBox_HL_Feb.setValue(heatingLoad[1])
            self.doubleSpinBox_HL_Mar.setValue(heatingLoad[2])
            self.doubleSpinBox_HL_Apr.setValue(heatingLoad[3])
            self.doubleSpinBox_HL_May.setValue(heatingLoad[4])
            self.doubleSpinBox_HL_Jun.setValue(heatingLoad[5])
            self.doubleSpinBox_HL_Jul.setValue(heatingLoad[6])
            self.doubleSpinBox_HL_Aug.setValue(heatingLoad[7])
            self.doubleSpinBox_HL_Sep.setValue(heatingLoad[8])
            self.doubleSpinBox_HL_Oct.setValue(heatingLoad[9])
            self.doubleSpinBox_HL_Nov.setValue(heatingLoad[10])
            self.doubleSpinBox_HL_Dec.setValue(heatingLoad[11])

            self.doubleSpinBox_CL_Jan.setValue(coolingLoad[0])
            self.doubleSpinBox_CL_Feb.setValue(coolingLoad[1])
            self.doubleSpinBox_CL_Mar.setValue(coolingLoad[2])
            self.doubleSpinBox_CL_Apr.setValue(coolingLoad[3])
            self.doubleSpinBox_CL_May.setValue(coolingLoad[4])
            self.doubleSpinBox_CL_Jun.setValue(coolingLoad[5])
            self.doubleSpinBox_CL_Jul.setValue(coolingLoad[6])
            self.doubleSpinBox_CL_Aug.setValue(coolingLoad[7])
            self.doubleSpinBox_CL_Sep.setValue(coolingLoad[8])
            self.doubleSpinBox_CL_Oct.setValue(coolingLoad[9])
            self.doubleSpinBox_CL_Nov.setValue(coolingLoad[10])
            self.doubleSpinBox_CL_Dec.setValue(coolingLoad[11])

            self.doubleSpinBox_Hp_Jan.setValue(peakHeating[0])
            self.doubleSpinBox_Hp_Feb.setValue(peakHeating[1])
            self.doubleSpinBox_Hp_Mar.setValue(peakHeating[2])
            self.doubleSpinBox_Hp_Apr.setValue(peakHeating[3])
            self.doubleSpinBox_Hp_May.setValue(peakHeating[4])
            self.doubleSpinBox_Hp_Jun.setValue(peakHeating[5])
            self.doubleSpinBox_Hp_Jul.setValue(peakHeating[6])
            self.doubleSpinBox_Hp_Aug.setValue(peakHeating[7])
            self.doubleSpinBox_Hp_Sep.setValue(peakHeating[8])
            self.doubleSpinBox_Hp_Oct.setValue(peakHeating[9])
            self.doubleSpinBox_Hp_Nov.setValue(peakHeating[10])
            self.doubleSpinBox_Hp_Dec.setValue(peakHeating[11])

            self.doubleSpinBox_Cp_Jan.setValue(peakCooling[0])
            self.doubleSpinBox_Cp_Feb.setValue(peakCooling[1])
            self.doubleSpinBox_Cp_Mar.setValue(peakCooling[2])
            self.doubleSpinBox_Cp_Apr.setValue(peakCooling[3])
            self.doubleSpinBox_Cp_May.setValue(peakCooling[4])
            self.doubleSpinBox_Cp_Jun.setValue(peakCooling[5])
            self.doubleSpinBox_Cp_Jul.setValue(peakCooling[6])
            self.doubleSpinBox_Cp_Aug.setValue(peakCooling[7])
            self.doubleSpinBox_Cp_Sep.setValue(peakCooling[8])
            self.doubleSpinBox_Cp_Oct.setValue(peakCooling[9])
            self.doubleSpinBox_Cp_Nov.setValue(peakCooling[10])
            self.doubleSpinBox_Cp_Dec.setValue(peakCooling[11])

            # write csv
            # folder = os.path.join(os.path.dirname(__file__), "Excel")
            # output = os.path.join(folder, self.write_filename)
            # df2.to_csv(output)

        except FileNotFoundError:
            error_dialog = QtWidgets_QMessageBox(QtWidgets_QMessageBox.Warning, self.translations.ErrorMassage,
                                                 self.translations.NoFileSelected, QtWidgets_QMessageBox.Ok, self.Dia)
            error_dialog.show()
        except IndexError:
            error_dialog = QtWidgets_QMessageBox(QtWidgets_QMessageBox.Warning, self.translations.ErrorMassage,
                                                 self.translations.ValueError, QtWidgets_QMessageBox.Ok,
                                                 self.Dia)
            error_dialog.show()
        except KeyError:
            error_dialog = QtWidgets_QMessageBox(QtWidgets_QMessageBox.Warning, self.translations.ErrorMassage,
                                                 self.translations.ColumnError, QtWidgets_QMessageBox.Ok,
                                                 self.Dia)
            error_dialog.show()

    # function to change the unit
    def funChangeUnit(self):
        # Umfaktorierung von comboBox im Thermal Demand Box
        peakNew = self.comboBox_Unit_peak.currentText()
        LoadNew = self.comboBox_Unit_Load.currentText()
        peakOld = self.label_Unit_pH.text()
        peakOld = peakOld.replace('[', '')
        peakOld = peakOld.replace(']', '')
        LoadOld = self.label_Unit_HL.text()
        LoadOld = LoadOld.replace('[', '')
        LoadOld = LoadOld.replace(']', '')

        self.label_Unit_HL.setText(f'[{LoadNew}]')
        self.label_Unit_CL.setText(f'[{LoadNew}]')
        self.label_Unit_pH.setText(f'[{peakNew}]')
        self.label_Unit_pC.setText(f'[{peakNew}]')

        if LoadNew == LoadOld:
            factorLoad = 1
        elif LoadOld == 'Wh' and LoadNew == 'MWh':
            factorLoad = 0.000001
        elif (LoadOld == 'Wh' and LoadNew == 'kWh') or (LoadOld == 'kWh' and LoadNew == 'MWh'):
            factorLoad = 0.001
        elif (LoadOld == 'kWh' and LoadNew == 'Wh') or (LoadOld == 'MWh' and LoadNew == 'kWh'):
            factorLoad = 1000
        elif LoadOld == 'MWh' and LoadNew == 'Wh':
            factorLoad = 1000000
        else:
            factorLoad = 0

        if peakOld == peakNew:
            factorPeak = 1
        elif peakOld == 'W' and peakNew == 'MW':
            factorPeak = 0.000_001
        elif (peakOld == 'W' and peakNew == 'kW') or (peakOld == 'kW' and peakNew == 'MW'):
            factorPeak = 0.001
        elif (peakOld == 'kW' and peakNew == 'W') or (peakOld == 'MW' and peakNew == 'kW'):
            factorPeak = 1000
        elif peakOld == 'MW' and peakNew == 'W':
            factorPeak = 1000000
        else:
            factorPeak = 0
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_HL_Jan, factorLoad)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_HL_Feb, factorLoad)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_HL_Mar, factorLoad)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_HL_Apr, factorLoad)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_HL_May, factorLoad)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_HL_Jun, factorLoad)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_HL_Jul, factorLoad)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_HL_Aug, factorLoad)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_HL_Sep, factorLoad)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_HL_Oct, factorLoad)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_HL_Nov, factorLoad)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_HL_Dec, factorLoad)

        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_CL_Jan, factorLoad)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_CL_Feb, factorLoad)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_CL_Mar, factorLoad)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_CL_Apr, factorLoad)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_CL_May, factorLoad)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_CL_Jun, factorLoad)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_CL_Jul, factorLoad)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_CL_Aug, factorLoad)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_CL_Sep, factorLoad)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_CL_Oct, factorLoad)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_CL_Nov, factorLoad)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_CL_Dec, factorLoad)

        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_Hp_Jan, factorPeak)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_Hp_Feb, factorPeak)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_Hp_Mar, factorPeak)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_Hp_Apr, factorPeak)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_Hp_May, factorPeak)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_Hp_Jun, factorPeak)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_Hp_Jul, factorPeak)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_Hp_Aug, factorPeak)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_Hp_Sep, factorPeak)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_Hp_Oct, factorPeak)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_Hp_Nov, factorPeak)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_Hp_Dec, factorPeak)

        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_Cp_Jan, factorPeak)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_Cp_Feb, factorPeak)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_Cp_Mar, factorPeak)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_Cp_Apr, factorPeak)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_Cp_May, factorPeak)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_Cp_Jun, factorPeak)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_Cp_Jul, factorPeak)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_Cp_Aug, factorPeak)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_Cp_Sep, factorPeak)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_Cp_Oct, factorPeak)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_Cp_Nov, factorPeak)
        self.DisplayValuesWithFloatingDecimal(self.doubleSpinBox_Cp_Dec, factorPeak)

    # function to check if the calculation works
    def funCheck(self, data1, data2):
        from pandas import read_excel as pd_read_excel, read_csv as pd_read_csv, set_option as pd_set_option
        from numpy import where as np_where
        # Basis Results aus Excel importieren
        cols_single = ["Month", "Heating Load", "peak Heating", "Cooling Load", "peak Cooling"]
        cols_combi = ["Month", "Combi_HeatingLoad", "Combi_CoolingLoad", "Combi_peakHeating", "Combi_peakCooling"]
        basis_single = pd_read_excel(data1, sheet_name="Stunde", usecols=cols_single,
                                     skiprows=[1], index_col="Month")
        basis_combi = pd_read_excel(data2, sheet_name="Stunde", usecols=cols_combi,
                                    skiprows=[1], index_col="Month")
        basis_single.dropna(how='any', inplace=True)
        basis_combi.dropna(how='any', inplace=True)

        # Resultsberechnung von Pandas importieren
        result_single = pd_read_csv("Excel/single_output_stunde.csv", index_col=0)
        result_combi = pd_read_csv("Excel/combi_output_stunde.csv", index_col=0)

        # Round them
        basis_single = round(basis_single, 2)  # Excel values as basis for comparison
        basis_combi = round(basis_combi, 2)  # Excel values as basis for comparison
        result_single = round(result_single,
                              2)  # Pandas Calculation Results for Single/Each Column heating and cooling Load
        result_combi = round(result_combi, 2)  # Pandas Calculation Results for Combined Column heating and cooling Load

        # Compare the values
        x = basis_single.values == result_single.values
        y = basis_combi.values == result_combi.values

        print("Excel Single x Pandas Single")
        print(x)
        print("Excel Combined x Pandas Combined")
        print(y)

        rows, cols = np_where(x == False)

        for item in zip(rows, cols):
            basis_single.iloc[item[0], item[1]] = ' {} --> {}'.format(basis_single.iloc[item[0], item[1]],
                                                                      result_single.iloc[item[0], item[1]])

        pd_set_option('display.max_columns', 4)

        print(
            "\nZusammenfassung: \nDie beiden Berechnungsprogrammen haben exakt das gleiche Ergebnis rausbekommen!\nSUPER :)")
        print("---------------------------------------------------------------------------------------------------\n")
        print(basis_single)

    # function to load externally stored scenario
    def funLoad(self):
        from pickle import load as pk_load
        # open interface and get file
        filename = QtWidgets_QFileDialog.getOpenFileName(caption=self.translations.ChoosePKL,
                                                         filter='Pickle (*.pkl)')
        # try to open the file
        try:
            f = open(filename[0], "rb")
            self.ListDS: list = pk_load(f)
            # replace uer window id
            for DS in self.ListDS:
                DS.ui = id(self)
            amount = self.comboBox_Scenario.count()
            # init user window
            for i in range(0, len(self.ListDS)):
                if i < amount:
                    self.comboBox_Scenario.setItemText(i, f'{self.scenarioStr}: {i + 1}')
                else:
                    self.comboBox_Scenario.addItem(f'{self.scenarioStr}: {i + 1}')
            self.comboBox_Scenario.setCurrentIndex(0)
            self.ListDS[0].setValues()
            self.checkDetermineDepth()
            f.close()
        except FileNotFoundError:
            error_dialog = QtWidgets_QMessageBox(QtWidgets_QMessageBox.Warning, self.translations.ErrorMassage,
                                                 self.translations.NoFileSelected, QtWidgets_QMessageBox.Ok, self.Dia)
            error_dialog.show()

    def funCalcThermalDemands(self):
        # load csv
        # arr = csv data
        # calc demand and peaks
        arr = [0]
        self.doubleSpinBox_Hp_Jan.setValue(arr[0])

    # save all scenarios externally
    def funSave(self):
        from pickle import dump as pk_dump, HIGHEST_PROTOCOL as pk_HP
        # open interface and get file
        filename = QtWidgets_QFileDialog.getSaveFileName(caption=self.translations.SavePKL,
                                                         filter='Pickle (*.pkl)')
        # Create list if no scenario is stored
        self.ListDS.append(DataStorage(id(self))) if len(self.ListDS) < 1 else None
        # try to store the file
        try:
            f = open(filename[0], "wb")
            print(filename[0])
            pk_dump(self.ListDS, f, pk_HP)
            f.close()
        except FileNotFoundError:
            error_dialog = QtWidgets_QMessageBox(QtWidgets_QMessageBox.Warning, self.translations.ErrorMassage,
                                                 self.translations.NoFileSelected, QtWidgets_QMessageBox.Ok, self.Dia)
            error_dialog.show()

    # update GUI if a new scenario at the comboBox is selected
    def ChangeScenario(self):
        idx = self.comboBox_Scenario.currentIndex()
        DS: DataStorage = self.ListDS[idx]
        DS.setValues()
        self.checkDetermineDepth()
        if self.stackedWidget.currentWidget() == self.page_Results:
            if DS.borefield is not None:
                self.displayResults()
                return
            self.changeToGeneralPage()

    # Save Scenario
    def SaveScenario(self):
        idx = max(self.comboBox_Scenario.currentIndex(), 0)
        if len(self.ListDS) == idx:
            self.AddScenario()
            return
        self.ListDS[idx] = DataStorage(id(self))

    # Delete selected Scenario
    def DeleteScenario(self):
        idx = self.comboBox_Scenario.currentIndex()
        if idx > 0:
            del self.ListDS[idx]
            self.comboBox_Scenario.removeItem(idx)
            for i in range(self.comboBox_Scenario.count()):
                self.comboBox_Scenario.setItemText(i, f'{self.scenarioStr}: {i + 1}')
            self.comboBox_Scenario.setCurrentIndex(idx - 1)

    # Add a new scenario
    def AddScenario(self):
        number: int = max(len(self.ListDS), 0)
        self.ListDS.append(DataStorage(id(self)))
        self.comboBox_Scenario.addItem(f'{self.scenarioStr}: {number + 1}')
        self.comboBox_Scenario.setCurrentIndex(number)

    # show hide fixed calculation depth
    def checkDetermineDepth(self):
        if self.checkBox_CalcDepth.isChecked():
            self.label_H.hide()
            self.doubleSpinBox_H.hide()
            return
        self.label_H.show()
        self.doubleSpinBox_H.show()

    # change page to settings page
    def changeToGeneralPage(self):
        self.stackedWidget.setCurrentWidget(self.page_General)

    # change page to settings page
    def changeToThermalPage(self):
        self.stackedWidget.setCurrentWidget(self.page_thermal)

    # change page to results page
    def changeToResultsPage(self):
        self.stackedWidget.setCurrentWidget(self.page_Results)

    # update progress bar or hide them if not needed
    def updateBar(self, val: int, OptStart: bool = bool(0)):
        if OptStart:
            self.label_Status.show()
            self.progressBar.show()
        else:
            self.label_Status.hide()
            self.progressBar.hide()
        val = val/self.NumberOfScenarios
        self.progressBar.setValue(round(val * 100))

    # turn on and off the old and new threads for the calculation
    def threadFunction(self, DS: DataStorage):
        self.threads[self.finished].stop()
        self.ListDS[self.finished] = DS
        self.finished += 1
        self.updateBar(self.finished, True)

        if self.finished == self.NumberOfScenarios:
            self.pushButton_Start.setEnabled(True)
            self.pushButton_SaveScenario.setEnabled(True)
            self.pushButton_Results.show()
            self.pushButton_SaveFigure.show()
            self.pushButton_SaveData.show()
            self.changeToResultsPage()
            self.displayResults()
            return
        self.threads[self.finished].start()
        self.threads[self.finished].any_signal.connect(self.threadFunction)

    # start calculation
    def checkStart(self):
        self.pushButton_Start.setEnabled(False)
        self.pushButton_SaveScenario.setEnabled(False)
        # get values from GUI
        self.AddScenario() if not self.ListDS else self.SaveScenario()
        self.NumberOfScenarios: int = len(self.ListDS)
        self.finished: int = 0
        self.updateBar(0, True)
        self.threads = [CalcProblem(DS) for DS in self.ListDS]
        self.threads[0].start()
        self.threads[0].any_signal.connect(self.threadFunction)
        return

    # display results of the current selected scenario
    def displayResults(self):
        from GHEtool import Borefield
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        import matplotlib.pyplot as plt
        from numpy import array as np_array
        idx: int = self.comboBox_Scenario.currentIndex()
        DS: DataStorage = self.ListDS[idx]

        borefield: Borefield = DS.borefield
        resultsPeakCooling = borefield.resultsPeakCooling
        resultsPeakHeating = borefield.resultsPeakHeating
        resultsMonthCooling = borefield.resultsMonthCooling
        resultsMonthHeating = borefield.resultsMonthHeating
        Tb = borefield.Tb

        greyColor = '#00407a'
        COLOR: str = 'w'
        plt.rcParams['text.color'] = COLOR
        plt.rcParams['axes.labelcolor'] = COLOR
        plt.rcParams['xtick.color'] = COLOR
        plt.rcParams['ytick.color'] = COLOR
        self.fig = plt.Figure(facecolor=greyColor) if self.fig is None else self.fig
        canvas = FigureCanvas(self.fig) if self.canvas is None else self.canvas
        ax = canvas.figure.subplots() if self.ax is None else self.ax
        ax.clear()
        # calculation of all the different times at which the gfunction should be calculated.
        # this is equal to 'UPM' hours a month * 3600 seconds/hours for the simulationPeriod
        timeForgValues = [i * borefield.UPM * 3600. for i in range(1, 12 * borefield.simulationPeriod + 1)]

        # make a time array
        timeArray = [i / 12 / 730. / 3600. for i in timeForgValues]

        # plot Temperatures
        ax.step(np_array(timeArray), np_array(Tb), 'w-', where="pre", lw=1.5, label="Tb")
        ax.step(np_array(timeArray), np_array(resultsPeakCooling), where="pre", lw=1.5,
                label=f'Tf {self.translations.PeakCooling}', color='#54bceb')
        ax.step(np_array(timeArray), np_array(resultsPeakHeating), where="pre", lw=1.5,
                label=f'Tf {self.translations.PeakHeating}', color='#ffc857')

        # define temperature bounds
        ax.step(np_array(timeArray), np_array(resultsMonthCooling), color='#54bceb', linestyle="dashed", where="pre",
                lw=1.5, label=f'Tf {self.translations.BaseCooling}')
        ax.step(np_array(timeArray), np_array(resultsMonthHeating), color='#ffc857', linestyle="dashed", where="pre",
                lw=1.5, label=f'Tf {self.translations.BaseHeating}')
        ax.hlines(borefield.Tf_C, 0, DS.simulationPeriod, colors='#ffc857', linestyles='dashed', label='', lw=1)
        ax.hlines(borefield.Tf_H, 0, DS.simulationPeriod, colors='#54bceb', linestyles='dashed', label='', lw=1)
        ax.set_xticks(range(0, DS.simulationPeriod+1, 2))

        # Plot legend
        ax.legend()
        ax.set_xlim(left=0, right=DS.simulationPeriod)
        ax.legend(facecolor=greyColor, loc='best')
        ax.set_xlabel(self.translations.X_Axis, color='white')
        ax.set_ylabel(self.translations.Y_Axis, color='white')
        ax.spines['bottom'].set_color('w')
        ax.spines['top'].set_color('w')
        ax.spines['right'].set_color('w')
        ax.spines['left'].set_color('w')
        ax.set_facecolor(greyColor)
        self.label_Size.setText(f'{self.translations.label_Size}{round(borefield.H,2)} m')

        self.ax = ax
        self.gridLayout_8.addWidget(canvas, 1, 0) if self.canvas is None else None
        self.canvas = canvas

        plt.tight_layout()
        canvas.draw()

    # function to check if a legend should be displayed
    def checkLegend(self):
        if self.checkBox_Legend.isChecked():
            greyColor = '#00407a'
            self.ax.legend(facecolor=greyColor, loc='best')
            self.canvas.draw()
            return
        self.ax.get_legend().remove()
        self.canvas.draw()

    # save figure
    def SaveFigure(self):
        # get filename at storage place
        filename = QtWidgets_QFileDialog.getSaveFileName(caption=self.translations.SaveFigure,
                                                         filter='png (*.png)')
        # save the figure
        self.fig.savefig(filename[0])

    # Save the data in a csv file
    def SaveData(self):
        from csv import writer as csv_writer
        # get filename at storage place
        filename = QtWidgets_QFileDialog.getSaveFileName(caption=self.translations.SaveData,
                                                         filter='csv (*.csv)')
        toWrite = [['name', 'unit'],  # 0
                   ['depth', 'm'],  # 1
                   ['borehole spacing', 'm'],  # 2
                   ['conductivity of the soil', 'W/mK'],  # 3
                   ['Ground temperature at infinity', 'C'],  # 4
                   ['Equivalent borehole resistance', 'mK/W'],  # 5
                   ['width of rectangular field', '#'],  # 6
                   ['length of rectangular field', '#'],  # 7
                   ['Determine length', '0/1'],
                   ['Simulation Period', 'years'],
                   ['Minimal temperature', 'C'],
                   ['Maximal temperature', 'C']]
        month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        month_yrs = [f'{mon}_{int(idx/12)+1}' for idx, mon in enumerate(month*20)]
        toWrite = toWrite + [[f'Peak heating {mon}', 'kW'] for mon in month]
        toWrite = toWrite + [[f'Peak cooling {mon}', 'kW'] for mon in month]
        toWrite = toWrite + [[f'Load heating {mon}', 'kWh'] for mon in month]
        toWrite = toWrite + [[f'Load cooling {mon}', 'kWh'] for mon in month]
        toWrite = toWrite + [[f'Results peak heating {mon}', 'C'] for mon in month_yrs]
        toWrite = toWrite + [[f'Results peak cooling {mon}', 'C'] for mon in month_yrs]
        toWrite = toWrite + [[f'Results load heating {mon}', 'C'] for mon in month_yrs]
        toWrite = toWrite + [[f'Results load cooling {mon}', 'C'] for mon in month_yrs]
        ran_yr = range(12)
        ran_Simu = range(12*20)
        for idx, DS in enumerate(self.ListDS):
            DS: DataStorage = DS
            i = 0
            toWrite[i].append(f'{self.scenarioStr}: {idx + 1}')
            i += 1
            toWrite[i].append(f'{round(DS.H, 2)}')
            i += 1
            toWrite[i].append(f'{round(DS.B, 2)}')
            i += 1
            toWrite[i].append(f'{round(DS.k_s, 2)}')
            i += 1
            toWrite[i].append(f'{round(DS.Tg, 2)}')
            i += 1
            toWrite[i].append(f'{round(DS.Rb, 4)}')
            i += 1
            toWrite[i].append(f'{round(DS.N_1, 0)}')
            i += 1
            toWrite[i].append(f'{round(DS.N_2, 0)}')
            i += 1
            toWrite[i].append(f'{round(DS.DetermineDepth, 0)}')
            i += 1
            toWrite[i].append(f'{round(DS.simulationPeriod, 0)}')
            i += 1
            toWrite[i].append(f'{round(DS.T_min, 2)}')
            i += 1
            toWrite[i].append(f'{round(DS.T_max, 2)}')
            for j in ran_yr:
                i += 1
                toWrite[i].append(f'{round(DS.peakHeating[j], 2)}')
            for j in ran_yr:
                i += 1
                toWrite[i].append(f'{round(DS.peakCooling[j], 2)}')
            for j in ran_yr:
                i += 1
                toWrite[i].append(f'{round(DS.monthlyLoadHeating[j], 2)}')
            for j in ran_yr:
                i += 1
                toWrite[i].append(f'{round(DS.monthlyLoadCooling[j], 2)}')
            if DS.borefield is None:
                i += 1
                [toWrite[i+j].append(f'not calculated') for j in ran_Simu]
                i += len(ran_Simu)
                [toWrite[i+j].append(f'not calculated') for j in ran_Simu]
                i += len(ran_Simu)
                [toWrite[i+j].append(f'not calculated') for j in ran_Simu]
                i += len(ran_Simu)
                [toWrite[i+j].append(f'not calculated') for j in ran_Simu]
                i += len(ran_Simu)
                continue
            for j in ran_Simu:
                i += 1
                toWrite[i].append(f'{round(DS.borefield.resultsPeakHeating[j], 2)}')
            for j in ran_Simu:
                i += 1
                toWrite[i].append(f'{round(DS.borefield.resultsPeakCooling[j], 2)}')
            for j in ran_Simu:
                i += 1
                toWrite[i].append(f'{round(DS.borefield.resultsMonthHeating[j], 2)}')
            for j in ran_Simu:
                i += 1
                toWrite[i].append(f'{round(DS.borefield.resultsMonthCooling[j], 2)}')

        file = open(filename[0], 'w', newline='')
        with file:
            writer = csv_writer(file, delimiter=';')
            for row in toWrite:
                writer.writerow(row)
        file.close()

    # close gui
    def checkCancel(self):
        for i in self.threads:
            i.stop()
        sys_exit(self.app.exec_())


# class to calculate the problem in an external thread
class CalcProblem(QtCore_QThread):
    any_signal = QtCore_pyqtSignal(DataStorage)

    def __init__(self, DS: DataStorage, parent=None) -> None:
        super(CalcProblem, self).__init__(parent)
        self.DS = DS
        self.is_running = True

    def run(self) -> None:
        from GHEtool import GroundData, Borefield
        # relevant borefield data for the calculations
        GD = GroundData(self.DS.H, self.DS.B, self.DS.k_s, self.DS.Tg, self.DS.Rb, self.DS.N_1, self.DS.N_2)

        # create the borefield object

        borefield = Borefield(simulationPeriod=self.DS.simulationPeriod,
                              peakHeating=self.DS.peakHeating,
                              peakCooling=self.DS.peakCooling,
                              baseloadHeating=self.DS.monthlyLoadHeating,
                              baseloadCooling=self.DS.monthlyLoadCooling)

        borefield.setGroundParameters(GD)

        # set temperature boundaries
        borefield.setMaxGroundTemperature(self.DS.T_max)  # maximum temperature
        borefield.setMinGroundTemperature(self.DS.T_min)  # minimum temperature

        # size borefield
        borefield.size(GD.H) if self.DS.DetermineDepth else None

        borefield.calculateTemperatures(borefield.H)
        self.DS.borefield = borefield
        self.any_signal.emit(self.DS)
        return

    def stop(self):
        self.is_running = False
        print('Stopping thread...', 0)
        self.terminate()
