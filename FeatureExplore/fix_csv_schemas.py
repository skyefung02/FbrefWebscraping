"""
Quick fix script to drop deprecated columns from 29 defender CSV files.

This script reads CSV files with 135 columns and removes the 23 deprecated
FPL columns to create files with the correct 112-column schema.

Author: Claude Code
Date: 2025-11-26
"""

import pandas as pd
import os

# Files with 135 columns that need fixing
FILES_TO_FIX = [
    'adragovic_finaldat.csv', 'bennett_finaldat.csv', 'britos_finaldat.csv',
    'clowe_finaldat.csv', 'dsimpson_finaldat.csv', 'durm_finaldat.csv',
    'gcameron_finaldat.csv', 'hadergjonaj_finaldat.csv', 'jcollins_finaldat.csv',
    'jgstankovic_finaldat.csv', 'kompany_finaldat.csv', 'lichtsteiner_finaldat.csv',
    'manga_finaldat.csv', 'martinsindi_finaldat.csv', 'mbauer_finaldat.csv',
    'molsson_finaldat.csv', 'moreno_finaldat.csv', 'morrison_finaldat.csv',
    'naughton_finaldat.csv', 'nyom_finaldat.csv', 'saltor_finaldat.csv',
    'sbamba_finaldat.csv', 'schindler_finaldat.csv', 'shawcross_finaldat.csv',
    'sward_finaldat.csv', 'tsmith_finaldat.csv', 'valencia_finaldat.csv',
    'vanderhoorn_finaldat.csv', 'wimmer_finaldat.csv'
]

# Deprecated columns to drop
DEPRECATED_COLUMNS = [
    'attempted_passes', 'big_chances_created', 'big_chances_missed',
    'clearances_blocks_interceptions', 'completed_passes', 'dribbles',
    'ea_index', 'errors_leading_to_goal', 'errors_leading_to_goal_attempt',
    'fouls', 'id', 'key_passes', 'kickoff_time_formatted', 'loaned_in',
    'loaned_out', 'offside', 'open_play_crosses', 'penalties_conceded',
    'recoveries', 'tackled', 'tackles', 'target_missed', 'winning_goals'
]

def main():
    """Fix CSV schemas by dropping deprecated columns."""
    defender_path = 'Player_Data/Defenders'

    print("=" * 70)
    print("CSV SCHEMA FIX SCRIPT")
    print("=" * 70)
    print(f"Fixing {len(FILES_TO_FIX)} CSV files")
    print(f"Removing {len(DEPRECATED_COLUMNS)} deprecated columns")
    print("=" * 70)
    print()

    successful = []
    failed = []

    for idx, filename in enumerate(FILES_TO_FIX, 1):
        filepath = os.path.join(defender_path, filename)
        print(f"[{idx}/{len(FILES_TO_FIX)}] Processing: {filename}")

        try:
            # Read the CSV
            df = pd.read_csv(filepath)
            original_cols = len(df.columns)
            print(f"  Original columns: {original_cols}")

            if original_cols == 112:
                print(f"  Status: Already correct!")
                successful.append(filename)
                continue

            # Drop deprecated columns
            cols_to_drop = [col for col in DEPRECATED_COLUMNS if col in df.columns]
            df = df.drop(columns=cols_to_drop, errors='ignore')

            new_cols = len(df.columns)
            print(f"  Dropped {len(cols_to_drop)} columns")
            print(f"  New columns: {new_cols}")

            # Save back
            df.to_csv(filepath, index=False)

            if new_cols == 112:
                print(f"  Status: OK")
                successful.append(filename)
            else:
                print(f"  Status: WARNING - Expected 112, got {new_cols}")
                failed.append(f"{filename} ({new_cols} cols)")

        except Exception as e:
            print(f"  Status: FAILED - {str(e)}")
            failed.append(f"{filename} ({str(e)[:50]})")

    # Print summary
    print("\n" + "=" * 70)
    print("FIX COMPLETE")
    print("=" * 70)
    print(f"Successful: {len(successful)}/{len(FILES_TO_FIX)}")
    print(f"Failed: {len(failed)}/{len(FILES_TO_FIX)}")

    if failed:
        print("\nFailed files:")
        for f in failed:
            print(f"  - {f}")

    print("\nNext steps:")
    print("  1. Run: python compile_defender_data.py")
    print("  2. Test: pd.read_csv('def_finaldat.csv')")
    print("=" * 70)

if __name__ == "__main__":
    main()
