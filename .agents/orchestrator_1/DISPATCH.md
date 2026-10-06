# Dispatch Log

## 2026-09-28T08:39:33Z

You are the Project Orchestrator for the IPOS project.

Your Working Directory: `c:\GitDev\Investment\.agents\orchestrator_1`
Project Root: `c:\GitDev\Investment`
Reference Directory: `c:\GitDev\apexai-os-meta\apex-meta\orchestration\architecture-improvements\03-wsl2-native-stack-consolidation\`
Original Request: `c:\GitDev\Investment\.agents\ORIGINAL_REQUEST.md` (also at `c:\GitDev\Investment\ORIGINAL_REQUEST.md`)

Task Summary:
Align and harmonize the IPOS August 28 Modular Rebuild Pipeline with the ratified WSL2-native consolidated architecture (`03-wsl2-native-stack-consolidation`), establishing a deterministic multi-stack integration contract that prevents accidental overwrites and identifies reusable assets from the legacy Master Plan.

Integrity Mode: `development`

Core Requirements & Deliverables:
1. Unified Cross-Stack Topology & Port/Network Mapping (R1):
   - Map communication pathways between the Windows host IPOS runtime (`127.0.0.1` / ports `8084`, `8086`, `8010`, `8642`, `3000`) and WSL2 containers.
   - Establish explicit network and database boundaries for IPOS data (Karakeep evidence custody, Hermes orchestration MCP, OpenProject work packages) ensuring zero cross-tenant contamination.
   - Deliver complete architectural specification in `docs/architecture/04_CONSOLIDATED_PIPELINE_ALIGNMENT.md`.
   - Verified network matrix specifying all host ports, container ports, subnets, and connection protocols without port conflicts or 9P regressions.
   - Explicit role and privilege mapping for IPOS interaction with the shared PostgreSQL cluster (`ki-basis-shared-postgres`).

2. Deterministic Persistence & Anti-Regression Guardrails (R2):
   - Specify exact file/volume paths for all artifacts across host NTFS (`C:\GitDev\Investment`) and WSL2 ext4 (`/var/lib/docker/volumes/`).
   - Enforce strict append-only / tamper-evident mechanics (SHA-256 receipts, BOM-free JSON, versioned migration logs).
   - Guard all existing live data: `priv_openproject` (38 work packages), `comm_openproject` (56 work packages), confirmed Smartbroker ledger histories, and active test baselines. Zero destruction of live data.

3. Research-to-Portfolio Pipeline (WF-07) Service Integration (R3):
   - Map each stage of WF-07 Decision Flow to the newly consolidated infrastructure:
     - Stage 1 & 2 (Evidence Custody & Extraction): Karakeep Docker container on ext4 + WhisperX transcripts with monotonic quote grounding.
     - Stage 3 (Thesis Invalidation): Hermes Agent in `investment` profile reading read-only MCPs and writing to `data/action_watch_register.json`.
     - Stage 4 & 5 (Quantitative Stance & Action Matrix): Pure Windows Python numerical engine (126 rules, sector bounds [0.20, 1.80], Riskfolio-Lib 7.3.0).
     - Stage 6 (Execution Gate): Sovereign manual limit orders with 0.5% buffers (SMARTBROKER vs ZERO); zero automated broker credentials.

4. Legacy Masterplan Value Extraction & Deprecation Matrix (R4):
   - Audit the July 2026 Master Plan (`05_blueprint/00_MASTER_PLAN.md`) and Meso Plans C1–C9 against the August 28 Modular Rebuild (`05_blueprint/research/2026-08-28-modular-rebuild/` and `docs/architecture/PIPELINE_DECISION_MATRIX.md`).
   - Produce an item-by-item deprecation and preservation matrix classifying components as RETAIN (Core Mathematical IP), TRANSITION (Replaced by External Tool), or DEPRECATE (Obsolete Scaffolding).
   - Authoritative Master Plan Reconciliation Matrix documenting exactly how all 126 seminar rules and 44 process steps remain intact within the new toolchain.
   - Concrete migration roadmap defining safe execution phases for connecting live Karakeep, Hermes MCP, and TradingView webhooks into the production weekly pipeline.

Invariants to Preserve:
- Governing Axiom: Code computes everything numeric; the LLM only narrates.
- Canonical Branch: `main`.
- Raw Sources: `Sources/` is read-only input material; do not mutate.
- 100% Test Suite Preservation: Ensure all 271 existing pytest unit/integration tests in `c:\GitDev\Investment` continue to pass.

## 2026-09-28T08:43:55Z

CRITICAL OPERATOR GUIDANCE & STEERING DIRECTIVE (2026-09-28T08:43:35Z):

1. ANTI-OVERENGINEERING & ZERO-DRIFT MANDATE:
The operator has explicitly warned that previous AI sessions hallucinated impossible cross-environment connections (e.g. attempting to run desktop GUI apps inside headless Linux Docker, cross-mounting databases over 9P causing file-lock corruption and 300x latency, inventing unsupported API sockets). Stop any speculative architectures immediately.

2. USER-STORY DRIVEN DECOMPOSITION:
Structure the alignment deliverables around concrete, verifiable USER STORIES. For every module interaction, explicitly define:
- Exact Execution Environment: Host Windows 11 (NTFS) vs WSL2 (native ext4) vs Docker Container ("Apex" engine) vs Native Desktop GUI vs Cloud/SaaS.
- Concrete Inputs & Outputs: Exact file paths, formats, schemas, and persistence contracts.
- Deterministic Step-by-Step Interactions: How data flows between modules without mixing environments or creating brittle sync loops.

3. STRICT TECHNICAL REALITIES TO ENFORCE:
- Core Quantitative IPOS (DuckDB, Pandas, Riskfolio-Lib 7.3.0, Portfolio Performance parser, Action Matrix): Runs natively on Windows 11 Python (.venv).
- Background Containers (Karakeep, Activepieces, Hermes): Run inside the single WSL2 "Apex" Docker engine on native ext4.
- Wealthfolio: Runs as a Windows desktop Electron/Tauri app (%APPDATA%\com.teymz.wealthfolio). Cannot be containerized or headless-bridged.
- TradingView Pro: Cloud service. Interacted with via CSV exports and inbound HTTP webhooks only.

Incorporate these boundaries directly into your milestone specifications and victory audit. This guidance has also been appended to ORIGINAL_REQUEST.md.
