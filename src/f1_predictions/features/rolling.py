import pandas as pd


def add_grid_cleaned(df):
    out = df.copy()
    out["field_size"] = out.groupby(["season", "round"])["driverId"].transform("count")
    out["grid_cleaned"] = out["grid"]
    grid_mask = out["grid"] == 0
    out.loc[grid_mask, "grid_cleaned"] = out.loc[grid_mask, "field_size"]
    out.drop(columns=["field_size"], inplace=True)
    return out


def add_positions_gained(df):
    out = df.copy()
    out = add_grid_cleaned(out)
    out["positions_gained"] = out["grid_cleaned"] - out["position_race"]
    finish_mask = ~out["positionText"].str.isdigit()
    out.loc[finish_mask, "positions_gained"] = float("nan")
    return out


def calculate_driver_rolling_finish(df, periods=5):
    avg_finish_df = df.copy()
    avg_finish_df["raceDate"] = pd.to_datetime(avg_finish_df["raceDate"])
    avg_finish_df = avg_finish_df.sort_values(by="raceDate", ascending=True)
    avg_finish_df["driver_rolling_pos_avg"] = avg_finish_df.groupby(["driverId"])[
        "position_race"
    ].transform(lambda x: x.shift(1).rolling(periods, min_periods=1).mean())
    return avg_finish_df[["season", "round", "driverId", "driver_rolling_pos_avg"]]


def calculate_team_rolling_finish(df, periods=5):
    avg_finish_df = df.copy()
    team_pos_avg_df = (
        avg_finish_df.groupby(["constructorId", "season", "round"])["position_race"]
        .agg("mean")
        .reset_index()
    )
    team_pos_avg_df = team_pos_avg_df.sort_values(by=["season", "round"], ascending=True)
    team_pos_avg_df["team_rolling_pos_avg"] = team_pos_avg_df.groupby(["constructorId"])[
        "position_race"
    ].transform(lambda x: x.shift(1).rolling(periods, min_periods=1).mean())
    return team_pos_avg_df[["season", "round", "constructorId", "team_rolling_pos_avg"]]


def calculate_driver_rolling_positions_gained(df, periods=5):
    avg_finish_df = df.copy()
    avg_finish_df["raceDate"] = pd.to_datetime(avg_finish_df["raceDate"])
    avg_finish_df = avg_finish_df.sort_values(by="raceDate", ascending=True)
    avg_finish_df = add_positions_gained(avg_finish_df)
    avg_finish_df["driver_rolling_positions_gained_avg"] = avg_finish_df.groupby(["driverId"])[
        "positions_gained"
    ].transform(lambda x: x.shift(1).rolling(periods, min_periods=1).mean())
    return avg_finish_df[["season", "round", "driverId", "driver_rolling_positions_gained_avg"]]


def calculate_team_rolling_positions_gained(df, periods=5):
    avg_finish_df = df.copy()
    avg_finish_df = add_positions_gained(avg_finish_df)
    team_pos_avg_df = (
        avg_finish_df.groupby(["constructorId", "season", "round"])["positions_gained"]
        .agg("mean")
        .reset_index()
    )
    team_pos_avg_df = team_pos_avg_df.sort_values(by=["season", "round"], ascending=True)
    team_pos_avg_df["team_rolling_positions_gained_avg"] = team_pos_avg_df.groupby(
        ["constructorId"]
    )["positions_gained"].transform(lambda x: x.shift(1).rolling(periods, min_periods=1).mean())
    return team_pos_avg_df[
        ["season", "round", "constructorId", "team_rolling_positions_gained_avg"]
    ]
