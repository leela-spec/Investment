# IPOS Master Plan — Macro Iteration (v1.0)

**Date:** 2026-07-19
**Status:** Approved planning artifact — supersedes nothing, operationalizes `Automated Investment Playbook.md` (the Blueprint) and the extracted Playbook (`03_extract/`, `04_playbook/`).
**Design goal:** the most modern, most efficient, most resilient, and *simplest* implementation of the IPOS Blueprint — ranked by **impact per token/effort**, free-only, maximum automation.

---

## 1. Meta/Macro analysis — what IPOS is and where the project stands

### 1.1 Vision (from Blueprint + transcript, verified)

IPOS is a **local-first, weekly Investment Process OS** on Windows that:

1. ingests ~60 indicators (scaling to 120 without refactor) across the full A2 macro stack (Equity, Rates, Credit, FX, Commodities + Sentiment/Technical),
2. scores each 0–100 (percentile / z-score / band) with explicit directionality,
3. aggregates into **module scores → stance vector (tilts) → overall risk budget (0–100) → confidence (0–100) → contradictions** (no traffic lights),
4. is governed by regime classification (**CHOPPY / TRENDY / MOMENTUM / UNCERTAIN**) and portfolio governors (drawdown cap, CRV ≥ 1.3, liquidity gates),
5. exports a compact **`snapshot.json`** weekly, and
6. uses an LLM only as a **last-mile narrator**: snapshot + only-relevant Playbook modules in, bounded weekly report out ("snapshot-first", no RAG, no PDF re-feeding).

### 1.2 Locked constraints (non-negotiable)

| ID | Constraint |
|----|-----------|
| A2 | Full macro stack: Equity + Rates + Credit + FX + Commodities |
| B1 | Weekly cadence (`as_of_date` = Friday / last business day; run Sat morning) |
| C2 | Windows, local-first |
| D2→D3 | 60 indicators MVP, scale to 120 **without refactor** (registry-driven) |
| Out | Module scores + risk budget 0–100 + stance vector + confidence + contradictions |
| PB | Playbook is modular & retrieval-based; **never** feed the seminar PDF into runs |
| CP | Composite policy: store external composites (Fear & Greed, Goersch Trend) as single series; never rebuild components |
| $0 | Free data sources and free/near-free AI only; heavy lifting in code, not tokens |

### 1.3 Current state (verified 2026-07-19)

**Done & QA-verified (Workstream B — extraction):**
- 10 Playbook modules (`04_playbook/modules/`), incl. `TRAILING_STOP_POLICIES.md` and `SENTIMENT_POSITIONING.md` (the two items the handover listed as open — both exist now).
- `03_extract/`: 34 indicators, 126 rules, 44 process steps; 204/204 IDs reconciled vs transcript (`logs/QA_REPORT.md`: all green).
- QA tooling exists (`scripts/qa_repo.py`, `qa_chat_vs_repo.py`, `qa_playbook_refs.py`).

**Not started (Workstream A — the Blueprint build):**
- **Zero implementation code.** No `ipos/` scaffold, no registry, no DB, no ETL, no scoring, no snapshot, no report, no scheduling.
- Empty placeholders: `04_playbook/index.json`, `blueprint_map.md`, `snapshot_flags.md`.
- Indicator registry covers ~34 of 60 MVP indicators; **Credit, FX, Commodities are nearly absent**; no per-indicator data-source mapping exists.
- Many extracted items carry `needs_verification: true` (ISM subindices, buyback series, NAAIM cadence, …).

**Conclusion:** the knowledge layer is complete and stable → the highest-impact move is to build the **thin end-to-end pipeline** now, then widen coverage. Depth-first (one working weekly run) beats breadth-first (more extraction).

---

## 2. Design principles (the ranking function)

Every feature is ranked by **Impact ÷ (build effort + recurring token cost)**. Concretely:

1. **Code computes, LLM narrates.** Everything numeric/deterministic runs as Python/SQL at zero marginal cost. The LLM sees only a compact snapshot + selected rules and produces bounded prose. (Validated as recognized best practice: "deterministic pipeline + generative last mile".)
2. **Registry-driven everything.** Adding an indicator = adding a YAML row. No code change from 34 → 60 → 120. The registry is the single source of truth for source, transforms, scoring, directionality, module mapping and `playbook_refs`.
3. **Artifacts over servers.** The weekly run emits *files* (DuckDB tables, `snapshot.json`, static HTML report). Files are archivable, diffable, and need no running process. Interactive UI is optional and on-demand, never load-bearing.
4. **Fail-degraded, never fail-silent.** Missing non-critical series → lower confidence + staleness flag, run continues. Missing critical series → keep last good snapshot, write FAILED-attempt record.
5. **Append-only + versioned.** Raw pulls archived forever (Parquet), scoring params frozen in `params_json`, prompt contracts versioned. Any output is reproducible.
6. **Free-first, dual-source.** Every market-data category has a primary and a fallback source; fragile sources (yfinance, unofficial endpoints) are never single points of failure.
7. **Simplicity budget.** No orchestrator (Prefect/Dagster = overkill for one weekly job), no RAG/embeddings (deterministic `playbook_refs` retrieval), no always-on services, no cloud dependency.

---

## 3. Validated architecture decisions (own analysis × 2026 web best practice)

| # | Decision | Blueprint said | 2026 validation → final call |
|---|----------|----------------|------------------------------|
| A1 | **DuckDB** single-file warehouse | DuckDB | ✅ Confirmed (v1.5.x stable, consensus "SQLite of OLAP"). Caveat adopted: DuckDB is single-writer → weekly job is the only writer; report/dashboard opens **read-only**. |
| A2 | **uv** (Astral) for env + deps | (not specified) | ✅ Adopted. 2026 default Python toolchain; Task Scheduler invokes `uv run ipos-weekly` — no venv activation fragility, `uv.lock` = reproducibility. |
| A3 | **Static HTML report** as primary UI | Streamlit multipage | 🔄 **Changed.** Weekly batch → server-less static artifact (self-contained Plotly HTML per week) is more resilient, archivable, and simpler. Streamlit stays as *optional on-demand* explorer (Phase 4), not as the deliverable. |
| A4 | Plain script + **Windows Task Scheduler** | Task Scheduler | ✅ Confirmed best practice for single-user weekly jobs. Config: "run whether user is logged on or not" + "run as soon as possible after a missed start" (laptop-off case). Registration itself scripted (PowerShell). |
| A5 | **pandera** validation, **pytest** + golden snapshots | pandera/GE | ✅ pandera confirmed (light, pandas+polars, schema-as-code fits pytest). Great Expectations rejected (100+ deps). |
| A6 | **pandas** at edges, **SQL in DuckDB** for transforms | pandas/polars | ✅ pandas (tiny data; SQL does the heavy lifting anyway). |
| A7 | **FRED backbone + dual-source market data** | FRED/manual | ✅ FRED (free key, ~120 req/min) + Stooq (no key) as yfinance fallback + Tiingo/Alpha Vantage free keys as tertiary. ⚠️ New 2026 fact: FRED truncated ICE BofA OAS series to a rolling 3-year window (Apr 2026) → **archive-everything policy is mandatory from day 1**. |
| A8 | LLM = last-mile narrator, snapshot-first, no RAG | same | ✅ Confirmed recognized pattern. Cost reality: ~8k in + 2k out per week ≈ **2–8 ¢/month** on cheap APIs, **$0** on Gemini free tier / local Ollama model / manual paste into a Claude Project. Levers that matter at weekly cadence: **Batch API (−50%) + structured outputs**, *not* prompt caching (TTL expires between weekly runs; keep cache-correct prompt hygiene anyway). |
| A9 | No orchestrator, no embeddings, no service | (implied) | ✅ Confirmed by 2026 comparisons (Dagster/Prefect overkill single-machine; RAG pointless at 60 indicators — everything fits in context). |
| A10 | OpenBB Platform | (not mentioned) | 📌 Not adopted wholesale (AGPL, heavy), but its **provider-registry pattern** validates our registry design; usable later as an extra connector if a source dies. |

---

## 4. Macro clusters (the decomposition)

The system decomposes into **9 clusters**. Each has a meso plan in `05_blueprint/meso/`.

| Cluster | Name | What it owns | Meso plan |
|---------|------|--------------|-----------|
| C1 | Registry & Warehouse | `registry.yaml` (60-indicator definitions incl. source mapping), DuckDB schema, migrations | `meso/C1_registry_warehouse.md` |
| C2 | Ingestion & Connectors | FRED/Stooq/yfinance/Tiingo/scrape connectors, fallback chains, raw archiving, validation | `meso/C2_ingestion_connectors.md` |
| C3 | Transform & Scoring | Weekly canonicalization, features (deltas/z/percentile), scoring 0–100, confidence | `meso/C3_transform_scoring.md` |
| C4 | Regime & Aggregation | MARKET_CONDITIONS classifier, module scores, stance vector, risk budget, contradictions | `meso/C4_regime_aggregation.md` |
| C5 | Playbook Integration | `index.json`, `playbook_refs`, `snapshot_flags`, deterministic retrieval | `meso/C5_playbook_integration.md` |
| C6 | Snapshot & AI Layer | `snapshot.json` schema + token design, prompt contracts, $0 LLM options | `meso/C6_snapshot_ai_layer.md` |
| C7 | Reporting & Visualization | Static weekly HTML report (risk budget, heatmap, regime trail, movers), report.md | `meso/C7_reporting_visualization.md` |
| C8 | Automation & Operations | Task Scheduler setup script, run contract, logging, fail-safe, health checks | `meso/C8_automation_operations.md` |
| C9 | QA, Testing & Governance | pytest suites, golden snapshots, versioning, 60→120 expansion protocol | `meso/C9_qa_governance.md` |

**Dependency spine:** C1 → C2 → C3 → C4 → C6 → C7, with C5 feeding C6, and C8/C9 wrapping everything. This ordering is also the build order.

---

## 5. Feature ranking — impact per token/effort

Effort in ~focused build sessions (S=½ day, M=1–2 days, L=3–5 days). Recurring token cost is ~0 for everything except the weekly LLM narration (~10k tokens/week total).

| Rank | Feature | Impact | Effort | Why this rank |
|------|---------|--------|--------|---------------|
| 1 | Walking skeleton: registry (≈20 core indicators) → FRED/Stooq pull → weekly canonical → percentile/band scores → module agg → `snapshot.json` | ★★★★★ | M | Delivers the *entire value loop* end-to-end at minimum width; everything after is widening/hardening. FRED-heavy core = most reliable data first. |
| 2 | Raw-archive policy (Parquet, append-only) | ★★★★★ | S | Irreversible-loss prevention (FRED OAS 3-yr truncation). Cheapest insurance in the whole plan. |
| 3 | Contradictions engine + top movers (config-driven predicates) | ★★★★★ | S | The Blueprint's core differentiator vs traffic lights; trivially cheap once scores exist. |
| 4 | Static HTML weekly report + report.md template (no LLM needed to be useful) | ★★★★☆ | M | The user-facing artifact; works even when every AI option is down → resilience. |
| 5 | Task Scheduler automation + fail-safe run contract | ★★★★☆ | S | Turns the system from "tool" into "OS"; scripted, idempotent, catch-up on missed runs. |
| 6 | LLM narration layer ($0 default, structured outputs, versioned prompts) | ★★★★☆ | S–M | High perceived value, near-zero cost; strictly optional at runtime (report works without it). |
| 7 | Confidence scoring + staleness/data-quality flags | ★★★★☆ | M | Makes outputs trustworthy; feeds fail-degraded behavior. |
| 8 | Regime classifier (CHOPPY/TRENDY/MOMENTUM governor + risk_scaler) | ★★★★☆ | M–L | Central Playbook governor; needs OHLC swing/ATR features — worth full session, after skeleton. |
| 9 | Indicator expansion 34→60 (Credit/FX/Commodities + sentiment scrapes) | ★★★☆☆ | M (spread) | Pure registry+connector work; value grows linearly, so it comes after the loop exists. |
| 10 | Golden-snapshot regression tests + scoring monotonicity tests | ★★★☆☆ | M | Protects against silent drift when tuning weights/bands. |
| 11 | Vintage/revision handling for macro series | ★★☆☆☆ | M | Correctness nicety; percentile windows tolerate revisions early on. Defer to Phase 3. |
| 12 | Streamlit on-demand explorer | ★★☆☆☆ | M | Nice for drill-down; static report covers 90% of weekly need. Phase 4. |
| 13 | COT family, ISM subindices, buybacks, 120-indicator scale-out | ★★☆☆☆ | L | Explicitly deferred in extraction (`needs_verification`/`defer`); registry makes it cheap later. |

**Explicit non-goals (dropped for now):** RAG/embeddings, always-on services, cloud deploys, backtesting engine, broker integration, rebuilding composites, stock-screening layer (Finviz template stays deferred reference).

---

## 6. Phased roadmap (macro)

Each phase ends with a runnable, verified state ("no phase without a green weekly run").

### Phase 0 — Scaffold (effort ~S)
`ipos/` package scaffold per Blueprint folder layout; `uv init` + `uv.lock`; `pyproject.toml` with entry point `ipos-weekly`; config loading (pydantic); logging setup; pytest wired; `.env` for API keys (FRED, Tiingo — both free).

### Phase 1 — Walking skeleton, "golden ~20" (effort ~M–L)
Registry v1 with ~20 highest-reliability indicators (FRED: T10Y2Y, T10Y3M, HY & IG OAS, NFCI, VIXCLS, WALCL, DTWEXBGS, WTI, UMich, …; Stooq/yfinance: SPX + sector/benchmark set; scrapes deferred). DuckDB schema (Blueprint DDL). FRED + Stooq + manual-CSV connectors with fallback chain + raw Parquet archive. Weekly canonicalization SQL. Percentile + band scoring with directionality. Module aggregation + stance vector + risk budget. `snapshot.json` v1. Deterministic `report.md`. **Exit test:** one command produces a correct snapshot for the current week, twice (idempotent).

### Phase 2 — Core value (effort ~L)
Z-score scoring + tanh damping; confidence composite (quality/stability/coherence); contradictions engine (YAML predicates) + top movers + key drivers; regime classifier from MARKET_CONDITIONS module (features: overlap_index, retracement_ratio, ATR accel, swing structure) + `risk_scaler` applied to risk budget; static HTML report (risk budget + confidence, module bars, 52-week score heatmap, regime map with 26-week trail, indicator sparklines); Playbook retrieval (C5) + LLM narration with structured output ($0 default); Task Scheduler registration script.

### Phase 3 — Coverage & hardening (effort ~L, spreadable)
Registry expansion to 60 (Credit/FX/Commodities completion; CBOE put/call, AAII headline, NAAIM, CNN F&G, ISM headline via DBnomics — each scrape ≤ ~30 lines with cache + graceful failure); pandera schemas per source; golden-snapshot + monotonicity + integrity test suites; vintage/revision support; `scoring_version` governance; health-check command (`ipos-doctor`: source freshness, DB integrity, task status).

### Phase 4 — Optional & scale (defer freely)
Streamlit on-demand explorer; COT/ISM-subindex/buyback families toward 120; portfolio/exposure module (manual CSV first, per transcript guidance); local-LLM (Ollama) offline narration variant.

---

## 7. Token design of the AI layer (summary; detail in C6)

Weekly run budget (hard caps, enforced in code):

| Block | Budget | Content |
|-------|--------|---------|
| System+role prompt (frozen, versioned) | ≤ 600 tok | Contract, output schema, style, guardrails |
| Playbook excerpt (deterministic retrieval) | ≤ 3,000 tok | Only modules referenced by movers/extremes/contradictions |
| `snapshot.json` (minified) | ≤ 4,000 tok | Overall + modules + contradictions + movers + only *surfaced* indicators (not all 60) |
| Output (structured) | ≤ 1,800 tok | Fixed sections, bullet caps |
| **Total** | **≤ ~9,400 tok/week** | ≈ **$0.00–0.08/month** depending on provider |

Provider ladder (all acceptable, pick per week): ① Gemini free tier (0 €), ② manual paste into Claude/ChatGPT subscription (0 € marginal, frontier quality), ③ cheap API w/ Batch −50% (cents), ④ local Ollama Qwen-class model (0 €, offline). The report renders fully without any LLM (rank-4 resilience property).

---

## 8. Risks & mitigations (macro)

| Risk | Mitigation |
|------|------------|
| yfinance breakage waves (structural, recurring) | Dual-source per category (Stooq primary-fallback), cached last pull, staleness→confidence hit, never sole source |
| FRED OAS 3-yr history window | Day-1 raw archiving; seed backfill now while data exists |
| Unofficial endpoints die (CNN F&G, CBOE page) | Accumulate own history weekly; each scrape isolated + optional; missing → deferred flag, not failure |
| Scope creep (120 indicators, screener, backtests) | ROI gate stays: registry rows only after the loop is green; deferred list is a feature, not a debt |
| Silent scoring drift when tuning | `scoring_version` + `params_json` freeze + golden snapshots (C9) |
| Windows machine off on Saturday | Task Scheduler missed-start catch-up + idempotent runs + `ipos-doctor` staleness alarm |
| DuckDB single-writer conflicts | Only the weekly job writes; report reads read-only; UI reads Parquet marts |

---

## 9. Immediate next actions

1. Review this master plan + meso plans (this commit).
2. Execute Phase 0 + Phase 1 (walking skeleton) — the meso plans C1–C3 contain the exact file-by-file steps.
3. Seed the raw archive immediately (FRED OAS history before further truncation).

*Meso iteration: see `05_blueprint/meso/C1…C9`. Each meso plan: options considered → decision + rationale → implementation steps → definition of done → effort/token cost.*
