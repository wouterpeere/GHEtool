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

def timeValues():
    """This function calculates the default time values for the gfunction."""
    dt: float = 3600.  # Time step (s)
    tmax: float = 100. * 8760. * 3600.  # Maximum time (s)

    # Load aggregation scheme
    LoadAgg: list = gt.load_aggregation.ClaessonJaved(dt, tmax)

    return LoadAgg.get_times_for_simulation()


class GroundData:
    __slots__ = 'H', 'B', 'k_s', 'Tg', 'Rb', 'N_1', 'N_2'

    def __init__(self, h: float, b: float, k_s: float, t_g: float, r_b: float, n_1: int, n_2: int) -> None:
        """
        Data for storage of ground data
        :param h: Depth of boreholes [m]
        :param b: Borehole spacing [m]
        :param k_s: Ground thermal conductivity [W/m.K]
        :param t_g: Ground temperature at infinity [°C]
        :param r_b: Equivalent borehole resistance [m K/W]
        :param n_1: Width of rectangular field [#]
        :param n_2: Length of rectangular field [#]
        """
        self.H = h  # m
        self.B = b  # m
        self.k_s = k_s  # W/mK
        self.Tg = t_g  # °C
        self.Rb = r_b  # mK/W
        self.N_1 = n_1  # #
        self.N_2 = n_2  # #

    def __eq__(self, other):
        if not isinstance(other, GroundData):
            return False
        for i in self.__slots__:
            if getattr(self, i) != getattr(other, i):
                return False
        return True


class FluidData:

    __slots__ = 'k_f', 'rho', 'Cp', 'mu', 'mfr'

    def __init__(self, mfr: float, k_f: float, rho: float, Cp: float, mu: float):
        self.k_f = k_f  # Thermal conductivity W/mK
        self.mfr = mfr  # Mass flow rate kg/s
        self.rho = rho  # Density kg/m3
        self.Cp = Cp    # Thermal capacity J/kgK
        self.mu = mu    # Dynamic viscosity Pa/s

    def __eq__(self, other):
        if not isinstance(other, FluidData):
            return False
        for i in self.__slots__:
            if getattr(self, i) != getattr(other, i):
                return False
        return True


class PipeData:

    __slots__ = 'r_in', 'r_out', 'k_p', 'D_s', 'r_b', 'numberOfPipes', 'epsilon', 'k_g', 'D'

    def __init__(self, k_g: float, r_in: float, r_out: float, k_p: float, D_s: float, r_b: float, numberOfPipes: int, epsilon: float = 1e-6, D: float = 4):

        self.k_g = k_g                      # grout thermal conductivity W/mK
        self.r_in = r_in                    # inner pipe radius m
        self.r_out = r_out                  # outer pipe radius m
        self.k_p = k_p                      # pipe thermal conductivity W/mK
        self.D_s = D_s                      # distance of pipe until center m
        self.r_b = r_b                      # borehole radius m
        self.numberOfPipes = numberOfPipes  # number of pipes #
        self.epsilon = epsilon              # pipe roughness
        self.D = D                          # burial depth m

    def __eq__(self, other):
        if not isinstance(other, FluidData):
            return False
        for i in self.__slots__:
            if getattr(self, i) != getattr(other, i):
                return False
        return True


class Borefield:
    UPM: float = 730.  # number of hours per month
    thresholdBorholeDepth: float = 0.05  # threshold for iteration
    maxSimulationPeriod: int = 100  # maximal value for simulation

    # define default values
    defaultInvestement: list = [35, 0]  # 35 EUR/m
    defaultLengthPeak: int = 6  # hours
    defaultDepthArray: list = [1] + list(range(25, 351, 25))  # m
    defaultTimeArray: list = timeValues()  # sec

    temp: int = 0
    hourlyLoadArray: list = []
    for i in [0, 24 * 31, 24 * 28, 24 * 31, 24 * 30, 24 * 31, 24 * 30, 24 * 31, 24 * 31, 24 * 30, 24 * 31, 24 * 30,
              24 * 31]:
        temp += i
        hourlyLoadArray.append(temp)

    __slots__ = 'baseloadHeating', 'baseloadCooling', 'H', 'H_init', 'B', 'N_1', 'N_2', 'Rb', 'k_s', 'Tg', 'ty', 'tm', \
                'td', 'time', 'hourlyHeatingLoad', 'H_max', \
                'hourlyCoolingLoad', 'numberOfBoreholes', 'borefield', 'customGfunction', 'costInvestement', \
                'lengthPeak', 'th', 'Tf_H', 'Tf_C', 'limitingQuadrant', 'monthlyLoad', 'monthlyLoadHeating', \
                'monthlyLoadCooling', 'peakHeating', 'imbalance', 'qa', 'Tf', 'qm', 'qh', 'qpm', 'tcm', 'tpm', \
                'peakCooling', 'simulationPeriod', 'gfunctionInterpolationArray', 'fluidDataAvailable', \
                'resultsCooling', 'resultsHeating', 'resultsPeakHeating', 'pipeDataAvailable', \
                'resultsPeakCooling', 'resultsMonthCooling', 'resultsMonthHeating', 'Tb', 'thresholdWarningShallowField', \
                'GUI', 'timeL3FirstYear', 'timeL3LastYear', 'peakHeatingExternal', 'peakCoolingExternal', \
                'monthlyLoadHeatingExternal', 'monthlyLoadCoolingExternal', 'hourlyHeatingLoadExternal', \
                'hourlyCoolingLoadExternal', 'hourlyHeatingLoadOnTheBorefield', 'hourlyCoolingLoadOnTheBorefield', \
                'k_f', 'mfr', 'Cp', 'mu', 'rho', 'useConstantRb', 'h_f', 'R_f', 'R_p', 'printing', 'combo', \
                'r_in', 'r_out', 'k_p', 'D_s', 'r_b', 'numberOfPipes', 'epsilon', 'k_g', 'pos', 'D'

    def __init__(self, simulationPeriod: int = 20, numberOfBoreholes: int = None, peakHeating: list = None,
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

        self.limitingQuadrant: int = 0  # parameter that tells in which quadrant the field is limited
        self.thresholdWarningShallowField: int = 50  # m hereafter one needs to chance to fewer boreholes with more depth, because the calculations are no longer that accurate.
        self.useConstantRb = True  # parameter that determines whether or not the Rb-value should be altered in the optimisation

        self.H_max: float = 0  # max threshold for interpolation (will with first sizing)

        self.gfunctionInterpolationArray: list = []

        # initiate variables for temperature plotting
        self.resultsHeating: list = []  # list with the minimum temperatures
        self.resultsCooling: list = []  # list with the maximum temperatures
        self.resultsPeakHeating: list = []  # list with the minimum temperatures due to the peak heating
        self.resultsPeakCooling: list = []  # list with the maximum temperatures due to peak cooling
        self.Tb: list = []  # list of borehole wall temperatures

        # initiate variables for optimal sizing
        self.hourlyHeatingLoad: list = []
        self.hourlyCoolingLoad: list = []
        self.hourlyCoolingLoadExternal: list = []
        self.hourlyHeatingLoadExternal: list = []
        self.peakHeatingExternal: list = []
        self.peakCoolingExternal: list = []
        self.monthlyLoadHeatingExternal: list = []
        self.monthlyLoadCoolingExternal: list = []
        self.hourlyHeatingLoadOnTheBorefield: list = []
        self.hourlyCoolingLoadOnTheBorefield: list = []

        # initiate load variables
        self.baseloadHeating: list = listOfZeros  # list with baseLoad heating kWh
        self.baseloadCooling: list = listOfZeros  # list with baseLoad cooling kWh
        self.peakCooling: list = listOfZeros  # list with the peak load cooling kW
        self.peakHeating: list = listOfZeros  # list with peak load heating kW

        # initiate time variables
        self.ty: float = 0.  # yearly time value
        self.tm: float = 0.  # monthly time value
        self.td: float = 0.  # daily time value
        self.th: float = 0.  # duration of peak in seconds
        self.lengthPeak: float = 0.  # duration of the peak in hours
        self.time: list = []  # list of time values
        self.tcm: float = 0.  # time constant for first year sizing
        self.tpm: float = 0.  # time constant for first year sizing
        self.timeL3FirstYear: list = []  # list with time values for L3 sizing
        self.timeL3LastYear: list = []  # list with time values for L3 sizing

        # initiate ground loads
        self.qa: float = 0.  # yearly load W
        self.qm: float = 0.  # monthly load W
        self.qh: float = 0.  # peak load W
        self.qpm: float = 0.  # cummulative load first year sizing
        self.imbalance: float = 0.  # imbalance kWh

        # initiate ground parameters
        self.H = 0.  # borehole depth m
        self.B = 0.  # borehole spacing m
        self.k_s = 0.  # ground thermal conductivity W/mK
        self.Tg = 0.  # ground temperature at infinity °C
        self.Rb = 0.  # effective borehole thermal resistance mK/W
        self.N_1 = 0  # number of boreholes in one direction #
        self.N_2 = 0  # number of boreholes in the other direction #

        # initiate fluid parameters
        self.k_f = 0.  # Thermal conductivity W/mK
        self.mfr = 0.  # Mass flow rate kg/s
        self.rho = 0.  # Density kg/m3
        self.Cp = 0.  # Thermal capacity J/kgK
        self.mu = 0.  # Dynamic viscosity Pa/s.
        self.Tf: float = 0.  # temperature of the fluid
        self.Tf_H: float = 16.  # maximum temperature of the fluid
        self.Tf_C: float = 0.  # minimum temperature of the fluid
        self.fluidDataAvailable: bool = False  # needs to be True in order to calculate Rb*

        # initiate borehole parameters
        self.r_in: float = 0.015  # inner pipe radius m
        self.r_out: float = 0.  # outer pipe radius m
        self.r_b: float = 0.  # borehole radius m
        self.k_g: float = 0.  # grout thermal conductivity W/mK
        self.k_p: float = 0.  # pipe thermal conductivity W/mK
        self.D_s: float = 0.  # distance of pipe until center of the borehole
        self.numberOfPipes: int = 0  # number of pipes in the borehole (single = 1, double = 2 etc.)
        self.D: float = 4.  # burial depth m
        self.epsilon = 1e-6  # pipe roughness
        self.pipeDataAvailable: bool = False  # needs to be True in order to calculate Rb*

        # check if the GHEtool is used by the GUI i
        self.GUI = GUI

        # set boolean for printing output
        self.printing: bool = True
        # set list for the sizing ba length and width output
        self.combo: list = []

        ### define vars
        # set load profiles
        self.setPeakHeating(peakHeating)
        self.setPeakCooling(peakCooling)
        self.setBaseloadCooling(baseloadCooling)
        self.setBaseloadHeating(baseloadHeating)

        # set simulation period
        self.simulationPeriod: int = simulationPeriod

        # set investement cost
        self.setInvestementCost(investementCost)

        # set length of the peak
        self.setLengthPeak()

        # calculate number of boreholes
        self.setNumberOfBoreholes(numberOfBoreholes if numberOfBoreholes is not None else 1)

        # set a custom borefield
        self.setBorefield(borefield)

        # set a custom gfunction
        self.setCustomGfunction(customGfunction)

    @staticmethod
    def configurationString(N_1: int, N_2: int):
        """This functions returns the filename for the given configuration N_1, N_2."""
        string: str = str(max(N_1, N_2)) + "x" + str(min(N_1, N_2))
        return string

    def setNumberOfBoreholes(self, numberOfBoreholes: int = 1):
        """This functions sets the number of boreholes"""
        self.numberOfBoreholes = numberOfBoreholes if numberOfBoreholes > 1 else self.N_1 * self.N_2

    def setBorefield(self, borefield=None):
        """This function sets the borefield configuration. When no input, an empty array of length N_1 * N_2 will be made"""
        if borefield is None:
            return
        self.borefield = borefield
        self.setNumberOfBoreholes(len(borefield))

    def setCustomGfunction(self, customGfunction):
        """This functions sets the custom g-function."""
        self.customGfunction = customGfunction
        self.gfunctionInterpolationArray: list = []

    def setInvestementCost(self, investementCost: list = defaultInvestement):
        """This function sets the investement cost. This is linear with respect to the total field length."""
        self.costInvestement: list = investementCost

    def setLengthPeak(self, length: float = defaultLengthPeak):
        """This function sets the length of the peak to length."""
        self.lengthPeak: float = length
        self.setTimeConstants()

    def setTimeConstants(self):
        # Number of segments per borehole
        self.th: float = self.lengthPeak * 3600.  # length of peak in seconds
        self.ty: float = self.simulationPeriod * 8760. * 3600
        self.tm: float = Borefield.UPM * 3600.
        self.td: float = self.lengthPeak * 3600.
        self.time = np.array([self.td, self.td + self.tm, self.ty + self.tm + self.td])

        # set the time array for the L3 sizing
        # This is one time for every month in the whole simulation period
        self.timeL3FirstYear = [i * Borefield.UPM * 3600. for i in range(1, 12 + 1)]
        self.timeL3LastYear = [i * Borefield.UPM * 3600. for i in range(1, self.simulationPeriod * 12 + 1)]

    def setGroundParameters(self, data):
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

        else:
            # backup for backwards compatibility
            self.H: float = data["H"]  # Borehole length (m)
            self.B: float = data["B"]  # Borehole spacing (m)

            self.N_1: int = data["N_1"]
            self.N_2: int = data["N_2"]

            self.Rb: float = data["Rb"]

            # Ground properties
            self.k_s: float = data["k_s"]  # Ground thermal conductivity (W/m.K)
            self.Tg: float = data["Tg"]  # Ground temperature at infinity (C)

        # sets the number of boreholes as if it was a rectangular field, iff there is not yet a number of boreholes
        # defined by a custom configuration
        self.setNumberOfBoreholes(self.N_1 * self.N_2)

        # new ground data implies that a new gfunction should be loaded
        self.gfunctionInterpolationArray = []

    def setFluidParameters(self, data):
        """This function sets the relevant fluid characteristics."""

        self.k_f = data.k_f  # Thermal conductivity W/mK
        self.rho = data.rho  # Density kg/m3
        self.Cp = data.Cp  # Thermal capacity J/kgK
        self.mu = data.mu  # Dynamic viscosity Pa/s
        self.setMassFlowRate(data.mfr)
        self.fluidDataAvailable = True

        if self.pipeDataAvailable:
            self.calculateFluidThermalResistance()

    def setPipeParameters(self, data):
        """This function sets the pipe parameters."""

        self.r_in = data.r_in  # inner pipe radius m
        self.r_out = data.r_out  # outer pipe radius m
        self.k_p = data.k_p  # pipe thermal conductivity W/mK
        self.D_s = data.D_s  # distance of pipe until center m
        self.r_b = data.r_b  # borehole radius m
        self.numberOfPipes = data.numberOfPipes  # number of pipes #
        self.epsilon = data.epsilon  # pipe roughness
        self.k_g = data.k_g  # grout thermal conductivity W/mK
        self.D = data.D  # burial depth m
        self.pos = self._axisymmetricalPipe  # calculates the position of the pipes based on an axisymmetrical positioning

        self.pipeDataAvailable = True
        # calculate the different resistances
        if self.fluidDataAvailable:
            self.calculateFluidThermalResistance()
        self.calculatePipethermalResistance()

    def setMaxGroundTemperature(self, temp: float):
        """This function sets the maximal ground temperature to temp."""
        self.Tf_H: float = temp

    def setMinGroundTemperature(self, temp: float):
        """This function sets the minimal ground temperature to temp."""
        self.Tf_C: float = temp

    def setMassFlowRate(self, mfr: float):
        """This function sets the mass flow rate."""
        self.mfr = mfr

    def calculateFluidThermalResistance(self):
        """This function calcules and sets the fluid thermal resistance R_f."""
        self.h_f = gt.pipes.convective_heat_transfer_coefficient_circular_pipe(self.mfr, self.r_in, self.mu, self.rho,
                                                                               self.k_f, self.Cp, self.epsilon)
        self.R_f = 1. / (self.h_f * 2 * pi * self.r_in)

    def calculatePipethermalResistance(self):
        """This function calculates and sets the pipe thermal resistance R_p."""
        self.R_p = gt.pipes.conduction_thermal_resistance_circular_pipe(self.r_in, self.r_out, self.k_p)

    @property
    def _Rb(self):
        """This function gives back the equivalent borehole resistance."""
        # use a constant Rb*
        if self.useConstantRb:
            return self.Rb

        # calculate Rb*
        return self.calculateRb()

    def calculateRb(self):
        """This function returns the calculated equivalent borehole thermal resistance Rb* value."""
        # check if all data is available
        if not self.pipeDataAvailable or not self.fluidDataAvailable:
            print("Please make sure you set al the pipe and fluid data.")
            raise ValueError

        # initiate temporary borefield
        borehole = gt.boreholes.Borehole(self.H, self.D, self.r_b, 0, 0)
        # initiate pipe
        pipe = gt.pipes.MultipleUTube(self.pos, self.r_in, self.r_out, borehole, self.k_s, self.k_g,
                                      self.R_p + self.R_f, self.numberOfPipes, J=2)
        return gt.pipes.borehole_thermal_resistance(pipe, self.mfr, self.Cp)

    @property
    def _axisymmetricalPipe(self):
        """This function gives back the coordinates of the pipes in an axisymmetrical pipe."""
        dt = pi / float(self.numberOfPipes)
        pos = [(0., 0.) for i in range(2 * self.numberOfPipes)]
        for i in range(self.numberOfPipes):
            pos[i] = (self.D_s * np.cos(2.0 * i * dt + pi), self.D_s * np.sin(2.0 * i * dt + pi))
            pos[i + self.numberOfPipes] = (
            self.D_s * np.cos(2.0 * i * dt + pi + dt), self.D_s * np.sin(2.0 * i * dt + pi + dt))
        return pos

    @property
    def _Bernier(self):
        """This function sizes the field based on the last year of operation, i.e. quadrants 2 and 4."""

        # initiate iteration
        H_prev = 0

        if self.H < 1:
            self.H = 50

        # Iterates as long as there is no convergence
        # (convergence if difference between depth in iterations is smaller than thresholdBoreholeDepth)
        while abs(self.H - H_prev) >= Borefield.thresholdBorholeDepth:
            # calculate the required gfunction values
            gfuncUniformT = self.gfunction(self.time, self.H)

            # calculate the thermal resistances
            Ra = (gfuncUniformT[2] - gfuncUniformT[1]) / (2 * pi * self.k_s)
            Rm = (gfuncUniformT[1] - gfuncUniformT[0]) / (2 * pi * self.k_s)
            Rd = (gfuncUniformT[0]) / (2 * pi * self.k_s)

            # calculate the totale borehole length
            L = (self.qa * Ra + self.qm * Rm + self.qh * Rd + self.qh * self._Rb) / abs(self.Tf - self.Tg)

            # updating the depth values
            H_prev = self.H
            self.H = L / self.numberOfBoreholes

        return self.H

    @property
    def _Carcel(self):
        """This function sizes the field based on the first year of operation, i.e. quadrants 1 and 3."""

        # initiate iteration
        H_prev = 0
        timeSteps = np.array([self.th, self.th + self.tm, self.tcm + self.th])
        if self.H < 1:
            self.H = 50

        # Iterates as long as there is no convergence
        # (convergence if difference between depth in iterations is smaller than thresholdBoreholeDepth)
        while abs(self.H - H_prev) >= Borefield.thresholdBorholeDepth:
            # get the gfunction values
            gfuncUniformT = self.gfunction(timeSteps, self.H)

            # calculate the thermal resistances
            Rpm = (gfuncUniformT[2] - gfuncUniformT[1]) / (2 * pi * self.k_s)
            Rcm = (gfuncUniformT[1] - gfuncUniformT[0]) / (2 * pi * self.k_s)
            Rh = (gfuncUniformT[0]) / (2 * pi * self.k_s)

            # calculate the total length
            L = (self.qh * self._Rb + self.qh * Rh + self.qm * Rcm + self.qpm * Rpm) / abs(self.Tf - self.Tg)

            # updating the depth values
            H_prev = self.H
            self.H = L / self.numberOfBoreholes
        return self.H

    def size(self, H_init: float, L2Sizing: bool = 1, quadrantSizing: int = 0, useConstantRb: bool = None):
        """This function lets the user chose between two sizing options.
        * The L2 sizing is the one explained in (Peere et al., 2021) and is quicker
        * The L3 sizing is a more general approach which is slower but more accurate
        - quadrantSizing lets you size the borefield according to a specific quadrant
        - useConstantRb makes sure that the self.useConstantRb = True.
        Note, the constant Rb* value will be overwritten!"""

        # sets the constant Rb
        useConstantRbBackup = self.useConstantRb
        self.useConstantRb = useConstantRb if useConstantRb is not None else self.useConstantRb

        result = self.sizeL2(H_init, quadrantSizing) if L2Sizing else self.sizeL3(H_init, quadrantSizing)

        self.Rb = self._Rb

        # reset useConstantRb
        self.useConstantRb = useConstantRbBackup
        return result

    def sizeL2(self, H_init: float, quadrantSizing: int = 0):
        """This function sizes the borefield of the given configuration according to the methodology explained in (Peere et al., 2021), which is a L2 method.
        When quadrantsizing is other than 0, it sizes the field based on the asked quadrant.
        It returns the borefield depth."""

        # initiate with a given depth
        self.H_init: float = H_init

        def sizeQuadrant1():
            self.calculateL3Params(False)  # calculate parameters
            return self._Carcel  # size

        def sizeQuadrant2():
            self.calculateL2Params(False)  # calculate parameters
            self.qa = self.qa
            return self._Bernier  # size

        def sizeQuadrant3():
            self.calculateL3Params(True)  # calculate parameters
            return self._Carcel  # size

        def sizeQuadrant4():
            self.calculateL2Params(True)  # calculate parameters
            self.qa = self.qa
            return self._Bernier  # size

        if quadrantSizing != 0:
            # size according to a specific quadrant
            if quadrantSizing == 1:
                self.H = sizeQuadrant1()
            elif quadrantSizing == 2:
                self.H = sizeQuadrant2()
            elif quadrantSizing == 3:
                self.H = sizeQuadrant3()
            else:
                self.H = sizeQuadrant4()
        else:
            # size accoring to the biggest quadrant
            # determine which quadrants are relevant
            if self.imbalance <= 0:
                # extraction dominated, so quadrants 1 and 4 are relevant
                quadrant1 = sizeQuadrant1()
                quadrant4 = sizeQuadrant4()
                self.H = max(quadrant1, quadrant4)

                if self.H == quadrant1:
                    self.limitingQuadrant = 1
                else:
                    self.limitingQuadrant = 4
            else:
                # injection dominated, so quadrants 2 and 3 are relevant
                quadrant2 = sizeQuadrant2()
                quadrant3 = sizeQuadrant3()
                self.H = max(quadrant2, quadrant3)

                if self.H == quadrant2:
                    self.limitingQuadrant = 2
                else:
                    self.limitingQuadrant = 3

        # check if the field is not shallow
        if self.H < self.thresholdWarningShallowField and self.printing:
            print(f"The field has a calculated depth of {round(self.H, 2)} m which is lower than the proposed minimum "
                  f"of {self.thresholdWarningShallowField} m.")
            print("Please change your configuration accordingly to have a not so shallow field.")

        return self.H

    def sizeL3(self, H_init: float, quadrantSizing: int = 0):
        """This functions sizes the borefield based on a L3 method."""

        # initiate with a given depth
        self.H_init: float = H_init

        if quadrantSizing != 0:
            # size according to a specific quadrant
            self.H = self._sizeL3quadrants(quadrantSizing)
        else:
            # size accoring to the biggest quadrant
            # determine which quadrants are relevant
            if self.imbalance <= 0:
                # extraction dominated, so quadrants 1 and 4 are relevant
                quadrant1 = self._sizeL3quadrants(1)
                quadrant4 = self._sizeL3quadrants(4)
                self.H = max(quadrant1, quadrant4)

                if self.H == quadrant1:
                    self.limitingQuadrant = 1
                else:
                    self.limitingQuadrant = 4
            else:
                # injection dominated, so quadrants 2 and 3 are relevant
                quadrant2 = self._sizeL3quadrants(2)
                quadrant3 = self._sizeL3quadrants(3)
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

    def _sizeL3quadrants(self, quadrant: int):
        """This function sizes based on the L3 method for a specific quadrant.
        It uses 24 thermal pulses for each year, while the L2-sizing method only uses 3 pulses for the whole simulation period.
        It returns a borefield depth."""

        # make a numpy array of the monthly average loads for the whole simulation period
        # in case of quadrants 1 and 3, the array can stop after the first year
        # in case of quadrants 2 and 4, we need the whole simulation period
        if quadrant == 1 or quadrant == 3:
            monthlyLoadArray = np.asarray(self.monthlyLoad)
            time = self.timeL3FirstYear
        else:
            monthlyLoadArray = np.asarray(self.monthlyLoad * self.simulationPeriod)
            time = self.timeL3LastYear

        # initiate iteration
        H_prev = 0

        if self.H < 1:
            self.H = 50

        # in case of quadrants 1 and 3, we need the first year only
        # in case of quadrants 2 and 4, we need the last year only
        if quadrant == 1 or quadrant == 3:
            relevantPeriod = (0, 12)
        else:
            relevantPeriod = (12 * (self.simulationPeriod - 1), 12 * self.simulationPeriod)

        # Iterates as long as there is no convergence
        # (convergence if difference between depth in iterations is smaller than thresholdBoreholeDepth)
        while abs(self.H - H_prev) >= Borefield.thresholdBorholeDepth:

            # set Rb value
            self.Rb = self._Rb

            # define and reset
            temperatureProfile = []

            # calculate the required gfunction values
            gfunc_uniform_T = self.gfunction(time, self.H)

            # calculate the gvalue for the peak
            gvaluePeak = self.gfunction(self.lengthPeak * 3600., self.H)

            # calculation of needed differences of the gfunction values. These are the weight factors in the calculation of Tb.
            # (Tb_i - Tg) * 120 boreholes * length  = 1/2pi k_s [ q_i * g(1 month) + q_(i-1)*[g(2 months)-g(1month)] + q_(i-2)*[g(3 months) - g(2 months)]]
            gvalueDifferences = [gfunc_uniform_T[i] if i == 0 else gfunc_uniform_T[i] - gfunc_uniform_T[i - 1] for i in
                                 range(len(gfunc_uniform_T))]

            # calculation of the differences in borehole wall temperature for every month i w.r.t. the Tg
            boreholeWallTemperature = []
            temp = []

            for i in range(len(monthlyLoadArray)):
                temp.insert(0, monthlyLoadArray[i] * 1000.)
                boreholeWallTemperature.append(np.dot(temp, gvalueDifferences[:i + 1]) / (2 * pi * self.k_s))

            # calculate the Tf = Tb + QR_b

            for i in range(relevantPeriod[0], relevantPeriod[1]):
                # in case of quadrants 1 and 2, we want the maximum temperature
                # in case of quadrants 3 and 4, we want the minimum temperature

                # influence of the average monthly load
                if quadrant == 1 or quadrant == 2:
                    temperatureProfile.append(
                        boreholeWallTemperature[i] + self.monthlyLoadCooling[i % 12] * 1000. * self.Rb)
                else:
                    temperatureProfile.append(
                        boreholeWallTemperature[i] - self.monthlyLoadHeating[i % 12] * 1000. * self.Rb)

                # influence of the peak load
                if quadrant == 1 or quadrant == 2:
                    temperatureProfile[i % 12] = temperatureProfile[i % 12] + (
                        (self.peakCooling[i % 12] - self.monthlyLoadCooling[i % 12]) if self.peakCooling[i % 12] >
                                                                                        self.monthlyLoadCooling[i % 12] \
                            else 0) * 1000. * (gvaluePeak[0] / (2 * pi * self.k_s) + self.Rb)
                else:
                    temperatureProfile[i % 12] = temperatureProfile[i % 12] - (
                        (self.peakHeating[i % 12] - self.monthlyLoadHeating[i % 12]) if self.peakHeating[i % 12] >
                                                                                        self.monthlyLoadHeating[i % 12] \
                            else 0) * 1000. * (gvaluePeak[0] / (2 * pi * self.k_s) + self.Rb)

            # convert to temperature
            temp = [i / self.numberOfBoreholes / self.H + self.Tg for i in temperatureProfile]

            H_prev = self.H
            if quadrant == 1 or quadrant == 2:
                # maximum temperature
                # convert back to required length
                self.H = abs(temperatureProfile[temp.index(max(temp))] / (self.Tf_H - self.Tg) / self.numberOfBoreholes)
            else:
                # minimum temperature
                # convert back to required length
                self.H = abs(temperatureProfile[temp.index(min(temp))] / (self.Tf_C - self.Tg) / self.numberOfBoreholes)

        return self.H

    def calculateMonthlyLoad(self):
        """This function calculates the average monthly load in kW"""
        self.monthlyLoad = [(-self.baseloadHeating[i] + self.baseloadCooling[i]) / Borefield.UPM for i in range(12)]

    def setBaseloadHeating(self, baseload: list):
        """This function defines the baseLoad in heating both in an energy as in an average power perspective"""
        self.baseloadHeating = [i if i >= 0 else 0 for i in baseload]  # kWh
        self.monthlyLoadHeating = list(map(lambda x: x / Borefield.UPM, self.baseloadHeating))  # kW
        self.calculateMonthlyLoad()
        self.calculateImbalance()

        # new peak heating if baseLoad is larger than the peak
        self.setPeakHeating([max(self.peakHeating[i], self.monthlyLoadHeating[i]) for i in range(12)])

    def setBaseloadCooling(self, baseload: list):
        """This function defines the baseLoad in cooling both in an energy as in an average power perspective"""
        self.baseloadCooling = [i if i >= 0 else 0 for i in baseload]  # kWh
        self.monthlyLoadCooling = list(map(lambda x: x / Borefield.UPM, self.baseloadCooling))  # kW
        self.calculateMonthlyLoad()
        self.calculateImbalance()

        # new peak cooling if baseLoad is larger than the peak
        self.setPeakCooling([max(self.peakCooling[i], self.monthlyLoadCooling[i]) for i in range(12)])

    def setPeakHeating(self, peakload: list):
        """This function sets the peak heating to peakLoad"""
        self.peakHeating = [i if i >= 0 else 0 for i in peakload]

    def setPeakCooling(self, peakload: list):
        """This function sets the peak cooling to peak load"""
        self.peakCooling = [i if i >= 0 else 0 for i in peakload]

    @property
    def investementCost(self):
        """This function calculates the investement cost based on a cost profile lineair to the total borehole length."""
        return np.polyval(self.costInvestement, self.H * self.numberOfBoreholes)

    def calculateImbalance(self):
        """This function calculates the imbalance of the field.
        A positive imbalance means that the field is injection dominated, i.e. it heats up every year."""
        self.imbalance = functools.reduce(lambda x, y: x + y, self.baseloadCooling) - \
                         functools.reduce(lambda x, y: x + y, self.baseloadHeating)

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
        self.tcm = (monthIndex + 1) * Borefield.UPM * 3600
        self.tpm = monthIndex * Borefield.UPM * 3600

        return monthIndex

    def calculateTemperatures(self, depth: float = None):
        """Calculate all the temperatures without plotting the figure. When depth is given, it calculates it for a given depth."""
        self._printTemperatureProfile(figure=False, H=depth)

    def printTemperatureProfile(self, legend: bool = True):
        """This function plots the temperature profile for the calculated depth."""
        self._printTemperatureProfile(legend=legend)

    def printTemperatureProfileFixedDepth(self, depth, legend: bool = True):
        """This function plots the temperature profile for a fixed depth depth."""
        self._printTemperatureProfile(legend=legend, H=depth)

    def _printTemperatureProfile(self, legend: bool = True, H: float = None, figure: bool = True):
        """
        This function calculates the temperature evolution in the borefield using temporal superposition.
        It is possible to calculate this for a certain depth H, otherwise self.H will be used.
        If Figure = True than a figure will be plotted.
        """
        H_backup = self.H
        if H is not None:
            self.H = H
        # set Rb* value
        self.Rb = self._Rb

        self.H = H_backup

        # making a numpy array of the monthly balance (self.montlyLoad) for a period of self.simulationPeriod years [kW]
        monthlyLoadsArray = np.asarray(self.monthlyLoad * self.simulationPeriod)

        # self.gfunction is a function that uses the precalculated data to interpolate the correct values of the gfunction.
        # this dataset is checked over and over again and is correct
        gValues = self.gfunction(self.timeL3LastYear, self.H if H is None else H)

        # the gfunction value of the peak with lengthPeak hours
        gValuePeak = self.gfunction(self.lengthPeak * 3600., self.H if H is None else H)

        # calculation of needed differences of the gfunction values. These are the weight factors in the calculation of Tb.
        gValueDifferences = [gValues[i] if i == 0 else gValues[i] - gValues[i - 1] for i in range(len(gValues))]

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
            timeArray = [i / 12 / 730. / 3600. for i in self.timeL3LastYear]

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

    def gfunction(self, timeValue: list, H: float):
        """This function calculated the gfunction based on interpolation of the precalculated data."""

        # set folder if no GUI is used
        folder = '.' if self.GUI else FOLDER
        # get the name of the data fileImport
        if self.customGfunction is None:
            name = f'{self.configurationString(self.N_1, self.N_2)}.pickle'
        else:
            name = f'{self.customGfunction}.pickle'

        # check if datafile exists
        if not os.path.isfile(f'{folder}/Data/{name}'):
            print(name)
            raise Exception('There is no precalculated data available. Please use the createCustomDatafile.')

        # load data fileImport
        data = pickle.load(open(f'{folder}/Data/{name}', "rb"))

        # remove the time value
        Time = Borefield.defaultTimeArray
        try:
            data.pop("Time")
        except KeyError:
            data = data

        if not self.gfunctionInterpolationArray:
            # if no interpolation array exists, it creates one
            def makeInterpolationListDefault():
                """This function creates an interpolation list and saves it under gfunctionInterpolationArray."""

                B_array = list(data.keys())
                ks_array = list(data[B_array[0]].keys())
                H_array = list(data[B_array[0]][ks_array[0]].keys())
                self.H_max = max(H_array)
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

            def makeInterpolationListCustom():
                """This function creates an interpolation list from a custom dataset and saves it under gfunctionInterpolationArray."""

                H_array = list(data["Data"].keys())
                H_array.sort()

                points = (H_array, Time)

                values = []

                for H in H_array:
                    values.append(data["Data"][H])

                self.gfunctionInterpolationArray = (points, values)

            if self.customGfunction is None:
                makeInterpolationListDefault()
            else:
                makeInterpolationListCustom()
        try:
            if self.customGfunction is None:
                # interpolate
                points, values = self.gfunctionInterpolationArray
                if not isinstance(timeValue, float):
                    # multiple values are requested
                    gvalue = interpolate.interpn(points, values,
                                                 np.array([[self.B, self.k_s, H, t] for t in timeValue]))
                else:
                    # only one value is requested
                    gvalue = interpolate.interpn(points, values, np.array([self.B, self.k_s, H, timeValue]))
            else:
                # interpolate
                points, values = self.gfunctionInterpolationArray
                if not isinstance(timeValue, float):
                    # multiple values are requested
                    gvalue = interpolate.interpn(points, values, np.array([[H, t] for t in timeValue]))
                else:
                    # only one value is requested
                    gvalue = interpolate.interpn(points, values, np.array([H, timeValue]))
            return gvalue
        except ValueError as e:
            if self.printing:
                if self.simulationPeriod > Borefield.maxSimulationPeriod:
                    print(f'Your requested simulationperiod of {self.simulationPeriod} years is beyond the limit of '
                          f'{Borefield.maxSimulationPeriod}) years of the precalculated data.')
                else:
                    print(f"Your requested depth of {H} m is beyond the limit {self.H_max} m of the precalculated data.")
                    print("Please change your borefield configuration accordingly.")
                print("-------------------------")
                print("This calculation stopped.")
            raise ValueError

    def createCustomDataset(self, customBorefield: str, nameDatafile: str, nSegments: int = 12,
                            timeArray: list = defaultTimeArray, depthArray: list = defaultDepthArray):
        """This function makes a datafile for a given custom borefield."""
        # set folder if no GUI is used
        folder = '.' if self.GUI else FOLDER
        # make filename
        name = f'{nameDatafile}.pickle'
        # check if fileImport exists
        if not os.path.isfile(f"Data/{name}"):
            # does not exist, so create
            pickle.dump(dict([]), open(f'{folder}/Data/{name}', "wb"))
        else:
            raise Exception(f"The dataset {name} already exists. Please chose a different name.")

        data = pickle.load(open(f'{folder}/Data/{name}', "rb"), encoding='latin1')

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
        print(f"A new dataset with name {name} has been created in {os.path.dirname(os.path.realpath(__file__))}\Data.")
        pickle.dump(data, open(f'{folder}/Data/{name}', "wb"))

    def loadHourlyProfile(self, filePath: str = None, header: bool = True, seperator: str = ";",
                          firstColumnHeating: bool = True):
        """This function loads in an hourly load profile. It opens a csv and asks for the relevant column where the data is in.
        firstColumnHeating is true if the first column in the datafile is for the heating values.
        header is true if there is a header in the csv fileImport.
        seperator is the seperator in the csv fileImport."""

        # if there is no given location, open a filedialog box
        if filePath is None:
            filePath = filedialog.askopenfilename(title="Select csv-fileImport with hourly load.")

        if header:
            header: int = 0
        else:
            header = None
        import pandas as pd
        db = pd.read_csv(filePath, sep=seperator, header=header)

        if firstColumnHeating:
            self.hourlyHeatingLoad = db.iloc[:, 0].tolist()
            self.hourlyCoolingLoad = db.iloc[:, 1].tolist()
        else:
            self.hourlyHeatingLoad = db.iloc[:, 1].tolist()
            self.hourlyCoolingLoad = db.iloc[:, 0].tolist()

    def convertHourlyToMonthly(self, peakCoolLoad: float = None, peakHeatLoad: float = None):
        """This function converts an hourly loadprofile to the monthly profiles used in the sizing."""

        try:
            self.hourlyCoolingLoad[0]
            self.hourlyHeatingLoad[0]
        except:
            self.loadHourlyProfile()

        if peakCoolLoad is None:
            peakCoolLoad = max(self.hourlyCoolingLoad)
        if peakHeatLoad is None:
            peakHeatLoad = max(self.hourlyHeatingLoad)

        # calculate peak and base loads
        self.setPeakCooling(self._reduceToPeakLoad(self.hourlyCoolingLoad, peakCoolLoad))
        self.setPeakHeating(self._reduceToPeakLoad(self.hourlyHeatingLoad, peakHeatLoad))
        self.setBaseloadCooling(self._reduceToMonthLoad(self.hourlyCoolingLoad, peakCoolLoad))
        self.setBaseloadHeating(self._reduceToMonthLoad(self.hourlyHeatingLoad, peakHeatLoad))

    def _reduceToMonthLoad(self, load: list, peak: float):
        """This function calculates the monthly load based, taking a maximum peak value into account."""
        monthLoad = []
        for i in range(12):
            temp = load[Borefield.hourlyLoadArray[i]:Borefield.hourlyLoadArray[i + 1] + 1]
            monthLoad.append(functools.reduce(lambda x, y: x + y, [min(j, peak) for j in temp]))
        return monthLoad

    def _reduceToPeakLoad(self, load: list, peak: float):
        """This function calculates the monthly peak load, taking a maximum peak value into account."""
        peakLoad = []
        for i in range(12):
            temp = load[Borefield.hourlyLoadArray[i]:Borefield.hourlyLoadArray[i + 1] + 1]
            peakLoad.append(max([min(j, peak) for j in temp]))
        return peakLoad

    def optimiseLoadProfile(self, depth: float = 150, printResults: bool = False):
        """This function optimises the load based on the given borefield and the given hourly load.
        It does so based on a load-duration curve."""

        # since the depth does not change, the Rb* value is constant
        # set to use a constant Rb* value but save the initial parameters
        Rb_backup = self.Rb
        if not self.useConstantRb:
            self.Rb = self.calculateRb()
        useConstantRb_backup = self.useConstantRb
        self.useConstantRb = True

        # if no hourly profile is given, load one
        if self.hourlyCoolingLoad == []:
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
            self.convertHourlyToMonthly(peakCoolLoad, peakHeatLoad)

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

        # calculate the resulting hourly profile that can be put on the field
        self.hourlyCoolingLoadOnTheBorefield = [max(i, peakCoolLoad) for i in self.hourlyCoolingLoad]
        self.hourlyHeatingLoadOnTheBorefield = [max(i, peakHeatLoad) for i in self.hourlyHeatingLoad]

        # calculate the resulting hourly profile that cannot be put on the field
        self.hourlyCoolingLoadExternal = [max(0, i - peakCoolLoad) for i in self.hourlyCoolingLoad]
        self.hourlyHeatingLoadExternal = [max(0, i - peakHeatLoad) for i in self.hourlyHeatingLoad]

        # calculate the resulting monthly profile that cannot be put on the field
        temp = self._reduceToMonthLoad(self.hourlyCoolingLoad, max(self.hourlyCoolingLoad))
        self.monthlyLoadCoolingExternal = [temp[i] - self.baseloadCooling[i] for i in range(12)]
        temp = self._reduceToMonthLoad(self.hourlyHeatingLoad, max(self.hourlyHeatingLoad))
        self.monthlyLoadHeatingExternal = [temp[i] - self.baseloadHeating[i] for i in range(12)]
        temp = self._reduceToPeakLoad(self.hourlyCoolingLoad, max(self.hourlyCoolingLoad))
        self.peakCoolingExternal = [temp[i] - self.peakCooling[i] for i in range(12)]
        temp = self._reduceToPeakLoad(self.hourlyHeatingLoad, max(self.hourlyHeatingLoad))
        self.peakHeatingExternal = [temp[i] - self.peakHeating[i] for i in range(12)]

        # restore the initial parameters
        self.Rb = Rb_backup
        self.useConstantRb = useConstantRb_backup
        if printResults:
            # print results
            print("The peak load heating is: ", int(peakHeatLoad), "kW, leading to",
                  np.round(np.sum(self.baseloadHeating), 2), "kWh of heating.")
            print("This is", np.round(np.sum(self.baseloadHeating) / np.sum(self.hourlyHeatingLoad) * 100, 2),
                  "% of the total heating load.")
            print("Another", np.round(-np.sum(self.baseloadHeating) + np.sum(self.hourlyHeatingLoad), 2),
                  "kWh of heating should come from another source, with a peak of",
                  int(max(self.hourlyHeatingLoad)) - int(peakHeatLoad), "kW.")
            print("------------------------------------------")
            print("The peak load cooling is: ", int(peakCoolLoad), "kW, leading to",
                  np.round(np.sum(self.baseloadCooling), 2), "kWh of cooling.")
            print("This is", np.round(np.sum(self.baseloadCooling) / np.sum(self.hourlyCoolingLoad) * 100, 2),
                  "% of the total cooling load.")
            print("Another", np.round(-np.sum(self.baseloadCooling) + np.sum(self.hourlyCoolingLoad), 2),
                  "kWh of cooling should come from another source, with a peak of",
                  int(max(self.hourlyCoolingLoad)) - int(peakCoolLoad), "kW.")

            # plot results
            self._printTemperatureProfile(H=depth)

    def size_complete_field_robust(self, h_max: float, l_1: float, l_2: float, b_min: float = 3.0, b_max: float = 9.0,
                                   L2Sizing: bool = True, useConstantRb: bool = False) -> list:
        """
        function to size the minimal number of bore field by bore field length and width on a robust and more
        time-consuming way
        :param h_max: maximal borehole depth [m]
        :param l_1: maximal width of borehole field [m]
        :param l_2: maximal length of borehole field [m]
        :param b_min: minimal borehole spacing [m]
        :param b_max: maximal borehole spacing [m]
        :param L2Sizing: boolean to check if level two or level three sizing method should be used
        :param useConstantRb: boolean to check if a constant borehole resistance should be used
        :return: list of possible combinations. An Empty list is returned if no results is found
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
        self.printing: bool = False
        # minimal product to break loop
        product_min = 0
        # start loop over borehole spacing
        for B in np.arange(b_max, b_min * 0.99999, -0.5):
            # calculate maximal number of boreholes in length and width direction
            n_1_max = min(int(l_1 / B), 20)
            n_2_max = min(int(l_2 / B), 20)
            # set borehole spacing
            self.B = B
            # start loop over number of boreholes in length and width direction
            for N_1 in range(n_1_max, 0, -1):
                for N_2 in range(min(n_2_max, N_1), 0, -1):
                    # reset bore field values for sizing
                    self._resetForSizing(N_1, N_2)
                    # calculate number of total boreholes which should be minimal
                    product = N_1 * N_2
                    # continue loop if product is higher than current maxima to avoid calculation
                    if product > n_n_max:
                        continue
                    # break loop id product is less than the current minima to avoid calculation
                    if product < product_min:
                        break
                    # try to size current bore field configuration else set minimal product
                    try:
                        depth = self.size(h_max, L2Sizing, useConstantRb=useConstantRb)
                    except ValueError:
                        product_min = product
                        continue
                    # break loop if depth is higher than the maxima
                    if depth > h_max:
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
        combo = [[i[1], i[0], i[2], i[3]] for i in combo] if l_2_bigger_then_l_1 else combo
        self.N_1 = combo[0][0]
        self.N_2 = combo[0][1]
        self.B = combo[0][2]
        self.H = combo[0][3]
        self._resetForSizing(self.N_1, self.N_2)
        self.printing: bool = True
        self.combo = combo
        return combo

    def size_complete_field_fast(self, HMax: float, L1: float, L2: float, BMin: float = 3.0, BMax: float = 9.0,
                                 L2Sizing: bool = True, useConstantRb: bool = False) -> list:
        """
        function to size the minimal number of borefield by borefield length and width on a fast and not robust way.
        There are possible solution that can not be found
        :param HMax: maximal borehole depth [m]
        :param L1: maximal width of borehole field [m]
        :param L2: maximal length of borehole field [m]
        :param BMin: minimal borehole spacing [m]
        :param BMax: maximal borehole spacing [m]
        :param L2Sizing: boolean to check if level two or level three sizing method should be used
        :param useConstantRb: boolean to check if a constant borehole resistance should be used
        :return: list of possible combinations. An Empty list is returned if no results is found
        """
        L2BiggerThenL1: bool = L2 > L1
        (L1, L2) = (L2, L1) if L2BiggerThenL1 else (L1, L2)
        n_n_max_start: int = 21 * 21
        n_n_max: int = n_n_max_start
        combo: list = [[21, 21, 9, HMax]]
        self.printing: bool = False
        for B in np.arange(BMax, BMin * 0.99999, -0.5):
            N1Max = min(int(L1 / B), 20)
            N2Max = min(int(L2 / B), 20)
            self._resetForSizing(N1Max, N2Max)
            self.N_1 = N1Max
            self.B = B
            product_old = self.N_1 * self.N_2
            try:
                depth = self.size(HMax, L2Sizing, useConstantRb=useConstantRb)
                numberBoreholes = int(depth * product_old / HMax) + 1
                res = self._calcNumberHoles(numberBoreholes, N1Max, N2Max)
                self._resetForSizing(res[0][0], res[0][1])
                product_new = self.N_1 * self.N_2
                counter = 0
                from numpy import sign
                while product_old != product_new:
                    gradient = int(0.51 * (product_new - product_old)) if counter > 4 else int(product_new -
                                                                                               product_old)
                    product_new = product_old + sign(gradient) * min(abs(gradient), 1)
                    depth = self.size(HMax, L2Sizing, useConstantRb=useConstantRb)
                    numberBoreholes = int(depth * product_new / HMax) + 1
                    res = self._calcNumberHoles(numberBoreholes, N1Max, N2Max)
                    self._resetForSizing(res[0][0], res[0][1])
                    product_old = self.N_1 * self.N_2
                    counter += 1
                    if counter > 20 and depth < HMax:
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
                            self._resetForSizing(i[0], i[1])
                            self.size(HMax, L2Sizing, useConstantRb=useConstantRb)
                            if self.H < HMax:
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
                            self._resetForSizing(i[0], i[1])
                            self.size(HMax, L2Sizing, useConstantRb=useConstantRb)
                            if self.H < HMax:
                                combo.append([i[0], i[1], B, self.H])
                    else:
                        combo += [[res[0][0], res[0][1], B, self.H]]

            except ValueError:
                break

        if n_n_max == n_n_max_start:
            return []
        combo = [[i[1], i[0], i[2], i[3]] for i in combo] if L2BiggerThenL1 else combo
        self.N_1 = combo[0][1]
        self.N_2 = combo[0][0]
        self.B = combo[0][2]
        self.H = combo[0][3]
        self._resetForSizing(self.N_1, self.N_2)
        self.printing: bool = True
        self.combo = combo
        return combo

    def _resetForSizing(self, N_1: int, N_2: int) -> None:
        """
        function to reset borehole
        :param N_1: width of rectangular field (#)
        :param N_2: length of rectangular field (#)
        :return:
        """
        # set number of boreholes
        self.N_1, self.N_2 = N_1, N_2
        # reset interpolation array
        self.gfunctionInterpolationArray = []
        # set number of boreholes because number of boreholes has changed
        self.setNumberOfBoreholes()

    @staticmethod
    def _calcNumberHoles(nMin: int, N1Max: int, N2Max: int) -> list:
        """
        calculation for number of boreholes which is higher than n but minimal total number
        :param nMin: minimal number of boreholes
        :param N1Max: maximal width of rectangular field (#)
        :param N2Max: maximal length of rectangular field (#)
        :return: list of possible solutions
        """
        # set default result
        res = [(20, 20)]
        # set maximal number
        maxVal = 20 * 20
        # loop over maximal number in length and width
        for i in range(1, N1Max + 1):
            for j in range(1, min(N2Max, i) + 1):
                # determine current number
                currentNumber: int = i * j
                # save number of boreholes  and maximal value if is lower than current maximal value and higher than
                # minimal value
                if nMin <= currentNumber < maxVal:
                    res = [(i, j)]
                    maxVal = currentNumber
                # also append combination if current number is equal to current maximal value
                elif currentNumber == maxVal:
                    res.append((i, j))
        # return list of possible solutions
        return res
