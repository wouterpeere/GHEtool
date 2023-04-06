"""
This file contains the code for the monthly geothermal load data where the load is given in kWh and kW per month.
"""
import numpy as np

from GHEtool.VariableClasses.LoadData._LoadData import _LoadData
from GHEtool.logger.ghe_logger import ghe_logger


class MonthlyGeothermalLoadAbsolute(_LoadData):

    def __init__(self, baseload_heating, baseload_cooling, peak_heating, peak_cooling):

        super().__init__(hourly_resolution=False)

        # initiate variables
        self._baseload_heating: np.array = np.zeros(12)
        self._baseload_cooling: np.array = np.zeros(12)
        self._peak_heating: np.array = np.zeros(12)
        self._peak_cooling: np.array = np.zeros(12)

        # set variables
        self.baseload_heating = baseload_heating
        self.baseload_cooling = baseload_cooling
        self.peak_heating = peak_heating
        self.peak_cooling = peak_cooling

    def _check_input(self, input) -> bool:
        if not isinstance(input, (np.array, list, tuple)):
            ghe_logger.error("The load should be of type np.array, list or tuple.")
            return False
        if not len(input) == 12:
            ghe_logger.error("The length of the load should be 12.")
            return False
        if np.min(input) < 0:
            ghe_logger("No value in the load can be smaller than zero.")
            return False

    @property
    def baseload_cooling(self) -> np.array:
        return self._baseload_cooling

    @baseload_cooling.setter
    def baseload_cooling(self, load: np.array | list | tuple) -> None:
        if self._check_input(load):
            self._baseload_cooling = load
            return
        raise ValueError

    @property
    def baseload_heating(self) -> np.array:
        return self._baseload_heating

    @baseload_heating.setter
    def baseload_heating(self, load) -> None:
        if self._check_input(load):
            self._baseload_heating = load
            return
        raise ValueError

    @property
    def peak_cooling(self) -> np.array:
        return self._peak_cooling

    @peak_cooling.setter
    def peak_cooling(self, load) -> None:
        if self._check_input(load):
            self._peak_cooling = load
            return
        raise ValueError

    @property
    def peak_heating(self) -> np.array:
        return self._peak_heating

    @peak_heating.setter
    def peak_heating(self, load) -> None:
        if self._check_input(load):
            self._peak_heating = load
            return
        raise ValueError
