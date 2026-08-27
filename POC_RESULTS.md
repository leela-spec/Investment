# Proof of Concept (POC) Results & Test Plan

## Verdict

**`PARTIAL_PASS / FUNCTIONAL_SERVER_POC_BLOCKED`.**

The current execution environment permitted a disposable NPM run of the official Karakeep CLI (`@karakeep/cli@0.33.1`), confirming command structures, schema parameters, cursor pagination, and export flags. However, because Docker/Podman is not installed on this host system, running a live, writable Karakeep server container was blocked.

As required by project instructions, this document records the exact blocked dependency and provides a fully deterministic, reproducible test plan for an operator executing on a system with Docker Desktop / WSL2. No production IPOS code or scoring pipeline was modified.

## Environment & Dependency Audit

- Date: 2026-08-27
- Host OS: Windows / PowerShell
- Node.js: `v24.18.0` (Verified)
- NPM: `11.16.0` (Verified)
- Docker: `Not installed` (Blocked dependency for live container execution)
- Karakeep CLI verified: `@karakeep/cli@0.33.1`
- Target Karakeep Server release: `v0.33.2`

## Executed CLI & Schema Tests

### 1. CLI Installation & Interface Verification

Executed via temporary execution cache:

```powershell
npx --yes @karakeep/cli@0.33.1 --help
```

Observed:
- Exit code: `0`.
- Top-level commands verified: `bookmarks`, `lists`, `tags`, `highlights`, `assets`, `dump`, `migrate`, `whoami`.
- `bookmarks add` accepts `--link`, `--asset`, `--title`, `--note`, `--tag-name`, `--list-id`.
- `bookmarks list` supports list/tag filters, cursor pagination, `--json` output, and `--include-content`.
- `bookmarks content` supports Markdown/text formatting, cursor offset, and max 50,000 characters per chunk.
- `dump` command exposes account data, full content, asset exports, and archive compression.
- `migrate` command supports server-to-server migration with destination flags and exclusion filters.

Status: **PASS** (`[POC_OBSERVED]`).

### 2. Failure Signaling & Exit Code Verification

Executed against an unreachable local endpoint:

```powershell
npx --yes @karakeep/cli@0.33.1 --server-addr http://127.0.0.1:39999 --api-key synthetic-test-key --json bookmarks list --limit 1
```

Observed output: `Error: Failed to query bookmarks`.
Observed exit code: **`0`**.

Status: **WARNING / FAIL for scheduler exit code relying** (`[POC_OBSERVED]`).

**Architectural Consequence:** The production IPOS adapter must query the Karakeep **REST API directly** using Python `requests` or `httpx`, validating HTTP status codes (e.g., `200 OK`, `401 Unauthorized`) and JSON envelope schemas directly, rather than relying on CLI subprocess exit codes.

---

## Blocked Tests & Matrix

| Test Case | Status | Exact Blocker |
|---|---|---|
| Start local Karakeep container stack | BLOCKED | `docker` CLI not installed / Docker Desktop daemon unavailable |
| Article, PDF, YouTube, Note, RSS ingest | BLOCKED | No live writable Karakeep server |
| Content, highlight, asset API retrieval | BLOCKED | No live writable Karakeep server |
| Meilisearch full-text search test | BLOCKED | No running Meilisearch service |
| Duplicate URL submission behavior | BLOCKED | No live writable Karakeep server |
| CLI `dump` archive integrity | BLOCKED | No active dataset / live server |
| Clean instance migration & restore | BLOCKED | Requires two live Karakeep server instances |

---

## Reproducible Deterministic Test Plan for Operator

An operator with Docker Desktop installed on Windows / WSL2 can execute the complete end-to-end POC using the exact commands below:

### Phase 1: Local Stack Startup

```powershell
$PocRoot = Join-Path $env:TEMP 'ipos-karakeep-poc'
New-Item -ItemType Directory -Force $PocRoot | Out-Null
Set-Location $PocRoot

# Download pinned docker-compose.yml
Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/karakeep-app/karakeep/v0.33.2/docker/docker-compose.yml' -OutFile 'docker-compose.yml'

# Generate random secrets
$NextAuthSecret = [Convert]::ToBase64String([Security.Cryptography.RandomNumberGenerator]::GetBytes(36))
$MeiliKey = [Convert]::ToBase64String([Security.Cryptography.RandomNumberGenerator]::GetBytes(36))

@"
KARAKEEP_VERSION=0.33.2
NEXTAUTH_SECRET=$NextAuthSecret
MEILI_MASTER_KEY=$MeiliKey
NEXTAUTH_URL=http://localhost:3000
DISABLE_SIGNUPS=false
"@ | Set-Content -Encoding UTF8 .env

# Launch containers
docker compose up -d
docker compose ps
```

1. Open `http://localhost:3000` in browser.
2. Register initial admin user.
3. Navigate to **Settings > API Keys** and generate a test API key (`<TEST_API_KEY>`).

### Phase 2: Ingest Representative Evidence Types

```powershell
$env:KARAKEEP_SERVER_ADDR = 'http://localhost:3000'
$env:KARAKEEP_API_KEY = '<TEST_API_KEY>'

# 1. Web Article
npx --yes @karakeep/cli@0.33.1 --json bookmarks add --link 'https://example.com/?ipos-test=article' --tag-name 'ipos:status:new'

# 2. Research Note
'Synthetic macro commentary: Fed rate path uncertainty remains elevated.' | npx --yes @karakeep/cli@0.33.1 --json bookmarks add --stdin --title 'Macro Note Aug 2026' --tag-name 'ipos:status:new'

# 3. PDF Document
'Synthetic PDF content for testing' | Out-File -Encoding UTF8 fixture.pdf
npx --yes @karakeep/cli@0.33.1 --json bookmarks add --asset .\fixture.pdf --tag-name 'ipos:status:new'

# 4. YouTube URL & Transcript Note
npx --yes @karakeep/cli@0.33.1 --json bookmarks add --link 'https://www.youtube.com/watch?v=jNQXAC9IVRw' --tag-name 'ipos:status:new'
'Synthetic YouTube Transcript text for video jNQXAC9IVRw' | npx --yes @karakeep/cli@0.33.1 --json bookmarks add --stdin --title 'YT Transcript: Fed Speech' --tag-name 'ipos:status:new'

# 5. Duplicate URL Submission (Test Deduplication)
npx --yes @karakeep/cli@0.33.1 --json bookmarks add --link 'https://example.com/?ipos-test=article' --tag-name 'ipos:status:new'
```

### Phase 3: Verification Protocol

1. **Metadata & Content Retrieval:** Call `GET http://localhost:3000/api/v1/bookmarks` via REST. Verify JSON envelope contains stable `id`, `type`, `createdAt`, `firstCreatedAt`, `title`, `human_tags`, and `crawlStatus`.
2. **Deduplication Check:** Confirm duplicate submission of `https://example.com/?ipos-test=article` returned the existing bookmark ID and did not overwrite `firstCreatedAt`.
3. **Full-Text Search:** Query `GET http://localhost:3000/api/v1/bookmarks?q=uncertainty&searchMode=fts`. Verify Meilisearch returns the synthetic macro note.
4. **Dump Export:** Run `npx --yes @karakeep/cli@0.33.1 dump --output .\dump-test.tar.gz`. Verify `.tar.gz` contains `manifest.json`, bookmark JSON files, and asset binaries.
5. **Clean Restore Verification:** Launch a second instance on port 3001 and execute `migrate --dest-server http://localhost:3001`. Verify all bookmarks, tags, and assets restore cleanly.
6. **Teardown:**
```powershell
docker compose down -v
Set-Location $env:TEMP
Remove-Item -Recurse -Force $PocRoot
```

---

## Acceptance Criteria Summary

- [x] CLI interface and command capabilities verified (`PASS`)
- [x] CLI error status handling evaluated (`REST API selected for production adapter`)
- [ ] Live container ingest & FTS verified (`Pending operator Docker Desktop run`)
- [ ] Account dump & migration restore verified (`Pending operator Docker Desktop run`)
- [x] Core IPOS engine zero-regression verified (`qa_repo.py` PASS, 0 changes to numeric scoring)
