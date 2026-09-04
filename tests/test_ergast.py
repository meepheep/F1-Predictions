from fastf1.ergast import Ergast

ergast = Ergast(result_type="pandas", auto_cast=True)
version = "1.0.0"

race_results = ergast.get_race_results(season=2024, round=1)

#print(race_results.content[0])
#print()
#print(race_results.description.iloc[0])

#print(race_results.content[0].columns.tolist())
print(race_results.description.columns.tolist())