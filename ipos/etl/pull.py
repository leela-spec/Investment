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
from ipos.etl import dbnomics, fred, manual_csv, stooq, ustreasury
from ipos.etl.base import PullResult, run_fallback
from ipos.etl.validators import ValidationError, validate_observations

CONNECTORS = {
    "fred": fred.pull,
    "stooq": stooq.pull,
    "manual_csv": manual_csv.pull,
    "dbnomics": dbnomics.pull,
    "ustreasury": ustreasury.pull,
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
    synthetic: bool = False

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
    synthetic: bool = False,
) -> list[SeriesPullReport]:
    """Pull, validate, and load every active indicator. Idempotent: the
    vintage_id for a given (as_of, series) is stable so re-runs upsert in
    place rather than accumulating rows.

    If ``synthetic=True`` (the --seed-offline demo path), observations are
    generated locally and tagged with a ``synthetic@`` vintage; nothing is
    written to or read from the real archive, so synthetic values can never be
    served as real (WS-A trust fix)."""
    from ipos.etl.fixtures import synthetic_connector  # local import avoids cycle

    conns = connectors if connectors is not None else CONNECTORS
    pd_date = pull_date or as_of
    reports: list[SeriesPullReport] = []

    for entry in registry.active():
        if synthetic:
            df = synthetic_connector(entry)
            result = PullResult(series_id=entry.series_id, df=df,
                                 source_type="synthetic")
        else:
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
        # must produce identical observation rows. Synthetic data carries a
        # 'synthetic@' vintage so it is self-identifying downstream and can
        # never be mistaken for real data.
        prefix = "synthetic@" if synthetic else ""
        vintage_id = f"{prefix}{entry.series_id}@{as_of.isoformat()}"
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
                synthetic=synthetic,
            )
        )
    return reports
