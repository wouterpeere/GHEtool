"""
This file contains all the code for the borefield calculations.
"""
from __future__ import annotations

import math
import warnings
from math import pi
from typing import Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pygfunction as gt

from numpy.typing import ArrayLike
from scipy.signal import convolve

from GHEtool.VariableClasses import FluidData, Borehole, GroundConstantTemperature, ResultsMonthly, ResultsHourly, \
    TemperatureDependentFluidData
from GHEtool.VariableClasses import CustomGFunction, load_custom_gfunction, GFunction, CalculationSetup, Cluster, \
    EERCombined
from GHEtool.VariableClasses.LoadData import *
from GHEtool.VariableClasses.LoadData import _LoadData, _LoadDataBuilding
from GHEtool.VariableClasses.PipeData import _PipeData
from GHEtool.VariableClasses.BaseClass import BaseClass, UnsolvableDueToTemperatureGradient, MaximumNumberOfIterations
from GHEtool.VariableClasses.GroundData._GroundData import _GroundData
from GHEtool.VariableClasses.FluidData._FluidData import _FluidData
from GHEtool.VariableClasses.FlowData._FlowData import _FlowData
from GHEtool.VariableClasses.PipeData._PipeData import _PipeData


class Borefield(BaseClass):
    """Main borefield class"""

    UPM: float = 730.0  # number of hours per month
    THRESHOLD_BOREHOLE_LENGTH: float = 0.05  # threshold for iteration

    # define default values
    DEFAULT_INVESTMENT: list = [35, 0]  # 35 EUR/m
    DEFAULT_LENGTH_PEAK: int = 6  # hours
    THRESHOLD_DEPTH_ERROR: int = 10000  # m

    HOURLY_LOAD_ARRAY: np.ndarray = np.arange(0, 8761, UPM).astype(np.uint32)

    def __init__(
            self,
            peak_extraction: ArrayLike = None,
            peak_injection: ArrayLike = None,
            baseload_extraction: ArrayLike = None,
            baseload_injection: ArrayLike = None,
            borefield: gt.borefield.Borefield = None,
            custom_gfunction: CustomGFunction = None,
            *,
            load: _LoadData = None,
            ground_data: _GroundData = GroundConstantTemperature(),
            fluid_data: _FluidData = None,
            flow_data: _FlowData = None,
            pipe_data: _PipeData = None,
            **kwargs
    ):
        """

        Parameters
        ----------
        peak_extraction : list, numpy array
            Monthly peak extraction values [kW]
        peak_injection : list, numpy array
            Monthly peak injection values [kW]
        baseload_extraction : list, numpy array
            Monthly baseload extraction values [kWh]
        baseload_injection : list, numpy array
            Monthly baseload extraction values [kWh]
        borefield : pygfunction borehole/borefield object
            Set the borefield for which the calculations will be carried out
        custom_gfunction : CustomGFunction
            Custom gfunction dataset
        load : _LoadData
            Load data of the borefield
        ground_data : _GroundData
            Ground data for the borefield
        fluid_data : FluidData
            Fluid data for the borefield
        flow_data : FlowData
            Flow data for the borefield
        pipe_data : PipeData
            Pipe data of the borehole
        """

        self.limiting_quadrant: int = 0  # parameter that tells in which quadrant the field is limited
        # m hereafter one needs to chance to fewer boreholes with more depth, because the calculations are no longer
        # that accurate.
        self.THRESHOLD_WARNING_SHALLOW_FIELD: int = 50

        if len(kwargs) != 0:
            raise ValueError('Please check your input for the Borefield class')

        if custom_gfunction is not None:
            warnings.warn(
                'From version 2.4.0 it will no longer be possible to initiate a borefield object with a custom gfunction.'
                'Please use the load_custom_gfunction function.', DeprecationWarning)
            self.custom_gfunction: CustomGFunction = custom_gfunction
        self.gfunction_calculation_object: GFunction = GFunction()

        # initialize variables for temperature plotting
        self.results: ResultsMonthly | ResultsHourly = ResultsMonthly()

        # initiate ground parameters
        self._H = 0.0  # borehole length [m]
        self._ground_data: _GroundData = ground_data
        self.D: float = 0.0  # buried depth of the borehole [m]
        self.r_b: float = 0.0  # borehole radius [m]

        # initiate fluid parameters
        self.Tf_max: float = 16.0  # maximum temperature of the fluid
        self.Tf_min: float = 0.0  # minimum temperature of the fluid

        # initiate borehole
        self.avg_tilt: float = 0.
        self.borehole = Borehole()
        self.pipe_data = pipe_data
        self.flow_data = flow_data
        self.fluid_data = fluid_data

        # initiate different sizing
        self._calculation_setup: CalculationSetup = CalculationSetup()
        self.calculation_setup()

        # load on the geothermal borefield, used in calculations
        self._borefield_load = MonthlyGeothermalLoadAbsolute()

        if load is not None:
            self.load = load
        else:
            warnings.warn('From version 2.4.0 you will need to load a load object instead of the base and peak load.',
                          DeprecationWarning)
            self.load = MonthlyGeothermalLoadAbsolute(baseload_extraction,
                                                      baseload_injection,
                                                      peak_extraction,
                                                      peak_injection)

        # set investment cost
        self.cost_investment: list = Borefield.DEFAULT_INVESTMENT

        # set a custom borefield
        self._borefield_description = None
        self.borefield = borefield

    @property
    def number_of_boreholes(self) -> int:
        """
        This returns the number of boreholes in the borefield attribute.

        Returns
        -------
        int
            Number of boreholes
        """
        return self.borefield.nBoreholes if self.borefield is not None else 0

    @property
    def depth(self) -> float:
        """
        This function returns the average borehole depth.

        Returns
        -------
        float
            Average borehole depth [meters]
        """
        return self.calculate_depth(self.H, self.D)

    def calculate_depth(self, borehole_length: float, buried_depth: float) -> float:
        """
        This function calculates the depth of the borehole given the average tilt of the borefield.

        Parameters
        ----------
        borehole_length : float
            Length of the borehole [m]
        buried_depth : float
            Buried depth of the borehole [m]

        Returns
        -------
        float
            Depth of the borehole [m]
        """
        if self.borefield is None or np.all(self.borefield.tilt == 0):
            return borehole_length + buried_depth
        return np.average([bor.H * math.cos(bor.tilt) for bor in self.borefield]) + buried_depth

    @property
    def H(self) -> float:
        """
        This function returns the borehole length as measured alongside the axis of the borehole.

        Returns
        -------
        float
            Borehole length [meters]
        """
        return self._H

    @H.setter
    def H(self, H: float) -> None:
        """
        This function sets the borehole length as measured alongside the axis of the borehole.

        Parameters
        ----------
        H : float
            Borehole length [meters]

        Returns
        -------
        None
        """
        self._H = H
        self._borefield.H = np.full(self.number_of_boreholes, H)

        # the boreholes are equal in length
        self.gfunction_calculation_object.store_previous_values = \
            self.gfunction_calculation_object._store_previous_values_backup

    def set_borefield(self, borefield: gt.borefield.Borefield = None) -> None:
        """
        This function set the borefield object. When None is given, the borefield will be deleted.

        Parameters
        ----------
        borefield : pygfunction.borefield.Borefield
            Borefield created with the pygfunction package

        Returns
        -------
        None
        """
        self._borefield_description = None
        self.borefield = borefield

    def create_rectangular_borefield(self, N_1: int, N_2: int, B_1: float, B_2: float, H: float, D: float = 1,
                                     r_b: float = 0.075):
        """
        This function creates a rectangular borefield.
        It calls the pygfunction module in the background.
        The documentation of this function is based on pygfunction.

        Parameters
        ----------
        N_1 : int
            Number of boreholes in the x direction
        N_2 : int
            Number of boreholes in the y direction
        B_1 : int
            Distance between adjacent boreholes in the x direction [m]
        B_2 : int
            Distance between adjacent boreholes in the y direction [m]
        H : float
            Borehole length [m]
        D : float
            Borehole buried depth [m]
        r_b : float
            Borehole radius [m]

        Returns
        -------
        pygfunction borefield object
        """
        borefield = gt.borefield.Borefield.rectangle_field(N_1, N_2, B_1, B_2, H, D, r_b)
        self.set_borefield(borefield)
        self._borefield_description = {'N_1': N_1, 'N_2': N_2, 'B_1': B_1, 'B_2': B_2, 'type': 'rect'}
        return borefield

    def create_circular_borefield(self, N: int, R: float, H: float, D: float = 1, r_b: float = 0.075):
        """
        This function creates a circular borefield.
        It calls the pygfunction module in the background.
        The documentation of this function is based on pygfunction.

        Parameters
        ----------
        N : int
            Number of boreholes in the borefield
        R : float
            Distance of boreholes from the center of the field
        H : float
            Borehole length [m]
        D : float
            Borehole buried depth [m]
        r_b : float
            Borehole radius [m]

        Returns
        -------
        pygfunction borefield object
        """
        borefield = gt.borefield.Borefield.circle_field(N, R, H, D, r_b)
        self.set_borefield(borefield)
        return borefield

    def create_U_shaped_borefield(self, N_1: int, N_2: int, B_1: float, B_2: float, H: float, D: float = 1,
                                  r_b: float = 0.075):
        """
        This function creates a U shaped borefield.
        It calls the pygfunction module in the background.
        The documentation of this function is based on pygfunction.

        Parameters
        ----------
        N_1 : int
            Number of boreholes in the x direction
        N_2 : int
            Number of boreholes in the y direction
        B_1 : int
            Distance between adjacent boreholes in the x direction [m]
        B_2 : int
            Distance between adjacent boreholes in the y direction [m]
        H : float
            Borehole length [m]
        D : float
            Borehole buried depth [m]
        r_b : float
            Borehole radius [m]

        Returns
        -------
        pygfunction borefield object
        """
        borefield = gt.borefield.Borefield.U_shaped_field(N_1, N_2, B_1, B_2, H, D, r_b)
        self.set_borefield(borefield)
        self._borefield_description = {'N_1': N_1, 'N_2': N_2, 'B_1': B_1, 'B_2': B_2, 'type': 'U'}
        return borefield

    def create_L_shaped_borefield(self, N_1: int, N_2: int, B_1: float, B_2: float, H: float, D: float = 1,
                                  r_b: float = 0.075):
        """
        This function creates a L shaped borefield.
        It calls the pygfunction module in the background.
        The documentation of this function is based on pygfunction.

        Parameters
        ----------
        N_1 : int
            Number of boreholes in the x direction
        N_2 : int
            Number of boreholes in the y direction
        B_1 : int
            Distance between adjacent boreholes in the x direction [m]
        B_2 : int
            Distance between adjacent boreholes in the y direction [m]
        H : float
            Borehole length [m]
        D : float
            Borehole buried depth [m]
        r_b : float
            Borehole radius [m]

        Returns
        -------
        pygfunction borefield object
        """
        borefield = gt.borefield.Borefield.L_shaped_field(N_1, N_2, B_1, B_2, H, D, r_b)
        self.set_borefield(borefield)
        self._borefield_description = {'N_1': N_1, 'N_2': N_2, 'B_1': B_1, 'B_2': B_2, 'type': 'L'}

        return borefield

    def create_box_shaped_borefield(self, N_1: int, N_2: int, B_1: float, B_2: float, H: float, D: float = 1,
                                    r_b: float = 0.075):
        """
        This function creates a box shaped borefield.
        It calls the pygfunction module in the background.
        The documentation of this function is based on pygfunction.

        Parameters
        ----------
        N_1 : int
            Number of boreholes in the x direction
        N_2 : int
            Number of boreholes in the y direction
        B_1 : int
            Distance between adjacent boreholes in the x direction [m]
        B_2 : int
            Distance between adjacent boreholes in the y direction [m]
        H : float
            Borehole length [m]
        D : float
            Borehole buried depth [m]
        r_b : float
            Borehole radius [m]

        Returns
        -------
        pygfunction borefield object
        """
        borefield = gt.borefield.Borefield.box_shaped_field(N_1, N_2, B_1, B_2, H, D, r_b)
        self.set_borefield(borefield)
        self._borefield_description = {'N_1': N_1, 'N_2': N_2, 'B_1': B_1, 'B_2': B_2, 'type': 'box'}
        return borefield

    @property
    def borefield(self):
        """
        Returns the hidden _borefield variable.

        Returns
        -------
        Hidden _borefield object
        """
        return self._borefield

    @borefield.setter
    def borefield(self, borefield: gt.borefield.Borefield = None) -> None:
        """
        This function sets the borefield configuration. When no input is given, the borefield variable will be deleted.

        Parameters
        ----------
        borefield : pygfunction.borefield.Borefield
            Borefield created with the pygfunction package

        Returns
        -------
        None
        """
        if borefield is None:
            del self.borefield
            return
        self._borefield = borefield
        self.D = np.average(borefield.D)
        self.r_b = np.average(borefield.r_b)
        self._H = np.average(borefield.H)
        self.avg_tilt = np.average(borefield.tilt)
        if not np.all(borefield.tilt == 0):
            self.gfunction_calculation_object.options['method'] = 'similarities'
        self.gfunction_calculation_object.remove_previous_data()
        unequal_length = not np.all(borefield.H == self.H)
        if unequal_length:
            self.gfunction_calculation_object._store_previous_values = not unequal_length
        else:
            self.gfunction_calculation_object.store_previous_values = \
                self.gfunction_calculation_object._store_previous_values_backup

    @borefield.deleter
    def borefield(self):
        """
        This function deletes the hidden _borefield object.
        It also sets the number of boreholes to zero

        Returns
        -------
        None
        """
        self._borefield = None
        self.gfunction_calculation_object.remove_previous_data()
        self.custom_gfunction = None

    def load_custom_gfunction(self, location: str) -> None:
        """
        This function loads the custom gfunction.

        Parameters
        ----------
        location : str
            Path to the location of the custom gfunction file

        Returns
        -------
        None
        """

        self.custom_gfunction = load_custom_gfunction(location)

    def set_investment_cost(self, investment_cost: list = None) -> None:
        """
        This function sets the investment cost. This is linear with respect to the total field length.
        If None, the default is set.

        Parameters
        ----------
        investment_cost : list
            1D array of polynomial coefficients (including coefficients equal to zero) from highest degree to the constant term

        Returns
        -------
        None
        """
        if investment_cost is None:
            investment_cost = Borefield.DEFAULT_INVESTMENT
        self.cost_investment: list = investment_cost

    def set_load(self, load: Union[_LoadData, Cluster]) -> None:
        """
        This function sets the _load attribute.

        Parameters
        ----------
        load : _LoadData or Cluster
            Load data object

        Returns
        -------
        None
        """
        self.load = load

    @property
    def load(self) -> HourlyGeothermalLoad | MonthlyGeothermalLoadAbsolute | \
                      HourlyBuildingLoad | MonthlyBuildingLoadAbsolute:
        """
        This returns the LoadData object.

        Returns
        -------
        Load data: LoadData
        """
        return self._borefield_load

    @load.setter
    def load(self, load: Union[_LoadData, Cluster]) -> None:
        """
        This function sets the _load attribute.

        Parameters
        ----------
        load : _LoadData or Cluster
            Load data object

        Returns
        -------
        None
        """
        self._borefield_load = load
        self._delete_calculated_temperatures()

    @property
    def simulation_period(self) -> int:
        """
        This returns the simulation period from the LoadData object.

        Returns
        -------
        Simulation period [years] : int
        """
        return self.load.simulation_period

    @simulation_period.setter
    def simulation_period(self, simulation_period: float) -> None:
        """
        This function sets the simulation period.

        Parameters
        ----------
        simulation_period : float
            Simulation period in years

        Returns
        -------
        None
        """
        self._borefield_load.simulation_period = simulation_period

    @property
    def Rb(self) -> float:
        """
        This function returns the equivalent borehole thermal resistance at the minimum average fluid temperature.

        Returns
        -------
        Rb : float
            Equivalent borehole thermal resistance [mK/W]
        """
        return self.borehole.get_Rb(self.H, self.D, self.r_b, self.ground_data.k_s, self.depth,
                                    temperature=min(self.Tf_min,
                                                    self.results.min_temperature if self.results.min_temperature is not None else 10e6))

    @Rb.setter
    def Rb(self, Rb: float) -> None:
        """
        This function sets the constant equivalent borehole thermal resistance.

        Parameters
        ----------
        Rb : float
            Equivalent borehole thermal resistance [mk/W]

        Returns
        -------
        None
        """
        self.set_Rb(Rb)

    @property
    def ground_data(self) -> _GroundData:
        """
        This function returns the ground data.

        Returns
        -------
        ground data : GroundData

        """
        return self._ground_data

    @ground_data.setter
    def ground_data(self, data: _GroundData) -> None:
        """
        This function sets the relevant ground parameters.

        Parameters
        ----------
        data : GroundData
            All the relevant ground data

        Returns
        -------
        None
        """
        # Ground properties
        self._ground_data = data

        # new ground data implies that a new g-function should be loaded
        self.custom_gfunction = None

        # the stored gfunction data should be deleted
        self.gfunction_calculation_object.remove_previous_data()

    def set_ground_parameters(self, data: _GroundData) -> None:
        """
        This function sets the relevant ground parameters.

        Parameters
        ----------
        data : GroundData
            All the relevant ground data

        Returns
        -------
        None
        """
        warnings.warn(
            'From version 2.4.0 this function will be depreciated. Please set the ground properties by using a direct '
            'assignment.', DeprecationWarning)
        self.ground_data = data

    @property
    def pipe_data(self) -> _PipeData:
        """
        This function returns the pipe data.

        Returns
        -------
        pipe data : PipeData

        """
        return self.borehole.pipe_data

    @pipe_data.setter
    def pipe_data(self, data: _PipeData) -> None:
        """
        This function sets the relevant pipe parameters.

        Parameters
        ----------
        data : PipeData
            All the relevant pipe data

        Returns
        -------
        None
        """
        self.borehole.pipe_data = data

    @property
    def fluid_data(self) -> _FluidData:
        """
        This function returns the fluid data.

        Returns
        -------
        fluid data : FluidData

        """
        return self.borehole.fluid_data

    @fluid_data.setter
    def fluid_data(self, data: _FluidData) -> None:
        """
        This function sets the relevant fluid parameters.

        Parameters
        ----------
        data : FluidData
            All the relevant fluid data

        Returns
        -------
        None
        """
        self.borehole.fluid_data = data

    @property
    def flow_data(self) -> _FlowData:
        """
        This function returns the flow rate data.

        Returns
        -------
        flow data : FlowData

        """
        return self.borehole.flow_data

    @flow_data.setter
    def flow_data(self, data: _FlowData) -> None:
        """
        This function sets the relevant flow rate parameters.

        Parameters
        ----------
        data : FlowData
            All the relevant flow data

        Returns
        -------
        None
        """
        self.borehole.flow_data = data

    def set_fluid_parameters(self, data: _FluidData) -> None:
        """
        This function sets the fluid parameters.

        Parameters
        ----------
        data : FluidData
            All the relevant fluid data

        Returns
        -------
        None
        """
        warnings.warn(
            'From version 2.4.0 this function will be depreciated. Please set the fluid properties by using a direct '
            'assignment.', DeprecationWarning)
        self.fluid_data = data

    def set_pipe_parameters(self, data: _PipeData) -> None:
        """
        This function sets the pipe parameters.

        Parameters
        ----------
        data : PipeData
            All the relevant pipe parameters

        Returns
        -------
        None
        """
        warnings.warn(
            'From version 2.4.0 this function will be depreciated. Please set the pipe properties by using a direct '
            'assignment.', DeprecationWarning)
        self.pipe_data = data

    def set_Rb(self, Rb: float) -> None:
        """
        This function sets the constant equivalent borehole thermal resistance.

        Parameters
        ----------
        Rb : float
            Equivalent borehole thermal resistance (mK/W)

        Returns
        -------
        None
        """
        self.borehole.Rb = Rb

    def set_max_avg_fluid_temperature(self, temp: float) -> None:
        """
        This functions sets the maximal average fluid temperature to temp.

        Parameters
        ----------
        temp : float
            Maximal average fluid temperature [deg C]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When the maximal average fluid temperature is lower than the minimal average fluid temperature
        """
        if temp <= self.Tf_min:
            raise ValueError(
                f"The maximum average fluid temperature {temp} is lower than the minimum average fluid temperature {self.Tf_min}")
        self.Tf_max: float = temp

    def set_min_avg_fluid_temperature(self, temp: float) -> None:
        """
        This functions sets the minimal average fluid temperature to temp.

        Parameters
        ----------
        temp : float
            Minimal average fluid temperature [deg C]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When the maximal average temperature is lower than the minimal average temperature
        """
        if temp >= self.Tf_max:
            raise ValueError(
                f"The minimum average fluid temperature {temp} is lower than the maximum average fluid temperature {self.Tf_max}")
        self.Tf_min: float = temp

    def _Tg(self, H: float = None) -> float:
        """
        This function gives back the ground temperature.

        Parameters
        ----------
        H : float
            Depth of the field at which the temperature is to be evaluated

        Returns
        -------
        Temperature of the ground : float
        """
        # check if specific depth is given
        if H is None:
            H = self.H

        return self.ground_data.calculate_Tg(self.calculate_depth(H, self.D), self.D)

    def _check_convergence(self, new_length: float, old_length: float, iter: int) -> bool:
        """
        This function checks, with the absolute and relative tolerance, if the borehole length is converged.
        This is the case if both criteria are met. Raises MaximumNumberOfIterations error if the max number of iterations is crossed.

        Parameters
        ----------
        new_length : float
            Borehole length from the current interation [m]
        old_length : float
            Borehole length from the previous iteration [m]
        iter : int
            Current number of iteration

        Returns
        -------
        bool
            True if the borehole length is converged

        Raises
        ------
        MaximumNumberOfIterations
            MaximumNumberOfIterations if the max number of iterations is crossed
        """
        if iter + 1 > self._calculation_setup.max_nb_of_iterations:
            raise MaximumNumberOfIterations(self._calculation_setup.max_nb_of_iterations)

        if old_length == 0:
            return False
        test_a_tol = abs(
            new_length - old_length) <= self._calculation_setup.atol if self._calculation_setup.atol != False else True
        test_rtol = abs(
            new_length - old_length) / old_length <= self._calculation_setup.rtol if self._calculation_setup.rtol != False else True

        return test_a_tol and test_rtol

    def _Ahmadfard(self, th: float, qh: float, qm: float, qa: float, Tf: float) -> float:
        """
        This function sizes the field based on the last year of operation, i.e. quadrants 2 and 4.

        It uses the methodology developed by (Ahmadfard and Bernier, 2019) [#Ahmadfard2019]_.
        The concept of borefield quadrants is developed by (Peere et al., 2020) [#PeereBS]_ [#PeereThesis]_.

        Parameters
        ----------
        th : float
            Peak duration [s]
        qh : float
            Peak load [W]
        qm : float
            Monthly average load [W]
        qa : float
            Yearly imbalance load [W]
        Tf : float
            Temperature limit of the fluid [°C]

        Returns
        -------
        H : float
            Required borehole length [m]

        References
        ----------
        .. [#Ahmadfard2019] Ahmadfard M. and Bernier M., A review of vertical ground heat exchanger sizing tools including an inter-model comparison,
        Renewable and Sustainable Energy Reviews, Volume 110, 2019, Pages 247-265, ISSN 1364-0321, https://doi.org/10.1016/j.rser.2019.04.045
        .. [#PeereBS] Peere, W., Picard, D., Cupeiro Figueroa, I., Boydens, W., and Helsen, L. (2021) Validated combined first and last year borefield sizing methodology. In Proceedings of International Building Simulation Conference 2021. Brugge (Belgium), 1-3 September 2021. https://doi.org/10.26868/25222708.2021.30180
        .. [#PeereThesis] Peere, W. (2020) Methode voor economische optimalisatie van geothermische verwarmings- en koelsystemen. Master thesis, Department of Mechanical Engineering, KU Leuven, Belgium.
        """
        # initiate iteration
        H_prev = 0
        # set minimal length to 50 m
        self.H = 50 if self.H < 1 else self.H

        time = np.array([th, th + self.load.tm, self.load.ty + self.load.tm + th])
        # Iterates as long as there is no convergence
        # (convergence if difference between borehole length in iterations is smaller than THRESHOLD_BOREHOLE_LENGTH)
        i = 0
        while not self._check_convergence(self.H, H_prev, i):
            # calculate the required g-function values
            gfunct_uniform_T = self.gfunction(time, max(1, self.H))
            # calculate the thermal resistances
            k_s = self.ground_data.k_s(self.depth, self.D)
            Ra = (gfunct_uniform_T[2] - gfunct_uniform_T[1]) / (2 * pi * k_s)
            Rm = (gfunct_uniform_T[1] - gfunct_uniform_T[0]) / (2 * pi * k_s)
            Rd = (gfunct_uniform_T[0]) / (2 * pi * k_s)
            # calculate the total borehole length
            L = (qa * Ra + qm * Rm + qh * Rd + qh * self.Rb) / abs(Tf - self._Tg())
            # updating the borehole length values
            H_prev = self.H
            self.H = L / self.number_of_boreholes
            i += 1

        return self.H

    def _Carcel(self, th: float, tcm: float, qh: float, qpm: float, qm: float, Tf: float) -> float:
        """
        This function sizes the field based on the first year of operation, i.e. quadrants 1 and 3.

        It uses the methodology developed by (Monzo et al., 2016) [#Monzo]_ and adapted by (Peere et al., 2021) [#PeereBS]_.
        The concept of borefield quadrants is developed by (Peere et al., 2021) [#PeereBS]_, [#PeereThesis]_.

                Parameters
        ----------
        th : float
            Peak duration [s]
        tcm : float
            Duration of the current month [s]
        qp : float
            Peak load [W]
        qpm : float
            Average load of the past months [W]
        qm : float
            Monthly average load [W]
        Tf :float
            Temperature limit of the fluid [°C]

        Returns
        -------
        H : float
            Required borehole length [m]

        References
        ----------
        .. [#Monzo] Monzo, P., M. Bernier, J. Acuna, and P. Mogensen. (2016). A monthly based bore field sizing methodology with applications to optimum borehole spacing. ASHRAE Transactions 122, 111–126.
        .. [#PeereBS] Peere, W., Picard, D., Cupeiro Figueroa, I., Boydens, W., and Helsen, L. (2021) Validated combined first and last year borefield sizing methodology. In Proceedings of International Building Simulation Conference 2021. Brugge (Belgium), 1-3 September 2021. https://doi.org/10.26868/25222708.2021.30180
        .. [#PeereThesis] Peere, W. (2020) Methode voor economische optimalisatie van geothermische verwarmings- en koelsystemen. Master thesis, Department of Mechanical Engineering, KU Leuven, Belgium.
        """

        # initiate iteration
        H_prev = 0
        time_steps = [th, th + self.load.tm, tcm + th]
        if self.H < 1:
            self.H = 50

        # Iterates as long as there is no convergence
        # (convergence if difference between the borehole lengths in iterations is smaller than THRESHOLD_BOREHOLE_LENGTH)
        i = 0
        while not self._check_convergence(self.H, H_prev, i):
            # get the g-function values
            gfunc_uniform_T = self.gfunction(time_steps, max(1, self.H))

            # calculate the thermal resistances
            k_s = self.ground_data.k_s(self.depth, self.D)
            Rpm = (gfunc_uniform_T[2] - gfunc_uniform_T[1]) / (2 * pi * k_s)
            Rcm = (gfunc_uniform_T[1] - gfunc_uniform_T[0]) / (2 * pi * k_s)
            Rh = (gfunc_uniform_T[0]) / (2 * pi * k_s)

            # calculate the total length
            L = (qh * self.Rb + qh * Rh + qm * Rcm + qpm * Rpm) / abs(Tf - self._Tg())

            # updating the borehole lengths
            H_prev = self.H
            self.H = L / self.number_of_boreholes
            i += 1
        return self.H

    def calculation_setup(self, calculation_setup: CalculationSetup = None, use_constant_Rb: bool = None,
                          **kwargs) -> None:
        """
        This function sets the options for the sizing function.

        * The L2 sizing is the one explained in (Peere et al., 2021) [#PeereBS]_ and is the quickest method (it uses 3 pulses)

        * The L3 sizing is a more general approach which is slower but more accurate (it uses 24 pulses/year)

        * The L4 sizing is the most exact one, since it uses hourly data (8760 pulses/year)

        Parameters
        ----------
        calculation_setup : CalculationSetup
            An instance of the CalculationSetup class. When this argument differs from None, all the other parameters are
            set based on this calculation_setup
        use_constant_Rb : bool
            True if a constant borehole equivalent resistance (Rb*) value should be used
        kwargs
            Dictionary with all the other options that can be set within GHEtool. For a complete list,
            see the documentation in the CalculationSetup class.

        Returns
        -------
        None

        References
        ----------
        .. [#PeereBS] Peere, W., Picard, D., Cupeiro Figueroa, I., Boydens, W., and Helsen, L. (2021) Validated combined first and last year borefield sizing methodology. In Proceedings of International Building Simulation Conference 2021. Brugge (Belgium), 1-3 September 2021. https://doi.org/10.26868/25222708.2021.30180
        .. [#PeereThesis] Peere, W. (2020) Methode voor economische optimalisatie van geothermische verwarmings- en koelsystemen. Master thesis, Department of Mechanical Engineering, KU Leuven, Belgium.
        """

        # if calculation_setup is not None, then the sizing setup is set directly
        if calculation_setup is not None:
            self._calculation_setup = calculation_setup
            return

        self._calculation_setup.update_variables(**kwargs)

        if not use_constant_Rb is None:
            self.borehole.use_constant_Rb = use_constant_Rb

    def size(self, H_init: float = None,
             use_constant_Rb: bool = None,
             L2_sizing: bool = None,
             L3_sizing: bool = None,
             L4_sizing: bool = None,
             quadrant_sizing: int = None,
             **kwargs) -> float:
        """
        This function sets the options for the sizing function.

        * The L2 sizing is the one explained in (Peere et al., 2021) [#PeereBS]_ and is the quickest method (it uses 3 pulses)

        * The L3 sizing is a more general approach which is slower but more accurate (it uses 24 pulses/year)

        * The L4 sizing is the most exact one, since it uses hourly data (8760 pulses/year)

        Please note that the changes sizing setup changes here are not saved! Use self.setupSizing for this.

        Parameters
        ----------
        H_init : float
            Initial borehole length for the iteration. If None, the default H_init is chosen.
        use_constant_Rb : bool
            True if a constant borehole equivalent resistance (Rb*) value should be used
        L2_sizing : bool
            True if a sizing with the L2 method is needed
        L3_sizing : bool
            True if a sizing with the L3 method is needed
        L4_sizing : bool
            True if a sizing with the L4 method is needed
        quadrant_sizing : int
            Differs from 0 when a sizing in a certain quadrant is desired.
            Quadrants are developed by (Peere et al., 2021) [#PeereBS]_, [#PeereThesis]_
        kwargs : dict
            Dictionary with all the other options that can be set within GHEtool. For a complete list,
            see the documentation in the CalculationSetup class.

        Returns
        -------
        borehole length : float

        Raises
        ------
        ValueError
            ValueError when no ground data is provided
        """
        # check ground data
        if not self.ground_data.check_values():
            raise ValueError("Please provide ground data.")

        # make backup of initial parameter states
        self._calculation_setup.make_backup()
        use_constant_Rb_backup = self.borehole.use_constant_Rb

        # run the sizing setup
        self._calculation_setup.update_variables(H_init=H_init, L2_sizing=L2_sizing, L3_sizing=L3_sizing,
                                                 L4_sizing=L4_sizing, quadrant_sizing=quadrant_sizing)
        self._calculation_setup.update_variables(**kwargs)

        if not use_constant_Rb is None:
            self.borehole.use_constant_Rb = use_constant_Rb

        # sizes according to the correct algorithm
        if self._calculation_setup.L2_sizing:
            length = self.size_L2(H_init, self._calculation_setup.quadrant_sizing)
        if self._calculation_setup.L3_sizing:
            length = self.size_L3(H_init, self._calculation_setup.quadrant_sizing)
        if self._calculation_setup.L4_sizing:
            length = self.size_L4(H_init, self._calculation_setup.quadrant_sizing)

        # reset initial parameters
        self._calculation_setup.restore_backup()
        self.borehole.use_constant_Rb = use_constant_Rb_backup

        # check if the field is not shallow
        if length < self.THRESHOLD_WARNING_SHALLOW_FIELD:
            print(
                f"The field has a calculated borehole length of {round(length, 2)}"
                f"m which is lower than the proposed minimum "
                f"of {self.THRESHOLD_WARNING_SHALLOW_FIELD} m. "
                f"Please change your configuration accordingly to have a not so shallow field."
            )

        return length

    def _select_size(self, size_max_temp: float, size_min_temp: float, hourly: bool = False) -> float:
        """
        This function selects the correct size based on a size for the minimum and maximum temperature.
        When no temperature gradient is taken into account, this is just the maximum value of the two.
        When there is a temperature gradient and the sizing for the minimum temperature is higher than the sizing
        for the max temperature, it is checked if this sizing does not cross the maximum temperature limit.
        If it does, an error is returned.

        Parameters
        ----------
        size_max_temp : float
            Sizing according to the quadrants limited by the maximum temperature [m]
        size_min_temp : float
            Sizing according to the quadrants limited by the minimum temperature [m]
        hourly : bool
            True if the sizing was hourly

        Returns
        -------
        length : float
            Required borehole length [m]

        Raises
        ------
        UnsolvableDueToTemperatureGradient
            Error when no solution can be found
        """
        # return the max of both sizes when no temperature gradient is used
        if not self.ground_data.variable_Tg:
            return max(size_max_temp, size_min_temp)

        if size_max_temp > size_min_temp:
            # no problem, since the field is already sized by the maximum temperature
            return size_max_temp

        # check if sizing by the minimum temperature (quadrant 3/4) does not cross the temperature boundary
        self.calculate_temperatures(size_min_temp, hourly=hourly)
        if np.max(self.results.peak_injection) <= self.Tf_max:
            return size_min_temp
        raise UnsolvableDueToTemperatureGradient

    def size_L2(self, H_init: float = None, quadrant_sizing: int = 0) -> float:
        """
        This function sizes the  of the given configuration according to the methodology explained in
        (Peere et al., 2021) [#PeereBS]_, which is a L2 method. When quadrant sizing is other than 0, it sizes the field based on
        the asked quadrant. It returns the borehole length.

        Parameters
        ----------
        H_init : float
            Initial length from where to start the iteration [m]
        quadrant_sizing : int
            If a quadrant is given the sizing is performed for this quadrant else for the relevant

        Returns
        -------
        H : float
            Required borehole length [m]

        Raises
        ------
        ValueError
            ValueError when no ground data is provided or quadrant is not in range.
        """
        # check ground data
        if not self.ground_data.check_values():
            raise ValueError("Please provide ground data.")
        # check quadrants
        if not quadrant_sizing in range(0, 5):
            raise ValueError(f"Quadrant {quadrant_sizing} does not exist.")

        # check if it is building load
        if isinstance(self.load, _LoadDataBuilding):
            warnings.warn('The L2 method does not work with building load data. The L3 method will be used instead.')
            return self.size_L3(H_init, quadrant_sizing)

        # initiate with a given length
        self.H: float = H_init if H_init is not None else self._calculation_setup.H_init

        def size_quadrant1():
            th, _, tcm, qh, qpm, qm = self.load._calculate_first_year_params(False)  # calculate parameters
            return self._Carcel(th, tcm, qh, qpm, qm, self.Tf_max)  # size

        def size_quadrant2():
            th, qh, qm, qa = self.load._calculate_last_year_params(False)  # calculate parameters
            return self._Ahmadfard(th, qh, qm, qa, self.Tf_max)  # size

        def size_quadrant3():
            th, _, tcm, qh, qpm, qm = self.load._calculate_first_year_params(True)  # calculate parameters
            return self._Carcel(th, tcm, qh, qpm, qm, self.Tf_min)  # size

        def size_quadrant4():
            th, qh, qm, qa = self.load._calculate_last_year_params(True)  # calculate parameters
            return self._Ahmadfard(th, qh, qm, qa, self.Tf_min)  # size

        if quadrant_sizing != 0:
            # size according to a specific quadrant
            if quadrant_sizing == 1:
                self.H = size_quadrant1()
            elif quadrant_sizing == 2:
                self.H = size_quadrant2()
            elif quadrant_sizing == 3:
                self.H = size_quadrant3()
            else:
                self.H = size_quadrant4()
            self.limiting_quadrant = quadrant_sizing
        else:
            # size according to the biggest quadrant
            # determine which quadrants are relevant
            if self.load.imbalance <= 0:
                # extraction dominated, so quadrants 1 and 4 are relevant
                if self.load.max_peak_injection != 0:
                    quadrant1 = size_quadrant1()
                else:
                    quadrant1 = 0
                quadrant4 = size_quadrant4()

                self.H = self._select_size(quadrant1, quadrant4)

                if quadrant1 == self.H:
                    self.limiting_quadrant = 1
                else:
                    self.limiting_quadrant = 4
            else:
                # injection dominated, so quadrants 2 and 3 are relevant
                quadrant2 = size_quadrant2()
                if self.load.max_peak_extraction != 0:
                    quadrant3 = size_quadrant3()
                else:
                    quadrant3 = 0

                self.H = self._select_size(quadrant2, quadrant3)

                if quadrant2 == self.H:
                    self.limiting_quadrant = 2
                else:
                    self.limiting_quadrant = 3

        return self.H

    def size_L3(self, H_init: float = None, quadrant_sizing: int = 0) -> float:
        """
        This function sizes the borefield based on a monthly (L3) method.

        Parameters
        ----------
        H_init : float
            Initial borehole length from where to start the iteration [m]
        quadrant_sizing : int
            If a quadrant is given the sizing is performed for this quadrant else for the relevant

        Returns
        -------
        H : float
            Required borehole length of the borefield [m]

        Raises
        ------
         ValueError
            ValueError when no ground data is provided or quadrant is not in range.
        UnsolvableDueToTemperatureGradient
            Error when the field cannot be sized.
        """
        # check ground data
        if not self.ground_data.check_values():
            raise ValueError("Please provide ground data.")
        # check quadrants
        if not quadrant_sizing in range(0, 5):
            raise ValueError(f"Quadrant {quadrant_sizing} does not exist.")

        # initiate with a given borehole length
        self.H: float = H_init if H_init is not None else self._calculation_setup.H_init

        if quadrant_sizing != 0:
            # size according to a specific quadrant
            self.H, _ = self._size_based_on_temperature_profile(quadrant_sizing)
            return self.H
        else:
            try:
                max_temp, sized = self._size_based_on_temperature_profile(10,
                                                                          deep_sizing=self._calculation_setup.force_deep_sizing)
            except MaximumNumberOfIterations as e:
                # no convergence with normal method, but perhaps with deep_sizing enabled
                if self._calculation_setup.deep_sizing and self.ground_data.variable_Tg:
                    max_temp, sized = self._size_based_on_temperature_profile(10, deep_sizing=True)
                else:
                    raise e
            if sized:
                # already correct size
                self.H = max_temp
                if self.load.imbalance <= 0:
                    self.limiting_quadrant = 1
                else:
                    self.limiting_quadrant = 2
                return max_temp
            min_temp, sized = self._size_based_on_temperature_profile(20)
            if sized:
                self.H = min_temp
                if self.load.imbalance <= 0:
                    self.limiting_quadrant = 4
                else:
                    self.limiting_quadrant = 3
                return min_temp
            raise UnsolvableDueToTemperatureGradient

    def size_L4(self, H_init: float = None, quadrant_sizing: int = 0) -> float:
        """
        This function sizes the borefield based on an hourly (L4) sizing methodology.

        Parameters
        ----------
        H_init : float
            Initial borehole length from where to start the iteration [m]
        quadrant_sizing : int
            If a quadrant is given the sizing is performed for this quadrant else for the relevant

        Returns
        -------
        H : float
            Required borehole length of the borefield [m]

        Raises
        ------
        ValueError
           ValueError when no ground data is provided or quadrant is not in range.
        UnsolvableDueToTemperatureGradient
           When the field cannot be sized due to the temperature gradient.
        """
        # check ground data
        if not self.ground_data.check_values():
            raise ValueError("Please provide ground data.")
        # check quadrants
        if not quadrant_sizing in range(0, 5):
            raise ValueError(f"Quadrant {quadrant_sizing} does not exist.")

        # check if hourly data is given
        if not self.load._hourly:
            raise ValueError("There is no hourly resolution available!")

        # initiate with a given borehole length
        self.H: float = H_init if H_init is not None else self._calculation_setup.H_init

        if quadrant_sizing != 0:
            # size according to a specific quadrant
            self.H, _ = self._size_based_on_temperature_profile(quadrant_sizing, hourly=True)
            return self.H
        else:
            try:
                max_temp, sized = (
                    self._size_based_on_temperature_profile(10, hourly=True,
                                                            deep_sizing=self._calculation_setup.force_deep_sizing)
                    if np.any(self.load.hourly_injection_load)
                    else (0, False)
                )
            except MaximumNumberOfIterations as e:
                # no convergence with normal method, but perhaps with deep_sizing enabled
                if self._calculation_setup.deep_sizing and self.ground_data.variable_Tg:
                    max_temp, sized = (
                        self._size_based_on_temperature_profile(10, hourly=True, deep_sizing=True) if np.any(
                            self.load.hourly_injection_load) else (0, False)
                    )
                else:
                    raise e
            if sized:
                # already correct size
                self.H = max_temp
                if self.load.imbalance <= 0:
                    self.limiting_quadrant = 1
                else:
                    self.limiting_quadrant = 2
                return max_temp
            min_temp, sized = self._size_based_on_temperature_profile(20, hourly=True) if np.any(
                self.load.hourly_extraction_load) else (0, False)
            if sized:
                if self.load.imbalance <= 0:
                    self.limiting_quadrant = 4
                else:
                    self.limiting_quadrant = 3
                self.H = min_temp
                return min_temp
            raise UnsolvableDueToTemperatureGradient

    def calculate_next_depth_deep_sizing(self, current_length: float) -> float:
        """
        This method is a slower but more robust way of calculating the next borehole length in the sizing iteration when the
        borefield is sized for the maximum fluid temperature when there is a non-constant ground temperature.
        The method is based (as can be seen in its corresponding validation document) on the assumption that the
        difference between the maximum temperature in peak injection and the average undisturbed ground temperature
        is irreversily proportional to the borehole length. In this way, given this difference in temperature and the current
        borehole length, a new borehole length can be calculated.

        Parameters
        ----------
        current_length : float
            The current borehole length  [m]

        Returns
        -------
        float
            New borehole length [m]
        """
        # diff between the max temperature in peak injection and the avg undisturbed ground temperature at current_length
        delta_temp = np.max(
            self.results.peak_injection - self.ground_data.calculate_Tg(self.calculate_depth(current_length, self.D)))

        # calculate the maximum temperature difference between the temperature limit and the ground temperature
        # at current_length
        delta_wrt_max = self.Tf_max - self.ground_data.calculate_Tg(self.calculate_depth(current_length, self.D))

        # delta_t1/H1 ~ delta_t2/H2
        # H2 = delta_t2/delta_t1*current_length
        rel_diff = delta_wrt_max / delta_temp
        new_length = current_length / rel_diff

        return new_length

    def _size_based_on_temperature_profile(self, quadrant: int, hourly: bool = False, deep_sizing: bool = False) -> (
            float, bool):
        """
        This function sizes based on the temperature profile.
        It sizes for a specific quadrant and can both size with a monthly or an hourly resolution.

        Parameters
        ----------
        quadrant : int
            Differs from 0 when a sizing in a certain quadrant is desired.
            Quadrants are developed by (Peere et al., 2021) [#PeereBS]_, [#PeereThesis]_
        hourly : bool
            True if an hourly resolution should be used
        deep_sizing : bool
            True if the slower method should be used for the sizing, which is robuster.

        Returns
        -------
        Borehole length : float
            Required borehole length of the borefield [m]
        Sized : bool
            True if the required borehole length also satisfies the other temperature constraint [m]
        """
        # initiate iteration
        H_prev = 0

        if self.H < 1:
            self.H = 50

        if deep_sizing:
            # set borefield to minimal borehole length
            self.H = 20

        # Iterates as long as there is no convergence
        # (convergence if difference between borehole length in iterations is smaller than THRESHOLD_BOREHOLE_LENGTH)
        i = 0
        while not self._check_convergence(self.H, H_prev, i):
            if hourly:
                self._calculate_temperature_profile(self.H, hourly=True)
            else:
                self._calculate_temperature_profile(self.H, hourly=False)
            H_prev = self.H
            if not deep_sizing:
                if quadrant == 1:
                    # maximum temperature
                    # convert back to required length
                    self.H = (np.max(self.results.peak_injection[: 8760 if hourly else 12]) - self._Tg()) / (
                            self.Tf_max - self._Tg()) * H_prev
                elif quadrant == 2:
                    # maximum temperature
                    # convert back to required length
                    self.H = (np.max(self.results.peak_injection[-8760 if hourly else -12:]) - self._Tg()) / (
                            self.Tf_max - self._Tg()) * H_prev
                elif quadrant == 3:
                    # minimum temperature
                    # convert back to required length
                    self.H = (np.min(self.results.peak_extraction[: 8760 if hourly else 12]) - self._Tg()) / (
                            self.Tf_min - self._Tg()) * H_prev
                elif quadrant == 4:
                    # minimum temperature
                    # convert back to required length
                    self.H = (np.min(self.results.peak_extraction[-8760 if hourly else -12:]) - self._Tg()) / (
                            self.Tf_min - self._Tg()) * H_prev
                elif quadrant == 10:
                    # over all years
                    # maximum temperature
                    # convert back to required length
                    self.H = (np.max(self.results.peak_injection) - self._Tg()) / (self.Tf_max - self._Tg()) * H_prev
                elif quadrant == 20:
                    # over all years
                    # minimum temperature
                    # convert back to required length
                    self.H = (np.min(self.results.peak_extraction) - self._Tg()) / (self.Tf_min - self._Tg()) * H_prev
            elif self.ground_data.variable_Tg:
                # for when the temperature gradient is active and it is injection
                self.H = self.calculate_next_depth_deep_sizing(H_prev)
            if self.H < 0:
                return 0, False

            i += 1

        return self.H, (np.max(self.results.peak_injection) <= self.Tf_max + 0.05 or (
                quadrant == 10 or quadrant == 1 or quadrant == 2)) and (
                               np.min(self.results.peak_extraction) >= self.Tf_min - 0.05 or (
                               quadrant == 20 or quadrant == 3 or quadrant == 4)
                       )

    @property
    def investment_cost(self) -> float:
        """
        This function calculates the investment cost based on a cost profile linear to the total borehole length.

        Returns
        -------
        float
            Investment cost
        """
        return np.polyval(self.cost_investment, self.H * self.number_of_boreholes)

    def calculate_temperatures(self, length: float = None, hourly: bool = False) -> None:
        """
        Calculate all the temperatures without plotting the figure. When length is given, it calculates it for a given
        borehole length.

        Parameters
        ----------
        length : float
            Borehole length for which the temperature profile should be calculated for [m]
        hourly : bool
            True when the temperatures should be calculated based on hourly data

        Returns
        -------
        None
        """
        self._calculate_temperature_profile(H=length, hourly=hourly)

    def print_temperature_profile(self, legend: bool = True, plot_hourly: bool = False) -> None:
        """
        This function plots the temperature profile for the calculated borehole length.
        It uses the available temperature profile data.

        Parameters
        ----------
        legend : bool
            True if the legend should be printed
        plot_hourly : bool
            True if the temperature profile printed should be based on the hourly load profile.

        Returns
        -------
        fig, ax
            Figure object
        """
        # calculate temperature profile
        self._calculate_temperature_profile(hourly=plot_hourly)

        return self._plot_temperature_profile(legend=legend, plot_hourly=plot_hourly)

    def print_temperature_profile_fixed_length(self, length: float, legend: bool = True, plot_hourly: bool = False):
        """
        This function plots the temperature profile for a fixed borehole length.
        It uses the already calculated temperature profile data, if available.

        Parameters
        ----------
        length : float
            Borehole length at which the temperature profile should be shown
        legend : bool
            True if the legend should be printed
        plot_hourly : bool
            True if the temperature profile printed should be based on the hourly load profile.

        Returns
        -------
        fig, ax
            Figure object
        """
        # calculate temperature profile
        self._calculate_temperature_profile(H=length, hourly=plot_hourly)

        return self._plot_temperature_profile(legend=legend, plot_hourly=plot_hourly)

    def _plot_temperature_profile(self, legend: bool = True, plot_hourly: bool = False) -> Tuple[plt.Figure, plt.Axes]:
        """
        This function plots the temperature profile.

        Parameters
        ----------
        legend : bool
            True if the legend should be printed
        plot_hourly : bool
            True if the temperature profile printed should be based on the hourly load profile.

        Returns
        -------
        fig, ax
            Figure object
        """

        # make a time array
        if plot_hourly:
            time_array = self.load.time_L4 / 12 / 3600 / 730
        else:
            time_array = self.load.time_L3 / 12 / 730.0 / 3600.0

        # plt.rc('figure')
        # create new figure and axes if it not already exits otherwise clear it.
        fig = plt.figure()
        ax = fig.add_subplot(111)
        # set axes labelsv
        ax.set_xlabel(r"Time (year)")
        ax.set_ylabel(r"Temperature ($^\circ C$)")
        ax.yaxis.label.set_color(plt.rcParams["axes.labelcolor"])
        ax.xaxis.label.set_color(plt.rcParams["axes.labelcolor"])

        # plot Temperatures
        ax.step(time_array, self.results.Tb, "k-", where="post", lw=1.5, label="Tb")

        if plot_hourly:
            ax.step(time_array, self.results.Tf, "b-", where="post", lw=1, label="Tf")
        else:
            ax.step(time_array, self.results.peak_injection, "b-", where="post", lw=1.5, label="Tf peak injection")
            ax.step(time_array, self.results.peak_extraction, "r-", where="post", lw=1.5, label="Tf peak extraction")

            ax.step(time_array, self.results.monthly_injection, color="b", linestyle="dashed", where="post", lw=1.5,
                    label="Tf base injection")
            ax.step(time_array, self.results.monthly_extraction, color="r", linestyle="dashed", where="post", lw=1.5,
                    label="Tf base extraction")

        # define temperature bounds
        ax.hlines(self.Tf_min, 0, self.simulation_period, colors="r", linestyles="dashed", label="", lw=1)
        ax.hlines(self.Tf_max, 0, self.simulation_period, colors="b", linestyles="dashed", label="", lw=1)
        ax.set_xticks(range(0, self.simulation_period + 1, 2))

        # Plot legend
        if legend:
            ax.legend()
        ax.set_xlim(left=0, right=self.simulation_period)
        plt.show()
        return fig, ax

    def _delete_calculated_temperatures(self) -> None:
        """
        This function deletes all the calculated temperatures.

        Returns
        -------
        None
        """
        self.results = ResultsMonthly()
        self.load.reset_results(self.Tf_min, self.Tf_max)

    def _calculate_temperature_profile(self, H: float = None, hourly: bool = False) -> None:
        """
        This function calculates the evolution in the fluid temperature and borehole wall temperature.

        Parameters
        ----------
        H : float
            Borehole length at which the temperatures should be evaluated [m]. If None, then the current length is taken.
        hourly : bool
            True if the temperature evolution should be calculated on an hourly basis.

        Returns
        -------
        None
        """

        # reset self.results
        self.results = ResultsMonthly()

        def calculate_temperatures(H, hourly=hourly, results_temperature=ResultsMonthly()):
            # set Rb* value
            H = H if H is not None else self.H
            depth = self.calculate_depth(H, self.D)

            results = None

            def get_rb(temperature):
                if len(temperature) == 0:
                    return self.borehole.get_Rb(H, self.D, self.r_b,
                                                self.ground_data.k_s(depth, self.D), depth,
                                                temperature=self.Tf_min)
                return self.borehole.get_Rb(H, self.D, self.r_b,
                                            self.ground_data.k_s(depth, self.D), depth,
                                            temperature=temperature)

            if not hourly:
                # self.g-function is a function that uses the precalculated data to interpolate the correct values of the
                # g-function. This dataset is checked over and over again and is correct
                g_values = self.gfunction(self.load.time_L3, H)

                # the g-function value of the peak with length_peak hours
                g_value_peak_injection = self.gfunction(self.load.peak_injection_duration, H)[0]
                if self.load.peak_injection_duration == self.load.peak_extraction_duration:
                    g_value_peak_extraction = g_value_peak_injection
                else:
                    g_value_peak_extraction = self.gfunction(self.load.peak_extraction_duration, H)[0]

                # calculation of needed differences of the g-function values. These are the weight factors in the calculation
                # of Tb.
                g_value_differences = np.diff(g_values, prepend=0)

                # convolution to get the monthly results
                results = convolve(self.load.monthly_average_injection_power_simulation_period * 1000,
                                   g_value_differences)[
                          : 12 * self.simulation_period]

                # calculation the borehole wall temperature for every month i
                k_s = self.ground_data.k_s(self.calculate_depth(H, self.D), self.D)
                Tb = results / (2 * pi * k_s) / (H * self.number_of_boreholes) + self._Tg(H)

                # now the Tf will be calculated based on
                # Tf = Tb + Q * R_b
                results_month_injection = Tb + self.load.monthly_baseload_injection_power_simulation_period * 1000 * (
                        get_rb(results_temperature.monthly_injection) / self.number_of_boreholes / H)
                results_month_extraction = Tb - self.load.monthly_baseload_extraction_power_simulation_period * 1000 * (
                        get_rb(results_temperature.monthly_extraction) / self.number_of_boreholes / H)

                # extra summation if the g-function value for the peak is included
                results_peak_injection = (
                        Tb
                        + (self.load.monthly_peak_injection_simulation_period
                           * (g_value_peak_injection / k_s / 2 / pi + get_rb(results_temperature.peak_injection))
                           - self.load.monthly_baseload_injection_power_simulation_period * g_value_peak_injection / k_s / 2 / pi)
                        * 1000 / self.number_of_boreholes / H
                )
                results_peak_extraction = (
                        Tb +
                        (- self.load.monthly_peak_extraction_simulation_period
                         * (g_value_peak_extraction / k_s / 2 / pi + get_rb(results_temperature.peak_extraction))
                         + self.load.monthly_baseload_extraction_power_simulation_period * g_value_peak_extraction / k_s / 2 / pi)
                        * 1000 / self.number_of_boreholes / H
                )
                # save temperatures under variable
                results = ResultsMonthly(
                    borehole_wall_temp=Tb,
                    peak_extraction=results_peak_extraction,
                    peak_injection=results_peak_injection,
                    monthly_extraction=results_month_extraction,
                    monthly_injection=results_month_injection,
                )

            if hourly:
                # check for hourly data if this is requested
                if not self.load._hourly:
                    raise ValueError("There is no hourly resolution available!")

                hourly_load = self.load.hourly_net_resulting_injection_power

                # self.g-function is a function that uses the precalculated data to interpolate the correct values of the
                # g-function. This dataset is checked over and over again and is correct
                g_values = self.gfunction(self.load.time_L4, H)

                # calculation of needed differences of the g-function values. These are the weight factors in the calculation
                # of Tb.
                g_value_differences = np.diff(g_values, prepend=0)

                # convolution to get the monthly results
                results = convolve(hourly_load * 1000, g_value_differences)[: len(hourly_load)]

                # calculation the borehole wall temperature for every month i
                Tb = results / (2 * pi * self.ground_data.k_s(self.calculate_depth(H, self.D), self.D)) / (
                        H * self.number_of_boreholes) + self._Tg(H)

                # now the Tf will be calculated based on
                # Tf = Tb + Q * R_b
                temperature_result = Tb + hourly_load * 1000 * (
                        get_rb(results_temperature.peak_injection) / self.number_of_boreholes / H)

                # reset other variables
                results = ResultsHourly(borehole_wall_temp=Tb, temperature_fluid=temperature_result)

            return results

        def calculate_difference(results_old: Union[ResultsMonthly, ResultsHourly],
                                 result_new: Union[ResultsMonthly, ResultsHourly]) -> float:
            return max(
                np.max(result_new.peak_injection - results_old.peak_injection),
                np.max(result_new.peak_extraction - results_old.peak_extraction))

        if isinstance(self.load, _LoadDataBuilding) or \
                isinstance(self.borehole.fluid_data, TemperatureDependentFluidData):
            # when building load is given, the load should be updated after each temperature calculation.
            # check if active_passive, because then, threshold should be taken
            if isinstance(self.load, _LoadDataBuilding) and \
                    isinstance(self.load.eer, EERCombined) and self.load.eer.threshold_temperature is not None:
                self.load.reset_results(self.Tf_min, self.load.eer.threshold_temperature)
            else:
                self.load.reset_results(self.Tf_min, self.Tf_max)
            results_old = calculate_temperatures(H, hourly=hourly)
            self.load.set_results(results_old)
            results = calculate_temperatures(H, hourly=hourly, results_temperature=results_old)

            # safety
            i = 0
            while calculate_difference(results_old, results) > self._calculation_setup.atol \
                    and i < self._calculation_setup.max_nb_of_iterations:
                results_old = results
                self.load.set_results(results)
                results = calculate_temperatures(H, hourly=hourly, results_temperature=results)
                i += 1
            self.results = results
            self.load.set_results(results)
            return

        self.results = calculate_temperatures(H, hourly=hourly)

    def set_options_gfunction_calculation(self, options: dict) -> None:
        """
        This function sets the options for the gfunction calculation of pygfunction.
        This dictionary is directly passed through to the gFunction class of pygfunction.
        For more information, please visit the documentation of pygfunction.

        Parameters
        ----------
        options : dict
            Dictionary with options for the gFunction class of pygfunction

        Returns
        -------
        None
        """
        self.gfunction_calculation_object.set_options_gfunction_calculation(options)

    def gfunction(self, time_value: ArrayLike, H: float = None) -> np.ndarray:
        """
        This function returns the gfunction value.
        It can do so by either calculating the gfunctions just-in-time or by interpolating from a
        loaded custom data file.

        Parameters
        ----------
        time_value : list, float, np.ndarray
            Time value(s) in seconds at which the gfunctions should be calculated
        H : float
            Borehole length [m] at which the gfunctions should be calculated.
            If no length is given, the current borehole length is taken.

        Returns
        -------
        gvalue : np.ndarray
            1D array with the g-values for all the requested time_value(s)
        """
        H_var = H
        if H is None:
            H_var = self.H
        # when using a variable ground temperature, sometimes no solution can be found
        if not isinstance(self.ground_data, GroundConstantTemperature) and H_var > Borefield.THRESHOLD_DEPTH_ERROR:
            raise UnsolvableDueToTemperatureGradient

        def jit_gfunction_calculation() -> np.ndarray:
            """
            This function calculates the gfunction just-in-time.

            Returns
            -------
            gvalues : np.ndarray
                1D array with the g-values for the requested time intervals
            """
            # set the correct borehole length
            if not H is None:
                # only update if H is provided, otherwise the borehole length of the borefield itself will be used
                self.H = H
            return self.gfunction_calculation_object.calculate(
                time_value, self.borefield, self.ground_data.alpha(self.depth, self.D),
                interpolate=self._calculation_setup.interpolate_gfunctions,
                use_neural_network=self._calculation_setup.use_neural_network,
                borefield_description=self._borefield_description
            )

        ## 1 bypass any possible precalculated g-functions
        # if calculate is False, then the gfunctions are calculated jit
        if not self._calculation_setup.use_precalculated_dataset:
            return jit_gfunction_calculation()

        ## 2 use precalculated g-functions when available
        if self.custom_gfunction is not None:
            # there is precalculated data available
            # check if the requested values can be calculated using the custom_gfunction
            if self.custom_gfunction.within_range(time_value, H_var):
                return self.custom_gfunction.calculate_gfunction(time_value, H_var)

        ## 3 calculate g-function jit
        return jit_gfunction_calculation()

    def create_custom_dataset(self, time_array: ArrayLike = None, borehole_length_array: ArrayLike = None,
                              options: dict = {}) -> None:
        """
        This function makes a datafile for a given custom borefield and sets it for the borefield object.
        It automatically sets this datafile in the current borefield object, so it can be used as a source for
        the interpolation of g-values.

        Parameters
        ----------
        time_array : list, np.array
            Time values (in seconds) used for the calculation of the datafile
        borehole_length_array : list, np.array
            List or arrays of borehole lengths for which the datafile should be created
        options : dict
            Options for the g-function calculation (check pygfunction.gfunction.gFunction() for more information)

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When no borefield or ground data is set
        """

        if self.borefield is None:
            raise ValueError("No borefield is set for which the gfunctions should be calculated")
        try:
            self.ground_data.alpha(depth=100)
        except AttributeError:
            raise ValueError("No ground data is set for which the gfunctions should be calculated")

        self.custom_gfunction = CustomGFunction(time_array, borehole_length_array, options)
        self.custom_gfunction.create_custom_dataset(self.borefield, self.ground_data.alpha)

    def Re(self, **kwargs) -> float:
        """
        Reynolds number.

        Returns
        -------
        float
            Reynolds number
        """
        return self.borehole.Re(**kwargs)

    def calculate_quadrant(self) -> int:
        """
        This function returns the borefield quadrant (as defined by Peere et al., 2021 [#PeereEtAl]_)
        based on the calculated temperature profile.
        If there is no limiting quadrant, None is returned.\n
        Quadrant 1 is limited in the first year by the maximum temperature\n
        Quadrant 2 is limited in the last year by the maximum temperature\n
        Quadrant 3 is limited in the first year by the minimum temperature\n
        Quadrant 4 is limited in the last year by the maximum temperature

        Returns
        ----------
        quadrant : int
            The quadrant which limits the borefield

        References
        ----------
        .. [#PeereEtAl] Peere, W., Picard, D., Cupeiro Figueroa, I., Boydens, W., and Helsen, L. (2021) Validated combined first and last year borefield sizing methodology. In Proceedings of International Building Simulation Conference 2021. Brugge (Belgium), 1-3 September 2021. https://doi.org/10.26868/25222708.2021.30180
        """

        # calculate temperatures if they are not calculated
        if not np.any(self.results.peak_extraction):
            print(
                "There are not yet temperatures calculated, hence there is no limiting quadrant. The temperature is calculated now, based on monthly values."
            )
            self.calculate_temperatures()

        # calculate max/min fluid temperatures
        max_temp = np.max(self.results.peak_injection)
        min_temp = np.min(self.results.peak_extraction)

        # calculate temperature difference w.r.t. the limits
        DT_max = -self.Tf_max + max_temp + 1000  # + 1000 to have no problems with negative temperatures
        DT_min = self.Tf_min - min_temp + 1000

        # if the temperature limit is not crossed, return None
        if self.Tf_max - 0.1 > max_temp and self.Tf_min + 0.1 < min_temp:
            return

        # True if extraction dominated
        if self.load.imbalance < 0:
            # either quadrant 1 or 4
            if DT_min > DT_max:
                # limited by minimum temperature
                return 4
            return 1

        # quadrant 2 or 3
        if DT_min > DT_max:
            # limited by minimum temperature
            return 3
        return 2

    def __export__(self):
        return {
            'Maximum average fluid temperature [°C]': self.Tf_max,
            'Minimum average fluid temperature [°C]': self.Tf_min,
            'Average buried depth [m]': self.D,
            'Average borehole length [m]': self.H,
            'Average borehole depth [m]': self.depth,
            'Borehole diameter [mm]': self.r_b * 2000,
            'Number of boreholes [-]': self.number_of_boreholes,
            'Ground data': self.ground_data.__export__(),
            'Borehole data': self.borehole.__export__(),
            'Load data': self.load.__export__()
        }
