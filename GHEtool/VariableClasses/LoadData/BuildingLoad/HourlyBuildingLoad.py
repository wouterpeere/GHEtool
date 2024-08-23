from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import warnings

from typing import Tuple, TYPE_CHECKING, Union

from GHEtool.VariableClasses.Efficiency import *
from GHEtool.VariableClasses.LoadData.Baseclasses import _SingleYear, _HourlyDataBuilding

if TYPE_CHECKING:
    from numpy.typing import ArrayLike


class HourlyBuildingLoad(_SingleYear, _HourlyDataBuilding):
    """
    This class contains all the information for building load data with an hourly resolution.
    """

    def __init__(self, heating_load: ArrayLike = None,
                 cooling_load: ArrayLike = None,
                 simulation_period: int = 20,
                 efficiency_heating: Union[int, float, COP, SCOP] = 5,
                 efficiency_cooling: Union[int, float, EER, SEER] = 20,
                 dhw: Union[float, np.ndarray] = None,
                 efficiency_dhw: Union[int, float, COP, SCOP] = 4):
        """

        Parameters
        ----------
        heating_load : np.ndarray, list, tuple
            Heating load [kWh/h]
        cooling_load : np.ndarray, list, tuple
            Cooling load [kWh/h]
        simulation_period : int
            Length of the simulation period in years
        efficiency_heating : int, float, COP, SCOP
            Efficiency in heating
        efficiency_cooling : int, float, EER, SEER
            Efficiency in cooling
        dhw : float, np.ndarray
            Yearly value of array with energy demand for domestic hot water (DHW) [kWh]
        efficiency_dhw : int, float, COP, SCOP,
            Efficiency in DHW
        """

        _HourlyDataBuilding.__init__(self, efficiency_heating, efficiency_cooling, dhw, efficiency_dhw)
        _SingleYear.__init__(self, simulation_period)
        self._hourly = True

        # initiate variables
        self._hourly_heating_load: np.ndarray = np.zeros(8760)
        self._hourly_cooling_load: np.ndarray = np.zeros(8760)

        # set variables
        self.hourly_heating_load: np.ndarray = np.zeros(8760) if heating_load is None else np.array(
            heating_load)
        self.hourly_cooling_load: np.ndarray = np.zeros(8760) if cooling_load is None else np.array(cooling_load)

    @property
    def hourly_heating_load(self) -> np.ndarray:
        """
        This function returns the hourly heating load in kWh/h including DHW.

        Returns
        -------
        hourly heating : np.ndarray
            Hourly heating values (incl. DHW) [kWh/h] for one year, so the length of the array is 8760
        """
        return self.correct_for_start_month(self._hourly_heating_load)

    @hourly_heating_load.setter
    def hourly_heating_load(self, load: ArrayLike) -> None:
        """
        This function sets the hourly heating load [kWh/h] after it has been checked.

        Parameters
        ----------
        load : np.ndarray, list or tuple
            Hourly heating [kWh/h]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When either the length is not 8760, the input is not of the correct type, or it contains negative
            values
        """
        if self._check_input(load):
            self._hourly_heating_load = load
            return
        raise ValueError

    def set_hourly_heating_load(self, load: ArrayLike) -> None:
        """
        This function sets the hourly heating load [kWh/h] after it has been checked.

        Parameters
        ----------
        load : np.ndarray, list or tuple
            Hourly heating [kWh/h]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When either the length is not 8760, the input is not of the correct type, or it contains negative
            values
        """
        self.hourly_heating_load = load

    @property
    def hourly_cooling_load(self) -> np.ndarray:
        """
        This function returns the hourly cooling load in kWh/h.

        Returns
        -------
        hourly cooling : np.ndarray
            Hourly cooling values [kWh/h] for one year, so the length of the array is 8760
        """
        return self.correct_for_start_month(self._hourly_cooling_load)

    @hourly_cooling_load.setter
    def hourly_cooling_load(self, load: ArrayLike) -> None:
        """
        This function sets the hourly cooling load [kWh/h] after it has been checked.

        Parameters
        ----------
        load : np.ndarray, list or tuple
            Hourly cooling [kWh/h]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When either the length is not 8760, the input is not of the correct type, or it contains negative
            values
        """
        if self._check_input(load):
            self._hourly_cooling_load = load
            return
        raise ValueError

    def set_hourly_cooling_load(self, load: ArrayLike) -> None:
        """
        This function sets the hourly cooling load [kWh/h] after it has been checked.

        Parameters
        ----------
        load : np.ndarray, list or tuple
            Hourly cooling [kWh/h]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When either the length is not 8760, the input is not of the correct type, or it contains negative
            values
        """
        self.hourly_cooling_load = load

    @property
    def hourly_cooling_load_simulation_period(self) -> np.ndarray:
        """
        This function returns the hourly cooling in kWh/h for a whole simulation period.

        Returns
        -------
        hourly cooling : np.ndarray
            hourly cooling for the whole simulation period
        """
        return np.tile(self.hourly_cooling_load, self.simulation_period)

    @property
    def hourly_heating_load_simulation_period(self) -> np.ndarray:
        """
        This function returns the hourly heating in kWh/h for a whole simulation period.

        Returns
        -------
        hourly heating : np.ndarray
            hourly heating for the whole simulation period
        """
        return np.tile(self.hourly_heating_load, self.simulation_period)

    @property
    def hourly_dhw_load_simulation_period(self) -> np.ndarray:
        """
        This function returns the hourly DHW load in kWh/h for the whole simulation period.

        Returns
        -------
        hourly DHW : np.ndarray
            Hourly DHW values [kWh/h] for the whole simulation period
        """
        dhw = self._dhw
        if dhw is None:
            dhw = 0.
        if isinstance(dhw, (int, float)):
            temp = dhw / 8760
            return np.tile(temp, self.simulation_period * 8760)
        return np.tile(dhw, self.simulation_period)

    @property
    def _start_hour(self) -> int:
        """
        This function returns the hour at which the year starts based on the start month.

        Returns
        -------
        int
            Start hour of the year
        """
        return int(np.sum([self.UPM[i] for i in range(self.start_month - 1)]))

    def correct_for_start_month(self, array: np.ndarray) -> np.ndarray:
        """
        This function corrects the load for the correct start month.
        If the simulation starts in september, the start month is 9 and hence the array should start
        at index of the first hour of month 9.

        Parameters
        ----------
        array : np.ndarray
            Load array

        Returns
        -------
        load : np.ndarray
        """
        if self.start_month == 1:
            return array
        return np.concatenate((array[self._start_hour:], array[: self._start_hour]))

    @property
    def _time_array(self) -> np.ndarray:
        """
        This property returns the array of all monthly indices for the simulation period.

        Returns
        -------
        time array : np.ndarray
        """
        return np.tile(self.correct_for_start_month(np.repeat(np.arange(1, 13), self.UPM)), self.simulation_period)

    def plot_load_duration(self, legend: bool = False) -> Tuple[plt.Figure, plt.Axes]:
        """
        This function makes a load-duration curve from the hourly values.

        Parameters
        ----------
        legend : bool
            True if the figure should have a legend

        Returns
        ----------
        Tuple
            plt.Figure, plt.Axes
        """
        # sort heating and cooling load
        heating = self.hourly_heating_load.copy()
        heating[::-1].sort()

        cooling = self.hourly_cooling_load.copy()
        cooling[::-1].sort()
        cooling = cooling * (-1)
        # create new figure and axes if it not already exits otherwise clear it.
        fig = plt.figure()
        ax = fig.add_subplot(111)
        # add sorted loads to plot
        ax.step(np.arange(0, 8760, 1), heating, "r-", label="Heating")
        ax.step(np.arange(0, 8760, 1), cooling, "b-", label="Cooling")
        # create 0 line
        ax.hlines(0, 0, 8759, color="black")
        # add labels
        ax.set_xlabel("Time [hours]")
        ax.set_ylabel("Power [kW]")
        # set x limits to 8760
        ax.set_xlim(0, 8760)
        # plot legend if wanted
        if legend:
            ax.legend()  #
        plt.show()
        return fig, ax
