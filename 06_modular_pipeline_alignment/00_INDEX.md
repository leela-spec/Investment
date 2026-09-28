# 06: Modular Pipeline & Cross-Stack Infrastructure Alignment

> **NAVIGATION HUB & SYSTEM OF RECORD**  
> **Authority State:** Canonical Ratified Specification  
> **Target Environment:** Windows 11 NTFS (`C:\GitDev\Investment`) $\leftrightarrow$ WSL2 Ubuntu 26.04 ("Apex" Engine)  
> **Date:** 2026-09-28 · **Status:** Active & Ratified · **Test Baseline:** 271 / 271 passing (`uv run pytest`)  
> **Auditor Verdict:** `VICTORY CONFIRMED` (Independent Audit Attestation, 2026-09-28)

---

## 1. Fast Orientation (< 30 Seconds)

This project folder permanently aligns and harmonizes three foundational pillars of the IPOS architecture:
1. **The Modular Rebuild Pipeline (August 28, 2026)**: Integrating proven external tools (Riskfolio-Lib 7.3.0, Portfolio Performance, OpenBB, Karakeep, TradingView Pro, Hermes Agent) across the 6-stage WF-07 Decision Flow.
2. **The Consolidated WSL2 Stack (`03-wsl2-native-stack-consolidation`)**: Ratifying the single "Apex" WSL2 Docker engine, shared PostgreSQL cluster (`ki-basis-shared-postgres`) with role-based database isolation (`REVOKE CONNECT`), and strict elimination of 9P cross-filesystem performance bottlenecks.
3. **The Legacy Master Plan (`05_blueprint/00_MASTER_PLAN.md`)**: Preserving 100% of the mathematical IP (126 seminar rules, 44 process steps, Z-score/tanh scoring, regime classifiers) while cleanly deprecating obsolete custom scaffolding.

---

## 2. Directory Navigation & Decision Router

*Use this table to find exactly what you need without context bloat:*

| Directory / File | Description | When to Read |
|---|---|---|
| [`spec/04_CONSOLIDATED_PIPELINE_ALIGNMENT.md`](spec/04_CONSOLIDATED_PIPELINE_ALIGNMENT.md) | **The Canonical Specification** (938 lines, 81 KB). Comprehensive network matrix, persistence contracts, US-01..US-12 user stories, and deprecation matrix. | When designing, implementing, or auditing any cross-stack integration seam. |
| [`surveys/01_survey_world1_rebuild_pipeline.md`](surveys/01_survey_world1_rebuild_pipeline.md) | Deep survey of the August 28 Rebuild, WF-07 stages 1–6, and external tool capabilities. | When reviewing tool selections or decision flows. |
| [`surveys/02_survey_world2_wsl2_stack.md`](surveys/02_survey_world2_wsl2_stack.md) | Deep survey of `03-wsl2-native-stack-consolidation`, decisions D-01..D-18, and database isolation. | When inspecting ports, subnets, PostgreSQL roles, or Docker configurations. |
| [`surveys/03_survey_world3_legacy_masterplan.md`](surveys/03_survey_world3_legacy_masterplan.md) | Comprehensive audit of initial Master Plan and Meso Plans C1–C9 against the rebuild. | When verifying mathematical algorithms or checking deprecated features. |
| [`reviews/01_review_topology_persistence.md`](reviews/01_review_topology_persistence.md) | Reviewer 1 report on cross-stack topology (R1) and fail-closed persistence (R2). | To check topology validation details. |
| [`reviews/02_review_wf07_rules.md`](reviews/02_review_wf07_rules.md) | Reviewer 2 report on WF-07 pipeline (R3) and Master Plan value extraction (R4). | To check rule mapping and pipeline validation. |
| [`reviews/03_challenge_network_storage.md`](reviews/03_challenge_network_storage.md) | Adversarial challenger analysis on ports, database security, and 9P I/O stress. | To inspect security boundaries and network risks. |
| [`reviews/04_challenge_test_math.md`](reviews/04_challenge_test_math.md) | Adversarial challenger analysis on 271 unit tests, Riskfolio math, and seminar rules. | To verify mathematical reproducibility. |
| [`reviews/05_forensic_audit_report.md`](reviews/05_forensic_audit_report.md) | Forensic auditor report verifying zero placeholders, no mock facades, and strict integrity. | To inspect anti-cheating verification logs. |
| [`ROADMAP_FUTURE_STEPS.md`](ROADMAP_FUTURE_STEPS.md) | **Concrete Future Implementation Roadmap**. Phased next steps (Karakeep sync, Hermes Telegram dispatch, TradingView webhook ingress, 60-indicator graduation). | When planning or executing the next operational steps. |
| [`audit/03_operator_reality_verification_suite.md`](audit/03_operator_reality_verification_suite.md) | **Operator Reality Verification Suite**. Step-by-step diagnostic guide to catch hallucinations and prove external libraries execute authentically. | When verifying that code is real and non-hallucinated. |
| [`audit/verify_reality_battery.py`](audit/verify_reality_battery.py) | **Automated Reality Check Script**. 1-click Python battery testing Riskfolio, Wealthfolio fail-closed, Smartbroker PDF match, and order tickets. | Run with `uv run python 06_modular_pipeline_alignment/audit/verify_reality_battery.py`. |
| [`audit/01_victory_audit_attestation.md`](audit/01_victory_audit_attestation.md) | Independent Victory Auditor final verdict (`VICTORY CONFIRMED`). | To review the final attestation and phase pass criteria. |
| [`audit/02_orchestrator_project_plan.md`](audit/02_orchestrator_project_plan.md) | Original multi-agent orchestration dispatch plan and execution timeline. | For process and orchestration history. |
| [`audit/test_db_isolation.sh`](audit/test_db_isolation.sh) | Executable bash script testing live role separation across all 6 databases on `ki-basis-shared-postgres`. | To programmatically verify database access denial in WSL2. |
| [`references/README.md`](references/README.md) | Cross-repository links pointing to `apexai-os-meta`, parent blueprints, and runbooks. | To trace upstream architecture handovers. |

---

## 3. High-Level Architecture & Environment Isolation

```
                               ┌──────────────────────────────────────────────────────────┐
                               │        WINDOWS 11 HOST NATIVE (NTFS - C:\GitDev)         │
                               │                                                          │
                               │  • Core Quantitative Engine (DuckDB, Pandas, Python 3.12)│
                               │  • Riskfolio-Lib 7.3.0 (Convex Risk Parity & HRP)        │
                               │  • Portfolio Performance (Ledger Activity Replay)        │
                               │  • Action Matrix & Buffered Staged Limit Orders (0.5%)   │
                               │  • Wealthfolio Desktop GUI (%APPDATA% - Manual CSV Sync) │
                               └────────────────────────────┬─────────────────────────────┘
                                                            │
                                                            │ Localhost HTTP / SSE (127.0.0.1)
                                                            │ [Strict 9P Avoidance - Zero DB Locks]
                                                            ▼
                               ┌──────────────────────────────────────────────────────────┐
                               │         WSL2 UBUNTU 26.04 - "APEX" DOCKER ENGINE         │
                               │                                                          │
                               │  • Shared PostgreSQL Cluster (ki-basis-shared-postgres)  │
                               │    ├─ priv_* DBs (OpenProject 17.8 :8083, Firefly, Paper)│
                               │    └─ comm_* DBs (OpenProject :9082, Firefly, Paperless) │
                               │    └─ Isolation: REVOKE CONNECT per role (D-07, D-10)    │
                               │  • Evidence Custody: Karakeep (Next.js, Meili, Chrome)   │
                               │  • Cognitive Orchestrator: Hermes Agent :8642 / :9119    │
                               │  • Event Intake Sidecar: Activepieces                    │
                               └──────────────────────────────────────────────────────────┘
```

---

## 4. Non-Negotiable Architectural Invariants

1. **Governing Axiom**: *Code computes everything numeric; the LLM only narrates.* (Zero LLM arithmetic or portfolio allocation).
2. **9P Virtual Filesystem Quarantine**: Core Python quantitative code and DuckDB database files **MUST run natively on Windows 11 NTFS**. Never run core quantitative code inside WSL2/Docker mounted over `/mnt/c/` (prevents 300× I/O degradation and DuckDB file-lock corruption).
3. **Desktop GUI Isolation**: **Wealthfolio** is a Windows desktop Tauri GUI application with **zero public REST API and zero CLI**. Never attempt to containerize it or wrap it in a fake headless server. Integration is strictly manual CSV export/import.
4. **Single WSL2 Docker Engine**: All containerized background services (Karakeep, Activepieces, Hermes) run inside the single WSL2-native **"Apex" Docker engine** on native Linux ext4. Docker Desktop is uninstalled (D-09).
5. **Database Role Isolation**: The shared PostgreSQL cluster (`ki-basis-shared-postgres`) strictly isolates databases via `REVOKE CONNECT` (D-07, D-10). No cross-database or cross-tenant reads are permitted.
6. **TradingView Webhook Security**: TradingView is a cloud SaaS that can only POST to public HTTPS URLs. Never point TradingView alerts to unrouted `http://localhost`. All webhooks must pass through a secured ingress (Cloudflare Tunnel or Activepieces).
7. **Sovereign Execution Gate**: All broker order tickets generated by the Action Matrix are staged purely for manual operator entry. **Zero broker API credentials, zero auto-trading sockets.**

---

## 5. The 12 User Stories Summary

| Story | Focus | Execution Environment | Input | Output |
|---|---|---|---|---|
| **US-01** | Broker Activity Replay | Windows Host (.venv) | Smartbroker / PP CSVs | Canonical 24–32 holdings (100% PDF match) |
| **US-02** | Wealthfolio Presentation | Windows Desktop GUI | `wealthfolio_import.csv` | Visual desktop portfolio analysis |
| **US-03** | Media & Document Custody | WSL2 Docker (ext4) | Research URLs, PDFs | Karakeep archive + SHA-256 receipt |
| **US-04** | WhisperX Quote Grounding | Windows / WSL2 Python | Audio + Monotonic ASR JSON | Exact time intervals + defanged text |
| **US-05** | Action & Watch Register | Windows Host (.venv) | Validated research claims | Single-writer `action_watch_register.json` |
| **US-06** | Macro Data Ingestion | Windows Host (.venv) | Free feeds (FRED, DBnomics, Stooq) | Single-writer DuckDB tables |
| **US-07** | Macro Stance & Tilts | Windows Host (.venv) | 126 seminar rules | Sector tilts bounded in $[0.20, 1.80]$ |
| **US-08** | Riskfolio Risk Parity | Windows Host (.venv) | Returns covariance matrix | Euler Percentage Risk Contributions ($RC\%$) |
| **US-09** | Action Matrix Gating | Windows Host (.venv) | Stance + Holdings + Risk Parity | Rebalancing deltas & stop policies |
| **US-10** | Staged Order Tickets | Windows Host (.venv) | Action Matrix deltas | Priority Batch 1 & 2 tickets (0.5% limit buffers) |
| **US-11** | Hermes Telegram Digest | WSL2 Docker (Hermes) | Pre-computed `report.md` | Executive channel message to operator |
| **US-12** | TradingView Alert Ingest | Cloud $\to$ Ingress Sidecar | Webhook JSON alert | Open Watch Register alert item |

---

## 6. How AI Agents Must Work in This Repository

1. **Start Here**: Any AI agent entering this repository must read this file (`06_modular_pipeline_alignment/00_INDEX.md`) first.
2. **Consult Specific Specs**: If you need exact technical details, consult the relevant file in `spec/`, `surveys/`, or `reviews/` listed in Section 2. Do not read the entire directory at once.
3. **Never Overwrite Live Data**: Do not modify `data/warehouse.duckdb`, `data/action_watch_register.json`, or live PostgreSQL containers without explicit operator approval.
4. **Maintain Test Baseline**: Any proposed code changes must preserve 100% pass rate on `uv run pytest` (271 tests) and `scripts/qa_repo.py`.
