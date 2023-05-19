"""
This file contains all the code for the borefield calculations.
"""
from math import pi
from typing import Tuple, Union, List

import matplotlib.pyplot as plt
import numpy as np
import pygfunction as gt
from scipy.signal import convolve

from GHEtool.VariableClasses import GroundData, FluidData, PipeData
from GHEtool.VariableClasses import CustomGFunction, load_custom_gfunction, GFunction, SizingSetup
from GHEtool.VariableClasses.BaseClass import BaseClass


class Borefield(BaseClass):
    """Main borefield class"""
    UPM: float = 730.  # number of hours per month
    THRESHOLD_BOREHOLE_DEPTH: float = 0.05  # threshold for iteration
    MAX_SIMULATION_PERIOD: int = 100  # maximal value for simulation

    # define default values
    DEFAULT_INVESTMENT: list = [35, 0]  # 35 EUR/m
    DEFAULT_LENGTH_PEAK: int = 6  # hours
    THRESHOLD_DEPTH_ERROR: int = 10000  # m

    HOURLY_LOAD_ARRAY: np.ndarray = np.arange(0, 8761, UPM).astype(np.uint32)

    __slots__ = 'baseload_heating', 'baseload_cooling', 'H', 'H_init', 'Rb', 'ty', 'tm', \
                'hourly_heating_load', 'hourly_cooling_load', 'number_of_boreholes', '_borefield', 'cost_investment', \
                'length_peak', 'th', 'Tf_max', 'Tf_min', 'limiting_quadrant', 'monthly_load', 'monthly_load_heating', \
                'monthly_load_cooling', 'peak_heating', 'imbalance', 'qa', 'Tf', 'qm', 'qh', 'qpm', 'tcm', 'tpm', \
                'peak_cooling', 'simulation_period', 'ground_data', 'pipe_data', 'fluid_data',\
                'results_peak_heating', 'time_L4', 'options_pygfunction',\
                'results_peak_cooling', 'results_month_cooling', 'results_month_heating', 'Tb', 'THRESHOLD_WARNING_SHALLOW_FIELD', \
                'gui', 'time_L3_last_year', 'peak_heating_external', 'peak_cooling_external', \
                'monthly_load_heating_external', 'monthly_load_cooling_external', 'hourly_heating_load_external', \
                'hourly_cooling_load_external', 'hourly_heating_load_on_the_borefield', 'hourly_cooling_load_on_the_borefield', \
                'printing', 'combo', 'D', 'r_b', 'recalculation_needed', 'gfunction_calculation_object',\
                'H_init', 'use_precalculated_data', '_sizing_setup'

    def __init__(self, simulation_period: int = 20, peak_heating: list = None,
                 peak_cooling: list = None, baseload_heating: list = None, baseload_cooling: list = None,
                 borefield=None, custom_gfunction: CustomGFunction = None, gui: bool = False):
        """

        Parameters
        ----------
        simulation_period : int
            Simulation period in years
        peak_heating : list, numpy array
            Monthly peak heating values [kW]
        peak_cooling : list, numpy array
            Monthly peak cooling values [kW]
        baseload_heating : list, numpy array
            Monthly baseload heating values [kWh]
        baseload_cooling : list, numpy array
            Monthly baseload heating values [kWh]
        borefield : pygfunction borehole/borefield object
            Set the borefield for which the calculations will be carried out
        custom_gfunction : CustomGFunction
            Custom gfunction dataset
        gui : bool
            True if the Borefield object is created by the GUI. This should not be used in the code version
            of GHEtool itself.

        Examples
        --------

        monthly peak values [kW]

        >>> peak_cooling = np.array([0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.])
        >>> peak_heating = np.array([160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.])

        annual heating and cooling load [kWh]

        >>> annual_heating_load = 300 * 10 ** 3
        >>> annual_cooling_load = 160 * 10 ** 3

        percentage of annual load per month (15.5% for January ...)

        >>> monthly_load_heating_percentage = np.array([0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144])
        >>> monthly_load_cooling_percentage = np.array([0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025])

        resulting load per month [kWh]

        >>> monthly_load_heating = annual_heating_load * monthly_load_heating_percentage
        >>> monthly_load_cooling = annual_cooling_load * monthly_load_cooling_percentage

        create the borefield object

        >>> borefield = Borefield(simulation_period=20,
        >>>                      peak_heating=peak_heating,
        >>>                      peak_cooling=peak_cooling,
        >>>                      baseload_heating=monthly_load_heating,
        >>>                      baseload_cooling=monthly_load_cooling)

        """

        # initiate vars
        LIST_OF_ZEROS = np.zeros(12)
        if baseload_cooling is None:
            baseload_cooling: list = LIST_OF_ZEROS
        if baseload_heating is None:
            baseload_heating: list = LIST_OF_ZEROS
        if peak_cooling is None:
            peak_cooling: list = LIST_OF_ZEROS
        if peak_heating is None:
            peak_heating: list = LIST_OF_ZEROS

        self.limiting_quadrant: int = 0  # parameter that tells in which quadrant the field is limited
        # m hereafter one needs to chance to fewer boreholes with more depth, because the calculations are no longer
        # that accurate.
        self.THRESHOLD_WARNING_SHALLOW_FIELD: int = 50

        # setting this to False will make sure every g-value is calculated on the spot
        # this will make everything way slower!
        self.use_precalculated_data: bool = True

        self.monthly_load = np.array([])
        self.H_init: float = 0.
        self.custom_gfunction: CustomGFunction = custom_gfunction
        self.gfunction_calculation_object: GFunction = GFunction()
        self.recalculation_needed: bool = False

        ## params w.r.t. pygfunction
        self.options_pygfunction: dict = {"method": "equivalent"}

        # initialize variables for temperature plotting
        self.results_peak_heating = np.array([])  # list with the minimum temperatures due to the peak heating
        self.results_peak_cooling = np.array([])  # list with the maximum temperatures due to peak cooling
        self.results_month_heating = np.array([])
        self.results_month_cooling = np.array([])
        self.Tb = np.array([])  # list of borehole wall temperatures

        # initiate variables for optimal sizing
        self.hourly_heating_load = np.array([])
        self.hourly_cooling_load = np.array([])
        self.hourly_cooling_load_external = np.array([])
        self.hourly_heating_load_external = np.array([])
        self.peak_heating_external = np.array([])
        self.peak_cooling_external = np.array([])
        self.monthly_load_heating_external = np.array([])
        self.monthly_load_cooling_external = np.array([])
        self.hourly_heating_load_on_the_borefield = np.array([])
        self.hourly_cooling_load_on_the_borefield = np.array([])

        # initiate load variables
        self.baseload_heating = LIST_OF_ZEROS  # list with baseload heating kWh
        self.baseload_cooling = LIST_OF_ZEROS  # list with baseload cooling kWh
        self.monthly_load_cooling = LIST_OF_ZEROS
        self.monthly_load_heating = LIST_OF_ZEROS
        self.peak_cooling = LIST_OF_ZEROS  # list with the peak load cooling kW
        self.peak_heating = LIST_OF_ZEROS  # list with peak load heating kW

        # initiate time variables
        self.ty: float = 0.  # yearly time value
        self.tm: float = 0.  # monthly time value
        self.th: float = 0.  # duration of peak in seconds
        self.length_peak: float = Borefield.DEFAULT_LENGTH_PEAK
        self.length_peak_cooling: float = Borefield.DEFAULT_LENGTH_PEAK
        self.length_peak_heating: float = Borefield.DEFAULT_LENGTH_PEAK
        self.tcm: float = 0.  # time constant for first year sizing
        self.tpm: float = 0.  # time constant for first year sizing
        self.time_L3_last_year = np.array([])  # list with time values for L3 sizing
        self.time_L4 = np.array([])  # list with all the time values for the L4 sizing

        # initiate ground loads
        self.qa: float = 0.  # yearly load W
        self.qm: float = 0.  # monthly load W
        self.qh: float = 0.  # peak load W
        self.qpm: float = 0.  # cumulative load first year sizing
        self.imbalance: float = 0.  # imbalance kWh

        # initiate ground parameters
        self.H = 0.  # borehole depth m
        self.Rb = 0.  # effective borehole thermal resistance mK/W
        self.number_of_boreholes = 0  # number of total boreholes #
        self.ground_data: GroundData = GroundData()
        self.D: float = 0.  # buried depth of the borehole [m]
        self.r_b: float = 0.  # borehole radius [m]

        # initiate fluid parameters
        self.Tf: float = 0.  # temperature of the fluid
        self.Tf_max: float = 16.  # maximum temperature of the fluid
        self.Tf_min: float = 0.  # minimum temperature of the fluid
        self.fluid_data: FluidData = FluidData()

        # initiate borehole parameters
        self.pipe_data: PipeData = PipeData()

        # initiate different sizing
        self._sizing_setup: SizingSetup = SizingSetup()
        self.H_init: float = 100.
        self.sizing_setup()

        # check if the GHEtool is used by the gui i
        self.gui = gui

        # set boolean for printing output
        self.printing: bool = True
        # set list for the sizing ba length and width output
        self.combo: list = []

        # set load profiles
        self.set_peak_heating(peak_heating)
        self.set_peak_cooling(peak_cooling)
        self.set_baseload_cooling(baseload_cooling)
        self.set_baseload_heating(baseload_heating)

        # set simulation period
        self.simulation_period: int = simulation_period

        # set investment cost
        self.cost_investment: list = Borefield.DEFAULT_INVESTMENT

        # set length of the peak
        self.set_length_peak()

        # set a custom borefield
        self.borefield = borefield

    def _set_number_of_boreholes(self) -> None:
        """
        This functions sets the number of boreholes based on the length of the borefield attribute.

        Returns
        -------
        None
        """
        self.number_of_boreholes = len(self.borefield) if self.borefield is not None else 0

    def set_borefield(self, borefield: List[gt.boreholes.Borehole] = None) -> None:
        """
        This function set the borefield object.

        Parameters
        ----------
        borefield : List[pygfunction.boreholes.Borehole]
            Borefield created with the pygfunction package

        Returns
        -------
        None
        """
        if borefield is None:
            return
        self.borefield = borefield

    def create_rectangular_borefield(self, N_1: int, N_2: int, B_1: int, B_2: int, H: float, D: float = 1, r_b: float = 0.075):
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
            Borehole depth [m]
        D : float
            Borehole buried depth [m]
        r_b : float
            Borehole radius [m]

        Returns
        -------
        pygfunction borefield object
        """
        borefield = gt.boreholes.rectangle_field(N_1, N_2, B_1, B_2, H, D, r_b)
        self.set_borefield(borefield)
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
            Borehole depth [m]
        D : float
            Borehole buried depth [m]
        r_b : float
            Borehole radius [m]

        Returns
        -------
        pygfunction borefield object
        """
        borefield = gt.boreholes.circle_field(N, R, H, D, r_b)
        self.set_borefield(borefield)
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
    def borefield(self, borefield: List[gt.boreholes.Borehole]=None) -> None:
        """
        This function sets the borefield configuration. When no input is given, the borefield variable will be deleted.

        Parameters
        ----------
        borefield : List[pygfunction.boreholes.Borehole]
            Borefield created with the pygfunction package

        Returns
        -------
        None
        """
        if borefield is None:
            del self.borefield
            return
        self._borefield = borefield
        self._set_number_of_boreholes()
        self.D = borefield[0].D
        self.r_b = borefield[0].r_b
        self.H = borefield[0].H

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
        self._set_number_of_boreholes()

    def _update_borefield_depth(self, H: float = None) -> None:
        """
        This function updates the borehole depth.

        Parameters
        ----------
        H : float
            Borehole depth.

        Returns
        -------
        None
        """
        H = H if H is not None else self.H

        if self._borefield[0].H == H:
            # the borefield is already at the correct depth
            return

        for bor in self._borefield:
            bor.H = H

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

    def set_investment_cost(self, investment_cost: list =None) -> None:
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

    def set_length_peak(self, length: float = DEFAULT_LENGTH_PEAK) -> None:
        """
        This function sets the length of the peak.

        Parameters
        ----------
        length : float
            Length of the peak [hours]

        Returns
        -------
        None
        """
        self.set_length_peak_heating(length)
        self.set_length_peak_cooling(length)
        self.length_peak = length
        self._set_time_constants()

    def set_length_peak_heating(self, length: float = DEFAULT_LENGTH_PEAK) -> None:
        """
        This function sets the length of the heating peak.

        Parameters
        ----------
        length : float
            Length of the peak [hours]

        Returns
        -------
        None
        """
        self.length_peak_heating = length

    def set_length_peak_cooling(self, length: float = DEFAULT_LENGTH_PEAK) -> None:
        """
        This function sets the length of the cooling peak.

        Parameters
        ----------
        length : float
            Length of the peak [hours]

        Returns
        -------
        None
        """
        self.length_peak_cooling = length

    def set_simulation_period(self, simulation_period: int) -> None:
        """
        This function sets the simulation period and updates the time constants.

        Parameters
        ----------
        simulation_period : int
            Simulation period [years]

        Returns
        -------
        None
        """
        self.simulation_period = simulation_period
        self._set_time_constants()

    def _set_time_constants(self) -> None:
        """
        This function calculates and sets the time constants for the L2 and L3 sizing.

        Parameters
        ----------
        length_peak : float
            Length of the peak [hours]

        Returns
        -------
        None
        """
        # Number of segments per borehole
        self.th: float = self.length_peak * 3600.  # length of peak in seconds
        self.ty: float = self.simulation_period * 8760. * 3600
        self.tm: float = Borefield.UPM * 3600.

        # set the time array for the L3 sizing
        # This is one time for every month in the whole simulation period
        self.time_L3_last_year = Borefield.UPM * 3600 * np.arange(1, self.simulation_period * 12 + 1)

        # set the time constant for the L4 sizing
        self.time_L4 = 3600 * np.arange(1, 8760 * self.simulation_period + 1, dtype=np.float16)
        if np.isinf(self.time_L4).any():
            # 16 bit is not enough, go to 32
            self.time_L4 = 3600 * np.arange(1, 8760 * self.simulation_period + 1, dtype=np.float32)

    def set_ground_parameters(self, data: GroundData) -> None:
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
        self.Rb: float = data.Rb

        # Ground properties
        self.ground_data = data

        # new ground data implies that a new g-function should be loaded
        self.custom_gfunction = None

    def set_fluid_parameters(self, data: FluidData) -> None:
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
        self.fluid_data = data

        if self.pipe_data.check_values():
            self.calculate_fluid_thermal_resistance()

    def set_pipe_parameters(self, data: PipeData) -> None:
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
        self.pipe_data = data

        # calculate the different resistances
        if self.fluid_data.check_values():
            self.calculate_fluid_thermal_resistance()
        self.pipe_data.calculate_pipe_thermal_resistance()

    def set_max_ground_temperature(self, temp: float) -> None:
        """
        This functions sets the maximal ground temperature to temp.

        Parameters
        ----------
        temp : float
            Maximal ground temperature [deg C]

        Returns
        -------
        None
        """
        self.Tf_max: float = temp

    def set_min_ground_temperature(self, temp: float) -> None:
        """
        This functions sets the minimal ground temperature to temp.

        Parameters
        ----------
        temp : float
            Minimal ground temperature [deg C]

        Returns
        -------
        None
        """
        self.Tf_min: float = temp

    def calculate_fluid_thermal_resistance(self) -> None:
        """
        This function calculates and sets the fluid thermal resistance R_f.

        Returns
        -------
        None
        """
        self.fluid_data.h_f: float =\
            gt.pipes.convective_heat_transfer_coefficient_circular_pipe(self.fluid_data.mfr /
                                                                        self.pipe_data.number_of_pipes,
                                                                        self.pipe_data.r_in,
                                                                        self.fluid_data.mu,
                                                                        self.fluid_data.rho,
                                                                        self.fluid_data.k_f,
                                                                        self.fluid_data.Cp,
                                                                        self.pipe_data.epsilon)
        self.fluid_data.R_f: float = 1. / (self.fluid_data.h_f * 2 * pi * self.pipe_data.r_in)

    @property
    def _Rb(self) -> float:
        """
        This function gives back the equivalent borehole resistance.
        If self._sizing_setup.use_constant_Rb is False, it calculates the equivalent borehole thermal resistance.

        Returns
        -------
        Rb : float
            Equivalent borehole thermal resistance [mK/W]
        """
        # use a constant Rb*
        if self._sizing_setup.use_constant_Rb:
            return self.Rb

        # calculate Rb*
        return self.calculate_Rb()

    def _Tg(self, H: float = None) -> float:
        """
        This function gives back the ground temperature
        When use_constant_Tg is False, the thermal heat flux is taken into account.

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

        return self.ground_data.calculate_Tg(H, use_constant_Tg=self._sizing_setup.use_constant_Tg)

    def calculate_Rb(self) -> float:
        """
        This function returns the calculated equivalent borehole thermal resistance Rb* value.

        Returns
        -------
        Rb* : float
            Equivalent borehole thermal resistance [mK/W]

        Raises
        ------
        ValueError
            ValueError when no pipe or fluid data is available.
        """
        # check if all data is available
        if not self.pipe_data.check_values() or not self.fluid_data.check_values():
            print("Please make sure you set al the pipe and fluid data.")
            raise ValueError

        # initiate temporary borefield
        borehole = gt.boreholes.Borehole(self.H, self.D, self.r_b, 0, 0)
        # initiate pipe
        pipe = gt.pipes.MultipleUTube(self.pipe_data.pos, self.pipe_data.r_in, self.pipe_data.r_out,
                                      borehole, self.ground_data.k_s, self.pipe_data.k_g,
                                      self.pipe_data.R_p + self.fluid_data.R_f, self.pipe_data.number_of_pipes, J=2)

        return pipe.effective_borehole_thermal_resistance(self.fluid_data.mfr, self.fluid_data.Cp)

    @property
    def _Ahmadfard(self) -> float:
        """
        This function sizes the field based on the last year of operation, i.e. quadrants 2 and 4.

        It uses the methodology developed by (Ahmadfard and Bernier, 2019) [#Ahmadfard2019]_.
        The concept of borefield quadrants is developed by (Peere et al., 2020) [#PeereBS]_ [#PeereThesis]_.

        Returns
        -------
        H : float
            Required borehole depth [m]

        References
        ----------
        .. [#Ahmadfard2019] Ahmadfard M. and Bernier M., A review of vertical ground heat exchanger sizing tools including an inter-model comparison,
        Renewable and Sustainable Energy Reviews, Volume 110, 2019, Pages 247-265, ISSN 1364-0321, https://doi.org/10.1016/j.rser.2019.04.045
        .. [#PeereBS] Peere, W., Picard, D., Cupeiro Figueroa, I., Boydens, W., and Helsen, L. (2021) Validated combined first and last year borefield sizing methodology. In Proceedings of International Building Simulation Conference 2021. Brugge (Belgium), 1-3 September 2021. https://doi.org/10.26868/25222708.2021.30180
        .. [#PeereThesis] Peere, W. (2020) Methode voor economische optimalisatie van geothermische verwarmings- en koelsystemen. Master thesis, Department of Mechanical Engineering, KU Leuven, Belgium.
        """
        # initiate iteration
        H_prev = 0
        # set minimal depth to 50 m
        self.H = 50 if self.H < 1 else self.H

        time = np.array([self.th, self.th + self.tm, self.ty + self.tm + self.th])
        # Iterates as long as there is no convergence
        # (convergence if difference between depth in iterations is smaller than THRESHOLD_BOREHOLE_DEPTH)
        while abs(self.H - H_prev) >= Borefield.THRESHOLD_BOREHOLE_DEPTH:
            # calculate the required g-function values
            gfunct_uniform_T = self.gfunction(time, self.H)
            # calculate the thermal resistances
            Ra = (gfunct_uniform_T[2] - gfunct_uniform_T[1]) / (2 * pi * self.ground_data.k_s)
            Rm = (gfunct_uniform_T[1] - gfunct_uniform_T[0]) / (2 * pi * self.ground_data.k_s)
            Rd = (gfunct_uniform_T[0]) / (2 * pi * self.ground_data.k_s)
            # calculate the total borehole length
            L = (self.qa * Ra + self.qm * Rm + self.qh * Rd + self.qh * self._Rb) / abs(self.Tf - self._Tg())
            # updating the depth values
            H_prev = self.H
            self.H = L / self.number_of_boreholes
        return self.H

    @property
    def _Carcel(self) -> float:
        """
        This function sizes the field based on the first year of operation, i.e. quadrants 1 and 3.

        It uses the methodology developed by (Monzo et al., 2016) [#Monzo]_ and adapted by (Peere et al., 2021) [#PeereBS]_.
        The concept of borefield quadrants is developed by (Peere et al., 2021) [#PeereBS]_, [#PeereThesis]_.

        Returns
        -------
        H : float
            Required borehole depth [m]

        References
        ----------
        .. [#Monzo] Monzo, P., M. Bernier, J. Acuna, and P. Mogensen. (2016). A monthly based bore field sizing methodology with applications to optimum borehole spacing. ASHRAE Transactions 122, 111–126.
        .. [#PeereBS] Peere, W., Picard, D., Cupeiro Figueroa, I., Boydens, W., and Helsen, L. (2021) Validated combined first and last year borefield sizing methodology. In Proceedings of International Building Simulation Conference 2021. Brugge (Belgium), 1-3 September 2021. https://doi.org/10.26868/25222708.2021.30180
        .. [#PeereThesis] Peere, W. (2020) Methode voor economische optimalisatie van geothermische verwarmings- en koelsystemen. Master thesis, Department of Mechanical Engineering, KU Leuven, Belgium.
        """

        # initiate iteration
        H_prev = 0
        time_steps = [self.th, self.th + self.tm, self.tcm + self.th]
        if self.H < 1:
            self.H = 50

        # Iterates as long as there is no convergence
        # (convergence if difference between depth in iterations is smaller than THRESHOLD_BOREHOLE_DEPTH)
        while abs(self.H - H_prev) >= Borefield.THRESHOLD_BOREHOLE_DEPTH:
            # get the g-function values
            gfunc_uniform_T = self.gfunction(time_steps, self.H)

            # calculate the thermal resistances
            Rpm = (gfunc_uniform_T[2] - gfunc_uniform_T[1]) / (2 * pi * self.ground_data.k_s)
            Rcm = (gfunc_uniform_T[1] - gfunc_uniform_T[0]) / (2 * pi * self.ground_data.k_s)
            Rh = (gfunc_uniform_T[0]) / (2 * pi * self.ground_data.k_s)

            # calculate the total length
            L = (self.qh * self._Rb + self.qh * Rh + self.qm * Rcm + self.qpm * Rpm) / abs(self.Tf - self._Tg())

            # updating the depth values
            H_prev = self.H
            self.H = L / self.number_of_boreholes
        return self.H

    def sizing_setup(self, H_init: float = 100, use_constant_Rb: bool = None, use_constant_Tg: bool = None, quadrant_sizing: int = 0,
                     L2_sizing: bool = None, L3_sizing: bool = None, L4_sizing: bool = None, sizing_setup: SizingSetup = None) -> None:
        """
        This function sets the options for the sizing function.

        * The L2 sizing is the one explained in (Peere et al., 2021) [#PeereBS]_ and is the quickest method (it uses 3 pulses)

        * The L3 sizing is a more general approach which is slower but more accurate (it uses 24 pulses/year)

        * The L4 sizing is the most exact one, since it uses hourly data (8760 pulses/year)

        Parameters
        ----------
        H_init : float
            Initial depth of the borefield to start the iteration (m)
        use_constant_Rb : bool
            True if a constant borehole equivalent resistance (Rb*) value should be used
        use_constant_Tg : bool
            True if a constant Tg value should be used (the geothermal flux is neglected)
        quadrant_sizing : int
            Differs from 0 when a sizing in a certain quadrant is desired.
            Quadrants are developed by (Peere et al., 2021) [#PeereBS]_, [#PeereThesis]_
        L2_sizing : bool
            True if a sizing with the L2 method is needed
        L3_sizing : bool
            True if a sizing with the L3 method is needed
        L4_sizing : bool
            True if a sizing with the L4 method is needed
        sizing_setup : SizingSetup
            An instance of the SizingSetup class. When this argument differs from None, all the other parameters are
            set based on this sizing_setup

        Returns
        -------
        None

        References
        ----------
        .. [#PeereBS] Peere, W., Picard, D., Cupeiro Figueroa, I., Boydens, W., and Helsen, L. (2021) Validated combined first and last year borefield sizing methodology. In Proceedings of International Building Simulation Conference 2021. Brugge (Belgium), 1-3 September 2021. https://doi.org/10.26868/25222708.2021.30180
        .. [#PeereThesis] Peere, W. (2020) Methode voor economische optimalisatie van geothermische verwarmings- en koelsystemen. Master thesis, Department of Mechanical Engineering, KU Leuven, Belgium.
        """
        self.H_init = H_init

        # if sizing_setup is not None, than the sizing setup is set directly
        if sizing_setup is not None:
            self._sizing_setup = sizing_setup
            return

        self._sizing_setup = SizingSetup(use_constant_Rb=use_constant_Rb,
                                         use_constant_Tg=use_constant_Tg,
                                         quadrant_sizing=quadrant_sizing,
                                         L2_sizing=L2_sizing,
                                         L3_sizing=L3_sizing,
                                         L4_sizing=L4_sizing)

    def size(self, H_init: float = 100, use_constant_Rb: bool = None, use_constant_Tg: bool = None,
             L2_sizing: bool = None, L3_sizing: bool = None, L4_sizing: bool = None, quadrant_sizing: int = None) -> float:
        """
        This function sets the options for the sizing function.

        * The L2 sizing is the one explained in (Peere et al., 2021) [#PeereBS]_ and is the quickest method (it uses 3 pulses)

        * The L3 sizing is a more general approach which is slower but more accurate (it uses 24 pulses/year)

        * The L4 sizing is the most exact one, since it uses hourly data (8760 pulses/year)

        Please note that the changes sizing setup changes here are not saved! Use self.setupSizing for this.
        (e.g. if you size by putting the constantTg param to True but it was False, if you plot the results afterwards
        the constantTg will be False again and your results will seem off!)

        Parameters
        ----------
        H_init : float
            Initial depth of the borefield to start the iteration (m)
        use_constant_Rb : bool
            True if a constant borehole equivalent resistance (Rb*) value should be used
        use_constant_Tg : bool
            True if a constant Tg value should be used (the geothermal flux is neglected)
        quadrant_sizing : int
            Differs from 0 when a sizing in a certain quadrant is desired.
            Quadrants are developed by (Peere et al., 2021) [#PeereBS]_, [#PeereThesis]_
        L2_sizing : bool
            True if a sizing with the L2 method is needed
        L3_sizing : bool
            True if a sizing with the L3 method is needed
        L4_sizing : bool
            True if a sizing with the L4 method is needed

        Returns
        -------
        None

        Raises
        ------
        ValueError
            ValueError when no ground data is provided
        """

        # check ground data
        if not self.ground_data.check_values():
            raise ValueError("Please provide ground data.")

        # make backup of initial parameter states
        self._sizing_setup.make_backup()

        # run the sizing setup
        self._sizing_setup.update_variables(use_constant_Rb=use_constant_Rb, use_constant_Tg=use_constant_Tg,
                                            L2_sizing=L2_sizing, L3_sizing=L3_sizing, L4_sizing=L4_sizing,
                                            quadrant_sizing=quadrant_sizing)

        # sizes according to the correct algorithm
        if self._sizing_setup.L2_sizing:
            depth = self.size_L2(self.H_init, self._sizing_setup.quadrant_sizing)
        if self._sizing_setup.L3_sizing:
            depth = self.size_L3(self.H_init, self._sizing_setup.quadrant_sizing)
        if self._sizing_setup.L4_sizing:
            depth = self.size_L4(self.H_init, self._sizing_setup.quadrant_sizing)

        # reset initial parameters
        self._sizing_setup.restore_backup()

        # check if the field is not shallow
        if depth < self.THRESHOLD_WARNING_SHALLOW_FIELD and self.printing:
            print(f"The field has a calculated depth of {round(depth, 2)} m which is lower than the proposed minimum "
                  f"of {self.THRESHOLD_WARNING_SHALLOW_FIELD} m.")
            print("Please change your configuration accordingly to have a not so shallow field.")

        return depth

    def size_L2(self, H_init: float, quadrant_sizing: int = 0) -> float:
        """
        This function sizes the  of the given configuration according to the methodology explained in
        (Peere et al., 2021) [#PeereBS]_, which is a L2 method. When quadrant sizing is other than 0, it sizes the field based on
        the asked quadrant. It returns the borefield depth.

        Parameters
        ----------
        H_init : float
            Initial depth from where to start the iteration [m]
        quadrant_sizing : int
            If a quadrant is given the sizing is performed for this quadrant else for the relevant

        Returns
        -------
        H : float
            Required depth of the borefield [m]
        """

        # initiate with a given depth
        self.H_init: float = H_init

        def size_quadrant1():
            self._calculate_first_year_params(False)  # calculate parameters
            return self._Carcel  # size

        def size_quadrant2():
            self._calculate_last_year_params(False)  # calculate parameters
            self.qa = self.qa
            return self._Ahmadfard  # size

        def size_quadrant3():
            self._calculate_first_year_params(True)  # calculate parameters
            return self._Carcel  # size

        def size_quadrant4():
            self._calculate_last_year_params(True)  # calculate parameters
            self.qa = self.qa
            return self._Ahmadfard  # size

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
        else:
            # size according to the biggest quadrant
            # determine which quadrants are relevant
            if self.imbalance <= 0:
                # extraction dominated, so quadrants 1 and 4 are relevant
                quadrant1 = size_quadrant1()
                quadrant4 = size_quadrant4()
                self.H = max(quadrant1, quadrant4)

                if self.H == quadrant1:
                    self.limiting_quadrant = 1
                else:
                    self.limiting_quadrant = 4
            else:
                # injection dominated, so quadrants 2 and 3 are relevant
                quadrant2 = size_quadrant2()
                quadrant3 = size_quadrant3()
                self.H = max(quadrant2, quadrant3)

                if self.H == quadrant2:
                    self.limiting_quadrant = 2
                else:
                    self.limiting_quadrant = 3

        return self.H

    def size_L3(self, H_init: float, quadrant_sizing: int = 0) -> float:
        """
        This function sizes the borefield based on a monthly (L3) method.

        Parameters
        ----------
        H_init : float
            Initial depth from where to start the iteration [m]
        quadrant_sizing : int
            If a quadrant is given the sizing is performed for this quadrant else for the relevant

        Returns
        -------
        H : float
            Required depth of the borefield [m]
        """
        # initiate with a given depth
        self.H_init: float = H_init

        if quadrant_sizing != 0:
            # size according to a specific quadrant
            self.H = self._size_based_on_temperature_profile(quadrant_sizing)
        else:
            # size according to the biggest quadrant
            # determine which quadrants are relevant
            if self.imbalance <= 0:
                # extraction dominated, so quadrants 1 and 4 are relevant
                quadrant1 = self._size_based_on_temperature_profile(1)
                quadrant4 = self._size_based_on_temperature_profile(4)
                self.H = max(quadrant1, quadrant4)

                if self.H == quadrant1:
                    self.limiting_quadrant = 1
                    # the last calculated temperature was for quadrant 4, which was the smaller one
                    self.recalculation_needed = True
                else:
                    self.limiting_quadrant = 4
                    self.recalculation_needed = False
            else:
                # injection dominated, so quadrants 2 and 3 are relevant
                quadrant2 = self._size_based_on_temperature_profile(2)
                quadrant3 = self._size_based_on_temperature_profile(3)
                self.H = max(quadrant2, quadrant3)

                if self.H == quadrant2:
                    self.limiting_quadrant = 2
                    # the last calculation was for quadrant 3, which is the smaller one
                    self.recalculation_needed = True
                else:
                    self.limiting_quadrant = 3
                    self.recalculation_needed = False

        return self.H

    def size_L4(self, H_init: float, quadrant_sizing: int = 0) -> float:
        """
        This function sizes the borefield based on an hourly (L4) sizing methodology.

        Parameters
        ----------
        H_init : float
            Initial depth from where to start the iteration [m]
        quadrant_sizing : int
            If a quadrant is given the sizing is performed for this quadrant else for the relevant

        Returns
        -------
        H : float
            Required depth of the borefield [m]
        """
        # check if hourly data is given
        if not self._check_hourly_load():
            raise ValueError("The hourly data is incorrect.")

        # initiate with a given depth
        self.H_init: float = H_init

        if quadrant_sizing != 0:
            # size according to a specific quadrant
            self.H = self._size_based_on_temperature_profile(quadrant_sizing, hourly=True)
        else:
            # size according to the biggest quadrant
            # determine which quadrants are relevant
            if self.imbalance <= 0:
                # extraction dominated, so quadrants 1 and 4 are relevant
                quadrant1 = self._size_based_on_temperature_profile(1, hourly=True)
                quadrant4 = self._size_based_on_temperature_profile(4, hourly=True)
                self.H = max(quadrant1, quadrant4)

                if self.H == quadrant1:
                    self.limiting_quadrant = 1
                    # the last calculation was for quadrant 4, which is the smaller one
                    self.recalculation_needed = True
                else:
                    self.limiting_quadrant = 4
                    self.recalculation_needed = False
            else:
                # injection dominated, so quadrants 2 and 3 are relevant
                quadrant2 = self._size_based_on_temperature_profile(2, hourly=True)
                quadrant3 = self._size_based_on_temperature_profile(3, hourly=True)
                self.H = max(quadrant2, quadrant3)

                if self.H == quadrant2:
                    self.limiting_quadrant = 2
                    # the last calculation was for quadrant 3, which is the smaller one
                    self.recalculation_needed = True
                else:
                    self.limiting_quadrant = 3
                    self.recalculation_needed = False

        return self.H

    def _size_based_on_temperature_profile(self, quadrant: int, hourly: bool = False) -> float:
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

        Returns
        -------
        Depth : float
            Required depth of the borefield [m]
        """
        # initiate iteration
        H_prev = 0

        if self.H < 1:
            self.H = 50

        # define loads for sizing
        # it only calculates the first and the last year, so the sizing is less computationally expensive
        loads_short = self.hourly_cooling_load - self.hourly_heating_load if hourly else self.monthly_load
        loads_short_rev = loads_short[::-1]
        loads_long = np.tile(loads_short, 2)

        # initialise the results array
        results = np.zeros(loads_short.size * 2)

        # Iterates as long as there is no convergence
        # (convergence if difference between depth in iterations is smaller than THRESHOLD_BOREHOLE_DEPTH)
        while abs(self.H - H_prev) >= Borefield.THRESHOLD_BOREHOLE_DEPTH:

            if hourly:
                # calculate g-values
                g_values = self.gfunction(self.time_L4, self.H)

                # calculation of needed differences of the g-function values. These are the weight factors
                # in the calculation of Tb.
                g_value_differences = np.diff(g_values, prepend=0)

                # convolution to get the monthly results
                results[:8760] = convolve(loads_short * 1000, g_value_differences[:8760])[:8760]

                g_sum_n1 = g_value_differences[:8760 * (self.simulation_period - 1)].reshape(self.simulation_period - 1,
                                                                                             8760).sum(axis=0)
                g_sum = g_sum_n1 + g_value_differences[8760 * (self.simulation_period - 1):]
                g_sum_n2 = np.concatenate((np.array([0]), g_sum_n1[::-1]))[:-1]

                results[8760:] = convolve(loads_short * 1000, g_sum)[:8760] + convolve(loads_short_rev * 1000,
                                                                                       g_sum_n2)[:8760][::-1]

                # calculation the borehole wall temperature for every month i
                Tb = results / (2 * pi * self.ground_data.k_s) / (self.H * self.number_of_boreholes) + self._Tg(self.H)

                self.Tb = Tb
                # now the Tf will be calculated based on
                # Tf = Tb + Q * R_b
                temperature_result = Tb + loads_long * 1000 * (self.Rb / self.number_of_boreholes / self.H)
                # reset other variables
                self.results_peak_heating = temperature_result
                self.results_peak_cooling = temperature_result

            else:
                # calculate g-values
                g_values = self.gfunction(self.time_L3_last_year, self.H)

                # the g-function value of the peak with length_peak hours
                g_value_peak_heating = self.gfunction(self.length_peak_heating * 3600., self.H)[0]
                g_value_peak_cooling = self.gfunction(self.length_peak_cooling * 3600., self.H)[0]

                # calculation of needed differences of the g-function values. These are the weight factors in
                # the calculation of Tb.
                g_value_differences = np.diff(g_values, prepend=0)

                # convolution to get the monthly results
                results[:12] = convolve(loads_short * 1000, g_value_differences[:12])[:12]

                g_sum_n1 = g_value_differences[:12 * (self.simulation_period - 1)]\
                    .reshape(self.simulation_period - 1, 12).sum(axis=0)
                g_sum = g_sum_n1 + g_value_differences[12 * (self.simulation_period - 1):]
                g_sum_n2 = np.concatenate((np.array([0]), g_sum_n1[::-1]))[:-1]

                results[12:] = convolve(loads_short * 1000, g_sum)[:12]\
                               + convolve(loads_short_rev * 1000, g_sum_n2)[:12][::-1]

                # calculation the borehole wall temperature for every month i
                Tb = results / (2 * pi * self.ground_data.k_s) / (self.H * self.number_of_boreholes) + self._Tg(self.H)

                self.Tb = Tb
                # now the Tf will be calculated based on
                # Tf = Tb + Q * R_b
                results_month_cooling = Tb + np.tile(self.monthly_load_cooling, 2) * 1000 \
                                        * (self.Rb / self.number_of_boreholes / self.H)
                results_month_heating = Tb - np.tile(self.monthly_load_heating, 2) * 1000 \
                                        * (self.Rb / self.number_of_boreholes / self.H)

                # extra summation if the g-function value for the peak is included
                results_peak_cooling = results_month_cooling +\
                                       np.tile(self.peak_cooling - self.monthly_load_cooling, 2) * 1000 *\
                                       (g_value_peak_cooling / self.ground_data.k_s / 2 / pi + self.Rb) / self.number_of_boreholes / self.H
                results_peak_heating = results_month_heating - np.tile(self.peak_heating - self.monthly_load_heating, 2) * 1000 \
                                       * (g_value_peak_heating / self.ground_data.k_s / 2 / pi + self.Rb)\
                                       / self.number_of_boreholes / self.H

                # save temperatures under variable
                self.results_peak_heating = results_peak_heating
                self.results_peak_cooling = results_peak_cooling

            H_prev = self.H

            if quadrant == 1 or quadrant == 2:
                # maximum temperature
                # convert back to required length
                self.H = (np.max(self.results_peak_cooling) - self._Tg()) / (self.Tf_max - self._Tg()) * H_prev
            else:
                # minimum temperature
                # convert back to required length
                self.H = (np.min(self.results_peak_heating) - self._Tg()) / (self.Tf_min - self._Tg()) * H_prev

        return self.H

    def calculate_monthly_load(self) -> None:
        """
        This function calculates the average monthly load in kW.

        Returns
        -------
        None
        """
        self.monthly_load = (self.baseload_cooling - self.baseload_heating) / Borefield.UPM

    def set_baseload_heating(self, baseload: Union[np.ndarray, list]) -> None:
        """
        This function defines the baseload in heating both in an energy as in an average power perspective.

        Parameters
        ----------
        baseload : np.ndarray, list
            Baseload heating per month [kWh]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            ValueError when the baseload is no list or np.ndarray
        """
        if (isinstance(baseload, list) or isinstance(baseload, np.ndarray)) and len(baseload) != 12:
            raise ValueError("No correct list/array is given!")
        if isinstance(baseload, float) or isinstance(baseload, int):
            raise ValueError("No correct list/array is given!")
        self.baseload_heating = np.maximum(baseload, np.zeros(12))  # kWh
        self.monthly_load_heating = self.baseload_heating / Borefield.UPM  # kW
        self.calculate_monthly_load()
        self.calculate_imbalance()

        # new peak heating if baseload is larger than the peak
        self.set_peak_heating(np.maximum(self.peak_heating, self.monthly_load_heating))

    def set_baseload_cooling(self, baseload: Union[np.array, list]) -> None:
        """
        This function defines the baseload in cooling both in an energy as in an average power perspective.

        Parameters
        ----------
        baseload : np.ndarray, list
            Baseload cooling per month [kWh]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            ValueError when the baseload is no list or np.ndarray
        """
        if (isinstance(baseload, list) or isinstance(baseload, np.ndarray)) and len(baseload) != 12:
            raise ValueError("No correct list/array is given!")
        if isinstance(baseload, float) or isinstance(baseload, int):
            raise ValueError("No correct list/array is given!")
        self.baseload_cooling = np.maximum(baseload, np.zeros(12))  # kWh
        self.monthly_load_cooling = self.baseload_cooling / Borefield.UPM  # kW
        self.calculate_monthly_load()
        self.calculate_imbalance()

        # new peak cooling if baseload is larger than the peak
        self.set_peak_cooling(np.maximum(self.peak_cooling, self.monthly_load_cooling))

    def set_peak_heating(self, peak_load: Union[np.ndarray, list]) -> None:
        """
        This function sets the peak heating to peak load heating.

        Parameters
        ----------
        peak_load : np.ndarray, list
            Peak load of heating per month [kW]

        Returns
        -------
        None
        Raises
        ------
        ValueError
            ValueError when the peak_load is no list or np.ndarray
        """
        if (isinstance(peak_load, list) or isinstance(peak_load, np.ndarray)) and len(peak_load) != 12:
            raise ValueError("No correct list/array is given!")
        if isinstance(peak_load, float) or isinstance(peak_load, int):
            raise ValueError("No correct list/array is given!")
        self.peak_heating = np.maximum(peak_load, self.monthly_load_heating)

    def set_peak_cooling(self, peak_load: Union[np.ndarray, list]) -> None:
        """
        This function sets the peak cooling to peak load cooling.

        Parameters
        ----------
        peak_load : np.ndarray, list
            Peak load of cooling per month [kW]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            ValueError when the peak_load is no list or np.ndarray
        """
        if (isinstance(peak_load, list) or isinstance(peak_load, np.ndarray)) and len(peak_load) != 12:
            raise ValueError("No correct list/array is given!")
        if isinstance(peak_load, float) or isinstance(peak_load, int):
            raise ValueError("No correct list/array is given!")
        self.peak_cooling = np.maximum(peak_load, self.monthly_load_cooling)

    @property
    def investment_cost(self) -> float:
        """
        This function calculates the investment cost based on a cost profile linear to the total borehole length.

        Returns
        -------
        float
            Investement cost
        """
        return np.polyval(self.cost_investment, self.H * self.number_of_boreholes)

    def calculate_imbalance(self) -> None:
        """
        This function calculates the imbalance of the field.
        A positive imbalance means that the field is injection dominated, i.e. it heats up every year.

        Returns
        -------
        None
        """
        self.imbalance = np.sum(self.baseload_cooling) - np.sum(self.baseload_heating)

    def _calculate_last_year_params(self, HC: bool) -> None:
        """
        This function calculates the parameters for the sizing based on the last year of operation.
        This is needed for the L2 sizing.

        Parameters
        ----------
        HC : bool
            True if the borefield is limited by extraction load

        Returns
        -------
        None
        """

        # convert imbalance to Watt
        self.qa = self.imbalance / 8760. * 1000

        if HC:
            # limited by extraction load

            # set length peak
            self.th = 3600. * self.length_peak_heating

            # temperature limit is set to the minimum temperature
            self.Tf = self.Tf_min

            # Select month with the highest peak load and take both the peak and average load from that month
            month_index = np.where(self.peak_heating == np.max(self.peak_heating))[0][0]
            self.qm = self.monthly_load[month_index] * 1000.
            self.qh = np.max(self.peak_heating) * 1000.

            # correct signs
            self.qm = -self.qm
            self.qa = -self.qa

        else:
            # limited by injection load

            # set length peak
            self.th = 3600. * self.length_peak_cooling

            # temperature limit set to maximum temperature
            self.Tf = self.Tf_max

            # Select month with the highest peak load and take both the peak and average load from that month
            month_index = np.where(self.peak_cooling == np.max(self.peak_cooling))[0][0]
            self.qm = self.monthly_load[month_index] * 1000.
            self.qh = np.max(self.peak_cooling) * 1000.

    def _calculate_first_year_params(self, HC: bool, month_index: int = None) -> int:
        """
        This function calculates the parameters for the sizing based on the first year of operation.
        This is needed for the L2 sizing.

        Parameters
        ----------
        HC : bool
            True if the borefield is limited by extraction load
        month_index : int
            Month index with the highest peak load (jan = 0, feb = 1 ...)

        Returns
        -------
        month_index : int
            Month with the highest peak load (jan = 0, feb = 1 ...)
        """

        if HC:
            # limited by extraction load

            # set peak length
            self.th = 3600. * self.length_peak_heating

            # temperature limit is set to the minimum temperature
            self.Tf = self.Tf_min

            # Select month with the highest peak load and take both the peak and average load from that month
            month_index = np.where(self.peak_heating == np.max(self.peak_heating))[0][0] if month_index is None else month_index
            self.qh = np.max(self.peak_heating) * 1000.

            self.qm = self.monthly_load[month_index] * 1000.

            if month_index < 1:
                self.qpm = 0
            else:
                self.qpm = np.sum(self.monthly_load[:month_index]) * 1000 / (month_index + 1)

            self.qm = -self.qm
        else:
            # limited by injection

            # set peak length
            self.th = 3600. * self.length_peak_cooling

            # temperature limit set to maximum temperature
            self.Tf = self.Tf_max

            # Select month with the highest peak load and take both the peak and average load from that month
            month_index = np.where(self.peak_cooling == np.max(self.peak_cooling))[0][0] if month_index is None else month_index
            self.qh = np.max(self.peak_cooling) * 1000.

            self.qm = self.monthly_load[month_index] * 1000.
            if month_index < 1:
                self.qpm = 0
            else:
                self.qpm = np.sum(self.monthly_load[:month_index]) * 1000 / (month_index + 1)

        self.tcm = (month_index + 1) * Borefield.UPM * 3600
        self.tpm = month_index * Borefield.UPM * 3600

        return month_index

    def calculate_temperatures(self, depth: float = None, hourly: bool = False) -> None:
        """
        Calculate all the temperatures without plotting the figure. When depth is given, it calculates it for a given
        depth.

        Parameters
        ----------
        depth : float
            Depth for which the temperature profile should be calculated for [m]
        hourly : bool
            True when the temperatures should be calculated based on hourly data
        Returns
        -------
        None
        """
        self._calculate_temperature_profile(H=depth, hourly=hourly)

    def print_temperature_profile(self, legend: bool = True, plot_hourly: bool = False, recalculate: bool = False) -> None:
        """
        This function plots the temperature profile for the calculated depth.
        It uses the available temperature profile data.

        Parameters
        ----------
        legend : bool
            True if the legend should be printed
        plot_hourly : bool
            True if the temperature profile printed should be based on the hourly load profile.
        recalculate : bool
            True if the temperature profile should be calculated, regardless of this temperature profile
            is already calculated.

        Returns
        -------
        fig, ax
            If the borefield object is part of the GUI, it returns the figure object
        """
        # check if the data should be recalculated or no correct temperature profile is available
        if recalculate or not self._check_temperature_profile_available(plot_hourly):
            self._calculate_temperature_profile(hourly=plot_hourly)

        return self._plot_temperature_profile(legend=legend, plot_hourly=plot_hourly)

    def print_temperature_profile_fixed_depth(self, depth: float, legend: bool = True, plot_hourly: bool = False,
                                              recalculate: bool = False):
        """
        This function plots the temperature profile for a fixed depth.
        It uses the already calculated temperature profile data, if available.

        Parameters
        ----------
        depth : float
            Depth at which the temperature profile should be shown
        legend : bool
            True if the legend should be printed
        plot_hourly : bool
            True if the temperature profile printed should be based on the hourly load profile.
        recalculate : bool
            True if the temperature profile should be calculated, regardless of this temperature profile
            is already calculated.
        Returns
        -------
        fig, ax
            If the borefield object is part of the GUI, it returns the figure object
        """
        # check if the data should be recalculated or no correct temperature profile is available
        # or the depth is different from the one already calculated
        if recalculate or not self._check_temperature_profile_available(plot_hourly) or self.H != depth:
            self._calculate_temperature_profile(H=depth, hourly=plot_hourly)

        return self._plot_temperature_profile(legend=legend, plot_hourly=plot_hourly)

    def _check_temperature_profile_available(self, hourly: bool = True) -> bool:
        """
        This function checks whether or not the temperature profile is already calculated.

        Parameters
        ----------
        hourly : bool
            True if an hourly profile is wanted.

        Returns
        -------
        bool
            True if the needed temperatures are available
        """
        
        if self.recalculation_needed:
            self.recalculation_needed = False
            return False

        if hourly and np.array_equal(self.results_peak_heating, self.results_peak_cooling)\
                and self.results_peak_cooling.any() and len(self.results_peak_cooling) == len(self.Tb)\
                and self.results_peak_cooling.size == 8760 * self.simulation_period:
            # this equals whenever an hourly calculation has been preformed
            return True

        if self.results_month_heating.any() and self.results_month_heating.size == self.simulation_period * 12\
                and not hourly:
            return True

        return False

    def _plot_temperature_profile(self, legend: bool = True, plot_hourly: bool = False) -> Tuple[plt.Figure, plt.Axes]:
        """
        This function plots the temperature profile.
        If the Borefield object exists as part of the GUI, than the figure is returned,
        otherwise it is shown.

        Parameters
        ----------
        legend : bool
            True if the legend should be printed
        plot_hourly : bool
            True if the temperature profile printed should be based on the hourly load profile.

        Returns
        -------
        fig, ax
            If the borefield object is part of the GUI, it returns the figure object
        """

        # make a time array
        if plot_hourly:
            time_array = self.time_L4 / 12 / 3600 / 730
        else:
            time_array = self.time_L3_last_year / 12 / 730. / 3600.

        plt.rc('figure')
        # create new figure and axes if it not already exits otherwise clear it.
        fig = plt.figure()
        ax = fig.add_subplot(111)
        # set axes labels
        ax.set_xlabel(r'Time (year)')
        ax.set_ylabel(r'Temperature ($^\circ C$)')

        # plot Temperatures
        ax.step(time_array, self.Tb, 'k-', where="pre", lw=1.5, label="Tb")

        if plot_hourly:
            ax.step(time_array, self.results_peak_cooling, 'b-', where="pre", lw=1, label='Tf')
        else:
            ax.step(time_array, self.results_peak_cooling, 'b-', where="pre", lw=1.5, label='Tf peak cooling')
            ax.step(time_array, self.results_peak_heating, 'r-', where="pre", lw=1.5, label='Tf peak heating')

            ax.step(time_array, self.results_month_cooling, color='b', linestyle="dashed", where="pre", lw=1.5, label='Tf base cooling')
            ax.step(time_array, self.results_month_heating, color='r', linestyle="dashed", where="pre", lw=1.5, label='Tf base heating')

        # define temperature bounds
        ax.hlines(self.Tf_min, 0, self.simulation_period, colors='r', linestyles='dashed', label='', lw=1)
        ax.hlines(self.Tf_max, 0, self.simulation_period, colors='b', linestyles='dashed', label='', lw=1)
        ax.set_xticks(range(0, self.simulation_period + 1, 2))

        # Plot legend
        if legend:
            ax.legend()
        ax.set_xlim(left=0, right=self.simulation_period)
        # show figure if not in gui mode
        if not self.gui:
            plt.show()
        return fig, ax

    def _calculate_temperature_profile(self, H: float = None, hourly: bool = False) -> None:
        """
        This function calculates the evolution in the fluid temperature and borehole wall temperature.

        Parameters
        ----------
        H : float
            Depth at which the temperatures should be evaluated [m]. If None, than the current depth is taken.
        hourly : bool
            True if the temperature evolution should be calculated on an hourly basis.

        Returns
        -------
        None
        """

        H_backup = self.H
        if H is not None:
            self.H = H
        # set Rb* value
        self.Rb = self._Rb

        self.H = H_backup

        H = self.H if H is None else H

        if not hourly:
            # making a numpy array of the monthly balance (self.monthly_load) for a period of self.simulation_period years
            # [kW]
            monthly_loads_array = np.tile(self.monthly_load, self.simulation_period)

            # self.g-function is a function that uses the precalculated data to interpolate the correct values of the
            # g-function. This dataset is checked over and over again and is correct
            g_values = self.gfunction(self.time_L3_last_year, H)

            # the g-function value of the peak with length_peak hours
            g_value_peak_cooling = self.gfunction(self.length_peak_cooling * 3600., H)[0]
            g_value_peak_heating = self.gfunction(self.length_peak_heating * 3600., H)[0]

            # calculation of needed differences of the g-function values. These are the weight factors in the calculation
            # of Tb.
            g_value_differences = np.diff(g_values, prepend=0)

            # convolution to get the monthly results
            results = convolve(monthly_loads_array * 1000, g_value_differences)[:len(monthly_loads_array)]

            # calculation the borehole wall temperature for every month i
            Tb = results / (2 * pi * self.ground_data.k_s) / (H * self.number_of_boreholes) + self._Tg(H)

            self.Tb = Tb
            # now the Tf will be calculated based on
            # Tf = Tb + Q * R_b
            results_month_cooling = Tb + np.tile(self.monthly_load_cooling, self.simulation_period) * 1000 \
                              * (self.Rb / self.number_of_boreholes / H)
            results_month_heating = Tb - np.tile(self.monthly_load_heating, self.simulation_period) * 1000 \
                              * (self.Rb / self.number_of_boreholes / H)

            # extra summation if the g-function value for the peak is included
            results_peak_cooling = results_month_cooling + np.tile(self.peak_cooling - self.monthly_load_cooling, self.simulation_period) * 1000 \
                                     * (g_value_peak_cooling / self.ground_data.k_s / 2 / pi + self.Rb) / self.number_of_boreholes / H
            results_peak_heating = results_month_heating - np.tile(self.peak_heating - self.monthly_load_heating, self.simulation_period) * 1000 \
                                   * (g_value_peak_heating / self.ground_data.k_s / 2 / pi + self.Rb) / self.number_of_boreholes / H

            # save temperatures under variable
            self.results_peak_heating = results_peak_heating
            self.results_peak_cooling = results_peak_cooling
            self.results_month_cooling = results_month_cooling
            self.results_month_heating = results_month_heating

        if hourly:

            # check for hourly data if this is requested
            self._check_hourly_load()

            # making a numpy array of the monthly balance (self.monthly_load) for a period of self.simulation_period years
            # [kW]
            if np.any(self.hourly_heating_load_on_the_borefield):
                hourly_load = np.tile(self.hourly_cooling_load_on_the_borefield - self.hourly_heating_load_on_the_borefield,
                                      self.simulation_period)
            else:
                hourly_load = np.tile(self.hourly_cooling_load - self.hourly_heating_load, self.simulation_period)

            # self.g-function is a function that uses the precalculated data to interpolate the correct values of the
            # g-function. This dataset is checked over and over again and is correct
            g_values = self.gfunction(self.time_L4, H)

            # calculation of needed differences of the g-function values. These are the weight factors in the calculation
            # of Tb.
            g_value_differences = np.diff(g_values, prepend=0)

            # convolution to get the monthly results
            results = convolve(hourly_load * 1000, g_value_differences)[:len(hourly_load)]

            # calculation the borehole wall temperature for every month i
            Tb = results / (2 * pi * self.ground_data.k_s) / (H * self.number_of_boreholes) + self._Tg(H)

            self.Tb = Tb
            # now the Tf will be calculated based on
            # Tf = Tb + Q * R_b
            temperature_result = Tb + hourly_load * 1000 * (self.Rb / self.number_of_boreholes / H)

            # reset other variables
            self.results_peak_heating = temperature_result
            self.results_peak_cooling = temperature_result
            self.results_month_cooling = np.array([])
            self.results_month_heating = np.array([])

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
        self.options_pygfunction = options

    def gfunction(self, time_value: Union[list, float, np.ndarray], H: float = None) -> np.ndarray:
        """
        This function returns the gfunction value.
        It can do so by either calculating the gfunctions just-in-time or by interpolating from a
        loaded custom data file.

        Parameters
        ----------
        time_value : list, float, np.ndarray
            Time value(s) in seconds at which the gfunctions should be calculated
        H : float
            Depth [m] at which the gfunctions should be calculated.
            If no depth is given, the current depth is taken.

        Returns
        -------
        gvalue : np.ndarray
            1D array with the g-values for all the requested time_value(s)
        """
        # when using a variable ground temperature, sometimes no solution can be found
        if not self._sizing_setup.use_constant_Tg and H > Borefield.THRESHOLD_DEPTH_ERROR:
            raise ValueError("Due to the use of a variable ground temperature, no solution can be found."
                             "To see the temperature profile, one can plot it using the depth of ",
                             str(Borefield.THRESHOLD_DEPTH_ERROR), "m.")

        def jit_gfunction_calculation() -> np.ndarray:
            """
            This function calculates the gfunction just-in-time.

            Returns
            -------
            gvalues : np.ndarray
                1D array with the g-values for the requested time intervals
            """
            # set the correct depth of the borefield
            self._update_borefield_depth(H=H)

            return self.gfunction_calculation_object.calculate(time_value, self.borefield, self.ground_data.alpha)

        ## 1 bypass any possible precalculated g-functions

        # if calculate is False, than the gfunctions are calculated jit
        if not self.use_precalculated_data:
            return jit_gfunction_calculation()

        ## 2 use precalculated g-functions when available
        if not self.custom_gfunction is None:
            # there is precalculated data available
            # check if the requested values can be calculated using the custom_gfunction
            if self.custom_gfunction.within_range(time_value, H):
                return self.custom_gfunction.calculate_gfunction(time_value, H)

        ## 3 calculate g-function jit
        return jit_gfunction_calculation()

    def create_custom_dataset(self, time_array: Union[list, np.ndarray] = None,
                              depth_array: Union[list, np.ndarray] = None,
                              options: dict = {}) -> None:
        """
        This function makes a datafile for a given custom borefield and sets it for the borefield object.
        It automatically sets this datafile in the current borefield object so it can be used as a source for
        the interpolation of g-values.

        Parameters
        ----------
        time_array : list, np.array
            Time values (in seconds) used for the calculation of the datafile
        depth_array : list, np.array
            List or arrays of depths for which the datafile should be created
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

        try:
            self.borefield[0]
        except TypeError:
            raise ValueError("No borefield is set for which the gfunctions should be calculated")
        try:
            self.ground_data.alpha
        except AttributeError:
            raise ValueError("No ground data is set for which the gfunctions should be calculated")

        self.custom_gfunction = CustomGFunction(time_array, depth_array, options)
        self.custom_gfunction.create_custom_dataset(self.borefield, self.ground_data.alpha)

    def set_hourly_heating_load(self, heating_load: np.array) -> None:
        """
        This function sets the hourly heating load in kW.

        Parameters
        ----------
        heating_load : np.array
            Array with hourly heating load values [kW]

        Returns
        -------
        None
        """
        self.hourly_heating_load = np.array(heating_load)

        # set monthly loads
        self.set_peak_heating(self._reduce_to_peak_load(self.hourly_heating_load, np.max(heating_load)))
        self.set_baseload_heating(self._reduce_to_monthly_load(self.hourly_heating_load, np.max(heating_load)))

    def set_hourly_cooling_load(self, cooling_load: np.array) -> None:
        """
        This function sets the hourly cooling load in kW.

        Parameters
        ----------
        cooling_load : np.array
            Array with hourly cooling load values [kW]

        Returns
        -------
        None
        """
        self.hourly_cooling_load = np.array(cooling_load)

        # set monthly loads
        self.set_peak_cooling(self._reduce_to_peak_load(self.hourly_cooling_load, np.max(cooling_load)))
        self.set_baseload_cooling(self._reduce_to_monthly_load(self.hourly_cooling_load, np.max(cooling_load)))

    def _check_hourly_load(self) -> bool:
        """
        This function checks if there is correct hourly data available.

        Returns
        -------
        bool
            True if the data is correct
        """
        # check whether there is data given
        if self.hourly_cooling_load is None or self.hourly_heating_load is None:
            raise ValueError("No data is given for either the heating or cooling load.")

        # check whether the data is hourly
        if len(self.hourly_heating_load) != 8760 or len(self.hourly_cooling_load) != 8760:
            raise ValueError("Incorrect length for either the heating or cooling load")

        # check whether or not there are negative values in the data
        if min(self.hourly_cooling_load) < 0 or min(self.hourly_heating_load) < 0:
            raise ValueError("There are negative values in either the heating or cooling load.")

        return True

    def load_hourly_profile(self, file_path: str, header: bool = True, separator: str = ";",
                            first_column_heating: bool = True) -> None:
        """
        This function loads in an hourly load profile [kW].

        Parameters
        ----------
        file_path : str
            Path to the hourly load file
        header : bool
            True if this file contains a header row
        separator : str
            Symbol used in the file to seperate the columns
        first_column_heating : bool
            True if the first column in the file is for the heating load

        Returns
        -------
        None
        """
        if header:
            header: int = 0
        else:
            header = None
        from pandas import read_csv
        db = read_csv(file_path, sep=separator, header=header)

        if first_column_heating:
            self.set_hourly_heating_load(db.iloc[:, 0].tolist())
            self.set_hourly_cooling_load(db.iloc[:, 1].tolist())
        else:
            self.set_hourly_heating_load(db.iloc[:, 1].tolist())
            self.set_hourly_cooling_load(db.iloc[:, 0].tolist())

    def convert_hourly_to_monthly(self, peak_cooling_load: float = None, peak_heating_load: float = None) -> None:
        """
        This function converts self.hourly_cooling_load and self.hourly_heating_load to the monthly profiles used in the sizing.

        Parameters
        ----------
        peak_cooling_load : float
            peak power in cooling [kW]
        peak_heating_load : float
            peak power in heating [kW]

        Returns
        -------
        None
        """

        try:
            self.hourly_cooling_load[0]
            self.hourly_heating_load[0]
        except IndexError:
            raise IndexError("No hourly loads are loaded yet!")

        if peak_cooling_load is None:
            peak_cooling_load = np.max(self.hourly_cooling_load)
        if peak_heating_load is None:
            peak_heating_load = np.max(self.hourly_heating_load)

        # calculate peak and base loads
        self.set_peak_cooling(self._reduce_to_peak_load(self.hourly_cooling_load, peak_cooling_load))
        self.set_peak_heating(self._reduce_to_peak_load(self.hourly_heating_load, peak_heating_load))
        self.set_baseload_cooling(self._reduce_to_monthly_load(self.hourly_cooling_load, peak_cooling_load))
        self.set_baseload_heating(self._reduce_to_monthly_load(self.hourly_heating_load, peak_heating_load))

    @staticmethod
    def _reduce_to_monthly_load(load: list, peak: float) -> list:
        """
        This function calculates the monthly load based, taking a maximum peak value into account.
        This means that it sums the hourly load for each month, and if a peak occurs larger than the given peak,
        it is limited to the last one.

        Parameters
        ----------
        load : list or numpy.array
            hourly load values [kW]
        peak : float
            maximum peak power [kW]

        Returns
        -------
        monthly baseloads : list
            list with monthly baseloads [kW]
        """
        month_load = [np.sum(np.minimum(peak, load[Borefield.HOURLY_LOAD_ARRAY[i]:Borefield.HOURLY_LOAD_ARRAY[i + 1]])) for i in range(12)]

        return month_load

    @staticmethod
    def _reduce_to_peak_load(load: list, peak: float) -> list:
        """
        This function calculates the monthly peak load, taking a maximum peak value into account.
        This means that for each month, it takes the minimum of either the peak in that month or the given peak.

        Parameters
        ----------
        load : list or numpy.array
            hourly loads [kW]
        peak : float
            maximum peak power [kW]

        Returns
        -------
        peak loads : list
            list with monthly peak loads [kW]
        """

        peak_load = [np.max(np.minimum(peak, load[Borefield.HOURLY_LOAD_ARRAY[i]:Borefield.HOURLY_LOAD_ARRAY[i + 1]])) for i in range(12)]
        return peak_load

    def optimise_load_profile(self, depth: float = None, print_results: bool = False) -> None:
        """
        This function optimises the load based on the given borefield and the given hourly load.
        It does so based on a load-duration curve. The temperatures of the borefield are calculated on a monthly
        basis, even though we have hourly data, for an hourly calculation of the temperatures
        would take a very long time.

        Parameters
        ----------
        depth : float
            Depth of the boreholes in the borefield [m]
        print_results : bool
            True when the results of this optimisation are to be printed in the terminal

        Returns
        -------
        None
        """

        if depth is None:
            depth = self.H

        # since the depth does not change, the Rb* value is constant
        # set to use a constant Rb* value but save the initial parameters
        Rb_backup = self.Rb
        if not self._sizing_setup.use_constant_Rb:
            self.Rb = self.calculate_Rb()
        use_constant_Rb_backup = self._sizing_setup.use_constant_Rb
        self._sizing_setup.use_constant_Rb = True

        # check if hourly profile is given
        self._check_hourly_load()

        # set initial peak loads
        init_peak_heat_load = np.max(self.hourly_heating_load)
        init_peak_cool_load = np.max(self.hourly_cooling_load)

        # peak loads for iteration
        peak_heat_load = init_peak_heat_load
        peak_cool_load = init_peak_cool_load

        # set iteration criteria
        cool_ok, heat_ok = False, False

        while not cool_ok or not heat_ok:
            # calculate peak and base loads
            self.convert_hourly_to_monthly(peak_cool_load, peak_heat_load)

            # calculate temperature profile, just for the results
            self.calculate_temperatures(depth=depth)

            # deviation from minimum temperature
            if abs(min(self.results_peak_heating) - self.Tf_min) > 0.05:

                # check if it goes below the threshold
                if min(self.results_peak_heating) < self.Tf_min:
                    peak_heat_load -= 1 * max(1, 10 * (self.Tf_min - min(self.results_peak_heating)))
                else:
                    peak_heat_load = min(init_peak_heat_load, peak_heat_load + 1)
                    if peak_heat_load == init_peak_heat_load:
                        heat_ok = True
            else:
                heat_ok = True

            # deviation from maximum temperature
            if abs(np.max(self.results_peak_cooling) - self.Tf_max) > 0.05:

                # check if it goes above the threshold
                if np.max(self.results_peak_cooling) > self.Tf_max:
                    peak_cool_load -= 1 * max(1, 10 * (-self.Tf_max + np.max(self.results_peak_cooling)))
                else:
                    peak_cool_load = min(init_peak_cool_load, peak_cool_load + 1)
                    if peak_cool_load == init_peak_cool_load:
                        cool_ok = True
            else:
                cool_ok = True

        # calculate the resulting hourly profile that can be put on the field
        self.hourly_cooling_load_on_the_borefield = np.minimum(peak_cool_load, self.hourly_cooling_load)
        self.hourly_heating_load_on_the_borefield = np.minimum(peak_heat_load, self.hourly_heating_load)

        # calculate the resulting hourly profile that cannot be put on the field
        self.hourly_cooling_load_external = np.maximum(0, self.hourly_cooling_load - peak_cool_load)
        self.hourly_heating_load_external = np.maximum(0, self.hourly_heating_load - peak_heat_load)
        # calculate the resulting monthly profile that cannot be put on the field
        temp = self._reduce_to_monthly_load(self.hourly_cooling_load, np.max(self.hourly_cooling_load))
        self.monthly_load_cooling_external = temp - self.baseload_cooling
        temp = self._reduce_to_monthly_load(self.hourly_heating_load, np.max(self.hourly_heating_load))
        self.monthly_load_heating_external = temp - self.baseload_heating
        temp = self._reduce_to_peak_load(self.hourly_cooling_load, np.max(self.hourly_cooling_load))
        self.peak_cooling_external = temp - self.peak_cooling
        temp = self._reduce_to_peak_load(self.hourly_heating_load, np.max(self.hourly_heating_load))
        self.peak_heating_external = temp - self.peak_heating

        # restore the initial parameters
        self.Rb = Rb_backup
        self._sizing_setup.use_constant_Rb = use_constant_Rb_backup

        if print_results:
            # print results
            print("The peak load heating is: ", int(peak_heat_load), "kW, leading to",
                  np.round(np.sum(self.baseload_heating), 2), "kWh of heating.")
            print("This is", np.round(np.sum(self.baseload_heating) / np.sum(self.hourly_heating_load) * 100, 2),
                  "% of the total heating load.")
            print("Another", np.round(-np.sum(self.baseload_heating) + np.sum(self.hourly_heating_load), 2),
                  "kWh of heating should come from another source, with a peak of",
                  int(max(self.hourly_heating_load)) - int(peak_heat_load), "kW.")
            print("------------------------------------------")
            print("The peak load cooling is: ", int(peak_cool_load), "kW, leading to",
                  np.round(np.sum(self.baseload_cooling), 2), "kWh of cooling.")
            print("This is", np.round(np.sum(self.baseload_cooling) / np.sum(self.hourly_cooling_load) * 100, 2),
                  "% of the total cooling load.")
            print("Another", np.round(-np.sum(self.baseload_cooling) + np.sum(self.hourly_cooling_load), 2),
                  "kWh of cooling should come from another source, with a peak of",
                  int(max(self.hourly_cooling_load)) - int(peak_cool_load), "kW.")

            # plot results
            self.print_temperature_profile_fixed_depth(depth=depth)

    @property
    def _percentage_heating(self) -> float:
        """
        This function returns the percentage of heating load that can be done geothermally.

        Returns
        -------
        float
            Percentage of heating load that can be done geothermally.
        """
        return np.sum(self.baseload_heating) / np.sum(self.hourly_heating_load) * 100

    @property
    def _percentage_cooling(self) -> float:
        """
        This function returns the percentage of cooling load that can be done geothermally.

        Returns
        -------
        float
            Percentage of cooling load that can be done geothermally.
        """
        return np.sum(self.baseload_cooling) / np.sum(self.hourly_cooling_load) * 100

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

        # calculate max/min fluid temperatures
        max_temp = np.max(self.results_peak_cooling)
        min_temp = np.min(self.results_peak_heating)

        # calculate temperature difference w.r.t. the limits
        DT_max = self.Tf_max - max_temp + 1000  # + 1000 to have no problems with negative temperatures
        DT_min = self.Tf_min - min_temp + 1000

        # if the temperature limit is not crossed, return None
        if self.Tf_max - 0.1 > max_temp and self.Tf_min + 0.1 < min_temp:
            return

        # True if heating/extraction dominated
        if self.imbalance < 0:
            # either quadrant 1 or 4
            if DT_min < DT_max:
                # limited by minimum temperature
                return 4
            return 1

        # quadrant 2 or 3
        if DT_min < DT_max:
            # limited by minimum temperature
            return 3
        return 2

    def draw_borehole_internal(self) -> None:
        """
        This function draws the internal structure of a borehole.
        This means, it draws the pipes inside the borehole.

        Returns
        -------
        None
        """

        # calculate the pipe positions
        pos = self.pipe_data._axis_symmetrical_pipe

        # set figure
        figure, axes = plt.subplots()

        # initate circles
        circles_outer = []
        circles_inner = []

        # color inner circles and outer circles
        for i in range(self.pipe_data.number_of_pipes):
            circles_outer.append(plt.Circle(pos[i], self.pipe_data.r_out, color="black"))
            circles_inner.append(plt.Circle(pos[i], self.pipe_data.r_in, color="red"))
            circles_outer.append(plt.Circle(pos[i + self.pipe_data.number_of_pipes], self.pipe_data.r_out, color="black"))
            circles_inner.append(plt.Circle(pos[i + self.pipe_data.number_of_pipes], self.pipe_data.r_in, color="blue"))

        # set visual settings for figure
        axes.set_aspect('equal')
        axes.set_xlim([-self.r_b, self.r_b])
        axes.set_ylim([-self.r_b, self.r_b])
        axes.get_xaxis().set_visible(False)
        axes.get_yaxis().set_visible(False)
        plt.tight_layout()

        # define borehole circle
        borehole_circle = plt.Circle((0, 0), self.r_b, color="white")

        # add borehole circle to canvas
        axes.add_artist(borehole_circle)

        # add other circles to canvas
        for i in circles_outer:
            axes.add_artist(i)
        for i in circles_inner:
            axes.add_artist(i)

        # set background color
        axes.set_facecolor("grey")

        # show plot
        plt.show()

    def plot_load_duration(self, legend: bool = False) -> Tuple[plt.Figure, plt.Axes]:
        """
        This function makes a load-duration curve from the hourly values.

        Parameters
        ----------
        legend : bool
            True if the figure should have a legend

        Returns
        ----------
        Tuple
            plt.Figure, plt.Axes
        """
        # check if there are hourly values
        if not self._check_hourly_load():
            fig = plt.figure()
            return fig, fig.add_subplot(111)
        # sort heating and cooling load
        heating = self.hourly_heating_load.copy()
        heating[::-1].sort()

        cooling = self.hourly_cooling_load.copy()
        cooling.sort()
        cooling = cooling * (-1)
        # create new figure and axes if it not already exits otherwise clear it.
        fig = plt.figure()
        ax = fig.add_subplot(111)
        # add sorted loads to plot
        ax.step(np.arange(0, 8760, 1), heating, 'r-', label="Heating")
        ax.step(np.arange(0, 8760, 1), cooling, 'b-', label="Cooling")
        # create 0 line
        ax.hlines(0, 0, 8759, color="black")
        # add labels
        ax.set_xlabel("Time [hours]")
        ax.set_ylabel("Power [kW]")
        # set x limits to 8760
        ax.set_xlim(0, 8760)
        # plot legend if wanted
        if legend:
            ax.legend()
        # show plt if not in gui
        if not self.gui:
            plt.show()
        return fig, ax
