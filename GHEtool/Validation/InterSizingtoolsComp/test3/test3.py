"""
The work of (Ahmadfard and Bernier, 2019) provides a set of test cases that can be used to compare
software tools with the ultimate goal of improving the reliability of design methods for sizing
vertical ground heat exchangers. This document delivers the results on the test file using the GHEtool
L2-, L3- and L4-sizing methods.

Test 3 – Required length during the first year

References:
-----------
    - Ahmadfard, M., and M. Bernier. 2019. A review of vertical ground heat exchanger sizing tools including an inter-model
comparison [in eng]. Renewable sustainable energy reviews (OXFORD) 110:247–265.
"""
# import all the relevant functions
from GHEtool import *
from statistics import mean
import time

if __name__ == "__main__":

    # initiate ground, fluid and pipe data
    ground_data = GroundFluxTemperature(k_s=2.25, T_g=10, volumetric_heat_capacity=2592000, flux=0)
    fluid_data = FluidData(mfr=33.1 / 49, rho=1026, Cp=4019, mu=0.003377, k_f=0.468)
    pipe_data = MultipleUTube(r_in=0.013, r_out=0.0167, D_s=0.075 / 2, k_g=1.73, k_p=0.4, number_of_pipes=1)

    # start test with dynamic Rb*
    # initiate borefield
    borefield = Borefield()

    # set ground data in borefield
    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.create_rectangular_borefield(7, 7, 5, 5, 110, 2.5, 0.075)

    options = {'nSegments': 12,
               'segment_ratios': None,
               'disp': False,
               'profiles': True,
               'method': 'equivalent'
               }

    borefield.set_options_gfunction_calculation(options)

    # load the hourly profile
    load = HourlyGeothermalLoad(simulation_period=10)
    load.load_hourly_profile("test3.csv", header=True, separator=",", col_heating=1, col_cooling=0)
    borefield.load = load

    Qmax = load.hourly_heating_load.max()

    if load.hourly_cooling_load.max() > Qmax:
        Qmax = load.hourly_cooling_load.max()
    Dt = Qmax * 1000 / (fluid_data.Cp * fluid_data.mfr) / 49

    # set temperature bounds
    borefield.set_max_avg_fluid_temperature(35 + Dt / 2)
    borefield.set_min_avg_fluid_temperature(0 - Dt / 2)

    # Sizing with dynamic Rb
    # according to L2
    L2_start = time.time()
    depth_L2 = borefield.size(100, L2_sizing=True)
    L2_stop = time.time()

    # according to L3
    L3_start = time.time()
    depth_L3 = borefield.size(100, L3_sizing=True)
    L3_stop = time.time()

    # according to L4
    L4_start = time.time()
    depth_L4 = borefield.size(100, L4_sizing=True)
    L4_stop = time.time()

    spacing = [3, 5, 7]
    simulationperiod = [1, 10]
    results = []

    for s in simulationperiod:
        for B in spacing:

            # start test with constant Rb*
            # initiate borefield
            borefield = Borefield()

            # set ground data in borefield
            borefield.set_ground_parameters(ground_data)
            borefield.set_fluid_parameters(fluid_data)
            borefield.set_pipe_parameters(pipe_data)
            borefield.create_rectangular_borefield(7, 7, B, B, 110, 2.5, 0.075)
            Rb_static = 0.1
            borefield.set_Rb(Rb_static)
            borefield.set_options_gfunction_calculation(options)

            # set temperature bounds
            borefield.set_max_avg_fluid_temperature(35 + Dt/2)
            borefield.set_min_avg_fluid_temperature(0 - Dt/2)

            # load the hourly profile
            load = HourlyGeothermalLoad(simulation_period=s)
            load.load_hourly_profile("test3.csv", header=True, separator=",", col_heating=1, col_cooling=0)
            borefield.load = load

            #Sizing with constant Rb

            L2s_start = time.time()
            depth_L2s = borefield.size(100, L2_sizing=True)
            results.append(depth_L2s)
            L2s_stop = time.time()

            # according to L3
            L3s_start = time.time()
            depth_L3s = borefield.size(100, L3_sizing=True)
            results.append(depth_L3s)
            L3s_stop = time.time()

            # according to L4
            L4s_start = time.time()
            depth_L4s = borefield.size(100, L4_sizing=True)
            results.append(depth_L4s)
            L4s_stop = time.time()

    #peak load duration of 6 hours

    print("Results for a peak load duration of 6 hours:")
    print("The sizing according to L2 has a depth of", depth_L2, "m (using dynamic Rb*) and", results[12],
          "m (using constant Rb*)")
    print("The sizing according to L3 has a depth of", depth_L3, "m (using dynamic Rb*) and", results[13],
          "m (using constant Rb*)")
    print("The sizing according to L4 has a depth of", depth_L4, "m (using dynamic Rb*) and", results[14],
          "m (using constant Rb*)")

    #effects of spacing and design period
    print("Effects of spacing and desing period:")
    print("The sizing according to L2 using constant Rb* has a depth of", results[0], "(B=3m)", results[3], "(B=5m)",
          results[6], "(B=7m) for a simulation period of 1 year and ", results[9], "(B=3m)", results[12], "(B=5m)",
          results[15], "(B=7m) for a simulation period of 10 years")
    print("The sizing according to L3 using constant Rb* has a depth of", results[1], "(B=3m)", results[4], "(B=5m)",
          results[7], "(B=7m) for a simulation period of 1 year and ", results[10], "(B=3m)", results[13], "(B=5m)",
          results[16],
          "(B=7m) for a simulation period of 10 years")
    print("The sizing according to L4 using constant Rb* has a depth of", results[2], "(B=3m)", results[5], "(B=5m)",
          results[8], "(B=7m) for a simulation period of 1 year and ", results[11], "(B=3m)", results[14], "(B=5m)",
          results[17],
          "(B=7m) for a simulation period of 10 years")



