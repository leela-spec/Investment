# Gaps and Uncertainties

These items are deliberately excluded from unconditional production claims. None changes the recommendation to test Karakeep as an optional sidecar; the blocking items prevent production adoption until resolved.

## Blocking before production adoption

| Gap | Evidence status | Why it matters | Deterministic closure test |
|---|---|---|---|
| No live Karakeep server POC ran in this environment | `[UNVERIFIED]` — Docker and Podman were absent; no server/API key was available | Ingest, crawl, search, duplicate, export, and recovery behavior remain schema/documentation evidence rather than end-to-end observation | Run the pinned Compose matrix in `POC_RESULTS.md` on Windows Docker Desktop using only its six synthetic fixtures; retain commands, HTTP responses, hashes, and counts |
| Clean-instance recovery not proven | `[UNVERIFIED]` | A downloadable backup or dump is not proof that the operator can recover service and evidence | Restore/migrate to an empty pinned instance; compare URLs/IDs or mapping, metadata, content hashes, tags, lists, highlights, and asset hashes |
| Portable dump/migration does not explicitly enumerate highlights in [tagged CLI source](https://github.com/karakeep-app/karakeep/blob/v0.33.2/apps/cli/src/commands/dump.ts) | `[VERIFIED_PRIMARY]` for source inspection; recovery effect `[UNVERIFIED]` | Highlights are required evidence objects, but `dump.ts` has no explicit highlight-export phase and official migration coverage does not explicitly promise them | Create two highlights, dump and migrate, inspect archive and destination via highlights API; retain database-level backup if portable path omits them |
| Duplicate URL timestamp/provenance behavior on v0.33.2 not reproduced | `[COMMUNITY_REPORT]` only for alleged v0.33.1 behavior | Resetting `createdAt`/`modifiedAt` could break cursoring and original provenance | POST the same synthetic URL twice; compare status, ID, `firstCreatedAt`, `createdAt`, `modifiedAt`, source, tags, and readable-content version |
| Removal/degraded-mode isolation not executed | `[UNVERIFIED]` | Optional-sidecar safety requires the existing weekly IPOS path to remain byte/stage stable during outage | Record golden snapshot/report, stop Karakeep and revoke key, run existing IPOS tests/weekly command, compare outputs and verify explicit stale adapter status |

## Important non-blocking uncertainties

| Uncertainty | Current treatment | Closure |
|---|---|---|
| Exact API-key permission granularity | Assume bearer authentication, but do not claim least privilege is available | Inspect v0.33.2 UI/API-key model and create the narrowest read-only key if supported; otherwise document broader authority and compensating controls |
| Server/CLI patch-version alignment | Server release `v0.33.2` is current while latest NPM CLI observed is `0.33.1` | Run the full POC with that exact pairing and pin both independently; do not assume identical release cadence |
| Webhook delivery, ordering, signature, retry, and replay semantics | Do not use webhooks in version 1 | Fault-inject a disposable receiver before considering event-driven sync |
| Backup ZIP contents and a direct restore procedure | Treat API backup as a recovery artifact, not a portable restore guarantee | Inspect ZIP manifest and execute clean restore; document exact procedure |
| Mutable page recrawl history | Assume Karakeep retains current state, not an immutable revision log; append each observed hash in IPOS mirror | Change a synthetic page twice, recrawl, and inspect API/database/export history |
| YouTube transcript availability | Do not claim first-class transcript extraction; store URL and any separately supplied transcript artifact | Test a public synthetic/non-sensitive video and compare page text, media archive, metadata, and explicitly uploaded transcript note/file |
| OCR and PDF text quality | Capability exists, accuracy is workload-dependent | Test born-digital, scanned, multi-column, and image-only PDFs; retain originals and extraction-status metadata |
| Paywall/login/bot-protected page capture | Not guaranteed | Test representative operator-approved sites; record failure rather than fabricate content |
| Search-index recovery | Treat Meilisearch as rebuildable but not yet time-bounded | Delete only the disposable search volume, rebuild, measure duration and result parity |
| Disk/CPU footprint at expected evidence volume | Not measured | Load a representative synthetic corpus and record steady-state volumes, crawl backlog, latency, and backup size |
| Smart-list/query stability across upgrades | Useful view only, never ingestion authority | Pin release; regression-test saved queries before upgrades |
| Docker Desktop licensing applicability | Operator decision | Apply Docker's official license terms to the actual organization/use or select a permitted container runtime |
| AGPL obligations for future adapter/deployment choices | Architecture/legal review if Karakeep is modified or exposed over a network | Keep initial adapter separate and unmodified; obtain qualified review before redistribution or source modifications |

## Scope deliberately deferred

- No evidence has established a need for semantic/hybrid search, embeddings, MCP, agentic skills, or a new RAG stack.
- No newly captured prose may modify scoring, configs, or Playbook rules automatically.
- No reverse sync from IPOS to Karakeep is required for the first useful release.
- No direct read of Karakeep's SQLite database is proposed; it would couple IPOS to private schema.
- Karakeep is not evaluated here as a portfolio ledger, market-data warehouse, trade engine, or weekly-report replacement.

## Confidence statement

Confidence is **high** in product/interface fit from tagged source and schema inspection, **medium** in operational fit, and **low** in recovery completeness until the live POC closes the blocking rows. The decision is therefore `TEST_FURTHER`, not unconditional adoption.
