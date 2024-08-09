import abc

import numpy as np

from abc import ABC
from GHEtool.logger.ghe_logger import ghe_logger
from GHEtool.VariableClasses.Efficiency import *
from GHEtool.VariableClasses.LoadData.Baseclasses import _LoadData
from GHEtool.VariableClasses.Result import ResultsMonthly, ResultsHourly
from typing import Union


class _LoadDataBuilding(_LoadData, ABC):
    """
    This class contains all the general functionalities for the load classes for the building loads.
    """

    def __init__(self,
                 efficiency_heating: Union[int, float, COP, SCOP],
                 efficiency_cooling: Union[int, float, EER, SEER],
                 dhw: Union[float, np.ndarray] = 0.,
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
        super().__init__()

        # initiate variables
        self._baseload_heating: np.ndarray = np.zeros(12)
        self._baseload_cooling: np.ndarray = np.zeros(12)
        self._peak_heating: np.ndarray = np.zeros(12)
        self._peak_cooling: np.ndarray = np.zeros(12)
        self._dhw = 0.

        self._cop = None
        self._eer = None
        self._cop_dhw = None
        self._results = None
        self._results_fixed = (0, 17)
        self.exclude_DHW_from_peak: bool = False  # by default, the DHW increase the peak load. Set to false,
        # if you only want the heating load to determine the peak in extraction

        # set variables
        self.cop = efficiency_heating
        self.eer = efficiency_cooling
        self.cop_dhw = efficiency_dhw
        self.dhw = dhw

    @abc.abstractmethod
    def monthly_baseload_heating_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly heating baseload in kWh/month for the whole simulation period.

        Returns
        -------
        baseload heating : np.ndarray
            Baseload heating for the whole simulation period
        """

    @abc.abstractmethod
    def monthly_baseload_cooling_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly cooling baseload in kWh/month for the whole simulation period.

        Returns
        -------
        baseload cooling : np.ndarray
            Baseload cooling for the whole simulation period
        """

    @abc.abstractmethod
    def monthly_peak_heating_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly heating peak in kW/month for the whole simulation period.

        Returns
        -------
        peak heating : np.ndarray
            Peak heating for the whole simulation period
        """

    @abc.abstractmethod
    def monthly_peak_cooling_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly cooling peak in kW/month for the whole simulation period.

        Returns
        -------
        peak cooling : np.ndarray
            Peak cooling for the whole simulation period
        """

    @property
    def monthly_baseload_cooling(self) -> np.ndarray:
        """

        Returns
        -------

        """
        return np.mean(self.monthly_baseload_cooling_simulation_period.reshape((self.simulation_period, 12)),
                       axis=0)

    @property
    def monthly_baseload_heating(self) -> np.ndarray:
        """

        Returns
        -------

        """
        return np.mean(self.monthly_baseload_heating_simulation_period.reshape((self.simulation_period, 12)),
                       axis=0)

    @property
    def monthly_peak_cooling(self) -> np.ndarray:
        """

        Returns
        -------

        """
        return np.mean(self.monthly_peak_cooling_simulation_period.reshape((self.simulation_period, 12)),
                       axis=0)

    @property
    def monthly_peak_heating(self) -> np.ndarray:
        """

        Returns
        -------

        """
        return np.mean(self.monthly_peak_heating_simulation_period.reshape((self.simulation_period, 12)),
                       axis=0)

    @property
    def monthly_baseload_cooling_power(self) -> np.ndarray:
        """

        Returns
        -------

        """
        return np.divide(self.monthly_baseload_cooling, self.UPM)

    @property
    def monthly_baseload_heating_power(self) -> np.ndarray:
        """

        Returns
        -------

        """
        return np.divide(self.monthly_baseload_heating, self.UPM)

    @property
    def cop(self):
        """
        This function returns the cop/scop object.

        Returns
        -------
        COP or SCOP
        """
        return self._cop

    @cop.setter
    def cop(self, efficiency_heating: Union[int, float, COP, SCOP]) -> None:
        """
        This function defines the efficiency in heating.
        Integer and float values will be automatically converted to an SCOP object.

        Parameters
        ----------
        efficiency_heating : int, float, COP, SCOP
            The efficiency in heating

        Returns
        -------
        None
        """
        if isinstance(efficiency_heating, (int, float)):
            self._cop = SCOP(efficiency_heating)
            return
        self._cop = efficiency_heating

    @property
    def eer(self):
        """
        This function returns the eer/seer object.

        Returns
        -------
        EER or SEER
        """
        return self._eer

    @eer.setter
    def eer(self, efficiency_cooling: Union[int, float, EER, SEER]) -> None:
        """
        This function defines the efficiency in cooling.
        Integer and float values will be automatically converted to an SEER object.

        Parameters
        ----------
        efficiency_cooling : int, float, COP, SCOP
            The efficiency in cooling

        Returns
        -------
        None
        """
        if isinstance(efficiency_cooling, (int, float)):
            self._eer = SEER(efficiency_cooling)
            return
        self._eer = efficiency_cooling

    @property
    def cop_dhw(self):
        """
        This function returns the cop/scop object for DHW.

        Returns
        -------
        COP or SCOP
        """
        return self._cop_dhw

    @cop_dhw.setter
    def cop_dhw(self, efficiency_dhw: Union[int, float, COP, SCOP]) -> None:
        """
        This function defines the efficiency in DHW production.
        Integer and float values will be automatically converted to an SCOP object.

        Parameters
        ----------
        efficiency_dhw : int, float, COP, SCOP
            The efficiency in DHW production

        Returns
        -------
        None
        """
        if isinstance(efficiency_dhw, (int, float)):
            self._cop_dhw = SCOP(efficiency_dhw)
            return
        self._cop_dhw = efficiency_dhw

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
            If the length of the results is not equal to the length of the data in the load class.

        Returns
        -------
        None
        """
        # check if the length is correct
        if len(results.Tb) != self.simulation_period * (8760 if self._hourly else 12) or (
                self._hourly != isinstance(results, ResultsHourly)):
            raise ValueError(
                'The results have a length of {len(results.Tb)} whereas, with a simulation period of {self.simulation_period} years '
                'a length of {self.simulation_period * (8760 if self._hourly else 12)} was expected.')
        self._results = results

    def reset_results(self, min_temperature: float, max_temperature: float) -> None:
        """
        This function resets the result object sets the temperature boundaries to the minimum and maximum temperature.

        Parameters
        ----------
        min_temperature : float
            Minimum average temperature of the fluid [°C]
        max_temperature : float
            Maximum average temperature of the fluid [°C]

        Returns
        -------
        None
        """
        self._results = None
        self._results_fixed = (min_temperature, max_temperature)

    @property
    def results(self) -> Union[tuple, ResultsHourly, ResultsMonthly]:
        """
        This function returns the saved temperature results. If these are not available, the constant temperature
        boundaries are returned.

        Returns
        -------
        result : tuple, np.ndarray
            Temperature results or a tuple with constant temperature boundaries
        """
        if self._results is None:
            return self._results_fixed
        return self._results

    @property
    def peak_heating_duration(self) -> float:
        """
        Length of the peak in heating.

        Returns
        -------
        Length peak in heating [s]
        """
        return self._peak_extraction_duration * 3600

    @peak_heating_duration.setter
    def peak_heating_duration(self, duration: float) -> None:
        """
        This function sets the duration of the peak in heating.

        Parameters
        ----------
        duration : float
            Duration of the peak in hours

        Returns
        -------
        None
        """
        self._peak_extraction_duration = duration

    @property
    def peak_cooling_duration(self) -> float:
        """
        Duration of the peak in cooling.

        Returns
        -------
        Duration of the peak in cooling [s]
        """
        return self._peak_injection_duration * 3600

    @peak_cooling_duration.setter
    def peak_cooling_duration(self, duration: float) -> None:
        """
        This function sets the duration of the peak in cooling.

        Parameters
        ----------
        duration : float
            Duration of the peak in hours

        Returns
        -------
        None
        """
        self._peak_injection_duration = duration

    def get_cop(self, peak: bool) -> Union[float, np.ndarray]:
        """
        This function returns the COP value for the given temperature result profile.

        Parameters
        ----------
        peak : bool
            True if the COP values for the peak load in heating should be given.
            When False, the values for the baseload heating are given.

        Returns
        -------
        COP : float | np.ndarray
            Array of COP values
        """
        if isinstance(self.results, tuple):
            return self.results[0]
        if isinstance(self.results, ResultsHourly):
            return self.results.Tf
        if peak:
            return self.results.peak_extraction
        return self.results.monthly_extraction

    def get_eer(self, peak: bool) -> Union[float, np.ndarray]:
        """
        This function returns the EER value for the given temperature result profile.

        Parameters
        ----------
        peak : bool
            True if the EER values for the peak load in cooling should be given.
            When False, the values for the baseload cooling are given.

        Returns
        -------
        EER : float | np.ndarray
            Array of EER values
        """
        if isinstance(self.results, tuple):
            return self.results[1]
        if isinstance(self.results, ResultsHourly):
            return self.results.Tf
        if peak:
            return self.results.peak_injection
        return self.results.monthly_injection

    @staticmethod
    def conversion_factor_secondary_to_primary_heating(cop_value: Union[int, float, np.ndarray]) -> Union[
        float, np.ndarray]:
        """
        This function returns the correction factor to convert a secondary heating load to the primary load
        using the definition of the COP = Qh/W.

        Parameters
        ----------
        cop_value : int, float, np.ndarray
            Value(s) for the COP

        Returns
        -------
        COP value(s) : float, np.ndarray
        """
        return 1 - 1 / cop_value

    @staticmethod
    def conversion_factor_secondary_to_primary_cooling(eer_value: Union[int, float, np.ndarray]):
        """
        This function returns the correction factor to convert a secondary cooling load to the primary load
        using the definition of the EER = Ql/W.

        Parameters
        ----------
        eer_value : int, float, np.ndarray
            Value(s) for the EER

        Returns
        -------
        EER value(s) : float, np.ndarray
        """
        return 1 + 1 / eer_value

    @property
    def monthly_baseload_injection_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly injection baseload in kWh/month for the whole simulation period.

        Returns
        -------
        baseload injection : np.ndarray
            Baseload injection for the whole simulation period
        """
        part_load = None
        if self.eer._range_part_load:
            part_load = np.divide(self.monthly_baseload_cooling_simulation_period,
                                  np.tile(self.UPM, self.simulation_period)) / self.max_peak_cooling
        return np.divide(
            self.monthly_baseload_cooling_simulation_period,
            self.eer.get_EER(self.get_eer(False), part_load=part_load))

    @property
    def monthly_baseload_extraction_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly extraction baseload in kWh/month for the whole simulation period.
        This takes into account the DHW profile

        Returns
        -------
        baseload extraction : np.ndarray
            Baseload extraction for the whole simulation period
        """
        part_load = None
        if self.cop._range_part_load:
            part_load = np.divide(self.monthly_baseload_heating_simulation_period,
                                  np.tile(self.UPM, self.simulation_period)) / self.max_peak_heating
        extraction_due_to_heating = np.divide(
            self.monthly_baseload_heating_simulation_period,
            self.cop.get_COP(self.get_cop(True), part_load=part_load))

        if isinstance(self.dhw, (int, float)) and self.dhw == 0.:
            return extraction_due_to_heating

        part_load_dhw = self.monthly_baseload_dhw_power_simulation_period / np.max(
            self.monthly_baseload_dhw_power_simulation_period)
        return extraction_due_to_heating + np.divide(
            self.monthly_baseload_dhw_simulation_period,
            self.cop_dhw.get_COP(self.get_cop(True), part_load=part_load_dhw))

    @property
    def monthly_peak_injection_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly injection peak in kW/month for the whole simulation period.

        Returns
        -------
        peak injection : np.ndarray
            Peak injection for the whole simulation period
        """
        part_load = None
        if self.eer._range_part_load:
            part_load = self.monthly_peak_cooling_simulation_period / self.max_peak_cooling
        return np.divide(
            self.monthly_peak_cooling_simulation_period,
            self.eer.get_EER(self.get_eer(True), part_load=part_load))

    @property
    def monthly_peak_extraction_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly extraction peak in kW/month for the whole simulation period.
        DHW is by default taken into account for the calculation of the peak extraction.
        This behaviour can be disabled by setting the 'exclude_DHW_from_peak' attribute to False.

        Returns
        -------
        peak extraction : np.ndarray
            Peak extraction for the whole simulation period
        """
        part_load = None
        if self.cop._range_part_load:
            part_load = self.monthly_peak_heating_simulation_period / self.max_peak_heating

        extraction_due_to_heating = np.divide(
            self.monthly_peak_heating_simulation_period,
            self.cop.get_COP(self.get_cop(True), part_load=part_load))

        if self.exclude_DHW_from_peak or (isinstance(self.dhw, (int, float)) and self.dhw == 0.):
            return extraction_due_to_heating

        part_load_dhw = self.monthly_baseload_dhw_power_simulation_period / np.max(
            self.monthly_baseload_dhw_power_simulation_period)
        return extraction_due_to_heating + np.divide(
            self.monthly_baseload_dhw_power_simulation_period,
            self.cop_dhw.get_COP(self.get_cop(True), part_load=part_load_dhw))

    @property
    def max_peak_cooling(self) -> float:
        """
        This returns the max peak cooling in kW.

        Returns
        -------
        max peak cooling : float
        """
        return np.max(self.monthly_peak_cooling_simulation_period)

    @property
    def max_peak_heating(self) -> float:
        """
        This returns the max peak heating in kW.

        Returns
        -------
        max peak heating : float
        """
        return np.max(self.monthly_peak_heating_simulation_period)

    @property
    def yearly_average_cooling_load(self) -> float:
        """
        This function returns the average yearly cooling load in kWh.

        Returns
        -------
        float
            Yearly cooling load kWh/year
        """
        return np.sum(self.monthly_baseload_cooling)

    @property
    def yearly_average_heating_load(self) -> float:
        """
        This function returns the average yearly heating load in kWh.

        Returns
        -------
        float
            Yearly heating load kWh/year
        """
        return np.sum(self.monthly_baseload_heating)

    @property
    def yearly_heating_load_simulation_period(self) -> np.array:
        """
        This function returns the yearly heating demand in kWh/year for the whole simulation period.

        Returns
        -------
        yearly heating : np.ndarray
            yearly heating for the whole simulation period
        """
        return np.sum(np.reshape(self.monthly_baseload_heating_simulation_period, (self.simulation_period, 12)),
                      axis=1)

    @property
    def yearly_cooling_load_simulation_period(self) -> np.array:
        """
        This function returns the yearly cooling demand in kWh/year for the whole simulation period.

        Returns
        -------
        yearly cooling : np.ndarray
            yearly cooling for the whole simulation period
        """
        return np.sum(np.reshape(self.monthly_baseload_cooling_simulation_period, (self.simulation_period, 12)),
                      axis=1)

    @property
    def yearly_heating_peak_simulation_period(self) -> np.array:
        """
        This function returns the yearly heating peak in kW/year for the whole simulation period.

        Returns
        -------
        yearly heating : np.ndarray
            yearly heating for the whole simulation period
        """
        return np.max(np.reshape(self.monthly_peak_heating_simulation_period, (self.simulation_period, 12)), axis=1)

    @property
    def yearly_cooling_peak_simulation_period(self) -> np.array:
        """
        This function returns the yearly cooling peak in kW/year for the whole simulation period.

        Returns
        -------
        yearly cooling : np.ndarray
            yearly cooling for the whole simulation period
        """
        return np.max(np.reshape(self.monthly_peak_cooling_simulation_period, (self.simulation_period, 12)), axis=1)

    def add_dhw(self, dhw: Union[float, np.ndarray]) -> None:
        """
        This function adds the domestic hot water (dhw).
        An error is raised if the dhw is not positive.

        Parameters
        ----------
        dhw : float, np.ndarray
            Yearly value of array with energy demand for domestic hot water (DHW) [kWh]

        Returns
        -------
        None
        """
        self.dhw = dhw

    @property
    def dhw(self) -> Union[float, np.ndarray]:
        """
        This function returns the DHW object.

        Returns
        -------
        DHW object
        """
        return self._dhw

    @dhw.setter
    def dhw(self, dhw: Union[float, np.ndarray]) -> None:
        """
        This function adds the domestic hot water (dhw).
        An error is raised is the dhw is not positive.

        Parameters
        ----------
        dhw : float, np.ndarray
            Yearly value of array with energy demand for domestic hot water (DHW) [kWh]

        Raises
        ------
        ValueError
            For negative DHW values
            When the array is not the right length.

        Returns
        -------
        None
        """
        if isinstance(dhw, (float, int)):
            if not dhw >= 0:
                raise ValueError(f'Please fill in a positive value for the domestic hot water instead of {dhw}.')
            self._dhw = dhw
            return
        if not self._check_input(dhw):
            raise ValueError('Wrong value for the DHW array. Please make sure the length matches that of the heating '
                             'and cooling array.')
        self._dhw = dhw

    @property
    def monthly_baseload_dhw_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly domestic hot water baseload in kWh/month for the whole simulation period.

        Returns
        -------
        baseload domestic hot water : np.ndarray
            Baseload domestic hot water for the whole simulation period
        """
        if isinstance(self._dhw, (int, float)):
            temp = self._dhw / (8760 if self._hourly else 12)
            return np.full(self.simulation_period * (8760 if self._hourly else 12), temp)
        if self._multiyear:
            return self._dhw
        return np.tile(self._dhw, self.simulation_period)

    @property
    def monthly_baseload_dhw_power_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly baseload power coming from the domestic hot water demand
        in kW/month for the whole simulation period.

        Returns
        -------
        baseload power domestic hot water : np.ndarray
            Baseload power domestic hot water for the whole simulation period
        """
        return np.divide(self.monthly_baseload_dhw_simulation_period, np.tile(self.UPM, self.simulation_period))

    @property
    def monthly_baseload_dhw(self) -> np.ndarray:
        """
        This function returns the monthly domestic hot water baseload in kWh/month for one year.

        Returns
        -------
        baseload domestic hot water : np.ndarray
            Baseload domestic hot water for one year
        """

        return np.mean(self.monthly_baseload_dhw_simulation_period.reshape((self.simulation_period, 12)), axis=0)

    @property
    def monthly_peak_dhw(self) -> np.ndarray:
        """
        This function returns the monthly domestic hot water peak in kW/month for one year.

        Returns
        -------
        peak domestic hot water : np.ndarray
            Peak domestic hot water for one year
        """
        return np.mean(self.monthly_baseload_dhw_power_simulation_period.reshape((self.simulation_period, 12)), axis=0)

    @property
    def yearly_average_dhw_load(self) -> float:
        """
        This function returns the average yearly DHW load in kWh.

        Returns
        -------
        float
            Yearly dhw load kWh/year
        """
        return np.sum(self.monthly_baseload_dhw)

    @property
    def yearly_dhw_load_simulation_period(self) -> np.array:
        """
        This function returns the yearly DHW demand in kWh/year for the whole simulation period.

        Returns
        -------
        yearly DHW : np.ndarray
            yearly DHW for the whole simulation period
        """
        return np.sum(np.reshape(self.monthly_baseload_dhw_simulation_period, (self.simulation_period, 12)), axis=1)
