"""Staged Order Generation & Broker Order Tickets (WF-07 Stage 6).

Translates Action Matrix quantitative recommendations (TRIM, BUY, SELL, HOLD, HOLD (GATED))
into structured, broker-routed staged order tickets for sovereign manual execution.

Governing Axioms:
1. Zero automated trade execution: All orders are staged strictly for manual operator execution.
   Zero broker execution APIs, zero stored credentials, zero execution network sockets.
2. Deterministic priority batching:
   - Batch 1 (Capital Release): Defensive SELL and TRIM actions execute first to liberate
     cash and reduce risk exposure.
   - Batch 2 (Capital Deployment): Permitted BUY actions execute second, funded by Batch 1.
3. Pure numeric pricing mechanics: Limit orders with configurable price buffers protect
   against market order slippage and volatility spikes.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import datetime as dt
from pathlib import Path
from typing import Any

import yaml

from ipos.config.load import REPO_ROOT

MAPPING_PATH = REPO_ROOT / "configs" / "portfolio_mapping.yaml"
DEFAULT_PRICE_BUFFER_PCT = 0.5  # 0.5% buffer for limit price protection


def load_broker_mapping(path: Path | None = None) -> dict[str, str]:
    """Load instrument -> broker account routing from portfolio mapping config."""
    p = path or MAPPING_PATH
    if not p.exists():
        return {}
    try:
        raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        return dict(raw.get("broker_accounts") or {})
    except Exception:
        return {}


@dataclass
class OrderTicket:
    """Executable broker order ticket specification for manual operator entry."""

    ticket_id: str
    batch: str
    priority: int
    broker: str
    instrument: str
    name: str
    sector: str
    sector_name: str
    action: str  # "TRIM", "SELL", "BUY"
    shares: int
    reference_price_eur: float
    limit_price_eur: float
    estimated_consideration_eur: float
    order_type: str  # "LIMIT"
    time_in_force: str  # "GFD" (Good For Day) or "GTC"
    trailing_stop_policy: str
    initial_stop_policy: str
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GatedHolding:
    """Record of a rebalancing addition that was gated by macro policy."""

    instrument: str
    name: str
    sector: str
    sector_name: str
    broker: str
    current_value_eur: float
    delta_weight_pct: float
    delta_value_eur: float
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def stage_orders_from_action_matrix(
    action_matrix: dict[str, Any] | None,
    *,
    as_of: dt.date | None = None,
    broker_mapping: dict[str, str] | None = None,
    price_buffer_pct: float = DEFAULT_PRICE_BUFFER_PCT,
    time_in_force: str = "GFD",
) -> dict[str, Any]:
    """Generate staged order tickets from an Action Matrix dictionary.

    Args:
        action_matrix: Action matrix result dict containing 'summary' and 'items'
        as_of: Optional run date stamp
        broker_mapping: Optional dict[instrument -> broker_name]
        price_buffer_pct: Limit price buffer percentage (e.g. 0.5%)
        time_in_force: Order validity (default: GFD)

    Returns:
        Dictionary containing 'summary', 'batch_1_tickets', 'batch_2_tickets',
        'gated_holdings', and 'all_tickets'.
    """
    if not action_matrix or not action_matrix.get("items"):
        return {
            "summary": None,
            "batch_1_tickets": [],
            "batch_2_tickets": [],
            "gated_holdings": [],
            "all_tickets": [],
        }

    brokers = broker_mapping if broker_mapping is not None else load_broker_mapping()
    items = action_matrix.get("items") or []
    summary_in = action_matrix.get("summary") or {}
    regime_label = summary_in.get("regime_label", "UNCERTAIN")

    batch_1_candidates: list[dict[str, Any]] = []
    batch_2_candidates: list[dict[str, Any]] = []
    gated_holdings: list[GatedHolding] = []
    hold_count = 0

    # Categorize items into Batch 1 (TRIM/SELL), Batch 2 (BUY), or Gated
    for item in items:
        action = item.get("action", "HOLD")
        inst = str(item.get("instrument", ""))
        broker = brokers.get(inst, "SMARTBROKER")
        units = int(item.get("action_units", 0) or 0)
        curr_val = float(item.get("current_value_eur", 0.0) or 0.0)
        delta_val = float(item.get("delta_value_eur", 0.0) or 0.0)
        delta_pct = float(item.get("delta_weight_pct", 0.0) or 0.0)
        unit_price = float(item.get("unit_price_eur", 0.0) or 0.0)

        if action in ("TRIM", "SELL"):
            if abs(units) > 0 and unit_price > 0:
                batch_1_candidates.append({
                    "item": item,
                    "broker": broker,
                    "shares": abs(units),
                    "action": action,
                    "sort_key": abs(delta_val),
                })
        elif action == "BUY":
            if units > 0 and unit_price > 0:
                batch_2_candidates.append({
                    "item": item,
                    "broker": broker,
                    "shares": units,
                    "action": action,
                    "sort_key": delta_val,
                })
        elif action == "HOLD (GATED)":
            gated_holdings.append(
                GatedHolding(
                    instrument=inst,
                    name=str(item.get("name", inst)),
                    sector=str(item.get("sector", "OTHER")),
                    sector_name=str(item.get("sector_name", "Other")),
                    broker=broker,
                    current_value_eur=curr_val,
                    delta_weight_pct=delta_pct,
                    delta_value_eur=delta_val,
                    notes=str(item.get("notes", "Additions gated by macro policy")),
                )
            )
        else:
            hold_count += 1

    # Sort Batch 1: Largest capital release first (descending abs(delta_val))
    batch_1_candidates.sort(key=lambda x: -x["sort_key"])

    # Sort Batch 2: Largest capital deployment first (descending delta_val)
    batch_2_candidates.sort(key=lambda x: -x["sort_key"])

    as_of_str = as_of.isoformat() if as_of else dt.date.today().isoformat()
    ticket_seq = 1

    batch_1_tickets: list[OrderTicket] = []
    total_batch_1_release_eur = 0.0

    for cand in batch_1_candidates:
        item = cand["item"]
        inst = str(item.get("instrument", ""))
        unit_price = float(item.get("unit_price_eur", 0.0) or 0.0)
        shares = cand["shares"]
        action = cand["action"]
        broker = cand["broker"]

        # Limit price with downside buffer (guarantees execution price floor)
        limit_price = round(unit_price * (1.0 - price_buffer_pct / 100.0), 4)
        est_val = round(shares * limit_price, 2)
        total_batch_1_release_eur += est_val

        ticket = OrderTicket(
            ticket_id=f"ORD-{as_of_str.replace('-', '')}-{ticket_seq:02d}",
            batch="BATCH_1_CAPITAL_RELEASE",
            priority=ticket_seq,
            broker=broker,
            instrument=inst,
            name=str(item.get("name", inst)),
            sector=str(item.get("sector", "OTHER")),
            sector_name=str(item.get("sector_name", "Other")),
            action=action,
            shares=shares,
            reference_price_eur=unit_price,
            limit_price_eur=limit_price,
            estimated_consideration_eur=est_val,
            order_type="LIMIT",
            time_in_force=time_in_force,
            trailing_stop_policy=str(item.get("trailing_stop", "defensive_quick_exit")),
            initial_stop_policy=str(item.get("initial_stop", "wide_buffer")),
            notes=str(item.get("notes", f"{action} to align with macro budget")),
        )
        batch_1_tickets.append(ticket)
        ticket_seq += 1

    batch_2_tickets: list[OrderTicket] = []
    total_batch_2_deploy_eur = 0.0

    for cand in batch_2_candidates:
        item = cand["item"]
        inst = str(item.get("instrument", ""))
        unit_price = float(item.get("unit_price_eur", 0.0) or 0.0)
        shares = cand["shares"]
        action = cand["action"]
        broker = cand["broker"]

        # Limit price with upside cap (guarantees operator will not pay runaway ask price)
        limit_price = round(unit_price * (1.0 + price_buffer_pct / 100.0), 4)
        est_val = round(shares * limit_price, 2)
        total_batch_2_deploy_eur += est_val

        ticket = OrderTicket(
            ticket_id=f"ORD-{as_of_str.replace('-', '')}-{ticket_seq:02d}",
            batch="BATCH_2_REBALANCE_DEPLOYMENT",
            priority=ticket_seq,
            broker=broker,
            instrument=inst,
            name=str(item.get("name", inst)),
            sector=str(item.get("sector", "OTHER")),
            sector_name=str(item.get("sector_name", "Other")),
            action=action,
            shares=shares,
            reference_price_eur=unit_price,
            limit_price_eur=limit_price,
            estimated_consideration_eur=est_val,
            order_type="LIMIT",
            time_in_force=time_in_force,
            trailing_stop_policy=str(item.get("trailing_stop", "defensive_quick_exit")),
            initial_stop_policy=str(item.get("initial_stop", "wide_buffer")),
            notes=str(item.get("notes", "Add to reach target allocation")),
        )
        batch_2_tickets.append(ticket)
        ticket_seq += 1

    all_tickets = batch_1_tickets + batch_2_tickets

    net_cash_impact = round(total_batch_1_release_eur - total_batch_2_deploy_eur, 2)

    broker_breakdown: dict[str, dict[str, Any]] = {}
    for t in all_tickets:
        b = t.broker
        if b not in broker_breakdown:
            broker_breakdown[b] = {"orders_count": 0, "total_eur": 0.0, "actions": {}}
        broker_breakdown[b]["orders_count"] += 1
        broker_breakdown[b]["total_eur"] = round(broker_breakdown[b]["total_eur"] + t.estimated_consideration_eur, 2)
        broker_breakdown[b]["actions"][t.action] = broker_breakdown[b]["actions"].get(t.action, 0) + 1

    summary = {
        "as_of": as_of_str,
        "regime_label": regime_label,
        "total_tickets_count": len(all_tickets),
        "batch_1_capital_release_count": len(batch_1_tickets),
        "batch_1_estimated_release_eur": round(total_batch_1_release_eur, 2),
        "batch_2_rebalance_deploy_count": len(batch_2_tickets),
        "batch_2_estimated_deploy_eur": round(total_batch_2_deploy_eur, 2),
        "net_estimated_cash_change_eur": net_cash_impact,
        "gated_holdings_count": len(gated_holdings),
        "hold_holdings_count": hold_count,
        "price_buffer_pct": price_buffer_pct,
        "time_in_force": time_in_force,
        "broker_breakdown": broker_breakdown,
        "sovereign_execution_note": (
            "Orders staged strictly for manual operator review and execution on broker portals. "
            "Zero automated trade execution."
        ),
    }

    return {
        "summary": summary,
        "batch_1_tickets": [t.to_dict() for t in batch_1_tickets],
        "batch_2_tickets": [t.to_dict() for t in batch_2_tickets],
        "gated_holdings": [g.to_dict() for g in gated_holdings],
        "all_tickets": [t.to_dict() for t in all_tickets],
    }
