# PROJECT_STATE — IPOS (Investment Process OS)

> **READ THIS FIRST** (a brand-new AI agent should read [`HANDOVER.md`](HANDOVER.md) first, then this).
> This file is the single entry point for any new session (human or AI).
> It answers: What is this? Where are we? Which plan is active? What happens next? Where is everything?
> **Hard rule:** update this file at the end of every working session (checklist at the bottom). It supersedes `For next chat.md` (old handover, kept for history).

**Last updated:** 2026-07-27 · **Updated by:** implementation session (Portfolio vs. Stance module built) · **Branch of record:** `main` (direct commits only — no long-lived work branches; see §4 below)

---

## 1. What is IPOS? (30 seconds)

A **local-first, weekly Investment Process OS** on Windows: ~60 free-source indicators (→120 later) across Equity/Rates/Credit/FX/Commodities are pulled, scored 0–100, and aggregated into **risk budget (0–100) + stance vector + confidence + contradictions**, governed by a regime classifier (CHOPPY/TRENDY/MOMENTUM). Output: a compact `snapshot.json` + static HTML report; an LLM only *narrates* the pre-computed numbers (≤ ~9.4k tokens/week, ≈ $0). Knowledge base: rules extracted from a 231-page seminar PDF into modular Playbook files (never re-fed into runs).

## 2. Where are we? (status)

| Workstream | Status |
|---|---|
| **B — Knowledge extraction** (PDF → modules + JSONL) | ✅ **DONE & QA-verified** (204/204 IDs reconciled; 10 modules; 34 indicators, 126 rules, 44 process steps; `scripts/qa_repo.py` green) |
| **A — Implementation planning** | ✅ **DONE**: macro master plan + 9 meso plans + decision analysis + research archive |
| **A — Phase 0 (scaffold) + Phase 1 (walking skeleton)** | ✅ **DONE** (2026-07-23): `ipos/` package, configs (golden-20), DuckDB warehouse, ETL (FRED/Stooq/manual_csv + archive + fallback), transforms+scoring, aggregation, `snapshot.json`+`report.md`, CLI, 29 tests green in ~18s. |
| **A — Phase 2 (core value)** | ✅ **DONE** — contradictions engine, golden-snapshot harness, regime classifier + risk_scaler + policy selectors, static self-contained HTML report, LLM narration scaffolding ($0 `none`/`manual`). |
| **A — Phase 3 (de-risk + dashboard + calendar)** | 🚧 **MOSTLY DONE** — ✅ keyless sources (DBnomics/US Treasury) so live runs need no FRED key; fallback chains; no single-sourced critical series. ✅ synthetic-leak closed (synthetic data can't be served as real — **two more instances of this exact leak found & fixed 2026-07-26, see §3 item 7**). ✅ real-ATR regime from OHLC. ✅ confidence/rates/scoring cleanups. ✅ richer dashboard (regime 2D trail, sparklines, 52w heatmap — still self-contained). ✅ free economic calendar. ✅ widened to **22 indicators** (no single-member modules). ✅ manual ($0) LLM narration wired end-to-end (`provider: file`), with markdown rendering fixed. ✅ hover-explanation glossary for every indicator/module/stance-dim/regime label (CSS-only popovers, `configs/glossary.yaml`). ✅ **`FRED_API_KEY` set (operator's own free key, in gitignored `.env`) + Yahoo Finance fallback added — first real (non-synthetic) live snapshot produced 2026-07-26.** ⬜ Windows Task Scheduler, ⬜ full 60-indicator breadth + fragile scrapes. |
| **A — Portfolio vs. Stance module** (Phase-4 item, pulled forward) | ✅ **DONE (2026-07-27)** — `ipos/etl/portfolio_csv.py` + `ipos/aggregate/portfolio.py`, optional `portfolio` block in `snapshot.json`, matching sections in the HTML + markdown reports. Drop a CSV in `data/inbox/portfolio*.csv` → per-module weight vs. this week's tilt, plain-language read, unmapped-instrument flagging. Zero impact when no file is present (fail-degraded). Full design + post-build notes + 6 ranked follow-ups: `05_blueprint/03_PORTFOLIO_MODULE.md` §8. **94 tests green** (18 new). |

**Active plan:** `05_blueprint/00_MASTER_PLAN.md` (v1.0, 2026-07-19) — 5 phases, ranked by impact per token/effort.
**Current phase:** **Phase 2 (core value) — mostly complete**. Skeleton + contradictions + regime governor + static HTML report + AI scaffolding all done and testable end-to-end offline; live data now flowing for real. Remaining Phase 2 item: Windows Task Scheduler; then Phase 3 (widen to 60 indicators).

**Data-source policy (locked 2026-07-23, extended 2026-07-26):** free, established sources only; paid = future. **Tier 1 keyless** (Stooq, and now Yahoo Finance as its second leg) runs live with zero setup; **Tier 2 free-with-key** (FRED, `FRED_API_KEY`) is operator-provided — **now set** — and degrades gracefully when absent. Full rationale: `01_DECISION_ANALYSIS.md` amendment log.

**How to run:**
- Offline demo/tests (no network, no key): `uv sync --extra dev`; `uv run pytest -q`; `uv run ipos-init`; `uv run ipos-weekly --as-of 2026-07-17 --seed-offline` → `data/exports/snapshots/2026-07-17/{snapshot.json,report.md}`.
- Live: `FRED_API_KEY` is already in the gitignored `.env` (loaded automatically by `ipos-*` CLI commands) → just `uv run ipos-weekly`. This machine also needed `SSL_CERT_FILE`/`REQUESTS_CA_BUNDLE` pointed at Avast's CA bundle for `uv`/`requests` to work at all (local antivirus TLS interception, unrelated to the project).
- Backfill max OAS history early (needs network + FRED key, now available): `uv run ipos-backfill`.
- Portfolio vs. Stance section (optional): drop a broker export as `data/inbox/portfolio*.csv` (columns `instrument,quantity,value_eur` — or `price`/`price_eur` instead of `value_eur`), map instruments to modules in `configs/portfolio_mapping.yaml`, then run `ipos-weekly` as usual. No file → section is simply omitted. Not yet verified against a real Smartbroker/finanzen.net zero export — see `05_blueprint/03_PORTFOLIO_MODULE.md` §8 item 1.

## 3. What happens next? (in order — do not reorder without recording why)

> **Concrete build spec for steps 1–3 below:** [`05_blueprint/02_PHASE1_WORKPLAN.md`](05_blueprint/02_PHASE1_WORKPLAN.md) — exact scaffold, the golden-20 indicator list with source tickers, file-creation order, and Definition of Done.

1. ✅ **Phase 0 (DONE):** `ipos/` package scaffold, uv toolchain, pydantic config loading, pytest wiring → `C1` steps 1–2.
2. ✅ **Phase 1 (DONE):** registry (golden-20) → DuckDB init → pull (FRED/Stooq/manual_csv + archive + fallback) → weekly canonical → percentile/band/zscore scores + confidence → module aggregation + stance + risk budget → `snapshot.json`/`snapshot.min.json` → deterministic `report.md`; idempotent (byte-identical), degrades offline, 29 tests green → `C1`–`C3`, `C6` (partial), `C8` (CLI+fail-safe).
   - ⏳ **Operator action (deferred, not blocking):** run `scripts/backfill_seed.py` (`uv run ipos-backfill`) on a networked machine **with a FRED key** to archive max ICE BofA OAS history before further 3-year-window truncation. Cannot run in a keyless/offline sandbox — the script reports unreachable series and does not fabricate data.
3. **→ Phase 2 (core value) — IN PROGRESS:**
   - ✅ **Contradictions engine** (`configs/contradictions.yaml` + `ipos/aggregate/contradictions.py`): safe AST predicate evaluator (no `eval`), 9 seed predicates over golden-20 modules, writes `log_contradiction`, surfaced in snapshot + report.
   - ✅ **Golden-snapshot regression harness** (`ipos/golden.py`, `scripts/update_golden.py`, `tests/test_golden.py`, `tests/golden/`): byte-exact guard against silent scoring drift; intentional updates via `update_golden.py` + `scoring_version` bump.
   - ✅ **Regime classifier** (`ipos/aggregate/regime.py`, migration `002`): close-only MVP of MARKET_CONDITIONS (CHOPPY/TRENDY/MOMENTUM/UNCERTAIN) + confidence + hysteresis + `risk_scaler` (scales risk budget) + policy selectors; in snapshot + report.
   - ✅ **Static HTML report** (`ipos/report/`): self-contained (inline CSS/SVG, no CDN), gauges + stance bars + contradiction cards + module/indicator tables + 26-week score heatmap; `report.html` per week + stable `latest.html`.
   - ✅ **LLM narration scaffolding** (`ipos/ai/`, `prompts/`, `configs/ai.yaml`): provider interface + `none`/`manual` ($0), deterministic playbook retrieval (no RAG), token-budgeted `prompt_bundle.md` for manual paste; report appends an Interpretation section when a live provider is configured.
   - ⬜ **Remaining Phase 2 (need external setup):** a live LLM provider (key + network; or use the manual bundle at $0); Windows Task Scheduler registration script (Windows-only).
   - ⬜ **Then Phase 3:** widen to 60 indicators (Tier-1 keyless first), pandera, scrapes, vintage handling → `C2`, `C9`.
4. **Phase 3:** expand to 60 indicators (Tier-1 keyless first, then FRED), scrapes, pandera schemas, golden-snapshot tests, hardening → `C2`, `C9`.
5. **Phase 4 (optional):** Streamlit explorer, COT/ISM subindices, 120 indicators.
6. **Unscoped possible future phase — not part of this roadmap:** a multi-analyst/cloud-hosted agent-governance layer (Slack review channels, scheduled extraction/reconciliation automations, tool allow/deny matrix) exists as an unreconciled 2026-04-15 draft — `docs/ipos-notes/` — that conflicts with locked decisions D4/D6 (local-first, single-operator, no orchestrator). See `01_DECISION_ANALYSIS.md` amendment 2026-07-26 before touching it.
7. **✅ Live data fixed 2026-07-26** — root cause + fix in `01_DECISION_ANALYSIS.md` amendment 2026-07-26 (live-data audit + Yahoo fallback). Operator obtained a free `FRED_API_KEY` (in `.env`, gitignored) → 15/22 series live direct from FRED. Added `ipos/etl/yahoo.py` (free public chart endpoint) as a second leg for the 7 Stooq-only series with zero prior fallback (`SPX`, `NDX`, `RUT`, `DAX`, `GOLD`, `COPPER`, `EURUSD`, `US10Y_STOOQ`) → **first-ever real (non-synthetic) snapshot produced, `data/exports/snapshots/2026-07-24/`, status OK, 22/22 real.**
   Getting real data flowing surfaced **two real synthetic-served-as-real bugs**, both fixed with regression tests (see amendment): (a) the canonical ASOF join's same-date tie-break preferred `synthetic@...` vintage strings over real ones; (b) `snapshot.py`'s `synthetic_data` flag used `as_of_date <= ?` so one past demo week tainted every later real week forever. Real runs now exclude synthetic-vintage rows from the canonical join entirely (`build_canonical(..., synthetic=seed_offline)`).
   Remaining, lower priority: `ipos-doctor` per-source live health check; retry/backoff + an explicit "last successful live pull" timestamp separate from `as_of`.
8. **UX/explainability improvement plan (2026-07-26), ranked, only item 1 built so far:**
   1. ✅ **Done** — hover-explanation glossary (indicators/modules/stance-vector/regime), CSS-only popovers, `configs/glossary.yaml` + `ipos/report/glossary.py`.
   2. ⬜ Progressive-disclosure layout pass (F/Z-scan ordering, grouped modules, 1-line plain-language section captions) — research basis: contemporary fintech-dashboard UX guidance favors summary-first/detail-on-demand and jargon replaced by tooltips/glossary links, which item 1 already covers most of.
   3. ⬜ General polish pass once the above and the live-data fixes land.
9. **✅ Portfolio vs. Stance module — built 2026-07-27, 5/7 follow-ups closed same day.** Full design + post-build notes: [`05_blueprint/03_PORTFOLIO_MODULE.md`](05_blueprint/03_PORTFOLIO_MODULE.md) §8. Compares actual holdings (CSV drop-in from Smartbroker/finanzen.net zero, auto-ingested on next run — no live broker API is free for either, researched 2026-07-26) against the weekly suggested stance vector; degrades to fully omitted with no CSV present. Ranked follow-ups, highest first:
   1. ✅ **Done** — verified against a real finanzen.net Zero export same day: it was semicolon-delimited, German column names/number format, matching none of the invented schema. Parser rewritten (delimiter sniffing + file-level locale decision, not per-column — see §8 note 1 for why per-column detection would have silently misparsed thousands-only values like `"8.849"`); all 5 real positions verified to parse exactly right.
   2. ✅ **Done** — weight/tilt mismatches now feed the contradictions engine (`fact_portfolio_weight` table + 8 new `PORTFOLIO_*_MISMATCH` rules), not just a buried table row.
   3. ✅ **Done** — non-EUR positions convert via the existing live `EURUSD` series (`convert_to_eur`), warn-and-skip on an unsupported currency.
   4. ✅ **Done** — the portfolio build is now its own logged `run_log` stage, like every other pipeline stage.
   5. ✅ **Done** — a stale/aging portfolio CSV (file mtime vs. `as_of`, 14-day allowance) now shows the same `.banner.warn` used elsewhere.
   6. ⬜ A single aggregate portfolio-level read (portfolio-weighted tilt vs. `risk_budget`), not just per-module rows — deferred, needs a weighting-formula decision.
   7. ⬜ Weight-history sparkline — cosmetic, Phase-4-optional.
   8. ⬜ *(new)* Populate real ISIN→module mappings in `configs/portfolio_mapping.yaml` (ships empty) — an operator judgment call, not something to invent silently.
   9. ⬜ *(new)* Smartbroker PDF ingestion — that broker has no CSV export path, only a gated paid API; PDF table extraction is a separate, larger feature.

Details, file-by-file steps and **Definition of Done per cluster**: `05_blueprint/meso/C1…C9`.

## 4. Key decisions & why (1-line each; full analysis with alternatives + switch triggers → `05_blueprint/01_DECISION_ANALYSIS.md`)

- **Depth-first walking skeleton** before indicator breadth (extraction is done; code is the constraint).
- **DuckDB** single-file warehouse; weekly job = sole writer, readers read-only (D2).
- **Static self-contained HTML report** is the primary UI; Streamlit demoted to optional explorer — *the one deliberate change vs. the original Blueprint* (D3).
- **Plain CLI + Windows Task Scheduler**, no orchestrator (D4).
- **$0 data**: FRED backbone + Stooq/yfinance dual-source + free-key fallbacks + isolated scrapes; **archive-everything from day 1** (D5).
- **LLM = last-mile narrator**, snapshot-first, no RAG; provider ladder Gemini-free → manual paste → cheap API batched → Ollama; system fully functional with AI off (D6).
- **uv + pandas-at-edges + pandera + pytest/golden snapshots** (D7).
- **Every threshold/config row keeps `extract_ref` provenance** back to `03_extract/*.jsonl` (auditability to PDF page level).

## 5. File map (where everything lives)

| Path | What it is |
|---|---|
| `HANDOVER.md` | **First read for a brand-new AI agent** — entry contract, rules of engagement, how to disagree with the plan |
| `PROJECT_STATE.md` | **This file — the index. Start here.** |
| `05_blueprint/00_MASTER_PLAN.md` | Macro plan: vision, constraints, principles, validated architecture, feature ranking, 5 phases, risks |
| `05_blueprint/01_DECISION_ANALYSIS.md` | Risk/benefit/cost/performance per decision, **alternatives + switch triggers**, risk register |
| `05_blueprint/02_PHASE1_WORKPLAN.md` | Concrete next-build spec: scaffold, golden-20 indicators + tickers, build order, Definition of Done |
| `05_blueprint/03_PORTFOLIO_MODULE.md` | **Planned, not built.** Portfolio-vs-stance module design: CSV drop-in schema, Smartbroker/finanzen.net zero automation-feasibility research, Definition of Done |
| `05_blueprint/meso/C1…C9_*.md` | Per-cluster implementation plans (options → decision → steps → Definition of Done) |
| `05_blueprint/research/2026-07-19_*.md` | Archived evidence: transcript digest, free data sources, stack validation, LLM token patterns |
| `Automated Investment Playbook.md` | The original full Blueprint (deliverables 1–9: stack, schema DDL, scoring math, prompts, mock MVP) |
| `04_playbook/modules/*.md` (10 files) | Playbook knowledge modules (regime, stops, sentiment, technicals, governors) — runtime retrieval targets |
| `03_extract/*.jsonl` | Structured extraction (34 indicators / 126 rules / 44 process) — **upstream knowledge, runtime never reads it directly; configs are seeded from it with provenance** |
| `00_runbook/extraction_process.md` | Extraction runbook (workstream B — done; reuse only if new source PDFs arrive) |
| `scripts/qa_*.py` | Repo QA (all green as of 2026-07-19); extend per meso plan C9 |
| `logs/` | Extraction QA report + transcript copy |
| `For next chat.md` | **Superseded** old handover (2026-02-14) — historical context only |
| `docs/ipos-notes/*.md` | **Unreconciled 2026-04-15 draft** — a multi-analyst/cloud agent-governance framework that conflicts with D4/D6 (local-first, single-operator). Not part of the current roadmap; see `01_DECISION_ANALYSIS.md` amendment 2026-07-26 before adopting anything from it. |
| `Everything from this chat.md` | Extraction transcript (source of truth for extraction; not the blueprint chat) |
| `ipos/` | **Implementation package**: `config/` (pydantic + loader), `warehouse/` (DuckDB DDL + migrations + db), `etl/` (connectors + archive + fallback + fixtures + `portfolio_csv.py`), `transforms/` (canonical SQL + scoring), `aggregate/` (modules/stance/risk-budget + `regime.py` + `contradictions.py` + `portfolio.py`), `export/` (snapshot + md report), `report/` (self-contained HTML), `ai/` (provider + playbook retrieval + prompt bundle), `run.py` (stage runner + fail-safe), `cli.py`, `backfill.py`, `golden.py` |
| `configs/` | `registry.yaml` (golden-20), `modules.yaml`, `weights.yaml`, `scoring_defaults.yaml`, `contradictions.yaml`, `ai.yaml`, `glossary.yaml`, `portfolio_mapping.yaml` (optional, operator-maintained) — single source of truth, validated at load |
| `prompts/` | `weekly_checkup.md` — frozen, versioned LLM system contract |
| `tests/` | pytest suites (config, warehouse, etl, scoring, snapshot, fail-safe, contradictions, golden, regime, report-html, ai, portfolio, canonical, calendar, connectors, ohlc-regime) — **94 tests**, no live calls, green; `tests/golden/` holds the regression snapshot |
| `data/` | gitignored runtime: `warehouse.duckdb`, `archive/` (append-only Parquet), `inbox/`, `exports/snapshots/<friday>/` |
| `pyproject.toml` / `uv.lock` | uv toolchain + entry points (`ipos-init/pull/score/weekly/doctor/backfill`) |

## 6. Session protocol (how any future chat resumes work)

**Kickoff (2 minutes):** read this file → read the meso plan(s) for the current phase → run `python scripts/qa_repo.py` → start at the first unchecked step in §3.
**Working rules:** follow meso steps; if a step is too coarse, refine it *in the meso file first*, then code (plan-repair before code). Free-only, token-frugal, everything scripted/testable. Commit small, push to a feature branch, merge to `main` when the phase's Definition of Done is demonstrably met.
**Before ending every session (checklist):**
- [ ] `PROJECT_STATE.md`: update "Last updated", §2 status, §3 next steps (check off / reorder with reason)
- [ ] New decisions? → add to `01_DECISION_ANALYSIS.md` (incl. alternatives + switch trigger)
- [ ] New evidence/research? → archive under `05_blueprint/research/YYYY-MM-DD_*.md`
- [ ] QA scripts green, work committed & pushed

## 7. Honesty note on continuity (2026-07-19)

This plan generation ran in an ephemeral cloud container. Everything load-bearing was written to the repo: plans, decision analysis with alternatives, and the four research reports (archived verbatim from the analysis agents). What is *not* preserved: the agents' raw intermediate browsing transcripts — only their final findings (with source URLs) survive, which is sufficient to re-verify any claim. If a future session doubts a finding, re-run the research; the questions asked are documented at the top of each research file.
