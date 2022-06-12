"""
This file is an example on how to use the functionality of GHEtool of sizing a borefield by length and width.
"""
# import all the relevant functions
from GHEtool import Borefield, GroundData

if __name__ == "__main__":
    # set ground data
    data = GroundData(110, 6, 3, 10, 0.2, 10, 12)

    # montly loading values
    peakCooling = [0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.]  # Peak cooling in kW
    peakHeating = [160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.]  # Peak heating in kW

    # annual heating and cooling load
    annualHeatingLoad = 300 * 10 ** 3  # kWh
    annualCoolingLoad = 160 * 10 ** 3  # kWh

    # percentage of annual load per month (15.5% for January ...)
    montlyLoadHeatingPercentage = [0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144]
    montlyLoadCoolingPercentage = [0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025]

    # resulting load per month
    monthlyLoadHeating = list(map(lambda x: x * annualHeatingLoad, montlyLoadHeatingPercentage))  # kWh
    monthlyLoadCooling = list(map(lambda x: x * annualCoolingLoad, montlyLoadCoolingPercentage))  # kWh

    # create the borefield object
    borefield = Borefield(simulationPeriod=20,
                          peakHeating=peakHeating,
                          peakCooling=peakCooling,
                          baseloadHeating=monthlyLoadHeating,
                          baseloadCooling=monthlyLoadCooling)

    borefield.setGroundParameters(data)

    # set temperature boundaries
    borefield.setMaxGroundTemperature(16)  # maximum temperature
    borefield.setMinGroundTemperature(0)  # minimum temperature

    # set parameters for sizing
    maxWidth = 60
    maxLength = 60
    minSpacing = 5
    maxSpacing = 8
    maxDepth = 250

    # size by length and width
    result = borefield.sizeByLengthAndWidth(maxDepth, maxWidth, maxLength, minSpacing,
                                            maxSpacing)
    # print the possible solutions
    if not result:
        print("There are no possible solutions!")
        exit()

    for solution in result:
        print("A possible borefield is a borefield of size", solution[0], "by", solution[1], end=" ")
        print("with a spacing of", solution[2], "m and a depth of", round(solution[3], 2), "m.")
