"""Tests for WF-07 Stage 6 Staged Order Generation and Broker Order Tickets.

Verifies:
1. Complete broker routing coverage across all holdings (finanzen.net zero vs. Smartbroker+).
2. Deterministic priority batching (Batch 1 capital releases execute before Batch 2 rebalance buys).
3. Pure numeric limit price buffer calculations and whole-share considerations.
4. Gated additions are quarantined from order tickets into gated_holdings.
5. Zero execution leak (strictly zero automated broker APIs, zero credentials, zero sockets).
6. End-to-end integration into snapshot schema and multi-format report templates.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path
import re

import pandas as pd
import pytest

from ipos.portfolio.order_staging import (
    load_broker_mapping,
    stage_orders_from_action_matrix,
    OrderTicket,
    GatedHolding,
)


def test_01_broker_routing_coverage() -> None:
    """All 32 broker holdings and reference assets must have explicit broker routing."""
    brokers = load_broker_mapping()
    assert len(brokers) >= 32, f"Expected at least 32 mapped brokers, got {len(brokers)}"

    # Check key assets
    assert brokers.get("US0079031078") == "ZERO"          # AMD
    assert brokers.get("US67066G1040") == "ZERO"          # NVIDIA
    assert brokers.get("CH0454664027") == "ZERO"          # 21Shares Ethereum
    assert brokers.get("DE000A2YN504") == "SMARTBROKER"  # Knaus Tabbert
    assert brokers.get("DE000MK6QKZ0") == "SMARTBROKER"  # Broadcom Turbo
    assert brokers.get("IE000YYE6WK5") == "SMARTBROKER"  # VanEck Defense
    assert brokers.get("CA64073L1013") == "SMARTBROKER"  # Neptune Digital Assets
    assert brokers.get("CA74447P1009") == "SMARTBROKER"  # Psyched Wellness

    # All values must be valid known brokers
    for inst, broker in brokers.items():
        assert broker in ("ZERO", "SMARTBROKER"), f"Unknown broker {broker} for {inst}"


def test_02_execution_priority_batching() -> None:
    """Batch 1 must contain TRIM/SELL ordered by largest capital release; Batch 2 BUY ordered by deploy."""
    mock_action_matrix = {
        "summary": {
            "regime_label": "TRENDY",
            "total_value_eur": 100000.0,
        },
        "items": [
            {
                "instrument": "US0079031078",
                "name": "AMD",
                "sector": "TECHNOLOGY_AI",
                "sector_name": "Technology, AI & Semiconductors",
                "action": "TRIM",
                "action_units": -50,
                "unit_price_eur": 150.0,
                "current_value_eur": 30000.0,
                "delta_value_eur": -7500.0,
                "delta_weight_pct": -7.5,
                "trailing_stop": "atr_2x",
                "initial_stop": "swing_low",
                "notes": "Trim 7.5% to align with risk budget",
            },
            {
                "instrument": "DE000A2YN504",
                "name": "Knaus Tabbert",
                "sector": "DEFENSE_INDUSTRIALS",
                "sector_name": "Defense & Industrials",
                "action": "SELL",
                "action_units": -200,
                "unit_price_eur": 40.0,
                "current_value_eur": 8000.0,
                "delta_value_eur": -8000.0,
                "delta_weight_pct": -8.0,
                "trailing_stop": "defensive_quick_exit",
                "initial_stop": "wide_buffer",
                "notes": "Full exit",
            },
            {
                "instrument": "IE000YYE6WK5",
                "name": "VanEck Defense ETF",
                "sector": "DEFENSE_INDUSTRIALS",
                "sector_name": "Defense & Industrials",
                "action": "BUY",
                "action_units": 100,
                "unit_price_eur": 30.0,
                "current_value_eur": 5000.0,
                "delta_value_eur": 3000.0,
                "delta_weight_pct": 3.0,
                "trailing_stop": "moving_avg_50d",
                "initial_stop": "swing_low",
                "notes": "Add 3.0% to reach target",
            },
            {
                "instrument": "US67066G1040",
                "name": "NVIDIA Corp",
                "sector": "TECHNOLOGY_AI",
                "sector_name": "Technology, AI & Semiconductors",
                "action": "HOLD",
                "action_units": 0,
                "unit_price_eur": 120.0,
                "current_value_eur": 15000.0,
                "delta_value_eur": 100.0,
                "delta_weight_pct": 0.1,
                "trailing_stop": "atr_2x",
                "notes": "Within tolerance band",
            },
            {
                "instrument": "CH0454664027",
                "name": "21Shares Ethereum",
                "sector": "CRYPTO_DIGITAL_ASSETS",
                "sector_name": "Crypto & Digital Assets",
                "action": "HOLD (GATED)",
                "action_units": 0,
                "unit_price_eur": 25.0,
                "current_value_eur": 4000.0,
                "delta_value_eur": 2500.0,
                "delta_weight_pct": 2.5,
                "trailing_stop": "defensive_quick_exit",
                "notes": "Add gated: Down regime gate restricts additions",
            },
        ],
    }

    staged = stage_orders_from_action_matrix(mock_action_matrix, as_of=dt.date(2026, 9, 25))
    summary = staged["summary"]

    assert summary["total_tickets_count"] == 3
    assert summary["batch_1_capital_release_count"] == 2
    assert summary["batch_2_rebalance_deploy_count"] == 1
    assert summary["gated_holdings_count"] == 1
    assert summary["hold_holdings_count"] == 1

    # Batch 1 ordering: Knaus Tabbert (€8000 release) must precede AMD (€7500 release)
    b1 = staged["batch_1_tickets"]
    assert b1[0]["name"] == "Knaus Tabbert"
    assert b1[0]["priority"] == 1
    assert b1[0]["batch"] == "BATCH_1_CAPITAL_RELEASE"
    assert b1[0]["broker"] == "SMARTBROKER"
    assert b1[0]["shares"] == 200

    assert b1[1]["name"] == "AMD"
    assert b1[1]["priority"] == 2
    assert b1[1]["batch"] == "BATCH_1_CAPITAL_RELEASE"
    assert b1[1]["broker"] == "ZERO"
    assert b1[1]["shares"] == 50

    # Batch 2: VanEck Defense
    b2 = staged["batch_2_tickets"]
    assert b2[0]["name"] == "VanEck Defense ETF"
    assert b2[0]["priority"] == 3
    assert b2[0]["batch"] == "BATCH_2_REBALANCE_DEPLOYMENT"
    assert b2[0]["broker"] == "SMARTBROKER"
    assert b2[0]["shares"] == 100

    # Gated holdings
    gated = staged["gated_holdings"]
    assert len(gated) == 1
    assert gated[0]["name"] == "21Shares Ethereum"
    assert "Down regime gate" in gated[0]["notes"]


def test_03_limit_price_and_consideration_math() -> None:
    """Limit price buffer calculations and estimated considerations must be exact."""
    mock_am = {
        "summary": {"regime_label": "TRENDY"},
        "items": [
            {
                "instrument": "US0079031078",
                "name": "AMD",
                "action": "TRIM",
                "action_units": -10,
                "unit_price_eur": 100.0,
                "delta_value_eur": -1000.0,
            },
            {
                "instrument": "IE000YYE6WK5",
                "name": "Defense",
                "action": "BUY",
                "action_units": 20,
                "unit_price_eur": 50.0,
                "delta_value_eur": 1000.0,
            },
        ],
    }

    # Buffer 0.5%
    staged = stage_orders_from_action_matrix(mock_am, price_buffer_pct=0.5)
    b1 = staged["batch_1_tickets"][0]
    b2 = staged["batch_2_tickets"][0]

    # TRIM limit price: 100 * (1 - 0.005) = 99.50
    assert b1["reference_price_eur"] == 100.0
    assert b1["limit_price_eur"] == 99.50
    assert b1["estimated_consideration_eur"] == 995.0

    # BUY limit price: 50 * (1 + 0.005) = 50.25
    assert b2["reference_price_eur"] == 50.0
    assert b2["limit_price_eur"] == 50.25
    assert b2["estimated_consideration_eur"] == 1005.0

    # Net cash change: +995 - 1005 = -10.00
    assert staged["summary"]["net_estimated_cash_change_eur"] == -10.0


def test_04_gated_items_excluded_from_tickets() -> None:
    """HOLD (GATED) items must never generate executable order tickets."""
    mock_am = {
        "summary": {"regime_label": "UNCERTAIN"},
        "items": [
            {
                "instrument": "US0079031078",
                "name": "AMD",
                "action": "HOLD (GATED)",
                "action_units": 0,
                "unit_price_eur": 150.0,
                "current_value_eur": 5000.0,
                "delta_value_eur": 2000.0,
                "delta_weight_pct": 2.0,
                "notes": "Add gated: Confidence gate < 50.0% prohibits rebalancing additions.",
            }
        ],
    }
    staged = stage_orders_from_action_matrix(mock_am)
    assert len(staged["all_tickets"]) == 0
    assert len(staged["batch_1_tickets"]) == 0
    assert len(staged["batch_2_tickets"]) == 0
    assert len(staged["gated_holdings"]) == 1
    assert staged["summary"]["total_tickets_count"] == 0
    assert staged["summary"]["gated_holdings_count"] == 1


def test_05_zero_execution_leak() -> None:
    """Stage 6 code must contain zero execution sockets, zero credentials, zero broker API calls."""
    staging_file = Path(__file__).resolve().parent.parent / "ipos" / "portfolio" / "order_staging.py"
    code = staging_file.read_text(encoding="utf-8")

    forbidden_patterns = [
        r"broker_api",
        r"api_secret",
        r"api_key",
        r"requests\.post",
        r"requests\.put",
        r"urllib\.request",
        r"http\.client",
        r"socket\.connect",
        r"aiohttp",
        r"httpx\.post",
    ]

    for pat in forbidden_patterns:
        matches = re.findall(pat, code, re.IGNORECASE)
        assert not matches, f"Forbidden execution leak pattern '{pat}' found in order_staging.py: {matches}"


def test_06_snapshot_and_pipeline_integration() -> None:
    """Verify snapshot schema includes staged_orders and validates successfully."""
    from ipos.export.snapshot import SNAPSHOT_SCHEMA, validate
    import jsonschema

    # Check that staged_orders is in SNAPSHOT_SCHEMA properties
    assert "staged_orders" in SNAPSHOT_SCHEMA["properties"]
    assert "batch_1_tickets" in SNAPSHOT_SCHEMA["properties"]["staged_orders"]["properties"]
    assert "batch_2_tickets" in SNAPSHOT_SCHEMA["properties"]["staged_orders"]["properties"]
    assert "gated_holdings" in SNAPSHOT_SCHEMA["properties"]["staged_orders"]["properties"]

    # Verify a minimal valid snapshot with staged_orders validates cleanly
    minimal_snapshot = {
        "schema_version": "1.0",
        "scoring_version": "1.0",
        "as_of": "2026-09-25",
        "overall": {"risk_budget": 50.0, "confidence": 75.0, "stance_vector": {"equity": 0.0}},
        "regime": {"label": "UNCERTAIN", "confidence": 60.0, "risk_scaler": 0.5, "policy_selectors": {}},
        "modules": [],
        "contradictions": [],
        "events": [],
        "top_movers": [],
        "indicators": [],
        "breadth": {},
        "data_quality": {"n_indicators": 0, "n_stale": 0, "n_missing": 0, "stale_series": [], "missing_series": []},
        "flags": {"degraded": False, "has_contradictions": False, "n_high_severity": 0, "synthetic_data": False},
        "staged_orders": {
            "summary": {
                "as_of": "2026-09-25",
                "regime_label": "UNCERTAIN",
                "total_tickets_count": 1,
                "batch_1_capital_release_count": 1,
                "batch_1_estimated_release_eur": 995.0,
                "batch_2_rebalance_deploy_count": 0,
                "batch_2_estimated_deploy_eur": 0.0,
                "net_estimated_cash_change_eur": 995.0,
                "gated_holdings_count": 0,
                "hold_holdings_count": 0,
                "price_buffer_pct": 0.5,
                "time_in_force": "GFD",
                "broker_breakdown": {},
                "sovereign_execution_note": "Zero automated trade execution.",
            },
            "batch_1_tickets": [
                {
                    "ticket_id": "ORD-20260925-01",
                    "batch": "BATCH_1_CAPITAL_RELEASE",
                    "priority": 1,
                    "broker": "SMARTBROKER",
                    "instrument": "DE000A2YN504",
                    "name": "Knaus Tabbert",
                    "sector": "DEFENSE_INDUSTRIALS",
                    "sector_name": "Defense & Industrials",
                    "action": "SELL",
                    "shares": 10,
                    "reference_price_eur": 40.0,
                    "limit_price_eur": 39.80,
                    "estimated_consideration_eur": 398.0,
                    "order_type": "LIMIT",
                    "time_in_force": "GFD",
                    "trailing_stop_policy": "defensive_quick_exit",
                    "initial_stop_policy": "wide_buffer",
                    "notes": "Full exit",
                }
            ],
            "batch_2_tickets": [],
            "gated_holdings": [],
            "all_tickets": [],
        },
    }

    validate(minimal_snapshot)  # Should not raise
