from numpy import array as np_array, polyval as np_polyval, asarray as np_asarray, dot as np_dot
from pickle import load as pk_load, dump as pk_dump
from scipy.interpolate import interpn as interpolate_interpn
from math import pi
from pygfunction import load_aggregation as gt_load_aggregation, gfunction as gt_gfunction
from os.path import isfile as os_isfile
from os import getcwd as os_getcwd
from matplotlib.pyplot import rc as plt_rc, figure as plt_figure, show as plt_show
from functools import reduce as functools_reduce
from tkinter import filedialog
from openpyxl import load_workbook as openpyxl_load_workbook


def timeValues(years: int):
    """This function calculates the default time values for the gfunction."""
    dt = 3600.  # Time step (s)
    tmax = years * 8760. * 3600.  # Maximum time (s)

    # Load aggregation scheme
    LoadAgg = gt_load_aggregation.ClaessonJaved(dt, tmax)

    return LoadAgg.get_times_for_simulation()


def configurationString(N_1, N_2):
    """This functions returns the filename for the given configuration N_1, N_2."""
    string = str(max(N_1, N_2)) + "x" + str(min(N_1, N_2))
    return string


class GroundData:
    __slots__ = 'H', 'B', 'k_s', 'Tg', 'Rb', 'N_1', 'N_2'

    def __init__(self, H: float, B: float, k_s: float, Tg: float, Rb: float, N_1: int, N_2: int):
        self.H = H  # m
        self.B = B  # m
        self.k_s = k_s  # W/mK
        self.Tg = Tg  # °C
        self.Rb = Rb  # mK/W
        self.N_1 = N_1  # #
        self.N_2 = N_2  # #


class Borefield:
    __slots__ = 'baseloadHeating', 'baseloadCooling', 'H', 'H_init', 'B', 'N_1', 'N_2', 'Rb', 'k_s', 'Tg', 'ty', 'tm',\
                'td', 'time', 'UPM', 'thresholdBorholeDepth', 'defaultTimeArray', 'hourlyHeatingLoad', \
                'hourlyCoolingLoad', 'numberOfBoreholes', 'borefield', 'customGfunction', 'costInvestement', \
                'lengthPeak', 'th', 'Tf_H', 'Tf_C', 'limitingQuadrant', 'montlyLoad', 'monthlyLoadHeating', \
                'monthlyLoadCooling', 'peakHeating', 'imbalance', 'qa', 'Tf', 'qm', 'qh', 'qpm', 'tcm', 'tpm',\
                'gfunctionInterpolationArray', 'hourlyLoadArray', 'peakCooling', 'simulationPeriod', \
                'factoren_temperature_profile', 'resultsCooling', 'resultsHeating', 'resultsPeakHeating', \
                'resultsPeakCooling', 'resultsMonthCooling', 'resultsMonthHeating', 'Tb'

    def __init__(self, simulationPeriod: int, numberOfBoreholes: int = None, peakHeating: list = None,
                 peakCooling: list = None, baseloadHeating: list = None, baseloadCooling: list = None,
                 investementCost: list = None, borefield=None, customGfunction=None):
        """This function initiates the Borefield class"""

        # initiate vars
        listOfZeros = [0] * 12
        if baseloadCooling is None:
            baseloadCooling = listOfZeros
        if baseloadHeating is None:
            baseloadHeating = listOfZeros
        if peakCooling is None:
            peakCooling = listOfZeros
        if peakHeating is None:
            peakHeating = listOfZeros

        self.baseloadHeating = listOfZeros
        self.baseloadCooling = listOfZeros
        self.H: int = 0
        self.H_init: int = 0
        self.B: int = 0
        self.N_1: int = 0
        self.N_2: int = 0
        self.Rb: float = 0.0
        self.k_s: float = 0.0  # Ground thermal conductivity (W/m.K)
        self.Tg: float = 10.0  # Ground temperature at infinity (C)
        self.ty: float = 0.0
        self.tm: float = 0.0
        self.td: float = 0.0
        self.time: float = 0.0
        self.Tb: list = []
        self.UPM = 730.  # number of hours per month
        self.thresholdBorholeDepth = 0.05  # threshold for iteration
        self.defaultTimeArray = timeValues(simulationPeriod)  # sec

        self.hourlyHeatingLoad: list = []
        self.hourlyCoolingLoad: list = []
        self.numberOfBoreholes: int = 0
        self.borefield = None
        self.customGfunction = None
        self.costInvestement: list = []
        self.lengthPeak: float = 0.0
        self.th: float = 0.0
        self.Tf_H: float = 0.0
        self.Tf_C: float = 0.0
        self.limitingQuadrant: int = 0
        self.montlyLoad: list = []
        self.monthlyLoadHeating: list = []
        self.monthlyLoadCooling: list = []
        self.peakHeating: list = []
        self.peakCooling: list = []
        self.imbalance: float = 0.0
        self.qa: float = 0.0
        self.Tf: float = 0.0
        self.qm: float = 0.0
        self.qh: float = 0.0
        self.qpm: float = 0.0
        self.tcm: float = 0.0
        self.tpm: float = 0.0
        self.gfunctionInterpolationArray: list = []
        self.factoren_temperature_profile: list = []
        temp = 0
        self.hourlyLoadArray = []
        for i in [0, 24 * 31, 24 * 28, 24 * 31, 24 * 30, 24 * 31, 24 * 30, 24 * 31, 24 * 31, 24 * 30, 24 * 31, 24 * 30,
                  24 * 31]:
            temp += i
            self.hourlyLoadArray.append(temp)

        # define vars
        self.setPeakHeating(peakHeating)
        self.setPeakCooling(peakCooling)
        self.setBaseloadCooling(baseloadCooling)  # dit definieert ook imbalance etc
        self.setBaseloadHeating(baseloadHeating)

        self.simulationPeriod = simulationPeriod

        self.setInvestementCost(investementCost)

        # set length of the peak
        self.setLengthPeak()

        self.setNumberOfBoreholes(numberOfBoreholes)

        self.setBorefield(borefield)

        self.setCustomGfunction(customGfunction)

    def setNumberOfBoreholes(self, numberOfBoreholes: int):
        """This functions sets the number of boreholes"""
        self.numberOfBoreholes = numberOfBoreholes

    def setBorefield(self, borefield=None):
        """This function sets the borefield configuration. When no input, an empty array of length N_1 * N_2 will be
         made"""
        if borefield is None:
            return
        self.borefield = borefield
        self.setNumberOfBoreholes(len(borefield))

    def setCustomGfunction(self, customGfunction):
        """This functions sets the custom g-function."""
        self.customGfunction = customGfunction
        self.gfunctionInterpolationArray: list = []

    def setInvestementCost(self, investementCost: list = None):
        """This function sets the investement cost. This is linear with respect to the total field length."""
        if investementCost is None:
            investementCost = [35, 0]
        self.costInvestement = investementCost

    def setLengthPeak(self, length: float = None):
        if length is None:
            length: int = 6
        """This function sets the length of the peak to length."""
        self.lengthPeak = length
        self.th = length * 3600.  # length of peak in seconds

    def setGroundParameters(self, data: GroundData):
        """This function sets the relevant borefield characteristics."""

        self.H = data.H  # Borehole length (m)
        self.B = data.B  # Borehole spacing (m)

        self.N_1 = data.N_1
        self.N_2 = data.N_2

        self.Rb = data.Rb

        # Ground properties
        self.k_s = data.k_s  # Ground thermal conductivity (W/m.K)
        self.Tg = data.Tg    # Ground temperature at infinity (C)

        # Number of segments per borehole
        self.ty = self.simulationPeriod * 8760.*3600
        self.tm = self.UPM * 3600.
        self.td = 6*3600.
        self.time = np_array([self.td, self.td + self.tm, self.ty + self.tm + self.td])

        # sets the number of boreholes as if it was a rectangular field, iff there is not yet a number of boreholes
        # defined by a custom configuration
        if self.numberOfBoreholes is None:
            self.setNumberOfBoreholes(self.N_1*self.N_2)

    def setMaxGroundTemperature(self, temp: float):
        """This function sets the maximal ground temperature to temp"""
        self.Tf_H = temp

    def setMinGroundTemperature(self, temp: float):
        """This function sets the minimal ground temperature to temp"""
        self.Tf_C = temp

    @property
    def _Bernier(self):
        """This function sizes the field based on the last year of operation, i.e. quadrants 2 and 4."""

        # initiate iteration
        H_prev = 0

        if self.H < 1:
            self.H = 50

        # Iterates as long as there is no convergence
        # (convergence if difference between depth in iterations is smaller than thresholdBorholeDepth)
        while abs(self.H - H_prev) >= self.thresholdBorholeDepth:
            # calculate the required gfunction values
            gfunc_uniform_T = self.gfunction(self.time, self.H)

            # calculate the thermal resistances
            Ra = (gfunc_uniform_T[2] - gfunc_uniform_T[1]) / (2 * pi * self.k_s)
            Rm = (gfunc_uniform_T[1] - gfunc_uniform_T[0]) / (2 * pi * self.k_s)
            Rd = (gfunc_uniform_T[0]) / (2 * pi * self.k_s)

            # calculate the totale borehole length
            L = (self.qa * Ra + self.qm * Rm + self.qh * Rd + self.qh * self.Rb) / abs(self.Tf - self.Tg)

            # updating the depth values
            H_prev = self.H
            self.H = L / self.numberOfBoreholes

        return self.H

    @property
    def _Carcel(self):
        """This function sizes the field based on the first year of operation, i.e. quadrants 1 and 3."""

        # initiate iteration
        H_prev = 0
        timeSteps = np_array([self.th, self.th + self.tm, self.tcm + self.th])
        if self.H < 1:
            self.H = 50

        # Iterates as long as there is no convergence
        # (convergence if difference between depth in iterations is smaller than thresholdBorholeDepth)
        while abs(self.H - H_prev) >= self.thresholdBorholeDepth:
            # get the gfunction values
            gfunc_uniform_T = self.gfunction(timeSteps, self.H)

            # calculate the thermal resistances
            Rpm = (gfunc_uniform_T[2] - gfunc_uniform_T[1]) / (2 * pi * self.k_s)
            Rcm = (gfunc_uniform_T[1] - gfunc_uniform_T[0]) / (2 * pi * self.k_s)
            Rh = (gfunc_uniform_T[0]) / (2 * pi * self.k_s)

            # calculate the total length
            L = (self.qh * self.Rb + self.qh * Rh + self.qm * Rcm + self.qpm * Rpm) / abs(self.Tf - self.Tg)

            # updating the depth values
            H_prev = self.H
            self.H = L / self.numberOfBoreholes

        return self.H

    def sizeQuadrant1(self):
        self.calculateL3Params(False)  # calculate parameters
        return self._Carcel  # size

    def sizeQuadrant2(self):
        self.calculateL2Params(False)  # calculate parameters
        self.qa = self.qa
        return self._Bernier  # size

    def sizeQuadrant3(self):
        self.calculateL3Params(True)  # calculate parameters
        return self._Carcel  # size

    def sizeQuadrant4(self):
        self.calculateL2Params(True)  # calculate parameters
        self.qa = self.qa
        return self._Bernier  # size

    def size(self, H_init):

        """This function sizes the borefield of the given configuration according to the methodology explained in
        (Peere et al., 2021). It returns the borefield depth."""

        # initiate with a given depth
        self.H_init = H_init

        if self.imbalance <= 0:
            # extraction dominated, so quadrants 1 and 4 are relevant
            quadrant1 = self.sizeQuadrant1()
            quadrant4 = self.sizeQuadrant4()
            self.H = max(quadrant1, quadrant4)

            if self.H == quadrant1:
                self.limitingQuadrant = 1
                return self.H
            self.limitingQuadrant = 4
            return self.H
        # injection dominated, so quadrants 2 and 3 are relevant
        quadrant2 = self.sizeQuadrant2()
        quadrant3 = self.sizeQuadrant3()
        self.H = max(quadrant2, quadrant3)

        if self.H == quadrant2:
            self.limitingQuadrant = 2
            return self.H
        self.limitingQuadrant = 3
        return self.H

    def calculateMonthlyLoad(self):
        """This function calculates the average monthly load in kW"""
        self.montlyLoad = [(-self.baseloadHeating[i] + self.baseloadCooling[i]) / self.UPM for i in range(12)]

    def setBaseloadHeating(self, baseload: list):
        """This function defines the baseload in heating both in an energy as in an average power perspective"""
        self.baseloadHeating = [i if i >= 0 else 0 for i in baseload]  # kWh
        self.monthlyLoadHeating = list(map(lambda x: x / self.UPM, self.baseloadHeating))  # kW
        self.calculateMonthlyLoad()
        self.calculateImbalance()

        # new peak heating if baseload is larger than the peak
        self.setPeakHeating([max(self.peakHeating[i], self.monthlyLoadHeating[i]) for i in range(12)])

    def setBaseloadCooling(self, baseload: list):
        """This function defines the baseload in cooling both in an energy as in an average power perspective"""
        self.baseloadCooling = [i if i >= 0 else 0 for i in baseload]  # kWh
        self.monthlyLoadCooling = list(map(lambda x: x / self.UPM, self.baseloadCooling))  # kW
        self.calculateMonthlyLoad()
        self.calculateImbalance()

        # new peak cooling if baseload is larger than the peak
        self.setPeakCooling([max(self.peakCooling[i], self.monthlyLoadCooling[i]) for i in range(12)])

    def setPeakHeating(self, peakload: list):
        """This function sets the peak heating to peakload"""
        self.peakHeating = [i if i >= 0 else 0 for i in peakload]

    def setPeakCooling(self, peakload: list):
        """This function sets the peak cooling to peak load"""
        self.peakCooling = [i if i >= 0 else 0 for i in peakload]

    @property
    def investementCost(self):
        """This function calculates the investement cost based on a cost profile lineair to the total borehole
        length."""
        return np_polyval(self.costInvestement, self.H * self.numberOfBoreholes)

    def calculateImbalance(self):
        """This function calculates the imbalance of the field.
        A positive imbalance means that the field is injection dominated, i.e. it heats up every year."""
        self.imbalance = functools_reduce(lambda x, y: x + y, self.baseloadCooling) - functools_reduce(
            lambda x, y: x + y, self.baseloadHeating)

    def calculateL2Params(self, HC: bool):
        """This function calculates the parameters for the sizing based on the last year of operation"""

        # convert imbalance to Watt
        self.qa = self.imbalance / 8760. * 1000

        if HC:
            # limited by extraction load

            # temperature limit is set to the minimum temperature
            self.Tf = self.Tf_C

            # Select month with highest peak load and take both the peak and average load from that month
            monthIndex = self.peakHeating.index(max(self.peakHeating))
            self.qm = self.montlyLoad[monthIndex] * 1000.
            self.qh = max(self.peakHeating) * 1000.

            # correct signs
            self.qm = -self.qm
            self.qa = -self.qa
            return
        # limited by injection load

        # temperature limit set to maximum temperature
        self.Tf = self.Tf_H

        # Select month with highest peak load and take both the peak and average load from that month
        monthIndex = self.peakCooling.index(max(self.peakCooling))
        self.qm = self.montlyLoad[monthIndex] * 1000.
        self.qh = max(self.peakCooling) * 1000.

    def calculateL3Params(self, HC: bool, monthIndex: int = None):
        """This function calculates the parameters for the sizing based on the first year of operation"""

        if HC:
            # limited by extraction load

            # temperature limit is set to the minimum temperature
            self.Tf = self.Tf_C

            # Select month with highest peak load and take both the peak and average load from that month
            monthIndex = self.peakHeating.index(max(self.peakHeating)) if monthIndex is None else monthIndex
            self.qh = max(self.peakHeating) * 1000.

            self.qm = self.montlyLoad[monthIndex] * 1000.

            if monthIndex < 1:
                self.qpm = 0
            else:
                self.qpm = functools_reduce(lambda x, y: x + y, self.montlyLoad[:monthIndex]) * 1000. / (monthIndex + 1)

            self.qm = -self.qm
        else:
            # limited by injection

            # temperature limit set to maximum temperatue
            self.Tf = self.Tf_H

            # Select month with highest peak load and take both the peak and average load from that month
            monthIndex = self.peakCooling.index(max(self.peakCooling)) if monthIndex is None else monthIndex
            self.qh = max(self.peakCooling) * 1000.

            self.qm = self.montlyLoad[monthIndex] * 1000.
            if monthIndex < 1:
                self.qpm = 0
            else:
                self.qpm = functools_reduce(lambda x, y: x + y, self.montlyLoad[:monthIndex]) * 1000. / (monthIndex + 1)
        self.tcm = (monthIndex + 1) * self.UPM * 3600
        self.tpm = monthIndex * self.UPM * 3600

        return monthIndex

    def calculateTemperatures(self, depth: float = None):
        """Calculate all the temperatures without plotting the figure. When depth is given, it calculates it for a
        given depth."""
        self._printTemperatureProfile(figure=False, H=depth)

    def printTemperatureProfile(self, legend: bool = True):
        """This function plots the temperature profile for the calculated depth."""
        self._printTemperatureProfile(legend=legend)

    def printTemperatureProfileFixedDepth(self, depth: float, legend: bool = True):
        """This function plots the temperature profile for a fixed depth depth."""
        self._printTemperatureProfile(legend=legend, H=depth)

    def _printTemperatureProfile(self, legend: bool = True, H=None, figure=True):
        """
        This function would calculate a new length of the borefield using temporal superposition.
        Now it justs outputs the temperature graphs
        """

        # making a numpy array of the monthly balance (self.montlyLoad) for a period of 20 years [kW]
        monthlyLoadsArray = np_asarray(self.montlyLoad * self.simulationPeriod)

        # calculation of all the different times at which the gfunction should be calculated.
        # this is equal to 'UPM' hours a month * 3600 seconds/hours for the simulationPeriod
        timeForgValues = [i * self.UPM * 3600. for i in range(1, 12 * self.simulationPeriod + 1)]

        # self.gfunction is a function that uses the precalculated data to interpolate the correct values of the
        # gfunction.
        # this dataset is checked over and over again and is correct
        gValues = self.gfunction(timeForgValues, self.H if H is None else H)

        # the gfunction value of the peak with lengthPeak hours
        gValuePeak = self.gfunction(self.lengthPeak * 3600., self.H if H is None else H)

        # calculation of needed differences of the gfunction values. These are the weight factors in the calculation
        # of Tb.
        gValueDifferences = [gValues[i] if i == 0 else gValues[i] - gValues[i - 1] for i in range(len(gValues))]

        self.factoren_temperature_profile = gValueDifferences
        results: list = []
        temp: list = []

        # calculation of the product for every month in order to obtain a temperature profile
        for i in range(len(monthlyLoadsArray)):
            temp.insert(0, monthlyLoadsArray[i] * 1000.)
            results.append(np_dot(temp, gValueDifferences[:i + 1]))

        # calculation the borehole wall temperature for every month i
        Tb = [i / (2 * pi * self.k_s) / ((self.H if H is None else H) * self.numberOfBoreholes) + self.Tg for i
              in results]
        self.Tb = Tb
        # now the Tf will be calculated based on
        # Tf = Tb + Q * R_b
        ran_Simu = range(self.simulationPeriod*12)
        resultsCooling = [Tb[i] + self.monthlyLoadCooling[i % 12] * 1000. * (
                         self.Rb / self.numberOfBoreholes / (self.H if H is None else H)) for i in ran_Simu]
        resultsHeating = [Tb[i] - self.monthlyLoadHeating[i % 12] * 1000. * (
                        self.Rb / self.numberOfBoreholes / (self.H if H is None else H)) for i in ran_Simu]
        resultsMonthCooling = [Tb[i] + self.monthlyLoadCooling[i % 12] * 1000. * (
                        self.Rb / self.numberOfBoreholes / (self.H if H is None else H)) for i in ran_Simu]
        resultsMonthHeating = [Tb[i] - self.monthlyLoadHeating[i % 12] * 1000. * (
                        self.Rb / self.numberOfBoreholes / (self.H if H is None else H)) for i in ran_Simu]

        # extra sommation if the gfunction value for the peak is included
        resultsPeakCooling = [resultsCooling[i] + ((self.peakCooling[i % 12] - self.monthlyLoadCooling[i % 12] if
                                                    self.peakCooling[i % 12] > self.monthlyLoadCooling[i % 12]
                                                    else 0) * 1000. * (gValuePeak[0] / self.k_s / 2 / pi + self.Rb))
                              / self.numberOfBoreholes / (self.H if H is None else H) for i in ran_Simu]
        resultsPeakHeating = [resultsHeating[i] - ((self.peakHeating[i % 12] - self.monthlyLoadHeating[i % 12] if
                                                    self.peakHeating[i % 12] > self.monthlyLoadHeating[i % 12]
                                                    else 0) * 1000. * (gValuePeak[0] / self.k_s / 2 / pi + self.Rb)) /
                              self.numberOfBoreholes / (self.H if H is None else H) for i in ran_Simu]

        # save temperatures under variable
        self.resultsCooling = resultsCooling
        self.resultsHeating = resultsHeating
        self.resultsPeakHeating = resultsPeakHeating
        self.resultsPeakCooling = resultsPeakCooling
        self.resultsMonthCooling = resultsMonthCooling
        self.resultsMonthHeating = resultsMonthHeating

        # initiate figure
        if figure:
            # make a time array
            timeArray = [i / 12 / 730. / 3600. for i in timeForgValues]

            plt_rc('figure')
            fig = plt_figure()

            ax1 = fig.add_subplot(111)
            ax1.set_xlabel(r'Time (year)')
            ax1.set_ylabel(r'Temperature ($^\circ C$)')

            # plot Temperatures
            ax1.step(timeArray, Tb, 'k-', where="pre", lw=1.5, label="Tb")
            ax1.step(timeArray, resultsPeakCooling, 'b-', where="pre", lw=1.5, label='Tf peak cooling')
            ax1.step(timeArray, resultsPeakHeating, 'r-', where="pre", lw=1.5, label='Tf peak heating')

            # define temperature bounds
            ax1.step(timeArray, resultsMonthCooling, color='b', linestyle="dashed", where="pre", lw=1.5,
                     label='Tf base cooling')
            ax1.step(timeArray, resultsMonthHeating, color='r', linestyle="dashed", where="pre", lw=1.5,
                     label='Tf base heating')
            ax1.hlines(self.Tf_C, 0, 20, colors='r', linestyles='dashed', label='', lw=1)
            ax1.hlines(self.Tf_H, 0, 20, colors='b', linestyles='dashed', label='', lw=1)
            ax1.set_xticks(range(0, 21, 2))

            # Plot legend
            if legend:
                ax1.legend()
            ax1.set_xlim(left=0, right=20)
            plt_show()

    # if no interpolation array exists, it creates one
    def makeInterpolationListDefault(self, data, Time):
        """This function creates an interpolation list and saves it under gfunctionInterpolationArray."""

        B_array = list(data.keys())
        ks_array = list(data[B_array[0]].keys())
        H_array = list(data[B_array[0]][ks_array[0]].keys())
        B_array.sort()
        ks_array.sort()
        H_array.sort()

        points = (B_array, ks_array, H_array, Time)

        values = []
        for B in B_array:
            temp_ks = []
            for ks in ks_array:
                temp_H = []
                for H in H_array:
                    temp_H.append(data[B][ks][H])
                temp_ks.append(temp_H)
            values.append(temp_ks)
        self.gfunctionInterpolationArray = (points, values)

    def makeInterpolationListCustom(self, data, Time):
        """This function creates an interpolation list from a custom dataset and saves it under
        gfunctionInterpolationArray."""

        H_array = list(data["Data"].keys())
        H_array.sort()

        points = (H_array, Time)

        values = [data["Data"][i] for i in H_array]

        self.gfunctionInterpolationArray = (points, values)

    def gfunction(self, timeValue, H):
        """This function calculated the gfunction based on interpolation of the precalculated data."""

        # get the name of the data file
        if self.customGfunction is None:
            name = f'{configurationString(self.N_1, self.N_2)}.txt'
        else:
            name = self.customGfunction+".txt"

        # check if datafile exists
        if not os_isfile("Data/"+name):
            print(name)
            raise Exception('There is no precalculated data available. Please use the createCustomDatafile.')

        # load data file
        data = pk_load(open("Data/"+name, "rb"))

        # remove the time value
        Time = self.defaultTimeArray
        data.pop("Time")

        if not self.gfunctionInterpolationArray:

            if self.customGfunction is None:
                self.makeInterpolationListDefault(data, Time)
            else:
                self.makeInterpolationListCustom(data, Time)

        if self.customGfunction is None:
            # interpolate
            points, values = self.gfunctionInterpolationArray

            if not isinstance(timeValue, float):
                # multiple values are requested
                gvalue = interpolate_interpn(points, values, np_array([[self.B, self.k_s, H, t] for t in timeValue]))
                return gvalue
            # only one value is requested
            gvalue = interpolate_interpn(points, values, np_array([self.B, self.k_s, H, timeValue]))
            return gvalue
        # interpolate
        points, values = self.gfunctionInterpolationArray
        if not isinstance(timeValue, float):
            # multiple values are requested
            gvalue = interpolate_interpn(points, values, np_array([[H, t] for t in timeValue]))
            return gvalue
        # only one value is requested
        gvalue = interpolate_interpn(points, values, np_array([H, timeValue]))
        return gvalue

    def createCustomDataset(self, customBorefield: list, nameDatafile: str, nSegments: int = 12,
                            timeArray=None, depthArray=None):
        """This function makes a datafile for a given custom borefield."""
        if timeArray is None:
            timeArray = self.defaultTimeArray
        # make filename
        if depthArray is None:
            depthArray = [1]+list(range(25, 201, 25))  # m
        name = nameDatafile + ".txt"
        # check if file exists
        if not os_isfile("Data/"+name):
            # does not exist, so create
            pk_dump(dict([]), open("Data/"+name, "wb"))
        else:
            raise Exception("The dataset " + name + " already exists. Please chose a different name.")

        data = pk_load(open("Data/"+name, "rb"), encoding='latin1')

        # see if k_s exists
        data["Data"] = dict([])

        data["Time"] = timeArray

        for H in depthArray:
            print("Start H: ", H)

            # Calculate the g-function for uniform borehole wall temperature
            alpha = self.k_s / (2.4 * 10 ** 6)

            # set borehole depth in borefield
            for borehole in customBorefield:
                borehole.H = H

            gfunc_uniform_T = gt_gfunction.uniform_temperature(
                    customBorefield, timeArray, alpha, nSegments=nSegments, disp=True)

            data["Data"][H] = gfunc_uniform_T

        self.setCustomGfunction(name)
        print(f"A new dataset with name {name} has been created in {os_getcwd()}\Data.")
        pk_dump(data, open("Data/"+name, "wb"))

    def loadHourlyProfile(self):
        """This function loads in an hourly load profile. It opens a csv and asks for the relevant column where the
        data is in."""

        # give the location of the file
        filePath = filedialog.askopenfilename(title="Select csv-file with hourly load.")

        # workbook object is created
        wb_obj = openpyxl_load_workbook(filePath)

        sheet_obj = wb_obj.active
        max_row = sheet_obj.max_row

        # Loop will create lists with the hourly loads
        for i in range(2, max_row + 1):
            cell_obj = sheet_obj.cell(row=i, column=1)
            self.hourlyHeatingLoad.append(cell_obj.value)
        for i in range(2, max_row + 1):
            cell_obj = sheet_obj.cell(row=i, column=2)
            self.hourlyCoolingLoad.append(cell_obj.value)

    def reduceToMonthLoad(self, load: list, peak):
        """This function calculates the monthly load based, taking a maximum peak value into account."""
        monthLoad = []
        for i in range(12):
            temp = load[self.hourlyLoadArray[i]:self.hourlyLoadArray[i + 1] + 1]
            monthLoad.append(functools_reduce(lambda x, y: x + y, [min(j, peak) for j in temp]))
        return monthLoad

    def reduceToPeakLoad(self, load, peak):
        """This function calculates the monthly peak load, taking a maximum peak value into account."""
        peakLoad = []
        for i in range(12):
            temp = load[self.hourlyLoadArray[i]:self.hourlyLoadArray[i + 1] + 1]
            peakLoad.append(max([min(j, peak) for j in temp]))
        return peakLoad

    def optimiseLoadProfile(self, depth: float = 150.):
        """This function optimises the load based on the given borefield and the given hourly load."""

        # if no hourly profile is given, load one
        if not self.hourlyCoolingLoad:
            self.loadHourlyProfile()

        # set initial peak loads
        initPeakHeatLoad = max(self.hourlyHeatingLoad)
        initPeakCoolLoad = max(self.hourlyCoolingLoad)

        # peak loads for iteration
        peakHeatLoad = initPeakHeatLoad
        peakCoolLoad = initPeakCoolLoad

        # set iteration criteria
        coolOK, heatOK = False, False

        while not coolOK or not heatOK:
            # calculate peak and base loads
            self.setPeakCooling(self.reduceToPeakLoad(self.hourlyCoolingLoad, peakCoolLoad))
            self.setPeakHeating(self.reduceToPeakLoad(self.hourlyHeatingLoad, peakHeatLoad))
            self.setBaseloadCooling(self.reduceToMonthLoad(self.hourlyCoolingLoad, peakCoolLoad))
            self.setBaseloadHeating(self.reduceToMonthLoad(self.hourlyHeatingLoad, peakHeatLoad))

            # calculate temperature profile, just for the results
            self._printTemperatureProfile(legend=False, H=depth, figure=False)

            # deviation from minimum temperature
            if abs(min(self.resultsPeakHeating)-self.Tf_C) > 0.05:

                # check if it goes below the threshold
                if min(self.resultsPeakHeating) < self.Tf_C:
                    peakHeatLoad -= 1*max(1, 10*(self.Tf_C - min(self.resultsPeakHeating)))
                else:
                    peakHeatLoad = min(initPeakHeatLoad, peakHeatLoad+1)
                    if peakHeatLoad == initPeakHeatLoad:
                        heatOK = True
            else:
                heatOK = True

            # deviation from maximum temperature
            if abs(max(self.resultsPeakCooling)-self.Tf_H) > 0.05:

                # check if it goes above the threshold
                if max(self.resultsPeakCooling) > self.Tf_H:
                    peakCoolLoad -= 1*max(1, 10*(-self.Tf_H + max(self.resultsPeakCooling)))
                else:
                    peakCoolLoad = min(initPeakCoolLoad, peakCoolLoad+1)
                    if peakCoolLoad == initPeakCoolLoad:
                        coolOK = True
            else:
                coolOK = True

        # print results
        print(f"The peak load heating is: {peakHeatLoad}kW, leading to "
              f"{functools_reduce(lambda x, y: x + y, self.baseloadHeating)} kWh of heating.")
        print(f"The peak load cooling is: {peakCoolLoad} kW, leading to "
              f"{functools_reduce(lambda x, y: x + y, self.peakCooling)} kWh of cooling.")

        # plot results
        self._printTemperatureProfile(H=depth)
