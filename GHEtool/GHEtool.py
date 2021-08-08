import numpy as np
import pickle
from scipy import interpolate,pi
import pygfunction as gt
import os.path
import matplotlib.pyplot as plt
import functools

def timeValues():
    """This function calculates the default time values for the gfunction."""
    dt = 3600.  # Time step (s)
    tmax = 20. * 8760. * 3600.  # Maximum time (s)
    Nt = int(np.ceil(tmax / dt))  # Number of time steps

    # Load aggregation scheme
    LoadAgg = gt.load_aggregation.ClaessonJaved(dt, tmax)

    return LoadAgg.get_times_for_simulation()


def configurationString(N_1,N_2):
    """This functions returns the filename for the given configuration N_1, N_2."""
    string = str(max(N_1,N_2)) + "x" + str(min(N_1,N_2))
    return string


class Borefield():

    UPM = 730.
    threshold_temperatuur = 0.05
    threshold_passief_koelen = 15.5
    thresholdTemperature = 0.05  # threshold for iteration
    thresholdSoilConductivity = 0.05  # W/mK
    thresholdBoreholeSpacing = 0.5  # m
    thresholdBoreholeDepth = 25  # m

    # define default values
    defaultInvestement = [35, 0]  # 35 EUR/m
    defaultLengthPeak = 6  # hours
    defaultDepthArray = [1]+list(range(25, 201, 25))  # m
    defaultTimeArray = timeValues()  # sec
    defaultMelden = True

    gfunctionInterpolationArray=[]

    def __init__(self, simulationPeriod, numberOfBoreholes, peakHeating=[0] * 12, peakCooling=[0] * 12,
                 baseloadHeating=[0] * 12, baseloadCooling=[0] * 12, investementCost=None,borefield=None):
        """This function initiates the Borefield class"""

        # initiate vars
        self.baseloadHeating = [0] * 12
        self.baseloadCooling = [0] * 12

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

        self.H = 0

    def setNumberOfBoreholes(self,numberOfBoreholes):
        """This functions sets the number of boreholes"""
        self.numberOfBoreholes = numberOfBoreholes

    def setBorefield(self, borefield=None):
        """This function sets the borefield configuration. When no input, an empty array of length N_1 * N_2 will be made"""
        if borefield==None:
            pass
        else:
            self.borefield = borefield
            self.setNumberOfBoreholes(len(borefield))

    def setInvestementCost(self, investementCost=defaultInvestement):
        """This function sets the investement cost. This is linear with respect to the total field length."""
        self.costInvestement = investementCost

    def setLengthPeak(self, length=defaultLengthPeak):
        """This function sets the length of the peak to length."""
        self.lengthPeak = length
        self.th = length * 3600.  # length of peak in seconds

    def setGroundParameters(self,data):
        # Borehole dimensions
        self.D = data["D"]  # Borehole buried depth (m)
        self.H = data["H"]  # Borehole length (m)
        self.r_b = data["r_b"]  # Borehole radius (m)
        self.B = data["B"]  # Borehole spacing (m)

        self.N_1 = data["N_1"]
        self.N_2 = data["N_2"]

        # Pipe dimensions
        self.rp_out = data["rp_out"]  # Pipe outer radius (m)
        self.rp_in = data["rp_in"]  # Pipe inner radius (m)
        self.D_s = data["D_s"]  # Shank spacing (m)
        self.epsilon = data["epsilon"]  # Pipe roughness (m)
        self.Rb =data["Rb"]

        # Pipe positions
        # Single U-tube [(x_in, y_in), (x_out, y_out)]
        self.pos_pipes = data["pos_pipes"]

        # Ground properties
        self.alpha = data["alpha"]  # Ground thermal diffusivity (m2/s)
        self.k_s = data["k_s"]  # Ground thermal conductivity (W/m.K)
        self.Tg = data["Tg"]    # Grondtemperatuur (c)

        # Grout properties
        self.k_g = data["k_g"]  # Grout thermal conductivity (W/m.K)

        # Pipe properties
        self.k_p = data["k_p"]  # Pipe thermal conductivity (W/m.K)

        # Fluid properties
        self.m_flow = data["m_flow"]  # Total fluid mass flow rate (kg/s)
        self.cp_f = data["cp_f"]  # Fluid specific isobaric heat capacity (J/kg.K)
        self.den_f = data["den_f"]  # Fluid density (kg/m3)
        self.visc_f = data["visc_f"]  # Fluid dynamic viscosity (kg/m.s)
        self.k_f = data["k_f"]  # Fluid thermal conductivity (W/m.K)

        # Number of segments per borehole
        self.nSegments = data["nSegments"]
        self.ty = self.simulationPeriod * 8760.*3600
        self.tm = Borefield.UPM * 3600.
        self.td = 6*3600.
        self.time = np.array([self.td, self.td + self.tm, self.ty + self.tm + self.td])

    def setMaxGroundTemperature(self, temp):
        """This function sets the maximal ground temperature to temp"""
        self.Tf_H = temp

    def setMinGroundTemperature(self, temp):
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
        # (convergence if difference between depth in iterations is smaller than thresholTemperature)
        while abs(self.H - H_prev) >= Borefield.thresholdTemperature:
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
        timeSteps = np.array([self.th, self.th + self.tm, self.tcm + self.th])
        if self.H < 1:
            self.H = 50

        # Iterates as long as there is no convergence
        # (convergence if difference between depth in iterations is smaller than thresholTemperature)
        while abs(self.H - H_prev) >= Borefield.thresholdTemperature:
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

    def size(self,H_init):

        """This function sizes the borefield of the given configuration according to the methodology explained in (Peere et al., 2021).
        It returns the borefield depth."""

        # initiate with a given depth
        self.H_init = H_init

        def sizeQuadrant1():
            self.calculateL3Params(False)  # calculate parameters
            return self._Carcel  # size

        def sizeQuadrant2():
            self.calculateL2Params(False)  # calculate parameters
            self.qa = self.qa
            return self._Bernier  # size

        def sizeQuadrant3():
            self.calculateL3Params(True)  # calculate parameters
            return  self._Carcel  # size

        def sizeQuadrant4():
            self.calculateL2Params(True)  # calculate parameters
            self.qa = self.qa
            return self._Bernier  # size

        if self.imbalance<=0:
            # extraction dominated, so quadrants 1 and 4 are relevant
            self.H = max(sizeQuadrant1(),sizeQuadrant4())
        else:
            # injection dominated, so quadrants 2 and 3 are relevant
            self.H = max(sizeQuadrant2,sizeQuadrant3)

        return self.H


    def calculateMontlyLoad(self):
        """This function calculates the average monthly load in kW"""
        self.montlyLoad = [(-self.baseloadHeating[i] + self.baseloadCooling[i]) / Borefield.UPM for i in range(12)]

    def setBaseloadHeating(self, baseload):
        """This function defines the baseload in heating both in an energy as in an average power perspective"""
        self.baseloadHeating = [i if i >= 0 else 0 for i in baseload]  # kWh
        self.monthlyLoadHeating = list(map(lambda x: x / Borefield.UPM, self.baseloadHeating)) # kW
        self.calculateMontlyLoad()
        self.calculateImbalance()

        # new peak heating if baseload is larger than the peak
        self.setPeakHeating([max(self.peakHeating[i], self.monthlyLoadHeating[i]) for i in range(12)])

    def setBaseloadCooling(self, baseload):
        """This function defines the baseload in cooling both in an energy as in an average power perspective"""
        self.baseloadCooling = [i if i >= 0 else 0 for i in baseload]  # kWh
        self.monthlyLoadCooling = list(map(lambda x: x / Borefield.UPM, self.baseloadCooling))  # kW
        self.calculateMontlyLoad()
        self.calculateImbalance()

        # new peak cooling if baseload is larger than the peak
        self.setPeakCooling([max(self.peakCooling[i],self.monthlyLoadCooling[i]) for i in range(12)])

    def setPeakHeating(self, peakload):
        """This function sets the peak heating to peakload"""
        self.peakHeating = [i if i >= 0 else 0 for i in peakload]

    def setPeakCooling(self, peakload):
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
                         functools.reduce(lambda x, y: x + y,self.baseloadHeating)

    def calculateL2Params(self, HC):
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

        else:
            # limited by injection load

            # temperature limit set to maximum temperature
            self.Tf = self.Tf_H

            # Select month with highest peak load and take both the peak and average load from that month
            monthIndex = self.peakCooling.index(max(self.peakCooling))
            self.qm = self.montlyLoad[monthIndex] * 1000.
            self.qh = max(self.peakCooling) * 1000.

    def calculateL3Params(self, HC, monthIndex=None):
        """This function calculates the parameters for the sizing based on the first year of operation"""

        if HC:
            # limited by extraction load

            # temperature limit is set to the minimum temperature
            self.Tf = self.Tf_C

            # Select month with highest peak load and take both the peak and average load from that month
            monthIndex = self.peakHeating.index(max(self.peakHeating)) if monthIndex == None else monthIndex
            self.qh = max(self.peakHeating) * 1000.

            self.qm = self.montlyLoad[monthIndex] * 1000.

            if monthIndex < 1:
                self.qpm = 0
            else:
                self.qpm = functools.reduce(lambda x, y: x + y, self.montlyLoad[:monthIndex]) * 1000. / (monthIndex + 1)

            self.qm = -self.qm
        else:
            # limited by injection

            # temperature limit set to maximum temperatue
            self.Tf = self.Tf_H

            # Select month with highest peak load and take both the peak and average load from that month
            monthIndex = self.peakCooling.index(max(self.peakCooling)) if monthIndex == None else monthIndex
            self.qh = max(self.peakCooling) * 1000.

            self.qm = self.montlyLoad[monthIndex] * 1000.
            if monthIndex < 1:
                self.qpm = 0
            else:
                self.qpm = functools.reduce(lambda x, y: x + y, self.montlyLoad[:monthIndex]) * 1000. / (monthIndex + 1)
        self.tcm = (monthIndex + 1) * Borefield.UPM * 3600
        self.tpm = monthIndex * Borefield.UPM * 3600

        return monthIndex

    def calculateTemperatures(self,depth=None):
        """Calculate all the temperatures without plotting the figure. When depth is given, it calculates it for a given depth."""
        self._printTemperatureProfile(figure=False,H=depth)

    def printTemperatureProfile(self,legend=True):
        """This function plots the temperature profile for the calculated depth."""
        self._printTemperatureProfile(legend=legend)

    def printTemperatureProfileFixedDepth(self,depth,legend=True):
        """This function plots the temperature profile for a fixed depth depth."""
        self._printTemperatureProfile(legend=legend,H=depth)

    def _printTemperatureProfile(self, legend=True, H=None,figure=True):
        """
        This function would calculate a new length of the borefield using temporal superposition.
        Now it justs outputs the temperature graphs
        """

        # making a numpy array of the monthly balance (self.montlyLoad) for a period of 20 years [kW]
        monthlyLoadsArray = np.asarray(self.montlyLoad * self.simulationPeriod)

        # calculation of all the different times at which the gfunction should be calculated.
        # this is equal to 'UPM' hours a month * 3600 seconds/hours for the simulationPeriod
        timeForgValues = [i * Borefield.UPM * 3600. for i in range(1, 12 * self.simulationPeriod + 1)]

        # self.gfunction is a function that uses the precalculated data to interpolate the correct values of the gfunction.
        # this dataset is checked over and over again and is correct
        gValues = self.gfunction(timeForgValues, self.H if H == None else H)

        # the gfunction value of the peak with lengthPeak hours
        gValuePeak = self.gfunction(self.lengthPeak * 3600., self.H if H == None else H)

        # calculation of needed differences of the gfunction values. These are the weight factors in the calculation of Tb.
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
        Tb = [i / (2 * pi * self.k_s) / ((self.H if H == None else H) * self.numberOfBoreholes) + self.Tg for i in results]

        # now the Tf will be calculated based on
        # Tf = Tb + Q * R_b
        for i in range(240):
            resultsCooling.append(Tb[i] + self.monthlyLoadCooling[i % 12] * 1000. * (
                        self.Rb / self.numberOfBoreholes / (self.H if H == None else H)))
            resultsHeating.append(Tb[i] - self.monthlyLoadHeating[i % 12] * 1000. * (
                        self.Rb / self.numberOfBoreholes / (self.H if H == None else H)))
            resultsMonthCooling.append(Tb[i] + self.monthlyLoadCooling[i % 12] * 1000. * (
                        self.Rb / self.numberOfBoreholes / (self.H if H == None else H)))
            resultsMonthHeating.append(Tb[i] - self.monthlyLoadHeating[i % 12] * 1000. * (
                        self.Rb / self.numberOfBoreholes / (self.H if H == None else H)))

        # extra sommation if the gfunction value for the peak is included

        for i in range(240):
            resultsPeakCooling.append(resultsCooling[i] + ((self.peakCooling[i % 12] - self.monthlyLoadCooling[i % 12] if
                                                   self.peakCooling[i % 12] > self.monthlyLoadCooling[
                                                       i % 12] else 0) * 1000. * (
                                                              gValuePeak[0] / self.k_s / 2 / pi + self.Rb)) / self.numberOfBoreholes / (self.H if H == None else H))
            resultsPeakHeating.append(resultsHeating[i] - ((self.peakHeating[i % 12] - self.monthlyLoadHeating[i % 12] if
                                                   self.peakHeating[i % 12] > self.monthlyLoadHeating[
                                                       i % 12] else 0) * 1000. * (
                                                              gValuePeak[0] / self.k_s / 2 / pi + self.Rb)) / self.numberOfBoreholes / (self.H if H == None else H))

        # save temperatures under variable
        self.resultsCooling = resultsCooling
        self.resultsHeating = resultsHeating
        self.resultsPeakHeating = resultsPeakHeating
        self.resultsPeakCooling = resultsPeakCooling
        self.resultsMonthCooling = resultsMonthCooling
        self.resultsMonthHeating = resultsMonthHeating

        ## initiate figure
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
            ax1.step(timeArray, Tb, 'k-', where="pre", lw=1.5, label="Tb")
            ax1.step(timeArray, resultsMonthCooling, color='b', linestyle="dashed", where="pre", lw=1.5, label='Tf basis cooling')
            ax1.step(timeArray, resultsMonthHeating, color='r', linestyle="dashed", where="pre", lw=1.5, label='Tf basis heating')
            ax1.hlines(self.Tf_C, 0, 20, colors='r', linestyles='dashed', label='', lw=1)
            ax1.hlines(self.Tf_H, 0, 20, colors='b', linestyles='dashed', label='', lw=1)
            ax1.set_xticks(range(0, 21, 2))

            # Plot legend
            if legend:
                ax1.legend()
            ax1.set_xlim(left=0, right=20)
            plt.show()

    def gfunction(self, timeValue, H):
        """This function calculated the gfunction based on interpolation of the precalculated data"""

        def relevance(H_values,H,threshold):

            if H_values==[] or (H >= max(H_values) + threshold) or (H<=min(H_values) - threshold):
                return (True,)

            val_above,val_below = 0,0

            for i in H_values:
                if i<H:
                    val_below=i
                elif val_above==0:
                    val_above = i
                    return False,val_below,val_above

        def ask(prompt):
            while True:
                try:
                    return {1: True, 0: False}[input(prompt).lower()]
                except KeyError:
                    print ("Invalid input please enter True or False!")


        toAsk = False

        # get the name of the data file
        name = configurationString(self.N_1,self.N_2)+".txt"

        # check if datafile exists
        if not os.path.isfile("Data/"+name):
            # does not exist, so create
            pickle.dump(dict([]),open("Data/"+name,"wb"))
            toAsk = True

        data = pickle.load(open("Data/"+name,"rb"))

        # see if there is a spacing between the lines

        Time = boorveld.defaultTimeArray
        # print data.keys()
        data.pop("Time")
        lijst = list(data.keys())
        lijst.sort()
        # print "To ask",relevant(lijst,self.B,boorveld.thresholdBoreholeSpacing)[0]
        if not toAsk and relevance(lijst,self.B,boorveld.thresholdBoreholeSpacing)[0]:
            data[self.B] = dict([])
            toAsk = True

        # see if k_s exists
        lijst = list(data[lijst[0]].keys())
        lijst.sort()
        if not toAsk and relevance(lijst,self.k_s,boorveld.thresholdSoilConductivity)[0]:
            data[self.B][self.k_s] = dict([])
            toAsk = True

        if boorveld.defaultMelden and toAsk:
            # answer = ask("Deze data is niet geprecalculeerd. Wilt u deze data nu berekenen? (1 of 0)")
            # if True: # answer:
                # bereken nieuwe data
            self.makeDatafile()
            data = pickle.load(open("Data/" + name, "rb"))

        # 3D - interpolatie over zowel spacing, ks en H
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.griddata.html

        if boorveld.gfunctionInterpolationArray==[]:
            # maak interpolatielijst aan
            def makeInterpolationList():
                """Deze functie maakt een interpolatielijst aan en stokkeert deze onder
                de variabele gfunctionInterpolationArray"""

                B_array = list(data.keys())
                ks_array = list(data[B_array[0]].keys())
                H_array = list(data[B_array[0]][ks_array[0]].keys())
                B_array.sort()
                ks_array.sort()
                H_array.sort()

                points = (B_array,ks_array,H_array,Time)

                values = []
                for B in B_array:
                    temp_ks = []
                    for ks in ks_array:
                        temp_H = []
                        for H in H_array:
                            temp_H.append(data[B][ks][H])
                        temp_ks.append(temp_H)
                    values.append(temp_ks)
                boorveld.gfunctionInterpolationArray=(points,values)
                # print values
                # if self.B in B_array and self.k_s in ks_array:
                #     gfunctionTemp = [data[self.B][self.k_s][H] for H in H_array]
                #     boorveld.gfunctionInterpolationArray= (Time,H_array,gfunctionTemp)
                # elif self.B in B_array and not self.k_s in ks_array:
                #     # interpolate in ks

            makeInterpolationList()

        points,values = boorveld.gfunctionInterpolationArray

        # times = []
        # for t in tijd:
        #     print np.array([self.B, self.k_s, H, t]),H
        #     times.append(interpolate.interpn(points, values, np.array([self.B, self.k_s, H, t])))
        #
        if not isinstance(timeValue, float):
            times = interpolate.interpn(points, values, np.array([[self.B, self.k_s, H, t] for t in timeValue]))
        else:
            times = interpolate.interpn(points, values, np.array([self.B, self.k_s, H, timeValue]))
        # print times
        return times

        # B_array = data.keys().sort()
        # ks_array = data[B_array[0]].sort()
        # H_array = data[B_array[0]][ks_array[0]].sort()
        #
        # H_array = [i.get("H") for i in raw_data]
        # tijd_array = raw_data[0].get("Time")
        # respons = [i.get("Gfunc") for i in raw_data]
        #
        # f = interpolate.interp2d(tijd_array, H_array, respons)
        # return f(tijd, H)

    def makeDatafile(self,data=None,thresholdBoreholeDepth=thresholdBoreholeDepth,timeArray=defaultTimeArray,depthArray=defaultDepthArray):
        """This function makes a datafile for a given borefield spacing and ground conductivity."""
        if data==None:
            N_1=self.N_1
            N_2 = self.N_2
            k_s = self.k_s
            B = self.B
        else:
            N_1 = data["N_1"]
            N_2 = data["N_2"]
            k_s = data["k_s"]
            B = data["B"]
        def relevant(H_values,H):

            if H_values==[] or (H >= max(H_values) + thresholdBoreholeDepth) or (H<=min(H_values) - thresholdBoreholeDepth+1):
                return (True,)

            val_above,val_below = 0,0

            for i in H_values:
                if i<H:
                    val_below=i
                    if len(H_values)==1:
                        return True,
                elif val_above==0:
                    val_above = i
                    return False,val_below,val_above

        # make filename
        name = configurationString(N_1, N_2) + ".txt"
        # check if file exists
        if not os.path.isfile("Data/"+name):
            # does not exist, so create
            pickle.dump(dict([]), open("Data/"+name, "wb"))
        data = pickle.load(open("Data/"+name, "rb"),encoding='latin1')


        # see if spacing exists
        if not B in data:
            data[B]=dict([])

        # see if k_s exists
        if not k_s in data[B]:
            data[B][k_s] = dict([])

        data["Time"]= timeArray
        H_values = list(data[B][k_s].keys())
        H_values.sort()

        for H in depthArray:
            print ("Start H: ", H, "B: ", B, "k_s: ",k_s, "N_1 :", N_1, "N_2: ", N_2)
            # print ("Bereken de gfunctiewaarden voor H: ", H, "m")
            _relevant = relevant(H_values,H)
            # bekijk of deze waarde moet uitgerekend worden
            if H in data[B][k_s]:
                # bestaat al dus we slaan deze waarde over
                print ("De gfunctie is reeds bepaald voor H: ",H,"m!")
            elif not _relevant[0]:
                print ("Deze gfunctie wordt niet berekend daar deze te dicht ligt bij de berekende waarden van ", _relevant[1], " en ", _relevant[2])
            else:
                # Calculate the g-function for uniform borehole wall temperature
                boreFieldTemp = gt.boreholes.rectangle_field(N_1, N_2, B, B, H, self.D, self.r_b)

                alpha = k_s / (2.4 * 10 ** 6)

                # p1  = Process(target=gt.gfunction.uniform_temperature, args=(boreFieldTemp, timeArray, alpha,12,'linear',True,0.01,1e-06,None,True))
                # p2 = Process(target=gt.gfunction.uniform_temperature, args=(boreFieldTemp, timeArray, alpha,12,'linear',True,0.01,1e-06,None,True))
                # p1.start()
                # p2.start()
                # p1.join()
                # p2.join()
                # print ("Done")
                gfunc_uniform_T = gt.gfunction.uniform_temperature(
                        boreFieldTemp, timeArray, alpha, nSegments=self.nSegments, disp=False)

                data[B][k_s][H]=gfunc_uniform_T
                H_values.append(H)
                H_values.sort()
        # print ("Start H: ", H, "B: ", B, "k_s: ",k_s, "N_1 :", N_1, "N_2: ", N_2)

        pickle.dump(data,open("Data/"+name,"wb"))

    def printTemperatureProfile(self, legend=True):
        """This function plots the temperature profile for the calculated depth."""
        self._printTemperatureProfile(legend=legend)

    def printTemperatureProfileFixedDepth(self, depth, legend=True):
        """This function plots the temperature profile for a fixed depth depth."""
        self._printTemperatureProfile(legend=legend, H=depth)

if __name__=='__main__':

    # data voor het boorveld (alle conductiviteiten etc.)
    # deze zijn nog niet allemaal actief in de code
    # de parameters waarvan het effect meegenomen is zijn N_1 en N_2, Rb, k_s, Tg, Tinit en B

    data = {"D": 4.0,           # afstand vanwaar het boorgat begint (i.e. 4 meter onder de grond start de verticale leiding)
            "H": 110,           # diepte
            "B": 6,             # spaciëring: wat is de afstand tussen de boringen
            "r_b": 0.075,       # straal van het boorgat
            "rp_out": 0.0167,   # buitendiameter van de leiding
            "rp_in": 0.013,     # binnendiameter van de leiding
            "D_s": 0.031,       # afstand van het centrum van de leiding tot het centrum van het boorgat
            "epsilon": 1.0e-6,
            "alpha": 1.62e-6,
            "k_s": 3,           # conductiviteit van de bodem
            "k_g": 1.0,         # conductiviteit van de vulling
            "k_p": 0.4,         # conductiviteit van de leiding
            "m_flow": 3.98,     # massadebiet
            "cp_f": 4000.,      # soortelijke warmte van de vloeistof
            "den_f": 1016.,     # dichtheid van de vloeistof
            "visc_f": 0.00179,  # viscositeit van de vloeistof
            "k_f": 0.513,       # thermische conductiviteit van de vloeistof
            "nSegments": 12,    # aantal discretisatiesegmenten (standaard 12)
            "T_init": 10,       # initiële bodemtemperatuur (varieert typisch van 10-13 graden)
            "Tg":10,            # grondtemperatuur op oneiding, eigenlijk dezelfde als T_init
            "Rb":0.2,           # equivalente boorgatweerstand --> groot effect op dimensionering! 0.2 is een vrij slecht boorgat, 0.07 is een zeer goed boorgat
            "N_1":10,           # breedte rechthoekig veld
            "N_2":12}           # lengte rechthoekig veld

    data["pos_pipes"] = [(-data["D_s"], 0.), (data["D_s"], 0.)] # positie van de leidingen in het boorgat

    #Montly loading values
    piek_koel = [0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.]            # Peak cooling in kW
    piek_verwarming = [160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.]     # Peak heating in kW

    maandbelasting_H_E = [0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144] # procentuele verdeling van de jaarenergie per maand (15.5% voor januari ...)
    maandbelasting_C_E = [0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025]
    maandbelasting_H_E = list(map(lambda x: x * 300 * 10 ** 3, maandbelasting_H_E))  # kWh
    maandbelasting_C_E = list(map(lambda x: x * 160* 10 ** 3, maandbelasting_C_E))  # kWh

    # aanmaak van het object

    boorveld = Borefield(simulationPeriod=20,
                         numberOfBoreholes=data["N_1"]*data["N_2"],
                         peakHeating=piek_verwarming,
                         peakCooling=piek_koel,
                         baseloadHeating=maandbelasting_H_E,
                         baseloadCooling=maandbelasting_C_E)

    boorveld.setGroundParameters(data)

    # set temperature boundaries
    boorveld.setMaxGroundTemperature(16) # 16/17 voor passief koelen, 25 voor actief koelen
    boorveld.setMinGroundTemperature(0)

    print (boorveld.size(100)) # print depth of borefield
    print (boorveld.imbalance) # print imbalance
    boorveld.printTemperatureProfile(legend=True) # plot temperature profile for the calculated depth
    boorveld.printTemperatureProfileFixedDepth(depth=75,legend=False)
    print (boorveld.resultsPeakCooling) # waarden voor de piekkoeling
