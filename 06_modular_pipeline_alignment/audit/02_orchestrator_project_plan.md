# Project: IPOS Consolidated Pipeline Alignment

## Architecture
The IPOS (Investment Process Operating System) architecture harmonizes three distinct environments into a deterministic, multi-stack integration contract:
1. **Windows 11 Host (.venv Python 3.12 on NTFS)**:
   - Houses the core quantitative IPOS engine, DuckDB analytical warehouse (`data/warehouse.duckdb`), Parquet time-series archives (`data/archive/`), Riskfolio-Lib 7.3.0 optimization, Portfolio Performance adapter (`pp_adapter.py`), 126 seminar rules and 44 process steps (`ipos/advisor/rule_engine.py`), Action Matrix rebalancing, and limit order ticket staging (`order_staging.py`).
   - Run profile: Batch execution (<15 seconds per weekly cycle), 0 MB idle RAM.
2. **WSL2-Native Docker Daemon ("Apex", Ubuntu 26.04 on ext4)**:
   - Houses background containerized services on the unified `shared-db-net` (`172.20.0.0/16`):
     - `ki-basis-shared-postgres` (`pgvector/pgvector:pg16`): Consolidated multi-tenant database cluster with strict role isolation (`REVOKE CONNECT ON DATABASE <db> FROM PUBLIC`).
     - `leela-op178-openproject` (Private OpenProject 17.8 on port 8083, holding 38 live work packages in `priv_openproject`).
     - `community-openproject` (Community OpenProject on port 9082, holding 56 live work packages in `comm_openproject`).
     - `ki-basis-hermes` (Hermes Agent API on port 8642, dashboard on 9119, running `investment` profile with read-only MCPs).
     - `karakeep` (Research evidence custody on internal port 3000, ext4 volume).
     - `activepieces` (Event intake and webhook router on internal port 8080).
     - Supporting services: `ki-basis-nginx` (reverse proxy on 8084), `ki-basis-firefly` (8086), `ki-basis-paperless` (8010).
3. **Specialized Client & Cloud Services**:
   - **Wealthfolio Desktop**: Windows desktop Electron/Tauri app (`%APPDATA%\com.teymz.wealthfolio`) for visual portfolio review only; intentionally fails closed (`INTEGRATION_STATUS = "NOT_CONNECTED"`) to prevent desynchronization with sovereign IBOR accounting (`accounting.py`).
   - **TradingView Pro**: Cloud-hosted technical workbench. Interacted with via manual chart-data CSV export and outbound webhook alerts via Activepieces. Zero private holdings or credentials stored.
   - **Broker Execution**: Sovereign manual limit orders with 0.5% buffers executed manually via web interfaces at Smartbroker and finanzen.net zero. Zero automated broker credentials or trading APIs.

## Cross-Filesystem Boundary & 9P Quarantine
Cross-mounting databases or high-frequency file I/O across the WSL2 9P virtual bridge (`/mnt/c/`) is strictly prohibited. Benchmarks prove 9P introduces a 123×–308× latency degradation, broken `fcntl` database locks, and 350%–420% host CPU spikes from antivirus buffer inspection.
- **Rule**: Pure Python compute and DuckDB execute natively on NTFS. Container engines and PostgreSQL persist 100% on native WSL2 ext4 named volumes. Handoffs occur strictly via immutable file drops or local TCP/REST/MCP sockets.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | WSL2 Engine & Port Mapping | Map host `127.0.0.1` ports (8084, 8086, 8010, 8083, 8642, 9119, 9082) and container ports | M1 | World 2 (D-04, D-09, D-18) |
| 2 | Shared Postgres Isolation | Enforce `REVOKE CONNECT FROM PUBLIC` and role least-privilege on `ki-basis-shared-postgres` | M1 | World 2 (D-07, D-13) |
| 3 | Single-Edge Security | Document private vs community boundaries and Caddy/Nginx reverse proxy topology | M1 | AGENTS.md, World 2 |
| 4 | Exact File & Volume Paths | Codify NTFS host paths (`C:\GitDev\Investment`) vs WSL2 ext4 volumes (`/var/lib/docker/volumes/`) | M2 | World 2 (D-06, D-10), R2 |
| 5 | Append-Only Persistence | Codify BOM-free UTF-8 JSON, SHA-256 custody receipts, and atomic `.tmp` -> `.json` write mechanics | M2 | World 1 (register.py, ingest.py) |
| 6 | Live Data Guardrails | Fail-closed protection for `priv_openproject` (38 WPs), `comm_openproject` (56 WPs), Smartbroker ledgers | M2 | World 2, R2 |
| 7 | WF-07 Stage 1 & 2 Integration | Karakeep container on ext4 + WhisperX monotonic quote grounding in `claims.py` | M3 | World 1, WF-07, R3 |
| 8 | WF-07 Stage 3 Integration | Hermes Agent `investment` profile, read-only MCPs, and `data/action_watch_register.json` | M3 | World 1, WF-07, R3 |
| 9 | WF-07 Stage 4 & 5 Integration | Pure Python numerical rule engine (126 rules), sector bounds [0.20, 1.80], Riskfolio-Lib 7.3.0 | M3 | World 1, WF-07, R3 |
| 10 | WF-07 Stage 6 Integration | Sovereign manual limit orders with 0.5% buffers (SMARTBROKER vs ZERO); zero broker APIs | M3 | World 1, WF-07, R3 |
| 11 | User Stories US-01 to US-12 | Concrete operational user stories with execution environments, inputs, outputs, interactions | M3 | World 1 & 2 Survey Reports |
| 12 | 3-Way Master Plan Audit | Item-by-item audit of July 2026 Master Plan & Meso C1-C9 (RETAIN, TRANSITION, DEPRECATE) | M4 | World 3 Survey Report, R4 |
| 13 | 126-Rule Reconciliation Matrix | Document verbatim preservation of 126 seminar rules and 44 process steps in active codebase | M4 | World 3 Survey Report, R4 |
| 14 | Safe Migration Roadmap | Phased roadmap connecting Karakeep, Hermes MCP, TradingView webhooks into weekly pipeline | M4 | World 3 Survey Report, R4 |
| 15 | Consolidated Alignment Spec | Final architectural specification document `docs/architecture/04_CONSOLIDATED_PIPELINE_ALIGNMENT.md` | M5 | Acceptance Criteria, R1-R4 |
| 16 | 271-Test Suite Preservation | Independent verification that all 271 unit/integration pytest tests pass with zero errors | M5 | Acceptance Criteria, Invariants |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Cross-Stack Topology & Network Matrix (R1) | Network matrix, port mappings, PostgreSQL role isolation, single-edge security | Phase 0 | DONE (`docs/architecture/04_CONSOLIDATED_PIPELINE_ALIGNMENT.md` §1) |
| M2 | Deterministic Persistence & Anti-Regression (R2) | Physical filesystem layout, 9P avoidance, tamper-evident JSON/SHA-256, live data protection | M1 | DONE (`docs/architecture/04_CONSOLIDATED_PIPELINE_ALIGNMENT.md` §2) |
| M3 | WF-07 Pipeline Service Integration (R3) | Deep service integration for Stages 1-6, User Stories US-01..US-12, execution environments | M2 | DONE (`docs/architecture/04_CONSOLIDATED_PIPELINE_ALIGNMENT.md` §3) |
| M4 | Master Plan Reconciliation & Migration Matrix (R4) | 3-way component audit, 126 rules & 44 steps preservation matrix, phased migration roadmap | M3 | DONE (`docs/architecture/04_CONSOLIDATED_PIPELINE_ALIGNMENT.md` §4) |
| M5 | Final Spec Authoring & Full Verification | Author `04_CONSOLIDATED_PIPELINE_ALIGNMENT.md`, run 271 tests via worker, audit pass | M4 | DONE (All 5 verification agents APPROVED/CLEAN) |

## Code Layout & Write Boundaries
- Metadata / Coordination: `c:\GitDev\Investment\.agents/` (orchestrator and subagent working directories).
- Core Engine: `ipos/` (read-only for this architectural alignment task; zero code modification required).
- Configuration: `configs/` (`registry.yaml`, `registry_120.yaml` - read-only).
- Architectural Documentation Deliverable: `docs/architecture/04_CONSOLIDATED_PIPELINE_ALIGNMENT.md` (authored in Milestone M5 by Worker).
- Test Suite: `tests/` (executed to verify 100% preservation; zero modification).
- Sources: `Sources/` (strictly read-only input material; zero mutation).
