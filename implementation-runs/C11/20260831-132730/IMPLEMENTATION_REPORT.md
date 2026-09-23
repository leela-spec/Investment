# Implementation Report: C11 Normalizer Correction

- **Module**: C11 (repairs M11)
- **Title**: Portfolio normalizer accounting and reconciliation correction
- **Target Verdict**: `PASS_WITH_LIMITATIONS` (Limitations strictly restricted to absent real broker PDF/CSV exports)
- **Timestamp**: 2026-08-31T13:29:30Z

## Target & Invariant Repairs

1. **Independent Oracle**: Created hand-written ground truth fixture `tests/fixtures/golden_broker_expected.json` specifying independent cash flows, fees, taxes, and book cost basis.
2. **Reconciliation Multi-State Engine**: Replaced hardcoded `reconciliation_difference = 0.0` with true difference calculation. Defined 3 states: `BALANCED`, `MISMATCH`, and `UNVERIFIABLE_NO_SOURCE_CONTROL`.
3. **Cash-Direction Semantics**: Strict directional accounting per activity type:
   - BUY: `-(gross + fees + taxes)`
   - SELL: `+(gross - fees - taxes)`
   - DIVIDEND: `+(gross - fees - taxes)`
   - Standalone FEE: `-gross` (requires `fees=0, taxes=0`)
   - Standalone TAX: `-gross` (requires `fees=0, taxes=0`)
4. **Economic / Book Cost Basis Relief**: Proportional cost relief on `SELL` transactions (AAPL 540.90 EUR across 3 remaining shares). Disclaimed German broker tax-lot / tax-pot replication.
5. **Separation of Negative Tests**:
   - `ROW_ARITHMETIC_INVALID`: Raises `ValidationException`.
   - `SOURCE_CONTROL_MISMATCH`: Produces `reconciliation_status = "MISMATCH"` and non-zero difference.

## Files Modified / Created

- `ipos/portfolio/normalizer.py`: Full accounting normalizer with 3-state reconciliation.
- `ipos/portfolio/cli.py`: Updated CLI supporting `--control` and standard exit codes.
- `tests/fixtures/golden_broker_expected.json`: Hand-written independent oracle.
- `tests/fixtures/golden_broker_export.csv`: Golden transaction export.
- `tests/fixtures/invalid_arithmetic_broker_export.csv`: Arithmetic violation fixture.
- `tests/fixtures/mismatch_control_expected.json`: Control discrepancy fixture.
- `tests/test_m11_normalizer.py`: 8 comprehensive tests (M11-T01 through M11-T08).

## Test Results

All 8 tests passing in `tests/test_m11_normalizer.py`.
CLI `normalize`, `validate`, `reconcile`, and `doctor` verified.
