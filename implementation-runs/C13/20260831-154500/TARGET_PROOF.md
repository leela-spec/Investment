# TARGET_PROOF: C13 Real Riskfolio-Lib Optimizer Correction

```yaml
target_product: "Riskfolio-Lib"
expected_version: "7.3.0"
official_interface_to_use: "import riskfolio as rp; rp.Portfolio, port.assets_stats, port.optimization, port.rp_optimization"
proof_action: "Execute deterministic mean-variance (MinRisk, Sharpe), Risk Parity / risk budgeting (rp_optimization), and CVaR optimization under explicit linear inequality constraints (A @ w <= B) natively inside Riskfolio-Lib's convex solvers."
independent_oracle: "Matrix constraint arithmetic (sum=1, bounds), independent sample variance reduction check (w_opt.T @ cov @ w_opt <= w_ew.T @ cov @ w_ew), and anti-facade import denial / AST inspection."
facade_failure_example: "Installing riskfolio-lib but executing optimization via scipy.optimize.minimize(..., method='SLSQP') or custom fallback optimizer."
```

## Target Proof & Execution Boundaries

### 1. Installed Package & Official Surface
- **Target**: `riskfolio-lib==7.3.0`
- **Location**: `.venv/Lib/site-packages/riskfolio`
- **Solver Backends**: CVXPY (CLARABEL, ECOS, OSQP, SCS, CVXOPT)
- **Official Classes/Methods Executed**:
  - `rp.Portfolio(returns=returns_df)`: Portfolio container.
  - `port.assets_stats(method_mu='hist', method_cov='hist')`: Historical mean return and covariance estimation.
  - `port.ainequality = A; port.binequality = B`: Direct linear inequality constraint matrices.
  - `port.optimization(model='Classic', rm='MV', obj='MinRisk'|'Sharpe', rf=rf, hist=True)`: Mean-variance optimization.
  - `port.rp_optimization(model='Classic', rm='MV', rf=rf, b=b, hist=True)`: Risk Parity / risk budgeting optimization.
  - `port.optimization(model='Classic', rm='CVaR', obj='MinRisk'|'Sharpe', rf=rf, hist=True)`: Rockafellar-Uryasev CVaR tail-risk optimization.

### 2. Supported Pathways Verified
1. **MinRisk Mean-Variance**: Minimizes portfolio variance $w^T \Sigma w$ under bounds $\text{min\_weight} \le w_i \le \text{max\_weight}$ and $\sum w_i = 1$.
2. **Risk Parity / Risk Budgeting**: Solves equal risk contribution / budget allocation through `port.rp_optimization()`.
3. **CVaR MinRisk**: Minimizes tail Conditional Value at Risk through `port.optimization(rm='CVaR')`.

### 3. Anti-Facade Invariants
- `scipy.optimize` and `minimize` are completely eliminated from `ipos/portfolio/optimizer.py`.
- Monkeypatching / denying `rp.Portfolio.optimization` causes explicit hard `OptimizationException` rather than silent fallback.

### 4. Independent Oracles
- $\sum_{i=1}^n w_i = 1.0 \pm 10^{-4}$ (independent float sum).
- $\forall i: \text{min\_weight} - 10^{-5} \le w_i \le \text{max\_weight} + 10^{-5}$.
- $w_{\text{MinRisk}}^T \Sigma w_{\text{MinRisk}} \le w_{\text{EqualWeight}}^T \Sigma w_{\text{EqualWeight}}$.
- Low-volatility assets receive higher weight than high-volatility assets in MinRisk.
