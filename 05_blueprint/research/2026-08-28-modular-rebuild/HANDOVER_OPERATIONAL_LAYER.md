# IPOS Handover: First Operational Layer & Modular Rebuild

**Date:** 2026-09-07  
**Status:** ACTIVE REBUILD IN PROGRESS  
**Repository:** `leela-spec/Investment`  
**Active Working Branch:** `ipos-modular-rebuild-2026-08-28`  
**Authority Documentation:**
- Master Program: [`05_blueprint/research/2026-08-28-modular-rebuild/implementation-plans/00_PROGRAM.yaml`](./implementation-plans/00_PROGRAM.yaml)
- Executor Contract: [`05_blueprint/research/2026-08-28-modular-rebuild/implementation-plans/01_EXECUTOR_CONTRACT.yaml`](./implementation-plans/01_EXECUTOR_CONTRACT.yaml)
- Execution Integrity: [`.agents/rules/ipos-execution-integrity.md`](../../../../.agents/rules/ipos-execution-integrity.md)
- Context & Invariants: [`AGENTS.md`](../../../../AGENTS.md)

---

## 1. Runtime Environment & Dual-Filesystem Anchor

IPOS operates under a dual-filesystem model with execution rooted in **native Linux ext4 under Hermes**:

* **Primary Execution Environment (Linux)**:
  - **OS**: Ubuntu WSL2 on Windows 11.
  - **Filesystem**: Native Linux ext4 (`/root/workspaces/Investment`).
  - **Branch**: `ipos-modular-rebuild-2026-08-28` (synchronized bit-for-bit with the Windows host clone).
  - **Hermes Orchestrator**: Installed natively at `/usr/local/bin/hermes` (`v0.20.5`, provider `opencode-free`, model `muse-spark-1.2-contributor-free`).
  - **Hermes Profile**: Dedicated IPOS profile at `/root/.hermes/profiles/investment/` with governing invariants persisted in `SOUL.md`.
* **Host Workstation Environment (Windows)**:
  - **Filesystem**: `C:\GitDev\Investment\` (NTFS).
  - Used for IDE editing, Git synchronization, and operator command interface.
* **IPOS Evidence Custody & Workspace Anchor**:
  - Karakeep is anchored directly in the **`Investment` workspace on native ext4** (`/root/workspaces/Investment/`). It is the dedicated IPOS research/evidence archive, completely separate from the general KI-Basis enterprise stack.
  - Hermes connects to Karakeep via read-only REST / MCP (`http://localhost:3000` or local endpoint) strictly under the `investment` profile without mutation privileges.
  - Supporting ingress / webhook event tools (Activepieces) attach cleanly via the single Edge Gateway without artificial micro-subnets.

---

## 2. Status of the First Operational Layer Modules

```
[M01] Hermes Baseline (PASS & COMMITTED: 3b70a1c)
 ├── [M02] Telegram Channel & Authenticated Webhooks (Pending Operator Credentials)
 ├── [M03] Public Ingress Edge (Single Gateway Ingress Route)
 │    └── [M04] Activepieces Platform (Unified Docker Environment)
 │         ├── [M06] Action / Watch Register (Activepieces Tables)
 │         └── [M05] Email Ingestion Flows (Gmail & WEB.DE -> Karakeep -> Hermes)
 └── [M07] Karakeep Evidence Custody (READY FOR IMMEDIATE EXECUTION)
```

### Module Breakdown

| Module | Title | Status | Details / Blocker |
|---|---|---|---|
| **`M01`** | Hermes Baseline & Investment Profile | **PASS (VERIFIED)** | Runtime verified; profile `investment` created; invariants enforced; negative test refusing broker orders passed. Commit `3b70a1c`. |
| **`M07`** | Karakeep Evidence Custody | **READY NOW** | Straightforward service deployment in unified Docker environment; read-only Hermes MCP client integration; test fixtures for URL, PDF, RSS. |
| **`M02`** | Telegram & Authenticated Webhook Intake | **BLOCKED (OPERATOR)** | Requires: 1) Bot Token from `@BotFather`, 2) Private Group ID with Topics, 3) Operator User IDs allowlist. |
| **`M03`** | Minimal Public HTTPS Ingress | **DECISION GATE** | Single edge gateway selection: Cloudflare Tunnel vs. Caddy reverse proxy. |
| **`M04`** | Activepieces Event Platform | **PENDING M03** | Unified Docker service connected to M03 public webhook URL. |
| **`M06`** | Action / Watch Register | **PENDING M02+M04** | Activepieces Tables CRUD; deterministic upsert; Hermes register query mapping. |
| **`M05`** | Email Ingestion Flows | **PENDING M02+M04+M07** | WEB.DE (IMAP SSL/993) & Gmail connectors; common normalized event schema; evidence referencing. |

---

## 3. Parallel Bootstrap Option: M10–M14 Bootstrap Slice

If you prefer to advance the quantitative analytical and portfolio modules while waiting on external ingress/credentials:
* **Handoff Document**: [`ANTIGRAVITY_M10_M14_HANDOVER.md`](./implementation-plans/ANTIGRAVITY_M10_M14_HANDOVER.md)
* **Contract**: [`05_ANTIGRAVITY_M10_M14_SLICE.yaml`](./implementation-plans/05_ANTIGRAVITY_M10_M14_SLICE.yaml)
* **Scope**:
  - `M10`: OpenBB ODP local/free data POC.
  - `M11`: Portfolio CSV/PDF normalizer.
  - `M12`: Wealthfolio desktop/local integration POC.
  - `M13`: Riskfolio-Lib deterministic optimization engine.
  - `M14`: TA-Lib technical computation engine.

---

## 4. Immediate Execution Recommendation

To realize the **First Operational Layer** without delay:
1. **Execute `M07` (Karakeep Evidence Custody)**:
   - Deploy Karakeep anchored directly within the `Investment` workspace on native ext4 (`/root/workspaces/Investment/`).
   - Configure native ext4 storage volumes (`karakeep-data`).
   - Wire the Hermes `investment` profile to Karakeep via read-only MCP / REST (`http://localhost:3000` or local endpoint).
   - Ingest and verify URL and PDF research fixtures.
   - Run independent adversarial verification via `ipos-proof-verifier`.
2. **In Parallel**:
   - Provide the Telegram bot token and group ID for **`M02`**.
   - Select the ingress route for **`M03`**.
