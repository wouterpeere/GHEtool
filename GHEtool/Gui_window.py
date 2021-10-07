from sys import exit as sys_exit
from PyQt5 import QtWidgets, QtCore
from ui.gui import Ui_GHEtool


# Create Data storage class to store the input and output variables
class DataStorage:
    __slots__ = 'H', 'B', 'k_s', 'Tg', 'Rb', 'N_1', 'N_2', 'T_max', 'T_min', 'simulationPeriod', 'peakHeating', \
                'peakCooling', 'monthlyLoadHeating', 'monthlyLoadHeating', 'monthlyLoadCooling', 'borefield', 'ui',\
                'DetermineDepth'

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

        # Montly loading values
        self.peakHeating: list = [getattr(obj, 'doubleSpinBox_Hp_Jan').value(),
                                  getattr(obj, 'doubleSpinBox_Hp_Feb').value(),
                                  getattr(obj, 'doubleSpinBox_Hp_Mar').value(),
                                  getattr(obj, 'doubleSpinBox_Hp_Apr').value(),
                                  getattr(obj, 'doubleSpinBox_Hp_May').value(),
                                  getattr(obj, 'doubleSpinBox_Hp_Jun').value(),
                                  getattr(obj, 'doubleSpinBox_Hp_Jul').value(),
                                  getattr(obj, 'doubleSpinBox_Hp_Aug').value(),
                                  getattr(obj, 'doubleSpinBox_Hp_Sep').value(),
                                  getattr(obj, 'doubleSpinBox_Hp_Oct').value(),
                                  getattr(obj, 'doubleSpinBox_Hp_Nov').value(),
                                  getattr(obj, 'doubleSpinBox_Hp_Dec').value()]  # kW

        self.peakCooling: list = [getattr(obj, 'doubleSpinBox_Cp_Jan').value(),
                                  getattr(obj, 'doubleSpinBox_Cp_Feb').value(),
                                  getattr(obj, 'doubleSpinBox_Cp_Mar').value(),
                                  getattr(obj, 'doubleSpinBox_Cp_Apr').value(),
                                  getattr(obj, 'doubleSpinBox_Cp_May').value(),
                                  getattr(obj, 'doubleSpinBox_Cp_Jun').value(),
                                  getattr(obj, 'doubleSpinBox_Cp_Jul').value(),
                                  getattr(obj, 'doubleSpinBox_Cp_Aug').value(),
                                  getattr(obj, 'doubleSpinBox_Cp_Sep').value(),
                                  getattr(obj, 'doubleSpinBox_Cp_Oct').value(),
                                  getattr(obj, 'doubleSpinBox_Cp_Nov').value(),
                                  getattr(obj, 'doubleSpinBox_Cp_Dec').value()]  # kW

        # percentage of annual load per month (15.5% for January ...)
        self.monthlyLoadHeating: list = [getattr(obj, 'doubleSpinBox_HL_Jan').value(),
                                         getattr(obj, 'doubleSpinBox_HL_Feb').value(),
                                         getattr(obj, 'doubleSpinBox_HL_Mar').value(),
                                         getattr(obj, 'doubleSpinBox_HL_Apr').value(),
                                         getattr(obj, 'doubleSpinBox_HL_May').value(),
                                         getattr(obj, 'doubleSpinBox_HL_Jun').value(),
                                         getattr(obj, 'doubleSpinBox_HL_Jul').value(),
                                         getattr(obj, 'doubleSpinBox_HL_Aug').value(),
                                         getattr(obj, 'doubleSpinBox_HL_Sep').value(),
                                         getattr(obj, 'doubleSpinBox_HL_Oct').value(),
                                         getattr(obj, 'doubleSpinBox_HL_Nov').value(),
                                         getattr(obj, 'doubleSpinBox_HL_Dec').value()]  # kWh

        self.monthlyLoadCooling: list = [getattr(obj, 'doubleSpinBox_CL_Jan').value(),
                                         getattr(obj, 'doubleSpinBox_CL_Feb').value(),
                                         getattr(obj, 'doubleSpinBox_CL_Mar').value(),
                                         getattr(obj, 'doubleSpinBox_CL_Apr').value(),
                                         getattr(obj, 'doubleSpinBox_CL_May').value(),
                                         getattr(obj, 'doubleSpinBox_CL_Jun').value(),
                                         getattr(obj, 'doubleSpinBox_CL_Jul').value(),
                                         getattr(obj, 'doubleSpinBox_CL_Aug').value(),
                                         getattr(obj, 'doubleSpinBox_CL_Sep').value(),
                                         getattr(obj, 'doubleSpinBox_CL_Oct').value(),
                                         getattr(obj, 'doubleSpinBox_CL_Nov').value(),
                                         getattr(obj, 'doubleSpinBox_CL_Dec').value()]  # kWh

        self.borefield: Borefield = None

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

        # Montly loading values
        getattr(obj, 'doubleSpinBox_Hp_Jan').setValue(self.peakHeating[0])
        getattr(obj, 'doubleSpinBox_Hp_Feb').setValue(self.peakHeating[1])
        getattr(obj, 'doubleSpinBox_Hp_Mar').setValue(self.peakHeating[2])
        getattr(obj, 'doubleSpinBox_Hp_Apr').setValue(self.peakHeating[3])
        getattr(obj, 'doubleSpinBox_Hp_May').setValue(self.peakHeating[4])
        getattr(obj, 'doubleSpinBox_Hp_Jun').setValue(self.peakHeating[5])
        getattr(obj, 'doubleSpinBox_Hp_Jul').setValue(self.peakHeating[6])
        getattr(obj, 'doubleSpinBox_Hp_Aug').setValue(self.peakHeating[7])
        getattr(obj, 'doubleSpinBox_Hp_Sep').setValue(self.peakHeating[8])
        getattr(obj, 'doubleSpinBox_Hp_Oct').setValue(self.peakHeating[9])
        getattr(obj, 'doubleSpinBox_Hp_Nov').setValue(self.peakHeating[10])
        getattr(obj, 'doubleSpinBox_Hp_Dec').setValue(self.peakHeating[11])

        getattr(obj, 'doubleSpinBox_Cp_Jan').setValue(self.peakCooling[0])
        getattr(obj, 'doubleSpinBox_Cp_Feb').setValue(self.peakCooling[1])
        getattr(obj, 'doubleSpinBox_Cp_Mar').setValue(self.peakCooling[2])
        getattr(obj, 'doubleSpinBox_Cp_Apr').setValue(self.peakCooling[3])
        getattr(obj, 'doubleSpinBox_Cp_May').setValue(self.peakCooling[4])
        getattr(obj, 'doubleSpinBox_Cp_Jun').setValue(self.peakCooling[5])
        getattr(obj, 'doubleSpinBox_Cp_Jul').setValue(self.peakCooling[6])
        getattr(obj, 'doubleSpinBox_Cp_Aug').setValue(self.peakCooling[7])
        getattr(obj, 'doubleSpinBox_Cp_Sep').setValue(self.peakCooling[8])
        getattr(obj, 'doubleSpinBox_Cp_Oct').setValue(self.peakCooling[9])
        getattr(obj, 'doubleSpinBox_Cp_Nov').setValue(self.peakCooling[10])
        getattr(obj, 'doubleSpinBox_Cp_Dec').setValue(self.peakCooling[11])

        # percentage of annual load per month (15.5% for January ...)
        getattr(obj, 'doubleSpinBox_HL_Jan').setValue(self.monthlyLoadHeating[0])
        getattr(obj, 'doubleSpinBox_HL_Feb').setValue(self.monthlyLoadHeating[1])
        getattr(obj, 'doubleSpinBox_HL_Mar').setValue(self.monthlyLoadHeating[2])
        getattr(obj, 'doubleSpinBox_HL_Apr').setValue(self.monthlyLoadHeating[3])
        getattr(obj, 'doubleSpinBox_HL_May').setValue(self.monthlyLoadHeating[4])
        getattr(obj, 'doubleSpinBox_HL_Jun').setValue(self.monthlyLoadHeating[5])
        getattr(obj, 'doubleSpinBox_HL_Jul').setValue(self.monthlyLoadHeating[6])
        getattr(obj, 'doubleSpinBox_HL_Aug').setValue(self.monthlyLoadHeating[7])
        getattr(obj, 'doubleSpinBox_HL_Sep').setValue(self.monthlyLoadHeating[8])
        getattr(obj, 'doubleSpinBox_HL_Oct').setValue(self.monthlyLoadHeating[9])
        getattr(obj, 'doubleSpinBox_HL_Nov').setValue(self.monthlyLoadHeating[10])
        getattr(obj, 'doubleSpinBox_HL_Dec').setValue(self.monthlyLoadHeating[11])

        getattr(obj, 'doubleSpinBox_CL_Jan').setValue(self.monthlyLoadCooling[0])
        getattr(obj, 'doubleSpinBox_CL_Feb').setValue(self.monthlyLoadCooling[1])
        getattr(obj, 'doubleSpinBox_CL_Mar').setValue(self.monthlyLoadCooling[2])
        getattr(obj, 'doubleSpinBox_CL_Apr').setValue(self.monthlyLoadCooling[3])
        getattr(obj, 'doubleSpinBox_CL_May').setValue(self.monthlyLoadCooling[4])
        getattr(obj, 'doubleSpinBox_CL_Jun').setValue(self.monthlyLoadCooling[5])
        getattr(obj, 'doubleSpinBox_CL_Jul').setValue(self.monthlyLoadCooling[6])
        getattr(obj, 'doubleSpinBox_CL_Aug').setValue(self.monthlyLoadCooling[7])
        getattr(obj, 'doubleSpinBox_CL_Sep').setValue(self.monthlyLoadCooling[8])
        getattr(obj, 'doubleSpinBox_CL_Oct').setValue(self.monthlyLoadCooling[9])
        getattr(obj, 'doubleSpinBox_CL_Nov').setValue(self.monthlyLoadCooling[10])
        getattr(obj, 'doubleSpinBox_CL_Dec').setValue(self.monthlyLoadCooling[11])


# main GUI class
class MainWindow(Ui_GHEtool):

    # initialize window
    def __init__(self, Dialog: QtWidgets.QWidget, app: QtWidgets.QApplication):
        # init windows
        super(MainWindow, self).__init__()
        super().setupUi(Dialog)
        self.app: QtWidgets.QApplication = app
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

    # function to load externally stored scenario
    def funLoad(self):
        from pickle import load as pk_load
        # open interface and get file
        filename = QtWidgets.QFileDialog.getOpenFileName(caption="Choose pkl to load configuration",
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
                    self.comboBox_Scenario.setItemText(i, 'scenario ' + str(i + 1))  # addItem('scenario '+str(i + 1))
                else:
                    self.comboBox_Scenario.addItem('scenario ' + str(i + 1))
            self.comboBox_Scenario.setCurrentIndex(0)
            self.ListDS[0].setValues()
            self.checkDetermineDepth()
            f.close()
        except FileNotFoundError:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('no file selected')
            print('no file selected')

    # save all scenarios externally
    def funSave(self):
        from pickle import dump as pk_dump, HIGHEST_PROTOCOL as pk_HP
        # open interface and get file
        filename = QtWidgets.QFileDialog.getSaveFileName(caption="Choose pkl to save configuration",
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
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('no file selected')
            print('no file selected')

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
                self.comboBox_Scenario.setItemText(i, f'Scenario {i + 1}')
            self.comboBox_Scenario.setCurrentIndex(idx - 1)

    # Add a new scenario
    def AddScenario(self):
        number: int = max(len(self.ListDS), 0)
        self.ListDS.append(DataStorage(id(self)))
        self.comboBox_Scenario.addItem(f'Scenario {number + 1}')
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
            self.label_Status.setText('Progress:')
            self.progressBar.show()
        else:
            self.label_Status.hide()
            self.label_Status.setText(':')
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
        ax.step(np_array(timeArray), np_array(resultsPeakCooling), where="pre", lw=1.5, label='Tf peak cooling',
                color='#54bceb')
        ax.step(np_array(timeArray), np_array(resultsPeakHeating), where="pre", lw=1.5, label='Tf peak heating',
                color='#ffc857')

        # define temperature bounds
        ax.step(np_array(timeArray), np_array(resultsMonthCooling), color='#54bceb', linestyle="dashed", where="pre",
                lw=1.5, label='Tf base cooling')
        ax.step(np_array(timeArray), np_array(resultsMonthHeating), color='#ffc857', linestyle="dashed", where="pre",
                lw=1.5, label='Tf base heating')
        ax.hlines(borefield.Tf_C, 0, DS.simulationPeriod, colors='#ffc857', linestyles='dashed', label='', lw=1)
        ax.hlines(borefield.Tf_H, 0, DS.simulationPeriod, colors='#54bceb', linestyles='dashed', label='', lw=1)
        ax.set_xticks(range(0, DS.simulationPeriod+1, 2))

        # Plot legend
        ax.legend()
        ax.set_xlim(left=0, right=DS.simulationPeriod)
        ax.legend(facecolor=greyColor, loc='best')
        ax.set_xlabel(r'Time [year]', color='white')
        ax.set_ylabel(r'Temperature [$^\circ C$]', color='white')
        ax.spines['bottom'].set_color('w')
        ax.spines['top'].set_color('w')
        ax.spines['right'].set_color('w')
        ax.spines['left'].set_color('w')
        ax.set_facecolor(greyColor)
        self.label_Size.setText(f'Borehole Depth: {round(borefield.H,2)} m')

        self.ax = ax
        self.gridLayout_4.addWidget(canvas, 2, 0) if self.canvas is None else None
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
        filename = QtWidgets.QFileDialog.getSaveFileName(caption="Choose pkl to save configuration",
                                                         filter='png (*.png)')
        # save the figure
        self.fig.savefig(filename[0])

    # Save the data in a csv file
    def SaveData(self):
        from csv import writer as csv_writer
        # get filename at storage place
        filename = QtWidgets.QFileDialog.getSaveFileName(caption="Choose pkl to save configuration",
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
            toWrite[i].append(f'Scenario {idx + 1}')
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
class CalcProblem(QtCore.QThread):
    any_signal = QtCore.pyqtSignal(DataStorage)

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
