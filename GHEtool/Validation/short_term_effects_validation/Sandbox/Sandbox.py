"""
The short-term behavior of the borefield models in Meertens et al. (2024) is validated using the Sandbox
experiment of Beier et al. (2011). The experiment consists of a constant heat injection in a borehole over a period of 52h.
The measured heat injection rate together with the borefield parameters are used to simulate the fluid
temperatures as the average between the inlet and outlet temperature

References:
-----------
    - Beier, R. A., M. D. Smith, and J. D. Spitler. 2011. Reference data sets for vertical borehole ground heat exchanger models
and thermal response test analysis. Geothermics (Oxford-New York) 40 (1): 79–85.
    - Meertens, L., Peere, W., and Helsen, L. (2024). Influence of short-term dynamic effects on geothermal borefield size. 
In _Proceedings of International Ground Source Heat Pump Association Conference 2024_. Montreal (Canada), 28-30 May 2024. 
https://doi.org/10.22488/okstate.24.000004 
"""
import os
import time

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

import sys
sys.path.append("C:\Workdir\Develop\ghetool")

from GHEtool import *


def Sandbox():
    # initiate ground, fluid and pipe data
    ground_data = GroundConstantTemperature(k_s=2.88, T_g=22.09, volumetric_heat_capacity=2.55*10**6)
    fluid_data = FluidData(0.197, 0.593, 997, 4180, 1e-3)
    pipe_data = MultipleUTube(k_g=0.73, r_in=0.0137, r_out=0.0167,k_p= 0.39, D_s=0.0265, number_of_pipes=1)

    # initiate borefield
    borefield = Borefield()

    # set ground data in borefield
    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.create_rectangular_borefield(N_1=1, N_2=1, B_1=0, B_2=0, H=18.3, D=0, r_b=0.063)
    borefield.set_Rb(0.165)

    # load the hourly profile
    load = HourlyGeothermalLoad(simulation_period=10)
    load.load_hourly_profile(os.path.join(os.path.dirname(__file__), 'Sandbox_Q_elec_1uur.csv'), header=True, separator=";",
                             decimal_seperator=".", col_heating=1,
                             col_cooling=0)
    borefield.load = load

    borefield.calculate_temperatures(hourly=True)
    Tf_L4 = borefield.results.peak_cooling
    Tb_L4 = borefield.results.Tb

    # initiate borefield
    borefield = Borefield()

    # set ground data in borefield
    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.create_rectangular_borefield(N_1=1, N_2=1, B_1=0, B_2=0, H=18.3, D=0, r_b=0.063)
    borefield.set_Rb(0.165)

    # load the hourly profile
    borefield.load = load

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

    borefield.calculate_temperatures(hourly=True)
    Tf_L4_ste = borefield.results.peak_cooling
    Tb_L4_ste = borefield.results.Tb

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


if __name__ == "__main__":  # pragma: no cover
    Sandbox()
