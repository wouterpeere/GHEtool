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
                 efficiency_cooling: Union[int, float, EER, SEER, EERCombined],
                 dhw: Union[float, np.ndarray] = None,
                 efficiency_dhw: Union[int, float, COP, SCOP] = 4,
                 multiyear: bool = False):
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
        multiyear : bool
            True if multiyear data
        """
        _LoadDataBuilding.__init__(self, efficiency_heating, efficiency_cooling, dhw, efficiency_dhw, multiyear)
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
        return np.mean(self.hourly_dhw_load_simulation_period.reshape((self.simulation_period, 8760)), axis=0)

    def _get_hourly_cop(self, power: np.ndarray = None) -> Union[float, np.ndarray]:
        """
        This function returns the hourly COP value for the given temperature result profile.

        Parameters
        ----------
        power : np.ndarray
            Array with power data.

        Raises
        ------
        TypeError
            When the results are provided on a monthly basis

        Returns
        -------
        COP : float | np.ndarray
            Array of COP values
        """
        if isinstance(self.cop, SCOP) and isinstance(self.eer, SEER) and isinstance(self.cop_dhw, SCOP):
            return self.cop.get_COP(0, power=np.nan_to_num(power))
        if isinstance(self.results, ResultsMonthly):
            raise TypeError('You cannot get an hourly EER values based on monthly temperature results.')
        if isinstance(self.results, tuple):
            temperature = self.results[1]
        else:
            temperature = self.results.Tf

        return self.cop.get_COP(temperature, power=np.nan_to_num(power))

    def _get_hourly_cop_dhw(self, power: np.ndarray = None) -> Union[float, np.ndarray]:
        """
        This function returns the hourly COP DHW value for the given temperature result profile.

        Parameters
        ----------
        power : np.ndarray
            Array with power data.

        Raises
        ------
        TypeError
            When the results are provided on a monthly basis

        Returns
        -------
        COP : float | np.ndarray
            Array of COP values
        """
        if isinstance(self.cop, SCOP) and isinstance(self.eer, SEER) and isinstance(self.cop_dhw, SCOP):
            return self.cop_dhw.get_COP(0, power=np.nan_to_num(power))
        if isinstance(self.results, ResultsMonthly):
            raise TypeError('You cannot get an hourly EER values based on monthly temperature results.')
        if isinstance(self.results, tuple):
            temperature = self.results[1]
        else:
            temperature = self.results.Tf

        return self.cop_dhw.get_COP(temperature, power=np.nan_to_num(power))

    def _get_hourly_eer(self, power: np.ndarray = None) -> Union[float, np.ndarray]:
        """
        This function returns the hourly EER value for the given temperature result profile.

        Parameters
        ----------
        power : np.ndarray
            Array with power data.

        Raises
        ------
        TypeError
            When the results are provided on a monthly basis

        Returns
        -------
        EER : float | np.ndarray
            Array of EER values
        """
        if isinstance(self.cop, SCOP) and isinstance(self.eer, SEER) and isinstance(self.cop_dhw, SCOP):
            return self.eer.get_EER(0, power=np.nan_to_num(power), month_indices=self.month_indices)
        if isinstance(self.results, ResultsMonthly):
            raise TypeError('You cannot get an hourly EER values based on monthly temperature results.')
        if isinstance(self.results, tuple):
            temperature = self.results[1]
        else:
            temperature = self.results.Tf

        return self.eer.get_EER(temperature, power=np.nan_to_num(power), month_indices=self.month_indices)

    @property
    def hourly_injection_load_simulation_period(self) -> np.ndarray:
        """
        This function returns the hourly injection load in kWh/h for the whole simulation period.

        Returns
        -------
        hourly injection : np.ndarray
            Hourly injection values [kWh/h] for the whole simulation period
        """
        part_load = self.hourly_cooling_load_simulation_period
        return np.multiply(
            self.hourly_cooling_load_simulation_period,
            self.conversion_factor_secondary_to_primary_cooling(self._get_hourly_eer(part_load)))

    @property
    def hourly_extraction_load_simulation_period(self) -> np.ndarray:
        """
        This function returns the hourly extraction load in kWh/h for the whole simulation period.

        Returns
        -------
        hourly extraction : np.ndarray
            Hourly extraction values [kWh/h] for the whole simulation period
        """
        if isinstance(self.dhw, (int, float)) and self.dhw == 0.:
            return self._hourly_extraction_load_heating_simulation_period
        return self._hourly_extraction_load_heating_simulation_period + self._hourly_extraction_load_dhw_simulation_period

    @property
    def _hourly_extraction_load_heating_simulation_period(self) -> np.ndarray:
        """
        This function returns the hourly extraction load for space heating in kWh/h for the whole simulation period.

        Returns
        -------
        hourly extraction : np.ndarray
            Hourly extraction values [kWh/h] for the whole simulation period
        """
        part_load = self.hourly_heating_load_simulation_period
        return np.multiply(
            self.hourly_heating_load_simulation_period,
            self.conversion_factor_secondary_to_primary_heating(self._get_hourly_cop(part_load)))

    @property
    def _hourly_extraction_load_dhw_simulation_period(self) -> np.ndarray:
        """
        This function returns the hourly extraction load for DHW in kWh/h for the whole simulation period.

        Returns
        -------
        hourly extraction : np.ndarray
            Hourly extraction values [kWh/h] for the whole simulation period
        """
        part_load_dhw = self.hourly_dhw_load_simulation_period
        return np.multiply(
            self.hourly_dhw_load_simulation_period,
            self.conversion_factor_secondary_to_primary_heating(self._get_hourly_cop_dhw(part_load_dhw)))

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
    def monthly_baseload_injection_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly injection baseload in kWh/month for the whole simulation period.
        Redefined for Hourly Building data. When the results are in hourly format, the monthly baseload injection
        should be calculated based on the hourly injection load. When results are available in a monthly format,
        the monthly baseload injection should be based on the monthly baseload cooling.

        Returns
        -------
        baseload injection : np.ndarray
            baseload injection for the whole simulation period
        """
        if isinstance(self.results, ResultsMonthly):
            return super(_HourlyDataBuilding, self).monthly_baseload_injection_simulation_period
        return self.resample_to_monthly(self.hourly_injection_load_simulation_period)[1]

    @property
    def _monthly_baseload_extraction_heating_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly extraction baseload for space heating.in kWh/month for the whole simulation period.

        Returns
        -------
        baseload extraction : np.ndarray
            Baseload extraction for the whole simulation period
        """
        if isinstance(self.results, ResultsMonthly):
            return super(_HourlyDataBuilding, self)._monthly_baseload_extraction_heating_simulation_period
        return self.resample_to_monthly(self._hourly_extraction_load_heating_simulation_period)[1]

    @property
    def _monthly_baseload_extraction_dhw_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly extraction baseload for DHW production in kWh/month for the whole simulation period.

        Returns
        -------
        baseload extraction : np.ndarray
            Baseload extraction for the whole simulation period
        """
        if isinstance(self.results, ResultsMonthly):
            return super(_HourlyDataBuilding, self)._monthly_baseload_extraction_dhw_simulation_period
        return self.resample_to_monthly(self._hourly_extraction_load_dhw_simulation_period)[1]

    @property
    def monthly_peak_injection_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly injection peak in kW/month for the whole simulation period.
        Redefined for Hourly Building data. When the results are in hourly format, the monthly peak injection
        should be calculated based on the hourly injection load. When results are available in a monthly format,
        the monthly peak injection should be based on the monthly peak cooling.

        Returns
        -------
        peak injection : np.ndarray
            peak injection for the whole simulation period
        """
        if isinstance(self.results, ResultsMonthly):
            return super(_HourlyDataBuilding, self).monthly_peak_injection_simulation_period
        return self.resample_to_monthly(self.hourly_injection_load_simulation_period)[0]

    @property
    def _monthly_peak_extraction_heating_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly extraction peak of space heating in kW/month for the whole simulation period.

        Returns
        -------
        peak extraction : np.ndarray
            Peak extraction for the whole simulation period
        """
        if isinstance(self.results, ResultsMonthly):
            return super(_HourlyDataBuilding, self)._monthly_peak_extraction_heating_simulation_period
        return self.resample_to_monthly(self._hourly_extraction_load_heating_simulation_period)[0]

    @property
    def _monthly_peak_extraction_dhw_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly extraction peak of the DHW production in kW/month for the whole simulation period.
        Returns
        -------
        peak extraction : np.ndarray
            Peak extraction for the whole simulation period
        """
        if isinstance(self.results, ResultsMonthly):
            return super(_HourlyDataBuilding, self)._monthly_peak_extraction_dhw_simulation_period
        return self.resample_to_monthly(self._hourly_extraction_load_dhw_simulation_period)[0]

    @property
    def monthly_baseload_dhw_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly domestic hot water baseload in kWh/month for the whole simulation period.

        Returns
        -------
        baseload domestic hot water : np.ndarray
            Baseload domestic hot water for the whole simulation period
        """
        return self.resample_to_monthly(self.hourly_dhw_load_simulation_period)[1]

    @property
    def monthly_peak_dhw_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly peak power coming from the domestic hot water demand
        in kW/month for the whole simulation period.

        Returns
        -------
        peak power domestic hot water : np.ndarray
            Peak power domestic hot water for the whole simulation period
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

    @property
    def max_peak_cooling(self) -> float:
        """
        This returns the max peak cooling in kW.

        Returns
        -------
        max peak cooling : float
        """
        return np.max(self.hourly_cooling_load_simulation_period)

    @property
    def max_peak_heating(self) -> float:
        """
        This returns the max peak heating in kW.

        Returns
        -------
        max peak heating : float
        """
        return np.max(self.hourly_heating_load_simulation_period)

    @property
    def max_peak_dhw(self) -> float:
        """
        This returns the max peak DHW in kW.

        Returns
        -------
        max peak DHW : float
        """
        return np.max(self.hourly_dhw_load_simulation_period)

    def load_hourly_profile(
            self, file_path: str, header: bool = True, separator: str = ";", decimal_seperator: str = ".",
            col_heating: int = 0, col_cooling: int = 1, col_dhw: int = None) -> None:
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
        col_heating : int
            Column index for heating data
        col_cooling : int
            Column index for cooling data
        col_dhw : int
            Column index for dhw data. None if not applicable

        Returns
        -------
        None
        """
        if header:
            header: int = 0
        else:
            header = None

        # TODO implement single column

        # import data
        df = pd.read_csv(file_path, sep=separator, header=header, decimal=decimal_seperator)

        # set data
        self.hourly_heating_load = np.array(df.iloc[:, col_heating])
        self.hourly_cooling_load = np.array(df.iloc[:, col_cooling])
        if col_dhw is not None:
            self.dhw = np.array(df.iloc[:, col_dhw])

    @property
    def max_peak_injection(self) -> float:
        """
        This returns the max peak injection in kW.

        Returns
        -------
        max peak injection : float
        """
        if isinstance(self._results, ResultsMonthly):
            return np.max(self.monthly_peak_injection_simulation_period)
        return np.max(self.hourly_injection_load_simulation_period)

    @property
    def max_peak_extraction(self) -> float:
        """
        This returns the max peak extraction in kW.

        Returns
        -------
        max peak extraction : float
        """
        if isinstance(self._results, ResultsMonthly):
            return np.max(self.monthly_peak_extraction_simulation_period)
        return np.max(self.hourly_extraction_load_simulation_period)

    @property
    def imbalance(self) -> float:
        """
        This function calculates the average yearly ground imbalance.
        A positive imbalance means that the field is injection dominated, i.e. it heats up every year.

        Returns
        -------
        imbalance : float
        """
        if isinstance(self._results, ResultsMonthly):
            return super(_HourlyData, self).imbalance
        return np.sum(
            self.hourly_injection_load_simulation_period - self.hourly_extraction_load_simulation_period) / self.simulation_period

    @property
    def month_indices(self) -> np.ndarray:
        """
        This property returns the array of all monthly indices for the simulation period.

        Returns
        -------
        time array : np.ndarray
        """
        return np.tile(np.repeat(np.arange(1, 13), self.UPM), self.simulation_period)
