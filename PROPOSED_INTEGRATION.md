# Proposed Integration Specification — Thin, Read-Only Karakeep Sidecar

## Architecture Overview

**Integration Pattern:** Polling, read-only REST sidecar adapter. Karakeep remains strictly optional; core IPOS is 100% functional and green when Karakeep is offline or removed.

```text
External Source (Web / PDF / YouTube / RSS / Note)
   │
   ▼
[ Karakeep App ] ◄── Human Curation (UI / Extension / Mobile / RSS Rules)
   │               (List: "IPOS Inbox", Tags: ipos:status:reviewed, ipos:module:<id>)
   │
   ▼ (Scheduled REST API Poll: GET /api/v1/bookmarks)
[ IPOS Karakeep Adapter ]
   │
   ├─ Verification: SHA-256 contentVersion, metadata SHA-256
   ├─ Schema Validation: ipos.karakeep.evidence-event/1
   │
   ▼
[ Append-Only IPOS Mirror ] ──► data/research/karakeep/
   │                               ├── state.json
   │                               ├── events.jsonl
   │                               └── objects/<bookmark_id>/<event_id>/
   │
   ❌ (STRICT BOUNDARY: NEVER WRITES TO)
   ├── DuckDB warehouse.duckdb (fact_weekly, fact_score, agg_*)
   ├── Operational Playbook (04_playbook/modules/*)
   └── Scoring Configs (configs/*)
```

The integration avoids webhooks, direct SQLite database file access, automatic Playbook rule promotion, or embedding vector stores. Polling REST endpoints provides a public, versionable, retryable, and recoverable boundary.

---

## Detailed Boundary Specifications

### Interface 1: Human Ingest & Curation Boundary

**Input → Process → Output:**

`URL / PDF / Note / RSS Feed`
→ Karakeep UI / Extension / Mobile / RSS Ingestion
→ `bookmark.id` + Crawled Assets + Human Tags

**Operating Conventions:**
- **List Scope:** Manual list `IPOS Inbox`.
- **Tag Conventions:**
  - `ipos:status:new` — Newly ingested, awaiting operator review.
  - `ipos:status:reviewed` — Reviewed by operator; eligible for IPOS mirror sync.
  - `ipos:status:rejected` — Ignored by IPOS adapter.
  - `ipos:module:<module_id>` — Target module tag (e.g. `ipos:module:EquityRisk`, `ipos:module:RatesYieldCurve`).
- **Human Authority:** The human operator retains 100% control over tag assignment, notes, highlights, and review status.

---

### Interface 2: Metadata & Envelope Discovery Boundary

**Input → Process → Output:**

`KARAKEEP_BASE_URL + API Key + Tag Filter (ipos:status:reviewed)`
→ `GET /api/v1/bookmarks?includeContent=false` (Cursor paginated)
→ Normalized Evidence Envelope (`ipos.karakeep.evidence-event/1`)

**Normalized Envelope JSON Schema (`ipos.karakeep.evidence-event/1`):**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "IPOSKarakeepEvidenceEnvelope",
  "type": "object",
  "properties": {
    "schema_version": { "type": "string", "const": "ipos.karakeep.evidence-event/1" },
    "karakeep_instance_id": { "type": "string" },
    "karakeep_bookmark_id": { "type": "string" },
    "bookmark_type": { "type": "string", "enum": ["link", "text", "asset"] },
    "first_created_at": { "type": ["string", "null"] },
    "created_at": { "type": "string" },
    "modified_at": { "type": ["string", "null"] },
    "source_channel": { "type": ["string", "null"] },
    "source_url": { "type": ["string", "null"] },
    "title": { "type": ["string", "null"] },
    "note": { "type": ["string", "null"] },
    "summary": { "type": ["string", "null"] },
    "human_tags": { "type": "array", "items": { "type": "string" } },
    "ai_tags": { "type": "array", "items": { "type": "string" } },
    "crawl_status": { "type": ["string", "null"], "enum": ["success", "failure", "pending", null] },
    "crawled_at": { "type": ["string", "null"] },
    "date_published": { "type": ["string", "null"] },
    "asset_manifest": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "string" },
          "type": { "type": "string" },
          "file_name": { "type": ["string", "null"] }
        },
        "required": ["id", "type"]
      }
    },
    "content_version": { "type": "string" },
    "metadata_sha256": { "type": "string" },
    "event_id": { "type": "string" },
    "retrieved_at": { "type": "string" },
    "adapter_version": { "type": "string" }
  },
  "required": [
    "schema_version",
    "karakeep_instance_id",
    "karakeep_bookmark_id",
    "bookmark_type",
    "created_at",
    "human_tags",
    "content_version",
    "metadata_sha256",
    "event_id",
    "retrieved_at"
  ]
}
```

---

### Interface 3: Content, Highlights & Asset Ingestion Boundary

**Input → Process → Output:**

`karakeep_bookmark_id`
→ `GET /api/v1/bookmarks/{id}/content?format=markdown&maxChars=50000` (Cursor paginated)
→ Normalized `content.md` + official Karakeep `contentVersion`

`karakeep_bookmark_id`
→ `GET /api/v1/bookmarks/{id}/highlights`
→ `highlights.json`

`asset_id`
→ `GET /api/v1/assets/{id}`
→ Binary asset file + local SHA-256 validation

**Hash & Identifier Contracts:**
- `content_version`: Returned directly by Karakeep (`SHA-256(format + \0 + normalized_content)`).
- `metadata_sha256`: `SHA-256` of canonical JSON envelope (excluding volatile `retrieved_at`).
- `artifact_sha256`: `SHA-256` of downloaded binary bytes.
- `event_id`: `SHA-256(instance_id + \0 + bookmark_id + \0 + content_version + \0 + metadata_sha256)`.

---

### Interface 4: Append-Only Local Storage Boundary

**Directory Layout (`data/research/karakeep/`):**

```text
data/research/karakeep/
├── state.json                              # High-water mark & last sync metadata
├── events.jsonl                            # Append-only stream of all evidence events
└── objects/
    └── <karakeep_bookmark_id>/
        └── <event_id>/
            ├── envelope.json               # Full metadata envelope
            ├── content.md                  # Markdown text content
            ├── highlights.json             # Associated text highlights
            ├── assets.json                 # Asset manifest
            └── files/
                └── <asset_id>              # Raw PDF / Image / Media files
```

---

### Retry & Idempotency Rules

1. **HTTP Retries:** Connect timeout = 10s, Read timeout = 60s. Exponential backoff for `408`, `429`, `5xx` (1s, 2s, 4s + jitter, max 3 retries).
2. **Fatal Errors:** Immediate fail on `401 Unauthorized`, `403 Forbidden`, `404 Not Found`.
3. **Idempotency Guarantee:** Re-polling an unchanged object produces an identical `event_id`. Duplicate writes to existing `objects/<bookmark_id>/<event_id>/` directories are skipped (no-op).
4. **State Commit:** `state.json` (`last_successful_sync_at`) is updated ONLY after all envelope, content, highlight, and asset writes for a poll batch complete and validate cleanly.

---

### Failure Behavior & Degraded Modes

| Failure Condition | System Behavior | Impact on Core IPOS |
|---|---|---|
| Karakeep server offline / down | Log warning; retain prior local mirror; skip evidence sync | ZERO. `ipos-weekly` and reports run 100% normally |
| `401 Unauthorized` (bad API key) | Halt adapter immediately; write alarm log | ZERO. Core IPOS unaffected |
| Bookmark crawl `pending` | Record metadata envelope; retry content pull in next weekly run | ZERO |
| Bookmark crawl `failure` | Record crawl status `failure`; retain URL and note | ZERO |
| Asset download fails | Do NOT commit complete event; retry asset download next run | ZERO |
| Karakeep removed permanently | Local mirror `data/research/karakeep/` remains fully readable | ZERO. Core IPOS unaffected |

---

### Security & Authentication Controls

1. **Network Binding:** Karakeep Web UI bound strictly to `localhost` (`127.0.0.1`) or private LAN/Tailscale VPN. Never exposed to public internet.
2. **API Secret Management:** API key read from `.env` (`KARAKEEP_API_KEY`) or Windows Credential Manager. Never hardcoded or committed to Git.
3. **Data Scope Isolation:** Private portfolio holdings, broker CSVs, and API credentials are NEVER sent to Karakeep.

---

### Acceptance Criteria Before Production Adoption

1. All POC test cases in `POC_RESULTS.md` pass on Docker Desktop host.
2. Repeated identical polling runs produce 0 duplicate event directories (idempotency verified).
3. Karakeep server shutdown verified: `python ipos/run.py` completes cleanly with zero errors.
4. `python scripts/qa_repo.py` passes 100% green; `snapshot.json` and Plotly HTML report remain byte-identical.
