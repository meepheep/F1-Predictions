import fastf1

from f1_predictions.config import enable_fastf1_cache


def load_session(season: int, event: str | int, session: str = "R") -> fastf1.core.Session:
    """Load a FastF1 session (e.g. load_session(2024, "Bahrain", "R")) using the local cache."""
    enable_fastf1_cache()
    s = fastf1.get_session(season, event, session)
    s.load()
    return s
