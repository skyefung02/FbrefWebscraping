# Data Compilation Notes

## Issue Fixed: def_finaldat.csv

### Problem
The original `def_finaldat.csv` file was a duplicate of `att_finaldat.csv` (identical MD5 checksum). Both files contained 39,673 rows of attacker/midfielder data.

### Solution
Rebuilt `def_finaldat.csv` by compiling all 345 individual defender CSV files from the `Player_Data/Defenders/` directory.

### Results
- **Old def_finaldat.csv**: 39,674 lines (duplicate of attackers)
- **New def_finaldat.csv**: 23,212 lines (actual defender data)
- **Unique players**: 345 defenders
- **Primary positions**: CB (11,026 rows), RB (4,070 rows), LB (3,989 rows), WB (1,070 rows)

### Files Updated
1. **`def_finaldat.csv`** - Rebuilt with actual defender data
2. **`GeneralScrape.ipynb`** - Added compilation code at the end (cells 975-977)
3. **`compile_defender_data.py`** - New standalone script for future re-compilation

## Current Dataset Summary

### Compiled Datasets
- **`att_finaldat.csv`**: 39,673 rows - Attackers and Midfielders
- **`def_finaldat.csv`**: 23,211 rows - Defenders
- **`team_finaldat.csv`**: 5,320 rows - Team match data (7 seasons × 380 matches × 2 teams)

### Individual Player Files
- **Attackers/Midfielders**: 527 files in `Player_Data/`
- **Defenders**: 345 files in `Player_Data/Defenders/`
- **Total**: 872 individual player files

### Data Coverage
- **Seasons**: 2017-2018 through 2023-2024 (7 seasons)
- **Matches per season**: 380 Premier League matches
- **Data sources**: FBref (match stats) + Fantasy Premier League (FPL data)

## How to Re-compile Defender Data

### Option 1: Run the Python script
```bash
python compile_defender_data.py
```

### Option 2: Run the notebook cells
Open `GeneralScrape.ipynb` and run the last 3 cells (975-977)

### Option 3: Use bash (quickest)
```bash
cd /home/user/FbrefWebscraping
first_file=$(ls Player_Data/Defenders/*.csv | head -1)
head -1 "$first_file" > def_finaldat.csv
for file in Player_Data/Defenders/*.csv; do
    tail -n +2 "$file" >> def_finaldat.csv
done
```

## Notes
- All individual player files contain the same column structure
- Both attacker and defender files include comprehensive stats: basic performance, advanced metrics (xG, SCA, GCA), passing, defensive stats, and FPL data
- The `Player ID` column can be used to identify unique players across datasets
