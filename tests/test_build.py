"""Tests for features/build.py.

They reuse the hand-made table from test_features.py (3 races, 2 teams, 2 drivers each), so the
expected feature values are the same ones worked out by hand there.
"""

import pandas as pd
import pytest

from f1_predictions.features import build
from tests.test_features import make_df

KEYS = ["season", "round", "driverId"]
FEATURE_COLUMNS = [
    "grid_cleaned",
    "driver_rolling_pos_avg",
    "team_rolling_pos_avg",
    "driver_rolling_positions_gained_avg",
    "team_rolling_positions_gained_avg",
]


def row(df, driver, round_num):
    """Return the single row for one driver in one race, failing clearly if it's missing or
    duplicated."""
    rows = df[(df["driverId"] == driver) & (df["round"] == round_num)]
    assert len(rows) == 1, f"expected 1 row for {driver} round {round_num}, got {len(rows)}"
    return rows.iloc[0]


def test_one_row_per_driver_per_race():
    df = make_df()
    out = build.build_rolling_features(df, periods=5)
    assert len(out) == len(df)  # merges must not add or drop rows
    assert not out.duplicated(KEYS).any()


def test_all_feature_columns_present():
    out = build.build_rolling_features(make_df(), periods=5)
    missing = [c for c in FEATURE_COLUMNS if c not in out.columns]
    assert not missing, f"missing feature columns: {missing}"


def test_original_columns_kept():
    """The target and the raw grid must survive the merges unchanged (the model and the baseline
    need them)."""
    df = make_df()
    out = build.build_rolling_features(df, periods=5)
    merged = df.merge(out, on=KEYS, suffixes=("", "_out"))
    for col in ["position_race", "grid", "constructorId"]:
        assert col in out.columns
        assert (merged[col] == merged[f"{col}_out"]).all(), f"{col} changed during the build"


def test_pit_lane_start_cleaned_in_output():
    out = build.build_rolling_features(make_df(), periods=5)
    b2 = row(out, "b2", 1)
    assert b2["grid_cleaned"] == 4  # pit lane start = field size of race 1
    assert b2["grid"] == 0  # raw grid kept as it was
    a1 = row(out, "a1", 1)
    assert a1["grid_cleaned"] == a1["grid"] == 1  # normal starts are unchanged


def test_driver_feature_lands_on_the_right_driver():
    out = build.build_rolling_features(make_df(), periods=5)
    # Same numbers as test_driver_rolling_finish / test_driver_rolling_positions_gained.
    assert row(out, "a2", 3)["driver_rolling_pos_avg"] == pytest.approx(3.5)
    assert row(out, "b1", 3)["driver_rolling_pos_avg"] == pytest.approx(1.5)
    assert row(out, "b2", 3)["driver_rolling_positions_gained_avg"] == pytest.approx(0.5)
    assert pd.isna(row(out, "a1", 1)["driver_rolling_pos_avg"])  # no earlier races


def test_team_feature_copied_to_both_drivers():
    out = build.build_rolling_features(make_df(), periods=5)
    # team_a race 3: mean of its race 1 (2.0) and race 2 (3.0) average finishes.
    for driver in ["a1", "a2"]:
        assert row(out, driver, 3)["team_rolling_pos_avg"] == pytest.approx(2.5)
    # team_b race 3 positions gained: mean of 0.5 and 1.5.
    for driver in ["b1", "b2"]:
        assert row(out, driver, 3)["team_rolling_positions_gained_avg"] == pytest.approx(1.0)


def test_input_is_not_modified():
    df = make_df()
    original = df.copy()
    build.build_rolling_features(df, periods=5)
    pd.testing.assert_frame_equal(df, original)


def test_no_leakage_from_same_race():
    """End to end: changing race 3's results must not change any race 3 feature."""
    before = build.build_rolling_features(make_df(), periods=5)

    edited = make_df()
    race3 = edited["round"] == 3
    edited.loc[race3, "position_race"] = edited.loc[race3, "position_race"][::-1].values
    edited.loc[race3, "positionText"] = edited.loc[race3, "position_race"].astype(str)
    after = build.build_rolling_features(edited, periods=5)

    b = before[before["round"] == 3].sort_values("driverId").reset_index(drop=True)
    a = after[after["round"] == 3].sort_values("driverId").reset_index(drop=True)
    pd.testing.assert_frame_equal(b[FEATURE_COLUMNS], a[FEATURE_COLUMNS])
