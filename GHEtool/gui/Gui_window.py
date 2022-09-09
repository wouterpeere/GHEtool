from functools import partial as ft_partial
from os.path import dirname, realpath
from os.path import split as os_split
from pickle import HIGHEST_PROTOCOL as pk_HP
from pickle import dump as pk_dump
from pickle import load as pk_load
from sys import path
from time import sleep
from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QEvent as QtCore_QEvent
from PySide6.QtCore import QModelIndex as QtCore_QModelIndex
from PySide6.QtCore import QSize as QtCore_QSize
from PySide6.QtCore import QThread as QtCore_QThread
from PySide6.QtCore import Signal as QtCore_pyqtSignal
from PySide6.QtCore import QSettings as QtCore_QSettings
from PySide6.QtGui import QIcon as QtGui_QIcon
from PySide6.QtGui import QPixmap as QtGui_QPixmap
from PySide6.QtWidgets import QApplication as QtWidgets_QApplication
from PySide6.QtWidgets import QDialog as QtWidgets_QDialog
from PySide6.QtWidgets import QDoubleSpinBox as QtWidgets_QDoubleSpinBox
from PySide6.QtWidgets import QFileDialog as QtWidgets_QFileDialog
from PySide6.QtWidgets import QHBoxLayout as QtWidgets_QHBoxLayout
from PySide6.QtWidgets import QInputDialog as QtWidgets_QInputDialog
from PySide6.QtWidgets import QListWidgetItem as QtWidgets_QListWidgetItem
from PySide6.QtWidgets import QListWidget as QtWidgets_QListWidget
from PySide6.QtWidgets import QMainWindow as QtWidgets_QMainWindow
from PySide6.QtWidgets import QMenu as QtWidgets_QMenu
from PySide6.QtWidgets import QMessageBox as QtWidgets_QMessageBox
from PySide6.QtWidgets import QPushButton as QtWidgets_QPushButton
from PySide6.QtWidgets import QWidget as QtWidgets_QWidget
from PySide6.QtWidgets import QGraphicsView as QtWidgets_QGraphicsView, QSpacerItem, QSizePolicy
from math import pi
from numpy import cos, sin
from PySide6.QtWidgets import QGraphicsScene, QGraphicsEllipseItem
from PySide6.QtGui import QColor, QPen

from GHEtool.gui.data_storage_new import DataStorageNew
from GHEtool.gui.gui_Main_new import Ui_GHEtool
from GHEtool.gui.Translation_class import TrClass
from GHEtool.gui.gui_structure import GuiStructure

from typing import List, Tuple

if TYPE_CHECKING:
    from pandas import DataFrame as pd_DataFrame
    from pandas import ExcelFile as pd_ExcelFile

    from GHEtool import Borefield

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
        # 'E:/Git/GHEtool_test/GHEtool/gui/ui/icons/Options.svg'
        # pyside6-rcc icons.qrc -o icons_rc.py

        self.gui_structure = GuiStructure(self.centralwidget, self.status_bar)
        for page in self.gui_structure.list_of_pages:
            page.create_page(self.centralwidget, self.stackedWidget, self.verticalLayout_menu)

        self.gui_structure.translate(1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout_menu.addItem(self.verticalSpacer)

        #ds = DataStorageNew(self.gui_structure)
        #ds.save()
        # self.add_aims(list_button)
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
        self.threads: List[CalcProblem] = []  # list of calculation threads
        self.list_ds: List[DataStorageNew] = []  # list of data storages
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
        self.gui_structure.option_language.widget.addItems(self.translations.comboBoxLanguageList)
        # hide warning for custom bore field calculation
        self.gui_structure.hint_calc_time.hide()
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
        # set links to check if changes happen
        self.actionInputChanged.triggered.connect(self.change)
        # allow checking of changes
        self.checking: bool = True
        # reset push button size
        self.set_push(False)
        # set start page to general page
        self.gui_structure.page_aim.button.click()

        self.settings: QtCore_QSettings = QtCore_QSettings('GHEtool', 'GHEtoolApp')

        self.update_borehole()

        try:
            self.resize(self.settings.value('window size'))

            self.move(self.settings.value('window position'))
        except TypeError:
            pass

    def eventFilterInstall(self) -> None:
        """
        install event filter for push button sizing
        :return: None
        """
        for page in self.gui_structure.list_of_pages:
            page.button.installEventFilter(self)
            page.label_gap.installEventFilter(self)

    def setLinks(self) -> None:
        """
        set links of buttons and actions to function
        :return: None
        """
        self.gui_structure.option_pipe_number.widget.valueChanged.connect(self.update_borehole)
        self.gui_structure.option_pipe_outer_radius.widget.valueChanged.connect(self.update_borehole)
        self.gui_structure.option_pipe_inner_radius.widget.valueChanged.connect(self.update_borehole)
        self.gui_structure.option_pipe_borehole_radius.widget.valueChanged.connect(self.update_borehole)
        self.gui_structure.option_pipe_distance.widget.valueChanged.connect(self.update_borehole)
        self.gui_structure.option_pipe_number.widget.valueChanged.connect(self.check_distance_between_pipes)
        self.gui_structure.option_pipe_outer_radius.widget.valueChanged.connect(self.check_distance_between_pipes)
        self.gui_structure.option_pipe_inner_radius.widget.valueChanged.connect(self.check_distance_between_pipes)
        self.gui_structure.option_pipe_borehole_radius.widget.valueChanged.connect(self.check_distance_between_pipes)
        self.gui_structure.option_pipe_distance.widget.valueChanged.connect(self.check_distance_between_pipes)
        self.gui_structure.option_pipe_outer_radius.widget.valueChanged.connect(self.gui_structure.option_pipe_inner_radius.widget.setMaximum)
        self.gui_structure.option_pipe_inner_radius.widget.valueChanged.connect(self.gui_structure.option_pipe_outer_radius.widget.setMinimum)
        self.gui_structure.page_result.button.clicked.connect(self.displayResults)
        self.gui_structure.function_save_figure.button.clicked.connect(self.saveFigure)
        self.gui_structure.function_save_results.button.clicked.connect(self.save_data)
        self.gui_structure.filename.widget.textChanged.connect(self.fun_update_combo_box_data_file)
        self.actionAdd_Scenario.triggered.connect(self.addScenario)
        self.actionUpdate_Scenario.triggered.connect(self.saveScenario)
        self.actionDelete_scenario.triggered.connect(self.deleteScenario)
        for button in self.gui_structure.option_show_legend.widget:
            button.clicked.connect(self.checkLegend)
        self.action_start_multiple.triggered.connect(self.startMultipleScenariosCalculation)
        self.action_start_single.triggered.connect(self.startCurrentScenarioCalculation)
        self.actionSave.triggered.connect(self.funSave)
        self.actionSave_As.triggered.connect(self.funSaveAs)
        self.actionOpen.triggered.connect(self.funLoad)
        self.actionNew.triggered.connect(self.funNew)
        self.actionEnglish.triggered.connect(ft_partial(self.gui_structure.option_language.widget.setCurrentIndex, 0))
        self.actionGerman.triggered.connect(ft_partial(self.gui_structure.option_language.widget.setCurrentIndex, 1))
        self.actionDutch.triggered.connect(ft_partial(self.gui_structure.option_language.widget.setCurrentIndex, 2))
        self.actionItalian.triggered.connect(ft_partial(self.gui_structure.option_language.widget.setCurrentIndex, 3))
        self.actionFrench.triggered.connect(ft_partial(self.gui_structure.option_language.widget.setCurrentIndex, 4))
        self.actionSpanish.triggered.connect(ft_partial(self.gui_structure.option_language.widget.setCurrentIndex, 5))
        self.actionGalician.triggered.connect(ft_partial(self.gui_structure.option_language.widget.setCurrentIndex, 6))
        self.gui_structure.option_depth.widget.valueChanged.connect(self.check_bounds)
        self.gui_structure.option_spacing.widget.valueChanged.connect(self.check_bounds)
        self.gui_structure.option_conductivity.widget.valueChanged.connect(self.check_bounds)
        self.gui_structure.option_length.widget.valueChanged.connect(self.check_bounds)
        self.gui_structure.option_width.widget.valueChanged.connect(self.check_bounds)
        self.gui_structure.button_load_csv.button.clicked.connect(self.funDisplayData)
        self.actionRename_scenario.triggered.connect(self.funRenameScenario)
        self.list_widget_scenario.model().rowsMoved.connect(self.funMoveScenario)
        self.list_widget_scenario.currentItemChanged.connect(self.funAutoSaveScenario)
        # self.actionCheckUDistance.triggered.connect(self.check_distance_between_pipes)
        self.gui_structure.option_language.widget.currentIndexChanged.connect(self.changeLanguage)

        self.Dia.closeEvent = self.closeEvent
        self.gui_structure.page_result.button.clicked.connect(self.displayResults)
        #self.update_aim(self.pushButton_temp_profile)
        #self.checkBox_Import.toggle()
        #self.checkBox_Import.toggle()

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
        if self.gui_structure.option_auto_saving.get_value() == 1:
            return
        # if list is empty return
        if not self.list_ds:
            return
        # get text string of current scenario
        text: str = self.list_widget_scenario.currentItem().text()
        # abort if there is no text
        if len(text) < 1:
            return
        # get current index of scenario
        idx: int = self.list_widget_scenario.currentRow()
        # create current data storage
        ds: DataStorageNew = DataStorageNew(self.gui_structure)
        # check if current data storage is equal to the previous one then delete the *
        if self.list_ds:
            if ds == self.list_ds[idx]:
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
        if self.gui_structure.option_auto_saving.get_value() == 1:
            # save old scenario
            self.list_ds[self.list_widget_scenario.row(oldRowItem)] = DataStorageNew(self.gui_structure)
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

    def check_distance_between_pipes(self) -> None:
        """
        calculate and set minimal and maximal distance between U pipes and center
        :return: None
        """
        # import math stuff
        from math import pi, sin, cos, tan
        nU: int = self.gui_structure.option_pipe_number.get_value()  # get number of U pipes
        rBorehole: float = self.gui_structure.option_pipe_borehole_radius.get_value()  # get borehole radius
        rOuterPipe: float = self.gui_structure.option_pipe_outer_radius.get_value()  # get outer pipe radius
        rOuterPipeMax: float = rBorehole/(1+1/sin(pi/(2*nU)))  # calculate maximal outer pipe radius(see Circle packing)
        distanceMax: float = rBorehole - rOuterPipeMax  # calculate maximal distance between pipe and center
        alpha: float = pi/nU  # determine equal angle between pipes
        # determine minimal distance between pipe and center if number of pipes is bigger than one else set to half
        # borehole radius
        distanceMin: float = 2*rOuterPipe*(cos((pi-alpha)/2)+sin((pi-alpha)/2)/tan(alpha)) if nU > 1 else rBorehole/2
        # set minimal and maximal value for pipe distance
        self.gui_structure.option_pipe_distance.widget.setMinimum(distanceMin)
        self.gui_structure.option_pipe_distance.widget.setMaximum(distanceMax)

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
        self.list_ds.insert(targetIndex, self.list_ds.pop(startIndex))
        self.list_ds.insert(targetIndex, self.list_ds.pop(startIndex))

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
        if any([(i.borefield is None) for i in self.list_ds]) or self.list_ds == []:
            self.gui_structure.function_save_results.hide()
            self.gui_structure.page_aim.button.click()
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

    def check_bounds(self) -> None:
        """
        check if precalculated bounds are extended then show warning
        :return: None
        """
        # check if current selection is outside the precalculated data
        outside_bounds: bool = self.BOPD.check_if_outside_bounds(self.gui_structure.option_depth.get_value(),
                                                                 self.gui_structure.option_spacing.get_value(),
                                                                 self.gui_structure.option_conductivity.get_value(),
                                                                 max(self.gui_structure.option_length.get_value(), self.gui_structure.option_width.get_value())
                                                                 )
        # if so show label with warning message
        self.gui_structure.hint_calc_time.show() if outside_bounds else self.gui_structure.hint_calc_time.hide()

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

    def set_push_button_icon_size(self, button: QtWidgets_QPushButton, big: bool = False, name: str = '') -> None:
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

    def set_push(self, mouse_over: bool) -> None:
        """
        function to Set PushButton Text if MouseOver
        :param mouse_over: bool true if Mouse is over PushButton
        :return: None
        """
        # if Mouse is over PushButton change size to big otherwise to small
        if mouse_over:
            for page in self.gui_structure.list_of_pages:
                self.set_push_button_icon_size(page.button, True, page.button_name)
            return
        for page in self.gui_structure.list_of_pages:
            self.set_push_button_icon_size(page.button)

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
        self.translations.changeLanguage(self.gui_structure.option_language.get_value())
        # update all label, pushButtons, action and Menu names
        for i in [j for j in self.translations.__slots__ if hasattr(self, j)]:
            if isinstance(getattr(self, i), QtWidgets_QMenu):
                getattr(self, i).setTitle(getattr(self.translations, i))
                continue
            getattr(self, i).setText(getattr(self.translations, i))
        # set translation of toolbox items
        self.gui_structure.translate(self.gui_structure.option_language.get_value())
        # set small PushButtons
        self.set_push(False)
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
            self.list_ds, li = li[0], li[1]  # unpack tuple to get list of data-storages and scenario names
            self.gui_structure.option_language.set_value(settings[0])  # set last time selected language
            self.gui_structure.option_auto_saving.set_value(settings[1])  # set last time selected automatic saving scenario option
            # replace uer window id
            for DS in self.list_ds:
                DS.ui = id(self)
            # clear list widget and add new items and select the first one
            self.list_widget_scenario.clear()
            self.list_widget_scenario.addItems(li)
            self.list_widget_scenario.setCurrentRow(0)
            # check if results exits and then display them
            self.checkResults()
        except FileNotFoundError:
            # hide custom bore field warning
            self.gui_structure.hint_calc_time.hide()
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
        if len(self.list_ds) < 1:
            self.list_ds.append(DataStorageNew(self.gui_structure))
        # create list of scenario names
        li: list = [self.list_widget_scenario.item(idx).text() for idx in range(self.list_widget_scenario.count())]
        # create list of settings with language and autosave option
        settings: list = [self.gui_structure.option_language.get_value(), self.gui_structure.option_auto_saving.get_value()]
        # try to write data to back up file
        try:
            # write data to back up file
            with open("backup.pkl", "wb") as f:
                saving = self.filename, [self.list_ds, li], settings
                pk_dump(saving, f, pk_HP)
        except FileNotFoundError:
            self.status_bar.showMessage(self.translations.NoFileSelected, 5000)

    def fun_update_combo_box_data_file(self, filename: str) -> None:
        """
        update comboBox if new data file is selected
        :param filename: filename of data file
        :return: None
        """
        # import pandas here to save start up time
        from pandas import read_csv as pd_read_csv
        # get decimal and column seperator
        sep: str = ';' if self.gui_structure.option_seperator_csv.get_value() == 0 else ','
        dec: str = '.' if self.gui_structure.option_decimal_csv.get_value() == 0 else ','
        # try to read CSV-File
        try:
            data: pd_DataFrame = pd_read_csv(filename, sep=sep, decimal=dec)
        except FileNotFoundError:
            self.status_bar.showMessage(self.translations.NoFileSelected, 5000)
            return
        except PermissionError:
            self.status_bar.showMessage(self.translations.NoFileSelected, 5000)
            return
        # get data column names to set them to comboBoxes
        columns = data.columns
        # clear comboBoxes and add column names
        self.gui_structure.option_heating_column.widget.clear()
        self.gui_structure.option_cooling_column.widget.clear()
        self.gui_structure.option_single_column.widget.clear()
        self.gui_structure.option_heating_column.widget.addItems(columns)
        self.gui_structure.option_cooling_column.widget.addItems(columns)
        self.gui_structure.option_single_column.widget.addItems(columns)
        # set column selection mode to 2 columns if more than one line exists
        self.gui_structure.option_column.set_value(0 if len(columns) > 0 else 1)

    def update_borehole(self) -> None:
        """
        plots the position of the pipes in the borehole
        :return: None
        """
        if isinstance(self.gui_structure.category_pipe_data.graphic_left, QtWidgets_QGraphicsView):
            # import all that is needed
            # get variables from gui
            numberOfPipes = self.gui_structure.option_pipe_number.get_value()
            rOut = self.gui_structure.option_pipe_outer_radius.get_value() * 10
            rIn = self.gui_structure.option_pipe_inner_radius.get_value() * 10
            rBore = self.gui_structure.option_pipe_borehole_radius.get_value() * 10
            dis = self.gui_structure.option_pipe_distance.get_value() * 10
            # calculate scale from graphic view size
            max_l = min(self.gui_structure.category_pipe_data.graphic_left.width(), self.gui_structure.category_pipe_data.graphic_left.height())
            scale = max_l/rBore/1.25  # leave 25 % space
            # set colors
            blue_color = QColor(0, 64, 122)
            blue_light = QColor(84, 188, 235)
            white_color = QColor(255, 255, 255)
            grey = QColor(100, 100, 100)
            brown = QColor(145, 124, 111)
            # create graphic scene if not exits otherwise get scene and delete items
            if self.gui_structure.category_pipe_data.graphic_left.scene() is None:
                scene = QGraphicsScene()#parent=self.centralwidget)
                self.gui_structure.category_pipe_data.graphic_left.setScene(scene)
                self.gui_structure.category_pipe_data.graphic_left.setBackgroundBrush(brown)
            else:
                scene = self.gui_structure.category_pipe_data.graphic_left.scene()
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
            filename: str = self.gui_structure.filename.get_value()
            # raise error if no filename exists
            if filename == '':
                raise FileNotFoundError
            # get thermal demands index (1 = 2 columns, 2 = 1 column)
            thermalDemand: int = self.gui_structure.option_column.get_value()
            # Generate list of columns that have to be imported
            cols: list = []
            heatingLoad: str = self.gui_structure.option_heating_column.widget.currentText()
            if len(heatingLoad) >= 1:
                cols.append(heatingLoad)
            coolingLoad: str = self.gui_structure.option_cooling_column.widget.currentText()
            if len(coolingLoad) >= 1:
                cols.append(coolingLoad)
            combined: str = self.gui_structure.option_single_column.widget.currentText()
            if len(combined) >= 1:
                cols.append(combined)
            date: str = 'Date'
            # import pandas here to save start up time
            from pandas import read_csv as pd_read_csv
            sep: str = ';' if self.gui_structure.option_seperator_csv.get_value() == 0 else ','
            dec: str = '.' if self.gui_structure.option_decimal_csv.get_value() == 0 else ','
            df2: pd_DataFrame = pd_read_csv(filename, usecols=cols, sep=sep, decimal=dec)
            # ---------------------- Time Step Section  ----------------------
            # import pandas here to save start up time
            from pandas import to_datetime as pd_to_datetime, date_range as pd_date_range, Series as pd_Series
            # Define start and end date
            start = pd_to_datetime("2019-01-01 00:00:00")
            end = pd_to_datetime("2019-12-31 23:59:00")
            # add date column
            df2[date] = pd_Series(pd_date_range(start, end, freq="1H"))
            # Create no dict to create mean values for
            dictAgg: Optional[None, dict] = None

            # set date to index
            df2.set_index(date, inplace=True)
            # resample data to hourly resolution if necessary
            df2 = df2 if dictAgg is None else df2.resample("H").agg(dictAgg)
            # ------------------- Calculate Section --------------------
            # Choose path between Single or Combined Column and create new columns
            if thermalDemand == 1:
                # Resample the Data for peakHeating and peakCooling
                df2.rename(columns={heatingLoad: "Heating Load", coolingLoad: "Cooling Load"}, inplace=True)
                df2["peak Heating"] = df2["Heating Load"]
                df2["peak Cooling"] = df2["Cooling Load"]
            # by single column split by 0 to heating (>0) and cooling (<0)
            elif thermalDemand == 0:
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
            data_unit = self.gui_structure.option_unit_data.get_value()
            # define unit factors
            fac = 0.001 if data_unit == 0 else 1 if data_unit == 1 else 1000
            # multiply dataframe with unit factor and collect data
            df3 = df3 * fac
            peak_heating = df3["peak Heating"]
            peak_cooling = df3["peak Cooling"]
            heatingLoad = df3["Heating Load"]
            coolingLoad = df3["Cooling Load"]
            # set heating loads to double spinBoxes
            self.gui_structure.option_hl_jan.set_value(heatingLoad[0])
            self.gui_structure.option_hl_feb.set_value(heatingLoad[1])
            self.gui_structure.option_hl_mar.set_value(heatingLoad[2])
            self.gui_structure.option_hl_apr.set_value(heatingLoad[3])
            self.gui_structure.option_hl_may.set_value(heatingLoad[4])
            self.gui_structure.option_hl_jun.set_value(heatingLoad[5])
            self.gui_structure.option_hl_jul.set_value(heatingLoad[6])
            self.gui_structure.option_hl_aug.set_value(heatingLoad[7])
            self.gui_structure.option_hl_sep.set_value(heatingLoad[8])
            self.gui_structure.option_hl_oct.set_value(heatingLoad[9])
            self.gui_structure.option_hl_nov.set_value(heatingLoad[10])
            self.gui_structure.option_hl_dec.set_value(heatingLoad[11])
            # set cooling loads to double spinBoxes
            self.gui_structure.option_cl_jan.set_value(coolingLoad[0])
            self.gui_structure.option_cl_feb.set_value(coolingLoad[1])
            self.gui_structure.option_cl_mar.set_value(coolingLoad[2])
            self.gui_structure.option_cl_apr.set_value(coolingLoad[3])
            self.gui_structure.option_cl_may.set_value(coolingLoad[4])
            self.gui_structure.option_cl_jun.set_value(coolingLoad[5])
            self.gui_structure.option_cl_jul.set_value(coolingLoad[6])
            self.gui_structure.option_cl_aug.set_value(coolingLoad[7])
            self.gui_structure.option_cl_sep.set_value(coolingLoad[8])
            self.gui_structure.option_cl_oct.set_value(coolingLoad[9])
            self.gui_structure.option_cl_nov.set_value(coolingLoad[10])
            self.gui_structure.option_cl_dec.set_value(coolingLoad[11])
            # set peak heating load to double spinBoxes
            self.gui_structure.option_hp_jan.set_value(peak_heating[0])
            self.gui_structure.option_hp_feb.set_value(peak_heating[1])
            self.gui_structure.option_hp_mar.set_value(peak_heating[2])
            self.gui_structure.option_hp_apr.set_value(peak_heating[3])
            self.gui_structure.option_hp_may.set_value(peak_heating[4])
            self.gui_structure.option_hp_jun.set_value(peak_heating[5])
            self.gui_structure.option_hp_jul.set_value(peak_heating[6])
            self.gui_structure.option_hp_aug.set_value(peak_heating[7])
            self.gui_structure.option_hp_sep.set_value(peak_heating[8])
            self.gui_structure.option_hp_oct.set_value(peak_heating[9])
            self.gui_structure.option_hp_nov.set_value(peak_heating[10])
            self.gui_structure.option_hp_dec.set_value(peak_heating[11])
            # set peak cooling load to double spinBoxes
            self.gui_structure.option_cp_jan.set_value(peak_cooling[0])
            self.gui_structure.option_cp_feb.set_value(peak_cooling[1])
            self.gui_structure.option_cp_mar.set_value(peak_cooling[2])
            self.gui_structure.option_cp_apr.set_value(peak_cooling[3])
            self.gui_structure.option_cp_may.set_value(peak_cooling[4])
            self.gui_structure.option_cp_jun.set_value(peak_cooling[5])
            self.gui_structure.option_cp_jul.set_value(peak_cooling[6])
            self.gui_structure.option_cp_aug.set_value(peak_cooling[7])
            self.gui_structure.option_cp_sep.set_value(peak_cooling[8])
            self.gui_structure.option_cp_oct.set_value(peak_cooling[9])
            self.gui_structure.option_cp_nov.set_value(peak_cooling[10])
            self.gui_structure.option_cp_dec.set_value(peak_cooling[11])
        # raise error and display error massage in status bar
        except FileNotFoundError:
            self.status_bar.showMessage(self.translations.NoFileSelected, 5000)
        except IndexError:
            self.status_bar.showMessage(self.translations.ValueError, 5000)
        except KeyError:
            self.status_bar.showMessage(self.translations.ColumnError, 5000)



    def funLoad(self) -> None:
        """
        function to load externally stored scenario
        :return: None
        """
        # open interface and get file name
        self.filename = QtWidgets_QFileDialog.getOpenFileName(self.centralwidget, caption=self.translations.ChoosePKL, filter='Pickle (*.pkl)')
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
            self.list_ds, li = li[0], li[1]
            # change window title to new loaded filename
            self.changeWindowTitle()
            # replace user window id
            for DS in self.list_ds:
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
            self.filename: tuple = QtWidgets_QFileDialog.getSaveFileName(self.centralwidget, caption=self.translations.SavePKL, filter='Pickle (*.pkl)')
            # break function if no file is selected
            if self.filename == MainWindow.filenameDefault:
                return False
        # save scenarios
        self.saveScenario()
        # update backup file
        self.funSaveAuto()
        # Create list if no scenario is stored
        self.list_ds.append(DataStorageNew(self.gui_structure)) if len(self.list_ds) < 1 else None
        # try to store the data in the pickle file
        try:
            # create list of all scenario names
            li = [self.list_widget_scenario.item(idx).text() for idx in range(self.list_widget_scenario.count())]
            # store data
            with open(self.filename[0], "wb") as f:
                pk_dump([self.list_ds, li], f, pk_HP)
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
        self.list_ds: list = []  # reset list of data storages
        self.list_ds = []
        self.list_widget_scenario.clear()  # clear list widget with scenario list

    def changeScenario(self, idx: int) -> None:
        """
        update GUI if a new scenario at the comboBox is selected
        :param idx: index of selected scenario
        :return: None
        """
        # if i no scenario is selected (idx < 0) or no scenario exists break function
        if idx < 0 or idx >= len(self.list_ds):
            return
        # deactivate checking for changes
        self.checking: bool = False
        # get selected Datastorage from list
        ds: DataStorageNew = self.list_ds[idx]
        # set values of selected Datastorage
        ds.set_values(self.gui_structure)
        # activate checking for changed
        self.checking: bool = True
        # refresh results if results page is selected
        self.gui_structure.page_result.button.click() if self.stackedWidget.currentWidget() == self.gui_structure.page_result else None

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
        if len(self.list_ds) == idx:
            self.addScenario()
        else:
            self.list_ds[idx] = DataStorageNew(self.gui_structure)
        # create auto backup
        self.funSaveAuto()
        # remove * from scenario if not Auto save is checked and if the last char is a *
        if not self.gui_structure.option_auto_saving.get_value() == 1:
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
        if idx > 0 or (len(self.list_ds) > 1 and idx == 0):
            # delete scenario from list
            del self.list_ds[idx]
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
        number: int = max(len(self.list_ds), 0)
        # append new scenario to List of DataStorages
        self.list_ds.append(DataStorageNew(self.gui_structure))
        # add new scenario name and item to list widget
        self.list_widget_scenario.addItem(f'{self.translations.scenarioString}: {number + 1}')
        # select new list item
        self.list_widget_scenario.setCurrentRow(number)
        # run change function to mark unsaved inputs
        self.change()

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

    def threadFunction(self, ds: DataStorageNew) -> None:
        """
        turn on and off the old and new threads for the calculation
        :param ds: DataStorage of current thread
        :return: None
        """
        # stop finished thread
        self.threads[self.finished].terminate()

        self.list_ds[self.finished] = ds
        print(self.list_ds[self.finished].borefield)
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
            self.gui_structure.page_result.button.click()
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
        self.addScenario() if not self.list_ds else self.saveScenario()
        # return to thermal demands page if no file is selected
        if any([i.fileSelected for i in self.list_ds]):
            self.gui_structure.page_thermal.button.click()
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
        self.threads = [CalcProblem(DS, idx) for idx, DS in enumerate(self.list_ds) if DS.borefield is None]
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
        self.addScenario() if not self.list_ds else self.saveScenario()
        # return to thermal demands page if no file is selected
        if self.list_ds[self.list_widget_scenario.currentRow()].fileSelected:
            self.gui_structure.page_thermal.button.click()
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
        ds: DataStorageNew = self.list_ds[idx]
        # if calculation is already done just show results
        if ds.borefield is not None:
            self.gui_structure.page_result.button.click()
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
        if not self.list_ds:
            self.gui_structure.hint_depth.label.setText(self.translations.NotCalculated)
            # self.label_WarningDepth.hide()
            self.gui_structure.option_show_legend.hide()
            self.gui_structure.function_save_results.hide()
            self.gui_structure.function_save_figure.hide()
            self.canvas.hide() if self.canvas is not None else None
            return
        # import here to save start up time
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        import matplotlib.pyplot as plt
        from matplotlib import axes as matplotlib_axes
        from numpy import array as np_array
        # get Datastorage of selected scenario
        ds: DataStorageNew = self.list_ds[self.list_widget_scenario.currentRow()]
        # get bore field of selected scenario
        boreField: Borefield = ds.borefield
        # hide widgets if no results bore field exists and display not calculated text
        if boreField is None:
            self.gui_structure.hint_depth.label.setText(self.translations.NotCalculated)
            # self.label_WarningDepth.hide()
            self.gui_structure.option_show_legend.hide()
            self.gui_structure.function_save_results.hide()
            self.gui_structure.function_save_figure.hide()
            self.canvas.hide() if self.canvas is not None else None
            return
        # get results of bore field sizing by length and width
        li_size = [str(round(i[3], 2)) for i in boreField.combo]
        li_b = [str(round(i[2], 2)) for i in boreField.combo]
        li_n_1 = [str(round(i[0], 2)) for i in boreField.combo]
        li_n_2 = [str(round(i[1], 2)) for i in boreField.combo]
        # hide widgets if no solution exists and display no solution text
        if (ds.aim_size_length and not li_size) or (ds.aim_req_depth and boreField.H == boreField.H_max):
            self.gui_structure.hint_depth.label.setText(self.translations.NotCalculated)
            # self.label_WarningDepth.hide()
            self.gui_structure.option_show_legend.hide()
            self.gui_structure.function_save_results.hide()
            self.gui_structure.function_save_figure.hide()
            self.canvas.hide() if self.canvas is not None else None
            return
        # show checkBox for legend and save figure button
        self.gui_structure.option_show_legend.show()
        self.gui_structure.function_save_figure.show()
        # just show save Data button if not optmize load profile is selected because the output for this is not
        # defined so far
        self.gui_structure.function_save_results.hide() if self.gui_structure.aim_optimize.widget.isChecked() else \
            self.gui_structure.function_save_results.show()
        # get peak heating and cooling and monthly loads as well as Tb temperature
        results_peak_cooling = boreField.results_peak_cooling
        results_peak_heating = boreField.results_peak_heating
        results_month_cooling = boreField.results_month_cooling
        results_month_heating = boreField.results_month_heating
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
        if ds.aim_optimize:
            # create new x-axe
            time_array: list = [i+1 for i in range(12)]
            # create second y-axe if not already exists
            ax2 = ax.twinx() if len(self.ax) < 2 else self.ax[1]
            # clear the axe
            ax2.clear()
            # plot load and peaks
            ax.step(np_array(time_array), np_array(boreField.peak_cooling_external), where="pre", lw=1.5,
                    label=f'P {self.translations.PeakCooling}', color='#54bceb')
            ax.step(np_array(time_array), np_array(boreField.peak_heating_external), where="pre", lw=1.5,
                    label=f'P {self.translations.PeakHeating}', color='#ffc857')
            ax2.step(np_array(time_array), np_array(boreField.monthly_load_cooling_external), color='#54bceb',
                     linestyle="dashed", where="pre", lw=1.5, label=f'Q {self.translations.BaseCooling}')
            ax2.step(np_array(time_array), np_array(boreField.monthly_load_heating_external), color='#ffc857',
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
                               f"{int(max(boreField.hourly_heating_load)) - int(np.max(boreField.peak_heating_external))}" \
                               f" / {int(max(boreField.hourly_cooling_load)) - int(np.max(boreField.peak_cooling_external))} kW\n" \
                               f"{self.translations.label_ResOptimizeLoad2}{np.round(np.sum(boreField.baseload_heating), 2)} / " \
                               f"{np.round(np.sum(boreField.baseload_cooling), 2)}   kWh\n" \
                               f"{self.translations.label_ResOptimizeLoad3}" \
                               f"{np.round(np.sum(boreField.baseload_heating) / np.sum(boreField.hourly_heating_load) * 100, 2)} / " \
                               f"{np.round(np.sum(boreField.baseload_cooling) / np.sum(boreField.hourly_cooling_load) * 100, 2)} " \
                               f"{self.translations.label_ResOptimizeLoad4}\n" \
                               f"{self.translations.label_ResOptimizeLoad5}" \
                               f"{int(np.max(boreField.peak_heating_external))} / " \
                               f"{int(np.max(boreField.peak_cooling_external))} kW\n" \
                               f"{self.translations.label_ResOptimizeLoad6}" \
                               f"{np.round(-np.sum(boreField.baseload_heating) + np.sum(boreField.hourly_heating_load), 2)} / " \
                               f"{np.round(-np.sum(boreField.baseload_cooling) + np.sum(boreField.hourly_cooling_load), 2)} kWh"
        else:
            # remove second axes if exist
            self.ax[1].remove() if len(self.ax) > 1 else None
            # calculation of all the different times at which the g_function should be calculated.
            # this is equal to 'UPM' hours a month * 3600 seconds/hours for the simulationPeriod
            time_for_g_values = [i * boreField.UPM * 3600. for i in range(1, 12 * boreField.simulation_period + 1)]
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
            ax.hlines(boreField.Tf_C, 0, ds.option_simu_period, colors='#ffc857', linestyles='dashed', label='', lw=1)
            ax.hlines(boreField.Tf_H, 0, ds.option_simu_period, colors='#54bceb', linestyles='dashed', label='', lw=1)
            ax.set_xticks(range(0, ds.option_simu_period+1, 2))
            # Plot legend
            ax.set_xlim(left=0, right=ds.option_simu_period)
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
                if ds.aim_size_length else f'{self.translations.label_Size}{round(boreField.H, 2)} m'
            # not use axe 2
            ax2 = None
        # set string to depth size label
        self.gui_structure.hint_depth.label.setText(string_size)
        # display warning if depth is to small
        # self.label_WarningDepth.show() if boreField.H < 50 else self.label_WarningDepth.hide()
        # save variables
        self.ax = [ax] if not ds.aim_optimize else [ax, ax2]
        self.gui_structure.category_result_figure.frame.layout().addWidget(canvas) if self.canvas is None else None
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
        if self.canvas is None:
            return
        # check if the legend should be displayed
        if self.gui_structure.option_show_legend.get_value() == 0:
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
        filename = QtWidgets_QFileDialog.getSaveFileName(self.centralwidget, caption=self.translations.SaveFigure, filter='png (*.png)')
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
        filename = QtWidgets_QFileDialog.getSaveFileName(self.centralwidget, caption=self.translations.SaveData, filter='csv (*.csv)')
        # display message and return if no file is selected
        if filename == MainWindow.filenameDefault:
            self.status_bar.showMessage(self.translations.NoFileSelected, 5000)
            return
        # get maximal simulation period
        simulationTime = max([i.option_simu_period for i in self.list_ds])
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
        # start looping over results in list_ds and append them to toWrite
        for idx, ds in enumerate(self.list_ds):
            ds: DataStorageNew = ds
            i = 0
            toWrite[i].append(f'{self.list_widget_scenario.item(idx).text()}')
            i += 1
            toWrite[i].append(f'{round(ds.ground_data.H, 2)}')
            i += 1
            toWrite[i].append(f'{round(ds.ground_data.B, 2)}')
            i += 1
            toWrite[i].append(f'{round(ds.ground_data.k_s, 2)}')
            i += 1
            toWrite[i].append(f'{round(ds.ground_data.Tg, 2)}')
            i += 1
            toWrite[i].append(f'{round(ds.ground_data.Rb, 4)}')
            i += 1
            toWrite[i].append(f'{round(ds.ground_data.N_1, 0)}')
            i += 1
            toWrite[i].append(f'{round(ds.ground_data.N_2, 0)}')
            i += 1
            toWrite[i].append(f'{round(ds.aim_req_depth, 0)}')
            i += 1
            toWrite[i].append(f'{round(ds.option_simu_period, 0)}')
            i += 1
            toWrite[i].append(f'{round(ds.option_min_temp, 2)}')
            i += 1
            toWrite[i].append(f'{round(ds.option_max_temp, 2)}')
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
            if ds.borefield is None:
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
                    toWrite[i].append(f'{round(ds.borefield.results_peak_heating[j], 2)}')
                except IndexError:
                    toWrite[i].append(self.translations.NotCalculated)
            for j in ran_simu:
                i += 1
                try:
                    toWrite[i].append(f'{round(ds.borefield.results_peak_cooling[j], 2)}')
                except IndexError:
                    toWrite[i].append(self.translations.NotCalculated)
            for j in ran_simu:
                i += 1
                try:
                    toWrite[i].append(f'{round(ds.borefield.results_month_heating[j], 2)}')
                except IndexError:
                    toWrite[i].append(self.translations.NotCalculated)
            for j in ran_simu:
                i += 1
                try:
                    toWrite[i].append(f'{round(ds.borefield.results_month_cooling[j], 2)}')
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
        self.settings.setValue('window size', self.size())
        self.settings.setValue('window position', self.pos())
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
    any_signal = QtCore_pyqtSignal(DataStorageNew)

    def __init__(self, ds: DataStorageNew, idx: int, parent=None) -> None:
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
        boreField = Borefield(simulation_period=self.DS.option_simu_period, peak_heating=self.DS.peakHeating,
                              peak_cooling=self.DS.peakCooling, baseload_heating=self.DS.monthlyLoadHeating,
                              baseload_cooling=self.DS.monthlyLoadCooling, gui=True)
        # set temperature boundaries
        boreField.set_max_ground_temperature(self.DS.option_max_temp)  # maximum temperature
        boreField.set_min_ground_temperature(self.DS.option_min_temp)  # minimum temperature
        # set ground data
        boreField.set_ground_parameters(self.DS.ground_data)
        # check bounds of precalculated data
        bopd: BoundsOfPrecalculatedData = BoundsOfPrecalculatedData()
        outside_bounds: bool = bopd.check_if_outside_bounds(self.DS.ground_data.H, self.DS.ground_data.B, self.DS.ground_data.k_s,
                                                            max(self.DS.ground_data.N_1, self.DS.ground_data.N_2))
        # set default value for constant Rb calculation
        useConstantRb: bool = True
        # check if Rb is unknown
        if self.DS.option_method_rb_calc > 0:
            # set fluid and pipe data
            boreField.set_fluid_parameters(self.DS.fluid_data)
            boreField.set_pipe_parameters(self.DS.pipe_data)
            # set useConstantRb to False if R_b_calculation_method == 2
            useConstantRb: bool = self.DS.option_method_rb_calc == 1
            # set Rb to the new calculated one if a constant unknown Rb is selected
            boreField.Rb = boreField.calculate_Rb() if useConstantRb else self.DS.ground_data.Rb
        # create custom rectangle bore field if no precalculated data is available
        if outside_bounds:
            # import boreholes from pygfuntion here to save start up time
            from pygfunction import boreholes as gt_boreholes
            # get minimum and maximal number of boreholes in one direction
            n_max: int = max(self.DS.ground_data.N_1, self.DS.ground_data.N_2)
            n_min: int = max(self.DS.ground_data.N_1, self.DS.ground_data.N_2)
            # initialize custom field with variables selected
            custom_field = gt_boreholes.rectangle_field(N_1=n_max, N_2=n_min, B_1=self.DS.ground_data.B, B_2=self.DS.ground_data.B,
                                                        H=self.DS.ground_data.H, D=4, r_b=0.075)
            # create name of custom bore field to save it later
            boreFieldCustom: str = f'customField_{n_max}_{n_min}_{self.DS.ground_data.B}_{self.DS.ground_data.k_s}'
            # try if the bore field has already be calculated then open this otherwise calculate it
            try:
                from GHEtool import FOLDER
                pk_load(open(f'{FOLDER}/Data/{boreFieldCustom}.pickle', "rb"))
            except FileNotFoundError:
                boreField.create_custom_dataset(custom_field, boreFieldCustom)
            # set new bore field g-function
            boreField.set_custom_gfunction(boreFieldCustom)
            # set bore field to custom one
            boreField.set_borefield(custom_field)
        # if load should be optimized do this
        if self.DS.aim_optimize:
            # get column and decimal seperator
            sep: str = ';' if self.DS.option_seperator_csv == 0 else ','
            dec: str = '.' if self.DS.option_decimal_csv == 0 else ','
            # import pandas here to save start up time
            from pandas import read_csv as pd_read_csv
            # load data from csv file
            try:
                data = pd_read_csv(self.DS.filename, sep=sep, decimal=dec)
            except FileNotFoundError:
                self.any_signal.emit(self.DS)
                return
            # get data unit factor of energy demand
            unit: float = 0.001 if self.DS.option_unit_data == 0 else 1 if self.DS.option_unit_data == 1 else 1_000
            # if data is in 2 column create a list of the loaded data else sepperate data by >0 and <0 and then create a
            # list and muliplty in both cases with the unit factor to achive data in kW
            if self.DS.option_column == 1:
                print(data.columns[self.DS.option_heating_column])
                boreField.hourly_heating_load = data[data.columns[self.DS.option_heating_column]] * unit
                boreField.hourly_cooling_load = data[data.columns[self.DS.option_cooling_column]] * unit
            else:
                boreField.hourly_heating_load = data[data.columns[self.DS.option_single_column]].apply(lambda x: x >= 0) * unit
                boreField.hourly_cooling_load = data[data.columns[self.DS.option_single_column]].apply(lambda x: x < 0) * unit
            # optimize load profile without printing the results
            boreField.optimise_load_profile(depth=self.DS.ground_data.H, print_results=False)
            # save bore field in Datastorage
            self.DS.borefield = boreField
            # return Datastorage as signal
            self.any_signal.emit(self.DS)
            return
        if self.DS.aim_req_depth:
            # size the borehole depth if wished
            boreField.size(self.DS.ground_data.H, L2_sizing=self.DS.option_method_size_depth == 0, L3_sizing=self.DS.option_method_size_depth == 1,
                           L4_sizing=self.DS.option_method_size_depth == 2, use_constant_Rb=useConstantRb)

        if self.DS.aim_size_length:
            # size bore field by length and width either fast (Size_Method == 0) or robust (Size_Method == 1)
            if self.DS.option_method_size_length == 0:
                boreField.size_complete_field_fast(self.DS.option_max_depth, self.DS.option_max_width, self.DS.option_max_length, self.DS.option_min_spacing,
                                                   self.DS.option_max_spacing, self.DS.option_method_size_depth == 0, useConstantRb)
            else:
                boreField.size_complete_field_robust(self.DS.option_max_depth, self.DS.option_max_width, self.DS.option_max_length, self.DS.option_min_spacing,
                                                     self.DS.option_max_spacing, self.DS.option_method_size_depth == 0, useConstantRb)
        # try to calculate temperatures
        try:
            boreField.calculate_temperatures(boreField.H)
        except ValueError:
            pass
        # save bore field in Datastorage
        self.DS.borefield = boreField
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

    def __init__(self, widget: QtWidgets_QListWidget, item: QtWidgets_QListWidgetItem, parent=None) -> None:
        """
        initialize change scenario / item class
        :param widget: widget to set later item for
        :param item: item to set
        :param parent: parent class
        """
        super(SetItem, self).__init__(parent)
        self.widget: QtWidgets_QListWidget = widget
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
