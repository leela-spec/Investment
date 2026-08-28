# Revised Decision Matrix — v0.1

Date: 2026-08-28
Status: candidate, not frozen

## Decision dimensions

Every component is judged on:
- role / what it owns;
- cost;
- deterministic vs AI;
- local vs cloud;
- data egress;
- supported integration seam;
- whether it replaces custom IPOS work;
- evidence quality;
- POC requirement.

## Matrix

| # | Function | Primary candidate | Cost | Deterministic? | Runs locally? | Data egress | Supported seam | Current decision |
|---:|---|---|---|---|---|---|---|---|
| 1 | Orchestration | **Hermes Agent** | Software free/open source; model/provider cost depends on chosen inference route | Agentic, not numeric authority | Yes | **Conditional on LLM provider and tools** | MCP, terminal/files, cron, skills, delegation | **PROVISIONAL_ADOPT** |
| 2 | Research/news/evidence | **Karakeep self-hosted** | Free/open source | Storage/search deterministic; optional AI tagging/summarization | Yes | Local if self-hosted; AI egress only if external LLM selected | REST API, MCP, CLI, RSS | **PROVISIONAL_ADOPT** |
| 3 | Market/macro/fundamental data integration | **OpenBB ODP** | ODP is open/free under AGPL; data providers may have their own costs | Yes for data retrieval/normalization | Yes | Local ODP itself: no telemetry; provider calls leave host as required | Python, REST, MCP, Docker | **TEST_FURTHER** |
| 4 | OpenBB graphical Workspace | **Not default** | Community free but OpenBB-hosted; Lite $2,400/year list price | N/A | Community no; Lite self-hosted | Community is cloud | Workspace/MCP | **REJECT_DEFAULT_COST/PRIVACY** |
| 5 | Portfolio ingestion | **Our deterministic CSV/PDF normalization** | Free, existing/local | **Yes** | Yes | None unless OCR/extraction tool is external | Files -> canonical normalized portfolio schema | **KEEP/REDESIGN** |
| 6 | Portfolio visualization and human analysis | **Wealthfolio local app** | Core app free/local; optional Connect paid/cloud | Yes for portfolio calculations; AI optional | Yes | **LOCAL_ONLY if Connect and AI disabled** | CSV import/export, local DB, MCP | **TEST_FURTHER, narrower role** |
| 7 | Portfolio optimization | **Riskfolio-Lib** | Free, BSD-3-Clause | **Yes, mathematical optimizer** | **Yes** | None | Python library/files | **PROVISIONAL_ADOPT** |
| 8 | Rebalance presentation | **Wealthfolio UI if target import seam is supported** | As above | Yes | Yes | Local-only configuration possible | Needs POC; do not assume writable target API | **UNRESOLVED** |
| 9 | Machine-only discrete orders | **PyPortfolioOpt only if needed** | Free/open source | Yes | Yes | None | Python/files | **CONDITIONAL** |
| 10 | Technical analysis workbench | **TradingView Pro subscription already owned** | Existing sunk subscription cost | Platform calculations deterministic; scripts/alerts deterministic conditional logic | Cloud service | **Cloud**; chart/watchlist/portfolio/alerts live at TradingView when used | CSV export, webhooks, Pine scripts, screeners | **ADOPT_EXISTING** |
| 11 | Local technical indicator calculations | **TA-Lib** | Free, BSD-style | **Yes** | Yes | None | Python/native library | **CONDITIONAL** |
| 12 | Custom dashboard | **None by default** | Avoided | — | — | — | Use specialist UIs first | **DROP_DEFAULT** |
| 13 | Extra intake automation | **No tool by default** | $0 | — | — | — | Add only if a concrete gap exists | **HOLD** |
| 14 | Activepieces | Optional intake sidecar only | Community Edition open source/self-hostable | Workflow deterministic | Yes | Depends on connected services | Triggers/actions/webhooks | **HOLD_PENDING_GAP** |
| 15 | LangGraph | None | Avoided | — | — | — | Redundant with Hermes orchestration | **DROP** |
| 16 | OpenClaw | None in this target architecture | Avoided | — | — | — | Hermes replaces orchestration role | **HOLD** |

## Key corrections from previous matrix

### Hermes instead of OpenClaw
Hermes currently supports MCP clients for local stdio and remote HTTP servers, per-server tool filtering, built-in terminal/file/web/browser capabilities, cron scheduling, skills, delegation, and tool-search/progressive disclosure. This is enough to make Hermes the first orchestration candidate without adding LangGraph.

**Risk:** Hermes is still an AI agent. It must not become the numeric authority. All portfolio weights, risk measures, technical values, and rule evaluations must be produced by deterministic tools and passed to Hermes as facts.

### OpenBB ODP is not the $2,400/year product
The $2,400/year list price applies to **Workspace Lite**, not ODP. ODP is open source under AGPL and can run locally. Workspace Community is free but OpenBB-hosted.

**Current policy:** test ODP only. Do not buy Workspace Lite. A paid tool must clear a separate value gate and should normally fit the operator's stated roughly EUR 20-30/month range unless its value is exceptional.

### Portfolio tracker scope is reduced
We do **not** need Wealthfolio to connect to brokers or ingest accounts automatically. The intended flow is:
1. operator supplies CSV/PDF;
2. our deterministic normalization creates a canonical portfolio dataset;
3. a portfolio product receives clean data for visualization, performance analysis, allocation and planning.

Therefore Wealthfolio's broker-connect features are not a reason to choose it. The POC should judge it mainly on:
- visual quality;
- local-first privacy;
- clean import/export;
- performance/allocation analysis;
- target/rebalancing usability;
- ability to expose data safely to Hermes if desired.

### Riskfolio-Lib facts
- Open source, BSD-3-Clause.
- Python library built around CVXPY and other numerical/statistical libraries.
- Runs locally.
- No subscription required.
- Deterministic for a fixed dataset, model, parameters and solver configuration, subject to normal numerical-solver reproducibility considerations.
- No inherent data upload.

### TradingView role promoted
TradingView should be used substantially because the user already pays for it. Officially supported useful seams include:
- chart-data CSV export, including displayed indicators;
- webhook alerts via HTTP POST;
- Pine indicators/strategies/alerts;
- screeners;
- economic data and yield curves;
- portfolio/watchlist functionality depending on plan.

**Boundary:** TradingView is cloud software and is not treated as the canonical local portfolio database or unrestricted data API.

## What remains custom

Only custom work that directly preserves unique operator value is justified:
- deterministic normalization of operator-provided broker CSV/PDF data;
- canonical portfolio schema;
- IPOS Playbook/rules/governors/contradictions;
- adapter scripts only where a documented import/export/API seam requires format conversion;
- validation tests and evidence logs.

Everything else should first be assigned to an existing product.