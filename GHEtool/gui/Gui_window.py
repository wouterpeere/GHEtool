from sys import path
from typing import Optional, TYPE_CHECKING
from .Translation_class import TrClass
from PyQt5.QtWidgets import QMainWindow as QtWidgets_QMainWindow, QWidget as QtWidgets_QWidget, QApplication as \
    QtWidgets_QApplication, QPushButton as QtWidgets_QPushButton, QMessageBox as QtWidgets_QMessageBox, QFileDialog as \
    QtWidgets_QFileDialog, QInputDialog as QtWidgets_QInputDialog, QDialog as QtWidgets_QDialog, QMenu as \
    QtWidgets_QMenu, QDoubleSpinBox as QtWidgets_QDoubleSpinBox, QListWidgetItem as QtWidgets_QListWidgetItem, \
    QHBoxLayout as QtWidgets_QHBoxLayout
from pickle import dump as pk_dump, HIGHEST_PROTOCOL as pk_HP, load as pk_load
from PyQt5.QtCore import QSize as QtCore_QSize, QEvent as QtCore_QEvent, QThread as QtCore_QThread, \
    pyqtSignal as QtCore_pyqtSignal, QModelIndex as QtCore_QModelIndex
from PyQt5.QtGui import QIcon as QtGui_QIcon, QPixmap as QtGui_QPixmap
from .gui_Main import Ui_GHEtool
from os.path import dirname, realpath, split as os_split
from functools import partial as ft_partial
from .DataStorage_v1_0_0 import DataStorage
from time import sleep

if TYPE_CHECKING:
    from GHEtool import Borefield
    from pandas import DataFrame as pd_DataFrame, ExcelFile as pd_ExcelFile

currentdir = dirname(realpath(__file__))
parentdir = dirname(currentdir)
path.append(parentdir)


class BoundsOfPrecalculatedData:
    """
    class to check if selected values are within the bounds for the precalculated data
    """
    __slots__ = 'H', 'B_Min', 'B_Max', 'k_s_Min', 'k_s_Max', 'N_Max'

    def __init__(self) -> None:
        self.H: float = 350.0  # Maximal depth [m]
        self.B_Max: float = 9.0  # Maximal borehole spacing [m]
        self.B_Min: float = 3.0  # Minimal borehole spacing [m]
        self.k_s_Min: float = 1  # Minimal thermal conductivity of the soil [W/mK]
        self.k_s_Max: float = 4  # Maximal thermal conductivity of the soil [W/mK]
        self.N_Max: int = 20  # Maximal number of boreholes in one direction [#]

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


# main GUI class
class MainWindow(QtWidgets_QMainWindow, Ui_GHEtool):
    filenameDefault: tuple = ('', '')

    def __init__(self, dialog: QtWidgets_QWidget, app: QtWidgets_QApplication) -> None:
        """
        initialize window
        :param dialog: Q widget as main window
        :param app: application widget
        """
        # init windows of parent class
        super(MainWindow, self).__init__()
        super().setupUi(dialog)
        # set app and dialog
        self.app: QtWidgets_QApplication = app
        self.Dia = dialog
        # init variables of class
        self.translations: TrClass = TrClass()  # init translation class
        self.fileImport = None  # init import file
        self.filename: tuple = MainWindow.filenameDefault  # filename of stored inputs
        self.list_widget_scenario.clear()  # reset list widget with stored scenarios
        self.changedScenario: bool = False  # set change scenario variable to false
        self.changedFile: bool = False  # set change file variable to false
        self.ax: list = []  # axes of figure
        self.axBorehole = None
        self.canvas = None  # canvas class of figure
        self.fig = None  # figure
        self.NumberOfScenarios: int = 1  # number of scenarios
        self.finished: int = 1  # number of finished scenarios
        self.threads: list = []  # list of calculation threads
        self.ListDS: list = []  # list of data storages
        self.sizeB = QtCore_QSize(48, 48)  # size of big logo on push button
        self.sizeS = QtCore_QSize(24, 24)  # size of small logo on push button
        self.sizePushB = QtCore_QSize(150, 75)  # size of big push button
        self.sizePushS = QtCore_QSize(75, 75)  # size of small push button
        self.BOPD: BoundsOfPrecalculatedData = BoundsOfPrecalculatedData()  # init bounds of precalculated data class
        # init links from buttons to functions
        self.setLinks()
        # reset progress bar
        self.updateBar(0, False)
        # set event filter for push button sizing
        self.eventFilterInstall()
        # reset data type frames for importing of data
        self.dataType()
        # start importing GHEtool by a thread to save start up time
        self.IG: ImportGHEtool = ImportGHEtool()
        self.IG.start()
        self.IG.any_signal.connect(self.checkGHEtool)
        # show loading GHEtool message in statusbar
        self.status_bar.showMessage(self.translations.GHE_tool_imported_start, 5000)
        # enable push button because GHEtool ist not imported
        self.pushButton_start_multiple.setEnabled(False)
        self.pushButton_start_single.setEnabled(False)
        self.action_start_multiple.setEnabled(False)
        self.action_start_single.setEnabled(False)
        # add languages to combo box
        self.comboBox_Language.addItems(self.translations.comboBoxLanguageList)
        # hide warning for custom bore field calculation
        self.label_WarningCustomBorefield.hide()
        # load backup data
        self.loadList()
        # add progress bar and label to statusbar
        self.status_bar.addPermanentWidget(self.label_Status, 0)
        self.status_bar.addPermanentWidget(self.progressBar, 1)
        self.status_bar.messageChanged.connect(self.statusHide)
        # change window title to saved filename
        self.changeWindowTitle()
        # add action shortcut for changing language to english
        self.actionEnglish.setShortcut("Ctrl+Alt+E")
        # show / hide frames
        self.showSimulationVariables(self.comboBox_aim.currentIndex())
        self.showBoreholeResistanceBoxes(self.comboBox_Rb_method.currentIndex())
        # set links to check if changes happen
        self.actionInputChanged.triggered.connect(self.change)
        # allow checking of changes
        self.checking: bool = True
        # reset push button size
        self.setPush(False)
        # set start page to general page
        self.pushButton_General.click()

    def eventFilterInstall(self) -> None:
        """
        install event filter for push button sizing
        :return: None
        """
        self.pushButton_General.installEventFilter(self)
        self.pushButton_thermalDemands.installEventFilter(self)
        self.pushButton_Results.installEventFilter(self)
        self.pushButton_Settings.installEventFilter(self)
        self.pushButton_borehole_resistance.installEventFilter(self)
        self.label_GapGenTh.installEventFilter(self)
        self.label_GapThRes.installEventFilter(self)
        self.label_GapResSet.installEventFilter(self)
        self.label_GapBR_Res.installEventFilter(self)

    def setLinks(self) -> None:
        """
        set links of buttons and actions to function
        :return: None
        """
        self.pushButton_thermalDemands.clicked.connect(ft_partial(self.stackedWidget.setCurrentWidget,
                                                                  self.page_thermal))
        self.pushButton_Results.clicked.connect(ft_partial(self.stackedWidget.setCurrentWidget, self.page_Results))
        self.pushButton_Results.clicked.connect(self.displayResults)
        self.pushButton_Settings.clicked.connect(ft_partial(self.stackedWidget.setCurrentWidget, self.page_Settings))
        self.pushButton_borehole_resistance.clicked.connect(ft_partial(self.stackedWidget.setCurrentWidget,
                                                                       self.page_borehole_resistance))
        self.pushButton_General.clicked.connect(ft_partial(self.stackedWidget.setCurrentWidget, self.page_General))
        self.pushButton_NextGeneral.clicked.connect(self.pushButton_borehole_resistance.click)
        self.pushButton_PreviousThermal.clicked.connect(self.pushButton_borehole_resistance.click)
        self.pushButton_PreviousResistance.clicked.connect(self.pushButton_General.click)
        self.pushButton_NextResistance.clicked.connect(self.pushButton_thermalDemands.click)
        self.pushButton_SaveFigure.clicked.connect(self.saveFigure)
        self.pushButton_SaveData.clicked.connect(self.save_data)
        self.actionAdd_Scenario.triggered.connect(self.addScenario)
        self.actionUpdate_Scenario.triggered.connect(self.saveScenario)
        self.actionDelete_scenario.triggered.connect(self.deleteScenario)
        self.checkBox_Legend.clicked.connect(self.checkLegend)
        self.comboBox_Datentyp.currentIndexChanged.connect(self.dataType)
        self.pushButton_loadCsv.clicked.connect(self.funChooseFile)
        self.action_start_multiple.triggered.connect(self.startMultipleScenariosCalculation)
        self.action_start_single.triggered.connect(self.startCurrentScenarioCalculation)
        self.actionSave.triggered.connect(self.funSave)
        self.actionSave_As.triggered.connect(self.funSaveAs)
        self.actionOpen.triggered.connect(self.funLoad)
        self.actionNew.triggered.connect(self.funNew)
        self.actionEnglish.triggered.connect(ft_partial(self.comboBox_Language.setCurrentIndex, 0))
        self.actionGerman.triggered.connect(ft_partial(self.comboBox_Language.setCurrentIndex, 1))
        self.actionDutch.triggered.connect(ft_partial(self.comboBox_Language.setCurrentIndex, 2))
        self.actionItalian.triggered.connect(ft_partial(self.comboBox_Language.setCurrentIndex, 3))
        self.actionFrench.triggered.connect(ft_partial(self.comboBox_Language.setCurrentIndex, 4))
        self.actionSpanish.triggered.connect(ft_partial(self.comboBox_Language.setCurrentIndex, 5))
        self.actionGalician.triggered.connect(ft_partial(self.comboBox_Language.setCurrentIndex, 6))
        self.doubleSpinBox_pipe_outer_radius.valueChanged.connect(self.doubleSpinBox_pipe_inner_radius.setMaximum)
        self.doubleSpinBox_pipe_inner_radius.valueChanged.connect(self.doubleSpinBox_pipe_outer_radius.setMinimum)
        self.doubleSpinBox_H.valueChanged.connect(self.checkBounds)
        self.doubleSpinBox_B.valueChanged.connect(self.checkBounds)
        self.doubleSpinBox_k_s.valueChanged.connect(self.checkBounds)
        self.spinBox_N_1.valueChanged.connect(self.checkBounds)
        self.spinBox_N_2.valueChanged.connect(self.checkBounds)
        self.pushButton_load.clicked.connect(self.funLoadFile)
        self.comboBox_dataColumn.currentIndexChanged.connect(self.funChooseColumnDemand)
        self.comboBox_timeStep.currentIndexChanged.connect(self.funChooseColumnTimeStep)
        self.pushButton_calculate.clicked.connect(self.funDisplayData)
        self.pushButton_Unit.clicked.connect(self.funChangeUnit)
        self.actionRename_scenario.triggered.connect(self.funRenameScenario)
        self.comboBox_aim.currentIndexChanged.connect(self.showSimulationVariables)
        self.comboBox_Rb_method.currentIndexChanged.connect(self.showBoreholeResistanceBoxes)
        self.list_widget_scenario.model().rowsMoved.connect(self.funMoveScenario)
        self.list_widget_scenario.currentItemChanged.connect(self.funAutoSaveScenario)
        self.pushButton_data_file_select.clicked.connect(self.funChooseDataFile)
        self.lineEdit_filename_data_file.textChanged.connect(self.funUpdateComboBoxDataFile)
        self.comboBox_dataColumn_data_file.currentIndexChanged.connect(self.frame_heatingLoad_data_File.setHidden)
        self.comboBox_dataColumn_data_file.currentIndexChanged.connect(self.frame_coolingLoad_data_file.setHidden)
        self.comboBox_dataColumn_data_file.currentIndexChanged.connect(self.frame_combined_data_file.setVisible)
        self.comboBox_dataColumn_data_file.setCurrentIndex(not self.comboBox_dataColumn_data_file.currentIndex())
        self.comboBox_dataColumn_data_file.setCurrentIndex(not self.comboBox_dataColumn_data_file.currentIndex())
        self.actionCheckUDistance.triggered.connect(self.checkDistanceBetweenPipes)
        self.comboBox_Language.currentIndexChanged.connect(self.changeLanguage)
        self.actionUpdateBoreholeGraph.triggered.connect(self.updateBorehole)
        self.Dia.closeEvent = self.closeEvent
        self.checkBox_Import.toggle()
        self.checkBox_Import.toggle()

    def change(self) -> None:
        """
        check if changes to scenario or saved file happened
        :return: None
        """
        # return if checking is not allowed
        if not self.checking:
            return
        # if changed File is not already True set it to True and update window title
        if self.changedFile is False:
            self.changedFile: bool = True
            self.changeWindowTitle()
        # abort here if autosave scenarios is used
        if self.checkBox_AutoSaving.isChecked():
            return
        # if list is empty return
        if not self.ListDS:
            return
        # get text string of current scenario
        text: str = self.list_widget_scenario.currentItem().text()
        # abort if there is no text
        if len(text) < 1:
            return
        # get current index of scenario
        idx: int = self.list_widget_scenario.currentRow()
        # create current data storage
        ds: DataStorage = DataStorage(id(self))
        # check if current data storage is equal to the previous one then delete the *
        if self.ListDS:
            if ds == self.ListDS[idx]:
                if text[-1] != '*':
                    return
                self.list_widget_scenario.item(idx).setText(text[:-1])
                return
        # if scenario is already marked as changed return
        if text[-1] == '*':
            return
        # else add * to current item string
        self.list_widget_scenario.item(idx).setText(f'{text}*')

    def funAutoSaveScenario(self, newRowItem: QtWidgets_QListWidgetItem, oldRowItem: QtWidgets_QListWidgetItem) -> None:
        """
        function to save a scenario when the item in the list Widget is changed and the checkBox to save automatic is
        checked or ask to save unsaved scenario changes
        :param newRowItem: new selected scenario item (not used)
        :param oldRowItem: old scenario item
        :return: None
        """
        # if no old item is selected do nothing and return
        if oldRowItem is None:
            # change entries to new scenario values
            self.changeScenario(self.list_widget_scenario.row(newRowItem))
            return
        # check if the auto saving should be performed and then save the last selected scenario
        if self.checkBox_AutoSaving.isChecked():
            # save old scenario
            self.ListDS[self.list_widget_scenario.row(oldRowItem)] = DataStorage(id(self))
            # update backup fileImport
            self.funSaveAuto()
            # change values to new scenario values
            self.changeScenario(self.list_widget_scenario.row(newRowItem))
            # abort function
            return
        # get test of old scenario (item)
        text = oldRowItem.text()
        # check if the old scenario is unsaved then create message box
        if text[-1] == '*':
            # create message box
            msg: QtWidgets_QMessageBox = QtWidgets_QMessageBox(self.Dia)
            # set Icon to question mark icon
            msg.setIcon(QtWidgets_QMessageBox.Question)
            # set label text to leave scenario text depending on language selected
            msg.setText(self.translations.label_LeaveScenarioText)
            # set window text to  leave scenario text depending on language selected
            msg.setWindowTitle(self.translations.label_CancelTitle)
            # set standard buttons to save, close and cancel
            msg.setStandardButtons(
                QtWidgets_QMessageBox.Save | QtWidgets_QMessageBox.Close | QtWidgets_QMessageBox.Cancel)
            # get save, close and cancel button
            buttonS = msg.button(QtWidgets_QMessageBox.Save)
            buttonCl = msg.button(QtWidgets_QMessageBox.Close)
            buttonCa = msg.button(QtWidgets_QMessageBox.Cancel)
            # set save, close and cancel button text depending on language selected
            buttonS.setText(f'{self.translations.pushButton_SaveScenario} ')
            buttonCl.setText(f'{self.translations.label_LeaveScenario} ')
            buttonCa.setText(f'{self.translations.label_StayScenario} ')
            # set  save, close and cancel button icon
            self.setPushButtonIcon(buttonS, 'Save_Inv')
            self.setPushButtonIcon(buttonCl, 'Exit')
            self.setPushButtonIcon(buttonCa, 'Abort')
            # execute message box and save response
            reply = msg.exec_()
            # check if closing should be canceled
            if reply == QtWidgets_QMessageBox.Cancel:
                # change item to old item by thread, because I have not found a direct way which is not lost after
                # return
                SI = SetItem(self.list_widget_scenario, oldRowItem)  # create class
                SI.start()  # start thread
                SI.any_signal.connect(SI.terminate)  # stop thread if finished
                # abort the rest
                return
            # save scenario if wanted
            self.saveScenario() if reply == QtWidgets_QMessageBox.Save else None
            # remove * symbol
            oldRowItem.setText(text[:-1])
        # change entries to new scenario values
        self.changeScenario(self.list_widget_scenario.row(newRowItem))
        return

    def checkDistanceBetweenPipes(self) -> None:
        """
        calculate and set minimal and maximal distance between U pipes and center
        :return: None
        """
        # import math stuff
        from math import pi, sin, cos, tan
        nU: int = self.spinBox_number_pipes.value()  # get number of U pipes
        rBorehole: float = self.doubleSpinBox_borehole_radius.value()  # get borehole radius
        rOuterPipe: float = self.doubleSpinBox_pipe_outer_radius.value()  # get outer pipe radius
        rOuterPipeMax: float = rBorehole/(1+1/sin(pi/(2*nU)))  # calculate maximal outer pipe radius(see Circle packing)
        distanceMax: float = rBorehole - rOuterPipeMax  # calculate maximal distance between pipe and center
        alpha: float = pi/nU  # determine equal angle between pipes
        # determine minimal distance between pipe and center if number of pipes is bigger than one else set to half
        # borehole radius
        distanceMin: float = 2*rOuterPipe*(cos((pi-alpha)/2)+sin((pi-alpha)/2)/tan(alpha)) if nU > 1 else rBorehole/2
        # set minimal and maximal value for pipe distance
        self.doubleSpinBox_pipe_distance.setMinimum(distanceMin)
        self.doubleSpinBox_pipe_distance.setMaximum(distanceMax)

    def funMoveScenario(self, startItem: QtCore_QModelIndex, startIndex: int, startIndex2: int,
                        endItem: QtCore_QModelIndex, targetIndex: int) -> None:
        """
        change list of ds entry if scenario is moved (more inputs than needed, because the list widget returns that much
        :param startItem: start item of moving
        :param startIndex: start index of moving
        :param startIndex2: start index of moving
        :param endItem: start end of moving
        :param targetIndex: target index of moving
        :return: None
        """
        self.ListDS.insert(targetIndex, self.ListDS.pop(startIndex))

    @staticmethod
    def setPushButtonIcon(button: QtWidgets_QPushButton, iconName: str) -> None:
        """
        set QPushButton icon
        :param button: QPushButton to change to icon for
        :param iconName: icon name as string
        :return: None
        """
        icon = QtGui_QIcon()  # create icon class
        # add pixmap to icon
        icon.addPixmap(QtGui_QPixmap(f":/icons/icons/{iconName}.svg"), QtGui_QIcon.Normal, QtGui_QIcon.Off)
        button.setIcon(icon)  # set icon to button

    def funRenameScenario(self) -> None:
        """
        function to rename current scenario with a dialog box to ask for new name
        :return: None
        """
        # get current item
        item = self.list_widget_scenario.currentItem()
        # get first item if no one is selected
        item = self.list_widget_scenario.item(0) if item is None else item
        # create dialog box to ask for a new name
        dialog = QtWidgets_QInputDialog(self.Dia)
        dialog.setWindowTitle(self.translations.label_new_scenario)
        dialog.setLabelText(f"{self.translations.new_name}{item.text()}:")
        dialog.setOkButtonText(self.translations.label_okay)  # +++
        dialog.setCancelButtonText(self.translations.label_abort)  # +++
        li = dialog.findChildren(QtWidgets_QPushButton)
        self.setPushButtonIcon(li[0], 'Okay')
        self.setPushButtonIcon(li[1], 'Abort')
        # set new name if the dialog is not canceled and the text is not None
        if dialog.exec_() == QtWidgets_QDialog.Accepted:
            text = dialog.textValue()
            item.setText(text) if text != '' else None

    def checkResults(self) -> None:
        """
        check if results exists and then display them
        :return:
        """
        # hide results buttons if no results where found
        if any([(i.boreField is None) for i in self.ListDS]) or self.ListDS == []:
            self.pushButton_SaveData.hide()
            self.pushButton_General.click()
            return
        # display results otherwise
        self.displayResults()

    def changeWindowTitle(self) -> None:
        """
        change window title to filename and mark with * if unsaved changes exists
        :return: None
        """
        # get filename separated from path
        path, filename = MainWindow.filenameDefault if self.filename == MainWindow.filenameDefault else \
            os_split(self.filename[0])
        # title determine new title if a filename is not empty
        title: str = '' if filename == '' else f' - {filename.replace(".pkl", "")}'
        # create new title name
        name: str = f'GHEtool {title}*' if self.changedFile else f'GHEtool {title}'
        # set new title name
        self.Dia.setWindowTitle(name)

    def statusHide(self, text) -> None:
        """
        show or hide statusbar if no text exists
        :param text: text in status bar
        :return: None
        """
        if text == '':
            self.status_bar.hide()
            return
        self.status_bar.show()

    def checkBounds(self) -> None:
        """
        check if precalculated bounds are extended then show warning
        :return: None
        """
        # check if current selection is outside the precalculated data
        outside_bounds: bool = self.BOPD.check_if_outside_bounds(self.doubleSpinBox_H.value(),
                                                                 self.doubleSpinBox_B.value(),
                                                                 self.doubleSpinBox_k_s.value(),
                                                                 max(self.spinBox_N_1.value(), self.spinBox_N_2.value())
                                                                 )
        # if so show label with warning message
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
            self.setPush(True)
            return True
        elif event.type() == QtCore_QEvent.Leave:
            # Mouse is not over the label
            self.setPush(False)
            return True
        return False

    def setPushButtonIconSize(self, button: QtWidgets_QPushButton, big: bool = False, name: str = '') -> None:
        """
        set button name and size
        :param button: QPushButton to set name and icon size for
        :param big: big or small icon size (True = big)
        :param name: name to set to QPushButton
        :return: None
        """
        button.setText(name)  # set name to button
        # size big or small QPushButton depending on input
        if big:
            button.setIconSize(self.sizeS)
            button.setMaximumSize(self.sizePushB)
            button.setMinimumSize(self.sizePushB)
            return
        button.setIconSize(self.sizeB)
        button.setMaximumSize(self.sizePushS)
        button.setMinimumSize(self.sizePushS)

    def setPush(self, mouseOver: bool) -> None:
        """
        function to Set PushButton Text if MouseOver
        :param mouseOver: bool true if Mouse is over PushButton
        :return: None
        """
        # if Mouse is over PushButton change size to big otherwise to small
        if mouseOver:
            self.setPushButtonIconSize(self.pushButton_General, True, self.translations.pushButton_General)
            self.setPushButtonIconSize(self.pushButton_thermalDemands, True,
                                       self.translations.pushButton_thermalDemands)
            self.setPushButtonIconSize(self.pushButton_Results, True, self.translations.pushButton_Results)
            self.setPushButtonIconSize(self.pushButton_Settings, True, self.translations.label_Settings)
            self.setPushButtonIconSize(self.pushButton_borehole_resistance, True,
                                       self.translations.pushButton_borehole_resistance)
            return
        self.setPushButtonIconSize(self.pushButton_General)
        self.setPushButtonIconSize(self.pushButton_thermalDemands)
        self.setPushButtonIconSize(self.pushButton_Results)
        self.setPushButtonIconSize(self.pushButton_Settings)
        self.setPushButtonIconSize(self.pushButton_borehole_resistance)

    @staticmethod
    def displayValuesWithFloatingDecimal(spinbox: QtWidgets_QDoubleSpinBox, factor: float) -> None:
        """
        change decimal of spinbox to given factor
        :param spinbox: QSpinbox to change value for
        :param factor: factor to change spinbox value with
        :return: None
        """
        value = spinbox.value() * factor  # determine new value by multiply with factor
        # determine decimal location depending on value
        decimal_loc = 0 if value >= 1_000 else 1 if value >= 100 else 2 if value >= 10 else 3 if value >= 1 else 4
        spinbox.setDecimals(decimal_loc)  # set decimal location
        spinbox.setMaximum(max(value*10, 1_000_000))  # set maximal value to maximal value * 10 or 1_000_000
        spinbox.setValue(value)  # set new value

    def changeLanguage(self) -> None:
        """
        function to change language on labels and push buttons
        :return: None
        """
        scenarioIndex: int = self.list_widget_scenario.currentRow()  # get current selected scenario
        amount: int = self.list_widget_scenario.count()  # number of scenario elements
        # check if list scenario names are not unique
        liStrMatch: list = [self.list_widget_scenario.item(idx).text() ==
                            f'{self.translations.scenarioString}: {idx + 1}' for idx in range(amount)]
        # change language to the selected one
        self.translations.changeLanguage(self.comboBox_Language.currentIndex())
        # update all label, pushButtons, action and Menu names
        for i in [j for j in self.translations.__slots__ if hasattr(self, j)]:
            if isinstance(getattr(self, i), QtWidgets_QMenu):
                getattr(self, i).setTitle(getattr(self.translations, i))
                continue
            getattr(self, i).setText(getattr(self.translations, i))
        # set translation of toolbox items
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_File), self.translations.toolBoxFile)
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_DataLocation), self.translations.toolBoxDataLocation)
        # update lists in comboBoxs
        [self.comboBox_Language.setItemText(i, name) for i, name in enumerate(self.translations.comboBoxLanguageList)]
        [self.comboBox_depth_Method.setItemText(i, name) for i, name in
         enumerate(self.translations.comboBoxSizeMethodList)]
        [self.comboBox_Size_Method.setItemText(i, name) for i, name in
         enumerate(self.translations.comboBoxSizeMethodList)]
        [self.comboBox_aim.setItemText(i, name) for i, name in enumerate(self.translations.comboBox_AimList)]
        [self.comboBox_Seperator.setItemText(i, name) for i, name in
         enumerate(self.translations.comboBox_SeperatorList)]
        [self.comboBox_SeperatorDataFile.setItemText(i, name) for i, name in
         enumerate(self.translations.comboBox_SeperatorList)]
        [self.comboBox_decimal.setItemText(i, name) for i, name in
         enumerate(self.translations.comboBox_decimalList)]
        [self.comboBox_decimalDataFile.setItemText(i, name) for i, name in
         enumerate(self.translations.comboBox_decimalList)]
        [self.comboBox_dataColumn.setItemText(i, name) for i, name in
         enumerate(self.translations.comboBoxDataColumnList)]
        [self.comboBox_dataColumn_data_file.setItemText(i, name) for i, name in
         enumerate(self.translations.comboBoxDataColumnList)]
        [self.comboBox_timeStep.setItemText(i, name) for i, name in enumerate(self.translations.comboBoxTimeStepList)]
        [self.comboBox_Rb_method.setItemText(i, name) for i, name in
         enumerate(self.translations.comboBox_Rb_methodList)]
        # update labels depending on selected scenario
        self.showSimulationVariables(self.comboBox_aim.currentIndex())
        # set small PushButtons
        self.setPush(False)
        # replace scenario names if they are not unique
        scenarios: list = [f'{self.translations.scenarioString}: {i}' if liStrMatch[i - 1] else
                           self.list_widget_scenario.item(i-1).text() for i in range(1, amount + 1)]
        # clear list widget with scenario and write new ones
        self.list_widget_scenario.clear()
        if amount > 0:
            self.list_widget_scenario.addItems(scenarios)
        # select current scenario
        self.list_widget_scenario.setCurrentRow(scenarioIndex) if scenarioIndex >= 0 else None

    def loadList(self) -> None:
        """
        try to open the backup file and set the old values
        :return: None
        """
        # try to open backup file if it exits
        try:
            # open backup file
            with open("backup.pkl", "rb") as f:
                saving: tuple = pk_load(f)
            self.filename, li, settings = saving  # get saved data and unpack tuple
            self.ListDS, li = li[0], li[1]  # unpack tuple to get list of data-storages and scenario names
            self.comboBox_Language.setCurrentIndex(settings[0])  # set last time selected language
            self.checkBox_AutoSaving.setChecked(settings[1])  # set last time selected automatic saving scenario option
            # replace uer window id
            for DS in self.ListDS:
                DS.ui = id(self)
            # clear list widget and add new items and select the first one
            self.list_widget_scenario.clear()
            self.list_widget_scenario.addItems(li)
            self.list_widget_scenario.setCurrentRow(0)
            # check if results exits and then display them
            self.checkResults()
        except FileNotFoundError:
            # hide custom bore field warning
            self.label_WarningCustomBorefield.hide()
            # change language to english
            self.changeLanguage()
            # show message that no backup file is found
            self.status_bar.showMessage(self.translations.NoBackupFile)

    def funSaveAuto(self) -> None:
        """
        function to automatically save data in backup file
        :return: None
        """
        # append scenario if no scenario is in list
        if len(self.ListDS) < 1:
            self.ListDS.append(DataStorage(id(self)))
        # create list of scenario names
        li: list = [self.list_widget_scenario.item(idx).text() for idx in range(self.list_widget_scenario.count())]
        # create list of settings with language and autosave option
        settings: list = [self.comboBox_Language.currentIndex(), self.checkBox_AutoSaving.isChecked()]
        # try to write data to back up file
        try:
            # write data to back up file
            with open("backup.pkl", "wb") as f:
                saving = self.filename, [self.ListDS, li], settings
                pk_dump(saving, f, pk_HP)
        except FileNotFoundError:
            self.status_bar.showMessage(self.translations.NoFileSelected, 5000)

    def dataType(self) -> str:
        """
        function to choose Datatype of selected data
        :return: str
        """
        # get current index of data file
        index = self.comboBox_Datentyp.currentText()
        # hide labels and reset line edit text
        self.lineEdit_displayCsv.setText("")
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
        # show and hide comboBoxes depending on index selected
        self.frame_Seperator.show() if index == '.csv' else self.frame_Seperator.hide()
        self.frame_decimal.show() if index == '.csv' else self.frame_decimal.hide()
        self.frame_sheetName.show() if index == '.xlsx' or index == '.xls' else self.frame_sheetName.hide()
        # return index
        return index

    def funChooseDataFile(self) -> None:
        """
        select csv fileImport for optimise load profile
        :return: None
        """
        # choose datafile to optimize load for
        filename = QtWidgets_QFileDialog.getOpenFileName(caption=self.translations.ChooseCSV,
                                                         filter='(*.csv)')
        # set filename to line edit
        self.lineEdit_filename_data_file.setText(filename[0])
        # update comboBoxes
        self.funUpdateComboBoxDataFile(filename[0])

    def funUpdateComboBoxDataFile(self, filename: str) -> None:
        """
        update comboBox if new data file is selected
        :param filename: filename of data file
        :return: None
        """
        # import pandas here to save start up time
        from pandas import read_csv as pd_read_csv
        # get decimal and column seperator
        sep: str = ';' if self.comboBox_SeperatorDataFile.currentIndex() == 0 else ','
        dec: str = '.' if self.comboBox_decimalDataFile.currentIndex() == 0 else ','
        # try to read CSV-File
        try:
            data: pd_DataFrame = pd_read_csv(filename, sep=sep, decimal=dec)
        except FileNotFoundError:
            self.status_bar.showMessage(self.translations.NoFileSelected, 5000)
            return
        # get data column names to set them to comboBoxes
        columns = data.columns
        # clear comboBoxes and add column names
        self.comboBox_heatingLoad_data_file.clear()
        self.comboBox_coolingLoad_data_file.clear()
        self.comboBox_combined_data_file.clear()
        self.comboBox_heatingLoad_data_file.addItems(columns)
        self.comboBox_coolingLoad_data_file.addItems(columns)
        self.comboBox_combined_data_file.addItems(columns)
        # set column selection mode to 2 columns if more than one line exists
        self.comboBox_dataColumn_data_file.setCurrentIndex(0 if len(columns) > 0 else 1)

    def funChooseFile(self) -> None:
        """
        function to choose data file Import
        :return: None
        """
        # try to ask for a file otherwise show message in status bar
        try:
            # get file data file type
            file_index = self.comboBox_Datentyp.currentText()
            # ask for a csv file if selected and set filename in line edit
            if file_index == '.csv':
                filename = QtWidgets_QFileDialog.getOpenFileName(caption=self.translations.ChooseCSV,
                                                                 filter='(*.csv)')
                self.lineEdit_displayCsv.setText(filename[0])
            # ask for excel file if selected and set filename in line edit
            elif file_index == '.xlsx' or file_index == '.xls':
                if file_index == '.xlsx':
                    filename = QtWidgets_QFileDialog.getOpenFileName(caption=self.translations.ChooseXLSX,
                                                                     filter='(*.xlsx)')
                else:
                    filename = QtWidgets_QFileDialog.getOpenFileName(caption=self.translations.ChooseXLS,
                                                                     filter='(*.xls)')
                self.lineEdit_displayCsv.setText(filename[0])
                # Retrieve the filename
                file = pd_ExcelFile(filename[0])
                # Get the sheet name and let the user choose in the comboBox
                sheet_name = file.sheet_names
                self.comboBox_sheetName.clear()
                self.comboBox_sheetName.addItems(sheet_name)
            else:
                pass
        # show warning if no file is selected in status bar for 5 seconds
        except FileNotFoundError:
            self.status_bar.showMessage(self.translations.NoFileSelected, 5000)

    def funLoadFile(self) -> None:
        """
        function to load data file import
        :return: None
        """
        # get filename from line edit
        filename = self.lineEdit_displayCsv.text()

        self.frame_heatingLoad.hide()
        self.frame_coolingLoad.hide()
        self.frame_date.hide()
        # clear all comboBox
        self.comboBox_coolingLoad.clear()
        self.comboBox_heatingLoad.clear()
        self.comboBox_combined.clear()
        self.comboBox_dataColumn.setCurrentIndex(-1)
        self.comboBox_timeStep.setCurrentIndex(-1)
        try:
            # open filename by sheet or with column and decimal seperator
            if ".xlsx" in filename:
                # import pandas here to save start up time
                sheet_name = self.comboBox_sheetName.currentText()
                from pandas import read_excel as pd_read_excel
                df = pd_read_excel(filename, sheet_name=sheet_name, nrows=1)
            elif ".csv" in filename:
                # import pandas here to save start up time
                from pandas import read_csv as pd_read_csv
                sep: str = ';' if self.comboBox_Seperator.currentIndex() == 0 else ','
                dec: str = '.' if self.comboBox_decimal.currentIndex() == 0 else ','
                df = pd_read_csv(filename, nrows=1, sep=sep, decimal=dec)
            else:
                df = None
            self.toolBox.setCurrentWidget(self.page_DataLocation)
            # Make the filename a Global variable so that it only load once
            self.fileImport = df
        # show warning if no file is selected in status bar for 5 seconds
        except FileNotFoundError:
            self.status_bar.showMessage(self.translations.NoFileSelected, 5000)

    def funChooseColumnDemand(self) -> None:
        """
        Show / hide / fill Column demand combo Boxes which includes the demand
        :return: None
        """
        # get imported data
        df = self.fileImport
        # if column list is empty create one
        columns: list = [''] if df is None else df.columns
        # get idx of current selection
        idx: int = self.comboBox_dataColumn.currentIndex()
        # show / hide load column combo Boxes / frames depending on index selectes
        self.frame_heatingLoad.show() if idx == 0 else self.frame_heatingLoad.hide()
        self.frame_coolingLoad.show() if idx == 0 else self.frame_coolingLoad.hide()
        self.frame_combined.show() if idx == 1 else self.frame_combined.hide()
        # clear combo Boxes
        self.comboBox_heatingLoad.clear()
        self.comboBox_coolingLoad.clear()
        self.comboBox_combined.clear()
        # Add the column names as items
        if idx == 0:
            self.comboBox_heatingLoad.addItems(columns)
            self.comboBox_coolingLoad.addItems(columns)
        elif idx == 1:
            self.comboBox_combined.addItems(columns)

    def funChooseColumnTimeStep(self) -> None:
        """
        Choose Column which includes the time step
        :return: None
        """
        # get file of to be imported data
        df = self.fileImport
        # get columns of import file
        columns = [''] if df is None else df.columns
        # index of time step selected
        idx: int = self.comboBox_timeStep.currentIndex()
        # if index is 2 (automatic time step by column) show comboBox/ frame and add columns
        self.frame_date.show() if idx == 2 else self.frame_date.hide()
        if idx == 2:
            self.comboBox_date.clear()
            self.comboBox_date.addItems(columns)

    def updateBorehole(self) -> None:
        """
        plots the position of the pipes in the borehole
        :return: None
        """
        # import all that is needed
        from math import pi
        from numpy import cos, sin
        from PyQt5.QtWidgets import QGraphicsScene, QGraphicsEllipseItem
        from PyQt5.QtGui import QColor, QPen
        # get variables from gui
        numberOfPipes = self.spinBox_number_pipes.value()
        rOut = self.doubleSpinBox_pipe_outer_radius.value() * 10
        rIn = self.doubleSpinBox_pipe_inner_radius.value() * 10
        rBore = self.doubleSpinBox_borehole_radius.value() * 10
        dis = self.doubleSpinBox_pipe_distance.value() * 10
        # calculate scale from graphic view size
        max_l = min(self.graphicsView.width(), self.graphicsView.height())
        scale = max_l/rBore/1.25  # leave 25 % space
        # set colors
        blue_color = QColor(0, 64, 122)
        blue_light = QColor(84, 188, 235)
        white_color = QColor(255, 255, 255)
        grey = QColor(100, 100, 100)
        brown = QColor(145, 124, 111)
        # create graphic scene if not exits otherwise get scene and delete items
        if self.graphicsView.scene() is None:
            scene = QGraphicsScene()
            self.graphicsView.setScene(scene)
            self.graphicsView.setBackgroundBrush(brown)
        else:
            scene = self.graphicsView.scene()
            scene.clear()
        # create borehole circle in grey wih no border
        circle = QGraphicsEllipseItem(-rBore*scale/2, -rBore*scale/2, rBore*scale, rBore*scale)
        circle.setPen(QPen(grey, 0))
        circle.setBrush(grey)
        scene.addItem(circle)
        # calculate pipe position and draw circle (white for outer pipe and blue for inner pipe)
        dt: float = pi / float(numberOfPipes)
        for i in range(numberOfPipes):
            pos_1 = dis * cos(2.0 * i * dt + pi)/2
            pos_2 = dis * sin(2.0 * i * dt + pi)/2
            circle = QGraphicsEllipseItem((pos_1 - rOut / 2) * scale, (pos_2 - rOut / 2) * scale,
                                          rOut * scale, rOut * scale)
            circle.setPen(white_color)
            circle.setBrush(white_color)
            scene.addItem(circle)
            circle = QGraphicsEllipseItem((pos_1 - rIn / 2) * scale, (pos_2 - rIn / 2) * scale,
                                          rIn * scale, rIn * scale)
            circle.setPen(blue_color)
            circle.setBrush(blue_color)
            scene.addItem(circle)
            pos_1 = dis * cos(2.0 * i * dt + pi + dt)/2
            pos_2 = dis * sin(2.0 * i * dt + pi + dt)/2
            circle = QGraphicsEllipseItem((pos_1 - rOut / 2) * scale, (pos_2 - rOut / 2) * scale,
                                          rOut * scale, rOut * scale)
            circle.setPen(white_color)
            circle.setBrush(white_color)
            scene.addItem(circle)
            circle = QGraphicsEllipseItem((pos_1 - rIn / 2) * scale, (pos_2 - rIn / 2) * scale,
                                          rIn * scale, rIn * scale)
            circle.setPen(blue_light)
            circle.setBrush(blue_light)
            scene.addItem(circle)

    def funDisplayData(self) -> None:
        """
        Load the Data to Display in the GUI
        :return: None
        """
        try:
            # get filename from line edit
            filename: str = self.lineEdit_displayCsv.text()
            # raise error if no filename exists
            if filename == '':
                raise FileNotFoundError
            # get thermal demands index (1 = 2 columns, 2 = 1 column)
            thermalDemand: int = self.comboBox_dataColumn.currentIndex()
            # Generate list of columns that have to be imported
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
            # read data either from excel file or csv file
            if ".xlsx" in filename or ".xls" in filename:
                # import pandas here to save start up time
                from pandas import read_excel as pd_read_excel
                sheet_name = self.comboBox_sheetName.currentText()
                df2: pd_DataFrame = pd_read_excel(filename, sheet_name=sheet_name, usecols=cols)
            elif ".csv" in filename:
                # import pandas here to save start up time
                from pandas import read_csv as pd_read_csv
                sep: str = ';' if self.comboBox_Seperator.currentIndex() == 0 else ','
                dec: str = '.' if self.comboBox_decimal.currentIndex() == 0 else ','
                df2: pd_DataFrame = pd_read_csv(filename, usecols=cols, sep=sep, decimal=dec)
            else:
                df2: pd_DataFrame = pd_DataFrame()
            # ---------------------- Time Step Section  ----------------------
            # get time step index
            timeStepIdx = self.comboBox_timeStep.currentIndex()
            # import pandas here to save start up time
            from pandas import to_datetime as pd_to_datetime, date_range as pd_date_range, Series as pd_Series
            # create date array of either 1 hour, 15 minute, or automatic
            if timeStepIdx == 0:  # 1 hour time step
                # Define start and end date
                start = pd_to_datetime("2019-01-01 00:00:00")
                end = pd_to_datetime("2019-12-31 23:59:00")
                # add date column
                df2[date] = pd_Series(pd_date_range(start, end, freq="1H"))
                # Create no dict to create mean values for
                dictAgg: Optional[None, dict] = None
            elif timeStepIdx == 1:  # 15 minute time step
                # Define start and end date
                start = pd_to_datetime("2019-01-01 00:00:00")
                end = pd_to_datetime("2019-12-31 23:59:00")
                # add date column
                df2[date] = pd_Series(pd_date_range(start, end, freq="15T"))
                # Create dict to create mean values for depending on selected columns
                dictAgg: Optional[None, dict] = {combined: 'mean'} if thermalDemand == 1 else {heatingLoad: 'mean',
                                                                                               coolingLoad: 'mean'}
            else:
                # Cast Date column to datetime format so pandas can work with it
                df2[date] = pd_to_datetime(df2[date])
                # Create dict to create mean values for depending on selected columns
                dictAgg: Optional[None, dict] = {combined: 'mean'} if thermalDemand == 1 else {heatingLoad: 'mean',
                                                                                               coolingLoad: 'mean'}
            # set date to index
            df2.set_index(date, inplace=True)
            # resample data to hourly resolution if necessary
            df2 = df2 if dictAgg is None else df2.resample("H").agg(dictAgg)
            # ------------------- Calculate Section --------------------
            # Choose path between Single or Combined Column and create new columns
            if thermalDemand == 0:
                # Resample the Data for peakHeating and peakCooling
                df2.rename(columns={heatingLoad: "Heating Load", coolingLoad: "Cooling Load"}, inplace=True)
                df2["peak Heating"] = df2["Heating Load"]
                df2["peak Cooling"] = df2["Cooling Load"]
            # by single column split by 0 to heating (>0) and cooling (<0)
            elif thermalDemand == 1:
                # Create Filter for heating and cooling load ( Heating Load +, Cooling Load -)
                heatingLoad = df2[combined].apply(lambda x: x >= 0)
                coolingLoad = df2[combined].apply(lambda x: x < 0)
                df2["Heating Load"] = df2.loc[heatingLoad, combined]
                df2["Cooling Load"] = df2.loc[coolingLoad, combined] * -1
                df2["peak Heating"] = df2["Heating Load"]
                df2["peak Cooling"] = df2["Cooling Load"]
            # resample to a monthly resolution as sum and maximal load
            df3 = df2.resample("M").agg({"Heating Load": "sum", "Cooling Load": "sum",
                                         "peak Heating": "max", "peak Cooling": "max"})
            # replace nan with 0
            df3 = df3.fillna(0)
            # ----------------------- Data Unit Section --------------------------
            # Get the Data Unit and set the label in the thermal Demand Box to follow
            data_unit = self.comboBox_dataUnit.currentText()
            # define unit factors
            fac = 0.001 if data_unit == 'W' else 1 if data_unit == 'kW' else 1000
            # set label unit to kW
            self.label_Unit_pH.setText(f'[kW]')
            self.label_Unit_pC.setText(f'[kW]')
            self.label_Unit_HL.setText(f'[kWh]')
            self.label_Unit_CL.setText(f'[kWh]')
            # multiply dataframe with unit factor and collect data
            df3 = df3 * fac
            peak_heating = df3["peak Heating"]
            peak_cooling = df3["peak Cooling"]
            heatingLoad = df3["Heating Load"]
            coolingLoad = df3["Cooling Load"]
            # set heating loads to double spinBoxes
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
            # set cooling loads to double spinBoxes
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
            # set peak heating load to double spinBoxes
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
            # set peak cooling load to double spinBoxes
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
        # raise error and display error massage in status bar
        except FileNotFoundError:
            self.status_bar.showMessage(self.translations.NoFileSelected, 5000)
        except IndexError:
            self.status_bar.showMessage(self.translations.ValueError, 5000)
        except KeyError:
            self.status_bar.showMessage(self.translations.ColumnError, 5000)

    def funChangeUnit(self) -> None:
        """
        function to change the unit
        :return: None
        """
        # get new and old unit from comboBox und labels
        peakNew = self.comboBox_Unit_peak.currentText()
        loadNew = self.comboBox_Unit_Load.currentText()
        peakOld = self.label_Unit_pH.text()
        peakOld = peakOld.replace('[', '')
        peakOld = peakOld.replace(']', '')
        loadOld = self.label_Unit_HL.text()
        loadOld = loadOld.replace('[', '')
        loadOld = loadOld.replace(']', '')
        # set new unit to labels
        self.label_Unit_HL.setText(f'[{loadNew}]')
        self.label_Unit_CL.setText(f'[{loadNew}]')
        self.label_Unit_pH.setText(f'[{peakNew}]')
        self.label_Unit_pC.setText(f'[{peakNew}]')
        # determine load converting factor
        if loadNew == loadOld:
            factorLoad = 1
        elif loadOld == 'Wh' and loadNew == 'MWh':
            factorLoad = 0.000_001
        elif (loadOld == 'Wh' and loadNew == 'kWh') or (loadOld == 'kWh' and loadNew == 'MWh'):
            factorLoad = 0.001
        elif (loadOld == 'kWh' and loadNew == 'Wh') or (loadOld == 'MWh' and loadNew == 'kWh'):
            factorLoad = 1_000
        elif loadOld == 'MWh' and loadNew == 'Wh':
            factorLoad = 1_000_000
        else:
            factorLoad = 0
        # determine peak converting factor
        if peakOld == peakNew:
            factorPeak = 1
        elif peakOld == 'W' and peakNew == 'MW':
            factorPeak = 0.000_001
        elif (peakOld == 'W' and peakNew == 'kW') or (peakOld == 'kW' and peakNew == 'MW'):
            factorPeak = 0.001
        elif (peakOld == 'kW' and peakNew == 'W') or (peakOld == 'MW' and peakNew == 'kW'):
            factorPeak = 1_000
        elif peakOld == 'MW' and peakNew == 'W':
            factorPeak = 1_000_000
        else:
            factorPeak = 0
        # set new values with a floating decimal to heating load
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_HL_Jan, factorLoad)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_HL_Feb, factorLoad)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_HL_Mar, factorLoad)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_HL_Apr, factorLoad)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_HL_May, factorLoad)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_HL_Jun, factorLoad)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_HL_Jul, factorLoad)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_HL_Aug, factorLoad)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_HL_Sep, factorLoad)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_HL_Oct, factorLoad)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_HL_Nov, factorLoad)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_HL_Dec, factorLoad)
        # set new values with a floating decimal to cooling load
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_CL_Jan, factorLoad)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_CL_Feb, factorLoad)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_CL_Mar, factorLoad)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_CL_Apr, factorLoad)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_CL_May, factorLoad)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_CL_Jun, factorLoad)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_CL_Jul, factorLoad)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_CL_Aug, factorLoad)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_CL_Sep, factorLoad)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_CL_Oct, factorLoad)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_CL_Nov, factorLoad)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_CL_Dec, factorLoad)
        # set new values with a floating decimal to peak heating
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_Hp_Jan, factorPeak)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_Hp_Feb, factorPeak)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_Hp_Mar, factorPeak)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_Hp_Apr, factorPeak)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_Hp_May, factorPeak)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_Hp_Jun, factorPeak)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_Hp_Jul, factorPeak)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_Hp_Aug, factorPeak)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_Hp_Sep, factorPeak)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_Hp_Oct, factorPeak)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_Hp_Nov, factorPeak)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_Hp_Dec, factorPeak)
        # set new values with a floating decimal to peak cooling
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_Cp_Jan, factorPeak)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_Cp_Feb, factorPeak)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_Cp_Mar, factorPeak)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_Cp_Apr, factorPeak)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_Cp_May, factorPeak)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_Cp_Jun, factorPeak)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_Cp_Jul, factorPeak)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_Cp_Aug, factorPeak)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_Cp_Sep, factorPeak)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_Cp_Oct, factorPeak)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_Cp_Nov, factorPeak)
        self.displayValuesWithFloatingDecimal(self.doubleSpinBox_Cp_Dec, factorPeak)

    def funLoad(self) -> None:
        """
        function to load externally stored scenario
        :return: None
        """
        # open interface and get file name
        self.filename = QtWidgets_QFileDialog.getOpenFileName(caption=self.translations.ChoosePKL,
                                                              filter='Pickle (*.pkl)')
        # load selected data
        self.funLoadKnownFilename()

    def funLoadKnownFilename(self) -> None:
        """
        load stored scenarios from external pickle file
        :return: None
        """
        # try to open the file
        try:
            # deactivate checking
            self.checking: bool = False
            # open file and get data
            with open(self.filename[0], "rb") as f:
                li: list = pk_load(f)
            # write data to variables
            self.ListDS, li = li[0], li[1]
            # change window title to new loaded filename
            self.changeWindowTitle()
            # replace user window id
            for DS in self.ListDS:
                DS.ui = id(self)
            # init user window by reset scenario list widget and check for results
            self.list_widget_scenario.clear()
            self.list_widget_scenario.addItems(li)
            self.list_widget_scenario.setCurrentRow(0)
            self.checkResults()
            # activate checking
            self.checking: bool = True
        # if no file is found display error message is status bar
        except FileNotFoundError:
            self.status_bar.showMessage(self.translations.NoFileSelected, 5000)

    def funSaveAs(self) -> None:
        """
        function to save under new filename
        :return: None
        """
        # reset filename because then the funSave function ask for a new filename
        self.filename = MainWindow.filenameDefault
        self.funSave()  # save data under a new filename

    def funSave(self) -> bool:
        """
        save all scenarios externally in a pickle file
        :return: boolean which is true if saving was successful
        """
        # ask for pickle file if the filename is still the default
        if self.filename == MainWindow.filenameDefault:
            self.filename: tuple = QtWidgets_QFileDialog.getSaveFileName(caption=self.translations.SavePKL,
                                                                         filter='Pickle (*.pkl)')
            # break function if no file is selected
            if self.filename == MainWindow.filenameDefault:
                return False
        # save scenarios
        self.saveScenario()
        # update backup file
        self.funSaveAuto()
        # Create list if no scenario is stored
        self.ListDS.append(DataStorage(id(self))) if len(self.ListDS) < 1 else None
        # try to store the data in the pickle file
        try:
            # create list of all scenario names
            li = [self.list_widget_scenario.item(idx).text() for idx in range(self.list_widget_scenario.count())]
            # store data
            with open(self.filename[0], "wb") as f:
                pk_dump([self.ListDS, li], f, pk_HP)
            # deactivate changed file * from window title
            self.changedFile: bool = False
            self.changeWindowTitle()
            # return true because everything was successful
            return True
        # show file not found message in status bar if an error appears
        except FileNotFoundError:
            self.status_bar.showMessage(self.translations.NoFileSelected, 5000)
            return False

    def funNew(self) -> None:
        """
        create new data file and reset GUI
        :return: None
        """
        self.filename: tuple = MainWindow.filenameDefault  # reset filename
        self.funSave()  # get and save filename
        self.ListDS: list = []  # reset list of data storages
        self.list_widget_scenario.clear()  # clear list widget with scenario list

    def changeScenario(self, idx: int) -> None:
        """
        update GUI if a new scenario at the comboBox is selected
        :param idx: index of selected scenario
        :return: None
        """
        # if i no scenario is selected (idx < 0) or no scenario exists break function
        if idx < 0 or idx >= len(self.ListDS):
            return
        # deactivate checking for changes
        self.checking: bool = False
        # get selected Datastorage from list
        ds: DataStorage = self.ListDS[idx]
        # set values of selected Datastorage
        ds.set_values()
        # activate checking for changed
        self.checking: bool = True
        # refresh results if results page is selected
        if self.stackedWidget.currentWidget() == self.page_Results:
            self.pushButton_Results.click()

    def saveScenario(self) -> None:
        """
        function to save selected scenario
        :return: None
        """
        # set boolean for unsaved scenario changes to False, because we save them now
        self.changedScenario: bool = False
        # get selected scenario index
        idx = max(self.list_widget_scenario.currentRow(), 0)
        # if no scenario exists create a new one else save DataStorage with new inputs in list of scenarios
        if len(self.ListDS) == idx:
            self.addScenario()
        else:
            self.ListDS[idx] = DataStorage(id(self))
        # create auto backup
        self.funSaveAuto()
        # remove * from scenario if not Auto save is checked and if the last char is a *
        if not self.checkBox_AutoSaving.isChecked():
            text = self.list_widget_scenario.item(idx).text()
            if text[-1] == '*':
                self.list_widget_scenario.item(idx).setText(text[:-1])

    def deleteScenario(self) -> None:
        """
        function to delete the selected scenario
        :return: None
        """
        # get current scenario index
        idx = self.list_widget_scenario.currentRow()
        # check if it is not scenarios exists and not the last one is selected (The last one can not be deleted)
        if idx > 0 or (len(self.ListDS) > 1 and idx == 0):
            # delete scenario from list
            del self.ListDS[idx]
            # delete scenario form list widget
            self.list_widget_scenario.takeItem(idx)
            # rename remaining scenarios if the name has not be changed
            for i in range(idx, self.list_widget_scenario.count()):
                item = self.list_widget_scenario.item(i)
                if item.text() == f'{self.translations.scenarioString}: {i + 2}':
                    item.setText(f'{self.translations.scenarioString}: {i + 1}')
            # select previous scenario then the deleted one but at least the first one
            self.list_widget_scenario.setCurrentRow(max(idx - 1, 0))

    def addScenario(self) -> None:
        """
        function to add a scenario
        :return: None
        """
        # get current number of scenario but at least 0
        number: int = max(len(self.ListDS), 0)
        # append new scenario to List of DataStorages
        self.ListDS.append(DataStorage(id(self)))
        # add new scenario name and item to list widget
        self.list_widget_scenario.addItem(f'{self.translations.scenarioString}: {number + 1}')
        # select new list item
        self.list_widget_scenario.setCurrentRow(number)
        # run change function to mark unsaved inputs
        self.change()

    def showSimulationVariables(self, idx: int) -> None:
        """
        show or hide input boxes depending on the purpose of simulation selected in comboBox_AimList
        :param idx: selected index
        :return: None
        """
        # hide import and thermal demands frames and label if optmize load profile is selected
        self.label_Import.hide() if idx == 3 else self.label_Import.show()
        self.frame_import.hide() if idx == 3 else self.frame_import.show()
        self.label_39.hide() if idx == 3 else self.label_39.show()
        self.label_ThermalDemands.hide() if idx == 3 else self.label_ThermalDemands.show()
        self.frame_thermal_demand.hide() if idx == 3 else self.frame_thermal_demand.show()
        self.label_51.hide() if idx == 3 else self.label_51.show()
        # show select datafile frame and label
        self.label_data_file.show() if idx == 3 else self.label_data_file.hide()
        self.frame_data_file.show() if idx == 3 else self.frame_data_file.hide()
        # hide borehole depth label and spin box if determination of depth is selected
        self.label_H.hide() if idx == 1 else self.label_H.show()
        self.doubleSpinBox_H.hide() if idx == 1 else self.doubleSpinBox_H.show()
        # show label and combo box for selecting depth calculation method
        self.label_calc_method_depth.show() if idx == 1 or idx == 2 else self.label_calc_method_depth.hide()
        self.comboBox_depth_Method.show() if idx == 1 or idx == 2 else self.comboBox_depth_Method.hide()
        # set borehole spacing name to minimal borehole spacing if sizing by length and width is selected
        self.label_BS.setText(self.translations.label_B_min) if idx == 2 else \
            self.label_BS.setText(self.translations.label_BS)
        # set borehole depth name to maximal borehole depth if sizing by length and width is selected
        self.label_H.setText(self.translations.label_H_max) if idx == 2 else \
            self.label_H.setText(self.translations.label_H)
        # show labels and boxes for sizing by length and width
        self.label_calc_method_sizing.show() if idx == 2 else self.label_calc_method_sizing.hide()
        self.comboBox_Size_Method.show() if idx == 2 else self.comboBox_Size_Method.hide()
        self.label_B_max.show() if idx == 2 else self.label_B_max.hide()
        self.doubleSpinBox_B_max.show() if idx == 2 else self.doubleSpinBox_B_max.hide()
        self.label_MaxWidthField.show() if idx == 2 else self.label_MaxWidthField.hide()
        self.doubleSpinBox_W_max.show() if idx == 2 else self.doubleSpinBox_W_max.hide()
        self.label_MaxLengthField.show() if idx == 2 else self.label_MaxLengthField.hide()
        self.doubleSpinBox_L_max.show() if idx == 2 else self.doubleSpinBox_L_max.hide()
        # hide width and length label and spin boxes for number of boreholes if sizing by length and width is selected
        self.label_WidthField.hide() if idx == 2 else self.label_WidthField.show()
        self.spinBox_N_1.hide() if idx == 2 else self.spinBox_N_1.show()
        self.label_LengthField.hide() if idx == 2 else self.label_LengthField.show()
        self.spinBox_N_2.hide() if idx == 2 else self.spinBox_N_2.show()

    def showBoreholeResistanceBoxes(self, idx: int):
        """
        show or hide input boxes depending on the borehole resistance calculation method selected in comboBox_Rb_method
        :param idx: selected index
        :return: None
        """
        # hide label and spinBox for constant known thermal resistance if thermal resistance is unknown
        self.label_BoreholeResistance.hide() if idx > 0 else self.label_BoreholeResistance.show()
        self.label_2.hide() if idx > 0 else self.label_2.show()
        self.doubleSpinBox_Rb.hide() if idx > 0 else self.doubleSpinBox_Rb.show()
        # show frames and labels for fluid and pipe data if thermal resistance is unknown
        self.label_fluid_data.show() if idx > 0 else self.label_fluid_data.hide()
        self.frame_fluid_data.show() if idx > 0 else self.frame_fluid_data.hide()
        self.label_47.show() if idx > 0 else self.label_47.hide()
        self.label_48.show() if idx > 0 else self.label_48.hide()
        self.label_pipe_data.show() if idx > 0 else self.label_pipe_data.hide()
        self.frame_pipe_data.show() if idx > 0 else self.frame_pipe_data.hide()
        self.updateBorehole() if idx > 0 else None

    def updateBar(self, val: int, opt_start: bool = False) -> None:
        """
        update progress bar or hide them if not needed
        :param val: int of successfully calculated scenarios
        :param opt_start: bool which is true if the calculation started to show progressbar and labels
        :return: None
        """
        # show label and progress bar if calculation started otherwise hide them
        if opt_start:
            self.label_Status.show()
            self.progressBar.show()
            self.status_bar.show()
        else:
            self.label_Status.hide()
            self.progressBar.hide()
        # calculate percentage of calculated scenario
        val = val/self.NumberOfScenarios
        # set percentage to progress bar
        self.progressBar.setValue(round(val * 100))
        # hide labels and progressBar if all scenarios are calculated
        if val > 0.9999:
            self.label_Status.hide()
            self.progressBar.hide()
            # show message that calculation is finished
            self.status_bar.showMessage(self.translations.Calculation_Finished, 5000)

    def checkGHEtool(self, finished: bool) -> None:
        """
        check if GHEtool import is finished
        :param finished: bool which is true if import is finished
        :return: None
        """
        if finished:
            # stop thread which imported the GHEtool
            self.IG.terminate()
            # Enable the buttons and action again
            self.pushButton_start_multiple.setEnabled(True)
            self.pushButton_start_single.setEnabled(True)
            self.action_start_multiple.setEnabled(True)
            self.action_start_single.setEnabled(True)
            # show message that the GHEtool has been successfully imported
            self.status_bar.showMessage(self.translations.GHE_tool_imported, 5000)

    def threadFunction(self, ds: DataStorage) -> None:
        """
        turn on and off the old and new threads for the calculation
        :param ds: DataStorage of current thread
        :return: None
        """
        # stop finished thread
        self.threads[self.finished].terminate()
        # count number of finished calculated scenarios
        self.finished += 1
        # update progress bar
        self.updateBar(self.finished, True)
        # if number of finished is the number that has to be calculated enable buttons and actions and change page to
        # results page
        if self.finished == self.NumberOfScenarios:
            self.pushButton_start_multiple.setEnabled(True)
            self.pushButton_start_single.setEnabled(True)
            self.pushButton_SaveScenario.setEnabled(True)
            self.action_start_single.setEnabled(True)
            self.action_start_multiple.setEnabled(True)
            self.pushButton_Results.click()
            return
        # start new thread
        self.threads[self.finished].start()
        self.threads[self.finished].any_signal.connect(self.threadFunction)

    def startMultipleScenariosCalculation(self) -> None:
        """
        start calculation of all not calculated scenarios
        :return: None
        """
        # add scenario if no list of scenarios exits else save current scenario
        self.addScenario() if not self.ListDS else self.saveScenario()
        # return to thermal demands page if no file is selected
        if any([i.fileSelected for i in self.ListDS]):
            self.stackedWidget.setCurrentWidget(self.page_thermal)
            self.status_bar.showMessage(self.translations.NoFileSelected)
            return
        # disable buttons and actions to avoid two calculation at once
        self.pushButton_start_multiple.setEnabled(False)
        self.pushButton_start_single.setEnabled(False)
        self.pushButton_SaveScenario.setEnabled(False)
        self.action_start_single.setEnabled(False)
        self.action_start_multiple.setEnabled(False)
        # initialize finished scenarios counting variable
        self.finished: int = 0
        # update progress bar
        self.updateBar(0, True)
        # create list of threads with scenarios that have not been calculated
        self.threads = [CalcProblem(DS, idx) for idx, DS in enumerate(self.ListDS) if DS.boreField is None]
        # set number of to calculate scenarios
        self.NumberOfScenarios: int = len(self.threads)
        # start calculation if at least one scenario has to be calculated
        if self.NumberOfScenarios > 0:
            self.threads[0].start()
            self.threads[0].any_signal.connect(self.threadFunction)
            return

    def startCurrentScenarioCalculation(self) -> None:
        """
        start calculation of selected scenario
        :return: None
        """
        # add scenario if no list of scenarios exits else save current scenario
        self.addScenario() if not self.ListDS else self.saveScenario()
        # return to thermal demands page if no file is selected
        if self.ListDS[self.list_widget_scenario.currentRow()].fileSelected:
            self.stackedWidget.setCurrentWidget(self.page_thermal)
            self.status_bar.showMessage(self.translations.NoFileSelected)
            return
        # disable buttons and actions to avoid two calculation at once
        self.pushButton_start_multiple.setEnabled(False)
        self.pushButton_start_single.setEnabled(False)
        self.pushButton_SaveScenario.setEnabled(False)
        self.action_start_single.setEnabled(False)
        self.action_start_multiple.setEnabled(False)
        # initialize finished scenarios counting variable
        self.finished: int = 0
        # update progress bar
        self.updateBar(0, True)
        # get index of selected scenario
        idx: int = self.list_widget_scenario.currentRow()
        # get Datastorage of selected scenario
        ds: DataStorage = self.ListDS[idx]
        # if calculation is already done just show results
        if ds.boreField is not None:
            self.pushButton_Results.click()
            return
        # create list of threads with calculation to be made
        self.threads = [CalcProblem(ds, idx)]
        # set number of to calculate scenarios
        self.NumberOfScenarios: int = len(self.threads)
        # start calculation
        self.threads[0].start()
        self.threads[0].any_signal.connect(self.threadFunction)

    def displayResults(self) -> None:
        """
        display results of the current selected scenario
        :return: None
        """
        # hide widgets if no list of scenarios exists and display not calculated text
        if not self.ListDS:
            self.label_Size.setText(self.translations.NotCalculated)
            self.label_WarningDepth.hide()
            self.checkBox_Legend.hide()
            self.pushButton_SaveData.hide()
            self.pushButton_SaveFigure.hide()
            self.canvas.hide() if self.canvas is not None else None
            return
        # import here to save start up time
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        import matplotlib.pyplot as plt
        from matplotlib import axes as matplotlib_axes
        from numpy import array as np_array
        # get Datastorage of selected scenario
        ds: DataStorage = self.ListDS[self.list_widget_scenario.currentRow()]
        # get bore field of selected scenario
        boreField: Borefield = ds.boreField
        # hide widgets if no results bore field exists and display not calculated text
        if boreField is None:
            self.label_Size.setText(self.translations.NotCalculated)
            self.label_WarningDepth.hide()
            self.checkBox_Legend.hide()
            self.pushButton_SaveData.hide()
            self.pushButton_SaveFigure.hide()
            self.canvas.hide() if self.canvas is not None else None
            return
        # get results of bore field sizing by length and width
        li_size = [str(round(i[3], 2)) for i in boreField.combo]
        li_b = [str(round(i[2], 2)) for i in boreField.combo]
        li_n_1 = [str(round(i[0], 2)) for i in boreField.combo]
        li_n_2 = [str(round(i[1], 2)) for i in boreField.combo]
        # hide widgets if no solution exists and display no solution text
        if (ds.size_bore_field and not li_size) or (ds.determineDepth and boreField.H == boreField.H_max):
            self.label_Size.setText(self.translations.NoSolution)
            self.label_WarningDepth.hide()
            self.checkBox_Legend.hide()
            self.pushButton_SaveData.hide()
            self.pushButton_SaveFigure.hide()
            self.canvas.hide() if self.canvas is not None else None
            return
        # show checkBox for legend and save figure button
        self.checkBox_Legend.show()
        self.pushButton_SaveFigure.show()
        # just show save Data button if not optmize load profile is selected because the output for this is not
        # defined so far
        self.pushButton_SaveData.hide() if ds.optimizeLoadProfile else self.pushButton_SaveData.show()
        # get peak heating and cooling and monthly loads as well as Tb temperature
        results_peak_cooling = boreField.resultsPeakCooling
        results_peak_heating = boreField.resultsPeakHeating
        results_month_cooling = boreField.resultsMonthCooling
        results_month_heating = boreField.resultsMonthHeating
        t_b = boreField.Tb
        # set colors for graph
        grey_color = '#00407a'
        color: str = 'w'
        plt.rcParams['text.color'] = color
        plt.rcParams['axes.labelcolor'] = color
        plt.rcParams['xtick.color'] = color
        plt.rcParams['ytick.color'] = color
        # create figure and axe if not already exists
        self.fig = plt.Figure(facecolor=grey_color) if self.fig is None else self.fig
        canvas = FigureCanvas(self.fig) if self.canvas is None else self.canvas
        ax: matplotlib_axes._subplots.AxesSubplot = canvas.figure.subplots() if self.ax == [] else self.ax[0]
        # clear axces for new plot
        ax.clear()
        # plot remaining peak heating and cooling as well as loads if the profile is optimized instead of temperatures
        if ds.optimizeLoadProfile:
            # create new x-axe
            time_array: list = [i+1 for i in range(12)]
            # create second y-axe if not already exists
            ax2 = ax.twinx() if len(self.ax) < 2 else self.ax[1]
            # clear the axe
            ax2.clear()
            # plot load and peaks
            ax.step(np_array(time_array), np_array(boreField.peakCoolingExternal), where="pre", lw=1.5,
                    label=f'P {self.translations.PeakCooling}', color='#54bceb')
            ax.step(np_array(time_array), np_array(boreField.peakHeatingExternal), where="pre", lw=1.5,
                    label=f'P {self.translations.PeakHeating}', color='#ffc857')
            ax2.step(np_array(time_array), np_array(boreField.monthlyLoadCoolingExternal), color='#54bceb',
                     linestyle="dashed", where="pre", lw=1.5, label=f'Q {self.translations.BaseCooling}')
            ax2.step(np_array(time_array), np_array(boreField.monthlyLoadHeatingExternal), color='#ffc857',
                     linestyle="dashed", where="pre", lw=1.5, label=f'Q {self.translations.BaseHeating}')
            # set x-axe limits
            ax.set_xlim(left=1, right=12)
            ax2.set_xlim(left=1, right=12)
            # create legends
            ax.legend(facecolor=grey_color, loc='upper left')
            ax2.legend(facecolor=grey_color, loc='upper right')
            # set labels of axes
            ax.set_xlabel(self.translations.X_Axis_Load, color='white')
            ax.set_ylabel(self.translations.Y_Axis_Load_P, color='white')
            ax2.set_xlabel(self.translations.X_Axis_Load, color='white')
            ax2.set_ylabel(self.translations.Y_Axis_Load_Q, color='white')
            # set axe colors
            ax.spines['bottom'].set_color('w')
            ax.spines['top'].set_color('w')
            ax.spines['right'].set_color('w')
            ax.spines['left'].set_color('w')
            ax2.spines['bottom'].set_color('w')
            ax2.spines['top'].set_color('w')
            ax2.spines['right'].set_color('w')
            ax2.spines['left'].set_color('w')
            ax.set_facecolor(grey_color)
            ax2.set_facecolor(grey_color)
            # import numpy here to save start up time
            import numpy as np
            # create string for result explanation
            string_size: str = f"{self.translations.label_ResOptimizeLoad1}" \
                               f"{int(max(boreField.hourlyHeatingLoad)) - int(np.max(boreField.peakHeatingExternal))}" \
                               f" / {int(max(boreField.hourlyCoolingLoad)) - int(np.max(boreField.peakCoolingExternal))} kW\n" \
                               f"{self.translations.label_ResOptimizeLoad2}{np.round(np.sum(boreField.baseloadHeating), 2)} / " \
                               f"{np.round(np.sum(boreField.baseloadCooling), 2)}   kWh\n" \
                               f"{self.translations.label_ResOptimizeLoad3}" \
                               f"{np.round(np.sum(boreField.baseloadHeating) / np.sum(boreField.hourlyHeatingLoad) * 100, 2)} / " \
                               f"{np.round(np.sum(boreField.baseloadCooling) / np.sum(boreField.hourlyCoolingLoad) * 100, 2)} " \
                               f"{self.translations.label_ResOptimizeLoad4}\n" \
                               f"{self.translations.label_ResOptimizeLoad5}" \
                               f"{int(np.max(boreField.peakHeatingExternal))} / " \
                               f"{int(np.max(boreField.peakCoolingExternal))} kW\n" \
                               f"{self.translations.label_ResOptimizeLoad6}" \
                               f"{np.round(-np.sum(boreField.baseloadHeating) + np.sum(boreField.hourlyHeatingLoad), 2)} / " \
                               f"{np.round(-np.sum(boreField.baseloadCooling) + np.sum(boreField.hourlyCoolingLoad), 2)} kWh"
        else:
            # remove second axes if exist
            self.ax[1].remove() if len(self.ax) > 1 else None
            # calculation of all the different times at which the g_function should be calculated.
            # this is equal to 'UPM' hours a month * 3600 seconds/hours for the simulationPeriod
            time_for_g_values = [i * boreField.UPM * 3600. for i in range(1, 12 * boreField.simulationPeriod + 1)]
            # make a time array
            time_array = [i / 12 / 730. / 3600. for i in time_for_g_values]
            # plot Temperatures
            ax.step(np_array(time_array), np_array(t_b), 'w-', where="pre", lw=1.5, label="Tb")
            ax.step(np_array(time_array), np_array(results_peak_cooling), where="pre", lw=1.5,
                    label=f'Tf {self.translations.PeakCooling}', color='#54bceb')
            ax.step(np_array(time_array), np_array(results_peak_heating), where="pre", lw=1.5,
                    label=f'Tf {self.translations.PeakHeating}', color='#ffc857')
            # define temperature bounds
            ax.step(np_array(time_array), np_array(results_month_cooling), color='#54bceb', linestyle="dashed",
                    where="pre", lw=1.5, label=f'Tf {self.translations.BaseCooling}')
            ax.step(np_array(time_array), np_array(results_month_heating), color='#ffc857', linestyle="dashed",
                    where="pre", lw=1.5, label=f'Tf {self.translations.BaseHeating}')
            ax.hlines(boreField.Tf_C, 0, ds.simulationPeriod, colors='#ffc857', linestyles='dashed', label='', lw=1)
            ax.hlines(boreField.Tf_H, 0, ds.simulationPeriod, colors='#54bceb', linestyles='dashed', label='', lw=1)
            ax.set_xticks(range(0, ds.simulationPeriod+1, 2))
            # Plot legend
            ax.set_xlim(left=0, right=ds.simulationPeriod)
            # create legend
            ax.legend(facecolor=grey_color, loc='best')
            # set axes names
            ax.set_xlabel(self.translations.X_Axis, color='white')
            ax.set_ylabel(self.translations.Y_Axis, color='white')
            # set colors
            ax.spines['bottom'].set_color('w')
            ax.spines['top'].set_color('w')
            ax.spines['right'].set_color('w')
            ax.spines['left'].set_color('w')
            ax.set_facecolor(grey_color)
            # create result display string
            string_size: str = f'{self.translations.label_Size}{"; ".join(li_size)} m \n'\
                               f'{self.translations.label_Size_B}{"; ".join(li_b)} m \n' \
                               f'{self.translations.label_Size_W}{"; ".join(li_n_1)} \n' \
                               f'{self.translations.label_Size_L}{"; ".join(li_n_2)} \n'\
                if ds.size_bore_field else f'{self.translations.label_Size}{round(boreField.H, 2)} m'
            # not use axe 2
            ax2 = None
        # set string to depth size label
        self.label_Size.setText(string_size)
        # display warning if depth is to small
        self.label_WarningDepth.show() if boreField.H < 50 else self.label_WarningDepth.hide()
        # save variables
        self.ax = [ax] if not ds.optimizeLoadProfile else [ax, ax2]
        self.gridLayout_8.addWidget(canvas, 1, 0) if self.canvas is None else None
        self.canvas.show() if self.canvas is not None else None
        self.canvas = canvas
        # draw new plot
        plt.tight_layout()
        canvas.draw()

    def checkLegend(self) -> None:
        """
        function to check if a legend should be displayed
        :return: None
        """
        # check if the legend should be displayed
        if self.checkBox_Legend.isChecked():
            # set grey color
            grey_color = '#00407a'
            # set legend to graph either two if load is optimized or one otherwise with their locations
            if len(self.ax) > 1:
                self.ax[0].legend(facecolor=grey_color, loc='upper left')
                self.ax[1].legend(facecolor=grey_color, loc='upper right')
            else:
                self.ax[0].legend(facecolor=grey_color, loc='best')
            # redraw graph
            self.canvas.draw()
            return
        # otherwise, remove legend and redraw graph
        for i in self.ax:
            i.get_legend().remove()
        self.canvas.draw()

    def saveFigure(self) -> None:
        """
        save figure to the QFileDialog asked location
        :return: None
        """
        # get filename at storage place
        filename = QtWidgets_QFileDialog.getSaveFileName(caption=self.translations.SaveFigure,
                                                         filter='png (*.png)')
        # display message and return if no file is selected
        if filename == MainWindow.filenameDefault:
            self.status_bar.showMessage(self.translations.NoFileSelected, 5000)
            return
        # save the figure
        self.fig.savefig(filename[0])

    def save_data(self) -> None:
        """
        Save the data in a csv file
        :return: None
        """
        # import csv writer here to save start up time
        from csv import writer as csv_writer
        # get filename at storage place
        filename = QtWidgets_QFileDialog.getSaveFileName(caption=self.translations.SaveData,
                                                         filter='csv (*.csv)')
        # display message and return if no file is selected
        if filename == MainWindow.filenameDefault:
            self.status_bar.showMessage(self.translations.NoFileSelected, 5000)
            return
        # get maximal simulation period
        simulationTime = max([i.simulationPeriod for i in self.ListDS])
        # create first two column entries
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
        month_yrs = [f'{mon}_{int(idx/12)+1}' for idx, mon in enumerate(month*simulationTime)]
        toWrite = toWrite + [[f'Peak heating {mon}', 'kW'] for mon in month]
        toWrite = toWrite + [[f'Peak cooling {mon}', 'kW'] for mon in month]
        toWrite = toWrite + [[f'Load heating {mon}', 'kWh'] for mon in month]
        toWrite = toWrite + [[f'Load cooling {mon}', 'kWh'] for mon in month]
        toWrite = toWrite + [[f'Results peak heating {mon}', 'C'] for mon in month_yrs]
        toWrite = toWrite + [[f'Results peak cooling {mon}', 'C'] for mon in month_yrs]
        toWrite = toWrite + [[f'Results load heating {mon}', 'C'] for mon in month_yrs]
        toWrite = toWrite + [[f'Results load cooling {mon}', 'C'] for mon in month_yrs]
        # define ranges for results
        ran_yr = range(12)
        ran_simu = range(12 * simulationTime)
        # start looping over results in ListDS and append them to toWrite
        for idx, ds in enumerate(self.ListDS):
            ds: DataStorage = ds
            i = 0
            toWrite[i].append(f'{self.list_widget_scenario.item(idx).text()}')
            i += 1
            toWrite[i].append(f'{round(ds.GD.H, 2)}')
            i += 1
            toWrite[i].append(f'{round(ds.GD.B, 2)}')
            i += 1
            toWrite[i].append(f'{round(ds.GD.k_s, 2)}')
            i += 1
            toWrite[i].append(f'{round(ds.GD.Tg, 2)}')
            i += 1
            toWrite[i].append(f'{round(ds.GD.Rb, 4)}')
            i += 1
            toWrite[i].append(f'{round(ds.GD.N_1, 0)}')
            i += 1
            toWrite[i].append(f'{round(ds.GD.N_2, 0)}')
            i += 1
            toWrite[i].append(f'{round(ds.determineDepth, 0)}')
            i += 1
            toWrite[i].append(f'{round(ds.simulationPeriod, 0)}')
            i += 1
            toWrite[i].append(f'{round(ds.T_min, 2)}')
            i += 1
            toWrite[i].append(f'{round(ds.T_max, 2)}')
            for j in ran_yr:
                i += 1
                toWrite[i].append(f'{round(ds.peakHeating[j], 2)}')
            for j in ran_yr:
                i += 1
                toWrite[i].append(f'{round(ds.peakCooling[j], 2)}')
            for j in ran_yr:
                i += 1
                toWrite[i].append(f'{round(ds.monthlyLoadHeating[j], 2)}')
            for j in ran_yr:
                i += 1
                toWrite[i].append(f'{round(ds.monthlyLoadCooling[j], 2)}')
            if ds.boreField is None:
                i += 1
                [toWrite[i+j].append(self.translations.NotCalculated) for j in ran_simu]
                i += len(ran_simu)
                [toWrite[i+j].append(self.translations.NotCalculated) for j in ran_simu]
                i += len(ran_simu)
                [toWrite[i+j].append(self.translations.NotCalculated) for j in ran_simu]
                i += len(ran_simu)
                [toWrite[i+j].append(self.translations.NotCalculated) for j in ran_simu]
                i += len(ran_simu)
                continue
            for j in ran_simu:
                i += 1
                try:
                    toWrite[i].append(f'{round(ds.boreField.resultsPeakHeating[j], 2)}')
                except IndexError:
                    toWrite[i].append(self.translations.NotCalculated)
            for j in ran_simu:
                i += 1
                try:
                    toWrite[i].append(f'{round(ds.boreField.resultsPeakCooling[j], 2)}')
                except IndexError:
                    toWrite[i].append(self.translations.NotCalculated)
            for j in ran_simu:
                i += 1
                try:
                    toWrite[i].append(f'{round(ds.boreField.resultsMonthHeating[j], 2)}')
                except IndexError:
                    toWrite[i].append(self.translations.NotCalculated)
            for j in ran_simu:
                i += 1
                try:
                    toWrite[i].append(f'{round(ds.boreField.resultsMonthCooling[j], 2)}')
                except IndexError:
                    toWrite[i].append(self.translations.NotCalculated)
        # try to write the data else show error message in status bar
        try:
            with open(filename[0], 'w', newline='') as f:
                writer = csv_writer(f, delimiter=';')
                for row in toWrite:
                    writer.writerow(row)
        except FileNotFoundError:
            self.status_bar.showMessage(self.translations.NoFileSelected, 5000)
            return

    def closeEvent(self, event) -> None:
        """
        new close Event to check if the input should be saved
        :param event: closing event
        :return: None
        """
        # close app if nothing has been changed
        if not self.changedFile:
            event.accept()
            return
        # create message box
        msg: QtWidgets_QMessageBox = QtWidgets_QMessageBox(self.Dia)
        # set Icon to question mark icon
        msg.setIcon(QtWidgets_QMessageBox.Question)
        # set label text to cancel text depending on language selected
        msg.setText(self.translations.label_CancelText)
        # set window text to cancel text depending on language selected
        msg.setWindowTitle(self.translations.label_CancelTitle)
        # set standard buttons to save, close and cancel
        msg.setStandardButtons(QtWidgets_QMessageBox.Save | QtWidgets_QMessageBox.Close | QtWidgets_QMessageBox.Cancel)
        # get save, close and cancel button
        buttonS = msg.button(QtWidgets_QMessageBox.Save)
        buttonCl = msg.button(QtWidgets_QMessageBox.Close)
        buttonCa = msg.button(QtWidgets_QMessageBox.Cancel)
        # set save, close and cancel button text depending on language selected
        buttonS.setText(f'{self.translations.label_Save} ')
        buttonCl.setText(f'{self.translations.label_close} ')
        buttonCa.setText(f'{self.translations.label_cancel} ')
        # set  save, close and cancel button icon
        self.setPushButtonIcon(buttonS, 'Save_Inv')
        self.setPushButtonIcon(buttonCl, 'Exit')
        self.setPushButtonIcon(buttonCa, 'Abort')
        # execute message box and save response
        reply = msg.exec_()
        # check if closing should be canceled
        if reply == QtWidgets_QMessageBox.Cancel:
            # cancel closing event
            event.ignore()
            return
        # check if inputs should be saved and if successfully set closing variable to true
        close: bool = self.funSave() if reply == QtWidgets_QMessageBox.Save else True
        # stop all calculation threads
        [i.terminate() for i in self.threads]
        # close window if close variable is true else not
        event.accept() if close else event.ignore()


class CalcProblem(QtCore_QThread):
    """
    class to calculate the problem in an external thread
    """
    any_signal = QtCore_pyqtSignal(DataStorage)

    def __init__(self, ds: DataStorage, idx: int, parent=None) -> None:
        """
        initialize calculation class
        :param ds: datastorage to perform calculation for
        :param idx: index of current thread
        :param parent: parent class
        """
        super(CalcProblem, self).__init__(parent)  # init parent class
        # set datastorage and index
        self.DS = ds
        self.idx = idx

    def run(self) -> None:
        """
        run calculations
        :return: None
        """
        # import bore field class from GHEtool and not in start up to save time
        from GHEtool import Borefield
        # create the bore field object
        boreField = Borefield(simulationPeriod=self.DS.simulationPeriod, peakHeating=self.DS.peakHeating,
                              peakCooling=self.DS.peakCooling, baseloadHeating=self.DS.monthlyLoadHeating,
                              baseloadCooling=self.DS.monthlyLoadCooling, GUI=True)
        # set temperature boundaries
        boreField.setMaxGroundTemperature(self.DS.T_max)  # maximum temperature
        boreField.setMinGroundTemperature(self.DS.T_min)  # minimum temperature
        # set ground data
        boreField.setGroundParameters(self.DS.GD)
        # check bounds of precalculated data
        bopd: BoundsOfPrecalculatedData = BoundsOfPrecalculatedData()
        outside_bounds: bool = bopd.check_if_outside_bounds(self.DS.GD.H, self.DS.GD.B, self.DS.GD.k_s,
                                                            max(self.DS.GD.N_1, self.DS.GD.N_2))
        # set default value for constant Rb calculation
        useConstantRb: bool = True
        # check if Rb is unknown
        if self.DS.R_b_calculation_method > 0:
            # set fluid and pipe data
            boreField.setFluidParameters(self.DS.fluidData)
            boreField.setPipeParameters(self.DS.pipeData)
            # set useConstantRb to False if R_b_calculation_method == 2
            useConstantRb: bool = self.DS.R_b_calculation_method == 1
            # set Rb to the new calculated one if a constant unknown Rb is selected
            boreField.Rb = boreField.calculateRb() if useConstantRb else self.DS.GD.Rb
        # create custom rectangle bore field if no precalculated data is available
        if outside_bounds:
            # import boreholes from pygfuntion here to save start up time
            from pygfunction import boreholes as gt_boreholes
            # get minimum and maximal number of boreholes in one direction
            n_max: int = max(self.DS.GD.N_1, self.DS.GD.N_2)
            n_min: int = max(self.DS.GD.N_1, self.DS.GD.N_2)
            # initialize custom field with variables selected
            custom_field = gt_boreholes.rectangle_field(N_1=n_max, N_2=n_min, B_1=self.DS.GD.B, B_2=self.DS.GD.B,
                                                        H=self.DS.GD.H, D=4, r_b=0.075)
            # create name of custom bore field to save it later
            boreFieldCustom: str = f'customField_{n_max}_{n_min}_{self.DS.GD.B}_{self.DS.GD.k_s}'
            # try if the bore field has already be calculated then open this otherwise calculate it
            try:
                from GHEtool import FOLDER
                pk_load(open(f'{FOLDER}/Data/{boreFieldCustom}.pickle', "rb"))
            except FileNotFoundError:
                boreField.createCustomDataset(custom_field, boreFieldCustom)
            # set new bore field g-function
            boreField.setCustomGfunction(boreFieldCustom)
            # set bore field to custom one
            boreField.setBorefield(custom_field)
        # if load should be optimized do this
        if self.DS.optimizeLoadProfile:
            # get column and decimal seperator
            sep: str = ';' if self.DS.dataSeperator == 0 else ','
            dec: str = '.' if self.DS.dataDecimal == 0 else ','
            # import pandas here to save start up time
            from pandas import read_csv as pd_read_csv
            # load data from csv file
            try:
                data = pd_read_csv(self.DS.dataFile, sep=sep, decimal=dec)
            except FileNotFoundError:
                self.any_signal.emit(self.DS)
                return
            # get data unit factor of energy demand
            unit: float = 0.001 if self.DS.dataUnit == 0 else 1 if self.DS.dataUnit == 1 else 1_000
            # if data is in 2 column create a list of the loaded data else sepperate data by >0 and <0 and then create a
            # list and muliplty in both cases with the unit factor to achive data in kW
            if self.DS.numberColumns == 0:
                boreField.hourlyHeatingLoad = list(data[self.DS.headerHeating] * unit)
                boreField.hourlyCoolingLoad = list(data[self.DS.headerCooling] * unit)
            else:
                boreField.hourlyHeatingLoad = list(data[self.DS.headerHeating].apply(lambda x: x >= 0) * unit)
                boreField.hourlyCoolingLoad = list(data[self.DS.headerHeating].apply(lambda x: x < 0) * unit)
            # optimize load profile without printing the results
            boreField.optimiseLoadProfile(depth=self.DS.GD.H, printResults=False)
            # save bore field in Datastorage
            self.DS.boreField = boreField
            # return Datastorage as signal
            self.any_signal.emit(self.DS)
            return
        # size the borehole depth if wished
        boreField.size(self.DS.GD.H, L2Sizing=self.DS.Depth_Method == 0, useConstantRb=useConstantRb) if \
            self.DS.determineDepth else None
        # size bore field by length and width either fast (Size_Method == 0) or robust (Size_Method == 1)
        if self.DS.Size_Method == 0:
            boreField.size_complete_field_fast(self.DS.H_max, self.DS.W_max, self.DS.L_max, self.DS.B_min,
                                               self.DS.B_max, self.DS.Depth_Method == 0, useConstantRb) if \
                self.DS.size_bore_field else None
        else:
            boreField.size_complete_field_robust(self.DS.H_max, self.DS.W_max, self.DS.L_max, self.DS.B_min,
                                                 self.DS.B_max, self.DS.Depth_Method == 0, useConstantRb) if \
                self.DS.size_bore_field else None
        # try to calculate temperatures
        try:
            boreField.calculateTemperatures(boreField.H)
        except ValueError:
            pass
        # save bore field in Datastorage
        self.DS.boreField = boreField
        # return Datastorage as signal
        self.any_signal.emit(self.DS)
        return


class ImportGHEtool(QtCore_QThread):
    """
    class to import GHEtool in an external thread
    """
    any_signal = QtCore_pyqtSignal(bool)

    def __init__(self, parent=None) -> None:
        """
        initialize importing class
        :param parent: parent class
        """
        super(ImportGHEtool, self).__init__(parent) # init parent class

    def run(self) -> None:
        """
        start import
        :return: None
        """
        import GHEtool  # import GHEtool
        GHEtool.FOLDER = './'
        self.any_signal.emit(True)  # emit true signal


class SetItem(QtCore_QThread):
    """
    class to reset item a bit later
    """
    any_signal: QtCore_pyqtSignal = QtCore_pyqtSignal(QtCore_QThread)

    def __init__(self, widget: QtWidgets_QWidget, item: QtWidgets_QListWidgetItem, parent=None) -> None:
        """
        initialize change scenario / item class
        :param widget: widget to set later item for
        :param item: item to set
        :param parent: parent class
        """
        super(SetItem, self).__init__(parent)
        self.widget = widget
        self.item = item

    def run(self) -> None:
        """
        change item after 0.01 seconds
        :return: None
        """
        sleep(0.01)  # wait for a little time
        self.widget.setCurrentItem(self.item)  # change current item
        self.any_signal.emit(self)  # return itself as signal
        return
