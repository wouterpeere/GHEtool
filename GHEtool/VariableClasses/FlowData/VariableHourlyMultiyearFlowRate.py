import numpy as np

from GHEtool.VariableClasses.FluidData._FluidData import _FluidData
from GHEtool.VariableClasses.FlowData.VariableHourlyFlowRate import VariableHourlyFlowRate


class VariableHourlyMultiyearFlowRate(VariableHourlyFlowRate):

    def __init__(self, *, mfr: np.ndarray = None, vfr: np.ndarray = None, flow_per_borehole: bool = True,
                 series_factor: int = 1, simulation_period: int = 1, **kwargs) -> None:
        """

        Parameters
        ----------
        mfr : ndarray
            Array of hourly mass flow rate [kg/s]
        vfr : ndarray
            Array of hourly volume flow rate [l/s]
        flow_per_borehole : bool
            True if the flow rate is given for a single borehole, False if it is given for the entire borefield
        series_factor : int
            Number of boreholes in series to couple the flow rate per borehole to the flow rate of the entire borefield
        simulation_period : int
            Length of the simulation period [years]
        """

        self._mfr = mfr
        self._vfr = vfr
        self._flow_per_borehole = flow_per_borehole
        self._series_factor = series_factor
        self._simulation_period = simulation_period

        if self._mfr is not None and self._vfr is not None:
            raise ValueError('You cannot set both the mass flow rate and volume flow rate')

        if self._mfr is not None and len(self._mfr) != 8760 * simulation_period:
            raise ValueError(
                f'VariableHourlyFlowRate requires an input length of {8760 * simulation_period} values, but only {len(self._mfr)} are given.')
        if self._vfr is not None and len(self._vfr) != 8760 * simulation_period:
            raise ValueError(
                f'VariableHourlyFlowRate requires an input length of {8760 * simulation_period} values, but only {len(self._vfr)} are given.')

    def vfr_borehole(self, fluid_data: _FluidData = None, nb_of_boreholes: int = None, series_factor: int = 1,
                     **kwargs) -> np.ndarray:
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

        Returns
        -------
        np.ndarray
            Array of volume flow rate for the entire simulation period [l/s]

        Raises
        ------
        ValueError
            When the constant flow rates is given for the volume and no fluid_data or temperature is given as an argument.
        """
        return super().vfr_borehole(fluid_data, nb_of_boreholes, series_factor, self._simulation_period, **kwargs)

    def mfr_borehole(self, fluid_data: _FluidData = None, nb_of_boreholes: int = None, series_factor: int = 1,
                     **kwargs) -> np.ndarray:
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

        Returns
        -------
        np.ndarray
            Array of mass flow rates for the entire simulation period [kg/s]

        Raises
        ------
        ValueError
            When the constant flow rate is given for the volume and no fluid_data or temperature is given as an argument.
        """
        return super().mfr_borehole(fluid_data, nb_of_boreholes, series_factor, self._simulation_period, **kwargs)

    def vfr_borefield(self, fluid_data: _FluidData = None, nb_of_boreholes: int = None, series_factor: int = 1,
                      **kwargs) -> np.ndarray:
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

        Returns
        -------
        np.ndarray
            Array of volume flow rates for the entire simulation period [l/s]

        Raises
        ------
        ValueError
            When the constant flow rate is given for the volume and no fluid_data or temperature is given as an argument.
        """
        return super().vfr_borefield(fluid_data, nb_of_boreholes, series_factor, self._simulation_period, **kwargs)

    def mfr_borefield(self, fluid_data: _FluidData = None, nb_of_boreholes: int = None, series_factor: int = 1,
                      **kwargs) -> np.ndarray:
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


        Returns
        -------
        np.ndarray
            Array of mass flow rates for the entire simulation period [kg/s]

        Raises
        ------
        ValueError
            When the constant flow rate is given for the volume and no fluid_data or temperature is given as an argument.
        """
        return super().mfr_borefield(fluid_data, nb_of_boreholes, series_factor, self._simulation_period, **kwargs)
