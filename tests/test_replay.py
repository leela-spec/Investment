"""Aggregate-layer replay tests (``ipos/replay.py``).

The critical one is the synthetic guard: replay is a new code path over
``fact_weekly``/``fact_score``, and this repo has already closed two
"synthetic data served as real" bugs. ``fact_score`` carries no vintage, so a
score built on a synthetic canonical value looks real — the guard therefore
has to work off ``fact_weekly.vintage_id``. No network.
"""

from __future__ import annotations

import datetime as dt

import pytest

from ipos.config.load import load_registry
from ipos.replay import (
    recent_scored_weeks,
    replay_aggregates,
    synthetic_weeks,
)
from ipos.warehouse.db import connect, init_db

WEEKS = [dt.date(2026, 5, 1), dt.date(2026, 5, 8), dt.date(2026, 5, 15),
         dt.date(2026, 5, 22), dt.date(2026, 5, 29)]


def _seed(db, *, synthetic_on: list[dt.date] | None = None):
    """Minimal multi-week warehouse: SPX closes + scores for two modules."""
    reg = load_registry()
    init_db(reg, db)
    synthetic_on = synthetic_on or []
    with connect(db) as con:
        for i, wk in enumerate(WEEKS):
            for sid, base in (("SPX", 5000.0), ("VIXCLS", 18.0), ("DGS10", 4.2)):
                vintage = ("synthetic@%s@2026-07-17" % sid) if wk in synthetic_on else "fred@2026-07-24"
                con.execute(
                    "INSERT OR REPLACE INTO fact_weekly (series_id, as_of_date, value, "
                    "vintage_id, obs_date, ingested_at) VALUES (?,?,?,?,?,?)",
                    [sid, wk, base + i * 10, vintage, wk, dt.datetime(2026, 7, 24)],
                )
                con.execute(
                    "INSERT OR REPLACE INTO fact_score (series_id, as_of_date, score_0_100, "
                    "scoring_method, confidence_0_100) VALUES (?,?,?,?,?)",
                    [sid, wk, 50.0 + i * 5, "percentile", 80.0],
                )
    return reg


def test_recent_scored_weeks_returns_oldest_first(tmp_path):
    db = tmp_path / "w.duckdb"
    _seed(db)
    with connect(db, read_only=True) as con:
        got = recent_scored_weeks(con, 3)
    assert got == WEEKS[-3:]  # last three, chronological


def test_synthetic_weeks_detects_tainted_canonical_rows(tmp_path):
    db = tmp_path / "w.duckdb"
    _seed(db, synthetic_on=[WEEKS[1], WEEKS[3]])
    with connect(db, read_only=True) as con:
        assert synthetic_weeks(con, WEEKS) == {WEEKS[1], WEEKS[3]}


def test_replay_writes_aggregates_for_every_clean_week(tmp_path):
    db = tmp_path / "w.duckdb"
    reg = _seed(db)
    with connect(db) as con:
        rep = replay_aggregates(con, reg, weeks=len(WEEKS))
        got = [r[0] for r in con.execute(
            "SELECT DISTINCT as_of_date FROM agg_module ORDER BY as_of_date"
        ).fetchall()]
    assert rep["done"] == len(WEEKS)
    assert rep["skipped_synthetic"] == []
    assert got == WEEKS


def test_replay_skips_synthetic_weeks_by_default(tmp_path):
    db = tmp_path / "w.duckdb"
    reg = _seed(db, synthetic_on=[WEEKS[2]])
    with connect(db) as con:
        rep = replay_aggregates(con, reg, weeks=len(WEEKS))
        got = [r[0] for r in con.execute(
            "SELECT DISTINCT as_of_date FROM agg_module ORDER BY as_of_date"
        ).fetchall()]
    assert rep["skipped_synthetic"] == [WEEKS[2].isoformat()]
    assert WEEKS[2] not in got, "synthetic week must never reach agg_module"
    assert rep["done"] == len(WEEKS) - 1


def test_replay_allow_synthetic_is_opt_in(tmp_path):
    db = tmp_path / "w.duckdb"
    reg = _seed(db, synthetic_on=[WEEKS[2]])
    with connect(db) as con:
        rep = replay_aggregates(con, reg, weeks=len(WEEKS), allow_synthetic=True)
        got = [r[0] for r in con.execute(
            "SELECT DISTINCT as_of_date FROM agg_module ORDER BY as_of_date"
        ).fetchall()]
    assert rep["skipped_synthetic"] == []
    assert got == WEEKS


def test_replay_is_idempotent(tmp_path):
    db = tmp_path / "w.duckdb"
    reg = _seed(db)
    with connect(db) as con:
        replay_aggregates(con, reg, weeks=len(WEEKS))
        first = con.execute(
            "SELECT as_of_date, module_id, module_score FROM agg_module ORDER BY 1,2"
        ).fetchall()
        replay_aggregates(con, reg, weeks=len(WEEKS))
        second = con.execute(
            "SELECT as_of_date, module_id, module_score FROM agg_module ORDER BY 1,2"
        ).fetchall()
        n = con.execute("SELECT count(*) FROM agg_module").fetchone()[0]
    assert first == second
    assert n == len(first), "re-running must not duplicate rows"


def test_replay_on_empty_warehouse_reports_nothing_to_do(tmp_path):
    db = tmp_path / "w.duckdb"
    reg = load_registry()
    init_db(reg, db)
    with connect(db) as con:
        rep = replay_aggregates(con, reg, weeks=26)
    assert rep == {"weeks": 0, "done": 0, "skipped_synthetic": [], "failed": []}
