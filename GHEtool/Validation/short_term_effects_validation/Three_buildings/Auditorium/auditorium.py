"""
The different L4-model inclusing the short-term effects is validated based on three different buildings: an auditorium, an office and a swimming
pool. The three buildings were simulated previously in IESVE and the resulting heating and cooling demand profiles
were exported (Peere et al., 2023). 

References:
-----------
    - Meertens, L., Peere, W., and Helsen, L. (2024). Influence of short-term dynamic effects on geothermal borefield size. 
In _Proceedings of International Ground Source Heat Pump Association Conference 2024_. Montreal (Canada), 28-30 May 2024. 
https://doi.org/10.22488/okstate.24.000004 
    - Peere, W., L. Hermans, W. Boydens, and L. Helsen. 2023. Evaluation of the oversizing and computational speed of different
open-source borefield sizing methods. BS2023 Conference, Shanghai, China, April
"""
import os
import time

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

import sys
sys.path.append("C:\Workdir\Develop\ghetool")

from GHEtool import *


def Auditorium():
    ## To do:
    # check load (ground) ghetool is same as input to modelica
    # put same pipe and grout vol. heat cap in modelica
    # size this model with modelica (based on average fluid temp)

    # Rb calculated by tool
    # initiate ground, fluid and pipe data
    ground_data = GroundFluxTemperature(k_s=3, T_g=10, volumetric_heat_capacity= 2.4 * 10**6, flux=0.06)
    fluid_data = FluidData(0.2, 0.568, 998, 4180, 1e-3)
    pipe_data = MultipleUTube(1, 0.015, 0.02, 0.4, 0.05, 1)
    plot_load = True

    # initiate borefield
    borefield = Borefield()

    # set ground data in borefield
    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.create_rectangular_borefield(5, 4, 6, 6, 100, 4, 0.075)
    #borefield.set_Rb(0.12)

    # set temperature bounds
    borefield.set_max_avg_fluid_temperature(17)
    borefield.set_min_avg_fluid_temperature(3)

    # load the hourly profile
    load = HourlyGeothermalLoad(simulation_period=20)
    load.load_hourly_profile(os.path.join(os.path.dirname(__file__), 'auditorium.csv'), header=True, separator=";",
                             decimal_seperator=".", col_heating=1,
                             col_cooling=0)
    borefield.load = load

    SEER = 20
    SCOP = 4

    # load hourly heating and cooling load and convert it to geothermal loads
    primary_geothermal_load = HourlyGeothermalLoad(simulation_period=load.simulation_period)
    primary_geothermal_load.set_hourly_cooling(load.hourly_cooling_load.copy() * (1 + 1 / SEER))
    primary_geothermal_load.set_hourly_heating(load.hourly_heating_load.copy() * (1 - 1 / SCOP))
    # set geothermal load
    borefield.load = primary_geothermal_load

    if plot_load:
        #Plotting Load
        heating = load.hourly_heating_load.copy() * (1 + 1 / SCOP)
        cooling = load.hourly_cooling_load.copy() * (1 + 1 / SEER)
        t = [i for i in range(8760)]
        fig = plt.subplots(figsize =(12, 8)) 
        plt.plot(t, heating, color ='orange', lw=2, label ='Heating')
        plt.plot(t, cooling, color ='b', lw=2, label ='Cooling')
        plt.xlabel('Time [h]', fontsize = 18)
        plt.ylabel('Load [kW]', fontsize = 18)
        plt.legend(fontsize = 16)
        plt.title('Profile 1: Yearly geothermal load profile auditorium building', fontsize = 22)
        plt.show() 


    options = {'nSegments': 12,
                'segment_ratios': None,
                   'disp': False,
                   'profiles': True,
                   'method': 'equivalent'
                     }

    borefield.set_options_gfunction_calculation(options)

    # according to L4
    L4_start = time.time()
    depth_L4 = borefield.size(100, L4_sizing=True)
    Rb_L4 = borefield.Rb
    L4_stop = time.time()
    Tf_L4 = borefield.results.peak_cooling
    Tb_L4 = borefield.results.Tb

    # initiate borefield
    borefield = Borefield()

    print('start my L4 model')

    # set ground data in borefield
    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.create_rectangular_borefield(5, 4, 6, 6, 100, 4, 0.075)
    #borefield.set_Rb(0.12)
    # set temperature bounds
    borefield.set_max_avg_fluid_temperature(17)
    borefield.set_min_avg_fluid_temperature(3)

    # load the hourly profile
    borefield.load = primary_geothermal_load
    # Addidional input data needed for short-term model
    rho_cp_grout = 3800000.0  
    rho_cp_pipe = 2150000.0  

    # Sample dictionary with short-term effect parameters
    short_term_effects_parameters = {
    'rho_cp_grout': rho_cp_grout,
    'rho_cp_pipe': rho_cp_pipe,
    }

    options = {'nSegments': 12,
                   'segment_ratios': None,
                   'disp': False,
                   'profiles': True,
                   'method': 'equivalent',
                   'cylindrical_correction': True,
                   'short_term_effects': True,
                   'ground_data': ground_data,
                   'fluid_data': fluid_data,
                   'pipe_data': pipe_data,
                   'borefield': borefield,
                   'short_term_effects_parameters': short_term_effects_parameters,
                     }

    borefield.set_options_gfunction_calculation(options)

    # according to L4 including short-term effects
    L4_ste_start = time.time()
    depth_L4_ste = borefield.size(100, L4_sizing=True)
    Rb_L4_ste = borefield.Rb
    L4_ste_stop = time.time()
    Tf_L4_ste = borefield.results.peak_cooling
    Tb_L4_ste = borefield.results.Tb


    print(
        f"The sizing according to L4 has a depth of {depth_L4:.2f}m (using dynamic Rb* of {Rb_L4:.3f})")
    print(
        f"The sizing according to L4 (including short-term effects) has a depth of {depth_L4_ste:.2f}m (using dynamic Rb* of {Rb_L4_ste:.3f})")
    print(
        f"Time needed for L4-sizing is {L4_stop-L4_start:.2f}s (using dynamic Rb*)")
    print(
        f"Time needed for L4-sizing including short-term effect is {L4_ste_stop-L4_ste_start:.2f}s (using dynamic Rb*)")
    

    """
    # Load modelica data and experimental data for plotting
    # import data
    df_st = pd.read_csv(os.path.join(os.path.dirname(__file__), 'Modelica_Tf_static.csv'), header=0, decimal=".")
    df_dyn = pd.read_csv(os.path.join(os.path.dirname(__file__), 'Modelica_Tf_dynamic.csv'), header=0, decimal=".")

    # set data
    Tf_mod_st = np.array(df_st.iloc[:, 0])
    Tf_mod_dyn = np.array(df_dyn.iloc[:, 0])

    ### Plotting figures
    legend = True
    # make a time array
    time_array = borefield.load.time_L4 / 3600
    time_array = time_array[:8759]
    print(time_array)
    # plt.rc('figure')
    # create new figure and axes if it not already exits otherwise clear it.
    fig = plt.figure()
    ax = fig.add_subplot(111)
    # set axes labelsv
    ax.set_xlabel(r"Time (year)")
    ax.set_ylabel(r"Temperature ($^\circ C$)")
    ax.yaxis.label.set_color(plt.rcParams["axes.labelcolor"])
    ax.xaxis.label.set_color(plt.rcParams["axes.labelcolor"])

    # plot Temperatures
    ax.step(time_array, Tb_L4[:8759], "k-", where="post", lw=1.5, label="Tb")
    ax.step(time_array, Tb_L4_ste[:8759], "k-", where="post", lw=1.5, label="Tb incl. ste")
    ax.step(time_array, Tf_L4[:8759], "b-", where="post", lw=1, label="Tf")
    ax.step(time_array, Tf_L4_ste[:8759], "r-", where="post", lw=1, label="Tf incl. ste")
    ax.step(time_array, Tf_mod_st[:8759], "c-", where="post", lw=1, label="Tf mod static")
    ax.step(time_array, Tf_mod_dyn[:8759], "g-", where="post", lw=1, label="Tf mod dynamic")
    ax.set_xticks(range(0, 52 + 1, 5))

    # Plot legend
    if legend:
        ax.legend()
    ax.set_xlim(left=0, right=52)
    plt.show()

    """
    plt.show()

if __name__ == "__main__":  # pragma: no cover
    Auditorium()
