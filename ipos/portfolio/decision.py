"""Macro-to-Portfolio Decision Connection Engine (WF-07 Stage 4 / US-06).

Connects macro signals (Regime, Risk Budget, Stance Vector, Contradictions, and Evidence Register)
directly to systematic portfolio rebalancing decisions, sector headwind/tailwind allocations,
and deterministic rebalancing gating rules before the Action Matrix (Stage 5).

Axioms:
1. Deterministic priority: All sector tilts, risk scalers, and gating verdicts are pure code.
2. Sovereign human execution: Gating decisions advise the operator; zero automated broker orders.
3. Asymmetric gating: Low macro confidence or high uncertainty blocks new adds (BUY -> HOLD (GATED)),
   but never blocks defensive capital-preserving trims or exits (TRIM / SELL).
"""

from __future__ import annotations

import datetime as dt
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import yaml

from ipos.config.load import REPO_ROOT

MAPPING_PATH = REPO_ROOT / "configs" / "portfolio_mapping.yaml"
REGISTER_PATH = REPO_ROOT / "data" / "action_watch_register.json"


@dataclass
class RebalanceGatingVerdict:
    """Deterministic rebalancing gating rules for portfolio additions and trims."""

    confidence_gate: str             # "PASS" | "RESTRICTED"
    confidence_value: float          # 0 - 100
    regime_gate: str                 # "PASS" | "SCALED" | "DEFENSIVE_BLOCK"
    regime_label: str                # "CHOPPY" | "TRENDY" | "MOMENTUM" | "UNCERTAIN"
    risk_scaler: float               # e.g. 0.50 for CHOPPY, 0.40 for UNCERTAIN, 1.00 for TRENDY
    contradiction_gate: str          # "PASS" | "CAUTION" | "BLOCKED"
    active_contradictions_count: int
    register_action_gate: str        # "PASS" | "ACTIVE_ALERTS"
    active_open_actions: list[dict[str, Any]] = field(default_factory=list)
    allow_adds: bool = True          # False when BUY actions are gated into HOLD (GATED)
    allow_trims: bool = True         # Always True to preserve capital
    allow_sells: bool = True         # Always True to preserve capital
    gating_rationale: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "confidence_gate": self.confidence_gate,
            "confidence_value": round(self.confidence_value, 2),
            "regime_gate": self.regime_gate,
            "regime_label": self.regime_label,
            "risk_scaler": round(self.risk_scaler, 2),
            "contradiction_gate": self.contradiction_gate,
            "active_contradictions_count": self.active_contradictions_count,
            "register_action_gate": self.register_action_gate,
            "active_open_actions_count": len(self.active_open_actions),
            "allow_adds": self.allow_adds,
            "allow_trims": self.allow_trims,
            "allow_sells": self.allow_sells,
            "gating_rationale": self.gating_rationale,
        }


@dataclass
class SectorAllocation:
    """Macro stance to sector cluster tilt and target weight allocation."""

    sector_id: str
    display_name: str
    current_value_eur: float
    current_weight_pct: float
    macro_tilt_multiplier: float     # e.g. 0.85 = 15% headwind, 1.20 = 20% tailwind
    headwind_tailwind: str           # "TAILWIND" | "HEADWIND" | "NEUTRAL"
    rationale: str
    target_weight_pct: float
    target_value_eur: float
    delta_weight_pct: float
    active_register_items: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "sector_id": self.sector_id,
            "display_name": self.display_name,
            "current_value_eur": round(self.current_value_eur, 2),
            "current_weight_pct": round(self.current_weight_pct, 2),
            "macro_tilt_multiplier": round(self.macro_tilt_multiplier, 3),
            "headwind_tailwind": self.headwind_tailwind,
            "rationale": self.rationale,
            "target_weight_pct": round(self.target_weight_pct, 2),
            "target_value_eur": round(self.target_value_eur, 2),
            "delta_weight_pct": round(self.delta_weight_pct, 2),
            "active_register_items": self.active_register_items,
        }


@dataclass
class MacroPortfolioDecision:
    """Stage 4 decision package connecting macro stance to portfolio optimization."""

    as_of: Optional[str]
    regime_label: str
    risk_budget: float
    macro_confidence: float
    stance_vector: dict[str, float]
    gating: RebalanceGatingVerdict
    sector_allocations: list[SectorAllocation]
    sector_target_weights: dict[str, float]
    instrument_sectors: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "as_of": self.as_of,
            "regime_label": self.regime_label,
            "risk_budget": round(self.risk_budget, 2),
            "macro_confidence": round(self.macro_confidence, 2),
            "stance_vector": {k: round(v, 3) for k, v in self.stance_vector.items()},
            "gating": self.gating.to_dict(),
            "sector_allocations": [sa.to_dict() for sa in self.sector_allocations],
            "sector_target_weights": {k: round(v, 2) for k, v in self.sector_target_weights.items()},
        }


class MacroPortfolioDecisionEngine:
    """Stage 4 engine translating macro signals & research evidence into sector tilts & gating rules."""

    def __init__(self, mapping_path: Optional[Path] = None, register_path: Optional[Path] = None):
        self.mapping_path = mapping_path or MAPPING_PATH
        self.register_path = register_path or REGISTER_PATH
        self._load_taxonomies()

    def _load_taxonomies(self) -> None:
        if self.mapping_path.exists():
            try:
                raw = yaml.safe_load(self.mapping_path.read_text(encoding="utf-8")) or {}
                self.sectors = dict(raw.get("sectors") or {})
                self.sector_definitions = dict(raw.get("sector_definitions") or {})
            except Exception:
                self.sectors = {}
                self.sector_definitions = {}
        else:
            self.sectors = {}
            self.sector_definitions = {}

    def load_open_register_actions(self) -> list[dict[str, Any]]:
        """Load open ACTION items from data/action_watch_register.json."""
        if not self.register_path.exists():
            return []
        try:
            data = json.loads(self.register_path.read_text(encoding="utf-8"))
            items = data.get("items") or []
            return [it for it in items if str(it.get("status")).upper() == "OPEN" and str(it.get("class")).upper() == "ACTION"]
        except Exception:
            return []

    def evaluate_gating(
        self,
        regime_info: dict[str, Any],
        overall_info: dict[str, Any],
        contradictions: Optional[list[dict[str, Any]]] = None,
    ) -> RebalanceGatingVerdict:
        """Evaluate deterministic rebalancing gating rules across Confidence, Regime, and Contradictions."""
        regime_label = str(regime_info.get("label", "UNCERTAIN")).upper()
        risk_scaler = float(regime_info.get("risk_scaler", 1.0) or 1.0)
        confidence = float(overall_info.get("confidence", 50.0) or 50.0)
        active_contradictions = contradictions or []

        open_actions = self.load_open_register_actions()
        rationale: list[str] = []
        allow_adds = True

        # 1. Confidence Gate (Gate 1)
        if confidence < 50.0:
            confidence_gate = "RESTRICTED"
            allow_adds = False
            rationale.append(f"Confidence Gate RESTRICTED: Macro confidence ({confidence:.1f}%) is below 50.0% threshold. Halting new additions.")
        elif regime_label == "UNCERTAIN":
            confidence_gate = "RESTRICTED"
            allow_adds = False
            rationale.append("Confidence Gate RESTRICTED: Macro regime is UNCERTAIN. Halting new additions to preserve capital.")
        else:
            confidence_gate = "PASS"

        # 2. Regime Scaler Gate (Gate 2)
        if regime_label == "UNCERTAIN":
            regime_gate = "DEFENSIVE_BLOCK"
            rationale.append(f"Regime Gate DEFENSIVE_BLOCK: Risk scaler {risk_scaler:.2f}x enforces defensive capital preservation.")
        elif risk_scaler < 0.70:
            regime_gate = "SCALED"
            rationale.append(f"Regime Gate SCALED: {regime_label} regime applies risk scaler {risk_scaler:.2f}x (Rule #42: penalize breakout additions).")
        else:
            regime_gate = "PASS"

        # 3. Contradiction Gate (Gate 3)
        crit_contra = [c for c in active_contradictions if str(c.get("severity")).lower() in ("high", "critical")]
        if crit_contra:
            contradiction_gate = "BLOCKED" if len(crit_contra) >= 2 else "CAUTION"
            if contradiction_gate == "BLOCKED":
                allow_adds = False
                rationale.append(f"Contradiction Gate BLOCKED: {len(crit_contra)} severe inter-module contradiction(s) active. Halting new risk allocation.")
            else:
                rationale.append(f"Contradiction Gate CAUTION: {len(crit_contra)} severe contradiction(s) active.")
        else:
            contradiction_gate = "PASS"

        # 4. Action/Watch Register Gate (Gate 4)
        if open_actions:
            register_action_gate = "ACTIVE_ALERTS"
            rationale.append(f"Evidence Register Gate: {len(open_actions)} active OPEN research action item(s) pending operator execution.")
        else:
            register_action_gate = "PASS"

        return RebalanceGatingVerdict(
            confidence_gate=confidence_gate,
            confidence_value=confidence,
            regime_gate=regime_gate,
            regime_label=regime_label,
            risk_scaler=risk_scaler,
            contradiction_gate=contradiction_gate,
            active_contradictions_count=len(active_contradictions),
            register_action_gate=register_action_gate,
            active_open_actions=open_actions,
            allow_adds=allow_adds,
            allow_trims=True,
            allow_sells=True,
            gating_rationale=rationale,
        )

    def compute_sector_tilts(
        self,
        positions: pd.DataFrame,
        stance_vector: dict[str, float],
        open_actions: list[dict[str, Any]],
        total_risk_budget_pct: float,
    ) -> list[SectorAllocation]:
        """Compute sector-level headwind/tailwind multipliers and target weights."""
        if positions.empty:
            return []

        total_portfolio_val = float(positions["value_eur"].sum())
        if total_portfolio_val <= 0:
            return []

        # Map each position to sector
        pos_df = positions.copy()
        pos_df["sector"] = pos_df["instrument"].map(lambda x: self.sectors.get(x, "OTHER_UNCLASSIFIED"))

        # Current capital by sector
        sector_totals = pos_df.groupby("sector")["value_eur"].sum().to_dict()

        allocations: list[SectorAllocation] = []
        raw_weighted_shares: dict[str, float] = {}

        # Distinct stance dimensions
        equity_stance = float(stance_vector.get("equity", 0.0) or 0.0)
        duration_stance = float(stance_vector.get("duration", 0.0) or 0.0)
        commodities_stance = float(stance_vector.get("commodities", 0.0) or 0.0)
        credit_stance = float(stance_vector.get("credit", 0.0) or 0.0)
        growth_stance = float(stance_vector.get("growth", 0.0) or 0.0)
        usd_stance = float(stance_vector.get("usd", 0.0) or 0.0)

        # Map active register actions to sectors
        sector_alert_map: dict[str, list[str]] = {}
        for it in open_actions:
            sec = str(it.get("sector", "")).upper()
            item_id = str(it.get("item_id", ""))
            # Cross-map standard sector names
            mapped_sec = None
            if "TECH" in sec or "INFORMATION_TECHNOLOGY" in sec:
                mapped_sec = "TECHNOLOGY_AI"
            elif "CRYPTO" in sec or "DIGITAL" in sec:
                mapped_sec = "CRYPTO_DIGITAL_ASSETS"
            elif "HEALTH" in sec or "BIOTECH" in sec:
                mapped_sec = "HEALTHCARE_BIOTECH"
            elif "COMMODIT" in sec or "ENERGY" in sec:
                mapped_sec = "ENERGY_COMMODITIES"
            elif "DEFENSE" in sec or "INDUSTRIAL" in sec:
                mapped_sec = "DEFENSE_INDUSTRIALS"

            if mapped_sec:
                sector_alert_map.setdefault(mapped_sec, []).append(item_id)
            elif sec == "EQUITY_EXPOSURE":
                # General equity alert tags all equity sectors
                for es in ("TECHNOLOGY_AI", "CRYPTO_DIGITAL_ASSETS", "HEALTHCARE_BIOTECH", "DEFENSE_INDUSTRIALS"):
                    sector_alert_map.setdefault(es, []).append(item_id)

        # Evaluate each sector
        known_sectors = list(self.sector_definitions.keys())
        all_active_sectors = sorted(set(known_sectors).union(sector_totals.keys()))

        for sec in all_active_sectors:
            sec_def = self.sector_definitions.get(sec, {})
            display_name = sec_def.get("display_name", sec.replace("_", " ").title())
            current_val = float(sector_totals.get(sec, 0.0))
            current_wt = (current_val / total_portfolio_val) * 100.0 if total_portfolio_val > 0 else 0.0

            # Compute macro tilt multiplier
            base_mult = 1.0
            rationale_parts = []

            if sec == "TECHNOLOGY_AI":
                # Growth tech benefits from equity stance, penalized by negative duration stance (higher yields)
                # Stance is -1 to +1
                tilt_delta = (0.5 * equity_stance) + (0.5 * duration_stance) + (0.2 * credit_stance)
                base_mult = 1.0 + tilt_delta
                rationale_parts.append(f"Equity stance ({equity_stance:+.2f}) & duration sensitivity ({duration_stance:+.2f})")

            elif sec == "CRYPTO_DIGITAL_ASSETS":
                # High-beta liquidity asset: sensitive to credit & risk appetite, penalized by strong USD
                tilt_delta = (0.6 * equity_stance) + (0.4 * credit_stance) - (0.3 * usd_stance)
                base_mult = 1.0 + tilt_delta
                rationale_parts.append(f"Risk appetite ({equity_stance:+.2f}), credit liquidity ({credit_stance:+.2f}), USD drag ({usd_stance:+.2f})")

            elif sec == "HEALTHCARE_BIOTECH":
                # Early clinical biotech behaves as long duration asset
                tilt_delta = (0.4 * equity_stance) + (0.6 * duration_stance)
                base_mult = 1.0 + tilt_delta
                rationale_parts.append(f"Duration sensitivity ({duration_stance:+.2f}) & equity stance ({equity_stance:+.2f})")

            elif sec == "ENERGY_COMMODITIES":
                # Direct commodity driver + inflation hedge
                tilt_delta = (0.8 * commodities_stance) - (0.2 * usd_stance)
                base_mult = 1.0 + tilt_delta
                rationale_parts.append(f"Commodities stance ({commodities_stance:+.2f}) & USD impact ({usd_stance:+.2f})")

            elif sec == "DEFENSE_INDUSTRIALS":
                # Driven by growth / capex stance and defensive equity demand
                tilt_delta = (0.5 * growth_stance) + (0.5 * equity_stance)
                base_mult = 1.0 + tilt_delta
                rationale_parts.append(f"Economic growth stance ({growth_stance:+.2f}) & equity stance ({equity_stance:+.2f})")

            elif sec == "FINANCIALS_VALUE":
                # Benefits from positive net interest margin / higher rates
                tilt_delta = (0.5 * equity_stance) - (0.5 * duration_stance)
                base_mult = 1.0 + tilt_delta
                rationale_parts.append(f"Net interest margin tilt & equity stance ({equity_stance:+.2f})")

            else:
                base_mult = 1.0
                rationale_parts.append("Unclassified sector baseline")

            # Check for active research action penalties
            alert_items = sector_alert_map.get(sec, [])
            if alert_items:
                base_mult *= 0.80  # 20% defensive penalty for active thesis invalidation
                rationale_parts.append(f"Active research alert penalty ({', '.join(alert_items)})")

            # Clamp multiplier to [0.20, 1.80]
            mult = max(0.20, min(1.80, base_mult))

            if mult >= 1.05:
                hw_tw = "TAILWIND"
            elif mult <= 0.95:
                hw_tw = "HEADWIND"
            else:
                hw_tw = "NEUTRAL"

            raw_weighted_shares[sec] = current_wt * mult

            allocations.append(SectorAllocation(
                sector_id=sec,
                display_name=display_name,
                current_value_eur=current_val,
                current_weight_pct=current_wt,
                macro_tilt_multiplier=mult,
                headwind_tailwind=hw_tw,
                rationale="; ".join(rationale_parts),
                target_weight_pct=0.0,
                target_value_eur=0.0,
                delta_weight_pct=0.0,
                active_register_items=alert_items,
            ))

        # Normalize target sector weights against macro risk budget
        total_raw = sum(raw_weighted_shares.values())
        for sa in allocations:
            sec = sa.sector_id
            norm_share = (raw_weighted_shares[sec] / total_raw) if total_raw > 0 else 0.0
            target_wt = round(norm_share * total_risk_budget_pct, 2)
            target_val = round(total_portfolio_val * (target_wt / 100.0), 2)
            delta_wt = round(target_wt - sa.current_weight_pct, 2)

            sa.target_weight_pct = target_wt
            sa.target_value_eur = target_val
            sa.delta_weight_pct = delta_wt

        # Sort: largest current weight first
        allocations.sort(key=lambda x: -x.current_weight_pct)
        return allocations

    def evaluate_decision(
        self,
        positions: pd.DataFrame,
        regime_info: dict[str, Any],
        overall_info: dict[str, Any],
        contradictions: Optional[list[dict[str, Any]]] = None,
        as_of: Optional[str | dt.date] = None,
    ) -> MacroPortfolioDecision:
        """Run Stage 4 decision engine end-to-end."""
        as_of_str = str(as_of) if as_of else None
        regime_label = str(regime_info.get("label", "UNCERTAIN")).upper()
        risk_budget = float(overall_info.get("risk_budget", 50.0) or 50.0)
        confidence = float(overall_info.get("confidence", 50.0) or 50.0)
        stance_vector = overall_info.get("stance_vector") or {}

        # 1. Gating
        gating = self.evaluate_gating(regime_info, overall_info, contradictions)

        # 2. Sector Tilts & Allocations
        sector_allocations = self.compute_sector_tilts(
            positions=positions,
            stance_vector=stance_vector,
            open_actions=gating.active_open_actions,
            total_risk_budget_pct=risk_budget,
        )

        sector_target_weights = {sa.sector_id: sa.target_weight_pct for sa in sector_allocations}

        return MacroPortfolioDecision(
            as_of=as_of_str,
            regime_label=regime_label,
            risk_budget=risk_budget,
            macro_confidence=confidence,
            stance_vector=stance_vector,
            gating=gating,
            sector_allocations=sector_allocations,
            sector_target_weights=sector_target_weights,
            instrument_sectors=self.sectors,
        )
