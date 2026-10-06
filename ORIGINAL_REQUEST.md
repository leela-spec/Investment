# Original User Request

## 2026-09-28T08:38:42Z

Align and harmonize the IPOS August 28 Modular Rebuild Pipeline with the ratified WSL2-native consolidated architecture (`03-wsl2-native-stack-consolidation`), establishing a deterministic multi-stack integration contract that prevents accidental overwrites and identifies reusable assets from the legacy Master Plan.

Working directory: `C:\GitDev\Investment`  
Reference directory: `C:\GitDev\apexai-os-meta\apex-meta\orchestration\architecture-improvements\03-wsl2-native-stack-consolidation\`  
Integrity mode: `development`

---

## Context & The Three Worlds to Align

1. **World 1 — The IPOS Modular Rebuild Pipeline (August 28 – September 2026)**:
   - External toolchain: Riskfolio-Lib 7.3.0, Portfolio Performance, OpenBB Platform Core (ODP), Karakeep, TradingView Pro, Hermes Agent, and Activepieces.
   - Core workflow: Research-to-Portfolio Decision Flow (WF-07 Stages 1–6).
   - Provenance: `05_blueprint/research/2026-08-28-modular-rebuild/` and `docs/architecture/PIPELINE_DECISION_MATRIX.md`.

2. **World 2 — The Ratified Consolidated WSL2 Architecture (`03-wsl2-native-stack-consolidation`)**:
   - Single WSL2-native Docker engine ("Apex" dockerd, Ubuntu 26.04, ext4, Docker Desktop uninstalled).
   - Consolidated PostgreSQL cluster (`ki-basis-shared-postgres`) hosting private (`priv_*`) and community (`comm_*`) databases with strict role isolation (`REVOKE CONNECT`).
   - Ratified decisions: D-01 through D-18 (OpenProject 17.8 authoritative, Hermes container wiring, shared DB net `172.20.0.0/16`, local named volumes).
   - Invariant: Avoid the 9P cross-filesystem latency penalty (Windows host Python for numerical IPOS computations; ext4 volumes for container databases).

3. **World 3 — The Legacy Master Plan (`05_blueprint/00_MASTER_PLAN.md`)**:
   - Extract and preserve the genuine mathematical IPOS core (126 seminar rules, Z-score/tanh scoring, regime classifiers, DuckDB single-file warehouse).
   - Explicitly deprecate outdated scaffolding (custom scrapers, bespoke solvers, obsolete container drafts) without accidental file deletion.

---

## Requirements

### R1. Unified Cross-Stack Topology & Port/Network Mapping
Synthesize a comprehensive topology specification showing how IPOS connects to the consolidated WSL2 "Apex" Docker stack:
- Map communication pathways between the Windows host IPOS runtime (`127.0.0.1` / ports `8084`, `8086`, `8010`, `8642`, `3000`) and WSL2 containers.
- Establish explicit network and database boundaries for IPOS data (e.g. Karakeep evidence custody, Hermes orchestration MCP, OpenProject work packages) ensuring zero cross-tenant contamination.

### R2. Deterministic Persistence & Anti-Regression Guardrails
Define fail-closed persistence boundaries to permanently eliminate accidental data overwriting:
- Specify exact file/volume paths for all artifacts across host NTFS (`C:\GitDev\Investment`) and WSL2 ext4 (`/var/lib/docker/volumes/`).
- Enforce strict append-only / tamper-evident mechanics (e.g. SHA-256 receipts, BOM-free JSON, versioned migration logs).
- Guard all existing live data: `priv_openproject` (38 work packages), `comm_openproject` (56 work packages), confirmed Smartbroker ledger histories, and active test baselines.

### R3. Research-to-Portfolio Pipeline (WF-07) Service Integration
Map each stage of the WF-07 Decision Flow to the newly consolidated infrastructure:
- **Stage 1 & 2 (Evidence Custody & Extraction)**: Karakeep Docker container on ext4 + WhisperX transcripts with monotonic quote grounding.
- **Stage 3 (Thesis Invalidation)**: Hermes Agent in `investment` profile reading read-only MCPs and writing to `data/action_watch_register.json`.
- **Stage 4 & 5 (Quantitative Stance & Action Matrix)**: Pure Windows Python numerical engine (126 rules, sector bounds $[0.20, 1.80]$, Riskfolio-Lib 7.3.0).
- **Stage 6 (Execution Gate)**: Sovereign manual limit orders with 0.5% buffers (SMARTBROKER vs ZERO); zero automated broker credentials.

### R4. Legacy Masterplan Value Extraction & Deprecation Matrix
Audit the initial July 2026 Master Plan (`05_blueprint/00_MASTER_PLAN.md`) and Meso Plans C1–C9 against the August 28 Modular Rebuild:
- Produce an item-by-item deprecation and preservation matrix.
- Clearly classify every component as **RETAIN (Core Mathematical IP)**, **TRANSITION (Replaced by External Tool)**, or **DEPRECATE (Obsolete Scaffolding)**.

---

## Acceptance Criteria

### Architectural Alignment & Topology
- [ ] Deliver a complete, unambiguous architectural specification document (`docs/architecture/04_CONSOLIDATED_PIPELINE_ALIGNMENT.md`) integrating the August 28 Rebuild, `03-wsl2-native-stack-consolidation`, and WF-07.
- [ ] Verified network matrix specifying all host ports, container ports, subnets, and connection protocols without port conflicts or 9P regressions.
- [ ] Explicit role and privilege mapping for any IPOS interaction with the shared PostgreSQL cluster (`ki-basis-shared-postgres`).

### Deterministic Integrity & Safety
- [ ] Zero destruction of existing live data: no tables dropped, no production database containers recreated, no source files clobbered.
- [ ] 100% test suite preservation: existing 271 pytest unit/integration tests in `C:\GitDev\Investment` continue to pass.
- [ ] Non-negotiable invariants preserved: Governing Axiom (*Code computes everything numeric; LLM only narrates*), Canonical Branch `main`, Raw Material Sovereignty (`Sources/` read-only).

### Deprecation & Value Mapping
- [ ] Authoritative Master Plan Reconciliation Matrix documenting exactly how all 126 seminar rules and 44 process steps remain intact within the new toolchain.
- [ ] Concrete migration roadmap defining safe execution phases for connecting live Karakeep, Hermes MCP, and TradingView webhooks into the production weekly pipeline.

## 2026-09-28T08:43:35Z

CRITICAL OPERATOR GUIDANCE & STEERING DIRECTIVE:

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

Incorporate these boundaries directly into your milestone specifications and victory audit.

