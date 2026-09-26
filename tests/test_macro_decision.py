"""Automated verification suite for WF-07 Stage 4 / E08 Macro-to-Portfolio Decision Connection."""

import datetime as dt
from pathlib import Path
import pandas as pd
import pytest
import yaml

from ipos.config.load import REPO_ROOT
from ipos.portfolio.decision import (
    MacroPortfolioDecisionEngine,
    MacroPortfolioDecision,
    RebalanceGatingVerdict,
    SectorAllocation,
)
from ipos.portfolio.action_matrix import build_action_matrix


@pytest.fixture
def sample_positions() -> pd.DataFrame:
    return pd.DataFrame([
        {"instrument": "US67066G1040", "quantity": 10.0, "value_eur": 10000.0, "currency": "EUR"},  # NVDA (Tech)
        {"instrument": "CA64073L1013", "quantity": 1000.0, "value_eur": 5000.0, "currency": "EUR"}, # NDA (Crypto)
        {"instrument": "CA24477V1058", "quantity": 200.0, "value_eur": 5000.0, "currency": "EUR"},  # Definium (Biotech)
        {"instrument": "DE000PS7JX34", "quantity": 50.0, "value_eur": 5000.0, "currency": "EUR"},   # Gold (Commodities)
    ])


@pytest.fixture
def sample_mapping() -> dict[str, str]:
    return {
        "US67066G1040": "EquityRisk",
        "CA64073L1013": "EquityRisk",
        "CA24477V1058": "EquityRisk",
        "DE000PS7JX34": "Commodities",
    }


def test_01_sector_mapping_coverage():
    """Verify that all holdings mapped in portfolio_mapping.yaml have a valid sector."""
    mapping_file = REPO_ROOT / "configs" / "portfolio_mapping.yaml"
    assert mapping_file.exists()
    cfg = yaml.safe_load(mapping_file.read_text(encoding="utf-8"))
    mappings = cfg.get("mappings") or {}
    sectors = cfg.get("sectors") or {}
    sector_defs = cfg.get("sector_definitions") or {}

    assert len(sectors) >= len(mappings)
    valid_sectors = set(sector_defs.keys())
    for inst, sec in sectors.items():
        assert sec in valid_sectors, f"Instrument {inst} has invalid sector {sec}"


def test_02_macro_stance_to_sector_tilts(sample_positions):
    """Verify macro stance vector correctly tilts sectors."""
    engine = MacroPortfolioDecisionEngine()

    # Case A: Commodities bull, high duration headwind (rising rates)
    stance_a = {
        "equity": 0.20,
        "duration": -0.60,       # headwind for tech & biotech
        "commodities": 0.80,    # strong tailwind for commodities
        "credit": 0.10,
        "usd": 0.0,
        "growth": 0.30,
    }
    alloc_a = engine.compute_sector_tilts(
        positions=sample_positions,
        stance_vector=stance_a,
        open_actions=[],
        total_risk_budget_pct=60.0,
    )
    alloc_dict_a = {a.sector_id: a for a in alloc_a}

    assert alloc_dict_a["ENERGY_COMMODITIES"].headwind_tailwind == "TAILWIND"
    assert alloc_dict_a["ENERGY_COMMODITIES"].macro_tilt_multiplier > 1.20
    assert alloc_dict_a["TECHNOLOGY_AI"].headwind_tailwind == "HEADWIND"
    assert alloc_dict_a["TECHNOLOGY_AI"].macro_tilt_multiplier < 1.0

    # Case B: Easing stance (falling yields, high risk appetite)
    stance_b = {
        "equity": 0.60,
        "duration": 0.50,        # tailwind for tech
        "commodities": -0.40,
        "credit": 0.50,
        "usd": -0.20,
        "growth": 0.40,
    }
    alloc_b = engine.compute_sector_tilts(
        positions=sample_positions,
        stance_vector=stance_b,
        open_actions=[],
        total_risk_budget_pct=75.0,
    )
    alloc_dict_b = {a.sector_id: a for a in alloc_b}

    assert alloc_dict_b["TECHNOLOGY_AI"].headwind_tailwind == "TAILWIND"
    assert alloc_dict_b["TECHNOLOGY_AI"].macro_tilt_multiplier > 1.10
    assert alloc_dict_b["ENERGY_COMMODITIES"].headwind_tailwind == "HEADWIND"


def test_03_evidence_register_action_gating(sample_positions, tmp_path):
    """Verify active register actions apply penalty multiplier and alert tags."""
    reg_file = tmp_path / "action_watch_register.json"
    reg_data = {
        "schema_version": "1.0.0",
        "items": [
            {
                "item_id": "ACT-202609-001",
                "class": "ACTION",
                "instrument_or_topic": "TECH_VALUATION",
                "sector": "INFORMATION_TECHNOLOGY",
                "action_or_condition": "TRIM_TECH_EXPOSURE",
                "reason_short": "Prolonged rate pause puts valuation multiple pressure on tech",
                "status": "OPEN",
                "created_at": "2026-09-26T10:00:00Z",
            }
        ]
    }
    import json
    reg_file.write_text(json.dumps(reg_data), encoding="utf-8")

    engine = MacroPortfolioDecisionEngine(register_path=reg_file)
    open_actions = engine.load_open_register_actions()
    assert len(open_actions) == 1

    stance = {"equity": 0.0, "duration": 0.0, "commodities": 0.0, "credit": 0.0, "growth": 0.0, "usd": 0.0}
    allocs = engine.compute_sector_tilts(
        positions=sample_positions,
        stance_vector=stance,
        open_actions=open_actions,
        total_risk_budget_pct=50.0,
    )
    alloc_dict = {a.sector_id: a for a in allocs}

    tech_alloc = alloc_dict["TECHNOLOGY_AI"]
    assert "ACT-202609-001" in tech_alloc.active_register_items
    # Base multiplier 1.0 * 0.80 penalty = 0.80
    assert tech_alloc.macro_tilt_multiplier == pytest.approx(0.80, abs=1e-3)
    assert tech_alloc.headwind_tailwind == "HEADWIND"


def test_04_confidence_gate_restricts_adds(sample_positions, sample_mapping):
    """Verify low macro confidence (<50) gates BUY actions into HOLD (GATED)."""
    engine = MacroPortfolioDecisionEngine()
    regime_info = {"label": "CHOPPY", "risk_scaler": 0.50, "policy_selectors": {}}
    overall_info = {
        "risk_budget": 50.0,
        "confidence": 42.0,     # LOW CONFIDENCE -> Gated
        "stance_vector": {"equity": 0.50, "commodities": 0.50},
    }

    decision = engine.evaluate_decision(
        positions=sample_positions,
        regime_info=regime_info,
        overall_info=overall_info,
        as_of="2026-09-26",
    )

    assert decision.gating.confidence_gate == "RESTRICTED"
    assert decision.gating.allow_adds is False
    assert decision.gating.allow_trims is True

    # Run through Action Matrix
    matrix = build_action_matrix(
        positions=sample_positions,
        regime_info=regime_info,
        overall_info=overall_info,
        mapping=sample_mapping,
        threshold_pct=1.0,
        macro_decision=decision,
    )

    actions = {it["instrument"]: it["action"] for it in matrix["items"]}
    # No BUY actions are permitted under restricted confidence gate
    assert "BUY" not in actions.values()
    assert matrix["summary"]["allow_adds"] is False
    assert matrix["summary"]["rebalance_gating"]["confidence_gate"] == "RESTRICTED"


def test_05_regime_uncertain_forces_defensive(sample_positions, sample_mapping):
    """Verify UNCERTAIN regime blocks additions and enforces defensive policy."""
    engine = MacroPortfolioDecisionEngine()
    regime_info = {"label": "UNCERTAIN", "risk_scaler": 0.40, "policy_selectors": {"trailing_stop": "defensive_quick_exit"}}
    overall_info = {
        "risk_budget": 35.0,
        "confidence": 30.0,
        "stance_vector": {"equity": -0.50, "commodities": 0.0},
    }

    decision = engine.evaluate_decision(
        positions=sample_positions,
        regime_info=regime_info,
        overall_info=overall_info,
        as_of="2026-09-26",
    )

    assert decision.gating.regime_gate == "DEFENSIVE_BLOCK"
    assert decision.gating.allow_adds is False

    matrix = build_action_matrix(
        positions=sample_positions,
        regime_info=regime_info,
        overall_info=overall_info,
        mapping=sample_mapping,
        macro_decision=decision,
    )

    for item in matrix["items"]:
        assert item["action"] != "BUY"
        assert item["trailing_stop"] == "defensive_quick_exit"


def test_06_action_matrix_annotates_sectors_and_gating(sample_positions, sample_mapping):
    """Verify Action Matrix output items contain sector, headwind_tailwind, and gating rationale."""
    regime_info = {"label": "TRENDY", "risk_scaler": 1.00, "policy_selectors": {"trailing_stop": "trailing_profit_protection"}}
    overall_info = {
        "risk_budget": 70.0,
        "confidence": 75.0,     # HIGH CONFIDENCE -> PASS
        "stance_vector": {"equity": 0.40, "commodities": 0.60},
    }

    matrix = build_action_matrix(
        positions=sample_positions,
        regime_info=regime_info,
        overall_info=overall_info,
        mapping=sample_mapping,
        use_risk_parity=False,
    )

    summary = matrix["summary"]
    assert summary["allow_adds"] is True
    assert summary["rebalance_gating"]["confidence_gate"] == "PASS"

    for it in matrix["items"]:
        assert "sector" in it
        assert "sector_name" in it
        assert "headwind_tailwind" in it
        assert it["headwind_tailwind"] in ("TAILWIND", "HEADWIND", "NEUTRAL")
