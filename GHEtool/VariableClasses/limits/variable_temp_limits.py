from typing import List, TYPE_CHECKING

from GHEtool.VariableClasses.limits.limit_base_class import LimitBase
if TYPE_CHECKING:
    import numpy as np
    from numpy.typing import NDArray


class VariableTempLimits(LimitBase):

    def __init__(self, temp_min: List[float], temp_max: List[float], simulation_period: int):
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
        self._temp_max_array = np.tile(self._temp_max, self._simulation_period)

    def _update_temp_min_array(self):
        """update the temp min array from the new inputs"""
        self._temp_min_array = np.tile(self._temp_min, self._simulation_period)

    def get_temp_max(self) -> NDArray[np.float64]:
        """gets the maximal temperature depending on the time"""
        return self._temp_max_array

    def get_temp_min(self) -> NDArray[np.float64]:
        """gets the minimal temperature depending on the time"""
        return self._temp_min_array

    def set_temp_max(self, temp_max: List[float]):
        """set the maximal temperature depending on the time"""
        self._temp_max = temp_max
        self._update_temp_max_array()

    def set_temp_min(self, temp_min: List[float]):
        """set the minimal temperature depending on the time"""
        self._temp_min = temp_min
        self._update_temp_min_array()
