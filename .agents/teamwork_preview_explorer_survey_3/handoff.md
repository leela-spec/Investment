# World 3 Handoff Report: Legacy Master Plan & Meso Plans Value Extraction

**Document Role:** Self-Contained 5-Component Handoff Report  
**Author / Sender:** Master Plan Legacy Auditor (`teamwork_preview_explorer_survey_3`)  
**Recipient:** Parent Orchestrator (`5a6e3a43-d5d8-4059-847a-5d1e9c30b145`, "parent")  
**Date:** 2026-09-28  
**Working Directory:** `c:\GitDev\Investment\.agents\teamwork_preview_explorer_survey_3`  
**Detailed Audit Deliverable:** `c:\GitDev\Investment\.agents\teamwork_preview_explorer_survey_3\survey_world3_report.md`  

---

## 1. Observation

### 1.1 Scope Boundaries & Input Documents Inspected
- Inspected `c:\GitDev\Investment\.agents\ORIGINAL_REQUEST.md` (lines 1–74).
- Inspected `05_blueprint/00_MASTER_PLAN.md` (lines 1–189, Macro iteration v1.0, dated 2026-07-19).
- Inspected all nine Meso Cluster Plans in `05_blueprint/meso/`:
  - `C1_registry_warehouse.md` (lines 1–53)
  - `C2_ingestion_connectors.md` (lines 1–43)
  - `C3_transform_scoring.md` (lines 1–38)
  - `C4_regime_aggregation.md` (lines 1–36)
  - `C5_playbook_integration.md` (lines 1–40)
  - `C6_snapshot_ai_layer.md` (lines 1–44)
  - `C7_reporting_visualization.md` (lines 1–44)
  - `C8_automation_operations.md` (lines 1–40)
  - `C9_qa_governance.md` (lines 1–34)
- Inspected the August 28 Modular Rebuild research dossiers in `05_blueprint/research/2026-08-28-modular-rebuild/`:
  - `00_README.md`, `01_REVISED_DECISION_MATRIX.md`, `02_ARCHITECTURE.md`, `03_COST_PRIVACY_DATA_BOUNDARIES.md`, `04_TRADINGVIEW_INTEGRATION.md`, `05_HERMES_ORCHESTRATION.md`, `08_USER_STORIES_AND_INTEGRATION_WORKFLOWS.md`, and `HANDOVER_INFRASTRUCTURE_ARCHITECTURE.okf.md`.
- Inspected `docs/architecture/PIPELINE_DECISION_MATRIX.md` (lines 1–169).
- Inspected `00_runbook/WF07_RESEARCH_TO_PORTFOLIO_DECISION_FLOW.md` (lines 1–177).
- Inspected `HANDOVER_INITIAL_PLAN_CONTROL.md` (lines 1–205).

### 1.2 Quantitative Core Code Observations
- **126 Seminar Rules**:
  - In `ipos/advisor/rule_engine.py:557`: verbatim assertion `assert len(RULES) == 126, f"expected 126 rules, have {len(RULES)}"`.
  - Grouped into 8 rulebooks: EQUITY (`R001`–`R018`, lines 128–184), RATES (`R019`–`R036`, lines 186–255), CREDIT (`R037`–`R052`, lines 257–312), FX (`R053`–`R066`, lines 314–360), COMMODITIES (`R067`–`R078`, lines 362–398), POSITIONING/COT (`R079`–`R092`, lines 400–436), MACRO/FUNDAMENTALS (`R093`–`R110`, lines 438–496), and GLOBAL LIQUIDITY (`R111`–`R126`, lines 498–548).
  - Validated against `03_extract/rules.jsonl` via `scripts/qa_repo.py`: "PASS: rules.jsonl: unique ids OK (126)".
- **44 Weekly Process Steps**:
  - In `ipos/advisor/rule_engine.py:565–618`: `PROCESS_STEPS` lists 44 ordered evaluation gates (`S01` through `S44`).
  - Validated against `03_extract/process.jsonl` via `scripts/qa_repo.py`: "PASS: process.jsonl: unique ids OK (44)".
- **Mathematical Scoring Formulas**:
  - `ipos/transforms/scoring.py:37–54`: Tanh-damped z-score formula `score = 50.0 * (math.tanh(z / k) + 1.0)` with `k = 2.0`, centered at 50, strictly bounded to $[0, 100]$, and inverted for `higher_is_better = False`.
  - `ipos/transforms/scoring.py:26–35`: Rolling percentile formula `pct = sum(1 for v in vals if v <= current) / len(vals) * 100.0`.
  - `ipos/transforms/scoring.py:56–64`: Piecewise constant ascending band mapping.
  - `05_blueprint/meso/C3_transform_scoring.md:23`: Confidence composite `0.45 * quality + 0.35 * stability + 0.20 * coherence`.
- **Regime Classification Mechanics**:
  - `ipos/aggregate/regime.py:102–143`: Derives Kaufman efficiency ratio `er = net / gross`, `overlap_index = 1.0 - er`, pivot detection `_pivots(p)`, swing structure `_swing_structure(p)`, and `_retracement_ratio(p)`.
  - `ipos/aggregate/regime.py:25`: `RISK_SCALER = {"CHOPPY": 0.50, "TRENDY": 1.00, "MOMENTUM": 0.75, "UNCERTAIN": 0.40}`.
  - `ipos/aggregate/regime.py:218–220`: Hysteresis filter requiring 2 consecutive weekly confirmations unless confidence $\ge 80.0$.
- **Portfolio Sector Bounds & Asymmetric Gating**:
  - `ipos/portfolio/decision.py:359`: `mult = max(0.20, min(1.80, base_mult))` enforcing strict $[0.20, 1.80]$ sector allocation bounds.
  - `ipos/portfolio/decision.py:355`: Thesis invalidation penalty `base_mult *= 0.80` for active alerts from `data/action_watch_register.json`.
  - `ipos/portfolio/decision.py:180–189`: Asymmetric rebalancing gate where `allow_adds = False` (forcing BUY $\to$ `HOLD (GATED)`) if confidence $< 50.0\%$ or regime is `UNCERTAIN`, while `allow_trims = True` and `allow_sells = True` unconditionally preserve capital.
- **Backtesting & Drawdown Suppression**:
  - `ipos/backtest/engine.py:260–281`: Walk-forward out-of-sample simulation computing realized regime accuracy and relative max drawdown suppression (`(static_dd - scaled_dd) / static_dd * 100`).
- **Warehouse & Parquet Persistence**:
  - `ipos/warehouse/db.py:23–30`: Single-writer DuckDB connection to `data/warehouse.duckdb`.
  - `ipos/etl/base.py:56–71`: Verbatim Parquet archive writer `data/archive/{source_type}/{series_id}/{pull_date}.parquet` using DuckDB native parquet engine.

### 1.3 Test & Verification Execution Results
- `uv run python scripts/qa_repo.py`: Executed with returncode 0. All 204 extraction items (44 process steps, 34 indicators, 126 rules) reconciled against transcripts with zero errors.
- `uv run pytest`: Executed synchronously in background (task-98) with returncode 0. Output: `271 passed, 9 warnings in 224.13s (0:03:44)`.

---

## 2. Logic Chain

1. **Premise 1 (Governing Axiom)**: The core IPOS mandate is *"Code computes everything numeric; the LLM only narrates and orchestrates."* Any component performing quantitative scoring, regime detection, risk budgeting, or portfolio accounting must be deterministic code.
2. **Observation Linking**: The audit revealed that `ipos/advisor/rule_engine.py` (126 rules, 44 steps), `ipos/transforms/scoring.py` (tanh z-score, percentile), `ipos/aggregate/regime.py` (Kaufman ER, ATR change, hysteresis), `ipos/portfolio/decision.py` (sector bounds $[0.20, 1.80]$, asymmetric rebalancing), and `ipos/portfolio/accounting.py` (FIFO tax lots, weighted-average economic cost basis) already execute 100% of the mathematical logic in pure Python without LLM dependencies.
3. **Premise 2 (Zero Over-Engineering & 9P Latency Penalty)**: Physical benchmark evidence from `HANDOVER_INFRASTRUCTURE_ARCHITECTURE.okf.md` demonstrated that executing Python database transactions across WSL2/Docker 9P mounts (`/mnt/c/`) causes 123×–308× file I/O penalties and database lock failures.
4. **Inference**: Therefore, the quantitative IPOS core must **RETAIN** its Windows 11 host Python runtime (`.venv\Scripts\python.exe`) and native NTFS DuckDB storage (`data/warehouse.duckdb`), strictly avoiding containerization for the analytical engine.
5. **Premise 3 (Replace Fragile Scaffolding with Mature Tools)**: Legacy Master Plan proposals included custom web scrapers, bespoke quadratic programming solvers, and custom GUI dashboards. These represented high maintenance burdens and brittle failure modes.
6. **Inference**:
   - Brittle custom scrapers must **TRANSITION** to the Dual-Feed architecture: native institutional APIs (FRED, Stooq, Treasury) backed by **OpenBB Platform Core (ODP)** as a redundant failover.
   - Bespoke quadratic solvers must **TRANSITION** to **Riskfolio-Lib 7.3.0**, which provides audited convex Risk Parity and HRP.
   - Custom portfolio tracking GUIs must **TRANSITION** to **Wealthfolio** desktop app (`%APPDATA%\com.teymz.wealthfolio`) for visual review, while **Portfolio Performance CSVs / `pp_adapter.py`** act as the sovereign IBOR source of truth.
   - Research video/document tracking must **TRANSITION** to **Karakeep** on WSL2 ext4 Docker with **WhisperX** monotonic timestamped quote grounding.
   - Agent orchestration must **TRANSITION** to **Hermes Agent** (`investment` profile), eliminating heavy frameworks (LangGraph, OpenClaw).
7. **Premise 4 (Eliminate Anti-Patterns & Obsolete Scaffolding)**:
   - Fragile unofficial HTML scrapers, multi-container Docker meshes for Python code, split-brain git repositories in WSL2, paid OpenBB Workspace Lite ($2,400/yr), synthetic test mocks, automated broker order submission sockets, and always-on background daemons are all classified as **DEPRECATE**.
8. **Conclusion**: The legacy July 2026 Master Plan and Meso Plans C1–C9 are fully reconciled with the August 28 Modular Rebuild and consolidated WSL2 architecture with zero loss of mathematical fidelity.

---

## 3. Caveats

1. **Active Registry Breadth**: While 120 indicators are fully modeled in `configs/registry_120.yaml`, only 22 indicators are currently active in `configs/registry.yaml` (the walking skeleton). Expanding to the target 60 indicators requires activating the secondary OpenBB ODP connectors and seeding historical Parquet archives (Phase 1 of migration roadmap).
2. **Wealthfolio Integration Boundary**: As documented in Epic E02, Wealthfolio v3.8 desktop app omits certain non-standard holdings (NDA, PSYC) and has an accepted €0.01 cash rounding discrepancy. Therefore, `ipos/portfolio/wealthfolio.py` intentionally fails closed (`INTEGRATION_STATUS = "NOT_CONNECTED"`). Wealthfolio is strictly a visual presentation client; `ipos/portfolio/accounting.py` remains the sovereign IBOR.
3. **TradingView Drawing Export Limitations**: TradingView does not provide a public REST API for programmatically exporting manual chart drawings (trendlines, channels, Fibonacci levels). Manual geometric levels must be maintained in a local chart registry (`US-TV-04`) rather than relying on automated TradingView API sync.
4. **Hermes Agent Profile Verification**: Hermes Agent orchestration profile (`investment`) has completed Maker development but is queued for formal adversarial sign-off by `ipos-proof-verifier` (Maker-Checker / Vier-Augen-Prinzip).

---

## 4. Conclusion

1. **Authoritative Reconciliation Completed**: The Master Plan Reconciliation Matrix (Section 5 of `survey_world3_report.md`) establishes a verified 1:1 mapping for all **126 seminar rules** and **44 process steps**, demonstrating 100% preservation within the active Python codebase.
2. **Clean 3-Way Classification Enforced**:
   - **RETAIN**: Pure Python IPOS engine on Windows host (126 rules, 44 steps, tanh z-scores, regime classifier, sector bounds $[0.20, 1.80]$, asymmetric rebalancing, drawdown suppression, DuckDB warehouse, Parquet archive, multi-currency IBOR, order ticket staging, Action/Watch Register).
   - **TRANSITION**: OpenBB ODP, Karakeep, WhisperX, Riskfolio-Lib 7.3.0, Wealthfolio Desktop, TradingView Pro (Cloud), TA-Lib, Activepieces, Hermes Agent.
   - **DEPRECATE**: Bespoke scrapers, multi-container Docker IPOS mesh, 9P cross-mount filesystems, split-brain clones, LangGraph/OpenClaw, paid OpenBB Workspace Lite, synthetic mocks, automated broker API submission, and always-on background daemons.
3. **Execution Readiness**: The 271-test test suite is green, repository QA is clean, and the 5-phase migration roadmap provides a deterministic path to wire live Karakeep, Hermes MCP, and TradingView webhooks into the production pipeline.

---

## 5. Verification Method

To independently verify the observations, claims, and conclusions of this report, execute the following commands from the repository root (`C:\GitDev\Investment`):

```powershell
# 1. Verify knowledge base extraction parity (must report: ALL REQUIRED TESTS PASSED, 126 rules, 44 process steps)
uv run python scripts/qa_repo.py

# 2. Run the complete automated test battery (must report: 271 passed)
uv run pytest

# 3. Verify rule engine and process steps assertion in Python code (must print: 126 rules, 44 steps, assertion passed)
uv run python -c "
from ipos.advisor.rule_engine import RULES, PROCESS_STEPS
assert len(RULES) == 126
assert len(PROCESS_STEPS) == 44
print(f'Verified: {len(RULES)} rules and {len(PROCESS_STEPS)} process steps loaded successfully.')
"

# 4. Verify test pipeline end-to-end execution offline in < 15 seconds (must exit 0 with status=OK)
uv run python -m ipos.cli weekly --seed-offline --as-of 2026-09-25 --provider none

# 5. Inspect generated survey report and reconciliation matrix
Get-Content -Path .agents\teamwork_preview_explorer_survey_3\survey_world3_report.md -TotalCount 60
```

### Invalidation Conditions
This handoff report and its conclusions shall be considered invalidated if:
1. `uv run python scripts/qa_repo.py` fails to reconcile any of the 126 seminar rules or 44 process steps.
2. Any of the 271 unit/integration tests fail.
3. Numerical calculations (portfolio weights, risk budgets, sector multipliers, or regime labels) are altered by an LLM prompt rather than deterministic Python code.
4. Source files outside the `.agents/teamwork_preview_explorer_survey_3` directory are mutated during this survey.
