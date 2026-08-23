# Current IPOS Gap Map

## Repository inspection scope

The effective project truth is [commit `6353c1a`](https://github.com/leela-spec/Investment/commit/6353c1acb768d61a7be83477e1cc4fee55653d97) on `main`. The eight commits inspected at or immediately before the pin cover the prompt split, launcher/method basis and preflight records, followed by the 2026-08-18 forecast/chart reconciliation and implemented forecast/report changes. This confirms the research prompt is newer than, but does not supersede, the implemented architecture recorded in `PROJECT_STATE.md` and code. `[REPO_OBSERVED]`

## Current implemented boundary

At the pinned commit, current code establishes this production chain:

`registry/config → source connector → validated observation → raw Parquet archive + DuckDB → deterministic features/scores/aggregates → snapshot.json → Markdown/static HTML → optional narration`

Evidence:

- `ipos/etl/base.py` defines connector fallback, append-only raw Parquet archive, stale replay and series-level fail-degraded behavior. `[REPO_OBSERVED]`
- `ipos/etl/pull.py` loads validated observations into DuckDB with deterministic row hashes and vintage IDs. `[REPO_OBSERVED]`
- `ipos/export/snapshot.py` creates byte-stable versioned weekly artifacts; `tests/test_snapshot.py` pins determinism. `[REPO_OBSERVED]`
- `ipos/ai/*` performs deterministic Playbook retrieval and optional last-mile narration; the numerical pipeline works with AI off. `[REPO_OBSERVED]`
- `03_extract/*.jsonl` is upstream knowledge; `PROJECT_STATE.md` explicitly says runtime does not read it directly. `[REPO_OBSERVED]`

## Gap table

| Need | Current implementation | Gap | Karakeep fit | Boundary decision |
|---|---|---|---|---|
| Capture arbitrary web research | No bookmark/web capture connector | High | Strong | Karakeep sidecar |
| Preserve article/page/media | Numeric pulls only (`data/archive/...parquet`) | High | Strong, when crawling/archival enabled | Karakeep + exported mirror |
| Capture PDF and research note | Portfolio/manual numeric CSV only | High | Strong | Karakeep sidecar |
| RSS discovery | No research RSS intake | High | Strong | Karakeep sidecar |
| Human tags/lists/highlights/notes | Playbook/config files are curated operational knowledge, not research records | High | Strong | Karakeep owns working curation |
| Full-text research search | No research corpus index | High | Strong with Meilisearch | Karakeep only |
| Provenance for numerical observations | `source_hash`, `vintage_id`, archive path, registry reference | Already strong | Karakeep is not a replacement | `IPOS_ALREADY_HAS_THIS` |
| Deterministic scores and rules | Python/SQL/config + golden tests | Complete | Karakeep conflicts if allowed to write here | `CONFLICTS_WITH_IPOS` |
| Weekly snapshots/report | Implemented and tested | No gap | Duplicating adds no value | `IPOS_ALREADY_HAS_THIS` |
| LLM narration | Optional provider/file bundle | No core gap | Karakeep AI is unrelated | `NOT_NEEDED` |
| Research-to-rule promotion governance | No implemented evidence promotion path | Real but belongs to downstream governance research | Karakeep can supply candidates, not approve | Out of R1 production scope |

## Stale/conflicting documents

- `PROJECT_STATE.md` marks `docs/ipos-notes/*` and four 2026-04-15 cloud/multi-analyst documents as unreconciled and conflicting with local-first/single-operator/no-orchestrator decisions. They are not authority for R1. `[REPO_OBSERVED]`
- Historical plans saying a phase is "not built" are superseded where `PROJECT_STATE.md`, current modules and tests show implementation. `[REPO_OBSERVED]`
- The active implementation is artifact-first and has no always-on production service. Karakeep therefore adds operational complexity and must remain optional/fail-open.

## Exact problem statement

Karakeep solves **research acquisition and working evidence custody**, not investment calculation. The absence is material because source pages, PDFs, notes and RSS items currently have no uniform identifier, archived content, curation metadata, search surface or deterministic export contract inside current IPOS.
