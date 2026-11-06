import warnings

import numpy as np
from typing import List, Union

from GHEtool.VariableClasses.GroundData._GroundData import _GroundData, GroundLayer


class GroundLayeredTemperature(_GroundData):
    """
    Ground data with a temperature per ground layer.

    Each GroundLayer has a `temperature` [deg C], the temperature at the top of that layer.
    Within a layer, the temperature varies linearly from its own temperature to the temperature
    at the top of the next layer.

    The last layer has no temperature below it. Its gradient follows from the geothermal heat flux,
    calculated from the second-to-last layer:

        q = k_(n-2) * (T_(n-1) - T_(n-2)) / thickness_(n-2)     [W/m2]
        gradient_last_layer = q / k_(n-1)                        [K/m]

    This gradient is also used below the last layer when its thickness is None or when the depth
    exceeds it (last_layer_infinite). With only one layer, the ground temperature is constant.

    Because the temperature profile is piecewise linear, the average ground temperature is
    calculated exactly (no discretisation).
    """
    __slots__ = _GroundData.__slots__

    def __init__(self, k_s: float = None,
                 volumetric_heat_capacity: float = 2.4 * 10 ** 6):
        """

        Parameters
        ----------
        k_s : float
            Ground thermal conductivity [W/mK]
        volumetric_heat_capacity : float
            The volumetric heat capacity of the ground [J/m3K]
        """
        super().__init__(k_s=k_s, volumetric_heat_capacity=volumetric_heat_capacity)
        self.variable_Tg = True

    def add_layer_on_top(self, layer: Union[GroundLayer, List[GroundLayer]]) -> None:
        super().add_layer_on_top(layer)
        self._update_Tg()

    def add_layer_on_bottom(self, layer: Union[GroundLayer, List[GroundLayer]]) -> None:
        super().add_layer_on_bottom(layer)
        self._update_Tg()

    def _update_Tg(self) -> None:
        """Keep Tg equal to the temperature at the ground surface (top of the first layer)."""
        if self.layers and self.layers[0].temperature is not None:
            self.Tg = self.layers[0].temperature

    def _check_temperatures(self) -> None:
        """
        Raises
        ------
        ValueError
            When there are no layers or when a layer has no temperature
        """
        if not np.any(self.layers):
            raise ValueError('There is no ground data available.')
        for idx, layer in enumerate(self.layers):
            if layer.temperature is None:
                raise ValueError(f'Ground layer {idx + 1} has no temperature.')

    @property
    def geothermal_heat_flux(self) -> float:
        """
        Geothermal heat flux [W/m2], calculated from the second-to-last ground layer.
        A positive value means the temperature increases with depth.
        With only one layer, the heat flux is 0.

        Returns
        -------
        float
            Geothermal heat flux [W/m2]
        Warns
        -----
        UserWarning
            When the heat flux is negative, i.e. the temperature decreases with depth in the last layer
        """
        self._check_temperatures()
        if len(self.layers) < 2:
            return 0.
        top, bottom = self.layers[-2], self.layers[-1]
        flux = top.k_s * (bottom.temperature - top.temperature) / top.thickness
        if flux < 0:
            warnings.warn(f'The geothermal heat flux is negative ({flux:.3f} W/m²): the ground temperature decreases '
                          f'with depth in the last ground layer. Please check the layer temperatures.')
        return flux

    @property
    def gradient_last_layer(self) -> float:
        """
        Temperature gradient in the last ground layer (and below) [K/m].

        Returns
        -------
        float
            Temperature gradient [K/m]
        """
        return self.geothermal_heat_flux / self.layers[-1].k_s

    def temperature_at_depth(self, depth: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        This function gives back the undisturbed ground temperature at a certain depth.

        Parameters
        ----------
        depth : float or np.ndarray
            Depth [m]

        Returns
        -------
        float or np.ndarray
            Ground temperature [deg C]
        """
        self._check_temperatures()
        layer_tops = np.asarray(self.layer_depths, dtype=float)
        temperatures = np.array([layer.temperature for layer in self.layers], dtype=float)

        depth = np.asarray(depth, dtype=float)
        result = np.interp(depth, layer_tops, temperatures)
        # in (and below) the last layer: gradient from the geothermal heat flux
        in_last_layer = depth > layer_tops[-1]
        result = np.where(in_last_layer,
                          temperatures[-1] + self.gradient_last_layer * (depth - layer_tops[-1]),
                          result)
        return float(result) if result.ndim == 0 else result

    def calculate_Tg(self, depth: float = 100, start_depth: float = 0) -> float:
        """
        This function gives back the average ground temperature for the borehole.

        Parameters
        ----------
        depth : float
            Depth of the borehole [m]
        start_depth : float
            Depth at which the borehole starts [m]

        Returns
        -------
        Tg : float
            Ground temperature [deg C]
        """
        self.check_depth(depth)
        if depth <= start_depth:
            return self.temperature_at_depth(depth)

        # integration points: borehole ends + all layer boundaries in between
        layer_tops = np.asarray(self.layer_depths, dtype=float)
        inner = layer_tops[(layer_tops > start_depth) & (layer_tops < depth)]
        z = np.concatenate(([start_depth], inner, [depth]))
        t = self.temperature_at_depth(z)

        # trapezoidal rule is exact for a piecewise-linear profile
        return float(np.sum(0.5 * (t[1:] + t[:-1]) * np.diff(z)) / (depth - start_depth))

    def calculate_delta_H(self, temperature_diff: float, H: float = 100) -> float:
        """
        This function calculates the difference in depth for a given difference in temperature.
        It linearises the average ground temperature (from the surface to H) around depth H.

        Parameters
        ----------
        temperature_diff : float
            Difference in temperature [deg C]
        H : float
            Depth around which the average ground temperature is linearised [m]

        Returns
        -------
        float
            Difference in depth [m]. Infinite when the average ground temperature does not change with depth.
        """
        # d(Tavg)/dH for Tavg = 1/H * integral_0^H T(z) dz
        derivative = (self.temperature_at_depth(H) - self.calculate_Tg(H, 0)) / H
        if np.isclose(derivative, 0):
            return np.inf
        return temperature_diff / derivative

    def max_depth(self, max_temp: float) -> float:
        """
        This function returns the maximum borehole depth, based on the maximum temperature.
        The maximum is the depth where the average ground temperature (from the surface) equals the
        maximum temperature limit. Since the profile is not necessarily linear, this is solved numerically.

        Parameters
        ----------
        max_temp : float
            Maximum temperature [deg C]

        Returns
        -------
        Depth : float
            Maximum depth [m]. Infinite when the limit is never reached.
        """
        f = lambda H: self.calculate_Tg(H, 0) - max_temp
        if self.temperature_at_depth(0) >= max_temp:
            # limit already reached at the surface
            return 0.
        # bracket the first crossing by doubling the depth
        low, high = 1e-6, 1.
        while f(high) < 0:
            low, high = high, high * 2
            if high > 1e5:
                return np.inf
        # bisection (bracket is at most 1e5 m, so this takes at most ~37 iterations)
        while high - low > 1e-6:
            mid = (low + high) / 2
            if f(mid) < 0:
                low = mid
            else:
                high = mid
        return (low + high) / 2

    def __export__(self):
        if len(self.layers) == 1:
            return {
                'type': 'Ground layered temperature',
                'Conductivity [W/(m·K)]': self.layers[0].k_s,
                'Volumetric heat capacity [MJ/(m³·K)]': self.layers[0].volumetric_heat_capacity / 10 ** 6,
                'Temperature [°C]': self.layers[0].temperature
            }
        temp = {
            'type': 'Ground layered temperature',
        }
        temp.update(super().__export__())
        return temp
