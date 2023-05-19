"""
This file contains the code for the hourly geothermal load data.
"""

import numpy as np
import pandas as pd

from typing import Union
from GHEtool.VariableClasses.LoadData._LoadData import _LoadData
from GHEtool.logger import ghe_logger


class HourlyGeothermalLoad(_LoadData):
    """
        This class contains all the information for geothermal load data with a monthly resolution and absolute input.
        This means that the inputs are both in kWh/month and kW/month.
        """

    __slots__ = tuple(_LoadData.__slots__) + ('_heating_load', '_cooling_load')

    # define parameters for conversion to monthly loads
    START = pd.to_datetime("2019-01-01 00:00:00")
    END = pd.to_datetime("2019-12-31 23:59:00")
    HOURS_SERIES = pd.Series(pd.date_range(START, END, freq="1H"))

    def __init__(self, heating_load: Union[np.ndarray, list, tuple] = np.zeros(8760),
                 cooling_load: Union[np.ndarray, list, tuple] = np.zeros(8760),
                 simulation_period: int = 20):
        """

        Parameters
        ----------
        heating_load : np.ndarray, list, tuple
            Heating load [kWh/h]
        cooling_load : np.ndarray, list, tuple
            Cooling load [kWh/h]
        simulation_period : int
            Length of the simulation period in years
        """

        super().__init__(hourly_resolution=True, simulation_period=simulation_period)

        # initiate variables
        self._hourly_heating_load: np.ndarray = np.zeros(8760)
        self._hourly_cooling_load: np.ndarray = np.zeros(8760)

        # set variables
        self.hourly_heating_load = heating_load
        self.hourly_cooling_load = cooling_load

    def _check_input(self, input: Union[np.ndarray, list, tuple]) -> bool:
        """
        This function checks whether the input is valid or not.
        The input is correct if and only if:
        1) the input is a np.ndarray, list or tuple
        2) the length of the input is 8760
        3) the input does not contain any negative values.

        Parameters
        ----------
        input : np.ndarray, list or tuple

        Returns
        -------
        bool
            True if the inputs are valid
        """
        if not isinstance(input, (np.ndarray, list, tuple)):
            ghe_logger.error("The load should be of type np.ndarray, list or tuple.")
            return False
        if not len(input) == 8760:
            ghe_logger.error("The length of the load should be 12.")
            return False
        if np.min(input) < 0:
            ghe_logger.error("No value in the load can be smaller than zero.")
            return False
        return True

    @property
    def hourly_heating_load(self) -> np.ndarray:
        """
        This function returns the hourly heating load in kWh/h.

        Returns
        -------
        hourly heating : np.ndarray
            Hourly heating values [kWh/h] for one year, so the length of the array is 8760
        """
        return self._hourly_heating_load

    @hourly_heating_load.setter
    def hourly_heating_load(self, load: Union[np.ndarray, list, tuple]) -> None:
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

    def set_hourly_heating(self, load: Union[np.ndarray, list, tuple]) -> None:
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
            When either the length is not 12, the input is not of the correct type, or it contains negative
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
        return self._hourly_cooling_load

    @hourly_cooling_load.setter
    def hourly_cooling_load(self, load: Union[np.ndarray, list, tuple]) -> None:
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

    def set_hourly_cooling(self, load: Union[np.ndarray, list, tuple]) -> None:
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
            When either the length is not 12, the input is not of the correct type, or it contains negative
            values
        """
        self.hourly_cooling_load = load

    @property
    def imbalance(self) -> float:
        """
        This function calculates the ground imbalance.
        A positive imbalance means that the field is injection dominated, i.e. it heats up every year.

        Returns
        -------
        imbalance : float
        """
        return np.sum(self.hourly_cooling_load - self.hourly_heating_load)

    @staticmethod
    def resample_to_monthly(hourly_load: np.ndarray, peak: bool = False) -> np.ndarray:
        """
        This function resamples an hourly_load to either monthly peaks (kW/month) or baseloads (kWh/month).

        Parameters
        ----------
        hourly_load : np.ndarray
            Hourly loads in kWh/h
        peak : bool
            True if the resampling is to peak loads, otherwise it is in baseloads

        Returns
        -------
        monthly loads : np.ndarray
            Either peak loads or baseloads
        """
        # create dataframe
        df = pd.DataFrame(hourly_load, index=HourlyGeothermalLoad.HOURS_SERIES, columns=['load'])

        # resample
        if peak:
            df = df.resample('M').agg({'load': 'max'})
        else:
            df = df.resample('M').agg({'load': 'sum'})

        return df['load']

    @property
    def baseload_cooling(self) -> np.ndarray:
        """
        This function returns the baseload cooling in kWh/month.

        Returns
        -------
        baseload cooling : np.ndarray
            Baseload cooling values [kWh/month] for one year, so the length of the array is 12
        """
        return self.resample_to_monthly(self.hourly_cooling_load, peak=False)

    @property
    def baseload_heating(self) -> np.ndarray:
        """
        This function returns the baseload heating in kWh/month.

        Returns
        -------
        baseload heating : np.ndarray
            Baseload heating values [kWh/month] for one year, so the length of the array is 12
        """
        return self.resample_to_monthly(self.hourly_heating_load, peak=False)

    @property
    def peak_cooling(self) -> np.ndarray:
        """
        This function returns the peak cooling load in kW/month.

        Returns
        -------
        peak cooling : np.ndarray
            Peak cooling values for one year, so the length of the array is 12
        """
        return self.resample_to_monthly(self.hourly_cooling_load, peak=True)

    @property
    def peak_heating(self) -> np.ndarray:
        """
        This function returns the peak heating load in kW/month.

        Returns
        -------
        peak heating : np.ndarray
            Peak heating values for one year, so the length of the array is 12
        """
        return self.resample_to_monthly(self.hourly_heating_load, peak=True)

    @property
    def hourly_cooling_simulation_period(self) -> np.ndarray:
        """
        This function returns the hourly cooling in kWh/h for a whole simulation period.

        Returns
        -------
        hourly cooling : np.ndarray
            hourly cooling for the whole simulation period
        """
        return np.tile(self.hourly_cooling_load)

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

    def load_hourly_profile(self, file_path: str, header: bool = True, separator: str = ";",
                            decimal_seperator: str = ".", first_column_heating: bool = True) -> None:
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
        first_column_heating : bool
            True if the first column in the file is for the heating load

        Returns
        -------
        None
        """
        if header:
            header: int = 0
        else:
            header = None

        # import data
        if first_column_heating:
            df = pd.read_csv(file_path, sep=separator, header=header, decimal=decimal_seperator,
                             usecols=['heating', 'cooling'])
        else:
            df = pd.read_csv(file_path, sep=separator, header=header, decimal=decimal_seperator,
                             usecols=['cooling', 'heating'])

        # set data
        self.hourly_heating_load = df['heating']
        self.hourly_cooling_load = df['cooling']

        ghe_logger.info("Hourly profile loaded!")

