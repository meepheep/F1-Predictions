import time
from datetime import datetime

import pandas as pd
from fastf1.ergast import Ergast
from fastf1.exceptions import ErgastInvalidRequestError
from tqdm import tqdm

from f1_predictions.config import enable_fastf1_cache
from f1_predictions.ingest import db


def fetch_with_retry(func, *args, max_retries=5, base_delay=2, **kwargs):
    """An Ergast API call wrapper that retries on rate limiting errors."""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except ErgastInvalidRequestError as e:
            if "Too Many Requests" in str(e):
                wait = base_delay * (2**attempt)  # 2s, 4s, 8s, 16s, 32s
                tqdm.write(f"Rate limited on attempt {attempt + 1}, waiting {wait}s...")
                time.sleep(wait)
            else:
                raise  # a different kind of invalid request — don't retry blindly, surface it
    raise RuntimeError("Max retries exceeded")


def fetch_results(
    seasons=range(2021, (datetime.now().year + 1)),
    fetch_type=None,
    table_name=None,
    column_list=None,
):
    enable_fastf1_cache()
    db.init_db()
    ergast = Ergast(result_type="pandas", auto_cast=True, limit=None)
    conn = db.connect()
    rounds = []
    fetch_method = getattr(ergast, fetch_type)

    for season in seasons:
        schedule = ergast.get_race_schedule(season=season)
        rounds.extend(schedule[["season", "round", "raceDate"]].values.tolist())

    loaded = conn.execute(f"SELECT DISTINCT season, round FROM {table_name}").fetchall()
    loaded_set = set(loaded)
    rounds = [
        r for r in rounds if tuple(r[:2]) not in loaded_set
    ]  # only fetch rounds that are not already in the database
    rounds = [
        r for r in rounds if pd.to_datetime(r[2]) < pd.Timestamp.now()
    ]  # only fetch rounds that have already happened

    for season, round_num, raceDate in tqdm(rounds, desc="Ingesting", unit="round"):
        try:
            results = fetch_with_retry(fetch_method, season=season, round=round_num)
            time.sleep(1.5)
            race_results = []
            for (_, race_description), result_df in zip(
                results.description.iterrows(), results.content
            ):
                result_df = result_df.copy()
                result_df.insert(0, "season", race_description["season"])
                result_df.insert(1, "round", race_description["round"])
                result_df.insert(2, "raceDate", race_description["raceDate"])
                result_df.insert(3, "circuitId", race_description["circuitId"])
                race_results.append(result_df)
            results_df = pd.concat(race_results, ignore_index=True)
            results_df = results_df[column_list]
            for col in results_df.columns:
                if pd.api.types.is_timedelta64_dtype(results_df[col]):
                    results_df[col] = results_df[col].apply(
                        lambda x: x.total_seconds() if pd.notnull(x) else None
                    )
            results_df.to_sql(table_name, conn, if_exists="append", index=False)
        except Exception as e:
            tqdm.write(f"Failed on season {season} round {round_num}: {e}")
            time.sleep(2)

    conn.close()


def main():
    fetch_results(
        fetch_type="get_race_results",
        table_name="race_results",
        column_list=[
            "season",
            "round",
            "raceDate",
            "circuitId",
            "driverId",
            "constructorId",
            "grid",
            "position",
            "status",
            "points",
            "positionText",
        ],
    )
    fetch_results(
        fetch_type="get_qualifying_results",
        table_name="qualifying_results",
        column_list=[
            "season",
            "round",
            "raceDate",
            "circuitId",
            "driverId",
            "constructorId",
            "position",
            "Q1",
            "Q2",
            "Q3",
        ],
    )


if __name__ == "__main__":
    main()
