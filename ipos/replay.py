"""Aggregate-layer replay: recompute ``agg_module`` / ``agg_regime`` for past
weeks from scores already in the warehouse.

Why this exists: ``fact_score`` and ``fact_feature`` carry the full history
(thousands of weeks), but the aggregate layer is only written for the week a
run executes. That left the report with two weeks of module/stance history —
not enough to draw the regime trail, stance sparklines, or module score paths
the report wants. Aggregation is a pure function of stored scores, so the
history is *derivable*: no network, no re-pull, no new observations.

SYNTHETIC SAFETY (the standing question from ``01_DECISION_ANALYSIS.md``):
this is a new code path reading ``fact_weekly``/``fact_score``, so it must not
let ``--seed-offline`` demo data reach real aggregates. ``fact_score`` has no
vintage column — a score computed from a synthetic canonical value is
indistinguishable from a real one — so the check happens one level down, on
``fact_weekly.vintage_id``. Any week with a synthetic canonical row is SKIPPED
by default and reported; ``allow_synthetic=True`` is opt-in and only intended
for offline demos.
"""

from __future__ import annotations

import datetime as dt
import logging

import duckdb

from ipos.config.models import Registry

log = logging.getLogger("ipos.replay")

DEFAULT_WEEKS = 26  # ~6 months: the report's regime-trail window


def recent_scored_weeks(
    con: duckdb.DuckDBPyConnection, weeks: int, *, as_of: dt.date | None = None
) -> list[dt.date]:
    """The most recent ``weeks`` week-keys that have scores, oldest first."""
    latest = as_of or con.execute("SELECT max(as_of_date) FROM fact_score").fetchone()[0]
    if latest is None:
        return []
    rows = con.execute(
        "SELECT DISTINCT as_of_date FROM fact_score WHERE as_of_date <= ? "
        "ORDER BY as_of_date DESC LIMIT ?",
        [latest, weeks],
    ).fetchall()
    return [r[0] for r in rows][::-1]


def synthetic_weeks(
    con: duckdb.DuckDBPyConnection, weeks: list[dt.date]
) -> set[dt.date]:
    """Of ``weeks``, those whose canonical values include a synthetic vintage.
    Aggregating one of these would build a real-looking module score on demo
    data — the bug class this repo has already closed twice."""
    if not weeks:
        return set()
    placeholders = ",".join("?" for _ in weeks)
    rows = con.execute(
        f"SELECT DISTINCT as_of_date FROM fact_weekly "
        f"WHERE as_of_date IN ({placeholders}) AND vintage_id LIKE 'synthetic@%'",
        list(weeks),
    ).fetchall()
    return {r[0] for r in rows}


def replay_aggregates(
    con: duckdb.DuckDBPyConnection,
    registry: Registry,
    *,
    weeks: int = DEFAULT_WEEKS,
    as_of: dt.date | None = None,
    allow_synthetic: bool = False,
) -> dict:
    """Recompute the aggregate layer for the most recent ``weeks`` scored weeks.

    Idempotent: ``aggregate()`` deletes the week's rows before inserting, so
    re-running produces the same state. Returns a small report."""
    from ipos.aggregate.modules import aggregate
    from ipos.aggregate.regime import classify_from_db
    from ipos.run import REGIME_BENCHMARK

    targets = recent_scored_weeks(con, weeks, as_of=as_of)
    if not targets:
        return {"weeks": 0, "done": 0, "skipped_synthetic": [], "failed": []}

    tainted = set() if allow_synthetic else synthetic_weeks(con, targets)
    done, failed = 0, []
    for week in targets:
        if week in tainted:
            log.warning("replay: skipping %s — synthetic canonical rows present", week)
            continue
        try:
            regime = classify_from_db(con, REGIME_BENCHMARK, week)
            aggregate(con, registry, week, regime=regime)
            done += 1
        except Exception as exc:  # one bad week must not abort the rest
            log.warning("replay: %s failed: %s", week, exc)
            failed.append((week.isoformat(), str(exc)))

    return {
        "weeks": len(targets),
        "done": done,
        "first": targets[0].isoformat(),
        "last": targets[-1].isoformat(),
        "skipped_synthetic": sorted(w.isoformat() for w in tainted),
        "failed": failed,
    }
