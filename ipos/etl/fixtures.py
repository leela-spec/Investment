"""Deterministic SYNTHETIC seed data for offline runs and tests.

This is NOT real market data. It exists so the walking skeleton can run and be
tested with **no network** (the offline-resilience Definition of Done) and so
tests need no live calls. On a networked machine with a FRED key, the live
connectors archive real pulls with a later ``pull_date`` filename, which the
fallback executor prefers over this seed automatically.

The generator is fully deterministic (fixed per-series seed, no wall-clock),
so a fresh checkout reproduces byte-identical results.
"""

from __future__ import annotations

import datetime as dt
import hashlib

import numpy as np
import pandas as pd

from ipos.config.models import Registry, RegistryEntry
from ipos.etl.base import archive_write

SEED_ANCHOR = dt.date(2026, 7, 17)  # a Friday
WEEKS = 220

# Approximate, plausible July-2026 base levels per series (synthetic).
_BASE: dict[str, float] = {
    "T10Y2Y": 0.45, "T10Y3M": 0.55, "DGS10": 4.30, "NFCI": -0.40,
    "DTWEXBGS": 121.0, "HY_OAS": 3.20, "IG_OAS": 0.90, "VIXCLS": 16.0,
    "WALCL": 6_700_000.0, "UMCSENT": 66.0, "WTI": 76.0, "DFF": 4.33,
    "SPX": 5500.0, "NDX": 19000.0, "RUT": 2200.0, "DAX": 18000.0,
    "GOLD": 2400.0, "COPPER": 4.30, "EURUSD": 1.08, "US10Y_STOOQ": 4.28,
}
# Relative amplitude of the deterministic wobble around the base level.
_AMPL: dict[str, float] = {
    "T10Y2Y": 0.5, "T10Y3M": 0.5, "NFCI": 0.6, "VIXCLS": 0.45,
}


def _seed(series_id: str) -> int:
    return int(hashlib.sha1(series_id.encode()).hexdigest()[:8], 16)


def generate_series(entry: RegistryEntry, weeks: int = WEEKS) -> pd.DataFrame:
    base = _BASE.get(entry.series_id, 100.0)
    ampl = _AMPL.get(entry.series_id, 0.12)  # fraction of base for most series
    rng = np.random.default_rng(_seed(entry.series_id))

    # weekly Fridays back from the anchor
    dates = [SEED_ANCHOR - dt.timedelta(weeks=w) for w in range(weeks)][::-1]

    n = len(dates)
    t = np.arange(n)
    # Mean-reverting, cyclical signal with a per-series phase so different
    # series land at different points in their own range (varied, realistic
    # scores at the anchor). No monotonic drift -> no forced extremes.
    phase = rng.uniform(0.0, 2 * np.pi)
    cycle_long = np.sin(2 * np.pi * t / 104.0 + phase)          # ~2yr
    cycle_short = 0.4 * np.sin(2 * np.pi * t / 26.0 + phase * 1.7)  # ~6mo
    raw = rng.normal(0.0, 1.0, n).cumsum()
    noise = (raw - raw.mean()) / (raw.std() + 1e-9) * 0.5
    signal = 0.7 * cycle_long + cycle_short + noise

    if entry.series_id in _AMPL:  # additive series (spreads / indices near 0)
        values = base + ampl * signal
    else:  # multiplicative wobble for levels
        values = base * (1.0 + ampl * signal)

    df = pd.DataFrame({"obs_date": dates, "value": values})

    if entry.frequency == "M":
        # keep ~monthly cadence for monthly series
        df = df.iloc[::4].reset_index(drop=True)

    df["obs_date"] = pd.to_datetime(df["obs_date"]).dt.date
    df["value"] = df["value"].round(4)
    return df


def seed_archive(registry: Registry, *, pull_date: dt.date = SEED_ANCHOR) -> int:
    """Write synthetic parquet into ``data/archive`` for every active series so
    the offline fallback executor can replay it. Returns count written."""
    n = 0
    for entry in registry.active():
        df = generate_series(entry)
        archive_write(entry.sources[0].type, entry.series_id, df, pull_date)
        n += 1
    return n
