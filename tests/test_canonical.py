"""Canonical-weekly transform tests: the ASOF join's same-obs_date tie-break
must never let a synthetic vintage outrank a real one (2026-07-26 regression
-- a live pull landing on a date a prior --seed-offline run had already
seeded synthetically was silently served as real, because the vintage-id
string tie-break ranked "synthetic@..." above the real series-id-prefixed
vintage)."""

from __future__ import annotations

import datetime as dt

from ipos.config.load import load_registry
from ipos.transforms.run import build_canonical
from ipos.warehouse.db import connect, init_db


def test_real_observation_wins_tie_over_synthetic_same_date(tmp_path):
    reg = load_registry()
    db = tmp_path / "w.duckdb"
    init_db(reg, db)
    obs_date = dt.date(2026, 7, 17)
    as_of = dt.date(2026, 7, 24)

    with connect(db) as con:
        # synthetic row seeded in an earlier session, then a real live pull
        # later lands on the exact same calendar obs_date.
        con.execute(
            "INSERT INTO fact_observation "
            "(series_id, obs_date, value, vintage_id, ingested_at, source_hash) VALUES "
            "('DTWEXBGS', ?, 132.0054, 'synthetic@DTWEXBGS@2026-07-17', ?, 'h1'), "
            "('DTWEXBGS', ?, 120.5315, 'DTWEXBGS@2026-07-24', ?, 'h2')",
            [obs_date, dt.datetime(2026, 7, 17, 8), obs_date, dt.datetime(2026, 7, 24, 8)],
        )
        build_canonical(con, as_of)
        row = con.execute(
            "SELECT value, vintage_id FROM fact_weekly "
            "WHERE series_id = 'DTWEXBGS' AND as_of_date = ?",
            [as_of],
        ).fetchone()

    assert row[1] == "DTWEXBGS@2026-07-24"  # the real vintage, not the synthetic one
    assert row[0] == 120.5315


def test_real_run_ignores_synthetic_even_when_synthetic_date_is_later(tmp_path):
    """UMCSENT-shaped case: the synthetic seed fabricates a LATER obs_date than
    any real observation published so far. A real run must still never surface
    it -- the ASOF 'most recent date' rule alone would otherwise pick the
    fabricated point over the real-but-older one."""
    reg = load_registry()
    db = tmp_path / "w.duckdb"
    init_db(reg, db)
    as_of = dt.date(2026, 7, 24)

    with connect(db) as con:
        con.execute(
            "INSERT INTO fact_observation "
            "(series_id, obs_date, value, vintage_id, ingested_at, source_hash) VALUES "
            "('UMCSENT', '2026-05-01', 44.8, 'UMCSENT@2026-07-24', ?, 'h1'), "
            "('UMCSENT', '2026-06-26', 64.872, 'synthetic@UMCSENT@2026-07-17', ?, 'h2')",
            [dt.datetime(2026, 7, 24, 8), dt.datetime(2026, 7, 17, 8)],
        )
        build_canonical(con, as_of, synthetic=False)
        row = con.execute(
            "SELECT value, vintage_id, obs_date FROM fact_weekly "
            "WHERE series_id = 'UMCSENT' AND as_of_date = ?",
            [as_of],
        ).fetchone()

    assert row[1] == "UMCSENT@2026-07-24"
    assert row[0] == 44.8
    assert row[2] == dt.date(2026, 5, 1)
