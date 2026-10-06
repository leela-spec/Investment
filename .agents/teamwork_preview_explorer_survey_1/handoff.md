# Handoff Report: World 1 Pipeline Architecture & WF-07 Decision Flow Survey

**Agent**: Pipeline Architecture Explorer (Teamwork Survey World 1)  
**Date**: 2026-09-28  
**Working Directory**: `c:\GitDev\Investment\.agents\teamwork_preview_explorer_survey_1`  
**Parent Conversation ID**: `5a6e3a43-d5d8-4059-847a-5d1e9c30b145`  
**Handoff Type**: Hard Handoff (Investigation & Survey Complete)  

---

## 1. Observation

Direct verified empirical facts, exact file paths, line numbers, tool commands, and outputs from the codebase:

1. **Pytest Test Battery Baseline**:
   - Command: `uv run pytest -q`
   - Result: `271 passed in 48.32s`, exit code `0`.
   - File count: 34 distinct test files in `tests/` covering Action Matrix (7), AI (9), Calendar (4), Canonical (2), Config (7), Connectors (9), Contradictions (10), ETL (4), Evidence Claims (9), Evidence Ingest (6), Failsafe (3), Forecast (9), Golden (1), Isolation (5), OpenBB (5), Normalizer (14), Wealthfolio (2), Optimizer (14), Technical Engine (4), Macro Decision (6), OHLC Regime (4), Operational Automation (5), Order Staging (6), Portfolio (37), Portfolio Audit Boundary (18), PP Adapter (7), Regime (6), Replay (7), Report HTML (13), Riskfolio Pipeline (10), Scoring (11), Snapshot (12), Stop Gate (3), Warehouse (2).
   - Invariant verified: 100% pass baseline on `main`.

2. **External Toolchain Status on `main`**:
   - **Riskfolio-Lib 7.3.0**: Fully integrated in `ipos/portfolio/optimizer.py:11` (`import riskfolio as rp`), tested by 14 tests in `tests/test_m13_optimizer.py`. Uses convex Risk Parity (`port.rp_optimization`) and HRP (`rp.HCPortfolio`), subject to linear inequality constraints ($A w \le B$). Sockets are blocked during optimization (`tests/test_isolation.py`).
   - **Portfolio Performance**: Native typed adapter implemented in `ipos/portfolio/pp_adapter.py:1-469`. Parses German (`Buchungen.csv`) and English exports, sniffs semicolons/commas and decimal formatting. Verified in Epic E03/E04; replays 332 confirmed activities across Smartbroker and finanzen.net zero to match exactly 24 open holdings (100% MATCH) against official broker statement PDFs, preserving NDA (1,000) and PSYC (10,000).
   - **OpenBB Platform Core (ODP)**: Tested in `tests/test_m10_openbb.py:1-5`. Acts as secondary/failover data feed (C10 Dual-Feed architecture) alongside primary native connectors (`fred.py`, `stooq.py`, `treasury.py`, `yahoo.py`, `dbnomics.py`).
   - **Wealthfolio**: Windows desktop app located at `%APPDATA%\com.teymz.wealthfolio`. In `ipos/portfolio/wealthfolio.py:9-20`, `INTEGRATION_STATUS = "NOT_CONNECTED"` and `require_real_wealthfolio()` raises `WealthfolioIntegrationUnavailable`. Intentionally fails closed due to dropped holdings (NDA, PSYC) and cash discrepancy observed during Epic E02 testing.
   - **Karakeep**: Self-hosted evidence archive. Read-only MCP server / REST API endpoint (`mcp-karakeep-read`). Stores whitepapers, PDFs, and media transcripts with SHA-256 receipts. Zero canonical financial state.
   - **TradingView Pro**: Cloud technical workbench. Used for chart reviews and outbound webhook alerts routed via Activepieces to Hermes. Manual chart-data CSV export. Zero private portfolio holdings or credentials stored in TradingView.
   - **Hermes Agent**: WSL2 container / CLI orchestrator running under `investment` profile. Reads `snapshot.json` and read-only MCPs; writes `data/action_watch_register.json` and narrates weekly `report.md`. Zero numeric authority.
   - **Activepieces**: Self-hosted event intake sidecar in WSL2 Docker. Normalizes WEB.DE, Gmail, and TradingView alerts into common HMAC-signed envelopes.

3. **WF-07 Stages 1–6 Code Grounding**:
   - **Stage 1 (Ingestion & Custody)**: Implemented in `ipos/evidence/ingest.py:98-150` (`discover_research_inbox`) and `implementation-runs/E05/` with SHA-256 custody receipts.
   - **Stage 2 (Quote Grounding & Defanging)**: Implemented in `ipos/evidence/claims.py:71-100` (`verify_quote_grounding` mapping exact word timestamps from WhisperX) and `lines 38-48` (`sanitize_malicious_instruction` defanging prompt injections into `[QUARANTINED_PROMPT_INJECTION: ...]`).
   - **Stage 3 (Thesis Invalidation & Register)**: Implemented in `ipos/evidence/register.py:36-100` (`ActionWatchRegister.upsert_item` enforcing idempotent upserting, BOM-free atomic `.tmp` $\to$ `.json` write, and FSM lifecycle `OPEN` $\to$ `TRIGGERED` $\to$ `RESOLVED`).
   - **Stage 4 (Quantitative Stance Engine & Sector Allocations)**: Implemented in `ipos/advisor/rule_engine.py` (evaluating all 126 seminar rules and 44 process steps in pure Python arithmetic) and `ipos/portfolio/decision.py:301-395` (mapping 6 sector clusters, applying 20% thesis invalidation penalties `base_mult *= 0.80`, clamping multipliers strictly to `[0.20, 1.80]` at line 359, and enforcing asymmetric gating rules).
   - **Stage 5 (Action Matrix Rebalancing)**: Implemented in `ipos/portfolio/action_matrix.py:41-110` (`build_action_matrix` reconciling actual holdings against Riskfolio target weights and macro risk budget, attaching regime trailing stop policies).
   - **Stage 6 (Execution Gate & Order Staging)**: Implemented in `ipos/portfolio/order_staging.py:89-260` (`stage_orders_from_action_matrix` routing to `SMARTBROKER` vs `ZERO`, priority batching Batch 1 Capital Release before Batch 2 Deployment, applying $\pm 0.5\%$ limit price buffers). Zero broker execution code, zero stored credentials, zero execution sockets (`tests/test_isolation.py`).

4. **Infrastructure & Filesystem Reality**:
   - Windows 11 Host NTFS (`C:\GitDev\Investment`): Hosts Python 3.12 `.venv`, DuckDB warehouse (`warehouse.duckdb`), Riskfolio-Lib, and Task Scheduler automation (`scripts/register_scheduler.ps1`, Saturday 06:00, `-StartWhenAvailable`).
   - WSL2 ext4 (`/var/lib/docker/volumes/`): Hosts the "Apex" Docker engine (`ki-basis-shared-postgres`, Karakeep, Activepieces, Hermes).
   - Documented 9P penalty in `HANDOVER_INFRASTRUCTURE_ARCHITECTURE.okf.md:78-85`: Small file creation is 123x slower (14.8 ms vs 0.12 ms), directory traversal is 308x slower (185 ms vs 0.6 ms per 1,000 inodes), concurrent file locks corrupt DuckDB/SQLite.

---

## 2. Logic Chain

1. **Premise**: IPOS requires both high-speed deterministic quantitative execution and resilient qualitative evidence ingestion without performance degradation or data corruption.
2. **From Observation 4 (9P Latency & Locking Failure)**: Running DuckDB or the core quantitative Python engine inside WSL2 over `/mnt/c/` causes a 123x–308x I/O slowdown, high CPU spikes from Windows Defender scanning virtual buffers, and broken database file locks.
3. **Inference**: Therefore, the quantitative engine must execute natively on Windows 11 Python (`.venv`), where a full weekly pipeline run takes $<15$ seconds and has an idle RAM footprint of 0 MB. Concurrently, background containerized tools (Karakeep, Activepieces, Hermes) must remain on native Linux ext4.
4. **From Observation 2 & 3 (Toolchain Roles & WF-07 Codification)**: The end-to-end WF-07 Decision Flow (Stages 1 through 6) is already fully codified in Python on `main` across `ipos/evidence/` and `ipos/portfolio/`. External tools fit naturally into specific stages without replacing IPOS policy:
   - Karakeep & Activepieces handle Stage 1 ingestion plumbing.
   - WhisperX handles Stage 2 transcript alignment; IPOS `claims.py` provides deterministic quote verification.
   - Hermes handles Stage 3 thesis invalidation narration, while `register.py` enforces atomic register persistence.
   - Pure Python rule engine and Riskfolio-Lib 7.3.0 handle Stage 4/5 mathematics.
   - `order_staging.py` handles Stage 6 limit order generation for sovereign human execution at Smartbroker / Zero.
5. **From Observation 1 (271 Pytest Baseline)**: The existing 271 unit and integration tests validate every component of this architecture, from multi-currency FIFO accounting to socket-blocked Riskfolio convex optimization and prompt-injection defense. Any architectural consolidation that breaks these tests or introduces synthetic facades is an unacceptable regression.
6. **From Observation 2 (Wealthfolio Desktop vs Fail-Closed Invariant)**: Because Wealthfolio is an Electron desktop app with documented import discrepancies (omitting NDA and PSYC), it cannot serve as the canonical IBOR. Portfolio Performance (`pp_adapter.py`) and native Python accounting (`accounting.py`) provide 100% verified accounting truth, while Wealthfolio remains an optional visual viewer that safely fails closed.

---

## 3. Caveats

1. **No Source Code Mutation**: In accordance with read-only explorer permissions, no code outside `.agents/teamwork_preview_explorer_survey_1/` was modified during this survey.
2. **Active vs Candidate Indicator Scope**: The active weekly pipeline runs 22 walking skeleton indicators (`configs/registry.yaml`), while the 120-indicator candidate expansion (`configs/registry_120.yaml`) remains in candidate status for Phase 3 graduation.
3. **Wealthfolio GUI Independence**: The current pipeline runs fully headlessly without requiring Wealthfolio to be open or running. Wealthfolio integration remains staged as a visual-only client.
4. **Hermes MCP Transport**: Hermes interaction with the local IPOS register currently operates via CLI / direct file inspection; formalizing a dedicated local stdio MCP server (`mcp-ipos-register`) is an M1/M2 design recommendation.

---

## 4. Conclusion

1. **Architectural Harmonization Is Fully Feasible**: World 1 (the IPOS Modular Rebuild Pipeline on `main`) is not a speculative design; it is a live, working, battle-tested reality with 271 passing tests and zero mock facades.
2. **Strict Boundary Adherence**:
   - Quantitative Core: Native Windows Python (`.venv`) on NTFS.
   - Background Services: WSL2 "Apex" Docker on ext4.
   - Inter-OS Handoff: Content-addressed JSON/Parquet drops and REST/MCP sockets (zero cross-OS 9P database mounts).
   - Ingestion: Portfolio Performance for broker statements; Karakeep + WhisperX for research.
   - Execution: Pure numeric Action Matrix and buffered limit order tickets (`SMARTBROKER` vs `ZERO`) for manual operator execution.
3. **M1–M4 Directives**:
   - **M1**: Codify the ratified cross-stack network topology (ports `8084`, `8086`, `8010`, `8642`, `3000` on `ki-basis-db-net`).
   - **M2**: Formalize fail-closed persistence boundaries with SHA-256 receipts and BOM-free JSON.
   - **M3**: Formally retain the 126 seminar rules and DuckDB warehouse, transition custom optimization to Riskfolio-Lib, and deprecate obsolete scaffolding (TTK drafts, OpenClaw).
   - **M4**: Execute the Phase 3 indicator graduation from `registry_120.yaml` to `registry.yaml`.

---

## 5. Verification Method

To independently reproduce and verify all findings in this report, execute the following commands in PowerShell from `C:\GitDev\Investment`:

1. **Verify Test Suite (271 / 271 Passing)**:
   ```powershell
   uv run pytest
   # Expected output: 271 passed in < 50s, exit code 0
   ```
2. **Verify Repository QA Integrity**:
   ```powershell
   uv run python scripts/qa_repo.py
   # Expected output: 204 items checked (44 process steps, 34 indicators, 126 rules), 0 errors
   ```
3. **Verify End-to-End Pipeline Dry Run**:
   ```powershell
   uv run python -m ipos.cli weekly --seed-offline --as-of 2026-09-25 --provider none
   # Expected output: Weekly pipeline executes cleanly in < 15 seconds, writing snapshot.json and report.html
   ```
4. **Verify Evidence Ingestion CLI**:
   ```powershell
   uv run python -m ipos.cli ingest-evidence
   # Expected output: Ingestion summary displayed with 0 errors
   ```
5. **Verify Zero Execution Leak**:
   ```powershell
   git grep -i "broker_api_secret"
   git grep -i "place_order" ipos/portfolio/order_staging.py
   # Expected output: Zero matches for active broker execution credentials or live execution endpoints
   ```
6. **Inspect Generated Survey Deliverable**:
   - View `c:\GitDev\Investment\.agents\teamwork_preview_explorer_survey_1\survey_world1_report.md`.
