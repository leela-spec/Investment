# External & Cross-Repository Reference Index

This directory establishes authoritative links to parent architecture dossiers, upstream decision logs, and foundational research outside this directory tree.

---

## 1. Upstream WSL2 Consolidated Stack Dossier
**Location:** `C:\GitDev\apexai-os-meta\apex-meta\orchestration\architecture-improvements\03-wsl2-native-stack-consolidation\`

| Document | Authority Role | Key Content for IPOS |
|---|---|---|
| [`01-architecture-and-gaps.md`](file:///C:/GitDev/apexai-os-meta/apex-meta/orchestration/architecture-improvements/03-wsl2-native-stack-consolidation/01-architecture-and-gaps.md) | Verified Topology | Live engines ("Apex" WSL2 dockerd vs uninstalled Docker Desktop), container port allocations (`8083`, `8084`, `8086`, `8010`, `8642`, `9082`, `9084`, `9086`, `9010`, `9642`), and network subnets. |
| [`02-decisions-log.md`](file:///C:/GitDev/apexai-os-meta/apex-meta/orchestration/architecture-improvements/03-wsl2-native-stack-consolidation/02-decisions-log.md) | Ratified Decisions | D-01 through D-18: OpenProject 17.8 authoritative, shared PostgreSQL cluster (`ki-basis-shared-postgres`), role isolation (`REVOKE CONNECT`), and elimination of the OneDrive bind. |
| [`03-execution-plan.md`](file:///C:/GitDev/apexai-os-meta/apex-meta/orchestration/architecture-improvements/03-wsl2-native-stack-consolidation/03-execution-plan.md) | Phased Runbook | Historical execution steps 0–9 of the stack migration. |
| [`05-handover.md`](file:///C:/GitDev/apexai-os-meta/apex-meta/orchestration/architecture-improvements/03-wsl2-native-stack-consolidation/05-handover.md) | Operational Handover | Non-blocking follow-up items (16 GB WSL2 memory ceiling verification, live connection tuning, backup schedules). |

---

## 2. Parent IPOS Modular Rebuild Research (August 28, 2026)
**Location:** `C:\GitDev\Investment\05_blueprint\research\2026-08-28-modular-rebuild\`

| Document | Role | Core Integration Standard |
|---|---|---|
| [`00_README.md`](file:///c:/GitDev/Investment/05_blueprint/research/2026-08-28-modular-rebuild/00_README.md) | Strategic Directive | "Reuse proven standalone products through supported interfaces before custom code." |
| [`01_REVISED_DECISION_MATRIX.md`](file:///c:/GitDev/Investment/05_blueprint/research/2026-08-28-modular-rebuild/01_REVISED_DECISION_MATRIX.md) | Tool Selection Matrix | Decisions on Hermes, Karakeep, OpenBB ODP, Wealthfolio, Riskfolio-Lib, TA-Lib, and TradingView Pro. |
| [`02_ARCHITECTURE.md`](file:///c:/GitDev/Investment/05_blueprint/research/2026-08-28-modular-rebuild/02_ARCHITECTURE.md) | Component Diagram | Macro component boundaries and unidirectional data flow. |
| [`04_TRADINGVIEW_INTEGRATION.md`](file:///c:/GitDev/Investment/05_blueprint/research/2026-08-28-modular-rebuild/04_TRADINGVIEW_INTEGRATION.md) | Charting Seam | Chart CSV exports, Pine script webhooks, and manual geometry tracking. |
| [`05_HERMES_ORCHESTRATION.md`](file:///c:/GitDev/Investment/05_blueprint/research/2026-08-28-modular-rebuild/05_HERMES_ORCHESTRATION.md) | Agent Orchestrator | Hermes Agent MCP boundaries, Telegram channel dispatch, and read-only tools. |
| [`08_USER_STORIES_AND_INTEGRATION_WORKFLOWS.md`](file:///c:/GitDev/Investment/05_blueprint/research/2026-08-28-modular-rebuild/08_USER_STORIES_AND_INTEGRATION_WORKFLOWS.md) | Foundational Stories | Original 12 workflow user stories spanning email, video, evidence, and orders. |

---

## 3. Operational Runbooks & Toolchain Specs
**Location:** `C:\GitDev\Investment\`

| Document | Location | Core Standard |
|---|---|---|
| Institutional Pipeline Spec | [`docs/architecture/PIPELINE_DECISION_MATRIX.md`](file:///c:/GitDev/Investment/docs/architecture/PIPELINE_DECISION_MATRIX.md) | 7-step institutional quantitative pipeline specification. |
| Decision Flow Runbook | [`00_runbook/WF07_RESEARCH_TO_PORTFOLIO_DECISION_FLOW.md`](file:///c:/GitDev/Investment/00_runbook/WF07_RESEARCH_TO_PORTFOLIO_DECISION_FLOW.md) | Stages 1 through 6: Evidence intake -> Staged order tickets. |
| Target-Product Handover | [`HANDOVER_TARGET_PRODUCT_EXECUTION_2026-09-24.md`](file:///c:/GitDev/Investment/HANDOVER_TARGET_PRODUCT_EXECUTION_2026-09-24.md) | Target epics E01–E10 and verification baseline. |
| Infrastructure Handover | [`HANDOVER_INFRASTRUCTURE_ARCHITECTURE.okf.md`](file:///c:/GitDev/Investment/HANDOVER_INFRASTRUCTURE_ARCHITECTURE.okf.md) | OKF 0.2 hardware topology and 9P virtual filesystem post-mortem. |
