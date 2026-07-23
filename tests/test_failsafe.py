"""Fail-safe tests (C8 Definition of Done): a missing critical series aborts
the export so the last-good snapshot is preserved and a FAILED_ATTEMPT row is
written; a healthy run produces OK; missing non-critical series only degrade.
No live network calls — connectors are fakes."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import pytest

import ipos.etl.base as etl_base
import ipos.export.report as report_mod
import ipos.export.snapshot as snap_mod
from ipos.config.load import load_registry
from ipos.etl.fixtures import SEED_ANCHOR, generate_series
from ipos.run import run_weekly
from ipos.warehouse.db import connect

AS_OF = SEED_ANCHOR


def _fake_ok(entry, source, start, end):
    return generate_series(entry)


def _fake_dead(entry, source, start, end):
    raise ConnectionError("offline")


@pytest.fixture
def env(tmp_path, monkeypatch):
    exports = tmp_path / "exports"
    monkeypatch.setattr(snap_mod, "EXPORTS_DIR", exports)
    monkeypatch.setattr(report_mod, "EXPORTS_DIR", exports)
    reg = load_registry()
    db = tmp_path / "w.duckdb"
    return tmp_path, db, reg, exports


def test_healthy_run_is_ok(env, monkeypatch):
    tmp, db, reg, exports = env
    monkeypatch.setattr(etl_base, "ARCHIVE_ROOT", tmp / "archiveA")
    conns = {"fred": _fake_ok, "stooq": _fake_ok, "manual_csv": _fake_ok}
    res = run_weekly(as_of=AS_OF, db_path=db, registry=reg, connectors=conns,
                     ingested_at=dt.datetime(2026, 7, 18, 8, 0, 0))
    assert res.status == "OK"
    assert not res.missing and not res.stale
    snap = exports / AS_OF.isoformat() / "snapshot.json"
    assert snap.exists()


def test_critical_missing_preserves_last_good(env, monkeypatch):
    tmp, db, reg, exports = env
    # --- run 1: healthy, writes last-good snapshot ---
    monkeypatch.setattr(etl_base, "ARCHIVE_ROOT", tmp / "archiveA")
    conns_ok = {"fred": _fake_ok, "stooq": _fake_ok, "manual_csv": _fake_ok}
    run_weekly(as_of=AS_OF, db_path=db, registry=reg, connectors=conns_ok,
               ingested_at=dt.datetime(2026, 7, 18, 8, 0, 0))
    snap_path = exports / AS_OF.isoformat() / "snapshot.json"
    good_bytes = snap_path.read_bytes()

    # --- run 2: everything dead, EMPTY archive -> critical series missing ---
    monkeypatch.setattr(etl_base, "ARCHIVE_ROOT", tmp / "archiveB_empty")
    conns_dead = {"fred": _fake_dead, "stooq": _fake_dead, "manual_csv": _fake_dead}
    res = run_weekly(as_of=AS_OF, db_path=db, registry=reg, connectors=conns_dead,
                     ingested_at=dt.datetime(2026, 7, 18, 8, 0, 0))

    assert res.status == "FAILED_ATTEMPT"
    assert res.critical_missing  # at least one critical series missing
    # last-good snapshot preserved byte-for-byte
    assert snap_path.read_bytes() == good_bytes
    # FAILED_ATTEMPT recorded in run_log
    with connect(db, read_only=True) as con:
        rows = con.execute(
            "SELECT status FROM run_log WHERE stage = 'export' AND as_of_date = ?",
            [AS_OF],
        ).fetchall()
    assert ("FAILED_ATTEMPT",) in rows


def test_offline_seeded_run_is_degraded_not_crash(env, monkeypatch):
    # the real DoD offline path: seed archive, no connectors reach live -> the
    # run degrades (stale flags) but still produces a valid snapshot.
    tmp, db, reg, exports = env
    monkeypatch.setattr(etl_base, "ARCHIVE_ROOT", tmp / "archiveC")
    conns_dead = {"fred": _fake_dead, "stooq": _fake_dead, "manual_csv": _fake_dead}
    res = run_weekly(as_of=AS_OF, db_path=db, registry=reg, connectors=conns_dead,
                     seed_offline=True, ingested_at=dt.datetime(2026, 7, 18, 8, 0, 0))
    assert res.status == "DEGRADED"
    assert len(res.stale) == 20 and not res.missing
    assert (exports / AS_OF.isoformat() / "snapshot.json").exists()
