"""
The work of (Ahmadfard and Bernier, 2019) provides a set of test cases that can be used to compare
software tools with the ultimate goal of improving the reliability of design methods for sizing
vertical ground heat exchangers. This document delivers the results on the test file using the GHEtool
L2-, L3- and L4-sizing methods.

Test 4 – High annual ground load imbalance

References:
-----------
    - Ahmadfard, M., and M. Bernier. 2019. A review of vertical ground heat exchanger sizing tools including an inter-model
comparison [in eng]. Renewable sustainable energy reviews (OXFORD) 110:247–265.
"""
import os
import time

import matplotlib.pyplot as plt

import numpy as np
import pygfunction as gt

import sys
sys.path.append("C:\Workdir\Develop\ghetool")

from GHEtool import *


def test_4_ste():
    # initiate ground, fluid and pipe data
    ground_data = GroundFluxTemperature(k_s=1.9, T_g=15, volumetric_heat_capacity=2052000, flux=0)
    base_mfr = 0.074 * 139.731 / 25 # Basis massastroom (kg/s)
    
    # Maak een water vloeistofobject via pygfunction
    fluid_str = 'Water'  # 'Water' is de standaard vloeistof in pygfunction
    percent = 0  # Geen mengsel, dus 0% andere vloeistoffen
    T_f = 0  # Temperatuur (bijvoorbeeld 20°C)
    fluid_object = gt.media.Fluid(fluid_str, percent, T=T_f)  # Maak fluid object
    
    # Maak FluidData object aan en laad vloeistofgegevens van pygfunction
    fluid_data = FluidData(mfr=base_mfr, rho=1026, Cp=4019, mu=0.003377, k_f=0.468)
    fluid_data.import_fluid_from_pygfunction(fluid_object)  # Laad de vloeistofgegevens in FluidData
    pipe_data = MultipleUTube(r_in=0.013, r_out=0.0167, D_s=0.083 / 2, k_g=0.69, k_p=0.4)

    # start test with dynamic Rb*
    # initiate borefield
    borefield = Borefield()

    # set ground data in borefield
    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.create_rectangular_borefield(5, 5, 8, 8, 110, 4, 0.075)

    # load the hourly profile
    load = HourlyGeothermalLoad(simulation_period=20)
    load.load_hourly_profile(os.path.join(os.path.dirname(__file__), 'test4.csv'), header=True, separator=",",
                             col_extraction=1, col_injection=0)
    borefield.load = load

    # convert inlet fluid temperature to heap pump constraints to constraints on average fluid temperature
    delta_t = max(load.max_peak_extraction, load.max_peak_injection) * 1000 / (fluid_data.Cp * fluid_data.mfr) / 25

    # set temperature bounds
    borefield.set_max_avg_fluid_temperature(38 + delta_t / 2)
    borefield.set_min_avg_fluid_temperature(0 - delta_t / 2)

    # Sizing with dynamic Rb
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
    borefield._plot_temperature_profile(plot_hourly=True)
    Rb_L4 = borefield.Rb
    L4_stop = time.time()

    # initiate borefield
    borefield = Borefield()

    # set ground data in borefield
    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.create_rectangular_borefield(5, 5, 8, 8, 110, 4, 0.075)

    borefield.load = load

    # set temperature bounds
    borefield.set_max_avg_fluid_temperature(38 + delta_t / 2)
    borefield.set_min_avg_fluid_temperature(0 - delta_t / 2)

    # Addidional input data needed for short-term model
    rho_cp_grout = 3800000.0  
    rho_cp_pipe = 1540000.0 

    # Sample dictionary with short-term effect parameters
    short_term_effects_parameters = {
    'rho_cp_grout': rho_cp_grout,
    'rho_cp_pipe': rho_cp_pipe,
    }

    options = {
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

    # according to L4
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
    borefield.create_rectangular_borefield(5, 5, 8, 8, 110, 4, 0.075)
    Rb_static = 0.2
    borefield.set_Rb(Rb_static)

    # set temperature bounds
    borefield.set_max_avg_fluid_temperature(38 + delta_t / 2)
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

    # initiate borefield
    borefield = Borefield()

    # set ground data in borefield
    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.create_rectangular_borefield(5, 5, 8, 8, 110, 4, 0.075)
    Rb_static = 0.2
    borefield.set_Rb(Rb_static)

    # set temperature bounds
    borefield.set_max_avg_fluid_temperature(38 + delta_t / 2)
    borefield.set_min_avg_fluid_temperature(0 - delta_t / 2)

    # load the hourly profile
    borefield.load = load

    # Addidional input data needed for short-term model
    rho_cp_grout = 3800000.0  
    rho_cp_pipe = 1540000.0 

    # Sample dictionary with short-term effect parameters
    short_term_effects_parameters = {
    'rho_cp_grout': rho_cp_grout,
    'rho_cp_pipe': rho_cp_pipe,
    }

    options = {
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

    # according to L4
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
        f"The sizing according to L4 (inclusing short-term effects) has a depth of {depth_L4_ste}m (using dynamic Rb* of {Rb_L4_ste}) and {depth_L4s_ste}m (using constant Rb*)")
    print(
        f"Time needed for L4-sizing is {L4_stop-L4_start:.2f}s (using dynamic Rb*) or {L4s_stop-L4s_start:.2f}s (using constant Rb*)")
    print(
        f"Time needed for L4-sizing including short-term effect is {L4_ste_stop-L4_ste_start:.2f}s (using dynamic Rb*) or {L4s_ste_stop-L4s_ste_start:.2f}s (using constant Rb*)")
    
    plt.show()

    assert np.isclose(depth_L2, 124.02695636769329)
    assert np.isclose(depth_L3, 124.67134582762849)
    assert np.isclose(depth_L4, 122.461471483961)
    assert np.isclose(depth_L4_ste, 116.61823578676353)
    assert np.isclose(depth_L2s, 121.50772080500283)
    assert np.isclose(depth_L3s, 122.15337731354852)
    assert np.isclose(depth_L4s, 119.99581098989934)
    assert np.isclose(depth_L4s_ste, 114.67191666829271)
    assert np.isclose(Rb_L2, 0.21023380751472076)
    assert np.isclose(Rb_L3, 0.21025731326271593)
    assert np.isclose(Rb_L4, 0.2101772055278848)
    assert np.isclose(Rb_L4_ste, 0.20997223493386377)


if __name__ == "__main__":  # pragma: no cover
    test_4_ste()