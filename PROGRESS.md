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

### Step 2: Features (`src/f1_predictions/features/build.py`), NEXT
- [ ] Load both tables and merge them on `(season, round, driverId)`.
- [ ] First feature end to end: the driver's average finish over the previous 3 races. Sort by
      date, group by driver, and `shift(1)` before `rolling()` so a race's own result never leaks in.
- [ ] Qualifying/grid position, treating grid 0 as last.
- [ ] Driver rolling finish over 3 and 5 races, and DNF rate.
- [ ] Constructor rolling finish and points.
- [ ] Driver's history at this circuit.
- [ ] Teammate qualifying gap.
- [ ] Save to `data/processed/features.parquet` (add `pyarrow` to the dependencies).
- [ ] Leakage test: changing round N's result must not change round N's features.

### Step 3: Baseline and model (`src/f1_predictions/models/`)
- [ ] Baseline: predicted finish = grid position.
- [ ] scikit-learn gradient boosting for finish position, plus a classifier for P(podium). Add
      `scikit-learn` to the dependencies.
- [ ] Save models with joblib to `data/processed/models/`.

### Step 4: Walk-forward backtest (`src/f1_predictions/evaluate/backtest.py`)
- [ ] For each race in 2024–2026, train only on earlier races and predict that race. Never split
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

- 2026-11-12: Finished ingestion: qualifying table, generic `fetch_results()`, season range up to
  the current year, ruff formatting. Next up is Step 2.
