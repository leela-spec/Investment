# Handover: Stage-by-Stage Implementation & Operational Contracts

> **AUDITOR & ENGINEER ORIENTATION — READ THIS FIRST**  
> **Repository Root:** `c:\GitDev\Investment`  
> **Branch of Record:** `main` (commit directly; no feature branches or long-lived worktrees)  
> **Primary Architecture Specification:** [`06_modular_pipeline_alignment/spec/04_CONSOLIDATED_PIPELINE_ALIGNMENT.md`](06_modular_pipeline_alignment/spec/04_CONSOLIDATED_PIPELINE_ALIGNMENT.md)  
> **Navigation Hub:** [`06_modular_pipeline_alignment/00_INDEX.md`](06_modular_pipeline_alignment/00_INDEX.md)  
> **Operational Roadmap:** [`06_modular_pipeline_alignment/ROADMAP_FUTURE_STEPS.md`](06_modular_pipeline_alignment/ROADMAP_FUTURE_STEPS.md)  
> **Reality Verification Suite:** [`06_modular_pipeline_alignment/audit/verify_reality_battery.py`](06_modular_pipeline_alignment/audit/verify_reality_battery.py)  
> **Date:** 2026-09-28 · **Status:** Active & Ratified

---

## 0. Two-Minute Kickoff Protocol (Mandatory)

Before writing any code or proposing changes, run these verification commands in PowerShell:

```powershell
# 1. Run the Reality Verification Battery (MUST report 5 PASSED, 0 FAILED)
uv run python 06_modular_pipeline_alignment/audit/verify_reality_battery.py

# 2. Run the full automated test suite (MUST report 271 passed)
uv run pytest

# 3. Run knowledge base QA checks (MUST report ALL REQUIRED TESTS PASSED)
uv run python scripts/qa_repo.py
```

### Governing Non-Negotiable Invariants:
1. **Governing Axiom**: *Code computes everything numeric; the LLM only narrates.* (Zero LLM arithmetic, position sizing, or limit price adjustments).
2. **Physical Environment Quarantine (9P Avoidance)**: Core Python quantitative code (`ipos/`), DuckDB files, and tests **MUST execute natively on Windows 11 NTFS** (`C:\GitDev\Investment\.venv`). Never execute core quantitative code inside WSL2/Docker mounted over `/mnt/c/` (prevents 300× I/O slowdowns and DuckDB file lock crashes).
3. **Desktop GUI Boundary**: **Wealthfolio** is a Windows desktop Tauri GUI application with **zero public REST API and zero CLI**. Never attempt to containerize it or wrap it in a mock API. Sync is strictly 1-click manual CSV export (`data/portfolio/wealthfolio_import.csv`).
4. **Single WSL2 Docker Engine**: All container services (PostgreSQL, Karakeep, Activepieces, Hermes) run inside the single WSL2-native **"Apex" Docker engine** (`ki-basis-shared-postgres`). Docker Desktop is uninstalled (D-09).
5. **Zero Facades**: External libraries (Riskfolio-Lib 7.3.0, Portfolio Performance, WhisperX) must execute authentic code. Never replace real execution with simulated return dicts or self-referential mock assertions.

---

## 1. Truthful Reality Matrix: What is ALREADY DONE vs. What to Implement

Do **NOT** waste time re-implementing what is already working and tested. The quantitative decision pipeline is 100% operational:

| WF-07 Pipeline Stage | Operational Status | Files & Verification | Action for This Chat |
|---|---|---|---|
| **Stage 1: Evidence Custody** | **SEMI-AUTOMATED** | Research drops processed via `data/inbox/research/`. | **ACTIVE MISSION 1**: Connect to live Karakeep REST API (`http://127.0.0.1:3000`). |
| **Stage 2: Claim Extraction & Grounding** | **100% OPERATIONAL** | [`ipos/evidence/claims.py`](ipos/evidence/claims.py), [`ingest.py`](ipos/evidence/ingest.py). Millisecond WhisperX quote grounding & anti-injection defense verified. | Stable. Do not modify. |
| **Stage 3: Thesis Invalidation & Register** | **100% OPERATIONAL** | [`ipos/evidence/register.py`](ipos/evidence/register.py), [`data/action_watch_register.json`](data/action_watch_register.json). FSM transitions (`OPEN` $\to$ `TRIGGERED` $\to$ `RESOLVED`). | Stable. Register is live. |
| **Stage 4: Quantitative Policy & Stance** | **100% OPERATIONAL** | [`ipos/portfolio/decision.py`](ipos/portfolio/decision.py), [`rule_engine.py`](ipos/advisor/rule_engine.py). Evaluates 126 seminar rules, 6 sector clusters, tilt bounds $[0.20, 1.80]$, and $0.80\times$ research penalties. | **ACTIVE MISSION 3**: Graduate candidate indicators from 22 to 60. |
| **Stage 5: Action Matrix & Risk Parity** | **100% OPERATIONAL** | [`ipos/portfolio/action_matrix.py`](ipos/portfolio/action_matrix.py), [`optimizer.py`](ipos/portfolio/optimizer.py). Native Riskfolio-Lib 7.3.0 convex Risk Parity and HRP. | Stable. Do not modify. |
| **Stage 6: Staged Order Tickets** | **100% OPERATIONAL** | [`ipos/portfolio/order_staging.py`](ipos/portfolio/order_staging.py). Priority Batch 1 (capital release) before Batch 2 (buys), whole shares, 0.5% limit buffers. | Stable. Zero execution leak verified. |
| **Operator Reporting & Digest** | **SEMI-AUTOMATED** | Generates static `report.html` and `report.md` via Windows Task Scheduler. | **ACTIVE MISSION 2**: Wire Hermes weekly Telegram channel dispatch. |

---

## 2. Active Implementation Missions (Prioritized)

### Mission 1: Live Karakeep REST / MCP Sync (Priority: HIGH)
- **Problem**: Qualitative research currently requires manually dropping transcripts and PDFs into `data/inbox/research/`.
- **Target**: Build `ipos/etl/karakeep.py` to query the live Karakeep container API running on `http://127.0.0.1:3000/api/v1/bookmarks`.
- **Implementation Requirements**:
  1. Add `KARAKEEP_API_KEY` and `KARAKEEP_URL` (default `http://127.0.0.1:3000`) configuration handling.
  2. Implement `fetch_tagged_evidence(tag="macro")`:
     - Queries Karakeep's REST endpoint.
     - Downloads newly archived PDFs, web HTML, or attached transcript JSON to `data/inbox/research/`.
     - Preserves Karakeep bookmark ID as `source_urn: "karakeep:entries:<id>"`.
  3. Wire into CLI: `uv run python -m ipos.cli ingest-evidence --source karakeep`.
  4. Write unit tests in `tests/test_karakeep_ingest.py` with mock-denial checks (must fail if network format changes).

### Mission 2: Hermes Weekly Telegram Digest Dispatch (Priority: MEDIUM)
- **Problem**: The weekly pipeline generates a high-quality `report.md`, but the operator must manually open the files.
- **Target**: Create `ipos/export/telegram.py` and CLI command `ipos notify-telegram` to dispatch the pre-computed summary to the operator's private Telegram topic.
- **Implementation Requirements**:
  1. Read pre-computed `data/exports/snapshots/YYYY-MM-DD/report.md`.
  2. Extract the **Executive Macro Stance**, **Regime Scaler**, **Active Contradictions**, and **Priority Batch 1 Order Tickets** (total message $< 4,000$ characters).
  3. Send via Telegram Bot API using `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` from `.env`.
  4. **Strict Invariant**: Zero LLM arithmetic. The script strictly formats pre-computed numbers into Markdown.

### Mission 3: Phase 3 Indicator Graduation (22 $\to$ 60 Breadth) (Priority: HIGH)
- **Problem**: Active registry runs 22 walking skeleton indicators; 120 candidate indicators are modeled in `configs/registry_120.yaml`.
- **Target**: Graduate 38 high-reliability candidate indicators into `configs/registry.yaml` to achieve the target 60-indicator breadth.
- **Key Candidates to Graduate**:
  - Real Yields: 10Y TIPS (`DFII10`), 5Y TIPS (`DFII5`) via FRED / US Treasury.
  - Breakeven Inflation: 10Y Breakeven (`T10YIE`), 5Y Breakeven (`T5YIE`).
  - Credit Spreads: High-Yield OAS (`BAMLH0A0HYM2`), IG OAS (`BAMLC0A0CM`).
  - Commodities: Copper/Gold ratio (`COPPER_GOLD`), WTI Term Structure.
  - Liquidity: Fed Net Liquidity (`FED_NET_LIQ`).
- **Implementation Requirements**:
  1. Validate live pulls using free keyless connectors (`dbnomics.py`, `ustreasury.py`) and FRED API.
  2. Update `configs/weights.yaml` with calibrated weights summing to 1.0 within each module.
  3. Run weekly pipeline: `uv run python -m ipos.cli weekly --as-of 2026-09-25` and confirm `status=OK`.
  4. Confirm all 271+ tests pass with zero synthetic leakage.

---

## 3. Copy-Paste Kickoff Prompt for the Next Session

Copy and paste the exact block below to start the next session:

```text
You are an independent Principal Quantitative Systems Engineer working in C:\GitDev\Investment.

We are implementing the Operational Stage Contracts for the IPOS pipeline.
Before doing anything:
1. Read HANDOVER_STAGE_IMPLEMENTATION.md, 06_modular_pipeline_alignment/00_INDEX.md, and 06_modular_pipeline_alignment/ROADMAP_FUTURE_STEPS.md.
2. Run the reality verification battery in PowerShell:
   uv run python 06_modular_pipeline_alignment/audit/verify_reality_battery.py (must report 5 PASSED).
3. Do not invent any fake REST APIs or mock wrappers. Wealthfolio is desktop GUI only; core Python runs on native Windows NTFS (no 9P cross-mounts).
4. Our mission for this session is Mission 1 (Live Karakeep REST Sync) and Mission 2 (Telegram Dispatch).

Implement the code in ipos/, verify with real tests, and prove that external dependencies actually execute. Show me git diff of code files when complete.
```
