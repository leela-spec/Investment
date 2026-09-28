from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest
import yaml

from ipos.etl.portfolio_csv import _parse_smartbroker_pdf, load_positions
from ipos.evidence.document_adapter import extract_pdf, verify_pdf_quote
from ipos.evidence.ingest import process_research_drop
from ipos.evidence.register import ActionWatchRegister
from ipos.evidence.schemas import WatchItem
from ipos.evidence.ttk_adapter import build_watch_drop, load_ttk_fixture
from ipos.portfolio.action_matrix import build_action_matrix, load_instrument_names
from ipos.portfolio.decision import MacroPortfolioDecisionEngine
from ipos.portfolio.order_staging import stage_orders_from_action_matrix


TTK_ROOT = Path(
    "C:/GitDev/apexai-os-meta/artifacts/transcript_pipeline_v2/"
    "corrective-run/raw/p20-four-source"
)
SNAPSHOT_PATH = Path("data/exports/snapshots/2026-09-25/snapshot.json")
PDF_PATH = Path("Sources/GER Elephant in The Room Analysis.pdf")
PDF_QUOTE = (
    "Die Welt ist nicht schwach genug für einen klassischen Deflations- oder "
    "Krisenmodus, aber auch nicht gesund genug für ein echtes, breites Risikoumfeld."
)
TTK_CASES = [
    ("vFTuLylvYnA", "Wir haben die Renditen", "TECHNOLOGY_AI"),
    ("CygwqaNg2PY", "which is a common pattern", "MARKET_TECHNICALS"),
    ("oZIsMX6WgFs", "It's pure math everyone could do that", "MARKET_CYCLES"),
]


def load_manifest() -> dict:
    return yaml.safe_load(Path("configs/fixture_acceptance.yaml").read_text(encoding="utf-8"))


def load_consolidated_positions() -> pd.DataFrame:
    portfolios = {item["id"]: Path(item["evidence_file"]) for item in load_manifest()["portfolios"]}
    statement = _parse_smartbroker_pdf(portfolios["smartbroker-statement"])
    zero = load_positions(path=portfolios["zero-positions"])
    assert zero is not None
    return pd.concat([statement, zero], ignore_index=True)


def ingest_fixture_watches(tmp_path: Path, register: ActionWatchRegister) -> WatchItem:
    markus_item = None
    for identity, quote_fragment, topic in TTK_CASES:
        fixture = load_ttk_fixture(TTK_ROOT / identity)
        claim_index = next(
            index
            for index, claim in enumerate(fixture.candidate_claims)
            if quote_fragment in claim["claim_text"]
        )
        drop = build_watch_drop(fixture, claim_index, topic)
        drop_path = tmp_path / f"{identity}.json"
        drop_path.write_text(json.dumps(drop, ensure_ascii=False), encoding="utf-8")
        result = process_research_drop(
            drop_path,
            register=register,
            receipts_dir=tmp_path / "receipts",
        )
        assert result.errors == []
        if identity == "vFTuLylvYnA":
            markus_item = register.get_item(drop["claims"][0]["item_id"])

    assert markus_item is not None
    return markus_item


def evaluate_snapshot(register_path: Path):
    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    engine = MacroPortfolioDecisionEngine(register_path=register_path)
    decision = engine.evaluate_decision(
        positions=load_consolidated_positions(),
        regime_info=snapshot["regime"],
        overall_info=snapshot["overall"],
        contradictions=snapshot.get("contradictions") or [],
        as_of=snapshot["as_of"],
    )
    return snapshot, engine, decision


def prepare_isolated_acceptance(tmp_path: Path):
    register_path = tmp_path / "action_watch_register.json"
    register = ActionWatchRegister(register_path)
    markus_item = ingest_fixture_watches(tmp_path, register)

    document = extract_pdf(PDF_PATH)
    pdf_grounding = verify_pdf_quote(document, PDF_QUOTE)
    control = load_ttk_fixture(TTK_ROOT / "P-h5WSQG1Sw")
    receipt = {
        "document_outcome": "REVIEW",
        "document_page": pdf_grounding.page_number,
        "control_identity": control.identity,
        "control_outcome": "NO_IMPACT",
    }
    (tmp_path / "review-and-control-receipt.json").write_text(
        json.dumps(receipt), encoding="utf-8"
    )
    snapshot, engine, baseline = evaluate_snapshot(register_path)
    return register, markus_item, snapshot, engine, baseline


def test_watch_and_review_evidence_cannot_change_portfolio(tmp_path: Path):
    register, _, _, engine, baseline = prepare_isolated_acceptance(tmp_path)

    assert len(register.get_active_items()) == 3
    assert engine.load_open_register_actions() == []
    assert baseline.gating.register_action_gate == "PASS"
    assert all(
        "Active research alert penalty" not in allocation.rationale
        for allocation in baseline.sector_allocations
    )


def test_simulated_operator_action_changes_only_target_sector_and_stays_manual(
    tmp_path: Path,
):
    register, markus_watch, snapshot, _, baseline = prepare_isolated_acceptance(tmp_path)
    simulated_id = f"SIMULATED-OPERATOR-APPROVAL-{markus_watch.item_id}"
    register.upsert_item(
        WatchItem(
            item_id=simulated_id,
            item_class="ACTION",
            instrument_or_topic="TECHNOLOGY_AI",
            action_or_condition=markus_watch.action_or_condition,
            reason_short=markus_watch.reason_short,
            linked_claim_ids=markus_watch.linked_claim_ids,
            evidence_refs=markus_watch.evidence_refs,
            status="OPEN",
        )
    )
    _, _, promoted = evaluate_snapshot(register.path)

    tech_baseline = next(
        item for item in baseline.sector_allocations if item.sector_id == "TECHNOLOGY_AI"
    )
    tech_promoted = next(
        item for item in promoted.sector_allocations if item.sector_id == "TECHNOLOGY_AI"
    )
    assert promoted.gating.register_action_gate == "ACTIVE_ALERTS"
    assert promoted.gating.allow_sells is True
    assert promoted.gating.allow_trims is True
    assert tech_promoted.macro_tilt_multiplier == pytest.approx(
        tech_baseline.macro_tilt_multiplier * 0.80
    )
    assert "SIMULATED-OPERATOR-APPROVAL-" in " ".join(
        tech_promoted.active_register_items
    )
    assert all(
        simulated_id not in allocation.active_register_items
        for allocation in promoted.sector_allocations
        if allocation.sector_id != "TECHNOLOGY_AI"
    )

    mapping_raw = yaml.safe_load(Path("configs/portfolio_mapping.yaml").read_text(encoding="utf-8"))
    action_matrix = build_action_matrix(
        load_consolidated_positions(),
        snapshot["regime"],
        snapshot["overall"],
        mapping_raw["mappings"],
        load_instrument_names(),
        macro_decision=promoted,
    )
    staged = stage_orders_from_action_matrix(action_matrix)
    assert all(ticket["order_type"] == "LIMIT" for ticket in staged["all_tickets"])
    assert all(
        ticket["broker"] in {"ZERO", "SMARTBROKER"}
        for ticket in staged["all_tickets"]
    )
    assert "Zero automated trade execution." in staged["summary"][
        "sovereign_execution_note"
    ]
