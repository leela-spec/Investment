# Disposable POC Results

## Verdict

**`PARTIAL_PASS / FUNCTIONAL_SERVER_POC_BLOCKED`.**

The environment permitted a disposable NPM execution of the official CLI, but it has no Docker or Podman runtime and no writable Karakeep server/API key. The prompt explicitly permits a blocked POC when the dependency and deterministic next test are recorded. No production machine or IPOS code was changed.

## Environment

- Date: 2026-08-23 UTC
- OS: ephemeral Linux sandbox
- Node: `v24.19.0`
- npm: `11.9.0`
- Docker: `command not found`
- Podman: `command not found`
- Karakeep CLI tested: `@karakeep/cli@0.33.1` (latest NPM version observed on 2026-08-23)
- Karakeep server: unavailable
- Test data: synthetic/non-sensitive only

## Executed tests

### CLI install and schema surface

Executed with a temporary cache:

```bash
poc_tmp=$(mktemp -d)
NPM_CONFIG_UPDATE_NOTIFIER=false npx --yes --cache "$poc_tmp/npm-cache" \
  @karakeep/cli@0.33.1 --help
```

Observed:

- exit `0`;
- commands include `bookmarks`, `lists`, `tags`, `highlights`, `assets`, `dump`, `migrate`, `whoami`;
- version command returned `0.33.1`;
- `bookmarks add` accepts repeated link/note/asset values plus list and tags;
- `bookmarks list` supports list/tag/feed filters, all-page pagination, JSON and included content;
- `bookmarks content` supports Markdown/text, cursor and max 50,000 characters;
- `dump` exposes account-data/content/assets export exclusions;
- `migrate` exposes destination server/key and granular exclusions.

Status: **PASS** `[POC_OBSERVED]`.

### Failure signaling

Executed:

```bash
NPM_CONFIG_UPDATE_NOTIFIER=false npx --yes --cache "$poc_tmp/npm-cache" \
  @karakeep/cli@0.33.1 \
  --server-addr http://127.0.0.1:39999 \
  --api-key synthetic-test-key --json \
  bookmarks list --limit 1
```

Observed output: `Error: Failed to query bookmarks`; observed process exit: **`0`**.

Status: **FAIL for scheduler-grade exit signaling** `[POC_OBSERVED]`.

Consequence: the proposed adapter uses REST directly and checks HTTP/body/schema. CLI remains an operator/export tool; any scripted CLI command must additionally validate output/artifact existence rather than trusting exit status.

## Blocked tests

| Required test | Status | Exact blocker |
|---|---|---|
| Start self-host server | BLOCKED | no Docker/Podman runtime in available disposable environment |
| Article/PDF/YouTube/note/RSS ingest | BLOCKED | no writable server/API key |
| Metadata/content/highlight retrieval | BLOCKED | no writable server/API key |
| Full-text search and tag/list assignment | BLOCKED | no running Meilisearch-backed server |
| Duplicate behavior | BLOCKED | no writable server; API contract/source verified only |
| Dump content verification | BLOCKED | no account dataset/server |
| Backup and clean restore | BLOCKED | needs two disposable server instances |

## Deterministic Windows POC

### 1. Prerequisites

- Supported Windows 10/11 with Docker Desktop using Linux containers/WSL2.
- PowerShell 7, Git, `curl.exe` and Python 3.12.
- Keep all files below a disposable directory; do not use production IPOS data.

### 2. Pin and start

```powershell
$PocRoot = Join-Path $env:TEMP 'ipos-karakeep-r1-poc'
New-Item -ItemType Directory -Force $PocRoot | Out-Null
Set-Location $PocRoot
curl.exe -L -o docker-compose.yml https://raw.githubusercontent.com/karakeep-app/karakeep/v0.33.2/docker/docker-compose.yml
$NextAuth = [Convert]::ToBase64String([Security.Cryptography.RandomNumberGenerator]::GetBytes(36))
$Meili = [Convert]::ToBase64String([Security.Cryptography.RandomNumberGenerator]::GetBytes(36))
@"
KARAKEEP_VERSION=0.33.2
NEXTAUTH_SECRET=$NextAuth
MEILI_MASTER_KEY=$Meili
NEXTAUTH_URL=http://localhost:3000
DISABLE_SIGNUPS=false
"@ | Set-Content -Encoding utf8 .env
docker compose up -d
docker compose ps
```

Create the first local user in `http://localhost:3000`, disable new signups, and create a dedicated test API key. This is the only interactive setup.

### 3. Synthetic fixtures

Create:

- `fixture-note.txt`: `Synthetic R1 research note; no investment advice.`
- `fixture-transcript.txt`: timestamped synthetic YouTube transcript text.
- `fixture.pdf`: one-page synthetic PDF generated locally.
- RSS feed containing one `https://example.com/ipos-r1-rss-item` entry.

Use non-sensitive representative links:

- web: `https://example.com/?ipos-r1=article`
- duplicate: submit that exact URL twice
- YouTube: `https://www.youtube.com/watch?v=jNQXAC9IVRw`, plus the synthetic transcript as a separate text bookmark whose `sourceUrl` equals the video URL

### 4. Ingest and organize

```powershell
$env:KARAKEEP_SERVER_ADDR = 'http://localhost:3000'
$env:KARAKEEP_API_KEY = '<TEST-ONLY-KEY>'
npx --yes @karakeep/cli@0.33.1 whoami
npx --yes @karakeep/cli@0.33.1 --json bookmarks add --link 'https://example.com/?ipos-r1=article' --tag-name 'ipos:status:new'
npx --yes @karakeep/cli@0.33.1 --json bookmarks add --asset .\fixture.pdf --tag-name 'ipos:status:new'
npx --yes @karakeep/cli@0.33.1 --json bookmarks add --link 'https://www.youtube.com/watch?v=jNQXAC9IVRw' --tag-name 'ipos:status:new'
Get-Content .\fixture-transcript.txt | npx --yes @karakeep/cli@0.33.1 --json bookmarks add --stdin --title 'Synthetic transcript' --tag-name 'ipos:status:new'
Get-Content .\fixture-note.txt | npx --yes @karakeep/cli@0.33.1 --json bookmarks add --stdin --title 'Synthetic research note' --tag-name 'ipos:status:new'
npx --yes @karakeep/cli@0.33.1 --json bookmarks add --link 'https://example.com/?ipos-r1=article' --tag-name 'ipos:status:new'
```

Add an RSS feed via the UI/API, trigger `POST /api/v1/feeds/{feedId}/fetch`, and wait for `lastFetchedStatus` to reach `success|failure` with a timestamp.

### 5. Verify

For every bookmark, save raw JSON from `bookmarks get`, retrieve all content chunks, and list highlights. Verify:

- one stable ID per exact duplicate URL;
- `firstCreatedAt`, `createdAt`, `modifiedAt`, `source`, URLs, tags and crawl status;
- PDF asset ID/file name/content;
- YouTube crawl/video asset result and failure state;
- FTS finds a unique synthetic phrase;
- list/tag/feed filters return expected IDs;
- content re-read produces the same `contentVersion`;
- resubmitting a duplicate does not unexpectedly change `firstCreatedAt`; record any `createdAt` change.

### 6. Export and recovery

```powershell
npx --yes @karakeep/cli@0.33.1 dump --output .\r1-dump.tar.gz
tar -tzf .\r1-dump.tar.gz | Sort-Object | Set-Content .\r1-dump-filelist.txt
Get-FileHash .\r1-dump.tar.gz -Algorithm SHA256
```

Start a second clean Compose project on port 3001 with separate named volumes, create a test account/key, and run:

```powershell
npx --yes @karakeep/cli@0.33.1 migrate --dest-server http://localhost:3001 --dest-api-key '<DEST-TEST-KEY>' --yes
```

Compare source/destination counts, URL-to-ID mapping, content hashes, tags, lists, highlights and downloaded PDF bytes. Record that webhook tokens require manual recreation.

### 7. Failure/retry and cleanup

- Stop Karakeep, run the adapter and verify it leaves prior mirror intact and returns nonzero.
- Restart; verify the same objects synchronize without duplicate events.
- Corrupt/revoke the test key; verify 401 is fatal and state is not advanced.
- Cleanup only the explicit POC project:

```powershell
docker compose down -v
Set-Location $env:TEMP
Remove-Item -Recurse -Force $PocRoot
```

## POC acceptance table

| Area | Pass criterion |
|---|---|
| Ingest | all six evidence cases create or intentionally dedupe with recorded IDs |
| Metadata | required identifiers/timestamps/source/status fields preserved |
| Retrieval | readable content and highlights are complete and repeatable |
| Search | unique phrases found by `fts` without embeddings |
| Duplicate | exact URL yields one object; original provenance remains reconstructible |
| Export | dump manifest/counts and binaries match live state |
| Recovery | clean destination matches selected source objects/hashes |
| Degraded mode | unavailable server cannot change core IPOS or prior mirror |
