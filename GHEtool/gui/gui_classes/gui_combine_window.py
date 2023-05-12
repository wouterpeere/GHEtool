from __future__ import annotations

import logging
import pathlib
from configparser import ConfigParser
from json import JSONDecodeError, load
from os.path import dirname, realpath
from pickle import load as pk_load
from sys import path

from GHEtool import Borefield
from ScenarioGUI import MainWindow
from ScenarioGUI.gui_classes.gui_data_storage import DataStorage

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
            return
            # raise ImportError("The datafile cannot be loaded!")
        except (JSONDecodeError, UnicodeDecodeError):
            # try to open as pickle
            import GHEtool
            from ScenarioGUI.gui_classes import gui_data_storage
            GHEtool.gui.gui_data_storage = gui_data_storage
            from GHEtool import GroundConstantTemperature
            class BoreFieldNew:
                """nothing"""

            BorefielOld = Borefield
            GHEtool.VariableClasses.VariableClasses.GroundData = GroundConstantTemperature
            GHEtool.gui.gui_data_storage.DataStorage = gui_data_storage.DataStorage
            GHEtool.main_class.Borefield = BoreFieldNew
            with open(location, "rb") as file:
                saving = pk_load(file)
            GHEtool.main_class.Borefield = BorefielOld
            version = "2.1.0"

        if version == "2.2.0":
            # write data to variables
            self.list_ds = []
            for val, borefield in zip(saving['values'], saving['results']):
                ds = DataStorage(self.gui_structure)
                ds.from_dict(val)
                if borefield is None:
                    ds.results = None
                else:
                    ds.results = Borefield()
                    ds.results.from_dict(borefield)
                self.list_ds.append(ds)
            # set and change the window title
            self.filename = saving['filename']
            general_changes(saving['names'])
            return

        if version in ["2.1.1", "2.1.2"]:
            # write data to variables
            self.list_ds = []
            for val, borefield in zip(saving['values'], saving['borefields']):
                ds = DataStorage(self.gui_structure)
                ds.from_dict(val)
                if borefield is None:  # pragma: no cover
                    setattr(ds, 'results', None)
                else:
                    borefield["ground_data"]["__module__"] = "GHEtool.VariableClasses.GroundData.GroundFluxTemperature"
                    borefield["ground_data"]["__name__"] = "GroundFluxTemperature"
                    setattr(ds, 'results', Borefield())
                    getattr(ds, 'results').from_dict(borefield)
                    ds.results.set_Rb(borefield["ground_data"]["Rb"])
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
            for ds in self.list_ds:
                setattr(ds, 'borefield', None)

            # convert to new ds format
            for idx, ds in enumerate(self.list_ds):
                ds_new = DataStorage(gui_structure=self.gui_structure)
                [setattr(ds_new, name, getattr(ds, name)) for name in ds.__dict__ if hasattr(ds_new, name)]
                self.list_ds[idx] = ds_new
            # write scenario names
            general_changes(li)