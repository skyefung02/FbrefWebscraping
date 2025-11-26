"""
Script to compile all individual defender CSV files into def_finaldat.csv

This script reads all defender files from Player_Data/Defenders/ and
concatenates them into a single def_finaldat.csv file.
"""

import pandas as pd
import os

def compile_defender_data():
    """Compile all defender CSV files into a single dataframe"""

    # Path to defender files
    defender_path = 'Player_Data/Defenders'

    # List to store all dataframes
    defender_dataframes = []

    print("Reading defender files...")

    # Read all CSV files from Defenders folder
    if os.path.exists(defender_path):
        for file in sorted(os.listdir(defender_path)):
            if file.endswith('.csv'):
                file_path = os.path.join(defender_path, file)
                df = pd.read_csv(file_path)
                defender_dataframes.append(df)

        print(f"Found {len(defender_dataframes)} defender files")

        # Concatenate all dataframes
        final_df = pd.concat(defender_dataframes, ignore_index=True)

        # Save to CSV
        output_path = 'def_finaldat.csv'
        final_df.to_csv(output_path, index=False)

        print(f"\n✓ Successfully compiled defender data!")
        print(f"  Total defenders: {len(defender_dataframes)}")
        print(f"  Total rows: {len(final_df):,}")
        print(f"  Columns: {len(final_df.columns)}")
        print(f"  Output: {output_path}")

        # Display summary
        print(f"\nDataset summary:")
        print(f"  Date range: {final_df['Date'].min()} to {final_df['Date'].max()}")
        print(f"  Unique players: {final_df['Player ID'].nunique() if 'Player ID' in final_df.columns else 'N/A'}")

        return final_df

    else:
        print(f"Error: Path {defender_path} does not exist")
        return None

if __name__ == "__main__":
    df = compile_defender_data()
