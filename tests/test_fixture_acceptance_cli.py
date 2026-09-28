from __future__ import annotations

import json
from pathlib import Path
import re

import pytest
import yaml

from ipos.cli import cmd_fixture_acceptance
from ipos.fixture_acceptance import FixtureAcceptanceError, run_fixture_acceptance


MANIFEST = Path("configs/fixture_acceptance.yaml")


def write_manifest_copy(tmp_path: Path, mutate) -> Path:
    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    mutate(data)
    path = tmp_path / "manifest.yaml"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path


def test_fixture_acceptance_cli_writes_complete_receipt(tmp_path: Path):
    output = tmp_path / "acceptance-output"

    rc = cmd_fixture_acceptance(
        ["--manifest", str(MANIFEST), "--output", str(output)]
    )

    assert rc == 0
    result_path = output / "result.json"
    assert not result_path.read_bytes().startswith(b"\xef\xbb\xbf")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    assert result["status"] == "PASS"
    assert result["transcripts"]["passed"] == 5
    assert result["documents"]["passed"] == 1
    assert result["portfolio"]["activities"] == 332
    assert result["portfolio"]["holdings"] == 32
    assert result["portfolio"]["reconciliation"] == "MATCH"
    assert result["idempotency"]["duplicate_register_items"] == 0
    assert result["manual_execution_only"] is True
    assert (output / "VERIFICATION_REPORT.md").is_file()


def test_altered_fixture_hash_fails_closed(tmp_path: Path):
    manifest = write_manifest_copy(
        tmp_path,
        lambda data: data["macro_snapshot"].update({"sha256": "0" * 64}),
    )

    with pytest.raises(FixtureAcceptanceError, match="hash mismatch.*macro-2026-09-25"):
        run_fixture_acceptance(manifest, tmp_path / "output")


def test_ungrounded_document_quote_fails_closed(tmp_path: Path):
    manifest = write_manifest_copy(
        tmp_path,
        lambda data: data["research_documents"][0].update(
            {"grounding_quote": "The source guarantees a risk-free return of 25 percent."}
        ),
    )

    with pytest.raises(FixtureAcceptanceError, match="Quote not found in PDF"):
        run_fixture_acceptance(manifest, tmp_path / "output")


def test_missing_private_portfolio_reports_exact_path(tmp_path: Path, monkeypatch):
    missing = tmp_path / "missing-private-activities.csv"
    monkeypatch.setenv("IPOS_SMARTBROKER_ACTIVITIES", str(missing))

    with pytest.raises(FixtureAcceptanceError, match=re.escape(str(missing))):
        run_fixture_acceptance(MANIFEST, tmp_path / "output")


def test_existing_output_directory_is_never_overwritten(tmp_path: Path):
    output = tmp_path / "existing"
    output.mkdir()
    sentinel = output / "sentinel.txt"
    sentinel.write_text("preserve", encoding="utf-8")

    with pytest.raises(FixtureAcceptanceError, match="output directory already exists"):
        run_fixture_acceptance(MANIFEST, output)

    assert sentinel.read_text(encoding="utf-8") == "preserve"


def test_fixture_runner_has_no_execution_or_credential_imports():
    source = Path("ipos/fixture_acceptance.py").read_text(encoding="utf-8")
    forbidden = [
        r"\brequests\b",
        r"\bsocket\b",
        r"\bselenium\b",
        r"broker[_-]?sdk",
        r"\bcredential",
        r"\bimaplib\b",
        r"\bsmtplib\b",
    ]

    for pattern in forbidden:
        assert re.search(pattern, source, re.IGNORECASE) is None, pattern
