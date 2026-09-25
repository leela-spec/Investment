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

        if w.shape != (n_assets, 1):
            raise OptimizationException(
                f"Riskfolio solver returned unexpected weight shape: {w.shape}"
            )
        if list(w.index) != assets:
            raise OptimizationException(
                "Riskfolio solver returned mismatched asset identity/order"
            )

        # Validate the actual solver receipt. Do not clip or renormalize it:
        # doing so could turn an infeasible/invalid result into a plausible one.
        weights = w.iloc[:, 0].to_numpy(dtype=float)
        if not np.isfinite(weights).all():
            raise OptimizationException("Riskfolio solver returned non-finite weights")
        sum_w = float(np.sum(weights))
        if sum_w <= 0.0:
            raise OptimizationException(f"Riskfolio solver returned invalid weight sum: {sum_w}")
        residual = abs(sum_w - 1.0)
        if residual > 1e-4:
            raise OptimizationException(
                f"Riskfolio solver returned invalid weight sum: {sum_w} != 1.0"
            )
        bound_tolerance = 1e-5
        if (
            (weights < min_weight - bound_tolerance).any()
            or (weights > max_weight + bound_tolerance).any()
        ):
            raise OptimizationException(
                "Riskfolio solver returned weights outside approved bounds"
            )

        df_weights = pd.DataFrame(weights, index=assets, columns=["weights"])

        diagnostics = {
            "solution_status": "SOLUTION_RETURNED",
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
            "network_required": False
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

    def compute_risk_contributions(
        self,
        returns_df: pd.DataFrame,
        weights: pd.Series | pd.DataFrame | np.ndarray,
        annualization_factor: float = 52.0,
    ) -> pd.DataFrame:
        """Calculate asset annualized volatility, marginal risk contribution, and percentage risk contribution.

        Args:
            returns_df: DataFrame of periodic asset returns (columns = asset names)
            weights: Vector or Series of weights matching assets in returns_df
            annualization_factor: Factor to annualize volatility (52 for weekly, 252 for daily)

        Returns:
            DataFrame indexed by asset with columns:
            [weight, volatility_annualized, mrc, rc_absolute, rc_percentage]
        """
        assets = list(returns_df.columns)
        if isinstance(weights, pd.DataFrame):
            w = weights.reindex(assets).iloc[:, 0].to_numpy(dtype=float)
        elif isinstance(weights, pd.Series):
            w = weights.reindex(assets).to_numpy(dtype=float)
        else:
            w = np.asarray(weights, dtype=float)

        if len(w) != len(assets):
            raise OptimizationException(f"Weight vector length ({len(w)}) != assets count ({len(assets)})")

        sum_w = float(np.sum(w))
        if sum_w <= 0.0:
            raise OptimizationException("Weights sum must be positive")
        w_norm = w / sum_w

        cov = returns_df.cov().to_numpy(dtype=float)
        port_variance = float(w_norm.T @ cov @ w_norm)
        port_vol = np.sqrt(max(port_variance, 1e-12))

        # Marginal risk contribution: d(sigma_p)/d(w_i) = (cov @ w)_i / sigma_p
        mrc = (cov @ w_norm) / port_vol
        # Absolute risk contribution: w_i * mrc_i
        rc_abs = w_norm * mrc
        # Percentage risk contribution: rc_abs_i / sigma_p * 100
        rc_pct = (rc_abs / port_vol) * 100.0

        asset_vols = returns_df.std().to_numpy(dtype=float) * np.sqrt(annualization_factor)

        return pd.DataFrame({
            "weight": w_norm,
            "volatility_annualized": asset_vols,
            "mrc": mrc,
            "rc_absolute": rc_abs,
            "rc_percentage": rc_pct,
        }, index=assets)

    def optimize_risk_parity(
        self,
        returns_df: pd.DataFrame,
        b: Optional[pd.DataFrame | np.ndarray] = None,
        min_weight: float = 0.0,
        max_weight: float = 1.0,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Run Riskfolio-Lib convex Risk Parity / Risk Budgeting optimization."""
        return self.optimize_portfolio(
            returns_df=returns_df,
            model="Classic",
            rm="MV",
            obj="RiskParity",
            min_weight=min_weight,
            max_weight=max_weight,
            b=b,
        )

    def optimize_hrp(
        self,
        returns_df: pd.DataFrame,
        codependence: str = "pearson",
        linkage: str = "ward",
        rm: str = "MV",
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Run Riskfolio-Lib Hierarchical Risk Parity (HRP) optimization."""
        assets = list(returns_df.columns)
        n_assets = len(assets)
        if n_assets == 0:
            raise OptimizationException("Empty return series provided for HRP")

        try:
            port = rp.HCPortfolio(returns=returns_df)
            w = port.optimization(
                model="HRP",
                codependence=codependence,
                rm=rm,
                linkage=linkage,
            )
        except Exception as e:
            raise OptimizationException(f"Riskfolio HRP solver failed: {e}") from e

        if w is None or not isinstance(w, pd.DataFrame) or len(w) == 0:
            raise OptimizationException("Riskfolio HRP solver returned empty result")

        weights = w.iloc[:, 0].to_numpy(dtype=float)
        sum_w = float(np.sum(weights))
        df_weights = pd.DataFrame(weights, index=assets, columns=["weights"])

        diagnostics = {
            "solution_status": "SOLUTION_RETURNED",
            "solver_engine": "Riskfolio-Lib-HRP",
            "riskfolio_version": rp.__version__,
            "model": "HRP",
            "codependence": codependence,
            "linkage": linkage,
            "risk_metric": rm,
            "seed": self.seed,
            "assets_count": n_assets,
            "weights_sum": sum_w,
            "network_required": False,
        }
        return df_weights, diagnostics


def compute_risk_contributions(
    returns_df: pd.DataFrame,
    weights: pd.Series | pd.DataFrame | np.ndarray,
    annualization_factor: float = 52.0,
) -> pd.DataFrame:
    """Calculate asset annualized volatility, marginal risk contribution, and percentage risk contribution."""
    return RiskfolioOptimizer().compute_risk_contributions(
        returns_df=returns_df,
        weights=weights,
        annualization_factor=annualization_factor,
    )

