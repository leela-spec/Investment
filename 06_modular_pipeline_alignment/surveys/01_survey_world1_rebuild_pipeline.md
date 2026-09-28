# IPOS World 1 Architecture Survey Report: Modular Rebuild Pipeline & WF-07 Decision Flow

**Author**: Pipeline Architecture Explorer (Teamwork Survey World 1)  
**Date**: 2026-09-28  
**Repository Root**: `C:\GitDev\Investment`  
**Governing Branch**: `main` (commit baseline: `c5aa649`)  
**Audited Test Suite**: 271 / 271 unit & integration tests passing (`uv run pytest`)  
**Target Reference**: Ratified Consolidated WSL2 Architecture (`03-wsl2-native-stack-consolidation`)  

---

## 1. Executive Summary

This survey provides an exhaustive, code-grounded investigation of **World 1 — The IPOS Modular Rebuild Pipeline and the Research-to-Portfolio Decision Flow (WF-07 Stages 1–6)**.

The IPOS (Investment Process Operating System) architecture harmonizes three distinct computational environments:
1. **Windows 11 Host Native Python Runtime (`.venv`)**: Houses the sovereign quantitative core—DuckDB analytical warehouse, 22 macro indicators, 126 seminar rules, regime classifier, contradictions engine, C11/E04 portfolio accounting IBOR, Riskfolio-Lib 7.3.0 convex optimizer, Stage 4 macro decision engine, Stage 5 Action Matrix reconciler, and Stage 6 staged order ticket generator.
2. **WSL2 "Apex" Consolidated Docker Engine (Ubuntu ext4)**: Houses the asynchronous background ingestion and AI narration sidecars—Karakeep evidence custody, Activepieces event intake, WhisperX audio transcription, and Hermes Agent running under the `investment` profile.
3. **External & Desktop Peripherals**: Portfolio Performance (local desktop/file IBOR ingestion), Wealthfolio (local Windows desktop visual client in `%APPDATA%\com.teymz.wealthfolio`, fail-closed), and TradingView Pro (cloud technical analysis workbench, webhook alerts, and chart CSV exports).

### Governing Non-Negotiable Invariants
- **Governing Axiom**: *Code computes everything numeric; the LLM only narrates and orchestrates.* No LLM is permitted to generate or alter portfolio weights, order quantities, limit prices, or risk scores.
- **Zero Automated Trade Execution**: IPOS stops strictly at the generation of structured limit order tickets for sovereign manual entry at the broker (`SMARTBROKER` vs `ZERO`). Zero broker API keys, zero automated execution network calls, zero execution sockets.
- **Zero Cross-OS 9P Database Locks**: `warehouse.duckdb`, SQLite databases, and volatile state never cross the 9P virtual mount boundary (`/mnt/c/`). All inter-OS communication is asynchronous, immutable, and file/receipt-based.
- **Single-Branch Discipline**: All development and automated runs occur directly on `main`.

---

## 2. Detailed Inventory of the External Toolchain

The August 28 – September 2026 Modular Rebuild strictly enforces a **"Reuse Proven Products Before Custom Code"** philosophy, rejecting custom prototypes and unverified mocks.

| Tool / Product | Version / License | Hosting / Execution Environment | Architectural Role in IPOS | Supported Integration Seam | Data Egress & Privacy Posture |
|---|---|---|---|---|---|
| **Riskfolio-Lib** | `7.3.0`<br>BSD-3-Clause | Native Windows Python (`.venv`) | Stage 4/5 Portfolio Optimization: Convex Risk Parity (`rp.Portfolio.rp_optimization`), Hierarchical Risk Parity (`rp.HCPortfolio`), Min-Risk, Max Sharpe, Euler risk contributions ($RC\%$). | Python Library API (`import riskfolio as rp`), called from `ipos/portfolio/optimizer.py` | `LOCAL_ONLY`<br>Zero network traffic; sockets blocked during optimization. |
| **Portfolio Performance** | `0.7x`<br>EPL-1.0 | Windows Desktop / Local Files | Stage 1/5 Authoritative Broker Ingestion: Ingests raw Smartbroker/DAB and finanzen.net zero statements; outputs canonical CSVs (`Buchungen.csv`, `Vermögensaufstellung.csv`). | Typed Python parser in `ipos/portfolio/pp_adapter.py` with delimiter and German/English locale sniffing. | `LOCAL_ONLY`<br>Local file parsing; zero external network dependencies. |
| **OpenBB Platform Core (ODP)** | `v4.x`<br>AGPL-3.0 | Native Windows Python (`.venv`) | Stage 4 Secondary Market/Macro Data Feed: Provides dual-feed redundancy (C10) as failover for FRED, Stooq, and US Treasury feeds. | Python API / CLI (`openbb`), tested in `tests/test_m10_openbb.py`. | `LOCAL_WITH_OPTIONAL_EXTERNAL_DATA_CALLS`<br>Local core; provider calls leave host only as configured. |
| **Karakeep** | Latest<br>Open Source | Containerized in WSL2 Docker on ext4 (`ki-basis-shared-postgres`) | Stage 1 Research Evidence Custody: Cryptographic custody and full-text search for macro whitepapers, analyst emails, transcripts, and presentation slides. | REST API / Read-Only MCP Server (`mcp-karakeep-read`); SHA-256 content-addressing. | `LOCAL_ONLY` (default)<br>`LLM_EGRESS_CONDITIONAL` if external LLM tagging is configured. |
| **TradingView Pro** | Sunk Subscription<br>Proprietary Cloud | Cloud SaaS (TradingView Web/Desktop) | Stage 5/6 Technical Workbench: Multi-timeframe chart reviews, market structure, ATR trailing stops, Watchlist Alerts, and chart-data CSV exports. | Outbound HTTPS Webhook POST alerts; manual chart-data CSV export. | `CLOUD_SERVICE`<br>Strictly public symbols and technical alerts; NO private portfolio holdings or transactions. |
| **Hermes Agent** | Nous Research<br>Open Source | WSL2 Ubuntu Container / CLI (`investment` profile) | Stage 3/6 Orchestrator & Narrator: Evaluates research claims for thesis invalidation; updates `action_watch_register.json`; narrates `snapshot.json` into executive `report.md`. | Standard MCP client (connecting to read-only toolsets); CLI invocation (`hermes narrate snapshot.json`). | `LLM_EGRESS_CONDITIONAL`<br>Context sent to approved LLM inference provider; minimum-context redaction applied. |
| **Activepieces** | Community Edition<br>MIT / Open Source | Containerized in WSL2 Docker on ext4 | Stage 1 Intake Automation: Non-critical sidecar routing incoming WEB.DE IMAP emails, Gmail alerts, and TradingView webhooks into normalized envelopes. | Webhook receivers, IMAP triggers, HMAC-signed dispatches to Hermes webhook routes. | `LOCAL_ONLY`<br>Local event intake; outbound payloads only to connected local endpoints. |
| **Wealthfolio** | `v3.8.0`<br>Local-First Desktop | Windows Desktop App (`%APPDATA%\com.teymz.wealthfolio`) | Stage 5 Visual Portfolio Presentation: Optional offline GUI for dividend tracking and visual IBOR inspection. Connect service is DISABLED. | Desktop CSV/JSON import/export. Code intentionally fails closed (`INTEGRATION_STATUS = "NOT_CONNECTED"` in `wealthfolio.py`). | `LOCAL_ONLY`<br>Local SQLite storage; zero cloud sync when Connect is disabled. |

---

## 3. Step-by-Step Breakdown of WF-07 Stages 1 through 6

The Research-to-Portfolio Decision Flow (`00_runbook/WF07_RESEARCH_TO_PORTFOLIO_DECISION_FLOW.md`) translates qualitative research into sovereign manual broker orders across six deterministic stages:

```mermaid
flowchart TB
    subgraph S1 ["Stage 1: Evidence Custody & Ingestion (WSL2 / Docker)"]
        RawMedia["Raw Media (YouTube / PDF / Email)"] --> YtDlp["M08 Media Engine (yt-dlp)"]
        YtDlp --> Karakeep[("Karakeep Custody\n(ext4 / Docker Postgres)\nSHA-256 Custody Receipt")]
    end

    subgraph S2 ["Stage 2: Signal Extraction & Quote Grounding (WSL2 / Windows)"]
        Karakeep --> WhisperX["WhisperX ASR + Phoneme Alignment\nPySceneDetect Slide Extractor"]
        WhisperX --> Claims["ipos.evidence.claims\nverify_quote_grounding()\nsanitize_malicious_instruction()"]
        Claims --> ClaimCard["ExtractedClaim\n(exact ms timestamps [start, end])"]
    end

    subgraph S3 ["Stage 3: Thesis Invalidation & Action Watch (Hermes / Windows)"]
        ClaimCard --> HermesEval["Hermes Thesis Invalidation Engine\n(Profile: 'investment')"]
        HermesEval --> RegEngine["ipos.evidence.register\nActionWatchRegister.upsert_item()"]
        RegEngine --> RegFile[("data/action_watch_register.json\n(BOM-free Atomic UTF-8)\nOPEN -> TRIGGERED -> RESOLVED")]
    end

    subgraph S4 ["Stage 4: Quantitative Stance & Sector Tilts (Native Windows)"]
        RegFile --> MacroEngine["ipos.advisor.rule_engine (126 Rules)\nipos.aggregate.regime (Regime Classifier)\nipos.portfolio.decision.MacroPortfolioDecisionEngine"]
        MacroEngine --> Tilts["Sector Tilt Multipliers [0.20, 1.80]\n20% Research Alert Invalidation Penalty (0.80x)\nAsymmetric Gating: Low Conf / UNCERTAIN -> HOLD (GATED)"]
    end

    subgraph S5 ["Stage 5: Portfolio Allocation & Action Matrix (Native Windows)"]
        Tilts --> Optimizer["ipos.portfolio.optimizer.RiskfolioOptimizer\nRiskfolio-Lib 7.3.0 Convex Risk Parity"]
        PPData["Authoritative Broker IBOR\n(ipos.portfolio.pp_adapter / normalizer)"] --> ActionMat["ipos.portfolio.action_matrix.build_action_matrix()"]
        Optimizer --> ActionMat
        ActionMat --> MatrixOut["Concrete Action Matrix\n(TRIM / BUY / HOLD / SELL / HOLD (GATED))\nRegime Trailing Stop Policies"]
    end

    subgraph S6 ["Stage 6: Execution Gate & Order Staging (Native Windows & Human)"]
        MatrixOut --> Stager["ipos.portfolio.order_staging.stage_orders_from_action_matrix()"]
        Stager --> Batch1["Batch 1: Capital Release (TRIM/SELL descending EUR)\nLimit Price -0.5% Buffer"]
        Stager --> Batch2["Batch 2: Capital Deployment (BUY descending EUR)\nLimit Price +0.5% Buffer"]
        Batch1 --> Digest["Hermes Weekly Narrative Digest (report.md)"]
        Batch2 --> Digest
        Digest --> Operator["Sovereign Human Operator\nManual Order Entry at SMARTBROKER / ZERO\nZero Live Broker API Execution"]
    end
```

### Stage 1: Evidence Custody & Ingestion
- **Actor & Environment**: M08 Media Engine running in Ubuntu WSL2 / Docker.
- **Inputs**: Raw video URLs (YouTube macro interviews, Fed press briefings), PDF research papers, analyst emails from WEB.DE / Gmail.
- **Execution Mechanism**:
  1. `yt-dlp` extracts high-fidelity audio (`.m4a`).
  2. `PySceneDetect` segments video and extracts representative chart and table slides.
  3. Asset is registered in Karakeep with a cryptographic SHA-256 custody hash.
- **Outputs**: Content-addressed media record in Karakeep and raw audio drop in `data/inbox/research/` (e.g. `implementation-runs/E05/20260923-230911/audio.json` with SHA-256 `6c4d790d869f2aa31d0a02299a1ba84fd75b498b537f3aa757882ae6e5343b76`).

### Stage 2: Signal Extraction & Monotonic Quote Grounding
- **Actor & Environment**: Candidate WhisperX transcription engine in WSL2; verification engine in native Windows Python (`ipos/evidence/claims.py` and `ipos/evidence/ingest.py`).
- **Execution Mechanism**:
  1. WhisperX performs Voice Activity Detection (VAD) and phoneme-level word alignment, generating timestamped segments (`TranscriptSegment`) with word-level start/end floats (`TranscriptWord`).
  2. `verify_quote_grounding(quote, segments)` mathematically searches the segment word array to locate the exact verbatim substring, extracting continuous start/end seconds:
     ```python
     # ipos/evidence/claims.py:71-100
     def verify_quote_grounding(quote: str, segments: List[TranscriptSegment]) -> Tuple[bool, float, float, List[int]]:
     ```
  3. `sanitize_malicious_instruction(text)` scans text against `MALICIOUS_PATTERNS` (e.g. `ignore previous instructions`, `buy 100% of`, `drop table`, `system prompt override`). Adversarial payloads are defanged into `[QUARANTINED_PROMPT_INJECTION: ...]` and marked `is_malicious = True`.
  4. Extracted claims are mapped to canonical models (`ExtractedClaim` in `ipos/evidence/schemas.py`).
- **Outputs**: Validated `ExtractedClaim` instances with exact millisecond timestamps and source provenance.

### Stage 3: Thesis Invalidation & Action Watch Register
- **Actor & Environment**: Hermes Agent operating under the `investment` profile; single-writer register manager in `ipos/evidence/register.py`.
- **Execution Mechanism**:
  1. Hermes reviews extracted claims against active portfolio theses (e.g., Thesis: "Overweight Equities on imminent rate cuts"; Claim: "Sticky services inflation delays Fed easing").
  2. When thesis invalidation or a watch threshold is detected, Hermes invokes register update.
  3. `ActionWatchRegister.upsert_item(item)` enforces:
     - Idempotent upserting keyed on `item_id`.
     - Boundary prompt-injection sanitization (items with injections are quarantined).
     - Strict FSM lifecycle: `OPEN` $\to$ `TRIGGERED` | `EXPIRED` | `QUARANTINED`; `TRIGGERED` $\to$ `RESOLVED` | `EXPIRED`.
     - Atomic persistence to disk via temporary file rename (`.tmp` $\to$ `.json`) with BOM-free UTF-8 encoding.
- **Outputs**: `data/action_watch_register.json` updated with active `WatchItem` entries (class `ACTION` or `WATCH`).

### Stage 4: Quantitative Stance Engine & Sector Allocations
- **Actor & Environment**: Pure Windows Python runtime (`ipos/advisor/rule_engine.py`, `ipos/aggregate/regime.py`, `ipos/portfolio/decision.py`). Zero container dependencies.
- **Execution Mechanism**:
  1. Evaluates 22 walking skeleton macro indicators from FRED, Stooq, and Treasury.
  2. Evaluates the 126 seminar rules grouped into structured rulebooks (Interest Rates, Liquidity, Inflation, Valuation, Momentum, Sentiment, Volatility, Breadth).
  3. Regime classifier calculates Retracement Ratio and Overlap Index over OHLC swing pivots, assigning one of four regimes: `CHOPPY` (0.50x risk scaler), `MOMENTUM` (0.75x), `UNCERTAIN` (0.40x), `TRENDY` (1.00x).
  4. Reads open `ACTION` items from `data/action_watch_register.json`.
  5. Deterministically maps holdings to 6 sector clusters: `TECHNOLOGY_AI`, `CRYPTO_DIGITAL_ASSETS`, `HEALTHCARE_BIOTECH`, `ENERGY_COMMODITIES`, `DEFENSE_INDUSTRIALS`, `FINANCIALS_VALUE`.
  6. Computes macro tilt multipliers per sector based on stance vector dimensions (Equity, Duration, Commodities, Credit, Growth, USD).
  7. Applies a **20% defensive penalty (`base_mult *= 0.80`)** to sectors with active research thesis invalidation alerts (`ipos/portfolio/decision.py:355`).
  8. Enforces strict numeric bounds on tilt multipliers:
     ```python
     # ipos/portfolio/decision.py:359
     mult = max(0.20, min(1.80, base_mult))
     ```
  9. Enforces **Asymmetric Gating Rules**:
     - **Confidence Gate**: Macro confidence $< 50.0\%$ or regime `UNCERTAIN` sets `allow_adds = False`.
     - **Regime Gate**: `UNCERTAIN` triggers `DEFENSIVE_BLOCK`.
     - **Contradiction Gate**: $\ge 2$ high/critical contradictions triggers `BLOCKED` (`allow_adds = False`).
     - **Capital Preservation Invariant**: `allow_trims = True` and `allow_sells = True` unconditionally.
- **Outputs**: `MacroPortfolioDecision` object containing sector tilt multipliers, target sector weights, and gating verdict.

### Stage 5: Portfolio Allocation & Action Matrix
- **Actor & Environment**: Pure Windows Python runtime (`ipos/portfolio/optimizer.py`, `ipos/portfolio/action_matrix.py`, `ipos/portfolio/normalizer.py`, `ipos/portfolio/pp_adapter.py`).
- **Execution Mechanism**:
  1. Authoritative portfolio holdings and cash balances are loaded via `pp_adapter.py` / `normalizer.py` (replaying 332 confirmed activities across Smartbroker and finanzen.net zero).
  2. `RiskfolioOptimizer.optimize_portfolio()` executes native Riskfolio-Lib 7.3.0 convex Risk Parity (`rp.Portfolio.rp_optimization`) or HRP (`rp.HCPortfolio`) under sector bounds and risk budget constraints with network sockets blocked.
  3. `build_action_matrix()` compares current holdings against target weights:
     $$\Delta W_i = W_{i,\text{target}} - W_{i,\text{actual}}$$
  4. Categorizes each instrument into:
     - `TRIM`: $\Delta W_i < -\text{threshold}$ (reduces position, FIFO lot identification).
     - `BUY`: $\Delta W_i > +\text{threshold}$ (permitted if `allow_adds = True`).
     - `HOLD (GATED)`: $\Delta W_i > +\text{threshold}$, but converted because macro confidence $<50\%$, regime is `UNCERTAIN`, or contradictions are active.
     - `SELL`: Complete liquidation.
     - `HOLD`: $|\Delta W_i| \le \text{threshold}$ (within 1% tolerance band).
  5. Attaches regime-modulated stop loss policies (tight pivot stop for `CHOPPY`; wide 3x ATR stop for `TRENDY`).
- **Outputs**: Structured Action Matrix dictionary (`summary`, `items`, `risk_diagnostics`).

### Stage 6: Execution Gate & Sovereign Order Staging
- **Actor & Environment**: Pure Windows Python (`ipos/portfolio/order_staging.py`), Hermes Narrator CLI, and Sovereign Human Operator.
- **Execution Mechanism**:
  1. `stage_orders_from_action_matrix()` converts Action Matrix items into structured `OrderTicket` specifications.
  2. Routes orders to specific custodian broker accounts based on `configs/portfolio_mapping.yaml`:
     - `SMARTBROKER` (e.g. SPY, TLT, legacy equities, DAB bank custodian).
     - `ZERO` (e.g. European equities, zero-fee savings plans).
  3. Enforces **Deterministic Priority Batching**:
     - **Batch 1 (Capital Release)**: Defensive `TRIM` and `SELL` actions execute first to liberate cash. Sorted descending by absolute capital released (`abs(delta_val)`).
     - **Batch 2 (Capital Deployment)**: Permitted `BUY` actions execute second, funded by Batch 1 cash. Sorted descending by capital deployed (`delta_val`).
  4. Pure numeric limit price buffer protection:
     - `TRIM` / `SELL`: Limit price has **downside buffer of 0.5%** (`unit_price * 0.995`) to guarantee minimum execution price floor.
     - `BUY`: Limit price has **upside cap of 0.5%** (`unit_price * 1.005`) to prevent paying runaway ask prices.
     - Quantities rounded to whole-share integer quantities (`shares = int(...)`).
  5. Hermes CLI runs on-demand (`hermes narrate snapshot.json`) to synthesize `report.md` explaining macro drivers, fired rules, and research citations without altering numbers.
  6. **Execution Gate**: Automated trade execution is completely excluded from the codebase. The human operator logs into the broker web portals and enters the limit order tickets manually.
- **Outputs**: Staged order tickets in `report.md`, `report.html`, and `data/exports/snapshot.json`.

---

## 4. Comprehensive User Story Decomposition

Mapping the IPOS architecture to 12 concrete User Stories across execution environments, exact file paths, and data schemas:

### Domain A: Sovereign Quantitative & Research Stories

#### US-01: Research Evidence Ingestion & Cryptographic Custody
- **Execution Environment**: WSL2 Ubuntu / Docker (`ki-basis-shared-postgres`, Karakeep container).
- **Files**: `data/inbox/research/`, Karakeep REST API / MCP.
- **Input / Output**: Raw PDF whitepaper / Web URL $\to$ Immutable Karakeep asset + SHA-256 custody receipt (`.receipt.json`).
- **Schema**:
  ```json
  {
    "receipt_id": "RCP-20260928-01",
    "source_url": "https://federalreserve.gov/monetarypolicy/fomcpresconf20260923.htm",
    "sha256": "6c4d790d869f2aa31d0a02299a1ba84fd75b498b537f3aa757882ae6e5343b76",
    "ingested_at": "2026-09-28T08:00:00Z",
    "byte_size": 1048576,
    "karakeep_urn": "karakeep:entries:8492"
  }
  ```

#### US-02: Macro Video Acquisition & Slide Extraction (M08)
- **Execution Environment**: WSL2 Ubuntu CLI.
- **Files**: `yt-dlp`, `faster-whisper` / `whisperx`, `PySceneDetect`.
- **Input / Output**: YouTube video URL $\to$ `.m4a` audio stream + timestamped transcript `audio.json` + key slide frames (`slides/*.png`).
- **Schema**: `TranscriptSegment` and `TranscriptWord` models in `ipos/evidence/schemas.py`.

#### US-03: Source-Grounded Claim Extraction & Thesis Invalidation (M09 / WF-07)
- **Execution Environment**: Native Windows Python (`ipos/evidence/`) + Hermes CLI (`investment` profile).
- **Files**: `ipos/evidence/claims.py`, `ipos/evidence/register.py`, `data/action_watch_register.json`.
- **Input / Output**: Transcript JSON $\to$ `ExtractedClaim` with exact millisecond quote grounding $\to$ `WatchItem` upserted to `action_watch_register.json`.
- **Schema**:
  ```json
  {
    "item_id": "ACT-202609-003",
    "item_class": "ACTION",
    "instrument_or_topic": "TECHNOLOGY_AI",
    "action_or_condition": "TRIM_EQUITY_RISK_POSTURE",
    "reason_short": "Fed pause prolonged; 10Y real yield upward pressure",
    "linked_claim_ids": ["CLM-20260923-01"],
    "evidence_refs": ["karakeep:entries:8492#t=1423"],
    "status": "OPEN",
    "created_at": "2026-09-28T08:15:00Z"
  }
  ```

#### US-04: Autonomous Saturday Macro Indicator Sweep (WF-05 / C08)
- **Execution Environment**: Windows Task Scheduler $\to$ Native Windows Python 3.12 (`.venv`).
- **Files**: `scripts/run_pipeline_automated.ps1`, `scripts/register_scheduler.ps1`, `ipos/run.py`, `data/warehouse.duckdb`.
- **Trigger**: Every Saturday 06:00 (with `-StartWhenAvailable` catch-up).
- **Execution**: Evaluates 22 indicators, 126 seminar rules, regime classifier, updates DuckDB single-writer warehouse, writes `data/exports/snapshot.json` and `report.html` in $< 15$ seconds. Idle RAM footprint: **0 MB**.

#### US-05: Multi-Currency Broker Reconciliation & FIFO Lot Relief (C11 / E04)
- **Execution Environment**: Native Windows Python (`.venv`).
- **Files**: `ipos/portfolio/pp_adapter.py`, `ipos/portfolio/normalizer.py`, `ipos/portfolio/accounting.py`.
- **Input / Output**: Raw Smartbroker CSVs (`3370191001-*.csv`) and finanzen.net zero exports $\to$ canonical IBOR with multi-currency cash (`EUR`, `USD`, `CAD`, `CHF`), weighted-average cost basis, and FIFO tax lot relief.
- **Verification**: Exactly 24 open holdings match official PDF broker control (100% MATCH), preserving NDA (1,000) and PSYC (10,000).

#### US-06: Macro Stance & Hierarchical Sector Clustering Rebalancing (C13 / WF-07)
- **Execution Environment**: Native Windows Python (`.venv`).
- **Files**: `ipos/portfolio/decision.py`, `ipos/portfolio/optimizer.py`, `ipos/portfolio/returns.py`.
- **Execution**: Translates macro stance into sector headwinds/tailwinds across 6 clusters; applies 20% thesis invalidation penalty; clamps multipliers to $[0.20, 1.80]$; Riskfolio-Lib 7.3.0 solves convex Risk Parity target weights ($RC\%$, ENC = 2.08) with sockets blocked.

#### US-07: Action Matrix Generation & Sovereign Human Order Placement (WF-07 Stage 5/6)
- **Execution Environment**: Native Windows Python (`.venv`).
- **Files**: `ipos/portfolio/action_matrix.py`, `ipos/portfolio/order_staging.py`.
- **Execution**: Computes holding deltas ($\Delta W_i$), classifies TRIM/BUY/HOLD/SELL/HOLD (GATED), attaches regime trailing stops, routes to `SMARTBROKER` vs `ZERO`, batches by Capital Release (Batch 1) vs Capital Deployment (Batch 2), applies $\pm 0.5\%$ price buffers.
- **Output**: Terminal Action Matrix and structured `OrderTicket` specifications.

#### US-08: Visual IBOR Reconciliation & Desktop Verification (C12 Wealthfolio)
- **Execution Environment**: Windows 11 Desktop (Electron/Tauri GUI).
- **Files**: `%APPDATA%\com.teymz.wealthfolio`, `ipos/portfolio/wealthfolio.py`.
- **Status**: Visual inspection only; Connect service disabled. `wealthfolio.py` intentionally fails closed (`INTEGRATION_STATUS = "NOT_CONNECTED"`) to prevent unverified synchronization dependencies.

#### US-09: Weekly Executive Review Briefing & Notification Delivery (Hermes Narrator)
- **Execution Environment**: WSL2 Container / CLI + Telegram Bot API.
- **Files**: `ipos/ai/narrator.py`, `configs/ai.yaml`, `data/exports/snapshot.json`, `report.md`.
- **Execution**: Hermes reads `snapshot.json` and active Karakeep citations; synthesizes `report.md`; delivers narrative briefing to allowlisted Telegram group topic (Actions, Alerts, Research, Weekly Review).

---

### Domain B: Cross-Workspace & Community Operational Stories

#### US-10: Community Operations & Expense Intake (KI-Basis Stack)
- **Execution Environment**: WSL2 "Apex" Docker Engine (`ki-basis-shared-postgres`).
- **Files**: Paperless-ngx (`priv_paperless`), Firefly III (`priv_firefly`), OpenProject (`priv_openproject`).
- **Execution**: Event invoices for Safer Space e.V. processed via Paperless-ngx OCR and Firefly III accounting without touching IPOS data.

#### US-11: Cross-Workspace Meta-Orchestration over All 4 Repositories
- **Execution Environment**: WSL2 ext4 / Hermes Global Meta-Orchestrator.
- **Target Repositories**: `Investment`, `MasterOfArts`, `lika-community`, `acim-secular`, and `apexai-os-meta`.
- **Execution**: Hermes coordinates cross-repo schedules and system sweeps while respecting strict repository quarantine boundaries.

#### US-12: Preserving Untouched Community Operations on Docker Desktop
- **Execution Environment**: WSL2 LinuxKit VM / Docker Engine.
- **Ports & Boundaries**: Community services hosted on host ports (`8084`, `8082`, `8010`, `8086`, `3000`) completely isolated from Windows Python IPOS runtime (`127.0.0.1`). Zero cross-tenant contamination.

---

## 5. Inventory of the 271 Pytest Unit/Integration Tests

The IPOS test suite contains **271 tests across 34 test files**, executed via `uv run pytest`. All 271 tests are verified **100% passing**.

```
========================================================================================
Test Execution Summary: 271 passed in 48.32s (100% Green Baseline)
========================================================================================
```

### Complete Test File Breakdown

| # | Test File Path | Tests | Test Category | Tested Capabilities & Invariants |
|---|---|---:|---|---|
| 1 | `tests/test_action_matrix.py` | 7 | Portfolio Action Matrix | Rebalancing delta calculations, TRIM/BUY/HOLD classification, regime stop policy attachment, Riskfolio target weight integration. |
| 2 | `tests/test_ai.py` | 9 | AI Narration & Token Budget | Token cap enforcement ($\le 9.4\text{k}$ tokens/week), $0 offline narrator (`provider: none`), fallback handling. |
| 3 | `tests/test_calendar.py` | 4 | Market Calendar & Dates | Friday canonical `as_of_date` calculation, market holiday shifts. |
| 4 | `tests/test_canonical.py` | 2 | Canonical Normalization | Time-series canonicalization, date index alignment. |
| 5 | `tests/test_config.py` | 7 | Configuration Schemas | Pydantic model validation of `registry.yaml`, `contradictions.yaml`, and system settings (`extra='forbid'`). |
| 6 | `tests/test_connectors.py` | 9 | ETL Connectors | FRED, Stooq, DBnomics, US Treasury, and Yahoo Finance connector resilience. |
| 7 | `tests/test_contradictions.py` | 10 | Macro Contradictions | Inter-module contradiction rules, severity weighting (high/critical), threshold triggers. |
| 8 | `tests/test_etl.py` | 4 | ETL Pipeline Orchestration | Multi-source ingestion, raw Parquet archive generation. |
| 9 | `tests/test_evidence_claims.py` | 9 | WF-07 Stage 2 Claim Grounding | Word-level timestamp quote grounding, single/multi-segment matching, adversarial prompt-injection defanging. |
| 10 | `tests/test_evidence_ingest.py` | 6 | WF-07 Stage 1-3 Ingestion | Inbox discovery, cryptographic receipt hashing, idempotent upserting to `action_watch_register.json`. |
| 11 | `tests/test_failsafe.py` | 3 | Failsafe & Error Handling | Degraded network operation, offline cache replay fallbacks. |
| 12 | `tests/test_forecast.py` | 9 | Scenario Forecasts | Indicator projection curves, trend extrapolation. |
| 13 | `tests/test_golden.py` | 1 | End-to-End Regression | Full golden snapshot regression test verifying end-to-end pipeline consistency. |
| 14 | `tests/test_isolation.py` | 5 | Network & Security Isolation | Socket blocking during computation, zero execution leak, offline enforcement. |
| 15 | `tests/test_m10_openbb.py` | 5 | OpenBB Integration (C10) | OpenBB Platform Core imports, free provider query normalization, dual-feed redundancy. |
| 16 | `tests/test_m11_normalizer.py` | 14 | Portfolio Normalizer (C11) | Multi-currency FX conversion, FIFO lot relief, cost basis accounting, schema validation. |
| 17 | `tests/test_m12_wealthfolio.py` | 2 | Wealthfolio Integration (C12) | Fail-closed verification (`require_real_wealthfolio`), native desktop CSV export formatting. |
| 18 | `tests/test_m13_optimizer.py` | 14 | Riskfolio Optimizer (C13) | Riskfolio-Lib 7.3.0 convex Risk Parity, HRP, Min-Risk, linear inequality constraints ($A w \le B$), socket-blocked determinism. |
| 19 | `tests/test_m14_technical_engine.py` | 4 | Technical Indicators (C14) | ATR, swing pivot high/low detection, trailing stop distance calculations. |
| 20 | `tests/test_macro_decision.py` | 6 | Macro Decision Engine (Stage 4) | Sector tilt bounds $[0.20, 1.80]$, 20% thesis invalidation penalties, asymmetric rebalancing gating rules. |
| 21 | `tests/test_ohlc_regime.py` | 4 | OHLC Swing Regime | Retracement ratio, overlap index, swing pivot volatility calculations. |
| 22 | `tests/test_operational_automation.py` | 5 | Operational Automation (E10) | Task Scheduler script validation, BOM-free `automation_status.json`, log rotation. |
| 23 | `tests/test_order_staging.py` | 6 | Order Staging (Stage 6) | Batch 1 (defensive capital release) vs Batch 2 (deployment), limit order 0.5% buffers, broker account routing (`SMARTBROKER` vs `ZERO`). |
| 24 | `tests/test_portfolio.py` | 37 | Portfolio Accounting Core | Multi-asset position calculation, valuation currency conversion, cash balance tracking. |
| 25 | `tests/test_portfolio_audit_boundary.py` | 18 | Financial-Grade Audit Boundary | Zero mock facades, real library execution, IBOR reconciliation against official broker statements. |
| 26 | `tests/test_pp_adapter.py` | 7 | Portfolio Performance Adapter | German/English CSV dialect parsing, semicolon/comma delimiter sniffing, German decimal-comma parsing. |
| 27 | `tests/test_regime.py` | 6 | Regime Classifier (C04) | CHOPPY / TRENDY / MOMENTUM / UNCERTAIN classification, risk scaler assignment (0.40x to 1.00x). |
| 28 | `tests/test_replay.py` | 7 | Market Replay Engine | Historical date point-in-time state reconstruction. |
| 29 | `tests/test_report_html.py` | 13 | Reporting & HTML Dashboard | Static self-contained HTML generation, sparklines, tooltips, standalone scenario explorer. |
| 30 | `tests/test_riskfolio_pipeline.py` | 10 | Riskfolio Pipeline Integration | Euler percentage risk contribution ($RC\%$), Effective Number of Constituents (ENC), volatility scaling. |
| 31 | `tests/test_scoring.py` | 11 | Indicator Scoring (C03) | Percentile rank, z-score with tanh damping, band scoring tables. |
| 32 | `tests/test_snapshot.py` | 12 | Weekly Snapshot Schema | `snapshot.json` structure, JSON export compliance. |
| 33 | `tests/test_stop_gate.py` | 3 | Stop Policy Gates | Trailing stop tightening under CHOPPY regimes. |
| 34 | `tests/test_warehouse.py` | 2 | DuckDB Warehouse (C01) | Single-writer OLAP warehouse, read-only reader concurrency. |
| **Total** | **34 Files** | **271** | **All Categories** | **100% Passing (0 failures, 0 errors)** |

---

## 6. Identification of Pain Points, Gaps, and Inter-OS Boundaries

### 1. The 9P Cross-Filesystem Latency Penalty & File Locking
- **Problem**: When Linux containers or WSL2 processes access files mounted from the Windows host (`/mnt/c/GitDev/Investment`), all I/O is serialized through the Linux kernel `v9fs` driver across virtual sockets to Windows `wslservice.exe`. Small file creation is **123x slower** (14.8 ms vs 0.12 ms), and directory traversal is **308x slower** (185 ms vs 0.6 ms per 1,000 inodes). Concurrent file locks (`fcntl`/`flock`) over 9P fail, risking corruption of `warehouse.duckdb` and SQLite ledgers.
- **Architectural Solution**:
  - Keep `warehouse.duckdb` and all quantitative Python execution strictly on the native Windows NTFS filesystem (`C:\GitDev\Investment`).
  - Keep Karakeep, Activepieces, and Hermes workspace strictly on the WSL2 Linux ext4 virtual disk (`/var/lib/docker/volumes/`).
  - Communication across the OS boundary occurs strictly via **asynchronous, content-addressed, immutable file drops** (`snapshot.json`, `.receipt.json`, Parquet archives) or local REST/MCP sockets, never by sharing live database files across `/mnt/c/`.

### 2. Wealthfolio Desktop GUI vs Headless Containerization
- **Problem**: Wealthfolio is a Windows-native desktop application (`%APPDATA%\com.teymz.wealthfolio`), not a web service. Earlier sessions attempted to run Wealthfolio in headless Docker containers, which cannot launch or render Windows desktop GUIs. Furthermore, real import testing in Epic E02 revealed that Wealthfolio dropped 2 holdings (NDA, PSYC) and had a cash discrepancy.
- **Architectural Solution**:
  - Demote Wealthfolio to an optional, local visual presentation layer.
  - Keep `ipos/portfolio/wealthfolio.py` strictly **fail-closed** (`INTEGRATION_STATUS = "NOT_CONNECTED"`).
  - Use Portfolio Performance (`pp_adapter.py`) and native Python IBOR (`accounting.py`) as the authoritative investment ledger.

### 3. Activepieces & TradingView Webhook Ingestion Pipeline
- **Problem**: TradingView webhook alerts originate from TradingView's cloud servers. Activepieces runs inside WSL2 Docker. The IPOS engine runs on Windows.
- **Architectural Solution**:
  - Activepieces acts as an ingestion sidecar inside WSL2 Docker, receiving inbound webhooks from TradingView and emails from WEB.DE / Gmail.
  - Activepieces normalizes and HMAC-signs the event envelope, dispatching it to Hermes or writing a verified JSON drop to `data/inbox/`.
  - The Windows Task Scheduler runs the deterministic pipeline to process inbox drops, maintaining zero always-on listener bloat on the Windows host.

### 4. Single-Writer Boundary for `action_watch_register.json`
- **Problem**: Both the Windows Python evidence ingestion CLI (`ipos ingest-evidence`) and the WSL2 Hermes Agent write to `data/action_watch_register.json`. Uncoordinated cross-OS writes could cause race conditions, partial writes, or BOM encoding issues.
- **Architectural Solution**:
  - Enforce atomic file persistence using a temporary file replacement pattern (`.tmp` $\to$ `.json`) with BOM-free UTF-8 encoding (already implemented in `ipos/evidence/register.py`).
  - Establish Hermes MCP interface (`mcp-ipos-register`) to serialize register modifications through strict schema validation rather than arbitrary file writes.

### 5. Dependency Footprint: OpenBB ODP vs Native Connectors
- **Problem**: OpenBB Platform Core (ODP) introduces significant dependency overhead and deprecated Pydantic v2.12 classmethod validator warnings during test runs.
- **Architectural Solution**:
  - Maintain the **Dual-Feed Market Data Architecture (C10)**: Direct native connectors (`fred.py`, `stooq.py`, `treasury.py`, `yahoo.py`, `dbnomics.py`) serve as the primary institutional feed ($< 15\text{s}$ execution, zero extra dependencies).
  - OpenBB Platform Core serves strictly as an on-demand secondary failover feed.

---

## 7. Strategic Recommendations for Milestones M1–M4

Based on the verified reality of World 1, the upcoming harmonization milestones should proceed under these explicit directives:

1. **M1 (Consolidated Cross-Stack Topology Specification)**:
   - Codify the exact host port allocations (`8084`, `8086`, `8010`, `8642`, `3000`) and shared internal Docker network (`ki-basis-db-net`, `172.20.0.0/16`).
   - Ratify the two-lane inter-OS boundary: Windows Host NTFS for quantitative IPOS; WSL2 ext4 for containerized services.
2. **M2 (Deterministic Persistence & Anti-Regression Guardrails)**:
   - Formalize SHA-256 receipt tracking for all inbox research drops and broker statements.
   - Enforce BOM-free UTF-8 JSON persistence across all exports (`snapshot.json`, `action_watch_register.json`, `automation_status.json`).
   - Ensure the 271 pytest battery remains an unconditional CI/CD and pre-commit gate (100% pass requirement).
3. **M3 (Legacy Master Plan Reconciliation & Deprecation Matrix)**:
   - Audit the 9 meso clusters (C1–C9) against live code.
   - Formally **RETAIN** the mathematical core (126 rules in `rule_engine.py`, DuckDB warehouse, regime classifier, contradictions engine, 22 active indicators).
   - Formally **TRANSITION** custom optimization to Riskfolio-Lib 7.3.0 and custom broker scraping to Portfolio Performance.
   - Formally **DEPRECATE** obsolete scaffolding (unverified TTK concepts, OpenClaw/LangGraph drafts, always-on container daemons for IPOS).
4. **M4 (Phase 3 Indicator Expansion Roadmap)**:
   - Progressively activate candidates from `configs/registry_120.yaml` into the active `configs/registry.yaml` (targeting 60 core indicators across real yields, breakeven inflation, and credit spreads) using keyless and verified feeds.

---
*End of Report — Delivered by Pipeline Architecture Explorer.*
