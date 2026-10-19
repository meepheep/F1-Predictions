import pandas as pd

from f1_predictions.config import CACHE_DIR

obj = pd.read_pickle(
    CACHE_DIR / "2024" / "2024-03-02_Bahrain_Grand_Prix" / "2024-03-02_Race" / "driver_info.ff1pkl"
)

dfs = obj["data"]

print(dfs["1"].loc[:, ["Time", "SessionTime", "Date"]])
