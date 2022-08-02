"""
This document compares the speed of the L2 sizing method of (Peere et al., 2021) with and without the precalculated gfunction data.
This is done for two fields with different sizes. It shows that, specifically for the larger fields, the precalculated data is way faster.
"""

import time

from GHEtool import Borefield, GroundData


def test64boreholes():
    data = GroundData(110, 6, 3, 10, 0.2, 8, 8)

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

    # size borefield
    t1 = time.time()
    depthPrecalculated = borefield.size(100)
    t1end = time.time()

    ### size without the precalculation

    borefield.usePrecalculatedData = False
    # size borefield
    t2 = time.time()
    depthCalculated = borefield.size(100)
    t2end = time.time()

    print("With precalculated data, the sizing took", round(t1end - t1, 3), "s for 64 boreholes.")
    print("Without the precalculated data, the sizing took", round(t2end - t2, 3), "s for 64 boreholes.")
    print("The difference in accuracy between the two results is",
          round((depthCalculated - depthPrecalculated) / depthCalculated * 100, 3), "%.")


def test10boreholes():
    data = GroundData(110, 6, 3, 10, 0.2, 2, 5)

    # montly loading values
    peakCooling = [0., 0, 3., 9., 13., 20., 43., 30., 16., 7., 0., 0.]  # Peak cooling in kW
    peakHeating = [16., 14, 10., 5., 0., 0., 0., 0., 4, 8., 19., 13.]  # Peak heating in kW

    # annual heating and cooling load
    annualHeatingLoad = 16 * 10 ** 3  # kWh
    annualCoolingLoad = 24 * 10 ** 3  # kWh

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

    # size borefield
    t1 = time.time()
    depthPrecalculated = borefield.size(100)
    t1end = time.time()

    ### size without the precalculation

    borefield.usePrecalculatedData = False
    # size borefield
    t2 = time.time()
    depthCalculated = borefield.size(100)
    t2end = time.time()

    print("With precalculated data, the sizing took", round(t1end - t1, 3), "s for 10 boreholes.")
    print("Without the precalculated data, the sizing took", round(t2end - t2, 3), "s for 10 boreholes.")
    print("The difference in accuracy between the two results is",
          round((depthCalculated - depthPrecalculated) / depthCalculated * 100, 3), "%.")


if __name__ == "__main__":

    test10boreholes()
    test64boreholes()
