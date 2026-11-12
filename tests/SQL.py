from f1_predictions.ingest import db
import pandas as pd

conn = db.connect()
loaded = pd.read_sql("SELECT status, COUNT(*) FROM race_results GROUP BY status", conn)

print(loaded.head())
