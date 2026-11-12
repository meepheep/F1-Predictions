import sqlite3
import pandas as pd
from f1_predictions.config import DB_PATH

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

race_df = pd.read_sql_query("SELECT * FROM race_results", conn)
quali_df = pd.read_sql_query("SELECT * FROM qualifying_results", conn)

merged_df = pd.merge(race_df, quali_df, on=["season", "round", "driverId"], how="left", suffixes=("_race", "_quali"))