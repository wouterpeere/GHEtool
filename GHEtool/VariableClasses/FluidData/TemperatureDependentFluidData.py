import numpy as np

from scp.ethyl_alcohol import EthylAlcohol
from scp.ethylene_glycol import EthyleneGlycol
from scp.methyl_alcohol import MethylAlcohol
from scp.propylene_glycol import PropyleneGlycol
from scp.water import Water
from scp.base_melinder import BaseMelinder

from GHEtool.VariableClasses.FluidData._FluidData import _FluidData
from GHEtool.VariableClasses.FluidData.ConstantFluidData import ConstantFluidData
from GHEtool.VariableClasses.BaseClass import BaseClass
from typing import Optional


class TemperatureDependentFluidData(_FluidData, BaseClass):
    """
    Contains information regarding the fluid data of the borefield, assuming there is temperature dependency.
    """

    NB_OF_SAMPLES = 500

    __slots__ = '_name', '_percentage'

    def __init__(self, name: str, percentage: float):
        """

        Parameters
        ----------
        name : str
            Name of the antifreeze. Currently, there is: Water, MEG, MPG, MEA, MMA
        percentage : float
            Percentage of the antifreeze [%]
        """

        self._name = name
        self._percentage = percentage
        self._fluid: BaseMelinder | None = None

        super().__init__(0)

        self.set_fluid(name, percentage)

        # create interp array
        self._spacing = np.linspace(self.freezing_point, 100, TemperatureDependentFluidData.NB_OF_SAMPLES)
        self._k_f_array = np.array([self._fluid.conductivity(i) for i in self._spacing])
        self._mu_array = np.array([self._fluid.viscosity(i) for i in self._spacing])
        self._rho_array = np.array([self._fluid.density(i) for i in self._spacing])
        self._cp_array = np.array([self._fluid.specific_heat(i) for i in self._spacing])

    def set_fluid(self, name, percentage) -> None:
        """
        This function sets the fluid.

        Parameters
        ----------
        name : str
            Name of the antifreeze. Currently, there is: Water, MEG, MPG, MEA, MMA
        percentage : float
            Percentage of the antifreeze [%]

        Returns
        -------
        None
        """
        if name == 'Water':
            self._fluid = Water()
            self._freezing_point = self._fluid.freeze_point(percentage / 100)
            return
        if name == 'MPG':
            self._fluid = PropyleneGlycol(percentage / 100)
            self._freezing_point = self._fluid.freeze_point(percentage / 100)
            return
        if name == 'MEG':
            self._fluid = EthyleneGlycol(percentage / 100)
            self._freezing_point = self._fluid.freeze_point(percentage / 100)
            return
        if name == 'MMA':
            self._fluid = MethylAlcohol(percentage / 100)
            self._freezing_point = self._fluid.freeze_point(percentage / 100)
            return
        if name == 'MEA':
            self._fluid = EthylAlcohol(percentage / 100)
            self._freezing_point = self._fluid.freeze_point(percentage / 100)
            return
        raise ValueError(f'The fluid {name} is not yet supported by GHEtool.')

    def k_f(self, temperature: Optional[float, np.ndarray], **kwargs) -> Optional[float, np.ndarray]:
        """
        This function returns the conductivity of the fluid in W/(mK).

        Parameters
        ----------
        temperature : float
            Temperature at which to evaluate the fluid properties [°C]

        Returns
        -------
        float
            Fluid thermal conductivity [W/(mK)]
        """
        return np.interp(temperature, self._spacing, self._k_f_array)

    def rho(self, temperature: Optional[float, np.ndarray], **kwargs) -> Optional[float, np.ndarray]:
        """
        This function returns the density of the fluid in kg/m^3.

        Parameters
        ----------
        temperature : float
            Temperature at which to evaluate the fluid properties [°C]

        Returns
        -------
        float
            Density [kg/m^3]
        """
        return np.interp(temperature, self._spacing, self._rho_array)

    def cp(self, temperature: Optional[float, np.ndarray], **kwargs) -> Optional[float, np.ndarray]:
        """
        This function returns the heat capacity of the fluid in J/(kgK).

        Parameters
        ----------
        temperature : float
            Temperature at which to evaluate the fluid properties [°C]

        Returns
        -------
        float
            Heat capacity of the fluid [J/(kgK)]
        """
        return np.interp(temperature, self._spacing, self._cp_array)

    def mu(self, temperature: Optional[float, np.ndarray], **kwargs) -> Optional[float, np.ndarray]:
        """
        This function returns the dynamic viscosity of the fluid in Pa.s.

        Parameters
        ----------
        temperature : float
            Temperature at which to evaluate the fluid properties [°C]

        Returns
        -------
        float
            Dynamic viscosity [Pa.s]
        """
        return np.interp(temperature, self._spacing, self._mu_array)

    def create_constant(self, temperature: float) -> ConstantFluidData:
        """
        This function creates a constant fluid data object.

        Parameters
        ----------
        temperature : float
            Temperature at which to evaluate the fluid properties [°C]

        Returns
        -------
        ConstantFluidData
            Fluid data object with constant properties
        """
        return ConstantFluidData(
            self.k_f(temperature),
            self.rho(temperature),
            self.cp(temperature),
            self.mu(temperature),
            self.freezing_point
        )

    def __repr__(self):
        return {
            'name': self._name,
            'percentage': self._percentage
        }

    def __eq__(self, other):
        if not isinstance(other, TemperatureDependentFluidData):
            return False
        if self._name != other._name or self._percentage != other._percentage:
            return False
        return True
