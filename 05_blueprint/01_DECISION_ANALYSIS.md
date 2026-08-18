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

### 2026-07-29 — Visualization audit: the gap was rendering, not chart types. Tier 0+1 built; self-scoring spec'd, not built

Operator asked, before continuing the roadmap, for research into the highest-impact
visualizations for a financial report/status/decision framework, a check for gaps, and a
ranking by build cost, maintenance, copycat-ability, free access, value, **evidence** of
that value, and risk. Full audit with sources archived at
`05_blueprint/research/2026-07-29_dashboard_visualization_audit.md`.

**The finding was not "add more chart types."** The visual vocabulary was already ahead of
most of what the research turned up — two of the research's own recommendations (Few's
bullet-graph-over-circular-gauge, Tufte's sparklines-in-tables) were already satisfied.
The gap was that **the pipeline computed and stored numbers that no renderer drew**:

- `fact_feature.pctile_156w` / `z_104w` — computed since Phase 1 at `transforms/run.py:154`,
  never exported to the snapshot at all, so where a reading sat in its own history was
  invisible. This is the backbone of the most-copied institutional chart form
  (JP Morgan's *Guide to the Markets* valuation pages).
- `agg_regime.risk_budget_0_100` / `confidence_0_100` history — stored per week, but
  `_regime_history` only ever selected label/confidence/scaler, so **the two headline KPIs
  had no history anywhere in the report.**
- `agg_regime.params_json` — already carried `base_risk_budget` and the classifier's
  `regime_features`, so "why is this week UNCERTAIN, and how much did the scaler cut?" was
  fully computed and wholly unanswerable from the report. Every institutional composite
  publishes its decomposition (the OFR Financial Stress Index is the reference).
- `portfolio.fx_warnings` — written at `run.py:164`, rendered by nothing, so an
  unconvertible currency was **silently dropped from every module weight**. A correctness
  bug, not a cosmetic gap, and the fourth instance of this project's recurring
  "computed-but-not-surfaced" failure mode.
- `data_quality.stale_series` / `missing_series` names, `flags.n_high_severity`,
  `indicators[].delta_4w/12w`, `playbook_selection`, `interpretation_meta.model` — all
  exported, none rendered in the HTML (some were in the markdown, making the *dashboard*
  strictly less useful than its chart-free twin for the question you ask when a run
  degrades).
- Scale: `fact_score` holds ~3,847 weeks; the report charted 52. ~98% of scored history
  was never plotted.

**Decisions taken:**

20. **Tier 0 + Tier 1 built** (operator-selected scope): level-percentile strips, headline
    KPI history, a base → ×scaler → headline bridge with the classifier's measurements, a
    "what changed this week" panel above the fold, a breadth/diffusion index, per-module
    contribution bars, contradiction recurrence counts, and the parity/correctness fixes
    above. No new data source, no new table, **no `scoring_version` bump** — verified with a
    structural golden diff showing 84 added paths, 1 deliberate removal, and **0 changed
    figures**, which is exactly the C9 condition for regenerating the golden without a bump.
21. **`overall.risk_scaler` removed** as a dead duplicate; both renderers already read
    `regime.risk_scaler`.
22. **Contribution decomposition uses zero-anchored diverging bars, NOT a cumulative
    waterfall.** A waterfall positions bars by a running total, which forces the ~0-100
    opening balance and the ~±3-point contributions onto one axis and squashes the
    contributions into invisibility. Contributions are defined as
    `cₘ = (wₘ,t/Wt)·sₘ,t − (wₘ,p/Wp)·sₘ,p`, which telescopes to exactly `base_t − base_p`
    over the union of both weeks' modules — no residual term, and a module that appeared or
    dropped out shows as its own bar. A test asserts the bars sum to the rendered claim;
    the plan committed to dropping the panel rather than shipping arithmetic that did not
    close.
23. **The level percentile is deliberately drawn in neutral grey, not the RdBu risk ramp.**
    `pctile_156w` ranks the RAW level and is **not** direction-adjusted, so for an inverted
    indicator (VIXCLS, HY_OAS) a high percentile means a LOW score — the golden shows
    HY_OAS at the 91.7th level percentile with a score of 8.3. Painting it on the risk ramp
    would assert a good/bad reading the number does not carry. A test pins both the neutral
    ink and the inversion.
24. **Thin-history guard on percentiles.** The rolling percentile uses `min_periods=1`, so
    it returns a number from a handful of observations; `history_weeks` is now exported and
    the strip renders "—" below 52 weeks rather than presenting noise as a 3-year ranking.
25. **Tier 2 deferred** (long-history level charts with FRED `USREC` recession shading,
    regime persistence/transition stats, drawdown, `run_log` panel, correlation matrix) and
    **conditional analogs ("what happened next") rejected for now** — real practice, but the
    published examples display the failure mode vividly (one write-up reports a "−189%
    annualized" conditional return, a thin-sample artifact), and it slides from *analysis*
    toward *advice*. Revisit only with an explicit minimum-sample rule.
26. **Self-scoring (Brier + reliability diagram) spec'd, deliberately NOT built.** See the
    dedicated section below. It is the highest-value item on the whole ranked list and the
    easiest to do dishonestly.

**Defects found by rendering the page and looking at it** (the dataviz procedure's last
step, which the palette validator cannot cover): raw Python `None` leaking into the
classifier table as text; an SVG-only `fill` class reused on HTML text; and a **pre-existing
latent layout bug** — the 260px glossary popovers are absolutely positioned and count toward
`scrollWidth` even while hidden, so once the indicator table grew a column the whole page
scrolled sideways by 131px. Fixed with a pure-CSS right-anchor for the last four columns.
Measured 0px overflow after. Known and *not* fixed: the wide data tables still overflow at a
375px viewport. The documented remedy (an `overflow-x:auto` wrapper) would clip the glossary
popovers, which are a core feature, and a phone was never a target for a double-click local
file — recorded rather than traded away silently.

27. **Markdown template: `{% endif +%}`, not an extra `{{ nl }}`.** `trim_blocks` eats the
    newline after a block tag, so a line *ending* in a conditional swallows the line after
    it. This collapsed the Policy/Degraded bullets on 2026-07-27 and then the Risk
    budget/Breadth bullets here — each time silently, because the markdown still parsed. The
    correct fix is Jinja's per-tag override `{% endif +%}`; appending `{{ nl }}` instead
    stops `{% endif %}` being newline-adjacent, so the literal newline survives too and you
    get a blank line. `{{ nl }}` stays correct for bullets living entirely inside a
    conditional. A test (`test_markdown_overall_bullets_do_not_collapse_onto_one_line`) now
    pins it, plus one asserting no bare `None` reaches either renderer. The explanatory note
    lives in a Python comment, not a Jinja comment — the first attempt put it in `{#- … -#}`
    whose prose contained `#}`, which closed the comment early and leaked the remainder into
    the report, while the stripping form glued the first bullet to the heading.

28. **Test-isolation hole on the WRITE side (found 2026-07-29 while verifying determinism).**
    `EXPORTS_DIR` is re-bound in each importing module, and neither the per-test
    monkeypatches in `test_portfolio.py`/`test_failsafe.py` nor `ipos/golden.py` covered
    `ipos.report.html` — so `write_html` always wrote to the real directory and **every run
    of the test suite silently overwrote the operator's `data/exports/latest.html` and
    `report.html` with synthetic fixture output.** This is the project's recurring
    "synthetic served as real" failure mode arriving by a new route: the clobbered file
    still looks like a genuine weekly report. This is also what made a byte-comparison of
    two CLI runs appear non-deterministic — the baseline had been replaced by a test.
    Fixed centrally with an autouse `_no_operator_exports` fixture covering all four
    export-writing modules (so a future export path cannot leak because one test forgot to
    patch it), `html_mod` added to `golden.py`, and two guards in `tests/test_isolation.py`
    — one per-module, one end-to-end asserting no mtime under `data/exports` changes.
    **Standing lesson, third instance of the same shape:** `from x import CONST` defeats
    single-point monkeypatching. Isolate by enumerating modules, in `conftest.py`, not
    per-test.

**Evidence-quality note, recorded because it constrains future work here.** This domain has
almost no randomized-trial evidence. What exists is (a) genuine perception experiments on
encoding accuracy — Cleveland & McGill's hierarchy, replicated by Heer & Bostock, with the
important caveat from later work that only *position* is robust across tasks while
color/size/shape are task-dependent; (b) formal scoring-rule theory for forecast evaluation;
(c) revealed preference — what regulators and the largest asset managers actually ship.
Tufte's data-ink ratio rests on limited qualitative evidence and a later quantitative study
found some viewers *prefer* lower data-ink; "AI-adaptive dashboard" claims are vendor
marketing. Consequence for us: **the score heatmap is the weakest encoding in the report**
(color saturation) and should stay a scanning aid, never a reading surface.

#### Spec — item 17: scoring the framework's own past calls

**Status (2026-07-29, same session): the LOGGING half is now BUILT; the scoring/display
half is not.** After walking through the user stories, the operator's decision was to start
the forecast log immediately, on the argument that the *display* can wait but the *logging*
cannot: every week run without recording the week's calls is evidence that can never be
recovered. Delivered: migration `005_forecast.sql` (`log_forecast`),
`configs/forecast_targets.yaml`, `ipos/forecast.py`, a `forecast` stage in `run.py`, and
`tests/test_forecast.py` (9 tests). The first live run logged 9 calls across 3 dimensions.

Design points that differ from, or sharpen, the spec below:

- **Only 5 of 8 stance dimensions are forecast at all.** `growth`, `liquidity` and
  `fundamentals` are condition readings, not exposures — resolving them against the yield
  curve, WALCL or UMCSENT would be circular, because those series are the *inputs*. They are
  listed in an `excluded:` block with the reason, mirroring how `portfolio_mapping.yaml`
  already documents that only some modules map to investable assets. A test asserts no
  dimension is both forecast and excluded, and that every exclusion carries a reason.
- **The hurdle is the benchmark's own median move over the horizon, not "did it rise."**
  Equities rise over most 13-week windows, so "SPX goes up" would score well with no skill
  and make the Brier number uninterpretable. Beating your own typical move keeps the base
  rate near 50%.
- **`baseline_value` and `hurdle` are frozen into the row**, not looked up at resolution
  time, so a later backfill or purge cannot move a logged call's goalposts. Pinned by
  `test_hurdle_and_baseline_are_frozen_against_history_changing`, which rewrites the
  benchmark's entire past and asserts the row is unchanged. This is a direct lesson from the
  2026-07-27 purge, which moved 24 of 26 weeks of Credit scores.
- **Append-only via `ON CONFLICT DO NOTHING`.** The pipeline is idempotent and re-runnable,
  so without this a weights change plus a re-run would let the system silently retro-fit its
  own track record. `test_a_logged_call_can_never_be_rewritten` flips every stance sign,
  re-records under a different `scoring_version`, and asserts the rows are untouched.
- **Probability is capped at 0.20–0.80.** Nothing here justifies a claim stronger than
  4-to-1, so the tilt→probability map is not permitted to make one.
- **`resolve()` and `brier()` were built now even though nothing displays them**, to prove
  the frozen criteria are actually settleable — a resolution rule nobody has ever run is a
  rule that might not work. `brier()` returns the score beside `always_50` and `base_rate`
  because the score alone is meaningless, returns `None` rather than a flattering
  small-sample number, and reports the set of `scoring_version`s so pooling across a bump is
  visible.
- **Calls below |tilt| 0.2 are not logged.** They are not really claims, and near-50%
  predictions are trivially well-calibrated — logging them would pad and flatter the score.

Still to build: the report section (a reliability diagram plus the Brier table), which needs
~26 weeks of resolved calls before it can say anything honest. The spec below stands as
written for that half.

---

Original spec, written before any code, so it could not later be built the easy,
self-flattering way. Nothing in the report
today indicates whether this framework's stance has historically been right or wrong, which
for something named a *decision & analysis* framework is the most consequential omission on
the list.

**The one hard prerequisite: record before the verdict.** A forecast counts only if it was
logged *before* its outcome window opened — dated, quantified, with a fixed horizon and an
unambiguous resolution criterion. Implication: a new append-only `log_forecast` table written
by the weekly run, never back-filled.

- **What is forecast.** Not "the market goes up." Per stance dimension, the sign of the tilt
  is a claim about the *next* window. Proposal: for each dimension with `|tilt| ≥ 0.2`,
  record `P(dimension's benchmark outperforms its own trailing median over the horizon)`
  mapped monotonically from the tilt, plus the horizon and the exact benchmark series id.
- **Horizons.** Fixed at 4 / 13 / 26 weeks, chosen once and frozen. Resolution is mechanical
  from `fact_weekly`, never a judgement call.
- **Scoring.** Brier `BS = 1/N Σ (fₜ − oₜ)²` per dimension and overall, plus a reliability
  diagram (predicted probability vs. observed frequency per bin) and a count per bin. The
  count is not optional: a bin holding three observations must look like three
  observations.
- **The honesty constraints, which are the point of writing this down.**
  1. **No retro-scoring.** Scores computed over history the system has already seen are not
     evidence. If ever produced for calibration of the *method*, they must be labelled
     in-report as in-sample and excluded from any headline figure.
  2. **A baseline is mandatory.** A Brier score alone is uninterpretable. Report it beside
     the always-50% forecast and the trailing-base-rate forecast; if the framework does not
     beat both, the report must say so plainly.
  3. **Report the empty state honestly.** For the first ~26 weeks after this ships there is
     nothing to say, and the section must say "insufficient resolved forecasts (n=…)"
     rather than showing a flattering small-sample number.
  4. **`scoring_version` interacts.** A method change invalidates comparability of forecasts
     made under the old version. `log_forecast` must stamp `scoring_version`, and the
     calibration view must either segment by it or refuse to pool across a bump.
- **Switch trigger / fallback.** If after 52 resolved weeks the framework does not beat both
  baselines on either horizon, that is not a reason to hide the panel — it is the signal to
  revisit scoring weights and bands, and the finding belongs in this log.

### 2026-07-27 (final) — Source audit: three DEAD sources found, market history deepened 5y → up to 56y, OAS cap proven irrecoverable

**Context:** operator pushed back on accepting the OAS gap — "if the one source doesn't work and the fallback doesn't work, what do the alternatives have? Search for the most reliable fallback. Fill in all the data. If some things are not retrievable beyond a couple of years that is fine — we work with what we can get." So: exhaust the alternatives, then document the caps honestly.

**Three sources were dead, only one of which was known:**
1. **DBnomics no longer carries FRED at all.** Its API lists 93 providers and FRED is not one. So **all 15** `{type: dbnomics, locator: FRED/...}` legs were dead, not just the two OAS ones. Removed rather than left in place — a fallback that cannot fire hides the fact that a series is single-sourced. Removing them immediately exposed a genuine policy violation the fiction had masked: **`T10Y2Y` is `critical` and had become single-source**, which `tests/test_connectors.py` caught.
2. **Stooq returns an HTML block page for every symbol** (`^spx`, `spy.us`, `^ndx`, `^dax`, `xauusd`, `hg.f`, `eurusd`, `10usy.b`). Stooq is the *first* source for all eight market series, so Yahoo has silently been carrying them alone. Entries KEPT — this looks like a transient block/rate-limit rather than a structural removal — but no longer assumed live.
3. **The `ustreasury` connector's URL 404s.** The bare `/{year}/all` path no longer exists; the query string (`?type=daily_treasury_yield_curve&field_tdr_date_value={year}&_format=csv`) is required, and `all/all` is refused with 403 so the caller must loop per year. This connector had never been exercised because FRED always answered first — a fallback that was broken from the day it was written.

**Fixes that materially improved the data:**
- **Yahoo history was self-inflicted.** The connector defaulted to `range=5y`, which was the *only* reason the eight market series held exactly 5 years. Now it always requests explicit `period1`/`period2`. **`fact_weekly` grew from 31,889 to 45,763 real rows**: SPX and US10Y now reach 1970 (56.6y), NDX 1985, RUT/DAX 1987, GOLD/COPPER 2000, EURUSD 2003. **Trap avoided:** `range=max` looks like the obvious fix and is actively wrong — with `interval=1d` it silently returns QUARTERLY bars (^GSPC: 168 rows over 41 years, median gap 91 days). Using it would have swapped 5 years of daily data for 168 quarterly points. The 1970 floor is the Unix epoch, not a preference: pre-1970 `period1` values are negative and Windows cannot convert them back (`OSError: [Errno 22]`).
- **`ustreasury` now computes spreads** (`BC_10YEAR-BC_2YEAR`), giving `T10Y2Y`/`T10Y3M` an official keyless second leg from the Treasury itself — the same underlying data as FRED's series. Verified same-day against FRED: **+0.360 vs 0.36** and **+0.730 vs 0.73**. This resolves the critical-single-source violation with a real source rather than by relaxing the rule.
- **Two verified Yahoo legs added:** `VIXCLS` → `^VIX` (daily from 1990, matches FRED exactly at 18.70) and `WTI` → `CL=F` (daily from 2000, last leg only because front-month futures carry a small basis vs the DCOILWTICO spot series). **Rejected:** `DTWEXBGS` → `DX-Y.NYB`. The Fed's broad trade-weighted dollar and ICE's DXY are different indices — 120.5 vs 101.4 on the same day — so it would have been a plausible-looking wrong number.

**OAS: the 3-year cap is real and irrecoverable free.** Every avenue was tested: FRED's own note says *"Starting in April 2026, this series will only include 3 years of observations"* (`observation_start` = 2023-07-28); **ALFRED vintages do not escape it** (2024-01, 2025-06 and 2026-01 vintages all return the same truncated window — the history was purged, not re-dated); the truncation is **universal across ICE BofA series** (`BAMLC0A0CM`, `BAMLH0A1HYBB`, `BAMLH0A3HYC`, `BAMLH0A0HYM2EY` all start 2023-07-28, so no sibling index can stand in); DBnomics is gone. Remaining free routes are aggregator sites needing keys or scraping, deliberately not wired. Percentile scoring uses a 156-week (~3y) window, so 3 years still just fits. Recorded in the registry beside the series.

**Policy test rewritten to match reality.** `test_registry_multisource_no_single_critical` asserted that every FRED series carries a `dbnomics` leg — a rule now impossible to satisfy, and one that had been passing only because of dead entries. Replaced with a keyless-fallback assertion plus an explicit `NO_FREE_ALTERNATIVE` list (7 FRED-only macro series, each with a stated reason), and a second test that fails if that list rots — i.e. if a series named in it later gains a real fallback, or leaves the registry.

**Also corrected a wrong claim I made earlier in this session:** the runs I reported as "live data" were actually **archive-served**. Live pulls were failing TLS (this machine's antivirus intercepts TLS; `SSL_CERT_FILE`/`REQUESTS_CA_BUNDLE` must point at Avast's `wscert.pem`), the pipeline degraded to the archive exactly as designed, and I misread the resulting 22 stale flags as clock skew. With the CA bundle set the weekly run reports **status=OK with zero stale series**.

### 2026-07-27 (latest) — Synthetic data PURGED (real data confirmed unobtainable); portfolio mapping populated; two isolation bugs fixed

**Context:** operator instruction — "no invented data should be here anymore" — plus "get the data" if it exists.

**1. Tried to get the real data first; it is genuinely gone.** Probed both configured sources for `HY_OAS`/`IG_OAS` over 2022-04 → 2023-08:
- **FRED** returns nothing before **2023-07-28**, confirming the rolling-3-year truncation noted in `ipos/backfill.py`.
- **DBnomics** — the registry's designated fallback for exactly this case — is **dead upstream**: `FRED/BAMLH0A0HYM2` and `FRED/BAMLC0A0CM` both return "no series". Recorded as a comment on both registry entries so a future session does not assume the fallback works. **Only remaining route for pre-2023-07 OAS history is a `manual_csv` drop from another provider.**
Conclusion: the invented values could not be replaced, only removed. An honest gap beats a fabricated number.

**2. Purge + full rebuild** via new `scripts/purge_synthetic.py` (dry-run by default, backs the warehouse up first). Removed **4,675 synthetic observation rows** (all 22 series — far more than the 128 canonical rows first reported) and **128 synthetic canonical rows**, then rebuilt canonical + features + scores across the **full 3,847-week history** and replayed 26 weeks of aggregates. Rebuilding everything was required, not optional: scoring is a rolling ~156-week percentile, so every week whose window overlapped the synthetic span had inherited some of it.
**Measured effect:** this week's scores changed **not at all** (2026-07-24's window already cleared the tainted block by 7 days), but **24 of 26 weeks of Credit-module history moved by ±0.5–2.0 points**. So the contamination was real but small — and is now gone. `HY_OAS`/`IG_OAS` go from 221 canonical weeks to 157, starting honestly at 2023-07-28. Warehouse now reports **0 synthetic rows**.
**Prevention:** `ipos-doctor` now reports synthetic-row counts (non-zero canonical rows → warning **and exit code 1**, since those feed scoring) and flags a too-shallow aggregate history.

**3. `configs/portfolio_mapping.yaml` populated** from the operator's two real exports (18 ISINs; both halves checksum exactly against the totals printed in the source documents — €233,316.53 Zero, €596,124.72 Smartbroker). Documented decisions:
- Only **EquityRisk** and **Commodities** can match a share/fund portfolio. The other six modules are macro *condition* readings (yield curve, credit spreads, CB balance sheet, surveys), not asset buckets — noted at the top of the mapping file so the mostly-zero column is understood as expected, not broken.
- Three commodity-producer **equities** (Deutsche Rohstoff, Kinetik, Petrobras — ~€64k) assigned to **Commodities** rather than EquityRisk, on the grounds that their price is driven by the underlying commodity. Operator-confirmed. Flagged in-file as the one reviewable judgement call, since it shifts weight between two modules.
- One position (`DE000VV9F645`, a Vontobel structured product) left **deliberately unmapped**: the PDF names only the issuer, not the underlying, so there is no honest classification. It still counts toward total value and appears in the report's "unmapped" list.
- Combined read: **83.6% EquityRisk (aligned, tilt +0.62), 11.1% Commodities (aligned, +0.71)**, €43,760 unmapped.

**4. Dropped three portfolio-mismatch rules as unactionable.** `PORTFOLIO_LIQUIDITY_MISMATCH`, `PORTFOLIO_GROWTHRISK_MISMATCH` and `PORTFOLIO_FUNDAMENTALS_MISMATCH` would tell the operator they hold "0% of the yield curve" — there is no instrument that gives you weight in a macro reading. The five surviving rules (EquityRisk, Commodities, Credit, RatesLiquidity, FX) all map to investable asset classes; **the set of rules is now the declaration of what counts as investable**, documented in-file.

**5. TWO test-isolation bugs found and fixed** — both latent before, both exposed the moment a real portfolio CSV existed in `data/inbox/`:
- **`build_golden_min` isolated the archive and exports dirs but not `portfolio_csv.INBOX`/`MAPPING_PATH`.** The golden therefore picked up the operator's real holdings — which would have made the regression test machine-dependent *and committed holdings-derived contradictions into the tracked golden file*. Now isolated.
- **No suite-wide guard.** Added an autouse `_no_operator_portfolio` fixture in `conftest.py`, in the same spirit as the existing `_no_network` net, so no test can ever read the real inbox or mapping. Both pinned by `tests/test_isolation.py`, including an assertion that the committed golden contains no ISIN-shaped token.
`scoring_version` again not bumped: verified the regenerated golden is **byte-identical** to the committed one after these changes.

**Still open:** the report's Portfolio-vs-Stance table lists all eight modules, so six rows read 0.0% for a share portfolio. Cosmetic, but a "holdable modules only" view would read better — deferred as it needs an explicit investable-module flag in `configs/modules.yaml`.

### 2026-07-27 (later) — Report explainability pass; aggregate-layer replay added; THIRD synthetic-data instance found (latent, not shipped)

**Context:** operator reviewed the weekly report and reported that hover explanations were largely absent, the regime map's quadrants were unexplained with no visible 6-month path, contradictions gave no indication of *where* the mixed signals were, and every table offered only a one-week horizon. Investigation showed three of those were already-built features that were invisible or starved of data, not missing ones.

**Root causes found (each fixed):**
1. **Tooltip coverage rotted silently.** `glossary.tooltip()` returns the bare label when a key is missing — no warning, no log line, no test failure. Indicators/modules/regime labels/stance dims were fully covered; the entire *metric vocabulary* (`score`, `tilt`, `Δ`, `stale`, `conf`, `risk ×`, `spread`) and the four macro quadrants had no entries at all. **Fix:** entries added (glossary is now 22 concepts + 4 quadrants + 2 contradiction kinds + 7 per-id explanations), plus `tests/test_report_html.py::test_html_every_heading_and_column_is_explained`, which walks every rendered `<h2>`/`<th>` and fails on an unexplained one. That guard immediately caught a real structural mistake made while editing the glossary (a section boundary orphaned `portfolio_vs_stance` into the wrong parent), which is exactly the class of silent failure it exists to stop.
2. **The regime map's 26-week trail was already implemented but rendered TWO points**, because `agg_module`/`agg_regime` are only written for the week a run executes — 3,847 weeks of `fact_score` history but 2 weeks of aggregates. **Fix:** new `ipos/replay.py` + `ipos-replay` CLI recomputes the aggregate layer for past weeks from stored scores. Pure computation, no network, no re-pull: 26 weeks in ~3.5 s. The map was also rebuilt (dated month waypoints, direction arrowhead, start/now callouts, quadrant key panel in the previously-dead 380px to the map's right) and given a regime-label ribbon beneath it.
3. **`module_spread` collapsed a module's disagreement to one float and discarded which members disagreed** — so the report could say "68.0" but not "VIXCLS 28 vs RUT 96". **Fix:** `contradictions.module_members()` + detail enrichment (`lowest(X)`/`highest(X)`, plus a reserved `_modules` key the renderers use to draw a member strip and hide from the key=value display).
4. **Only 2 of 8 modules had a mixed-signal rule.** Fundamentals was running a 91-point internal disagreement (UMCSENT 8.3 vs ICSA 99.4) completely unflagged. **Fix:** one rule per golden module. Existing ids (`EQUITY_MIXED_SIGNAL`, `RATES_MIXED_SIGNAL`) deliberately kept so the `log_contradiction` history stays comparable.
5. **Two different quantities were both labelled "Δ1w"** — a raw-value change in the Indicators table and a score change in Top movers. Raw-value deltas are also not comparable across indicators (WALCL moves in billions, COPPER in cents). **Fix:** headers disambiguated ("Δ value 1w" vs "Δscore 1w"), and `snapshot.indicators[].score_deltas` now carries 1w/4w/12w/52w **score** deltas, rendered as a four-bar horizon strip. Chosen over four numeric columns because the Indicators table would otherwise reach 12 columns and scroll sideways.

**THIRD instance of the synthetic-served-as-real bug class — found, contained, NOT shipped.** The standing question recorded in the 2026-07-26 amendment ("re-audit whenever new code paths touch `fact_observation`/`fact_weekly`") paid off immediately: `ipos-replay` is exactly such a path. Audit found **`HY_OAS` and `IG_OAS` carry 64 weeks of synthetic canonical values (2022-05-06 → 2023-07-21, vintage `synthetic@…@2026-07-17`) still sitting in `fact_weekly`**, with `fact_score` rows derived from them — and `fact_score` has no vintage column, so those scores are indistinguishable from real ones. Current scores are clean by a **7-day margin** (the 156-week percentile window from 2026-07-24 reaches back to 2023-07-28, just past the tainted block), and the 26-week replay range is entirely clean. **Mitigation:** `replay_aggregates()` skips any week with a synthetic canonical row by default and reports what it skipped (`--allow-synthetic` is opt-in, demo-only); verified by test and observed live — a 200-week replay correctly skipped 43 tainted weeks. **Still open:** those 64×2 rows and their derived scores remain in the warehouse. They are harmless at today's lookbacks but will silently poison any deeper backfill or longer lookback window. Recommend purging them (real ICE BofA OAS history cannot cover that span anyway — FRED serves only a rolling 3-year window, which is *why* the demo synthesised them), tracked as a follow-up rather than done unilaterally since it deletes data.

**Not bumped: `scoring_version`.** Per `meso/C9_qa_governance.md` the bump is for changes to methods/lookbacks/bands/weights. Verified empirically before regenerating the golden: zero indicator scores, confidences, values, module rows, `overall`, `regime` or `top_movers` figures changed — the diff is purely additive (`score_deltas`, enriched contradiction details) plus `CREDIT_MIXED_SIGNAL` newly firing on the fixture, which is the item-4 gap being closed. Golden regenerated via `scripts/update_golden.py`.

**Also fixed in passing:** the markdown report's Overall section had a pre-existing Jinja `trim_blocks` bug that collapsed the Policy and Degraded-run bullets onto the Regime line.

### 2026-07-27 — Portfolio module built per the 2026-07-26 plan; one clarification, six ranked follow-ups identified

**Context:** implemented `05_blueprint/03_PORTFOLIO_MODULE.md` in full: `ipos/etl/portfolio_csv.py` (CSV connector, optional), `ipos/aggregate/portfolio.py` (module-weight aggregation + stance-alignment read), a `portfolio` block in `snapshot.json`, and matching sections in both the HTML and markdown reports. 94 tests green (18 new), no regressions.

**One clarification vs. the plan (not a design change, just underspecified in §3):** the plan didn't say whether an unmapped instrument's value counts toward the weight-% denominator under each `unmapped_policy`. Decided: it always does — `unmapped_policy` only controls whether the instrument is *listed*, never whether its euro value is silently dropped from the total (that would understate the operator's real holdings). Documented in `configs/portfolio_mapping.yaml`'s comments and `03_PORTFOLIO_MODULE.md` §8.

**Six follow-ups identified during the build, ranked by impact/effort, none blocking** (full detail: `03_PORTFOLIO_MODULE.md` §8):
1. Verify the CSV column-guessing against a *real* Smartbroker/finanzen.net zero export — the plan's schema was never checked against an actual file. Highest-priority next action for this module.
2. Surface a large weight/tilt mismatch through the existing contradictions engine (`configs/contradictions.yaml`), not just a buried table row — reuses a mechanism that already exists rather than inventing a new one.
3. Currency conversion for non-EUR positions, using the registry's own live `EURUSD` series — likely low real-world impact for German-broker exports, worth confirming after item 1 before building.
4. Log the portfolio stage in `run_log` like every other pipeline stage (currently silent — an audit-trail gap, not a correctness one).
5. Flag a stale/aging portfolio CSV (by file mtime) — the rest of the system has a whole staleness/confidence framework for this; the portfolio file currently has none.
6. A single aggregate portfolio-level read (portfolio-weighted tilt vs. the system's own `risk_budget`) in addition to the current per-module rows — deferred because the weighting formula needs its own small decision, not just code.
**Switch trigger:** none of these block current use (the module degrades correctly with no file present); pick up item 1 first if/when the operator does a real export, since it may invalidate assumptions in items 2–6.

### 2026-07-26 (later still) — Portfolio module planned (not built); automation-feasibility research for Smartbroker/finanzen.net zero

**Context:** operator asked how to integrate real portfolio holdings into the weekly report and, specifically, whether their Smartbroker and finanzen.net zero (Germany) broker accounts could be wired in via an API, and asked for this to be automated.

**Researched before answering (not guessed):**
- **Smartbroker**: has a real REST API (SMARTBROKER+ "API-Trading") that can query portfolios/transactions. Free only with "heavy trader" VIP status (≥45 trades/quarter); otherwise €29.90/month.
- **finanzen.net zero**: no public API found — CSV/PDF export only. Every third-party tool integrating with it (Portfolio Performance, DivvyDiary, Finanzfluss Copilot) relies on the same manual CSV export; there is no more-automated free path.
- **PSD2/open-banking aggregators** (FinAPI, Tink, etc.): real, BaFin-regulated, could read either broker with consent, but these are B2B products priced/scoped for companies integrating with banks, not a simple personal API key — out of scope for a $0 personal project without further access/cost research.

**Decision:** design for maximum automation within the $0 constraint — a drop-a-file, auto-ingest-on-next-run pattern (`data/inbox/portfolio*.csv`, same convention as the existing `manual_csv` connector), not manual data entry, but also not a live API pull (since that isn't free for either broker today). Full design: `05_blueprint/03_PORTFOLIO_MODULE.md`. **Zero code written yet — this is a plan only.**
**Alternative considered and rejected:** an unofficial/reverse-engineered scraping library for either broker (some exist in the wild for German neobrokers) — rejected outright: ToS risk, fragility, and would require storing broker login credentials, which is out of bounds for this agent and inconsistent with the project's security posture regardless of who operates it.
**Switch trigger:** if the operator already qualifies as (or becomes) a Smartbroker heavy trader, or decides €29.90/month or a PSD2-aggregator subscription is worth paying for full automation, revisit as a new D5-style decision — the CSV-drop-in design's aggregation/report logic doesn't change, only how position data arrives.

### 2026-07-26 (later) — Yahoo Finance added as D5's missing second leg; two synthetic-served-as-real bugs found and fixed

**Context:** operator obtained a free `FRED_API_KEY` (self-signup, stored in gitignored `.env`, loaded by `ipos/cli.py`'s built-in loader) — the highest-leverage item from the live-data audit above. This alone unblocked 15/22 series direct from FRED. The remaining blocker was the 7 series that are Stooq-only with zero fallback, one of which (`SPX`) is `critical` and was aborting the whole run.

**Decision — add Yahoo Finance's public chart JSON endpoint as a second leg (extends D5, does not change its policy).** Confirmed reachable and returning real data before building on it. `ipos/etl/yahoo.py` implements `pull`/`pull_ohlc` against `query1.finance.yahoo.com/v8/finance/chart/{symbol}`, registered in `ipos/etl/pull.py`'s `CONNECTORS` and a new `OHLC_CONNECTORS` list (stooq tried first, yahoo second, for the regime governor's OHLC too). Registry updated: all 7 series gained a `yahoo` source after their `stooq` entry (`^GSPC`, `^NDX`, `^RUT`, `^GDAXI`, `GC=F`, `HG=F`, `EURUSD=X`, `^TNX` — `^TNX`'s percent scale was verified against a live FRED value before adopting it, and `XAU=X`/`XAUUSD=X` were tried and rejected as 404 before landing on `GC=F` for gold).
**Alternatives considered:** wait for Stooq to recover (rejected — no ETA, and per-ticker retries showed a wholesale bot-block, not a transient blip); rely solely on the FRED key (rejected — doesn't cover equity indices/commodities/FX at all, FRED has no substitute for `SPX`/`DAX`/etc.).
**Risk, accepted:** Yahoo's endpoint is unofficial/undocumented (unlike FRED/DBnomics), could change or block without notice. Mitigated by never being sole source (Stooq still tried first) and degrading the same way every other source does (archive-replay, then stale-flag) if it also breaks.
**Switch trigger:** if Yahoo also becomes unreachable for >4 weeks for a given series, treat per D5's existing trigger (paid source for that category only).

**Result: the first real (non-synthetic) IPOS snapshot ever produced**, `data/exports/snapshots/2026-07-24/`, status OK, 22/22 real, `synthetic_data: false`.

**Getting there surfaced two real, confirmed instances of exactly the leak D5 amendment 12 ("Synthetic data can no longer be served as real") was meant to close — that fix covered archive-replay, not these:**

1. **Canonical ASOF join's same-date tie-break.** `canonical_weekly.sql` ordered tied `(series_id, obs_date)` candidates by `vintage_id DESC` — and the string `"synthetic@..."` sorts *after* a real vintage's series-id-prefixed string (lowercase `s` > uppercase prefix letters), so a synthetic seed row silently outranked a real pull landing on the same calendar date. Observed live: `DTWEXBGS` and `NFCI` both had a real 2026-07-24 pull and an old synthetic row sharing an obs_date; the synthetic value was served.
2. **Deeper issue, same root cause: fabricated obs_dates.** The `--seed-offline` fixture generator invents a plausible multi-year history *including dates that don't correspond to real-world publication dates*. When one of those fabricated dates is *later* than the real, genuinely-published latest value (observed live: `UMCSENT`, a monthly series — the synthetic seed invented a 2026-06-26 point; the real latest publication was 2026-05-01), the ASOF join's own "most recent obs_date" rule legitimately, correctly-by-its-literal-logic, prefers the fabricated point. The same-date tie-break above cannot catch this — the dates aren't equal.
3. **`snapshot.py`'s `synthetic_data` flag used `as_of_date <= ?`, not `= ?`**, in its check against `fact_weekly`. One legitimate past `--seed-offline` week (2026-07-17) permanently flagged every later real week's snapshot as synthetic too, since that past week's date is `<=` any future as_of.

**Fix:** `build_canonical()` gained a `synthetic: bool = False` parameter (wired from `run.py`'s `seed_offline` flag). A real run's ASOF join now excludes every `vintage_id LIKE 'synthetic@%'` row from the candidate set entirely — not just tie-breaks correctly — so neither a same-date collision nor a fabricated-later-date can surface synthetic data in a real run. `snapshot.py`'s flag query changed to `= ?`. Regression tests: `tests/test_canonical.py` (both shapes of the leak) and a new case in `tests/test_snapshot.py`.
**Why this matters beyond the bug fix:** this is the second time this exact leak class has needed closing (first: archive-replay, amendment 12; now: the canonical join itself, two ways). A future session finding a *third* instance should treat "can synthetic data reach a real snapshot" as a standing question to re-audit whenever new code paths touch `fact_observation`/`fact_weekly`, not assume amendment 12 fully closed it.

### 2026-07-26 — Live-data audit: root cause of 0/22 live pulls; UX explainability pass begun

**Context:** operator asked why a live `ipos-weekly` run produced no real data at all, given "only a few sources are down." Traced every one of the 22 registry entries through its full fallback chain directly (bypassing the fail-safe abort) to get a true per-series picture, not just the 3 `critical` ones that block the run.

**Finding — this is not "a few sources down," it's "the registry has exactly two keyless legs and both are down at once":**
- 15/22 series are FRED-sourced. With no `FRED_API_KEY` set, every one of them falls through to the DBnomics-as-FRED-proxy keyless fallback (D5 amendment 11) — and DBnomics' FRED-provider mirror was returning a server-side `"Could not load storage"` error for every FRED series tested (confirmed DBnomics itself was healthy: a non-FRED provider, ECB, worked fine).
- 7/22 series (`SPX`, `NDX`, `RUT`, `DAX`, `GOLD`, `COPPER`, `EURUSD`, `US10Y_STOOQ`) are Stooq-sourced, and Stooq was returning a bot-verification challenge page for every ticker tested, not a per-ticker issue.
- Of those 7, **`NDX`, `RUT`, `DAX`, `GOLD`, `COPPER`, `EURUSD`, `US10Y_STOOQ` have zero fallback at all** — a real gap against this file's own D5 "never sole source" rule that predates this finding (they were added across Phase 1/3 sessions without a second leg).
- Net: 0/22 succeeded, not because of 3 critical series, but because both live-data legs (Stooq, DBnomics-FRED) were simultaneously down and 7 series never had a second leg to begin with.

**Disposition — ranked fix list, tracked in `PROJECT_STATE.md` §3 item 7, not yet built:**
1. Operator obtains a free `FRED_API_KEY` (2-minute signup) — unblocks 15/22 series directly from FRED, independent of DBnomics. Highest leverage; account creation is operator-only, consistent with D5 amendment 11's original deferral reasoning.
2. Add a second free source (candidate: Yahoo Finance's public endpoint) for the 7 Stooq-only series — this is a new decision in the shape of D5 (alternatives + switch trigger), not a silent addition; not yet built.
3. `ipos-doctor` gains a per-source live reachability check, so this diagnosis takes ten seconds next time instead of an hour.
**Switch trigger:** none needed — this is root-cause documentation, not a policy change. D5's existing switch triggers (a critical series unavailable free for >4 weeks) still govern if the FRED-key fix doesn't materialize.

**Separately, a UX explainability pass began the same session** (operator: "I do not understand a lot of the stuff that is presented here"): item 1 of a ranked improvement plan (`PROJECT_STATE.md` §3 item 8) shipped — a plain-language glossary (`configs/glossary.yaml`) with CSS-only hover/focus popovers on every indicator, module, stance-vector dimension, and regime label in `report.html` (`ipos/report/glossary.py`, wired into `ipos/report/html.py`). No JS added; consistent with D3's self-contained-HTML constraint. Remaining ranked items (layout/progressive-disclosure pass) are listed but not built.

### 2026-07-26 — Discovered orphaned agent-governance draft (`docs/ipos-notes/`); filed as future-phase reference, not adopted

**Context:** a folder-name collision (Windows case-insensitivity merged a pre-existing untracked `IPOS/` folder with the git-tracked `ipos/` code package into one physical directory) surfaced 4 markdown files dated 2026-04-15 that predate this blueprint (v1.0, 2026-07-19): `IPOS_AGENT_OPERATING_MODEL.md`, `IPOS_AUTOMATION_ARCHITECTURE.md`, `IPOS_TOOL_MATRIX.md`, `runbook_investment_research_IPOS_v2.md`. Relocated to `docs/ipos-notes/` (code/docs separation, no content change).

**What they are:** a self-described *draft* agent-governance framework for a **different** deployment shape than what D4/D6 actually chose — a cloud-hosted, multi-analyst environment (Slack/Telegram review channels, a paid "Frontier model" tier, a `cron.schedule` tool, GitHub PR automation, concurrent-analyst locking). Five proposed automations (indicator extraction, reconciliation, daily market summary, monthly playbook refresh, maintenance alerts), a tool allow/deny matrix, and approval/rollback procedures. The documents twice state they are provisional and awaiting "the forthcoming IPOS blueprint" to reconcile against — that reconciliation never happened before this note.

**Why not adopted now:** it directly conflicts with locked decisions D4 (plain CLI + Windows Task Scheduler, explicitly *no orchestrator*) and D6 ($0-first, single-operator, no paid Frontier tier by default). Adopting it as-is would mean reopening both decisions, standing up Slack/GitHub-write/cron infrastructure, and taking on recurring paid-model cost — none of which the current single-operator/$0/local-first build needs.

**Disposition:** kept as-is, unreconciled, filed for a possible future phase (multi-analyst / cloud-hosted / Slack-collaborative IPOS) — **not** part of the current roadmap. See `00_MASTER_PLAN.md` Phase 4 for the pointer. If a future session considers building toward that future, treat this as a draft starting point requiring a fresh D4/D6-style decision analysis first (per §"How to disagree with the plan" in `HANDOVER.md` — do not silently merge it into the current $0/local design).

**Switch trigger:** IPOS moves from single-operator to a multi-analyst/team setting → revisit `docs/ipos-notes/` as the starting draft, run it through the same risk/benefit/cost process as D1–D8 before adopting anything from it.

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

### 2026-07-23 (later) — Phase 2 core value: contradictions, golden harness, regime, HTML report, AI scaffolding

Built four Phase-2 pieces on top of the skeleton. Deviations recorded:

7. **Contradictions engine — safe AST DSL, not a bespoke parser or `eval`.** `ipos/aggregate/contradictions.py` evaluates `configs/contradictions.yaml` predicates with a whitelisted Python `ast` walk (comparisons, boolean/unary ops, and calls to `module()/module_conf()/module_spread()/indicator()/regime()` only). Missing-this-week data ⇒ predicate can't fire (fail-degraded); genuinely unknown ids are caught against `dim_series` at run time. *Reason:* C4's "trivial DSL, no eval" done safely and testably; 9 seed predicates restricted to the golden-20 modules (tech/portfolio-module predicates from `rules.jsonl` return in Phase 3 when those modules have data).

8. **Regime classifier is a close-only MVP (refines C4 decision 4).** `fact_weekly` stores weekly *closes* only, so `ipos/aggregate/regime.py` derives the MARKET_CONDITIONS concepts from closes: overlap_index ← 1−Kaufman efficiency ratio; ATR-accel ← recent-vs-prior mean |return| (speed), *not* std of diffs (which falls for a smooth parabola — caught in testing); swing structure ← close pivots; retracement ← last two pivots. Rule order, confidence heuristic, hysteresis (2-week confirm unless conf≥80), risk_scaler {CHOPPY .5/TRENDY 1.0/MOMENTUM .75/UNCERTAIN .4} and policy_selectors are verbatim from the module. *Swap the feature functions for true weekly OHLC in Phase 3; the rule/confidence/hysteresis layer is unchanged.* Migration `002_regime.sql` adds `regime_confidence`/`policy_json`.

9. **HTML report uses inline CSS/SVG, not Plotly (refines C7 decision 1/3).** `ipos/report/` renders a self-contained report with inline CSS + colored divs/table cells (gauge, tilt bars, score heatmap) — **zero external references**, opens offline by double-click, ~65 KB/week. *Reason:* inlining ~3.5 MB of plotly.js into every weekly file contradicts the token-frugal / resilient principle; hand-rolled CSS meets C7's "static self-contained HTML" intent and the "good" test (understandable in <60s, contradictions inspectable, every indicator has value+score+history). Plotly/Quarto remains the documented upgrade path if interactivity is later needed.

10. **AI live providers deferred; $0 `none`/`manual` implemented (C6).** `ipos/ai/` ships the provider interface, `NoneProvider`/`ManualProvider`, deterministic playbook retrieval (surfaced modules only, no RAG), and a token-budgeted `prompt_bundle.md` writer (system + excerpts + `snapshot.min.json`, ~2.9k tokens on the seed week). `provider: none` is the default and the system is fully functional without it; `manual` writes the bundle for one-click paste into a Claude/ChatGPT subscription ($0). Live providers (gemini/anthropic/ollama) raise a clear "needs key + network, deferred" error rather than shipping untested key-dependent code — consistent with the free-source policy and the user's defer-risky-ops guidance.

### 2026-07-24 — Phase 3: de-risk data & trust, real regime signal, richer dashboard, free calendar

After a 3-part audit checking the build against the original vision, Phase 3 was
re-prioritized (de-risk → signal → dashboard → calendar → modest breadth) over a
blind indicator-widening. User decisions: enrich the static HTML (SVG, not
Streamlit — D3 unchanged); add a lightweight FREE economic calendar instead of a
news pipeline (a news/NLP pipeline was confirmed to have never been in the
vision, and "code computes, LLM narrates / no RAG" is retained); de-risk first.

11. **Keyless-first sourcing (extends D5).** Added `dbnomics` (keyless aggregator
    re-serving FRED/OECD/ECB/ISM) and `ustreasury` (keyless par-yield) connectors;
    every FRED entry now has a keyless fallback so the FRED key is OFF the critical
    path, and no single-sourced series is `critical`. This makes a fresh *keyless*
    machine able to produce a real snapshot — the missing piece of the "free/live
    now" constraint.
12. **Synthetic data can no longer be served as real.** `--seed-offline` routes
    through a synthetic pull path tagged with a `synthetic@` vintage (never written
    to / replayed from the real archive); the snapshot carries a `synthetic_data`
    flag and the reports show a prominent banner. Closes the archive-replay leak.
13. **Real regime signal from OHLC.** Migration 003 + `fact_ohlc`; the Stooq OHLC
    we used to discard is captured and the regime classifier uses real weekly
    true-range/ATR + range-overlap when present (close-only fallback otherwise).
14. **Confidence corrected.** Graded staleness quality; configurable stability
    scale; coherence weighted 0 (it double-counted the contradictions engine and
    inflated single-member modules).
15. **Rates de-dup.** `US10Y_STOOQ` reweighted to 0 (displayed cross-check of
    DGS10, no longer double-counted).
16. **Dashboard enriched within the static-HTML decision (D3 intact).** Pure
    inline-SVG sparklines (per indicator + per module) and a regime 2D map with a
    26-week trail; heatmap 26→52 weeks. Zero external references retained; no
    Streamlit, no Plotly.
17. **Free economic calendar (`ipos/econ_calendar.py`, `configs/calendar.yaml`).**
    Deterministic schedule-rule events (NFP/ISM/CPI/OPEX/FOMC) → snapshot `events`
    + report section. The lighter, $0, no-scrape alternative to a news pipeline.
18. **Thin-module widening.** Added keyless `WRESBAL` (Liquidity) and `ICSA`
    (Fundamentals) so no active module rides on a single indicator (golden-20 → 22).
19. **Cleanups:** scoring-parity test (vectorized == scalar), removed dead
    `stance_vector()`, playbook excerpt truncates large modules at H2 instead of
    dropping them, `playbook_selection` recorded in the snapshot.
