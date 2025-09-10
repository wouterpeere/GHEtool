import warnings

import numpy as np

from GHEtool.VariableClasses.Efficiency import *
from GHEtool.VariableClasses.LoadData.Baseclasses import _SingleYear, _LoadDataBuilding
from GHEtool.VariableClasses.Result import ResultsMonthly, ResultsHourly

from numpy.typing import ArrayLike
from typing import Union


class MonthlyBuildingLoadAbsolute(_SingleYear, _LoadDataBuilding):
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
            simulation_period: int = 20,
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

        _LoadDataBuilding.__init__(self, efficiency_heating, efficiency_cooling, efficiency_dhw)
        _SingleYear.__init__(self, simulation_period)

        # initiate variables
        self._baseload_heating: np.ndarray = np.zeros(12)
        self._baseload_cooling: np.ndarray = np.zeros(12)
        self._peak_heating: np.ndarray = np.zeros(12)
        self._peak_cooling: np.ndarray = np.zeros(12)
        self._baseload_dhw: np.ndarray = np.zeros(12)
        
        # set variables
        self.baseload_heating = np.zeros(12) if baseload_heating is None else baseload_heating
        self.baseload_cooling = np.zeros(12) if baseload_cooling is None else baseload_cooling
        self.peak_heating = np.zeros(12) if peak_heating is None else peak_heating
        self.peak_cooling = np.zeros(12) if peak_cooling is None else peak_cooling

        self._set_dhw(dhw)

    @property
    def baseload_cooling(self) -> np.ndarray:
        """
        This function returns the baseload cooling in kWh/month.

        Returns
        -------
        baseload cooling : np.ndarray
            Baseload cooling values [kWh/month] for one year, so the length of the array is 12
        """
        return self.correct_for_start_month(self._baseload_cooling)

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
            When either the length is not 12, the input is not of the correct type, or it contains negative
            values
        """
        if self._check_input(load):
            self._baseload_cooling = np.array(load)
            return
        raise ValueError

    def set_baseload_cooling(self, load: ArrayLike) -> None:
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
            When either the length is not 12, the input is not of the correct type, or it contains negative
            values
        """
        self.baseload_cooling = load

    @property
    def baseload_heating(self) -> np.ndarray:
        """
        This function returns the baseload heating in kWh/month (incl. DHW).

        Returns
        -------
        baseload heating : np.ndarray
            Baseload heating values [kWh/month] for one year, so the length of the array is 12
        """
        return self.correct_for_start_month(self._baseload_heating)

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
            When either the length is not 12, the input is not of the correct type, or it contains negative
            values
        """
        if self._check_input(load):
            self._baseload_heating = np.array(load)
            return
        raise ValueError

    def set_baseload_heating(self, load: ArrayLike) -> None:
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
            When either the length is not 12, the input is not of the correct type, or it contains negative
            values
        """
        self.baseload_heating = np.array(load)

    @property
    def baseload_dhw(self) -> np.ndarray:
        """
        This function returns the baseload DHW in kWh/month for one year.

        Returns
        -------
        baseload DHW : np.ndarray
            Baseload DHW values [kWh/month] for months
        """
        return self._baseload_dhw

    @baseload_dhw.setter
    def baseload_dhw(self, load: ArrayLike) -> None:
        """
        This function sets the baseload DHW [kWh/month] after it has been checked.

        Parameters
        ----------
        load : np.ndarray, list or tuple
            Baseload DHW [kWh/month]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When either the length is not 12 , the input is not of the correct type, or it contains negative
            values
        """
        if self._check_input(load):
            self._baseload_dhw = np.array(load)
            return
        raise ValueError

    @property
    def peak_cooling(self) -> np.ndarray:
        """
        This function returns the peak cooling load in kW/month.

        Returns
        -------
        peak cooling : np.ndarray
            Peak cooling values for one year, so the length of the array is 12
        """
        return np.maximum(self.correct_for_start_month(self._peak_cooling), self.monthly_baseload_cooling_power)

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
            When either the length is not 12, the input is not of the correct type, or it contains negative
            values
        """
        if self._check_input(load):
            self._peak_cooling = np.array(load)
            return
        raise ValueError

    def set_peak_cooling(self, load: ArrayLike) -> None:
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
            When either the length is not 12, the input is not of the correct type, or it contains negative
            values
        """
        self.peak_cooling = np.array(load)

    @property
    def peak_heating(self) -> np.ndarray:
        """
        This function returns the peak heating load in kW/month.

        Returns
        -------
        peak heating : np.ndarray
            Peak heating values for one year, so the length of the array is 12
        """
        return np.maximum(self.correct_for_start_month(self._peak_heating), self.monthly_baseload_heating_power)

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
            When either the length is not 12, the input is not of the correct type, or it contains negative
            values
        """
        if self._check_input(load):
            self._peak_heating = np.array(load)
            return
        raise ValueError

    def set_peak_heating(self, load: ArrayLike) -> None:
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
            When either the length is not 12, the input is not of the correct type, or it contains negative
            values
        """
        self.peak_heating = np.array(load)

    @property
    def monthly_baseload_heating_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly heating baseload in kWh/month for the whole simulation period.

        Returns
        -------
        baseload heating : np.ndarray
            Baseload heating for the whole simulation period
        """
        return np.tile(self.baseload_heating, self.simulation_period)

    @property
    def monthly_baseload_cooling_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly cooling baseload in kWh/month for the whole simulation period.

        Returns
        -------
        baseload cooling : np.ndarray
            Baseload cooling for the whole simulation period
        """
        return np.tile(self.baseload_cooling, self.simulation_period)

    @property
    def monthly_peak_heating_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly heating peak in kW/month for the whole simulation period.

        Returns
        -------
        peak heating : np.ndarray
            Peak heating for the whole simulation period
        """
        return np.tile(self.peak_heating, self.simulation_period)

    @property
    def monthly_peak_cooling_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly cooling peak in kW/month for the whole simulation period.

        Returns
        -------
        peak cooling : np.ndarray
            Peak cooling for the whole simulation period
        """
        return np.tile(self.peak_cooling, self.simulation_period)

    @property
    def monthly_baseload_dhw_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly domestic hot water baseload in kWh/month for the whole simulation period.

        Returns
        -------
        baseload domestic hot water : np.ndarray
            Baseload domestic hot water for the whole simulation period
        """
        return np.tile(self.baseload_dhw, self.simulation_period)

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
        return np.concatenate((array[self.start_month - 1:], array[: self.start_month - 1]))

    @property
    def month_indices(self) -> np.ndarray:
        """
        This property returns the array of all monthly indices for the simulation period.

        Returns
        -------
        time array : np.ndarray
        """
        return np.tile(self.correct_for_start_month(np.arange(1, 13)), self.simulation_period)

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

    def __export__(self):
        temp = {'type': 'Monthly building load', 'load': {}}
        for i in range(12):
            temp['load'][i + 1] = {'Peak heating [kW]': self.peak_heating[i],
                                   'Peak cooling [kW]': self.peak_cooling[i],
                                   'Baseload heating [kWh]': self.baseload_heating[i],
                                   'Baseload cooling [kWh]': self.baseload_cooling[i]
                                   }
        temp['Peak cooling duration [hour]'] = self.peak_injection_duration / 3600
        temp['Peak heating duration [hour]'] = self.peak_extraction_duration / 3600
        temp['Simulation period [year]'] = self.simulation_period
        temp['First month of simulation [-]'] = self.start_month
        temp['Efficiency heating'] = self.cop.__export__()
        temp['Efficiency cooling'] = self.eer.__export__()
        if self.max_peak_dhw == 0:
            return temp

        temp['DHW demand [kWh/year]'] = self.yearly_average_dhw_load
        temp['Efficiency DHW'] = self.cop_dhw.__export__()
        return temp
