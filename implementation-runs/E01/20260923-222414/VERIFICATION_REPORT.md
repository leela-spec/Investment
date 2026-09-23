# E01 verification report

## Runtime identity

- Python: `C:\GitDev\Investment\.venv\Scripts\python.exe`
- Distribution: `Riskfolio-Lib 7.3.0`
- Imported module: `C:\GitDev\Investment\.venv\Lib\site-packages\riskfolio\__init__.py`
- Official API exercised: `riskfolio.Portfolio.optimization(self, model='Classic', rm='MV', obj='Sharpe', kelly=None, rf=0, l=2, hist=True)`

## Real-product receipt

A seeded 180-observation, three-asset return frame was passed through
`RiskfolioOptimizer.optimize_portfolio`, which constructs and executes the
installed `riskfolio.Portfolio` optimizer with minimum weight 0.10 and maximum
weight 0.60.

```json
{
  "weights": {
    "DIVERSIFIER": 0.2662464273984908,
    "EQUITY": 0.13375357856457534,
    "LOW_VOL": 0.5999999940369339
  },
  "weight_sum": 1.0,
  "constraint_residual": 0.0,
  "optimized_variance": 1.0999498621408691e-05,
  "equal_weight_variance": 2.0206077170266775e-05,
  "independent_oracle_pass": true
}
```

The variance oracle was calculated independently as `w @ returns.cov() @ w`;
it did not reuse a Riskfolio diagnostic or an implementation-authored success
flag.

## Pass-condition matrix

| Pass condition | Real proof | Independent oracle | Verdict |
|---|---|---|---|
| Genuine Riskfolio executes | Imported 7.3.0 from site-packages and invoked `Portfolio.optimization` | Dependency-denial tests make the wrapper fail when Riskfolio calls are unavailable | PASS |
| Solver output is usable without repair | Raw receipt sums to 1.0 and remains within 0.10–0.60 | Direct NumPy checks of identity, finiteness, sum, and bounds | PASS |
| Minimum-variance result is economically meaningful | Riskfolio returned the weights above | Sample-covariance variance is below equal weight | PASS |
| Unresolved FX cannot become EUR | Aggregation raises while a row remains non-EUR | Literal malformed/no-rate fixtures | PASS |
| M11 basis meaning is explicit | Output field is `weighted_average_cost_basis` with basis and valuation currencies | Hand-checked broker fixture; mixed-currency basis is rejected | PASS |
| Wealthfolio facade is absent | Old CSV/JSON/MCP simulation methods were removed | Boundary reports `NOT_CONNECTED` and fails closed pending E02 | PASS |

## Test receipts

- Focused E01 suite: `48 passed`.
- Full repository suite after the final holdings-currency change: `210 passed,
  9 warnings in 243.65s`.
- Warnings are third-party OpenBB/Pydantic deprecations and are unrelated to
  this patch.
- `git diff --check`: clean.

## Adversarial verification

A fresh-context verifier independently ran the full suite, exercised genuine
Riskfolio 7.3.0, and confirmed the FX, M11 currency, and Wealthfolio fail-closed
behavior. It found one blocker: Riskfolio was present in `.venv` but absent from
project dependency metadata and the lock. E01 now declares the exact verified
version in `pyproject.toml` and `uv.lock`. A separate
`uv run --isolated --locked` environment installed 96 locked packages, imported
Riskfolio-Lib 7.3.0, and produced bounded weights
`[0.5999999978, 0.1285290816, 0.2714709205]` summing to 1.0. The verifier
rechecked both findings and marked them resolved.
