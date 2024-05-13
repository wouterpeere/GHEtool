"""
This work of (Ahmadfard and Bernier, 2019) provides a set of test cases that can be used to compare
software tools with the ultimate goal of improving the reliability of design methods for sizing
vertical ground heat exchangers. This document delivers the results on the test file using the GHEtool
L2-, L3- and L4-sizing methods.

Test 1 -Synthetic balanced load – one borehole

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
    ground_data = GroundFluxTemperature(k_s=1.8, T_g=17.5, volumetric_heat_capacity=2073600, flux=0)
    fluid_data = FluidData(mfr=0.5585, rho=1052, Cp=3795, mu=0.0052, k_f=0.48)
    pipe_data = MultipleUTube(r_in=0.0137, r_out=0.0167, D_s=0.075/2, k_g=1.4, k_p=0.43, number_of_pipes=1)

    # initiate borefield
    borefield = Borefield()
    # set ground data in borefield
    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.create_rectangular_borefield(1, 1, 6, 6, 110, 4, 0.075)

    options = {'nSegments': 12,
                   'segment_ratios': None,
                   'disp': False,
                   'profiles': True,
                   'method': 'equivalent',
                   'cyl_correction': False,
                   'use_short_term_g_function': False,
                   'use_short_term_trc': False,
                   'to_combine': False

                   }

    borefield.set_options_gfunction_calculation(options)



    # load the hourly profile
    load = HourlyGeothermalLoad(simulation_period=10)
    load.load_hourly_profile("test1b.csv", header=True, separator=";", decimal_seperator=",",col_heating=1, col_cooling=0)
    borefield.load = load

    Qmax = load.hourly_heating_load.max()

    if load.hourly_cooling_load.max() > Qmax:
        Qmax = load.hourly_cooling_load.max()

    print('Qmax in kW', Qmax)

    Dt = Qmax*1000/(fluid_data.Cp * fluid_data.mfr)

    print('Dt', Dt)

    # set temperature bounds
    borefield.set_max_avg_fluid_temperature(35 + Dt/2)
    borefield.set_min_avg_fluid_temperature(0 - Dt/2)

    # Sizing with dynamic Rb
    # according to L2
    print('Rb dynamic L2')
    L2_start = time.time()
    depth_L2 = borefield.size(100, L2_sizing=True)
    L2_stop = time.time()

    # according to L3
    print('Rb dynamic L3')
    L3_start = time.time()
    depth_L3 = borefield.size(100, L3_sizing=True)
    L3_stop = time.time()

    # according to L4
    print('Rb dynamic L4')
    L4_start = time.time()
    depth_L4 = borefield.size(100, L4_sizing=True)
    L4_stop = time.time()


    # initiate borefield
    borefield = Borefield()

    # set ground data in borefield
    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.create_rectangular_borefield(1, 1, 6, 6, 110, 4, 0.075)
    Rb_static = 0.13
    borefield.set_Rb(Rb_static)
    borefield.set_options_gfunction_calculation(options)

    # set temperature bounds
    borefield.set_max_avg_fluid_temperature(35 + Dt/2)
    borefield.set_min_avg_fluid_temperature(0 - Dt/2)

    # load the hourly profile
    load = HourlyGeothermalLoad(simulation_period=10)
    load.load_hourly_profile("test1b.csv", header=True, separator=";", decimal_seperator=",",col_heating=1, col_cooling=0)
    borefield.load = load

    #Sizing with constant Rb

    L2s_start = time.time()
    depth_L2s = borefield.size(100, L2_sizing=True)
    L2s_stop = time.time()

    # according to L3
    L3s_start = time.time()
    depth_L3s = borefield.size(100, L3_sizing=True)
    L3s_stop = time.time()

    # according to L4
    L4s_start = time.time()
    depth_L4s = borefield.size(100, L4_sizing=True)
    L4s_stop = time.time()

    borefield.print_temperature_profile(plot_hourly=True)

    print("sizing with dynamic Rb")
    print("The sizing according to L2 took", round((L2_stop - L2_start) * 1000, 4), "ms and was", depth_L2, "m.")
    print("The sizing according to L3 took", round((L3_stop - L3_start) * 1000, 4), "ms and was", depth_L3, "m.")
    print("The sizing according to L4 took", round((L4_stop - L4_start) * 1000, 4), "ms and was", depth_L4, "m.")
    print("Sizing with static Rb of", Rb_static)
    print("The sizing according to L2 took", round((L2s_stop - L2s_start) * 1000, 4), "ms and was", depth_L2s, "m.")
    print("The sizing according to L3 took", round((L3s_stop - L3s_start) * 1000, 4), "ms and was", depth_L3s, "m.")
    print("The sizing according to L4 took", round((L4s_stop - L4s_start) * 1000, 4), "ms and was", depth_L4s, "m.")
