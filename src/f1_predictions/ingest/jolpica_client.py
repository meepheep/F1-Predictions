import requests

from f1_predictions.config import JOLPICA_BASE_URL, USER_AGENT


def get(path: str) -> dict:
    """Fetch a Jolpica (Ergast-compatible) endpoint, e.g. get("2026/races")."""
    response = requests.get(
        f"{JOLPICA_BASE_URL}/{path.strip('/')}/",
        params={"format": "json"},
        headers={"User-Agent": USER_AGENT},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["MRData"]


def get_races(season: int) -> list[dict]:
    return get(f"{season}/races")["RaceTable"]["Races"]
