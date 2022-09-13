from functools import partial as ft_partial
from math import pi
from os.path import dirname, realpath
from os.path import split as os_split
from os import makedirs
from pathlib import Path, PurePath
from pickle import HIGHEST_PROTOCOL as pk_HP
from pickle import dump as pk_dump
from pickle import load as pk_load
from sys import path
from time import sleep
from typing import TYPE_CHECKING, List, Optional, Tuple

from numpy import cos, sin, array, float64, int64
from PySide6.QtCore import QEvent as QtCore_QEvent
from PySide6.QtCore import QModelIndex as QtCore_QModelIndex
from PySide6.QtCore import QSize as QtCore_QSize
from PySide6.QtCore import QThread as QtCore_QThread
from PySide6.QtCore import Signal as QtCore_pyqtSignal
from PySide6.QtGui import QAction as QtGui_QAction
from PySide6.QtGui import QColor
from PySide6.QtGui import QIcon as QtGui_QIcon
from PySide6.QtGui import QPen
from PySide6.QtGui import QPixmap as QtGui_QPixmap
from PySide6.QtWidgets import QApplication as QtWidgets_QApplication
from PySide6.QtWidgets import QDialog as QtWidgets_QDialog
from PySide6.QtWidgets import QDoubleSpinBox as QtWidgets_QDoubleSpinBox
from PySide6.QtWidgets import QFileDialog as QtWidgets_QFileDialog
from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsScene
from PySide6.QtWidgets import QGraphicsView as QtWidgets_QGraphicsView
from PySide6.QtWidgets import QInputDialog as QtWidgets_QInputDialog
from PySide6.QtWidgets import QListWidget as QtWidgets_QListWidget
from PySide6.QtWidgets import QListWidgetItem as QtWidgets_QListWidgetItem
from PySide6.QtWidgets import QMainWindow as QtWidgets_QMainWindow
from PySide6.QtWidgets import QMenu as QtWidgets_QMenu
from PySide6.QtWidgets import QMessageBox as QtWidgets_QMessageBox
from PySide6.QtWidgets import QPushButton as QtWidgets_QPushButton
from PySide6.QtWidgets import QSizePolicy, QSpacerItem
from PySide6.QtWidgets import QWidget as QtWidgets_QWidget

from GHEtool.gui.gui_calculation_thread import (BoundsOfPrecalculatedData,
                                                CalcProblem)
from GHEtool.gui.gui_data_storage import DataStorage
from GHEtool.gui.gui_main_new import UiGhetool, GREY, WHITE, DARK, LIGHT, WARNING
from GHEtool.gui.gui_structure import GuiStructure
from GHEtool.gui.translation_class import Translations

if TYPE_CHECKING:
    from pandas import DataFrame as pd_DataFrame
    from pandas import ExcelFile as pd_ExcelFile

    from GHEtool import Borefield

currentdir = dirname(realpath(__file__))
parentdir = dirname(currentdir)
path.append(parentdir)


# main GUI class
class MainWindow(QtWidgets_QMainWindow, UiGhetool):
    filenameDefault: tuple = ("", "")

    def __init__(self, dialog: QtWidgets_QWidget, app: QtWidgets_QApplication) -> None:
        """
        initialize window
        :param dialog: Q widget as main window
        :param app: application widget
        """
        # init windows of parent class
        super(MainWindow, self).__init__()
        super().setup_ui(dialog)
        # pyside6-rcc icons.qrc -o icons_rc.py

        self.gui_structure = GuiStructure(self.central_widget, self.status_bar)
        for page in self.gui_structure.list_of_pages:
            page.create_page(self.central_widget, self.stackedWidget, self.verticalLayout_menu)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout_menu.addItem(self.verticalSpacer)

        # self.add_aims(list_button)
        # set app and dialog
        self.app: QtWidgets_QApplication = app
        self.Dia = dialog
        # init variables of class
        # allow checking of changes
        self.checking: bool = False
        # create backup path in home documents directory
        self.backup_path: str = str(PurePath(Path.home(), 'Documents/GHEtool', 'backup.pkl'))
        # check if backup folder exits and otherwise create it
        makedirs(dirname(self.backup_path), exist_ok=True)
        self.translations: Translations = Translations()  # init translation class
        for idx, (name, icon, short_cut) in enumerate(zip(self.translations.option_language, self.translations.icon, self.translations.short_cut)):
            self.create_action_language(idx, name, icon, short_cut)
        # add languages to combo box
        self.gui_structure.option_language.widget.addItems(self.translations.option_language)
        self.gui_structure.translate(1, self.translations)
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
        self.list_ds: List[DataStorage] = []  # list of data storages
        self.sizeB = QtCore_QSize(48, 48)  # size of big logo on push button
        self.sizeS = QtCore_QSize(24, 24)  # size of small logo on push button
        self.sizePushB = QtCore_QSize(150, 75)  # size of big push button
        self.sizePushS = QtCore_QSize(75, 75)  # size of small push button
        self.BOPD: BoundsOfPrecalculatedData = BoundsOfPrecalculatedData()  # init bounds of precalculated data class
        # init links from buttons to functions
        self.set_links()
        # reset progress bar
        self.update_bar(0, False)
        # set event filter for push button sizing
        self.event_filter_install()
        # start importing GHEtool by a thread to save start up time
        self.IG: ImportGHEtool = ImportGHEtool()
        self.IG.start()
        self.IG.any_signal.connect(self.check_ghe_tool)
        # show loading GHEtool message in statusbar
        self.status_bar.showMessage(self.translations.GHE_tool_imported_start[self.gui_structure.option_language.get_value()], 5000)
        # enable push button because GHEtool ist not imported
        self.pushButton_start_multiple.setEnabled(False)
        self.pushButton_start_single.setEnabled(False)
        self.action_start_multiple.setEnabled(False)
        self.action_start_single.setEnabled(False)
        # hide warning for custom bore field calculation
        self.gui_structure.hint_calc_time.hide()
        # load backup data
        self.load_list()
        # add progress bar and label to statusbar
        self.status_bar.addPermanentWidget(self.label_Status, 0)
        self.status_bar.addPermanentWidget(self.progressBar, 1)
        self.status_bar.messageChanged.connect(self.status_hide)
        # change window title to saved filename
        self.change_window_title()
        # reset push button size
        self.set_push(False)
        # set start page to general page
        self.gui_structure.page_aim.button.click()

        self.update_borehole()

        current_aim = [aim for aim, _ in self.gui_structure.list_of_aims if aim.widget.isChecked()]
        for aim, _ in self.gui_structure.list_of_aims:
            if aim not in current_aim:
                aim.widget.click()

        current_aim[0].widget.click()

        [option.init_links() for option, _ in self.gui_structure.list_of_options]

        # allow checking of changes
        self.checking: bool = True

    def create_action_language(self, idx: int, name: str, icon_name: str, short_cut: str):
        action = QtGui_QAction(self.central_widget)
        icon = QtGui_QIcon()
        icon.addFile(icon_name, QtCore_QSize(), QtGui_QIcon.Normal, QtGui_QIcon.Off)
        action.setIcon(icon)
        self.menuLanguage.addAction(action)
        action.setText(name)
        action.setShortcut(short_cut)
        action.triggered.connect(ft_partial(self.gui_structure.option_language.widget.setCurrentIndex, idx))

    def event_filter_install(self) -> None:
        """
        install event filter for push button sizing
        :return: None
        """
        for page in self.gui_structure.list_of_pages:
            page.button.installEventFilter(self)
            page.label_gap.installEventFilter(self)

    def set_links(self) -> None:
        """
        set links of buttons and actions to function
        :return: None
        """
        for option, name in self.gui_structure.list_of_options:
            option.change_event(self.change)
        for option, name in self.gui_structure.list_of_aims:
            option.change_event(self.change)
        self.gui_structure.option_pipe_number.change_event(self.update_borehole)
        self.gui_structure.option_pipe_outer_radius.change_event(self.update_borehole)
        self.gui_structure.option_pipe_inner_radius.change_event(self.update_borehole)
        self.gui_structure.option_pipe_borehole_radius.change_event(self.update_borehole)
        self.gui_structure.option_pipe_distance.change_event(self.update_borehole)
        self.gui_structure.option_pipe_number.change_event(self.check_distance_between_pipes)
        self.gui_structure.option_pipe_outer_radius.change_event(self.check_distance_between_pipes)
        self.gui_structure.option_pipe_inner_radius.change_event(self.check_distance_between_pipes)
        self.gui_structure.option_pipe_borehole_radius.change_event(self.check_distance_between_pipes)
        self.gui_structure.option_pipe_distance.change_event(self.check_distance_between_pipes)
        self.gui_structure.option_pipe_outer_radius.change_event(self.gui_structure.option_pipe_inner_radius.widget.setMaximum)
        self.gui_structure.option_pipe_inner_radius.change_event(self.gui_structure.option_pipe_outer_radius.widget.setMinimum)
        self.gui_structure.page_result.button.clicked.connect(self.display_results)
        self.gui_structure.function_save_figure.button.clicked.connect(self.save_figure)
        self.gui_structure.function_save_results.button.clicked.connect(self.save_data)
        self.gui_structure.option_seperator_csv.change_event(self.fun_update_combo_box_data_file)
        self.gui_structure.option_decimal_csv.change_event(self.fun_update_combo_box_data_file)
        self.gui_structure.option_filename.change_event(self.fun_update_combo_box_data_file)
        self.gui_structure.option_auto_saving.change_event(self.change_auto_save)
        self.gui_structure.option_show_legend.change_event(self.check_legend)
        self.gui_structure.option_depth.change_event(self.check_bounds)
        self.gui_structure.option_spacing.change_event(self.check_bounds)
        self.gui_structure.option_conductivity.change_event(self.check_bounds)
        self.gui_structure.option_length.change_event(self.check_bounds)
        self.gui_structure.option_width.change_event(self.check_bounds)
        self.gui_structure.button_load_csv.button.clicked.connect(self.fun_display_data)
        self.gui_structure.option_language.change_event(self.changeLanguage)
        self.gui_structure.page_result.button.clicked.connect(self.display_results)
        self.actionAdd_Scenario.triggered.connect(self.add_scenario)
        self.actionUpdate_Scenario.triggered.connect(self.save_scenario)
        self.actionDelete_scenario.triggered.connect(self.delete_scenario)
        self.action_start_multiple.triggered.connect(self.start_multiple_scenarios_calculation)
        self.action_start_single.triggered.connect(self.start_current_scenario_calculation)
        self.actionSave.triggered.connect(self.fun_save)
        self.actionSave_As.triggered.connect(self.fun_save_as)
        self.actionOpen.triggered.connect(self.fun_load)
        self.actionNew.triggered.connect(self.fun_new)
        self.actionRename_scenario.triggered.connect(self.fun_rename_scenario)
        self.list_widget_scenario.model().rowsMoved.connect(self.fun_move_scenario)
        self.list_widget_scenario.currentItemChanged.connect(self.fun_auto_save_scenario)
        self.Dia.closeEvent = self.closeEvent

    def event_filter(self, obj: QtWidgets_QPushButton, event) -> bool:
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

    def set_push_button_icon_size(self, button: QtWidgets_QPushButton, big: bool = False, name: str = "") -> None:
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
            self.change_window_title()
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
        ds: DataStorage = DataStorage(self.gui_structure)
        # check if current data storage is equal to the previous one then delete the *
        if self.list_ds:
            if ds == self.list_ds[idx]:
                if text[-1] != "*":
                    return
                self.list_widget_scenario.item(idx).setText(text[:-1])
                return
        # if scenario is already marked as changed return
        if text[-1] == "*":
            return
        # else add * to current item string
        self.list_widget_scenario.item(idx).setText(f"{text}*")

    def fun_auto_save_scenario(self, new_row_item: QtWidgets_QListWidgetItem, old_row_item: QtWidgets_QListWidgetItem) -> None:
        """
        function to save a scenario when the item in the list Widget is changed and the checkBox to save automatic is
        checked or ask to save unsaved scenario changes
        :param new_row_item: new selected scenario item (not used)
        :param old_row_item: old scenario item
        :return: None
        """
        # if no old item is selected do nothing and return
        if old_row_item is None:
            # change entries to new scenario values
            self.change_scenario(self.list_widget_scenario.row(new_row_item))
            return
        # check if the auto saving should be performed and then save the last selected scenario
        if self.gui_structure.option_auto_saving.get_value() == 1:
            # save old scenario
            if DataStorage(self.gui_structure) != self.list_ds[self.list_widget_scenario.row(old_row_item)]:
                self.list_ds[self.list_widget_scenario.row(old_row_item)] = DataStorage(self.gui_structure)
            # update backup fileImport
            self.fun_save_auto()
            # change values to new scenario values
            self.change_scenario(self.list_widget_scenario.row(new_row_item))
            # abort function
            return
        # get test of old scenario (item)
        text = old_row_item.text()
        # check if the old scenario is unsaved then create message box
        if text[-1] == "*":
            # create message box
            msg: QtWidgets_QMessageBox = QtWidgets_QMessageBox(self.Dia)
            # set Icon to question mark icon
            msg.setIcon(QtWidgets_QMessageBox.Question)
            # set label text to leave scenario text depending on language selected
            msg.setText(self.translations.label_LeaveScenarioText[self.gui_structure.option_language.get_value()])
            # set window text to  leave scenario text depending on language selected
            msg.setWindowTitle(self.translations.label_CancelTitle[self.gui_structure.option_language.get_value()])
            # set standard buttons to save, close and cancel
            msg.setStandardButtons(QtWidgets_QMessageBox.Save | QtWidgets_QMessageBox.Close | QtWidgets_QMessageBox.Cancel)
            # get save, close and cancel button
            button_s = msg.button(QtWidgets_QMessageBox.Save)
            button_cl = msg.button(QtWidgets_QMessageBox.Close)
            button_ca = msg.button(QtWidgets_QMessageBox.Cancel)
            # set save, close and cancel button text depending on language selected
            button_s.setText(f"{self.translations.pushButton_SaveScenario[self.gui_structure.option_language.get_value()]} ")
            button_cl.setText(f"{self.translations.label_LeaveScenario[self.gui_structure.option_language.get_value()]} ")
            button_ca.setText(f"{self.translations.label_StayScenario[self.gui_structure.option_language.get_value()]} ")
            # set  save, close and cancel button icon
            self.set_push_button_icon(button_s, "Save_Inv")
            self.set_push_button_icon(button_cl, "Exit")
            self.set_push_button_icon(button_ca, "Abort")
            # execute message box and save response
            reply = msg.exec_()
            # check if closing should be canceled
            if reply == QtWidgets_QMessageBox.Cancel:
                # change item to old item by thread, because I have not found a direct way which is not lost after
                # return
                si = SetItem(self.list_widget_scenario, old_row_item)  # create class
                si.start()  # start thread
                si.any_signal.connect(si.terminate)  # stop thread if finished
                # abort the rest
                return
            # save scenario if wanted
            self.save_scenario(self.list_widget_scenario.row(old_row_item)) if reply == QtWidgets_QMessageBox.Save else None
            # remove * symbol
            old_row_item.setText(text[:-1])
        # change entries to new scenario values
        self.change_scenario(self.list_widget_scenario.row(new_row_item))
        return

    def check_distance_between_pipes(self) -> None:
        """
        calculate and set minimal and maximal distance between U pipes and center
        :return: None
        """
        # import math stuff
        from math import cos, pi, sin, tan

        n_u: int = self.gui_structure.option_pipe_number.get_value()  # get number of U pipes
        r_borehole: float = self.gui_structure.option_pipe_borehole_radius.get_value()  # get borehole radius
        r_outer_pipe: float = self.gui_structure.option_pipe_outer_radius.get_value()  # get outer pipe radius
        r_outer_pipe_max: float = r_borehole / (1 + 1 / sin(pi / (2 * n_u)))  # calculate maximal outer pipe radius(see Circle packing)
        distance_max: float = r_borehole - r_outer_pipe_max  # calculate maximal distance between pipe and center
        alpha: float = pi / n_u  # determine equal angle between pipes
        # determine minimal distance between pipe and center if number of pipes is bigger than one else set to half
        # borehole radius
        distance_min: float = 2 * r_outer_pipe * (cos((pi - alpha) / 2) + sin((pi - alpha) / 2) / tan(alpha)) if n_u > 1 else r_borehole / 2
        # set minimal and maximal value for pipe distance
        self.gui_structure.option_pipe_distance.widget.setMinimum(distance_min)
        self.gui_structure.option_pipe_distance.widget.setMaximum(distance_max)

    def fun_move_scenario(self, start_item: QtCore_QModelIndex, start_index: int, start_index2: int, end_item: QtCore_QModelIndex, target_index: int) -> None:
        """
        change list of ds entry if scenario is moved (more inputs than needed, because the list widget returns that much
        :param start_item: start item of moving
        :param start_index: start index of moving
        :param start_index2: start index of moving
        :param end_item: start end of moving
        :param target_index: target index of moving
        :return: None
        """
        self.list_ds.insert(target_index, self.list_ds.pop(start_index))
        self.list_ds.insert(target_index, self.list_ds.pop(start_index))

    @staticmethod
    def set_push_button_icon(button: QtWidgets_QPushButton, icon_name: str) -> None:
        """
        set QPushButton icon
        :param button: QPushButton to change to icon for
        :param icon_name: icon name as string
        :return: None
        """
        icon = QtGui_QIcon()  # create icon class
        # add pixmap to icon
        icon.addPixmap(QtGui_QPixmap(f":/icons/icons/{icon_name}.svg"), QtGui_QIcon.Normal, QtGui_QIcon.Off)
        button.setIcon(icon)  # set icon to button

    def fun_rename_scenario(self) -> None:
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
        dialog.setWindowTitle(self.translations.label_new_scenario[self.gui_structure.option_language.get_value()])
        dialog.setLabelText(f"{self.translations.new_name[self.gui_structure.option_language.get_value()]}{item.text()}:")
        dialog.setOkButtonText(self.translations.label_okay[self.gui_structure.option_language.get_value()])  # +++
        dialog.setCancelButtonText(self.translations.label_abort[self.gui_structure.option_language.get_value()])  # +++
        li = dialog.findChildren(QtWidgets_QPushButton)
        self.set_push_button_icon(li[0], "Okay")
        self.set_push_button_icon(li[1], "Abort")
        # set new name if the dialog is not canceled and the text is not None
        if dialog.exec_() == QtWidgets_QDialog.Accepted:
            text = dialog.textValue()
            item.setText(text) if text != "" else None

    def check_results(self) -> None:
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
        self.display_results()

    def change_window_title(self) -> None:
        """
        change window title to filename and mark with * if unsaved changes exists
        :return: None
        """
        # get filename separated from path
        _, filename = MainWindow.filenameDefault if self.filename == MainWindow.filenameDefault else os_split(self.filename[0])
        # title determine new title if a filename is not empty
        title: str = "" if filename == "" else f' - {filename.replace(".pkl", "")}'
        # create new title name
        name: str = f"GHEtool {title}*" if self.changedFile else f"GHEtool {title}"
        # set new title name
        self.Dia.setWindowTitle(name)

    def status_hide(self, text) -> None:
        """
        show or hide statusbar if no text exists
        :param text: text in status bar
        :return: None
        """
        if text == "":
            self.status_bar.hide()
            return
        self.status_bar.show()

    def check_bounds(self) -> None:
        """
        check if precalculated bounds are extended then show warning
        :return: None
        """
        # check if current selection is outside the precalculated data
        outside_bounds: bool = self.BOPD.check_if_outside_bounds(
            self.gui_structure.option_depth.get_value(),
            self.gui_structure.option_spacing.get_value(),
            self.gui_structure.option_conductivity.get_value(),
            max(self.gui_structure.option_length.get_value(), self.gui_structure.option_width.get_value()),
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

    @staticmethod
    def display_values_with_floating_decimal(spinbox: QtWidgets_QDoubleSpinBox, factor: float) -> None:
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
        spinbox.setMaximum(max(value * 10, 1_000_000))  # set maximal value to maximal value * 10 or 1_000_000
        spinbox.setValue(value)  # set new value

    def change_auto_save(self):
        for ds in self.list_ds:
            ds.option_auto_saving = self.gui_structure.option_auto_saving.get_value()

    def changeLanguage(self) -> None:
        """
        function to change language on labels and push buttons
        :return: None
        """
        scenario_index: int = self.list_widget_scenario.currentRow()  # get current selected scenario
        amount: int = self.list_widget_scenario.count()  # number of scenario elements

        for ds in self.list_ds:
            ds.option_language = self.gui_structure.option_language.get_value()
        # check if list scenario names are not unique
        li_str_match: List[bool] = [
            self.list_widget_scenario.item(idx).text() == f"{self.translations.scenarioString[self.gui_structure.option_language.get_value()]}: {idx + 1}"
            for idx in range(amount)
        ]
        # update all label, pushButtons, action and Menu names
        for i in [j for j in self.translations.__slots__ if hasattr(self, j)]:
            if isinstance(getattr(self, i), QtWidgets_QMenu):
                getattr(self, i).setTitle(getattr(self.translations, i)[self.gui_structure.option_language.get_value()])
                continue
            getattr(self, i).setText(getattr(self.translations, i)[self.gui_structure.option_language.get_value()])
        # set translation of toolbox items
        self.gui_structure.translate(self.gui_structure.option_language.get_value(), self.translations)
        # set small PushButtons
        self.set_push(False)
        # replace scenario names if they are not unique
        scenarios: list = [
            f"{self.translations.scenarioString[self.gui_structure.option_language.get_value()]}: {i}"
            if li_str_match[i - 1]
            else self.list_widget_scenario.item(i - 1).text()
            for i in range(1, amount + 1)
        ]
        # clear list widget with scenario and write new ones
        self.list_widget_scenario.clear()
        if amount > 0:
            self.list_widget_scenario.addItems(scenarios)
        # select current scenario
        self.list_widget_scenario.setCurrentRow(scenario_index) if scenario_index >= 0 else None

    def load_list(self) -> None:
        """
        try to open the backup file and set the old values
        :return: None
        """
        # try to open backup file if it exits
        try:
            # open backup file
            with open(self.backup_path, "rb") as f:
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
            self.check_results()
        except FileNotFoundError:
            # hide custom bore field warning
            self.gui_structure.hint_calc_time.hide()
            # change language to english
            self.changeLanguage()
            # show message that no backup file is found
            self.status_bar.showMessage(self.translations.NoBackupFile[self.gui_structure.option_language.get_value()])

    def fun_save_auto(self) -> None:
        """
        function to automatically save data in backup file
        :return: None
        """
        # append scenario if no scenario is in list
        if len(self.list_ds) < 1:
            self.list_ds.append(DataStorage(self.gui_structure))
        # create list of scenario names
        li: list = [self.list_widget_scenario.item(idx).text() for idx in range(self.list_widget_scenario.count())]
        # create list of settings with language and autosave option
        settings: list = [self.gui_structure.option_language.get_value(), self.gui_structure.option_auto_saving.get_value()]
        # try to write data to back up file
        try:
            # write data to back up file
            with open(self.backup_path, "wb") as f:
                saving = self.filename, [self.list_ds, li], settings
                pk_dump(saving, f, pk_HP)
        except FileNotFoundError:
            self.status_bar.showMessage(self.translations.NoFileSelected[self.gui_structure.option_language.get_value()], 5000)

    def fun_update_combo_box_data_file(self, filename: str) -> None:
        """
        update comboBox if new data file is selected
        :param filename: filename of data file
        :return: None
        """
        # import pandas here to save start up time
        from pandas import read_csv as pd_read_csv

        # get decimal and column seperator
        sep: str = ";" if self.gui_structure.option_seperator_csv.get_value() == 0 else ","
        dec: str = "." if self.gui_structure.option_decimal_csv.get_value() == 0 else ","
        # try to read CSV-File
        try:
            data: pd_DataFrame = pd_read_csv(filename, sep=sep, decimal=dec)
        except FileNotFoundError:
            self.status_bar.showMessage(self.translations.NoFileSelected[self.gui_structure.option_language.get_value()], 5000)
            return
        except PermissionError:
            self.status_bar.showMessage(self.translations.NoFileSelected[self.gui_structure.option_language.get_value()], 5000)
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
            number_of_pipes = self.gui_structure.option_pipe_number.get_value()
            r_out = self.gui_structure.option_pipe_outer_radius.get_value() * 10
            r_in = self.gui_structure.option_pipe_inner_radius.get_value() * 10
            r_bore = self.gui_structure.option_pipe_borehole_radius.get_value() * 10
            dis = self.gui_structure.option_pipe_distance.get_value() * 10
            # calculate scale from graphic view size
            max_l = min(self.gui_structure.category_pipe_data.graphic_left.width(), self.gui_structure.category_pipe_data.graphic_left.height())
            scale = max_l / r_bore / 1.25  # leave 25 % space
            # set colors
            dark_color = array(DARK.replace('rgb(', '').replace(')', '').split(','), dtype=int64)
            white_color = array(WHITE.replace('rgb(', '').replace(')', '').split(','), dtype=int64)
            light_color = array(LIGHT.replace('rgb(', '').replace(')', '').split(','), dtype=int64)
            grey_color = array(GREY.replace('rgb(', '').replace(')', '').split(','), dtype=int64)
            blue_color = QColor(dark_color[0], dark_color[1], dark_color[2])
            blue_light = QColor(light_color[0], light_color[1], light_color[2])
            white_color = QColor(white_color[0], white_color[1], white_color[2])
            grey = QColor(grey_color[0], grey_color[1], grey_color[2])
            brown = QColor(145, 124, 111)
            # create graphic scene if not exits otherwise get scene and delete items
            if self.gui_structure.category_pipe_data.graphic_left.scene() is None:
                scene = QGraphicsScene()  # parent=self.central_widget)
                self.gui_structure.category_pipe_data.graphic_left.setScene(scene)
                self.gui_structure.category_pipe_data.graphic_left.setBackgroundBrush(brown)
            else:
                scene = self.gui_structure.category_pipe_data.graphic_left.scene()
                scene.clear()
            # create borehole circle in grey wih no border
            circle = QGraphicsEllipseItem(-r_bore * scale / 2, -r_bore * scale / 2, r_bore * scale, r_bore * scale)
            circle.setPen(QPen(grey, 0))
            circle.setBrush(grey)
            scene.addItem(circle)
            # calculate pipe position and draw circle (white for outer pipe and blue for inner pipe)
            dt: float = pi / float(number_of_pipes)
            for i in range(number_of_pipes):
                pos_1 = dis * cos(2.0 * i * dt + pi) / 2
                pos_2 = dis * sin(2.0 * i * dt + pi) / 2
                circle = QGraphicsEllipseItem((pos_1 - r_out / 2) * scale, (pos_2 - r_out / 2) * scale, r_out * scale, r_out * scale)
                circle.setPen(white_color)
                circle.setBrush(white_color)
                scene.addItem(circle)
                circle = QGraphicsEllipseItem((pos_1 - r_in / 2) * scale, (pos_2 - r_in / 2) * scale, r_in * scale, r_in * scale)
                circle.setPen(blue_color)
                circle.setBrush(blue_color)
                scene.addItem(circle)
                pos_1 = dis * cos(2.0 * i * dt + pi + dt) / 2
                pos_2 = dis * sin(2.0 * i * dt + pi + dt) / 2
                circle = QGraphicsEllipseItem((pos_1 - r_out / 2) * scale, (pos_2 - r_out / 2) * scale, r_out * scale, r_out * scale)
                circle.setPen(white_color)
                circle.setBrush(white_color)
                scene.addItem(circle)
                circle = QGraphicsEllipseItem((pos_1 - r_in / 2) * scale, (pos_2 - r_in / 2) * scale, r_in * scale, r_in * scale)
                circle.setPen(blue_light)
                circle.setBrush(blue_light)
                scene.addItem(circle)

    def fun_display_data(self) -> None:
        """
        Load the Data to Display in the GUI
        :return: None
        """
        try:
            # get filename from line edit
            filename: str = self.gui_structure.option_filename.get_value()
            # raise error if no filename exists
            if filename == "":
                raise FileNotFoundError
            # get thermal demands index (1 = 2 columns, 2 = 1 column)
            thermal_demand: int = self.gui_structure.option_column.get_value()
            # Generate list of columns that have to be imported
            cols: list = []
            heating_load: str = self.gui_structure.option_heating_column.widget.currentText()
            if len(heating_load) >= 1:
                cols.append(heating_load)
            cooling_load: str = self.gui_structure.option_cooling_column.widget.currentText()
            if len(cooling_load) >= 1:
                cols.append(cooling_load)
            combined: str = self.gui_structure.option_single_column.widget.currentText()
            if len(combined) >= 1:
                cols.append(combined)
            date: str = "Date"
            # import pandas here to save start up time
            from pandas import read_csv as pd_read_csv

            sep: str = ";" if self.gui_structure.option_seperator_csv.get_value() == 0 else ","
            dec: str = "." if self.gui_structure.option_decimal_csv.get_value() == 0 else ","
            df2: pd_DataFrame = pd_read_csv(filename, usecols=cols, sep=sep, decimal=dec)
            # ---------------------- Time Step Section  ----------------------
            # import pandas here to save start up time
            from pandas import Series as pd_Series
            from pandas import date_range as pd_date_range
            from pandas import to_datetime as pd_to_datetime

            # Define start and end date
            start = pd_to_datetime("2019-01-01 00:00:00")
            end = pd_to_datetime("2019-12-31 23:59:00")
            # add date column
            df2[date] = pd_Series(pd_date_range(start, end, freq="1H"))
            # Create no dict to create mean values for
            dict_agg: Optional[None, dict] = None

            # set date to index
            df2.set_index(date, inplace=True)
            # resample data to hourly resolution if necessary
            df2 = df2 if dict_agg is None else df2.resample("H").agg(dict_agg)
            # ------------------- Calculate Section --------------------
            # Choose path between Single or Combined Column and create new columns
            if thermal_demand == 1:
                # Resample the Data for peakHeating and peakCooling
                df2.rename(columns={heating_load: "Heating Load", cooling_load: "Cooling Load"}, inplace=True)
                df2["peak Heating"] = df2["Heating Load"]
                df2["peak Cooling"] = df2["Cooling Load"]
            # by single column split by 0 to heating (>0) and cooling (<0)
            elif thermal_demand == 0:
                # Create Filter for heating and cooling load ( Heating Load +, Cooling Load -)
                heating_load = df2[combined].apply(lambda x: x >= 0)
                cooling_load = df2[combined].apply(lambda x: x < 0)
                df2["Heating Load"] = df2.loc[heating_load, combined]
                df2["Cooling Load"] = df2.loc[cooling_load, combined] * -1
                df2["peak Heating"] = df2["Heating Load"]
                df2["peak Cooling"] = df2["Cooling Load"]
            # resample to a monthly resolution as sum and maximal load
            df3 = df2.resample("M").agg({"Heating Load": "sum", "Cooling Load": "sum", "peak Heating": "max", "peak Cooling": "max"})
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
            heating_load = df3["Heating Load"]
            cooling_load = df3["Cooling Load"]
            # set heating loads to double spinBoxes
            self.gui_structure.option_hl_jan.set_value(heating_load[0])
            self.gui_structure.option_hl_feb.set_value(heating_load[1])
            self.gui_structure.option_hl_mar.set_value(heating_load[2])
            self.gui_structure.option_hl_apr.set_value(heating_load[3])
            self.gui_structure.option_hl_may.set_value(heating_load[4])
            self.gui_structure.option_hl_jun.set_value(heating_load[5])
            self.gui_structure.option_hl_jul.set_value(heating_load[6])
            self.gui_structure.option_hl_aug.set_value(heating_load[7])
            self.gui_structure.option_hl_sep.set_value(heating_load[8])
            self.gui_structure.option_hl_oct.set_value(heating_load[9])
            self.gui_structure.option_hl_nov.set_value(heating_load[10])
            self.gui_structure.option_hl_dec.set_value(heating_load[11])
            # set cooling loads to double spinBoxes
            self.gui_structure.option_cl_jan.set_value(cooling_load[0])
            self.gui_structure.option_cl_feb.set_value(cooling_load[1])
            self.gui_structure.option_cl_mar.set_value(cooling_load[2])
            self.gui_structure.option_cl_apr.set_value(cooling_load[3])
            self.gui_structure.option_cl_may.set_value(cooling_load[4])
            self.gui_structure.option_cl_jun.set_value(cooling_load[5])
            self.gui_structure.option_cl_jul.set_value(cooling_load[6])
            self.gui_structure.option_cl_aug.set_value(cooling_load[7])
            self.gui_structure.option_cl_sep.set_value(cooling_load[8])
            self.gui_structure.option_cl_oct.set_value(cooling_load[9])
            self.gui_structure.option_cl_nov.set_value(cooling_load[10])
            self.gui_structure.option_cl_dec.set_value(cooling_load[11])
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
            self.status_bar.showMessage(self.translations.NoFileSelected[self.gui_structure.option_language.get_value()], 5000)
        except IndexError:
            self.status_bar.showMessage(self.translations.ValueError[self.gui_structure.option_language.get_value()], 5000)
        except KeyError:
            self.status_bar.showMessage(self.translations.ColumnError[self.gui_structure.option_language.get_value()], 5000)

    def fun_load(self) -> None:
        """
        function to load externally stored scenario
        :return: None
        """
        # open interface and get file name
        self.filename = QtWidgets_QFileDialog.getOpenFileName(
            self.central_widget, caption=self.translations.ChoosePKL[self.gui_structure.option_language.get_value()], filter="Pickle (*.pkl)"
        )
        # load selected data
        self.fun_load_known_filename()

    def fun_load_known_filename(self) -> None:
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
            self.change_window_title()
            # replace user window id
            for DS in self.list_ds:
                DS.ui = id(self)
            # init user window by reset scenario list widget and check for results
            self.list_widget_scenario.clear()
            self.list_widget_scenario.addItems(li)
            self.list_widget_scenario.setCurrentRow(0)
            self.check_results()
            # activate checking
            self.checking: bool = True
        # if no file is found display error message is status bar
        except FileNotFoundError:
            self.status_bar.showMessage(self.translations.NoFileSelected[self.gui_structure.option_language.get_value()], 5000)

    def fun_save_as(self) -> None:
        """
        function to save under new filename
        :return: None
        """
        # reset filename because then the funSave function ask for a new filename
        self.filename = MainWindow.filenameDefault
        self.fun_save()  # save data under a new filename

    def fun_save(self) -> bool:
        """
        save all scenarios externally in a pickle file
        :return: boolean which is true if saving was successful
        """
        # ask for pickle file if the filename is still the default
        if self.filename == MainWindow.filenameDefault:
            self.filename: tuple = QtWidgets_QFileDialog.getSaveFileName(
                self.central_widget, caption=self.translations.SavePKL[self.gui_structure.option_language.get_value()], filter="Pickle (*.pkl)"
            )
            # break function if no file is selected
            if self.filename == MainWindow.filenameDefault:
                return False
        # save scenarios
        self.save_scenario()
        # update backup file
        self.fun_save_auto()
        # Create list if no scenario is stored
        self.list_ds.append(DataStorage(self.gui_structure)) if len(self.list_ds) < 1 else None
        # try to store the data in the pickle file
        try:
            # create list of all scenario names
            li = [self.list_widget_scenario.item(idx).text() for idx in range(self.list_widget_scenario.count())]
            # store data
            with open(self.filename[0], "wb") as f:
                pk_dump([self.list_ds, li], f, pk_HP)
            # deactivate changed file * from window title
            self.changedFile: bool = False
            self.change_window_title()
            # return true because everything was successful
            return True
        # show file not found message in status bar if an error appears
        except FileNotFoundError:
            self.status_bar.showMessage(self.translations.NoFileSelected[self.gui_structure.option_language.get_value()], 5000)
            return False

    def fun_new(self) -> None:
        """
        create new data file and reset GUI
        :return: None
        """
        self.filename: tuple = MainWindow.filenameDefault  # reset filename
        self.fun_save()  # get and save filename
        self.list_ds: list = []  # reset list of data storages
        self.list_ds = []
        self.list_widget_scenario.clear()  # clear list widget with scenario list

    def change_scenario(self, idx: int) -> None:
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
        ds: DataStorage = self.list_ds[idx]
        # set values of selected Datastorage
        ds.set_values(self.gui_structure)
        # activate checking for changed
        self.checking: bool = True
        # refresh results if results page is selected
        self.gui_structure.page_result.button.click() if self.stackedWidget.currentWidget() == self.gui_structure.page_result.page else None

    def save_scenario(self, idx: int = None) -> None:
        """
        function to save selected scenario
        :return: None
        """
        # set boolean for unsaved scenario changes to False, because we save them now
        self.changedScenario: bool = False
        # get selected scenario index
        idx = max(self.list_widget_scenario.currentRow(), 0) if idx is None or isinstance(idx, bool) else idx
        # if no scenario exists create a new one else save DataStorage with new inputs in list of scenarios
        if len(self.list_ds) == idx:
            self.add_scenario()
        else:
            self.list_ds[idx] = DataStorage(self.gui_structure)
        # create auto backup
        self.fun_save_auto()
        # remove * from scenario if not Auto save is checked and if the last char is a *
        if not self.gui_structure.option_auto_saving.get_value() == 1:
            text = self.list_widget_scenario.item(idx).text()
            if text[-1] == "*":
                self.list_widget_scenario.item(idx).setText(text[:-1])

    def delete_scenario(self) -> None:
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
                if item.text() == f"{self.translations.scenarioString[self.gui_structure.option_language.get_value()]}: {i + 2}":
                    item.setText(f"{self.translations.scenarioString[self.gui_structure.option_language.get_value()]}: {i + 1}")
            # select previous scenario then the deleted one but at least the first one
            self.list_widget_scenario.setCurrentRow(max(idx - 1, 0))

    def add_scenario(self) -> None:
        """
        function to add a scenario
        :return: None
        """
        # get current number of scenario but at least 0
        number: int = max(len(self.list_ds), 0)
        # append new scenario to List of DataStorages
        self.list_ds.append(DataStorage(self.gui_structure))
        # add new scenario name and item to list widget
        self.list_widget_scenario.addItem(f"{self.translations.scenarioString[self.gui_structure.option_language.get_value()]}: {number + 1}")
        # select new list item
        self.list_widget_scenario.setCurrentRow(number)
        # run change function to mark unsaved inputs
        self.change()

    def update_bar(self, val: int, opt_start: bool = False) -> None:
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
        val = val / self.NumberOfScenarios
        # set percentage to progress bar
        self.progressBar.setValue(round(val * 100))
        # hide labels and progressBar if all scenarios are calculated
        if val > 0.9999:
            self.label_Status.hide()
            self.progressBar.hide()
            # show message that calculation is finished
            self.status_bar.showMessage(self.translations.Calculation_Finished[self.gui_structure.option_language.get_value()], 5000)

    def check_ghe_tool(self, finished: bool) -> None:
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
            self.status_bar.showMessage(self.translations.GHE_tool_imported[self.gui_structure.option_language.get_value()], 5000)

    def thread_function(self, results: Tuple[DataStorage, int]) -> None:
        """
        turn on and off the old and new threads for the calculation
        :param results: DataStorage of current thread and current index
        :return: None
        """
        # stop finished thread
        self.threads[self.finished].terminate()

        self.list_ds[results[1]] = results[0]
        # count number of finished calculated scenarios
        self.finished += 1
        # update progress bar
        self.update_bar(self.finished, True)
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
        self.threads[self.finished].any_signal.connect(self.thread_function)

    def start_multiple_scenarios_calculation(self) -> None:
        """
        start calculation of all not calculated scenarios
        :return: None
        """
        # add scenario if no list of scenarios exits else save current scenario
        self.add_scenario() if not self.list_ds else self.save_scenario()
        # return to thermal demands page if no file is selected
        if any([i.fileSelected for i in self.list_ds]):
            self.gui_structure.page_thermal.button.click()
            self.status_bar.showMessage(self.translations.NoFileSelected[self.gui_structure.option_language.get_value()])
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
        self.update_bar(0, True)
        # create list of threads with scenarios that have not been calculated
        self.threads = [CalcProblem(DS, idx) for idx, DS in enumerate(self.list_ds) if DS.borefield is None]
        # set number of to calculate scenarios
        self.NumberOfScenarios: int = len(self.threads)
        # start calculation if at least one scenario has to be calculated
        if self.NumberOfScenarios > 0:
            self.threads[0].start()
            self.threads[0].any_signal.connect(self.thread_function)
            return

    def start_current_scenario_calculation(self) -> None:
        """
        start calculation of selected scenario
        :return: None
        """
        # add scenario if no list of scenarios exits else save current scenario
        self.add_scenario() if not self.list_ds else self.save_scenario()
        # return to thermal demands page if no file is selected
        if self.list_ds[self.list_widget_scenario.currentRow()].fileSelected:
            self.gui_structure.page_thermal.button.click()
            self.status_bar.showMessage(self.translations.NoFileSelected[self.gui_structure.option_language.get_value()])
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
        self.update_bar(0, True)
        # get index of selected scenario
        idx: int = self.list_widget_scenario.currentRow()
        # get Datastorage of selected scenario
        ds: DataStorage = self.list_ds[idx]
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
        self.threads[0].any_signal.connect(self.thread_function)

    def display_results(self) -> None:
        """
        display results of the current selected scenario
        :return: None
        """
        # hide widgets if no list of scenarios exists and display not calculated text
        if not self.list_ds:
            self.gui_structure.hint_depth.label_text.setText(self.translations.NotCalculated[self.gui_structure.option_language.get_value()])
            # self.label_WarningDepth.hide()
            self.gui_structure.option_show_legend.hide()
            self.gui_structure.function_save_results.hide()
            self.gui_structure.function_save_figure.hide()
            self.canvas.hide() if self.canvas is not None else None
            return
        # import here to save start up time
        import matplotlib.pyplot as plt
        from matplotlib import axes as matplotlib_axes
        from matplotlib.backends.backend_qt5agg import \
            FigureCanvasQTAgg as FigureCanvas
        from numpy import array as np_array

        # get Datastorage of selected scenario
        ds: DataStorage = self.list_ds[self.list_widget_scenario.currentRow()]
        # get bore field of selected scenario
        borefield: Borefield = ds.borefield
        # hide widgets if no results bore field exists and display not calculated text
        if borefield is None:
            self.gui_structure.hint_depth.set_text(self.translations.NotCalculated[self.gui_structure.option_language.get_value()])
            # self.label_WarningDepth.hide()
            self.gui_structure.option_show_legend.hide()
            self.gui_structure.function_save_results.hide()
            self.gui_structure.function_save_figure.hide()
            self.canvas.hide() if self.canvas is not None else None
            return
        # get results of bore field sizing by length and width
        li_size = [str(round(i[3], 2)) for i in borefield.combo]
        li_b = [str(round(i[2], 2)) for i in borefield.combo]
        li_n_1 = [str(round(i[0], 2)) for i in borefield.combo]
        li_n_2 = [str(round(i[1], 2)) for i in borefield.combo]
        # hide widgets if no solution exists and display no solution text
        if (ds.aim_size_length and not li_size) or (ds.aim_req_depth and borefield.H == borefield.H_max):
            self.gui_structure.hint_depth.label_text.setText(self.translations.NotCalculated[self.gui_structure.option_language.get_value()])
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
        self.gui_structure.function_save_results.hide() if self.gui_structure.aim_optimize.widget.isChecked() else self.gui_structure.function_save_results.show()
        # get peak heating and cooling and monthly loads as well as Tb temperature
        results_peak_cooling = borefield.results_peak_cooling
        results_peak_heating = borefield.results_peak_heating
        results_month_cooling = borefield.results_month_cooling
        results_month_heating = borefield.results_month_heating
        t_b = borefield.Tb
        # set colors for graph
        background_color: str = array(DARK.replace('rgb(', '').replace(')', '').split(','), dtype=float64)/255
        white_color: str = array(WHITE.replace('rgb(', '').replace(')', '').split(','), dtype=float64)/255
        light_color: str = array(LIGHT.replace('rgb(', '').replace(')', '').split(','), dtype=float64) / 255
        bright_color: str = array(WARNING.replace('rgb(', '').replace(')', '').split(','), dtype=float64) / 255
        plt.rcParams["text.color"] = white_color
        plt.rcParams["axes.labelcolor"] = white_color
        plt.rcParams["xtick.color"] = white_color
        plt.rcParams["ytick.color"] = white_color
        # create figure and axe if not already exists
        self.fig = plt.Figure(facecolor=background_color) if self.fig is None else self.fig
        canvas = FigureCanvas(self.fig) if self.canvas is None else self.canvas
        ax: matplotlib_axes._subplots.AxesSubplot = canvas.figure.subplots() if self.ax == [] else self.ax[0]
        # clear axces for new plot
        ax.clear()
        # plot remaining peak heating and cooling as well as loads if the profile is optimized instead of temperatures
        if ds.aim_optimize:
            # create new x-axe
            time_array: list = [i + 1 for i in range(12)]
            # create second y-axe if not already exists
            ax2 = ax.twinx() if len(self.ax) < 2 else self.ax[1]
            # clear the axe
            ax2.clear()
            # plot load and peaks
            ax.step(
                np_array(time_array),
                np_array(borefield.peak_cooling_external),
                where="pre",
                lw=1.5,
                label=f"P {self.translations.PeakCooling[self.gui_structure.option_language.get_value()]}",
                color=light_color,
            )
            ax.step(
                np_array(time_array),
                np_array(borefield.peak_heating_external),
                where="pre",
                lw=1.5,
                label=f"P {self.translations.PeakHeating[self.gui_structure.option_language.get_value()]}",
                color=bright_color,
            )
            ax2.step(
                np_array(time_array),
                np_array(borefield.monthly_load_cooling_external),
                color="#54bceb",
                linestyle="dashed",
                where="pre",
                lw=1.5,
                label=f"Q {self.translations.BaseCooling[self.gui_structure.option_language.get_value()]}",
            )
            ax2.step(
                np_array(time_array),
                np_array(borefield.monthly_load_heating_external),
                color=bright_color,
                linestyle="dashed",
                where="pre",
                lw=1.5,
                label=f"Q {self.translations.BaseHeating}",
            )
            # set x-axe limits
            ax.set_xlim(left=1, right=12)
            ax2.set_xlim(left=1, right=12)
            # create legends
            ax.legend(facecolor=background_color, loc="upper left")
            ax2.legend(facecolor=background_color, loc="upper right")
            # set labels of axes
            ax.set_xlabel(self.translations.X_Axis_Load[self.gui_structure.option_language.get_value()], color=white_color)
            ax.set_ylabel(self.translations.Y_Axis_Load_P[self.gui_structure.option_language.get_value()], color=white_color)
            ax2.set_xlabel(self.translations.X_Axis_Load[self.gui_structure.option_language.get_value()], color=white_color)
            ax2.set_ylabel(self.translations.Y_Axis_Load_Q[self.gui_structure.option_language.get_value()], color=white_color)
            # set axe colors
            ax.spines["bottom"].set_color(white_color)
            ax.spines["top"].set_color(white_color)
            ax.spines["right"].set_color(white_color)
            ax.spines["left"].set_color(white_color)
            ax2.spines["bottom"].set_color(white_color)
            ax2.spines["top"].set_color(white_color)
            ax2.spines["right"].set_color(white_color)
            ax2.spines["left"].set_color(white_color)
            ax.set_facecolor(background_color)
            ax2.set_facecolor(background_color)
            # import numpy here to save start up time
            import numpy as np

            # create string for result explanation
            string_size: str = (
                f"{self.translations.label_ResOptimizeLoad1[self.gui_structure.option_language.get_value()]}"
                f"{int(max(borefield.hourly_heating_load)) - int(np.max(borefield.peak_heating_external))}"
                f" / {int(max(borefield.hourly_cooling_load)) - int(np.max(borefield.peak_cooling_external))} kW\n"
                f"{self.translations.label_ResOptimizeLoad2[self.gui_structure.option_language.get_value()]}{np.round(np.sum(borefield.baseload_heating), 2)} / "
                f"{np.round(np.sum(borefield.baseload_cooling), 2)}   kWh\n"
                f"{self.translations.label_ResOptimizeLoad3[self.gui_structure.option_language.get_value()]}"
                f"{np.round(np.sum(borefield.baseload_heating) / np.sum(borefield.hourly_heating_load) * 100, 2)} / "
                f"{np.round(np.sum(borefield.baseload_cooling) / np.sum(borefield.hourly_cooling_load) * 100, 2)} "
                f"{self.translations.label_ResOptimizeLoad4[self.gui_structure.option_language.get_value()]}\n"
                f"{self.translations.label_ResOptimizeLoad5[self.gui_structure.option_language.get_value()]}"
                f"{int(np.max(borefield.peak_heating_external))} / "
                f"{int(np.max(borefield.peak_cooling_external))} kW\n"
                f"{self.translations.label_ResOptimizeLoad6[self.gui_structure.option_language.get_value()]}"
                f"{np.round(-np.sum(borefield.baseload_heating) + np.sum(borefield.hourly_heating_load), 2)} / "
                f"{np.round(-np.sum(borefield.baseload_cooling) + np.sum(borefield.hourly_cooling_load), 2)} kWh"
            )
        else:
            # remove second axes if exist
            self.ax[1].remove() if len(self.ax) > 1 else None
            # calculation of all the different times at which the g_function should be calculated.
            # this is equal to 'UPM' hours a month * 3600 seconds/hours for the simulationPeriod
            time_for_g_values = [i * borefield.UPM * 3600.0 for i in range(1, 12 * borefield.simulation_period + 1)]
            # make a time array
            time_array = [i / 12 / 730.0 / 3600.0 for i in time_for_g_values]
            # plot Temperatures
            ax.step(np_array(time_array), np_array(t_b), "w-", where="pre", lw=1.5, label="Tb")
            ax.step(
                np_array(time_array),
                np_array(results_peak_cooling),
                where="pre",
                lw=1.5,
                label=f"Tf {self.translations.PeakCooling[self.gui_structure.option_language.get_value()]}",
                color=light_color,
            )
            ax.step(
                np_array(time_array),
                np_array(results_peak_heating),
                where="pre",
                lw=1.5,
                label=f"Tf {self.translations.PeakHeating[self.gui_structure.option_language.get_value()]}",
                color=bright_color,
            )
            # define temperature bounds
            ax.step(
                np_array(time_array),
                np_array(results_month_cooling),
                color=light_color,
                linestyle="dashed",
                where="pre",
                lw=1.5,
                label=f"Tf {self.translations.BaseCooling[self.gui_structure.option_language.get_value()]}",
            )
            ax.step(
                np_array(time_array),
                np_array(results_month_heating),
                color=bright_color,
                linestyle="dashed",
                where="pre",
                lw=1.5,
                label=f"Tf {self.translations.BaseHeating[self.gui_structure.option_language.get_value()]}",
            )
            ax.hlines(borefield.Tf_C, 0, ds.option_simu_period, colors=bright_color, linestyles="dashed", label="", lw=1)
            ax.hlines(borefield.Tf_H, 0, ds.option_simu_period, colors=light_color, linestyles="dashed", label="", lw=1)
            ax.set_xticks(range(0, ds.option_simu_period + 1, 2))
            # Plot legend
            ax.set_xlim(left=0, right=ds.option_simu_period)
            # create legend
            ax.legend(facecolor=background_color, loc="best")
            # set axes names
            ax.set_xlabel(self.translations.X_Axis[self.gui_structure.option_language.get_value()], color=white_color)
            ax.set_ylabel(self.translations.Y_Axis[self.gui_structure.option_language.get_value()], color=white_color)
            # set colors
            ax.spines["bottom"].set_color(white_color)
            ax.spines["top"].set_color(white_color)
            ax.spines["right"].set_color(white_color)
            ax.spines["left"].set_color(white_color)
            ax.set_facecolor(background_color)
            # create result display string
            string_size: str = (
                f'{self.translations.hint_depth[self.gui_structure.option_language.get_value()]}{"; ".join(li_size)} m \n'
                f'{self.translations.label_Size_B[self.gui_structure.option_language.get_value()]}{"; ".join(li_b)} m \n'
                f'{self.translations.label_Size_W[self.gui_structure.option_language.get_value()]}{"; ".join(li_n_1)} \n'
                f'{self.translations.label_Size_L[self.gui_structure.option_language.get_value()]}{"; ".join(li_n_2)} \n'
                if ds.aim_size_length
                else f"{self.translations.hint_depth[self.gui_structure.option_language.get_value()]}{round(borefield.H, 2)} m"
            )
            # not use axe 2
            ax2 = None
        # set string to depth size label
        self.gui_structure.hint_depth.set_text(string_size)
        # display warning if depth is to small
        # self.label_WarningDepth.show() if borefield.H < 50 else self.label_WarningDepth.hide()
        # save variables
        self.ax = [ax] if not ds.aim_optimize else [ax, ax2]
        self.gui_structure.category_result_figure.frame.layout().addWidget(canvas) if self.canvas is None else None
        self.canvas.show() if self.canvas is not None else None
        self.canvas = canvas
        # draw new plot
        plt.tight_layout()
        canvas.draw()

    def check_legend(self) -> None:
        """
        function to check if a legend should be displayed
        :return: None
        """
        if self.canvas is None:
            return
        # check if the legend should be displayed
        if self.gui_structure.option_show_legend.get_value() == 0:
            # set grey color
            grey_color = GREY
            # set legend to graph either two if load is optimized or one otherwise with their locations
            if len(self.ax) > 1:
                self.ax[0].legend(facecolor=grey_color, loc="upper left")
                self.ax[1].legend(facecolor=grey_color, loc="upper right")
            else:
                self.ax[0].legend(facecolor=grey_color, loc="best")
            # redraw graph
            self.canvas.draw()
            return
        # otherwise, remove legend and redraw graph
        for i in self.ax:
            i.get_legend().remove()
        self.canvas.draw()

    def save_figure(self) -> None:
        """
        save figure to the QFileDialog asked location
        :return: None
        """
        # get filename at storage place
        filename = QtWidgets_QFileDialog.getSaveFileName(
            self.central_widget, caption=self.translations.SaveFigure[self.gui_structure.option_language.get_value()], filter="png (*.png)"
        )
        # display message and return if no file is selected
        if filename == MainWindow.filenameDefault:
            self.status_bar.showMessage(self.translations.NoFileSelected[self.gui_structure.option_language.get_value()], 5000)
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
        filename = QtWidgets_QFileDialog.getSaveFileName(
            self.central_widget, caption=self.translations.SaveData[self.gui_structure.option_language.get_value()], filter="csv (*.csv)"
        )
        # display message and return if no file is selected
        if filename == MainWindow.filenameDefault:
            self.status_bar.showMessage(self.translations.NoFileSelected[self.gui_structure.option_language.get_value()], 5000)
            return
        # get maximal simulation period
        simulation_time = max([i.option_simu_period for i in self.list_ds])
        # create first two column entries
        to_write = [
            ["name", "unit"],  # 0
            ["depth", "m"],  # 1
            ["borehole spacing", "m"],  # 2
            ["conductivity of the soil", "W/mK"],  # 3
            ["Ground temperature at infinity", "C"],  # 4
            ["Equivalent borehole resistance", "mK/W"],  # 5
            ["width of rectangular field", "#"],  # 6
            ["length of rectangular field", "#"],  # 7
            ["Determine length", "0/1"],
            ["Simulation Period", "years"],
            ["Minimal temperature", "C"],
            ["Maximal temperature", "C"],
        ]
        month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        month_yrs = [f"{mon}_{int(idx/12)+1}" for idx, mon in enumerate(month * simulation_time)]
        to_write = to_write + [[f"Peak heating {mon}", "kW"] for mon in month]
        to_write = to_write + [[f"Peak cooling {mon}", "kW"] for mon in month]
        to_write = to_write + [[f"Load heating {mon}", "kWh"] for mon in month]
        to_write = to_write + [[f"Load cooling {mon}", "kWh"] for mon in month]
        to_write = to_write + [[f"Results peak heating {mon}", "C"] for mon in month_yrs]
        to_write = to_write + [[f"Results peak cooling {mon}", "C"] for mon in month_yrs]
        to_write = to_write + [[f"Results load heating {mon}", "C"] for mon in month_yrs]
        to_write = to_write + [[f"Results load cooling {mon}", "C"] for mon in month_yrs]
        # define ranges for results
        ran_yr = range(12)
        ran_simu = range(12 * simulation_time)
        # start looping over results in list_ds and append them to to_write
        for idx, ds in enumerate(self.list_ds):
            ds: DataStorage = ds
            i = 0
            to_write[i].append(f"{self.list_widget_scenario.item(idx).text()}")
            i += 1
            to_write[i].append(f"{round(ds.ground_data.H, 2)}")
            i += 1
            to_write[i].append(f"{round(ds.ground_data.B, 2)}")
            i += 1
            to_write[i].append(f"{round(ds.ground_data.k_s, 2)}")
            i += 1
            to_write[i].append(f"{round(ds.ground_data.Tg, 2)}")
            i += 1
            to_write[i].append(f"{round(ds.ground_data.Rb, 4)}")
            i += 1
            to_write[i].append(f"{round(ds.ground_data.N_1, 0)}")
            i += 1
            to_write[i].append(f"{round(ds.ground_data.N_2, 0)}")
            i += 1
            to_write[i].append(f"{round(ds.aim_req_depth, 0)}")
            i += 1
            to_write[i].append(f"{round(ds.option_simu_period, 0)}")
            i += 1
            to_write[i].append(f"{round(ds.option_min_temp, 2)}")
            i += 1
            to_write[i].append(f"{round(ds.option_max_temp, 2)}")
            for j in ran_yr:
                i += 1
                to_write[i].append(f"{round(ds.peakHeating[j], 2)}")
            for j in ran_yr:
                i += 1
                to_write[i].append(f"{round(ds.peakCooling[j], 2)}")
            for j in ran_yr:
                i += 1
                to_write[i].append(f"{round(ds.monthlyLoadHeating[j], 2)}")
            for j in ran_yr:
                i += 1
                to_write[i].append(f"{round(ds.monthlyLoadCooling[j], 2)}")
            if ds.borefield is None:
                i += 1
                [to_write[i + j].append(self.translations.NotCalculated[self.gui_structure.option_language.get_value()]) for j in ran_simu]
                i += len(ran_simu)
                [to_write[i + j].append(self.translations.NotCalculated[self.gui_structure.option_language.get_value()]) for j in ran_simu]
                i += len(ran_simu)
                [to_write[i + j].append(self.translations.NotCalculated[self.gui_structure.option_language.get_value()]) for j in ran_simu]
                i += len(ran_simu)
                [to_write[i + j].append(self.translations.NotCalculated[self.gui_structure.option_language.get_value()]) for j in ran_simu]
                i += len(ran_simu)
                continue
            for j in ran_simu:
                i += 1
                try:
                    to_write[i].append(f"{round(ds.borefield.results_peak_heating[j], 2)}")
                except IndexError:
                    to_write[i].append(self.translations.NotCalculated[self.gui_structure.option_language.get_value()])
            for j in ran_simu:
                i += 1
                try:
                    to_write[i].append(f"{round(ds.borefield.results_peak_cooling[j], 2)}")
                except IndexError:
                    to_write[i].append(self.translations.NotCalculated[self.gui_structure.option_language.get_value()])
            for j in ran_simu:
                i += 1
                try:
                    to_write[i].append(f"{round(ds.borefield.results_month_heating[j], 2)}")
                except IndexError:
                    to_write[i].append(self.translations.NotCalculated[self.gui_structure.option_language.get_value()])
            for j in ran_simu:
                i += 1
                try:
                    to_write[i].append(f"{round(ds.borefield.results_month_cooling[j], 2)}")
                except IndexError:
                    to_write[i].append(self.translations.NotCalculated[self.gui_structure.option_language.get_value()])
        # try to write the data else show error message in status bar
        try:
            with open(filename[0], "w", newline="") as f:
                writer = csv_writer(f, delimiter=";")
                for row in to_write:
                    writer.writerow(row)
        except FileNotFoundError:
            self.status_bar.showMessage(self.translations.NoFileSelected[self.gui_structure.option_language.get_value()], 5000)
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
        msg.setText(self.translations.label_CancelText[self.gui_structure.option_language.get_value()])
        # set window text to cancel text depending on language selected
        msg.setWindowTitle(self.translations.label_CancelTitle[self.gui_structure.option_language.get_value()])
        # set standard buttons to save, close and cancel
        msg.setStandardButtons(QtWidgets_QMessageBox.Save | QtWidgets_QMessageBox.Close | QtWidgets_QMessageBox.Cancel)
        # get save, close and cancel button
        button_s = msg.button(QtWidgets_QMessageBox.Save)
        button_cl = msg.button(QtWidgets_QMessageBox.Close)
        button_ca = msg.button(QtWidgets_QMessageBox.Cancel)
        # set save, close and cancel button text depending on language selected
        button_s.setText(f"{self.translations.label_Save[self.gui_structure.option_language.get_value()]} ")
        button_cl.setText(f"{self.translations.label_close[self.gui_structure.option_language.get_value()]} ")
        button_ca.setText(f"{self.translations.label_cancel[self.gui_structure.option_language.get_value()]} ")
        # set  save, close and cancel button icon
        self.set_push_button_icon(button_s, "Save_Inv")
        self.set_push_button_icon(button_cl, "Exit")
        self.set_push_button_icon(button_ca, "Abort")
        # execute message box and save response
        reply = msg.exec_()
        # check if closing should be canceled
        if reply == QtWidgets_QMessageBox.Cancel:
            # cancel closing event
            event.ignore()
            return
        # check if inputs should be saved and if successfully set closing variable to true
        close: bool = self.fun_save() if reply == QtWidgets_QMessageBox.Save else True
        # stop all calculation threads
        [i.terminate() for i in self.threads]
        # close window if close variable is true else not
        event.accept() if close else event.ignore()


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
        super(ImportGHEtool, self).__init__(parent)  # init parent class

    def run(self) -> None:
        """
        start import
        :return: None
        """
        import GHEtool  # import GHEtool

        GHEtool.FOLDER = "./"
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
