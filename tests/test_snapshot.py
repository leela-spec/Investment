"""Snapshot & report tests (C6 Definition of Done): schema-valid snapshot,
byte-identical on re-run (determinism), and a report that renders with no LLM."""

from __future__ import annotations

import datetime as dt

from ipos.export.report import render_report, write_report
from ipos.export.snapshot import build_snapshot, validate, write_snapshot
from ipos.warehouse.db import connect


def _build(populated_db, as_of):
    db, reg = populated_db
    with connect(db, read_only=True) as con:
        return build_snapshot(con, reg, as_of)


def test_snapshot_schema_valid(populated_db, as_of):
    snap = _build(populated_db, as_of)
    validate(snap)  # raises on invalid
    assert snap["as_of"] == as_of.isoformat()
    assert len(snap["indicators"]) == 22
    assert len(snap["modules"]) == 8
    assert 0 <= snap["overall"]["risk_budget"] <= 100


def test_snapshot_deterministic_bytes(populated_db, as_of, tmp_path):
    snap1 = _build(populated_db, as_of)
    snap2 = _build(populated_db, as_of)
    p1 = write_snapshot(snap1, as_of, tmp_path / "a")
    p2 = write_snapshot(snap2, as_of, tmp_path / "b")
    b1 = open(p1["snapshot"], "rb").read()
    b2 = open(p2["snapshot"], "rb").read()
    assert b1 == b2  # byte-identical
    m1 = open(p1["snapshot_min"], "rb").read()
    m2 = open(p2["snapshot_min"], "rb").read()
    assert m1 == m2


def test_earlier_weeks_synthetic_flag_does_not_taint_this_week(populated_db, as_of):
    # 2026-07-26 regression: a PRIOR week's legitimate --seed-offline run
    # (synthetic-vintage fact_weekly rows) must not permanently flag every
    # later, genuinely real week's snapshot as synthetic too.
    db, reg = populated_db
    with connect(db) as con:
        con.execute(
            "INSERT OR REPLACE INTO fact_weekly "
            "(series_id, as_of_date, value, vintage_id, obs_date, ingested_at) "
            "VALUES ('SPX', ?, 100.0, 'synthetic@SPX@prior-week', ?, ?)",
            [as_of - dt.timedelta(weeks=1), as_of - dt.timedelta(weeks=1), dt.datetime(2026, 1, 1)],
        )
    snap = _build(populated_db, as_of)
    assert snap["flags"]["synthetic_data"] is False


def test_report_renders_without_llm(populated_db, as_of, tmp_path):
    snap = _build(populated_db, as_of)
    md = render_report(snap)
    assert "IPOS Weekly Report" in md
    assert "Risk budget" in md
    # deterministic
    assert render_report(snap) == md
    path = write_report(snap, as_of, tmp_path)
    assert path.endswith("report.md")
