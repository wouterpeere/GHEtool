from GHEtool.VariableClasses.FlowData._FlowData import _FlowData
from GHEtool.VariableClasses.FluidData._FluidData import _FluidData
from GHEtool.VariableClasses.BaseClass import BaseClass


class ConstantFlowRate(_FlowData, BaseClass):

    def __init__(self, *, mfr: float = None, vfr: float = None):
        """

        Parameters
        ----------
        mfr : float
            Mass flow rate [kg/s]
        vfr : float
            Volume flow rate [l/s]
        """

        self._mfr = mfr
        self._vfr = vfr

        if self._mfr is not None and self._vfr is not None:
            raise ValueError('You cannot set both the mass flow rate and volume flow rate')

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
        if self._vfr != other._vfr or self._mfr != other._mfr:
            return False
        return True

    def __export__(self):
        if self._mfr is not None:
            return {'mfr [kg/s]': self.mfr()}
        if self._vfr is not None:
            return {'vfr [l/s]': self.vfr()}
