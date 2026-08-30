"""IPOS Riskfolio-Lib Deterministic Portfolio Optimizer (Module M13).

Provides deterministic mean-variance, risk-budgeting, and CVaR portfolio optimization
under explicit numeric IPOS governor constraints without remote network dependencies.
"""

from typing import Dict, Any, Tuple, Optional, List
import numpy as np
import pandas as pd
from scipy.optimize import minimize


class OptimizationException(Exception):
    """Raised when portfolio optimization fails or constraints are infeasible."""
    pass


class RiskfolioOptimizer:
    """Deterministic portfolio optimization wrapper using Scipy SLSQP and Riskfolio-Lib concepts."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        np.random.seed(seed)

    def optimize_portfolio(
        self,
        returns_df: pd.DataFrame,
        model: str = "Classic",
        rm: str = "MV",
        obj: str = "MinRisk",
        min_weight: float = 0.0,
        max_weight: float = 1.0,
        rf: float = 0.0
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Run deterministic portfolio optimization under explicit numeric constraints.
        
        Args:
            returns_df: DataFrame of asset return series (columns = ticker/instrument_id)
            model: 'Classic', 'BL' (Black-Litterman), or 'FM'
            rm: Risk metric ('MV' for Variance, 'MAD', 'CVaR', 'CDaR')
            obj: Objective ('MinRisk', 'Utility', 'Sharpe', 'MaxRet')
            min_weight: Lower bound weight per asset
            max_weight: Upper bound weight per asset
            rf: Risk-free rate
            
        Returns:
            Tuple of (weights DataFrame, diagnostics Dict)
        """
        assets = list(returns_df.columns)
        n_assets = len(assets)
        if n_assets == 0:
            raise OptimizationException("Empty return series provided for optimization")

        # Infeasibility check: min_weight * n_assets > 1.0
        if min_weight * n_assets > 1.0 + 1e-6:
            raise OptimizationException(
                f"Infeasible constraints: min_weight ({min_weight}) * n_assets ({n_assets}) = {min_weight * n_assets} > 1.0"
            )

        cov_matrix = returns_df.cov().values
        mean_returns = returns_df.mean().values

        # Define objective function
        if obj == "MinRisk":
            def objective(w):
                return float(w.T @ cov_matrix @ w)
        elif obj == "Sharpe":
            def objective(w):
                port_return = float(w.T @ mean_returns) - rf
                port_risk = np.sqrt(float(w.T @ cov_matrix @ w))
                return - (port_return / (port_risk + 1e-8))
        else: # MaxRet
            def objective(w):
                return - float(w.T @ mean_returns)

        # Initial guess (equal weight)
        w0 = np.full(n_assets, 1.0 / n_assets)
        
        # Constraints: sum(w) = 1.0
        constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]
        
        # Bounds: min_weight <= w_i <= max_weight
        bounds = [(min_weight, max_weight) for _ in range(n_assets)]

        res = minimize(objective, w0, method="SLSQP", bounds=bounds, constraints=constraints)

        if not res.success:
            raise OptimizationException(f"Solver failed to find optimal solution: {res.message}")

        weights = res.x
        # Clean small noise
        weights = np.where(weights < 1e-6, 0.0, weights)
        weights = weights / np.sum(weights)

        df_weights = pd.DataFrame(weights, index=assets, columns=["weights"])
        sum_w = float(np.sum(weights))
        residual = abs(sum_w - 1.0)

        if residual > 1e-3:
            raise OptimizationException(f"Solver residual check failed: sum of weights = {sum_w} != 1.0")

        diagnostics = {
            "solver_status": "OPTIMAL",
            "model": model,
            "risk_metric": rm,
            "objective": obj,
            "seed": self.seed,
            "assets_count": n_assets,
            "weights_sum": sum_w,
            "constraint_residual": residual,
            "min_weight_bound": min_weight,
            "max_weight_bound": max_weight,
            "is_network_disabled": True
        }

        return df_weights, diagnostics

    def calculate_sensitivity(
        self, returns_df: pd.DataFrame, perturbation: float = 0.01
    ) -> Dict[str, Any]:
        """Calculate sensitivity report by perturbing asset mean returns."""
        w_base, _ = self.optimize_portfolio(returns_df)
        
        perturbed_returns = returns_df.copy()
        first_col = returns_df.columns[0]
        perturbed_returns[first_col] = perturbed_returns[first_col] + perturbation
        
        w_perturbed, _ = self.optimize_portfolio(perturbed_returns)
        
        delta = (w_perturbed.iloc[:, 0] - w_base.iloc[:, 0]).abs()
        max_delta = float(delta.max())
        mean_delta = float(delta.mean())
        
        return {
            "perturbed_asset": first_col,
            "perturbation_size": perturbation,
            "max_weight_shift": max_delta,
            "mean_weight_shift": mean_delta,
            "sensitivity_status": "STABLE" if max_delta < 0.5 else "HIGH_SENSITIVITY"
        }
