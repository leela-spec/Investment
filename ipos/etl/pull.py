"""Pull orchestration: run the fallback executor for every active indicator,
validate, and upsert into ``fact_observation``. Returns a per-series report
used by the run stage runner (staleness feeds confidence + fail-safe).
"""

from __future__ import annotations

import datetime as dt
import hashlib
from dataclasses import dataclass

import duckdb
import pandas as pd

from ipos.config.models import RegistryEntry, Registry
from ipos.etl import fred, manual_csv, stooq
from ipos.etl.base import PullResult, run_fallback
from ipos.etl.validators import ValidationError, validate_observations

CONNECTORS = {
    "fred": fred.pull,
    "stooq": stooq.pull,
    "manual_csv": manual_csv.pull,
}


@dataclass
class SeriesPullReport:
    series_id: str
    critical: bool
    rows: int
    source_type: str | None
    from_archive: bool
    stale: bool
    error: str | None
    warnings: list[str]

    @property
    def missing(self) -> bool:
        return self.rows == 0


def _row_hash(series_id: str, obs_date: dt.date, value: float) -> str:
    return hashlib.sha1(f"{series_id}|{obs_date}|{value}".encode()).hexdigest()[:16]


def upsert_observations(
    con: duckdb.DuckDBPyConnection,
    entry: RegistryEntry,
    result: PullResult,
    ingested_at: dt.datetime,
    vintage_id: str,
) -> int:
    if result.df.empty:
        return 0
    df = result.df.copy()
    df["series_id"] = entry.series_id
    df["value"] = df["value"].astype(float)
    df["vintage_id"] = vintage_id
    df["ingested_at"] = ingested_at
    df["source_hash"] = [
        _row_hash(entry.series_id, od, v) for od, v in zip(df["obs_date"], df["value"])
    ]
    # bulk insert via a registered frame (row-by-row executemany is slow in DuckDB)
    con.register("obs_df", df)
    con.execute(
        """
        INSERT OR REPLACE INTO fact_observation
          (series_id, obs_date, value, vintage_id, ingested_at, source_hash)
        SELECT series_id, obs_date::DATE, value, vintage_id, ingested_at, source_hash
        FROM obs_df
        """
    )
    con.unregister("obs_df")
    return len(df)


def pull_all(
    con: duckdb.DuckDBPyConnection,
    registry: Registry,
    *,
    as_of: dt.date,
    ingested_at: dt.datetime,
    pull_date: dt.date | None = None,
    connectors: dict | None = None,
) -> list[SeriesPullReport]:
    """Pull, validate, and load every active indicator. Idempotent: the
    vintage_id for a given (as_of, series) is stable so re-runs upsert in
    place rather than accumulating rows."""
    conns = connectors if connectors is not None else CONNECTORS
    pd_date = pull_date or as_of
    reports: list[SeriesPullReport] = []

    for entry in registry.active():
        result = run_fallback(
            entry, conns, start=None, end=as_of, pull_date=pd_date
        )
        warnings: list[str] = []
        if result.ok:
            try:
                warnings = validate_observations(entry, result.df)
            except ValidationError as exc:
                # treat a validation failure like a missing pull (fail-degraded)
                result = PullResult(
                    series_id=entry.series_id, df=result.df.iloc[0:0],
                    source_type=result.source_type, stale=True,
                    error=f"validation: {exc}", attempts=result.attempts,
                )

        # deterministic vintage: archive-replays and re-runs of the same week
        # must produce identical observation rows.
        vintage_id = f"{entry.series_id}@{as_of.isoformat()}"
        n = upsert_observations(con, entry, result, ingested_at, vintage_id)

        reports.append(
            SeriesPullReport(
                series_id=entry.series_id,
                critical=entry.critical,
                rows=n,
                source_type=result.source_type,
                from_archive=result.from_archive,
                stale=result.stale,
                error=result.error,
                warnings=warnings,
            )
        )
    return reports
