from sys import exit as sys_exit, path
from typing import Optional, Union
from Translation_class import TrClass
from PyQt5.QtWidgets import QWidget as QtWidgets_QWidget, QApplication as QtWidgets_QApplication, \
    QMainWindow as QtWidgets_QMainWindow, QPushButton as QtWidgets_QPushButton,\
    QDoubleSpinBox as QtWidgets_QDoubleSpinBox, QMessageBox as QtWidgets_QMessageBox, \
    QFileDialog as QtWidgets_QFileDialog
from pickle import dump as pk_dump, HIGHEST_PROTOCOL as pk_HP, load as pk_load
from PyQt5.QtCore import QSize as QtCore_QSize, QEvent as QtCore_QEvent, QThread as QtCore_QThread, \
    pyqtSignal as QtCore_pyqtSignal, QModelIndex as QtCore_QModelIndex
from ui.gui_Main import Ui_GHEtool
from os.path import dirname, realpath, split as os_split
from functools import partial as ft_partial

currentdir = dirname(realpath(__file__))
parentdir = dirname(currentdir)
path.append(parentdir)


class BoundsOfPrecalculatedData:
    """
    class to check if selected values are within the bounds for the precalculated data
    """
    __slots__ = 'H', 'B_Min', 'B_Max', 'k_s_Min', 'k_s_Max', 'N_Max'

    def __init__(self):
        self.H: float = 350.0
        self.B_Max: float = 9.0
        self.B_Min: float = 3.0
        self.k_s_Min: float = 1.5
        self.k_s_Max: float = 3.5
        self.N_Max: int = 20

    def check_if_outside_bounds(self, h: float, b: float, k_s: float, n: int) -> bool:
        """
        Check if selected values are within the bounds for the precalculated data
        :param h: depth [m]
        :param b: Spacings [m]
        :param k_s: Thermal conductivity of the soil [W/mK]
        :param n: Maximal number of borehole in one rectangular field direction
        :return: true if outside of bounds
        """
        if h > self.H:
            return True
        if not(self.B_Min <= b <= self.B_Max):
            return True
        if not(self.k_s_Min <= k_s <= self.k_s_Max):
            return True
        if n > self.N_Max:
            return True
        return False


# Create Data storage class to store the input and output variables
class DataStorage:
    __slots__ = 'H', 'B', 'k_s', 'Tg', 'Rb', 'N_1', 'N_2', 'T_max', 'T_min', 'simulationPeriod', 'peakHeating', \
                'peakCooling', 'monthlyLoadHeating', 'monthlyLoadHeating', 'monthlyLoadCooling', 'bore_field', 'ui',\
                'DetermineDepth', 'unitDemand', 'unitPeak', 'FactorDemand', 'FactorPeak', 'size_bore_field', 'H_max',\
                'B_max', 'B_min', 'L_max', 'W_max', 'Size_Method'

    # init class and store input data
    def __init__(self, ui: int) -> None:
        """
        Get Values from GUI and initialize DataStorage class
        Parameters
        ----------
        ui : int
            Integer of user interface ID

        Returns
        -------
        None
        """
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
        self.size_bore_field: bool = getattr(obj, 'checkBox_SizeBorefield').isChecked()
        self.H_max: float = getattr(obj, 'doubleSpinBox_H').value()  # m
        self.B_max: float = getattr(obj, 'doubleSpinBox_B_max').value()  # m
        self.B_min: float = getattr(obj, 'doubleSpinBox_B').value()  # m
        self.W_max: float = getattr(obj, 'doubleSpinBox_W_max').value()  # m
        self.L_max: float = getattr(obj, 'doubleSpinBox_L_max').value()  # m
        self.Size_Method: int = getattr(obj, 'comboBox_Size_Method').currentIndex()  # #
        self.unitPeak: str = getattr(obj, 'label_Unit_pH').text()
        self.unitDemand: str = getattr(obj, 'label_Unit_HL').text()
        u_p = self.unitPeak[1:-1]
        u_d = self.unitDemand[1:-1]
        self.FactorPeak: float = 1 if u_p == 'kW' else 0.001 if u_p == 'W' else 1000
        self.FactorDemand: float = 1 if u_d == 'kWh' else 0.001 if u_d == 'Wh' else 1000

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

        self.bore_field: Optional[Borefield, None] = None

    # set stored data to gui fields
    def set_values(self) -> None:
        """Set Values to GUI"""
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
        try:
            getattr(obj, 'checkBox_SizeBorefield').setChecked(self.size_bore_field)
            if self.size_bore_field:
                getattr(obj, 'doubleSpinBox_H').setValue(self.H_max)  # m
                getattr(obj, 'doubleSpinBox_B_max').setValue(self.B_max)  # m
                getattr(obj, 'comboBox_Size_Method').setCurrentIndex(self.Size_Method)  # #
                getattr(obj, 'doubleSpinBox_B').setValue(self.B_min)  # m
                getattr(obj, 'doubleSpinBox_W_max').setValue(self.W_max)  # m
                getattr(obj, 'doubleSpinBox_L_max').setValue(self.L_max)  # m
        except AttributeError:
            return


# main GUI class
class MainWindow(QtWidgets_QMainWindow, Ui_GHEtool):

    def __init__(self, dialog: QtWidgets_QWidget, app: QtWidgets_QApplication) -> None:
        """initialize window"""
        # init windows
        super(MainWindow, self).__init__()
        super().setupUi(dialog)
        self.app: QtWidgets_QApplication = app
        self.Dia = dialog
        self.translations: TrClass = TrClass()
        self.file = None
        self.list_widget_scenario.clear()
        # init links from buttons to functions
        self.pushButton_thermalDemands.clicked.connect(ft_partial(self.stackedWidget.setCurrentWidget,
                                                                  self.page_thermal))
        self.pushButton_Results.clicked.connect(ft_partial(self.stackedWidget.setCurrentWidget, self.page_Results))
        self.pushButton_Settings.clicked.connect(ft_partial(self.stackedWidget.setCurrentWidget, self.page_Settings))
        self.checkBox_CalcDepth.stateChanged.connect(self.check_determine_depth)
        self.checkBox_SizeBorefield.stateChanged.connect(self.check_size_bore_field)
        self.pushButton_General.clicked.connect(ft_partial(self.stackedWidget.setCurrentWidget, self.page_General))
        self.pushButton_SaveFigure.clicked.connect(self.save_figure)
        self.pushButton_SaveData.clicked.connect(self.save_data)
        self.list_widget_scenario.currentRowChanged.connect(self.change_scenario)
        self.actionAdd_Scenario.triggered.connect(self.add_scenario)
        self.actionUpdate_Scenario.triggered.connect(self.save_scenario)
        self.actionDelete_scenario.triggered.connect(self.delete_scenario)
        self.checkBox_Legend.clicked.connect(self.check_legend)
        self.pushButton_NextGeneral.clicked.connect(self.pushButton_thermalDemands.click)
        self.pushButton_PreviousThermal.clicked.connect(self.pushButton_General.click)
        self.comboBox_Datentyp.currentIndexChanged.connect(self.data_type)
        self.pushButton_loadCsv.clicked.connect(self.fun_choose_file)
        self.actionStart.triggered.connect(self.check_start)
        self.actionSave.triggered.connect(self.fun_save)
        self.actionSave_As.triggered.connect(self.fun_save_as)
        self.actionOpen.triggered.connect(self.fun_load)
        self.actionNew.triggered.connect(self.fun_new)
        self.actionEnglish.triggered.connect(ft_partial(self.comboBox_Language.setCurrentIndex, 0))
        self.actionGerman.triggered.connect(ft_partial(self.comboBox_Language.setCurrentIndex, 1))
        self.actionDutch.triggered.connect(ft_partial(self.comboBox_Language.setCurrentIndex, 2))
        self.actionItalian.triggered.connect(ft_partial(self.comboBox_Language.setCurrentIndex, 3))
        self.actionFrench.triggered.connect(ft_partial(self.comboBox_Language.setCurrentIndex, 4))
        self.doubleSpinBox_H.valueChanged.connect(self.check_bounds)
        self.doubleSpinBox_B.valueChanged.connect(self.check_bounds)
        self.doubleSpinBox_k_s.valueChanged.connect(self.check_bounds)
        self.spinBox_N_1.valueChanged.connect(self.check_bounds)
        self.spinBox_N_2.valueChanged.connect(self.check_bounds)
        self.pushButton_load.clicked.connect(self.fun_load_file)
        self.comboBox_dataColumn.currentIndexChanged.connect(self.fun_choose_column_demand)
        self.comboBox_timeStep.currentIndexChanged.connect(self.fun_choose_column_time_step)
        self.pushButton_calculate.clicked.connect(self.fun_display_data)
        self.pushButton_Einheit.clicked.connect(self.fun_change_unit)
        self.checkBox_Import.clicked.connect(self.hide_import)
        self.list_widget_scenario.itemDoubleClicked.connect(self.actionRename_scenario.trigger)
        self.actionRename_scenario.triggered.connect(self.fun_rename)
        # initialize so far unused variables
        self.ax = None  # axes of figure
        self.canvas = None  # canvas class of figure
        self.fig = None  # figure
        self.NumberOfScenarios: int = 1  # number of scenarios
        self.finished: int = 1  # number of finished scenarios
        self.threads: list = []  # list of calculation threads
        self.ListDS: list = []  # list of data storages
        # set start page to general page
        self.pushButton_General.click()
        # reset progress bar
        self.update_bar(0, False)
        # set language options and link them to the comboBox
        self.comboBox_Language.addItems(self.translations.comboBox_Language)
        self.comboBox_Language.currentIndexChanged.connect(self.change_language)

        self.pushButton_General.installEventFilter(self)
        self.pushButton_thermalDemands.installEventFilter(self)
        self.pushButton_Results.installEventFilter(self)
        self.pushButton_Settings.installEventFilter(self)
        self.label_GapGenTh.installEventFilter(self)
        self.label_GapThRes.installEventFilter(self)
        self.label_GapResSet.installEventFilter(self)
        # size
        self.sizeB = QtCore_QSize(48, 48)
        self.sizeS = QtCore_QSize(24, 24)
        self.sizePushB = QtCore_QSize(150, 75)
        self.sizePushS = QtCore_QSize(75, 75)

        self.pushButton_Start.setIconSize(self.sizeS)
        self.pushButton_Cancel.setIconSize(self.sizeS)

        self.scenarioStr: str = 'Scenario'
        self.hide_import()
        self.data_type()
        self.frame_heatingLoad.hide()
        self.frame_coolingLoad.hide()
        self.frame_combined.hide()
        self.set_push(False)
        self.IG: ImportGHEtool = ImportGHEtool()
        self.IG.start()
        self.IG.any_signal.connect(self.check_ghe_tool)
        self.statusBar.showMessage(self.translations.GHE_tool_imported_start, 5000)
        self.ImportFinished: bool = False
        self.pushButton_Start.setEnabled(self.ImportFinished)
        self.pushButton_Start.setStyleSheet(
            '*{border: 3px solid rgb(100, 100, 100);\nborder-radius: 5px;\ncolor: rgb(255, 255, 255);\n'
            'gridline-color: rgb(100, 100, 100);\nbackground-color: rgb(100, 100, 100);\nfont: 75 11pt "Verdana";}\n'
            '*:hover{background-color: rgb(0, 64, 122);}')
        self.actionStart.setEnabled(self.ImportFinished)
        self.label_WarningCustomBorefield.hide()
        self.BOPD: BoundsOfPrecalculatedData = BoundsOfPrecalculatedData()
        self.filename: tuple = ('', '')
        self.load_list()
        self.check_results()
        self.statusBar.addPermanentWidget(self.label_Status, 0)
        self.statusBar.addPermanentWidget(self.progressBar, 1)
        self.statusBar.messageChanged.connect(self.status_hide)
        self.change_window_title()

    def fun_rename(self):
        item = self.list_widget_scenario.currentItem()
        item = self.list_widget_scenario.item(0) if item is None else item
        from PyQt5 import QtWidgets
        dialog = QtWidgets.QInputDialog(self.Dia)
        dialog.setWindowTitle(self.translations.label_new_scenario)
        dialog.setLabelText(f"{self.translations.new_name}{item.text()}:")
        dialog.setOkButtonText(self.translations.label_okay)  # +++
        dialog.setCancelButtonText(self.translations.label_abort)  # +++
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            text = dialog.textValue()
            item.setText(text) if text != '' else None

    def check_results(self):
        # hide results buttons
        if any([(i.bore_field is None) for i in self.ListDS]) or self.ListDS == []:
            self.label_GapThRes.hide()
            self.pushButton_Results.hide()
            self.pushButton_SaveFigure.hide()
            self.pushButton_SaveData.hide()
            self.pushButton_General.click()
            return
        self.display_results()

    def change_window_title(self):
        path, filename = ('', '') if self.filename == ('', '') else os_split(self.filename[0])
        title: str = '' if filename == '' else f' - {filename.replace(".pkl", "")}'
        self.Dia.setWindowTitle(f'GHEtool {title}')

    def status_hide(self, text):
        if text == '':
            self.statusBar.hide()
            return
        self.statusBar.show()

    def check_bounds(self):
        outside_bounds: bool = self.BOPD.check_if_outside_bounds(self.doubleSpinBox_H.value(),
                                                                 self.doubleSpinBox_B.value(),
                                                                 self.doubleSpinBox_k_s.value(),
                                                                 max(self.spinBox_N_1.value(), self.spinBox_N_2.value())
                                                                 )
        self.label_WarningCustomBorefield.show() if outside_bounds else self.label_WarningCustomBorefield.hide()

    def eventFilter(self, obj: QtWidgets_QPushButton, event) -> bool:
        """
        function to check mouse over event
        :param obj:
        PushButton obj
        :param event:
        event to check if mouse over event is entering or leaving
        :return:
        Boolean to check if the function worked
        """
        if event.type() == QtCore_QEvent.Enter:
            # Mouse is over the label
            self.set_push(True)
            return True
        elif event.type() == QtCore_QEvent.Leave:
            # Mouse is not over the label
            self.set_push(False)
            return True
        return False

    def set_push(self, mouse_over: bool) -> None:
        """
        function to Set PushButton Text if MouseOver
        :param mouse_over:
        MouseOver: bool true if Mouse is over PushButton
        :return:
        None
        """
        if mouse_over:
            self.pushButton_General.setText(self.translations.pushButton_General)
            self.pushButton_thermalDemands.setText(self.translations.pushButton_thermalDemands)
            self.pushButton_Results.setText(self.translations.pushButton_Results)
            self.pushButton_Settings.setText(self.translations.label_Settings)
            # setting icon size
            self.pushButton_General.setIconSize(self.sizeS)
            self.pushButton_thermalDemands.setIconSize(self.sizeS)
            self.pushButton_Results.setIconSize(self.sizeS)
            self.pushButton_Settings.setIconSize(self.sizeS)
            self.pushButton_General.setMaximumSize(self.sizePushB)
            self.pushButton_General.setMinimumSize(self.sizePushB)
            self.pushButton_thermalDemands.setMaximumSize(self.sizePushB)
            self.pushButton_thermalDemands.setMinimumSize(self.sizePushB)
            self.pushButton_Results.setMaximumSize(self.sizePushB)
            self.pushButton_Results.setMinimumSize(self.sizePushB)
            self.pushButton_Settings.setMaximumSize(self.sizePushB)
            self.pushButton_Settings.setMinimumSize(self.sizePushB)
            return
        self.pushButton_General.setText('')
        self.pushButton_thermalDemands.setText('')
        self.pushButton_Results.setText('')
        self.pushButton_Settings.setText('')
        # setting icon size
        self.pushButton_General.setIconSize(self.sizeB)
        self.pushButton_thermalDemands.setIconSize(self.sizeB)
        self.pushButton_Results.setIconSize(self.sizeB)
        self.pushButton_Settings.setIconSize(self.sizeB)
        self.pushButton_General.setMaximumSize(self.sizePushS)
        self.pushButton_General.setMinimumSize(self.sizePushS)
        self.pushButton_thermalDemands.setMaximumSize(self.sizePushS)
        self.pushButton_thermalDemands.setMinimumSize(self.sizePushS)
        self.pushButton_Results.setMaximumSize(self.sizePushS)
        self.pushButton_Results.setMinimumSize(self.sizePushS)
        self.pushButton_Settings.setMaximumSize(self.sizePushS)
        self.pushButton_Settings.setMinimumSize(self.sizePushS)

    @staticmethod
    def display_values_with_floating_decimal(spinbox: QtWidgets_QDoubleSpinBox, factor: float) -> None:
        value = spinbox.value() * factor
        decimal_loc = 0 if value >= 1_000 else 1 if value >= 100 else 2 if value >= 10 else 3 if value >= 1 else 4
        spinbox.setDecimals(decimal_loc)
        spinbox.setMaximum(max(value*10, 1_000_000))
        spinbox.setValue(value)

    def hide_import(self) -> None:
        if self.checkBox_Import.isChecked():
            self.toolBox.show()
            self.toolBox.setCurrentWidget(self.page_File)
            return
        self.toolBox.hide()

    # function to change language on labels and push buttons
    def change_language(self) -> None:
        index = self.comboBox_Language.currentIndex()
        amount: int = self.list_widget_scenario.count()
        li_str_match: list = [self.list_widget_scenario.item(idx).text() == f'{self.scenarioStr}: {idx + 1}' for idx in
                              range(amount)]
        self.translations.change_language(index)
        self.label_Language.setText(f'{self.translations.label_Language}: ')
        self.pushButton_SaveScenario.setText(self.translations.pushButton_SaveScenario)
        self.pushButton_AddScenario.setText(self.translations.pushButton_AddScenario)
        self.pushButton_DeleteScenario.setText(self.translations.pushButton_DeleteScenario)
        self.pushButton_Start.setText(self.translations.pushButton_Start)
        self.pushButton_Cancel.setText(self.translations.pushButton_Cancel)
        self.label_Status.setText(self.translations.label_Status)
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
        self.label_WarningCustomBorefield.setText(self.translations.label_WarningCustomBorefield)
        self.label_WarningDepth.setText(self.translations.label_WarningDepth)
        self.menuFile.setTitle(self.translations.label_File)
        self.menuCalculation.setTitle(self.translations.label_Calculation)
        self.menuSettings.setTitle(self.translations.label_Settings)
        self.menuLanguage.setTitle(self.translations.label_Language)
        self.actionStart.setText(self.translations.pushButton_Start)
        self.actionGerman.setText(self.translations.label_German)
        self.actionEnglish.setText(self.translations.label_English)
        self.actionDutch.setText(self.translations.label_Dutch)
        self.actionFrench.setText(self.translations.label_French)
        self.actionItalian.setText(self.translations.label_Italian)
        self.actionNew.setText(self.translations.label_New)
        self.actionSave.setText(self.translations.label_Save)
        self.actionOpen.setText(self.translations.label_Open)
        self.actionUpdate_Scenario.setText(self.translations.pushButton_SaveScenario)
        self.actionAdd_Scenario.setText(self.translations.pushButton_AddScenario)
        self.actionDelete_scenario.setText(self.translations.pushButton_DeleteScenario)
        self.actionSave_As.setText(self.translations.label_Save_As)
        self.menuScenario.setTitle(self.translations.scenarioStr)
        [self.comboBox_Language.setItemText(i, name) for i, name in enumerate(self.translations.comboBox_Language)]
        try:
            self.checkBox_SizeBorefield.setText(self.translations.checkBox_SizeBorefield)
            if self.checkBox_SizeBorefield.isChecked():
                self.label_H.setText(self.translations.label_H_max)
                self.label_BS.setText(self.translations.label_B_min)
                self.label_B_max.setText(self.translations.label_B_max)
                self.label_MaxWidthField.setText(self.translations.label_MaxWidthField)
                self.label_MaxLengthField.setText(self.translations.label_MaxLengthField)
                self.comboBox_Size_Method.clear()
                self.comboBox_Size_Method.addItems(self.translations.comboBox_Size_Method)
            else:
                self.label_H.setText(self.translations.label_H)
                self.label_BS.setText(self.translations.label_BS)
        except AttributeError:
            pass

        self.comboBox_dataColumn.clear()
        self.comboBox_dataColumn.addItems(self.translations.comboBox_dataColumn)
        self.comboBox_timeStep.clear()
        self.comboBox_timeStep.addItems(self.translations.comboBox_timeStep)
        self.scenarioStr = self.translations.scenarioStr
        scenarios: list = [f'{self.scenarioStr}: {i}' if li_str_match[i - 1] else
                           self.list_widget_scenario.item(i-1).text() for i in range(1, amount + 1)]
        self.list_widget_scenario.clear()
        if amount > 0:
            self.list_widget_scenario.addItems(scenarios)

    def load_list(self):
        # try to open the file
        try:
            with open("backup.pkl", "rb") as f:
                saving: tuple = pk_load(f)
            self.filename, li, idx_lang = saving
            self.ListDS, li = li[0], li[1]
            self.comboBox_Language.setCurrentIndex(idx_lang)
            # replace uer window id
            for DS in self.ListDS:
                DS.ui = id(self)
            self.list_widget_scenario.clear()
            self.list_widget_scenario.addItems(li)
            self.list_widget_scenario.setCurrentRow(0)
        except FileNotFoundError:
            self.check_determine_depth()
            self.check_size_bore_field()
            print('no backup file')

    def fun_save_auto(self):
        print('save')
        if len(self.ListDS) < 1:
            self.ListDS.append(DataStorage(id(self)))
        try:
            with open("backup.pkl", "wb") as f:
                li = [self.list_widget_scenario.item(idx).text() for idx in range(self.list_widget_scenario.count())]
                saving = self.filename, [self.ListDS, li], self.comboBox_Language.currentIndex()
                pk_dump(saving, f, pk_HP)
        except FileNotFoundError:
            error_dialog = QtWidgets_QMessageBox(QtWidgets_QMessageBox.Warning, self.translations.ErrorMassage,
                                                 self.translations.NoFileSelected, QtWidgets_QMessageBox.Ok, self.Dia)
            error_dialog.show()

    # function to choose Datatype
    def data_type(self) -> int:
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
            return index
        elif index == '.xlsx' or index == '.xls':
            self.frame_sheetName.show()
        else:
            error_dialog = QtWidgets_QMessageBox(QtWidgets_QMessageBox.Warning, self.translations.ErrorMassage,
                                                 self.translations.UnableDataFormat, QtWidgets_QMessageBox.Ok, self.Dia)
            error_dialog.show()
        return index

    # function to choose data file
    def fun_choose_file(self) -> None:
        try:
            file_index = self.comboBox_Datentyp.currentText()
            if file_index == '.csv':
                filename = QtWidgets_QFileDialog.getOpenFileName(caption=self.translations.ChooseCSV,
                                                                 filter='(*.csv)')
                self.lineEdit_displayCsv.setText(filename[0])

            elif file_index == '.xlsx' or file_index == '.xls':
                if file_index == '.xlsx':
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
    def fun_load_file(self) -> None:
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
    def fun_choose_column_demand(self) -> None:
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
    def fun_choose_column_time_step(self) -> None:
        df = self.file
        columns = [''] if df is None else df.columns

        self.frame_date.hide()
        self.comboBox_date.clear()

        idx: int = self.comboBox_timeStep.currentIndex()

        if idx == 2:
            self.comboBox_date.addItems(columns)
            self.frame_date.show()

    # Load the Data to Display in the GUI
    def fun_display_data(self) -> None:
        try:
            # get filename from line edit
            filename: str = self.lineEdit_displayCsv.text()
            if filename == '':
                raise FileNotFoundError
            thermal_demand: int = self.comboBox_dataColumn.currentIndex()

            # Generate the column that have to be imported
            cols: list = []
            heating_load: str = self.comboBox_heatingLoad.currentText()
            if len(heating_load) >= 1:
                cols.append(heating_load)
            cooling_load: str = self.comboBox_coolingLoad.currentText()
            if len(cooling_load) >= 1:
                cols.append(cooling_load)
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
            time_step_idx = self.comboBox_timeStep.currentIndex()

            if time_step_idx == 0:  # 1 hour
                # Define start and end date
                from pandas import to_datetime as pd_to_datetime, Series as pd_Series, date_range as pd_date_range
                start = pd_to_datetime("2019-01-01 00:00:00")
                end = pd_to_datetime("2019-12-31 23:59:00")
                df2[date] = pd_Series(pd_date_range(start, end, freq="1H"))
                dict_agg: Optional[None, dict] = None
            elif time_step_idx == 1:  # 15 minute time step
                from pandas import to_datetime as pd_to_datetime, Series as pd_Series, date_range as pd_date_range
                start = pd_to_datetime("2019-01-01 00:00:00")
                end = pd_to_datetime("2019-12-31 23:59:00")
                df2[date] = pd_Series(pd_date_range(start, end, freq="15T"))
                dict_agg: Optional[None, dict] = {combined: 'mean'} if thermal_demand == 1 else {heating_load: 'mean',
                                                                                                 cooling_load: 'mean'}
            else:
                from pandas import to_datetime as pd_to_datetime
                df2[date] = pd_to_datetime(df2[date])
                dict_agg: Optional[None, dict] = {combined: 'mean'} if thermal_demand == 1 else {heating_load: 'mean',
                                                                                                 cooling_load: 'mean'}
            df2.set_index(date, inplace=True)
            df2 = df2 if dict_agg is None else df2.resample("H").agg(dict_agg)

            # ------------------- Calculate Section --------------------
            # Choose path between Single or Combined Column
            if thermal_demand == 0:
                # Resample the Data for peakHeating and peakCooling
                df2.rename(columns={heating_load: "Heating Load", cooling_load: "Cooling Load"}, inplace=True)
                df2["peak Heating"] = df2["Heating Load"]
                df2["peak Cooling"] = df2["Cooling Load"]
                # self.write_filename = "single_output.csv"

            elif thermal_demand == 1:
                # Create Filter for heating and cooling load ( Heating Load +, Cooling Load -)
                heating_load = df2[combined].apply(lambda x: x >= 0)
                cooling_load = df2[combined].apply(lambda x: x < 0)
                df2["Heating Load"] = df2.loc[heating_load, combined]
                df2["Cooling Load"] = df2.loc[cooling_load, combined] * -1
                df2["peak Heating"] = df2["Heating Load"]
                df2["peak Cooling"] = df2["Cooling Load"]
                # self.write_filename = "combi_output.csv"

            df3 = df2.resample("M").agg({"Heating Load": "sum", "Cooling Load": "sum",
                                         "peak Heating": "max", "peak Cooling": "max"})
            # TODO: https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects
            #       https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior

            # ----------------------- Data Unit Section --------------------------
            # Get the Data Unit and set the label in the thermal Demand Box to follow
            data_unit = self.comboBox_dataUnit.currentText()

            # define factors
            if data_unit == 'W':
                fac = 1
            elif data_unit == 'kW':
                fac = 0.001
            elif data_unit == 'MW':
                fac = 0.000001
            else:
                fac = 0

            self.label_Unit_pH.setText(f'[kW]')
            self.label_Unit_pC.setText(f'[kW]')
            self.label_Unit_HL.setText(f'[kWh]')
            self.label_Unit_CL.setText(f'[kWh]')

            df3 = df3 * fac
            peak_heating = df3["peak Heating"]
            peak_cooling = df3["peak Cooling"]
            heating_load = df3["Heating Load"]
            cooling_load = df3["Cooling Load"]

            self.doubleSpinBox_HL_Jan.setValue(heating_load[0])
            self.doubleSpinBox_HL_Feb.setValue(heating_load[1])
            self.doubleSpinBox_HL_Mar.setValue(heating_load[2])
            self.doubleSpinBox_HL_Apr.setValue(heating_load[3])
            self.doubleSpinBox_HL_May.setValue(heating_load[4])
            self.doubleSpinBox_HL_Jun.setValue(heating_load[5])
            self.doubleSpinBox_HL_Jul.setValue(heating_load[6])
            self.doubleSpinBox_HL_Aug.setValue(heating_load[7])
            self.doubleSpinBox_HL_Sep.setValue(heating_load[8])
            self.doubleSpinBox_HL_Oct.setValue(heating_load[9])
            self.doubleSpinBox_HL_Nov.setValue(heating_load[10])
            self.doubleSpinBox_HL_Dec.setValue(heating_load[11])

            self.doubleSpinBox_CL_Jan.setValue(cooling_load[0])
            self.doubleSpinBox_CL_Feb.setValue(cooling_load[1])
            self.doubleSpinBox_CL_Mar.setValue(cooling_load[2])
            self.doubleSpinBox_CL_Apr.setValue(cooling_load[3])
            self.doubleSpinBox_CL_May.setValue(cooling_load[4])
            self.doubleSpinBox_CL_Jun.setValue(cooling_load[5])
            self.doubleSpinBox_CL_Jul.setValue(cooling_load[6])
            self.doubleSpinBox_CL_Aug.setValue(cooling_load[7])
            self.doubleSpinBox_CL_Sep.setValue(cooling_load[8])
            self.doubleSpinBox_CL_Oct.setValue(cooling_load[9])
            self.doubleSpinBox_CL_Nov.setValue(cooling_load[10])
            self.doubleSpinBox_CL_Dec.setValue(cooling_load[11])

            self.doubleSpinBox_Hp_Jan.setValue(peak_heating[0])
            self.doubleSpinBox_Hp_Feb.setValue(peak_heating[1])
            self.doubleSpinBox_Hp_Mar.setValue(peak_heating[2])
            self.doubleSpinBox_Hp_Apr.setValue(peak_heating[3])
            self.doubleSpinBox_Hp_May.setValue(peak_heating[4])
            self.doubleSpinBox_Hp_Jun.setValue(peak_heating[5])
            self.doubleSpinBox_Hp_Jul.setValue(peak_heating[6])
            self.doubleSpinBox_Hp_Aug.setValue(peak_heating[7])
            self.doubleSpinBox_Hp_Sep.setValue(peak_heating[8])
            self.doubleSpinBox_Hp_Oct.setValue(peak_heating[9])
            self.doubleSpinBox_Hp_Nov.setValue(peak_heating[10])
            self.doubleSpinBox_Hp_Dec.setValue(peak_heating[11])

            self.doubleSpinBox_Cp_Jan.setValue(peak_cooling[0])
            self.doubleSpinBox_Cp_Feb.setValue(peak_cooling[1])
            self.doubleSpinBox_Cp_Mar.setValue(peak_cooling[2])
            self.doubleSpinBox_Cp_Apr.setValue(peak_cooling[3])
            self.doubleSpinBox_Cp_May.setValue(peak_cooling[4])
            self.doubleSpinBox_Cp_Jun.setValue(peak_cooling[5])
            self.doubleSpinBox_Cp_Jul.setValue(peak_cooling[6])
            self.doubleSpinBox_Cp_Aug.setValue(peak_cooling[7])
            self.doubleSpinBox_Cp_Sep.setValue(peak_cooling[8])
            self.doubleSpinBox_Cp_Oct.setValue(peak_cooling[9])
            self.doubleSpinBox_Cp_Nov.setValue(peak_cooling[10])
            self.doubleSpinBox_Cp_Dec.setValue(peak_cooling[11])

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
    def fun_change_unit(self) -> None:
        # Umfaktorierung von comboBox im Thermal Demand Box
        peak_new = self.comboBox_Unit_peak.currentText()
        load_new = self.comboBox_Unit_Load.currentText()
        peak_old = self.label_Unit_pH.text()
        peak_old = peak_old.replace('[', '')
        peak_old = peak_old.replace(']', '')
        load_old = self.label_Unit_HL.text()
        load_old = load_old.replace('[', '')
        load_old = load_old.replace(']', '')

        self.label_Unit_HL.setText(f'[{load_new}]')
        self.label_Unit_CL.setText(f'[{load_new}]')
        self.label_Unit_pH.setText(f'[{peak_new}]')
        self.label_Unit_pC.setText(f'[{peak_new}]')

        if load_new == load_old:
            factor_load = 1
        elif load_old == 'Wh' and load_new == 'MWh':
            factor_load = 0.000001
        elif (load_old == 'Wh' and load_new == 'kWh') or (load_old == 'kWh' and load_new == 'MWh'):
            factor_load = 0.001
        elif (load_old == 'kWh' and load_new == 'Wh') or (load_old == 'MWh' and load_new == 'kWh'):
            factor_load = 1000
        elif load_old == 'MWh' and load_new == 'Wh':
            factor_load = 1000000
        else:
            factor_load = 0

        if peak_old == peak_new:
            factor_peak = 1
        elif peak_old == 'W' and peak_new == 'MW':
            factor_peak = 0.000_001
        elif (peak_old == 'W' and peak_new == 'kW') or (peak_old == 'kW' and peak_new == 'MW'):
            factor_peak = 0.001
        elif (peak_old == 'kW' and peak_new == 'W') or (peak_old == 'MW' and peak_new == 'kW'):
            factor_peak = 1000
        elif peak_old == 'MW' and peak_new == 'W':
            factor_peak = 1000000
        else:
            factor_peak = 0
        self.display_values_with_floating_decimal(self.doubleSpinBox_HL_Jan, factor_load)
        self.display_values_with_floating_decimal(self.doubleSpinBox_HL_Feb, factor_load)
        self.display_values_with_floating_decimal(self.doubleSpinBox_HL_Mar, factor_load)
        self.display_values_with_floating_decimal(self.doubleSpinBox_HL_Apr, factor_load)
        self.display_values_with_floating_decimal(self.doubleSpinBox_HL_May, factor_load)
        self.display_values_with_floating_decimal(self.doubleSpinBox_HL_Jun, factor_load)
        self.display_values_with_floating_decimal(self.doubleSpinBox_HL_Jul, factor_load)
        self.display_values_with_floating_decimal(self.doubleSpinBox_HL_Aug, factor_load)
        self.display_values_with_floating_decimal(self.doubleSpinBox_HL_Sep, factor_load)
        self.display_values_with_floating_decimal(self.doubleSpinBox_HL_Oct, factor_load)
        self.display_values_with_floating_decimal(self.doubleSpinBox_HL_Nov, factor_load)
        self.display_values_with_floating_decimal(self.doubleSpinBox_HL_Dec, factor_load)

        self.display_values_with_floating_decimal(self.doubleSpinBox_CL_Jan, factor_load)
        self.display_values_with_floating_decimal(self.doubleSpinBox_CL_Feb, factor_load)
        self.display_values_with_floating_decimal(self.doubleSpinBox_CL_Mar, factor_load)
        self.display_values_with_floating_decimal(self.doubleSpinBox_CL_Apr, factor_load)
        self.display_values_with_floating_decimal(self.doubleSpinBox_CL_May, factor_load)
        self.display_values_with_floating_decimal(self.doubleSpinBox_CL_Jun, factor_load)
        self.display_values_with_floating_decimal(self.doubleSpinBox_CL_Jul, factor_load)
        self.display_values_with_floating_decimal(self.doubleSpinBox_CL_Aug, factor_load)
        self.display_values_with_floating_decimal(self.doubleSpinBox_CL_Sep, factor_load)
        self.display_values_with_floating_decimal(self.doubleSpinBox_CL_Oct, factor_load)
        self.display_values_with_floating_decimal(self.doubleSpinBox_CL_Nov, factor_load)
        self.display_values_with_floating_decimal(self.doubleSpinBox_CL_Dec, factor_load)

        self.display_values_with_floating_decimal(self.doubleSpinBox_Hp_Jan, factor_peak)
        self.display_values_with_floating_decimal(self.doubleSpinBox_Hp_Feb, factor_peak)
        self.display_values_with_floating_decimal(self.doubleSpinBox_Hp_Mar, factor_peak)
        self.display_values_with_floating_decimal(self.doubleSpinBox_Hp_Apr, factor_peak)
        self.display_values_with_floating_decimal(self.doubleSpinBox_Hp_May, factor_peak)
        self.display_values_with_floating_decimal(self.doubleSpinBox_Hp_Jun, factor_peak)
        self.display_values_with_floating_decimal(self.doubleSpinBox_Hp_Jul, factor_peak)
        self.display_values_with_floating_decimal(self.doubleSpinBox_Hp_Aug, factor_peak)
        self.display_values_with_floating_decimal(self.doubleSpinBox_Hp_Sep, factor_peak)
        self.display_values_with_floating_decimal(self.doubleSpinBox_Hp_Oct, factor_peak)
        self.display_values_with_floating_decimal(self.doubleSpinBox_Hp_Nov, factor_peak)
        self.display_values_with_floating_decimal(self.doubleSpinBox_Hp_Dec, factor_peak)

        self.display_values_with_floating_decimal(self.doubleSpinBox_Cp_Jan, factor_peak)
        self.display_values_with_floating_decimal(self.doubleSpinBox_Cp_Feb, factor_peak)
        self.display_values_with_floating_decimal(self.doubleSpinBox_Cp_Mar, factor_peak)
        self.display_values_with_floating_decimal(self.doubleSpinBox_Cp_Apr, factor_peak)
        self.display_values_with_floating_decimal(self.doubleSpinBox_Cp_May, factor_peak)
        self.display_values_with_floating_decimal(self.doubleSpinBox_Cp_Jun, factor_peak)
        self.display_values_with_floating_decimal(self.doubleSpinBox_Cp_Jul, factor_peak)
        self.display_values_with_floating_decimal(self.doubleSpinBox_Cp_Aug, factor_peak)
        self.display_values_with_floating_decimal(self.doubleSpinBox_Cp_Sep, factor_peak)
        self.display_values_with_floating_decimal(self.doubleSpinBox_Cp_Oct, factor_peak)
        self.display_values_with_floating_decimal(self.doubleSpinBox_Cp_Nov, factor_peak)
        self.display_values_with_floating_decimal(self.doubleSpinBox_Cp_Dec, factor_peak)

    # function to check if the calculation works
    @staticmethod
    def fun_check(data1, data2) -> None:
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

        # import results
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

        rows, cols = np_where(x is False)

        for item in zip(rows, cols):
            basis_single.iloc[item[0], item[1]] = ' {} --> {}'.format(basis_single.iloc[item[0], item[1]],
                                                                      result_single.iloc[item[0], item[1]])

        pd_set_option('display.max_columns', 4)

        print(
            "\nZusammenfassung: \nDie beiden Berechnungsprogrammen haben exakt das gleiche Ergebnis rausbekommen!\n"
            "SUPER :)")
        print("---------------------------------------------------------------------------------------------------\n")
        print(basis_single)

    # function to load externally stored scenario
    def fun_load(self) -> None:
        # open interface and get file
        self.filename = QtWidgets_QFileDialog.getOpenFileName(caption=self.translations.ChoosePKL,
                                                              filter='Pickle (*.pkl)')
        self.fun_load_known_filename()

    def fun_load_known_filename(self):
        # try to open the file
        try:
            with open(self.filename[0], "rb") as f:
                li: list = pk_load(f)
                self.ListDS, li = li[0], li[1]
                self.change_window_title()
            # replace uer window id
            for DS in self.ListDS:
                DS.ui = id(self)
            # init user window
            self.list_widget_scenario.clear()
            self.list_widget_scenario.addItems(li)
            self.list_widget_scenario.setCurrentRow(0)
            self.check_results()
        except FileNotFoundError:
            error_dialog = QtWidgets_QMessageBox(QtWidgets_QMessageBox.Warning, self.translations.ErrorMassage,
                                                 self.translations.NoFileSelected, QtWidgets_QMessageBox.Ok, self.Dia)
            error_dialog.show()

    def fun_save_as(self):
        self.filename = ('', '')
        self.fun_save()

    # save all scenarios externally
    def fun_save(self) -> None:
        self.fun_save_auto()
        if self.filename == ('', ''):
            self.filename: tuple = QtWidgets_QFileDialog.getSaveFileName(caption=self.translations.SavePKL,
                                                                         filter='Pickle (*.pkl)')
            self.change_window_title()
        # Create list if no scenario is stored
        self.ListDS.append(DataStorage(id(self))) if len(self.ListDS) < 1 else None
        # try to store the file
        try:
            with open(self.filename[0], "wb") as f:
                li = [self.list_widget_scenario.item(idx).text() for idx in range(self.list_widget_scenario.count())]
                pk_dump([self.ListDS, li], f, pk_HP)
        except FileNotFoundError:
            error_dialog = QtWidgets_QMessageBox(QtWidgets_QMessageBox.Warning, self.translations.ErrorMassage,
                                                 self.translations.NoFileSelected, QtWidgets_QMessageBox.Ok, self.Dia)
            error_dialog.show()

    def fun_new(self):
        # open interface and get file
        self.filename: tuple = ('', '')
        self.fun_save()
        self.ListDS: list = []
        self.list_widget_scenario.clear()

    # update GUI if a new scenario at the comboBox is selected
    def change_scenario(self) -> None:
        idx = self.list_widget_scenario.currentRow()
        if idx < 0:
            return
        ds: DataStorage = self.ListDS[idx]
        ds.set_values()
        if self.stackedWidget.currentWidget() == self.page_Results:
            if ds.bore_field is not None:
                self.display_results()
                return
            self.pushButton_General.click()

    # Save Scenario
    def save_scenario(self) -> None:
        idx = max(self.list_widget_scenario.currentRow(), 0)
        if len(self.ListDS) == idx:
            self.add_scenario()
            self.fun_save_auto()
            return
        self.ListDS[idx] = DataStorage(id(self))
        self.fun_save_auto()

    # Delete selected Scenario
    def delete_scenario(self) -> None:
        idx = self.list_widget_scenario.currentRow()
        if idx > 0:
            del self.ListDS[idx]
            self.list_widget_scenario.takeItem(idx)
            for i in range(idx, self.list_widget_scenario.count()):
                item = self.list_widget_scenario.item(i)
                if item.text() == f'{self.scenarioStr}: {i + 2}':
                    item.setText(f'{self.scenarioStr}: {i + 1}')
            self.list_widget_scenario.setCurrentRow(idx - 1)

    # Add a new scenario
    def add_scenario(self) -> None:
        number: int = max(len(self.ListDS), 0)
        self.ListDS.append(DataStorage(id(self)))
        self.list_widget_scenario.addItem(f'{self.scenarioStr}: {number + 1}')
        self.list_widget_scenario.setCurrentRow(number)

    # show hide fixed calculation depth
    def check_determine_depth(self) -> None:
        if self.checkBox_CalcDepth.isChecked():
            self.label_H.hide()
            self.doubleSpinBox_H.hide()
            if self.checkBox_SizeBorefield.isChecked():
                self.checkBox_SizeBorefield.setChecked(False)
                self.label_H.setText(self.translations.label_H)
                self.label_BS.setText(self.translations.label_BS)
                self.label_WidthField.show()
                self.spinBox_N_1.show()
                self.label_LengthField.show()
                self.spinBox_N_2.show()
                self.label_B_max.hide()
                self.comboBox_Size_Method.hide()
                self.doubleSpinBox_B_max.hide()
                self.label_MaxWidthField.hide()
                self.doubleSpinBox_W_max.hide()
                self.label_MaxLengthField.hide()
                self.doubleSpinBox_L_max.hide()
            return
        self.label_H.show()
        self.doubleSpinBox_H.show()

    # show hide fixed calculation depth
    def check_size_bore_field(self) -> None:
        if self.checkBox_SizeBorefield.isChecked():
            self.checkBox_CalcDepth.setChecked(False)
            self.label_H.show()
            self.doubleSpinBox_H.show()
            self.label_B_max.show()
            self.comboBox_Size_Method.show()
            self.doubleSpinBox_B_max.show()
            self.label_MaxWidthField.show()
            self.doubleSpinBox_W_max.show()
            self.label_MaxLengthField.show()
            self.doubleSpinBox_L_max.show()
            self.label_WidthField.hide()
            self.spinBox_N_1.hide()
            self.label_LengthField.hide()
            self.spinBox_N_2.hide()
            try:
                self.label_H.setText(self.translations.label_H_max)
                self.label_BS.setText(self.translations.label_B_min)
            except AttributeError:
                pass
            return
        self.label_B_max.hide()
        self.comboBox_Size_Method.hide()
        self.doubleSpinBox_B_max.hide()
        self.label_MaxWidthField.hide()
        self.doubleSpinBox_W_max.hide()
        self.label_MaxLengthField.hide()
        self.doubleSpinBox_L_max.hide()
        self.label_WidthField.show()
        self.spinBox_N_1.show()
        self.label_LengthField.show()
        self.spinBox_N_2.show()
        self.label_H.setText(self.translations.label_H)
        self.label_BS.setText(self.translations.label_BS)

    # update progress bar or hide them if not needed
    def update_bar(self, val: int, opt_start: bool = bool(0)) -> None:
        if opt_start:
            self.label_Status.show()
            self.progressBar.show()
            self.statusBar.show()
        else:
            self.label_Status.hide()
            self.progressBar.hide()
        val = val/self.NumberOfScenarios
        self.progressBar.setValue(round(val * 100))
        if val > 0.9999:
            self.label_Status.hide()
            self.progressBar.hide()
            self.statusBar.showMessage(self.translations.Calculation_Finished, 5000)

    def check_ghe_tool(self, finished: bool) -> None:
        """
        check if GHEtool import is finished
        :param finished: bool
        :return: None
        """
        self.IG.stop()
        self.ImportFinished = finished
        self.pushButton_Start.setEnabled(self.ImportFinished)
        self.actionStart.setEnabled(self.ImportFinished)
        self.pushButton_Start.setStyleSheet('*{border: 3px solid rgb(84, 188, 235);\n'
                                            'border-radius: 5px;\n'
                                            'color: rgb(255, 255, 255);\n'
                                            'gridline-color: rgb(84, 188, 235);\n'
                                            'background-color: rgb(84, 188, 235);\n'
                                            'font: 75 11pt "Verdana";}\n'
                                            '*:hover{background-color: rgb(0, 64, 122);}')
        self.statusBar.showMessage(self.translations.GHE_tool_imported, 5000)

    def thread_function(self, ds: DataStorage) -> None:
        """
        turn on and off the old and new threads for the calculation
        :param ds: DataStorage
        :return: None
        """
        self.threads[self.finished].stop()
        self.ListDS[self.finished] = ds
        self.finished += 1
        self.update_bar(self.finished, True)

        if self.finished == self.NumberOfScenarios:
            self.pushButton_Start.setEnabled(True)
            self.pushButton_SaveScenario.setEnabled(True)
            self.display_results()
            return
        self.threads[self.finished].start()
        self.threads[self.finished].any_signal.connect(self.thread_function)

    # start calculation
    def check_start(self) -> None:
        self.pushButton_Start.setEnabled(False)
        self.pushButton_SaveScenario.setEnabled(False)
        # get values from GUI
        self.add_scenario() if not self.ListDS else self.save_scenario()
        self.NumberOfScenarios: int = len(self.ListDS)
        self.finished: int = 0
        self.update_bar(0, True)
        self.threads = [CalcProblem(DS) for DS in self.ListDS]
        self.threads[0].start()
        self.threads[0].any_signal.connect(self.thread_function)
        return

    # display results of the current selected scenario
    def display_results(self) -> None:
        from GHEtool import Borefield
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        import matplotlib.pyplot as plt
        from numpy import array as np_array

        self.pushButton_Results.show()
        self.label_GapThRes.show()
        self.pushButton_SaveFigure.show()
        self.pushButton_SaveData.show()
        self.pushButton_Results.click()

        idx: int = self.list_widget_scenario.currentRow()
        ds: DataStorage = self.ListDS[idx]

        bore_field: Borefield = ds.bore_field
        results_peak_cooling = bore_field.resultsPeakCooling
        results_peak_heating = bore_field.resultsPeakHeating
        results_month_cooling = bore_field.resultsMonthCooling
        results_month_heating = bore_field.resultsMonthHeating
        t_b = bore_field.Tb

        grey_color = '#00407a'
        color: str = 'w'
        plt.rcParams['text.color'] = color
        plt.rcParams['axes.labelcolor'] = color
        plt.rcParams['xtick.color'] = color
        plt.rcParams['ytick.color'] = color
        self.fig = plt.Figure(facecolor=grey_color) if self.fig is None else self.fig
        canvas = FigureCanvas(self.fig) if self.canvas is None else self.canvas
        ax = canvas.figure.subplots() if self.ax is None else self.ax
        ax.clear()
        # calculation of all the different times at which the g_function should be calculated.
        # this is equal to 'UPM' hours a month * 3600 seconds/hours for the simulationPeriod
        time_for_g_values = [i * bore_field.UPM * 3600. for i in range(1, 12 * bore_field.simulationPeriod + 1)]

        # make a time array
        time_array = [i / 12 / 730. / 3600. for i in time_for_g_values]

        # plot Temperatures
        ax.step(np_array(time_array), np_array(t_b), 'w-', where="pre", lw=1.5, label="Tb")
        ax.step(np_array(time_array), np_array(results_peak_cooling), where="pre", lw=1.5,
                label=f'Tf {self.translations.PeakCooling}', color='#54bceb')
        ax.step(np_array(time_array), np_array(results_peak_heating), where="pre", lw=1.5,
                label=f'Tf {self.translations.PeakHeating}', color='#ffc857')

        # define temperature bounds
        ax.step(np_array(time_array), np_array(results_month_cooling), color='#54bceb', linestyle="dashed", where="pre",
                lw=1.5, label=f'Tf {self.translations.BaseCooling}')
        ax.step(np_array(time_array), np_array(results_month_heating), color='#ffc857', linestyle="dashed", where="pre",
                lw=1.5, label=f'Tf {self.translations.BaseHeating}')
        ax.hlines(bore_field.Tf_C, 0, ds.simulationPeriod, colors='#ffc857', linestyles='dashed', label='', lw=1)
        ax.hlines(bore_field.Tf_H, 0, ds.simulationPeriod, colors='#54bceb', linestyles='dashed', label='', lw=1)
        ax.set_xticks(range(0, ds.simulationPeriod+1, 2))

        # Plot legend
        ax.legend()
        ax.set_xlim(left=0, right=ds.simulationPeriod)
        ax.legend(facecolor=grey_color, loc='best')
        ax.set_xlabel(self.translations.X_Axis, color='white')
        ax.set_ylabel(self.translations.Y_Axis, color='white')
        ax.spines['bottom'].set_color('w')
        ax.spines['top'].set_color('w')
        ax.spines['right'].set_color('w')
        ax.spines['left'].set_color('w')
        ax.set_facecolor(grey_color)
        li_size = [str(round(i[3], 2)) for i in bore_field.combo]
        li_b = [str(round(i[2], 2)) for i in bore_field.combo]
        li_n_1 = [str(round(i[0], 2)) for i in bore_field.combo]
        li_n_2 = [str(round(i[1], 2)) for i in bore_field.combo]
        string_size: str = f'{self.translations.label_Size}{"; ".join(li_size)} m \n'\
                           f'{self.translations.label_Size_B}{"; ".join(li_b)} m \n' \
                           f'{self.translations.label_Size_W}{"; ".join(li_n_1)} \n' \
                           f'{self.translations.label_Size_L}{"; ".join(li_n_2)} \n'\
            if ds.size_bore_field else f'{self.translations.label_Size}{round(bore_field.H, 2)} m'
        self.label_Size.setText(string_size)

        self.label_WarningDepth.show() if bore_field.H < 50 else self.label_WarningDepth.hide()

        self.ax = ax
        self.gridLayout_8.addWidget(canvas, 1, 0) if self.canvas is None else None
        self.canvas = canvas

        plt.tight_layout()
        canvas.draw()

    # function to check if a legend should be displayed
    def check_legend(self) -> None:
        if self.checkBox_Legend.isChecked():
            grey_color = '#00407a'
            self.ax.legend(facecolor=grey_color, loc='best')
            self.canvas.draw()
            return
        self.ax.get_legend().remove()
        self.canvas.draw()

    # save figure
    def save_figure(self) -> None:
        # get filename at storage place
        filename = QtWidgets_QFileDialog.getSaveFileName(caption=self.translations.SaveFigure,
                                                         filter='png (*.png)')
        # save the figure
        self.fig.savefig(filename[0])

    # Save the data in a csv file
    def save_data(self) -> None:
        from csv import writer as csv_writer
        # get filename at storage place
        filename = QtWidgets_QFileDialog.getSaveFileName(caption=self.translations.SaveData,
                                                         filter='csv (*.csv)')
        to_write = [['name', 'unit'],  # 0
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
        to_write = to_write + [[f'Peak heating {mon}', 'kW'] for mon in month]
        to_write = to_write + [[f'Peak cooling {mon}', 'kW'] for mon in month]
        to_write = to_write + [[f'Load heating {mon}', 'kWh'] for mon in month]
        to_write = to_write + [[f'Load cooling {mon}', 'kWh'] for mon in month]
        to_write = to_write + [[f'Results peak heating {mon}', 'C'] for mon in month_yrs]
        to_write = to_write + [[f'Results peak cooling {mon}', 'C'] for mon in month_yrs]
        to_write = to_write + [[f'Results load heating {mon}', 'C'] for mon in month_yrs]
        to_write = to_write + [[f'Results load cooling {mon}', 'C'] for mon in month_yrs]
        ran_yr = range(12)
        ran_simu = range(12*20)
        for idx, ds in enumerate(self.ListDS):
            ds: DataStorage = ds
            i = 0
            to_write[i].append(f'{self.list_widget_scenario.item(idx).text()}')
            i += 1
            to_write[i].append(f'{round(ds.H, 2)}')
            i += 1
            to_write[i].append(f'{round(ds.B, 2)}')
            i += 1
            to_write[i].append(f'{round(ds.k_s, 2)}')
            i += 1
            to_write[i].append(f'{round(ds.Tg, 2)}')
            i += 1
            to_write[i].append(f'{round(ds.Rb, 4)}')
            i += 1
            to_write[i].append(f'{round(ds.N_1, 0)}')
            i += 1
            to_write[i].append(f'{round(ds.N_2, 0)}')
            i += 1
            to_write[i].append(f'{round(ds.DetermineDepth, 0)}')
            i += 1
            to_write[i].append(f'{round(ds.simulationPeriod, 0)}')
            i += 1
            to_write[i].append(f'{round(ds.T_min, 2)}')
            i += 1
            to_write[i].append(f'{round(ds.T_max, 2)}')
            for j in ran_yr:
                i += 1
                to_write[i].append(f'{round(ds.peakHeating[j], 2)}')
            for j in ran_yr:
                i += 1
                to_write[i].append(f'{round(ds.peakCooling[j], 2)}')
            for j in ran_yr:
                i += 1
                to_write[i].append(f'{round(ds.monthlyLoadHeating[j], 2)}')
            for j in ran_yr:
                i += 1
                to_write[i].append(f'{round(ds.monthlyLoadCooling[j], 2)}')
            if ds.bore_field is None:
                i += 1
                [to_write[i+j].append(f'not calculated') for j in ran_simu]
                i += len(ran_simu)
                [to_write[i+j].append(f'not calculated') for j in ran_simu]
                i += len(ran_simu)
                [to_write[i+j].append(f'not calculated') for j in ran_simu]
                i += len(ran_simu)
                [to_write[i+j].append(f'not calculated') for j in ran_simu]
                i += len(ran_simu)
                continue
            for j in ran_simu:
                i += 1
                to_write[i].append(f'{round(ds.bore_field.resultsPeakHeating[j], 2)}')
            for j in ran_simu:
                i += 1
                to_write[i].append(f'{round(ds.bore_field.resultsPeakCooling[j], 2)}')
            for j in ran_simu:
                i += 1
                to_write[i].append(f'{round(ds.bore_field.resultsMonthHeating[j], 2)}')
            for j in ran_simu:
                i += 1
                to_write[i].append(f'{round(ds.bore_field.resultsMonthCooling[j], 2)}')

        file = open(filename[0], 'w', newline='')
        with file:
            writer = csv_writer(file, delimiter=';')
            for row in to_write:
                writer.writerow(row)
        file.close()

    # close gui
    def check_cancel(self) -> None:
        """Stop threads and close GUI"""
        for i in self.threads:
            i.stop()
        sys_exit(self.app.exec_())


# class to calculate the problem in an external thread
class CalcProblem(QtCore_QThread):
    any_signal = QtCore_pyqtSignal(DataStorage)

    def __init__(self, ds: DataStorage, parent=None) -> None:
        """initialize calculation class"""
        super(CalcProblem, self).__init__(parent)
        self.DS = ds
        self.is_running = True

    def run(self) -> None:
        """run calculations"""
        from GHEtool import GroundData, Borefield
        # relevant bore field data for the calculations
        gd = GroundData(self.DS.H, self.DS.B, self.DS.k_s, self.DS.Tg, self.DS.Rb, self.DS.N_1, self.DS.N_2)
        # create the bore field object
        bore_field = Borefield(simulation_period=self.DS.simulationPeriod, peak_heating=self.DS.peakHeating,
                               peak_cooling=self.DS.peakCooling, base_load_heating=self.DS.monthlyLoadHeating,
                               base_load_cooling=self.DS.monthlyLoadCooling, gui=True)
        # set temperature boundaries
        bore_field.set_max_ground_temperature(self.DS.T_max)  # maximum temperature
        bore_field.set_min_ground_temperature(self.DS.T_min)  # minimum temperature
        bopd: BoundsOfPrecalculatedData = BoundsOfPrecalculatedData()
        outside_bounds: bool = bopd.check_if_outside_bounds(self.DS.H, self.DS.B, self.DS.k_s, max(self.DS.N_1,
                                                                                                   self.DS.N_2))
        bore_field.set_ground_parameters(gd)
        if outside_bounds:
            from pygfunction import boreholes as gt_boreholes

            n_max: int = max(gd.N_1, gd.N_2)
            n_min: int = max(gd.N_1, gd.N_2)
            bore_field_custom: str = f'customField_{n_max}_{n_min}_{gd.B}_{gd.k_s}'
            custom_field = gt_boreholes.rectangle_field(N_1=n_max, N_2=n_min, B_1=gd.B, B_2=gd.B, H=gd.H, D=4,
                                                        r_b=0.075)
            try:
                from GHEtool import FOLDER
                pk_load(open(f'{FOLDER}/Data/{bore_field_custom}.pickle', "rb"))
            except FileNotFoundError:
                bore_field.create_custom_dataset(custom_field, bore_field_custom)
            bore_field.set_custom_g_function(bore_field_custom)
            bore_field.set_bore_field(custom_field)

        bore_field.size(gd.H) if self.DS.DetermineDepth else None
        if self.DS.Size_Method == 0:
            bore_field.size_complete_field_fast(self.DS.H_max, self.DS.W_max, self.DS.L_max, self.DS.B_min,
                                                self.DS.B_max) if self.DS.size_bore_field else None
        else:
            bore_field.size_complete_field_robust(self.DS.H_max, self.DS.W_max, self.DS.L_max, self.DS.B_min,
                                                  self.DS.B_max) if self.DS.size_bore_field else None
        # calculate temperatures
        bore_field.calculate_temperatures(bore_field.H)
        self.DS.bore_field = bore_field
        self.any_signal.emit(self.DS)
        return

    def stop(self) -> None:
        """Stop threads"""
        self.is_running = False
        print('Stopping thread...', 0)
        self.terminate()


# class import GHEtool in an external thread
class ImportGHEtool(QtCore_QThread):
    any_signal = QtCore_pyqtSignal(bool)

    def __init__(self, parent=None) -> None:
        """initialize calculation class"""
        super(ImportGHEtool, self).__init__(parent)
        self.is_running = True

    def run(self) -> None:
        """run calculations"""
        from GHEtool import GroundData
        GroundData(100, 6, 1.5, 10, 0.05, 12, 10)
        self.any_signal.emit(True)
        return

    def stop(self) -> None:
        """Stop threads"""
        self.is_running = False
        print('Stopping thread...', 0)
        self.terminate()
