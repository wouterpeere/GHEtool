import pandas as pd

# Load the CSV file
input_file = r'GHEtool\Validation\short_term_effects_validation\Three_buildings\Swimming pool\swimming_pool.csv'  # Replace with your file path
output_file = 'swimmingpool_switched.csv'

df = pd.read_csv(input_file, sep=';')

# Ensure there are at least two columns
if len(df.columns) >= 2:
    # Swap the first two columns while keeping others the same
    cols = df.columns.tolist()
    cols[0], cols[1] = cols[1], cols[0]  # Swap the first two columns
    df = df[cols]
    
    # Save the modified CSV with semicolon delimiter
    df.to_csv(output_file, sep=';', index=False)
    print(f"Columns switched successfully! Saved as '{output_file}'.")
else:
    print("Error: The CSV file does not have at least two columns.")
