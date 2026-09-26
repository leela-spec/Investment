"""Action Matrix Engine (WF-07 Stage 5 / US-07).

Translates actual broker holdings (Smartbroker & finanzen.net zero) and macro
quantitative signals (Regime, Risk Budget, Stance Vector, and Policy Selectors)
into a concrete, holding-by-holding Action Matrix for sovereign human execution.

Axioms:
1. Deterministic priority: Code computes every delta, target weight, and stop policy.
2. Zero automated execution: Rebalancing output is strictly for manual operator execution.
3. Macro-governed: Portfolio risk allocation is strictly capped by the macro risk budget.
"""

from __future__ import annotations

import datetime as dt
import math
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from ipos.config.load import REPO_ROOT

MAPPING_PATH = REPO_ROOT / "configs" / "portfolio_mapping.yaml"
DEFAULT_REBALANCE_THRESHOLD_PCT = 1.0  # 1% tolerance band to avoid trade churn


def load_instrument_names(path: Path | None = None) -> dict[str, str]:
    """Load human-readable names for portfolio instruments."""
    p = path or MAPPING_PATH
    if not p.exists():
        return {}
    try:
        raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        return dict(raw.get("instrument_names") or {})
    except Exception:
        return {}


def build_action_matrix(
    positions: pd.DataFrame,
    regime_info: dict[str, Any],
    overall_info: dict[str, Any],
    mapping: dict[str, str],
    names: dict[str, str] | None = None,
    *,
    threshold_pct: float = DEFAULT_REBALANCE_THRESHOLD_PCT,
    as_of: dt.date | None = None,
    risk_diagnostics: dict[str, Any] | None = None,
    use_risk_parity: bool = False,
    macro_decision: Any = None,
) -> dict[str, Any]:
    """Generate the deterministic Action Matrix comparing actual holdings against macro targets.

    Args:
        positions: DataFrame[instrument, quantity, value_eur, currency]
        regime_info: dict with label, risk_scaler, policy_selectors
        overall_info: dict with risk_budget, stance_vector
        mapping: dict[instrument -> module_id]
        names: optional dict[instrument -> readable name]
        threshold_pct: minimum weight delta (%) to trigger BUY / TRIM
        as_of: optional date stamp
        risk_diagnostics: optional quantitative Riskfolio-Lib intelligence
        use_risk_parity: if True, target weights within risk budget follow Risk Parity
        macro_decision: optional Stage 4 MacroPortfolioDecision or dict

    Returns:
        dict containing 'summary', 'risk_diagnostics', and 'items' (action rows).
    """
    if positions is None or positions.empty:
        return {"summary": None, "items": []}

    names_map = names if names is not None else load_instrument_names()

    # Total portfolio value in EUR
    total_val = float(positions["value_eur"].sum())
    if total_val <= 0:
        return {"summary": None, "items": []}

    # Macro parameters
    regime_label = regime_info.get("label", "UNCERTAIN")
    risk_scaler = float(regime_info.get("risk_scaler", 1.0) or 1.0)
    risk_budget = float(overall_info.get("risk_budget", 50.0) or 50.0)
    policy = regime_info.get("policy_selectors") or {}
    stance_vector = overall_info.get("stance_vector") or {}

    # Target risk budget: maximum % allocated to active risk assets (equities, commodities, etc.)
    # In defensive / uncertain regimes, the remainder is targeted to cash / capital preservation.
    target_risk_pct = round(min(max(risk_budget, 0.0), 100.0), 2)
    target_cash_pct = round(100.0 - target_risk_pct, 2)
    target_risk_eur = round(total_val * (target_risk_pct / 100.0), 2)
    target_cash_eur = round(total_val * (target_cash_pct / 100.0), 2)

    # Actual position calculations
    pos_df = positions.copy()
    pos_df["current_weight_pct"] = (pos_df["value_eur"] / total_val) * 100.0
    pos_df["module"] = pos_df["instrument"].map(lambda x: mapping.get(x, "Unmapped"))

    # Current risk asset weight (all mapped risk assets)
    actual_risk_val = float(pos_df[pos_df["value_eur"] > 0]["value_eur"].sum())
    actual_risk_pct = round((actual_risk_val / total_val) * 100.0, 2)

    # Macro stance tilt adjustments
    # Dimension mapping: EquityRisk -> equity, Commodities -> commodities
    dim_map = {"EquityRisk": "equity", "Commodities": "commodities"}

    # Group positions by module to allocate target risk budget
    module_groups = pos_df.groupby("module")["value_eur"].sum().to_dict()
    total_mapped_risk_val = sum(v for m, v in module_groups.items() if m != "Unmapped" and v > 0)

    # Compute target module weights
    target_module_pct: dict[str, float] = {}
    if total_mapped_risk_val > 0:
        raw_shares: dict[str, float] = {}
        for mod, val in module_groups.items():
            if mod == "Unmapped" or val <= 0:
                raw_shares[mod] = 0.0
                continue
            base_share = val / total_mapped_risk_val
            stance_dim = dim_map.get(mod, mod.lower())
            tilt = float(stance_vector.get(stance_dim, 0.0) or 0.0)
            # Tilt modulates module share: tilt +0.2 increases share by 20%, -0.2 reduces by 20%
            multiplier = max(0.2, 1.0 + tilt)
            raw_shares[mod] = base_share * multiplier

        total_shares = sum(raw_shares.values())
        for mod, share in raw_shares.items():
            normalized_share = (share / total_shares) if total_shares > 0 else 0.0
            target_module_pct[mod] = target_risk_pct * normalized_share
    else:
        target_module_pct = {}

    # Build asset diagnostics lookup if Riskfolio intelligence is supplied
    from ipos.portfolio.decision import MacroPortfolioDecisionEngine, MacroPortfolioDecision

    if macro_decision is None:
        dec_engine = MacroPortfolioDecisionEngine()
        macro_dec_obj = dec_engine.evaluate_decision(
            positions=positions,
            regime_info=regime_info,
            overall_info=overall_info,
            as_of=as_of,
        )
        macro_decision_dict = macro_dec_obj.to_dict()
    elif isinstance(macro_decision, MacroPortfolioDecision):
        macro_dec_obj = macro_decision
        macro_decision_dict = macro_dec_obj.to_dict()
    elif isinstance(macro_decision, dict):
        macro_dec_obj = None
        macro_decision_dict = macro_decision
    else:
        macro_dec_obj = None
        macro_decision_dict = None

    gating = macro_decision_dict.get("gating", {}) if macro_decision_dict else {}
    allow_adds = gating.get("allow_adds", True)
    inst_sectors = macro_dec_obj.instrument_sectors if macro_dec_obj else (macro_decision_dict.get("instrument_sectors", {}) if macro_decision_dict else {})
    sector_allocs_map = {
        sa["sector_id"]: sa
        for sa in (macro_decision_dict.get("sector_allocations") or [])
    } if macro_decision_dict else {}

    asset_diag_map: dict[str, dict[str, Any]] = {}
    if risk_diagnostics and "asset_diagnostics" in risk_diagnostics:
        for ad in risk_diagnostics["asset_diagnostics"]:
            asset_diag_map[str(ad["instrument"])] = ad

    # Build per-instrument action items
    items: list[dict[str, Any]] = []
    actions_count = {"BUY": 0, "TRIM": 0, "SELL": 0, "HOLD": 0, "HOLD (GATED)": 0}
    net_trim_eur = 0.0
    net_buy_eur = 0.0

    for _, row in pos_df.iterrows():
        inst = str(row["instrument"])
        name = names_map.get(inst, inst)
        module = str(row["module"])
        qty = float(row["quantity"])
        curr_val = float(row["value_eur"])
        curr_wt = float(row["current_weight_pct"])

        unit_price = (curr_val / qty) if qty > 0 and curr_val > 0 else 0.0

        ad = asset_diag_map.get(inst)
        vol_pct = ad.get("volatility_annualized_pct") if ad else None
        rc_pct = ad.get("risk_contribution_pct") if ad else None
        rp_wt = ad.get("risk_parity_weight_pct") if ad else None
        hrp_wt = ad.get("hrp_weight_pct") if ad else None
        skew_ratio = ad.get("risk_skew_ratio") if ad else None
        status = ad.get("status") if ad else None

        # Sector attribution
        sec_id = inst_sectors.get(inst, "OTHER_UNCLASSIFIED")
        sec_info = sector_allocs_map.get(sec_id, {})
        sec_display = sec_info.get("display_name", sec_id.replace("_", " ").title())
        hw_tw = sec_info.get("headwind_tailwind", "NEUTRAL")
        alert_items = sec_info.get("active_register_items", [])

        # Calculate target weight for this instrument
        mod_val = module_groups.get(module, 0.0)
        mod_target_wt = target_module_pct.get(module, 0.0)

        if use_risk_parity and rp_wt is not None and target_risk_pct > 0:
            target_wt = round((rp_wt / 100.0) * target_risk_pct, 2)
        elif mod_val > 0 and mod_target_wt > 0 and curr_val > 0:
            inst_share_of_module = curr_val / mod_val
            target_wt = round(mod_target_wt * inst_share_of_module, 2)
        else:
            target_wt = 0.0

        target_val = round(total_val * (target_wt / 100.0), 2)
        delta_pct = round(target_wt - curr_wt, 2)
        delta_val = round(target_val - curr_val, 2)

        # Action logic with deterministic gating
        if curr_val <= 0 and target_val <= 0:
            action = "HOLD"
            action_units = 0
            notes = "Zero-value holding; no rebalance action needed."
        elif delta_pct < -threshold_pct:
            if target_wt <= 0:
                action = "SELL"
                action_units = -int(round(qty))
                notes = f"Full exit: module {module} unallocated or target zero."
            else:
                action = "TRIM"
                action_units = -int(round(abs(delta_val) / unit_price)) if unit_price > 0 else 0
                notes = f"Trim {abs(delta_pct):.1f}% (€{abs(delta_val):,.0f}) to align with {regime_label} risk budget ({target_risk_pct:.1f}%)."
            net_trim_eur += abs(delta_val)
        elif delta_pct > threshold_pct:
            if not allow_adds:
                action = "HOLD (GATED)"
                action_units = 0
                gating_reasons = "; ".join(gating.get("gating_rationale") or ["Additions gated by macro policy."])
                notes = f"Add gated ({delta_pct:.1f}% / €{delta_val:,.0f}): {gating_reasons}"
            else:
                action = "BUY"
                action_units = int(round(delta_val / unit_price)) if unit_price > 0 else 0
                notes = f"Add {delta_pct:.1f}% (€{delta_val:,.0f}) to reach target allocation."
                net_buy_eur += delta_val
        else:
            action = "HOLD"
            action_units = 0
            notes = f"Holding within ±{threshold_pct:.1f}% tolerance band."

        actions_count[action] += 1

        items.append({
            "instrument": inst,
            "name": name,
            "module": module,
            "sector": sec_id,
            "sector_name": sec_display,
            "headwind_tailwind": hw_tw,
            "active_register_items": alert_items,
            "quantity": qty,
            "unit_price_eur": round(unit_price, 4),
            "current_value_eur": round(curr_val, 2),
            "current_weight_pct": round(curr_wt, 2),
            "target_weight_pct": target_wt,
            "target_value_eur": target_val,
            "delta_weight_pct": delta_pct,
            "delta_value_eur": delta_val,
            "action": action,
            "action_units": action_units,
            "policy_size": policy.get("position_size", "small"),
            "initial_stop": policy.get("initial_stop", "wide_buffer"),
            "trailing_stop": policy.get("trailing_stop", "defensive_quick_exit"),
            "volatility_annualized_pct": vol_pct,
            "risk_contribution_pct": rc_pct,
            "risk_parity_weight_pct": rp_wt,
            "hrp_weight_pct": hrp_wt,
            "risk_skew_ratio": skew_ratio,
            "status": status,
            "notes": notes,
        })

    # Sort items: largest current value first
    items.sort(key=lambda x: -x["current_value_eur"])

    summary = {
        "as_of": as_of.isoformat() if as_of else None,
        "total_value_eur": round(total_val, 2),
        "regime_label": regime_label,
        "risk_scaler": risk_scaler,
        "base_risk_budget": round(float(regime_info.get("base_risk_budget", 0.0) or 0.0), 2),
        "risk_budget": round(risk_budget, 2),
        "actual_risk_weight_pct": actual_risk_pct,
        "target_risk_weight_pct": target_risk_pct,
        "target_cash_weight_pct": target_cash_pct,
        "target_cash_value_eur": target_cash_eur,
        "net_trim_eur": round(net_trim_eur, 2),
        "net_buy_eur": round(net_buy_eur, 2),
        "rebalance_threshold_pct": threshold_pct,
        "actions_count": actions_count,
        "policy_selectors": policy,
        "optimization_mode": "RiskParity" if (use_risk_parity and risk_diagnostics) else "Proportional",
        "riskfolio_enabled": risk_diagnostics is not None,
        "rebalance_gating": gating,
        "allow_adds": allow_adds,
        "gated_adds_count": actions_count.get("HOLD (GATED)", 0),
        "macro_decision": macro_decision_dict,
    }

    return {
        "summary": summary,
        "risk_diagnostics": risk_diagnostics,
        "items": items,
    }
