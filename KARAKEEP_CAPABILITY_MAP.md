# Karakeep Capability Map

**Verified release context:** Karakeep `v0.33.2` / docs `v0.33.0`. Primary verification sourced from official OpenAPI spec (`karakeep-openapi-spec.json`), Docker Compose manifests, tRPC models, CLI source (`apps/cli`), and official documentation site (`docs.karakeep.app`).

| Capability | Verified Current Behavior | IPOS Classification | Reason / Constraint |
|---|---|---|---|
| License | GNU AGPL-3.0 | `ADOPT_AS_OPTIONAL` | Open-source self-host fit. Keep custom IPOS adapter separate (REST client) to avoid license viral coupling. |
| Self-host / local | Docker Compose; persistent `/data` and Meilisearch volume | `ADOPT_AS_OPTIONAL` | Fits local-first constraint, but introduces always-on containers (`karakeep`, `meilisearch`, `chrome`). |
| Windows feasibility | Linux containers via Docker Desktop / WSL2 on Windows | `REQUIRES_OPERATOR_DECISION` | Feasible on Windows, but requires Docker Desktop installation and service management. |
| Storage architecture | PostgreSQL / Drizzle ORM + local filesystem `/data`; Meilisearch index volume | `ADOPT_AS_OPTIONAL` | Back up `/data` and asset files; Meilisearch index is rebuildable. |
| REST API | Bearer token authentication, cursor pagination; OpenAPI schema | `ADOPT` | Deterministic, versioned machine interface for IPOS evidence mirror. |
| CLI (@karakeep/cli) | Official NPM/container CLI; JSON output; bookmarks/lists/tags/dump/migrate | `ADOPT_AS_OPTIONAL` | Useful for backup, dump, and operator operations. REST API is preferred for automated scheduled adapter. |
| Official skills / MCP | Official agent skill and MCP server documented | `NOT_NEEDED` | Optional for human/agent interaction; not needed for scheduled background evidence mirror. |
| RSS ingestion | Automated feed checks, duplicate item skipping; list RSS export | `ADOPT_AS_OPTIONAL` | High value for macro research feeds; feed fetch errors logged gracefully. |
| Web-page archiving | Metadata, screenshots, PDF, full-page archive; headless Chrome | `ADOPT_AS_OPTIONAL` | Solves link rot for web articles; crawler cannot bypass paywalls or strict bot blocks. |
| PDF & media handling | Upload asset then create `asset` bookmark (`image` or `pdf`) | `ADOPT_AS_OPTIONAL` | Fits broker PDF reports and charts intake. |
| YouTube / Video | Video asset support and `yt-dlp` integration documented | `ADOPT_AS_OPTIONAL` | Retains video metadata; transcripts stored as separate text notes. |
| Notes | `text` type bookmarks + per-bookmark `note` field | `ADOPT` | Allows operator to attach qualitative notes directly to evidence items. |
| Highlights | Text highlights attached to link bookmarks | `ADOPT_AS_OPTIONAL` | Captures key quotes/claims from research articles. |
| Tags | Manual & AI tags; API records `attachedBy` (`human` vs `ai`) | `ADOPT` | IPOS adapter consumes only human-attached control tags (`ipos:status:reviewed`, `ipos:module:<id>`). |
| Manual & Smart Lists | Manual bookmark lists + query-based smart lists | `ADOPT` | Uses one dedicated manual list: `IPOS Inbox`. |
| Full-text search | Meilisearch-backed FTS; query language; API `searchMode=fts` | `ADOPT` | Instant qualitative evidence search across all saved articles, PDFs, and notes. |
| Semantic search | Experimental semantic/hybrid search in v0.33.x; model-dependent | `NOT_NEEDED` | Avoids non-deterministic vector search complexity; Meilisearch FTS is sufficient. |
| Webhooks | Bookmark creation/update webhook events documented | `ADOPT_AS_OPTIONAL` | Scheduled REST polling is preferred initially for failure recovery and idempotency. |
| Automation rules | If/then auto-tagging, routing, and archiving rules | `ADOPT_AS_OPTIONAL` | Use strictly for inbox hygiene; rules must never alter IPOS Playbook or numeric scores. |
| Readable content API | Markdown text retrieval, max 50,000 chars/chunk, cursor pagination; SHA-256 `contentVersion` | `ADOPT` | Excellent deterministic boundary: SHA-256 over format, NUL, and normalized content. |
| Export | CLI `dump` command exports account data, JSON/JSONL, assets to `.tar.gz` archive | `ADOPT` | Complete portable export; backup/dump verification required during onboarding. |
| Backup & restore | API `/api/v1/backups` generates downloadable ZIPs; CLI `migrate` transfers instances | `REQUIRES_OPERATOR_DECISION` | Disaster recovery path; verify clean-instance restore before production reliance. |
| Deduplication | Duplicate URL returns existing bookmark ID (`200 OK`); RSS duplicates skipped | `ADOPT` | API `check-url` prevents duplicate creation; stable bookmark IDs preserved. |
| Identifiers | Stable string UUIDs for bookmarks, lists, tags, assets, highlights, feeds | `ADOPT` | IPOS uses Karakeep UUIDs as stable foreign keys in evidence mirror envelopes. |
| Metadata preservation | `firstCreatedAt`, `createdAt`, `modifiedAt`, source URL, author, domain, published date, asset IDs | `ADOPT` | Complete provenance metadata captured and mirrored into IPOS evidence envelopes. |
| Update/versioning | Mutable bookmark metadata; content hash (`contentVersion`); append-only IPOS mirror | `ADOPT_AS_OPTIONAL` | IPOS appends new versions to local mirror (`data/research/karakeep/`) upon content hash change. |
| Authentication | Bearer API token generated in Web UI (Settings > API Keys) | `ADOPT` | Token stored securely in environment (`.env`), never committed to Git. |
| Failure behavior | Crawl/tag/fetch statuses exposed in API responses (`success`, `failure`, `pending`) | `ADOPT` | Adapter handles degraded states gracefully; failure on one item does not block others. |
| Release activity | Highly active maintenance; v0.33.2 released August 2026 | `ADOPT_AS_OPTIONAL` | Pin version (v0.33.2) to maintain schema stability. |

## Subsystem Responsibility Split

| Function / Component | Owner Subsystem |
|---|---|
| Live working research inbox & human curation UI | Karakeep |
| Captured page/file asset storage (PDFs, screenshots, HTML) | Karakeep (mirrored by IPOS export dump) |
| Append-only evidence event mirror consumed by IPOS | IPOS REST Adapter (`data/research/karakeep/`) |
| Qualitative research search interface | Karakeep (Meilisearch FTS) |
| Operational Playbook modules & Playbook rules | IPOS (`04_playbook/modules/`, `configs/`) |
| Quantitative market series, scoring, regime classification | IPOS (`ipos/`, DuckDB `warehouse.duckdb`) |
| Weekly risk budget, stance vector, static HTML report | IPOS (`ipos/export/`, `ipos/report/`) |
