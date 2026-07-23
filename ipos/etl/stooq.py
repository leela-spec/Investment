"""Stooq connector — free daily CSV endpoint, no key. Fragile-source policy:
never sole source for a category. Returns DataFrame[obs_date, value] (close)."""

from __future__ import annotations

import datetime as dt
import io

import pandas as pd
import requests

from ipos.config.models import RegistryEntry, Source

STOOQ_URL = "https://stooq.com/q/d/l/"
_TIMEOUT = 10
_HEADERS = {"User-Agent": "Mozilla/5.0 (IPOS weekly macro job)"}


def pull(
    entry: RegistryEntry,
    source: Source,
    start: dt.date | None,
    end: dt.date | None,
) -> pd.DataFrame:
    params = {"s": source.locator, "i": "d"}
    if start:
        params["d1"] = start.strftime("%Y%m%d")
    if end:
        params["d2"] = end.strftime("%Y%m%d")

    resp = requests.get(STOOQ_URL, params=params, headers=_HEADERS, timeout=_TIMEOUT)
    resp.raise_for_status()
    text = resp.text.strip()
    if not text or text.lower().startswith("no data") or "Date" not in text.splitlines()[0]:
        raise RuntimeError(f"stooq returned no usable data for {source.locator}")

    raw = pd.read_csv(io.StringIO(text))
    if "Close" not in raw.columns or "Date" not in raw.columns:
        raise RuntimeError(f"stooq unexpected columns for {source.locator}: {list(raw.columns)}")
    df = raw.rename(columns={"Date": "obs_date", "Close": "value"})[["obs_date", "value"]]
    return df
