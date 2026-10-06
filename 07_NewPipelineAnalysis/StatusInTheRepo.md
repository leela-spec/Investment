There are five distinct paths in the repository. They are not all current or equally trustworthy.

|Path|Status|What it does|
|---|---|---|
|Weekly macro / portfolio pipeline|Implemented and runnable|Produces macro scores, portfolio posture, reports, and manual order tickets|
|Existing evidence pipeline|Implemented, but not independently validated|Accepts already-structured claims and grounds their quotes; it does **not** extract claims from raw video/PDF/email itself|
|Offline fixture replay|Runnable|Tests pinned transcript/PDF/portfolio fixtures without live services|
|Old Karakeep + Activepieces intake design|Blocked and now under reconsideration|Email, YouTube, websites, PDF/bookmark custody via Karakeep|
|RI-11 replacement-tool research|Current active plan|Select externally proven tools for source → grounded claim extraction before building anything more|

## 1. Implemented weekly macro-to-portfolio pipeline

The actual running IPOS pipeline is in [`ipos/run.py`](C:/GitDev/Investment/ipos/run.py) and is started with:

```
uv run ipos weekly
```

Or scheduled through [`scripts/run_pipeline_automated.ps1`](C:/GitDev/Investment/scripts/run_pipeline_automated.ps1).

```
Market data sources
  → ipos/etl/
  → DuckDB warehouse
  → ipos/transforms/
  → ipos/aggregate/
  → macro regime + risk budget
  → portfolio mapping / risk parity / action matrix
  → manual-only order staging
  → report.md + report.html + snapshot.json
```

Key folders:

- [`ipos/etl`](C:/GitDev/Investment/ipos/etl) — FRED, Stooq, Yahoo, DBnomics, Treasury, broker CSV/PDF adapters.
- [`ipos/transforms`](C:/GitDev/Investment/ipos/transforms) — canonical weekly data and deterministic scoring.
- [`ipos/aggregate`](C:/GitDev/Investment/ipos/aggregate) — regime, macro modules, contradictions, portfolio aggregate.
- [`ipos/portfolio`](C:/GitDev/Investment/ipos/portfolio) — holdings normalization, accounting, risk parity, action matrix, decision gating, staged manual order tickets.
- [`ipos/report`](C:/GitDev/Investment/ipos/report) and [`ipos/export`](C:/GitDev/Investment/ipos/export) — HTML/Markdown reports and snapshots.
- [`configs`](C:/GitDev/Investment/configs) — indicator registry, weights, scoring, portfolio mapping, rules.

This is the strongest implemented path. It is quantitative and deterministic. It does not solve the “research sources become trustworthy claims” problem.

## 2. Existing research-evidence-to-decision path

This was the prior attempt at a source-grounding pipeline:

```
Structured research drop already containing claims
  → data/inbox/research/
  → ipos/evidence/ingest.py
  → exact transcript quote validation
  → action_watch_register.json
  → ipos/portfolio/decision.py
  → action matrix / manual staged order ticket
  → report
```

Relevant implementation:

- [`ipos/evidence/ingest.py`](C:/GitDev/Investment/ipos/evidence/ingest.py) — scans the inbox and processes structured research drops.
- [`ipos/evidence/claims.py`](C:/GitDev/Investment/ipos/evidence/claims.py) — validates a supplied quotation against transcript segments.
- [`ipos/evidence/document_adapter.py`](C:/GitDev/Investment/ipos/evidence/document_adapter.py) — PDF text extraction and page-level quote lookup.
- [`ipos/evidence/register.py`](C:/GitDev/Investment/ipos/evidence/register.py) — persists WATCH/ACTION items.
- [`ipos/portfolio/decision.py`](C:/GitDev/Investment/ipos/portfolio/decision.py) — compares approved evidence with portfolio clusters.
- [`ipos/portfolio/order_staging.py`](C:/GitDev/Investment/ipos/portfolio/order_staging.py) — creates reviewable tickets only; no broker execution.

Its command is:

```
uv run ipos ingest-evidence
```

Critical limitation: this pipeline expects an input file that already has fields such as `claim`, `quote_exact`, sector, and action/watch classification. It verifies and uses the claim, but does not reliably create that claim from a raw Markus Koch transcript, email, article, or PDF. That missing stage is exactly what RI-11 is investigating.

## 3. Offline fixture-acceptance pipeline

This is the test/replay path, not a live intake process:

```
Pinned transcript/PDF/portfolio fixtures
  → TTK + PDF adapters
  → isolated temporary output tree
  → evidence grounding / portfolio replay / simulated actions
  → verification report
```

Main files:

- [`ipos/fixture_acceptance.py`](C:/GitDev/Investment/ipos/fixture_acceptance.py)
- [`ipos/evidence/ttk_adapter.py`](C:/GitDev/Investment/ipos/evidence/ttk_adapter.py)
- [`configs/fixture_acceptance.yaml`](C:/GitDev/Investment/configs/fixture_acceptance.yaml)
- [`orchestration/work/RI-10.yaml`](C:/GitDev/Investment/orchestration/work/RI-10.yaml)

Run:

```
uv run ipos fixture-acceptance
```

It can prove replay, idempotency, quote-grounding, portfolio reconciliation, and manual-only order staging. It cannot prove that raw source material was intelligently and correctly transformed into candidate claims, because the candidate claims are already in the fixtures.

## 4. Old external research-intake architecture: Activepieces + Karakeep

This is the older planned path:

```
WEB.DE / Gmail / YouTube / RSS / manual PDF
  → Activepieces event flows
  → Karakeep custody and deduplication
  → media transcription / transcript-to-knowledge plans
  → IPOS evidence inbox
  → existing evidence-to-decision path
```

Its central historic design is in:

- [`05_blueprint/research/2026-08-28-modular-rebuild`](C:/GitDev/Investment/05_blueprint/research/2026-08-28-modular-rebuild)
- [`08_USER_STORIES_AND_INTEGRATION_WORKFLOWS.md`](C:/GitDev/Investment/05_blueprint/research/2026-08-28-modular-rebuild/08_USER_STORIES_AND_INTEGRATION_WORKFLOWS.md)
- [`implementation-plans`](C:/GitDev/Investment/05_blueprint/research/2026-08-28-modular-rebuild/implementation-plans)
- [`00_runbook/WF07_RESEARCH_TO_PORTFOLIO_DECISION_FLOW.md`](C:/GitDev/Investment/00_runbook/WF07_RESEARCH_TO_PORTFOLIO_DECISION_FLOW.md)

Component plans:

- [`M04_ACTIVEPIECES_PLATFORM.yaml`](C:/GitDev/Investment/05_blueprint/research/2026-08-28-modular-rebuild/implementation-plans/M04_ACTIVEPIECES_PLATFORM.yaml)
- [`M05_ACTIVEPIECES_EMAIL_EVENT_FLOWS.yaml`](C:/GitDev/Investment/05_blueprint/research/2026-08-28-modular-rebuild/implementation-plans/M05_ACTIVEPIECES_EMAIL_EVENT_FLOWS.yaml)
- [`M07_KARAKEEP.yaml`](C:/GitDev/Investment/05_blueprint/research/2026-08-28-modular-rebuild/implementation-plans/M07_KARAKEEP.yaml)
- [`M08_MEDIA_PIPELINE.yaml`](C:/GitDev/Investment/05_blueprint/research/2026-08-28-modular-rebuild/implementation-plans/M08_MEDIA_PIPELINE.yaml)
- [`M09_TRANSCRIPT_TO_KNOWLEDGE.yaml`](C:/GitDev/Investment/05_blueprint/research/2026-08-28-modular-rebuild/implementation-plans/M09_TRANSCRIPT_TO_KNOWLEDGE.yaml)
- [`M19_END_TO_END_ACCEPTANCE.yaml`](C:/GitDev/Investment/05_blueprint/research/2026-08-28-modular-rebuild/implementation-plans/M19_END_TO_END_ACCEPTANCE.yaml)

The machine-readable execution packets are:

- [`RI-01.yaml`](C:/GitDev/Investment/orchestration/work/RI-01.yaml) — source registry and approved samples; stopped because no source mandate was supplied.
- [`RI-04.yaml`](C:/GitDev/Investment/orchestration/work/RI-04.yaml) — WEB.DE and Gmail Activepieces flows; blocked.
- [`RI-05.yaml`](C:/GitDev/Investment/orchestration/work/RI-05.yaml) — approved YouTube discovery; blocked.
- [`RI-08.yaml`](C:/GitDev/Investment/orchestration/work/RI-08.yaml) — RSS/website feeds; blocked.
- [`RI-09.yaml`](C:/GitDev/Investment/orchestration/work/RI-09.yaml) — manual PDF and article bookmarks; blocked.

This path assumed Karakeep was useful as evidence custody. It is now not endorsed as the answer to knowledge extraction: Karakeep organizes and preserves content, but does not establish investment-grade claims.

Also, RI-02, RI-03, RI-06, and RI-07 are referenced as dependencies in older packets but do not exist under `orchestration/work/`. That is a real planning defect, not something to silently work around.

## 5. Current replacement path: source-to-investment-claim tool selection

This is the active plan, not an implementation:

- [`orchestration/work/RI-11.yaml`](C:/GitDev/Investment/orchestration/work/RI-11.yaml)
- [`orchestration/prompts/RI-11_GEMINI_DEEP_RESEARCH.md`](C:/GitDev/Investment/orchestration/prompts/RI-11_GEMINI_DEEP_RESEARCH.md)
- [`orchestration/state.yaml`](C:/GitDev/Investment/orchestration/state.yaml)

Its intended pipeline is:

```
Video / email / PDF / article
  → battle-proven parser or extractor
  → canonical text with stable anchors
  → LLM-generated structured candidate claims
  → exact deterministic quote / page / timestamp validation
  → deterministic portfolio and thesis comparison
  → WATCH or operator-review output
  → manual trading decision
```

RI-11 exists because the existing IPOS evidence code starts at the third line, while the practical value you want begins at the first line.

## Historic architecture material — reference only

These describe earlier competing versions, not separate current systems:

- [`05_blueprint`](C:/GitDev/Investment/05_blueprint) — original macro plan, decision analysis, Phase 1 plan, portfolio module.
- [`06_modular_pipeline_alignment`](C:/GitDev/Investment/06_modular_pipeline_alignment) — three-world reconciliation: original rebuild, WSL2/Apex tooling design, and legacy master plan.
- [`docs/architecture/PIPELINE_DECISION_MATRIX.md`](C:/GitDev/Investment/docs/architecture/PIPELINE_DECISION_MATRIX.md) — old “winning architecture,” including Karakeep assumptions; superseded where it conflicts with RI-11.
- [`docs/architecture/openclaw_research`](C:/GitDev/Investment/docs/architecture/openclaw_research) — archived April research, not active implementation guidance.
- [`docs/ipos-notes`](C:/GitDev/Investment/docs/ipos-notes) and similarly named files under [`ipos`](C:/GitDev/Investment/ipos) — duplicated historical operating notes, not independent pipelines.

The short answer: the weekly macro/portfolio system is real; the source-to-claim system is only partially real; the Karakeep/Activepieces design is an old blocked proposal; RI-11 is the active route to choose a credible replacement for the missing extraction stage.