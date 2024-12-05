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
import pygfunction as gt
import sys

sys.path.append(r"C:\Workdir\Develop\ghetool")  # Adjust the path to your GHEtool directory
from GHEtool import *


def initialize_borefield(load, delta_t, ground_data, fluid_data, pipe_data):
    """
    Initialize and set up borefield with necessary parameters.
    """
    # Initiate borefield
    borefield = Borefield()

    # Set ground data in borefield
    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.create_rectangular_borefield(1, 1, 6, 6, 110, 4, 0.075)

    # Load the load profile into borefield
    borefield.load = load

    # Set temperature bounds
    borefield.set_max_avg_fluid_temperature(35 + delta_t / 2)
    borefield.set_min_avg_fluid_temperature(0 - delta_t / 2)

    return borefield


def run_sizing_case(borefield, load, ground_data, fluid_data, pipe_data, peak_duration, delta_t, imposed_Rb=None):
    """
    Run sizing for L2, L3, L4, L3_ste, and L4_ste methods with imposed Rb and return results.
    If imposed_Rb is None, it uses the default calculated Rb.
    """
    # Set peak duration
    borefield.load.peak_duration = peak_duration

    # Define methods and short-term effects parameters
    methods = ['L2', 'L3', 'L4', 'L3_ste', 'L4_ste']
    short_term_params = {'rho_cp_grout': 3800000.0, 'rho_cp_pipe': 1540000.0}
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
        'short_term_effects_parameters': short_term_params,
    }

    # Set results dictionary
    results = {}

    # Set imposed Rb if provided
    if imposed_Rb is not None:
        borefield.set_Rb(imposed_Rb)

    for method in methods:
        start_time = time.time()

        # Re-initialize borefield if switching from L4 to L3_ste or L4_ste
        if method in ['L3_ste', 'L4_ste']:
            print(f"\nRe-initializing borefield for {method} method.")
            borefield = initialize_borefield(load, delta_t, ground_data, fluid_data, pipe_data)
            borefield.set_options_gfunction_calculation(options)
            # Perform sizing with short-term effects
            depth = borefield.size(100, L3_sizing=(method == 'L3_ste'), L4_sizing=(method == 'L4_ste'))
        else:
            # Perform sizing for regular methods (L2, L3, L4)
            borefield = initialize_borefield(load, delta_t, ground_data, fluid_data, pipe_data)
            depth = borefield.size(100, L2_sizing=(method == 'L2'), L3_sizing=(method == 'L3'), L4_sizing=(method == 'L4'))

        results[method] = {
            'depth': depth,
            'Rb': borefield.Rb,
            'time': time.time() - start_time
        }

    return results


def test1a_ste():
    """
    Test the L2, L3, L4, L3_ste, and L4_ste sizing methods of the GHEtool library on a synthetic balanced load profile.
    """
    """
    # Set up ground, fluid, and pipe data
    ground_data = GroundFluxTemperature(k_s=1.8, T_g=17.5, volumetric_heat_capacity=2073600, flux=0)
    fluid_data = FluidData(mfr=0.440, rho=1052, Cp=3795, mu=0.0052, k_f=0.48)
    pipe_data = MultipleUTube(r_in=0.0137, r_out=0.0167, D_s=0.075 / 2, k_g=1.4, k_p=0.43, number_of_pipes=1)
    """
    # Initialize ground, fluid, and pipe data
    ground_data = GroundFluxTemperature(k_s=1.8, T_g=17.5, volumetric_heat_capacity=2073600, flux=0)

    # Base mass flow rate (kg/s)
    base_mfr = 0.5585

    # Create a water fluid object using pygfunction
    fluid_str = 'Water'  # Default fluid in pygfunction
    percent = 0          # No mixture, pure water
    T_f = 35              # Temperature (e.g., 0°C)
    fluid_object = gt.media.Fluid(fluid_str, percent, T=T_f)  # Create fluid object

    # Create FluidData object and load fluid properties from pygfunction
    fluid_data = FluidData(mfr=base_mfr, rho=1052, Cp=3795, mu=0.0052, k_f=0.48)
    fluid_data.import_fluid_from_pygfunction(fluid_object)  # Import fluid data

    # Create pipe data for a Multiple U-Tube configuration
    pipe_data = MultipleUTube(r_in=0.0137, r_out=0.0167, D_s=0.075 / 2, k_g=1.4, k_p=0.43, number_of_pipes=1)


    # Load hourly profile
    load = HourlyGeothermalLoad(simulation_period=10)
    csv_file_path = os.path.join(os.path.dirname(__file__), 'test1b.csv')
    load.load_hourly_profile(csv_file_path, header=True, separator=";", decimal_seperator=",", col_extraction=1, col_injection=0)

    # Calculate delta temperature
    delta_t = max(load.max_peak_extraction, load.max_peak_injection) * 1000 / (fluid_data.Cp * fluid_data.mfr)

    # Test cases: for peak durations 6 hours and 1 hour
    for peak_duration in [6]:
        print(f"\nRunning test case for peak_duration = {peak_duration}")

        # Initialize borefield with required parameters
        borefield = initialize_borefield(load, delta_t, ground_data, fluid_data, pipe_data)

        # Run sizing for calculated Rb (default behavior)
        results_default_Rb = run_sizing_case(borefield, load, ground_data, fluid_data, pipe_data, peak_duration, delta_t)

        # Print results for default Rb
        print("\n--- Results for calculated Rb ---")
        for method, result in results_default_Rb.items():
            print(f"Method: {method}")
            print(f"  Depth: {result['depth']:.2f} m")
            print(f"  Rb: {result['Rb']:.3f}")
            print(f"  Time: {result['time']:.2f} s")
        print("\n----------------------------------")

        # Run sizing for imposed Rb (static value)
        Rb_static = 0.13  # Imposed Rb value
        # Initialize borefield with required parameters
        borefield = initialize_borefield(load, delta_t, ground_data, fluid_data, pipe_data)
        borefield.set_Rb(Rb_static)
        results_imposed_Rb = run_sizing_case(borefield, load, ground_data, fluid_data, pipe_data, peak_duration, delta_t, imposed_Rb=Rb_static)

        # Print results for imposed Rb
        print("\n--- Results for imposed Rb (Rb* = 0.13) ---")
        for method, result in results_imposed_Rb.items():
            print(f"Method: {method}")
            print(f"  Depth: {result['depth']:.2f} m")
            print(f"  Rb: {result['Rb']:.3f}")
            print(f"  Time: {result['time']:.2f} s")
        print("\n--------------------------------------------")

        """
        # Add assertions for validation (replace with expected values for your case)
        if peak_duration == 6:
            assert np.isclose(results_default_Rb['L2']['depth'], 59.366, atol=0.1)
            assert np.isclose(results_default_Rb['L3']['depth'], 59.543, atol=0.1)
            assert np.isclose(results_default_Rb['L4']['depth'], 56.266, atol=0.1)
            assert np.isclose(results_default_Rb['L4_ste']['depth'], 52.347, atol=0.1)
            assert np.isclose(results_default_Rb['L3_ste']['depth'], 58.123, atol=0.1)  # Example value
        else:
            # Adjust expected values based on 1-hour peak duration results
            pass
        """

if __name__ == "__main__":
    test1a_ste()
