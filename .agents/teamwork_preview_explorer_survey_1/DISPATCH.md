## 2026-09-28T08:40:45Z

You are the Pipeline Architecture Explorer for the IPOS project.
Working directory: c:\GitDev\Investment\.agents\teamwork_preview_explorer_survey_1
Identity: Explorer surveying World 1 (IPOS Modular Rebuild Pipeline & WF-07 Decision Flow).

MANDATORY INSTRUCTION: You MUST read the original user request at:
c:\GitDev\Investment\.agents\ORIGINAL_REQUEST.md
before starting your analysis. Do NOT skip reading this file.

OBJECTIVE:
Investigate and document all components of the IPOS Modular Rebuild Pipeline (August 28 – September 2026) and the Research-to-Portfolio Decision Flow (WF-07 Stages 1–6).

INPUT SOURCES:
- c:\GitDev\Investment\.agents\ORIGINAL_REQUEST.md
- c:\GitDev\Investment\05_blueprint\research\2026-08-28-modular-rebuild\ (all documents)
- c:\GitDev\Investment\docs\architecture\PIPELINE_DECISION_MATRIX.md
- c:\GitDev\Investment\00_runbook\WF07_RESEARCH_TO_PORTFOLIO_DECISION_FLOW.md
- c:\GitDev\Investment\00_runbook\extraction_process.md
- c:\GitDev\Investment\HANDOVER_INFRASTRUCTURE_ARCHITECTURE.okf.md
- c:\GitDev\Investment\HANDOVER_RESEARCH_TO_PORTFOLIO_AUDIT.md
- c:\GitDev\Investment\HANDOVER_INITIAL_PLAN_CONTROL.md
- c:\GitDev\Investment\PROJECT_STATE.md and README.md
- Codebase modules: ipos/ (advisor/rule_engine.py, backtest/engine.py, etc.), configs/registry.yaml, configs/registry_120.yaml
- Existing test suite (pytest structure, 271 tests in tests/)

SCOPE BOUNDARIES:
- Read-only exploration! DO NOT write, edit, or delete any source code, tests, or documentation outside your working directory.
- Write only to your working directory: c:\GitDev\Investment\.agents\teamwork_preview_explorer_survey_1/

SPECIFIC INVESTIGATION ITEMS:
1. Detailed inventory of the external toolchain: Riskfolio-Lib 7.3.0, Portfolio Performance, OpenBB Platform Core (ODP), Karakeep, TradingView Pro, Hermes Agent, Activepieces.
2. Step-by-step breakdown of WF-07 Stages 1 through 6:
   - Stage 1: Evidence Custody & Ingestion (Karakeep, raw video/audio/PDF/web)
   - Stage 2: Signal Extraction & Monotonic Quote Grounding (WhisperX, OCR, structured quotes)
   - Stage 3: Thesis Invalidation & Action Watch (Hermes Agent investment profile, action_watch_register.json)
   - Stage 4: Quantitative Stance Engine (Pure Python numerical rule engine, 126 rules, sector bounds [0.20, 1.80])
   - Stage 5: Portfolio Allocation & Action Matrix (Riskfolio-Lib 7.3.0, Portfolio Performance sync)
   - Stage 6: Execution Gate (Sovereign manual limit orders with 0.5% buffers, SMARTBROKER vs ZERO, zero automated broker credentials)
3. Inventory of existing 271 pytest unit/integration tests: test files, categories, dependencies, how they run, and verify they must remain 100% passing.
4. Identification of current pain points, gaps, or undefined interfaces between the Windows Python runtime and containerized tools.

OUTPUT DELIVERABLE:
Write a comprehensive, evidence-backed report to:
`c:\GitDev\Investment\.agents\teamwork_preview_explorer_survey_1\survey_world1_report.md`
and write your self-contained `c:\GitDev\Investment\.agents\teamwork_preview_explorer_survey_1\handoff.md` with:
- Observation (verified facts and file paths)
- Logic Chain (analysis of WF-07 mapping and toolchain interfaces)
- Caveats (assumptions, constraints)
- Conclusion (recommendations for M1-M4)
- Verification Method

Notify the parent orchestrator via send_message when complete.

## 2026-09-28T08:44:21Z

**Context**: World 1 Survey & WF-07 Decision Flow
**Content**: Critical operator guidance received. (1) Anti-overengineering mandate: no speculative desktop GUI in Docker, no 9P cross-mount DBs. (2) Strict technical realities: Pure Python IPOS (Riskfolio-Lib 7.3.0, DuckDB, Action Matrix) runs on Windows 11 Python (.venv); background containers (Karakeep, Activepieces, Hermes) run in WSL2 "Apex" Docker engine; Wealthfolio runs as Windows desktop Electron/Tauri app (%APPDATA%\com.teymz.wealthfolio); TradingView Pro is Cloud via CSV exports & inbound webhooks. (3) Structure findings around concrete User Stories with exact execution environments, file paths, and schemas.
**Action**: Incorporate these technical realities and user story decomposition into your survey_world1_report.md and handoff.md.
