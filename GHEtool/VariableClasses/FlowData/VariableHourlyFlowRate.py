import numpy as np

from GHEtool.VariableClasses.FlowData._FlowData import _FlowData
from GHEtool.VariableClasses.FluidData._FluidData import _FluidData
from GHEtool.VariableClasses.BaseClass import BaseClass


class VariableHourlyFlowRate(_FlowData, BaseClass):

    def __init__(self, *, mfr: np.ndarray = None, vfr: np.ndarray = None, flow_per_borehole: bool = True,
                 series_factor: int = 1):
        """

        Parameters
        ----------
        mfr : np.ndarray
            Array of hourly mass flow rate [kg/s]
        vfr : np.ndarray
            Array of hourly volume flow rate [l/s]
        flow_per_borehole : bool
            True if the flow rate is given for a single borehole, False if it is given for the entire borefield
        series_factor : int
            Number of boreholes in series to couple the flow rate per borehole to the flow rate of the entire borefield
        """

        self._mfr = mfr
        self._vfr = vfr
        self._flow_per_borehole = flow_per_borehole
        self._series_factor = series_factor

        if self._mfr is not None and self._vfr is not None:
            raise ValueError('You cannot set both the mass flow rate and volume flow rate')

        if self._mfr is not None and len(self._mfr) != 8760:
            raise ValueError(
                f'VariableHourlyFlowRate requires an input length of 8760 values, but only {len(self._mfr)} are given.')
        if self._vfr is not None and len(self._vfr) != 8760:
            raise ValueError(
                f'VariableHourlyFlowRate requires an input length of 8760 values, but only {len(self._vfr)} are given.')

    def vfr_borehole(self, fluid_data: _FluidData = None, nb_of_boreholes: int = None, series_factor: int = None,
                     simulation_period: int = None, **kwargs) -> np.ndarray:
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
        simulation_period : int
            Number of years in the simulation period [-]

        Returns
        -------
        np.ndarray
            Array of volume flow rate for the entire simulation period [l/s]

        Raises
        ------
        ValueError
            When the constant flow rates is given for the volume and no fluid_data or temperature is given as an argument.
        """
        if simulation_period is None:
            raise ValueError('Please provide a simulation period.')
        if not self._flow_per_borehole and nb_of_boreholes is None:
            raise ValueError('The flow rate is given for the entire borefield but no number of boreholes is specified.')
        if self._vfr is not None:
            if self._flow_per_borehole:
                return np.tile(self._vfr, simulation_period)
            else:
                return np.tile(
                    self._vfr / nb_of_boreholes * (series_factor if series_factor is not None else self._series_factor),
                    simulation_period)
        if fluid_data is None:
            raise ValueError(
                'The volume flow rate is based on the mass flow rate, the fluid data is needed.')
        return self.mfr_borehole(nb_of_boreholes=nb_of_boreholes, series_factor=series_factor,
                                 simulation_period=simulation_period, **kwargs) / fluid_data.rho(**kwargs) * 1000

    def mfr_borehole(self, fluid_data: _FluidData = None, nb_of_boreholes: int = None, series_factor: int = None,
                     simulation_period: int = None, **kwargs) -> np.ndarray:
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
        simulation_period : int
            Number of years in the simulation period [-]

        Returns
        -------
        np.ndarray
            Array of mass flow rates for the entire simulation period [kg/s]

        Raises
        ------
        ValueError
            When the constant flow rate is given for the volume and no fluid_data or temperature is given as an argument.
        """
        if simulation_period is None:
            raise ValueError('Please provide a simulation period.')
        if not self._flow_per_borehole and nb_of_boreholes is None:
            raise ValueError('The flow rate is given for the entire borefield but no number of boreholes is specified.')
        if self._mfr is not None:
            if self._flow_per_borehole:
                return np.tile(self._mfr, simulation_period)
            else:
                return np.tile(
                    self._mfr / nb_of_boreholes * (series_factor if series_factor is not None else self._series_factor),
                    simulation_period)
        if fluid_data is None:
            raise ValueError(
                'The mass flow rate is based on the volume flow rate, so the fluid data is needed.')
        return self.vfr_borehole(nb_of_boreholes=nb_of_boreholes, series_factor=series_factor,
                                 simulation_period=simulation_period, **kwargs) / 1000 * fluid_data.rho(**kwargs)

    def vfr_borefield(self, fluid_data: _FluidData = None, nb_of_boreholes: int = None, series_factor: int = None,
                      simulation_period: int = None, **kwargs) -> np.ndarray:
        """
        This function returns the volume flow rate for a single borefield. Either based on a given mass flow rate,
        or calculated based on a volume flow rate.

        Parameters
        ----------
        fluid_data : _FluidData
            Fluid data class
        nb_of_boreholes : int
            Number of boreholes in the borefield. This is required when the flow rate is given for the entire borefield.
        series_factor : int
            Number of boreholes in series to couple the flow rate per borehole to the flow rate of the entire borefield.
        simulation_period : int
            Number of years in the simulation period [-]

        Returns
        -------
        np.ndarray
            Array of volume flow rates for the entire simulation period [l/s]

        Raises
        ------
        ValueError
            When the constant flow rate is given for the volume and no fluid_data or temperature is given as an argument.
        """
        if simulation_period is None:
            raise ValueError('Please provide a simulation period.')
        if self._flow_per_borehole and nb_of_boreholes is None:
            raise ValueError('The flow rate is given for the entire borefield but no number of boreholes is specified.')
        if self._vfr is not None:
            if self._flow_per_borehole:
                return np.tile(
                    self._vfr * nb_of_boreholes / (series_factor if series_factor is not None else self._series_factor),
                    simulation_period)
            else:
                return np.tile(self._vfr, simulation_period)
        if fluid_data is None:
            raise ValueError(
                'The volume flow rate is based on the mass flow rate, the fluid data is needed.')
        return self.mfr_borefield(nb_of_boreholes=nb_of_boreholes, series_factor=series_factor,
                                  simulation_period=simulation_period, **kwargs) / fluid_data.rho(**kwargs) * 1000

    def mfr_borefield(self, fluid_data: _FluidData = None, nb_of_boreholes: int = None, series_factor: int = None,
                      simulation_period: int = None, **kwargs) -> np.ndarray:
        """
        This function returns the mass flow rate for the entire borefield. Either based on a given mass flow rate,
        or calculated based on a volume flow rate.

        Parameters
        ----------
        fluid_data : _FluidData
            Fluid data class
        nb_of_boreholes : int
            Number of boreholes in the borefield. This is required when the flow rate is given for the entire borefield.
        series_factor : int
            Number of boreholes in series to couple the flow rate per borehole to the flow rate of the entire borefield.
        simulation_period : int
            Number of years in the simulation period [-]

        Returns
        -------
        np.ndarray
            Array of mass flow rates for the entire simulation period [kg/s]

        Raises
        ------
        ValueError
            When the constant flow rate is given for the volume and no fluid_data or temperature is given as an argument.
        """
        if simulation_period is None:
            raise ValueError('Please provide a simulation period.')
        if self._flow_per_borehole and nb_of_boreholes is None:
            raise ValueError('The flow rate is given for the entire borefield but no number of boreholes is specified.')
        if self._mfr is not None:
            if self._flow_per_borehole:
                return np.tile(
                    self._mfr * nb_of_boreholes / (series_factor if series_factor is not None else self._series_factor),
                    simulation_period)
            else:
                return np.tile(self._mfr, simulation_period)
        if fluid_data is None:
            raise ValueError(
                'The mass flow rate is based on the volume flow rate, so the fluid data is needed.')
        return self.vfr_borefield(nb_of_boreholes=nb_of_boreholes, series_factor=series_factor,
                                  simulation_period=simulation_period, **kwargs) / 1000 * fluid_data.rho(**kwargs)

    def check_values(self) -> bool:
        return self._vfr is not None or self._mfr is not None

    def __eq__(self, other):
        if not isinstance(other, VariableHourlyFlowRate):
            return False
        if ((self._vfr is None and other._vfr is not None or self._vfr is not None and other._vfr is None) or
                (self._mfr is None and other._mfr is not None or self._mfr is not None and other._mfr is None) or
                (self._mfr is not None and not np.allclose(self._mfr, other._mfr)) or
                (self._vfr is not None and not np.allclose(self._vfr, other._vfr))
                or self._series_factor != other._series_factor or
                self._flow_per_borehole != other._flow_per_borehole):
            return False
        return True

    def __export__(self):
        if self._mfr is not None:
            if self._flow_per_borehole:
                return {'type': 'Hourly mfr per borehole [kg/s]'}
            else:
                return {'type': 'Hourly mfr per borefield [kg/s]', 'series factor [-]': self._series_factor}
        if self._vfr is not None:
            if self._flow_per_borehole:
                return {'type': 'Hourly vfr per borehole [l/s]'}
            else:
                return {'type': 'Hourly vfr per borefield [l/s]', 'series factor [-]': self._series_factor}
