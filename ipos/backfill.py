"""Backfill core: pull the MAXIMUM available history for every registry series
from live sources and archive it — the rank-2 insurance against irreversible
data loss (FRED truncated ICE BofA OAS to a rolling 3-year window in Apr 2026,
so every week of delay permanently loses a week of OAS history).

RUN THIS EARLY on a networked machine with a FRED key. It only needs the live
connectors + the archive writer; it does not touch the warehouse.

In an environment with no network to data hosts (e.g. this sandbox) the live
pulls fail and the function reports which series could not be reached — it does
not fabricate data.
"""

from __future__ import annotations

import argparse
import datetime as dt

from ipos.config.load import load_registry
from ipos.etl.base import run_fallback
from ipos.etl.pull import CONNECTORS


def backfill(*, pull_date: dt.date | None = None, only: list[str] | None = None) -> dict:
    reg = load_registry()
    pd_date = pull_date or dt.date.today()
    ok, failed = [], []
    for entry in reg.active():
        if only and entry.series_id not in only:
            continue
        # start=None => connectors request full available history
        res = run_fallback(entry, CONNECTORS, start=None, end=None, pull_date=pd_date)
        if res.ok and not res.from_archive:
            ok.append((entry.series_id, len(res.df)))
        else:
            failed.append((entry.series_id, res.error or "no live data"))
    return {"ok": ok, "failed": failed, "pull_date": pd_date.isoformat()}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="ipos-backfill",
        description="Archive maximum available history for all registry series (run early!).",
    )
    p.add_argument("--only", nargs="*", help="limit to specific series_ids")
    p.add_argument("--pull-date", help="stamp for the archive filename (YYYY-MM-DD)")
    args = p.parse_args(argv)
    pull_date = dt.date.fromisoformat(args.pull_date) if args.pull_date else None

    report = backfill(pull_date=pull_date, only=args.only)
    print(f"ipos-backfill (pull_date={report['pull_date']}):")
    for sid, n in report["ok"]:
        print(f"  OK      {sid}: {n} rows archived")
    for sid, err in report["failed"]:
        print(f"  FAILED  {sid}: {err}")
    print(f"  -> {len(report['ok'])} archived, {len(report['failed'])} unreachable")
    # non-zero exit if the critical OAS series could not be archived live
    critical_oas = {"HY_OAS", "IG_OAS"}
    failed_ids = {sid for sid, _ in report["failed"]}
    return 1 if (critical_oas & failed_ids) else 0


if __name__ == "__main__":
    raise SystemExit(main())
