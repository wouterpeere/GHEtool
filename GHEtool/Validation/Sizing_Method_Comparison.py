"""
This document compares both the L2 sizing method of (Peere et al., 2021) with a more general L3 sizing.
The comparison is based on speed and relative accuracy in the result.
"""
if __name__ == "__main__":

    import numpy as np
    import time

    from GHEtool import Borefield, GroundData

    numberOfIterations = 100
    maxValueCooling = 700
    maxValueHeating = 800

    # initiate the arrays
    resultsL2 = np.empty(numberOfIterations)
    resultsL3 = np.empty(numberOfIterations)
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
    data = GroundData(110,6,3,10,0.2,10,12)

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

    # set temperature boundaries
    borefield.setMaxGroundTemperature(16)   # maximum temperature
    borefield.setMinGroundTemperature(0)    # minimum temperature

    # size according to L2 method
    startL2 = time.time()
    for i in range(numberOfIterations):
        borefield.setBaseloadCooling(monthlyLoadCoolingArray[i])
        borefield.setBaseloadHeating(monthlyLoadHeatingArray[i])
        borefield.setPeakCooling(peakLoadCoolingArray[i])
        borefield.setPeakHeating(peakLoadHeatingArray[i])
        resultsL2[i] = borefield.size(100)
    endL2 = time.time()

    # size according to L3 method
    startL3 = time.time()
    for i in range(numberOfIterations):
        borefield.setBaseloadCooling(monthlyLoadCoolingArray[i])
        borefield.setBaseloadHeating(monthlyLoadHeatingArray[i])
        borefield.setPeakCooling(peakLoadCoolingArray[i])
        borefield.setPeakHeating(peakLoadHeatingArray[i])
        resultsL3[i] = borefield.size(100,0)
    endL3 = time.time()

    print("Time for sizing according to L2:", endL2 - startL2, "s")
    print("Time for sizing according to L3:", endL3 - startL3, "s")

    # calculate differences
    for i in range(numberOfIterations):
        differenceResults[i] = resultsL3[i] - resultsL2[i]

    print("The maximal difference between the sizing of L2 and L3 was:", np.round(np.max(differenceResults), 3), "m or", np.round(np.max(differenceResults)/resultsL2[np.argmax(differenceResults)]*100,3), "% w.r.t. the L2 sizing." )
    print("The mean difference between the sizing of L2 and L3 was:", np.round(np.mean(differenceResults), 3), "m or", np.round(np.mean(differenceResults)/np.mean(resultsL2) * 100, 3), "% w.r.t. the L2 sizing.")