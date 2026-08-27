# Executive Verdict — Karakeep → IPOS Integration Evaluation

## Decision

**`TEST_FURTHER`, then adopt strictly as an optional, fail-open research sidecar. Do NOT connect it to numeric scoring or automated Playbook rule modification.**

Karakeep solves a real and specific gap: current IPOS deterministically ingests numerical time-series and portfolio CSVs, archives raw numeric pulls in Parquet, calculates percentile/z-scores, aggregates risk budgets and regime stances, and renders weekly Plotly HTML reports. However, IPOS has no implemented system for capturing, archiving, tagging, highlighting, searching, and exporting external qualitative research artifacts (macro commentary, broker research PDFs, YouTube transcripts, research notes, and RSS feeds).

Karakeep should provide a combination of:
- **C — Ingestion inbox:** browser extension, mobile, REST API, CLI, and RSS feed capture;
- **B — Human-facing research dashboard:** lists, tags, notes, highlights, and full-text search;
- **A — Canonical working raw-research record (qualified):** Karakeep owns the live working object and preserved page/file assets, but it must not be the sole durable record. A version-pinned REST/dump pull and append-only IPOS-side export mirror (`data/research/karakeep/`) must preserve every consumed version.

Karakeep must **NOT** become the canonical operational Playbook, the DuckDB numeric warehouse, the scoring engine, the report renderer, or an autonomous source of Playbook rule changes.

## Exact Value Gained

| New Value | Current IPOS Status | Karakeep Evidence | Verdict |
|---|---|---|---|
| Single inbox for URLs, notes, PDFs, images, RSS | Not implemented | Three bookmark types (`link`, `text`, `asset`) + RSS ingest | `ADOPT_AS_OPTIONAL` |
| Local page/file preservation against link rot | Numeric Parquet archive only | Screenshots, PDF, full-page archive, uploaded assets, video assets | `ADOPT_AS_OPTIONAL` |
| Human curation & tagging | Configs/Playbook curation exists; no research inbox | Manual tags, lists, notes, highlights, favourites | `ADOPT_AS_OPTIONAL` |
| Deterministic retrieval/export | No research-object API | REST/OpenAPI, official CLI JSON, readable-content endpoint, portable dump | `ADOPT_AS_OPTIONAL` |
| Full-text evidence search | No research corpus search | Meilisearch-backed FTS and qualifier query language | `ADOPT_AS_OPTIONAL` |
| AI tagging / semantic search | IPOS deterministically computes numbers in Python/SQL | Optional Ollama / OpenAI-compatible features | `NOT_NEEDED` |

Karakeep's official Docker deployment uses persistent data and Meilisearch volumes; the REST API exposes bookmarks, assets, highlights, lists, tags, feeds, and downloadable backups; the CLI `dump` command exports account metadata and content as JSON/JSONL plus binary assets.

## Smallest Reliable Path

1. Run a **version-pinned disposable Karakeep v0.33.2 instance** on Windows Docker Desktop / WSL2 (or Linux host).
2. Disable external/paid AI features; enable full-text search (Meilisearch) and headless Chrome crawling. Create one manual list (`IPOS Inbox`) and an explicit operator tag vocabulary (`ipos:status:new|reviewed|rejected`, `ipos:module:<id>`).
3. Use a **read-only scheduled REST pull**, not webhooks and not CLI commands, as the primary integration. The adapter retrieves bookmark metadata, readable markdown content, highlights, and asset manifests, then writes append-only evidence event files with SHA-256 content/metadata hashes.
4. The adapter stops at an isolated IPOS evidence view (`data/research/karakeep/`). It **never** writes to DuckDB scoring tables (`fact_weekly`, `fact_score`, `agg_*`), Playbook modules (`04_playbook/modules/`), or production configs (`configs/`).
5. Require successful duplicate, dump, and clean-instance migration/restore tests before promotion to `ADOPT_NOW`.

The REST API is preferred over CLI execution for automation because the API supplies standard HTTP status codes and a formal OpenAPI schema. In the local partial CLI test, `karakeep bookmarks list` against an unreachable server printed an error message but exited with status code `0`; a production scheduler therefore cannot trust CLI exit codes alone.

## What It Replaces

- Replaces ad-hoc bookmark/note/RSS capture and manual collection folders outside the repository.
- Does **NOT** replace IPOS's numeric source connectors, raw Parquet archive, DuckDB warehouse, Playbook modules, extracted JSONL, snapshots, static HTML reports, portfolio CSV ingestion, or LLM narration.

## Decision Gates

- **No architecture gate now:** evidence strongly favors the sidecar boundary over core integration.
- **Adoption gate:** complete the blocked writable-instance POC (including dump and clean-instance recovery verification).
- **Operator choice after POC:** whether maintaining an always-on Docker container service is worth the qualitative workflow value. Core IPOS remains 100% functional with zero dependencies on Karakeep.

## Confidence Score

**84 / 100.** Product, API, schema, and license findings are verified from primary sources. The overall verdict remains `TEST_FURTHER` pending full end-to-end writable server POC execution on Docker Desktop.
