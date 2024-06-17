"""
The work of (Ahmadfard and Bernier, 2019) provides a set of test cases that can be used to compare
software tools with the ultimate goal of improving the reliability of design methods for sizing
vertical ground heat exchangers. This document delivers the results on the test file using the GHEtool
L2-, L3- and L4-sizing methods.

Test 1 -Synthetic balanced load – one borehole

References:
-----------
    - Ahmadfard, M., and M. Bernier. 2019. A review of vertical ground heat exchanger sizing tools including an inter-model
comparison [in eng]. Renewable sustainable energy reviews (OXFORD) 110:247–265.
"""
import os
import time

import numpy as np

import sys
sys.path.append("C:\Workdir\Develop\ghetool")

from GHEtool import *

def test_1a_6h_ste():
    # initiate ground, fluid and pipe data
    ground_data = GroundFluxTemperature(k_s=1.8, T_g=17.5, volumetric_heat_capacity=2073600, flux=0)
    fluid_data = FluidData(mfr=0.440, rho=1052, Cp=3795, mu=0.0052, k_f=0.48)
    pipe_data = MultipleUTube(r_in=0.0137, r_out=0.0167, D_s=0.075 / 2, k_g=1.4, k_p=0.43, number_of_pipes=1) 

    # start test with dynamic Rb*
    # initiate borefield
    borefield = Borefield()

    # set ground data in borefield
    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.create_rectangular_borefield(1, 1, 6, 6, 110, 4, 0.075)

    # load the hourly profile
    load = HourlyGeothermalLoad(simulation_period=10)
    load.load_hourly_profile(os.path.join(os.path.dirname(__file__), 'test1a.csv'), header=True, separator=",",
                             col_heating=1, col_cooling=0)
    borefield.load = load

    delta_t = max(load.max_peak_cooling, load.max_peak_cooling) * 1000 / (fluid_data.Cp * fluid_data.mfr)

    # set temperature bounds
    borefield.set_max_avg_fluid_temperature(35 + delta_t / 2)
    borefield.set_min_avg_fluid_temperature(0 - delta_t / 2)

    # according to L2
    L2_start = time.time()
    depth_L2 = borefield.size(100, L2_sizing=True)
    Rb_L2 = borefield.Rb
    L2_stop = time.time()

    # according to L3
    L3_start = time.time()
    depth_L3 = borefield.size(100, L3_sizing=True)
    Rb_L3 = borefield.Rb
    L3_stop = time.time()

    # according to L4
    L4_start = time.time()
    depth_L4 = borefield.size(100, L4_sizing=True)
    Rb_L4 = borefield.Rb
    L4_stop = time.time()

    # initiate ground, fluid and pipe data
    ground_data = GroundFluxTemperature(k_s=1.8, T_g=17.5, volumetric_heat_capacity=2073600, flux=0)
    fluid_data = FluidData(mfr=0.440, rho=1052, Cp=3795, mu=0.0052, k_f=0.48)
    pipe_data = MultipleUTube(r_in=0.0137, r_out=0.0167, D_s=0.075 / 2, k_g=1.4, k_p=0.43, number_of_pipes=1)
    # Addidional input data needed for short-term model
    rho_cp_grout = 3800000.0  
    rho_cp_pipe = 1540000.0    

    # start test with dynamic Rb*
    # initiate borefield
    borefield = Borefield()

    # set ground data in borefield
    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.create_rectangular_borefield(1, 1, 6, 6, 110, 4, 0.075)

    borefield.load = load

    # set temperature bounds
    borefield.set_max_avg_fluid_temperature(35 + delta_t / 2)
    borefield.set_min_avg_fluid_temperature(0 - delta_t / 2)

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

    # start test with constant Rb*
    # initiate borefield
    borefield = Borefield()

    # set ground data in borefield
    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.create_rectangular_borefield(1, 1, 6, 6, 110, 4, 0.075)
    Rb_static = 0.13
    borefield.set_Rb(Rb_static)

    # set temperature bounds
    borefield.set_max_avg_fluid_temperature(35 + delta_t / 2)
    borefield.set_min_avg_fluid_temperature(0 - delta_t / 2)

    # load the hourly profile
    borefield.load = load

    # Sizing with constant Rb
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
    
    # start test with constant Rb*
    # initiate borefield
    borefield = Borefield()

    # set ground data in borefield
    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.create_rectangular_borefield(1, 1, 6, 6, 110, 4, 0.075)
    Rb_static = 0.13
    borefield.set_Rb(Rb_static)
    # Addidional input data needed for short-term model
    rho_cp_grout = 3800000.0  
    rho_cp_pipe = 1540000.0

    # set temperature bounds
    borefield.set_max_avg_fluid_temperature(35 + delta_t / 2)
    borefield.set_min_avg_fluid_temperature(0 - delta_t / 2)

    # load the hourly profile
    borefield.load = load

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
    L4s_ste_start = time.time()
    depth_L4s_ste = borefield.size(100, L4_sizing=True)
    L4s_ste_stop = time.time()

    print(
        f"The sizing according to L2 has a depth of {depth_L2:.2f}m (using dynamic Rb* of {Rb_L2:.3f}) and {depth_L2s:.2f}m (using constant Rb*)")
    print(
        f"The sizing according to L3 has a depth of {depth_L3:.2f}m (using dynamic Rb* of {Rb_L3:.3f}) and {depth_L3s:.2f}m (using constant Rb*)")
    print(
        f"The sizing according to L4 has a depth of {depth_L4:.2f}m (using dynamic Rb* of {Rb_L4:.3f}) and {depth_L4s:.2f}m (using constant Rb*)")
    print(
        f"The sizing according to L4 (including short-term effects) has a depth of {depth_L4_ste:.2f}m (using dynamic Rb* of {Rb_L4_ste:.3f}) and {depth_L4s_ste:.2f}m (using constant Rb*)")
    print(
        f"Time needed for L4-sizing is {L4_stop-L4_start:.2f}s (using dynamic Rb*) or {L4s_stop-L4s_start:.2f}s (using constant Rb*)")
    print(
        f"Time needed for L4-sizing including short-term effect is {L4_ste_stop-L4_ste_start:.2f}s (using dynamic Rb*) or {L4s_ste_stop-L4s_ste_start:.2f}s (using constant Rb*)")
    
    assert np.isclose(depth_L2, 59.366333293365)
    assert np.isclose(depth_L3, 59.542511807290666)
    assert np.isclose(depth_L4, 56.2659729399716)
    assert np.isclose(depth_L4_ste, 52.34712690022354)
    assert np.isclose(depth_L2s, 59.83238790604271)
    assert np.isclose(depth_L3s, 60.00736579796592)
    assert np.isclose(depth_L4s, 56.73136082379056)
    assert np.isclose(depth_L4s_ste, 52.72442116662979)
    assert np.isclose(Rb_L2, 0.12801945735995454)
    assert np.isclose(Rb_L3, 0.1280244880933401)
    assert np.isclose(Rb_L4, 0.12793335445966403)
    assert np.isclose(Rb_L4_ste, 0.12783109689745237)


def test_1a_1h_ste():
    # initiate ground, fluid and pipe data
    ground_data = GroundFluxTemperature(k_s=1.8, T_g=17.5, volumetric_heat_capacity=2073600, flux=0)
    fluid_data = FluidData(mfr=0.440, rho=1052, Cp=3795, mu=0.0052, k_f=0.48)
    pipe_data = MultipleUTube(r_in=0.0137, r_out=0.0167, D_s=0.075 / 2, k_g=1.4, k_p=0.43, number_of_pipes=1)

    # start test with dynamic Rb*
    # initiate borefield
    borefield = Borefield()

    # set ground data in borefield
    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.create_rectangular_borefield(1, 1, 6, 6, 110, 4, 0.075)

    # load the hourly profile
    load = HourlyGeothermalLoad(simulation_period=10)
    load.load_hourly_profile(os.path.join(os.path.dirname(__file__), 'test1a.csv'), header=True, separator=",",
                             col_heating=1, col_cooling=0)
    borefield.load = load
    borefield.load.peak_duration = 1

    delta_t = max(load.max_peak_cooling, load.max_peak_cooling) * 1000 / (fluid_data.Cp * fluid_data.mfr)

    # set temperature bounds
    borefield.set_max_avg_fluid_temperature(35 + delta_t / 2)
    borefield.set_min_avg_fluid_temperature(0 - delta_t / 2)

    # according to L2
    L2_start = time.time()
    depth_L2 = borefield.size(100, L2_sizing=True)
    Rb_L2 = borefield.Rb
    L2_stop = time.time()

    # according to L3
    L3_start = time.time()
    depth_L3 = borefield.size(100, L3_sizing=True)
    Rb_L3 = borefield.Rb
    L3_stop = time.time()

    # according to L4 
    L4_start = time.time()
    depth_L4 = borefield.size(100, L4_sizing=True)
    Rb_L4 = borefield.Rb
    L4_stop = time.time()

    # initiate ground, fluid and pipe data
    ground_data = GroundFluxTemperature(k_s=1.8, T_g=17.5, volumetric_heat_capacity=2073600, flux=0)
    fluid_data = FluidData(mfr=0.440, rho=1052, Cp=3795, mu=0.0052, k_f=0.48)
    pipe_data = MultipleUTube(r_in=0.0137, r_out=0.0167, D_s=0.075 / 2, k_g=1.4, k_p=0.43, number_of_pipes=1)
    # Addidional input data needed for short-term model
    rho_cp_grout = 3800000.0  
    rho_cp_pipe = 1540000.0 

    # start test with dynamic Rb*
    # initiate borefield
    borefield = Borefield()

    # set ground data in borefield
    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.create_rectangular_borefield(1, 1, 6, 6, 110, 4, 0.075)

    borefield.load = load

    delta_t = max(load.max_peak_cooling, load.max_peak_cooling) * 1000 / (fluid_data.Cp * fluid_data.mfr)

    # set temperature bounds
    borefield.set_max_avg_fluid_temperature(35 + delta_t / 2)
    borefield.set_min_avg_fluid_temperature(0 - delta_t / 2)

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

    # start test with constant Rb*
    # initiate borefield
    borefield = Borefield()

    # set ground data in borefield
    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.create_rectangular_borefield(1, 1, 6, 6, 110, 4, 0.075)
    Rb_static = 0.13
    borefield.set_Rb(Rb_static)

    # set temperature bounds
    borefield.set_max_avg_fluid_temperature(35 + delta_t / 2)
    borefield.set_min_avg_fluid_temperature(0 - delta_t / 2)

    # load the hourly profile
    borefield.load = load
    borefield.load.peak_duration = 1

    # Sizing with constant Rb
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

    # set ground data in borefield
    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.create_rectangular_borefield(1, 1, 6, 6, 110, 4, 0.075)
    Rb_static = 0.13
    borefield.set_Rb(Rb_static)
    # Addidional input data needed for short-term model
    rho_cp_grout = 3800000.0  
    rho_cp_pipe = 1540000.0 

    # set temperature bounds
    borefield.set_max_avg_fluid_temperature(35 + delta_t / 2)
    borefield.set_min_avg_fluid_temperature(0 - delta_t / 2)

    # load the hourly profile
    borefield.load = load

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
    L4s_ste_start = time.time()
    depth_L4s_ste = borefield.size(100, L4_sizing=True)
    L4s_ste_stop = time.time()

    print(
        f"The sizing according to L2 has a depth of {depth_L2:.2f}m (using dynamic Rb* of {Rb_L2:.3f}) and {depth_L2s:.2f}m (using constant Rb*)")
    print(
        f"The sizing according to L3 has a depth of {depth_L3:.2f}m (using dynamic Rb* of {Rb_L3:.3f}) and {depth_L3s:.2f}m (using constant Rb*)")
    print(
        f"The sizing according to L4 has a depth of {depth_L4:.2f}m (using dynamic Rb* of {Rb_L4:.3f}) and {depth_L4s:.2f}m (using constant Rb*)")
    print(
        f"The sizing according to L4 (including short-term effects) has a depth of {depth_L4_ste:.2f}m (using dynamic Rb* of {Rb_L4_ste:.3f}) and {depth_L4s_ste:.2f}m (using constant Rb*)")
    print(
        f"Time needed for L4-sizing is {L4_stop-L4_start:.2f}s (using dynamic Rb*) or {L4s_stop-L4s_start:.2f}s (using constant Rb*)")
    print(
        f"Time needed for L4-sizing including short-term effect is {L4_ste_stop-L4_ste_start:.2f}s (using dynamic Rb*) or {L4s_ste_stop-L4s_ste_start:.2f}s (using constant Rb*)")
    
    assert np.isclose(depth_L2, 46.44356767605206)
    assert np.isclose(depth_L3, 46.73933500137179)
    assert np.isclose(depth_L4, 56.2659729399716)
    assert np.isclose(depth_L4_ste, 52.34712690022354)
    assert np.isclose(depth_L2s, 46.986986159967906)
    assert np.isclose(depth_L3s, 47.28116830541002)
    assert np.isclose(depth_L4s, 56.73136082379056)
    assert np.isclose(depth_L4s_ste, 52.72442116662979)
    assert np.isclose(Rb_L2, 0.12769092836836982)
    assert np.isclose(Rb_L3, 0.12769755355584275)
    assert np.isclose(Rb_L4, 0.12793335445966403)
    assert np.isclose(Rb_L4_ste, 0.12783109689745237)


if __name__ == "__main__":  # pragma: no cover
    test_1a_6h_ste()
    test_1a_1h_ste()
