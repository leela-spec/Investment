"""Shared builder for the deterministic golden snapshot (C9 regression harness).

Both the regeneration script (`scripts/update_golden.py`) and the regression
test (`tests/test_golden.py`) call ``build_golden_min`` so they exercise the
*identical* code path — the test can never drift from how the golden was made.

The golden is built from the deterministic synthetic fixtures (no network, no
key), so it is a pure logic-regression guard: it fails only when scoring,
aggregation, contradictions, or snapshot *code* changes the output — exactly
what should force an intentional `scoring_version` bump + golden refresh.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import ipos.aggregate.portfolio as portfolio_mod
import ipos.ai.bundle as bundle_mod
import ipos.etl.base as etl_base
import ipos.etl.portfolio_csv as portfolio_csv
import ipos.export.report as report_mod
import ipos.export.snapshot as snap_mod
import ipos.report.html as html_mod
from ipos.etl.fixtures import SEED_ANCHOR, generate_series
from ipos.run import run_weekly

GOLDEN_PATH = Path(__file__).resolve().parents[1] / "tests" / "golden" / "snapshot_2026-07-17.min.json"


def _fixture_connector(entry, source, start, end):
    return generate_series(entry)


FIXTURE_CONNECTORS = {
    "fred": _fixture_connector,
    "stooq": _fixture_connector,
    "manual_csv": _fixture_connector,
}


def build_golden_min(workdir: Path, as_of: dt.date = SEED_ANCHOR) -> str:
    """Run the full offline pipeline into an isolated workdir and return the
    minified snapshot JSON as text."""
    # isolate all on-disk side effects inside workdir
    etl_base.ARCHIVE_ROOT = workdir / "archive"
    # Every module with its own `EXPORTS_DIR` binding, `ipos.report.html`
    # included — it was missing here until 2026-07-29, so building the golden
    # overwrote the operator's real latest.html/report.html with fixture output.
    snap_mod.EXPORTS_DIR = workdir / "exports"
    report_mod.EXPORTS_DIR = workdir / "exports"
    bundle_mod.EXPORTS_DIR = workdir / "exports"
    html_mod.EXPORTS_DIR = workdir / "exports"
    # ...INCLUDING the operator's portfolio. Without this the golden picks up
    # whatever sits in the real data/inbox/, which would make it
    # machine-dependent AND commit holdings-derived contradictions into the
    # tracked golden file. The golden must stay pure synthetic fixtures.
    inbox = workdir / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    portfolio_csv.INBOX = inbox
    portfolio_mod.MAPPING_PATH = workdir / "no_portfolio_mapping.yaml"

    res = run_weekly(
        as_of=as_of,
        db_path=workdir / "w.duckdb",
        connectors=FIXTURE_CONNECTORS,
        ingested_at=dt.datetime(2026, 7, 18, 8, 0, 0),
    )
    min_path = Path(res.paths["snapshot_min"])
    return min_path.read_text(encoding="utf-8")
