# Decisions

Modelling and data decisions, with the reason for each. Newest at the top of each section.

## Feature table columns (`features/build.py` output)

| column | role | notes |
|---|---|---|
| `position_race` | target | finishing position |
| `status` | result-only | describes the race itself; never a model input |
| `points` | result-only | describes the race itself; never a model input |
| `positionText` | result-only | describes the race itself; never a model input |
| `driverId` | id | |
| `constructorId` | id | |
| `circuitId` | id | |
| `season` | ignore | kept in the table for ordering and walk-forward splits; not a model input |
| `round` | ignore | kept in the table for ordering and walk-forward splits; not a model input |
| `raceDate` | ignore | needed to sort races; can't be a model input |
| `grid` | ignore | raw value (0 = pit lane start); kept for reference, `grid_cleaned` replaces it |
| `grid_cleaned` | feature | pit lane start = field size; from `rolling.add_grid_cleaned()` |
| `position_quali` | feature | NaN when no qualifying row (left join) |
| `q1` | feature | lap time in seconds |
| `q2` | feature | NaN if knocked out in Q1 |
| `q3` | feature | NaN if outside the top 10 |
| `driver_rolling_pos_avg` | feature | |
| `team_rolling_pos_avg` | feature | |
| `driver_rolling_positions_gained_avg` | feature | |
| `team_rolling_positions_gained_avg` | feature | |

Decided 2026-11-12. Why: the goal is to predict the next race, and what matters most is recent form
(the last few races) and qualifying pace. Season, round and date describe *when* a race is, not how
fast anyone is, and the date can't be used as an input.

- 2026-11-12: Use `grid_cleaned`, not raw `grid`, as the model input, because raw `grid` makes a
  pit lane start (0) look better than pole.
- 2026-11-12: Raw q1/q2/q3 stay as features for the first model. A qualifying gap feature (relative
  to the session's fastest time, so it's comparable across circuits) is planned near the end.

## Feature engineering

- 2026-11-12: Rolling averages use `shift(1)` before `rolling(n, min_periods=1)`, so a race's own
  result never counts. Default window is 5 races.
- 2026-11-12: Team features are aggregated to one row per team per race before shifting/rolling;
  otherwise a teammate's same-race result leaks in.
- 2026-11-12: Pit lane start (`grid = 0`) counts as last place (field size), stored as
  `grid_cleaned`; the raw `grid` column is never overwritten.
- 2026-11-12: Positions gained is NaN for non-finishers (non-numeric `positionText`), so DNFs don't
  count as large losses.
- 2026-11-12: Rolling (not season-to-date) average for positions gained.
- 2026-11-12: Feature functions take a DataFrame, work on a copy, and never modify their input.

## Data

- 2026-11-12: Race results are left-joined with qualifying on `(season, round, driverId)`, so every
  race entry is kept even without a qualifying row.
