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
from GHEtool import *

def test_1b_6h_ste():
    # Ground properties
    ground_data = GroundFluxTemperature(k_s=1.8, T_g=17.5, volumetric_heat_capacity=2073600, flux=0)

    # Load fluid properties into FluidData
    base_mfr = 0.5585  # Baseline mass flow rate (kg/s)
    fluid_data = FluidData(mfr=base_mfr, rho=1052, Cp=3795, mu=0.0052, k_f=0.48)
 
    # Pipe properties
    pipe_data = MultipleUTube(r_in=0.0137, r_out=0.0167, D_s=0.075 / 2, k_g=1.4, k_p=0.43, number_of_pipes=1)

    # Short-term effect parameters
    rho_cp_grout = 3800000.0  
    rho_cp_pipe = 1540000.0  

    # Initialize results dictionary
    results = {}

    # Define function to store results
    def log_results(method, depth, borefield, start_time):
        results[method] = {
            'depth': depth,
            'Rb': borefield.Rb,
            'time': time.time() - start_time
        }

    # Load hourly profile
    load = HourlyGeothermalLoad(simulation_period=10)
    load.load_hourly_profile(os.path.join(os.path.dirname(__file__), 'test1b.csv'), header=True, separator=";",
                             decimal_seperator=",", col_extraction=1, col_injection=0)

    # Calculate temperature bounds
    delta_t = max(load.max_peak_extraction, load.max_peak_injection) * 1000 / (fluid_data.Cp * fluid_data.mfr) 

    # Test each sizing method
    for method, dynamic_rb, short_term_effects in [
        ('L2', True, False), ('L3', True, False), ('L4', True, False), ('L3_ste', True, True),
        ('L4_ste', True, True), ('L2_static', False, False), ('L3_static', False, False),
        ('L4_static', False, False), ('L3_static_ste', False, True), ('L4_static_ste', False, True)
    ]:
        # Initialize borefield
        borefield = Borefield()
        borefield.set_ground_parameters(ground_data)
        borefield.set_fluid_parameters(fluid_data)
        borefield.set_pipe_parameters(pipe_data)
        borefield.create_rectangular_borefield(1, 1, 6, 6, 110, 4, 0.075)

        # Set temperature bounds
        borefield.set_max_avg_fluid_temperature(35 + delta_t / 2)
        borefield.set_min_avg_fluid_temperature(0 - delta_t / 2)

        borefield.load = load

        # Handle short-term effects
        if short_term_effects:
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

        # Use constant Rb if required
        if not dynamic_rb:
            borefield.set_Rb(0.13)

        # Perform sizing
        start_time = time.time()
        depth = borefield.size(100, L2_sizing=(method.startswith('L2')), L3_sizing=(method.startswith('L3')), L4_sizing=(method.startswith('L4')))
        log_results(method, depth, borefield, start_time)

    # Print results
    for method, result in results.items():
        print(f"Method {method}: Depth = {result['depth']:.2f}m, Rb* = {result['Rb']:.3f}, Time = {result['time']:.2f}s")

if __name__ == "__main__":
    test_1b_6h_ste()
