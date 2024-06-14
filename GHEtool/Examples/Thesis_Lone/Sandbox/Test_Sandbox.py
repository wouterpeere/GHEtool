import pygfunction as gt
import numpy as np
import matplotlib.pyplot as plt

# import all the relevant functions
from GHEtool import *


def main():

    #option 0
    # initiate ground data
    data_ground = GroundData(k_s=2.88, T_g=22.09, R_b=0.165, volumetric_heat_capacity=2.55*10**6)
    data_fluid = FluidData(0.197, 0.593, 997, 4180, 1e-3)
    data_pipe = PipeData(k_g=0.73, r_in=0.0137, r_out=0.0167, k_p=0.39, D_s= 0.0265, number_of_pipes=1)
    borefield_gt = gt.boreholes.rectangle_field(N_1=1, N_2=1, B_1=0, B_2=0, D=0, H=18.3, r_b=0.063)
    borefield = Borefield()

    # This function sets the options for the gfunction calculation of pygfunction.
    options = {'nSegments': 12,
               'segment_ratios': None,
               'disp': True,
               'profiles': True,
               'cyl_correction': False,
               'use_cylindricalHeatSource': False,
               'use_short_term_g_function': False,
               'use_short_term_trc': True,
               'to_combine': False
               }

    borefield.set_options_gfunction_calculation(options)

    # set ground data in borefield
    borefield.set_ground_parameters(data_ground)

    borefield.set_pipe_parameters(data_pipe)

    borefield.set_fluid_parameters(data_fluid)

    #borefield.sizing_setup(use_constant_Rb=False)

    # aangezien pijp horizontaal ligt en niet verticaal
    borefield.sizing_setup(use_constant_Tg=True)

    # set borefield
    borefield.set_borefield(borefield_gt)


    # load the hourly profile
    borefield.load_hourly_profile("Sandbox_Q_elec_1uur.csv", header=True, separator=";",
                                  first_column_heating=False)


    borefield.print_temperature_profile(plot_hourly=True)


    file_option_0 = borefield.results_peak_cooling

    # Option 1
    # initiate borefield
    borefield = Borefield()

    options = {'nSegments': 12,
               'segment_ratios': None,
               'disp': True,
               'profiles': True,
               'cyl_correction': True,
               'use_cylindricalHeatSource': False,
               'use_short_term_g_function': False,
               'use_short_term_trc': False,
               'to_combine': False
               }

    borefield.set_options_gfunction_calculation(options)

    # set ground data in borefield
    borefield.set_ground_parameters(data_ground)

    borefield.set_pipe_parameters(data_pipe)

    borefield.set_fluid_parameters(data_fluid)

    #borefield.sizing_setup(use_constant_Rb=False)

    # aangezien pijp horizontaal ligt en niet verticaal
    borefield.sizing_setup(use_constant_Tg=True)

    # set borefield
    borefield.set_borefield(borefield_gt)

    # load the hourly profile
    borefield.load_hourly_profile("Sandbox_Q_elec_1uur.csv", header=True, separator=";",
                                  first_column_heating=False)

    borefield.print_temperature_profile(plot_hourly=True)


    file_option_1 = borefield.results_peak_cooling

    # Option 2
    # initiate borefield
    borefield = Borefield()

    options = {'nSegments': 12,
               'segment_ratios': None,
               'disp': True,
               'profiles': True,
               'cyl_correction': False,
               'use_cylindricalHeatSource': False,
               'use_short_term_g_function': True,
               'use_short_term_trc': False,
               'to_combine': False
               }

    borefield.set_options_gfunction_calculation(options)

    # set ground data in borefield
    borefield.set_ground_parameters(data_ground)

    borefield.set_pipe_parameters(data_pipe)

    borefield.set_fluid_parameters(data_fluid)

    #borefield.sizing_setup(use_constant_Rb=False)

    # aangezien pijp horizontaal ligt en niet verticaal
    borefield.sizing_setup(use_constant_Tg=True)

    # set borefield
    borefield.set_borefield(borefield_gt)

    # load the hourly profile
    borefield.load_hourly_profile("Sandbox_Q_elec_1uur.csv", header=True, separator=";",
                                  first_column_heating=False)

    borefield.print_temperature_profile(plot_hourly=True)


    file_option_2 = borefield.results_peak_cooling

    # Option 3
    # initiate borefield
    borefield = Borefield()

    options = {'nSegments': 12,
               'segment_ratios': None,
               'disp': False,
               'profiles': True,
               'cyl_correction': False,
               'use_cylindricalHeatSource': False,
               'use_short_term_g_function': False,
               'use_short_term_trc': False,
               'to_combine': True
               }

    borefield.set_options_gfunction_calculation(options)

    # set ground data in borefield
    borefield.set_ground_parameters(data_ground)

    borefield.set_pipe_parameters(data_pipe)

    borefield.set_fluid_parameters(data_fluid)

    #borefield.sizing_setup(use_constant_Rb=False)

    # aangezien pijp horizontaal ligt en niet verticaal
    borefield.sizing_setup(use_constant_Tg=True)

    # set borefield
    borefield.set_borefield(borefield_gt)

    # load the hourly profile
    borefield.load_hourly_profile("Sandbox_Q_elec_1uur.csv", header=True, separator=";",
                                  first_column_heating=False)

    borefield.print_temperature_profile(plot_hourly=True)


    file_option_3 = borefield.results_peak_cooling

    # Option 4
    # initiate borefield
    borefield = Borefield()

    options = {'nSegments': 12,
               'segment_ratios': None,
               'disp': True,
               'profiles': True,
               'cyl_correction': False,
               'use_cylindricalHeatSource': False,
               'use_short_term_g_function': False,
               'use_short_term_trc': False,
               'to_combine': True
               }

    borefield.set_options_gfunction_calculation(options)

    # set ground data in borefield
    borefield.set_ground_parameters(data_ground)

    borefield.set_pipe_parameters(data_pipe)

    borefield.set_fluid_parameters(data_fluid)

    #borefield.sizing_setup(use_constant_Rb=False)

    # aangezien pijp horizontaal ligt en niet verticaal
    borefield.sizing_setup(use_constant_Tg=True)

    # set borefield
    borefield.set_borefield(borefield_gt)

    # load the hourly profile
    borefield.load_hourly_profile("Sandbox_Q_elec_1uur.csv", header=True, separator=";",
                                  first_column_heating=False)



    #Compare all

    borefield.print_temperature_profile_comparison_modelica("Sandbox_Tf_1uur_T0_crr.csv", "Modelica_Tf_dynamic.csv", "Modelica_Tf_static.csv", file_option_0, file_option_1, file_option_2, file_option_3, compare=True, plot_hourly=True)

    return


if __name__ == "__main__": main()