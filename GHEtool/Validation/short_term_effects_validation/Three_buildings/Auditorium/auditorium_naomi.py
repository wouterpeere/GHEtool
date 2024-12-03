import os
import time

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

from GHEtool import *

plot_load = True

def Auditorium():
    # Rb calculated by tool
    # initiate ground, fluid and pipe data
    ground_data = GroundTemperatureGradient(k_s=3, T_g=10, volumetric_heat_capacity= 2.4 * 10**6, gradient=2)
    fluid_data = FluidData(0.2, 0.568, 998, 4180, 1e-3)
    pipe_data = MultipleUTube(1, 0.015, 0.02, 0.4, 0.05, 1)

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
                            decimal_seperator=".", col_extraction=1,
                            col_injection=0)
    borefield.load = load

    SEER = 20
    SCOP = 4

    # load hourly heating and cooling load and convert it to geothermal loads
    primary_geothermal_load = HourlyGeothermalLoad(simulation_period=load.simulation_period)
    primary_geothermal_load.set_hourly_injection_load(load.hourly_injection_load.copy() * (1 + 1 / SEER))
    primary_geothermal_load.set_hourly_extraction_load(load.hourly_extraction_load.copy() * (1 - 1 / SCOP))
    # set geothermal load
    borefield.load = primary_geothermal_load

    if plot_load:
        #Plotting Load
        heating = load.hourly_extraction_load.copy() * (1 + 1 / SCOP)
        cooling = load.hourly_injection_load.copy() * (1 + 1 / SEER)
        t = [i for i in range(8760)]
        fig = plt.subplots(figsize =(12, 8)) 
        plt.plot(t, heating, color ='orange', lw=2, label ='Heating')
        plt.plot(t, cooling, color ='b', lw=2, label ='Cooling')
        plt.xlabel('Time [h]', fontsize = 18)
        plt.ylabel('Load [kW]', fontsize = 18)
        plt.legend(fontsize = 16)
        plt.title('Profile 1: Yearly geothermal load profile auditorium building', fontsize = 22)
        plt.show() 

    #options for g-function calculation, given to other package pygfunction (Massimo)
    options = {'nSegments': 12,
                'disp': False,
                'profiles': True,
                'method': 'equivalent'
                    }

    borefield.set_options_gfunction_calculation(options)

    # according to L4
    L4_start = time.time()
    depth_L4 = borefield.size(100, L4_sizing=True)
    borefield.print_temperature_profile(plot_hourly=True)
    Rb_L4 = borefield.Rb
    L4_stop = time.time()
    Tf_L4 = borefield.results.peak_injection #you can use this for comparing different scenario's of fluid temperature on one plot
    Tb_L4 = borefield.results.Tb
  
    print(
        f"The sizing according to L4 has a depth of {depth_L4:.2f}m (using dynamic Rb* of {Rb_L4:.3f})")
    print(
        f"Time needed for L4-sizing is {L4_stop-L4_start:.2f}s (using dynamic Rb*)")
    
if __name__ == "__main__":  # pragma: no cover
    Auditorium()