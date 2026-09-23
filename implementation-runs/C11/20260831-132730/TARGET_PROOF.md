# TARGET_PROOF: C11 Deterministic Portfolio Normalizer & Reconciliation

```yaml
target_product: "Deterministic Portfolio Normalizer & Accounting Engine"
expected_version: "C11 (repairs M11)"
official_interface_to_use: "PortfolioNormalizer API & ipos.portfolio.cli CLI (normalize, validate, reconcile, doctor)"
proof_action: "Execute deterministic normalization, validation, and multi-state reconciliation on canonical CSV fixtures, verifying against physically independent ground truth control files."
independent_oracle: "tests/fixtures/golden_broker_expected.json containing manually specified net cash flow (-5520.25 EUR), component sums, and book cost basis."
facade_failure_example: "Hardcoding reconciliation_difference=0.0 or reconciliation_status='BALANCED' without comparing against independent source control totals, or summing gross values without transaction-direction semantics."
```

## Ground Truth Oracle Specification

### 1. Cash Direction Semantics:
- `BUY`: `-(gross + fees + taxes)` where gross = `qty * price`
- `SELL`: `+(gross - fees - taxes)` where gross = `qty * price`
- `DIVIDEND`: `+(gross - fees - taxes)`
- `DEPOSIT`: `+gross`
- `WITHDRAWAL`: `-gross`
- `FEE` (standalone): `-gross` (requires fees=0, taxes=0)
- `TAX` (standalone): `-gross` (requires fees=0, taxes=0)

### 2. Golden Ledger Ground Truth:
- Source Rows: 4 (SPY BUY, AAPL BUY, SPY DIVIDEND, AAPL SELL)
- Total Gross Purchases: 5900.00 EUR
- Total Gross Sales: 380.00 EUR
- Total Gross Dividends: 15.00 EUR
- Total Fees: 8.00 EUR
- Total Taxes: 7.25 EUR
- Expected Net Cash Flow: -5520.25 EUR
- Expected Ending Holdings:
  - SPY (US7846721097): 10.0 units, Book Cost Basis = 5005.00 EUR (500.50/unit)
  - AAPL (US0378331005): 3.0 units (5 - 2), Book Cost Basis = 540.90 EUR (180.30/unit)

### 3. Reconciliation States:
- `BALANCED`: Independent source control provided and matches calculated net cash ($\Delta \le 10^{-4}$).
- `MISMATCH`: Independent source control provided and differs from calculated net cash ($\Delta > 10^{-4}$).
- `UNVERIFIABLE_NO_SOURCE_CONTROL`: No source control provided; engine refuses to claim `BALANCED` merely from internal arithmetic.

### 4. Separate Negative Cases:
- `ROW_ARITHMETIC_INVALID`: Invalid row arithmetic raises `ValidationException`.
- `SOURCE_CONTROL_MISMATCH`: Valid rows but mismatched control file yields `reconciliation_status: "MISMATCH"` and non-zero `reconciliation_difference`.

### 5. Cost-Basis Scope:
- Weighted-average cost relief represents **Economic / Book Cost Basis** only.
- Does not claim to reproduce German broker tax-lot / tax-pot accounting.
- Raw transaction lineage is strictly preserved.
