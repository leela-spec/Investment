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
_TIMEOUT = 10
_HEADERS = {"User-Agent": "Mozilla/5.0 (IPOS weekly macro job)"}


def _fetch(locator: str, start: dt.date | None, end: dt.date | None) -> dict:
    params = {"interval": "1d"}
    if start:
        params["period1"] = str(int(dt.datetime.combine(start, dt.time.min, dt.timezone.utc).timestamp()))
        params["period2"] = str(int(dt.datetime.combine(
            end or dt.date.today(), dt.time.max, dt.timezone.utc).timestamp()))
    else:
        params["range"] = "5y"
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
