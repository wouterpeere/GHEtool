import pandas as pd
import numpy as np

# Step 1: Load the input file and check for multiples of 3600 seconds
file_path = 'C:\Workdir\Develop\ghetool\GHEtool\Validation\short_term_effects_validation\Sandbox\Beier_Smith_Spitler_2011_SandBox.txt'  # Replace with your actual file path
data = pd.read_csv(file_path, sep='\s+', header=None, on_bad_lines='skip')

# Assign proper column names
data.columns = ['Time', 'Inlet_Temperature', 'Outlet_Temperature', 'Heat_Load']

# Create a new DataFrame with time in multiples of 3600 seconds (hourly data)
desired_times = np.arange(0, data['Time'].max(), 3600)  # Generate all multiples of 3600s up to the max time
new_data = pd.DataFrame({'Time': desired_times})

# Merge with the original data and interpolate missing values
merged_data = pd.merge(new_data, data, on='Time', how='left')
merged_data.interpolate(method='linear', inplace=True)  # Interpolate missing rows

# Step 2: Resample the data to hourly intervals and convert time to hours
hourly_data = merged_data.copy()
hourly_data['Time'] = hourly_data['Time'] / 3600  # Convert seconds to hours

# Make sure there are at least 51 rows
if len(hourly_data) < 51:
    print("Warning: Hourly data has fewer than 51 rows.")

# Save hourly resampled data as a CSV file
hourly_data.to_csv('Hourly_data.csv', index=False, header=True)

# Step 3: Create the CSV files with 8760 rows

# 3a. First CSV: Tf (average of Inlet and Outlet temperatures)
hourly_data['Tf'] = (hourly_data['Inlet_Temperature'] + hourly_data['Outlet_Temperature']) / 2
tf_values = hourly_data[['Tf']]

# Fill with 0.0 until we have 8760 rows
while len(tf_values) < 8760:
    missing_rows = pd.DataFrame({'Tf': [0.0] * (8760 - len(tf_values))})
    tf_values = pd.concat([tf_values, missing_rows], ignore_index=True)

# Save Tf CSV without headers and index
tf_values.to_csv('Tf_values.csv', index=False, header=False)

# 3b. Second CSV: Cooling and Heating
# Cooling is the injected heat in kW, Heating is set to 0
hourly_data['Injected_Heat_kW'] = (hourly_data['Heat_Load'] * 1056) / 1000
cooling_heating_df = pd.DataFrame({
    'Cooling': hourly_data['Injected_Heat_kW'],
    'Heating': [0.0] * len(hourly_data)
})

# Fill Cooling and Heating with 0.0 until we have 8760 rows
while len(cooling_heating_df) < 8760:
    missing_rows = pd.DataFrame({'Cooling': [0.0] * (8760 - len(cooling_heating_df)), 'Heating': [0.0] * (8760 - len(cooling_heating_df))})
    cooling_heating_df = pd.concat([cooling_heating_df, missing_rows], ignore_index=True)

# Save Cooling and Heating CSV without headers and index
cooling_heating_df.to_csv('Cooling_Heating_values.csv', sep=';', index=False, header=False)

print("CSV files created successfully with 8760 rows and hourly values output!")
