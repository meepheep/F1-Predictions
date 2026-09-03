from fastf1.ergast import Ergast
import requests

ergast = Ergast(result_type="pandas", auto_cast=True)
version = "1.0.0"

#results = ergast.get_race_results(season=2024, round=1)

results = requests.get(
    "https://api.jolpi.ca/ergast/f1/2026/races/?format=json",
    headers={"User-Agent": f"YourAppName/{version}"},
)
print(results.json()["MRData"]['RaceTable']['Races'][0]['Circuit']['circuitName'])