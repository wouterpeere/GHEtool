# import all the relevant functions
from GHEtool import *
from statistics import mean
import time

if __name__ == "__main__":

    #Option 0

    ground_data = GroundConstantTemperature(k_s=2.88, T_g=22.09, volumetric_heat_capacity=2.55*10**6)
    fluid_data = FluidData(0.197, 0.593, 997, 4180, 1e-3)
    pipe_data = MultipleUTube(k_g=0.73, r_in=0.0137, r_out=0.0167,k_p= 0.39, D_s=0.0265, number_of_pipes=1)

    # initiate borefield
    borefield = Borefield()
    borehole = Borehole()
    # set ground data in borefield
    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.create_rectangular_borefield(N_1=1, N_2=1, B_1=0, B_2=0, H=18.3, D=0, r_b=0.063)
    borefield.set_Rb(0.165)
    # .borehole.use_constant_Rb = True

    # This function sets the options for the gfunction calculation of pygfunction.
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

    load = HourlyGeothermalLoad()
    load.load_hourly_profile("Sandbox_Q_elec_1uur.csv", header=True, separator=";", col_heating=1, col_cooling=0)
    borefield.load = load

    borefield.print_temperature_profile(plot_hourly=True)

    file_0 = borefield.results.peak_cooling

    # Option 1

    ground_data = GroundConstantTemperature(k_s=2.88, T_g=22.09, volumetric_heat_capacity=2.55 * 10 ** 6)
    fluid_data = FluidData(0.197, 0.593, 997, 4180, 1e-3)
    pipe_data = MultipleUTube(k_g=0.73, r_in=0.0137, r_out=0.0167, k_p=0.39, D_s=0.0265, number_of_pipes=1)

    # initiate borefield
    borefield = Borefield()
    # set ground data in borefield
    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.create_rectangular_borefield(N_1=1, N_2=1, B_1=0, B_2=0, H=18.3, D=0, r_b=0.063)
    borefield.set_Rb(0.165)
    # .borehole.use_constant_Rb = True

    # This function sets the options for the gfunction calculation of pygfunction.
    options = {'nSegments': 12,
               'segment_ratios': None,
               'disp': False,
               'profiles': True,
               'method': 'equivalent',
               'cyl_correction': True,
               'use_short_term_g_function': False,
               'use_short_term_trc': False,
               'to_combine': False

               }

    borefield.set_options_gfunction_calculation(options)

    load = HourlyGeothermalLoad()
    load.load_hourly_profile("Sandbox_Q_elec_1uur.csv", header=True, separator=";", col_heating=1, col_cooling=0)
    borefield.load = load

    borefield.print_temperature_profile(plot_hourly=True)

    file_1 = borefield.results.peak_cooling

    # Option 2

    ground_data = GroundConstantTemperature(k_s=2.88, T_g=22.09, volumetric_heat_capacity=2.55 * 10 ** 6)
    fluid_data = FluidData(0.197, 0.593, 997, 4180, 1e-3)
    pipe_data = MultipleUTube(k_g=0.73, r_in=0.0137, r_out=0.0167, k_p=0.39, D_s=0.0265, number_of_pipes=1)

    # initiate borefield
    borefield = Borefield()
    # set ground data in borefield
    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.create_rectangular_borefield(N_1=1, N_2=1, B_1=0, B_2=0, H=18.3, D=0, r_b=0.063)
    borefield.set_Rb(0.165)
    # .borehole.use_constant_Rb = True

    # This function sets the options for the gfunction calculation of pygfunction.
    options = {'nSegments': 12,
               'segment_ratios': None,
               'disp': False,
               'profiles': True,
               'method': 'equivalent',
               'cyl_correction': False,
               'use_short_term_g_function': True,
               'use_short_term_trc': False,
               'to_combine': False

               }

    borefield.set_options_gfunction_calculation(options)

    load = HourlyGeothermalLoad()
    load.load_hourly_profile("Sandbox_Q_elec_1uur.csv", header=True, separator=";", col_heating=1, col_cooling=0)
    borefield.load = load

    borefield.print_temperature_profile(plot_hourly=True)

    file_2 = borefield.results.peak_cooling

    # Option 3

    ground_data = GroundConstantTemperature(k_s=2.88, T_g=22.09, volumetric_heat_capacity=2.55 * 10 ** 6)
    fluid_data = FluidData(0.197, 0.593, 997, 4180, 1e-3)
    pipe_data = MultipleUTube(k_g=0.73, r_in=0.0137, r_out=0.0167, k_p=0.39, D_s=0.0265, number_of_pipes=1)

    # initiate borefield
    borefield = Borefield()
    # set ground data in borefield

    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.create_rectangular_borefield(N_1=1, N_2=1, B_1=0, B_2=0, H=18.3, D=0, r_b=0.063)
    borefield.set_Rb(0.165)
    #.borehole.use_constant_Rb = True

    # This function sets the options for the gfunction calculation of pygfunction.
    options = {'nSegments': 12,
               'segment_ratios': None,
               'disp': False,
               'profiles': True,
               'method': 'equivalent',
               'cyl_correction': False,
               'use_short_term_g_function': False,
               'use_short_term_trc': False,
               'to_combine': True

               }

    borefield.set_options_gfunction_calculation(options)

    load = HourlyGeothermalLoad()
    load.load_hourly_profile("Sandbox_Q_elec_1uur.csv", header=True, separator=";", col_heating=1, col_cooling=0)
    borefield.load = load

    borefield.print_temperature_profile(plot_hourly=True)

    file_3 = borefield.results.peak_cooling

    # Option 4

    ground_data = GroundConstantTemperature(k_s=2.88, T_g=22.09, volumetric_heat_capacity=2.55 * 10 ** 6)
    fluid_data = FluidData(0.197, 0.593, 997, 4180, 1e-3)
    pipe_data = MultipleUTube(k_g=0.73, r_in=0.0137, r_out=0.0167, k_p=0.39, D_s=0.0265, number_of_pipes=1)

    # initiate borefield
    borefield = Borefield()
    # set ground data in borefield
    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.create_rectangular_borefield(N_1=1, N_2=1, B_1=0, B_2=0, H=18.3, D=0, r_b=0.063)
    borefield.set_Rb(0.165)
    # .borehole.use_constant_Rb = True

    # This function sets the options for the gfunction calculation of pygfunction.
    options = {'nSegments': 12,
               'segment_ratios': None,
               'disp': False,
               'profiles': True,
               'method': 'equivalent',
               'cyl_correction': True,
               'use_short_term_g_function': False,
               'use_short_term_trc': False,
               'to_combine': True

               }

    borefield.set_options_gfunction_calculation(options)

    load = HourlyGeothermalLoad()
    load.load_hourly_profile("Sandbox_Q_elec_1uur.csv", header=True, separator=";", col_heating=1, col_cooling=0)
    borefield.load = load

    borefield.print_temperature_profile(plot_hourly=True)

    file_4 = borefield.results.peak_cooling

    # size the borefield and plot the resulting temperature evolution
    #depth = borefield.size(100, L4_sizing=True)
    #print(depth)
    #borefield.print_temperature_profile()
    #borefield.print_temperature_profile(plot_hourly=True)
    #borefield.print_temperature_profile_comparison("Sandbox_Tf_1uur_T0_crr.csv", file, compare = False, plot_hourly=True)


    borefield.print_temperature_profile_comparison("Sandbox_Tf_1uur_T0_crr.csv", "Modelica_Tf_dynamic.csv", "Modelica_Tf_static.csv", file_0, file_1, file_2, file_3, file_4,
                                                    plot_hourly=True)