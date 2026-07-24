"""WS-B: OHLC capture + real-ATR regime. Verifies migration 003 creates
fact_ohlc, the OHLC pull populates it, and the regime classifier uses real
weekly true-range when OHLC is present (falling back to close-only otherwise)."""

from __future__ import annotations

import datetime as dt

import pandas as pd

from ipos.aggregate.regime import _features, classify_from_db, classify_history
from ipos.config.load import load_registry
from ipos.etl.pull import pull_ohlc
from ipos.warehouse.db import connect, init_db


def test_migration_creates_fact_ohlc(tmp_path):
    reg = load_registry()
    db = tmp_path / "w.duckdb"
    init_db(reg, db)
    with connect(db, read_only=True) as con:
        cols = {r[1] for r in con.execute("PRAGMA table_info('fact_ohlc')").fetchall()}
    assert {"series_id", "obs_date", "high", "low", "close", "vintage_id"} <= cols


def test_features_use_ohlc_when_present():
    # a bar series where intra-week range accelerates but closes barely move ->
    # close-only speed is flat, but real ATR acceleration is detectable.
    n = 30
    closes = [100.0 + 0.1 * i for i in range(n)]
    highs = [c + (1 if i < n - 5 else 8) for i, c in enumerate(closes)]  # range blows out late
    lows = [c - (1 if i < n - 5 else 8) for i, c in enumerate(closes)]
    f_close = _features(pd.Series(closes).to_numpy())
    import numpy as np
    f_ohlc = _features(np.array(closes), np.array(highs), np.array(lows))
    assert f_close["atr_source"] == "close"
    assert f_ohlc["atr_source"] == "ohlc"
    assert f_ohlc["range_overlap"] is not None
    # real ATR acceleration picks up the late range expansion
    assert f_ohlc["atr_change_rate"] > f_close["atr_change_rate"]


def test_ohlc_pull_populates_and_regime_uses_it(tmp_path):
    reg = load_registry()
    db = tmp_path / "w.duckdb"
    init_db(reg, db)

    # fake stooq OHLC connector: a clean uptrend with real ranges
    def fake_ohlc(entry, source, start, end):
        rows = []
        base = dt.date(2026, 1, 2)
        for i in range(160):
            d = base + dt.timedelta(days=i * 2)
            if d > end:
                break
            c = 100 + 1.5 * i
            rows.append({"obs_date": d, "open": c - 1, "high": c + 2, "low": c - 2, "close": c})
        return pd.DataFrame(rows)

    with connect(db) as con:
        n = pull_ohlc(con, reg, ["SPX"], as_of=dt.date(2026, 7, 17),
                      ingested_at=dt.datetime(2026, 7, 18),
                      connectors={"stooq_ohlc": fake_ohlc})
        assert n.get("SPX", 0) > 0
        res = classify_from_db(con, "SPX", dt.date(2026, 7, 17))
    # real OHLC path was used and a clean uptrend is not called CHOPPY
    assert res.features.get("atr_source") == "ohlc"
    assert res.label in ("TRENDY", "MOMENTUM")


def test_close_only_still_works():
    r = classify_history([100 + 2.0 * i for i in range(40)])
    assert r.label in ("TRENDY", "MOMENTUM", "UNCERTAIN")
    assert r.features["atr_source"] == "close"
