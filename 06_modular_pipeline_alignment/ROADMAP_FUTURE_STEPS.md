# IPOS Concrete Future Implementation Roadmap

> **PURPOSE**: Defines the exact, prioritized operational next steps to connect external tools into the running pipeline, guarded against environmental drift, false completion, and overengineering.

---

## 1. Current State Baseline (The Truthful Reality)

Before starting any future work, verify this exact boundary:

| Layer | Physical Environment | Current Operational State | Next Action |
|---|---|---|---|
| **Quantitative Engine** | Windows 11 Native (`.venv`) | **100% OPERATIONAL & VERIFIED**<br>271 tests passing. Evaluates 126 rules, classifies regimes, runs Riskfolio-Lib 7.3.0, and generates buffered staged order tickets. | Ready for Phase 3 indicator graduation (22 $\to$ 60). |
| **Broker Ledger Replay** | Windows 11 Native (`.venv`) | **100% OPERATIONAL & VERIFIED**<br>Replays 332 Smartbroker activities to 24 holdings matching bank statement PDF with 0 discrepancies. | Stable; no code changes needed. |
| **WSL2 Docker Infrastructure** | WSL2 Ubuntu 26.04 ("Apex") | **100% OPERATIONAL & VERIFIED**<br>Single dockerd engine, shared PostgreSQL (`ki-basis-shared-postgres`) with strict `REVOKE CONNECT` role isolation. OpenProject 17.8 on port 8083. | Ready to host Karakeep & Activepieces. |
| **Qualitative Evidence Ingest** | Windows 11 Native (`.venv`) | **OPERATIONAL VIA DROP FOLDER**<br>Ingests WhisperX transcripts and PDFs from `data/inbox/research/` with word-level quote grounding and anti-injection defense. | Wire live HTTP query to Karakeep API. |
| **Wealthfolio GUI** | Windows 11 Desktop (`%APPDATA%`) | **FAIL-CLOSED BY DESIGN**<br>Rejects fake REST APIs. Supports 1-click manual CSV import via `data/portfolio/wealthfolio_import.csv`. | Keep manual desktop sync; never build fake APIs. |

---

## 2. Four Phased Implementation Steps

### Step 1: Live Karakeep REST / MCP Sync (Priority: HIGH)
- **Objective**: Automate qualitative research ingestion by querying Karakeep's live REST endpoint rather than requiring manual drops into `data/inbox/research/`.
- **Target Seam**: Karakeep API (`http://127.0.0.1:3000/api/v1/bookmarks`) with an API key generated from the Karakeep web UI.
- **Physical Environment**:
  - Karakeep container runs inside WSL2 "Apex" Docker engine on native ext4.
  - IPOS connector script runs in Windows Python (`.venv`) querying `http://127.0.0.1:3000` via localhost port forwarding.
- **Acceptance Criteria**:
  - [ ] Windows Python script `ipos/etl/karakeep.py` queries `GET /api/v1/bookmarks?tag=macro`.
  - [ ] Downloads attached PDFs and video transcripts to `data/inbox/research/`.
  - [ ] Ingest engine validates WhisperX quote grounding, records SHA-256 receipts, and updates `data/action_watch_register.json`.
- **Anti-Drift Guardrail**: NEVER attempt to mount Karakeep's internal PostgreSQL or Meilisearch volumes directly to Windows NTFS over 9P.

---

### Step 2: Hermes Weekly Telegram Digest Dispatch (Priority: MEDIUM)
- **Objective**: Automatically send the pre-computed weekly executive summary (`report.md`) to the operator's private Telegram topic.
- **Target Seam**: Telegram Bot API invoked via Hermes CLI or a standalone Python dispatch script.
- **Physical Environment**:
  - Hermes runs inside WSL2 Docker container (`ki-basis-hermes`) OR a lightweight Windows task runner.
- **Acceptance Criteria**:
  - [ ] Operator configures `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `.env`.
  - [ ] Script reads pre-computed `data/exports/snapshots/YYYY-MM-DD/report.md`.
  - [ ] Extracts the **Executive Regime Stance**, **Active Contradictions**, and **Priority Batch 1 Order Tickets**.
  - [ ] Successfully delivers message to Telegram with zero LLM arithmetic.
- **Anti-Drift Guardrail**: The LLM must NEVER calculate position sizes, alter limit prices, or modify portfolio weights.

---

### Step 3: TradingView Alert Webhook Ingress (Priority: MEDIUM)
- **Objective**: Receive real-time TradingView Pine script technical alerts (e.g. 200-day MA crosses, ATR trailing stop touches) and append them as open alerts to the Watch Register.
- **Target Seam**: TradingView Alert Webhook (`POST https://<public-url>/api/v1/tradingview`).
- **Physical Environment**:
  - Requires public HTTPS ingress: either a free **Cloudflare Tunnel** (`cloudflared`) pointing to `127.0.0.1:8080` OR an Activepieces webhook receiver container.
- **Acceptance Criteria**:
  - [ ] Webhook receiver listens on a secured port, verifying a shared secret token in the JSON payload: `{"secret": "...", "ticker": "{{ticker}}", "alert": "STOP_TOUCHED"}`.
  - [ ] Validates payload against `TradingViewAlertPayload` schema.
  - [ ] Appends alert to `data/action_watch_register.json` with status `TRIGGERED`.
- **Anti-Drift Guardrail**: Never configure TradingView to send webhooks to `http://localhost`. TradingView is a cloud SaaS and requires a public HTTPS URL.

---

### Step 4: Phase 3 Indicator Expansion (22 $\to$ 60 Breadth) (Priority: HIGH)
- **Objective**: Expand the macro walking skeleton from 22 active indicators to the target 60-indicator breadth.
- **Target Seam**: Graduate candidate series from `configs/registry_120.yaml` into `configs/registry.yaml`.
- **Key Series to Graduate**:
  - Real Yields: 10Y TIPS (`DFII10`) and 5Y TIPS (`DFII5`).
  - Breakeven Inflation: 10Y Breakeven (`T10YIE`) and 5Y Breakeven (`T5YIE`).
  - Credit Breadth: High-Yield OAS (`BAMLH0A0HYM2`) and Investment-Grade OAS (`BAMLC0A0CM`).
  - Commodities: Copper/Gold ratio (`COPPER_GOLD`) and WTI Term Structure.
  - Liquidity: Fed Net Liquidity index (`FED_NET_LIQ`).
- **Acceptance Criteria**:
  - [ ] Verify live feeds for each series using keyless sources (FRED, DBnomics, US Treasury).
  - [ ] Update `configs/weights.yaml` with calibrated intra-module weights.
  - [ ] Re-run `uv run python -m ipos.cli weekly --as-of <date>` and verify `status=OK` with 60 indicators.
  - [ ] 100% test pass on `uv run pytest`.
- **Anti-Drift Guardrail**: Never enable synthetic data fallbacks (`--seed-offline`) on live production runs.

---

## 3. Operator Instructions for Future AI Sessions

When delegating any of the above steps to a fresh AI session, paste this exact prompt:

```text
You are an independent Quantitative Systems Engineer working in C:\GitDev\Investment.

Before taking any action:
1. Read 06_modular_pipeline_alignment/00_INDEX.md and 06_modular_pipeline_alignment/ROADMAP_FUTURE_STEPS.md.
2. Run the reality verification battery: uv run python 06_modular_pipeline_alignment/audit/verify_reality_battery.py (must report 5 PASSED).
3. Do not invent any fake REST APIs or mock wrappers. Wealthfolio is desktop GUI only; core Python runs on native Windows NTFS (no 9P cross-mounts).
4. Our target for this session is [INSERT STEP 1, 2, 3, OR 4]. Implement the code in ipos/, verify with real tests, and prove that external dependencies actually execute.
```
