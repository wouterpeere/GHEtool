"""
This file contains all the main functionalities of GHEtool being:
    * sizing of the borefield
    * sizing of the borefield for a specific quadrant
    * plotting the temperature evolution
    * plotting the temperature evolution for a specific depth
    * printing the array of the temperature

"""

# import all the relevant functions
from GHEtool import Borefield, GroundData, FluidData, PipeData

if __name__ == "__main__":
    # relevant borefield data for the calculations
    data = {"H": 110,           # depth (m)
            "B": 6,             # borehole spacing (m)
            "k_s": 3,           # conductivity of the soil (W/mK)
            "Tg":10,            # Ground temperature at infinity (degrees C)
            "Rb":0.2,           # equivalent borehole resistance (K/W)
            "N_1":12,           # width of rectangular field (#)
            "N_2":10}           # length of rectangular field (#)}
    # the new, more efficient way, is to work with the class of GroundData
    data = GroundData(110, 6, 3, 10, 0.2, 10, 12)

    # montly loading values
    peakCooling = [0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.]              # Peak cooling in kW
    peakHeating = [160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.]             # Peak heating in kW

    # annual heating and cooling load
    annualHeatingLoad = 300*10**3 # kWh
    annualCoolingLoad = 160*10**3 # kWh

    # percentage of annual load per month (15.5% for January ...)
    montlyLoadHeatingPercentage = [0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144]
    montlyLoadCoolingPercentage = [0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025]

    # resulting load per month
    monthlyLoadHeating = list(map(lambda x: x * annualHeatingLoad, montlyLoadHeatingPercentage))   # kWh
    monthlyLoadCooling = list(map(lambda x: x * annualCoolingLoad, montlyLoadCoolingPercentage))   # kWh

    # create the borefield object
    borefield = Borefield(simulationPeriod=20,
                          peakHeating=peakHeating,
                          peakCooling=peakCooling,
                          baseloadHeating=monthlyLoadHeating,
                          baseloadCooling=monthlyLoadCooling)

    borefield.setGroundParameters(data)

    # set temperature boundaries
    borefield.setMaxGroundTemperature(16)   # maximum temperature
    borefield.setMinGroundTemperature(0)    # minimum temperature

    # size borefield
    depth = borefield.size(100)
    print("The borehole depth is: ", depth, "m")

    # print imbalance
    print("The borefield imbalance is: ", borefield.imbalance, "kWh/y. (A negative imbalance means the the field is heat extraction dominated so it cools down year after year.)") # print imbalance

    # plot temperature profile for the calculated depth
    borefield.printTemperatureProfile(legend=True)

    # plot temperature profile for a fixed depth
    borefield.printTemperatureProfileFixedDepth(depth=75, legend=False)

    # print gives the array of monthly temperatures for peak cooling without showing the plot
    borefield.calculateTemperatures(depth=90)
    print("Result array for cooling peaks")
    print(borefield.resultsPeakCooling)
    print("---------------------------------------------")

    # size the borefield for quadrant 3
    # for more information about borefield quadrants, see (Peere et al., 2021)
    depth = borefield.size(100, quadrantSizing=3)
    print("The borehole depth is: ", str(round(depth, 2)), "m for a sizing in quadrant 3")
    # plot temperature profile for the calculated depth
    borefield.printTemperatureProfile(legend=True)

    # size with a dynamic Rb* value
    # note that the original Rb* value will be overwritten!

    # this requires pipe and fluid data
    fluidData = FluidData(0.2, 0.568, 998, 4180, 1e-3)
    pipeData = PipeData(1, 0.015, 0.02, 0.4, 0.05, 0.075, 2)
    borefield.setFluidParameters(fluidData)
    borefield.setPipeParameters(pipeData)

    depth = borefield.size(100, useConstantRb=False)
    print("The borehole depth is: ", str(round(depth, 2)), "m for a sizing with dynamic Rb*.")
    borefield.printTemperatureProfile(legend=True)
