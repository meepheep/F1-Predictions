from f1_predictions.ingest import db


def test_init_db_creates_race_results(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "f1.db")
    db.init_db()

    with db.connect() as conn:
        columns = [row[1] for row in conn.execute("PRAGMA table_info(race_results)")]

    assert columns == [
        "season",
        "round",
        "raceDate",
        "circuitId",
        "driverId",
        "constructorId",
        "grid",
        "position",
    ]
