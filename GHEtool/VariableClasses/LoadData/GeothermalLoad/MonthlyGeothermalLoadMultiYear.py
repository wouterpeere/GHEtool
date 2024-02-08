from __future__ import annotations

import numpy as np

from typing import TYPE_CHECKING

from GHEtool.VariableClasses.LoadData.GeothermalLoad.MonthlyGeothermalLoadAbsolute import MonthlyGeothermalLoadAbsolute
from GHEtool.logger.ghe_logger import ghe_logger

if TYPE_CHECKING:
    from numpy.typing import ArrayLike


class MonthlyGeothermalLoadMultiYear(MonthlyGeothermalLoadAbsolute):
    """
    This class contains all the information for geothermal load data with a monthly resolution and absolute input.
    This means that the inputs are both in kWh/month and kW/month.
    """

    def __init__(
        self,
        baseload_heating: ArrayLike | None = None,
        baseload_cooling: ArrayLike | None = None,
        peak_heating: ArrayLike | None = None,
        peak_cooling: ArrayLike | None = None,
        dhw: float = 0.0,
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
        dhw : float
            Yearly consumption of domestic hot water [kWh/year]
        """

        # set variables
        baseload_heating = np.zeros(12) if baseload_heating is None and baseload_cooling is None else baseload_heating
        baseload_heating = np.zeros_like(baseload_cooling) if baseload_heating is None else baseload_heating
        baseload_cooling = np.zeros_like(baseload_heating) if baseload_cooling is None else baseload_cooling
        peak_heating = np.zeros(12) if peak_heating is None and peak_cooling is None else peak_heating
        peak_heating = np.zeros_like(peak_cooling) if peak_heating is None else peak_heating
        peak_cooling = np.zeros_like(peak_heating) if peak_cooling is None else peak_cooling
        dhw = dhw
        super().__init__(baseload_heating, baseload_cooling, peak_heating, peak_cooling, dhw=dhw)

    def _check_input(self, load_array: ArrayLike) -> bool:
        """
        This function checks whether the input is valid or not.
        The input is correct if and only if:
        1) the input is a np.ndarray, list or tuple
        2) the length of the input is 12
        3) the input does not contain any negative values.

        Parameters
        ----------
        load_array : np.ndarray, list or tuple

        Returns
        -------
        bool
            True if the inputs are valid
        """
        if not isinstance(load_array, (np.ndarray, list, tuple)):
            ghe_logger.error("The load should be of type np.ndarray, list or tuple.")
            return False
        if not len(load_array) % 12 == 0:
            ghe_logger.error("The length of the load should be multiples of 12.")
            return False
        if np.min(load_array) < 0:
            ghe_logger.error("No value in the load can be smaller than zero.")
            return False
        return True

    @property
    def baseload_heating_power(self) -> np.ndarray:
        """
        This function returns the baseload heating in kW avg/month.

        Returns
        -------
        baseload heating : np.ndarray
        """
        return self.baseload_heating / 730

    @property
    def baseload_cooling_power(self) -> np.ndarray:
        """
        This function returns the baseload heating in kW avg/month.

        Returns
        -------
        baseload heating : np.ndarray
        """
        return self.baseload_cooling / 730

    @property
    def baseload_heating_simulation_period(self) -> np.ndarray:
        """
        This function returns the baseload heating in kWh/month for a whole simulation period.

        Returns
        -------
        baseload heating : np.ndarray
            baseload heating for the whole simulation period
        """
        return self.baseload_heating

    @property
    def baseload_cooling_simulation_period(self) -> np.ndarray:
        """
        This function returns the baseload cooling in kWh/month for a whole simulation period.

        Returns
        -------
        baseload cooling : np.ndarray
            baseload cooling for the whole simulation period
        """
        return self.baseload_cooling

    @property
    def peak_heating_simulation_period(self) -> np.ndarray:
        """
        This function returns the peak heating in kW/month for a whole simulation period.

        Returns
        -------
        peak heating : np.ndarray
            peak heating for the whole simulation period
        """
        return self.peak_heating

    @property
    def peak_cooling_simulation_period(self) -> np.ndarray:
        """
        This function returns the peak cooling in kW/month for a whole simulation period.

        Returns
        -------
        peak cooling : np.ndarray
            peak cooling for the whole simulation period
        """
        return self.peak_cooling

    @property
    def baseload_heating_power_simulation_period(self) -> np.ndarray:
        """
        This function returns the avergae heating power in kW avg/month for a whole simulation period.

        Returns
        -------
        average heating power : np.ndarray
            average heating power for the whole simulation period
        """
        return self.baseload_heating_power

    @property
    def baseload_cooling_power_simulation_period(self) -> np.ndarray:
        """
        This function returns the average cooling power in kW avg/month for a whole simulation period.

        Returns
        -------
        average cooling power : np.ndarray
            average cooling for the whole simulation period
        """
        return self.baseload_cooling_power

    @property
    def monthly_average_load_simulation_period(self) -> np.ndarray:
        """
        This function calculates the average monthly load in kW for the whole simulation period.

        Returns
        -------
        monthly average load : np.ndarray
        """
        return self.monthly_average_load

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
            self.simulation_period = int(len(load) / 12)
            return
        raise ValueError

    @property
    def baseload_heating(self) -> np.ndarray:
        """
        This function returns the baseload heating in kWh/month (incl. DHW).

        Returns
        -------
        baseload heating : np.ndarray
            Baseload heating values (incl. DHW) [kWh/month] for one year, so the length of the array is 12
        """
        return self.correct_for_start_month(self._baseload_heating + self.dhw * 730 / 8760)

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
            self.simulation_period = int(len(load) / 12)
            return
        raise ValueError
