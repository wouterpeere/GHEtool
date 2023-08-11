"""
This file implements a Result class for temperature profiles.
"""
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class Results:
    peak_heating: np.ndarray = np.array([])
    peak_cooling: np.ndarray = np.array([])
    monthly_heating: np.ndarray = np.array([])
    monthly_cooling: np.ndarray = np.array([])
