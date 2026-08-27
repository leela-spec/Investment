# Current IPOS Gap Map

## Repository Inspection Scope

The effective project truth is [commit `cec42be`](https://github.com/leela-spec/Investment/commit/cec42be) on `main`. Recent commits cover merging the Macro Rule Advisor Engine (`ipos/advisor/rule_engine.py`), Backtesting & Simulation Engine (`ipos/backtest/engine.py`), 120-indicator registry candidate (`configs/registry_120.yaml`), root `AGENTS.md` authority routing, registry promotion scripts, and source health checks. This confirms current code is fully updated and operationalized.

## Current Implemented Boundary

Current production code establishes this deterministic execution chain:

`registry/config → source connector → validated observation → raw Parquet archive + DuckDB → deterministic features/scores/aggregates → snapshot.json → static Plotly HTML / report.md → optional narration`

Evidence in codebase:
- `ipos/etl/base.py` defines connector fallbacks, append-only raw Parquet archiving, stale replay, and series-level fail-degraded behavior.
- `ipos/etl/pull.py` loads validated observations into DuckDB (`warehouse.duckdb`) with deterministic row hashes and vintage IDs.
- `ipos/export/snapshot.py` creates byte-stable versioned weekly snapshots (`snapshot.json`).
- `ipos/advisor/rule_engine.py` evaluates 126 seminar rules and 44 process steps deterministically.
- `ipos/backtest/engine.py` evaluates regime classification accuracy and drawdown suppression.
- `ipos/ai/*` performs deterministic Playbook retrieval and optional last-mile narration; the numerical pipeline works 100% with AI off.
- `03_extract/*.jsonl` holds upstream knowledge extraction; `PROJECT_STATE.md` explicitly specifies that runtime code does not read JSONL directly.

## Gap Analysis Matrix

| Need | Current IPOS Implementation | Gap Severity | Karakeep Fit | Integration Boundary Verdict |
|---|---|---|---|---|
| Capture arbitrary web research | No bookmark / web capture connector | High | Strong | Karakeep sidecar |
| Preserve article/page/media | Numeric pulls only (`data/archive/...parquet`) | High | Strong (crawling/archiving) | Karakeep + exported mirror |
| Capture PDF & research notes | Portfolio/manual numeric CSV only | High | Strong | Karakeep sidecar |
| RSS discovery & feed intake | No research RSS intake | High | Strong | Karakeep sidecar |
| Human tags/lists/highlights/notes | Playbook/configs are operational knowledge, not research records | High | Strong | Karakeep owns working curation |
| Full-text research search | No research corpus search index | High | Strong (Meilisearch) | Karakeep only |
| Provenance for numerical series | `source_hash`, `vintage_id`, raw Parquet, registry refs | Complete (No gap) | Karakeep is not a replacement | `IPOS_ALREADY_HAS_THIS` |
| Deterministic scores and rules | Python / SQL / YAML configs + golden tests | Complete (No gap) | Karakeep conflicts if allowed to write here | `CONFLICTS_WITH_IPOS` |
| Weekly snapshots & HTML reports | Implemented and verified | Complete (No gap) | Duplicating adds no value | `IPOS_ALREADY_HAS_THIS` |
| LLM narration layer | Optional provider / prompt bundle | Complete (No gap) | Karakeep AI is unrelated | `NOT_NEEDED` |
| Research-to-rule promotion governance | No automated rule promotion path | Real | Karakeep supplies candidates, cannot approve | Out of R1 scope; requires human operator |

## Stale / Conflicting Documents

- `PROJECT_STATE.md` explicitly notes that `docs/ipos-notes/*` and historical cloud/multi-analyst draft proposals conflict with IPOS invariants (local-first, single-operator, no heavy orchestrator, $0-first). They are not authority.
- Historical plans stating a phase is "not built" are superseded where `PROJECT_STATE.md`, active code, and `pytest` suites demonstrate completion.
- The active IPOS engine is artifact-first and has no always-on server requirement. Karakeep adds always-on Docker service complexity and must remain optional and fail-open.

## Exact Problem Statement

Karakeep solves **qualitative research acquisition and working evidence custody**, NOT investment calculation or numeric scoring. The absence of qualitative intake in IPOS is material because source web pages, broker PDFs, analyst notes, and RSS items currently have no uniform identifier, archived content store, curation metadata, search index, or deterministic export contract inside IPOS.
