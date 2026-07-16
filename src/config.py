from pathlib import Path
import fastf1

CACHE_DIR = Path("data/raw/fastf1_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))
