"""DBnomics connector — keyless aggregator that re-serves FRED / OECD / ECB /
Eurostat / ISM series behind one free API (no account, no key).

This is the highest-leverage keyless source: it lets every FRED-backed
indicator run on a fresh machine with **no FRED key**, keeping the FRED key off
the critical path (Phase-3 de-risk). Locator format is DBnomics' canonical
``provider/dataset/series`` — for FRED series that is ``FRED/<SERIES_ID>``
(DBnomics maps FRED's flat namespace as dataset==series id), e.g.
``FRED/T10Y2Y``.

Archive-everything still applies: DBnomics may re-serve windowed source series
(e.g. ICE BofA OAS), so back up history early all the same.
"""

from __future__ import annotations

import datetime as dt

import pandas as pd
import requests

from ipos.config.models import RegistryEntry, Source

API = "https://api.db.nomics.world/v22/series"
_TIMEOUT = 15
_HEADERS = {"User-Agent": "IPOS weekly macro job (keyless)"}


def pull(
    entry: RegistryEntry,
    source: Source,
    start: dt.date | None,
    end: dt.date | None,
) -> pd.DataFrame:
    # locator: "FRED/T10Y2Y" or full "provider/dataset/series"
    parts = source.locator.split("/")
    if len(parts) == 2:  # provider/series  -> FRED-style flat namespace
        provider, series = parts
        series_ref = f"{provider}/{series}/{series}"
    elif len(parts) == 3:
        series_ref = source.locator
    else:
        raise RuntimeError(f"dbnomics: bad locator {source.locator!r}")

    resp = requests.get(
        API, params={"series_ids": series_ref, "observations": "1"},
        headers=_HEADERS, timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    payload = resp.json()
    docs = payload.get("series", {}).get("docs", [])
    if not docs:
        raise RuntimeError(f"dbnomics: no series for {series_ref}")
    doc = docs[0]
    periods = doc.get("period", [])
    values = doc.get("value", [])

    rows = []
    for period, value in zip(periods, values):
        if value is None or value == "NA":
            continue
        try:
            v = float(value)
        except (TypeError, ValueError):
            continue
        rows.append({"obs_date": period, "value": v})
    df = pd.DataFrame(rows, columns=["obs_date", "value"])
    if end is not None and not df.empty:
        df = df[pd.to_datetime(df["obs_date"]).dt.date <= end]
    return df
