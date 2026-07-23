"""Command-line entry points (C8). One idempotent CLI; Windows Task Scheduler
invokes ``ipos-weekly``.

Subcommands: init, pull, score, weekly, doctor, backfill. Each ``cmd_*`` is a
console-script entry point (see pyproject); ``main`` is the ``ipos`` dispatcher.
"""

from __future__ import annotations

import argparse
import datetime as dt
import logging
import os
import sys
from pathlib import Path


def _load_dotenv() -> None:
    """Minimal .env loader (no dependency) — populates os.environ if a .env
    file sits at the repo root and the key is not already set."""
    from ipos.config.load import REPO_ROOT

    env = REPO_ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip())


def _setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def _parse_as_of(s: str | None) -> dt.date | None:
    return dt.date.fromisoformat(s) if s else None


def _common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--as-of", help="Friday week key YYYY-MM-DD (default: last Friday)")
    parser.add_argument("--db", help="path to warehouse.duckdb (default: data/warehouse.duckdb)")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument(
        "--seed-offline", action="store_true",
        help="seed synthetic archive so the pipeline runs with no network (demo/offline)",
    )


# --- entry points -----------------------------------------------------------

def cmd_init(argv: list[str] | None = None) -> int:
    _load_dotenv()
    p = argparse.ArgumentParser(prog="ipos-init", description="Create/upgrade the warehouse and sync dim_series.")
    p.add_argument("--db")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)
    _setup_logging(args.verbose)
    from ipos.config.load import load_registry
    from ipos.warehouse.db import init_db

    report = init_db(load_registry(), args.db)
    print(f"ipos-init: schema={report['schema_version']} "
          f"migrations={report['migrations_applied'] or 'none'} "
          f"dim_series={report['dim_series_synced']}")
    return 0


def cmd_pull(argv: list[str] | None = None) -> int:
    _load_dotenv()
    p = argparse.ArgumentParser(prog="ipos-pull", description="Pull observations into fact_observation.")
    _common(p)
    args = p.parse_args(argv)
    _setup_logging(args.verbose)
    import datetime as _dt

    from ipos.config.load import load_registry
    from ipos.etl.fixtures import seed_archive
    from ipos.etl.pull import pull_all
    from ipos.run import last_friday
    from ipos.warehouse.db import connect, init_db

    reg = load_registry()
    aod = _parse_as_of(args.as_of) or last_friday()
    init_db(reg, args.db)
    if args.seed_offline:
        seed_archive(reg)
    with connect(args.db) as con:
        reports = pull_all(con, reg, as_of=aod, ingested_at=_dt.datetime.now())
    missing = [r.series_id for r in reports if r.missing]
    stale = [r.series_id for r in reports if r.stale and not r.missing]
    print(f"ipos-pull {aod}: {len(reports)} series, "
          f"{sum(r.rows for r in reports)} rows, missing={missing or 'none'}, stale={stale or 'none'}")
    return 0


def cmd_score(argv: list[str] | None = None) -> int:
    _load_dotenv()
    p = argparse.ArgumentParser(prog="ipos-score", description="Canonicalize, compute features, and score.")
    _common(p)
    args = p.parse_args(argv)
    _setup_logging(args.verbose)
    from ipos.aggregate.modules import aggregate
    from ipos.config.load import load_registry
    from ipos.run import last_friday
    from ipos.transforms.run import build_canonical, compute
    from ipos.warehouse.db import connect

    reg = load_registry()
    aod = _parse_as_of(args.as_of) or last_friday()
    with connect(args.db) as con:
        build_canonical(con, aod)
        summ = compute(con, reg, aod)
        agg = aggregate(con, reg, aod)
    print(f"ipos-score {aod}: {summ} risk_budget={agg.get('risk_budget')}")
    return 0


def cmd_weekly(argv: list[str] | None = None) -> int:
    _load_dotenv()
    p = argparse.ArgumentParser(prog="ipos-weekly", description="Full weekly run (pull->score->aggregate->export).")
    _common(p)
    args = p.parse_args(argv)
    _setup_logging(args.verbose)
    from ipos.run import run_weekly

    res = run_weekly(
        as_of=_parse_as_of(args.as_of), db_path=args.db, seed_offline=args.seed_offline
    )
    print(f"ipos-weekly {res.as_of}: status={res.status}")
    if res.status == "FAILED_ATTEMPT":
        print(f"  critical series missing: {res.critical_missing}; last-good snapshot preserved.", file=sys.stderr)
        return 2
    if res.missing:
        print(f"  missing (degraded): {res.missing}")
    if res.stale:
        print(f"  stale (degraded): {res.stale}")
    print(f"  snapshot: {res.paths.get('snapshot')}")
    print(f"  report:   {res.paths.get('report')}")
    return 0


def cmd_doctor(argv: list[str] | None = None) -> int:
    _load_dotenv()
    p = argparse.ArgumentParser(prog="ipos-doctor", description="Health check: config, DB, source freshness.")
    p.add_argument("--db")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)
    _setup_logging(args.verbose)
    from ipos.config.load import load_registry
    from ipos.warehouse.db import DEFAULT_DB_PATH, connect

    reg = load_registry()
    print(f"config: OK — {len(reg.active())} active indicators, {len(reg.modules)} modules")
    print(f"FRED_API_KEY: {'present' if os.environ.get('FRED_API_KEY') else 'MISSING (Phase 1 needs it for live FRED)'}")
    db = Path(args.db) if args.db else DEFAULT_DB_PATH
    if not db.exists():
        print(f"warehouse: MISSING at {db} — run ipos-init")
        return 1
    with connect(db, read_only=True) as con:
        n = con.execute("SELECT count(*) FROM dim_series WHERE enabled").fetchone()[0]
        last = con.execute("SELECT max(as_of_date) FROM agg_regime").fetchone()[0]
    print(f"warehouse: OK — {n} enabled series, last snapshot week: {last or 'none yet'}")
    return 0


def cmd_backfill(argv: list[str] | None = None) -> int:
    _load_dotenv()
    from ipos.backfill import main as backfill_main

    return backfill_main(argv)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    p = argparse.ArgumentParser(prog="ipos", description="Investment Process OS CLI.")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("init", "pull", "score", "weekly", "doctor", "backfill"):
        sub.add_parser(name, add_help=False)
    if not argv:
        p.print_help()
        return 1
    cmd, rest = argv[0], argv[1:]
    dispatch = {
        "init": cmd_init, "pull": cmd_pull, "score": cmd_score,
        "weekly": cmd_weekly, "doctor": cmd_doctor, "backfill": cmd_backfill,
    }
    if cmd not in dispatch:
        p.print_help()
        return 1
    return dispatch[cmd](rest)


if __name__ == "__main__":
    raise SystemExit(main())
