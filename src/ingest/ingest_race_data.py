import sqlite3
import pandas as pd
import time
import fastf1
from fastf1.exceptions import ErgastInvalidRequestError
from fastf1.ergast import Ergast
ergast = Ergast(result_type="pandas", auto_cast=True)
conn = sqlite3.connect("data/db/f1.db")
fastf1.Cache.enable_cache("data/raw/fastf1_cache")

def fetch_with_retry(func, *args, max_retries=5, base_delay=2, **kwargs):
    """An Ergast API call wrapper that retries on rate limiting errors."""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except ErgastInvalidRequestError as e:
            if "Too Many Requests" in str(e):
                wait = base_delay * (2 ** attempt)   # 2s, 4s, 8s, 16s, 32s
                print(f"Rate limited on attempt {attempt+1}, waiting {wait}s...")
                time.sleep(wait)
            else:
                raise   # a different kind of invalid request — don't retry blindly, surface it
    raise RuntimeError("Max retries exceeded")

for season in range(2021, 2027):
    schedule = ergast.get_race_schedule(season=season)
    for _, race_meta in schedule.iterrows():
        round_num = int(race_meta["round"])
        try:
            results = fetch_with_retry(ergast.get_race_results, season=season, round=round_num)
            time.sleep(1.5)
            race_results = []
            for (_, race_description), result_df in zip(results.description.iterrows(), results.content):
                result_df = result_df.copy()
                result_df.insert(0, "season", race_description["season"])
                result_df.insert(1, "round", race_description["round"])
                result_df.insert(2, "raceDate", race_description["raceDate"])
                result_df.insert(3, "circuitId", race_description["circuitId"])
                race_results.append(result_df)
            results_df = pd.concat(race_results, ignore_index=True)
            results_df = results_df[["season", "round", "raceDate", "circuitId", "driverId", "constructorId", "grid", "position"]]
            results_df.to_sql("race_results", conn, if_exists="append", index=False)
        except Exception as e:
            print(f"Failed on season {season} round {round_num}: {e}")
            time.sleep(2)


