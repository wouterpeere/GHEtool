from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np

from GHEtool.VariableClasses.limits.limit_base_class import LimitBase
if TYPE_CHECKING:
    from numpy.typing import NDArray


class ConstantLimits(LimitBase):

    def __init__(self, temp_min: float, temp_max: float, simulation_period: int):
        super().__init__(temp_min, temp_max, simulation_period)
        self._time_step: int = 12
        self._update_temp_max_array()
        self._update_temp_min_array()

    def set_time_step(self, time_step: int):
        """
        set the time step within the year from the load data

        Parameters
        ----------
        time_step: int
            time step for example 12 for monthly data
        """

        self._time_step = time_step
        self._update_temp_max_array()
        self._update_temp_min_array()

    def set_simulation_period(self, period: int):
        """
        set the simulation period

        Parameters
        ----------
        period: int
            simulation period
        """
        self._simulation_period = period
        self._update_temp_max_array()
        self._update_temp_min_array()

    def _update_temp_max_array(self):
        """update the temp max array from the new inputs"""
        self._temp_max_array = np.ones(self._time_step * self._simulation_period) * self._temp_max

    def _update_temp_min_array(self):
        """update the temp min array from the new inputs"""
        self._temp_min_array = np.ones(self._time_step * self._simulation_period) * self._temp_min

    def get_temp_max(self) -> NDArray[np.float64]:
        """gets the maximal temperature depending on the time"""
        return self._temp_max_array

    def get_temp_min(self) -> NDArray[np.float64]:
        """gets the minimal temperature depending on the time"""
        return self._temp_min_array

    def set_temp_max(self, temp_max: float):
        """set the maximal temperature depending on the time"""
        self._temp_max = temp_max
        self._update_temp_max_array()

    def set_temp_min(self, temp_min: float):
        """set the minimal temperature depending on the time"""
        self._temp_min = temp_min
        self._update_temp_min_array()


    simulation_period = property(LimitBase.get_simulation_period, set_simulation_period)
    temp_max = property(get_temp_max, set_temp_max)
    temp_min = property(get_temp_min, set_temp_min)
