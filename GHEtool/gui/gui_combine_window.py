from functools import partial as ft_partial
from pickle import load as pk_load
from json import dump, load, JSONDecodeError
from os import makedirs, remove
from os.path import dirname, exists, realpath
from os.path import split as os_split
from pathlib import Path, PurePath
from sys import path
from typing import List, Tuple
from GHEtool import Borefield, FOLDER
from configparser import ConfigParser

import PySide6.QtCore as QtC
import PySide6.QtGui as QtG
import PySide6.QtWidgets as QtW
import pathlib

from .gui_base_class import UiGhetool, set_graph_layout
from .gui_calculation_thread import CalcProblem
from .gui_data_storage import DataStorage
from .gui_structure import FigureOption, GuiStructure, Option
from .translation_class import Translations


currentdir = dirname(realpath(__file__))
parentdir = dirname(currentdir)
path.append(parentdir)

BACKUP_FILENAME: str = 'backup.GHEtoolBackUp'

# get current version
path = pathlib.Path(FOLDER).parent
config = ConfigParser()
config.read_file(open(path.joinpath('setup.cfg'), 'r'))
VERSION = config.get('metadata', 'version')


# main GUI class
class MainWindow(QtW.QMainWindow, UiGhetool):
    filenameDefault: tuple = ("", "")

    def __init__(self, dialog: QtW.QWidget, app: QtW.QApplication) -> None:
        """
        initialize window
        :param dialog: Q widget as main window
        :param app: application widget
        """
        # parameter to show the end of the init function
        self.started = False
        # init windows of parent class
        super(MainWindow, self).__init__()
        super().setup_ui(dialog)
        # pyside6-rcc icons.qrc -o icons_rc.py

        self.gui_structure = GuiStructure(self.central_widget, self.status_bar)
        for page in self.gui_structure.list_of_pages:
            page.create_page(self.central_widget, self.stackedWidget, self.verticalLayout_menu)

        self.verticalSpacer = QtW.QSpacerItem(20, 40, QtW.QSizePolicy.Minimum, QtW.QSizePolicy.Expanding)
        self.verticalLayout_menu.addItem(self.verticalSpacer)

        # self.add_aims(list_button)
        # set app and dialog
        self.app: QtW.QApplication = app
        self.Dia = dialog
        # init variables of class
        # allow checking of changes
        self.checking: bool = False
        # create backup path in home documents directory
        self.default_path: PurePath = PurePath(Path.home(), 'Documents/GHEtool')
        self.backup_file: PurePath = PurePath(self.default_path, BACKUP_FILENAME)
        # check if backup folder exits and otherwise create it
        makedirs(dirname(self.backup_file), exist_ok=True)
        makedirs(dirname(self.default_path), exist_ok=True)
        self.translations: Translations = Translations()  # init translation class
        for idx, (name, icon, short_cut) in enumerate(zip(self.translations.languages, self.translations.icon, self.translations.short_cut)):
            self.create_action_language(idx, name, icon, short_cut)
        # add languages to combo box
        self.gui_structure.option_language.widget.addItems(self.translations.languages)
        self.fileImport = None  # init import file
        self.filename: tuple = MainWindow.filenameDefault  # filename of stored inputs
        self.list_widget_scenario.clear()  # reset list widget with stored scenarios
        self.changedScenario: bool = False  # set change scenario variable to false
        self.changedFile: bool = False  # set change file variable to false
        self.ax: list = []  # axes of figure
        self.axBorehole = None
        self.NumberOfScenarios: int = 1  # number of scenarios
        self.finished: int = 1  # number of finished scenarios
        self.threads: List[CalcProblem] = []  # list of calculation threads
        self.list_ds: List[DataStorage] = []  # list of data storages
        self.sizeB = QtC.QSize(48, 48)  # size of big logo on push button
        self.sizeS = QtC.QSize(24, 24)  # size of small logo on push button
        self.sizePushB = QtC.QSize(150, 75)  # size of big push button
        self.sizePushS = QtC.QSize(75, 75)  # size of small push button
        # init links from buttons to functions
        self.set_links()
        # reset progress bar
        self.update_bar(0, False)
        # set event filter for push button sizing
        self.event_filter_install()
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

        current_aim = [aim for aim, _ in self.gui_structure.list_of_aims if aim.widget.isChecked()]
        for aim, _ in self.gui_structure.list_of_aims:
            if aim not in current_aim:
                aim.widget.click()

        current_aim[0].widget.click()

        [option.init_links() for option, _ in self.gui_structure.list_of_options]

        self.status_bar.showMessage(self.translations.GHE_tool_imported[self.gui_structure.option_language.get_value()], 5000)
        # allow checking of changes
        self.checking: bool = True

        # set the correct graph layout
        set_graph_layout()

        self.display_results()

        # set started to True
        # this is so that no changes are made when the file is opening
        self.started: bool = True

    def create_action_language(self, idx: int, name: str, icon_name: str, short_cut: str):
        action = QtG.QAction(self.central_widget)
        icon = QtG.QIcon()
        icon.addFile(icon_name, QtC.QSize(), QtG.QIcon.Normal, QtG.QIcon.Off)
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

        setting_options = [(opt_cat, name) for category in self.gui_structure.page_settings.list_categories for opt_cat in category.list_of_options if
                           isinstance(opt_cat, Option) for opt_glob, name in self.gui_structure.list_of_options if opt_cat == opt_glob]
        for option, name in [(opt, name) for opt, name in self.gui_structure.list_of_options
                             if not isinstance(opt, FigureOption) and not ((opt, name) in setting_options)]:
            option.change_event(self.change)
        for option, name in [(opt, name) for opt, name in self.gui_structure.list_of_options if isinstance(opt, FigureOption)]:
            option.change_event(self.update_graph)
        for option, name in self.gui_structure.list_of_aims:
            option.change_event(self.change)

        for option, name in setting_options:
            option.change_event(ft_partial(self.change_settings_in_all_data_storages, name))

        self.gui_structure.option_language.change_event(self.change_language)
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

    def update_graph(self):
        if not self.list_ds:
            return
        ds = self.list_ds[self.list_widget_scenario.currentRow()]
        if ds.borefield is None:
            return
        ds.close_figures()
        self.display_results()

    def event_filter(self, obj: QtW.QPushButton, event) -> bool:
        """
        function to check mouse over event
        :param obj:
        PushButton obj
        :param event:
        event to check if mouse over event is entering or leaving
        :return:
        Boolean to check if the function worked
        """
        if event.type() == QtC.QEvent.Enter:
            # Mouse is over the label
            self.set_push(True)
            return True
        elif event.type() == QtC.QEvent.Leave:
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

    def set_push_button_icon_size(self, button: QtW.QPushButton, big: bool = False, name: str = "") -> None:
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
        # return if not yet started
        if not self.started:
            return
        # return if checking is not allowed
        if not self.checking:
            return
        if self.check_values():
            self.pushButton_start_multiple.setEnabled(True)
            self.pushButton_start_single.setEnabled(True)
            self.pushButton_AddScenario.setEnabled(True)
            self.pushButton_SaveScenario.setEnabled(True)
            self.list_widget_scenario.setEnabled(True)
        else:
            self.pushButton_start_multiple.setEnabled(False)
            self.pushButton_start_single.setEnabled(False)
            self.pushButton_AddScenario.setEnabled(False)
            self.pushButton_SaveScenario.setEnabled(False)
            self.list_widget_scenario.setEnabled(False)
        # if changed File is not already True set it to True and update window title
        if self.changedFile is False:
            self.changedFile: bool = True
            self.change_window_title()
        # get current index of scenario
        idx: int = self.list_widget_scenario.currentRow()
        if self.list_ds:
            # remove borefield object
            self.list_ds[idx].borefield = None
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

    def fun_auto_save_scenario(self, new_row_item: QtW.QListWidgetItem, old_row_item: QtW.QListWidgetItem) -> None:
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

        def return_2_old_item():
            # change item to old item by thread, because I have not found a direct way which is not lost after
            # return
            ds = DataStorage(self.gui_structure)
            t = QtC.QTimer(self)

            def hello():
                self.list_widget_scenario.blockSignals(True)
                self.checking = False
                self.list_widget_scenario.setCurrentItem(old_row_item)
                # set values of selected Datastorage
                ds.set_values(self.gui_structure)
                self.checking = True
                self.list_widget_scenario.blockSignals(False)
                t.stop()

            t.timeout.connect(hello)
            t.start(10)  # after 30 seconds, "hello, world" will be printed
        # check if the auto saving should be performed and then save the last selected scenario
        if self.gui_structure.option_auto_saving.get_value() == 1:
            if not self.check_values():
                return_2_old_item()
                return
            # save old scenario
            if DataStorage(self.gui_structure) != self.list_ds[self.list_widget_scenario.row(old_row_item)]:
                self.list_ds[self.list_widget_scenario.row(old_row_item)].close_figures()
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
            msg: QtW.QMessageBox = QtW.QMessageBox(self.Dia)
            # set Icon to question mark icon
            msg.setIcon(QtW.QMessageBox.Question)
            # set label text to leave scenario text depending on language selected
            msg.setText(self.translations.label_LeaveScenarioText[self.gui_structure.option_language.get_value()])
            # set window text to  leave scenario text depending on language selected
            msg.setWindowTitle(self.translations.label_CancelTitle[self.gui_structure.option_language.get_value()])
            # set standard buttons to save, close and cancel
            msg.setStandardButtons(QtW.QMessageBox.Save | QtW.QMessageBox.Close | QtW.QMessageBox.Cancel)
            # get save, close and cancel button
            button_s = msg.button(QtW.QMessageBox.Save)
            button_cl = msg.button(QtW.QMessageBox.Close)
            button_ca = msg.button(QtW.QMessageBox.Cancel)
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
            if reply == QtW.QMessageBox.Cancel:
                return_2_old_item()
                return
            # save scenario if wanted
            if reply == QtW.QMessageBox.Save:
                if not self.save_scenario(self.list_widget_scenario.row(old_row_item)):
                    return_2_old_item()
            # remove * symbol
            old_row_item.setText(text[:-1])
        # change entries to new scenario values
        self.change_scenario(self.list_widget_scenario.row(new_row_item))
        return

    def fun_move_scenario(self, start_item: QtC.QModelIndex, start_index: int, start_index2: int, end_item: QtC.QModelIndex, target_index: int) -> None:
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
    def set_push_button_icon(button: QtW.QPushButton, icon_name: str) -> None:
        """
        set QPushButton icon
        :param button: QPushButton to change to icon for
        :param icon_name: icon name as string
        :return: None
        """
        icon = QtG.QIcon()  # create icon class
        # add pixmap to icon
        icon.addPixmap(QtG.QPixmap(f":/icons/icons/{icon_name}.svg"), QtG.QIcon.Normal, QtG.QIcon.Off)
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
        dialog = QtW.QInputDialog(self.Dia)
        dialog.setWindowTitle(self.translations.label_new_scenario[self.gui_structure.option_language.get_value()])
        dialog.setLabelText(f"{self.translations.new_name[self.gui_structure.option_language.get_value()]}{item.text()}:")
        dialog.setOkButtonText(self.translations.label_okay[self.gui_structure.option_language.get_value()])  # +++
        dialog.setCancelButtonText(self.translations.label_abort[self.gui_structure.option_language.get_value()])  # +++
        li = dialog.findChildren(QtW.QPushButton)
        self.set_push_button_icon(li[0], "Okay")
        self.set_push_button_icon(li[1], "Abort")
        # set new name if the dialog is not canceled and the text is not None
        if dialog.exec_() == QtW.QDialog.Accepted:
            text = dialog.textValue()
            item.setText(text) if text != "" else None

    def check_results(self) -> None:
        """
        check if results exists and then display them
        :return:
        """
        # hide results buttons if no results where found
        if any([(i.borefield is None) for i in self.list_ds]) or self.list_ds == []:
            # self.gui_structure.function_save_results.hide()
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
        title: str = "" if filename == "" else f' - {filename.replace(".GHEtool", "")}'
        # create new title name
        name: str = f"GHEtool v{VERSION} {title}*" if self.changedFile else f"GHEtool v{VERSION} {title}"
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

    def eventFilter(self, obj: QtW.QPushButton, event) -> bool:
        """
        function to check mouse over event
        :param obj:
        PushButton obj
        :param event:
        event to check if mouse over event is entering or leaving
        :return:
        Boolean to check if the function worked
        """
        if event.type() == QtC.QEvent.Enter:
            # Mouse is over the label
            self.set_push(True)
            return True
        elif event.type() == QtC.QEvent.Leave:
            # Mouse is not over the label
            self.set_push(False)
            return True
        return False

    def change_settings_in_all_data_storages(self, name_of_option: str, *args):
        for ds in self.list_ds:
            setattr(ds, name_of_option, getattr(self.gui_structure, name_of_option).get_value() if len(args) < 1 else args[0])

    def change_language(self) -> None:
        """
        function to change language on labels and push buttons
        :return: None
        """
        self.checking = False
        scenario_index: int = self.list_widget_scenario.currentRow()  # get current selected scenario
        amount: int = self.list_widget_scenario.count()  # number of scenario elements

        # check if list scenario names are not unique
        li_str_match: List[bool] = [
            self.list_widget_scenario.item(idx).text() == f"{self.translations.scenarioString[self.gui_structure.option_language.get_value()]}: {idx + 1}"
            for idx in range(amount)
        ]
        # update all label, pushButtons, action and Menu names
        for i in [j for j in self.translations.__slots__ if hasattr(self, j)]:
            if isinstance(getattr(self, i), QtW.QMenu):
                getattr(self, i).setTitle(getattr(self.translations, i)[self.gui_structure.option_language.get_value()])
                continue
            getattr(self, i).setText(getattr(self.translations, i)[self.gui_structure.option_language.get_value()])
        # set translation of toolbox items
        self.gui_structure.translate(self.gui_structure.option_language.get_value(), self.translations)
        for idx, name in enumerate(self.translations.languages):
            self.gui_structure.option_language.widget.setItemText(idx, name)
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
        self.checking = True

    def delete_backup(self):
        if exists(self.backup_file):
            remove(self.backup_file)

    def load_list(self) -> None:
        """
        try to open the backup file and set the old values
        :return: None
        """
        # try to open backup file if it exits
        if exists(self.backup_file):
            self._load_from_data(self.backup_file)
            # change language to english if no change has happened
            if self.gui_structure.option_language.get_value() == 0:
                self.change_language()
            return
        # change language to english
        self.change_language()
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

        self._save_to_data(self.backup_file)

    def _load_from_data(self, location: str) -> None:
        """
        This function loads the data from a JSON formatted file.

        Parameters
        ----------
        location : str
            Location of the data file

        Returns
        -------
        None
        """

        def general_changes(scenarios):
            # change window title to new loaded filename
            self.change_window_title()
            # replace user window id
            for DS in self.list_ds:
                DS.ui = id(self)

            # init user window by reset scenario list widget and check for results
            self.list_widget_scenario.clear()
            self.list_widget_scenario.addItems(scenarios)
            self.list_widget_scenario.setCurrentRow(0)
            self.check_results()

        try:
            # open file and get data
            with open(location, "r") as file:
                saving = load(file)

            version = saving['version']
        except (JSONDecodeError,  FileNotFoundError, UnicodeDecodeError):
            try:
                # try to open as pickle
                with open(location, "rb") as file:
                    saving = pk_load(file)

                version = "2.1.0"
            except (FileNotFoundError, ImportError):
                raise ImportError("The datafile cannot be loaded!")

        if version == "2.1.1":
            # write data to variables
            self.list_ds = []
            for val, borefield in zip(saving['values'], saving['borefields']):
                ds = DataStorage(self.gui_structure)
                ds.from_dict(val)
                if borefield is None:
                    setattr(ds, 'borefield', None)
                else:
                    setattr(ds, 'borefield', Borefield())
                    getattr(ds, 'borefield')._from_dict(borefield)
                self.list_ds.append(ds)
            # set and change the window title
            self.filename = saving['filename']
            general_changes(saving['names'])
            return

        if version == "2.1.0":
            self.filename, li, settings = saving
            # write data to variables
            self.list_ds, li = li[0], li[1]

            # since the borefield object is changed, this is deleted from the dataframe
            #for ds in self.list_ds:
            #    setattr(ds, 'borefield', None)

            # convert to new ds format
            for idx, ds in enumerate(self.list_ds):
                ds_new = DataStorage(self.gui_structure)
                [setattr(ds_new, name, getattr(ds, name)) for name in ds.__dict__ if hasattr(ds_new, name)]
                if ds.borefield is not None:
                    bf = Borefield()
                    [setattr(bf, name, getattr(ds.borefield, name)) for name in ds.borefield.__slots__ if hasattr(bf, name) and hasattr(ds.borefield, name)]
                    setattr(ds_new, 'borefield', bf)
                self.list_ds[idx] = ds_new
            # write scenario names
            general_changes(li)

    def _save_to_data(self, location: str) -> None:
        """
        This function saves the gui data to a json formatted file.

        Parameters
        ----------
        location : str
            Location of the data file.

        Returns
        -------
        None
        """
        # create list of all scenario names
        scenario_names = [self.list_widget_scenario.item(idx).text() for idx in
                          range(self.list_widget_scenario.count())]
        # create saving dict
        saving = {'filename': self.filename,
                  'names': scenario_names,
                  'version': VERSION,
                  'values': [ds.to_dict() for ds in self.list_ds],
                  'borefields': [getattr(ds, 'borefield')._to_dict() if getattr(ds, 'borefield') is not None else None
                                 for ds in self.list_ds]}
        try:
            # write data to back up file
            with open(location, "w") as file:
                dump(saving, file, indent=1)
        except FileNotFoundError:
            self.status_bar.showMessage(
                self.translations.NoFileSelected[self.gui_structure.option_language.get_value()], 5000)
        except PermissionError:
            self.status_bar.showMessage("PermissionError", 5000)

    def fun_load(self) -> None:
        """
        function to load externally stored scenario
        :return: None
        """
        # open interface and get file name
        self.filename = QtW.QFileDialog.getOpenFileName(
            self.central_widget, caption=self.translations.ChoosePKL[self.gui_structure.option_language.get_value()], filter="GHEtool (*.GHEtool)",
            dir=str(self.default_path)
        )
        # load selected data
        self.fun_load_known_filename()

    def fun_load_known_filename(self) -> None:
        """
        load stored scenarios from external json file
        :return: None
        """
        # try to open the file
        try:
            # deactivate checking
            self.checking: bool = False
            # open file and set data
            self._load_from_data(self.filename[0])
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
            self.filename: tuple = QtW.QFileDialog.getSaveFileName(
                self.central_widget, caption=self.translations.SavePKL[self.gui_structure.option_language.get_value()], filter="GHEtool (*.GHEtool)",
                dir=str(self.default_path),
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
            self._save_to_data(self.filename[0])
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
        if self.fun_save():  # get and save filename
            self.list_ds: list = []  # reset list of data storages
            self.list_widget_scenario.clear()  # clear list widget with scenario list
            self.display_results()  # clear the results page

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
        # refresh results if results page is selected
        self.display_results() if self.stackedWidget.currentWidget() == self.gui_structure.page_result.page else None
        # activate checking for changed
        self.checking: bool = True

    def check_values(self) -> bool:
        if not all(option.check_value() for option, _ in self.gui_structure.list_of_options):
            for option, _ in self.gui_structure.list_of_options:
                if not option.check_value():
                    self.status_bar.showMessage(f'Wrong value in option with label: {option.label_text}', 5000)
                    return False
        return True

    def save_scenario(self, idx: int = None) -> bool:
        """
        function to save selected scenario
        :return: None
        """
        # set boolean for unsaved scenario changes to False, because we save them now
        self.changedScenario: bool = False

        if not self.check_values():
            return False
        # get selected scenario index
        idx: int = max(self.list_widget_scenario.currentRow(), 0) if idx is None or isinstance(idx, bool) else idx
        # if no scenario exists create a new one else save DataStorage with new inputs in list of scenarios
        if len(self.list_ds) == idx:
            self.add_scenario()
        else:
            # do not overwrite any results
            if self.list_ds[idx].borefield is None:
                self.list_ds[idx].close_figures()
                self.list_ds[idx] = DataStorage(self.gui_structure)
        # create auto backup
        self.fun_save_auto()
        # remove * from scenario if not Auto save is checked and if the last char is a *
        if not self.gui_structure.option_auto_saving.get_value() == 1:
            text = self.list_widget_scenario.item(idx).text()
            if text[-1] == "*":
                self.list_widget_scenario.item(idx).setText(text[:-1])
        return True

    def delete_scenario(self) -> None:
        """
        function to delete the selected scenario
        :return: None
        """
        # get current scenario index
        idx = self.list_widget_scenario.currentRow()
        # check if it is not scenarios exists and not the last one is selected (The last one can not be deleted)
        if idx > 0 or (len(self.list_ds) > 1 and idx == 0):
            self.list_ds[idx].close_figures()
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
        number: int = len(self.list_ds)
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
        if not self.check_values():
            return
        # add scenario if no list of scenarios exits else save current scenario
        self.add_scenario() if not self.list_ds else self.save_scenario()
        if self.list_widget_scenario.currentItem().text()[-1] == '*':
            return
        # create list of threads with scenarios that have not been calculated
        self.threads = [CalcProblem(DS, idx) for idx, DS in enumerate(self.list_ds) if DS.borefield is None]
        # set number of to calculate scenarios
        self.NumberOfScenarios: int = len(self.threads)
        if self.NumberOfScenarios < 1:
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
        # start calculation if at least one scenario has to be calculated
        if self.NumberOfScenarios > 0:
            self.threads[0].start()
            self.threads[0].any_signal.connect(self.thread_function)
            return

    def start_current_scenario_calculation(self, no_run: bool = False) -> None:
        """
        start calculation of selected scenario
        :return: None
        """
        if not self.check_values():
            return
        # add scenario if no list of scenarios exits else save current scenario
        self.add_scenario() if not self.list_ds else self.save_scenario()
        if self.list_widget_scenario.currentItem().text()[-1] == '*':
            return
        # get index of selected scenario
        idx: int = self.list_widget_scenario.currentRow()
        # get Datastorage of selected scenario
        ds: DataStorage = self.list_ds[idx]
        # if calculation is already done just show results
        if ds.borefield is not None:
            self.gui_structure.page_result.button.click()
            return
        # return to thermal demands page if no file is selected
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
        # create list of threads with calculation to be made
        self.threads = [CalcProblem(ds, idx)]
        # set number of to calculate scenarios
        self.NumberOfScenarios: int = len(self.threads)
        # start calculation
        if not no_run:
            self.threads[0].start()
            self.threads[0].any_signal.connect(self.thread_function)

    def display_results(self) -> None:
        """
        display results of the current selected scenario
        :return: None
        """
        # hide widgets if no list of scenarios exists and display not calculated text
        def hide_no_result(hide: bool = True):
            if hide or self.list_widget_scenario.currentItem().text()[-1] == "*":
                for cat in self.gui_structure.page_result.list_categories:
                    cat.hide(results=True)
                self.gui_structure.cat_no_result.show()
                self.gui_structure.text_no_result.set_text(self.translations.NotCalculated[self.gui_structure.option_language.get_value()])
                return
            for cat in self.gui_structure.page_result.list_categories:
                cat.show(results=True)
            self.gui_structure.cat_no_result.hide()

        if not self.list_ds:
            hide_no_result(True)
            return

        # get Datastorage of selected scenario
        ds: DataStorage = self.list_ds[self.list_widget_scenario.currentRow()]
        # get borefield of selected scenario
        borefield: Borefield = ds.borefield

        # set debug message
        if ds.debug_message != "":
            hide_no_result(True)
            self.gui_structure.text_no_result.set_text(str(ds.debug_message))
            return

        # hide widgets if no results borefield exists and display not calculated text
        if borefield is None:
            hide_no_result(True)
            return

        # no errors, so proceed with showing the results
        hide_no_result(False)
        # create figure for every ResultFigure object
        for fig_obj, fig_name in self.gui_structure.list_of_result_figures:

            if fig_obj.is_hidden():
                continue

            fig = getattr(ds, fig_name)
            if fig is None:
                # create axes and drawing
                fig, ax_new = getattr(borefield, fig_obj.function_name)(**fig_obj.kwargs)
                fig_obj.replace_figure(fig)
                # show everything
                fig_obj.show()
                fig_obj.canvas.show()
                # draw new plot
                fig_obj.canvas.draw()
                # set figure to canvas figure
                continue
            fig_obj.replace_figure(fig)
            # show everything
            fig_obj.show()
            fig_obj.canvas.show()
            # draw new plot
            fig_obj.canvas.draw()

        # update result for every ResultText object
        for result_text_obj, result_text_name in self.gui_structure.list_of_result_texts:
            if not result_text_obj.is_hidden():
                text = borefield.__getattribute__(result_text_obj.var_name)  # currently only borefield
                if callable(text):
                    text = getattr(borefield, result_text_obj.var_name)()
                result_text_obj.set_text_value(text)

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
        msg: QtW.QMessageBox = QtW.QMessageBox(self.Dia)
        # set Icon to question mark icon
        msg.setIcon(QtW.QMessageBox.Question)
        # set label text to cancel text depending on language selected
        msg.setText(self.translations.label_CancelText[self.gui_structure.option_language.get_value()])
        # set window text to cancel text depending on language selected
        msg.setWindowTitle(self.translations.label_CancelTitle[self.gui_structure.option_language.get_value()])
        # set standard buttons to save, close and cancel
        msg.setStandardButtons(QtW.QMessageBox.Save | QtW.QMessageBox.Close | QtW.QMessageBox.Cancel)
        # get save, close and cancel button
        button_s = msg.button(QtW.QMessageBox.Save)
        button_cl = msg.button(QtW.QMessageBox.Close)
        button_ca = msg.button(QtW.QMessageBox.Cancel)
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
        if reply == QtW.QMessageBox.Cancel:
            # cancel closing event
            event.ignore()
            return
        # check if inputs should be saved and if successfully set closing variable to true
        close: bool = self.fun_save() if reply == QtW.QMessageBox.Save else True
        # stop all calculation threads
        [i.terminate() for i in self.threads]
        # close window if close variable is true else not
        event.accept() if close else event.ignore()
