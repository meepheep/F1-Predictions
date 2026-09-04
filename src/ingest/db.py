# src/ingest/db.py
import sqlite3
from pathlib import Path

DB_PATH = Path("data/db/f1.db")
conn = sqlite3.connect(DB_PATH)
connection = sqlite3.Connection(DB_PATH)
cursor = connection.cursor()

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

cursor = cursor.execute(SCHEMA)
#conn.execute("DELETE FROM race_results")
#conn.commit()