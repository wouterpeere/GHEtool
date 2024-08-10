import abc

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ._HourlyData import _HourlyData
from ._LoadDataBuilding import _LoadDataBuilding
from abc import ABC
from typing import Union
from GHEtool.logger import ghe_logger
from GHEtool.VariableClasses.Efficiency import *
from GHEtool.VariableClasses.Result import ResultsMonthly, ResultsHourly


class _HourlyDataBuilding(_LoadDataBuilding, _HourlyData, ABC):

    def __init__(self,
                 efficiency_heating: Union[int, float, COP, SCOP],
                 efficiency_cooling: Union[int, float, EER, SEER],
                 dhw: Union[float, np.ndarray] = None,
                 efficiency_dhw: Union[int, float, COP, SCOP] = 4):
        """

        Parameters
        ----------
        efficiency_heating : int, float, COP, SCOP
            Efficiency in heating
        efficiency_cooling : int, float, EER, SEER
            Efficiency in cooling
        dhw : float, np.ndarray
            Yearly value of array with energy demand for domestic hot water (DHW) [kWh]
        efficiency_dhw : int, float, COP, SCOP,
            Efficiency in DHW
        """
        _LoadDataBuilding.__init__(self, efficiency_heating, efficiency_cooling, dhw, efficiency_dhw)
        _HourlyData.__init__(self)

        # initiate variables
        self._hourly_heating_load: np.ndarray = np.zeros(8760)
        self._hourly_cooling_load: np.ndarray = np.zeros(8760)

        # delete unnecessary variables
        del self._peak_cooling
        del self._peak_heating
        del self._baseload_cooling
        del self._baseload_heating

    @abc.abstractmethod
    def hourly_cooling_load_simulation_period(self) -> np.ndarray:
        """
        This function returns the hourly cooling load in kWh/h for the whole simulation period.

        Returns
        -------
        hourly cooling : np.ndarray
            Hourly cooling values [kWh/h] for the whole simulation period
        """

    @abc.abstractmethod
    def hourly_heating_load_simulation_period(self) -> np.ndarray:
        """
        This function returns the hourly heating load in kWh/h for the whole simulation period.

        Returns
        -------
        hourly heating : np.ndarray
            Hourly heating values [kWh/h] for the whole simulation period
        """

    @abc.abstractmethod
    def hourly_dhw_load_simulation_period(self) -> np.ndarray:
        """
        This function returns the hourly DHW load in kWh/h for the whole simulation period.

        Returns
        -------
        hourly DHW : np.ndarray
            Hourly DHW values [kWh/h] for the whole simulation period
        """

    @property
    def hourly_cooling_load(self) -> np.ndarray:
        """
        This function returns the hourly cooling load in kWh/h.

        Returns
        -------
        hourly cooling : np.ndarray
            Hourly cooling values [kWh/h] for one year, so the length of the array is 8760
        """
        return np.mean(self.hourly_cooling_load_simulation_period.reshape((self.simulation_period, 8760)), axis=0)

    @property
    def hourly_heating_load(self) -> np.ndarray:
        """
        This function returns the hourly heating load in kWh/h.

        Returns
        -------
        hourly heating : np.ndarray
            Hourly heating values [kWh/h] for one year, so the length of the array is 8760
        """
        return np.mean(self.hourly_heating_load_simulation_period.reshape((self.simulation_period, 8760)), axis=0)

    @property
    def hourly_dhw_load(self) -> np.ndarray:
        """
        This function returns the hourly DHW load in kWh/h.

        Returns
        -------
        hourly DHW : np.ndarray
            Hourly DHW values [kWh/h] for one year, so the length of the array is 8760
        """
        return np.mean(self.hourly_heating_load_simulation_period.reshape((self.simulation_period, 8760)), axis=0)

    def _get_hourly_cop(self, part_load: np.ndarray = None) -> Union[float, np.ndarray]:
        """
        This function returns the hourly COP value for the given temperature result profile.

        Parameters
        ----------
        part_load : np.ndarray
            Array with part_load data.

        Returns
        -------
        COP : float | np.ndarray
            Array of COP values
        """
        if isinstance(self.results, tuple):
            temperature = self.results[1]
        else:
            temperature = self.results.Tf

        return self.cop.get_COP(temperature, part_load=part_load)

    def _get_hourly_cop_dhw(self, part_load: np.ndarray = None) -> Union[float, np.ndarray]:
        """
        This function returns the hourly COP DHW value for the given temperature result profile.

        Parameters
        ----------
        part_load : np.ndarray
            Array with part_load data.

        Returns
        -------
        COP : float | np.ndarray
            Array of COP values
        """
        if isinstance(self.results, tuple):
            temperature = self.results[1]
        else:
            temperature = self.results.Tf

        return self.cop_dhw.get_COP(temperature, part_load=part_load)

    def _get_hourly_eer(self, part_load: np.ndarray = None) -> Union[float, np.ndarray]:
        """
        This function returns the hourly EER value for the given temperature result profile.

        Parameters
        ----------
        part_load : np.ndarray
            Array with part_load data.

        Returns
        -------
        EER : float | np.ndarray
            Array of EER values
        """
        if isinstance(self.results, tuple):
            temperature = self.results[1]
        else:
            temperature = self.results.Tf

        return self.eer.get_EER(temperature, part_load=part_load)

    @property
    def hourly_injection_load_simulation_period(self) -> np.ndarray:
        """
        This function returns the hourly injection load in kWh/h for the whole simulation period.

        Returns
        -------
        hourly injection : np.ndarray
            Hourly injection values [kWh/h] for the whole simulation period
        """
        part_load = None
        if self.eer._range_part_load:
            part_load = self.hourly_cooling_load_simulation_period / self.max_peak_cooling
        return np.multiply(
            self.hourly_cooling_load_simulation_period, self._get_hourly_eer(part_load))

    @property
    def hourly_extraction_load_simulation_period(self) -> np.ndarray:
        """
        This function returns the hourly extraction load in kWh/h for the whole simulation period.

        Returns
        -------
        hourly extraction : np.ndarray
            Hourly extraction values [kWh/h] for the whole simulation period
        """
        part_load = None
        if self.cop._range_part_load:
            part_load = self.hourly_heating_load_simulation_period / self.max_peak_heating
        extraction_due_to_heating = np.multiply(
            self.hourly_heating_load_simulation_period, self._get_hourly_cop(part_load))

        if isinstance(self.dhw, (int, float)) and self.dhw == 0.:
            return extraction_due_to_heating

        part_load_dhw = self.hourly_dhw_load_simulation_period / self.max_peak_dhw
        return extraction_due_to_heating + np.multiply(
            self.hourly_dhw_load_simulation_period, self._get_hourly_cop_dhw(part_load_dhw))

    @property
    def monthly_baseload_heating_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly heating baseload in kWh/month for the whole simulation period.

        Returns
        -------
        baseload heating : np.ndarray
            Baseload heating for the whole simulation period
        """
        return self.resample_to_monthly(self.hourly_heating_load_simulation_period)[1]

    @property
    def monthly_baseload_cooling_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly cooling baseload in kWh/month for the whole simulation period.

        Returns
        -------
        baseload cooling : np.ndarray
            Baseload cooling for the whole simulation period
        """
        return self.resample_to_monthly(self.hourly_cooling_load_simulation_period)[1]

    @property
    def monthly_peak_heating_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly heating peak in kW/month for the whole simulation period.

        Returns
        -------
        peak heating : np.ndarray
            Peak heating for the whole simulation period
        """
        return self.resample_to_monthly(self.hourly_heating_load_simulation_period)[0]

    @property
    def monthly_peak_cooling_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly cooling peak in kW/month for the whole simulation period.

        Returns
        -------
        peak cooling : np.ndarray
            Peak cooling for the whole simulation period
        """
        return self.resample_to_monthly(self.hourly_cooling_load_simulation_period)[0]

    @property
    def monthly_baseload_dhw_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly domestic hot water baseload in kWh/month for the whole simulation period.

        Returns
        -------
        baseload domestic hot water : np.ndarray
            Baseload domestic hot water for the whole simulation period
        """
        return self.resample_to_monthly(self.hourly_dhw_load_simulation_period)[0]

    def set_results(self, results: Union[ResultsMonthly, ResultsHourly]) -> None:
        """
        This function sets the temperature results.

        Parameters
        ----------
        results : ResultsMonthly, ResultsHourly
            Results object

        Raises
        ------
        ValueError
            If the simulation period of the results do not match the simulation period of the load data.

        Returns
        -------
        None
        """
        # check if the length is correct
        if isinstance(results, ResultsMonthly) and len(results.Tb) != self.simulation_period * 12:
            raise ValueError(
                f'The results have a length of {len(results.Tb)} whereas, with a simulation period of {self.simulation_period} years '
                f'a length of {self.simulation_period * 12} was expected for a ResultsMonthly.')
        if isinstance(results, ResultsHourly) and len(results.Tb) != self.simulation_period * 8760:
            raise ValueError(
                f'The results have a length of {len(results.Tb)} whereas, with a simulation period of {self.simulation_period} years '
                f'a length of {self.simulation_period * 8760} was expected for a ResultsHourly.')
        self._results = results
