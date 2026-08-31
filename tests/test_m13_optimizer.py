"""Test suite for Module M13 / Correction C13 (Riskfolio-Lib Optimizer Bridge).

Tests M13-T01 through M13-T10 covering deterministic repeatability, constraint satisfaction,
infeasible handling, perturbation sensitivity, offline execution, Risk Parity, CVaR,
independent mathematical oracles, and anti-facade verification.
"""

import ast
import inspect
from unittest.mock import patch
import pytest
import numpy as np
import pandas as pd
import riskfolio as rp
import ipos.portfolio.optimizer as opt_module
from ipos.portfolio.optimizer import RiskfolioOptimizer, OptimizationException


@pytest.fixture
def synthetic_returns():
    np.random.seed(123)
    dates = pd.date_range(start="2025-01-01", periods=100, freq="B")
    data = {
        "SPY": np.random.normal(0.0005, 0.010, 100),
        "TLT": np.random.normal(0.0002, 0.006, 100),
        "GLD": np.random.normal(0.0003, 0.012, 100),
        "AAPL": np.random.normal(0.0008, 0.018, 100)
    }
    return pd.DataFrame(data, index=dates)


def test_m13_t01_fixed_inputs_produce_same_weights(synthetic_returns):
    """M13-T01: Same fixed inputs produce same weights within solver tolerance."""
    opt1 = RiskfolioOptimizer(seed=42)
    opt2 = RiskfolioOptimizer(seed=42)

    w1, diag1 = opt1.optimize_portfolio(synthetic_returns)
    w2, diag2 = opt2.optimize_portfolio(synthetic_returns)

    diff = (w1.iloc[:, 0] - w2.iloc[:, 0]).abs().max()
    assert diff < 1e-6
    assert diag1["solver_status"] == "OPTIMAL"
    assert diag1["solver_engine"] == "Riskfolio-Lib"
    assert "riskfolio_version" in diag1
    assert diag1["riskfolio_version"] == rp.__version__


def test_m13_t02_weights_satisfy_sum_and_bounds(synthetic_returns):
    """M13-T02: Weights satisfy sum = 1.0, bounds, and explicit IPOS constraints."""
    opt = RiskfolioOptimizer(seed=42)
    min_w = 0.05
    max_w = 0.50
    w, diag = opt.optimize_portfolio(synthetic_returns, min_weight=min_w, max_weight=max_w)

    weights = w.iloc[:, 0].values
    # Independent oracle checks
    assert np.isfinite(weights).all()
    assert abs(float(weights.sum()) - 1.0) < 1e-4
    assert (weights >= min_w - 1e-5).all()
    assert (weights <= max_w + 1e-5).all()
    assert diag["constraint_residual"] < 1e-4
    assert diag["weights_sum"] == pytest.approx(1.0, abs=1e-4)


def test_m13_t03_infeasible_constraints_fail_explicitly(synthetic_returns):
    """M13-T03: Infeasible constraints return explicit infeasible/error status."""
    opt = RiskfolioOptimizer(seed=42)

    # 4 assets with min_weight=0.30 -> sum >= 1.20 > 1.0 (Infeasible!)
    with pytest.raises(OptimizationException) as exc_info:
        opt.optimize_portfolio(synthetic_returns, min_weight=0.30)
    assert "Infeasible constraints" in str(exc_info.value)

    # 4 assets with max_weight=0.20 -> sum <= 0.80 < 1.0 (Infeasible!)
    with pytest.raises(OptimizationException) as exc_info2:
        opt.optimize_portfolio(synthetic_returns, max_weight=0.20)
    assert "Infeasible constraints" in str(exc_info2.value)

    # min_weight > max_weight
    with pytest.raises(OptimizationException) as exc_info3:
        opt.optimize_portfolio(synthetic_returns, min_weight=0.40, max_weight=0.30)
    assert "Infeasible constraints" in str(exc_info3.value)


def test_m13_t04_input_perturbation_sensitivity(synthetic_returns):
    """M13-T04: Small input perturbation produces documented sensitivity report."""
    opt = RiskfolioOptimizer(seed=42)
    sens = opt.calculate_sensitivity(synthetic_returns, perturbation=0.005)

    assert sens["perturbed_asset"] == "SPY"
    assert "max_weight_shift" in sens
    assert "mean_weight_shift" in sens
    assert sens["sensitivity_status"] in ["STABLE", "HIGH_SENSITIVITY"]
    assert 0.0 <= sens["max_weight_shift"] <= 1.0


def test_m13_t05_network_disabled(synthetic_returns):
    """M13-T05: Wrapper runs with network disabled."""
    opt = RiskfolioOptimizer(seed=42)
    _, diag = opt.optimize_portfolio(synthetic_returns)

    assert diag["is_network_disabled"] is True
    assert diag["solver_engine"] == "Riskfolio-Lib"


def test_m13_t06_risk_parity_pathway(synthetic_returns):
    """M13-T06: Risk parity / risk budgeting optimization executes via rp_optimization."""
    opt = RiskfolioOptimizer(seed=42)
    w, diag = opt.optimize_portfolio(
        synthetic_returns,
        obj="RiskParity",
        min_weight=0.05,
        max_weight=0.60
    )

    weights = w.iloc[:, 0].values
    assert np.isfinite(weights).all()
    assert abs(float(weights.sum()) - 1.0) < 1e-4
    assert (weights >= 0.05 - 1e-5).all()
    assert (weights <= 0.60 + 1e-5).all()
    assert diag["objective"] == "RiskParity"
    assert diag["solver_engine"] == "Riskfolio-Lib"


def test_m13_t07_cvar_pathway(synthetic_returns):
    """M13-T07: CVaR optimization executes natively through Riskfolio convex solver."""
    opt = RiskfolioOptimizer(seed=42)
    w, diag = opt.optimize_portfolio(
        synthetic_returns,
        rm="CVaR",
        obj="MinRisk",
        min_weight=0.02,
        max_weight=0.80
    )

    weights = w.iloc[:, 0].values
    assert np.isfinite(weights).all()
    assert abs(float(weights.sum()) - 1.0) < 1e-4
    assert (weights >= 0.02 - 1e-5).all()
    assert (weights <= 0.80 + 1e-5).all()
    assert diag["risk_metric"] == "CVaR"
    assert diag["solver_engine"] == "Riskfolio-Lib"


def test_m13_t08_independent_oracle_variance_reduction(synthetic_returns):
    """M13-T08: Independent mathematical oracle verifies MinRisk MV reduces variance vs equal weight."""
    opt = RiskfolioOptimizer(seed=42)
    w_df, _ = opt.optimize_portfolio(synthetic_returns, obj="MinRisk", rm="MV")
    w = w_df.iloc[:, 0].values

    # Compute independent sample covariance matrix
    cov = synthetic_returns.cov().values
    n = len(synthetic_returns.columns)
    w_ew = np.full(n, 1.0 / n)

    var_opt = float(w.T @ cov @ w)
    var_ew = float(w_ew.T @ cov @ w_ew)

    # Independent oracle assertion: optimal min-risk variance <= equal weight variance
    assert var_opt <= var_ew + 1e-6
    # Lowest volatility asset (TLT has lowest std) should receive higher weight than highest volatility (AAPL)
    tlt_idx = list(synthetic_returns.columns).index("TLT")
    aapl_idx = list(synthetic_returns.columns).index("AAPL")
    assert w[tlt_idx] > w[aapl_idx]


def test_m13_t09_anti_facade_no_scipy_in_module():
    """M13-T09: Anti-facade check: scipy.optimize is NOT imported or called in optimizer.py."""
    source = inspect.getsource(opt_module)
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert "scipy" not in alias.name, f"Forbidden import found: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            assert node.module is not None
            assert "scipy" not in node.module, f"Forbidden import from found: {node.module}"

    assert "minimize(" not in source
    assert "SLSQP" not in source


def test_m13_t10_anti_facade_riskfolio_denial(synthetic_returns):
    """M13-T10: Anti-facade check: denying Riskfolio optimization causes explicit hard failure."""
    opt = RiskfolioOptimizer(seed=42)

    with patch.object(rp.Portfolio, "optimization", side_effect=RuntimeError("Riskfolio unavailable")):
        with pytest.raises(OptimizationException) as exc_info:
            opt.optimize_portfolio(synthetic_returns)
        assert "Riskfolio solver failed" in str(exc_info.value)

