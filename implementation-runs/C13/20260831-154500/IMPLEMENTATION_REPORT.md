# Implementation Report: C13 Riskfolio-Lib Correction

- **Module**: C13 (repairs M13)
- **Title**: Real Riskfolio-Lib portfolio optimizer correction
- **Target Verdict**: `PASS`
- **Timestamp**: 2026-08-31T15:45:00+02:00
- **Integrity Mode**: `DEVELOPMENT`
- **Installed Package**: `riskfolio-lib==7.3.0` in `.venv`

---

## Target & Invariant Repairs

1. **Eliminated SciPy Facade**: Deleted `from scipy.optimize import minimize` and all SLSQP code from `ipos/portfolio/optimizer.py`.
2. **Direct Riskfolio-Lib Integration**:
   - `rp.Portfolio(returns=returns_df)` container initialization.
   - `port.assets_stats(method_mu="hist", method_cov="hist")` for statistical moment estimation.
   - Explicit linear inequality constraints: `port.ainequality = A` and `port.binequality = B` for asset bounds $[-I; I] w \le [-\text{min\_weight}; \text{max\_weight}]$.
3. **Three Core Pathways Fully Operational**:
   - **MinRisk (Mean-Variance)**: `port.optimization(model='Classic', rm='MV', obj='MinRisk', ...)`
   - **Risk Parity / Risk Budgeting**: `port.rp_optimization(model='Classic', rm='MV', b=b, ...)`
   - **CVaR Tail-Risk Optimization**: `port.optimization(model='Classic', rm='CVaR', obj='MinRisk', ...)`
4. **Anti-Facade Rigor**:
   - AST inspection test (`test_m13_t09_anti_facade_no_scipy_in_module`) confirms zero `scipy.optimize` imports or calls.
   - Import denial / monkeypatch test (`test_m13_t10_anti_facade_riskfolio_denial`) confirms `RiskfolioOptimizer` fails hard when Riskfolio is unavailable rather than falling back.
5. **Independent Oracles & Invariants**:
   - Weights sum to 1.0 within $10^{-4}$.
   - All weights within $[\text{min\_weight}, \text{max\_weight}]$.
   - Variance reduction oracle confirms MinRisk optimal variance $\le$ equal-weight portfolio variance.
   - Deterministic repeatability across identical runs ($\Delta < 10^{-6}$).
   - Zero network egress (`is_network_disabled=True`).

---

## Files Modified / Created

- `ipos/portfolio/optimizer.py`: Real Riskfolio-Lib optimizer implementation.
- `tests/test_m13_optimizer.py`: 10 comprehensive tests covering all pathways and anti-facade checks.
- `implementation-runs/C13/20260831-154500/TARGET_PROOF.md`: Official target proof contract.
- `implementation-runs/C13/20260831-154500/IMPLEMENTATION_REPORT.md`: This execution report.
- `implementation-runs/C13/20260831-154500/VERIFICATION_REPORT.md`: Verification evidence matrix.
- `implementation-runs/C13/20260831-154500/state.json`: State summary.
- `implementation-runs/C13/20260831-154500/test-results.json`: Pytest execution receipts.

---

## Test Execution Summary

All 10 tests in `tests/test_m13_optimizer.py` passed in 5.26s:
- `M13-T01`: Fixed inputs produce same weights deterministically (`diff < 1e-6`)
- `M13-T02`: Weights satisfy sum = 1.0, bounds, and explicit IPOS constraints
- `M13-T03`: Infeasible constraints return explicit error status
- `M13-T04`: Small input perturbation produces sensitivity report
- `M13-T05`: Offline execution (`is_network_disabled: True`)
- `M13-T06`: Risk Parity pathway executes via `rp_optimization`
- `M13-T07`: CVaR pathway executes natively via convex solver
- `M13-T08`: Independent mathematical oracle verifies variance reduction vs equal weight
- `M13-T09`: AST check confirms `scipy.optimize` is completely absent
- `M13-T10`: Denial check confirms explicit failure when Riskfolio is unavailable
