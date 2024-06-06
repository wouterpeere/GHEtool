"""
Test file for testing short-term dynamic effects in borehole. This test uses the short_term_effects.py file to override pygfunction 
and thereby modifies the g-function to incorporate the short-term effects. It makes uses of a 1D numerical model defined in 
Dynamic_borehole_model.py
"""

import sys
sys.path.append("C:\Workdir\Develop\ghetool")

from GHEtool import *
import numpy as np
import pygfunction as gt
import time


def test_short_term_effects():

    # initiate ground, fluid and pipe data
    ground_data = GroundFluxTemperature(k_s=1.8, T_g=17.5, volumetric_heat_capacity=2073600, flux=0)
    fluid_data = FluidData(mfr=0.1, rho=1052, Cp=3795, mu=0.0052, k_f=0.48)
    pipe_data = MultipleUTube(r_in=0.0137, r_out=0.0167, D_s=0.075/2, k_g=1.4, k_p=0.43)
    # Addidional input data needed for short-term model
    fluid_factor = 2 # 2 by default, make function to calculate this
    x = 1 # 1 by default, parameter to modify final time 
    u_tube = 1 # 1 for single U tube, 2 for dubble U tube (not yet possible) 
    rho_cp_grout = 3800000.0  # 3800000.0 by default
    rho_cp_pipe = 1800000.0  # 1800000.0 by default

    # initiate borefield
    borefield = Borefield()

    # set ground data in borefield
    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.create_rectangular_borefield(1, 1, 6, 6, 110, 4, 0.075)
    borefield.set_Rb(0.13)

    # Sample dictionary with example values
    short_term_effects_parameters = {
    'fluid_factor': fluid_factor,
    'x': x,
    'u_tube': u_tube,
    'rho_cp_grout': rho_cp_grout,
    'rho_cp_pipe': rho_cp_pipe
    }

    options = {'nSegments': 12,
                   'segment_ratios': None,
                   'disp': False,
                   'profiles': True,
                   'method': 'equivalent',
                   'cylindrical_correction': False,
                   'short_term_effects': True,
                   'ground_data': ground_data,
                   'fluid_data': fluid_data,
                   'pipe_data': pipe_data,
                   'short_term_effects_parameters': short_term_effects_parameters,
                     }


    borefield.set_options_gfunction_calculation(options)

    # set temperature bounds
    borefield.set_max_avg_fluid_temperature(35)
    borefield.set_min_avg_fluid_temperature(0)
    
    # load the hourly profile
    load = HourlyGeothermalLoad(simulation_period=10)
    load.load_hourly_profile("C:\\Workdir\\Develop\\ghetool\\GHEtool\\Examples\\test1a.csv", header=True, separator=",", col_heating=1, col_cooling=0)
    borefield.load = load

    # according to L4
    L4_start = time.time()
    depth_L4 = borefield.size(100, L4_sizing=True)
    L4_stop = time.time()

    print("The sizing according to L4 took", round((L4_stop - L4_start) * 1000, 4), "ms and was", depth_L4, "m.")


if __name__ == "__main__":
    test_short_term_effects()