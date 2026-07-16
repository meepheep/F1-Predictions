from fastf1.ergast import Ergast
import src.config

ergast = Ergast(result_type="pandas", auto_cast=True)

results = ergast.get_race_results(season=2024, round=1)
print(results.content[0].head())