from typing import TYPE_CHECKING


from abc import ABC, abstractmethod

from GHEtool.VariableClasses.BaseClass import BaseClass

if TYPE_CHECKING:
    import numpy as np
    from numpy.typing import NDArray


class LimitBase(BaseClass, ABC):

    def __init__(self, temp_min: any, temp_max: any, simulation_period: int):
        self._temp_min = temp_min
        self._temp_max = temp_max
        self._simulation_period: int = simulation_period

    @abstractmethod
    def set_simulation_period(self, period: int):
        """sets simulation period"""

    def get_simulation_period(self) -> int:
        """sets simulation period"""
        return self._simulation_period

    @abstractmethod
    def get_temp_max(self) -> NDArray[np.float64]:
        """gets the maximal temperature depending on the time"""

    @abstractmethod
    def get_temp_min(self) -> NDArray[np.float64]:
        """gets the minimal temperature depending on the time"""

    @abstractmethod
    def set_temp_max(self, temp_max: any):
        """set the maximal temperature depending on the time"""

    @abstractmethod
    def set_temp_min(self, temp_min: any):
        """set the minimal temperature depending on the time"""

    simulation_period = property(get_simulation_period, set_simulation_period)
    temp_max = property(get_temp_max, set_temp_max)
    temp_min = property(get_temp_min, set_temp_min)