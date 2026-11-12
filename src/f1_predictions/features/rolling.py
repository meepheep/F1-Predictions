import pandas as pd


def add_positions_gained(df):
    df["field_size"] = df.groupby(["season", "round"])["driverId"].transform("count")
    df["grid_cleaned"] = df["grid"]
    grid_mask = df["grid"] == 0
    df.loc[grid_mask, "grid_cleaned"] = df.loc[grid_mask, "field_size"]
    df["positions_gained"] = df["grid_cleaned"] - df["position_race"]
    finish_mask = ~df["positionText"].str.isdigit()
    df.loc[finish_mask, "positions_gained"] = float("nan")
    return df


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
