"""Connector protocol, fallback executor, and the append-only raw archive.

Contract (C2):
  * A connector is ``pull(entry, start, end) -> DataFrame[obs_date, value]``.
  * Every successful pull is archived verbatim to
    ``data/archive/{source_type}/{series_id}/{pull_date}.parquet`` **before**
    any transformation — the insurance against FRED windowing / endpoint death.
  * The fallback executor tries each source in the registry chain in order;
    on total live failure it replays the most-recent archived pull and marks
    the result **stale**; if there is no archive either, it returns an empty,
    errored result — never raises past the series level (fail-degraded, C8).

Parquet I/O uses DuckDB natively (no pyarrow dependency).
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import duckdb
import pandas as pd

from ipos.config.load import REPO_ROOT
from ipos.config.models import RegistryEntry, Source

ARCHIVE_ROOT = REPO_ROOT / "data" / "archive"

# A connector: (entry, source, start, end) -> DataFrame[obs_date, value]
Connector = Callable[[RegistryEntry, Source, "dt.date | None", "dt.date | None"], pd.DataFrame]


@dataclass
class PullResult:
    series_id: str
    df: pd.DataFrame            # columns: obs_date (date), value (float)
    source_type: str | None    # which source produced the data
    from_archive: bool = False
    stale: bool = False
    error: str | None = None
    attempts: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.df.empty


# --- archive I/O (DuckDB native parquet) -----------------------------------

def _archive_dir(source_type: str, series_id: str) -> Path:
    return ARCHIVE_ROOT / source_type / series_id


def archive_write(source_type: str, series_id: str, df: pd.DataFrame, pull_date: dt.date) -> Path:
    """Write a verbatim copy of a successful pull. Append-only (one file per
    pull_date); never pruned."""
    d = _archive_dir(source_type, series_id)
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"{pull_date.isoformat()}.parquet"
    out = df.copy()
    out["obs_date"] = pd.to_datetime(out["obs_date"]).dt.date
    con = duckdb.connect(":memory:")
    try:
        con.register("t", out)
        con.execute(f"COPY t TO '{path.as_posix()}' (FORMAT PARQUET)")
    finally:
        con.close()
    return path


def archive_latest(source_type: str, series_id: str) -> pd.DataFrame | None:
    """Return the most-recent archived pull for this series/source, or None."""
    d = _archive_dir(source_type, series_id)
    if not d.exists():
        return None
    files = sorted(d.glob("*.parquet"))
    if not files:
        return None
    latest = files[-1]
    con = duckdb.connect(":memory:")
    try:
        df = con.execute(
            f"SELECT obs_date, value FROM read_parquet('{latest.as_posix()}') ORDER BY obs_date"
        ).df()
    finally:
        con.close()
    df["obs_date"] = pd.to_datetime(df["obs_date"]).dt.date
    return df


# --- fallback executor ------------------------------------------------------

def run_fallback(
    entry: RegistryEntry,
    connectors: dict[str, Connector],
    *,
    start: dt.date | None = None,
    end: dt.date | None = None,
    pull_date: dt.date,
) -> PullResult:
    """Try each source in order; archive on success; on total failure replay
    the latest archive (stale) or return an errored empty result."""
    attempts: list[str] = []
    errors: list[str] = []

    for source in entry.sources:
        connector = connectors.get(source.type)
        if connector is None:
            attempts.append(f"{source.type}:no-connector")
            continue
        try:
            df = connector(entry, source, start, end)
            if df is None or df.empty:
                attempts.append(f"{source.type}:{source.locator}:empty")
                errors.append(f"{source.type} returned no rows")
                continue
            df = _normalize(df)
            archive_write(source.type, entry.series_id, df, pull_date)
            attempts.append(f"{source.type}:{source.locator}:ok")
            return PullResult(
                series_id=entry.series_id, df=df, source_type=source.type,
                attempts=attempts,
            )
        except Exception as exc:  # never raise past the series level
            attempts.append(f"{source.type}:{source.locator}:err")
            errors.append(f"{source.type}: {type(exc).__name__}: {exc}")

    # every live source failed -> replay archive (any source type in the chain)
    for source in entry.sources:
        cached = archive_latest(source.type, entry.series_id)
        if cached is not None and not cached.empty:
            attempts.append(f"{source.type}:archive-replay")
            return PullResult(
                series_id=entry.series_id, df=_normalize(cached),
                source_type=source.type, from_archive=True, stale=True,
                error="; ".join(errors) or None, attempts=attempts,
            )

    return PullResult(
        series_id=entry.series_id, df=_empty(), source_type=None,
        stale=True, error="; ".join(errors) or "no source produced data",
        attempts=attempts,
    )


def _empty() -> pd.DataFrame:
    return pd.DataFrame({"obs_date": pd.Series(dtype="object"), "value": pd.Series(dtype="float64")})


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    out = df[["obs_date", "value"]].copy()
    out["obs_date"] = pd.to_datetime(out["obs_date"]).dt.date
    out["value"] = pd.to_numeric(out["value"], errors="coerce")
    out = out.dropna(subset=["value"]).drop_duplicates(subset=["obs_date"], keep="last")
    out = out.sort_values("obs_date").reset_index(drop=True)
    return out
