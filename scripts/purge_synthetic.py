#!/usr/bin/env python
"""Remove synthetic (--seed-offline demo) data from a REAL warehouse and
rebuild everything derived from it.

Why this exists
---------------
A ``--seed-offline`` demo run against the real warehouse writes
``synthetic@...``-vintage rows into ``fact_observation``. The canonical join
ignores them on a real run (fixed 2026-07-26), so for a series that also has
real history they are inert. But for a series whose real history does NOT
cover those dates -- ``HY_OAS`` / ``IG_OAS``, where FRED serves only a rolling
3-year window -- the synthetic value was the only candidate and won by default.
Those weeks then produced ``fact_score`` rows, and ``fact_score`` carries no
vintage, so a score computed from invented data is indistinguishable from a
real one (the third instance of this bug class; see
``05_blueprint/01_DECISION_ANALYSIS.md``, amendment 2026-07-27).

Worse than the individual weeks: scoring is a *rolling percentile / z-score*
over ~156 weeks, so every week whose lookback window overlaps the synthetic
span inherits some of it. Deleting the rows is therefore not enough -- features
and scores must be recomputed across the affected history.

Before deleting, confirm the real data is genuinely unobtainable. As of
2026-07-27 for HY_OAS/IG_OAS it is: FRED returns nothing before 2023-07-28,
and the configured DBnomics fallback (``FRED/BAMLH0A0HYM2``) no longer exists
upstream. An honest gap is correct; an invented value is not.

Usage
-----
    python scripts/purge_synthetic.py            # dry run: report only
    python scripts/purge_synthetic.py --apply    # back up, purge, rebuild
"""

from __future__ import annotations

import argparse
import datetime as dt
import shutil
import sys
from pathlib import Path

from ipos.config.load import load_registry
from ipos.replay import replay_aggregates
from ipos.transforms.run import build_canonical, compute
from ipos.warehouse.db import DEFAULT_DB_PATH, connect

SYNTHETIC_LIKE = "synthetic@%"


def _report(con) -> dict:
    obs = con.execute(
        "SELECT count(*) FROM fact_observation WHERE vintage_id LIKE ?", [SYNTHETIC_LIKE]
    ).fetchone()[0]
    wk = con.execute(
        "SELECT count(*) FROM fact_weekly WHERE vintage_id LIKE ?", [SYNTHETIC_LIKE]
    ).fetchone()[0]
    per_series = con.execute(
        "SELECT series_id, count(*), min(as_of_date), max(as_of_date) FROM fact_weekly "
        "WHERE vintage_id LIKE ? GROUP BY 1 ORDER BY 1", [SYNTHETIC_LIKE]
    ).fetchall()
    return {"observations": obs, "weekly": wk, "weekly_per_series": per_series}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--apply", action="store_true",
                   help="actually purge and rebuild (default: dry run)")
    p.add_argument("--db", help="warehouse path (default: data/warehouse.duckdb)")
    p.add_argument("--as-of", help="week key to rebuild up to (default: warehouse max)")
    p.add_argument("--replay-weeks", type=int, default=26,
                   help="aggregate weeks to replay after the rebuild (default: 26)")
    args = p.parse_args(argv)

    db = Path(args.db) if args.db else DEFAULT_DB_PATH
    if not db.exists():
        print(f"no warehouse at {db}", file=sys.stderr)
        return 1

    reg = load_registry()
    with connect(db, read_only=True) as con:
        before = _report(con)
        max_week = con.execute("SELECT max(as_of_date) FROM fact_weekly").fetchone()[0]
    as_of = dt.date.fromisoformat(args.as_of) if args.as_of else max_week

    print(f"warehouse: {db}")
    print(f"synthetic rows found: {before['observations']} observation(s), "
          f"{before['weekly']} canonical week(s)")
    for sid, n, lo, hi in before["weekly_per_series"]:
        print(f"  canonical: {sid}  {n} weeks  {lo} .. {hi}  <- fed scoring")
    if not before["observations"] and not before["weekly"]:
        print("nothing to purge — warehouse is clean")
        return 0
    if not args.apply:
        print("\nDRY RUN — nothing changed. Re-run with --apply to:")
        print("  1. back up the warehouse alongside itself")
        print("  2. delete every synthetic-vintage row from fact_observation/fact_weekly")
        print(f"  3. rebuild canonical + features + scores up to {as_of} from real data only")
        print(f"  4. replay the last {args.replay_weeks} weeks of aggregates")
        return 0

    stamp = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    backup = db.with_name(f"{db.stem}.pre-purge-{stamp}{db.suffix}")
    shutil.copy2(db, backup)
    print(f"\nbackup written: {backup}")

    with connect(db) as con:
        n_obs = con.execute(
            "SELECT count(*) FROM fact_observation WHERE vintage_id LIKE ?", [SYNTHETIC_LIKE]
        ).fetchone()[0]
        con.execute("DELETE FROM fact_observation WHERE vintage_id LIKE ?", [SYNTHETIC_LIKE])
        con.execute("DELETE FROM fact_weekly WHERE vintage_id LIKE ?", [SYNTHETIC_LIKE])
        print(f"deleted {n_obs} synthetic observation rows + "
              f"{before['weekly']} synthetic canonical rows")

        # Rebuild from real data only. Both calls span the FULL history, which is
        # required: a rolling-window score is wrong for every week whose lookback
        # touched the synthetic span, not just the synthetic weeks themselves.
        print(f"rebuilding canonical up to {as_of} ...")
        n_weekly = build_canonical(con, as_of)          # synthetic=False by default
        print(f"  fact_weekly rows <= as_of: {n_weekly}")
        print("recomputing features + scores over the full history ...")
        summ = compute(con, reg, as_of)
        print(f"  {summ}")
        print(f"replaying {args.replay_weeks} weeks of aggregates ...")
        rep = replay_aggregates(con, reg, weeks=args.replay_weeks, as_of=as_of)
        print(f"  rebuilt {rep['done']}/{rep['weeks']} weeks "
              f"({rep.get('first')} .. {rep.get('last')})")

        after = _report(con)
        left = con.execute(
            "SELECT count(*) FROM fact_weekly WHERE vintage_id LIKE ?", [SYNTHETIC_LIKE]
        ).fetchone()[0]

    print(f"\nsynthetic rows remaining: {after['observations']} observations, {left} canonical")
    print("NOTE: HY_OAS/IG_OAS now have a genuine gap before 2023-07-25 — that is "
          "correct. FRED no longer serves that window and no configured fallback has it.")
    print(f"rollback if needed: copy {backup.name} back over {db.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
