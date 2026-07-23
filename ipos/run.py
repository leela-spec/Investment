"""Stage runner for the weekly pipeline, with structured ``run_log`` history
and the fail-safe contract (C8).

Stages: pull -> canonical -> features/scores -> aggregate -> export.
Fail-safe: a missing **critical** series aborts the export so the last-good
snapshot is preserved, and writes a FAILED_ATTEMPT row; missing non-critical
series only degrade (stale flags + lower confidence), the run continues.

``as_of`` resolution reads the wall-clock (last Friday); nothing downstream of
resolution does, preserving determinism for a fixed ``as_of``.
"""

from __future__ import annotations

import datetime as dt
import logging
from dataclasses import dataclass, field
from pathlib import Path

import duckdb

from ipos.aggregate.contradictions import evaluate as evaluate_contradictions
from ipos.aggregate.modules import aggregate
from ipos.config.load import load_registry
from ipos.config.models import Registry
from ipos.etl.fixtures import seed_archive
from ipos.etl.pull import pull_all
from ipos.export.report import write_report
from ipos.export.snapshot import build_snapshot, validate, write_snapshot
from ipos.transforms.run import build_canonical, compute
from ipos.warehouse.db import connect, init_db

log = logging.getLogger("ipos.run")


def last_friday(today: dt.date | None = None) -> dt.date:
    d = today or dt.date.today()
    # weekday(): Mon=0 ... Fri=4
    offset = (d.weekday() - 4) % 7
    return d - dt.timedelta(days=offset)


@dataclass
class RunResult:
    as_of: dt.date
    status: str                      # OK | DEGRADED | FAILED_ATTEMPT
    stages: dict = field(default_factory=dict)
    critical_missing: list[str] = field(default_factory=list)
    stale: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    paths: dict = field(default_factory=dict)


def _log_stage(con, run_id, as_of, stage, status, started, rows_in=None, rows_out=None, detail=None):
    con.execute(
        """
        INSERT OR REPLACE INTO run_log
          (run_id, as_of_date, stage, status, started_at, finished_at, rows_in, rows_out, detail)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [run_id, as_of, stage, status, started, dt.datetime.now(), rows_in, rows_out, detail],
    )


def run_weekly(
    as_of: dt.date | None = None,
    *,
    db_path: Path | str | None = None,
    registry: Registry | None = None,
    connectors: dict | None = None,
    seed_offline: bool = False,
    ingested_at: dt.datetime | None = None,
) -> RunResult:
    reg = registry or load_registry()
    aod = as_of or last_friday()
    run_id = aod.isoformat()
    ingested = ingested_at or dt.datetime.now()

    init_db(reg, db_path)
    if seed_offline:
        seed_archive(reg)

    result = RunResult(as_of=aod, status="OK")

    with connect(db_path) as con:
        # --- stage: pull ---
        t0 = dt.datetime.now()
        reports = pull_all(con, reg, as_of=aod, ingested_at=ingested, connectors=connectors)
        result.stale = sorted(r.series_id for r in reports if r.stale and not r.missing)
        result.missing = sorted(r.series_id for r in reports if r.missing)
        result.critical_missing = sorted(r.series_id for r in reports if r.missing and r.critical)
        result.stages["pull"] = {
            "series": len(reports), "missing": len(result.missing),
            "critical_missing": len(result.critical_missing), "stale": len(result.stale),
        }
        _log_stage(con, run_id, aod, "pull", "OK", t0,
                   rows_out=sum(r.rows for r in reports),
                   detail=f"missing={result.missing} stale={result.stale}")

        # --- FAIL-SAFE: a critical series is missing -> preserve last good ---
        if result.critical_missing:
            _log_stage(con, run_id, aod, "export", "FAILED_ATTEMPT", dt.datetime.now(),
                       detail=f"critical series missing: {result.critical_missing}; "
                              f"last-good snapshot preserved")
            result.status = "FAILED_ATTEMPT"
            log.error("FAILED_ATTEMPT: critical series missing %s", result.critical_missing)
            return result

        # --- stage: canonical + features/scores ---
        t0 = dt.datetime.now()
        nweekly = build_canonical(con, aod)
        _log_stage(con, run_id, aod, "canonical", "OK", t0, rows_out=nweekly)

        t0 = dt.datetime.now()
        summ = compute(con, reg, aod, forced_stale=set(result.stale))
        result.stages["score"] = summ
        _log_stage(con, run_id, aod, "score", "OK", t0, rows_out=summ.get("rows"))

        # --- stage: aggregate ---
        t0 = dt.datetime.now()
        agg = aggregate(con, reg, aod)
        result.stages["aggregate"] = agg
        _log_stage(con, run_id, aod, "aggregate", "OK", t0, rows_out=agg.get("modules"))

        # --- stage: contradictions ---
        t0 = dt.datetime.now()
        hits = evaluate_contradictions(con, aod)
        result.stages["contradictions"] = {
            "n": len(hits), "high": sum(1 for h in hits if h["severity"] == "high"),
        }
        _log_stage(con, run_id, aod, "contradictions", "OK", t0, rows_out=len(hits),
                   detail=f"{[h['id'] for h in hits]}")

        # --- stage: export ---
        t0 = dt.datetime.now()
        snap = build_snapshot(con, reg, aod)
        validate(snap)
        paths = write_snapshot(snap, aod)
        paths["report"] = write_report(snap, aod)
        result.paths = paths
        _log_stage(con, run_id, aod, "export", "OK", t0, detail=str(paths))

    if result.stale or result.missing:
        result.status = "DEGRADED"
    return result
