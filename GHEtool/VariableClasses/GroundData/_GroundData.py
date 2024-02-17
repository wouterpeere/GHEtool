import abc
import warnings

import numpy as np
from abc import ABC
from GHEtool.VariableClasses.BaseClass import BaseClass
from typing import Union, List


class GroundLayer(BaseClass):
    """
    Contains the information about a certain ground layer.
    """

    __slots__ = "k_s", "volumetric_heat_capacity", "thickness"

    def __init__(self, k_s: float = None,
                 volumetric_heat_capacity: float = 2.4 * 10**6,
                 thickness: float = None):
        """

        Parameters
        ----------
        k_s : float
            Layer thermal conductivity [W/mK]
        volumetric_heat_capacity : float
            Layer volumetric heat capacity [J/m³K]
        thickness : float
            Layer thickness [m]. None is assumed infinite depth
        """
        self.k_s: float = self.non_negative(k_s)
        self.volumetric_heat_capacity: float = self.non_negative(volumetric_heat_capacity)
        self.thickness: float = self.non_negative(thickness)

    def non_negative(self, value) -> float:
        """
        This function returns the value if the value > 0.
        Otherwise, an error is raised.

        Parameters
        ----------
        value : float
            Value to be checked

        Returns
        -------
        float
            Value

        Raises
        ------
        ValueError
            When the value equals 0 or is smaller
        """
        if value is None or value > 0:
            return value
        raise ValueError(f'The value {value} is smaller or equal to 0.')

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        for i in self.__slots__:
            if getattr(self, i) != getattr(other, i):
                return False
        return True


class _GroundData(BaseClass, ABC):
    """
    Contains information regarding the ground data of the borefield.
    """

    __slots__ = 'layers', 'layer_depths', 'variable_Tg', 'Tg', 'last_layer_infinite'

    def __init__(self, k_s: float = None,
                 volumetric_heat_capacity: float = 2.4 * 10**6):
        """

        Parameters
        ----------
        k_s : float
            Ground thermal conductivity [W/mK]
        volumetric_heat_capacity : float
            The volumetric heat capacity of the ground [J/m3K]
        """

        self.layers: List[GroundLayer] = []
        self.layer_depths: list = []
        self.variable_Tg: bool = False
        self.Tg: float = 10
        self.last_layer_infinite: bool = True  # assumes that the last ground layer is infinite

        if k_s is not None:
            self.add_layer_on_bottom(GroundLayer(k_s, volumetric_heat_capacity, thickness=None))

    def add_layer_on_top(self, layer: Union[GroundLayer, List[GroundLayer]]) -> None:
        """
        This function adds a ground layer on the top of the array. This hence becomes the highest
        ground layer.

        Parameters
        ----------
        layer : GroundLayer or list of ground layers
            GroundLayer object with thermal properties of this layer

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When you add a ground layer with no specified depth and there are already ground layers in the array
        """
        if not isinstance(layer, GroundLayer):
            for i in layer:
                self.add_layer_on_top(i)
            return
        # check if previous layer has a thickness different from None
        if np.any(self.layers):
            if layer.thickness is None:
                raise ValueError('You cannot add a layer on top of another layer if you have an undetermined depth.')

        self.layers.insert(0, layer)
        self.layer_depths = [0]
        for idx, layer in enumerate(self.layers):
            if layer.thickness is None:
                continue
            self.layer_depths.append(self.layer_depths[idx] + layer.thickness)

    def add_layer_on_bottom(self, layer: Union[GroundLayer, List[GroundLayer]]) -> None:
        """
        This function adds a ground layer on the bottom of the array. This hence becomes the deepest
        ground layer.

        Parameters
        ----------
        layer : GroundLayer or list of ground layers
            GroundLayer object with thermal properties of this layer

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When you add a ground layer on the bottom of a layer which has no predefined depth
        """
        if not isinstance(layer, GroundLayer):
            for i in layer:
                self.add_layer_on_bottom(i)
            return
        # check if previous layer has a thickness different from None
        if np.any(self.layers):
            if self.layers[-1].thickness is None:
                raise ValueError('You cannot add a layer on bottom of a layer which has un undetermined depth.')

        self.layers.append(layer)
        self.layer_depths.append(0 if len(self.layers) == 1 else self.layers[-2].thickness + self.layer_depths[-1])

    def check_depth(self, H: float) -> bool:
        """
        Checks if the depth is correct.
        A depth is False when it is lower than 0 or it exceeds the deepest ground layer and
        last_layer_infinite is set to False.

        Parameters
        ----------
        H : float
            Depth [m]

        Returns
        -------
        bool
            True if the depth is valid

        Raises
        ------
        ValueError
            When a depth is requested that is either smaller than zero or larger than the maximum depth.
        """
        if not np.any(self.layers):
            raise ValueError('There is no ground data available.')

        if self.layers[-1].thickness is None:
            # last layer is unbounded
            return True

        highest_depth = self.layer_depths[-1] + self.layers[-1].thickness
        if H <= highest_depth:
            return True

        if not self.last_layer_infinite:
            raise ValueError(f'The depth of {H}m exceeds the maximum depth that is provided: {highest_depth}m. '
                             f'One can set the last_layer_infinite assumption to True in the ground class.')

        warnings.warn(f'The depth of {H}m exceeds the maximum depth that is provided: {highest_depth}m. '
                             f'In order to continue, it is assumed the deepest layer is infinite.')
        return True

    def calculate_value(self, thickness_list: list, cumulative_thickness_list: list, y_range: list, H: float) -> float:
        """
        This function calculates the average value of a certain y_range of values for a certain depth,
        given the thickness of the ground layers.

        Parameters
        ----------
        thickness_list : list
            List of all the layer thicknesses
        cumulative_thickness_list : list
            Cumulative sum of all the layer thicknesses
        y_range : list
            Range with the values for each layer
        H : float
            Depth [m]

        Returns
        -------
        float
            Calculated value for either k_s or volumetric heat capacity
        """
        if H <= 0:
            # For negative values, the first conductivity is returned
            return y_range[0]

        result = 0

        idx_of_layer_in_which_H_falls = [i for i, v in enumerate(cumulative_thickness_list) if v <= H][-1]
        for idx, val in enumerate(y_range[:idx_of_layer_in_which_H_falls]):
            result += val * thickness_list[idx + 1] / H

        result += y_range[idx_of_layer_in_which_H_falls] * (H - cumulative_thickness_list[idx_of_layer_in_which_H_falls]) / H
        return result

    def k_s(self, H: float = 100) -> float:
        """
        Returns the ground thermal conductivity in W/mK for a given depth.

        Parameters
        ----------
        H : float
            Depth in meters.

        Returns
        -------
        float
            Ground thermal conductivity in W/mK for a given depth.
        """
        self.check_depth(H)
        if len(self.layers) == 1 and (self.layers[0].thickness is None or self.last_layer_infinite):
            return self.layers[0].k_s
        return self.calculate_value([0] + [layer.thickness for layer in self.layers], self.layer_depths, [layer.k_s for layer in self.layers], H)

    def volumetric_heat_capacity(self, H: float = 100) -> float:
        """
        Returns the ground volumetric heat capacity in J/m³K for a given depth.

        Parameters
        ----------
        H : float
            Depth in meters.

        Returns
        -------
        float
            Ground volumetric heat capacity in J/m³K for a given depth.
        """
        self.check_depth(H)
        if len(self.layers) == 1 and (self.layers[0].thickness is None or self.last_layer_infinite):
            return self.layers[0].volumetric_heat_capacity
        return self.calculate_value([0] + [layer.thickness for layer in self.layers], self.layer_depths, [layer.volumetric_heat_capacity for layer in self.layers], H)

    def alpha(self, H: float = 100) -> float:
        """
        Returns the ground thermal diffusivity in m²/s for a given depth.
        If no volumetric heat capacity or conductivity is given, None is returned.

        Parameters
        ----------
        H : float
            Depth in meters.

        Returns
        -------
        float
            Ground thermal diffusivity in m²/s for a given depth.
        """

        if not np.any(self.layers):
            return None
        else:
            return self.k_s(H) / self.volumetric_heat_capacity(H)  # m2/s

    @abc.abstractmethod
    def calculate_Tg(self, H: float) -> float:
        """
        This function gives back the ground temperature

        Parameters
        ----------
        H : float
            Depth of the borefield [m]

        Returns
        -------
        Tg : float
            Ground temperature [deg C]
        """

    @abc.abstractmethod
    def calculate_delta_H(self, temperature_diff: float) -> float:
        """
        This function calculates the difference in depth for a given difference in temperature.

        Parameters
        ----------
        temperature_diff : float
            Difference in temperature [deg C]

        Returns
        -------
        Difference in depth [m] : float
        """

    def max_depth(self, max_temp: float) -> float:
        """
        This function returns the maximum depth, based on the maximum temperature.
        The maximum is the depth where the ground temperature equals the maximum temperature limit.

        Parameters
        ----------
        max_temp : float
            Maximum temperature [deg C]

        Returns
        -------
        Depth : float
            Maximum depth [m]
        """
        return self.calculate_delta_H(max_temp-self.Tg)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        for i in self.__slots__:
            if getattr(self, i) != getattr(other, i):
                return False
        return True
