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
                 efficiency_dhw: Union[int, float, COP, SCOP] = 4):
        super().__init__()

        # initiate variables
        self._baseload_heating: np.ndarray = np.zeros(12)
        self._baseload_cooling: np.ndarray = np.zeros(12)
        self._peak_heating: np.ndarray = np.zeros(12)
        self._peak_cooling: np.ndarray = np.zeros(12)
        self._dhw: np.ndarray = np.zeros(12)

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
        return self._cop

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
        return self._cop

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
            self._cop = SCOP(efficiency_dhw)
            return
        self._cop = efficiency_dhw

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
        if len(results.Tb) != self.simulation_period * (8760 if self._hourly else 12):
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
    def results(self) -> Union[tuple, np.ndarray]:
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
    def conversion_factor_secondary_to_primary_cooling(eer_value: np.ndarray):
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
        return self.monthly_baseload_cooling_simulation_period

    @property
    def monthly_baseload_extraction_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly extraction baseload in kWh/month for the whole simulation period.

        Returns
        -------
        baseload extraction : np.ndarray
            Baseload extraction for the whole simulation period
        """
        ## include DHW
        return self.monthly_baseload_heating_simulation_period

    @property
    def monthly_peak_injection_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly injection peak in kW/month for the whole simulation period.

        Returns
        -------
        peak injection : np.ndarray
            Peak injection for the whole simulation period
        """
        return self.monthly_peak_cooling_simulation_period

    @property
    def monthly_peak_extraction_simulation_period(self) -> np.ndarray:
        """
        This function returns the monthly extraction peak in kW/month for the whole simulation period.

        Returns
        -------
        peak extraction : np.ndarray
            Peak extraction for the whole simulation period
        """
        ## include DHW
        return self.monthly_peak_heating_simulation_period

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
