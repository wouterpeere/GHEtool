import numpy as np

from scp.ethyl_alcohol import EthylAlcohol
from scp.ethylene_glycol import EthyleneGlycol
from scp.methyl_alcohol import MethylAlcohol
from scp.propylene_glycol import PropyleneGlycol
from scp.water import Water
from scp.base_melinder import BaseMelinder

from GHEtool.VariableClasses.FluidData._FluidData import _FluidData
from GHEtool.VariableClasses.FluidData.CommercialFluids._CommercialFluids import _CommercialFluids
from GHEtool.VariableClasses.FluidData.CommercialFluids import *
from GHEtool.VariableClasses.FluidData.ConstantFluidData import ConstantFluidData
from GHEtool.VariableClasses.BaseClass import BaseClass
from typing import Union


class TemperatureDependentFluidData(_FluidData, BaseClass):
    """
    Contains information regarding the fluid data of the borefield, assuming there is temperature dependency.
    """

    NB_OF_SAMPLES = 500

    # Concentration by weight (m/m%)
    _MM = np.arange(0, 101, 5, dtype=float)

    # Corresponding concentration by volume (v/v%) according to (Melinder, 2007)
    _VV = {
        "MEG": np.array([
            0, 4.4, 8.9, 13.6, 18.1, 22.9, 27.7, 32.6, 37.5, 42.5,
            47.6, 52.7, 57.8, 62.8, 68.3, 73.6, 78.9, 84.3, 89.7, 95.0, 100
        ]),
        "MPG": np.array([
            0, 4.8, 9.6, 14.5, 19.4, 24.4, 29.4, 34.4, 39.6, 44.7,
            49.9, 55.0, 60.0, 65.0, 70.0, 75.0, 80.0, 85.0, 90.0, 95.0, 100
        ]),
        "MEA": np.array([
            0, 6.24, 12.39, 18.47, 24.47, 30.39, 36.18, 41.83, 47.33, 52.66,
            57.83, 62.84, 67.69, 72.38, 76.91, 81.27, 85.46, 89.46, 93.25, 96.79, 100
        ])
    }

    __slots__ = '_name', '_percentage'

    def __init__(self, name: str, percentage: float, mass_percentage: bool = True):
        """

        Parameters
        ----------
        name : str
            Name of the antifreeze. Currently, there is: Water, MEG, MPG, MEA, MMA, Thermox DTX, Coolflow NTP, Kilfrost GEO, Kilfrost GEO Plus, GeoPro
        percentage : float
            Percentage of the antifreeze [%]
        mass_percentage : bool
            True if the given percentage is the mass percentage, false if it is the volume percentage
        """

        self._name = name
        self._percentage = percentage
        self._mass_percentage = mass_percentage
        self._fluid: BaseMelinder | _CommercialFluids | None = None

        super().__init__(0)

        self.set_fluid(name, percentage)

        if isinstance(self._fluid, _CommercialFluids):
            self._spacing = self._fluid._temperatures[::-1]
        else:
            # create interp array
            self._spacing = np.linspace(self.freezing_point, 100, TemperatureDependentFluidData.NB_OF_SAMPLES)

        self._k_f_array = np.array([float(self._fluid.conductivity(i)) for i in self._spacing])
        self._mu_array = np.array([float(self._fluid.viscosity(i)) for i in self._spacing])
        self._rho_array = np.array([float(self._fluid.density(i)) for i in self._spacing])
        self._cp_array = np.array([float(self._fluid.specific_heat(i)) for i in self._spacing])

        self._thermal_expansion = -np.gradient(self._rho_array, self._spacing) / self._rho_array

    def _calc_density_antifreeze(self, percentage: float = 30) -> float:
        """
        This function returns the density of the pure antifreeze in kg/m³.
        This uses the assumption of an ideal mixture, which can lead to small errors in the range of +-1%.
        rho_{antifreeze_mixture},per = rho_antifreeze_mixture * per + rho_water * (100-per)

        Parameters
        ----------
        percentage : float
            Percentage of antifreeze [%]

        Returns
        -------
        Density : float
        """
        antifreeze, _ = self._get_fluid(self._name, percentage)
        water, _ = self._get_fluid('Water', 0)
        water_mass = water.density(temp=15)
        total_mass = antifreeze.density(temp=15)
        return (total_mass - water_mass * (100 - percentage) / 100) / percentage * 100

    def _convert_to_mass_percentage(self, vol_per: float) -> float:
        """
        This function converts the volume percentage to mass percentage.
        This uses the assumption of an ideal mixture, which can lead to small errors in the range of +-1%.
        rho_{antifreeze_mixture},per = rho_antifreeze_mixture * per + rho_water * (100-per)

        Parameters
        ----------
        vol_per : float
            Volume percentage [%]

        Returns
        -------
        Mass percentage : float
        """
        if self._name in TemperatureDependentFluidData._VV:
            return np.interp(vol_per, TemperatureDependentFluidData._VV[self._name],
                             TemperatureDependentFluidData._MM)

        mass_density_antifreeze = self._calc_density_antifreeze()
        return vol_per * mass_density_antifreeze / (
                999.0996087908144 * (100 - vol_per) + mass_density_antifreeze * vol_per) * 100

    def _convert_to_vol_percentage(self, mass_per: float) -> float:
        """
        This function converts the mass percentage to volume percentage.
        This uses the assumption of an ideal mixture, which can lead to small errors in the range of +-1%.
        rho_{antifreeze_mixture},per = rho_antifreeze_mixture * per + rho_water * (100-per)

        Parameters
        ----------
        mass_per : float
            Mass percentage [%]

        Returns
        -------
        Volume percentage : float
        """
        if self._name in TemperatureDependentFluidData._VV:
            return np.interp(mass_per, TemperatureDependentFluidData._MM,
                             TemperatureDependentFluidData._VV[self._name], )

        mass_density_antifreeze = self._calc_density_antifreeze()
        return mass_per * 999.0996087908144 / (
                mass_density_antifreeze * (100 - mass_per) + mass_per * 999.0996087908144) * 100

    def _get_fluid(self, name: str, percentage: float) -> tuple:
        """
        This function gets the fluid.

        Parameters
        ----------
        name : str
            Name of the antifreeze. Currently, there is: Water, MEG, MPG, MEA, MMA, Thermox DTX, Coolflow NTP, Kilfrost GEO, Kilfrost GEO Plus, GeoPro
        percentage : float
            Percentage of the antifreeze [%]

        Returns
        -------
        Tuple (fluid object, freezing point)

        Raises
        ------
        ValueError
            When the fluid is not available in GHEtool.
        """
        if name == 'Water':
            fluid = Water()
            return fluid, fluid.freeze_point(percentage / 100)
        if name == 'MPG':
            fluid = PropyleneGlycol(percentage / 100)
            return fluid, fluid.freeze_point(percentage / 100)
        if name == 'MEG':
            fluid = EthyleneGlycol(percentage / 100)
            return fluid, fluid.freeze_point(percentage / 100)
        if name == 'MMA':
            fluid = MethylAlcohol(percentage / 100)
            return fluid, fluid.freeze_point(percentage / 100)
        if name == 'MEA':
            fluid = EthylAlcohol(percentage / 100)
            return fluid, fluid.freeze_point(percentage / 100)
        if name == 'Thermox DTX':
            fluid = ThermoxDTX(percentage / 100)
            return fluid, fluid.freeze_point(percentage / 100)
        if name == 'Coolflow NTP':
            fluid = CoolflowNTP(percentage / 100)
            return fluid, fluid.freeze_point(percentage / 100)
        if name == 'Kilfrost GEO':
            fluid = KilfrostGEO(percentage / 100)
            return fluid, fluid.freeze_point(percentage / 100)
        if name == 'Kilfrost GEO Plus':
            fluid = KilfrostGEOPlus(percentage / 100)
            return fluid, fluid.freeze_point(percentage / 100)
        if name == 'GeoPro':
            fluid = GeoPro(percentage / 100)
            return fluid, fluid.freeze_point(percentage / 100)
        raise ValueError(f'The fluid {name} is not yet supported by GHEtool.')

    def set_fluid(self, name: str, percentage: float) -> None:
        """
        This function sets the fluid.

        Parameters
        ----------
        name : str
            Name of the antifreeze. Currently, there is: Water, MEG, MPG, MEA, MMA, Thermox DTX, Coolflow NTP, Kilfrost GEO, Kilfrost GEO Plus
        percentage : float
            Percentage of the antifreeze [%]

        Returns
        -------
        None
        """

        if name in ['Water', 'MPG', 'MEG', 'MMA', 'MEA'] and not self._mass_percentage:
            # these properties are saved as mass percentage so the percentage should be converted
            percentage = self._convert_to_mass_percentage(percentage)
        if name not in ['Water', 'MPG', 'MEG', 'MMA', 'MEA'] and self._mass_percentage:
            # these properties are saved as volume percentage so the percentage should be converted
            percentage = self._convert_to_vol_percentage(percentage)

        self._fluid, self._freezing_point = self._get_fluid(name, percentage)

    def k_f(self, temperature: Union[float, np.ndarray], **kwargs) -> Union[float, np.ndarray]:
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

    def rho(self, temperature: Union[float, np.ndarray], **kwargs) -> Union[float, np.ndarray]:
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

    def cp(self, temperature: Union[float, np.ndarray], **kwargs) -> Union[float, np.ndarray]:
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

    def mu(self, temperature: Union[float, np.ndarray], **kwargs) -> Union[float, np.ndarray]:
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

    def __export__(self):
        return {
            'name': self._name,
            'percentage': self._percentage,
            'type': 'mass percentage' if self._mass_percentage else 'volume percentage'
        }

    def __eq__(self, other):
        if not isinstance(other, TemperatureDependentFluidData):
            return False
        if self._name != other._name or self._percentage != other._percentage:
            return False
        return True
