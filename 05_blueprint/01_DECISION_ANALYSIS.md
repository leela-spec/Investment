# IPOS Decision Analysis — Risk / Benefit / Cost / Performance / Management (v1.0)

**Date:** 2026-07-19 · **Purpose:** record *what* was chosen, *what the alternatives were*, *why*, and — critically — **the trigger that should make us switch** to an alternative. This file exists so future sessions (human or AI) can revisit any decision without re-deriving it, and can pivot fast when something proves harder than planned.
**Evidence base:** `05_blueprint/research/2026-07-19_*.md` (archived agent reports) + repo analysis in `00_MASTER_PLAN.md` §1.3.

## How to read the tables

- **Benefit** = value toward the IPOS vision (weekly risk budget / stance / contradictions with minimal tokens).
- **Cost** = build effort + recurring cost (money, tokens, human minutes/week).
- **Risk** = what can go wrong with the chosen option.
- **Switch trigger → fallback** = the pre-agreed condition under which we abandon the choice, and for what. *If a trigger fires, don't debate — execute the fallback.*

---

## D1. Build strategy: depth-first walking skeleton (vs. more extraction / breadth-first)

| | Chosen: thin end-to-end pipeline first (~20 indicators) | Alt A: finish 60-indicator registry first | Alt B: continue PDF extraction/refinement |
|---|---|---|---|
| Benefit | Value loop proven in weeks; every later step widens something that already works | Complete data day 1 | More rules |
| Cost | M–L once | Weeks of connector work before any output | Tokens, no runtime value |
| Risk | Skeleton choices might need rework when widening | Motivation/validation starve; unknown integration bugs surface late | Knowledge layer already QA-complete → near-zero marginal value |

**Rationale:** extraction is verified done (204/204 QA); the binding constraint is that *zero code exists*. Past plans failed on execution, not on knowledge.
**Switch trigger:** none — this is sequencing, self-correcting.

## D2. Database: DuckDB (vs. SQLite, chDB, Parquet+Polars-only)

| | DuckDB ✅ | SQLite | Parquet+Polars only | chDB |
|---|---|---|---|---|
| Benefit | OLAP window functions in SQL, single file, Parquet native, recompute-history in seconds | Ubiquity | No DB at all | ClickHouse speed |
| Cost | ~0 (free, in-process) | ~0 | ~0 | ~0 |
| Risk | Single-writer; young-ish ecosystem | Slow/awkward window math | Transforms move into Python code (more code = more bugs) | Niche, less tooling |
| Performance | Overkill-fast at our scale | Adequate | Adequate | Overkill |

**Rationale:** 2026 consensus default for local analytics (research: stack validation §1). Single-writer handled by design (job = sole writer; readers read-only).
**Switch trigger:** DuckDB file corruption twice, or a needed feature missing → **SQLite** (schema is portable ANSI-ish SQL; transforms would move partly to Python).

## D3. Primary UI: static self-contained HTML report (vs. Streamlit server — the one Blueprint change)

| | Static Plotly HTML ✅ | Streamlit (Blueprint's pick) | Quarto dashboard | Evidence.dev / Observable |
|---|---|---|---|---|
| Benefit | Server-less, archivable per week, diffable, e-mailable, opens offline; matches batch cadence | Rich interactivity | Prettier layout, still static | SQL-native BI |
| Cost | M build; 0 recurring | M build + always-on process + rerun model | M + extra toolchain | JS toolchain; vendor risk |
| Risk | Less ad-hoc drill-down | Server down = no UI; single-writer conflicts with DB | Rendering dep | Evidence = seed-stage company |
| Management | History accumulates as files | State lives in a session | — | — |

**Rationale:** resilience + simplicity ranking; "batch emits static artifact" is a recognized 2026 pattern (research: stack §2). Streamlit **not deleted** — demoted to optional Phase-4 on-demand explorer over the same queries.
**Switch trigger:** if during Phase 2–3 we repeatedly *need* interactive filtering to answer weekly questions → build the Streamlit explorer early (it's additive, not a rewrite). If Plotly HTML layout becomes limiting → Quarto (same batch pattern).

## D4. Scheduling: Windows Task Scheduler + idempotent CLI (vs. Prefect/Dagster/NSSM)

**Chosen** for zero infra; validated best practice for one weekly job (research: stack §3). Config: run-when-logged-off + missed-start catch-up; registration scripted (PowerShell).
**Risk:** silent non-execution (machine off, task disabled). **Mitigation:** `ipos-doctor` staleness check + report banner shows data age.
**Switch trigger:** pipeline grows real DAG branches (multiple independent schedules, backfills with dependencies) → **Prefect local**. Not before.

## D5. Data sourcing: FRED backbone + dual-source + archive-everything (vs. paid APIs / single source / OpenBB)

| | Chosen: FRED + Stooq/yfinance + free-key fallbacks + scrapes ✅ | Alt A: paid API (Tiingo paid, EODHD, …) | Alt B: yfinance-only | Alt C: OpenBB wholesale |
|---|---|---|---|---|
| Benefit | $0, redundancy per category, full 60-indicator coverage | Cleaner SLAs | Simplest | Many providers pre-wrapped |
| Cost | ~S per connector (≤60 lines each) | $10–80/month — violates $0 constraint | ~0 | Heavy dep, AGPL, their release cycle |
| Risk | Scrapes fragile; yfinance breakage waves; **FRED OAS history now windowed to 3y (Apr 2026!)** | Money for data we can get free at weekly cadence | Single point of failure, TOS gray | Overkill for 60 weekly series |

**Rationale + hard lesson from research:** free is fully viable *at weekly cadence*; the OAS truncation proves the **archive-everything policy** must be rank-2 priority (raw Parquet, append-only, backfill seeded immediately).
**Switch triggers:** a critical series unavailable free for >4 weeks → single cheapest paid source for that category only. ≥3 scrapes broken simultaneously → evaluate OpenBB as connector layer (not as platform).

## D6. AI layer: deterministic pipeline + LLM as last-mile narrator, $0-first provider ladder (vs. RAG, all-modules prompts, premium models, no AI)

| | Chosen: snapshot-first + ≤9.4k tok/week + ladder (Gemini free → manual paste → cheap API batched → Ollama) ✅ | Alt A: RAG/embeddings | Alt B: feed all modules each run | Alt C: premium model always | Alt D: no LLM at all |
|---|---|---|---|---|---|
| Benefit | Frontier-quality narration possible at ~$0; report works with AI off | "Scales" | No retrieval code | Best prose | Zero cost/risk |
| Cost | S–M build; **$0.00–0.08/month** recurring | Infra + nondeterminism | ~40k+ tok/run (≈4× budget) for no quality gain | ~$0.6–2/month (still cheap, but pointless weekly) | Loses interpretation layer |
| Risk | Free tiers change limits; Gemini free tier may train on prompts | Complexity for 10–20 docs that fit in context anyway | Token waste violates core requirement | Vendor lock reflex | Human does interpretation forever |
| Performance | All numbers pre-computed → small models suffice for narration (research: LLM §3–4) | — | — | — | — |

**Rationale:** research confirmed "code computes, LLM narrates" as recognized best practice; caching irrelevant at weekly cadence — Batch API + structured outputs are the real levers.
**Switch triggers:** narration quality unsatisfying on cheap/free models → one step up the ladder (cents). Gemini free tier terms unacceptable once portfolio data enters snapshots → paid API or Ollama. Provider outage → `provider: none` (deterministic report always renders).

## D7. Toolchain & libraries: uv, pandas-at-edges, pandera, pytest+golden (vs. poetry/pip, polars, Great Expectations)

**Chosen** per 2026 validation (research: stack §4–6). uv = reproducible + no venv fragility under Task Scheduler; pandera light (GE = 100+ deps, rejected); golden snapshots guard tuning drift.
**Switch triggers:** pandera abandons maintenance → Pointblank. Data volume × 100 (won't happen weekly) → polars.

## D8. Plan format itself: file-level meso plans with Definitions of Done (vs. prose plans of the past)

**The user's stated pain:** past plans weren't concrete enough for targeted execution ("nicht ausreichend für eine sehr gezielte Umsetzung").
**Chosen mitigation in this plan generation:** every cluster has (a) options *with verdicts*, (b) numbered file-by-file implementation steps, (c) a testable **Definition of Done**, (d) effort estimate; the master plan has a ranked feature table and phase exit criteria ("no phase without a green weekly run"); `PROJECT_STATE.md` gives any future session a 2-minute onboarding path.
**Residual risk (honest):** a plan is still not code. The two failure modes that remain are (1) starting Phase 1 with scope creep (fix: build ONLY the walking skeleton's ~20 indicators first), (2) session discontinuity (fix: PROJECT_STATE.md must be updated at the end of every working session — that is a **hard rule**, enforced by its own checklist).
**Switch trigger:** if after the first implementation session the meso steps prove too coarse to execute directly → the session's first job becomes writing the missing micro-steps *into* the meso file before coding (plan-repair before code, never silent divergence).

---

## Cost & performance summary (whole system, as planned)

| Dimension | Value |
|---|---|
| Money, recurring | **$0.00–0.08/month** (LLM narration only; $0 paths exist for everything) |
| Money, one-time | $0 (all free tiers/keys) |
| Tokens, recurring | ≤ ~40k/month (AI layer only; everything else is code) |
| Human time, recurring | ~0 min/week ops + reading the report; ~2 min/week if manual-paste AI path chosen |
| Build effort | Phase 0–1 ≈ 3–5 focused days; Phase 2 ≈ ~1 week; Phase 3 spreadable |
| Performance | DuckDB recomputes full 120-indicator multi-year history in seconds; weekly run target < 5 min wall-clock incl. pulls |

## Top-5 risk register (management view)

| # | Risk | Likelihood | Impact | Mitigation (planned) | Trigger → fallback |
|---|---|---|---|---|---|
| 1 | Data-source decay (scrapes, yfinance, FRED windowing) | High (certain over years) | Medium | Dual-source, archive-everything, staleness→confidence, isolated optional scrapes | D5 triggers |
| 2 | Execution stall (plan never becomes code — the historical pattern) | Medium | High | Walking-skeleton-first, DoD per cluster, PROJECT_STATE session protocol | D8 trigger |
| 3 | Silent scoring drift when tuning | Medium | High (destroys year-over-year comparability) | scoring_version + params_json freeze + golden snapshots | Golden diff fails → intentional bump or revert |
| 4 | Regime classifier mis-labels (hardest component) | Medium | Medium (wrong risk_scaler) | Synthetic-path tests, hysteresis, UNCERTAIN-priority defensive default, confidence gate <40 | Persistent mislabels → simplify to MA/ATR-only classifier v0 until tuned |
| 5 | Windows machine off / task rot | Medium | Low-Med | Missed-start catch-up, idempotent runs, doctor staleness alarm, report age banner | Repeated misses → move schedule to a time the machine is reliably on |

---

## Amendment log (plan-repair; newest first)

Per `HANDOVER.md` §5, every divergence from the v1.0 plan is recorded here with its reason before/at the time it lands in code.

### 2026-07-23 — Phase 1 walking skeleton built; free-source policy sharpened; scoring-math fixes

**Context:** first implementation session. Built the full walking skeleton (`ipos/` package, configs, DuckDB warehouse, ETL, transforms, scoring, aggregation, snapshot+report, CLI, tests). Ran in a sandbox with **no network to data hosts and no FRED key**.

1. **Free-data-source policy — refined and made explicit (extends D5, does not change it).**
   IPOS uses **only free, established data sources**; paid APIs / payment models are **out of scope and explicitly deferred to future development**. Within "free" we now distinguish two tiers, because it changes what can be run live with zero setup:
   - **Tier 1 — keyless free** (no account, no key): **Stooq** (equities, FX, gold/copper, market 10y). These run live the moment `stooq.com` is on the environment allowlist — the zero-setup Phase-1 path.
   - **Tier 2 — free-but-registration-keyed:** **FRED** (`FRED_API_KEY`, free account). Remains the designed backbone (rates/curve/credit/liquidity/vol). The key is **operator-provided**; obtaining it is a manual account signup (email verification) that an automated web agent cannot and should not perform — deferred to a human/CLI operator. Until a key exists, FRED series **degrade gracefully** (missing/stale → lower confidence, run continues) and the system stays fully functional on Tier-1 + archive.
   - **Switch trigger unchanged** (D5): a *critical* series unavailable free for >4 weeks → single cheapest paid source for that category only. No paid source enters before that trigger fires.
   *Reason:* the user directed that first stages rely only on free established sources and that anything else is future work; and that account/key creation is a risky outward-facing op to defer. This aligns with the $0 constraint and the fail-degraded principle.

2. **Z-score→0–100 mapping corrected (refines C3 decision 3).** Adopted `score = 50·(tanh(z/k)+1)`, clipped [0,100], inverted for `higher_is_better=false`. The Blueprint's prose `50+50·(z'+1)/2` yields [50,100] and its pseudocode `50+25z` yields [25,75] — neither is centered/range-safe. The adopted form is centered at 50 and range-safe, matching the evident intent. *Reason:* correctness + testability (hand-computed fixtures in `tests/test_scoring.py`).

3. **Feature/scoring math in vectorized pandas, not window-function SQL (refines C3 decision 1 & MASTER_PLAN A6).** `canonical_weekly` stays SQL (DuckDB ASOF join). Rolling percentile-of-current-value-within-its-own-window is awkward in SQL and the data is tiny; pandas rolling is fast, deterministic, and trivially hand-verifiable. *Reason:* simplicity + testable determinism. Revisit if golden-snapshot/perf needs demand SQL in Phase 2/3.

4. **`pandera` deferred to Phase 3 (refines D7).** Phase-1 validation is lightweight pandas (`ipos/etl/validators.py`: shape, dtype, monotonic dates, per-asset-class sanity ranges). *Reason:* pandera earns its dependency weight when many heterogeneous scrape sources arrive (Phase 3), not for the golden-20.

5. **Aggregation consolidated into one module.** C1's `aggregate/{modules,stance,risk_budget}.py` are implemented as one cohesive `ipos/aggregate/modules.py` (module scores + stance vector + risk budget). *Reason:* they share one weighted-blend pass; splitting adds indirection without benefit. Purely structural; no behavioral change.

6. **Deterministic synthetic fixtures for offline runs/tests (`ipos/etl/fixtures.py`).** Clearly labelled NOT real market data; exists only so the pipeline runs and tests pass with no network (the offline-resilience DoD) and so tests make **zero live calls**. Live pulls (Tier-1/Tier-2) archive real data with a later `pull_date`, which the fallback executor prefers automatically. *Reason:* the sandbox has no data-host network; this keeps the DoD demonstrable without fabricating "real" numbers.
