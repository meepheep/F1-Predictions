from f1_predictions.features import rolling, merge_tables
import pandas as pd


def build_rolling_features(df, periods=5):
    starting_length = len(df)
    driver_rolling_finish = rolling.calculate_driver_rolling_finish(df, periods)
    team_rolling_finish = rolling.calculate_team_rolling_finish(df, periods)
    driver_rolling_positions_gained = rolling.calculate_driver_rolling_positions_gained(df, periods)
    team_rolling_positions_gained = rolling.calculate_team_rolling_positions_gained(df, periods)

    df = rolling.add_grid_cleaned(df)

    df = pd.merge(df, driver_rolling_finish, on=["season", "round", "driverId"], how="left")
    df = pd.merge(df, team_rolling_finish, on=["season", "round", "constructorId"], how="left")
    df = pd.merge(
        df, driver_rolling_positions_gained, on=["season", "round", "driverId"], how="left"
    )
    df = pd.merge(
        df, team_rolling_positions_gained, on=["season", "round", "constructorId"], how="left"
    )

    assert len(df) == starting_length
    return df


def main():
    df = merge_tables.load_merged()
    df = build_rolling_features(df, periods=5)
    print(df.shape)
    print(df.tail())


if __name__ == "__main__":
    main()
