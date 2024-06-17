"""
The work of (Ahmadfard and Bernier, 2019) provides a set of test cases that can be used to compare
software tools with the ultimate goal of improving the reliability of design methods for sizing
vertical ground heat exchangers. This document delivers the results on the test file using the GHEtool
L2-, L3- and L4-sizing methods.

Test 2 – Shonder's test – 120 boreholes

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


def test_2_6h_ste():
    # initiate ground, fluid and pipe data
    ground_data = GroundFluxTemperature(k_s=2.25, T_g=12.41, volumetric_heat_capacity=2877000, flux=0)
    fluid_data = FluidData(mfr=0.2416667, rho=1026, Cp=4019, mu=0.003377, k_f=0.468)
    pipe_data = MultipleUTube(r_in=0.0137, r_out=0.0167, D_s=0.0471 / 2, k_g=1.73, k_p=0.45)

    # start test with dynamic Rb*
    # initiate borefield
    borefield = Borefield()

    # set ground data in borefield
    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.create_rectangular_borefield(12, 10, 6, 6, 110, 3, 0.054)

    # load the hourly profile
    load = HourlyGeothermalLoad(simulation_period=10)
    load.load_hourly_profile(os.path.join(os.path.dirname(__file__), 'test2.csv'), header=True, separator=",",
                             col_heating=1, col_cooling=0)
    borefield.load = load

    delta_t = max(load.max_peak_cooling, load.max_peak_cooling) * 1000 / (fluid_data.Cp * fluid_data.mfr) / 120

    # set temperature bounds
    borefield.set_max_avg_fluid_temperature(35 + delta_t / 2)
    borefield.set_min_avg_fluid_temperature(4.4 - delta_t / 2)

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
    ground_data = GroundFluxTemperature(k_s=2.25, T_g=12.41, volumetric_heat_capacity=2877000, flux=0)
    fluid_data = FluidData(mfr=0.2416667, rho=1026, Cp=4019, mu=0.003377, k_f=0.468)
    pipe_data = MultipleUTube(r_in=0.0137, r_out=0.0167, D_s=0.0471 / 2, k_g=1.73, k_p=0.45)
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
    borefield.create_rectangular_borefield(12, 10, 6, 6, 110, 3, 0.054)

    borefield.load = load

    # set temperature bounds
    borefield.set_max_avg_fluid_temperature(35 + delta_t / 2)
    borefield.set_min_avg_fluid_temperature(4.4 - delta_t / 2)

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

    # according to L4 inclusing short-term effects
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
    borefield.create_rectangular_borefield(12, 10, 6, 6, 110, 3, 0.054)
    Rb_static = 0.113
    borefield.set_Rb(Rb_static)

    # set temperature bounds
    borefield.set_max_avg_fluid_temperature(35 + delta_t / 2)
    borefield.set_min_avg_fluid_temperature(4.4 - delta_t / 2)

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

    # initiate borefield
    borefield = Borefield()

    # set ground data in borefield
    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.create_rectangular_borefield(12, 10, 6, 6, 110, 3, 0.054)
    Rb_static = 0.113
    borefield.set_Rb(Rb_static)

    # set temperature bounds
    borefield.set_max_avg_fluid_temperature(35 + delta_t / 2)
    borefield.set_min_avg_fluid_temperature(4.4 - delta_t / 2)

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
    Rb_L4s_ste = borefield.Rb
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
    
    assert np.isclose(depth_L2, 76.84063723898525)
    assert np.isclose(depth_L3, 79.11228401910488)
    assert np.isclose(depth_L4, 84.77559168467357)
    assert np.isclose(depth_L4_ste, 83.98494516311503)
    assert np.isclose(depth_L2s, 77.43318625702659)
    assert np.isclose(depth_L3s, 79.59733272530252)
    assert np.isclose(depth_L4s, 84.97661469091508)
    assert np.isclose(depth_L4s_ste, 84.19862780632221)
    assert np.isclose(Rb_L2, 0.11113022659380956)
    assert np.isclose(Rb_L3, 0.11146734480480838)
    assert np.isclose(Rb_L4, 0.11234852494964061)
    assert np.isclose(Rb_L4_ste, 0.11222202747473603)


if __name__ == "__main__":  # pragma: no cover
    test_2_6h_ste()
