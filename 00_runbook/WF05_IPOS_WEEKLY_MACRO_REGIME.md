# Workflow Plan 05: IPOS Autonomous Saturday Macro Indicator Pipeline

**Workflow ID:** WF-05  
**Target Domain:** Quantitative Investment Engine & Regime Allocation  
**Target Repositories:** `Investment/`  
**Cognitive Architecture:** Windows Task Scheduler (`scripts/register_scheduler.ps1`) -> Hermes (`investment` profile) -> Python Engine

---

## 1. Operational Overview
The primary quantitative automation of IPOS. Every Saturday at 05:00, the pipeline pulls the 22 active macro indicators, evaluates 126 seminar rules, commits snapshots to DuckDB, updates the Action/Watch Register, and dispatches a Telegram summary.

---

## 2. Step-by-Step Execution Procedure

1. **Schedule Registration & Verification**:
   - Windows Task Scheduler task `IPOS Weekly Pipeline` holds `-StartWhenAvailable` trigger.
2. **Data Pull & Normalization**:
   - Ingests Yield Curve (10Y-2Y), HY Credit Spreads, Fed Net Liquidity, ISM PMI, CPI YoY.
3. **Rule Engine Evaluation**:
   - `ipos/advisor/rule_engine.py` calculates composite Macro Regime score (Expansion, Slowdown, Contraction, Recovery).
4. **Register Synchronization**:
   - Updates `data/action_watch_register.json`.
   - Strictly enforces IPOS Invariant: No automated broker execution.

---

## 3. Specific Test Run & Verification Protocol

### Test Command: Execute Quantitative Pytest Test Suite
```powershell
cd C:\GitDev\Investment
.venv\Scripts\python.exe -m pytest -q tests/test_regime.py tests/test_scoring.py
```
*Expected Output*: `17 passed in < 25s (100%)`.

---

## 4. Pass / Fail Criteria
* **PASS**: 100% pytest pass rate. No numeric calculations performed by LLM (pure deterministic code).
* **FAIL**: Pytest failures, missing DuckDB tables, or attempt to send live broker orders.

---

## 5. Operator Interaction Points
* **PAUSE & PROMPT**: If the regime score triggers a macro transition (e.g. Expansion -> Slowdown), the agent must prompt the operator to review portfolio hedge recommendations.
