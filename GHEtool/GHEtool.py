import numpy as np
import pickle
from scipy import interpolate
from math import pi
import pygfunction as gt
import os.path
import matplotlib.pyplot as plt
import functools
from tkinter import filedialog
import openpyxl
from typing import Union

FOLDER = os.path.dirname(os.path.realpath(__file__))  # solve problem with importing GHEtool from subfolders


class GroundData:
    __slots__ = 'H', 'B', 'k_s', 'Tg', 'Rb', 'N_1', 'N_2'

    def __init__(self, h: float, b: float, k_s: float, t_g: float, r_b: float, n_1: int, n_2: int):
        self.H = h  # m
        self.B = b  # m
        self.k_s = k_s  # W/mK
        self.Tg = t_g  # °C
        self.Rb = r_b  # mK/W
        self.N_1 = n_1  # #
        self.N_2 = n_2  # #


class Borefield:
    __slots__ = 'base_load_heating', 'base_load_cooling', 'H', 'H_init', 'B', 'N_1', 'N_2', 'Rb', 'k_s', 'Tg', 'ty', \
                'td', 'time', 'hourlyHeatingLoad', 'UPM', 'thresholdBorholeDepth', 'H_max', 'maxSimulationPeriod', \
                'hourlyCoolingLoad', 'numberOfBoreholes', 'bore_field', 'custom_g_function', 'costInvestment', 'tm', \
                'lengthPeak', 'th', 'Tf_H', 'Tf_C', 'limiting_quadrant', 'monthlyLoad', 'monthlyLoadHeating', \
                'monthlyLoadCooling', 'peakHeating', 'imbalance', 'qa', 'T_f', 'qm', 'qh', 'qpm', 'tcm', 'tpm', \
                'peakCooling', 'simulationPeriod', 'defaultInvestement', 'defaultLengthPeak', 'defaultDepthArray', \
                'factor_temperature_profile', 'resultsCooling', 'resultsHeating', 'resultsPeakHeating', \
                'resultsPeakCooling', 'resultsMonthCooling', 'resultsMonthHeating', 'Tb', \
                'thresholdWarningShallowField', 'GUI', 'printing', 'defaultTimeArray', 'hourlyLoadArray', \
                'g_function_Interpolation_Array', 'combo'

    def __init__(self, simulation_period: int, number_of_boreholes: int = None, peak_heating: list = None,
                 peak_cooling: list = None, base_load_heating: list = None, base_load_cooling: list = None,
                 investment_cost: list = None, bore_field=None, custom_g_function=None, gui: bool = False):
        """This function initiates the Borefield class"""

        # initiate vars
        list_of_zeros = [0] * 12
        if base_load_cooling is None:
            base_load_cooling: list = list_of_zeros
        if base_load_heating is None:
            base_load_heating: list = list_of_zeros
        if peak_cooling is None:
            peak_cooling: list = list_of_zeros
        if peak_heating is None:
            peak_heating: list = list_of_zeros

        self.base_load_heating: list = list_of_zeros
        self.base_load_cooling: list = list_of_zeros
        self.limiting_quadrant: int = 0
        self.T_f: float = 0.
        self.g_function_Interpolation_Array: list = []

        self.H: float = 0.  # Borehole length (m)
        self.B: float = 0.  # Borehole spacing (m)

        self.N_1: int = 22
        self.N_2: int = 22

        self.numberOfBoreholes: int = self.N_1 * self.N_2

        self.Rb: float = 0.

        # Ground properties
        self.k_s: float = 0.  # Ground thermal conductivity (W/m.K)
        self.Tg: float = 0.  # Ground temperature at infinity (C)
        self.Tf_H: float = 0.
        self.Tf_C: float = 0.

        self.monthlyLoad: list = []
        self.monthlyLoadHeating: list = []
        self.monthlyLoadCooling: list = []

        self.peakHeating: list = []
        self.peakCooling: list = []
        self.imbalance: float = 0.

        self.qm: list = []
        self.qa: list = []
        self.qh: list = []
        self.qpm: float = 0.
        self.tcm: float = 0.
        self.tpm: float = 0.
        self.lengthPeak: float = 0
        self.th: float = 0.  # length of peak in seconds
        self.ty: float = 0.
        self.tm: float = 0.
        self.td: float = 0.
        self.time: np.array = np.zeros(1)
        self.thresholdWarningShallowField: int = 50  # m hereafter one needs to chance to fewer boreholes with more

        self.hourlyHeatingLoad: list = []
        self.hourlyCoolingLoad: list = []
        self.Tb: list = []
        self.GUI = gui  # check if the GHEtool is used by the GUI i
        self.printing: bool = True

        self.thresholdBorholeDepth: float = 0.05  # threshold for iteration
        self.H_max: float = 0  # max threshold for interpolation
        self.maxSimulationPeriod: int = 100  # maximal value for simulation

        # define default values
        self.defaultInvestement: list = [35, 0]  # 35 EUR/m
        self.defaultLengthPeak: int = 6  # hours
        self.defaultDepthArray: list = [1] + list(range(25, 351, 25))  # m
        self.defaultTimeArray: np.array = gt.load_aggregation.ClaessonJaved(3600., self.maxSimulationPeriod * 8760.
                                                                            * 3600.).get_times_for_simulation()  # sec

        temp: int = 0
        self.hourlyLoadArray: list = []
        for i in [0, 24 * 31, 24 * 28, 24 * 31, 24 * 30, 24 * 31, 24 * 30, 24 * 31, 24 * 31, 24 * 30, 24 * 31, 24 * 30,
                  24 * 31]:
            temp += i
            self.hourlyLoadArray.append(temp)
        # depth, because the calculations are no longer that accurate.

        # define vars
        self.UPM: float = 730.
        self.set_peak_heating(peak_heating)
        self.set_peak_cooling(peak_cooling)
        self.set_base_load_cooling(base_load_cooling)  # defines the imbalance
        self.set_base_load_heating(base_load_heating)

        self.simulationPeriod = simulation_period

        self.costInvestment = None
        self.set_investment_cost(investment_cost)

        # set length of the peak
        self.set_length_peak()

        self.set_number_of_boreholes(number_of_boreholes)

        self.bore_field = None
        self.set_bore_field(bore_field)

        self.custom_g_function = None
        self.set_custom_g_function(custom_g_function)
        self.combo: list = []

    @staticmethod
    def configuration_string(n_1: int, n_2: int):
        """This functions returns the filename for the given configuration N_1, N_2."""
        string: str = str(max(n_1, n_2)) + "x" + str(min(n_1, n_2))
        return string

    def set_number_of_boreholes(self, number_of_boreholes: int = 0):
        """This functions sets the number of boreholes"""
        self.numberOfBoreholes = self.N_1 * self.N_2 if number_of_boreholes == 0 else number_of_boreholes

    def set_bore_field(self, bore_field=None):
        """
        This function sets the bore field configuration. When no input, an empty array of length N_1 * N_2 will be made
        """
        if bore_field is None:
            return
        self.bore_field = bore_field
        self.set_number_of_boreholes(len(bore_field))

    def set_custom_g_function(self, custom_g_function):
        """This functions sets the custom g-function."""
        self.custom_g_function = custom_g_function
        self.g_function_Interpolation_Array: list = []

    def set_investment_cost(self, investment_cost: list = None):
        """This function sets the investment cost. This is linear with respect to the total field length."""
        self.costInvestment: list = self.defaultInvestement if investment_cost is None else investment_cost

    def set_length_peak(self, length: float = None):
        """This function sets the length of the peak to length."""
        self.lengthPeak: float = self.defaultLengthPeak if length is None else length
        self.set_time_constants()

    def set_time_constants(self):
        # Number of segments per borehole
        self.th: float = self.lengthPeak * 3600.  # length of peak in seconds
        self.ty: float = self.simulationPeriod * 8760. * 3600
        self.tm: float = self.UPM * 3600.
        self.td: float = self.lengthPeak * 3600.
        self.time: np.array = np.array([self.td, self.td + self.tm, self.ty + self.tm + self.td])

    def set_ground_parameters(self, data: Union[dict, GroundData]):
        """This function sets the relevant bore field characteristics."""
        if isinstance(data, GroundData):
            self.H: float = data.H  # Borehole length (m)
            self.B: float = data.B  # Borehole spacing (m)

            self.N_1: int = data.N_1
            self.N_2: int = data.N_2

            self.Rb: float = data.Rb

            # Ground properties
            self.k_s: float = data.k_s  # Ground thermal conductivity (W/m.K)
            self.Tg: float = data.Tg  # Ground temperature at infinity (C)
            # sets the number of boreholes as if it was a rectangular field, iff there is not yet a number of
            # boreholes defined by a custom configuration
            self.set_number_of_boreholes(self.N_1 * self.N_2)
            return

        # backup for backwards compatibility
        self.H: float = data["H"]  # Borehole length (m)
        self.B: float = data["B"]  # Borehole spacing (m)

        self.N_1: int = data["N_1"]
        self.N_2: int = data["N_2"]

        self.Rb: float = data["Rb"]

        # Ground properties
        self.k_s: float = data["k_s"]  # Ground thermal conductivity (W/m.K)
        self.Tg: float = data["Tg"]  # Ground temperature at infinity (C)
        self.set_number_of_boreholes()

    def set_max_ground_temperature(self, temp: float):
        """This function sets the maximal ground temperature to temp"""
        self.Tf_H: float = temp

    def set_min_ground_temperature(self, temp: float):
        """This function sets the minimal ground temperature to temp"""
        self.Tf_C: float = temp

    @property
    def _bernier(self):
        """This function sizes the field based on the last year of operation, i.e. quadrants 2 and 4."""

        # initiate iteration
        h_prev = 0

        self.H = 50 if self.H < 1 else self.H

        # Iterates as long as there is no convergence
        # (convergence if difference between depth in iterations is smaller than threshold borehole depth)
        while abs(self.H - h_prev) >= self.thresholdBorholeDepth:
            # calculate the required g function values
            gfunc_uniform_t = self.g_function(self.time, self.H)

            # calculate the thermal resistances
            r_a = (gfunc_uniform_t[2] - gfunc_uniform_t[1]) / (2 * pi * self.k_s)
            r_m = (gfunc_uniform_t[1] - gfunc_uniform_t[0]) / (2 * pi * self.k_s)
            r_d = (gfunc_uniform_t[0]) / (2 * pi * self.k_s)

            # calculate the totale borehole length
            l = (self.qa * r_a + self.qm * r_m + self.qh * r_d + self.qh * self.Rb) / abs(self.T_f - self.Tg)

            # updating the depth values
            h_prev = self.H
            self.H = l / self.numberOfBoreholes

        return self.H

    @property
    def _carcel(self):
        """This function sizes the field based on the first year of operation, i.e. quadrants 1 and 3."""

        # initiate iteration
        h_prev: float = 0
        time_steps: np.array = np.array([self.th, self.th + self.tm, self.tcm + self.th])
        self.H: float = 50 if self.H < 1 else self.H

        # Iterates as long as there is no convergence
        # (convergence if difference between depth in iterations is smaller than thresholdBorholeDepth)
        while abs(self.H - h_prev) >= self.thresholdBorholeDepth:
            # get the g function values
            gfunc_uniform_t = self.g_function(time_steps, self.H)

            # calculate the thermal resistances
            r_pm = (gfunc_uniform_t[2] - gfunc_uniform_t[1]) / (2 * pi * self.k_s)
            r_cm = (gfunc_uniform_t[1] - gfunc_uniform_t[0]) / (2 * pi * self.k_s)
            r_h = (gfunc_uniform_t[0]) / (2 * pi * self.k_s)

            # calculate the total length
            l = (self.qh * self.Rb + self.qh * r_h + self.qm * r_cm + self.qpm * r_pm) / abs(self.T_f - self.Tg)

            # updating the depth values
            h_prev = self.H
            self.H = l / self.numberOfBoreholes
        return self.H

    def size_quadrant1(self):
        self.calculate_l3_params(False)  # calculate parameters
        return self._carcel  # size

    def size_quadrant2(self):
        self.calculate_l2_params(False)  # calculate parameters
        return self._bernier  # size

    def size_quadrant3(self):
        self.calculate_l3_params(True)  # calculate parameters
        return self._carcel  # size

    def size_quadrant4(self):
        self.calculate_l2_params(True)  # calculate parameters
        return self._bernier  # size

    def size(self, h_init: float) -> float:
        """
        This function sizes the bore field of the given configuration according to the methodology explained in
        (Peere et al., 2021). It returns the bore field depth.
        :param h_init: float: bore field depth [m] to start calculation with
        :return: float: bore field depth [m]
        """
        # initiate with a given depth
        self.H: float = h_init

        if self.imbalance <= 0:
            # extraction dominated, so quadrants 1 and 4 are relevant
            quadrant1 = self.size_quadrant1()
            quadrant4 = self.size_quadrant4()
            self.H = max(quadrant1, quadrant4)

            if self.H == quadrant1:
                self.limiting_quadrant = 1
            else:
                self.limiting_quadrant = 4
        else:
            # injection dominated, so quadrants 2 and 3 are relevant
            quadrant2 = self.size_quadrant2()
            quadrant3 = self.size_quadrant3()
            self.H = max(quadrant2, quadrant3)

            if self.H == quadrant2:
                self.limiting_quadrant = 2
            else:
                self.limiting_quadrant = 3

        # check if the field is not shallow
        if self.H < self.thresholdWarningShallowField and self.printing:
            print("The field has a calculated depth of ", str(round(self.H, 2)),
                  " m which is lower than the proposed minimum of ", str(self.thresholdWarningShallowField), " m.")
            print("Please change your configuration accordingly to have a not so shallow field.")

        return self.H

    def calculate_monthly_load(self):
        """This function calculates the average monthly load in kW"""
        self.monthlyLoad = [(-self.base_load_heating[i] + self.base_load_cooling[i]) / self.UPM for i in range(12)]

    def set_base_load_heating(self, base_load: list):
        """This function defines the base load in heating both in an energy as in an average power perspective"""
        self.base_load_heating = [i if i >= 0 else 0 for i in base_load]  # kWh
        self.monthlyLoadHeating = list(map(lambda x: x / self.UPM, self.base_load_heating))  # kW
        self.calculate_monthly_load()
        self.calculate_imbalance()

        # new peak heating if base load is larger than the peak
        self.set_peak_heating([max(self.peakHeating[i], self.monthlyLoadHeating[i]) for i in range(12)])

    def set_base_load_cooling(self, base_load: list):
        """This function defines the base load in cooling both in an energy as in an average power perspective"""
        self.base_load_cooling = [i if i >= 0 else 0 for i in base_load]  # kWh
        self.monthlyLoadCooling = list(map(lambda x: x / self.UPM, self.base_load_cooling))  # kW
        self.calculate_monthly_load()
        self.calculate_imbalance()

        # new peak cooling if base load is larger than the peak
        self.set_peak_cooling([max(self.peakCooling[i], self.monthlyLoadCooling[i]) for i in range(12)])

    def set_peak_heating(self, peak_load: list):
        """This function sets the peak heating to peak load"""
        self.peakHeating = [i if i >= 0 else 0 for i in peak_load]

    def set_peak_cooling(self, peak_load: list):
        """This function sets the peak cooling to peak load"""
        self.peakCooling = [i if i >= 0 else 0 for i in peak_load]

    @property
    def calculate_investment_cost(self):
        """
        This function calculates the investment cost based on a cost profile linear to the total borehole length.
        """
        return np.polyval(self.costInvestment, self.H * self.numberOfBoreholes)

    def calculate_imbalance(self):
        """This function calculates the imbalance of the field.
        A positive imbalance means that the field is injection dominated, i.e. it heats up every year."""
        self.imbalance = functools.reduce(lambda x, y: x + y, self.base_load_cooling) - functools.reduce(
            lambda x, y: x + y, self.base_load_heating)

    def calculate_l2_params(self, hc: bool):
        """This function calculates the parameters for the sizing based on the last year of operation"""

        # convert imbalance to Watt
        self.qa = self.imbalance / 8760. * 1000

        if hc:
            # limited by extraction load

            # temperature limit is set to the minimum temperature
            self.T_f = self.Tf_C

            # Select month with the highest peak load and take both the peak and average load from that month
            month_index = self.peakHeating.index(max(self.peakHeating))
            self.qm = self.monthlyLoad[month_index] * 1000.
            self.qh = max(self.peakHeating) * 1000.

            # correct signs
            self.qm = -self.qm
            self.qa = -self.qa

        else:
            # limited by injection load

            # temperature limit set to maximum temperature
            self.T_f = self.Tf_H

            # Select month with the highest peak load and take both the peak and average load from that month
            month_index = self.peakCooling.index(max(self.peakCooling))
            self.qm = self.monthlyLoad[month_index] * 1000.
            self.qh = max(self.peakCooling) * 1000.

    def calculate_l3_params(self, hc: bool, month_index: int = None):
        """This function calculates the parameters for the sizing based on the first year of operation"""

        if hc:
            # limited by extraction load

            # temperature limit is set to the minimum temperature
            self.T_f = self.Tf_C

            # Select month with the highest peak load and take both the peak and average load from that month
            month_index = self.peakHeating.index(max(self.peakHeating)) if month_index is None else month_index
            self.qh = max(self.peakHeating) * 1000.

            self.qm = self.monthlyLoad[month_index] * 1000.

            if month_index < 1:
                self.qpm = 0
            else:
                self.qpm = functools.reduce(lambda x, y: x + y, self.monthlyLoad[:month_index]) * 1000. / (
                        month_index + 1)

            self.qm = -self.qm
        else:
            # limited by injection

            # temperature limit set to maximum temperature
            self.T_f = self.Tf_H

            # Select month with the highest peak load and take both the peak and average load from that month
            month_index = self.peakCooling.index(max(self.peakCooling)) if month_index is None else month_index
            self.qh = max(self.peakCooling) * 1000.

            self.qm = self.monthlyLoad[month_index] * 1000.
            if month_index < 1:
                self.qpm = 0
            else:
                self.qpm = functools.reduce(lambda x, y: x + y, self.monthlyLoad[:month_index]) * 1000. / (
                        month_index + 1)
        self.tcm = (month_index + 1) * self.UPM * 3600
        self.tpm = month_index * self.UPM * 3600

        return month_index

    def calculate_temperatures(self, depth: float = None):
        """
        Calculate all the temperatures without plotting the figure. When depth is given, it calculates it for a given
        depth.
        """
        self._print_temperature_profile(figure=False, h=depth)

    def print_temperature_profile(self, legend: bool = True):
        """This function plots the temperature profile for the calculated depth."""
        self._print_temperature_profile(legend=legend)

    def print_temperature_profile_fixed_depth(self, depth: float, legend: bool = True):
        """This function plots the temperature profile for a fixed depth depth."""
        self._print_temperature_profile(legend=legend, h=depth)

    def _print_temperature_profile(self, legend: bool = True, h: float = None, figure: bool = True):
        """
        This function would calculate a new length of the bore field using temporal superposition.
        Now it justs outputs the temperature graphs
        """

        # making a numpy array of the monthly balance (self.montlyLoad) for a period of self.simulationPeriod years [kW]
        monthly_loads_array = np.asarray(self.monthlyLoad * self.simulationPeriod)

        # calculation of all the different times at which the g_function should be calculated.
        # this is equal to 'UPM' hours a month * 3600 seconds/hours for the simulationPeriod
        time_forg_values = [i * self.UPM * 3600. for i in range(1, 12 * self.simulationPeriod + 1)]

        # self.g_function is a function that uses the precalculated data to interpolate the correct values of the
        # g_function. This dataset is checked over and over again and is correct
        g_values = self.g_function(time_forg_values, self.H if h is None else h)

        # the g_function value of the peak with lengthPeak hours
        g_value_peak = self.g_function(self.lengthPeak * 3600., self.H if h is None else h)

        # calculation of needed differences of the g_function values. These are the weight factors in the calculation of
        # Tb.
        g_value_differences = [g_values[i] if i == 0 else g_values[i] - g_values[i - 1] for i in range(len(g_values))]

        self.factor_temperature_profile = g_value_differences
        results = []
        temp = []

        # calculation of the product for every month in order to obtain a temperature profile
        for i in range(len(monthly_loads_array)):
            temp.insert(0, monthly_loads_array[i] * 1000.)
            results.append(np.dot(temp, g_value_differences[:i + 1]))

        results_cooling = []
        results_heating = []
        results_peak_cooling = []
        results_peak_heating = []
        results_month_cooling = []
        results_month_heating = []

        # calculation the borehole wall temperature for every month i
        t_b = [i / (2 * pi * self.k_s) / ((self.H if h is None else h) * self.numberOfBoreholes) + self.Tg for i in
               results]
        self.Tb = t_b
        # now the Tf will be calculated based on
        # Tf = Tb + Q * R_b
        for i in range(12 * self.simulationPeriod):
            results_cooling.append(t_b[i] + self.monthlyLoadCooling[i % 12] * 1000. * (
                    self.Rb / self.numberOfBoreholes / (self.H if h is None else h)))
            results_heating.append(t_b[i] - self.monthlyLoadHeating[i % 12] * 1000. * (
                    self.Rb / self.numberOfBoreholes / (self.H if h is None else h)))
            results_month_cooling.append(t_b[i] + self.monthlyLoadCooling[i % 12] * 1000. * (
                    self.Rb / self.numberOfBoreholes / (self.H if h is None else h)))
            results_month_heating.append(t_b[i] - self.monthlyLoadHeating[i % 12] * 1000. * (
                    self.Rb / self.numberOfBoreholes / (self.H if h is None else h)))

        # extra summation if the g-function value for the peak is included

        for i in range(12 * self.simulationPeriod):
            results_peak_cooling.append(
                results_cooling[i] + ((self.peakCooling[i % 12] - self.monthlyLoadCooling[i % 12] if
                                      self.peakCooling[i % 12] > self.monthlyLoadCooling[
                                          i % 12] else 0) * 1000. * (
                        g_value_peak[0] / self.k_s / 2 / pi + self.Rb)) / self.numberOfBoreholes / (
                    self.H if h is None else h))
            results_peak_heating.append(
                results_heating[i] - ((self.peakHeating[i % 12] - self.monthlyLoadHeating[i % 12] if
                                      self.peakHeating[i % 12] > self.monthlyLoadHeating[
                                          i % 12] else 0) * 1000. * (
                        g_value_peak[0] / self.k_s / 2 / pi + self.Rb)) / self.numberOfBoreholes / (
                    self.H if h is None else h))

        # save temperatures under variable
        self.resultsCooling: list = results_cooling
        self.resultsHeating: list = results_heating
        self.resultsPeakHeating: list = results_peak_heating
        self.resultsPeakCooling: list = results_peak_cooling
        self.resultsMonthCooling: list = results_month_cooling
        self.resultsMonthHeating: list = results_month_heating

        # initiate figure
        if figure:
            # make a time array
            time_array = [i / 12 / 730. / 3600. for i in time_forg_values]

            plt.rc('figure')
            fig = plt.figure()

            ax1 = fig.add_subplot(111)
            ax1.set_xlabel(r'Time (year)')
            ax1.set_ylabel(r'Temperature ($^\circ C$)')

            # plot Temperatures
            ax1.step(time_array, t_b, 'k-', where="pre", lw=1.5, label="Tb")
            ax1.step(time_array, results_peak_cooling, 'b-', where="pre", lw=1.5, label='Tf peak cooling')
            ax1.step(time_array, results_peak_heating, 'r-', where="pre", lw=1.5, label='Tf peak heating')

            # define temperature bounds
            ax1.step(time_array, results_month_cooling, color='b', linestyle="dashed", where="pre", lw=1.5,
                     label='Tf base cooling')
            ax1.step(time_array, results_month_heating, color='r', linestyle="dashed", where="pre", lw=1.5,
                     label='Tf base heating')
            ax1.hlines(self.Tf_C, 0, self.simulationPeriod, colors='r', linestyles='dashed', label='', lw=1)
            ax1.hlines(self.Tf_H, 0, self.simulationPeriod, colors='b', linestyles='dashed', label='', lw=1)
            ax1.set_xticks(range(0, self.simulationPeriod + 1, 2))

            # Plot legend
            if legend:
                ax1.legend()
            ax1.set_xlim(left=0, right=self.simulationPeriod)
            plt.show()

    # if no interpolation array exists, it creates one
    def make_interpolation_list_default(self, data, time):
        """This function creates an interpolation list and saves it under gfunctionInterpolationArray."""

        b_array = list(data.keys())
        ks_array = list(data[b_array[0]].keys())
        h_array = list(data[b_array[0]][ks_array[0]].keys())
        self.H_max = max(h_array)
        b_array.sort()
        ks_array.sort()
        h_array.sort()

        points: tuple = (b_array, ks_array, h_array, time)

        values: list = [[[data[B][ks][i] for i in h_array] for ks in ks_array] for B in b_array]
        self.g_function_Interpolation_Array = points, values

    def make_interpolation_list_custom(self, data, time):
        """
        This function creates an interpolation list from a custom dataset and saves it under
        g-function Interpolation Array.
        """
        h_array = list(data["Data"].keys())
        h_array.sort()
        points = (h_array, time)
        values = [data["Data"][i] for i in h_array]
        self.g_function_Interpolation_Array = points, values

    def g_function(self, time_value: np.array, h: float):
        """This function calculated the g_function based on interpolation of the precalculated data."""

        if self.GUI:
            if self.custom_g_function is None:
                max_n = max(self.N_1, self.N_2)
                min_n = min(self.N_1, self.N_2)
                data_file = f'Data.data_{max_n}x{min_n}'
                from importlib import import_module as im
                data_module = im(data_file)
                data = data_module.data
            else:
                name = f'{FOLDER}/Data/{self.custom_g_function}.pickle'

                # check if datafile exists
                if not os.path.isfile(name):
                    print(name)
                    raise Exception('There is no precalculated data available. Please use the createCustomDatafile.')

                # load data file
                data = pickle.load(open(name, "rb"), encoding='latin1')

        else:
            # get the name of the data file
            if self.custom_g_function is None:
                name = self.configuration_string(self.N_1, self.N_2) + ".pickle"
            else:
                name = self.custom_g_function + ".pickle"
            # check if datafile exists
            if not os.path.isfile(FOLDER + "/Data/" + name):
                print(name)
                raise Exception('There is no precalculated data available. Please use the createCustomDatafile.')
            # load data file
            data = pickle.load(open(FOLDER + "/Data/" + name, "rb"), encoding='latin1')

        # remove the time value
        time_array = self.defaultTimeArray
        try:
            data.pop("Time")
        except KeyError:
            data = data

        if not self.g_function_Interpolation_Array:
            if self.custom_g_function is None:
                self.make_interpolation_list_default(data, time_array)
            else:
                self.make_interpolation_list_custom(data, time_array)
        try:
            points, values = self.g_function_Interpolation_Array
            if self.custom_g_function is None:
                # interpolate
                if not isinstance(time_value, float):
                    # multiple values are requested
                    gvalue = interpolate.interpn(points, values,
                                                 np.array([[self.B, self.k_s, h, t] for t in time_value]), 'linear',
                                                 bounds_error=False, fill_value=np.nan)
                else:
                    # only one value is requested
                    gvalue = interpolate.interpn(points, values, np.array([self.B, self.k_s, h, time_value]), 'linear',
                                                 bounds_error=False, fill_value=np.nan)
            else:
                # interpolate
                if not isinstance(time_value, float):
                    # multiple values are requested
                    gvalue = interpolate.interpn(points, values, np.array([[h, t] for t in time_value]), 'linear',
                                                 bounds_error=False, fill_value=np.nan)
                else:
                    # only one value is requested
                    gvalue = interpolate.interpn(points, values, np.array([h, time_value]), 'linear',
                                                 bounds_error=False, fill_value=np.nan)
            return gvalue
        except ValueError:
            if self.printing:
                if self.simulationPeriod > self.maxSimulationPeriod:
                    print("Your requested simulationperiod of " + str(
                        self.simulationPeriod) + " years is beyond the limit of " + str(
                        self.maxSimulationPeriod) + " years of the precalculated data.")
                else:
                    print("Your requested depth of " + str(h) + "m is beyond the limit " + str(
                        self.H_max) + "m of the precalculated data.")
                    print("Please change your borefield configuration accordingly.")
                print("-------------------------")
                print("This calculation stopped.")
            raise ValueError

    def create_custom_dataset(self, custom_bore_field: str, name_datafile: str, n_segments: int = 12,
                              time_array: list = None, depth_array: list = None):
        """This function makes a datafile for a given custom borefield."""
        time_array = self.defaultTimeArray if time_array is None else time_array
        depth_array = self.defaultDepthArray if depth_array is None else depth_array
        # make filename
        name = name_datafile + ".pickle"
        # check if file exists
        if not os.path.isfile("Data/" + name):
            # does not exist, so create
            pickle.dump(dict([]), open(FOLDER + "/Data/" + name, "wb"))
        else:
            raise Exception("The dataset " + name + " already exists. Please chose a different name.")

        data = pickle.load(open(FOLDER + "/Data/" + name, "rb"), encoding='latin1')

        # see if k_s exists
        data["Data"] = dict([])

        data["Time"] = time_array

        for H in depth_array:
            print("Start H: ", H)

            # Calculate the g-function for uniform borehole wall temperature
            alpha = self.k_s / (2.4 * 10 ** 6)

            # set borehole depth in borefield
            for borehole in custom_bore_field:
                borehole.H = H

            gfunc_uniform_t = gt.gfunction.uniform_temperature(
                custom_bore_field, time_array, alpha, nSegments=n_segments, disp=True)

            data["Data"][H] = gfunc_uniform_t

        self.set_custom_g_function(name_datafile)
        print("A new dataset with name " + name + " has been created in " + os.path.dirname(
            os.path.realpath(__file__)) + "\Data.")
        pickle.dump(data, open(FOLDER + "/Data/" + name, "wb"))

    def load_hourly_profile(self):
        """
        This function loads in an hourly load profile. It opens a csv and asks for the relevant column where the data
        is in.
        """

        # give the location of the file
        file_path = filedialog.askopenfilename(title="Select csv-file with hourly load.")

        # workbook object is created
        wb_obj = openpyxl.load_workbook(file_path)

        sheet_obj = wb_obj.active
        max_row = sheet_obj.max_row

        # Loop will create lists with the hourly loads
        for i in range(2, max_row + 1):
            cell_obj = sheet_obj.cell(row=i, column=1)
            self.hourlyHeatingLoad.append(cell_obj.value)
        for i in range(2, max_row + 1):
            cell_obj = sheet_obj.cell(row=i, column=2)
            self.hourlyCoolingLoad.append(cell_obj.value)

    def optimise_load_profile(self, depth: float = 150):
        """This function optimises the load based on the given bore field and the given hourly load."""

        def reduce_to_month_load(load: list, peak: float):
            """This function calculates the monthly load based, taking a maximum peak value into account."""
            month_load = []
            for i in range(12):
                temp = load[self.hourlyLoadArray[i]:self.hourlyLoadArray[i + 1] + 1]
                month_load.append(functools.reduce(lambda x, y: x + y, [min(j, peak) for j in temp]))
            return month_load

        def reduce_to_peak_load(load: list, peak: float):
            """This function calculates the monthly peak load, taking a maximum peak value into account."""
            peak_load = []
            for i in range(12):
                temp = load[self.hourlyLoadArray[i]:self.hourlyLoadArray[i + 1] + 1]
                peak_load.append(max([min(j, peak) for j in temp]))
            return peak_load

        # if no hourly profile is given, load one
        if not self.hourlyCoolingLoad:
            self.load_hourly_profile()

        # set initial peak loads
        init_peak_heat_load = max(self.hourlyHeatingLoad)
        init_peak_cool_load = max(self.hourlyCoolingLoad)

        # peak loads for iteration
        peak_heat_load = init_peak_heat_load
        peak_cool_load = init_peak_cool_load

        # set iteration criteria
        cool_ok, heat_ok = False, False

        while not cool_ok or not heat_ok:
            # calculate peak and base loads
            self.set_peak_cooling(reduce_to_peak_load(self.hourlyCoolingLoad, peak_cool_load))
            self.set_peak_heating(reduce_to_peak_load(self.hourlyHeatingLoad, peak_heat_load))
            self.set_base_load_cooling(reduce_to_month_load(self.hourlyCoolingLoad, peak_cool_load))
            self.set_base_load_heating(reduce_to_month_load(self.hourlyHeatingLoad, peak_heat_load))

            # calculate temperature profile, just for the results
            self._print_temperature_profile(legend=False, h=depth, figure=False)

            # deviation from minimum temperature
            if abs(min(self.resultsPeakHeating) - self.Tf_C) > 0.05:

                # check if it goes below the threshold
                if min(self.resultsPeakHeating) < self.Tf_C:
                    peak_heat_load -= 1 * max(1, 10 * (self.Tf_C - min(self.resultsPeakHeating)))
                else:
                    peak_heat_load = min(init_peak_heat_load, peak_heat_load + 1)
                    if peak_heat_load == init_peak_heat_load:
                        heat_ok = True
            else:
                heat_ok = True

            # deviation from maximum temperature
            if abs(max(self.resultsPeakCooling) - self.Tf_H) > 0.05:

                # check if it goes above the threshold
                if max(self.resultsPeakCooling) > self.Tf_H:
                    peak_cool_load -= 1 * max(1, 10 * (-self.Tf_H + max(self.resultsPeakCooling)))
                else:
                    peak_cool_load = min(init_peak_cool_load, peak_cool_load + 1)
                    if peak_cool_load == init_peak_cool_load:
                        cool_ok = True
            else:
                cool_ok = True

        # print results
        print("The peak load heating is: ", int(peak_heat_load), "kW, leading to ",
              int(functools.reduce(lambda x, y: x + y, self.base_load_heating)), "kWh of heating.")
        print("The peak load cooling is: ", int(peak_cool_load), "kW, leading to ",
              int(functools.reduce(lambda x, y: x + y, self.peakCooling)), "kWh of cooling.")

        # plot results
        self._print_temperature_profile(h=depth)

    def size_complete_field_robust(self, h_max: float, l_1: float, l_2: float, b_min: float = 3.0, b_max: float = 9.0) \
            -> list:
        l_2_bigger_then_l_1: bool = l_2 > l_1
        (l_1, l_2) = (l_2, l_1) if l_2_bigger_then_l_1 else (l_1, l_2)
        n_n_max_start: int = 20 * 20
        n_n_max: int = n_n_max_start
        combo_start: list = [[20, 20, 9]]
        combo = combo_start
        self.printing: bool = False
        product_min = 0
        for B in np.arange(b_max, b_min * 0.99999, -0.5):
            n_1_max = min(int(l_1 / B), 20)
            n_2_max = min(int(l_2 / B), 20)
            for N_1 in range(n_1_max, 0, -1):
                for N_2 in range(min(n_2_max, N_1), 0, -1):
                    self.N_1 = N_1
                    self.N_2 = N_2
                    self.B = B
                    product = N_1 * N_2
                    if product > n_n_max:
                        continue
                    if product < product_min:
                        break
                    self.set_number_of_boreholes(product)
                    try:
                        self.g_function_Interpolation_Array = []
                        depth = self.size(h_max)
                    except ValueError:
                        product_min = product
                        break
                    if depth > h_max:
                        break
                    if product < n_n_max:
                        n_n_max = product
                        combo = [[N_1, N_2, B, self.H]]
                    elif product == n_n_max:
                        combo.append([self.N_1, self.N_2, B, self.H])
        if n_n_max == n_n_max_start:
            return [[0, 0, 0, 0]]
        self.N_1 = combo[0][1] if l_2_bigger_then_l_1 else combo[0][0]
        self.N_2 = combo[0][0] if l_2_bigger_then_l_1 else combo[0][1]
        self.B = combo[0][2]
        if l_2_bigger_then_l_1:
            for i in combo:
                i[0], i[1] = i[1], i[0]
        self.set_number_of_boreholes(self.N_1 * self.N_2)
        self.g_function_Interpolation_Array = []
        self.H = self.size(h_max)
        self.printing: bool = True
        self.combo = combo
        return combo

    def size_complete_field_fast(self, h_max: float, l_1: float, l_2: float, b_min: float = 3.0, b_max: float = 9.0) \
            -> list:
        l_2_bigger_then_l_1: bool = l_2 > l_1
        (l_1, l_2) = (l_2, l_1) if l_2_bigger_then_l_1 else (l_1, l_2)
        n_n_max_start: int = 20 * 20
        n_n_max: int = n_n_max_start
        combo_start: list = [[20, 20, 9, h_max]]
        combo = combo_start
        self.printing: bool = False
        for B in np.arange(b_max, b_min * 0.99999, -0.5):
            n_1_max = min(int(l_1 / B), 20)
            n_2_max = min(int(l_2 / B), 20)
            self._reset_for_sizing(n_1_max, n_2_max)
            self.N_1 = n_1_max
            self.B = B
            product_old = self.N_1 * self.N_2
            try:
                depth = self.size(h_max)
                number_of_boreholes = int(depth * product_old / h_max) + 1
                res = self._calc_number_of_holes(number_of_boreholes, n_1_max, n_2_max)
                self._reset_for_sizing(res[0][0], res[0][1])
                product_new = self.N_1 * self.N_2
                counter = 0
                from numpy import sign
                while product_old != product_new:
                    gradient = int(0.51 * (product_new - product_old)) if counter > 4 else int(product_new -
                                                                                               product_old)
                    product_new = product_old + sign(gradient) * min(abs(gradient), 1)
                    depth = self.size(h_max)
                    number_of_boreholes = int(depth * product_new / h_max) + 1
                    res = self._calc_number_of_holes(number_of_boreholes, n_1_max, n_2_max)
                    self._reset_for_sizing(res[0][0], res[0][1])
                    product_old = self.N_1 * self.N_2
                    counter += 1
                    if counter > 20 and depth < h_max:
                        break
                if product_new < n_n_max:
                    n_n_max = product_new
                    if len(res) > 1:
                        combo: list = []
                        first: bool = True
                        for i in res:
                            if first:
                                combo.append([i[0], i[1], B, self.H])
                                first = False
                                continue
                            self._reset_for_sizing(i[0], i[1])
                            self.size(h_max)
                            if self.H < h_max:
                                combo.append([i[0], i[1], B, self.H])
                    else:
                        combo = [[res[0][0], res[0][1], B, self.H]]
                elif product_new == n_n_max:
                    if len(res) > 1:
                        first: bool = True
                        for i in res:
                            if first:
                                combo.append([i[0], i[1], B, self.H])
                                first = False
                                continue
                            self._reset_for_sizing(i[0], i[1])
                            self.size(h_max)
                            if self.H < h_max:
                                combo.append([i[0], i[1], B, self.H])
                    else:
                        combo += [[res[0][0], res[0][1], B, self.H]]

            except ValueError:
                break

        if n_n_max == n_n_max_start:
            return [[0, 0, 0, 0]]
        self.N_1 = combo[0][1] if l_2_bigger_then_l_1 else combo[0][0]
        self.N_2 = combo[0][0] if l_2_bigger_then_l_1 else combo[0][1]
        self.B = combo[0][2]
        if l_2_bigger_then_l_1:
            for i in combo:
                i[0], i[1] = i[1], i[0]
        self.set_number_of_boreholes(self.N_1 * self.N_2)
        self.H = self.size(h_max)
        self.printing: bool = True
        self.combo = combo
        return combo

    def _reset_for_sizing(self, n_1: int, n_2: int) -> None:
        self.N_1, self.N_2 = n_1, n_2
        self.g_function_Interpolation_Array = []
        self.set_number_of_boreholes()

    @staticmethod
    def _calc_number_of_holes(n: int, n_1_max: int, n_2_max: int) -> list:
        res = [(20, 20)]
        max_val = 20 * 20
        for i in range(1, n_1_max + 1):
            for j in range(1, min(n_2_max, i) + 1):
                if n <= j * i < max_val:
                    res = [(i, j)]
                    max_val = i * j
                elif i * j == max_val:
                    res.append((i, j))

        return res
