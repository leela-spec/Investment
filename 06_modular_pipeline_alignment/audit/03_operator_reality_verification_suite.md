# 03: Operator Reality Verification Suite (Anti-Drift & Anti-Facade Diagnostics)

> **PURPOSE**: Provide the operator with an unfalsifiable, deterministic testing battery to prove that external tools and calculations are authentic, physical, and executing genuine code on Windows 11 and WSL2 rather than simulated AI mocks.

---

## 1. Quick One-Line Automated Reality Check

Run the automated reality battery from your terminal at any time:

```powershell
uv run python 06_modular_pipeline_alignment/audit/verify_reality_battery.py
```

*Expected Terminal Receipt:*
```text
================================================================================
 IPOS REALITY VERIFICATION BATTERY — ANTI-FACADE & DRIFT AUDIT
================================================================================
 [PASS] Riskfolio-Lib 7.3.0: Genuine solver executed (version=7.3.0, weight_sum=1.0000, assets=['ASSET_A', 'ASSET_B', 'ASSET_C'])
 [PASS] Wealthfolio Boundary: Strictly fails closed: 'Wealthfolio is not connected; complete E02 native product validation first'
 [PASS] Broker Ledger: 332 activities replayed to exactly 24 open positions matching broker PDF (NDA=1000, PSYC=10000).
 [PASS] Quote Grounding: Word-level grounding verified [10.0s - 11.8s] & injection quarantined.
 [PASS] Weekly Execution: Generated report.html (322350 bytes), snapshot.json (119591 bytes), with buffered staged order tickets.
================================================================================
 SUMMARY: 5 PASSED, 0 FAILED
================================================================================
```

---

## 2. The 5 Diagnostic Tests in Detail

### Test 1: Native Convex Optimization Proof (Riskfolio-Lib 7.3.0)
- **What it checks**: Proves that Riskfolio-Lib is authentically installed and executes real quadratic programming through CVXPY/CLARABEL solvers, rather than returning a mocked dictionary.
- **Manual Command**:
  ```powershell
  uv run python -c "import riskfolio as rp; print('Riskfolio Version:', rp.__version__)"
  ```
- **Falsification Threshold**: If Riskfolio is uninstalled or replaced with a fake wrapper, the import fails or solver receipts do not compute an exact $1.0000$ weight sum.

### Test 2: Wealthfolio Fail-Closed Boundary Proof
- **What it checks**: Proves that the codebase refuses to fake a Wealthfolio REST API or mock desktop backup.
- **Manual Command**:
  ```powershell
  uv run python -c "from ipos.portfolio.wealthfolio import require_real_wealthfolio; require_real_wealthfolio()"
  ```
- **Falsification Threshold**: Must raise `WealthfolioIntegrationUnavailable: "Wealthfolio is not connected; complete E02 native product validation first"`. If this command exits 0 or claims success, an agent has introduced a fake facade!

### Test 3: Official Broker Statement Oracle Replay (Smartbroker 332 Trades $\to$ DAB PDF)
- **What it checks**: Chronologically replays 332 historical transactions from `3370191001-2026-09-24T09-02-24.190Z.csv` and checks them against the official DAB BNP Paribas bank statement PDF (`3370191001-2026-09-25T15-15-35.459Z.pdf`).
- **Manual Command**:
  ```powershell
  uv run pytest tests/test_pp_adapter.py -k "test_07" -v
  ```
- **Falsification Threshold**: If any single position differs by even 0.001 shares (especially Neptune Digital Assets `CA64073L1013` = 1,000 shares or Psyched Wellness `CA74447P1009` = 10,000 shares), the test fails with `DISCREPANCY_DETECTED`.

### Test 4: Engine-Level Database Isolation Proof (PostgreSQL in WSL2)
- **What it checks**: Proves that the shared PostgreSQL cluster (`ki-basis-shared-postgres`) in WSL2 actively denies cross-tenant reads via `REVOKE CONNECT`.
- **Manual Command**:
  ```bash
  wsl -d Ubuntu -u root -- bash c:/GitDev/Investment/06_modular_pipeline_alignment/audit/test_db_isolation.sh
  ```
- **Falsification Threshold**: Out of 36 cross-role connection attempts, exactly 6 authorized database connections must pass and 30 unauthorized attempts must return `FATAL: permission denied for database`.

### Test 5: End-to-End Pipeline & Staged Order Ticket Generation
- **What it checks**: Executes the complete quantitative pipeline and produces interactive artifacts.
- **Manual Command**:
  ```powershell
  uv run python -m ipos.cli weekly --seed-offline --as-of 2026-09-25 --provider none
  ```
- **Operator Verification**:
  Open `data/exports/snapshots/2026-09-25/report.html` in your browser. Verify:
  1. Risk budget is 30.1% (CHOPPY regime, 0.5 scaler).
  2. Euler Percentage Risk Contributions ($RC\%$) rendered across all holdings.
  3. Priority Batch 1 (capital release TRIM/SELL) and Priority Batch 2 (rebalancing BUY) tickets have whole-share quantities and 0.5% limit price buffers.

---

## 3. How to Spot AI Hallucinations in Future Sessions

Enforce these strict rules before accepting any work from future AI sessions:

1. **The "Code First, Markdown Never" Rule**:
   - If an AI claims it "implemented a new tool" or "connected a pipeline", immediately run `git status`.
   - If only files in `docs/` or `.md` files changed, **nothing was implemented**. Demand code changes in `ipos/` or `scripts/`.
2. **The Facade Deletion Test**:
   - Ask the AI: *"If I uninstall this tool or delete this dependency, does your test fail?"* If the test still passes, the test is a self-referential mock.
3. **The 5-Minute Baseline Rule**:
   - Run before and after every working session:
     ```powershell
     uv run pytest
     uv run python scripts/qa_repo.py
     ```
   - Must report 271 passed tests and 204 QA items with 0 errors.
