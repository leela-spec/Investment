# Proposed Integration — Thin, Read-Only Karakeep Sidecar

## Architecture decision

**Pattern:** polling sidecar, not core connector; Karakeep remains optional and IPOS remains fully functional when it is down.

```text
external source / human note / RSS
→ Karakeep bookmark + assets + human curation
→ version-pinned REST read
→ append-only IPOS research-event mirror
→ isolated evidence view for later review
↛ numeric scoring / operational Playbook (no automatic path)
```

The first implementation should not use webhooks, MCP, an AI skill, semantic search, a new RAG stack or direct reads of Karakeep's SQLite database. REST polling is public, versionable, retryable and recoverable after downtime.

## Interface 1 — capture

**Input → process → output**

`URL | text note | PDF/image | RSS item`
→ Karakeep UI/browser/CLI/API/RSS
→ `bookmark.id` plus content/assets and human curation

Required capture conventions:

- Manual list: `IPOS Inbox`.
- Human tags only for control state:
  - `ipos:status:new|reviewed|rejected`
  - `ipos:module:<module_id>` using current `configs/modules.yaml` IDs
  - optional `ipos:source:<source_class>`
- Preserve the original URL in `content.url` or `content.sourceUrl`.
- Do not require AI tagging or embeddings.
- RSS rules may tag/route, but cannot mark evidence reviewed or promote rules.

Human control: source selection, notes, highlights, tags, list membership, review/rejection.

## Interface 2 — discovery and metadata pull

**Input → process → output**

`KARAKEEP_BASE_URL + secret API key + list/tag selection`
→ `GET /api/v1/bookmarks` with cursor pagination and `includeContent=false`
→ normalized bookmark envelope

Minimum envelope schema:

```json
{
  "schema_version": "ipos.karakeep.evidence-event/1",
  "karakeep_instance_id": "operator-configured-stable-id",
  "karakeep_bookmark_id": "string",
  "bookmark_type": "link|text|asset",
  "first_created_at": "ISO-8601|null",
  "created_at": "ISO-8601",
  "modified_at": "ISO-8601|null",
  "source_channel": "api|web|cli|mobile|extension|singlefile|rss|import|null",
  "source_url": "string|null",
  "title": "string|null",
  "note": "string|null",
  "summary": "string|null",
  "human_tags": ["string"],
  "ai_tags": ["string"],
  "crawl_status": "success|failure|pending|null",
  "crawled_at": "ISO-8601|null",
  "date_published": "ISO-8601|null",
  "date_modified": "ISO-8601|null",
  "asset_manifest": [{"id":"string","type":"string","file_name":"string|null"}],
  "retrieved_at": "ISO-8601",
  "adapter_version": "string"
}
```

Do not use `createdAt` as a high-water mark: current releases intentionally bump re-saved bookmarks and an open 0.33.1 report alleges API duplicate submission may reset dates. Re-scan the bounded `IPOS Inbox`/selected tag set each run and deduplicate locally by stable ID plus hashes. `[INFERENCE]`

## Interface 3 — content, highlights and assets

**Input → process → output**

`karakeep_bookmark_id`
→ `GET /api/v1/bookmarks/{id}/content?format=markdown&maxChars=50000` until `nextCursor=null`
→ normalized `content.md` and official `contentVersion`

`karakeep_bookmark_id`
→ `GET /api/v1/bookmarks/{id}/highlights`
→ `highlights.json`

`asset_manifest`
→ retain IDs/metadata by default; download only evidence-bearing original PDF/image/full-page archive required by retention policy
→ binary artifact plus local SHA-256

Hash contract:

- `content_version`: return value from Karakeep; [tagged source](https://github.com/karakeep-app/karakeep/blob/v0.33.2/packages/trpc/models/bookmarks.ts) defines it as SHA-256 over format, NUL, normalized content. `[VERIFIED_PRIMARY]`
- `metadata_sha256`: SHA-256 of canonical JSON (UTF-8, sorted keys, compact separators) excluding volatile `retrieved_at`.
- `artifact_sha256`: SHA-256 of exact downloaded bytes.
- `event_id`: `sha256(instance_id + NUL + bookmark_id + NUL + content_version + NUL + metadata_sha256)`.

## Interface 4 — append-only mirror

**Input → process → output**

`normalized envelope + content/highlights/artifacts`
→ validate schema, hash, write temp files, atomically rename
→ append-only version directory and one index event

Proposed non-production contract (final path to be chosen during implementation):

```text
data/research/karakeep/
  state.json
  events.jsonl
  objects/<bookmark_id>/<event_id>/
    bookmark.json
    content.md
    highlights.json
    assets.json
    files/<asset_id>
```

`data/` is already the project's gitignored runtime-artifact root. No change to numerical tables is required for the first useful version. A read-only DuckDB evidence view may be added later only if queries justify it.

## Interface 5 — backup and recovery

**Input → process → output**

`live Karakeep account`
→ `karakeep dump --output <dated>.tar.gz`
→ portable manifest + JSON/JSONL + assets

`pinned Compose bind mounts`
→ quiesced filesystem backup of Karakeep `/data` plus configuration/secrets backup and optional Meilisearch volume snapshot
→ service recovery point

`source instance + clean destination instance`
→ `karakeep migrate --dest-server ... --dest-api-key ...`
→ behavioral restore verification

The API backup/download feature or CLI dump is not considered a proven restore until a clean-instance migration is compared by counts, IDs/URL mapping, content hashes, tags/lists/highlights and assets. The official [server migration guide](https://docs.karakeep.app/administration/server-migration/) says webhook tokens must be re-entered after migration. `[VERIFIED_PRIMARY]`

## Retry and idempotency

- HTTP timeouts: connect 10 s, read 60 s; bounded retries for 408/429/5xx and network errors at 1/2/4 seconds plus jitter.
- Do not retry 400/401/403/404 blindly.
- Before create operations in any future reverse sync, call `GET /bookmarks/check-url`; first adapter version is read-only and has no create path.
- Re-reading the same object version produces the same `event_id`; existing directories/events are a no-op.
- A changed metadata or content hash creates a new immutable event; prior versions remain.
- Update `state.json.last_successful_sync_at` only after every selected page/object has validated and committed.

## Failure behavior

| Failure | Required behavior |
|---|---|
| Karakeep unreachable | Preserve prior mirror, write explicit failed-run log, mark evidence view stale; weekly IPOS continues |
| 401/403 | Stop immediately; surface credential/scope failure; no partial success marker |
| Bookmark crawl `pending` | Record metadata/status; retry content in later run; never treat empty content as complete |
| Bookmark crawl `failure` / broken link | Preserve failure metadata and any assets; do not fabricate text |
| One asset fails | Commit no complete event unless event records the missing asset as an explicit failure; retry later |
| Schema drift | Quarantine raw response, fail adapter visibly; do not coerce unknown fields into old meanings |
| Duplicate URL | Reuse stable Karakeep ID; append only if content/metadata version changed |
| Karakeep entirely removed | Existing mirrored events remain readable; core IPOS is unaffected |

## Security and authentication

- Bind web UI to localhost/Tailscale/private LAN only; never expose it publicly for this use case.
- Keep the crawler restricted to trusted operator input. Karakeep's own security guide warns that untrusted crawler users can induce requests from the host network; built-in SSRF protection is explicitly partial. [Security guidance](https://docs.karakeep.app/administration/security-considerations/) `[VERIFIED_PRIMARY]`
- Store API key outside Git (`.env`/Windows credential mechanism); use a dedicated least-privilege key if current UI scopes permit it.
- Never send private portfolio data to Karakeep; this integration handles research evidence only.

## What remains human-controlled

- saving/selecting sources;
- status and module tags;
- highlights and notes;
- accepting/rejecting evidence;
- any promotion into operational Playbook/configs;
- any architecture/version upgrade;
- recovery validation and secret rotation.

## Acceptance tests before production adoption

1. Full POC matrix in `POC_RESULTS.md` passes.
2. Repeated identical poll is byte/idempotency stable.
3. Duplicate URL does not corrupt original provenance in the chosen pinned release.
4. Dump archive contents match live counts/hashes.
5. Clean destination migration restores selected objects and assets.
6. Karakeep shutdown leaves `ipos-weekly` and existing reports green.
7. Golden snapshot remains byte-identical; no scoring/config/Playbook file is touched.
