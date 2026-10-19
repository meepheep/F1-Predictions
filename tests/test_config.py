from pathlib import Path

import pandas as pd

from f1_predictions import config

FIXTURES = Path(__file__).parent / "fixtures"


def test_paths_are_inside_project():
    assert (config.PROJECT_ROOT / "pyproject.toml").exists()
    assert config.DB_PATH.is_relative_to(config.PROJECT_ROOT)
    assert config.CACHE_DIR.is_relative_to(config.PROJECT_ROOT)


def test_laps_fixture_loads():
    laps = pd.read_csv(FIXTURES / "laps_sample.csv")
    assert {"Driver", "LapTime", "NumberOfLaps"} <= set(laps.columns)
