# Adversarial Verification Report: IPOS Correction Module C11

**Module**: C11 (Portfolio Normalizer Accounting & Reconciliation Correction, repairs M11)  
**Target Verdict**: `PASS_WITH_LIMITATIONS`  
**Limitations Authorized**: Real ZERO / Smartbroker broker-specific PDF/CSV adapters remain explicitly deferred/blocked due to absent real broker exports; normalizer canonical accounting core is fully proven on golden and adversarial fixtures.

---

## 1. Verdict & Summary
- **Verdict**: `PASS_WITH_LIMITATIONS`
- **Assessment**: The implementation in [normalizer.py](file:///c:/GitDev/Investment/ipos/portfolio/normalizer.py) and [cli.py](file:///c:/GitDev/Investment/ipos/portfolio/cli.py) completely eliminates hardcoded reconciliation flags, implements strict directional cash semantics, establishes proportional economic cost basis relief on sales, enforces non-overlapping fee/tax contracts, separates row validation from ledger reconciliation, and evaluates against a physically independent static ground truth oracle.

---

## 2. Claim Under Test
- **Spec Authority**: [C11_NORMALIZER_CORRECTION.yaml](file:///c:/GitDev/Investment/05_blueprint/research/2026-08-28-modular-rebuild/antigravity-v2/C11_NORMALIZER_CORRECTION.yaml)
- **Target Proof**: [TARGET_PROOF.md](file:///c:/GitDev/Investment/implementation-runs/C11/20260831-132730/TARGET_PROOF.md)
- **Claim**: Replace defective M11 implementation with deterministic portfolio normalizer that:
  1. Computes directional net cash flows ($BUY \rightarrow -(gross+fees+taxes)$, $SELL \rightarrow +(gross-fees-taxes)$, $DIVIDEND \rightarrow +(gross-fees-taxes)$, $FEE \rightarrow -gross$, $TAX \rightarrow -gross$).
  2. Relieves cost basis proportionally on sale transactions.
  3. Evaluates reconciliation dynamically against an independent source control file (`BALANCED` if $\Delta \le 10^{-4}$, `MISMATCH` if $\Delta > 10^{-4}$, `UNVERIFIABLE_NO_SOURCE_CONTROL` if control absent).
  4. Fails loudly on invalid arithmetic or duplicate lineage.

---

## 3. Real Target-System Proof
Runtime code inspection of [normalizer.py](file:///c:/GitDev/Investment/ipos/portfolio/normalizer.py):
- Lines 235–274: Net cash flow and component sums are aggregated across activities applying directional signs.
- Lines 186–203: Weighted-average cost relief `relief_basis = (qty / curr_qty) * curr_basis` correctly reduces basis on `SELL`.
- Lines 284–305: Reconciliation difference `diff = abs(summary_totals["net_cash_flow"] - expected_net)` calculated dynamically; status `BALANCED` or `MISMATCH` determined by comparison. Without control input, status is `UNVERIFIABLE_NO_SOURCE_CONTROL` and `rec_diff = None`.
- Lines 88–123: Row arithmetic validation enforces $gross = qty \times price$ for BUY/SELL, verifies standalone fee/tax constraints (must have fees=0, taxes=0 to prevent double counting), and rejects corrupt types.

---

## 4. Facade-Detection Result
- **Hard-coded reconciliation removal**: Confirmed. Normalizer no longer assigns `reconciliation_difference = 0.0` unconditionally. When run without control, it yields `UNVERIFIABLE_NO_SOURCE_CONTROL`. When run against mismatched control, it yields `MISMATCH` with $\Delta = 520.25$.
- **Dependency / Engine Bypass**: Normalization executes real pandas and arrow serialization; dual runs of `normalize` command produced bitwise identical SHA-256 hashes across all output tables (`activities.csv`, `activities.parquet`, `portfolio_snapshot.csv`, `portfolio_snapshot.parquet`, `reconciliation.json`, `source_manifest.json`).

---

## 5. Test-Oracle Audit
- **Fixture Independence**: [golden_broker_expected.json](file:///c:/GitDev/Investment/tests/fixtures/golden_broker_expected.json) is a hand-calculated static JSON file containing ground-truth values (-5520.25 EUR net cash, 5900.00 buys, 380.00 sells, 15.00 dividends, 8.00 fees, 7.25 taxes, ending SPY basis 5005.00 EUR, ending AAPL basis 540.90 EUR).
- **Oracle derivation**: Not derived from `PortfolioNormalizer` code; test assertions compare actual computed structures against this static fixture.

---

## 6. Implementation Steps Matrix

| Step | Requirement | Status | Evidence |
|---|---|---|---|
| 1 | Read M11 authority & inspect fixtures | `DONE_PROVEN` | Code & fixtures reviewed |
| 2 | Create `TARGET_PROOF.md` | `DONE_PROVEN` | [TARGET_PROOF.md](file:///c:/GitDev/Investment/implementation-runs/C11/20260831-132730/TARGET_PROOF.md) |
| 3 | Create golden fixture & independent oracle | `DONE_PROVEN` | [golden_broker_export.csv](file:///c:/GitDev/Investment/tests/fixtures/golden_broker_export.csv), [golden_broker_expected.json](file:///c:/GitDev/Investment/tests/fixtures/golden_broker_expected.json) |
| 4 | Define directional cash semantics | `DONE_PROVEN` | `normalizer.py:235-266` |
| 5 | Document economic book cost basis | `DONE_PROVEN` | `normalizer.py:186-203` |
| 6 | Derive reconciliation dynamically | `DONE_PROVEN` | `normalizer.py:284-305` |
| 7 | Add mismatch fixture producing non-zero diff | `DONE_PROVEN` | [mismatch_control_expected.json](file:///c:/GitDev/Investment/tests/fixtures/mismatch_control_expected.json) |
| 8 | Keep ZERO/Smartbroker adapters deferred/blocked | `DEFERRED_BY_APPROVED_WAIVER` | Authorized waiver: absent real broker exports |
| 9 | CLI normalize/validate/reconcile dual run hash test | `DONE_PROVEN` | Verified SHA-256 match |
| 10 | Invoke verifier | `DONE_PROVEN` | Independent adversarial verification executed |

---

## 7. Pass Conditions Matrix

| Pass Condition | Named Target Involved? | Independent Evidence | Result |
|---|---|---|---|
| Inconsistent fixture fails reconciliation | Yes | `test_m11_t06` & CLI reconcile return code 1 with `MISMATCH` diff 520.25 | **PASS** |
| Expected balances fixed independently | Yes | `golden_broker_expected.json` static fixture | **PASS** |
| Cash signs & positions match ledger | Yes | `test_m11_t01`, `test_m11_t02`, `test_m11_t08` verify exact amounts | **PASS** |
| No silent drops | Yes | `manifest["total_source_rows"] == manifest["normalized_activities_count"] == 4` | **PASS** |
| Real broker coverage truthful | Yes | Missing broker adapters remain deferred/blocked; no fake adapters | **PASS** |
| Verifier verdict | Yes | `PASS_WITH_LIMITATIONS` | **PASS** |

---

## 8. Independent Reruns & Verification Execution Receipts

1. **Pytest suite execution**:
   - Command: `.venv\Scripts\python.exe -m pytest tests/test_m11_normalizer.py -v`
   - Output: `8 passed in 0.20s` (M11-T01 through M11-T08)
2. **Global test suite execution**:
   - Command: `.venv\Scripts\python.exe -m pytest -v`
   - Output: `23 passed in 0.29s` (zero regressions across test_doctor, test_environment, test_m11_normalizer, test_storage)
3. **CLI Doctor execution**:
   - Command: `.venv\Scripts\python.exe -m ipos.portfolio.cli doctor`
   - Output: `M11 Normalizer Doctor: OK (Python, Pandas, PyArrow ready)` (Exit code 0)
4. **CLI Validate execution**:
   - Valid fixture: Exit code 0, `Validation SUCCESS: 4 canonical activity rows valid.`
   - Invalid fixture: Exit code 1, `Validation FAILED: Row arithmetic error at source_row_id 301: gross 9999.0 != qty 10.0 * price 500.0 (5000.0)`
5. **CLI Reconcile execution**:
   - Balanced control: Exit code 0, status `BALANCED`, difference `0.0`.
   - Without control: Exit code 0, status `UNVERIFIABLE_NO_SOURCE_CONTROL`, difference `null`.
   - Mismatched control: Exit code 1, status `MISMATCH`, difference `520.25`.
6. **Dual Run Hash Determinism**:
   - Normalized `tmp/run1` and `tmp/run2`: All output SHA-256 hashes matched identically across runs.

---

## 9. Negative Tests Audited
- `ROW_ARITHMETIC_INVALID`: [invalid_arithmetic_broker_export.csv](file:///c:/GitDev/Investment/tests/fixtures/invalid_arithmetic_broker_export.csv) raises `ValidationException` (tested in `test_m11_t05`).
- `CORRUPT_SCHEMA`: [corrupt_broker_export.csv](file:///c:/GitDev/Investment/tests/fixtures/corrupt_broker_export.csv) raises `ValidationException` (tested in `test_m11_t05`).
- `STANDALONE_FEE_DOUBLE_COUNTING`: Ambiguous fee with non-zero fee columns raises `ValidationException` with `double-counting` warning (tested in `test_m11_t03`).
- `OVERSELL_PROTECTION`: Selling more shares than held raises `ValidationException: Oversell condition` (verified in `normalizer.py:188`).
- `SOURCE_CONTROL_MISMATCH`: [mismatch_control_expected.json](file:///c:/GitDev/Investment/tests/fixtures/mismatch_control_expected.json) generates `reconciliation_status: "MISMATCH"` and difference 520.25 (tested in `test_m11_t06`).

---

## 10. Deviations / State-Integrity Failures
- None. Implementation is strictly aligned with the C11 specification.

---

## 11. Residual Risks
- Real broker imports (e.g. Smartbroker / ZERO CSV/PDF exports) require broker-specific ingestion adapters once representative real-world export files become available from the operator.
- Cost basis calculation is explicitly documented as Economic / Book Cost Basis (weighted-average relief) and does not model German tax-lot / tax-pot tracking.

---

## 12. Repair Requirement
- None. C11 is verified and accepted under `PASS_WITH_LIMITATIONS`.
