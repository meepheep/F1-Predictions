"""Tests for the rolling features in features/rolling.py.

They use a small hand-made table (3 races, 2 teams, 2 drivers each) instead of the real database, so
the expected numbers can be worked out by hand. Each feature function takes the table as its first
argument, so the tests pass it in directly.
"""

import pandas as pd
import pytest

from f1_predictions.features import rolling

# Rows are deliberately out of date order, so the functions must sort them themselves.
#   race 1: b2 starts from the pit lane (grid 0, i.e. last of 4)
#   race 2: a2 retires ("R")
#   race 3: b2 is disqualified ("D")
ROWS = [
    # season, round, raceDate, driverId, constructorId, grid, position_race, positionText
    (2024, 3, "2024-04-01", "a1", "team_a", 1, 1, "1"),
    (2024, 3, "2024-04-01", "a2", "team_a", 2, 2, "2"),
    (2024, 3, "2024-04-01", "b1", "team_b", 3, 3, "3"),
    (2024, 3, "2024-04-01", "b2", "team_b", 4, 4, "D"),
    (2024, 1, "2024-03-01", "a1", "team_a", 1, 1, "1"),
    (2024, 1, "2024-03-01", "a2", "team_a", 2, 3, "3"),
    (2024, 1, "2024-03-01", "b1", "team_b", 3, 2, "2"),
    (2024, 1, "2024-03-01", "b2", "team_b", 0, 4, "4"),
    (2024, 2, "2024-03-15", "a1", "team_a", 2, 2, "2"),
    (2024, 2, "2024-03-15", "a2", "team_a", 1, 4, "R"),
    (2024, 2, "2024-03-15", "b1", "team_b", 3, 1, "1"),
    (2024, 2, "2024-03-15", "b2", "team_b", 4, 3, "3"),
]
COLUMNS = [
    "season",
    "round",
    "raceDate",
    "driverId",
    "constructorId",
    "grid",
    "position_race",
    "positionText",
]


def make_df():
    return pd.DataFrame(ROWS, columns=COLUMNS)


def value(result, key_col, key, round_num, col):
    """Pick one feature value out of a result table, failing clearly if the row is missing or
    duplicated."""
    rows = result[(result[key_col] == key) & (result["round"] == round_num)]
    assert len(rows) == 1, f"expected 1 row for {key} round {round_num}, got {len(rows)}"
    return rows[col].iloc[0]


# --- add_positions_gained ------------------------------------------------------------------------


def run_positions_gained():
    df = make_df()
    out = rolling.add_positions_gained(df)
    return out if out is not None else df  # works whether it edits in place or returns the df


def test_pit_lane_start_counts_as_last():
    df = run_positions_gained()
    row = df[(df["driverId"] == "b2") & (df["round"] == 1)].iloc[0]
    assert row["grid_cleaned"] == 4  # field size of race 1
    assert row["grid"] == 0  # raw grid is left untouched
    assert row["positions_gained"] == 0  # started last (4th), finished 4th


@pytest.mark.parametrize("driver, round_num", [("a2", 2), ("b2", 3)])  # "R" and "D"
def test_non_finishers_have_no_positions_gained(driver, round_num):
    df = run_positions_gained()
    row = df[(df["driverId"] == driver) & (df["round"] == round_num)].iloc[0]
    assert pd.isna(row["positions_gained"])


def test_finishers_keep_positions_gained():
    df = run_positions_gained()
    finishers = df[df["positionText"].str.isdigit()]
    assert finishers["positions_gained"].notna().all()
    row = df[(df["driverId"] == "b1") & (df["round"] == 2)].iloc[0]
    assert row["positions_gained"] == 2  # grid 3 -> finished 1st


# --- driver rolling features ---------------------------------------------------------------------


def test_driver_rolling_finish():
    result = rolling.calculate_driver_rolling_finish(make_df(), periods=5)
    col = "driver_rolling_pos_avg"
    assert pd.isna(value(result, "driverId", "a1", 1, col))  # no earlier races
    assert value(result, "driverId", "a2", 2, col) == pytest.approx(3)  # race 1 only
    assert value(result, "driverId", "a2", 3, col) == pytest.approx(3.5)  # mean(3, 4)
    assert value(result, "driverId", "b1", 3, col) == pytest.approx(1.5)  # mean(2, 1)


def test_driver_rolling_finish_respects_window():
    result = rolling.calculate_driver_rolling_finish(make_df(), periods=1)
    col = "driver_rolling_pos_avg"
    assert value(result, "driverId", "a2", 3, col) == pytest.approx(4)  # race 2 only


def test_driver_rolling_positions_gained():
    result = rolling.calculate_driver_rolling_positions_gained(make_df(), periods=5)
    col = "driver_rolling_positions_gained_avg"
    assert pd.isna(value(result, "driverId", "b1", 1, col))
    assert value(result, "driverId", "b1", 3, col) == pytest.approx(1.5)  # mean(1, 2)
    assert value(result, "driverId", "b2", 3, col) == pytest.approx(0.5)  # mean(0 pit lane, 1)
    assert value(result, "driverId", "a2", 3, col) == pytest.approx(-1)  # race 2 DNF skipped


# --- team rolling features -----------------------------------------------------------------------


def test_team_rolling_finish():
    result = rolling.calculate_team_rolling_finish(make_df(), periods=5)
    col = "team_rolling_pos_avg"
    assert len(result) == 6  # one row per team per race
    # team_a average finish per race: r1 2.0, r2 3.0
    assert pd.isna(value(result, "constructorId", "team_a", 1, col))
    assert value(result, "constructorId", "team_a", 2, col) == pytest.approx(2.0)
    assert value(result, "constructorId", "team_a", 3, col) == pytest.approx(2.5)
    # team_b average finish per race: r1 3.0, r2 2.0
    assert value(result, "constructorId", "team_b", 3, col) == pytest.approx(2.5)


def test_team_rolling_positions_gained():
    result = rolling.calculate_team_rolling_positions_gained(make_df(), periods=5)
    col = "team_rolling_positions_gained_avg"
    assert len(result) == 6
    # team_a average positions gained per race: r1 -0.5, r2 0.0 (a2's DNF skipped)
    assert value(result, "constructorId", "team_a", 2, col) == pytest.approx(-0.5)
    assert value(result, "constructorId", "team_a", 3, col) == pytest.approx(-0.25)
    # team_b average positions gained per race: r1 0.5, r2 1.5
    assert value(result, "constructorId", "team_b", 3, col) == pytest.approx(1.0)


# --- leakage and input safety ------------------------------------------------------------------

FEATURES = [
    (rolling.calculate_driver_rolling_finish, "driverId", "driver_rolling_pos_avg"),
    (
        rolling.calculate_driver_rolling_positions_gained,
        "driverId",
        "driver_rolling_positions_gained_avg",
    ),
    (rolling.calculate_team_rolling_finish, "constructorId", "team_rolling_pos_avg"),
    (
        rolling.calculate_team_rolling_positions_gained,
        "constructorId",
        "team_rolling_positions_gained_avg",
    ),
]
FEATURE_IDS = [f[0].__name__ for f in FEATURES]


@pytest.mark.parametrize("func, key_col, col", FEATURES, ids=FEATURE_IDS)
def test_no_leakage_from_same_race(func, key_col, col):
    """Changing race 3's results must not change any race 3 feature: they may only use races 1-2."""
    before = func(make_df(), periods=5)

    edited = make_df()
    race3 = edited["round"] == 3
    edited.loc[race3, "position_race"] = edited.loc[race3, "position_race"][::-1].values
    edited.loc[race3, "positionText"] = edited.loc[race3, "position_race"].astype(str)
    after = func(edited, periods=5)

    for key in before[key_col].unique():
        b = value(before, key_col, key, 3, col)
        a = value(after, key_col, key, 3, col)
        assert b == pytest.approx(a, nan_ok=True), f"{key}: race 3 feature changed from {b} to {a}"


@pytest.mark.parametrize("func, key_col, col", FEATURES, ids=FEATURE_IDS)
def test_input_is_not_modified(func, key_col, col):
    """Feature functions must work on a copy and leave the caller's DataFrame exactly as it was."""
    df = make_df()
    original = df.copy()
    func(df, periods=5)
    pd.testing.assert_frame_equal(df, original)
