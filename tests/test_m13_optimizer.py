"""Test suite for Module M13 (Riskfolio-Lib Optimizer Bridge).

Tests M13-T01 through M13-T05 specified in M13_RISKFOLIO.yaml.
"""

import pytest
import numpy as np
import pandas as pd
from ipos.portfolio.optimizer import RiskfolioOptimizer, OptimizationException


@pytest.fixture
def synthetic_returns():
    np.random.seed(123)
    dates = pd.date_range(start="2025-01-01", periods=100, freq="B")
    data = {
        "SPY": np.random.normal(0.0005, 0.01, 100),
        "TLT": np.random.normal(0.0002, 0.008, 100),
        "GLD": np.random.normal(0.0003, 0.012, 100),
        "AAPL": np.random.normal(0.0008, 0.015, 100)
    }
    return pd.DataFrame(data, index=dates)


def test_m13_t01_fixed_inputs_produce_same_weights(synthetic_returns):
    """M13-T01: Same fixed inputs produce same weights within solver tolerance."""
    opt1 = RiskfolioOptimizer(seed=42)
    opt2 = RiskfolioOptimizer(seed=42)
    
    w1, diag1 = opt1.optimize_portfolio(synthetic_returns)
    w2, diag2 = opt2.optimize_portfolio(synthetic_returns)
    
    diff = (w1.iloc[:, 0] - w2.iloc[:, 0]).abs().max()
    assert diff < 1e-5
    assert diag1["solver_status"] == "OPTIMAL"


def test_m13_t02_weights_satisfy_sum_and_bounds(synthetic_returns):
    """M13-T02: Weights satisfy sum = 1.0, bounds, and explicit IPOS constraints."""
    opt = RiskfolioOptimizer(seed=42)
    w, diag = opt.optimize_portfolio(synthetic_returns, min_weight=0.05, max_weight=0.50)
    
    weights = w.iloc[:, 0]
    assert abs(weights.sum() - 1.0) < 1e-3
    assert (weights >= 0.05 - 1e-4).all()
    assert (weights <= 0.50 + 1e-4).all()
    assert diag["constraint_residual"] < 1e-3


def test_m13_t03_infeasible_constraints_fail_explicitly(synthetic_returns):
    """M13-T03: Infeasible constraints return explicit infeasible/error status."""
    opt = RiskfolioOptimizer(seed=42)
    
    # 4 assets with min_weight=0.30 -> sum = 1.20 > 1.0 (Infeasible!)
    with pytest.raises(OptimizationException) as exc_info:
        opt.optimize_portfolio(synthetic_returns, min_weight=0.30)
        
    assert "Infeasible constraints" in str(exc_info.value)


def test_m13_t04_input_perturbation_sensitivity(synthetic_returns):
    """M13-T04: Small input perturbation produces documented sensitivity report."""
    opt = RiskfolioOptimizer(seed=42)
    sens = opt.calculate_sensitivity(synthetic_returns, perturbation=0.005)
    
    assert sens["perturbed_asset"] == "SPY"
    assert "max_weight_shift" in sens
    assert sens["sensitivity_status"] in ["STABLE", "HIGH_SENSITIVITY"]


def test_m13_t05_network_disabled(synthetic_returns):
    """M13-T05: Wrapper runs with network disabled."""
    opt = RiskfolioOptimizer(seed=42)
    _, diag = opt.optimize_portfolio(synthetic_returns)
    
    assert diag["is_network_disabled"] is True
