"""FRED connector. Free API key (env FRED_API_KEY), ~120 req/min — weekly
cadence stays far inside all limits. Returns DataFrame[obs_date, value]."""

from __future__ import annotations

import datetime as dt
import os

import pandas as pd
import requests

from ipos.config.models import RegistryEntry, Source

FRED_URL = "https://api.stlouisfed.org/fred/series/observations"
_TIMEOUT = 10


def pull(
    entry: RegistryEntry,
    source: Source,
    start: dt.date | None,
    end: dt.date | None,
) -> pd.DataFrame:
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        raise RuntimeError("FRED_API_KEY not set")

    params = {
        "series_id": source.locator,
        "api_key": api_key,
        "file_type": "json",
    }
    if start:
        params["observation_start"] = start.isoformat()
    if end:
        params["observation_end"] = end.isoformat()

    resp = requests.get(FRED_URL, params=params, timeout=_TIMEOUT)
    resp.raise_for_status()
    payload = resp.json()

    rows = []
    for obs in payload.get("observations", []):
        v = obs.get("value")
        if v in (None, ".", ""):  # FRED marks missing values with "."
            continue
        rows.append({"obs_date": obs["date"], "value": float(v)})
    return pd.DataFrame(rows, columns=["obs_date", "value"])
