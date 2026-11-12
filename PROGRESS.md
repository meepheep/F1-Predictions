# Progress and next steps

Last updated: 2026-11-12

## Goal

Predict F1 race results (finishing position and podium probability) from historical results,
qualifying and session data. The model has to beat a simple "finish = grid position" baseline in a
walk-forward backtest before any dashboard work starts.

## Done

- **Repo setup:** `src/f1_predictions` package, `pip install -e ".[dev]"`, ruff and pytest set up.
  All paths are in `config.py`.
- **Ingestion (Step 1), complete:** `python -m f1_predictions.ingest.ingest`
  - Fills two SQLite tables in `data/db/f1.db` (schema in `ingest/db.py`):
    - `race_results`: season, round, raceDate, circuitId, driverId, constructorId, grid, position,
      status, points, positionText
    - `qualifying_results`: season, round, raceDate, circuitId, driverId, constructorId, position,
      q1, q2, q3 (lap times in seconds as REAL; NULL when the driver didn't reach that session)
  - Both tables use `(season, round, driverId)` as the primary key.
  - The script covers 2021 to the current year, and both race results and qualifying run through one
    `fetch_results()` function.
  - It's safe to rerun: rounds already in the table are skipped, so are future races. It retries on
    429 rate limits and shows a tqdm progress bar.
  - As of 2026-11-12: 134 rounds in each table (2021 R1 to 2026 R20).
- **Known data quirks:**
  - `grid = 0` means a pit lane start.
  - `position` is filled in even for DNFs, so use `status` or `positionText` to find retirements.
  - Two qualifying rows have a Q3 time but no Q1 time (a gap in the source data).

## Next steps

### Step 2: Features (`src/f1_predictions/features/build.py`), IN PROGRESS
- [x] Load both tables and merge them on `(season, round, driverId)`. Done in
      `features/merge_tables.py` as `load_merged()`: left join from race results, only the
      qualifying columns needed, suffixes `_race`/`_quali` (so `position_race`, `position_quali`).
- [x] First feature end to end: the driver's average finish over the previous 3 races, in
      `features/rolling.py`. Pattern: sort by date, then
      `groupby("driverId")[col].transform(lambda s: s.shift(1).rolling(n, min_periods=1).mean())`.
- [x] Driver rolling positions gained (`add_positions_gained`: grid 0 -> field size, non-numeric
      `positionText` -> NaN). Tests in `tests/test_features.py` pass for all driver features.
- [x] Team rolling finish and positions gained: aggregate to one row per team per race first,
      then shift/roll (otherwise the teammate's same-race result leaks in). All feature tests pass,
      including the leakage test.
- [x] Fixed `tests/test_features.py` (`COLUMNS` matches the 8-value `ROWS` and `load_merged()`
      names again). 18 tests pass; ruff clean.
- [x] Refactored `rolling.py`: each `calculate_*(df, periods=5)` takes a DataFrame, works on
      `df.copy()`, and returns `driver_...`/`team_...` columns. Tests pass `make_df()` directly and
      include `test_input_is_not_modified`. `add_positions_gained` now writes `grid_cleaned`
      instead of overwriting `grid` (test checks `grid_cleaned == 4` and `grid` still 0). 22 pass,
      ruff clean.
- [ ] NEXT: `features/build.py`: load once, sort once, call each feature as `add_xxx(df)`, merge
      the team features back onto driver rows on `(season, round, constructorId)`.
- [ ] Qualifying/grid position, treating grid 0 as last.
- [ ] Driver DNF rate (rolling finish is done; window is the `periods` argument).
- [ ] Constructor rolling points (rolling finish is done).
- [ ] Driver's history at this circuit.
- [ ] Teammate qualifying gap.
- [ ] Save to `data/processed/features.parquet` (add `pyarrow` to the dependencies).
- [x] Leakage test: changing round N's result must not change round N's features
      (`test_no_leakage_from_same_race`). Extend it to each new feature.

### Step 3: Baseline and model (`src/f1_predictions/models/`)
- [ ] Baseline: predicted finish = grid position.
- [ ] scikit-learn gradient boosting for finish position, plus a classifier for P(podium). Add
      `scikit-learn` to the dependencies.
- [ ] Save models with joblib to `data/processed/models/`.

### Step 4: Walk-forward backtest (`src/f1_predictions/evaluate/backtest.py`)
- [ ] For each race in 2024-2026, train only on earlier races and predict that race. Never split
      randomly.
- [ ] Report MAE, Spearman rank correlation per race, podium hit rate and Brier score, for the model
      and the baseline side by side.

### Step 5: Later
- [ ] Practice-session pace features from FastF1 (FP2 long runs); `tests/fixtures/laps_sample.csv`
      can be the test fixture.
- [ ] `serve/predict.py`: a function `predict_race(season, round) -> DataFrame`.
- [ ] Streamlit dashboard in `dashboard/`.

## Session log

Add one line per working session, newest first.

- 2026-11-12: Fixed broken test table (commit 4601462). Refactored `rolling.py` to take a
  DataFrame and not modify its input; tests rewritten to match; `grid_cleaned` instead of overwriting `grid` (22 pass).
  Next: `build.py`.

- 2026-11-12: Tidied `load_merged()`; rolling 3-race average finish works. Chose a rolling
  (not season) average for positions gained, as the next feature.
- 2026-11-12: Fixed `ModuleNotFoundError` (reran `pip install -e ".[dev]"` in `.venv`). Loaded and
  merged both tables in `features/merge_tables.py`. README brought up to date. Next: rolling
  3-race finish feature.
- 2026-11-12: Finished ingestion: qualifying table, generic `fetch_results()`, season range up to
  the current year, ruff formatting. Next up is Step 2.
