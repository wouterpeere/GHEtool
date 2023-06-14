from __future__ import annotations

import logging
import pathlib
from configparser import ConfigParser
from json import JSONDecodeError, load, dump
from os.path import dirname, realpath
from pathlib import PurePath
from pickle import load as pk_load
from sys import path

from GHEtool import Borefield
from ScenarioGUI import MainWindow
from ScenarioGUI.gui_classes.gui_data_storage import DataStorage
import ScenarioGUI.global_settings as globs

currentdir = dirname(realpath(__file__))
parentdir = dirname(currentdir)
path.append(parentdir)

BACKUP_FILENAME: str = 'backup.GHEtoolBackUp'


# main GUI class
class MainWindow(MainWindow):
    """
    This class contains the general functionalities of the GUI (e.g. the handling of creating new scenarios,
    saving documents etc.)
    """

    def _load_from_data(self, location: str) -> bool:
        """
        This function loads the data from a JSON formatted file.

        Parameters
        ----------
        location : str
            Location of the data file

        Returns
        -------
        True if it is loaded, False otherwise
        """

        def general_changes(scenarios):
            # change window title to new loaded filename
            self.change_window_title()
            # init user window by reset scenario list widget and check for results
            self.list_widget_scenario.clear()
            self.list_widget_scenario.addItems(scenarios)
            self.change_scenario(0)
            self.list_widget_scenario.setCurrentRow(0)
            self.check_results()

        try:
            # open file and get data
            with open(location) as file:
                saving = load(file)

            version = saving['version']
        except FileNotFoundError:
            logging.info(self.translations.no_file_selected[self.gui_structure.option_language.get_value()[0]])
            return False
            # raise ImportError("The datafile cannot be loaded!")
        except (JSONDecodeError, UnicodeDecodeError):
            # try to open as pickle
            globs.LOGGER.warning('One cannot open a GHEtool v2.1.0')
            return False

        if version == "2.2.0":
            # write data to variables
            self.list_ds = []
            for val in saving['values']:
                ds = DataStorage(self.gui_structure)
                ds.from_dict(val)
                ds.results = None
                self.list_ds.append(ds)
            # set and change the window title
            self.filename = saving['filename']
            general_changes(saving['names'])
            return True

        if version in ["2.1.1", "2.1.2"]:
            # write data to variables
            self.list_ds = []
            for val, borefield in zip(saving['values'], saving['borefields']):
                ds = DataStorage(self.gui_structure)
                ds.from_dict(val)
                ds.results = None
                self.list_ds.append(ds)

            # set and change the window title
            self.filename = saving['filename']
            general_changes(saving['names'])
            return True

    def _save_to_data(self, location: str | PurePath) -> bool:
        """
        This function saves the gui data to a json formatted file.

        Parameters
        ----------
        location : str
            Location of the data file.

        Returns
        -------
        bool
            True if it was saved succesfully
        """
        # create list of all scenario names
        scenario_names = [self.list_widget_scenario.item(idx).text() for idx in range(self.list_widget_scenario.count())]
        # create saving dict
        saving = {
            "filename": self.filename,
            "names": scenario_names,
            "version": globs.VERSION,
            "values": [ds.to_dict() for ds in self.list_ds]
        }
        try:
            # write data to back up file
            with open(location, "w") as file:
                dump(saving, file, indent=1)
            assert False
            return True
        except FileNotFoundError:
            globs.LOGGER.error(self.translations.no_file_selected[self.gui_structure.option_language.get_value()[0]])
            return False
        except PermissionError:  # pragma: no cover
            globs.LOGGER.error("PermissionError")
            return False
