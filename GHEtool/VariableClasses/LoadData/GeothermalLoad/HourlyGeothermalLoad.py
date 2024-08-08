from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import warnings

from typing import Tuple, TYPE_CHECKING

from GHEtool.VariableClasses.LoadData.Baseclasses import _SingleYear, _HourlyData
from GHEtool.logger import ghe_logger

if TYPE_CHECKING:
    from numpy.typing import ArrayLike


class HourlyGeothermalLoad(_SingleYear, _HourlyData):
    """
    This class contains all the information for geothermal load data with a monthly resolution and absolute input.
    This means that the inputs are both in kWh/month and kW/month.
    """

    def __init__(self, extraction_load: ArrayLike = None,
                 injection_load: ArrayLike = None,
                 simulation_period: int = 20,
                 *args,
                 **kwargs):
        """

        Parameters
        ----------
        extraction_load : np.ndarray, list, tuple
            Heating load [kWh/h]
        injection_load : np.ndarray, list, tuple
            Cooling load [kWh/h]
        simulation_period : int
            Length of the simulation period in years
        dhw : float
            Yearly consumption of domestic hot water [kWh/year]
        """
        # check legacy
        if len(args) > 0 or len(kwargs) > 0:
            raise DeprecationWarning(
                'The definition of the HourlyGeothermalLoad class has been changed to injection/extraction terminology instead of cooling/heating terminology. '
                'Support for DHW is also dropped. You can use the HourlyBuildingLoad class with the same definitions instead.')

        _HourlyData.__init__(self)
        _SingleYear.__init__(self, simulation_period)
        self._hourly = True

        # initiate variables
        self._hourly_extraction_load: np.ndarray = np.zeros(8760)
        self._hourly_injection_load: np.ndarray = np.zeros(8760)

        # set variables
        self.hourly_extraction_load: np.ndarray = np.zeros(8760) if extraction_load is None else np.array(
            extraction_load)
        self.hourly_injection_load: np.ndarray = np.zeros(8760) if injection_load is None else np.array(injection_load)

    @property
    def hourly_extraction_load(self) -> np.ndarray:
        """
        This function returns the hourly heating load in kWh/h including DHW.

        Returns
        -------
        hourly heating : np.ndarray
            Hourly heating values (incl. DHW) [kWh/h] for one year, so the length of the array is 8760
        """
        return self.correct_for_start_month(self._hourly_extraction_load)

    @hourly_extraction_load.setter
    def hourly_extraction_load(self, load: ArrayLike) -> None:
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
            self._hourly_extraction_load = load
            return
        raise ValueError

    def set_hourly_extraction_load(self, load: ArrayLike) -> None:
        """
        This function sets the hourly extraction load [kWh/h] after it has been checked.

        Parameters
        ----------
        load : np.ndarray, list or tuple
            Hourly extraction [kWh/h]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When either the length is not 8760, the input is not of the correct type, or it contains negative
            values
        """
        self.hourly_extraction_load = load

    @property
    def hourly_injection_load(self) -> np.ndarray:
        """
        This function returns the hourly cooling load in kWh/h.

        Returns
        -------
        hourly cooling : np.ndarray
            Hourly cooling values [kWh/h] for one year, so the length of the array is 8760
        """
        return self.correct_for_start_month(self._hourly_injection_load)

    @hourly_injection_load.setter
    def hourly_injection_load(self, load: ArrayLike) -> None:
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
            self._hourly_injection_load = load
            return
        raise ValueError

    def set_hourly_injection_load(self, load: ArrayLike) -> None:
        """
        This function sets the hourly injection load [kWh/h] after it has been checked.

        Parameters
        ----------
        load : np.ndarray, list or tuple
            Hourly injection [kWh/h]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When either the length is not 8760, the input is not of the correct type, or it contains negative
            values
        """
        self.hourly_injection_load = load

    @property
    def hourly_injection_load_simulation_period(self) -> np.ndarray:
        """
        This function returns the hourly cooling in kWh/h for a whole simulation period.

        Returns
        -------
        hourly cooling : np.ndarray
            hourly cooling for the whole simulation period
        """
        return np.tile(self.hourly_injection_load, self.simulation_period)

    @property
    def hourly_extraction_load_simulation_period(self) -> np.ndarray:
        """
        This function returns the hourly heating in kWh/h for a whole simulation period.

        Returns
        -------
        hourly heating : np.ndarray
            hourly heating for the whole simulation period
        """
        return np.tile(self.hourly_extraction_load, self.simulation_period)

    def load_hourly_profile(
            self, file_path: str, header: bool = True, separator: str = ";", decimal_seperator: str = ".",
            col_extraction: int = 0, col_injection: int = 1
    ) -> None:
        """
        This function loads in an hourly load profile [kW].

        Parameters
        ----------
        file_path : str
            Path to the hourly load file
        header : bool
            True if this file contains a header row
        separator : str
            Symbol used in the file to separate the columns
        decimal_seperator : str
            Symbol used for the decimal number separation
        col_extraction : int
            Column index for extraction data
        col_injection : int
            Column index for injection data

        Returns
        -------
        None
        """
        if header:
            header: int = 0
        else:
            header = None

        # TODO implement single column
        # if col_extraction == col_injection:
        #     ghe_logger.info('Only one column with data selected. Load will be splitted into heating and cooling load.')

        # import data
        df = pd.read_csv(file_path, sep=separator, header=header, decimal=decimal_seperator)

        # set data
        self.hourly_extraction_load = np.array(df.iloc[:, col_extraction])
        self.hourly_injection_load = np.array(df.iloc[:, col_injection])

        ghe_logger.info("Hourly profile loaded!")

    def __eq__(self, other) -> bool:
        if not isinstance(other, HourlyGeothermalLoad):
            return False
        if not np.array_equal(self.hourly_injection_load, other.hourly_injection_load):
            return False
        if not np.array_equal(self.hourly_extraction_load, other.hourly_extraction_load):
            return False
        if not self.simulation_period == other.simulation_period:
            return False
        return True

    def __add__(self, other):
        if isinstance(other, HourlyGeothermalLoad):
            if self.simulation_period != other.simulation_period:
                warnings.warn(
                    f"The simulation period for both load classes are different. "
                    f"The maximum simulation period of "
                    f"{max(self.simulation_period, other.simulation_period)} years will be taken."
                )
            return HourlyGeothermalLoad(
                self._hourly_extraction_load + other._hourly_extraction_load,
                self._hourly_injection_load + other._hourly_injection_load,
                max(self.simulation_period, other.simulation_period),
            )

        try:
            return other.__add__(self)
        except TypeError:  # pragma: no cover
            raise TypeError("Cannot perform addition. Please check if you use correct classes.")  # pragma: no cover

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
        at index 9.

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
        # sort extraction and cooling load
        extraction = self.hourly_extraction_load.copy()
        extraction[::-1].sort()

        injection = self.hourly_injection_load.copy()
        injection[::-1].sort()
        injection = injection * (-1)
        # create new figure and axes if it not already exits otherwise clear it.
        fig = plt.figure()
        ax = fig.add_subplot(111)
        # add sorted loads to plot
        ax.step(np.arange(0, 8760, 1), extraction, "r-", label="Extraction")
        ax.step(np.arange(0, 8760, 1), injection, "b-", label="Injection")
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
