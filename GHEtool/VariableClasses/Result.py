"""
This file implements a Result class for temperature profiles.
"""
import numpy as np


class Results:

    def __init__(self,
                 peak_heating: np.ndarray = np.array([]),
                 peak_cooling: np.ndarray = np.array([]),
                 monthly_heating: np.ndarray = np.array([]),
                 monthly_cooling: np.ndarray = np.array([])):
        self._peak_heating = peak_heating
        self._peak_cooling = peak_cooling
        self._monthly_heating = monthly_heating
        self._monthly_cooling = monthly_cooling

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
