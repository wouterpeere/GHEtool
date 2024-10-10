import pandas as pd

# Load your CSV file (adjust the file path as necessary)
input_file = 'C:\Workdir\Develop\ghetool\GHEtool\Validation\short_term_effects_validation\Sandbox\Tb_modelica.csv'
df = pd.read_csv(input_file)

# Print column names to check for issues
print(df.columns)

# Calculate the average temperature between TBorFieIn and TBorFieOut
df['Tb'] = df['TBorAve']

# Resample the data by keeping only rows where 'Time' is a multiple of 3600 seconds
df_resampled = df[df['Time'] % 3600 == 0][['Tb']]

# If there are fewer than 8760 rows, pad the DataFrame with zeros
required_rows = 8760
num_rows_to_add = required_rows - len(df_resampled)

if num_rows_to_add > 0:
    padding = pd.DataFrame({'Tb': [0.0] * num_rows_to_add})
    df_resampled = pd.concat([df_resampled, padding], ignore_index=True)

# Save the output to a new CSV file
output_file = 'modelica_sim_houly_Tb.csv'
df_resampled.to_csv(output_file, index=False)

print(f"Output CSV saved as {output_file}")