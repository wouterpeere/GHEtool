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

    def __init__(self, H: float, B: float, k_s: float, Tg: float, Rb: float, N_1: int, N_2: int):
        self.H = H  # m
        self.B = B  # m
        self.k_s = k_s  # W/mK
        self.Tg = Tg  # °C
        self.Rb = Rb  # mK/W
        self.N_1 = N_1  # #
        self.N_2 = N_2  # #


class Borefield:
    __slots__ = 'baseloadHeating', 'baseloadCooling', 'H', 'H_init', 'B', 'N_1', 'N_2', 'Rb', 'k_s', 'Tg', 'ty', 'tm', \
                'td', 'time', 'hourlyHeatingLoad', 'UPM', 'thresholdBorholeDepth', 'H_max', 'maxSimulationPeriod',\
                'hourlyCoolingLoad', 'numberOfBoreholes', 'borefield', 'customGfunction', 'costInvestement', \
                'lengthPeak', 'th', 'Tf_H', 'Tf_C', 'limitingQuadrant', 'monthlyLoad', 'monthlyLoadHeating', \
                'monthlyLoadCooling', 'peakHeating', 'imbalance', 'qa', 'Tf', 'qm', 'qh', 'qpm', 'tcm', 'tpm', \
                'peakCooling', 'simulationPeriod', 'defaultInvestement', 'defaultLengthPeak', 'defaultDepthArray',\
                'factoren_temperature_profile', 'resultsCooling', 'resultsHeating', 'resultsPeakHeating', \
                'resultsPeakCooling', 'resultsMonthCooling', 'resultsMonthHeating', 'Tb',\
                'thresholdWarningShallowField', 'GUI', 'printing', 'defaultTimeArray', 'hourlyLoadArray', \
                'gfunctionInterpolationArray', 'combo'

    def __init__(self, simulationPeriod: int, numberOfBoreholes: int = None, peakHeating: list = None,
                 peakCooling: list = None,
                 baseloadHeating: list = None, baseloadCooling: list = None, investementCost: list = None,
                 borefield=None, customGfunction=None, GUI: bool = False):
        """This function initiates the Borefield class"""

        # initiate vars
        listOfZeros = [0] * 12
        if baseloadCooling is None:
            baseloadCooling: list = listOfZeros
        if baseloadHeating is None:
            baseloadHeating: list = listOfZeros
        if peakCooling is None:
            peakCooling: list = listOfZeros
        if peakHeating is None:
            peakHeating: list = listOfZeros

        self.baseloadHeating: list = listOfZeros
        self.baseloadCooling: list = listOfZeros
        self.limitingQuadrant: int = 0
        self.Tf: float = 0.
        self.gfunctionInterpolationArray: list = []

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
        self.GUI = GUI  # check if the GHEtool is used by the GUI i
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
        self.setPeakHeating(peakHeating)
        self.setPeakCooling(peakCooling)
        self.setBaseloadCooling(baseloadCooling)  # defines the imbalance
        self.setBaseloadHeating(baseloadHeating)

        self.simulationPeriod = simulationPeriod

        self.costInvestement = None
        self.setInvestementCost(investementCost)

        # set length of the peak
        self.setLengthPeak()

        self.setNumberOfBoreholes(numberOfBoreholes)

        self.borefield = None
        self.setBorefield(borefield)

        self.customGfunction = None
        self.setCustomGfunction(customGfunction)
        self.combo: list = []

    @staticmethod
    def configurationString(N_1: int, N_2: int):
        """This functions returns the filename for the given configuration N_1, N_2."""
        string: str = str(max(N_1, N_2)) + "x" + str(min(N_1, N_2))
        return string

    def setNumberOfBoreholes(self, numberOfBoreholes: int = 0):
        """This functions sets the number of boreholes"""
        self.numberOfBoreholes = self.N_1 * self.N_2 if numberOfBoreholes == 0 else numberOfBoreholes

    def setBorefield(self, borefield=None):
        """
        This function sets the borefield configuration. When no input, an empty array of length N_1 * N_2 will be made
        """
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
        self.costInvestement: list = self.defaultInvestement if investementCost is None else investementCost

    def setLengthPeak(self, length: float = None):
        """This function sets the length of the peak to length."""
        self.lengthPeak: float = self.defaultLengthPeak if length is None else length
        self.setTimeConstants()

    def setTimeConstants(self):
        # Number of segments per borehole
        self.th: float = self.lengthPeak * 3600.  # length of peak in seconds
        self.ty: float = self.simulationPeriod * 8760. * 3600
        self.tm: float = self.UPM * 3600.
        self.td: float = self.lengthPeak * 3600.
        self.time: np.array = np.array([self.td, self.td + self.tm, self.ty + self.tm + self.td])

    def setGroundParameters(self, data: Union[dict, GroundData]):
        """This function sets the relevant borefield characteristics."""
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
            self.setNumberOfBoreholes(self.N_1 * self.N_2)
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
        self.setNumberOfBoreholes()

    def setMaxGroundTemperature(self, temp: float):
        """This function sets the maximal ground temperature to temp"""
        self.Tf_H: float = temp

    def setMinGroundTemperature(self, temp: float):
        """This function sets the minimal ground temperature to temp"""
        self.Tf_C: float = temp

    @property
    def _Bernier(self):
        """This function sizes the field based on the last year of operation, i.e. quadrants 2 and 4."""

        # initiate iteration
        H_prev = 0

        self.H = 50 if self.H < 1 else self.H

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
        H_prev: float = 0
        timeSteps: np.array = np.array([self.th, self.th + self.tm, self.tcm + self.th])
        self.H: float = 50 if self.H < 1 else self.H

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
        return self._Bernier  # size

    def sizeQuadrant3(self):
        self.calculateL3Params(True)  # calculate parameters
        return self._Carcel  # size

    def sizeQuadrant4(self):
        self.calculateL2Params(True)  # calculate parameters
        return self._Bernier  # size

    def size(self, H_init: float) -> float:
        """
        This function sizes the borefield of the given configuration according to the methodology explained in
        (Peere et al., 2021). It returns the borefield depth.
        :param H_init: float: borefield depth [m] to start calculation with
        :return: float: borefield depth [m]
        """
        # initiate with a given depth
        self.H: float = H_init

        if self.imbalance <= 0:
            # extraction dominated, so quadrants 1 and 4 are relevant
            quadrant1 = self.sizeQuadrant1()
            quadrant4 = self.sizeQuadrant4()
            self.H = max(quadrant1, quadrant4)

            if self.H == quadrant1:
                self.limitingQuadrant = 1
            else:
                self.limitingQuadrant = 4
        else:
            # injection dominated, so quadrants 2 and 3 are relevant
            quadrant2 = self.sizeQuadrant2()
            quadrant3 = self.sizeQuadrant3()
            self.H = max(quadrant2, quadrant3)

            if self.H == quadrant2:
                self.limitingQuadrant = 2
            else:
                self.limitingQuadrant = 3

        # check if the field is not shallow
        if self.H < self.thresholdWarningShallowField and self.printing:
            print("The field has a calculated depth of ", str(round(self.H, 2)),
                  " m which is lower than the proposed minimum of ", str(self.thresholdWarningShallowField), " m.")
            print("Please change your configuration accordingly to have a not so shallow field.")

        return self.H

    def calculateMonthlyLoad(self):
        """This function calculates the average monthly load in kW"""
        self.monthlyLoad = [(-self.baseloadHeating[i] + self.baseloadCooling[i]) / self.UPM for i in range(12)]

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
    def Calculate_Investement_Cost(self):
        """
        This function calculates the investement cost based on a cost profile lineair to the total borehole length.
        """
        return np.polyval(self.costInvestement, self.H * self.numberOfBoreholes)

    def calculateImbalance(self):
        """This function calculates the imbalance of the field.
        A positive imbalance means that the field is injection dominated, i.e. it heats up every year."""
        self.imbalance = functools.reduce(lambda x, y: x + y, self.baseloadCooling) - functools.reduce(
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
            self.qm = self.monthlyLoad[monthIndex] * 1000.
            self.qh = max(self.peakHeating) * 1000.

            # correct signs
            self.qm = -self.qm
            self.qa = -self.qa

        else:
            # limited by injection load

            # temperature limit set to maximum temperature
            self.Tf = self.Tf_H

            # Select month with highest peak load and take both the peak and average load from that month
            monthIndex = self.peakCooling.index(max(self.peakCooling))
            self.qm = self.monthlyLoad[monthIndex] * 1000.
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

            self.qm = self.monthlyLoad[monthIndex] * 1000.

            if monthIndex < 1:
                self.qpm = 0
            else:
                self.qpm = functools.reduce(lambda x, y: x + y, self.monthlyLoad[:monthIndex]) * 1000. / (
                            monthIndex + 1)

            self.qm = -self.qm
        else:
            # limited by injection

            # temperature limit set to maximum temperatue
            self.Tf = self.Tf_H

            # Select month with highest peak load and take both the peak and average load from that month
            monthIndex = self.peakCooling.index(max(self.peakCooling)) if monthIndex is None else monthIndex
            self.qh = max(self.peakCooling) * 1000.

            self.qm = self.monthlyLoad[monthIndex] * 1000.
            if monthIndex < 1:
                self.qpm = 0
            else:
                self.qpm = functools.reduce(lambda x, y: x + y, self.monthlyLoad[:monthIndex]) * 1000. / (
                            monthIndex + 1)
        self.tcm = (monthIndex + 1) * self.UPM * 3600
        self.tpm = monthIndex * self.UPM * 3600

        return monthIndex

    def calculateTemperatures(self, depth: float = None):
        """
        Calculate all the temperatures without plotting the figure. When depth is given, it calculates it for a given
        depth.
        """
        self._printTemperatureProfile(figure=False, H=depth)

    def printTemperatureProfile(self, legend: bool = True):
        """This function plots the temperature profile for the calculated depth."""
        self._printTemperatureProfile(legend=legend)

    def printTemperatureProfileFixedDepth(self, depth, legend: bool = True):
        """This function plots the temperature profile for a fixed depth depth."""
        self._printTemperatureProfile(legend=legend, H=depth)

    def _printTemperatureProfile(self, legend: bool = True, H: float = None, figure: bool = True):
        """
        This function would calculate a new length of the borefield using temporal superposition.
        Now it justs outputs the temperature graphs
        """

        # making a numpy array of the monthly balance (self.montlyLoad) for a period of self.simulationPeriod years [kW]
        monthlyLoadsArray = np.asarray(self.monthlyLoad * self.simulationPeriod)

        # calculation of all the different times at which the gfunction should be calculated.
        # this is equal to 'UPM' hours a month * 3600 seconds/hours for the simulationPeriod
        timeForgValues = [i * self.UPM * 3600. for i in range(1, 12 * self.simulationPeriod + 1)]

        # self.gfunction is a function that uses the precalculated data to interpolate the correct values of the
        # gfunction. This dataset is checked over and over again and is correct
        gValues = self.gfunction(timeForgValues, self.H if H is None else H)

        # the gfunction value of the peak with lengthPeak hours
        gValuePeak = self.gfunction(self.lengthPeak * 3600., self.H if H is None else H)

        # calculation of needed differences of the gfunction values. These are the weight factors in the calculation of
        # Tb.
        gValueDifferences = [gValues[i] if i == 0 else gValues[i] - gValues[i - 1] for i in range(len(gValues))]

        self.factoren_temperature_profile = gValueDifferences
        results = []
        temp = []

        # calculation of the product for every month in order to obtain a temperature profile
        for i in range(len(monthlyLoadsArray)):
            temp.insert(0, monthlyLoadsArray[i] * 1000.)
            results.append(np.dot(temp, gValueDifferences[:i + 1]))

        resultsCooling = []
        resultsHeating = []
        resultsPeakCooling = []
        resultsPeakHeating = []
        resultsMonthCooling = []
        resultsMonthHeating = []

        # calculation the borehole wall temperature for every month i
        Tb = [i / (2 * pi * self.k_s) / ((self.H if H is None else H) * self.numberOfBoreholes) + self.Tg for i in
              results]
        self.Tb = Tb
        # now the Tf will be calculated based on
        # Tf = Tb + Q * R_b
        for i in range(12 * self.simulationPeriod):
            resultsCooling.append(Tb[i] + self.monthlyLoadCooling[i % 12] * 1000. * (
                    self.Rb / self.numberOfBoreholes / (self.H if H is None else H)))
            resultsHeating.append(Tb[i] - self.monthlyLoadHeating[i % 12] * 1000. * (
                    self.Rb / self.numberOfBoreholes / (self.H if H is None else H)))
            resultsMonthCooling.append(Tb[i] + self.monthlyLoadCooling[i % 12] * 1000. * (
                    self.Rb / self.numberOfBoreholes / (self.H if H is None else H)))
            resultsMonthHeating.append(Tb[i] - self.monthlyLoadHeating[i % 12] * 1000. * (
                    self.Rb / self.numberOfBoreholes / (self.H if H is None else H)))

        # extra sommation if the gfunction value for the peak is included

        for i in range(12 * self.simulationPeriod):
            resultsPeakCooling.append(
                resultsCooling[i] + ((self.peakCooling[i % 12] - self.monthlyLoadCooling[i % 12] if
                                      self.peakCooling[i % 12] > self.monthlyLoadCooling[
                                          i % 12] else 0) * 1000. * (
                                             gValuePeak[0] / self.k_s / 2 / pi + self.Rb)) / self.numberOfBoreholes / (
                    self.H if H is None else H))
            resultsPeakHeating.append(
                resultsHeating[i] - ((self.peakHeating[i % 12] - self.monthlyLoadHeating[i % 12] if
                                      self.peakHeating[i % 12] > self.monthlyLoadHeating[
                                          i % 12] else 0) * 1000. * (
                                             gValuePeak[0] / self.k_s / 2 / pi + self.Rb)) / self.numberOfBoreholes / (
                    self.H if H is None else H))

        # save temperatures under variable
        self.resultsCooling: list = resultsCooling
        self.resultsHeating: list = resultsHeating
        self.resultsPeakHeating: list = resultsPeakHeating
        self.resultsPeakCooling: list = resultsPeakCooling
        self.resultsMonthCooling: list = resultsMonthCooling
        self.resultsMonthHeating: list = resultsMonthHeating

        # initiate figure
        if figure:
            # make a time array
            timeArray = [i / 12 / 730. / 3600. for i in timeForgValues]

            plt.rc('figure')
            fig = plt.figure()

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
            ax1.hlines(self.Tf_C, 0, self.simulationPeriod, colors='r', linestyles='dashed', label='', lw=1)
            ax1.hlines(self.Tf_H, 0, self.simulationPeriod, colors='b', linestyles='dashed', label='', lw=1)
            ax1.set_xticks(range(0, self.simulationPeriod + 1, 2))

            # Plot legend
            if legend:
                ax1.legend()
            ax1.set_xlim(left=0, right=self.simulationPeriod)
            plt.show()

    # if no interpolation array exists, it creates one
    def makeInterpolationListDefault(self, data, Time):
        """This function creates an interpolation list and saves it under gfunctionInterpolationArray."""

        B_array = list(data.keys())
        ks_array = list(data[B_array[0]].keys())
        H_array = list(data[B_array[0]][ks_array[0]].keys())
        self.H_max = max(H_array)
        B_array.sort()
        ks_array.sort()
        H_array.sort()

        points: tuple = (B_array, ks_array, H_array, Time)

        values: list = [[[data[B][ks][i] for i in H_array] for ks in ks_array] for B in B_array]
        self.gfunctionInterpolationArray = points, values

    def makeInterpolationListCustom(self, data, Time):
        """
        This function creates an interpolation list from a custom dataset and saves it under
        gfunctionInterpolationArray.
        """
        H_array = list(data["Data"].keys())
        H_array.sort()
        points = (H_array, Time)
        values = [data["Data"][i] for i in H_array]
        self.gfunctionInterpolationArray = points, values

    def gfunction(self, timeValue: np.array, H: float):
        """This function calculated the gfunction based on interpolation of the precalculated data."""

        if self.GUI:
            if self.customGfunction is None:
                MaxN = max(self.N_1, self.N_2)
                MinN = min(self.N_1, self.N_2)
                dataFile = f'Data.data_{MaxN}x{MinN}'
                from importlib import import_module as im
                dataModule = im(dataFile)
                data = dataModule.data
            else:
                name = f'{FOLDER}/Data/{self.customGfunction}.pickle'

                # check if datafile exists
                if not os.path.isfile(name):
                    print(name)
                    raise Exception('There is no precalculated data available. Please use the createCustomDatafile.')

                # load data file
                data = pickle.load(open(name, "rb"))

        else:
            # get the name of the data file
            if self.customGfunction is None:
                name = self.configurationString(self.N_1, self.N_2) + ".pickle"
            else:
                name = self.customGfunction + ".pickle"
            # check if datafile exists
            if not os.path.isfile(FOLDER + "/Data/" + name):
                print(name)
                raise Exception('There is no precalculated data available. Please use the createCustomDatafile.')
            # load data file
            data = pickle.load(open(FOLDER + "/Data/" + name, "rb"))

        # remove the time value
        Time = self.defaultTimeArray
        try:
            data.pop("Time")
        except KeyError:
            data = data

        if not self.gfunctionInterpolationArray:
            if self.customGfunction is None:
                self.makeInterpolationListDefault(data, Time)
            else:
                self.makeInterpolationListCustom(data, Time)
        try:
            points, values = self.gfunctionInterpolationArray
            if self.customGfunction is None:
                # interpolate
                if not isinstance(timeValue, float):
                    # multiple values are requested
                    gvalue = interpolate.interpn(points, values,
                                                 np.array([[self.B, self.k_s, H, t] for t in timeValue]))
                else:
                    # only one value is requested
                    gvalue = interpolate.interpn(points, values, np.array([self.B, self.k_s, H, timeValue]))
            else:
                # interpolate
                if not isinstance(timeValue, float):
                    # multiple values are requested
                    gvalue = interpolate.interpn(points, values, np.array([[H, t] for t in timeValue]))
                else:
                    # only one value is requested
                    gvalue = interpolate.interpn(points, values, np.array([H, timeValue]))
            return gvalue
        except ValueError:
            if self.printing:
                if self.simulationPeriod > self.maxSimulationPeriod:
                    print("Your requested simulationperiod of " + str(
                        self.simulationPeriod) + " years is beyond the limit of " + str(
                        self.maxSimulationPeriod) + " years of the precalculated data.")
                else:
                    print("Your requested depth of " + str(H) + "m is beyond the limit " + str(
                        self.H_max) + "m of the precalculated data.")
                    print("Please change your borefield configuration accordingly.")
                print("-------------------------")
                print("This calculation stopped.")
            raise ValueError

    def createCustomDataset(self, customBorefield: str, nameDatafile: str, nSegments: int = 12,
                            timeArray: list = None, depthArray: list = None):
        """This function makes a datafile for a given custom borefield."""
        timeArray = self.defaultTimeArray if timeArray is None else timeArray
        depthArray = self.defaultDepthArray if depthArray is None else depthArray
        # make filename
        name = nameDatafile + ".pickle"
        # check if file exists
        if not os.path.isfile("Data/" + name):
            # does not exist, so create
            pickle.dump(dict([]), open(FOLDER + "/Data/" + name, "wb"))
        else:
            raise Exception("The dataset " + name + " already exists. Please chose a different name.")

        data = pickle.load(open(FOLDER + "/Data/" + name, "rb"), encoding='latin1')

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

            gfunc_uniform_T = gt.gfunction.uniform_temperature(
                customBorefield, timeArray, alpha, nSegments=nSegments, disp=True)

            data["Data"][H] = gfunc_uniform_T

        self.setCustomGfunction(nameDatafile)
        print("A new dataset with name " + name + " has been created in " + os.path.dirname(
            os.path.realpath(__file__)) + "\Data.")
        pickle.dump(data, open(FOLDER + "/Data/" + name, "wb"))

    def printTemperatureProfile(self, legend: bool = True):
        """This function plots the temperature profile for the calculated depth."""
        self._printTemperatureProfile(legend=legend)

    def printTemperatureProfileFixedDepth(self, depth: float, legend: bool = True):
        """This function plots the temperature profile for a fixed depth depth."""
        self._printTemperatureProfile(legend=legend, H=depth)

    def loadHourlyProfile(self):
        """
        This function loads in an hourly load profile. It opens a csv and asks for the relevant column where the data
        is in.
        """

        # give the location of the file
        filePath = filedialog.askopenfilename(title="Select csv-file with hourly load.")

        # workbook object is created
        wb_obj = openpyxl.load_workbook(filePath)

        sheet_obj = wb_obj.active
        max_row = sheet_obj.max_row

        # Loop will create lists with the hourly loads
        for i in range(2, max_row + 1):
            cell_obj = sheet_obj.cell(row=i, column=1)
            self.hourlyHeatingLoad.append(cell_obj.value)
        for i in range(2, max_row + 1):
            cell_obj = sheet_obj.cell(row=i, column=2)
            self.hourlyCoolingLoad.append(cell_obj.value)

    def optimiseLoadProfile(self, depth: float = 150):
        """This function optimises the load based on the given borefield and the given hourly load."""

        def reduceToMonthLoad(load: list, peak: float):
            """This function calculates the monthly load based, taking a maximum peak value into account."""
            monthLoad = []
            for i in range(12):
                temp = load[self.hourlyLoadArray[i]:self.hourlyLoadArray[i + 1] + 1]
                monthLoad.append(functools.reduce(lambda x, y: x + y, [min(j, peak) for j in temp]))
            return monthLoad

        def reduceToPeakLoad(load: list, peak: float):
            """This function calculates the monthly peak load, taking a maximum peak value into account."""
            peakLoad = []
            for i in range(12):
                temp = load[self.hourlyLoadArray[i]:self.hourlyLoadArray[i + 1] + 1]
                peakLoad.append(max([min(j, peak) for j in temp]))
            return peakLoad

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
            self.setPeakCooling(reduceToPeakLoad(self.hourlyCoolingLoad, peakCoolLoad))
            self.setPeakHeating(reduceToPeakLoad(self.hourlyHeatingLoad, peakHeatLoad))
            self.setBaseloadCooling(reduceToMonthLoad(self.hourlyCoolingLoad, peakCoolLoad))
            self.setBaseloadHeating(reduceToMonthLoad(self.hourlyHeatingLoad, peakHeatLoad))

            # calculate temperature profile, just for the results
            self._printTemperatureProfile(legend=False, H=depth, figure=False)

            # deviation from minimum temperature
            if abs(min(self.resultsPeakHeating) - self.Tf_C) > 0.05:

                # check if it goes below the threshold
                if min(self.resultsPeakHeating) < self.Tf_C:
                    peakHeatLoad -= 1 * max(1, 10 * (self.Tf_C - min(self.resultsPeakHeating)))
                else:
                    peakHeatLoad = min(initPeakHeatLoad, peakHeatLoad + 1)
                    if peakHeatLoad == initPeakHeatLoad:
                        heatOK = True
            else:
                heatOK = True

            # deviation from maximum temperature
            if abs(max(self.resultsPeakCooling) - self.Tf_H) > 0.05:

                # check if it goes above the threshold
                if max(self.resultsPeakCooling) > self.Tf_H:
                    peakCoolLoad -= 1 * max(1, 10 * (-self.Tf_H + max(self.resultsPeakCooling)))
                else:
                    peakCoolLoad = min(initPeakCoolLoad, peakCoolLoad + 1)
                    if peakCoolLoad == initPeakCoolLoad:
                        coolOK = True
            else:
                coolOK = True

        # print results
        print("The peak load heating is: ", int(peakHeatLoad), "kW, leading to ",
              int(functools.reduce(lambda x, y: x + y, self.baseloadHeating)), "kWh of heating.")
        print("The peak load cooling is: ", int(peakCoolLoad), "kW, leading to ",
              int(functools.reduce(lambda x, y: x + y, self.peakCooling)), "kWh of cooling.")

        # plot results
        self._printTemperatureProfile(H=depth)

    def Size_Complete_Field_Robust(self, H_max: float, L_1: float, L_2: float, B_min: float = 3.0, B_max: float = 9.0) \
            -> list:
        L_2_bigger_then_L_1: bool = L_2 > L_1
        (L_1, L_2) = (L_2, L_1) if L_2_bigger_then_L_1 else (L_1, L_2)
        N_N_max_start: int = 20 * 20
        N_N_max: int = N_N_max_start
        combo_start: list = [[20, 20, 9]]
        combo = combo_start
        self.printing: bool = False
        product_min = 0
        for B in np.arange(B_max, B_min * 0.99999, -0.5):
            N_1_max = min(int(L_1 / B), 20)
            N_2_max = min(int(L_2 / B), 20)
            for N_1 in range(N_1_max, 0, -1):
                for N_2 in range(min(N_2_max, N_1), 0, -1):
                    self.N_1 = N_1
                    self.N_2 = N_2
                    self.B = B
                    product = N_1 * N_2
                    if product > N_N_max:
                        continue
                    if product < product_min:
                        break
                    self.setNumberOfBoreholes(product)
                    try:
                        self.gfunctionInterpolationArray = []
                        depth = self.size(H_max)
                        print(f'N_1: {N_1}; N_2: {N_2}; B: {B}; depth: {depth};')
                    except ValueError:
                        product_min = product
                        break
                    if depth > H_max:
                        break
                    if product < N_N_max:
                        N_N_max = product
                        combo = [[N_1, N_2, B, self.H]]
                    elif product == N_N_max:
                        combo.append([self.N_1, self.N_2, B, self.H])
        if N_N_max == N_N_max_start:
            return [[0, 0, 0, 0]]
        self.N_1 = combo[0][1] if L_2_bigger_then_L_1 else combo[0][0]
        self.N_2 = combo[0][0] if L_2_bigger_then_L_1 else combo[0][1]
        self.B = combo[0][2]
        if L_2_bigger_then_L_1:
            for i in combo:
                i[0], i[1] = i[1], i[0]
        self.setNumberOfBoreholes(self.N_1 * self.N_2)
        self.gfunctionInterpolationArray = []
        self.H = self.size(H_max)
        self.printing: bool = True
        self.combo = combo
        return combo

    def Size_Complete_Field_Fast(self, H_max: float, L_1: float, L_2: float, B_min: float = 3.0, B_max: float = 9.0) \
            -> list:
        L_2_bigger_then_L_1: bool = L_2 > L_1
        (L_1, L_2) = (L_2, L_1) if L_2_bigger_then_L_1 else (L_1, L_2)
        N_N_max_start: int = 20 * 20
        N_N_max: int = N_N_max_start
        combo_start: list = [[20, 20, 9, H_max]]
        combo = combo_start
        self.printing: bool = False
        for B in np.arange(B_max, B_min * 0.99999, -0.5):
            N_1_max = min(int(L_1 / B), 20)
            N_2_max = min(int(L_2 / B), 20)
            self._Reset_For_Sizing(N_1_max, N_2_max)
            self.N_1 = N_1_max
            self.B = B
            product_old = self.N_1 * self.N_2
            try:
                depth = self.size(H_max)
                Number_Of_boreholes = int(depth * product_old/H_max)+1
                res = self._Calc_NumberOfHoles(Number_Of_boreholes, N_1_max, N_2_max)
                self._Reset_For_Sizing(res[0][0], res[0][1])
                product_new = self.N_1 * self.N_2
                counter = 0
                from numpy import sign
                while product_old != product_new:
                    gradient = int(0.51 * (product_new - product_old)) if counter > 4 else int(product_new -
                                                                                               product_old)
                    product_new = product_old + sign(gradient) * min(abs(gradient), 1)
                    depth = self.size(H_max)
                    Number_Of_boreholes = int(depth * product_new / H_max) + 1
                    res = self._Calc_NumberOfHoles(Number_Of_boreholes, N_1_max, N_2_max)
                    self._Reset_For_Sizing(res[0][0], res[0][1])
                    product_old = self.N_1 * self.N_2
                    counter += 1
                    if counter > 20 and depth < H_max:
                        break
                if product_new < N_N_max:
                    N_N_max = product_new
                    if len(res) > 1:
                        combo: list = []
                        First: bool = True
                        for i in res:
                            if First:
                                combo.append([i[0], i[1], B, self.H])
                                First = False
                                continue
                            self._Reset_For_Sizing(i[0], i[1])
                            self.size(H_max)
                            if self.H < H_max:
                                combo.append([i[0], i[1], B, self.H])
                    else:
                        combo = [[res[0][0], res[0][1], B, self.H]]
                elif product_new == N_N_max:
                    if len(res) > 1:
                        First: bool = True
                        for i in res:
                            if First:
                                combo.append([i[0], i[1], B, self.H])
                                First = False
                                continue
                            self._Reset_For_Sizing(i[0], i[1])
                            self.size(H_max)
                            if self.H < H_max:
                                combo.append([i[0], i[1], B, self.H])
                    else:
                        combo += [[res[0][0], res[0][1], B, self.H]]

            except ValueError:
                break

        if N_N_max == N_N_max_start:
            return [[0, 0, 0, 0]]
        self.N_1 = combo[0][1] if L_2_bigger_then_L_1 else combo[0][0]
        self.N_2 = combo[0][0] if L_2_bigger_then_L_1 else combo[0][1]
        self.B = combo[0][2]
        if L_2_bigger_then_L_1:
            for i in combo:
                i[0], i[1] = i[1], i[0]
        self.setNumberOfBoreholes(self.N_1 * self.N_2)
        self.H = self.size(H_max)
        self.printing: bool = True
        self.combo = combo
        return combo

    def _Reset_For_Sizing(self, N_1: int, N_2: int) -> None:
        self.N_1, self.N_2 = N_1, N_2
        self.gfunctionInterpolationArray = []
        self.setNumberOfBoreholes()

    @staticmethod
    def _Calc_NumberOfHoles(n: int, N_1_max: int, N_2_max: int) -> list:
        res = [(20, 20)]
        maxVal = 20 * 20
        for i in range(1, N_1_max + 1):
            for j in range(1, min(N_2_max, i) + 1):
                if n <= j * i < maxVal:
                    res = [(i, j)]
                    maxVal = i * j
                elif i*j == maxVal:
                    res.append((i, j))

        return res
