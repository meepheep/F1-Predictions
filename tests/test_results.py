import pandas as pd

from fastf1.ergast import Ergast

ergast = Ergast(result_type="pandas", auto_cast=True)

results = ergast.get_race_results(season=2024, round=1)

race_results = []
for (_, race_description), result_df in zip(results.description.iterrows(), results.content):
	result_df = result_df.copy()
	result_df.insert(0, "season", race_description["season"])
	result_df.insert(1, "round", race_description["round"])
	result_df.insert(2, "raceDate", race_description["raceDate"])
	result_df.insert(3, "circuit_id", race_description["circuitId"])
	race_results.append(result_df)
results_df = pd.concat(race_results, ignore_index=True)

print(results_df.columns.tolist())
results_df = results_df[["season", "round", "raceDate", "circuit_id", "driverId", "constructorId", "grid", "position"]]
print(results_df.head())