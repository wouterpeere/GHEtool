import numpy as np

from GHEtool.VariableClasses.FlowData._FlowData import _FlowData
from GHEtool.VariableClasses.FluidData._FluidData import _FluidData
from GHEtool.VariableClasses.BaseClass import BaseClass
from typing import Union


class ConstantDeltaTFlowRate(_FlowData, BaseClass):

    def __init__(self, *, delta_temp_extraction: float = 4, delta_temp_injection: float = 4, series_factor: int = 1,
                 **kwargs):
        """

        Parameters
        ----------
        delta_temp_extraction : float
            (Positive) temperature difference between the borehole outlet and inlet temperature during extraction [°C]
        delta_temp_injection : float
            (Positive) temperature difference between the borehole inlet and outlet temperature during injection [°C]
        series_factor : int
            Number of boreholes in series to couple the flow rate per borehole to the flow rate of the entire borefield
        """

        self._delta_temp_heating = delta_temp_extraction
        self._delta_temp_cooling = delta_temp_injection
        self._series_factor = series_factor

        if series_factor < 1:
            raise ValueError('The series factor cannot be less than 1.')

        if delta_temp_extraction <= 0 or delta_temp_injection <= 0:
            raise ValueError('The temperature difference should be always greater than 0.')

    def vfr_borehole(self, fluid_data: _FluidData = None, nb_of_boreholes: int = None, series_factor: int = None,
                     power: Union[float, np.ndarray] = None, **kwargs) -> Union[float, np.ndarray]:
        """
        This function returns the volume flow rate for a single borefield for the entire simulation period.
        Either based on a given mass flow rate, or calculated based on a volume flow rate.

        Parameters
        ----------
        fluid_data : _FluidData
            Fluid data class
        nb_of_boreholes : int
            Number of boreholes in the borefield. This is required when the flow rate is given for the entire borefield.
        series_factor : int
            Number of boreholes in series to couple the flow rate per borehole to the flow rate of the entire borefield.
        power : float | np.ndarray
            Power of the entire borefield, positive when injection, negative during extraction [kW]

        Returns
        -------
        np.ndarray
            Array of volume flow rate for the entire simulation period [l/s]

        Raises
        ------
        ValueError
            When the constant flow rates is given for the volume and no fluid_data or temperature is given as an argument.
        """
        if nb_of_boreholes is None:
            raise ValueError('The flow rate is given for the entire borefield but no number of boreholes is specified.')
        return self.vfr_borefield(fluid_data=fluid_data, power=power, **kwargs) / nb_of_boreholes * (
            series_factor if series_factor is not None else self._series_factor)

    def mfr_borehole(self, fluid_data: _FluidData = None, nb_of_boreholes: int = None, series_factor: int = None,
                     power: Union[float, np.ndarray] = None, **kwargs) -> np.ndarray:
        """
        This function returns the mass flow rate for a single borehole. Either based on a given mass flow rate,
        or calculated based on a volume flow rate.

        Parameters
        ----------
        fluid_data : _FluidData
            Fluid data class
        nb_of_boreholes : int
            Number of boreholes in the borefield. This is required when the flow rate is given for the entire borefield.
        series_factor : int
            Number of boreholes in series to couple the flow rate per borehole to the flow rate of the entire borefield.
        power : float | np.ndarray
            Power of the entire borefield, positive when injection, negative during extraction [kW]

        Returns
        -------
        np.ndarray
            Array of mass flow rates for the entire simulation period [kg/s]

        Raises
        ------
        ValueError
            When the constant flow rate is given for the volume and no fluid_data or temperature is given as an argument.
        """
        if nb_of_boreholes is None:
            raise ValueError('The flow rate is given for the entire borefield but no number of boreholes is specified.')
        return self.mfr_borefield(fluid_data=fluid_data, power=power, **kwargs) / nb_of_boreholes * (
            series_factor if series_factor is not None else self._series_factor)

    def vfr_borefield(self, fluid_data: _FluidData = None, power: Union[float, np.ndarray] = None,
                      **kwargs) -> np.ndarray:
        """
        This function returns the volume flow rate for a single borefield. Either based on a given mass flow rate,
        or calculated based on a volume flow rate.

        Parameters
        ----------
        fluid_data : _FluidData
            Fluid data class
        power : float | np.ndarray
            Power of the entire borefield, positive when injection, negative during extraction [kW]

        Returns
        -------
        np.ndarray
            Array of volume flow rates for the entire simulation period [l/s]

        Raises
        ------
        ValueError
            When the constant flow rate is given for the volume and no fluid_data or temperature is given as an argument.
        """
        return self.mfr_borefield(fluid_data=fluid_data, power=power, **kwargs) / fluid_data.rho(**kwargs) * 1000

    def mfr_borefield(self, fluid_data: _FluidData = None, power: Union[float, np.ndarray] = None,
                      **kwargs) -> np.ndarray:
        """
        This function returns the mass flow rate for the entire borefield. Either based on a given mass flow rate,
        or calculated based on a volume flow rate.

        Parameters
        ----------
        fluid_data : _FluidData
            Fluid data class
        power : float | np.ndarray
            Power of the entire borefield, positive when injection, negative during extraction [kW]

        Returns
        -------
        np.ndarray
            Array of mass flow rates for the entire simulation period [kg/s]

        Raises
        ------
        ValueError
            When the constant flow rate is given for the volume and no fluid_data or temperature is given as an argument.
        """
        if power is None:
            raise ValueError('Please provide a valid (array of) powers to calculate the flow rate')
        if fluid_data is None:
            raise ValueError('Fluid data is required to calculate the flow rate.')

        power = np.asarray(power)

        deltaT = np.where(power >= 0, self._delta_temp_heating, self._delta_temp_cooling)

        return np.abs(power) / (fluid_data.cp(**kwargs) / 1000 * deltaT)

    def check_values(self) -> bool:
        return self._delta_temp_cooling is not None or self._delta_temp_heating is not None

    def __eq__(self, other):
        if not isinstance(other, ConstantDeltaTFlowRate):
            return False
        if (
                self._delta_temp_cooling != other._delta_temp_cooling or self._delta_temp_heating != other._delta_temp_heating
                or self._series_factor != other._series_factor):
            return False
        return True

    def __export__(self):
        return {'type': 'Constant delta T flow rate',
                'delta T in heating': self._delta_temp_heating,
                'delta T in cooling': self._delta_temp_cooling,
                'series factor': self._series_factor
                }
