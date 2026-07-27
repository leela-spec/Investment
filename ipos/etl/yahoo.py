"""Yahoo Finance connector — free public chart JSON endpoint, no key.

Added 2026-07-26 (see 01_DECISION_ANALYSIS.md amendment) as a SECOND leg
behind Stooq for the equity/FX/commodity series that had zero fallback.
Unofficial/undocumented endpoint (not a supported API surface, unlike FRED or
DBnomics) — never the sole source for a series; if it also breaks, the
fallback chain still degrades to archive-replay or a stale flag, never a
crash. Returns DataFrame[obs_date, value] (close)."""

from __future__ import annotations

import datetime as dt

import pandas as pd
import requests

from ipos.config.models import RegistryEntry, Source

CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
_TIMEOUT = 30  # a 40-year daily pull is a bigger payload than a 5-year one
_HEADERS = {"User-Agent": "Mozilla/5.0 (IPOS weekly macro job)"}

# Earliest date we ever ask for when the caller wants "all available history"
# (start=None, i.e. ipos-backfill and the weekly pull). Yahoo simply starts at
# whenever the symbol begins, so this is a floor, not a claim about coverage.
# It is the Unix epoch for a hard technical reason, not taste: the endpoint
# takes period1 as a Unix timestamp, and pre-1970 dates are negative, which
# Windows cannot convert back (`OSError: [Errno 22]` — verified 2026-07-27).
# Symbols whose history predates 1970 (e.g. ^GSPC reaches 1927) are therefore
# capped here; 56 years still dwarfs the 156-week scoring window.
MAX_HISTORY_START = dt.date(1970, 1, 1)


def _fetch(locator: str, start: dt.date | None, end: dt.date | None) -> dict:
    """Always request an EXPLICIT period1/period2 window — never `range=max`.

    This matters more than it looks: `range=max` with `interval=1d` silently
    returns QUARTERLY bars (verified 2026-07-27: ^GSPC gave 168 rows spanning
    41 years, median gap 91 days). An explicit period1/period2 over the same
    span returns true daily data (10,469 rows). Requesting `range=max` would
    therefore have swapped 5 years of daily history for 168 quarterly points
    and quietly wrecked every weekly canonical value.

    The previous default of `range="5y"` was the *only* reason the eight market
    series were capped at 5 years of history — the sources were never the limit.
    """
    params = {"interval": "1d"}
    period_start = start or MAX_HISTORY_START
    params["period1"] = str(int(dt.datetime.combine(
        period_start, dt.time.min, dt.timezone.utc).timestamp()))
    params["period2"] = str(int(dt.datetime.combine(
        end or dt.date.today(), dt.time.max, dt.timezone.utc).timestamp()))
    resp = requests.get(CHART_URL.format(symbol=locator), params=params,
                         headers=_HEADERS, timeout=_TIMEOUT)
    resp.raise_for_status()
    payload = resp.json()
    result = ((payload.get("chart") or {}).get("result")) or []
    if not result:
        raise RuntimeError(f"yahoo: no chart result for {locator}")
    return result[0]


def _quote(result: dict) -> dict:
    quotes = (result.get("indicators") or {}).get("quote") or [{}]
    return quotes[0]


def pull(
    entry: RegistryEntry,
    source: Source,
    start: dt.date | None,
    end: dt.date | None,
) -> pd.DataFrame:
    result = _fetch(source.locator, start, end)
    ts = result.get("timestamp") or []
    closes = _quote(result).get("close") or []
    rows = [
        {"obs_date": dt.datetime.fromtimestamp(t, dt.timezone.utc).date(), "value": float(c)}
        for t, c in zip(ts, closes) if c is not None
    ]
    if not rows:
        raise RuntimeError(f"yahoo returned no usable data for {source.locator}")
    return pd.DataFrame(rows)


def pull_ohlc(
    entry: RegistryEntry,
    source: Source,
    start: dt.date | None,
    end: dt.date | None,
) -> pd.DataFrame:
    """Full daily OHLC bars for the regime governor, mirroring stooq.pull_ohlc."""
    result = _fetch(source.locator, start, end)
    ts = result.get("timestamp") or []
    q = _quote(result)
    opens, highs = q.get("open") or [], q.get("high") or []
    lows, closes = q.get("low") or [], q.get("close") or []
    rows = []
    for t, o, h, lo, c in zip(ts, opens, highs, lows, closes):
        if None in (o, h, lo, c):
            continue
        rows.append({
            "obs_date": dt.datetime.fromtimestamp(t, dt.timezone.utc).date(),
            "open": o, "high": h, "low": lo, "close": c,
        })
    if not rows:
        raise RuntimeError(f"yahoo returned no usable OHLC for {source.locator}")
    return pd.DataFrame(rows)
