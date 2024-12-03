import pandas as pd

# Load the CSV file
input_file = r'GHEtool\Validation\short_term_effects_validation\Three_buildings\Auditorium\auditorium.csv'  # Replace with your file path
output_file = 'auditorium_switched.csv'

# Read the CSV file
df = pd.read_csv(input_file, sep=';')

# Ensure there are exactly two columns
if len(df.columns) == 2:
    # Swap the columns
    df = df[df.columns[::-1]]
    
    # Save the modified CSV
    df.to_csv(output_file, index=False)
    print(f"Columns switched successfully! Saved as '{output_file}'.")
else:
    print("Error: The CSV file does not have exactly two columns.")
