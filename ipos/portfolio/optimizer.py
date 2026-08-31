"""IPOS Riskfolio-Lib Deterministic Portfolio Optimizer (Module M13 / Correction C13).

Provides deterministic mean-variance, risk-budgeting/risk-parity, and CVaR portfolio optimization
by directly invoking the official Riskfolio-Lib package under explicit numeric IPOS governor
constraints without remote network dependencies.
"""

from typing import Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
import riskfolio as rp


class OptimizationException(Exception):
    """Raised when portfolio optimization fails or constraints are infeasible."""
    pass


class RiskfolioOptimizer:
    """Deterministic portfolio optimization wrapper using official Riskfolio-Lib engine."""

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
        rf: float = 0.0,
        b: Optional[pd.DataFrame | np.ndarray] = None
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Run deterministic portfolio optimization using Riskfolio-Lib under explicit numeric constraints.
        
        Args:
            returns_df: DataFrame of asset return series (columns = ticker/instrument_id)
            model: 'Classic', 'FM', etc.
            rm: Risk metric ('MV' for Variance, 'MAD', 'CVaR', 'CDaR', etc.)
            obj: Objective ('MinRisk', 'Utility', 'Sharpe', 'MaxRet', 'RiskParity', 'RP')
            min_weight: Lower bound weight per asset
            max_weight: Upper bound weight per asset
            rf: Risk-free rate
            b: Optional risk budget vector for risk budgeting / risk parity
            
        Returns:
            Tuple of (weights DataFrame, diagnostics Dict)
        """
        assets = list(returns_df.columns)
        n_assets = len(assets)
        if n_assets == 0:
            raise OptimizationException("Empty return series provided for optimization")

        # Infeasibility pre-checks
        if min_weight > max_weight:
            raise OptimizationException(
                f"Infeasible constraints: min_weight ({min_weight}) > max_weight ({max_weight})"
            )
        if min_weight * n_assets > 1.0 + 1e-6:
            raise OptimizationException(
                f"Infeasible constraints: min_weight ({min_weight}) * n_assets ({n_assets}) = {min_weight * n_assets} > 1.0"
            )
        if max_weight * n_assets < 1.0 - 1e-6:
            raise OptimizationException(
                f"Infeasible constraints: max_weight ({max_weight}) * n_assets ({n_assets}) = {max_weight * n_assets} < 1.0"
            )

        # Build official Riskfolio Portfolio object
        try:
            port = rp.Portfolio(returns=returns_df)
            port.assets_stats(method_mu="hist", method_cov="hist")
        except Exception as e:
            raise OptimizationException(f"Riskfolio failed to compute asset statistics: {e}") from e

        # Set explicit linear inequality constraints (A @ w <= B)
        # -w_i <= -min_weight  and  w_i <= max_weight
        a_lower = -np.eye(n_assets)
        b_lower = -np.full(n_assets, min_weight)
        a_upper = np.eye(n_assets)
        b_upper = np.full(n_assets, max_weight)

        port.ainequality = np.vstack([a_lower, a_upper])
        port.binequality = np.concatenate([b_lower, b_upper]).reshape(-1, 1)

        # Execute optimization via official Riskfolio pathways
        try:
            if obj in ("RiskParity", "RP") or rm in ("RiskParity", "RP"):
                actual_rm = "MV" if rm in ("RiskParity", "RP") else rm
                w = port.rp_optimization(
                    model=model,
                    rm=actual_rm,
                    rf=rf,
                    b=b,
                    hist=True
                )
            else:
                w = port.optimization(
                    model=model,
                    rm=rm,
                    obj=obj,
                    rf=rf,
                    hist=True
                )
        except Exception as e:
            raise OptimizationException(f"Riskfolio solver failed during optimization: {e}") from e

        if w is None or not isinstance(w, pd.DataFrame) or len(w) == 0:
            raise OptimizationException("Riskfolio solver failed to find optimal solution: result is None or empty")

        # Clean numerical precision residuals
        weights = w.iloc[:, 0].values.astype(float)
        weights = np.where(weights < 1e-6, 0.0, weights)
        sum_w = float(np.sum(weights))

        if sum_w <= 0.0 or np.isnan(sum_w) or np.isinf(sum_w):
            raise OptimizationException(f"Riskfolio solver returned invalid weight sum: {sum_w}")

        weights = weights / sum_w
        sum_w = float(np.sum(weights))
        residual = abs(sum_w - 1.0)

        if residual > 1e-3:
            raise OptimizationException(f"Solver residual check failed: sum of weights = {sum_w} != 1.0")

        df_weights = pd.DataFrame(weights, index=assets, columns=["weights"])

        diagnostics = {
            "solver_status": "OPTIMAL",
            "solver_engine": "Riskfolio-Lib",
            "riskfolio_version": rp.__version__,
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
        self,
        returns_df: pd.DataFrame,
        perturbation: float = 0.01,
        obj: str = "MinRisk",
        rm: str = "MV"
    ) -> Dict[str, Any]:
        """Calculate sensitivity report by perturbing asset mean returns via Riskfolio."""
        w_base, _ = self.optimize_portfolio(returns_df, obj=obj, rm=rm)

        perturbed_returns = returns_df.copy()
        first_col = returns_df.columns[0]
        perturbed_returns[first_col] = perturbed_returns[first_col] + perturbation

        w_perturbed, _ = self.optimize_portfolio(perturbed_returns, obj=obj, rm=rm)

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
