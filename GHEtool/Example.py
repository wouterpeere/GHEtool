# import all the relevant functions
import time

if __name__ == "__main__":
    start_time = time.time()
    from GHEtool import GroundData, Borefield
    # relevant borefield data for the calculations
    GD = GroundData(20, 6, 1.5, 10, 0.015, 3, 10)
    """
    data = {"H": 110,           # depth (m)
            "B": 6,             # borehole spacing (m)
            "k_s": 3,           # conductivity of the soil (W/mK)
            "Tg": 10,            # Ground temperature at infinity (degrees C)
            "Rb": 0.015,           # equivalent borehole resistance (mK/W)
            "N_1": 12,           # width of rectangular field (#)
            "N_2": 10}           # length of rectangular field (#)}
    """

    # Montly loading values
    peakCooling = [7.24006803112718, 7.91640793466793 , 7.93142796562257 , 30.6245989476554 , 92.0857774159487 , 99.3846552040444 , 94.3169463382497 , 94.5627877909329 , 55.5394812600721 , 20.1632367197915 , 7.32336560997682 , 6.84875737909299]
    #   [0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.]              # Peak cooling in kW
    peakHeating = [146.21610153779, 133.098259924366 , 119.962665173753 , 98.6222446348889 , 80.1705151831765 , 57.4771989928561 , 51.5559710176718 , 53.0995883686714 , 80.0904631601402 , 100.829455068718 , 121.321791749458 , 133.968329018649]
    #  [160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.]             # Peak heating in kW

    # annual heating and cooling load
    annualHeatingLoad = 27_543  # kWh
    annualCoolingLoad = 8_819  # kWh

    # percentage of annual load per month (15.5% for January ...)
    montlyLoadHeatingPercentage = [0.200107800528595 , 0.159389250764114 , 0.118299355546073 , 0.0554851541806094 , 0.0220409343536828 , 0.00742482737237752 , 0.004648224055289 , 0.00602266709040733 , 0.0212199071059557 , 0.0664226889022011 , 0.134971438051717 , 0.203967752048978]
    # [0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144]
    montlyLoadCoolingPercentage = [0.0079985106033993 , 0.00811428411889902 , 0.0135214509418991 , 0.040233393972715 , 0.124233421785196 , 0.195477891394806 , 0.235326108235187 , 0.252794281055884 , 0.0849047896362326 , 0.0214925713483836 , 0.00960306246579645 , 0.00630023444160209]
    #[0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025]

    # resulting load per month
    monthlyLoadHeating = [20668.5979870973 , 16462.8881972912 , 12218.8231316104 , 5730.91275293516 , 2276.54899115827 , 766.890504407588 , 480.102595195909 , 622.065129759708 , 2191.74728890129 , 6860.62137765313 , 13940.8378157288 , 21067.2820264688]
    #list(map(lambda x: x * annualHeatingLoad, montlyLoadHeatingPercentage))   # kWh
    monthlyLoadCooling = [264.540599715167 , 268.369661991888 , 447.20485082173 , 1330.66850790887 , 4108.86295377989 , 6465.1834803671 , 7783.11274285434 , 8360.8504171598 , 2808.118296363 , 710.839554492314 , 317.609118718222 , 208.372268309458]
    #list(map(lambda x: x * annualCoolingLoad, montlyLoadCoolingPercentage))   # kWh

    # create the borefield object

    borefield = Borefield(simulationPeriod=20,
                          peakHeating=peakHeating,
                          peakCooling=peakCooling,
                          baseloadHeating=monthlyLoadHeating,
                          baseloadCooling=monthlyLoadCooling)

    borefield.setGroundParameters(GD)

    # set temperature boundaries
    borefield.setMaxGroundTemperature(16)   # maximum temperature
    borefield.setMinGroundTemperature(0)    # minimum temperature

    # size borefield
    depth = borefield.size(GD.H)
    print(depth)

    # print imbalance
    print(borefield.imbalance)  # print imbalance

    # plot temperature profile for the calculated depth
    #borefield.printTemperatureProfile(legend=True)

    # plot temperature profile for a fixed depth
    #borefield.printTemperatureProfileFixedDepth(depth=75, legend=False)

    # print gives the array of montly tempartures for peak cooling without showing the plot
    #borefield.calculateTemperatures(depth=90)
    #print(borefield.resultsPeakCooling)
    print(f'Calculation Time: {time.time() - start_time}')
    # Custom field
    """When working on a custom borefield configuration, one needs to import this configuration into the GHEtool.
    Based on the pygfunction, one creates his custom borefield and gives it as an argument to the class initiater 
    Borefield of GHEtool.
    
    You also need a custom g-function file for interpolation. This can also be given as an argument to the class 
    initiater as customGfunction.
    This custom variable, must contain gfunctions for all time steps in Borefield.defaultTimeArray, and should be 
    structured as follows:
    {"Time":Borefield.defaultTimeArray,"Data":[[Depth1,[Gfunc1,Gfunc2 ...]],[Depth2,[Gfunc1, Gfunc2 ...]]]}.
    
    However, one can use the function 'createCustomDataset' when a custom borefield is given. This will make the 
    required dataset for the optimisation.
    Please note that, depending on the complexity of the custom field, this can range between 5 minutes and 5 hours. 
    """
    """
    # Montly loading values
    peakCooling = [0., 0, 3.4, 6.9, 13., 18., 21., 50., 16., 3.7, 0., 0.]  # Peak cooling in kW
    peakHeating = [60., 42., 10., 5., 0., 0., 0., 0., 4.4, 8.5, 19., 36.]  # Peak heating in kW

    # annual heating and cooling load
    annualHeatingLoad = 30 * 10 ** 3  # kWh
    annualCoolingLoad = 16 * 10 ** 3  # kWh

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

    borefield.setGroundParameters(GD)

    # set temperature boundaries
    borefield.setMaxGroundTemperature(16)  # maximum temperature
    borefield.setMinGroundTemperature(0)  # minimum temperature
    from pygfunction import boreholes as gt_boreholes
    customField = gt_boreholes.L_shaped_field(N_1=3, N_2=3, B_1=5., B_2=5., H=100., D=4, r_b=0.05)
    borefield.createCustomDataset(customField, "customField1")
    borefield.setCustomGfunction("customfield1")
    borefield.setBorefield(customField)
    #borefield.printTemperatureProfileFixedDepth(100)
    print(f'Calculation Time: {time.time() - start_time}')
    """

    # Montly loading values
    peakCooling = [9.90774198025594 , 8.80222553187507 , 15.9537424086594 , 39.6400411079079 , 93.5939286160559 , 100.864201729618 , 96.1049252306382 , 96.2447867107533 , 63.8963464509923 , 27.8181717285616 , 12.5262313640001 , 9.21466447772456]

    #   [0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.]              # Peak cooling in kW
    peakHeating = [131.898485163246 , 119.621068946396 , 105.237931052855 , 82.8311567040254 , 31.5652129440992 , 2.88970753289537 , 2.70385346383288 , 2.76840792191908 , 60.4344584633911 , 85.163473294732 , 108.387807213857 , 120.896239429697]

    # [160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.]             # Peak heating in kW

    # resulting load per month
    monthlyLoadHeating = [6354.86252558095 , 4768.52279277154 , 2816.42458773617 , 1011.29760358047 , 194.582964414328 , 41.5638533683192 , 37.5001618658962 , 42.4498274939292 , 235.224638751268 , 1392.10860042073 , 3588.39434642812 , 6523.77801459608]

    # list(map(lambda x: x * annualHeatingLoad, montlyLoadHeatingPercentage))   # kWh
    monthlyLoadCooling = [710.200596746764 , 703.058837975982 , 1089.51448317703 , 2624.70589302045 , 6419.03677579987 , 9204.79062068319 , 10689.5593644846 , 10941.7314389406 , 4364.46220366253 , 1594.99751601865 , 873.848376382275 , 618.413555866671]

    # list(map(lambda x: x * annualCoolingLoad, montlyLoadCoolingPercentage))   # kWh

    # create the borefield object

    borefield = Borefield(simulationPeriod=20,
                          peakHeating=peakHeating,
                          peakCooling=peakCooling,
                          baseloadHeating=monthlyLoadHeating,
                          baseloadCooling=monthlyLoadCooling)

    borefield.setGroundParameters(GD)

    # set temperature boundaries
    borefield.setMaxGroundTemperature(20)  # maximum temperature
    borefield.setMinGroundTemperature(0)  # minimum temperature

    # size borefield
    depth = borefield.size(GD.H)
    print(depth)
    borefield.printTemperatureProfile(legend=True)