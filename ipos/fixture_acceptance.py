"""Unattended, offline acceptance runner for pinned research and portfolio fixtures."""

from __future__ import annotations

import datetime as dt
from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from ipos.config.load import REPO_ROOT
from ipos.etl.portfolio_csv import _parse_smartbroker_pdf, load_positions
from ipos.evidence.claims import load_e05_research_artifact
from ipos.evidence.document_adapter import extract_pdf, verify_pdf_quote
from ipos.evidence.ingest import process_research_drop
from ipos.evidence.register import ActionWatchRegister
from ipos.evidence.schemas import WatchItem
from ipos.evidence.ttk_adapter import build_watch_drop, load_ttk_fixture
from ipos.portfolio.accounting import PortfolioLedger
from ipos.portfolio.action_matrix import build_action_matrix, load_instrument_names
from ipos.portfolio.decision import MacroPortfolioDecisionEngine
from ipos.portfolio.order_staging import stage_orders_from_action_matrix
from ipos.portfolio.pp_adapter import PortfolioPerformanceAdapter


PDF_QUOTE = (
    "Die Welt ist nicht schwach genug für einen klassischen Deflations- oder "
    "Krisenmodus, aber auch nicht gesund genug für ein echtes, breites Risikoumfeld."
)
COMPANION_SHA256 = "157feb8d8d1bf014857a4bef80b1c1cff0698153c3b2dd2e633b1822c2f2cf13"
TTK_WATCH_SELECTIONS = {
    "markus-koch-tech-pressure": ("Wir haben die Renditen", "TECHNOLOGY_AI"),
    "elliott-wave-technical-market": ("which is a common pattern", "MARKET_TECHNICALS"),
    "market-cycles-watch": ("It's pure math everyone could do that", "MARKET_CYCLES"),
}


class FixtureAcceptanceError(RuntimeError):
    """A fixture-integrity or acceptance invariant failed closed."""


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPO_ROOT / path


def _all_fixtures(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    return (
        list(manifest["transcripts"])
        + list(manifest["research_documents"])
        + list(manifest["portfolios"])
        + [manifest["macro_snapshot"]]
    )


def _fixture_path(fixture: dict[str, Any]) -> Path:
    if fixture["id"] == "smartbroker-activities":
        override = os.environ.get("IPOS_SMARTBROKER_ACTIVITIES")
        if override:
            return Path(override)
    return _repo_path(fixture["evidence_file"])


def _validate_manifest(manifest: dict[str, Any]) -> dict[str, str]:
    if manifest.get("mode") != "offline_read_only":
        raise FixtureAcceptanceError("manifest mode must be offline_read_only")
    hashes: dict[str, str] = {}
    for fixture in _all_fixtures(manifest):
        if "output_path" in fixture:
            raise FixtureAcceptanceError(f"source fixture declares output_path: {fixture['id']}")
        path = _fixture_path(fixture)
        if not path.is_file():
            raise FixtureAcceptanceError(f"missing fixture {fixture['id']}: {path}")
        actual = _digest(path)
        if actual != fixture["sha256"]:
            raise FixtureAcceptanceError(
                f"hash mismatch for {fixture['id']}: expected {fixture['sha256']}, got {actual}"
            )
        hashes[fixture["id"]] = actual
    return hashes


def _protected_state(manifest: dict[str, Any]) -> dict[str, str | None]:
    paths: set[Path] = {_fixture_path(item) for item in _all_fixtures(manifest)}
    for transcript in manifest["transcripts"]:
        for key in ("transcript_file", "claims_file", "validation_file"):
            if transcript.get(key):
                paths.add(_repo_path(transcript[key]))
    for document in manifest["research_documents"]:
        if document.get("companion_text"):
            paths.add(_repo_path(document["companion_text"]))
    paths.update(
        {
            REPO_ROOT / "data" / "action_watch_register.json",
            REPO_ROOT / "data" / "warehouse.duckdb",
        }
    )
    exports = REPO_ROOT / "data" / "exports"
    if exports.exists():
        paths.update(path for path in exports.rglob("*") if path.is_file())
    return {
        str(path): _digest(path) if path.is_file() else None
        for path in sorted(paths, key=lambda value: str(value).lower())
    }


def _write_drop(path: Path, drop: dict[str, Any]) -> None:
    path.write_text(json.dumps(drop, ensure_ascii=False, indent=2), encoding="utf-8")


def _find_claim_index(fixture, fragment: str) -> int:
    try:
        return next(
            index
            for index, claim in enumerate(fixture.candidate_claims)
            if fragment in str(claim.get("claim_text", ""))
        )
    except StopIteration as exc:
        raise FixtureAcceptanceError(
            f"selected candidate claim is absent from {fixture.identity}: {fragment}"
        ) from exc


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise FixtureAcceptanceError(message)


def _write_receipts(output_root: Path, result: dict[str, Any]) -> None:
    result_path = output_root / "result.json"
    result_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report = f"""# Fixture Acceptance Verification Report

- Status: **{result['status']}**
- Run time: {result['run_at']}
- Transcripts: {result['transcripts']['passed']} passed ({result['transcripts']['watches']} WATCH, {result['transcripts']['no_impact']} NO_IMPACT)
- Research documents: {result['documents']['passed']} passed, exact page grounding verified
- Portfolio: {result['portfolio']['activities']} activities, {result['portfolio']['smartbroker_positions']} Smartbroker positions, {result['portfolio']['zero_positions']} ZERO positions, {result['portfolio']['holdings']} total holdings
- Reconciliation: {result['portfolio']['reconciliation']}, {result['portfolio']['quantity_discrepancies']} quantity discrepancies
- Research boundary: WATCH and REVIEW produced no portfolio mutation; only the isolated simulated operator ACTION applied the targeted 0.80 multiplier
- Idempotency: {result['idempotency']['duplicate_register_items']} duplicate register items
- Orders: LIMIT tickets staged for manual review only. Zero automated trade execution.
- Protected inputs: source fixtures, live register, warehouse, and prior exports remained byte-identical
"""
    (output_root / "VERIFICATION_REPORT.md").write_text(report, encoding="utf-8")


def run_fixture_acceptance(
    manifest_path: Path,
    output_root: Path,
) -> dict[str, Any]:
    """Run the complete pinned fixture path and write a PASS receipt."""
    manifest_path = _repo_path(manifest_path)
    output_root = Path(output_root)
    if output_root.exists():
        raise FixtureAcceptanceError(f"output directory already exists: {output_root}")
    try:
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        fixture_hashes = _validate_manifest(manifest)
        protected_before = _protected_state(manifest)

        document_spec = manifest["research_documents"][0]
        document = extract_pdf(_fixture_path(document_spec))
        _assert(len(document.pages) == document_spec["expected_pages"], "PDF page count mismatch")
        grounding_quote = document_spec.get("grounding_quote", PDF_QUOTE)
        grounding = verify_pdf_quote(document, grounding_quote)
        companion = _repo_path(document_spec["companion_text"])
        _assert(_digest(companion) == COMPANION_SHA256, "companion Markdown hash mismatch")

        output_root.mkdir(parents=True, exist_ok=False)
        register_path = output_root / "action_watch_register.json"
        receipts_dir = output_root / "ingestion-receipts"
        drops_dir = output_root / "drops"
        drops_dir.mkdir()
        register = ActionWatchRegister(register_path)
        drop_paths: list[Path] = []

        transcript_specs = {item["id"]: item for item in manifest["transcripts"]}
        markus_watch: WatchItem | None = None
        for fixture_id, (fragment, topic) in TTK_WATCH_SELECTIONS.items():
            spec = transcript_specs[fixture_id]
            fixture = load_ttk_fixture(_repo_path(spec["root"]))
            claim_index = _find_claim_index(fixture, fragment)
            drop = build_watch_drop(fixture, claim_index, topic)
            drop_path = drops_dir / f"{fixture_id}.json"
            _write_drop(drop_path, drop)
            ingest = process_research_drop(
                drop_path, register=register, receipts_dir=receipts_dir
            )
            _assert(not ingest.errors and ingest.watches_registered == 1, f"TTK ingest failed: {fixture_id}")
            drop_paths.append(drop_path)
            if fixture_id == "markus-koch-tech-pressure":
                markus_watch = register.get_item(drop["claims"][0]["item_id"])

        imf_spec = transcript_specs["imf-weo-july-2026"]
        media = load_e05_research_artifact(_fixture_path(imf_spec))
        imf_quote = (
            "Trade fragmentation could accelerate, and a correction in "
            "technology-driven expectations is another downside risk"
        )
        imf_drop = {
            "source_id": imf_spec["identity"],
            "segments": [segment.model_dump() for segment in media.segments],
            "claims": [
                {
                    "claim_id": "CLM-FIXTURE-IMF-WATCH",
                    "item_id": "WATCH-FIXTURE-IMF-WATCH",
                    "item_class": "WATCH",
                    "theme": "RISK_FRAGILE",
                    "instrument_or_topic": "TRADE_GEOPOLITICS",
                    "assertion": imf_quote,
                    "invalidation_condition": "Review when newer verified evidence arrives",
                    "quote_exact": imf_quote,
                    "action_or_condition": "Monitor only; operator review required",
                    "reason_short": "Verified IMF downside-risk evidence",
                }
            ],
        }
        imf_drop_path = drops_dir / "imf-weo-july-2026.json"
        _write_drop(imf_drop_path, imf_drop)
        imf_ingest = process_research_drop(
            imf_drop_path, register=register, receipts_dir=receipts_dir
        )
        _assert(not imf_ingest.errors and imf_ingest.watches_registered == 1, "IMF ingest failed")
        drop_paths.append(imf_drop_path)

        control_spec = transcript_specs["emotions-non-investment-control"]
        control = load_ttk_fixture(_repo_path(control_spec["root"]))
        _assert(control.validation.get("ok") is True, "NO_IMPACT control validation failed")
        _assert(len(register.get_active_items()) == 4, "unexpected WATCH register count")

        portfolio_specs = {item["id"]: item for item in manifest["portfolios"]}
        activities = PortfolioPerformanceAdapter(
            default_account="SMARTBROKER"
        ).parse_smartbroker_activities(_fixture_path(portfolio_specs["smartbroker-activities"]))
        _assert(len(activities) == portfolio_specs["smartbroker-activities"]["expected_activities"], "activity count mismatch")
        ledger = PortfolioLedger(account_name="SMARTBROKER")
        ledger.replay_activities(activities)
        ledger_positions = ledger.get_open_positions()
        _assert(len(ledger_positions) == 24, "Smartbroker replay position count mismatch")

        statement = _parse_smartbroker_pdf(_fixture_path(portfolio_specs["smartbroker-statement"]))
        reconciliation = ledger.reconciliation_report(
            external_holdings_control=dict(zip(statement.instrument, statement.quantity))
        )
        _assert(reconciliation["reconciliation_status"] == "MATCH", "Smartbroker reconciliation mismatch")
        _assert(
            abs(float(statement["value_eur"].sum()) - 36411.09) < 0.01,
            "Smartbroker market value mismatch",
        )
        zero = load_positions(path=_fixture_path(portfolio_specs["zero-positions"]))
        _assert(zero is not None and len(zero) == 8, "ZERO position count mismatch")
        _assert(abs(float(zero["value_eur"].sum()) - 3837.21) < 0.01, "ZERO market value mismatch")
        positions = pd.concat([statement, zero], ignore_index=True)
        _assert(len(positions) == 32, "consolidated holding count mismatch")

        snapshot_spec = manifest["macro_snapshot"]
        snapshot = json.loads(_fixture_path(snapshot_spec).read_text(encoding="utf-8"))
        _assert(snapshot["as_of"] == str(snapshot_spec["expected_as_of"]), "macro snapshot date mismatch")
        engine = MacroPortfolioDecisionEngine(register_path=register_path)
        baseline = engine.evaluate_decision(
            positions=positions,
            regime_info=snapshot["regime"],
            overall_info=snapshot["overall"],
            contradictions=snapshot.get("contradictions") or [],
            as_of=snapshot["as_of"],
        )
        _assert(engine.load_open_register_actions() == [], "WATCH affected portfolio action gate")
        _assert(
            all("Active research alert penalty" not in item.rationale for item in baseline.sector_allocations),
            "WATCH or REVIEW affected sector allocation",
        )

        _assert(markus_watch is not None, "Markus WATCH missing")
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
        promoted = engine.evaluate_decision(
            positions=positions,
            regime_info=snapshot["regime"],
            overall_info=snapshot["overall"],
            contradictions=snapshot.get("contradictions") or [],
            as_of=snapshot["as_of"],
        )
        baseline_tech = next(item for item in baseline.sector_allocations if item.sector_id == "TECHNOLOGY_AI")
        promoted_tech = next(item for item in promoted.sector_allocations if item.sector_id == "TECHNOLOGY_AI")
        multiplier_ratio = promoted_tech.macro_tilt_multiplier / baseline_tech.macro_tilt_multiplier
        _assert(abs(multiplier_ratio - 0.80) < 1e-12, "simulated ACTION multiplier mismatch")
        _assert(
            all(
                simulated_id not in item.active_register_items
                for item in promoted.sector_allocations
                if item.sector_id != "TECHNOLOGY_AI"
            ),
            "simulated ACTION leaked to a non-target sector",
        )

        mapping_raw = yaml.safe_load((REPO_ROOT / "configs" / "portfolio_mapping.yaml").read_text(encoding="utf-8"))
        action_matrix = build_action_matrix(
            positions,
            snapshot["regime"],
            snapshot["overall"],
            mapping_raw["mappings"],
            load_instrument_names(),
            macro_decision=promoted,
        )
        staged = stage_orders_from_action_matrix(action_matrix)
        _assert(all(item["order_type"] == "LIMIT" for item in staged["all_tickets"]), "non-LIMIT ticket staged")
        _assert(
            all(item["broker"] in {"ZERO", "SMARTBROKER"} for item in staged["all_tickets"]),
            "unknown broker route staged",
        )
        _assert(
            "Zero automated trade execution." in staged["summary"]["sovereign_execution_note"],
            "manual execution boundary missing",
        )

        before_duplicate_count = len(register.doc.items)
        skipped = 0
        for drop_path in drop_paths:
            repeated = process_research_drop(
                drop_path, register=register, receipts_dir=receipts_dir
            )
            skipped += repeated.files_skipped_receipt
        duplicate_items = len(register.doc.items) - before_duplicate_count
        _assert(skipped == 4 and duplicate_items == 0, "receipt idempotency failed")

        protected_after = _protected_state(manifest)
        _assert(protected_after == protected_before, "protected source or live state changed")
        result = {
            "status": "PASS",
            "run_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "manifest": str(manifest_path),
            "fixture_hashes": fixture_hashes,
            "transcripts": {"passed": 5, "watches": 4, "no_impact": 1},
            "documents": {
                "passed": 1,
                "pages": len(document.pages),
                "grounded_page": grounding.page_number,
            },
            "portfolio": {
                "activities": len(activities),
                "smartbroker_positions": len(statement),
                "zero_positions": len(zero),
                "holdings": len(positions),
                "reconciliation": reconciliation["reconciliation_status"],
                "quantity_discrepancies": len(reconciliation["holdings_discrepancies"]),
                "smartbroker_market_value_eur": round(float(statement["value_eur"].sum()), 2),
                "zero_market_value_eur": round(float(zero["value_eur"].sum()), 2),
                "ledger_cost_value_eur": round(float(ledger.to_ipos_positions()["value_eur"].sum()), 2),
            },
            "decision_boundary": {
                "baseline_open_actions": 0,
                "simulated_action_id": simulated_id,
                "target_sector": "TECHNOLOGY_AI",
                "target_multiplier_ratio": round(multiplier_ratio, 2),
                "non_target_leaks": 0,
            },
            "orders": {
                "tickets": len(staged["all_tickets"]),
                "order_type": "LIMIT",
                "routes": sorted({item["broker"] for item in staged["all_tickets"]}),
            },
            "idempotency": {
                "receipts_skipped": skipped,
                "duplicate_register_items": duplicate_items,
            },
            "manual_execution_only": True,
            "protected_inputs_unchanged": True,
        }
        _write_receipts(output_root, result)
        return result
    except FixtureAcceptanceError:
        raise
    except Exception as exc:
        raise FixtureAcceptanceError(str(exc)) from exc
