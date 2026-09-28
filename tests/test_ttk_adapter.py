from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from ipos.evidence.ingest import process_research_drop
from ipos.evidence.register import ActionWatchRegister
from ipos.evidence.ttk_adapter import build_watch_drop, load_ttk_fixture


TTK_ROOT = Path(
    "C:/GitDev/apexai-os-meta/artifacts/transcript_pipeline_v2/"
    "corrective-run/raw/p20-four-source"
)

INVESTMENT_CASES = [
    (
        "vFTuLylvYnA",
        "Wir haben die Renditen der 10-j",
        "TECHNOLOGY_AI",
    ),
    (
        "CygwqaNg2PY",
        "which is a common pattern and the market did the exact opposite because that was actually part",
        "MARKET_TECHNICALS",
    ),
    (
        "oZIsMX6WgFs",
        "It's pure math everyone could do that so now the trap is for sure those cycles are not stable.",
        "MARKET_CYCLES",
    ),
]


def claim_index_containing(fixture, quote_fragment: str) -> int:
    return next(
        index
        for index, claim in enumerate(fixture.candidate_claims)
        if quote_fragment in claim["claim_text"]
    )


def test_load_ttk_fixture_normalizes_string_segment_ids():
    fixture = load_ttk_fixture(TTK_ROOT / "vFTuLylvYnA")

    assert fixture.identity == "vFTuLylvYnA"
    assert fixture.validation["ok"] is True
    assert len(fixture.segments) == 178
    assert fixture.segments[0].id == 0
    assert fixture.original_segment_ids[0] == "seg-000001"


@pytest.mark.parametrize(("identity", "quote_fragment", "topic"), INVESTMENT_CASES)
def test_ttk_candidate_claim_builds_one_grounded_watch(
    tmp_path: Path,
    identity: str,
    quote_fragment: str,
    topic: str,
):
    fixture = load_ttk_fixture(TTK_ROOT / identity)
    index = claim_index_containing(fixture, quote_fragment)
    candidate = fixture.candidate_claims[index]
    cited_id = candidate["source_segment_ids"][0]
    cited_index = fixture.original_segment_ids.index(cited_id)

    drop = build_watch_drop(fixture, index, topic)
    drop_path = tmp_path / f"{identity}.json"
    drop_path.write_text(json.dumps(drop, ensure_ascii=False), encoding="utf-8")
    register = ActionWatchRegister(tmp_path / f"{identity}-register.json")

    result = process_research_drop(
        drop_path,
        register=register,
        receipts_dir=tmp_path / "receipts",
    )

    assert result.errors == []
    assert result.claims_verified == 1
    assert result.watches_registered == 1
    assert result.actions_registered == 0
    item = register.get_active_items()[0]
    assert item.item_class == "WATCH"
    assert item.evidence_refs == [
        f"{identity}#t={fixture.segments[cited_index].start:.1f}"
    ]
    assert drop["claims"][0]["quote_exact"] == candidate["claim_text"]


def test_build_watch_drop_rejects_claim_with_unknown_segment_id():
    fixture = load_ttk_fixture(TTK_ROOT / "vFTuLylvYnA")
    index = claim_index_containing(fixture, "Wir haben die Renditen")
    claims = [dict(claim) for claim in fixture.candidate_claims]
    claims[index]["source_segment_ids"] = ["seg-missing"]
    invalid_fixture = replace(fixture, candidate_claims=claims)

    with pytest.raises(ValueError, match="unknown transcript segment"):
        build_watch_drop(invalid_fixture, index, "TECHNOLOGY_AI")


def test_non_investment_control_is_validated_without_register_impact(tmp_path: Path):
    fixture = load_ttk_fixture(TTK_ROOT / "P-h5WSQG1Sw")
    register = ActionWatchRegister(tmp_path / "register.json")
    receipt = {
        "identity": fixture.identity,
        "transcript_sha256": fixture.transcript_sha256,
        "validation_ok": fixture.validation["ok"],
        "outcome": "NO_IMPACT",
    }
    (tmp_path / "validation-receipt.json").write_text(
        json.dumps(receipt), encoding="utf-8"
    )

    assert fixture.validation["complete"] is True
    assert fixture.transcript_sha256 == (
        "bab3e71c67dfb43a4bf416ec94ef23a14dd205807ac6f2c1207b6a4dd5c21f09"
    )
    assert json.loads((tmp_path / "validation-receipt.json").read_text())["outcome"] == (
        "NO_IMPACT"
    )
    assert register.get_active_items() == []
