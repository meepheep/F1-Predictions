from fastf1.ergast import Ergast
import requests

ergast = Ergast(result_type="pandas", auto_cast=True)
version = "1.0.0"

results = ergast.get_race_results(season=2024, round=1)

print(results)