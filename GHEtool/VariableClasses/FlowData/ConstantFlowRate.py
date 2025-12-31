import warnings

from GHEtool.VariableClasses.FlowData._FlowData import _FlowData
from GHEtool.VariableClasses.FluidData._FluidData import _FluidData
from GHEtool.VariableClasses.BaseClass import BaseClass


class ConstantFlowRate(_FlowData, BaseClass):

    def __init__(self, *, mfr: float = None, vfr: float = None, flow_per_borehole: bool = True, series_factor: int = 1):
        """

        Parameters
        ----------
        mfr : float
            Mass flow rate [kg/s]
        vfr : float
            Volume flow rate [l/s]
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

    def vfr_borehole(self, fluid_data: _FluidData = None, nb_of_boreholes: int = None, series_factor: int = 1,
                     **kwargs) -> float:
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
        float
            Volume flow rate [l/s]

        Raises
        ------
        ValueError
            When the constant flow rate is given for the volume and no fluid_data or temperature is given as an argument.
        """
        if not self._flow_per_borehole and nb_of_boreholes is None:
            raise ValueError('The flow rate is given for the entire borefield but no number of boreholes is specified.')
        if self._vfr is not None:
            if self._flow_per_borehole:
                return self._vfr
            else:
                return self._vfr / nb_of_boreholes * max(series_factor, self._series_factor)
        if fluid_data is None:
            raise ValueError(
                'The volume flow rate is based on the mass flow rate, the fluid data is needed.')
        return self.mfr_borehole(nb_of_boreholes=nb_of_boreholes, series_factor=series_factor,
                                 **kwargs) / fluid_data.rho(**kwargs) * 1000

    def mfr_borehole(self, fluid_data: _FluidData = None, nb_of_boreholes: int = None, series_factor: int = 1,
                     **kwargs) -> float:
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
        float
            Mass flow rate [kg/s]

        Raises
        ------
        ValueError
            When the constant flow rate is given for the volume and no fluid_data or temperature is given as an argument.
        """
        if not self._flow_per_borehole and nb_of_boreholes is None:
            raise ValueError('The flow rate is given for the entire borefield but no number of boreholes is specified.')
        if self._mfr is not None:
            if self._flow_per_borehole:
                return self._mfr
            else:
                return self._mfr / nb_of_boreholes * max(series_factor, self._series_factor)
        if fluid_data is None:
            raise ValueError(
                'The mass flow rate is based on the volume flow rate, so the fluid data is needed.')
        return self.vfr_borehole(nb_of_boreholes=nb_of_boreholes, series_factor=series_factor,
                                 **kwargs) / 1000 * fluid_data.rho(**kwargs)

    def vfr_borefield(self, fluid_data: _FluidData = None, nb_of_boreholes: int = None, series_factor: int = 1,
                      **kwargs) -> float:
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
        float
            Volume flow rate [l/s]

        Raises
        ------
        ValueError
            When the constant flow rate is given for the volume and no fluid_data or temperature is given as an argument.
        """
        if self._flow_per_borehole and nb_of_boreholes is None:
            raise ValueError('The flow rate is given for the entire borefield but no number of boreholes is specified.')
        if self._vfr is not None:
            if self._flow_per_borehole:
                return self._vfr * nb_of_boreholes / max(series_factor, self._series_factor)
            else:
                return self._vfr
        if fluid_data is None:
            raise ValueError(
                'The volume flow rate is based on the mass flow rate, the fluid data is needed.')
        return self.mfr_borefield(nb_of_boreholes=nb_of_boreholes, series_factor=series_factor,
                                  **kwargs) / fluid_data.rho(**kwargs) * 1000

    def mfr_borefield(self, fluid_data: _FluidData = None, nb_of_boreholes: int = None, series_factor: int = 1,
                      **kwargs) -> float:
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
        float
            Mass flow rate [kg/s]

        Raises
        ------
        ValueError
            When the constant flow rate is given for the volume and no fluid_data or temperature is given as an argument.
        """
        if self._flow_per_borehole and nb_of_boreholes is None:
            raise ValueError('The flow rate is given for the entire borefield but no number of boreholes is specified.')
        if self._mfr is not None:
            if self._flow_per_borehole:
                return self._mfr * nb_of_boreholes / max(series_factor, self._series_factor)
            else:
                return self._mfr
        if fluid_data is None:
            raise ValueError(
                'The mass flow rate is based on the volume flow rate, so the fluid data is needed.')
        return self.vfr_borefield(nb_of_boreholes=nb_of_boreholes, series_factor=series_factor,
                                  **kwargs) / 1000 * fluid_data.rho(**kwargs)

    def vfr(self, fluid_data: _FluidData = None, **kwargs) -> float:
        """
        This function returns the volume flow rate. Either based on a given mass flow rate,
        or calculated based on a volume flow rate.

        Parameters
        ----------
        fluid_data : _FluidData
            Fluid data class

        Returns
        -------
        float
            Volume flow rate [l/s]

        Raises
        ------
        ValueError
            When the constant flow rate is given for the volume and no fluid_data or temperature is given as an argument.
        """
        warnings.warn(DeprecationWarning(
            'The mfr and vfr functions are depreciated and will be removed in v2.5.0. Please use mfr_borehole or mfr_borefield instead.'))
        if self._vfr is not None:
            return self._vfr
        if fluid_data is None:
            raise ValueError(
                'The volume flow rate is based on the mass flow rate, the fluid data is needed.')
        return self.mfr(**kwargs) / fluid_data.rho(**kwargs) * 1000

    def mfr(self, fluid_data: _FluidData = None, **kwargs) -> float:
        """
        This function returns the mass flow rate. Either based on a given mass flow rate,
        or calculated based on a volume flow rate.

        Parameters
        ----------
        fluid_data : _FluidData
            Fluid data class

        Returns
        -------
        float
            Mass flow rate [kg/s]

        Raises
        ------
        ValueError
            When the constant flow rate is given for the volume and no fluid_data or temperature is given as an argument.
        """
        warnings.warn(DeprecationWarning(
            'The mfr and vfr functions are depreciated and will be removed in v2.5.0. Please use mfr_borehole or mfr_borefield instead.'))
        if self._mfr is not None:
            return self._mfr
        if fluid_data is None:
            raise ValueError(
                'The mass flow rate is based on the volume flow rate, so the fluid data is needed.')
        return self.vfr(**kwargs) / 1000 * fluid_data.rho(**kwargs)

    def check_values(self) -> bool:
        return self._vfr is not None or self._mfr is not None

    def __eq__(self, other):
        if not isinstance(other, ConstantFlowRate):
            return False
        if (self._vfr != other._vfr or self._mfr != other._mfr or self._series_factor != other._series_factor or
                self._flow_per_borehole != other._flow_per_borehole):
            return False
        return True

    def __export__(self):
        if self._mfr is not None:
            if self._flow_per_borehole:
                return {'mfr per borehole [kg/s]': self.mfr_borehole()}
            else:
                return {'mfr per borefield [kg/s]': self.mfr_borefield(), 'series factor [-]': self._series_factor}
        if self._vfr is not None:
            if self._flow_per_borehole:
                return {'vfr per borehole [l/s]': self.vfr_borehole()}
            else:
                return {'vfr per borefield [l/s]': self.vfr_borefield(), 'series factor [-]': self._series_factor}
