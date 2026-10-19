# F1-Predictions

Formula 1 prediction model built on [FastF1](https://docs.fastf1.dev/) session data and the
[Jolpica](https://github.com/jolpica/jolpica-f1) (Ergast-compatible) API.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows (macOS/Linux: source .venv/bin/activate)
pip install -e ".[dev]"
```

## Project layout

```
src/f1_predictions/   the package; all reusable logic lives here
  config.py           paths and constants
  ingest/             pull data from FastF1 / Jolpica into SQLite
  features/           build model inputs from the database
  models/             train and predict
  evaluate/           backtests and metrics
  serve/              functions the dashboard calls
scripts/              small entry points you run directly
notebooks/            exploration
dashboard/            the front end
tests/                pytest tests (fixtures/ holds sample data)
data/                 local data, not committed (raw/, db/, processed/)
```

## Common commands

```bash
pytest                          # run tests
ruff check . && ruff format .   # lint and format
python scripts/explore_ergast.py
```
