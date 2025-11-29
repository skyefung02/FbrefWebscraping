# Fixture Difficulty Rating (FDR) Implementation

## Overview

The FDR feature has been successfully integrated into the player performance dataset. The implementation provides complete FDR coverage (100%) across all seasons from 2017-18 to 2023-24.

## How to Use

### Quick Start

Open [FormFixtures.ipynb](FormFixtures.ipynb) and run all cells to:
1. Load player and team data
2. Merge datasets
3. Add FDR column
4. Get `merged_df` with 149 columns × 62,884 observations

The final `merged_df` DataFrame will be ready for analysis with complete FDR coverage.

### Data Sources

- **2017-18**: Predicted FDR using calibrated ordinal regression model (LogisticIT)
- **2018-19 onwards**: Observed FDR from Fantasy Premier League official data

## Model Information

The FDR prediction model was trained in [FDR_Imputation_Model.ipynb](FDR_Imputation_Model.ipynb):

- **Model Type**: LogisticIT (ordinal regression)
- **Approach**: Home/Away split with 6-game rolling metrics
- **Performance**: 60.2% exact accuracy, 95.4% within-1 accuracy
- **Features**: Opponent's rolling xG, xGA, goals scored/conceded, points, possession (context-aware by venue)

### Model Files

- `fdr_model.pkl` - Trained LogisticIT model (original)
- `fdr_model_calibrated.pkl` - Threshold-calibrated version (optional)
- `fdr_scaler.pkl` - Feature scaler
- `fdr_model_meta.pkl` - Model metadata
- `fixtures_2017-18_predicted.csv` - Pre-generated 2017-18 predictions

## FDR Coverage

After running [FormFixtures.ipynb](FormFixtures.ipynb), you'll see:

```
2017-18: 8,770 / 8,770 (100.0%) ✅
2018-19: 9,060 / 9,060 (100.0%) ✅
2019-20: 9,039 / 9,039 (100.0%) ✅
2020-21: 8,686 / 8,686 (100.0%) ✅
2021-22: 8,843 / 8,843 (100.0%) ✅
2022-23: 9,319 / 9,319 (100.0%) ✅
2023-24: 9,167 / 9,167 (100.0%) ✅
```

All promoted teams (Norwich, Sheffield Utd, Luton, Leeds, Nott'm Forest) have 100% FDR coverage.

## Example Usage

```python
# Run FormFixtures.ipynb to get merged_df

# Filter to players with high fixture difficulty
hard_fixtures = merged_df[merged_df['FDR'] >= 4]

# Analyze defender performance by FDR
defenders = merged_df[merged_df['Position'].str.contains('CB|RB|LB', na=False)]
performance_by_fdr = defenders.groupby('FDR')['Points'].mean()
print(performance_by_fdr)
```

## Key Features

1. **Complete Coverage**: 100% FDR coverage across all 62,884 observations
2. **Team Name Harmonization**: Automatic mapping between FBREF and FPL naming conventions
3. **Context-Aware**: FDR represents fixture difficulty for the player's team (not opponent)
4. **No Duplicates**: Each player observation has exactly one FDR value per match

## Files Organization

### Main Notebooks
- **FormFixtures.ipynb** - Primary notebook for analysis (loads data, adds FDR, creates merged_df)
- **FDR_Imputation_Model.ipynb** - Model training notebook (only needed for regenerating predictions)

### Supporting Files
- Model artifacts: `*.pkl` files
- Predictions: `fixtures_2017-18_predicted.csv`
- Source data: `def_finaldat.csv`, `att_finaldat.csv`, `team_finaldat.csv`
- FPL data: `Fantasy-Premier-League/data/*/fixtures.csv`

## Workflow

1. **For Analysis**: Just run [FormFixtures.ipynb](FormFixtures.ipynb)
2. **For Model Updates**:
   - Modify [FDR_Imputation_Model.ipynb](FDR_Imputation_Model.ipynb)
   - Regenerate `fixtures_2017-18_predicted.csv`
   - Run [FormFixtures.ipynb](FormFixtures.ipynb) to apply changes

## Notes

- FDR scale: 2 (easiest) to 5 (hardest)
- FDR is team-specific: Same fixture has different FDR for each team
- Example: Bournemouth (Home) vs West Ham (Away) → Bournemouth FDR=2, West Ham FDR=2
- Example: Norwich (Away) vs Liverpool (Home) → Norwich FDR=5, Liverpool FDR=2

## Validation

The implementation has been validated for:
- ✅ Team-specific FDR mapping
- ✅ Date matching accuracy
- ✅ Opponent strength correlation
- ✅ Distribution consistency across seasons
- ✅ Complete promoted team coverage
