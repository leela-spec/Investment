# Autonomous Multi-Agent Handover: Automation Architecture, 10 Workflows & Simulation Test Suite

**Date:** 2026-09-07  
**Prepared For:** Autonomous Multi-Agent Orchestration Team (Next Chat Session)  
**Execution Authority:** Multi-Agent CLI Team (Lead Orchestrator, Infra Verifier, IPOS Verifier, Community Verifier)  
**System Scope:** Three-Tier Cognitive Architecture, Clean Separation of Content vs. Bookkeeping, Isolated Community Alpine Stack, 10 Verified Workflows, and Autonomous Execution Protocol.

---

## 1. The Three-Tier Cognitive & Operational Architecture

The system operates across three strictly delineated layers of cognition and responsibility:

```mermaid
flowchart TB
    subgraph Tier1 ["Tier 1: High-Reasoning CLI Agents (Antigravity / Local Skills)"]
        CLIAgent["CLI Agent Cognitive Core
(Deep Multi-Step Reasoning & Strategy)"]
        SkillsEngine["Local Skills Library (.agents/skills/)
(ipos-product-proof, agy-customizations, etc.)"]
        CLIAgent --- SkillsEngine
    end

    subgraph Tier2 ["Tier 2: Hermes Master Orchestration & Automation Engine"]
        HermesMaster["Hermes Master Orchestrator (/usr/local/bin/hermes)
(Persistent Automation Lines, Profiles & MCP)"]
        subgraph Profiles ["Active Role Profiles (/root/.hermes/profiles/)"]
            ProfDefault["default (Cross-Repo Execution)"]
            ProfInv["investment (IPOS Rules & Evidence Custody)"]
            ProfWork["workshop-designer (Curriculum & Workshops)"]
            ProfStrat["research-strategist (Deep Literature Synthesis)"]
            ProfMkt["marketing-executive (Outreach & Event Workflows)"]
            ProfRev["independent-reviewer (Quality Gates & Audits)"]
        end
        HermesMaster --> Profiles
    end

    subgraph Tier3_Content ["Tier 3A: The Content Domain (Native ext4 Repositories)"]
        RepoApex["📁 apexai-os-meta (OS, Tools & Architecture)"]
        RepoInv["📁 Investment (IPOS Core, Rules, DuckDB)"]
        Karakeep_Custody["🗄️ Karakeep Evidence Custody (Anchored in Investment)"]
        RepoMoA["📁 MasterOfArts (Workshops, Website, Coaching, Art)"]
        RepoAcim["📁 acim-secular (Philosophical Corpus)"]
        
        RepoInv --- Karakeep_Custody
    end

    subgraph Tier3_PrivateBiz ["Tier 3B: Private Bookkeeping Domain (WSL2 KI-Basis Stack)"]
        PrivEdge["Nginx Gateway :8084"]
        PrivPaperless["Paperless-ngx (Client Invoices & Contracts)"]
        PrivFirefly["Firefly III (Private Business Ledger & Bank Sync)"]
        PrivOpenProject["OpenProject (Private Milestones & Tasks)"]
        PrivPostgres[("Consolidated PostgreSQL 16")]
    end

    subgraph Tier3_Community ["Tier 3C: Community Operations Domain (Windows Alpine Docker) - FULL SEPARATION"]
        CommNginx["Nginx Gateway :8084 (Windows Host)"]
        CommPretix["Pretix API Ticketing Adapter (Safer Space e.V.)"]
        CommPaperless["Paperless-ngx (Event Receipts & Payouts)"]
        CommFirefly["Firefly III (Non-Profit 4-Sphere EÜR Ledger)"]
        CommOpenProject["OpenProject (Equinox 2026 Volunteer Shift Board)"]
        CommNote["⚠️ Isolated Alpine VM: Shareable with Community Organizers without Exposing Private Repos/Finances"]
    end

    %% Inter-Tier Operational Links
    CLIAgent ==>|Directs Strategy, Reads Outputs, Inspects Boards| HermesMaster
    CLIAgent ==>|Queries & Audits Local Code| Tier3_Content

    HermesMaster ==>|Executes Automation & Content Generation| Tier3_Content
    HermesMaster -.->|Binds Status & Triggers to Business Side| Tier3_PrivateBiz

    Tier3_Content -.->|Extracts Outgoing Invoices / Deliverables| Tier3_PrivateBiz
    Tier3_Community -.-x|NO ROUTING / NO SHARED DB / CORE SEPARATION| Tier3_PrivateBiz
```

### Key Architectural Truths:
1. **CLI Agents = The Cognitive Brain**:
   * CLI agents possess high-reasoning capacity and execute deep research, complex refactors, and strategic synthesis.
   * They access local skills (`.agents/skills/`), inspect Hermes logs, review OpenProject Kanban boards, and direct Hermes automation.
2. **Hermes = The Persistent Automation Line**:
   * Hermes maintains long-running state, role profiles, crons, and MCP tool connections.
   * It handles scheduled executions, repetitive pipelines, and programmatic queries.
3. **Content vs. Bookkeeping Division**:
   * **Content Side (Hermes + ext4 Repos)**: Workshops, website creation, ideas, research pipelines, algorithmic backtests.
   * **Bookkeeping Side (KI-Basis)**: Strictly the receiving end for invoices, banking reconciliation, and administrative accounting.
4. **Community Operations Quarantined in Alpine Docker**:
   * The Equinox 2026 ticketing, Safer Space e.V. non-profit accounting, and volunteer shift planning live **strictly in the Windows Alpine Docker Desktop environment**.
   * It is 100% segregated so it can be shared with club collaborators without ever exposing private source code or personal business financials.

---

## 2. Execution Reality: Schedulers, Offline Queues & Catch-Up Mechanics

### 1. Who Initiates and Holds the Automation?
* **Windows Task Scheduler (`scripts/register_scheduler.ps1`)**:
  Holds `IPOS Weekly Pipeline`. Configured with `-StartWhenAvailable` to catch up missed runs.
* **Linux Cron / Systemd (`scripts/run_weekly_cron.sh`)**:
  Executes in Ubuntu WSL2 under `flock -n /tmp/ipos-weekly.lock` to prevent concurrent database writes.
* **Hermes Event Loop (`ki-basis-hermes`)**:
  Listens for incoming webhooks and API triggers on `127.0.0.1:8642`.

### 2. What Happens When the Laptop is Offline or Asleep?
* **Hardware State**: Local CPU is paused during sleep/off states.
* **Windows Scheduler Catch-Up**:
  If the laptop was asleep during the 05:00 Saturday schedule, Windows detects the missed event upon wake and triggers the pipeline immediately.
* **Telegram Cloud Message Queue**:
  Telegram Bot API servers store messages for 24+ hours. When `hermes_telegram_intake.py` reconnects, it retrieves updates with the last known `offset`, processing all missed receipts and ideas in chronological order without loss.
* **Pretix Cloud Queue**:
  Pretix retains all ticket sales and transaction logs in the cloud. Upon reconnection, `pretix_adapter.py` queries by timestamp and reconciles the backlog into Firefly III and Paperless.

---

## 3. Workflow Relocation & Retained IPOS Runbooks

To eliminate domain pollution and maintain strict repository sovereignty, the non-investment workflows have been moved to their respective sibling repositories with dedicated README index files:

| Workflow | Title | New Authoritative Location |
|---|---|---|
| **MPP-001** | Autonomous Multi-Agent Sequential Test Plan | `C:\GitDev\apexai-os-meta\docs\plans\00_META_PROGRAM_PLAN.md` |
| **WF-01** | Weekly Meta-Orchestration Sweep | `C:\GitDev\apexai-os-meta\docs\workflows\WF01_WEEKLY_META_ORCHESTRATION.md` |
| **WF-02** | Creative Writing & Thematic Synthesis | `C:\GitDev\MasterOfArts\docs\workflows\WF02_CREATIVE_WRITING_SYNTHESIS.md` |
| **WF-03** | "Transcendents" Workshop Concept | `C:\GitDev\MasterOfArts\workshops\plans\WF03_TRANSCENDENTS_WORKSHOP_CONCEPT.md` |
| **WF-04** | Business Website Multi-Variant Pipeline | `C:\GitDev\MasterOfArts\WEbsite\WF04_MOA_BUSINESS_WEBSITE_PIPELINE.md` |
| **WF-07** | Coaching Onboarding & Invoicing | `C:\GitDev\MasterOfArts\Coaching\WF07_COACHING_LIFECYCLE_INVOICING.md` |
| **WF-08** | Equinox 2026 Pretix Ticketing Settlement | `C:\GitDev\lika-community\docs\workflows\WF08_EQUINOX_PRETIX_TICKETING.md` |
| **WF-09** | Telegram Bot Offline Intake | `C:\GitDev\lika-community\docs\workflows\WF09_TELEGRAM_BOT_OFFLINE_INTAKE.md` |
| **WF-10** | Secular Corpus Cross-Referencing | `C:\GitDev\acim-secular\docs\workflows\WF10_ACIM_SECULAR_CROSS_REFERENCE.md` |

### Retained IPOS Operational Procedures (in `00_runbook/`):
- **[`WF05_IPOS_WEEKLY_MACRO_REGIME.md`](../../../00_runbook/WF05_IPOS_WEEKLY_MACRO_REGIME.md)**: Saturday 05:00 22-indicator macro regime calculation via DuckDB and rule engine.
- **[`WF06_IPOS_EVIDENCE_CUSTODY_WATCHDOG.md`](../../../00_runbook/WF06_IPOS_EVIDENCE_CUSTODY_WATCHDOG.md)**: Karakeep research custody watchdog archiving financial research artifacts with cryptographic receipts.

---

## 4. Multi-Agent Autonomous Simulation & Test Protocol (IPOS Focus)

**Instructions for the incoming Multi-Agent Team:**
Do NOT ask the operator to run terminal commands manually. Execute, observe, and verify the following IPOS test battery autonomously:

```mermaid
flowchart TD
    LeadAgent["Lead Orchestrator (IPOS Focus)"]
    
    subgraph IPOS_Verification_Agents ["Autonomous IPOS Verification Team"]
        MacroAgent["Macro Regime & Scoring Verifier"]
        NormalizerAgent["Portfolio Accounting Verifier (C11)"]
        OptimizerAgent["Riskfolio Optimizer Verifier (C13)"]
        ReportingAgent["HTML Report & Explorer Verifier"]
    end

    LeadAgent --> MacroAgent
    LeadAgent --> NormalizerAgent
    LeadAgent --> OptimizerAgent
    LeadAgent --> ReportingAgent
```

### Agent Runbook: 5 Autonomous IPOS Test Tasks

#### Task 1: Macro Regime & Scoring Deterministic Test Suite (Assigned to: MacroAgent)
* **Command**: `C:\GitDev\Investment\.venv\Scripts\python.exe -m pytest -q tests/test_regime.py tests/test_scoring.py`
* **Pass Criteria**:
  - All test cases pass (100% pass rate) in < 30 seconds.
  - Regime classifier deterministically outputs CHOPPY, TRENDY, or MOMENTUM based on golden fixtures.

#### Task 2: Portfolio Normalizer & Reconciliation Engine Suite (Assigned to: NormalizerAgent)
* **Command**: `C:\GitDev\Investment\.venv\Scripts\python.exe -m pytest -q tests/test_m11_normalizer.py tests/test_stop_gate.py`
* **Pass Criteria**:
  - Validates FIFO book cost basis, multi-currency conversions (EUR/USD), and control matrix checks.
  - Stop-gate fails closed on arithmetic discrepancies.

#### Task 3: Riskfolio-Lib Quantitative Optimization Suite (Assigned to: OptimizerAgent)
* **Command**: `C:\GitDev\Investment\.venv\Scripts\python.exe -m pytest -q tests/test_m13_optimizer.py`
* **Pass Criteria**:
  - Proves real Riskfolio-Lib execution (HRP, Min-Risk, Max Sharpe).
  - Validates socket blocking (offline invariant) and constraints sum to 1.0.

#### Task 4: Contradiction Detection & Historical Replay Suite (Assigned to: MacroAgent)
* **Command**: `C:\GitDev\Investment\.venv\Scripts\python.exe -m pytest -q tests/test_contradictions.py tests/test_replay.py`
* **Pass Criteria**:
  - Verifies inter-market macro contradiction rules (Credit vs Equity, Yield Curve vs Stance).
  - Historical replay produces deterministic point-in-time snapshots.

#### Task 5: Static Report & Macro Risk Explorer Verification (Assigned to: ReportingAgent)
* **Command**: `C:\GitDev\Investment\.venv\Scripts\python.exe -m pytest -q tests/test_report_html.py`
* **Pass Criteria**:
  - Generates self-contained static HTML report (`report.html`).
  - Validates all report sections without network leakage.
