"""Warehouse tests: init creates all tables, syncs dim_series, and is a no-op
on re-run (C1 Definition of Done)."""

from __future__ import annotations

from ipos.config.load import load_registry
from ipos.warehouse.db import connect, init_db

EXPECTED_TABLES = {
    "meta", "dim_series", "fact_observation", "fact_weekly", "fact_feature",
    "fact_score", "agg_module", "agg_regime", "log_contradiction", "run_log",
}


def test_init_creates_schema_and_syncs(tmp_path):
    reg = load_registry()
    db = tmp_path / "w.duckdb"
    report = init_db(reg, db)
    assert "001_init.sql" in report["migrations_applied"]
    assert report["dim_series_synced"] == 22

    with connect(db, read_only=True) as con:
        tables = {
            r[0]
            for r in con.execute(
                "SELECT table_name FROM information_schema.tables"
            ).fetchall()
        }
        assert EXPECTED_TABLES <= tables
        n = con.execute("SELECT count(*) FROM dim_series").fetchone()[0]
        assert n == 22


def test_init_is_idempotent(tmp_path):
    reg = load_registry()
    db = tmp_path / "w.duckdb"
    init_db(reg, db)
    second = init_db(reg, db)
    assert second["migrations_applied"] == []  # no-op re-run
    assert second["dim_series_synced"] == 22
