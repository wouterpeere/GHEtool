import numpy as np
import pickle
from scipy import interpolate
from scipy.signal import convolve
from math import pi
import pygfunction as gt
import os.path
import matplotlib.pyplot as plt
import functools

if __name__ == "__main__":
    from VariableClasses import *
else:
    try:
        from .VariableClasses import *
    except ImportError:
        from VariableClasses import *

FOLDER = os.path.dirname(os.path.realpath(__file__))  # solve problem with importing GHEtool from sub-folders


def timeValues():
    """This function calculates the default time values for the g-function."""
    dt: float = 3600.  # Time step (s)
    t_max: float = 100. * 8760. * 3600.  # Maximum time (s)

    # Load aggregation scheme
    load_agg = gt.load_aggregation.ClaessonJaved(dt, t_max)

    return load_agg.get_times_for_simulation()


class Borefield:
    UPM: float = 730.  # number of hours per month
    THRESHOLD_BOREHOLE_DEPTH: float = 0.05  # threshold for iteration
    MAX_SIMULATION_PERIOD: int = 100  # maximal value for simulation

    # define default values
    DEFAULT_INVESTMENT: list = [35, 0]  # 35 EUR/m
    DEFAULT_LENGTH_PEAK: int = 6  # hours
    DEFAULT_DEPTH_ARRAY: list = [1] + list(range(25, 351, 25))  # m
    DEFAULT_TIME_ARRAY: list = timeValues()  # sec
    DEFAULT_CONVERGENCE_MINIMAL_DEPTH: int = 15

    temp: int = 0
    HOURLY_LOAD_ARRAY: list = []
    for i in [0, 24 * 31, 24 * 28, 24 * 31, 24 * 30, 24 * 31, 24 * 30, 24 * 31, 24 * 31, 24 * 30, 24 * 31, 24 * 30,
              24 * 31]:
        temp += i
        HOURLY_LOAD_ARRAY.append(temp)

    __slots__ = 'baseload_heating', 'baseload_cooling', 'H', 'H_init', 'B', 'N_1', 'N_2', 'Rb', 'k_s', 'Tg', 'ty', 'tm', \
                'td', 'time', 'hourly_heating_load', 'H_max', 'use_constant_Tg', 'flux', 'volumetric_heat_capacity',\
                'hourly_cooling_load', 'number_of_boreholes', 'borefield', 'custom_gfunction', 'cost_investment', \
                'length_peak', 'th', 'Tf_H', 'Tf_C', 'limiting_quadrant', 'monthly_load', 'monthly_load_heating', \
                'monthly_load_cooling', 'peak_heating', 'imbalance', 'qa', 'Tf', 'qm', 'qh', 'qpm', 'tcm', 'tpm', \
                'peak_cooling', 'simulation_period', 'gfunction_interpolation_array', 'fluid_data_available', \
                'results_peak_heating', 'pipe_data_available', 'alpha', 'time_L4', 'temperature_result',\
                'results_peak_cooling', 'results_month_cooling', 'results_month_heating', 'Tb', 'THRESHOLD_WARNING_SHALLOW_FIELD', \
                'gui', 'time_L3_first_year', 'time_L3_last_year', 'peak_heating_external', 'peak_cooling_external', \
                'monthly_load_heating_external', 'monthly_load_cooling_external', 'hourly_heating_load_external', \
                'hourly_cooling_load_external', 'hourly_heating_load_on_the_borefield', 'hourly_cooling_load_on_the_borefield', \
                'k_f', 'mfr', 'Cp', 'mu', 'rho', 'use_constant_Rb', 'h_f', 'R_f', 'R_p', 'printing', 'combo', \
                'r_in', 'r_out', 'k_p', 'D_s', 'r_b', 'number_of_pipes', 'epsilon', 'k_g', 'pos', 'D', \
                'L2_sizing', 'L3_sizing', 'L4_sizing', 'quadrant_sizing', 'H_init', 'use_precalculated_data', 'convergence'

    def __init__(self, simulation_period: int = 20, number_of_boreholes: int = None, peak_heating: list = None,
                 peak_cooling: list = None, baseload_heating: list = None, baseload_cooling: list = None, investement_cost: list = None,
                 borefield=None, custom_gfunction=None, gui: bool = False):
        """This function initiates the Borefield class"""

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
        # parameter that determines whether or not the Rb-value should be altered in the optimisation
        self.use_constant_Rb = True
        # parameter that determines whether or not the Tg should be calculated with a heat flux or without
        self.use_constant_Tg = True

        self.H_max: float = 350  # max threshold for interpolation (will with first sizing)
        # setting this to False will make sure every gvalue is calculated on the spot
        # this will make everything way slower!
        self.use_precalculated_data: bool = True

        # initialize variables for equivalent borehole resistance calculation
        self.pos: list = []
        self.h_f: float = 0.
        self.R_f: float = 0.
        self.R_p: float = 0.

        #
        self.monthly_load = np.array([])
        self.H_init: float = 0.
        self.convergence = 0

        self.gfunction_interpolation_array = np.array([])

        # initialize variables for temperature plotting
        self.results_peak_heating = np.array([])  # list with the minimum temperatures due to the peak heating
        self.results_peak_cooling = np.array([]) # list with the maximum temperatures due to peak cooling
        self.temperature_result = np.array([])  # list with the temperatures with an hourly profile
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
        self.td: float = 0.  # daily time value
        self.th: float = 0.  # duration of peak in seconds
        self.length_peak: float = 0.  # duration of the peak in hours
        self.time = np.array([])  # list of time values
        self.tcm: float = 0.  # time constant for first year sizing
        self.tpm: float = 0.  # time constant for first year sizing
        self.time_L3_first_year = np.array([])  # list with time values for L3 sizing
        self.time_L3_last_year = np.array([]) # list with time values for L3 sizing
        self.time_L4 = np.array([]) # list with all the time values for the L4 sizing

        # initiate ground loads
        self.qa: float = 0.  # yearly load W
        self.qm: float = 0.  # monthly load W
        self.qh: float = 0.  # peak load W
        self.qpm: float = 0.  # cumulative load first year sizing
        self.imbalance: float = 0.  # imbalance kWh

        # initiate ground parameters
        self.H = 0.  # borehole depth m
        self.B = 0.  # borehole spacing m
        self.k_s = 0.  # ground thermal conductivity W/mK
        self.Tg = 0.  # ground temperature at infinity °C
        self.Rb = 0.  # effective borehole thermal resistance mK/W
        self.N_1 = 0  # number of boreholes in one direction #
        self.N_2 = 0  # number of boreholes in the other direction #
        self.flux = 0.  # geothermal heat flux W/m2
        self.volumetric_heat_capacity = 0.  # ground volumetric heat capacity (J/m3K)
        self.alpha = 0.  # ground diffusivity (m2/s)
        self.number_of_boreholes = 0  # number of total boreholes #

        # initiate fluid parameters
        self.k_f = 0.  # Thermal conductivity W/mK
        self.mfr = 0.  # Mass flow rate kg/s
        self.rho = 0.  # Density kg/m3
        self.Cp = 0.  # Thermal capacity J/kgK
        self.mu = 0.  # Dynamic viscosity Pa/s.
        self.Tf: float = 0.  # temperature of the fluid
        self.Tf_H: float = 16.  # maximum temperature of the fluid
        self.Tf_C: float = 0.  # minimum temperature of the fluid
        self.fluid_data_available: bool = False  # needs to be True in order to calculate Rb*

        # initiate borehole parameters
        self.r_in: float = 0.015  # inner pipe radius m
        self.r_out: float = 0.  # outer pipe radius m
        self.r_b: float = 0.  # borehole radius m
        self.k_g: float = 0.  # grout thermal conductivity W/mK
        self.k_p: float = 0.  # pipe thermal conductivity W/mK
        self.D_s: float = 0.  # distance of pipe until center of the borehole
        self.number_of_pipes: int = 0  # number of pipes in the borehole (single = 1, double = 2 etc.)
        self.D: float = 4.  # burial depth m
        self.epsilon = 1e-6  # pipe roughness
        self.pipe_data_available: bool = False  # needs to be True in order to calculate Rb*

        # initiate different sizing
        self.L2_sizing: bool = True
        self.L3_sizing: bool = False
        self.L4_sizing: bool = False
        self.quadrant_sizing: int = 0
        self.H_init: float = 100.
        self.sizing_setup()

        # check if the GHEtool is used by the gui i
        self.gui = gui

        # set boolean for printing output
        self.printing: bool = True
        # set list for the sizing ba length and width output
        self.combo: list = []

        """ define vars """
        # set load profiles
        self.set_peak_heating(peak_heating)
        self.set_peak_cooling(peak_cooling)
        self.set_baseload_cooling(baseload_cooling)
        self.set_baseload_heating(baseload_heating)

        # set simulation period
        self.simulation_period: int = simulation_period

        # set investment cost
        self.cost_investment: list = Borefield.DEFAULT_INVESTMENT
        self.set_investment_cost(investement_cost)

        # set length of the peak
        self.set_length_peak()

        # calculate number of boreholes
        self.set_number_of_boreholes(number_of_boreholes if number_of_boreholes is not None else 1)

        # set a custom borefield
        self.borefield = None
        self.set_borefield(borefield)

        # set a custom g-function
        self.custom_gfunction = None
        self.set_custom_gfunction(custom_gfunction)

    @staticmethod
    def configuration_string(N_1: int, N_2: int) -> str:
        """
        This functions returns the filename for the given configuration N_1, N_2.

        :return: the name of the datafile
        """
        string: str = str(max(N_1, N_2)) + "x" + str(min(N_1, N_2))
        return string

    def set_number_of_boreholes(self, number_of_boreholes: int = 1) -> None:
        """
        This functions sets the number of boreholes.

        :return None
        """
        self.number_of_boreholes = number_of_boreholes if number_of_boreholes > 1 else self.N_1 * self.N_2

    def set_borefield(self, borefield=None) -> None:
        """
        This function sets the borefield configuration. When no input, an empty array of length N_1 * N_2 will be made.

        :return None
        """
        if borefield is None:
            return
        self.borefield = borefield
        self.set_number_of_boreholes(len(borefield))

    def set_custom_gfunction(self, custom_gfunction) -> None:
        """
        This functions sets the custom gfunction.

        :return None
        """
        self.custom_gfunction = custom_gfunction
        self.gfunction_interpolation_array: list = []

    def set_investment_cost(self, investement_cost=None) -> None:
        """
        This function sets the investment cost. This is linear with respect to the total field length.

        :return None
        """
        if investement_cost is None:
            investement_cost = Borefield.DEFAULT_INVESTMENT
        self.cost_investment: list = investement_cost

    def set_length_peak(self, length: float = DEFAULT_LENGTH_PEAK) -> None:
        """
        This function sets the length of the peak to length.

        :return None
        """
        self.length_peak: float = length
        self.set_time_constants()

    def set_simulation_period(self, simulation_period: int) -> None:
        """
        This function sets the simulation period and updates the time constants.

        :param simulation_period: simulation period in years
        :return: None
        """
        self.simulation_period = simulation_period
        self.set_time_constants()

    def set_time_constants(self) -> None:
        """
        This function sets the time constants

        :return: None
        """
        # Number of segments per borehole
        self.th: float = self.length_peak * 3600.  # length of peak in seconds
        self.ty: float = self.simulation_period * 8760. * 3600
        self.tm: float = Borefield.UPM * 3600.
        self.td: float = self.length_peak * 3600.
        self.time = np.array([self.td, self.td + self.tm, self.ty + self.tm + self.td])

        # set the time array for the L3 sizing
        # This is one time for every month in the whole simulation period
        self.time_L3_first_year = Borefield.UPM * 3600 * np.arange(1, 13)
        self.time_L3_last_year = Borefield.UPM * 3600 * np.arange(1, self.simulation_period * 12 + 1)

        # set the time constant for the L4 sizing
        self.time_L4 = 3600 * np.arange(1, 8760 * self.simulation_period + 1)

    def set_ground_parameters(self, data: GroundData) -> None:
        """
        This function sets the relevant ground and borefield characteristics.

        :return None
        """
        self.H: float = data.H  # Borehole length (m)
        self.B: float = data.B  # Borehole spacing (m)

        self.N_1: int = data.N_1
        self.N_2: int = data.N_2

        self.Rb: float = data.Rb

        # Ground properties
        self.k_s: float = data.k_s  # Ground thermal conductivity (W/m.K)
        self.Tg: float = data.Tg  # Ground temperature at infinity (C)
        self.volumetric_heat_capacity: float = data.volumetric_heat_capacity  # Ground volumetric heat capacity (W/m3K)
        self.alpha: float = data.alpha  # Ground difussivity (defined as k_s/volumetric_heat_capacity)
        self.flux: float = data.flux  # Ground thermal heat flux (W/m2)

        # sets the number of boreholes as if it was a rectangular field, iff there is not yet a number of boreholes
        # defined by a custom configuration
        self.set_number_of_boreholes(self.N_1 * self.N_2)

        # new ground data implies that a new g-function should be loaded
        self.gfunction_interpolation_array = []

    def set_fluid_parameters(self, data: FluidData) -> None:
        """
        This function sets the relevant fluid characteristics.

        :return None
        """

        self.k_f = data.k_f  # Thermal conductivity W/mK
        self.rho = data.rho  # Density kg/m3
        self.Cp = data.Cp  # Thermal capacity J/kgK
        self.mu = data.mu  # Dynamic viscosity Pa/s
        self.set_mass_flow_rate(data.mfr)
        self.fluid_data_available = True

        if self.pipe_data_available:
            self.calculate_fluid_thermal_resistance()

    def set_pipe_parameters(self, data: PipeData) -> None:
        """
        This function sets the pipe parameters.

        :return None
        """

        self.r_in = data.r_in  # inner pipe radius m
        self.r_out = data.r_out  # outer pipe radius m
        self.k_p = data.k_p  # pipe thermal conductivity W/mK
        self.D_s = data.D_s  # distance of pipe until center m
        self.r_b = data.r_b  # borehole radius m
        self.number_of_pipes = data.number_of_pipes  # number of pipes #
        self.epsilon = data.epsilon  # pipe roughness
        self.k_g = data.k_g  # grout thermal conductivity W/mK
        self.D = data.D  # burial depth m
        # calculates the position of the pipes based on an axis-symmetrical positioning
        self.pos: list = self._axis_symmetrical_pipe

        self.pipe_data_available = True
        # calculate the different resistances
        if self.fluid_data_available:
            self.calculate_fluid_thermal_resistance()
        self.calculate_pipe_thermal_resistance()

    def set_max_ground_temperature(self, temp: float) -> None:
        """
        This function sets the maximal ground temperature to temp.

        :return None
        """
        self.Tf_H: float = temp

    def set_min_ground_temperature(self, temp: float) -> None:
        """
        This function sets the minimal ground temperature to temp.

        :return None
        """
        self.Tf_C: float = temp

    def set_mass_flow_rate(self, mfr: float) -> None:
        """
        This function sets the mass flow rate per borehole.

        :return None
        """
        self.mfr = mfr

    def calculate_fluid_thermal_resistance(self) -> None:
        """
        This function calculates and sets the fluid thermal resistance R_f.

        :return: None"""
        self.h_f: float = gt.pipes.convective_heat_transfer_coefficient_circular_pipe(self.mfr / self.number_of_pipes, self.r_in, self.mu,
                                                                                      self.rho, self.k_f, self.Cp,
                                                                                      self.epsilon)
        self.R_f: float = 1. / (self.h_f * 2 * pi * self.r_in)

    def calculate_pipe_thermal_resistance(self) -> None:
        """
        This function calculates and sets the pipe thermal resistance R_p.

        :return: None
        """
        self.R_p: float = gt.pipes.conduction_thermal_resistance_circular_pipe(self.r_in, self.r_out, self.k_p)

    @property
    def _Rb(self) -> float:
        """
        This function gives back the equivalent borehole resistance.

        :return: the borehole equivalent thermal resistance
        """
        # use a constant Rb*
        if self.use_constant_Rb:
            return self.Rb

        # calculate Rb*
        return self.calculate_Rb()

    def _Tg(self, H: float = None) -> float:
        """
        This function gives back the ground temperature
        When use_constant_Tg is False, the thermal heat flux is taken into account.

        :param H: depth of the field (optional)
        :return: ground temperature
        """
        if self.use_constant_Tg:
            return self.Tg

        # check if specific depth is given
        if H is None:
            H = self.H

        # geothermal gradient is equal to the geothermal heat flux divided by the thermal conductivity
        # avg ground temperature is (Tg + gradient + Tg) / 2
        return self.Tg + H * self.flux / self.k_s / 2

    def calculate_Rb(self) -> float:
        """
        This function returns the calculated equivalent borehole thermal resistance Rb* value.

        :return: the borehole equivalent thermal resistance
        """
        # check if all data is available
        if not self.pipe_data_available or not self.fluid_data_available:
            print("Please make sure you set al the pipe and fluid data.")
            raise ValueError

        # initiate temporary borefield
        borehole = gt.boreholes.Borehole(self.H, self.D, self.r_b, 0, 0)
        # initiate pipe
        pipe = gt.pipes.MultipleUTube(self.pos, self.r_in, self.r_out, borehole, self.k_s, self.k_g,
                                      self.R_p + self.R_f, self.number_of_pipes, J=2)
        try:
            # only in pygfunction >= v2.2.1
            return pipe.effective_borehole_thermal_resistance(self.mfr, self.Cp)
        except AttributeError:
            return gt.pipes.borehole_thermal_resistance(pipe, self.mfr, self.Cp)

    @property
    def _axis_symmetrical_pipe(self) -> list:
        """
        This function gives back the coordinates of the pipes in an axis-symmetrical pipe.

        :return: list of coordinates of the pipes in the borehole"""
        dt: float = pi / float(self.number_of_pipes)
        pos: list = [(0., 0.)] * 2 * self.number_of_pipes
        for i in range(self.number_of_pipes):
            pos[i] = (self.D_s * np.cos(2.0 * i * dt + pi), self.D_s * np.sin(2.0 * i * dt + pi))
            pos[i + self.number_of_pipes] = (self.D_s * np.cos(2.0 * i * dt + pi + dt),
                                             self.D_s * np.sin(2.0 * i * dt + pi + dt))
        return pos

    @property
    def _Bernier(self) -> float:
        """
        This function sizes the field based on the last year of operation, i.e. quadrants 2 and 4.

        :return: borefield depth
        """
        # initiate iteration
        H_prev = 0
        # set minimal depth to 50 m
        self.H = 50 if self.H < 1 else self.H
        # Iterates as long as there is no convergence
        # (convergence if difference between depth in iterations is smaller than THRESHOLD_BOREHOLE_DEPTH)
        while abs(self.H - H_prev) >= Borefield.THRESHOLD_BOREHOLE_DEPTH:
            # calculate the required g-function values
            gfunct_uniform_T = self.gfunction(self.time, self.H)
            # calculate the thermal resistances
            Ra = (gfunct_uniform_T[2] - gfunct_uniform_T[1]) / (2 * pi * self.k_s)
            Rm = (gfunct_uniform_T[1] - gfunct_uniform_T[0]) / (2 * pi * self.k_s)
            Rd = (gfunct_uniform_T[0]) / (2 * pi * self.k_s)
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

        :return: borefield depth
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
            Rpm = (gfunc_uniform_T[2] - gfunc_uniform_T[1]) / (2 * pi * self.k_s)
            Rcm = (gfunc_uniform_T[1] - gfunc_uniform_T[0]) / (2 * pi * self.k_s)
            Rh = (gfunc_uniform_T[0]) / (2 * pi * self.k_s)

            # calculate the total length
            L = (self.qh * self._Rb + self.qh * Rh + self.qm * Rcm + self.qpm * Rpm) / abs(self.Tf - self._Tg())

            # updating the depth values
            H_prev = self.H
            self.H = L / self.number_of_boreholes
        return self.H

    def sizing_setup(self, H_init: float = 100, use_constant_Rb: bool = None, use_constant_Tg: bool = None, quadrant_sizing: int = 0,
                     L2_sizing: bool = None, L3_sizing: bool = None, L4_sizing: bool = None) -> None:
        """
        This function sets the options for the sizing function.
        * The L2 sizing is the one explained in (Peere et al., 2021) and is the quickest method (it uses 3 pulses)
        * The L3 sizing is a more general approach which is slower but more accurate (it uses 24 pulses/year)
        * The L4 sizing is the most exact one, since it uses hourly data (8760 pulses/year)

        :param H_init: initial depth of the borefield to start the iteratation (m)
        :param use_constant_Rb: true if a constant Rb* value should be used
        :param use_constant_Tg: true if a constant Tg value should be used (the geothermal flux is neglected)
        :param quadrant_sizing: differs from 0 when a sizing in a certain quadrant is desired
        :param L2_sizing: true if a sizing with the l_2 method is needed
        :param L3_sizing: true if a sizing with the L3 method is needed
	:param L4_sizing: true if a sizing with the L4 method is needed
        :return: None
        """

        # check if just one sizing is given
        if np.sum([L2_sizing if L2_sizing is not None else 0, L3_sizing if L3_sizing is not None else 0, L4_sizing if L4_sizing is not None else 0]) > 1:
            raise ValueError("Please check if just one sizing method is chosen!")

        # set variables
        if use_constant_Rb is not None:
            self.use_constant_Rb = use_constant_Rb
        if use_constant_Tg is not None:
            self.use_constant_Tg = use_constant_Tg
        if quadrant_sizing is not None:
            self.quadrant_sizing = quadrant_sizing
        if self.H_init is not None:
            self.H_init = H_init
        if L2_sizing is not None:
            self.L2_sizing = L2_sizing
        if L3_sizing is not None:
            self.L3_sizing = L3_sizing
        if L4_sizing is not None:
            self.L4_sizing = L4_sizing

    def size(self, H_init: float = 100, use_constant_Rb: bool = None, use_constant_Tg: bool = None,
             L2_sizing: bool = None, L3_sizing: bool = None, L4_sizing: bool = None, quadrant_sizing: int = None) -> float:
        """
        This function sizes the borefield. It lets the user chose between three sizing methods.
        * The L2 sizing is the one explained in (Peere et al., 2021) and is the quickest method (it uses 3 pulses)
        * The L3 sizing is a more general approach which is slower but more accurate (it uses 24 pulses/year)
        * The L4 sizing is the most exact one, since it uses hourly data (8760 pulses/year)

        Please note that the changes sizing setup changes here are not saved! Use self.setupSizing for this.
        (e.g. if you size by putting the constantTg param to True but it was False, if you plot the results afterwards
        the constantTg will be False again and your results will seem off!)

        :param H_init: initial depth of the borefield to start the iteratation (m)
        :param use_constant_Rb: true if a constant Rb* value should be used
        :param use_constant_Tg: true if a constant Tg value should be used (the geothermal flux is neglected)
        :param L2_sizing: true if a sizing with the L2 method is needed
        :param L3_sizing: true if a sizing with the L3 method is needed
        :param L4_sizing: true if a sizing with the L4 method is needed
        :param quadrant_sizing: differs from 0 when a sizing in a certain quadrant is desired
        :return: borefield depth
        """
        # make backup of initial parameter states
        backup = (self.H_init, self.use_constant_Rb, self.use_constant_Tg, self.L2_sizing, self.L3_sizing, self.L4_sizing, self.quadrant_sizing)

        # run the sizing setup
        self.sizing_setup(H_init=H_init, use_constant_Rb=use_constant_Rb, use_constant_Tg=use_constant_Tg,
                          L2_sizing=L2_sizing, L3_sizing=L3_sizing, L4_sizing=L4_sizing, quadrant_sizing=quadrant_sizing)

        # sizes according to the correct algorithm
        if self.L2_sizing:
            depth = self.size_L2(self.H_init, self.quadrant_sizing)
        if self.L3_sizing:
            depth = self.size_L3(self.H_init, self.quadrant_sizing)
        if self.L4_sizing:
            depth = self.size_L4(self.H_init, self.quadrant_sizing)

        # reset initial parameters
        self.sizing_setup(H_init=backup[0], use_constant_Rb=backup[1], use_constant_Tg=backup[2], L2_sizing=backup[3],
                          L3_sizing=backup[4], L4_sizing=backup[5], quadrant_sizing=backup[6])

        # check if the field is not shallow
        if depth < self.THRESHOLD_WARNING_SHALLOW_FIELD and self.printing:
            print(f"The field has a calculated depth of {round(depth, 2)} m which is lower than the proposed minimum "
                  f"of {self.THRESHOLD_WARNING_SHALLOW_FIELD} m.")
            print("Please change your configuration accordingly to have a not so shallow field.")

        return depth

    def size_L2(self, H_init: float, quadrant_sizing: int = 0) -> float:
        """
        This function sizes the borefield of the given configuration according to the methodology explained in
        (Peere et al., 2021), which is a L2 method. When quadrant sizing is other than 0, it sizes the field based on
        the asked quadrant. It returns the borefield depth.

        :param H_init: initialize depth for sizing
        :param quadrant_sizing: if a quadrant is given the sizing is performed for this quadrant else for the relevant
        :return: borefield depth
        """

        # initiate with a given depth
        self.H_init: float = H_init

        def size_quadrant1():
            self.calculate_L3_params(False)  # calculate parameters
            return self._Carcel  # size

        def size_quadrant2():
            self.calculate_L2_params(False)  # calculate parameters
            self.qa = self.qa
            return self._Bernier  # size

        def size_quadrant3():
            self.calculate_L3_params(True)  # calculate parameters
            return self._Carcel  # size

        def size_quadrant4():
            self.calculate_L2_params(True)  # calculate parameters
            self.qa = self.qa
            return self._Bernier  # size

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
        This functions sizes the borefield based on a L3 method.

        :param H_init: initial value for the depth of the borefield to start iteration
        :param quadrant_sizing: differs from 0 if a sizing in a certain quadrant is desired
        :return: borefield depth
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
                else:
                    self.limiting_quadrant = 4
            else:
                # injection dominated, so quadrants 2 and 3 are relevant
                quadrant2 = self._size_based_on_temperature_profile(2)
                quadrant3 = self._size_based_on_temperature_profile(3)
                self.H = max(quadrant2, quadrant3)

                if self.H == quadrant2:
                    self.limiting_quadrant = 2
                else:
                    self.limiting_quadrant = 3

        return self.H

    def size_L4(self, H_init: float, quadrant_sizing: int = 0) -> float:
        """
        This functions sizes the borefield based on a L4 method (hourly method).

        :param H_init: initial value for the depth of the borefield to start iteration
        :param quadrant_sizing: differs from 0 if a sizing in a certain quadrant is desired
        :return: borefield depth
        """

        # check if hourly data is given
        if not self._check_hourly_load():
            raise Exception("The hourly data is incorrect.")

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
                else:
                    self.limiting_quadrant = 4
            else:
                # injection dominated, so quadrants 2 and 3 are relevant
                quadrant2 = self._size_based_on_temperature_profile(2, hourly=True)
                quadrant3 = self._size_based_on_temperature_profile(3, hourly=True)
                self.H = max(quadrant2, quadrant3)

                if self.H == quadrant2:
                    self.limiting_quadrant = 2
                else:
                    self.limiting_quadrant = 3

        return self.H

    def _size_based_on_temperature_profile(self, quadrant: int, hourly: bool = False) -> float:
        """
        This function sizes based on the temperature profile.
        It sizes for a specific quadrant and can both size with a monthly or an hourly resolution.

        :param quadrant: integer for the specific quadrant to be sized for (see (Peere et al., 2021) doi: 10.26868/25222708.2021.30180)
        :param hourly: True if an hourly resolution should be used
        :return: depth of the borefield
        """

        # initiate iteration
        H_prev = 0

        if self.H < 1:
            self.H = 50

        # Iterates as long as there is no convergence
        # (convergence if difference between depth in iterations is smaller than THRESHOLD_BOREHOLE_DEPTH)
        while abs(self.H - H_prev) >= Borefield.THRESHOLD_BOREHOLE_DEPTH:
            # calculate temperature profile
            self.calculate_temperatures(depth=self.H, hourly=hourly)

            # in case of quadrant 1 and 2, we are interested in the maximum temperature
            if quadrant == 1 or quadrant == 2:
                temperature_profile = self.results_peak_cooling
            else:
                temperature_profile = self.results_peak_heating

            if hourly:
                temperature_profile = self.temperature_result

            nb_of_steps = 12 if not hourly else 8760

            # in case of quadrants 1 and 3, we need the first year only
            # in case of quadrants 2 and 4, we need the last year only
            if quadrant == 1 or quadrant == 3:
                temperature_profile = temperature_profile[:nb_of_steps]
            else:
                temperature_profile = temperature_profile[-nb_of_steps:]

            H_prev = self.H

            if quadrant == 1 or quadrant == 2:
                # maximum temperature
                # convert back to required length
                self.H = (max(temperature_profile) - self._Tg()) / (self.Tf_H - self._Tg()) * H_prev
            else:
                # minimum temperature
                # convert back to required length
                self.H = (min(temperature_profile) - self._Tg()) / (self.Tf_C - self._Tg()) * H_prev

        return self.H

    def calculate_monthly_load(self) -> None:
        """
        This function calculates the average monthly load in kW.

        :return: None
        """
        self.monthly_load = (self.baseload_cooling - self.baseload_heating) / Borefield.UPM

    def set_baseload_heating(self, baseload: np.array) -> None:
        """
        This function defines the baseload in heating both in an energy as in an average power perspective.

        :param baseload: baseload in kWh (np.array or list)
        :return: None
        """
        self.baseload_heating = np.maximum(baseload, np.zeros(12))  # kWh
        self.monthly_load_heating = self.baseload_heating / Borefield.UPM  # kW
        self.calculate_monthly_load()
        self.calculate_imbalance()

        # new peak heating if baseload is larger than the peak
        self.set_peak_heating(np.maximum(self.peak_heating, self.monthly_load_heating))

    def set_baseload_cooling(self, baseload: np.array) -> None:
        """
        This function defines the baseload in cooling both in an energy as in an average power perspective.

        :param baseload: baseload in kWh (np.array or list)
        :return None
        """
        self.baseload_cooling = np.maximum(baseload, np.zeros(12))  # kWh
        self.monthly_load_cooling = self.baseload_cooling / Borefield.UPM # kW
        self.calculate_monthly_load()
        self.calculate_imbalance()

        # new peak cooling if baseload is larger than the peak
        self.set_peak_cooling(np.maximum(self.peak_cooling, self.monthly_load_cooling))

    def set_peak_heating(self, peak_load: np.array) -> None:
        """
        This function sets the peak heating to peak load.

        :param peak_load: peak load heating in kW (np.array or list)
        :return: None
        """
        self.peak_heating = np.maximum(peak_load, self.monthly_load_heating)

    def set_peak_cooling(self, peak_load: np.array) -> None:
        """
        This function sets the peak cooling to peak load.

        :param peak_load: peak load cooling in kW (np.array or list)
        :return: None
        """
        self.peak_cooling = np.maximum(peak_load, self.monthly_load_cooling)

    @property
    def investment_cost(self) -> float:
        """
        This function calculates the investment cost based on a cost profile linear to the total borehole length.

        :return: investement cost
        """
        return np.polyval(self.cost_investment, self.H * self.number_of_boreholes)

    def calculate_imbalance(self) -> None:
        """
        This function calculates the imbalance of the field.
        A positive imbalance means that the field is injection dominated, i.e. it heats up every year.

        :return: None
        """
        self.imbalance = np.sum(self.baseload_cooling) - np.sum(self.baseload_heating)

    def calculate_L2_params(self, HC: bool) -> None:
        """
        This function calculates the parameters for the sizing based on the last year of operation.

        :param HC: true if the borefield is limited by extraction load
        :return: None
        """

        # convert imbalance to Watt
        self.qa = self.imbalance / 8760. * 1000

        if HC:
            # limited by extraction load

            # temperature limit is set to the minimum temperature
            self.Tf = self.Tf_C

            # Select month with the highest peak load and take both the peak and average load from that month
            month_index = np.where(self.peak_heating == max(self.peak_heating))[0][0]
            self.qm = self.monthly_load[month_index] * 1000.
            self.qh = max(self.peak_heating) * 1000.

            # correct signs
            self.qm = -self.qm
            self.qa = -self.qa

        else:
            # limited by injection load

            # temperature limit set to maximum temperature
            self.Tf = self.Tf_H

            # Select month with the highest peak load and take both the peak and average load from that month
            month_index = np.where(self.peak_cooling == max(self.peak_cooling))[0][0]
            self.qm = self.monthly_load[month_index] * 1000.
            self.qh = max(self.peak_cooling) * 1000.

    def calculate_L3_params(self, HC: bool, month_index: int = None) -> int:
        """
        This function calculates the parameters for the sizing based on the first year of operation.

        :param HC: true if the field is limited by extraction load
        :param month_index: month with the highest peak load
        :return: month with the highest peak load
        """

        if HC:
            # limited by extraction load

            # temperature limit is set to the minimum temperature
            self.Tf = self.Tf_C

            # Select month with the highest peak load and take both the peak and average load from that month
            month_index = np.where(self.peak_heating == max(self.peak_heating))[0][0] if month_index is None else month_index
            self.qh = max(self.peak_heating) * 1000.

            self.qm = self.monthly_load[month_index] * 1000.

            if month_index < 1:
                self.qpm = 0
            else:
                self.qpm = np.sum(self.monthly_load[:month_index]) * 1000 / (month_index + 1)

            self.qm = -self.qm
        else:
            # limited by injection

            # temperature limit set to maximum temperature
            self.Tf = self.Tf_H

            # Select month with the highest peak load and take both the peak and average load from that month
            month_index = np.where(self.peak_cooling == max(self.peak_cooling))[0][0] if month_index is None else month_index
            self.qh = max(self.peak_cooling) * 1000.

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

        :param depth: depth for which the temperature profile should be calculated for.
        :param hourly: if True, then the temperatures are calculated based on the hourly data
        :return: None
        """
        self._print_temperature_profile(figure=False, H=depth, plot_hourly=hourly)

    def print_temperature_profile(self, legend: bool = True, plot_hourly: bool = False) -> None:
        """
        This function plots the temperature profile for the calculated depth.

        :param legend: bool if True a legend is printed
        :param plot_hourly: bool if True, then the temperature profile is calculated based on the hourly load
        if there is any.
        :return: None
        """

        # check for hourly data if this is requested
        if plot_hourly:
            self._check_hourly_load()

        self._print_temperature_profile(legend=legend, plot_hourly=plot_hourly)

    def print_temperature_profile_fixed_depth(self, depth, legend: bool = True, plot_hourly: bool = False) -> None:
        """
        This function plots the temperature profile for a fixed depth.

        :param depth: depth for which the temperature profile is calculated for
        :param legend: bool if True a legend is printed
        :param plot_hourly: bool if True, then the temperature profile is calculated based on the hourly load
        if there is any.
        :return: None
        """
        self._print_temperature_profile(legend=legend, H=depth, plot_hourly=plot_hourly)

    def _print_temperature_profile(self, legend: bool = True, H: float = None,
                                   plot_hourly: bool = False, figure: bool = True) -> None:
        """
        This function calculates the temperature evolution in the borefield using temporal superposition.
        It is possible to calculate this for a certain depth H, otherwise self.H will be used.
        If Figure = True than a figure will be plotted.

        :param legend: true if the legend should be shown
        :param H: depth of the borefield to evaluate the temperature profile
        :param figure: true if a figure should be shown
        :param plot_hourly: bool if True, then the temperature profile is calculated based on the hourly load
        if there is any.
        :return: None
        """

        H_backup = self.H
        if H is not None:
            self.H = H
        # set Rb* value
        self.Rb = self._Rb

        self.H = H_backup

        H = self.H if H is None else H

        if not plot_hourly:
            # making a numpy array of the monthly balance (self.monthly_load) for a period of self.simulation_period years
            # [kW]
            monthly_loads_array = np.tile(self.monthly_load, self.simulation_period)

            # self.g-function is a function that uses the precalculated data to interpolate the correct values of the
            # g-function. This dataset is checked over and over again and is correct
            g_values = self.gfunction(self.time_L3_last_year, H)

            # the g-function value of the peak with length_peak hours
            g_value_peak = self.gfunction(self.length_peak * 3600., H)

            # calculation of needed differences of the g-function values. These are the weight factors in the calculation
            # of Tb. Last element removed in order to make arrays the same length
            g_value_previous_step = np.concatenate((np.array([0]), g_values))[:-1]
            g_value_differences = g_values - g_value_previous_step

            temp = []

            # convolution to get the monthly results
            results = convolve(monthly_loads_array * 1000, g_value_differences)[:len(monthly_loads_array)]

            # calculation the borehole wall temperature for every month i
            Tb = results / (2 * pi * self.k_s) / (H * self.number_of_boreholes) + self._Tg(H)

            self.Tb = Tb
            # now the Tf will be calculated based on
            # Tf = Tb + Q * R_b
            results_month_cooling = Tb + np.tile(self.monthly_load_cooling, self.simulation_period) * 1000 \
                              * (self.Rb / self.number_of_boreholes / H)
            results_month_heating = Tb - np.tile(self.monthly_load_heating, self.simulation_period) * 1000 \
                              * (self.Rb / self.number_of_boreholes / H)

            # extra summation if the g-function value for the peak is included
            results_peak_cooling = results_month_cooling + np.tile(self.peak_cooling - self.monthly_load_cooling, self.simulation_period) * 1000 \
                                     * (g_value_peak[0] / self.k_s / 2 / pi + self.Rb) / self.number_of_boreholes / H
            results_peak_heating = results_month_heating - np.tile(self.peak_heating - self.monthly_load_heating, self.simulation_period) * 1000 \
                                   * (g_value_peak[0] / self.k_s / 2 / pi + self.Rb) / self.number_of_boreholes / H

            # save temperatures under variable
            self.results_peak_heating = results_peak_heating
            self.results_peak_cooling = results_peak_cooling
            self.results_month_cooling = results_month_cooling
            self.results_month_heating = results_month_heating

            # reset other variables
            self.temperature_result = np.array([])

        if plot_hourly:
            # making a numpy array of the monthly balance (self.monthly_load) for a period of self.simulation_period years
            # [kW]
            hourly_load = np.tile(self.hourly_cooling_load - self.hourly_heating_load, self.simulation_period)

            # self.g-function is a function that uses the precalculated data to interpolate the correct values of the
            # g-function. This dataset is checked over and over again and is correct
            g_values = self.gfunction(self.time_L4, H)

            # calculation of needed differences of the g-function values. These are the weight factors in the calculation
            # of Tb. Last element removed in order to make arrays the same length
            g_value_previous_step = np.concatenate((np.array([0]), g_values))[:-1]
            g_value_differences = g_values - g_value_previous_step

            temp = []

            # convolution to get the monthly results
            results = convolve(hourly_load * 1000, g_value_differences)[:len(hourly_load)]

            # calculation the borehole wall temperature for every month i
            Tb = results / (2 * pi * self.k_s) / (H * self.number_of_boreholes) + self._Tg(H)

            self.Tb = Tb
            # now the Tf will be calculated based on
            # Tf = Tb + Q * R_b
            temperature_result = Tb + hourly_load * 1000 * (self.Rb / self.number_of_boreholes / H)

            # save variables
            self.temperature_result = temperature_result

            # reset other variables
            self.results_peak_heating = np.array([])
            self.results_peak_cooling = np.array([])
            self.results_month_cooling = np.array([])
            self.results_month_heating = np.array([])

        # initiate figure
        if figure:
            # make a time array
            if plot_hourly:
                time_array = self.time_L4 / 12 / 3600 / 730
            else:
                time_array = self.time_L3_last_year / 12 / 730. / 3600.

            plt.rc('figure')
            fig = plt.figure()

            ax1 = fig.add_subplot(111)
            ax1.set_xlabel(r'Time (year)')
            ax1.set_ylabel(r'Temperature ($^\circ C$)')

            # plot Temperatures
            ax1.step(time_array, Tb, 'k-', where="pre", lw=1.5, label="Tb")

            if plot_hourly:
                ax1.step(time_array, temperature_result, 'b-', where="pre", lw=1, label='Tf')
            else:
                ax1.step(time_array, results_peak_cooling, 'b-', where="pre", lw=1.5, label='Tf peak cooling')
                ax1.step(time_array, results_peak_heating, 'r-', where="pre", lw=1.5, label='Tf peak heating')


                ax1.step(time_array, results_month_cooling, color='b', linestyle="dashed", where="pre", lw=1.5,
                         label='Tf base cooling')
                ax1.step(time_array, results_month_heating, color='r', linestyle="dashed", where="pre", lw=1.5,
                         label='Tf base heating')

            # define temperature bounds
            ax1.hlines(self.Tf_C, 0, self.simulation_period, colors='r', linestyles='dashed', label='', lw=1)
            ax1.hlines(self.Tf_H, 0, self.simulation_period, colors='b', linestyles='dashed', label='', lw=1)
            ax1.set_xticks(range(0, self.simulation_period + 1, 2))

            # Plot legend
            if legend:
                ax1.legend()
            ax1.set_xlim(left=0, right=self.simulation_period)
            plt.show()

    def gfunction(self, time_value: list, H: float) -> np.ndarray:
        """
        This function calculated the g-function based on interpolation of the precalculated data.

        :param time_value: list of seconds at which the gfunctions should be evaluated
        :param H: depth at which the gfunctions should be evaluated
        :return: np.array of gfunction values
        """

        # check for value of H < 1
        if H < 1:
            self.convergence += 1
            # check if the requested value is already DEFAULT_CONVERGENCE_MINIMAL_DEPTH below 1m
            if self.convergence == Borefield.DEFAULT_CONVERGENCE_MINIMAL_DEPTH:
                raise RuntimeError("Already ",
                                   Borefield.DEFAULT_CONVERGENCE_MINIMAL_DEPTH,
                                   "a depth smaller than 1m has been asked. This will lead to a convergence to a way to small"
                                   "field. Please check your borefield dimensions and load!")
        else:
            self.convergence = 0

        # set depth to minimum 1m
        H = max(H, 5)

        # if calculate is False, than the gfunctions are calculated on the spot
        if not self.use_precalculated_data:
            # Calculate the g-function for uniform borehole wall temperature

            # create custom Borefield
            custom_borefield = gt.boreholes.rectangle_field(self.N_1, self.N_2, self.B, self.B, H, D=4, r_b=0.075)

            # calculate gfunction
            gfunc_uniform_T = gt.gfunction.uniform_temperature(
                custom_borefield, np.asarray(time_value), self.alpha, nSegments=12, disp=False)

            return gfunc_uniform_T

        # set folder if no gui is used
        folder = FOLDER
        # get the name of the data fileImport
        if self.custom_gfunction is None:
            name = f'{self.configuration_string(self.N_1, self.N_2)}.pickle'
        else:
            name = f'{self.custom_gfunction}.pickle'

        # check if datafile exists
        if not os.path.isfile(f'{folder}/Data/{name}'):
            raise Exception('There is no precalculated data available. Please use the create_custom_datafile.')

        # load data fileImport
        data = pickle.load(open(f'{folder}/Data/{name}', "rb"))

        # remove the time value
        Time = Borefield.DEFAULT_TIME_ARRAY
        try:
            data.pop("Time")
        except KeyError:
            data = data

        if not self.gfunction_interpolation_array:
            # if no interpolation array exists, it creates one
            def make_interpolation_list_default() -> None:
                """
                This function creates an interpolation list and saves it under gfunction_interpolation_array.

                :return: None
                """

                B_array = list(data.keys())
                alpha_array = list(data[B_array[0]].keys())
                H_array = list(data[B_array[0]][alpha_array[0]].keys())
                self.H_max = max(H_array)
                B_array.sort()
                alpha_array.sort()
                H_array.sort()

                points = (B_array, alpha_array, H_array, Time)

                values: list = [[[data[B][alpha][h] for h in H_array] for alpha in alpha_array] for B in B_array]
                self.gfunction_interpolation_array = (points, values)

            def make_interpolation_list_custom() -> None:
                """
                This function creates an interpolation list from a custom dataset and saves it under
                gfunction_interpolation_array.

                :return: None
                """
                H_array = list(data["Data"].keys())
                H_array.sort()

                points = (H_array, Time)

                values = [data["Data"][h] for h in H_array]

                self.gfunction_interpolation_array = (points, values)

            if self.custom_gfunction is None:
                make_interpolation_list_default()
            else:
                make_interpolation_list_custom()
        try:
            if self.custom_gfunction is None:
                # interpolate
                points, values = self.gfunction_interpolation_array
                if not isinstance(time_value, float):
                    # multiple values are requested
                    g_value = interpolate.interpn(points, values,
                                                 np.array([[self.B, self.alpha, H, t] for t in time_value]))
                else:
                    # only one value is requested
                    g_value = interpolate.interpn(points, values, np.array([self.B, self.alpha, H, time_value]))
            else:
                # interpolate
                points, values = self.gfunction_interpolation_array
                if not isinstance(time_value, float):
                    # multiple values are requested
                    g_value = interpolate.interpn(points, values, np.array([[H, t] for t in time_value]))
                else:
                    # only one value is requested
                    g_value = interpolate.interpn(points, values, np.array([H, time_value]))
            return g_value

        except ValueError:
            if self.printing:
                if self.simulation_period > Borefield.MAX_SIMULATION_PERIOD:
                    print(f'Your requested simulation period of {self.simulation_period} years is beyond the limit of '
                          f'{Borefield.MAX_SIMULATION_PERIOD}) years of the precalculated data.')
                else:
                    print(f"Your requested depth of {H} m is beyond the limit {self.H_max} m of the precalculated "
                          f"data.")
                    print("Please change your borefield configuration accordingly.")
                print("-------------------------")
                print("This calculation stopped.")
            raise ValueError

    def create_custom_dataset(self, custom_borefield, name_datafile: str, n_segments: int = 12,
                              time_array=None, depth_array=None) -> None:
        """
        This function makes a datafile for a given custom borefield.

        :param custom_borefield: borefield object from pygfunction
        :param name_datafile: name of the custom datafile
        :param n_segments: number of segments used in creating the datafile
        :param time_array: timevalues used for the calculation of the datafile
        :param depth_array: the values for the borefield depth used to calculate the datafile
        :return: None
        """
        # set folder if no gui is used
        if depth_array is None:
            depth_array = Borefield.DEFAULT_DEPTH_ARRAY
        if time_array is None:
            time_array = Borefield.DEFAULT_TIME_ARRAY
        folder = '.' if self.gui else FOLDER
        # make filename
        name = f'{name_datafile}.pickle'
        # check if fileImport exists
        if not os.path.isfile(f"Data/{name}"):
            # does not exist, so create
            pickle.dump(dict([]), open(f'{folder}/Data/{name}', "wb"))
        else:
            raise Exception(f"The dataset {name} already exists. Please chose a different name.")

        data = pickle.load(open(f'{folder}/Data/{name}', "rb"), encoding='latin1')

        # see if k_s exists
        data["Data"] = dict([])

        data["Time"] = time_array

        for H in depth_array:
            print("Start H: ", H)

            # Calculate the g-function for uniform borehole wall temperature

            # set borehole depth in borefield
            for borehole in custom_borefield:
                borehole.H = H

            gfunc_uniform_T = gt.gfunction.uniform_temperature(
                custom_borefield, time_array, self.alpha, nSegments=n_segments, disp=True)

            data["Data"][H] = gfunc_uniform_T

        self.set_custom_gfunction(name_datafile)
        print(f"A new dataset with name {name} has been created in {os.path.dirname(os.path.realpath(__file__))}\Data.")
        pickle.dump(data, open(f'{folder}/Data/{name}', "wb"))

    def set_hourly_heating_load(self, heating_load: np.array) -> None:
        """
        This function sets the hourly heating load in kW.

        :param heating_load: the hourly heating load as an array/list
        :return None
        """
        self.hourly_heating_load = np.array(heating_load)

        # set monthly loads
        self.set_peak_heating(self._reduce_to_peak_load(self.hourly_heating_load, max(heating_load)))
        self.set_baseload_heating(self._reduce_to_monthly_load(self.hourly_heating_load, max(heating_load)))

    def set_hourly_cooling_load(self, cooling_load: np.array) -> None:
        """
        This function sets the hourly heating load in kW.

        :param cooling_load: the hourly heating load as an array/list
        :return None
        """
        self.hourly_cooling_load = np.array(cooling_load)

        # set monthly loads
        self.set_peak_cooling(self._reduce_to_peak_load(self.hourly_cooling_load, max(cooling_load)))
        self.set_baseload_cooling(self._reduce_to_monthly_load(self.hourly_cooling_load, max(cooling_load)))

    def _check_hourly_load(self) -> bool:
        """
        This function checks if there is correct hourly data available.

        :return: True if the data is correct
        """
        # check whether there is data given
        if self.hourly_cooling_load is None or self.hourly_heating_load is None:
            raise ValueError("No data is given for either the heating or cooling load.")
            return False

        # check whether the data is hourly
        if len(self.hourly_heating_load) != 8760 or len(self.hourly_cooling_load) != 8760:
            raise ValueError("Incorrect length for either the heating or cooling load")
            return False

        # check whether or not there are negative values in the data
        if min(self.hourly_cooling_load) < 0 or min(self.hourly_heating_load) < 0:
            raise ValueError("There are negative values in either the heating or cooling load.")
            return False

        return True

    def load_hourly_profile(self, file_path, header: bool = True, separator: str = ";",
                            first_column_heating: bool = True) -> None:
        """
        This function loads in an hourly load profile. It opens a csv and asks for the relevant column where the data
        is in. first_column_heating is true if the first column in the datafile is for the heating values.
        header is true if there is a header in the csv fileImport.
        separator is the separator in the csv fileImport.
        the load should be provided in kW.

        :param file_path: location of the hourly load file
        :param header: true if the file contains a header
        :param separator: symbol used in the file to separate columns
        :param first_column_heating: true if the first column in the file is the column with heating loads
        :return: None
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
        This function converts an hourly load profile to the monthly profiles used in the sizing.

        :param peak_cooling_load: peak power in cooling [kW]
        :param peak_heating_load: peak power in heating [kW]
        :return: None
        """

        try:
            self.hourly_cooling_load[0]
            self.hourly_heating_load[0]
        except IndexError:
            self.load_hourly_profile()

        if peak_cooling_load is None:
            peak_cooling_load = max(self.hourly_cooling_load)
        if peak_heating_load is None:
            peak_heating_load = max(self.hourly_heating_load)

        # calculate peak and base loads
        self.set_peak_cooling(self._reduce_to_peak_load(self.hourly_cooling_load, peak_cooling_load))
        self.set_peak_heating(self._reduce_to_peak_load(self.hourly_heating_load, peak_heating_load))
        self.set_baseload_cooling(self._reduce_to_monthly_load(self.hourly_cooling_load, peak_cooling_load))
        self.set_baseload_heating(self._reduce_to_monthly_load(self.hourly_heating_load, peak_heating_load))

    @staticmethod
    def _reduce_to_monthly_load(load: list, peak: float) -> list:
        """
        This function calculates the monthly load based, taking a maximum peak value into account.

        :param load: a list of hourly loads
        :param peak: a maximum peak power [kW]
        :return: list of monthly loads [kWh]
        """
        month_load = []
        for i in range(12):
            temp = load[Borefield.HOURLY_LOAD_ARRAY[i]:Borefield.HOURLY_LOAD_ARRAY[i + 1] + 1]
            month_load.append(np.sum(np.minimum(temp, peak)))

        return month_load

    @staticmethod
    def _reduce_to_peak_load(load: list, peak: float) -> list:
        """
        This function calculates the monthly peak load, taking a maximum peak value into account.

        :param load: a list of hourly loads
        :param peak: a maximum peak power [kW]
        :return: list of monthly peak loads
        """
        peak_load = []
        for i in range(12):
            temp = load[Borefield.HOURLY_LOAD_ARRAY[i]:Borefield.HOURLY_LOAD_ARRAY[i + 1] + 1]
            peak_load.append(max(np.minimum(peak, temp)))
        return peak_load

    def optimise_load_profile(self, depth: float = 150, print_results: bool = False) -> None:
        """
        This function optimises the load based on the given borefield and the given hourly load.
        It does so base on a load-duration curve.

        :param depth: depth of the borefield [m]
        :param print_results: True if results need to be plotted
        :return: None
        """

        # since the depth does not change, the Rb* value is constant
        # set to use a constant Rb* value but save the initial parameters
        Rb_backup = self.Rb
        if not self.use_constant_Rb:
            self.Rb = self.calculate_Rb()
        use_constant_Rb_backup = self.use_constant_Rb
        self.use_constant_Rb = True

        # if no hourly profile is given, load one
        if not self._check_hourly_load():
            return

        # set initial peak loads
        init_peak_heat_load = max(self.hourly_heating_load)
        init_peak_cool_load = max(self.hourly_cooling_load)

        # peak loads for iteration
        peak_heat_load = init_peak_heat_load
        peak_cool_load = init_peak_cool_load

        # set iteration criteria
        cool_ok, heat_ok = False, False

        while not cool_ok or not heat_ok:
            # calculate peak and base loads
            self.convert_hourly_to_monthly(peak_cool_load, peak_heat_load)

            # calculate temperature profile, just for the results
            self._print_temperature_profile(legend=False, H=depth, figure=False)

            # deviation from minimum temperature
            if abs(min(self.results_peak_heating) - self.Tf_C) > 0.05:

                # check if it goes below the threshold
                if min(self.results_peak_heating) < self.Tf_C:
                    peak_heat_load -= 1 * max(1, 10 * (self.Tf_C - min(self.results_peak_heating)))
                else:
                    peak_heat_load = min(init_peak_heat_load, peak_heat_load + 1)
                    if peak_heat_load == init_peak_heat_load:
                        heat_ok = True
            else:
                heat_ok = True

            # deviation from maximum temperature
            if abs(max(self.results_peak_cooling) - self.Tf_H) > 0.05:

                # check if it goes above the threshold
                if max(self.results_peak_cooling) > self.Tf_H:
                    peak_cool_load -= 1 * max(1, 10 * (-self.Tf_H + max(self.results_peak_cooling)))
                else:
                    peak_cool_load = min(init_peak_cool_load, peak_cool_load + 1)
                    if peak_cool_load == init_peak_cool_load:
                        cool_ok = True
            else:
                cool_ok = True

        # calculate the resulting hourly profile that can be put on the field
        self.hourly_cooling_load_on_the_borefield = np.maximum(peak_cool_load, self.hourly_cooling_load)
        self.hourly_heating_load_on_the_borefield = np.maximum(peak_heat_load, self.hourly_heating_load)

        # calculate the resulting hourly profile that cannot be put on the field
        self.hourly_cooling_load_external = np.maximum(0, self.hourly_cooling_load - peak_cool_load)
        self.hourly_heating_load_external = np.maximum(0, self.hourly_heating_load - peak_heat_load)

        # calculate the resulting monthly profile that cannot be put on the field
        temp = self._reduce_to_monthly_load(self.hourly_cooling_load, max(self.hourly_cooling_load))
        self.monthly_load_cooling_external = temp - self.baseload_cooling
        temp = self._reduce_to_monthly_load(self.hourly_heating_load, max(self.hourly_heating_load))
        self.monthly_load_heating_external = temp - self.baseload_heating
        temp = self._reduce_to_peak_load(self.hourly_cooling_load, max(self.hourly_cooling_load))
        self.peak_cooling_external = temp - self.peak_cooling
        temp = self._reduce_to_peak_load(self.hourly_heating_load, max(self.hourly_heating_load))
        self.peak_heating_external = temp - self.peak_heating

        # restore the initial parameters
        self.Rb = Rb_backup
        self.use_constant_Rb = use_constant_Rb_backup

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

        if print_results:
            # plot results
            self._print_temperature_profile(H=depth)

    def size_by_length_and_width(self, H_max: float, L1: float, L2: float, B_min: float = 3.0,
                                 B_max: float = 9.0, L2_sizing: bool = True, nb_of_options: int = 5) -> list:
        """
        Function to size the borefield by length and with. It returns a list of possible borefield sizes,
        with increasing total length.

        :param H_max: maximal borehole depth [m]
        :param L1: maximal width of borehole field [m]
        :param L2: maximal length of borehole field [m]
        :param B_min: minimal borehole spacing [m]
        :param B_max: maximal borehole spacing [m]
        :param L2_sizing: boolean to check if level two or level three sizing method should be used
        :param nb_of_options: number of options that should be returned.
        :return: list of possible combinations (each combination is a tuple where the first two elements are the
        number of boreholes in each direction, the third element the borehole spacing and the fourth element
        the depth of the borefield and the last element is the total borefield length).
        An Empty list is returned if no result is found
        """

        # set larger one of l_1 and l_2 to the width
        max_width = max(L1, L2)
        max_length = min(L1, L2)

        # calculate max borefield size
        N1_max = min(int(max_width / B_min), 20)
        N2_max = min(int(max_length / B_min), 20)

        # set depth to maximum depth
        self.H = H_max

        # calculate set of possible options
        options = set([])
        for N1 in range(1, N1_max + 1):
            N2 = N1
            while N2 <= N2_max:
                # calculate possible spacings
                B = min(max_width / N1, max_length / N2, B_max)

                # iterate over all possible B's
                for B in np.arange(B_min, B + 0.1, 0.5):
                    # set borefield parameters
                    self.B = B
                    self._reset_for_sizing(N1, N2)
                    self._print_temperature_profile(figure=False)
                    if max(self.results_peak_cooling) < self.Tf_H and max(self.results_peak_heating) > self.Tf_C:
                        options.add((N1, N2, B))

                N2 += 1

        # return empty list if options = {}
        if options == set([]):
            return []

        # set result dictionary
        results = {}

        # size all options
        for option in options:
            self._reset_for_sizing(option[0], option[1])
            self.B = option[2]
            depth = self.size(H_init=100, L2_sizing=L2_sizing)

            # save result in results dictionary with the total length as key
            results[depth * self.number_of_boreholes] = (option[0], option[1], option[2], depth)

        # get all the solutions
        lengths = list(results.keys())
        lengths.sort()
        # reverse for decending order
        lengths[::-1]

        # cut to right length
        lengths = lengths[0:nb_of_options]

        return [results[i] for i in lengths]

    def size_complete_field_robust(self, H_max: float, l_1: float, l_2: float, B_min: float = 3.0, B_max: float = 9.0,
                                   L2_sizing: bool = True, use_constant_Rb: bool = False) -> list:
        """
        Function to size the minimal number of borefield by borefield length and width on a robust and more
        time-consuming way.

        :param H_max: maximal borehole depth [m]
        :param l_1: maximal width of borehole field [m]
        :param l_2: maximal length of borehole field [m]
        :param B_min: minimal borehole spacing [m]
        :param B_max: maximal borehole spacing [m]
        :param L2_sizing: boolean to check if level two or level three sizing method should be used
        :param use_constant_Rb: boolean to check if a constant borehole resistance should be used
        :return: list of possible combinations (each combination is a tuple where the first two elements are the
        number of boreholes in each direction, the third element the borehole spacing and the last element
        the depth of the borefield). An Empty list is returned if no result is found
        """
        # check if length > width
        l_2_bigger_then_l_1: bool = l_2 > l_1
        # change length and width if length > width
        (l_1, l_2) = (l_2, l_1) if l_2_bigger_then_l_1 else (l_1, l_2)
        # set start maximal number of boreholes
        n_n_max_start: int = 20 * 20
        # set maximal number of boreholes
        n_n_max: int = n_n_max_start
        # list of possible combinations
        combo: list = []
        # deactivate printing
        printing_backup = self.printing
        self.printing: bool = False
        # minimal product to break loop
        product_min = 0
        # start loop over borehole spacing
        for B in np.arange(B_max, B_min * 0.99999, -0.5):
            # calculate maximal number of boreholes in length and width direction
            n_1_max = min(int(l_1 / B), 20)
            n_2_max = min(int(l_2 / B), 20)
            # set borehole spacing
            self.B = B
            # start loop over number of boreholes in length and width direction
            for N_1 in range(n_1_max, 0, -1):
                for N_2 in range(min(n_2_max, N_1), 0, -1):
                    # reset borefield values for sizing
                    self._reset_for_sizing(N_1, N_2)
                    # calculate number of total boreholes which should be minimal
                    product = N_1 * N_2
                    # continue loop if product is higher than current maxima to avoid calculation
                    if product > n_n_max:
                        continue
                    # break loop id product is less than the current minima to avoid calculation
                    if product < product_min:
                        break
                    # try to size current borefield configuration else set minimal product
                    try:
                        depth = self.size(H_max, L2Sizing=L2_sizing, L3_sizing=not L2_sizing, use_constant_Rb=use_constant_Rb)
                    except ValueError:
                        product_min = product
                        continue
                    # break loop if depth is higher than the maxima
                    if depth > H_max:
                        break
                    # save result in combo list and update maximal number of boreholes if current product is less the
                    # maxima
                    if product < n_n_max:
                        n_n_max = product
                        combo = [[N_1, N_2, B, depth]]
                    # append solution which leads to the same number of boreholes
                    elif product == n_n_max:
                        combo.append([N_1, N_2, B, depth])
        # if no solution is found return an empty list
        if n_n_max == n_n_max_start:
            return []
        # change N_1 and N_2 if length > width
        combo = [[i[1], i[0], i[2], i[3]] for i in combo] if l_2_bigger_then_l_1 else combo
        # set number of boreholes in length and width, borehole spacing and depth of first solution
        self.N_1 = combo[0][0]
        self.N_2 = combo[0][1]
        self.B = combo[0][2]
        self.H = combo[0][3]
        # reset variables for further calculations
        self._reset_for_sizing(self.N_1, self.N_2)
        # reset printing
        self.printing: bool = printing_backup
        # save result list
        self.combo = combo
        # return results list
        return combo

    def size_complete_field_fast(self, H_max: float, l_1: float, l_2: float, B_min: float = 3.0, B_max: float = 9.0,
                                 L2_sizing: bool = True, use_constant_Rb: bool = False) -> list:
        """
        Function to size the minimal number of borefield by borefield length and width on a fast and not robust way.
        There are possible solution that can not be found.

        :param H_max: maximal borehole depth [m]
        :param l_1: maximal width of borehole field [m]
        :param l_2: maximal length of borehole field [m]
        :param B_min: minimal borehole spacing [m]
        :param B_max: maximal borehole spacing [m]
        :param L2_sizing: boolean to check if level two or level three sizing method should be used
        :param use_constant_Rb: boolean to check if a constant borehole resistance should be used
        :return: list of possible combinations (each combination is a tuple where the first two elements are the
        number of boreholes in each direction, the third element the borehole spacing and the last element
        the depth of the borefield). An Empty list is returned if no results is found
        """
        # check if length > width
        l2_bigger_then_l1: bool = l_2 > l_1
        # change length and width if length > width
        (l_1, l_2) = (l_2, l_1) if l2_bigger_then_l1 else (l_1, l_2)
        # set start maximal number of boreholes
        n_n_max_start: int = 21 * 21
        # set maximal number of boreholes
        n_n_max: int = n_n_max_start
        # list of possible combinations
        combo: list = []
        # deactivate printing
        printing_backup = self.printing
        self.printing: bool = False
        # start loop over borehole spacing
        for B in np.arange(B_max, B_min * 0.99999, -0.5):
            # calculate maximal number of boreholes in length and width direction
            N1_max = min(int(l_1 / B), 20)
            N2_max = min(int(l_2 / B), 20)
            # reset variables for sizing
            self._reset_for_sizing(N1_max, N2_max)
            # set borehole spacing
            self.B = B
            # save start configuration to product old
            total_number_boreholes_old = self.N_1 * self.N_2
            # try to determine depth and break loop if unsuccessful
            try:
                # size current borefield configuration
                depth = self.size(H_max, L2_sizing=L2_sizing, L3_sizing=not L2_sizing, use_constant_Rb=use_constant_Rb)
                # determine required number of boreholes
                number_boreholes = int(depth * total_number_boreholes_old / H_max) + 1
                # determine number of boreholes in length and width direction which accomplish the total number of
                # boreholes
                res = self._calc_number_boreholes(number_boreholes, N1_max, N2_max)
                # reset variables for sizing
                self._reset_for_sizing(res[0][0], res[0][1])
                # determine new total number of boreholes
                total_number_boreholes_new = self.N_1 * self.N_2
                # start counter
                counter = 0
                # start while loop to size borefield
                while total_number_boreholes_old != total_number_boreholes_new:
                    # determine gradient to calculate new total borehole number if counter > 4 with a gradient of 0.51
                    # else 1
                    gradient = int(0.51 * (total_number_boreholes_new - total_number_boreholes_old)) if counter > 4 \
                        else int(total_number_boreholes_new - total_number_boreholes_old)
                    # determine new total borehole number
                    total_number_boreholes_new = total_number_boreholes_old + np.sign(gradient) * min(abs(gradient), 1)
                    # determine depth for the new configuration
                    depth = self.size(H_max, L2_sizing, use_constant_Rb=use_constant_Rb)
                    # determine new total number of boreholes
                    number_boreholes = int(depth * total_number_boreholes_new / H_max) + 1
                    # determine number of boreholes in length and width directions
                    res = self._calc_number_boreholes(number_boreholes, N1_max, N2_max)
                    # reset borefield variables for sizing
                    self._reset_for_sizing(res[0][0], res[0][1])
                    # set old total number of boreholes
                    total_number_boreholes_old = self.N_1 * self.N_2
                    # count counter
                    counter += 1
                    # break loop if counter is higher than 20 and the depth is below the maximal depth
                    if counter > 20 and depth <= H_max:
                        break
                # save configuration if new total number of boreholes is smaller than the maximal number so far
                if total_number_boreholes_new < n_n_max:
                    # save new maximal number
                    n_n_max = total_number_boreholes_new
                    # if more than 1 result is found calculate the depth and append the solution if it fits maximal
                    # depth
                    if len(res) > 1:
                        # reset list
                        combo: list = []
                        # reset boolean for first element
                        first: bool = True
                        # start loop over possible solutions
                        for i in res:
                            # if first element just append results
                            if first:
                                combo.append([i[0], i[1], B, self.H])
                                first = False
                                continue
                            # if not first element reset variables and determine new depth and then append if it fits
                            # the maximal depth
                            self._reset_for_sizing(i[0], i[1])
                            self.size(H_max, L2_sizing, use_constant_Rb=use_constant_Rb)
                            if self.H < H_max:
                                combo.append([i[0], i[1], B, self.H])
                    else:
                        # just create the list if just one solution is found
                        combo = [[res[0][0], res[0][1], B, self.H]]
                # append solutions if the same total number of boreholes is found as the current maximal number
                elif total_number_boreholes_new == n_n_max:
                    # if more than 1 result is found calculate the depth and append the solution if it fits maximal
                    # depth
                    if len(res) > 1:
                        first: bool = True
                        for i in res:
                            # if first element just append results
                            if first:
                                combo.append([i[0], i[1], B, self.H])
                                first = False
                                continue
                            # if not first element reset variables and determine new depth and then append if it fits
                            # the maximal depth
                            self._reset_for_sizing(i[0], i[1])
                            self.size(H_max, L2_sizing, use_constant_Rb=use_constant_Rb)
                            if self.H < H_max:
                                combo.append([i[0], i[1], B, self.H])
                    else:
                        # just append list if just one solution is found
                        combo += [[res[0][0], res[0][1], B, self.H]]

            except ValueError:
                # break if no result can be found, because depth is too deep for precalculated data
                break
        # if no solution is found return an empty list
        if n_n_max == n_n_max_start:
            return []
        # change N_1 and N_2 if length > width
        combo = [[i[1], i[0], i[2], i[3]] for i in combo] if l2_bigger_then_l1 else combo
        # set number of boreholes in length and width, borehole spacing and depth
        self.N_1 = combo[0][1]
        self.N_2 = combo[0][0]
        self.B = combo[0][2]
        self.H = combo[0][3]
        # reset variables for further calculations
        self._reset_for_sizing(self.N_1, self.N_2)
        # activate printing
        self.printing: bool = printing_backup
        # save result list
        self.combo = combo
        # return results list
        return combo

    def _reset_for_sizing(self, N_1: int, N_2: int) -> None:
        """
        Function to reset borehole

        :param N_1: width of rectangular field (#)
        :param N_2: length of rectangular field (#)
        :return: None
        """
        # set number of boreholes
        self.N_1, self.N_2 = N_1, N_2
        # reset interpolation array
        self.gfunction_interpolation_array = []
        # set number of boreholes because number of boreholes has changed
        self.set_number_of_boreholes()

    @staticmethod
    def _calc_number_boreholes(n_min: int, N1_max: int, N2_max: int) -> list:
        """
        calculation for number of boreholes which is higher than n but minimal total number

        :param n_min: minimal number of boreholes
        :param N1_max: maximal width of rectangular field (#)
        :param N2_max: maximal length of rectangular field (#)
        :return: list of possible solutions
        """
        # set default result
        res = [(20, 20)]
        # set maximal number
        max_val = 20 * 20
        # loop over maximal number in width and length
        for i in range(1, N1_max + 1):
            for j in range(1, min(N2_max, i) + 1):
                # determine current number
                current_number: int = i * j
                # save number of boreholes  and maximal value if is lower than current maximal value and higher than
                # minimal value
                if n_min <= current_number < max_val:
                    res = [(i, j)]
                    max_val = current_number
                # also append combination if current number is equal to current maximal value
                elif current_number == max_val:
                    res.append((i, j))
        # return list of possible solutions
        return res

    def draw_borehole_internal(self) -> None:
        """
        plots the position of the pipes in the borehole

        :return: None
        """

        # calculate the pipe positions
        pos = self._axis_symmetrical_pipe

        # set figure
        figure, axes = plt.subplots()

        # initate circles
        circles_outer = []
        circles_inner = []

        # color inner circles and outer circles
        for i in range(self.number_of_pipes):
            circles_outer.append(plt.Circle(pos[i], self.r_out, color="black"))
            circles_inner.append(plt.Circle(pos[i], self.r_in, color="red"))
            circles_outer.append(plt.Circle(pos[i + self.number_of_pipes], self.r_out, color="black"))
            circles_inner.append(plt.Circle(pos[i + self.number_of_pipes], self.r_in, color="blue"))

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

    def plot_load_duration(self) -> None:
        """
        This function makes a load-duration curve from the hourly values.

        :return: None
        """

        # check if there are hourly values
        if not self._check_hourly_load():
            return

        heating = self.hourly_heating_load.copy()
        heating[::-1].sort()

        cooling = self.hourly_cooling_load.copy()
        cooling.sort()
        cooling = cooling * (-1)
        print(np.average(cooling[-10:]), cooling[-10])

        plt.figure()
        plt.step(np.arange(0, 8760, 1), heating, 'r-', label="Heating")
        plt.step(np.arange(0, 8760, 1), cooling, 'b-', label="Heating")
        plt.hlines(0, 0, 8759, color="black")

        plt.xlabel("Time [hours]")
        plt.ylabel("Power [kW]")

        plt.xlim(0, 8760)

        plt.title("Load-duration curve")

        plt.show()
