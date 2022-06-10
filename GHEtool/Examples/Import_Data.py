"""
This document is an example on how to import hourly load profiles into GHEtool.

"""
# import all the relevant functions
from GHEtool import *

if __name__ == "__main__":

    # initiate ground data
    data = GroundData(110, 6, 3, 10, 0.2, 10, 10)

    # initiate borefield
    borefield = Borefield()

    # set ground data in borefield
    borefield.setGroundParameters(data)

    # load the hourly profile
    borefield.loadHourlyProfile("Hourly_Profile.csv", header=True, separator=";", firstColumnHeating=True)
    borefield.convertHourlyToMonthly()

    # size the borefield and plot the resulting temperature evolution
    borefield.size(100)
    borefield.printTemperatureProfile()
