"""Test-isolation guards: the suite and the golden must never read the
operator's real portfolio.

Found 2026-07-27: ``build_golden_min`` isolated the archive and exports dirs
but not ``portfolio_csv.INBOX``, so dropping a real broker export into
``data/inbox/`` changed the golden snapshot — which would have committed
holdings-derived contradictions into a tracked file and made the regression
test machine-dependent. These tests pin the fix.
"""

from __future__ import annotations

import datetime as dt
import json
import tempfile
from pathlib import Path

import ipos.aggregate.portfolio as portfolio_mod
import ipos.etl.portfolio_csv as portfolio_csv
from ipos.golden import build_golden_min


def test_autouse_fixture_hides_the_real_inbox():
    """The autouse fixture in conftest must have redirected both paths away
    from the repo, for every test in the suite."""
    assert portfolio_csv.INBOX.name == "_isolated_inbox"
    assert not portfolio_csv.latest_portfolio_file(), "a test can see a portfolio CSV"
    assert not portfolio_mod.MAPPING_PATH.exists()
    mapping, policy = portfolio_mod.load_mapping()
    assert mapping == {}, "a test can see the operator's real instrument mapping"


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
