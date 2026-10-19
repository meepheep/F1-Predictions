from pathlib import Path

import fastf1

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
DB_PATH = DATA_DIR / "db" / "f1.db"
CACHE_DIR = RAW_DIR / "fastf1_cache"

VERSION = "0.1.0"
JOLPICA_BASE_URL = "https://api.jolpi.ca/ergast/f1"
USER_AGENT = f"F1-Predictions/{VERSION}"


def enable_fastf1_cache() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    fastf1.Cache.enable_cache(str(CACHE_DIR))
