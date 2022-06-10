"""
This document is an example of how the borefield configuration can influence the total borehole length and hence the cost of the borefield.
"""

# import all the relevant functions
from GHEtool import *

if __name__ == "__main__":
    # GroundData for an initial field of 11 x 11
    data = GroundData(110,6,3,10,0.2,11,11)

    # Montly loading values
    peakCooling = [0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.]              # Peak cooling in kW
    peakHeating = [160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.]             # Peak heating in kW

    # annual heating and cooling load
    annualHeatingLoad = 150*10**3 # kWh
    annualCoolingLoad = 400*10**3 # kWh

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
    print("The borehole depth is:", depth, "m for a 11x11 field")
    print("The total length is:", int(depth * 11 * 11), "m")
    print("------------------------")
    # borefield of 6x20
    data = GroundData(110,6,3,10,0.2,6,20)

    # set ground parameters to borefield
    borefield.setGroundParameters(data)

    # size borefield
    depth6_20 = borefield.size(100)
    print("The borehole depth is:", depth6_20, "m for a 6x20 field")
    print("The total length is:", int(depth6_20 * 6 * 20), "m")
    print("The second field is hence", -int(depth6_20 * 6 * 20) + int(depth * 11 * 11), "m shorter")
    borefield.printTemperatureProfile()
