"""
This document compares the sizing with a constant Rb*-value with sizing where the Rb*-value is being recalculated.
For the test, the L2 sizing method is used.
The comparison is based on speed and relative accuracy in the result.
It is shown that the speed difference is significant, but so is the difference in the result. With a constant Rb* value, it is important that the initial depth is rather accurate.
"""
if __name__ == "__main__":

    import numpy as np
    import time

    from GHEtool import Borefield, GroundData, FluidData, PipeData

    numberOfIterations = 50
    maxValueCooling = 700
    maxValueHeating = 800

    # initiate the arrays
    resultsRbStatic = np.empty(numberOfIterations)
    resultsRbDynamic = np.empty(numberOfIterations)
    differenceResults = np.empty(numberOfIterations)

    monthlyLoadCoolingArray = np.empty((numberOfIterations, 12))
    monthlyLoadHeatingArray = np.empty((numberOfIterations, 12))
    peakLoadCoolingArray = np.empty((numberOfIterations, 12))
    peakLoadHeatingArray = np.empty((numberOfIterations, 12))

    # populate arrays with random values
    for i in range(numberOfIterations):
        for j in range(12):
            monthlyLoadCoolingArray[i, j] = np.random.randint(0, maxValueCooling)
            monthlyLoadHeatingArray[i, j] = np.random.randint(0, maxValueHeating)
            peakLoadCoolingArray[i, j] = np.random.randint(monthlyLoadCoolingArray[i, j], maxValueCooling)
            peakLoadHeatingArray[i, j] = np.random.randint(monthlyLoadHeatingArray[i, j], maxValueHeating)

    # initiate borefield model
    data = GroundData(100,6,3,10,0.2,10,12) # ground data with an accurate guess of 185m for the depth of the borefield
    fluidData = FluidData(0.2, 0.568, 998, 4180, 1e-3)
    pipeData = PipeData(1, 0.015, 0.02, 0.4, 0.05, 0.075, 2)

    # Montly loading values
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
    borefield.setFluidParameters(fluidData)
    borefield.setPipeParameters(pipeData)

    # set temperature boundaries
    borefield.setMaxGroundTemperature(16)   # maximum temperature
    borefield.setMinGroundTemperature(0)    # minimum temperature

    # size with constant Rb* value
    borefield.useConstantRb = True # True by default, you can also give 'useConstantRb = True' as an argument to the size function

    # calculate the Rb* value
    borefield.Rb = borefield.calculateRb()

    startRbConstant = time.time()
    for i in range(numberOfIterations):
        borefield.setBaseloadCooling(monthlyLoadCoolingArray[i])
        borefield.setBaseloadHeating(monthlyLoadHeatingArray[i])
        borefield.setPeakCooling(peakLoadCoolingArray[i])
        borefield.setPeakHeating(peakLoadHeatingArray[i])
        resultsRbStatic[i] = borefield.size(100)
    endRbConstant = time.time()

    # size with a dynamic Rb* value
    borefield.useConstantRb = False

    startRbDynamic = time.time()
    for i in range(numberOfIterations):
        borefield.setBaseloadCooling(monthlyLoadCoolingArray[i])
        borefield.setBaseloadHeating(monthlyLoadHeatingArray[i])
        borefield.setPeakCooling(peakLoadCoolingArray[i])
        borefield.setPeakHeating(peakLoadHeatingArray[i])
        resultsRbDynamic[i] = borefield.size(100)
    endRbDynamic = time.time()

    print("These are the results when an accurate constant Rb* value is used.")
    print("Time for sizing with a constant Rb* value:", endRbConstant - startRbConstant, "s")
    print("Time for sizing with a dynamic Rb* value:", endRbDynamic - startRbDynamic, "s")

    # calculate differences
    for i in range(numberOfIterations):
        differenceResults[i] = resultsRbDynamic[i] - resultsRbStatic[i]

    print("The maximal difference between the sizing with a constant and a dynamic Rb* value:", np.round(np.max(differenceResults), 3), "m or", np.round(np.max(differenceResults) / resultsRbStatic[np.argmax(differenceResults)] * 100, 3), "% w.r.t. the constant Rb* approach.")
    print("The mean difference between the sizing with a constant and a dynamic Rb* value:", np.round(np.mean(differenceResults), 3), "m or", np.round(np.mean(differenceResults) / np.mean(resultsRbStatic) * 100, 3), "% w.r.t. the constant Rb* approach.")
    print("------------------------------------------------------------------------------")

    # Do the same thing but with another constant Rb* value based on a borehole depth of 185m.

    data = GroundData(185, 6, 3, 10, 0.2, 10, 12)  # ground data with an inaccurate guess of 185m for the depth of the borefield
    borefield.setGroundParameters(data)

    # size with a constant Rb* value
    borefield.useConstantRb = True

    # calculate the Rb* value
    borefield.Rb = borefield.calculateRb()

    startRbConstant = time.time()
    for i in range(numberOfIterations):
        borefield.setBaseloadCooling(monthlyLoadCoolingArray[i])
        borefield.setBaseloadHeating(monthlyLoadHeatingArray[i])
        borefield.setPeakCooling(peakLoadCoolingArray[i])
        borefield.setPeakHeating(peakLoadHeatingArray[i])
        resultsRbStatic[i] = borefield.size(100)
    endRbConstant = time.time()

    # size with a dynamic Rb* value
    borefield.useConstantRb = False

    startRbDynamic = time.time()
    for i in range(numberOfIterations):
        borefield.setBaseloadCooling(monthlyLoadCoolingArray[i])
        borefield.setBaseloadHeating(monthlyLoadHeatingArray[i])
        borefield.setPeakCooling(peakLoadCoolingArray[i])
        borefield.setPeakHeating(peakLoadHeatingArray[i])
        resultsRbDynamic[i] = borefield.size(100)
    endRbDynamic = time.time()

    print("These are the results when an inaccurate constant Rb* value is used.")
    print("Time for sizing with a constant Rb* value:", endRbConstant - startRbConstant, "s")
    print("Time for sizing with a dynamic Rb* value:", endRbDynamic - startRbDynamic, "s")

    # calculate differences
    for i in range(numberOfIterations):
        differenceResults[i] = resultsRbDynamic[i] - resultsRbStatic[i]

    print("The maximal difference between the sizing with a constant and a dynamic Rb* value:",
          np.round(np.max(differenceResults), 3), "m or",
          np.round(np.max(differenceResults) / resultsRbStatic[np.argmax(differenceResults)] * 100, 3),
          "% w.r.t. the constant Rb* approach.")
    print("The mean difference between the sizing with a constant and a dynamic Rb* value:",
          np.round(np.mean(differenceResults), 3), "m or",
          np.round(np.mean(differenceResults) / np.mean(resultsRbStatic) * 100, 3),
          "% w.r.t. the constant Rb* approach.")
