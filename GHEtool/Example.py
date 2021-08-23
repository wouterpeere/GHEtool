# import all the relevant functions
from GHEtool import *
if __name__ == "__main__":
    # relevant borefield data for the calculations
    data = {"H": 110,           # depth (m)
            "B": 6,             # borehole spacing (m)
            "k_s": 3,           # conductivity of the soil (W/mK)
            "Tg":10,            # Ground temperature at infinity (degrees C)
            "Rb":0.2,           # equivalent borehole resistance (K/W)
            "N_1":12,           # width of rectangular field (#)
            "N_2":10}           # length of rectangular field (#)}

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
    montlyLoadHeating = list(map(lambda x: x * annualHeatingLoad, montlyLoadHeatingPercentage))   # kWh
    montlyLoadCooling = list(map(lambda x: x * annualCoolingLoad, montlyLoadCoolingPercentage))   # kWh

    # create the borefield object

    borefield = Borefield(simulationPeriod=20,
                         peakHeating=peakHeating,
                         peakCooling=peakCooling,
                         baseloadHeating=montlyLoadHeating,
                         baseloadCooling=montlyLoadCooling)

    borefield.setGroundParameters(data)

    # set temperature boundaries
    borefield.setMaxGroundTemperature(16)   # maximum temperature
    borefield.setMinGroundTemperature(0)    # minimum temperature

    # size borefield
    depth = borefield.size(100)
    print (depth)

    #print imbalance
    print (borefield.imbalance) # print imbalance

    # plot temperature profile for the calculated depth
    borefield.printTemperatureProfile(legend=True)

    #plot temperature profile for a fixed depth
    borefield.printTemperatureProfileFixedDepth(depth=75,legend=False)

    # print gives the array of montly tempartures for peak cooling without showing the plot
    borefield.calculateTemperatures(depth=90)
    print (borefield.resultsPeakCooling)

    ### Custom field
    """When working on a custom borefield configuration, one needs to import this configuration into the GHEtool.
    Based on the pygfunction, one creates his custom borefield and gives it as an argument to the class initiater Borefield of GHEtool.
    
    You also need a custom g-function file for interpolation. This can also be given as an argument to the class initiater as customGfunction.
    This custom variable, must contain gfunctions for all time steps in Borefield.defaultTimeArray, and should be structured as follows:
    {"Time":Borefield.defaultTimeArray,"Data":[[Depth1,[Gfunc1,Gfunc2 ...]],[Depth2,[Gfunc1, Gfunc2 ...]]]}.
    
    However, one can use the function 'createCustomDataset' when a custom borefield is given. This will make the required dataset for the optimisation.
    Please note that, depending on the complexity of the custom field, this can range between 5 minutes and 5 hours. 
    """

    # Montly loading values
    peakCooling = [0., 0, 3.4, 6.9, 13., 18., 21., 50., 16., 3.7., 0., 0.]  # Peak cooling in kW
    peakHeating = [60., 42., 10., 5., 0., 0., 0., 0., 4.4, 8.5, 19., 36.]  # Peak heating in kW

    # annual heating and cooling load
    annualHeatingLoad = 30 * 10 ** 3  # kWh
    annualCoolingLoad = 16 * 10 ** 3  # kWh

    # percentage of annual load per month (15.5% for January ...)
    montlyLoadHeatingPercentage = [0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144]
    montlyLoadCoolingPercentage = [0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025]

    # resulting load per month
    montlyLoadHeating = list(map(lambda x: x * annualHeatingLoad, montlyLoadHeatingPercentage))  # kWh
    montlyLoadCooling = list(map(lambda x: x * annualCoolingLoad, montlyLoadCoolingPercentage))  # kWh

    # create the borefield object

    borefield = Borefield(simulationPeriod=20,
                          peakHeating=peakHeating,
                          peakCooling=peakCooling,
                          baseloadHeating=montlyLoadHeating,
                          baseloadCooling=montlyLoadCooling)

    borefield.setGroundParameters(data)

    # set temperature boundaries
    borefield.setMaxGroundTemperature(16)  # maximum temperature
    borefield.setMinGroundTemperature(0)  # minimum temperature

    customField = gt.boreholes.L_shaped_field(N_1=3, N_2=3, B_1=5., B_2=5.,H=100., D=4, r_b=0.05)
    Borefield.createCustomDataset(borefield,customField,"customField")
    borefield.setCustomGfunction("customfield")
    borefield.setBorefield(customField)
    borefield.printTemperatureProfileFixedDepth(100)