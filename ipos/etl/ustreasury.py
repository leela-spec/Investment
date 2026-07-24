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

# keyless CSV of daily par yields by year
CSV_URL = (
    "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/"
    "daily-treasury-rates.csv/{year}/all"
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


def pull(
    entry: RegistryEntry,
    source: Source,
    start: dt.date | None,
    end: dt.date | None,
) -> pd.DataFrame:
    col = _COL.get(source.locator)
    if col is None:
        raise RuntimeError(f"ustreasury: unknown tenor {source.locator!r}")

    end_year = (end or dt.date.today()).year
    start_year = start.year if start else end_year - 4
    frames = []
    for year in range(start_year, end_year + 1):
        resp = requests.get(CSV_URL.format(year=year), headers=_HEADERS, timeout=_TIMEOUT)
        if resp.status_code != 200 or not resp.text.strip():
            continue
        raw = pd.read_csv(io.StringIO(resp.text))
        if "Date" not in raw.columns or col not in raw.columns:
            continue
        frames.append(raw[["Date", col]].rename(columns={"Date": "obs_date", col: "value"}))
    if not frames:
        raise RuntimeError(f"ustreasury: no data for {source.locator}")
    df = pd.concat(frames, ignore_index=True)
    df["obs_date"] = pd.to_datetime(df["obs_date"]).dt.date
    return df[["obs_date", "value"]]
