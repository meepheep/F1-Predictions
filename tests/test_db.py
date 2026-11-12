from f1_predictions.ingest import db


def table_columns(conn, table):
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}


def primary_key(conn, table):
    # PRAGMA table_info's last field is the column's position in the primary key (0 = not in it)
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return [row[1] for row in sorted(rows, key=lambda r: r[5]) if row[5] > 0]


def test_init_db_creates_race_results(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "f1.db")
    db.init_db()

    with db.connect() as conn:
        # compared as a set: to_sql matches columns by name, so their order doesn't matter
        assert table_columns(conn, "race_results") == {
            "season",
            "round",
            "raceDate",
            "circuitId",
            "driverId",
            "constructorId",
            "grid",
            "position",
            "status",
            "points",
            "positionText",
        }
        assert primary_key(conn, "race_results") == ["season", "round", "driverId"]


def test_init_db_creates_qualifying_results(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "f1.db")
    db.init_db()

    with db.connect() as conn:
        assert table_columns(conn, "qualifying_results") == {
            "season",
            "round",
            "raceDate",
            "circuitId",
            "driverId",
            "constructorId",
            "position",
            "q1",
            "q2",
            "q3",
        }
        assert primary_key(conn, "qualifying_results") == ["season", "round", "driverId"]


def test_init_db_can_run_twice(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "f1.db")
    db.init_db()
    db.init_db()  # CREATE TABLE IF NOT EXISTS must not fail on an existing database
