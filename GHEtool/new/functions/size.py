from typing import Protocol
import numpy as np

class GroundData(Protocol):

    def calculate_Tg(self, h: float) -> float:
        ...

class GFunction(Protocol):

    def calculate_Rg(self, H: float, time: np.array) -> float:
        ...

class Pipe(Protocol):

    def calculate_Rb(self, h: float) -> float:
        ...

class Load(Protocol):
    hourly_heating_load: np.ndarray
    hourly_cooling_load: np.ndarray

class Limit(Protocol):

    simulation_period: int
    t_max: float
    t_min: float


def size(ground: GroundData, g_function: GFunction, pipe: Pipe, load: Load, limits: Limit) -> float:
    return 0