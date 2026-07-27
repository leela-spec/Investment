"""US Treasury daily par-yield curve connector — keyless official source.

The Treasury publishes the daily Treasury par-yield curve rates as a free,
keyless CSV feed (fiscaldata / the XML `pages` feed). This gives the raw tenors
(3m, 2y, 10y, ...) used by the curve indicators and the 10y level — an official
keyless backstop for the FRED rates series (Phase-3 de-risk).

Locator = the Treasury tenor column name, e.g. ``BC_10YEAR`` / ``BC_2YEAR`` /
``BC_3MONTH``. Curve *spreads* (10y-2y) are better sourced from DBnomics'
FRED re-serve; this connector supplies the single tenors.
"""

from __future__ import annotations

import datetime as dt
import io

import pandas as pd
import requests

from ipos.config.models import RegistryEntry, Source

# Keyless CSV of daily par yields, one year per request.
# The bare `/{year}/all` path 404s (verified 2026-07-27) — the query string is
# required. Requesting `all/all` is refused with 403, so the caller must loop
# per year. Columns are quoted tenor labels: Date,"1 Mo",..,"2 Yr",..,"10 Yr",..
CSV_URL = (
    "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/"
    "daily-treasury-rates.csv/{year}/all"
    "?type=daily_treasury_yield_curve&field_tdr_date_value={year}&page&_format=csv"
)
_TIMEOUT = 15
_HEADERS = {"User-Agent": "IPOS weekly macro job (keyless)"}

# map our tenor locators to the CSV column headers
_COL = {
    "BC_3MONTH": "3 Mo",
    "BC_2YEAR": "2 Yr",
    "BC_10YEAR": "10 Yr",
    "BC_30YEAR": "30 Yr",
}


EARLIEST_YEAR = 1990  # Treasury's per-year CSV feed starts here


def _columns(locator: str) -> tuple[str, str | None]:
    """Resolve a locator to (column, minus_column).

    A plain locator is a single tenor (``BC_10YEAR``). A locator of the form
    ``A-B`` is the SPREAD ``A minus B`` (``BC_10YEAR-BC_2YEAR``), computed from
    two columns of the same daily file. Spread support exists because the curve
    indicators T10Y2Y/T10Y3M are `critical` and, since FRED left DBnomics
    (2026-07-27), FRED was their only remaining source — violating the
    no-single-source-for-a-critical-series rule. The Treasury is the same
    underlying data as FRED's series, keyless and official, so it is the
    best available second leg."""
    if "-" in locator:
        a, b = locator.split("-", 1)
        for name in (a, b):
            if name not in _COL:
                raise RuntimeError(f"ustreasury: unknown tenor {name!r} in {locator!r}")
        return _COL[a], _COL[b]
    if locator not in _COL:
        raise RuntimeError(f"ustreasury: unknown tenor {locator!r}")
    return _COL[locator], None


def pull(
    entry: RegistryEntry,
    source: Source,
    start: dt.date | None,
    end: dt.date | None,
) -> pd.DataFrame:
    col, minus_col = _columns(source.locator)
    need = [col] + ([minus_col] if minus_col else [])

    end_year = (end or dt.date.today()).year
    start_year = start.year if start else EARLIEST_YEAR
    frames = []
    for year in range(start_year, end_year + 1):
        resp = requests.get(CSV_URL.format(year=year), headers=_HEADERS, timeout=_TIMEOUT)
        if resp.status_code != 200 or not resp.text.strip():
            continue
        raw = pd.read_csv(io.StringIO(resp.text))
        if "Date" not in raw.columns or not all(c in raw.columns for c in need):
            continue
        part = raw[["Date"] + need].rename(columns={"Date": "obs_date"})
        if minus_col:
            # a spread is only defined where BOTH tenors printed that day
            part = part.dropna(subset=need)
            part["value"] = part[col].astype(float) - part[minus_col].astype(float)
        else:
            part = part.rename(columns={col: "value"})
        frames.append(part[["obs_date", "value"]])
    if not frames:
        raise RuntimeError(f"ustreasury: no data for {source.locator}")
    df = pd.concat(frames, ignore_index=True)
    df["obs_date"] = pd.to_datetime(df["obs_date"]).dt.date
    return df.dropna(subset=["value"])[["obs_date", "value"]]
