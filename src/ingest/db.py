# src/ingest/db.py
import sqlite3
from pathlib import Path

DB_PATH = Path("data/db/f1.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS 
"""