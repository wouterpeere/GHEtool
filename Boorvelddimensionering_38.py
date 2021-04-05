import numpy as np
import pickle
from scipy import interpolate,pi
import pygfunction as gt
import os.path
import csv
import matplotlib.pyplot as plt
import multiprocessing
import multiprocessing.pool
import sys
from scipy.linalg import solve
from matplotlib.ticker import AutoMinorLocator
from scipy.signal import hilbert
from scipy.integrate import quad
import functools
from multiprocessing import Process

from scipy.special import j0, j1, y0, y1, exp1
class NoDaemonProcess(multiprocessing.Process):
    # make 'daemon' attribute always return False
    def _get_daemon(self):
        return False
    def _set_daemon(self, value):
        pass
    daemon = property(_get_daemon, _set_daemon)

# We sub-class multiprocessing.pool.Pool instead of multiprocessing.Pool
# because the latter is only a wrapper function, not a proper class.
class MyPool(multiprocessing.pool.Pool):
    Process = NoDaemonProcess

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


class Boorveld():

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

    def __init__(self,grondparameters,simulatieperiode,borefield,piekvermogen_H=[0]*12,piekvermogen_C=[0]*12,basisbelasting_H=[0]*12,basisbelasting_C=[0]*12,kosten_investering=None):

        self.piekvermogen_H = piekvermogen_H
        self.piekvermogen_C = piekvermogen_C
        self.basisbelasting_H = basisbelasting_H
        self.set_basisbelasting_C(basisbelasting_C) #dit definieert ook onbalans etc
        self.set_basisbelasting_H(basisbelasting_H)

        self.simulatieperiode = simulatieperiode
        self.borefield = borefield

        self.set_grondparameters(grondparameters)
        self.limiterende_maand =0

        if kosten_investering ==None:
            self.kosten_investering = [35,0]
        else:
            self.kosten_investering = kosten_investering

        self.lengte_piek = 6


    def set_grondparameters(self,data):
        # Borehole dimensions
        self.D = data["D"]  # Borehole buried depth (m)
        self.H = data["H"]  # Borehole length (m)
        self.r_b = data["r_b"]  # Borehole radius (m)
        self.B = data["B"]  # Borehole spacing (m)

        self.N_1 = 10
        self.N_2 = 12

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
        self.ty = self.simulatieperiode * 8760.*3600
        self.tm = Boorveld.UPM*3600.#744
        self.td = 6*3600.
        self.time = np.array([self.td, self.td + self.tm, self.ty + self.tm + self.td])

    def set_max_grondtemperatuur(self,temp):
        self.Tf_H = temp

    def set_min_grondtemperatuur(self,temp):
        self.Tf_C = temp

    @property
    def _Bernier(self):
        # Dimensionering in het laatste werkingsjaar
        # Initieer iteratie
        H_prev = 0

        if self.H<1:
            self.H = 50

        # Herhaal zolang geen convergentie (convergentie indien verschil <1m diepte)
        while np.round(self.H - H_prev, 1) != 0:
            gfunc_uniform_T = self.gfunctie(self.time, self.H)

            Ra = (gfunc_uniform_T[2] - gfunc_uniform_T[1]) / (2 * pi * self.k_s)
            Rm = (gfunc_uniform_T[1] - gfunc_uniform_T[0]) / (2 * pi * self.k_s)
            Rd = (gfunc_uniform_T[0]) / (2 * pi * self.k_s)

            L = (self.qa * Ra + self.qm * Rm + self.qh * Rd + self.qh * self.Rb) / abs(self.Tf - self.Tg)

            H_prev = self.H
            self.H = L / (len(self.borefield))

        return self.H

    @property
    def _Carcel(self):
        # Dit is voor de dimensionering in het eerste jaar
        # Initieer iteratie
        H_prev = 0
        tijd = np.array([self.td, self.td + self.tm, self.tcm + self.td])
        if self.H < 1:
            self.H = 50

        # Herhaal zolang geen convergentie (convergentie indien verschil <1m diepte)
        while np.round(self.H - H_prev, 1) != 0:
            gfunc_uniform_T = self.gfunctie(tijd, self.H)

            Rpm = (gfunc_uniform_T[2] - gfunc_uniform_T[1]) / (2 * pi * self.k_s)
            Rcm = (gfunc_uniform_T[1] - gfunc_uniform_T[0]) / (2 * pi * self.k_s)
            Rh = (gfunc_uniform_T[0]) / (2 * pi * self.k_s)

            L = (self.qh*self.Rb+self.qh*Rh+self.qm*Rcm+self.qpm*Rpm) / abs(self.Tf - self.Tg)

            H_prev = self.H
            self.H = L / (len(self.borefield))

        return self.H

    def dimensioneer_boorveld(self,H_init):

        self.H_init = H_init

        # dimensioneer laatste jaar
        self.bereken_L2_params(True)    # bereken parameters voor verwarmingsgelimiteerd
        self.qa = self.qa
        self.H_H_Bernier = self._Bernier # Dimensioneer
        self.bereken_L2_params(False)   # bereken parameters voor koelgelimiteerd
        self.qa = self.qa
        self.H_C_bernier = self._Bernier # Dimensioneer
        self.H_Bernier = max(self.H_H_Bernier,self.H_C_bernier) # Neem maximale lengte van deze twee dimensioneringen


        # dimensioneer eerste jaar
        self.bereken_L3_params(True) # bereken parameters voor verwarmingsgelimiteerd
        self.H_H_Carcel = self._Carcel # Dimensioneer
        self.bereken_L3_params(False) # bereken parameters voor koelgelimiteerd
        self.H_C_Carcel = self._Carcel # Dimensioneer
        self.H_Carcel = max(self.H_H_Carcel,self.H_C_Carcel) # Neem maximale lengte van deze twee dimensioneringen


        self.H = max(self.H_Bernier,self.H_Carcel) # Neem maximale lengte van dimensionering in eerste of laatste werkingsjaar

        return self.H

    def gfunctie(self,tijd, H):
        # Deze functie berekend de g-waarden indien ze gegeven zijn

        def relevant(H_values,H,threshold):
            # print H_values,H,threshold
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
        if not toAsk and relevant(lijst,self.B,boorveld.thresholdBoreholeSpacing)[0]:
            data[self.B] = dict([])
            toAsk = True

        # see if k_s exists
        lijst = list(data[lijst[0]].keys())
        lijst.sort()
        if not toAsk and relevant(lijst,self.k_s,boorveld.thresholdSoilConductivity)[0]:
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
        if not isinstance(tijd,float):
            times = interpolate.interpn(points, values, np.array([[self.B, self.k_s, H, t] for t in tijd]))
        else:
            times = interpolate.interpn(points, values, np.array([self.B, self.k_s, H, tijd]))
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

    def set_basisbelasting_H(self,basisbelasting):
        self.basisbelasting_H=[i if i>=0 else 0 for i in basisbelasting]
        self.maandbelasting = [(-self.basisbelasting_H[i]+self.basisbelasting_C[i])/Boorveld.UPM for i in range(12)]
        self.maandbelasting_H = list(map(lambda x:x/Boorveld.UPM,self.basisbelasting_H))
        self.jaarenergie_H = functools.reduce(lambda x,y : x+y,self.basisbelasting_H)
        self.bereken_onbalans()

    def set_basisbelasting_C(self,basisbelasting):
        self.basisbelasting_C=[i if i>=0 else 0 for i in basisbelasting]
        self.maandbelasting = [(-self.basisbelasting_H[i]+self.basisbelasting_C[i])/Boorveld.UPM for i in range(12)]
        self.maandbelasting_C = list(map(lambda x:x/Boorveld.UPM,self.basisbelasting_C))
        self.jaarenergie_C = functools.reduce(lambda x,y : x+y,self.basisbelasting_C)
        self.bereken_onbalans()

    def set_piekbelasting_H(self,piekbelasting,duur=None):
        self.piekvermogen_H=[i if i>=0 else 0 for i in piekbelasting]
        if duur!=None:
            self.td = duur*3600.
            self.lengte_piek = duur

    def set_piekbelasting_C(self,piekbelasting,duur=None):
        self.piekvermogen_C=[i if i>=0 else 0 for i in piekbelasting]
        if duur!=None:
            self.td = duur*3600.
            self.lengte_piek = duur

    @property
    def investeringskost(self):
        return np.polyval(self.kosten_investering,self.H*len(self.borefield))

    def bereken_onbalans(self):
        try:
            self.onbalans = self.jaarenergie_C-self.jaarenergie_H
            self.C_dom = self.onbalans>0
        except:
            pass

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

    def bereken_L2_params(self, HC):
        # Deze functie berekend de nodige parameters voor de dimensionering in het laatste werkingsjaar
        # Vooral de tekens zijn hier van belang.
        self.qa = self.onbalans/8760.*1000

        if HC:
            # Gelimiteerd door verwarming
            # Tempeartuur ingesteld op minimale temperatuur Tf_C
            self.Tf=self.Tf_C

            # Selecteer de maand waarin de hoogste piek voorkomt. Het is mogelijk dat er een bepaalde maand is
            # waarin het gemiddeld vermogen hoger is dan de piek. In praktijk mogen jullie ervan uitgaan
            # dat het altijd true gaat zijn.
            if max(self.piekvermogen_H) > max(self.maandbelasting_H):
                maand_index = self.piekvermogen_H.index(max(self.piekvermogen_H))
                self.qm = self.maandbelasting[maand_index] * 1000.
                self.qh = max(self.piekvermogen_H) * 1000.
                self.peak=True
            else:
                maand_index = self.maandbelasting_H.index(max(self.maandbelasting_H))
                self.qm = self.maandbelasting[maand_index] * 1000.
                self.qh = self.maandbelasting_H[maand_index] * 1000.
                self.peak=False

            self.qm = -self.qm
            self.qa = -self.qa
            # print "Heating", self.qa, self.qm, self.qh,self.H
        else:
            # Gelimiteerd door koeling
            # Temperatuur ingesteld op maximale temperatuur Tf_H
            self.Tf=self.Tf_H

            # Selecteer de maand waarin de hoogste piek voorkomt. Het is mogelijk dat er een bepaalde maand is
            # waarin het gemiddeld vermogen hoger is dan de piek. In praktijk mogen jullie ervan uitgaan
            # dat het altijd true gaat zijn.
            if max(self.piekvermogen_C) > max(self.maandbelasting_C):
                maand_index = self.piekvermogen_C.index(max(self.piekvermogen_C))
                self.qm = self.maandbelasting[maand_index] * 1000.
                self.qh = max(self.piekvermogen_C) * 1000.
                self.peak=True
            else:
                maand_index = self.maandbelasting_C.index(max(self.maandbelasting_C))
                self.qm = self.maandbelasting[maand_index] * 1000.
                self.qh = self.maandbelasting_C[maand_index] * 1000.
                self.peak=False

    def bereken_L3_params(self,HC,maandindex=None):

        if HC:
            # Gelimiteerd door verwarming
            # Temperatuur ingesteld op minimale temperatuur Tf_C
            self.Tf = self.Tf_C

            # Selecteer de maand waarin de hoogste piek voorkomt. Het is mogelijk dat er een bepaalde maand is
            # waarin het gemiddeld vermogen hoger is dan de piek. In praktijk mogen jullie ervan uitgaan
            # dat het altijd true gaat zijn.
            if max(self.piekvermogen_H) > max(self.maandbelasting_H):
                maand_index = self.piekvermogen_H.index(max(self.piekvermogen_H)) if maandindex==None else maandindex
                self.qh = max(self.piekvermogen_H) * 1000.
                self.peak = True
            else:
                maand_index = self.maandbelasting_H.index(max(self.maandbelasting_H)) if maandindex==None else maandindex
                self.qh = self.maandbelasting_H[maand_index] * 1000.
                self.peak = False

            self.qm = self.maandbelasting[maand_index] * 1000.
            if maand_index < 1:
                self.qpm = 0
            else:
                self.qpm = functools.reduce(lambda x, y: x + y, self.maandbelasting[:maand_index])*1000./(maand_index+1)

            self.qm = -self.qm
        else:
            # Gelimiteerd door koeling
            # Temperatuursgrens ingesteld op maximale temperatuur tf_H
            self.Tf = self.Tf_H

            # Selecteer de maand waarin de hoogste piek voorkomt. Het is mogelijk dat er een bepaalde maand is
            # waarin het gemiddeld vermogen hoger is dan de piek. In praktijk mogen jullie ervan uitgaan
            # dat het altijd true gaat zijn.
            if max(self.piekvermogen_C) > max(self.maandbelasting_C):
                maand_index = self.piekvermogen_C.index(max(self.piekvermogen_C)) if maandindex==None else maandindex
                self.qh = max(self.piekvermogen_C) * 1000.
                self.peak = True
            else:
                maand_index = self.maandbelasting_C.index(max(self.maandbelasting_C)) if maandindex==None else maandindex
                self.qh = self.maandbelasting_C[maand_index] * 1000.
                self.peak = False

            self.qm = self.maandbelasting[maand_index] * 1000.
            if maand_index < 1:
                self.qpm = 0
            else:
                self.qpm = functools.reduce(lambda x, y: x + y, self.maandbelasting[:maand_index])*1000./(maand_index+1)
        self.tcm = (maand_index + 1) * Boorveld.UPM * 3600
        self.tpm = maand_index * Boorveld.UPM * 3600

        return maand_index

    def print_temperature_profile(self,legende=True,H = None):
        """
        This function would calculate a new length of the borefield using temporal superposition.
        Now it justs outputs the temperature graphs
        """

        # making a numpy array of the monthly balance (self.maandbelasting) for a period of 20 years [kW]
        maandbelasting_array = np.asarray(self.maandbelasting*self.simulatieperiode)

        #calculation of all the different times at which the gfunction should be calculated.
        #this is equal to 730 hours a month * 3600 seconds/hours for a period of 20 years
        gwaarden_tijd = [i*730*3600. for i in range(1,12*self.simulatieperiode + 1)]

        #self.gfunctie is a function that uses the data in data_k3.5.txt to interpolate the correct values of the gfunction.
        #this dataset is checked over and over again and is correct
        gwaarden= self.gfunctie(gwaarden_tijd,self.H if H ==None else H)

        #the gfunction value of the peak with 6 hours
        gwaarde_piek = self.gfunctie(6 * 3600., self.H if H ==None else H)

        #calculation of needed differences of the gfunction values. These are the weight factors in the calculation of Tb.
        lijst = [gwaarden[i] if i ==0 else gwaarden[i]-gwaarden[i-1] for i in range(len(gwaarden))]

        self.factoren_temperature_profile = lijst
        results = []
        temp=[]

        #calculation of the product for every month in order to obtain a temperature profile
        for i in range(len(maandbelasting_array)):
            temp.insert(0,maandbelasting_array[i]*1000.)
            results.append(np.dot(temp,lijst[:i+1]))

        results_C = []
        results_H = []
        results_piek_C = []
        results_piek_H = []
        results_month_C = []
        results_month_H = []

        #calculation the borehole wall temperature for every month i
        Tb = [i/(2*pi*self.k_s)/((self.H if H ==None else H)*len(self.borefield))+self.Tg for i in results]

        #now the Tf will be calculated based on
        #Tf = Tb + QR_b
        for i in range(240):
            results_C.append(Tb[i] + self.maandbelasting_C[i%12]*1000.*(self.Rb/len(self.borefield)/(self.H if H ==None else H)))
            results_H.append(Tb[i]-self.maandbelasting_H[i%12]*1000.*(self.Rb/len(self.borefield)/(self.H if H ==None else H)))
            results_month_C.append(Tb[i] + self.maandbelasting_C[i%12]*1000.*(self.Rb/len(self.borefield)/(self.H if H ==None else H)))
            results_month_H.append(Tb[i] - self.maandbelasting_H[i%12]*1000.*(self.Rb/len(self.borefield)/(self.H if H ==None else H)))

        #extra sommation if the gfunction value for the peak is included

        for i in range(240):
            results_piek_C.append(results_C[i] + ((self.piekvermogen_C[i % 12] - self.maandbelasting_C[i%12] if self.piekvermogen_C[i%12]>self.maandbelasting_C[i%12] else 0)*1000.*(gwaarde_piek[0]/self.k_s/2/pi + self.Rb))/len(self.borefield)/(self.H if H ==None else H))
            results_piek_H.append(results_H[i] - ((self.piekvermogen_H[i % 12] - self.maandbelasting_H[i%12] if self.piekvermogen_H[i%12]>self.maandbelasting_H[i%12] else 0) * 1000. * (gwaarde_piek[0]/self.k_s/2/pi + self.Rb))/ len(self.borefield) / (self.H if H ==None else H))


        #definieer de tijd
        tijd = [i/12/730./3600. for i in gwaarden_tijd]

        plt.rc('figure')
        fig = plt.figure()

        ax1 = fig.add_subplot(111)
        ax1.set_xlabel(r'Time (year)')
        ax1.set_ylabel(r'Temperature ($^\circ C$)')

        # Plot Temperatures
        ax1.step(tijd,Tb,'k-',where="pre",lw=1.5,label="Tb")
        ax1.step(tijd, results_piek_C, 'b-', where="pre", lw=1.5,label='Tf peak cooling')
        ax1.step(tijd, results_piek_H, 'r-', where="pre", lw=1.5,label='Tf peak heating')

        # Teken temperatuursgrenzen
        ax1.step(tijd, Tb, 'k-', where="pre", lw=1.5, label="Tb")
        ax1.step(tijd, results_month_C, color='b', linestyle="dashed",  where="pre", lw=1.5, label='Tf basis cooling')
        ax1.step(tijd, results_month_H, color='r', linestyle="dashed", where="pre", lw=1.5, label='Tf basis heating')
        ax1.hlines(self.Tf_C, 0, 20, colors='r', linestyles='dashed', label='',lw=1)
        ax1.hlines(self.Tf_H, 0, 20, colors='b', linestyles='dashed', label='',lw=1)
        ax1.set_xticks(range(0,21,2))

        # Plot legend
        if legende:
            ax1.legend()
        ax1.set_xlim(left=0,right=20)
        plt.show()




if __name__=='__main__':
    data = {"D": 4.0,
            "H": 110,
            "B": 6,
            "r_b": 0.075,
            "rp_out": 0.0167,
            "rp_in": 0.013,
            "D_s": 0.031,
            "epsilon": 1.0e-6,
            "alpha": 1.62e-6,
            "k_s": 3,
            "k_g": 1.0,
            "k_p": 0.4,
            "m_flow": 3.98,
            "cp_f": 4000.,
            "den_f": 1016.,
            "visc_f": 0.00179,
            "k_f": 0.513,
            "nSegments": 12,
            "T_init": 10,
            "Tg":10,
            "Rb":0.2}
    data["pos_pipes"] = [(-data["D_s"], 0.), (data["D_s"], 0.)]

    #Montly loading values
    piek_koel = [0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.]            # Peak cooling in kW
    piek_verwarming = [160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.]    # Peak heating in kW #530
    # piek_koel = [0, 0, 22, 44, 83, 117, 134, 150, 100, 23, 0, 0]
    # piek_verwarming = [300, 268, 191, 103, 75, 0, 0, 38, 76, 160, 224, 255]

    # piek_koel = [0]*12
    maandbelasting_H_E = [0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144] #0.155
    maandbelasting_C_E = [0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025]
    maandbelasting_H_E = list(map(lambda x: x * 300 * 10 ** 3, maandbelasting_H_E))  # kWh
    maandbelasting_C_E = list(map(lambda x: x * 160* 10 ** 3, maandbelasting_C_E))  # kWh
    # piek_koel = [0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.]  # kW
    # piek_verwarming = [160., 143., 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.]  # kW

    # piek_koel = [0]*12

    #
    piek_koel=[piek_koel[i] if piek_koel[i]>maandbelasting_C_E[i]/730. else maandbelasting_C_E[i]/730. for i in range(12)]
    piek_verwarming=[piek_verwarming[i] if piek_verwarming[i]>maandbelasting_H_E[i]/730. else maandbelasting_H_E[i]/730. for i in range(12)]
    #
    # maandbelasting_C_E =[0.0, 0.0, 0.0, 0.0, 24.65753424657534, 32.87671232876713, 65.75342465753425, 60.47191246575342, 32.87671232876713, 0.0, 0.0, 0.0]
    #
    # maandbelasting_H_E=[33.83413108624657, 32.255937582794516, 27.160361020821917, 21.433251792438355, 13.741615901369862, 0.0, 0.0, 0.0, 13.138064054136986, 18.88257253709589, 25.493912723178088, 31.428355705315067]
    #
    # piek_koel=[0, 0, 9.342450849412101, 52.56163, 75.355208, 75.35521, 65.75342465753425, 61.07019, 75.355208, 12.342450849412101, 0, 0]
    #
    # piek_verwarming=[133.966373944, 131.346465416, 101.763100744, 54.734621656, 13.741615901369864, 0.0, 0.0, 0.0, 40.16820104, 84.814079384, 118.85007710400001, 133.96637379199998]




    # maandbelasting_C_E = map(lambda x:x*730.,maandbelasting_C_E)
    # maandbelasting_H_E = map(lambda x:x*730.,maandbelasting_H_E)
    # print sum(maandbelasting_C_E),sum(maandbelasting_H_E)

    # piek_koel[7] -= 33.119579313166184


    temp = piek_verwarming

    boreField = gt.boreholes.rectangle_field(10, 12, 6.5, 6.5, 110, 4, 0.075)  # setting up the borefield

    boorveld = Boorveld(data, 20, boreField, piek_verwarming, piek_koel, maandbelasting_H_E, maandbelasting_C_E)  #making of an object

    #set temperature boundaries
    boorveld.set_max_grondtemperatuur(16)
    boorveld.set_min_grondtemperatuur(0)

    # boorveld.dimensioneer_boorveld(100,old=True)
    # print boorveld.H

    # a_pool = MyPool(4)
    # a_pool.map(boorveld.makeDatafile,[{"B": 3, "N_1": 5,"N_2":5,"k_s":1.5}])
    # a_pool.close()
    # a_pool.join()

    #boorveld.dimensioneer_boorveld(100)
    for N_1 in range(1,21):
        for N_2 in range (1,21):
            for ks in (1.5,2,2.5,3,3.5):
                # data3 = {"B": 3, "N_1": N_1,"N_2":N_2,"k_s":ks}
                # p1 = Process(target=boorveld.makeDatafile,args=(data3,))
                # data6 = {"B": 6, "N_1": N_1, "N_2": N_2, "k_s": ks}
                # p2 = Process(target=boorveld.makeDatafile,args=(data6,))
                # data9 = {"B": 9, "N_1": N_1, "N_2": N_2, "k_s": ks}
                # p3 = Process(target=boorveld.makeDatafile,args=(data9,))
                # p1.start()
                # p2.start()
                # p3.start()
                # p1.join()
                # p2.join()
                # p3.join()
                for B in (3,6,9):
                    boorveld.N_1=N_1
                    boorveld.N_2=N_2
                    boorveld.k_s=ks
                    boorveld.B=B
                    boorveld.makeDatafile()


    # print (boorveld.H)
    # print (boorveld.dimensioneer_boorveld(100))
    # # print boorveld.limiterende_maand_heating,boorveld.limiterende_maand_cooling,boorveld.cooling_lim,boorveld.heating_lim
    # boorveld.print_temperature_profile(legende=True)
    # # print boorveld.actief_koelen_referentietemperatuur
    # # print boorveld.bepaal_baseloadopties((((0,)*12,(0,)*12),((0,)*12,(0,)*12),"",93.8405439071284))
    # print (boorveld.H)
    # temp = boorveld.bepaal_opties(boorveld.H,True,optimale_reductie = True)
    # # boorveld.cooling_lim = False
    # # temp = boorveld.zuiver_gelimiteerd(boorveld.H,reductie=True,optimale_reductie=True,recursief=True)
    # for _,i in enumerate(temp):
    #     print (i)
    #     print (boorveld.bepaal_baseloadopties(i))
