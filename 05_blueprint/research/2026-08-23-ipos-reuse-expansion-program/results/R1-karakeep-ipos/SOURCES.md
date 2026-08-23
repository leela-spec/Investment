# R1 Source Ledger

Research cut-off: **2026-08-23**. Repository claims are pinned to `leela-spec/Investment@6353c1acb768d61a7be83477e1cc4fee55653d97`; Karakeep source/schema claims are pinned to `v0.33.2` unless a page is explicitly versioned otherwise.

## Evidence labels

- `[REPO_OBSERVED]`: inspected directly at the effective repository pin.
- `[VERIFIED_PRIMARY]`: inspected in official documentation, tagged source, schema, or release metadata.
- `[POC_OBSERVED]`: reproduced in the disposable local command-line test described in `POC_RESULTS.md`.
- `[INFERENCE]`: reasoned conclusion from cited evidence, not a product guarantee.
- `[COMMUNITY_REPORT]`: user/community report used only to identify a test case.
- `[UNVERIFIED]`: unresolved and excluded from any unconditional production claim.

## Authoritative IPOS project sources

The following were read from the effective pin, not from the mutable `main` branch:

| Source | Use |
|---|---|
| [R1 prompt](https://github.com/leela-spec/Investment/blob/6353c1acb768d61a7be83477e1cc4fee55653d97/ExternalAddonsResearch/prompts/R1_Karakeep_to_IPOS_integration.md) | Track requirements and definition of done |
| [Autonomous program launcher](https://github.com/leela-spec/Investment/blob/6353c1acb768d61a7be83477e1cc4fee55653d97/05_blueprint/research/2026-08-23-ipos-reuse-expansion-program/AUTONOMOUS-PROGRAM-LAUNCHER.md) | Global controls, evidence requirements, review gates |
| [METHOD-BASIS](https://github.com/leela-spec/Investment/blob/6353c1acb768d61a7be83477e1cc4fee55653d97/05_blueprint/research/2026-08-23-ipos-reuse-expansion-program/METHOD-BASIS.md) | Research and independent-review method |
| [PROJECT_STATE.md](https://github.com/leela-spec/Investment/blob/6353c1acb768d61a7be83477e1cc4fee55653d97/PROJECT_STATE.md) | Current implementation authority and stale-doc warnings |
| [Master plan](https://github.com/leela-spec/Investment/blob/6353c1acb768d61a7be83477e1cc4fee55653d97/05_blueprint/00_MASTER_PLAN.md) | Architectural principles and target operating model |
| [Decision analysis](https://github.com/leela-spec/Investment/blob/6353c1acb768d61a7be83477e1cc4fee55653d97/05_blueprint/01_DECISION_ANALYSIS.md) | Reuse, local-first, determinism, and optional-LLM constraints |
| [Portfolio module](https://github.com/leela-spec/Investment/blob/6353c1acb768d61a7be83477e1cc4fee55653d97/05_blueprint/03_PORTFOLIO_MODULE.md) | Current portfolio/scoring boundary |
| [Playbook modules](https://github.com/leela-spec/Investment/tree/6353c1acb768d61a7be83477e1cc4fee55653d97/04_playbook/modules) | Operational modules that research must not silently alter |
| [Extract artifacts](https://github.com/leela-spec/Investment/tree/6353c1acb768d61a7be83477e1cc4fee55653d97/03_extract) | Upstream process, indicator, and rule evidence artifacts |
| [Runtime configs](https://github.com/leela-spec/Investment/tree/6353c1acb768d61a7be83477e1cc4fee55653d97/configs) | Active module/source/scoring/report controls |
| [ETL implementation](https://github.com/leela-spec/Investment/tree/6353c1acb768d61a7be83477e1cc4fee55653d97/ipos/etl) | Current registry/connectors/raw-store and fail-degraded behavior |
| [Export implementation](https://github.com/leela-spec/Investment/tree/6353c1acb768d61a7be83477e1cc4fee55653d97/ipos/export) | Snapshot boundary |
| [Report implementation](https://github.com/leela-spec/Investment/tree/6353c1acb768d61a7be83477e1cc4fee55653d97/ipos/report) | Existing Markdown/static-HTML reporting boundary |
| [AI implementation](https://github.com/leela-spec/Investment/tree/6353c1acb768d61a7be83477e1cc4fee55653d97/ipos/ai) | Optional last-mile narration boundary |

All files under the required directories above were inspected locally at the pin. Repository search found no current Karakeep/bookmark/research-evidence intake implementation outside research-program material. `[REPO_OBSERVED]`

## Karakeep primary sources

### Product, deployment, storage, security, and maintenance

| Source | Claims supported |
|---|---|
| [Documentation home, v0.33.0](https://docs.karakeep.app/) | Current feature overview, media capture, extension/mobile ecosystem |
| [Docker installation](https://docs.karakeep.app/installation/docker/) | Supported Compose deployment and persistent-volume pattern |
| [Tagged Compose file](https://github.com/karakeep-app/karakeep/blob/v0.33.2/docker/docker-compose.yml) | Web, Chrome, and Meilisearch services; `/data` and search-index volumes |
| [Minimal installation](https://docs.karakeep.app/installation/minimal-install/) | Degraded behavior without Chrome, Meilisearch, or AI |
| [Administration FAQ](https://docs.karakeep.app/administration/FAQ/) | SQLite `db.db`, assets under `/data`, operational storage facts |
| [Security considerations](https://docs.karakeep.app/administration/security-considerations/) | Crawler/SSRF threat boundary and partial protection warning |
| [AGPL-3.0 license](https://github.com/karakeep-app/karakeep/blob/v0.33.2/LICENSE) | License identity and terms |
| [v0.33.2 release](https://github.com/karakeep-app/karakeep/releases/tag/v0.33.2) | 2026-08-11 release and current maintenance evidence |
| [All releases](https://github.com/karakeep-app/karakeep/releases) | Recent release cadence |
| [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) | Windows/WSL2 execution feasibility |
| [Docker Desktop license terms](https://docs.docker.com/subscription/desktop-license/) | Operator-specific commercial-use licensing caveat |

### Capture, retrieval, automation, and agent surfaces

| Source | Claims supported |
|---|---|
| [Bookmarking](https://docs.karakeep.app/using-karakeep/bookmarking/) | Link metadata, screenshots/full-page/PDF archive, notes, assets, crawling |
| [Search query language](https://docs.karakeep.app/using-karakeep/search-query-language/) | Full-text qualifiers and smart-list/search behavior |
| [Advanced workflows](https://docs.karakeep.app/using-karakeep/advanced-workflows/) | Rules and bookmark webhook events |
| [RSS feeds](https://docs.karakeep.app/integrations/rss-feeds/) | Periodic RSS ingestion, duplicate skipping, list RSS publication |
| [Command-line integration](https://docs.karakeep.app/integrations/command-line/) | Official CLI installation/authentication/use |
| [Published CLI package](https://www.npmjs.com/package/@karakeep/cli) | Latest published CLI version observed (`0.33.1`) and package availability |
| [MCP integration](https://docs.karakeep.app/integrations/mcp/) | Official MCP support |
| [Agentic skills](https://docs.karakeep.app/integrations/agentic-skills/) | Official agent skill support |

### Deterministic interface and portability evidence

| Source | Claims supported |
|---|---|
| [REST API documentation](https://docs.karakeep.app/api/karakeep-api/) | Bearer API-key use and API entry point |
| [v0.33.2 OpenAPI schema](https://github.com/karakeep-app/karakeep/blob/v0.33.2/packages/open-api/karakeep-openapi-spec.json) | Paths, object schemas, cursor pagination, HTTP results, identifiers, timestamps, types, statuses, assets, highlights, feeds, backups |
| [Bookmark model/readable-content source](https://github.com/karakeep-app/karakeep/blob/v0.33.2/packages/trpc/models/bookmarks.ts) | Content chunking and `contentVersion` computation |
| [CLI source tree](https://github.com/karakeep-app/karakeep/tree/v0.33.2/apps/cli/src) | Actual commands and JSON/CLI implementation |
| [CLI dump source](https://github.com/karakeep-app/karakeep/blob/v0.33.2/apps/cli/src/commands/dump.ts) | Dump manifest, JSON/JSONL, content and binary export implementation; also the absence of an explicit highlight-export phase |
| [CLI migrate source](https://github.com/karakeep-app/karakeep/blob/v0.33.2/apps/cli/src/commands/migrate.ts) | Migration coverage, URL dedupe, and limitations |
| [Server migration](https://docs.karakeep.app/administration/server-migration/) | Official server-to-server migration workflow and webhook-token caveat |

## Community evidence used only to define a test

| Source | Limited use |
|---|---|
| [Issue #2986](https://github.com/karakeep-app/karakeep/issues/2986) | A v0.33.1 reporter alleges duplicate API POST resets creation/modification timestamps. This is **not** treated as verified current behavior; it motivates the duplicate-provenance POC and the decision not to use `createdAt` as the sole sync cursor. `[COMMUNITY_REPORT]` |

No third-party review, vendor-comparison blog, or marketing aggregator was used as evidence for license, security, API, storage, release health, or architecture conclusions.
