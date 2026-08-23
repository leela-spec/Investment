# Independent Review — R1 Karakeep → IPOS

**Reviewer role:** independent of the R1 researcher  
**Review date:** 2026-08-23  
**IPOS pin reviewed:** `6353c1acb768d61a7be83477e1cc4fee55653d97`  
**Karakeep verification target:** tagged source/release `v0.33.2`; official docs currently labeled `v0.33.0`  
**Method:** launcher §7 and `METHOD-BASIS.md`

## Score

| Dimension | Score (0–2) | Review finding |
|---|---:|---|
| Repo grounding | 2 | Uses the effective pinned commit, identifies executable ETL/archive/DuckDB/snapshot/report/optional-narration boundaries, and explicitly excludes stale/unreconciled planning material. Spot checks against `PROJECT_STATE.md`, `ipos/etl/base.py`, `ipos/etl/pull.py`, `ipos/warehouse/migrations/001_init.sql`, and `tests/test_snapshot.py` support the gap analysis. |
| Factual grounding | 2 | Consequential product claims are supported by current official docs, tagged source, OpenAPI, release metadata, or a reproducible local CLI observation. Facts are separated from inference and unverified server behavior. |
| Citation accuracy | 2 | Spot-checked citations support the attached claims: license, Compose services/volumes, API authentication and cursor pagination, RSS polling/deduplication, rule/webhook surface, capture/media behavior, migration limits, security boundary, readable-content hash, and dump coverage. |
| Source quality | 2 | Relies almost entirely on official documentation, tagged Karakeep source/OpenAPI/release records, Docker's official Windows/licensing documentation, and the pinned IPOS repository. A community issue is used only to define an adversarial duplicate test. |
| Coverage | 2 | All four objective questions, every requested capability area, A/B/C canonical-role choice, capability classifications, seven named deliverables, MCDA, interface contracts, and POC requirements are addressed. JSON files parse and their inventories/totals reconcile. |
| Uncertainty | 2 | Live-server, recovery, duplicate provenance, webhook, permission, version-alignment, mutable-history, OCR/paywall, performance, licensing, and removal risks are explicit, bounded, and connected to closure tests. |
| Target alignment | 2 | Keeps Karakeep outside numeric scoring, Playbook promotion, DuckDB numeric truth, reporting, and AI narration. It recommends a removable read-only research sidecar rather than redesigning IPOS. |
| Reuse-first discipline | 2 | Reuses Karakeep's capture, archive, search, API and dump surfaces and rejects a custom bookmark manager, direct SQLite coupling, a new RAG stack, and unnecessary webhooks/MCP/AI in the first path. |
| POC integrity | 1 | The observed CLI install/schema and erroneous zero-exit network failure were independently reproduced. Docker/Podman absence is also reproducible, and the blocked server POC is honestly labeled. The next-test matrix is strong, but it is not fully immutable/reproducible yet because tagged Compose still references `karakeep-chrome:release`, and the second-instance/RSS setup is described rather than supplied as exact pinned configuration and request payloads. This does not invalidate the blocked-POC result or `TEST_FURTHER` verdict. |
| Efficiency | 2 | The work is decision-focused, uses one source ledger, avoids redundant landscape prose, and stops at evidence sufficient for the specified sidecar-versus-baseline decision. |

**Total: 19/20.** The mandatory dimensions (`repo_grounding`, `factual_grounding`, `citation_accuracy`, `coverage`) contain no zero. **Pass threshold met.**

## Major claims spot-checked

1. **Current IPOS boundary.** At the pin, `ipos/etl/base.py` writes one raw Parquet archive per pull date and replays the newest archive after total live-source failure; `ipos/etl/pull.py` validates/upserts observations with `vintage_id` and `source_hash`; migration `001_init.sql` separates observations, weekly canonicals, scores and aggregates; `tests/test_snapshot.py` verifies byte-identical snapshots and report rendering without an LLM. This supports the conclusion that Karakeep fills a research-artifact gap rather than a numeric-pipeline gap.
2. **Current release and maintenance.** Karakeep's official `v0.33.2` release is marked latest and dated 2026-08-11, with crawler/container fixes and 25 subsequent commits visible at review time. The maintenance characterization is reasonable and not based on stars.
3. **License and local deployment.** The tag contains the GNU Affero GPL v3 license. The tagged Compose file defines Karakeep web, Chrome and Meilisearch services, with persistent `/data` and `/meili_data` volumes; official Docker docs describe Compose self-hosting and version pinning. The report correctly treats Windows/Docker licensing and service overhead as operator/environment questions rather than free/local guarantees.
4. **API shape.** The `v0.33.2` OpenAPI file has 35 paths, bearer authentication, cursor pagination, three bookmark types, stable string IDs, `firstCreatedAt`/`createdAt`/`modifiedAt`, tags with `human|ai`, bookmark content/assets/highlights, URL checking, feeds and downloadable-backup endpoints. The proposed read-only polling boundary is supported by this schema.
5. **Readable-content contract.** Tagged `packages/trpc/models/bookmarks.ts` normalizes line endings, trims content, and computes `contentVersion` as SHA-256 over `format`, NUL and normalized content. The report's hash description is accurate.
6. **RSS/rules/webhooks/search.** Official docs state enabled RSS feeds are checked hourly and duplicates skipped; the rule engine can tag/favourite/route; bookmark added/updated/archived webhooks exist; and the documented query language supports tags/lists/source/date and full-text filtering. The choice to start with FTS plus polling is an architectural judgment clearly labeled as such.
7. **Export/migration limitations.** Tagged `dump.ts` exports account settings, lists, tags, rules, feeds, prompts, webhooks, bookmark metadata/content, membership and binary assets; no explicit highlight-export phase was found. Official migration documentation lists user settings, lists, feeds, prompts, webhooks, tags, rules and bookmarks, and warns webhook tokens are not migrated. The recovery caution is warranted.
8. **CLI POC.** Independent rerun on the same disposable environment returned CLI version `0.33.1`, exposed the documented command surface, and reproduced `Error: Failed to query bookmarks` with process exit `0` against `127.0.0.1:39999`. Neither Docker nor Podman is installed. The observed-versus-blocked labels are honest.

## Weak or unsupported claims

- **Full stack is not completely pinned.** `KARAKEEP_VERSION=0.33.2` pins the web image, but the fetched tagged Compose file still uses `ghcr.io/karakeep-app/karakeep-chrome:release`. A real adoption POC should resolve and record an immutable Chrome image digest (and preferably all image digests) before claiming byte-for-byte reproducibility.
- **Second-instance and RSS steps need executable detail before the adoption POC.** `POC_RESULTS.md` states the required behavior and acceptance criteria, but does not give the complete second Compose project override, port/volume names, RSS fixture server command, or exact `POST /feeds` request body. These are minor next-test packaging gaps, not unsupported product conclusions.
- **“Stable” IDs are schema-level identities, not an observed cross-restore guarantee.** The outputs appropriately require a URL/ID mapping comparison after migration; consumers must not assume a Karakeep ID survives server-to-server migration until observed.
- **Least-privilege API-key scope remains unverified.** The proposal already marks this uncertainty and must not represent a dedicated key as read-only unless the pinned UI/API proves enforceable scope.

## Missing requirements

None that blocks acceptance. Every prompt deliverable exists, and the launcher-required plan, source ledger, gaps file and track manifest exist. `MCDA.json`, `MACHINE_READABLE_DECISION.json`, and `TRACK-MANIFEST.json` are valid JSON; the two weighted MCDA totals recompute to `82.8` and `72.4`; the manifest output list is complete.

## Drift / overengineering findings

- No production code/config/scoring/Playbook changes are proposed or present.
- The proposed append-only evidence-event mirror is narrowly justified by Karakeep's mutable working records and portability uncertainty; it does not duplicate capture/search/dashboard behavior.
- Webhooks, semantic search, embeddings, MCP/skills, reverse sync, direct SQLite reads, and a new DuckDB evidence table are deferred or rejected for the first path. This is consistent with reuse-first and deterministic/local-first constraints.
- `data/research/karakeep/` is explicitly a proposed contract whose final location is deferred; it is not presented as an implemented production subsystem.

## Verdict

**ACCEPT**

R1 is sufficiently repo-grounded, primary-source-grounded, complete, and honest about the blocked live-server POC. Its recommendation remains appropriately conditional: `TEST_FURTHER` for an optional read-only Karakeep research sidecar, with no scoring or Playbook write path and with recovery/duplicate/isolation tests required before adoption.
