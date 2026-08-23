# Executive Verdict — Karakeep → IPOS

## Decision

**`TEST_FURTHER`, then adopt only as an optional research sidecar. Do not connect it to scoring.**

Karakeep solves a real gap: current IPOS can deterministically ingest numerical series and portfolio CSVs, archive raw numeric pulls, calculate scores, and render weekly reports, but it has no implemented system for capturing, archiving, tagging, highlighting, searching and exporting external research artifacts. This is verified from the pinned code and repository tree, not inferred from old planning prose. `[REPO_OBSERVED]`

Karakeep should provide a combination of:

- **C — ingestion inbox:** browser/mobile/API/CLI/RSS capture;
- **B — human-facing research dashboard:** lists, tags, notes, highlights and search;
- **A — canonical working raw-research record, qualified:** Karakeep may own the live working object and preserved page/file assets, but it must not be the only durable record. A version-pinned CLI dump and append-only IPOS-side export mirror must preserve every consumed version.

It must **not** become the canonical operational Playbook, the DuckDB numeric warehouse, the scoring engine, the report renderer, or an autonomous source of rule changes.

## Exact value gained

| New value | Current IPOS status | Karakeep evidence | Verdict |
|---|---|---|---|
| One inbox for URLs, text notes, images/PDFs and RSS | Not implemented | Three bookmark types plus RSS import | `ADOPT_AS_OPTIONAL` |
| Local page/file preservation against link rot | Numeric Parquet archive only | screenshots, PDF, full-page archive, uploaded assets, video assets | `ADOPT_AS_OPTIONAL` |
| Human curation | Playbook/config curation exists, not a research inbox | manual tags, lists, notes, highlights, archive/favourite | `ADOPT_AS_OPTIONAL` |
| Deterministic retrieval/export | No research-object API | REST/OpenAPI, official CLI JSON, readable-content endpoint, portable dump | `ADOPT_AS_OPTIONAL` |
| Full-text evidence search | No research corpus search | Meilisearch-backed FTS and query language | `ADOPT_AS_OPTIONAL` |
| AI tagging/semantic search | IPOS deliberately avoids RAG and AI computation | optional Ollama/OpenAI-compatible features | `NOT_NEEDED` initially |

Karakeep's official Docker deployment uses persistent `data` and Meilisearch volumes; the API exposes bookmarks, assets, highlights, lists/tags, feeds and downloadable backups; the CLI `dump` command exports account metadata/content as JSON/JSONL plus binary assets. The tagged dump source does **not** explicitly export highlights, so dump/migration remains a recovery test gate. `[VERIFIED_PRIMARY]` See [Docker install](https://docs.karakeep.app/installation/docker/), [API](https://docs.karakeep.app/api/karakeep-api/), and [v0.33.2 dump source](https://github.com/karakeep-app/karakeep/blob/v0.33.2/apps/cli/src/commands/dump.ts).

## Smallest reliable path

1. Run a **version-pinned disposable Karakeep v0.33.2 POC** on Windows Docker Desktop/WSL2.
2. Disable paid/AI features; keep FTS and crawling. Create one manual list, `IPOS Inbox`, and a small operator-owned tag vocabulary.
3. Use a **read-only scheduled REST pull**, not webhooks and not the CLI, as the first integration. The adapter retrieves bookmark metadata, readable content, highlights and asset manifests, then writes append-only evidence-event files with hashes.
4. The adapter stops at an isolated `IPOS evidence view`. It never writes `fact_observation`, `fact_weekly`, `fact_score`, `agg_*`, Playbook modules or production configs.
5. Require successful duplicate, dump and clean-instance migration/restore tests before `ADOPT_NOW`.

The REST API is preferred over the CLI for automation because the API supplies HTTP status codes and a formal OpenAPI schema. In the local partial POC, `karakeep bookmarks list` against an unreachable server printed an error but exited `0`; a production scheduler therefore cannot trust that CLI command's process status alone. `[POC_OBSERVED]`

## What it replaces

- Replaces ad-hoc bookmark/note/RSS research capture and manual collection folders, if any exist outside the repository.
- Does **not** replace IPOS's numeric source connectors, append-only Parquet archive, DuckDB, Playbook, extracted JSONL, snapshots, HTML report, portfolio CSV path or optional narration.

## Decision gates

- **No architecture gate now:** evidence strongly favors the sidecar boundary over core integration.
- **Adoption gate:** complete the blocked writable-instance POC, including dump plus clean-instance recovery.
- **Operator choice after POC:** whether the added always-on Docker service is worth the workflow value. The evidence does not justify making it load-bearing.

## Confidence

**84/100.** Product/API/schema findings are current and primary-sourced; the recommendation remains `TEST_FURTHER` because this environment could not execute a writable server POC.
