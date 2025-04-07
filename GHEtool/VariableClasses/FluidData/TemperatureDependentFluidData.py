from scp.ethyl_alcohol import EthylAlcohol
from scp.ethylene_glycol import EthyleneGlycol
from scp.methyl_alcohol import MethylAlcohol
from scp.propylene_glycol import PropyleneGlycol
from scp.water import Water
from scp.base_melinder import BaseMelinder

from GHEtool.VariableClasses.FluidData._FluidData import _FluidData
from GHEtool.VariableClasses.FluidData.ConstantFluidData import ConstantFluidData
from GHEtool.VariableClasses.BaseClass import BaseClass


class TemperatureDependentFluidData(_FluidData, BaseClass):
    """
    Contains information regarding the fluid data of the borefield, assuming there is temperature dependency.
    """

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

    def k_f(self, temperature: float, **kwargs) -> float:
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
        return self._fluid.conductivity(temperature)

    def rho(self, temperature: float, **kwargs) -> float:
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
        return self._fluid.density(temperature)

    def cp(self, temperature: float, **kwargs) -> float:
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
        return self._fluid.specific_heat(temperature)

    def mu(self, temperature: float, **kwargs) -> float:
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
        return self._fluid.viscosity(temperature)

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
