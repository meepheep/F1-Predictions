# F1-Predictions

A Formula 1 race prediction model built on [FastF1](https://docs.fastf1.dev/) session data and the
[Jolpica](https://github.com/jolpica/jolpica-f1) API (an Ergast-compatible replacement for the
retired Ergast API).

> **Status:** early development. Data ingestion works. Feature building, models, evaluation and
> the dashboard are scaffolded but not yet implemented.

## Requirements

- Python 3.11+
- Internet access for the first data pull (FastF1 caches responses locally after that)

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows (macOS/Linux: source .venv/bin/activate)
pip install -e ".[dev]"
```

The editable install (`-e`) makes `f1_predictions` importable from anywhere in the repo, including
`scripts/` and `notebooks/`.

## Getting the data

Pull race results for the 2021–2026 seasons into a local SQLite database:

```bash
python -m f1_predictions.ingest.ingest_race_data
```

This command:

- creates `data/db/f1.db` and the `race_results` table if they don't exist
- fetches each round's results through FastF1's Ergast interface (which calls Jolpica)
- waits between requests and backs off on HTTP 429 rate limits, so a full run takes a few minutes
- caches raw API responses in `data/raw/fastf1_cache/`

Rounds that fail are logged and skipped, so the rest of the run still finishes. Rows are appended,
and `(season, round, driverId)` is the primary key. If you run the command again over seasons that
are already loaded, those rounds will report duplicate-key failures. To rebuild from scratch,
delete `data/db/f1.db` first.

To pull a different range of seasons:

```python
from f1_predictions.ingest.ingest_race_data import main
main(seasons=range(2018, 2021))
```

### Database schema

`race_results`: one row per driver per race.

| column          | type    | notes                                    |
|-----------------|---------|------------------------------------------|
| `season`        | INTEGER |                                          |
| `round`         | INTEGER |                                          |
| `raceDate`      | TEXT    |                                          |
| `circuitId`     | TEXT    | Ergast circuit ID, e.g. `bahrain`        |
| `driverId`      | TEXT    | Ergast driver ID, e.g. `max_verstappen`  |
| `constructorId` | TEXT    | Ergast constructor ID, e.g. `red_bull`   |
| `grid`          | INTEGER | starting position (0 = pit lane start)   |
| `position`      | INTEGER | finishing position                       |

A quick check query is in [scripts/check_race_results.sql](scripts/check_race_results.sql).

### Other data helpers

```python
from f1_predictions.ingest.fastf1_client import load_session
from f1_predictions.ingest import jolpica_client

session = load_session(2024, "Bahrain", "R")   # full FastF1 session (laps, telemetry, weather)
races = jolpica_client.get_races(2026)         # raw Jolpica schedule JSON
```

## Project layout

```
src/f1_predictions/   the package; all reusable logic lives here
  config.py           paths, API URL, User-Agent, FastF1 cache setup
  ingest/             pull data from FastF1 / Jolpica into SQLite
  features/           build model inputs from the database        (planned)
  models/             train and predict                           (planned)
  evaluate/           backtests and metrics                       (planned)
  serve/              functions the dashboard calls               (planned)
scripts/              small exploration scripts you run directly
notebooks/            exploration
dashboard/            the front end                               (planned)
tests/                pytest tests (fixtures/ holds sample data)
data/                 local data, not committed (raw/, db/, processed/)
```

All paths are defined in [config.py](src/f1_predictions/config.py) relative to the project root, so
scripts work no matter which directory you run them from.

## Development

```bash
pytest                          # run tests
ruff check . && ruff format .   # lint and format (line length 100)
```

## License

MIT. See [LICENSE](LICENSE).
