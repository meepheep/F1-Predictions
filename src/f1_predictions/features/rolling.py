from f1_predictions.features import merge_tables
import pandas as pd


def add_positions_gained(df):
    df["field_size"] = df.groupby(["season", "round"])["driverId"].transform("count")
    grid_mask = df["grid"] == 0
    df.loc[grid_mask, "grid"] = df.loc[grid_mask, "field_size"]
    df["positions_gained"] = df["grid"] - df["position_race"]
    finish_mask = ~df["positionText"].str.isdigit()
    df.loc[finish_mask, "positions_gained"] = float("nan")
    return df


def calculate_driver_rolling_finish(periods=5):
    merged_df = merge_tables.load_merged()
    avg_finish_df = merged_df
    avg_finish_df["raceDate"] = pd.to_datetime(avg_finish_df["raceDate"])
    avg_finish_df = avg_finish_df.sort_values(by="raceDate", ascending=True)
    avg_finish_df["rolling_pos_avg"] = avg_finish_df.groupby(["driverId"])[
        "position_race"
    ].transform(lambda x: x.shift(1).rolling(periods, min_periods=1).mean())
    return avg_finish_df[["season", "round", "driverId", "rolling_pos_avg"]]


def calculate_team_rolling_finish(periods=5):
    merged_df = merge_tables.load_merged()
    avg_finish_df = merged_df
    team_pos_avg_df = (
        avg_finish_df.groupby(["constructorId", "season", "round"])["position_race"]
        .agg("mean")
        .reset_index()
    )
    team_pos_avg_df = team_pos_avg_df.sort_values(by=["season", "round"], ascending=True)
    team_pos_avg_df["rolling_pos_avg"] = team_pos_avg_df.groupby(["constructorId"])[
        "position_race"
    ].transform(lambda x: x.shift(1).rolling(periods, min_periods=1).mean())
    return team_pos_avg_df[["season", "round", "constructorId", "rolling_pos_avg"]]


def calculate_driver_rolling_positions_gained(periods=5):
    merged_df = merge_tables.load_merged()
    avg_finish_df = merged_df
    avg_finish_df["raceDate"] = pd.to_datetime(avg_finish_df["raceDate"])
    avg_finish_df = avg_finish_df.sort_values(by="raceDate", ascending=True)
    add_positions_gained(avg_finish_df)
    avg_finish_df["rolling_positions_gained_avg"] = avg_finish_df.groupby(["driverId"])[
        "positions_gained"
    ].transform(lambda x: x.shift(1).rolling(periods, min_periods=1).mean())
    return avg_finish_df[["season", "round", "driverId", "rolling_positions_gained_avg"]]


def calculate_team_rolling_positions_gained(periods=5):
    merged_df = merge_tables.load_merged()
    avg_finish_df = merged_df
    add_positions_gained(avg_finish_df)
    team_pos_avg_df = (
        avg_finish_df.groupby(["constructorId", "season", "round"])["positions_gained"]
        .agg("mean")
        .reset_index()
    )
    team_pos_avg_df = team_pos_avg_df.sort_values(by=["season", "round"], ascending=True)
    team_pos_avg_df["rolling_positions_gained_avg"] = team_pos_avg_df.groupby(["constructorId"])[
        "positions_gained"
    ].transform(lambda x: x.shift(1).rolling(periods, min_periods=1).mean())
    return team_pos_avg_df[["season", "round", "constructorId", "rolling_positions_gained_avg"]]
