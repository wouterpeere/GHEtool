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
    def peak_extraction(self) -> np.ndarray:
        """

        Returns
        -------

        """

    @abc.abstractmethod
    def peak_injection(self) -> np.ndarray:
        """

        Returns
        -------

        """


class ResultsMonthly(_Results):
    """
    Class which contains the temperatures of the fluid and borehole wall with a monthly resolution.
    """

    def __init__(self,
                 borehole_wall_temp: np.ndarray = np.array([]),
                 peak_extraction: np.ndarray = np.array([]),
                 peak_injection: np.ndarray = np.array([]),
                 monthly_extraction: np.ndarray = np.array([]),
                 monthly_injection: np.ndarray = np.array([])):
        """

        Parameters
        ----------
        borehole_wall_temp : np.ndarray
            Borehole wall temperature [deg C]
        peak_extraction : np.ndarray
            Average fluid temperature in peak heating [deg C]
        peak_injection : np.ndarray
            Average fluid temperature in peak cooling [deg C]
        monthly_extraction : np.ndarray
            Average temperature due to average monthly heating [deg C]
        monthly_injection : np.ndarray
            Average temperature due to average monthly cooling [deg C]
        """
        self._peak_extraction = peak_extraction
        self._peak_injection = peak_injection
        self._monthly_extraction = monthly_extraction
        self._monthly_injection = monthly_injection

        super().__init__(borehole_wall_temp)
        self.hourly = False

    @property
    def peak_extraction(self) -> np.ndarray:
        return self._peak_extraction

    @property
    def peak_injection(self) -> np.ndarray:
        return self._peak_injection

    @property
    def monthly_extraction(self) -> np.ndarray:
        return self._monthly_extraction

    @property
    def monthly_injection(self) -> np.ndarray:
        return self._monthly_injection


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
    def peak_extraction(self) -> np.ndarray:
        return self.Tf

    @property
    def peak_injection(self) -> np.ndarray:
        return self.Tf
