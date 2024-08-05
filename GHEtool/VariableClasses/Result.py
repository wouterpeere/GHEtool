"""
This file implements a Result class for temperature profiles.
"""
import abc
import numpy as np
from abc import ABC


class _Results(ABC):

    def __init__(self, borehole_wall_temp: np.ndarray = np.array([])):
        """
        Parameters
        ----------
        borehole_wall_temp : np.ndarray
            Borehole wall temperature [deg C]
        """
        self._Tb = borehole_wall_temp
        self.hourly = None

    @property
    def Tb(self) -> np.ndarray:
        return self._Tb

    @abc.abstractmethod
    def peak_heating(self) -> np.ndarray:
        return np.ndarray([])

    @abc.abstractmethod
    def peak_cooling(self) -> np.ndarray:
        return np.ndarray([])


class ResultsMonthly(_Results):
    """
    Class which contains the temperatures of the fluid and borehole wall with a monthly resolution.
    """

    def __init__(self,
                 borehole_wall_temp: np.ndarray = np.array([]),
                 peak_heating: np.ndarray = np.array([]),
                 peak_cooling: np.ndarray = np.array([]),
                 monthly_heating: np.ndarray = np.array([]),
                 monthly_cooling: np.ndarray = np.array([])):
        """

        Parameters
        ----------
        borehole_wall_temp : np.ndarray
            Borehole wall temperature [deg C]
        peak_heating : np.ndarray
            Average fluid temperature in peak heating [deg C]
        peak_cooling : np.ndarray
            Average fluid temperature in peak cooling [deg C]
        monthly_heating : np.ndarray
            Average temperature due to average monthly heating [deg C]
        monthly_cooling : np.ndarray
            Average temperature due to average monthly cooling [deg C]
        """
        self._peak_heating = peak_heating
        self._peak_cooling = peak_cooling
        self._monthly_heating = monthly_heating
        self._monthly_cooling = monthly_cooling

        super().__init__(borehole_wall_temp)
        self.hourly = False

    @property
    def peak_heating(self) -> np.ndarray:
        return self._peak_heating

    @property
    def peak_cooling(self) -> np.ndarray:
        return self._peak_cooling

    @property
    def monthly_heating(self) -> np.ndarray:
        return self._monthly_heating

    @property
    def monthly_cooling(self) -> np.ndarray:
        return self._monthly_cooling


class ResultsHourly(_Results):
    """
    Class which contains the temperatures of the fluid and borehole wall with an hourly resolution.
    """

    def __init__(self,
                 borehole_wall_temp: np.ndarray = np.array([]),
                 temperature_fluid: np.ndarray = np.array([])):
        """

        Parameters
        ----------
        borehole_wall_temp : np.ndarray
            Borehole wall temperature [deg C]
        temperature_fluid : np.ndarray
            Average fluid temperature [deg C]
        """
        self._Tf = temperature_fluid

        super().__init__(borehole_wall_temp)
        self.hourly = True

    @property
    def Tf(self) -> np.ndarray:
        return self._Tf

    @property
    def peak_heating(self) -> np.ndarray:
        return self.Tf

    @property
    def peak_cooling(self) -> np.ndarray:
        return self.Tf
