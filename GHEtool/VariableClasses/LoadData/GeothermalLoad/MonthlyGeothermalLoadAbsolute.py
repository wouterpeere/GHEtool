"""
This file contains the code for the monthly geothermal load data where the load is given in kWh and kW per month.
"""
import numpy as np

from GHEtool.VariableClasses.LoadData._LoadData import _LoadData
from GHEtool.logger.ghe_logger import ghe_logger


class MonthlyGeothermalLoadAbsolute(_LoadData):
    """
    This class contains all the information for geothermal load data with a monthly resolution and absolute input.
    This means that the inputs are both in kWh/month and kW/month.
    """

    __slots__ = _LoadData.__slots__ + ('_baseload_heating', '_baseload_cooling', '_peak_heating', '_peak_cooling')

    def __init__(self, baseload_heating: np.array | list | tuple = np.zeros(12),
                 baseload_cooling: np.array | list | tuple = np.zeros(12),
                 peak_heating: np.array | list | tuple = np.zeros(12),
                 peak_cooling: np.array | list | tuple = np.zeros(12)):
        """

        Parameters
        ----------
        baseload_heating : np.array, list, tuple
            Baseload heating values [kWh/month]
        baseload_cooling : np.array, list, tuple
            Baseload cooling values [kWh/month]
        peak_heating : np.array, list, tuple
            Peak heating values [kW/month]
        peak_cooling : np.array, list, tuple
            Peak cooling values [kW/month]
        """

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

    def _check_input(self, input: np.array | list | tuple) -> bool:
        """
        This function checks whether the input is valid or not.
        The input is correct if and only if:
        1) the input is a np.array, list or tuple
        2) the length of the input is 12
        3) the input does not contain any negative values.

        Parameters
        ----------
        input : np.array, list or tuple

        Returns
        -------
        bool
            True if the inputs are valid
        """
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
        """
        This function returns the baseload cooling in kWh/month.

        Returns
        -------
        baseload cooling : np.array
            Baseload cooling values for one year, so the length of the array is 12
        """
        return self._baseload_cooling

    @baseload_cooling.setter
    def baseload_cooling(self, load: np.array | list | tuple) -> None:
        """
        This function sets the baseload cooling [kWh/month] after it has been checked.

        Parameters
        ----------
        load : np.array, list or tuple
            Baseload cooling [kWh/month]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When either the length is not 12, the input is not of the correct type, or it contains negative
            values
        """
        if self._check_input(load):
            self._baseload_cooling = load
            return
        raise ValueError

    def set_baseload_cooling(self, load: np.array | list | tuple) -> None:
        """
        This function sets the baseload cooling [kWh/month] after it has been checked.

        Parameters
        ----------
        load : np.array, list or tuple
            Baseload cooling [kWh/month]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When either the length is not 12, the input is not of the correct type, or it contains negative
            values
        """
        self.baseload_cooling = load

    @property
    def baseload_heating(self) -> np.array:
        """
        This function returns the baseload heating in kWh/month.

        Returns
        -------
        baseload heating : np.array
            Baseload heating values for one year, so the length of the array is 12
        """
        return self._baseload_heating

    @baseload_heating.setter
    def baseload_heating(self, load: np.array | list | tuple) -> None:
        """
        This function sets the baseload heating [kWh/month] after it has been checked.

        Parameters
        ----------
        load : np.array, list or tuple
            Baseload heating [kWh/month]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When either the length is not 12, the input is not of the correct type, or it contains negative
            values
        """
        if self._check_input(load):
            self._baseload_heating = load
            return
        raise ValueError

    def set_baseload_heating(self, load: np.array | list | tuple) -> None:
        """
        This function sets the baseload heating [kWh/month] after it has been checked.

        Parameters
        ----------
        load : np.array, list or tuple
            Baseload heating [kWh/month]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When either the length is not 12, the input is not of the correct type, or it contains negative
            values
        """
        self.baseload_heating = load

    @property
    def peak_cooling(self) -> np.array:
        """
        This function returns the peak cooling load in kW/month.

        Returns
        -------
        peak cooling : np.array
            Peak cooling values for one year, so the length of the array is 12
        """
        return self._peak_cooling

    @peak_cooling.setter
    def peak_cooling(self, load) -> None:
        """
        This function sets the peak cooling load [kW/month] after it has been checked.

        Parameters
        ----------
        load : np.array, list or tuple
            Peak cooling load [kW/month]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When either the length is not 12, the input is not of the correct type, or it contains negative
            values
        """
        if self._check_input(load):
            self._peak_cooling = load
            return
        raise ValueError

    def set_peak_cooling(self, load: np.array | list | tuple) -> None:
        """
        This function sets the peak cooling load [kW/month] after it has been checked.

        Parameters
        ----------
        load : np.array, list or tuple
            Peak cooling load [kW/month]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When either the length is not 12, the input is not of the correct type, or it contains negative
            values
        """
        self.peak_cooling = load

    @property
    def peak_heating(self) -> np.array:
        """
        This function returns the peak heating load in kW/month.

        Returns
        -------
        peak heating : np.array
            Peak heating values for one year, so the length of the array is 12
        """
        return self._peak_heating

    @peak_heating.setter
    def peak_heating(self, load: np.array | list | tuple) -> None:
        """
        This function sets the peak heating load [kW/month] after it has been checked.

        Parameters
        ----------
        load : np.array, list or tuple
            Peak heating load [kW/month]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When either the length is not 12, the input is not of the correct type, or it contains negative
            values
        """
        if self._check_input(load):
            self._peak_heating = load
            return
        raise ValueError

    def set_peak_heating(self, load: np.array | list | tuple) -> None:
        """
        This function sets the peak heating load [kW/month] after it has been checked.

        Parameters
        ----------
        load : np.array, list or tuple
            Peak heating load [kW/month]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When either the length is not 12, the input is not of the correct type, or it contains negative
            values
        """
        self.peak_heating = load