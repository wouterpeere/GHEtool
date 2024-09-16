import warnings

import numpy as np

from GHEtool.VariableClasses.Efficiency import *
from GHEtool.VariableClasses.LoadData.Baseclasses import _LoadDataBuilding
from GHEtool.VariableClasses.Result import ResultsMonthly, ResultsHourly

from numpy.typing import ArrayLike
from typing import Union


class MonthlyBuildingLoadMultiYear(_LoadDataBuilding):
    """
    This class contains all the information for building load data with a monthly resolution and absolute input.
    This means that the inputs are both in kWh/month and kW/month.
    """

    def __init__(
            self,
            baseload_heating: ArrayLike = None,
            baseload_cooling: ArrayLike = None,
            peak_heating: ArrayLike = None,
            peak_cooling: ArrayLike = None,
            efficiency_heating: Union[int, float, COP, SCOP] = 5,
            efficiency_cooling: Union[int, float, EER, SEER, EERCombined] = 20,
            dhw: Union[float, np.ndarray] = None,
            efficiency_dhw: Union[int, float, COP, SCOP] = 4
    ):
        """

        Parameters
        ----------
        baseload_heating : np.ndarray, list, tuple
            Baseload heating values [kWh/month]
        baseload_cooling : np.ndarray, list, tuple
            Baseload cooling values [kWh/month]
        peak_heating : np.ndarray, list, tuple
            Peak heating values [kW/month]
        peak_cooling : np.ndarray, list, tuple
            Peak cooling values [kW/month]
        efficiency_heating : int, float, COP, SCOP
            Efficiency in heating
        efficiency_cooling : int, float, EER, SEER
            Efficiency in cooling
        dhw : float, np.ndarray
            Yearly value of array with energy demand for domestic hot water (DHW) [kWh]
        efficiency_dhw : int, float, COP, SCOP,
            Efficiency in DHW
        """

        _LoadDataBuilding.__init__(self, efficiency_heating, efficiency_cooling, dhw, efficiency_dhw, True)
        self._multiyear = True

        # initiate variables
        self._baseload_heating: np.ndarray = np.zeros(12)
        self._baseload_cooling: np.ndarray = np.zeros(12)
        self._peak_heating: np.ndarray = np.zeros(12)
        self._peak_cooling: np.ndarray = np.zeros(12)

        # set variables
        self.baseload_heating = np.zeros(12) if baseload_heating is None else baseload_heating
        self.baseload_cooling = np.zeros(12) if baseload_cooling is None else baseload_cooling
        self.peak_heating = np.zeros(12) if peak_heating is None else peak_heating
        self.peak_cooling = np.zeros(12) if peak_cooling is None else peak_cooling

    @property
    def monthly_baseload_cooling_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly cooling baseload in kWh/month for the whole simulation period.

        Returns
        -------
        baseload cooling : np.ndarray
            baseload cooling for the whole simulation period
        """
        return self.baseload_cooling

    @property
    def monthly_baseload_heating_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly heating baseload in kWh/month for the whole simulation period.

        Returns
        -------
        baseload heating : np.ndarray
            baseload heating for the whole simulation period
        """
        return self.baseload_heating

    @property
    def monthly_peak_cooling_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly cooling peak in kW/month for the whole simulation period.

        Returns
        -------
        peak cooling : np.ndarray
            peak cooling for the whole simulation period
        """
        return self.peak_cooling

    @property
    def monthly_peak_heating_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly heating peak in kW/month for the whole simulation period.

        Returns
        -------
        peak heating : np.ndarray
            peak heating for the whole simulation period
        """
        return self.peak_heating

    @property
    def baseload_cooling(self) -> np.ndarray:
        """
        This function returns the baseload cooling in kWh/month for the whole simulation period.

        Returns
        -------
        baseload cooling : np.ndarray
            Baseload cooling values [kWh/month] for all years
        """
        return self._baseload_cooling

    @baseload_cooling.setter
    def baseload_cooling(self, load: ArrayLike) -> None:
        """
        This function sets the baseload cooling [kWh/month] after it has been checked.
        If the baseload cooling gives a higher average power than the peak power,
        this is taken as the peak power in that month.

        Parameters
        ----------
        load : np.ndarray, list or tuple
            Baseload cooling [kWh/month]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When either the length is not a multiple of 12 , the input is not of the correct type, or it contains negative
            values
        """
        if self._check_input(load):
            self._baseload_cooling = np.array(load)
            return
        raise ValueError

    @property
    def baseload_heating(self) -> np.ndarray:
        """
        This function returns the baseload heating in kWh/month for the whole simulation period.

        Returns
        -------
        baseload heating : np.ndarray
            Baseload heating values [kWh/month] for all years
        """
        return self._baseload_heating

    @baseload_heating.setter
    def baseload_heating(self, load: ArrayLike) -> None:
        """
        This function sets the baseload heating [kWh/month] after it has been checked.
        If the baseload heating gives a higher average power than the peak power,
        this is taken as the peak power in that month.

        Parameters
        ----------
        load : np.ndarray, list or tuple
            Baseload heating [kWh/month]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When either the length is not a multiple of 12, the input is not of the correct type, or it contains
            negative values
        """
        if self._check_input(load):
            self._baseload_heating = np.array(load)
            return
        raise ValueError

    @property
    def peak_cooling(self) -> np.ndarray:
        """
        This function returns the peak cooling load in kW/month for the whole simulation period.

        Returns
        -------
        peak cooling : np.ndarray
            Peak cooling values for all years
        """
        return self._peak_cooling

    @peak_cooling.setter
    def peak_cooling(self, load) -> None:
        """
        This function sets the peak cooling load [kW/month] after it has been checked.
        If the baseload cooling gives a higher average power, this is taken as the peak power in that month.

        Parameters
        ----------
        load : np.ndarray, list or tuple
            Peak cooling load [kW/month]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When either the length is not a multiple of 12, the input is not of the correct type, or it contains
            negative values
        """
        if self._check_input(load):
            self._peak_cooling = np.array(load)
            return
        raise ValueError

    @property
    def peak_heating(self) -> np.ndarray:
        """
        This function returns the peak heating load in kW/month for the whole simulation period.

        Returns
        -------
        peak heating : np.ndarray
            Peak heating values for all years
        """
        return self._peak_heating

    @peak_heating.setter
    def peak_heating(self, load: ArrayLike) -> None:
        """
        This function sets the peak heating load [kW/month] after it has been checked.
        If the baseload heating gives a higher average power, this is taken as the peak power in that month.

        Parameters
        ----------
        load : np.ndarray, list or tuple
            Peak heating load [kW/month]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When either the length is not a multiple of 12, the input is not of the correct type, or it contains
            negative values
        """
        if self._check_input(load):
            self._peak_heating = np.array(load)
            return
        raise ValueError

    @property
    def monthly_baseload_dhw_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly domestic hot water baseload in kWh/month for the whole simulation period.

        Returns
        -------
        baseload domestic hot water : np.ndarray
            Baseload domestic hot water for the whole simulation period
        """
        if self._dhw is None:
            return np.zeros(12 * self.simulation_period)
        return self._dhw

    def set_results(self, results: ResultsMonthly) -> None:
        """
        This function sets the temperature results.

        Parameters
        ----------
        results : ResultsMonthly
            Results object

        Raises
        ------
        ValueError
            If the simulation period of the results do not match the simulation period of the load data.
            If a ResultHourly was given as result argument.

        Returns
        -------
        None
        """
        if isinstance(results, ResultsHourly):
            raise ValueError('You cannot use an hourly result class for a monthly load class.')
        if len(results.Tb) != self.simulation_period * 12:
            raise ValueError(
                f'The results have a length of {len(results.Tb)} whereas, with a simulation period of {self.simulation_period} years '
                f'a length of {self.simulation_period * (8760 if self._hourly else 12)} was expected.')
        self._results = results
