"""Test-isolation guards: the suite and the golden must never read the
operator's real portfolio, and must never write into their real exports.

Found 2026-07-27: ``build_golden_min`` isolated the archive and exports dirs
but not ``portfolio_csv.INBOX``, so dropping a real broker export into
``data/inbox/`` changed the golden snapshot — which would have committed
holdings-derived contradictions into a tracked file and made the regression
test machine-dependent.

Found 2026-07-29: the write side had the mirror-image hole. ``EXPORTS_DIR`` is
re-bound per importing module, and neither the per-test monkeypatches nor
``ipos/golden.py`` covered ``ipos.report.html`` — so every run of the suite
overwrote the operator's real ``data/exports/latest.html`` and ``report.html``
with synthetic fixture output that still looked like a real report.

These tests pin both fixes.
"""

from __future__ import annotations

import datetime as dt
import json
import tempfile
from pathlib import Path

import ipos.aggregate.portfolio as portfolio_mod
import ipos.etl.portfolio_csv as portfolio_csv
from ipos.config.load import REPO_ROOT
from ipos.golden import build_golden_min


def test_autouse_fixture_hides_the_real_inbox():
    """The autouse fixture in conftest must have redirected both paths away
    from the repo, for every test in the suite."""
    assert portfolio_csv.INBOX.name == "_isolated_inbox"
    assert not portfolio_csv.latest_portfolio_file(), "a test can see a portfolio CSV"
    assert not portfolio_mod.MAPPING_PATH.exists()
    mapping, policy = portfolio_mod.load_mapping()
    assert mapping == {}, "a test can see the operator's real instrument mapping"


def test_no_module_can_write_into_the_real_exports_dir():
    """Checked per module, because ``from ... import EXPORTS_DIR`` gives each one
    its own binding — the exact reason ``ipos.report.html`` was missed."""
    import ipos.ai.bundle as bundle_mod
    import ipos.export.report as report_mod
    import ipos.export.snapshot as snap_mod
    import ipos.report.html as html_mod

    real = REPO_ROOT / "data" / "exports"
    for mod in (snap_mod, report_mod, html_mod, bundle_mod):
        target = Path(mod.EXPORTS_DIR)
        assert real not in target.parents and target != real, (
            f"{mod.__name__}.EXPORTS_DIR still points inside the operator's real "
            f"exports dir ({target}) — a test run would clobber their report"
        )


def test_writing_a_report_does_not_touch_the_real_exports_dir(populated_db, as_of):
    """End-to-end version of the guard: run the real writers and confirm nothing
    landed in the repo's data/exports."""
    from ipos.report.html import write_html
    from ipos.warehouse.db import connect

    from ipos.export.snapshot import build_snapshot

    real = REPO_ROOT / "data" / "exports"
    before = {p: p.stat().st_mtime_ns for p in real.rglob("*") if p.is_file()} \
        if real.exists() else {}

    db, reg = populated_db
    with connect(db, read_only=True) as con:
        snap = build_snapshot(con, reg, as_of)
        write_html(con, snap, as_of)   # no base_dir: the path that used to leak

    after = {p: p.stat().st_mtime_ns for p in real.rglob("*") if p.is_file()} \
        if real.exists() else {}
    assert before == after, (
        "writing a report modified files under the operator's real data/exports: "
        f"{sorted({k.name for k in set(before) ^ set(after)} | {k.name for k in before if after.get(k) != before[k]})}"
    )


def test_golden_is_portfolio_free_even_when_a_real_inbox_exists(tmp_path, monkeypatch):
    """Simulate the operator's warehouse: a populated inbox + a real mapping.
    The golden must come out identical to one built with an empty inbox."""
    # a decoy inbox + mapping that WOULD be picked up without isolation
    decoy = tmp_path / "decoy_inbox"
    decoy.mkdir()
    (decoy / "portfolio.csv").write_text(
        "instrument,quantity,value_eur\nDE0008404005,400,149120.00\n", encoding="utf-8"
    )
    mapping = tmp_path / "mapping.yaml"
    mapping.write_text(
        "mappings:\n  DE0008404005: EquityRisk\nunmapped_policy: warn\n", encoding="utf-8"
    )
    monkeypatch.setattr(portfolio_csv, "INBOX", decoy)
    monkeypatch.setattr(portfolio_mod, "MAPPING_PATH", mapping)

    with tempfile.TemporaryDirectory() as d:
        built = json.loads(build_golden_min(Path(d)))

    assert "portfolio" not in built, (
        "the golden picked up a portfolio — build_golden_min must isolate "
        "portfolio_csv.INBOX so the committed golden never depends on, or "
        "embeds, operator holdings"
    )
    assert not any(c["id"].startswith("PORTFOLIO_") for c in built["contradictions"]), (
        "portfolio-mismatch contradictions leaked into the golden"
    )


def test_committed_golden_has_no_portfolio_data():
    """Belt-and-braces on the artifact itself, not just the builder."""
    from ipos.golden import GOLDEN_PATH

    blob = GOLDEN_PATH.read_text(encoding="utf-8")
    assert '"portfolio"' not in blob
    assert "PORTFOLIO_" not in blob
    # no ISIN-shaped tokens (2 letters + 10 alphanumerics) from a broker export
    import re

    assert not re.search(r'"[A-Z]{2}[A-Z0-9]{10}"', blob), "possible ISIN in the golden"
