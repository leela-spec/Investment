"""Tests for the Action Matrix Engine (WF-07 Stage 5 / US-07).

Tests cover:
- Graceful handling of empty/missing positions
- Deterministic repeatability
- Arithmetic accuracy of weight deltas and value deltas
- Action categorization (HOLD, TRIM, BUY, SELL)
- Tolerance threshold band behavior
- Regime policy inheritance
- JSON schema compliance
"""

import datetime as dt
import pandas as pd
import pytest

from ipos.export.snapshot import validate
from ipos.portfolio.action_matrix import build_action_matrix, load_instrument_names


@pytest.fixture
def sample_positions():
    return pd.DataFrame([
        {"instrument": "US0079031078", "quantity": 100, "value_eur": 10000.0, "currency": "EUR"},
        {"instrument": "US67066G1040", "quantity": 50, "value_eur": 5000.0, "currency": "EUR"},
        {"instrument": "DE000PS7JX34", "quantity": 10, "value_eur": 1000.0, "currency": "EUR"},
        {"instrument": "XC000A42NLY5", "quantity": 500, "value_eur": 0.0, "currency": "EUR"},
    ])


@pytest.fixture
def sample_mapping():
    return {
        "US0079031078": "EquityRisk",
        "US67066G1040": "EquityRisk",
        "DE000PS7JX34": "Commodities",
        "XC000A42NLY5": "EquityRisk",
    }


@pytest.fixture
def sample_names():
    return {
        "US0079031078": "AMD",
        "US67066G1040": "NVIDIA",
        "DE000PS7JX34": "Gold Mini-Long",
        "XC000A42NLY5": "CVR",
    }


@pytest.fixture
def sample_regime():
    return {
        "label": "UNCERTAIN",
        "risk_scaler": 0.4,
        "base_risk_budget": 50.0,
        "policy_selectors": {
            "position_size": "small",
            "initial_stop": "wide_buffer",
            "trailing_stop": "defensive_quick_exit",
        },
    }


@pytest.fixture
def sample_overall():
    return {
        "risk_budget": 20.0,
        "confidence": 85.0,
        "stance_vector": {"equity": -0.2, "commodities": +0.1},
    }


def test_action_matrix_empty_positions():
    res = build_action_matrix(pd.DataFrame(), {}, {}, {})
    assert res == {"summary": None, "items": []}
    res_none = build_action_matrix(None, {}, {}, {})
    assert res_none == {"summary": None, "items": []}


def test_action_matrix_deterministic_repeatability(sample_positions, sample_regime, sample_overall, sample_mapping, sample_names):
    res1 = build_action_matrix(sample_positions, sample_regime, sample_overall, sample_mapping, sample_names)
    res2 = build_action_matrix(sample_positions, sample_regime, sample_overall, sample_mapping, sample_names)
    assert res1 == res2


def test_action_matrix_delta_arithmetic(sample_positions, sample_regime, sample_overall, sample_mapping, sample_names):
    res = build_action_matrix(sample_positions, sample_regime, sample_overall, sample_mapping, sample_names)
    summary = res["summary"]
    items = res["items"]

    assert summary["total_value_eur"] == 16000.0
    assert summary["target_risk_weight_pct"] == 20.0
    assert summary["target_cash_weight_pct"] == 80.0
    assert summary["target_cash_value_eur"] == 12800.0

    for item in items:
        # Check delta = target - current
        expected_delta_pct = round(item["target_weight_pct"] - item["current_weight_pct"], 2)
        assert item["delta_weight_pct"] == pytest.approx(expected_delta_pct, abs=0.01)
        expected_delta_val = round(item["target_value_eur"] - item["current_value_eur"], 2)
        assert item["delta_value_eur"] == pytest.approx(expected_delta_val, abs=0.01)


def test_action_matrix_action_categorization(sample_positions, sample_regime, sample_overall, sample_mapping, sample_names):
    res = build_action_matrix(sample_positions, sample_regime, sample_overall, sample_mapping, sample_names, threshold_pct=1.0)
    items_by_inst = {it["instrument"]: it for it in res["items"]}

    # AMD is 10k of 16k = 62.5% actual, target is ~12.5% -> Delta ~ -50% -> TRIM
    amd = items_by_inst["US0079031078"]
    assert amd["action"] == "TRIM"
    assert amd["action_units"] < 0
    assert "Trim" in amd["notes"]

    # CVR is 0 value -> HOLD with 0 units
    cvr = items_by_inst["XC000A42NLY5"]
    assert cvr["action"] == "HOLD"
    assert cvr["action_units"] == 0


def test_action_matrix_threshold_tolerance(sample_positions, sample_regime, sample_overall, sample_mapping, sample_names):
    # If threshold is very wide (e.g. 80%), everything within tolerance becomes HOLD
    res = build_action_matrix(sample_positions, sample_regime, sample_overall, sample_mapping, sample_names, threshold_pct=80.0)
    for it in res["items"]:
        assert it["action"] == "HOLD"


def test_action_matrix_policy_inheritance(sample_positions, sample_regime, sample_overall, sample_mapping, sample_names):
    res = build_action_matrix(sample_positions, sample_regime, sample_overall, sample_mapping, sample_names)
    for it in res["items"]:
        assert it["policy_size"] == "small"
        assert it["initial_stop"] == "wide_buffer"
        assert it["trailing_stop"] == "defensive_quick_exit"


def test_action_matrix_in_snapshot_schema_validates(sample_positions, sample_regime, sample_overall, sample_mapping, sample_names):
    res = build_action_matrix(sample_positions, sample_regime, sample_overall, sample_mapping, sample_names)
    # Minimal snapshot matching schema
    snapshot = {
        "schema_version": "1.0",
        "scoring_version": "1.0",
        "as_of": "2026-07-17",
        "overall": {"risk_budget": 20.0, "confidence": 85.0, "stance_vector": {"equity": 0.0}},
        "modules": [{"module": "EquityRisk", "score": 45.0, "confidence": 80.0, "tilt": 0.0}],
        "contradictions": [],
        "top_movers": [],
        "indicators": [],
        "data_quality": {"n_indicators": 0, "n_stale": 0, "n_missing": 0, "stale_series": [], "missing_series": []},
        "flags": {"degraded": False, "has_contradictions": False, "n_high_severity": 0, "synthetic_data": False},
        "action_matrix": res,
    }
    # Must not raise jsonschema.ValidationError
    validate(snapshot)
