"""Unit and regression tests for Riskfolio-Lib portfolio intelligence and Risk Parity (E07).

Tests cover:
- Mathematical accuracy of Marginal & Percentage Risk Contributions (Euler attribution)
- Independent oracle test: analytical 2-asset covariance & risk contributions
- Risk Parity optimization (equal risk contributions verification)
- Hierarchical Risk Parity (HRP) optimization
- In-warehouse return extraction & no future leakage guarantee
- Risk Diagnostics aggregation & status classification (HIGH RISK SKEW, DIVERSIFIER, BALANCED)
- Action Matrix integration with Risk Parity target weights
- Full snapshot schema validation with riskfolio block
"""

import datetime as dt
import duckdb
import numpy as np
import pandas as pd
import pytest
import riskfolio as rp

from ipos.export.snapshot import validate, SNAPSHOT_SCHEMA
from ipos.portfolio.action_matrix import build_action_matrix
from ipos.portfolio.optimizer import (
    RiskfolioOptimizer,
    compute_risk_contributions,
)
from ipos.portfolio.returns import (
    PROXY_SERIES_MAP,
    build_portfolio_return_matrix,
    compute_portfolio_risk_diagnostics,
    get_proxy_returns,
)


@pytest.fixture
def synthetic_multivariate_returns():
    """Deterministic 4-asset synthetic returns with known volatility hierarchy."""
    np.random.seed(42)
    n = 120
    dates = pd.date_range("2025-01-01", periods=n, freq="B")
    # Asset A: low vol (e.g. bonds/gold)
    a = np.random.normal(0.0002, 0.005, n)
    # Asset B: mid vol (e.g. broad equity)
    b = 0.5 * a + np.random.normal(0.0005, 0.010, n)
    # Asset C: high vol (e.g. tech/crypto)
    c = 0.3 * b + np.random.normal(0.0010, 0.025, n)
    # Asset D: moderate vol
    d = np.random.normal(0.0003, 0.012, n)
    return pd.DataFrame({"A": a, "B": b, "C": c, "D": d}, index=dates)


# ==============================================================================
# 1. Independent Mathematical Oracle for Euler Risk Contributions
# ==============================================================================

def test_risk_contributions_independent_oracle():
    """Independent oracle test: analytical 2-asset covariance & risk contributions."""
    sigma_1 = 0.10
    sigma_2 = 0.20
    rho = 0.30
    cov_12 = rho * sigma_1 * sigma_2  # 0.006

    cov = np.array([
        [sigma_1**2, cov_12],
        [cov_12, sigma_2**2]
    ])
    w = np.array([0.60, 0.40])

    # Analytical portfolio variance: w^T Cov w
    port_var = float(w @ cov @ w)
    port_vol = float(np.sqrt(port_var))

    # Analytical marginal risk contributions: Cov w / sigma_p
    mrc = (cov @ w) / port_vol
    # Absolute risk contributions: w_i * MRC_i
    rc = w * mrc
    # Percentage risk contributions: 100 * rc / sigma_p
    rc_pct = 100.0 * (rc / port_vol)

    # Invariants:
    assert abs(rc.sum() - port_vol) < 1e-9
    assert abs(rc_pct.sum() - 100.0) < 1e-9

    # Generate synthetic zero-mean normal returns matching this covariance
    np.random.seed(123)
    n = 100000
    L = np.linalg.cholesky(cov)
    Z = np.random.normal(0, 1, size=(n, 2))
    sim_returns = pd.DataFrame(Z @ L.T, columns=["X1", "X2"])

    # Run compute_risk_contributions
    weights_s = pd.Series([0.60, 0.40], index=["X1", "X2"])
    rc_df = compute_risk_contributions(sim_returns, weights_s, annualization_factor=1.0)

    # Validate against analytical oracle (within Monte Carlo sampling error < 2%)
    assert abs(rc_df.loc["X1", "rc_percentage"] - rc_pct[0]) < 2.0
    assert abs(rc_df.loc["X2", "rc_percentage"] - rc_pct[1]) < 2.0
    assert abs(rc_df["rc_percentage"].sum() - 100.0) < 1e-4


def test_risk_contributions_properties(synthetic_multivariate_returns):
    """Test properties of compute_risk_contributions with multi-asset returns."""
    w = pd.Series([0.25, 0.25, 0.25, 0.25], index=["A", "B", "C", "D"])
    rc_df = compute_risk_contributions(synthetic_multivariate_returns, w, annualization_factor=52.0)

    assert set(rc_df.columns) == {
        "weight", "volatility_annualized", "mrc", "rc_absolute", "rc_percentage"
    }
    # Risk contribution percentage must sum to 100.0%
    assert abs(rc_df["rc_percentage"].sum() - 100.0) < 1e-4

    # High vol asset C should have highest risk contribution when weights are equal
    assert rc_df.loc["C", "rc_percentage"] > rc_df.loc["A", "rc_percentage"]


# ==============================================================================
# 2. Risk Parity & Hierarchical Risk Parity Optimization
# ==============================================================================

def test_optimize_risk_parity_equal_risk_budget(synthetic_multivariate_returns):
    """Risk Parity optimization produces approximately equal risk contributions."""
    opt = RiskfolioOptimizer(seed=42)
    w_rp, diag = opt.optimize_risk_parity(synthetic_multivariate_returns)

    assert diag["solution_status"] == "SOLUTION_RETURNED"
    assert diag["model"] == "Classic"
    assert diag["objective"] == "RiskParity"

    weights = w_rp.iloc[:, 0]
    # Sum of weights is 1.0 within solver tolerance
    assert abs(float(weights.sum()) - 1.0) < 1e-4
    assert (weights >= 0.0).all()

    # Asset A (lowest vol) must have significantly higher capital weight than Asset C (highest vol)
    assert weights["A"] > weights["C"]

    # Compute risk contributions under the RP weights
    rc_df = compute_risk_contributions(synthetic_multivariate_returns, weights)
    # For 4 assets with equal budget, each should contribute ~25% of total risk
    for asset in ["A", "B", "C", "D"]:
        assert abs(rc_df.loc[asset, "rc_percentage"] - 25.0) < 1.0


def test_optimize_risk_parity_bounds(synthetic_multivariate_returns):
    """Risk Parity respects min and max weight bounds."""
    opt = RiskfolioOptimizer(seed=42)
    min_w = 0.10
    max_w = 0.40
    w_rp, _ = opt.optimize_risk_parity(
        synthetic_multivariate_returns, min_weight=min_w, max_weight=max_w
    )
    weights = w_rp.iloc[:, 0]
    assert (weights >= min_w - 1e-5).all()
    assert (weights <= max_w + 1e-5).all()
    assert abs(float(weights.sum()) - 1.0) < 1e-4


def test_optimize_hrp(synthetic_multivariate_returns):
    """Hierarchical Risk Parity (HRP) returns valid non-negative weights."""
    opt = RiskfolioOptimizer(seed=42)
    w_hrp, diag = opt.optimize_hrp(synthetic_multivariate_returns)

    assert diag["solution_status"] == "SOLUTION_RETURNED"
    assert diag["model"] == "HRP"

    weights = w_hrp.iloc[:, 0]
    assert abs(float(weights.sum()) - 1.0) < 1e-4
    assert (weights >= 0.0).all()
    # All assets get positive allocation
    assert (weights > 0.01).all()


# ==============================================================================
# 3. Warehouse Return Extraction & Future Leak Protection
# ==============================================================================

@pytest.fixture
def mock_warehouse():
    """In-memory DuckDB database with mock weekly observations."""
    con = duckdb.connect(":memory:")
    con.execute("""
        CREATE TABLE fact_observation (
            series_id VARCHAR,
            obs_date DATE,
            value DOUBLE
        )
    """)
    dates = pd.date_range("2025-01-03", "2026-09-25", freq="W-FRI")
    for series in ["NDX", "GOLD", "COPPER", "RUT", "DAX", "WTI", "SPX"]:
        base = 100.0
        for i, d in enumerate(dates):
            base *= (1.0 + (np.sin(i * 0.1) * 0.02))
            con.execute(
                "INSERT INTO fact_observation VALUES (?, ?, ?)",
                [series, d.strftime("%Y-%m-%d"), float(base)]
            )
    return con


def test_get_proxy_returns_no_future_leak(mock_warehouse):
    """Ensure observation extraction stops strictly at as_of."""
    as_of = dt.date(2026, 6, 1)
    ret_df = get_proxy_returns(mock_warehouse, as_of=as_of, series_ids=["NDX", "GOLD"])

    assert ret_df is not None
    # Maximum date in index must not exceed as_of
    assert ret_df.index.max().date() <= as_of
    assert "NDX" in ret_df.columns
    assert "GOLD" in ret_df.columns


def test_build_portfolio_return_matrix(mock_warehouse):
    """Test mapping portfolio positions to proxy return matrix."""
    positions = pd.DataFrame([
        {"instrument": "US88023B1035", "quantity": 100, "value_eur": 10000.0},
        {"instrument": "DE000PS7JX34", "quantity": 50, "value_eur": 5000.0},
    ])
    as_of = dt.date(2026, 9, 25)
    ret_df, weights, meta = build_portfolio_return_matrix(positions, mock_warehouse, as_of)

    assert ret_df is not None
    assert "NDX" in ret_df.columns
    assert "GOLD" in ret_df.columns
    assert meta["asset_to_proxy"]["US88023B1035"] == "NDX"
    assert meta["asset_to_proxy"]["DE000PS7JX34"] == "GOLD"


# ==============================================================================
# 4. Risk Diagnostics & Action Matrix Integration
# ==============================================================================

def test_compute_portfolio_risk_diagnostics_integration(mock_warehouse):
    """End-to-end test of compute_portfolio_risk_diagnostics."""
    positions = pd.DataFrame([
        {"instrument": "US88023B1035", "quantity": 100, "value_eur": 10000.0},  # NDX (higher vol)
        {"instrument": "DE000PS7JX34", "quantity": 50, "value_eur": 5000.0},    # GOLD (lower vol)
    ])
    as_of = dt.date(2026, 9, 25)
    names_map = {
        "US88023B1035": "Tempus AI",
        "DE000PS7JX34": "Gold Mini-Long",
    }
    diag = compute_portfolio_risk_diagnostics(positions, mock_warehouse, as_of, names_map=names_map)

    assert diag is not None
    summary = diag["summary"]
    assert "portfolio_volatility_annualized_pct" in summary
    assert "effective_number_of_bets_enc" in summary
    assert summary["effective_number_of_bets_enc"] > 1.0

    items = diag["asset_diagnostics"]
    assert len(items) == 2
    # Verify risk contribution percentage sums to 100%
    total_rc = sum(item["risk_contribution_pct"] for item in items)
    assert abs(total_rc - 100.0) < 1e-4

    # Verify status assignment
    for item in items:
        assert item["status"] in ("HIGH RISK SKEW", "DIVERSIFIER", "BALANCED")
        assert item["name"] in ("Tempus AI", "Gold Mini-Long")


def test_action_matrix_with_risk_parity_weights():
    """Action matrix scales target weights using Risk Parity when enabled."""
    positions = pd.DataFrame([
        {"instrument": "US88023B1035", "quantity": 100, "value_eur": 10000.0, "currency": "EUR"},
        {"instrument": "DE000PS7JX34", "quantity": 50, "value_eur": 5000.0, "currency": "EUR"},
    ])
    mapping = {
        "US88023B1035": "EquityRisk",
        "DE000PS7JX34": "Commodities",
    }
    regime = {
        "label": "UNCERTAIN",
        "risk_scaler": 0.4,
        "base_risk_budget": 50.0,
        "policy_selectors": {"trailing_stop": "defensive_quick_exit"},
    }
    overall = {
        "risk_budget": 20.0,
        "confidence": 80.0,
        "stance_vector": {"equity": 0.0, "commodities": 0.0},
    }
    # Mock risk diagnostics with 40% NDX, 60% GOLD optimal RP weights
    mock_risk_diag = {
        "asset_diagnostics": [
            {
                "instrument": "US88023B1035",
                "volatility_annualized_pct": 25.0,
                "risk_contribution_pct": 75.0,
                "risk_parity_weight_pct": 40.0,
                "risk_skew_ratio": 1.88,
                "status": "HIGH RISK SKEW",
            },
            {
                "instrument": "DE000PS7JX34",
                "volatility_annualized_pct": 12.0,
                "risk_contribution_pct": 25.0,
                "risk_parity_weight_pct": 60.0,
                "risk_skew_ratio": 0.75,
                "status": "DIVERSIFIER",
            }
        ]
    }

    am = build_action_matrix(
        positions,
        regime,
        overall,
        mapping,
        risk_diagnostics=mock_risk_diag,
        use_risk_parity=True,
    )

    items = {item["instrument"]: item for item in am["items"]}
    # Risk budget is 20.0%. RP target for US88023B1035 should be 40% of 20% = 8.0%
    assert items["US88023B1035"]["target_weight_pct"] == 8.0
    # RP target for DE000PS7JX34 should be 60% of 20% = 12.0%
    assert items["DE000PS7JX34"]["target_weight_pct"] == 12.0
    # Diagnostics attached to items
    assert items["US88023B1035"]["risk_skew_ratio"] == 1.88
    assert items["DE000PS7JX34"]["status"] == "DIVERSIFIER"


# ==============================================================================
# 5. Schema Validation
# ==============================================================================

def test_snapshot_schema_accepts_riskfolio_block():
    """Verify that SNAPSHOT_SCHEMA validates a snapshot containing riskfolio."""
    doc = {
        "schema_version": "1.0.0",
        "scoring_version": "1.0.0",
        "as_of": "2026-09-25",
        "regime": {"current": "UNCERTAIN", "risk_scaler": 0.4},
        "overall": {"risk_budget": 20.0, "confidence": 85.0, "stance_vector": {"equity": 0.0}},
        "modules": [
            {"module": "EquityRisk", "score": 45.0, "confidence": 80.0, "tilt": -0.1}
        ],
        "contradictions": [],
        "top_movers": [],
        "indicators": [],
        "data_quality": {"coverage_ratio": 1.0, "staleness_days": 0},
        "flags": {"emergency_cut": False},
        "riskfolio": {
            "summary": {
                "portfolio_volatility_annualized_pct": 16.5,
                "effective_number_of_bets_enc": 4.2,
                "risk_parity_weights": {"NDX": 30.0, "GOLD": 70.0},
            },
            "proxy_diagnostics": {
                "NDX": {
                    "weight_pct": 50.0,
                    "volatility_annualized_pct": 28.5,
                    "risk_contribution_pct": 65.0,
                    "optimal_risk_parity_weight_pct": 30.0,
                }
            },
            "asset_diagnostics": [
                {
                    "instrument": "US88023B1035",
                    "name": "Tempus AI",
                    "proxy": "NDX",
                    "value_eur": 10000.0,
                    "capital_weight_pct": 50.0,
                    "volatility_annualized_pct": 28.5,
                    "risk_contribution_pct": 65.0,
                    "risk_parity_weight_pct": 30.0,
                    "risk_skew_ratio": 1.30,
                    "status": "HIGH RISK SKEW",
                }
            ],
        }
    }
    # Should validate without error
    validate(doc)
