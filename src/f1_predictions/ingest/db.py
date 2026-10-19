import sqlite3

from f1_predictions.config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS race_results (
    season INTEGER,
    round INTEGER,
    raceDate TEXT,
    circuitId TEXT,
    driverId TEXT,
    constructorId TEXT,
    grid INTEGER,
    position INTEGER,
    PRIMARY KEY (season, round, driverId)
);
"""


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)
