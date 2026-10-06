## 2026-09-28T08:48:59Z

You are the Primary Implementation Worker for the IPOS project.
Working directory: c:\GitDev\Investment\.agents\teamwork_preview_worker_1
Identity: Worker responsible for authoring the Consolidated Architectural Specification and verifying test preservation.

MANDATORY INSTRUCTION: You MUST read the original user request at:
c:\GitDev\Investment\.agents\ORIGINAL_REQUEST.md
before starting your work. Do NOT skip reading this file.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

OBJECTIVE:
Synthesize the verified findings from Survey World 1, Survey World 2, and Survey World 3 into the complete, authoritative architectural specification document:
`c:\GitDev\Investment\docs\architecture\04_CONSOLIDATED_PIPELINE_ALIGNMENT.md`
and run full test and repository QA verification on the Windows 11 host.

INPUT SOURCES:
- c:\GitDev\Investment\.agents\ORIGINAL_REQUEST.md
- c:\GitDev\Investment\.agents\orchestrator_1\PROJECT.md
- c:\GitDev\Investment\.agents\teamwork_preview_explorer_survey_1\survey_world1_report.md
- c:\GitDev\Investment\.agents\teamwork_preview_explorer_survey_1\handoff.md
- c:\GitDev\Investment\.agents\teamwork_preview_spec_miner_survey_2\survey_world2_report.md
- c:\GitDev\Investment\.agents\teamwork_preview_spec_miner_survey_2\handoff.md
- c:\GitDev\Investment\.agents\teamwork_preview_explorer_survey_3\survey_world3_report.md
- c:\GitDev\Investment\.agents\teamwork_preview_explorer_survey_3\handoff.md
- c:\GitDev\Investment\00_runbook\WF07_RESEARCH_TO_PORTFOLIO_DECISION_FLOW.md
- c:\GitDev\Investment\HANDOVER_INFRASTRUCTURE_ARCHITECTURE.okf.md
- c:\GitDev\Investment\HANDOVER_INITIAL_PLAN_CONTROL.md
- c:\GitDev\Investment\05_blueprint\00_MASTER_PLAN.md

WRITE OWNERSHIP:
- You exclusively own and must write: `c:\GitDev\Investment\docs\architecture\04_CONSOLIDATED_PIPELINE_ALIGNMENT.md`
- You write your working notes, test logs, and handoff to: `c:\GitDev\Investment\.agents\teamwork_preview_worker_1/`
- DO NOT modify source code files in `ipos/`, tests in `tests/`, or sources in `Sources/`.

SPECIFIC SECTIONS TO DELIVER IN `04_CONSOLIDATED_PIPELINE_ALIGNMENT.md`:
1. Executive Summary & Architectural Invariants:
   - Harmonizing World 1 (August 28 Modular Rebuild), World 2 (Consolidated WSL2 Native Architecture `03-wsl2-native-stack-consolidation`), and World 3 (Legacy Master Plan IP).
   - Core Invariants: Governing Axiom (*Code computes everything numeric; LLM only narrates*), Canonical Branch `main`, Raw Sources `Sources/` read-only, 100% test preservation.
2. Section 1 (R1): Unified Cross-Stack Topology & Port/Network Mapping:
   - Comprehensive network matrix (Host Port, Container Port, Service, Subnet, DNS Name, Protocol, Binding IP).
   - Authoritative reconciliation of colloquial prompt ports vs ratified execution reality:
     * 127.0.0.1:8084 = ki-basis-nginx (Private edge reverse proxy)
     * 127.0.0.1:8086 = ki-basis-firefly
     * 127.0.0.1:8010 = ki-basis-paperless
     * 127.0.0.1:8083 = leela-op178-openproject (Private OpenProject 17.8 with 38 live WPs in priv_openproject)
     * 127.0.0.1:8642 / 9119 = ki-basis-hermes (API Gateway & Dashboard)
     * 3000/tcp = Karakeep Evidence Custody native internal container port
     * 8080/tcp = Activepieces native internal container port
     * 127.0.0.1:9082 = community-openproject (56 live WPs in comm_openproject)
   - Docker engine consolidation (D-04, D-09): single WSL2 "Apex" dockerd, Docker Desktop uninstalled, memory cap 16 GB (D-10), logon keepalive (D-06).
   - Shared PostgreSQL cluster `ki-basis-shared-postgres` (`pgvector:pg16`) role isolation:
     * Exact SQL statements: `REVOKE CONNECT ON DATABASE <db> FROM PUBLIC; GRANT CONNECT ON DATABASE <db> TO <role>;`
     * Role definitions, connection limits, and verified error behavior on cross-database access.
3. Section 2 (R2): Deterministic Persistence & Anti-Regression Guardrails:
   - Physical filesystem boundaries: Host NTFS (`C:\GitDev\Investment`) vs WSL2 ext4 (`/var/lib/docker/volumes/`).
   - Strict 9P virtual bridge quarantine: Document the 123x latency penalty, directory traversal 308x slowdown, broken `fcntl` locks (`ENOLCK`), and Windows Defender CPU spikes (350-420%).
   - Tamper-evident mechanics: BOM-free UTF-8 JSON, SHA-256 custody receipts, atomic `.tmp` -> `.json` write semantics (as implemented in `register.py` and `ingest.py`).
   - Live data protection guarantees:
     * `priv_openproject` (38 work packages, 241 migrations)
     * `comm_openproject` (56 work packages)
     * Confirmed Smartbroker / finanzen.net zero multi-currency ledgers (replaying 332 activities resolves 24 open holdings with 100% match against broker statements, preserving NDA 1,000 and PSYC 10,000)
     * Active 271-test pytest battery.
4. Section 3 (R3): Research-to-Portfolio Pipeline (WF-07) Service Integration:
   - End-to-end mapping of WF-07 Stages 1 through 6:
     * Stage 1: Evidence Custody & Ingestion (Karakeep ext4 container + `ipos/evidence/ingest.py`)
     * Stage 2: Signal Extraction & Monotonic Quote Grounding (WhisperX + `ipos/evidence/claims.py:verify_quote_grounding` with millisecond word timestamps and prompt injection defanging)
     * Stage 3: Thesis Invalidation & Action Watch (Hermes Agent `investment` profile reading read-only MCPs, writing atomic `data/action_watch_register.json`)
     * Stage 4: Quantitative Stance Engine (`ipos/advisor/rule_engine.py` evaluating 126 seminar rules; `ipos/portfolio/decision.py` clamping sector multipliers to [0.20, 1.80], applying 20% thesis invalidation penalties, and asymmetric gating)
     * Stage 5: Portfolio Allocation & Action Matrix (`ipos/portfolio/action_matrix.py` rebalancing broker holdings with Riskfolio-Lib 7.3.0 convex Risk Parity / HRP)
     * Stage 6: Sovereign Execution Gate (`ipos/portfolio/order_staging.py` staging limit orders with 0.5% buffers for manual execution at Smartbroker vs Zero; zero broker execution code)
   - Detailed User Stories: Include full specifications for US-01 through US-12 detailing execution environment, inputs, outputs, schemas, and deterministic step-by-step interactions.
   - Strict Technical Realities: Pure Python IPOS on Windows 11 host (.venv), background containers on WSL2 ext4, Wealthfolio visual desktop app (%APPDATA%\com.teymz.wealthfolio) failing closed, TradingView Pro Cloud via CSV/webhooks.
5. Section 4 (R4): Legacy Masterplan Value Extraction & Deprecation Matrix:
   - Item-by-item 3-way audit of July 2026 Master Plan and Meso Plans C1 through C9:
     * RETAIN (Core Mathematical IP)
     * TRANSITION (Replaced by External Tool)
     * DEPRECATE (Obsolete Scaffolding)
   - Authoritative Master Plan Reconciliation Matrix: Complete mapping of all 126 seminar rules and 44 process steps proving 100% mathematical preservation in native Python.
   - Concrete Migration Roadmap: Phased execution plan for connecting live Karakeep, Hermes MCP, and TradingView webhooks into weekly pipeline without disruption.
6. Section 5: Verification & Audit Attestation:
   - Verification commands and results:
     * Run `uv run pytest` from `C:\GitDev\Investment` and record full output.
     * Run `uv run python scripts/qa_repo.py` and record full output.

COMPLETION CRITERIA:
1. `docs/architecture/04_CONSOLIDATED_PIPELINE_ALIGNMENT.md` is fully authored, comprehensive, highly detailed, and free of placeholders or generic hand-waving.
2. Both verification commands (`uv run pytest` and `uv run python scripts/qa_repo.py`) executed and documented.
3. Handoff report written to `c:\GitDev\Investment\.agents\teamwork_preview_worker_1\handoff.md`.
4. Notify parent orchestrator via send_message when complete.
