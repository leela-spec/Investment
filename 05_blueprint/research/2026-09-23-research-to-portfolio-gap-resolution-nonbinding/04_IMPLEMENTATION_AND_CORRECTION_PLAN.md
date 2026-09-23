# Implementation and correction plan

**Scope:** repository `leela-spec/Investment`, `main` only. The chat made no remote writes. CLI applies surgical patches; it must not reconstruct or replace whole existing files from this narrative.

**Order:** source alignment and safety -> native ownership/publication -> broker/C12 reconciliation -> research extraction/custody -> policy/action integration and operational acceptance. No product benchmark program, database migration or community-stack rewrite is required.

## Phase 0 - Establish the real main state and apply the bounded correction

Owner: Windows CLI operator/agent. Prerequisite: package extracted locally; actual checkout path verified. The following PowerShell is deliberately strict: it stops instead of resetting a more recent local checkout to the audit's older reference. Replace `$Package` with the extraction directory; no other semantic edits are required.

```powershell
$ErrorActionPreference = 'Stop'
$Repo = 'C:\GitDev\Investment'
$Package = Join-Path $env:USERPROFILE 'Downloads\IPOS_Process_Verification_Gap_Resolution_2026-09-23'
Set-Location $Repo
if ((git branch --show-current).Trim() -ne 'main') {
    throw 'Use the existing main checkout; do not switch or create branches automatically.'
}
git fetch origin main
if ($LASTEXITCODE -ne 0) { throw 'Fetch failed.' }
$Pin = 'cec42be2aaf922c74ea6b13dc44fe11adfdd618f'
$Head = (git rev-parse HEAD).Trim()
$Remote = (git rev-parse origin/main).Trim()
git status --short
if ($Head -ne $Pin -or $Remote -ne $Pin) {
    throw 'Source state differs. Re-ground affected files and refresh the patch; never reset to the audit pin.'
}
if (git status --porcelain) { throw 'Preserve existing work; do not apply into a dirty tree.' }
$Expected = @{
    'ipos/etl/portfolio_csv.py' = '1ceec565aa070d9a03a5c49cdeaff12c204110e8'
    'ipos/aggregate/portfolio.py' = 'f294f551281e36536250486416c8b24a157c1e07'
}
foreach ($Path in $Expected.Keys) {
    $Actual = (git rev-parse ('HEAD:' + $Path)).Trim()
    if ($Actual -ne $Expected[$Path]) { throw "Unexpected source blob: $Path" }
}
$Patch = Join-Path $Package '05_SURGICAL_PATCHES.diff'
git apply --check --whitespace=error-all $Patch
if ($LASTEXITCODE -ne 0) { throw 'Patch check failed; do not use --reject or fuzzy replacement.' }
git apply --whitespace=error-all $Patch
if ($LASTEXITCODE -ne 0) { throw 'Patch application failed.' }
git diff --check
if ($LASTEXITCODE -ne 0) { throw 'Whitespace check failed.' }
$Py = Join-Path $Repo '.venv\Scripts\python.exe'
if (-not (Test-Path $Py)) { throw 'Use the verified native Windows project environment; do not install arbitrary latest dependencies.' }
& $Py -c 'import os,sys; print(sys.executable); assert os.name == "nt"'
if ($LASTEXITCODE -ne 0) { throw 'Not the required native Windows interpreter.' }
& $Py -m pytest -q tests/test_portfolio_audit_boundary.py tests/test_portfolio.py tests/test_regime.py
if ($LASTEXITCODE -ne 0) { throw 'Regression failed: inspect, do not weaken expected results.' }
git diff --stat
```

The test file is new, so `git diff --stat` alone will not list it until staged; inspect `git status --short` as well. Complete repository tests must run before declaring production compatibility. The safety patch modifies only two existing modules and adds one regression test file. It does not implement FIFO, change the optimizer, install external products, or authorize trades.

**If the preflight stops:** inspect only the named missing sources and affected modules in the operator's actual main checkout. Record `HEAD`, `origin/main`, missing/present paths and test results. If files exist only locally, preserve them; do not upload private data or assume a force push. Bring the selected current main state into the audit authority and regenerate exact hunks against it. Do not rewrite the older two files on top of a modern implementation. The missing normalizer/optimizer/runbooks are a source-resolution gate, not a request to invent replacements.

After successful review/tests, stage only the three patch paths, commit on main, and push without force:

```powershell
git add -- ipos/etl/portfolio_csv.py ipos/aggregate/portfolio.py tests/test_portfolio_audit_boundary.py
git diff --cached --check
git diff --cached --stat
git commit -m 'Reject incomplete holdings and unresolved FX before EUR aggregation'
if ($LASTEXITCODE -ne 0) { throw 'Commit failed.' }
git push origin main
if ($LASTEXITCODE -ne 0) { throw 'Push failed; preserve the local commit and reconcile, never force.' }
```

Persist this package, without overwriting older material, under proposed folder `05_blueprint/research/2026-09-23-research-to-portfolio-gap-resolution/`. Existing decision and runbook amendments must be supplied as subsequent exact patches once their current content is known. The proposed destination is not claimed to exist remotely.

**Recovery:** before a commit, `git apply --reverse --check $Patch` and then `git apply --reverse $Patch` undo only these hunks if they remain unchanged. After a committed deployment, use `git revert <the-actual-correction-commit>` on main with tests; never `reset --hard`, forced checkout, bulk file replacement, or history rewriting. Do not revert unrelated later work.

## Phase 1 - Native ownership, immutable publication and two-way transfer

Owner: host runtime integrator. Target existing `ipos/run.py` and `ipos/export/snapshot.py`; infrastructure/WF05/WF06/WF07 amendments require recovered source first. [R8] [R9]

### 1A. Non-mutating host inventory

Run on Windows, before modifying any scheduler, Docker or SSH settings:

```powershell
wsl.exe --list --verbose
Get-Command python,ssh,sftp,docker -ErrorAction SilentlyContinue | Select-Object Name,Source
Get-NetTCPConnection -State Listen | Where-Object {
    $_.LocalPort -in @(2222,8084,8082,8010,8086)
} | Select-Object LocalAddress,LocalPort,OwningProcess
Get-ScheduledTask | Where-Object TaskName -Match 'IPOS' |
    Select-Object TaskPath,TaskName,State
docker context show
docker ps --format '{{.ID}} {{.Names}} {{.Image}} {{.Ports}}'
```

Then inspect the known Ubuntu environment, without entering excluded data directories:

```powershell
wsl.exe -d Ubuntu -- sh -lc 'printf "HOME=%s\n" "$HOME"; findmnt -T "$HOME"; command -v sshd; command -v python; command -v whisperx; command -v scenedetect'
```

`Ubuntu`, port 2222 and the native environment path are proposed/default identifiers; if absent or occupied, record the actual identifier rather than silently installing, switching Docker contexts or editing global settings. No `wsl --shutdown`, `docker system prune`, `compose down`, community restart, firewall disable or global daemon reconfiguration is permitted.

### 1B. Storage and execution contract

| State | Owner | Allowed readers |
|---|---|---|
| Quant warehouse and IBOR | Windows native Python; NTFS, not cloud-synchronized or UNC storage | Same process while writing; closed exported artifacts for other processes |
| Evidence originals/index | WSL2 ext4 | Local evidence process; APIs/export for others |
| Karakeep application state | Existing Docker Linux storage | Product API only |
| Wealthfolio app DB | Native Windows application | Built-in exported local backup for parity checks |
| Community databases | Existing community stack | Existing permissions only; untouched by IPOS |

Use separate native virtual environments. Source deployments may be native checkouts of the same main commit; databases are not synchronized between them. Keep heavy media/model I/O on ext4, host quantitative I/O on NTFS. [E1] [E2] [E3]

### 1C. Existing transport, not a new server framework

Use OpenSSH's supported SFTP subsystem, pinned host keys and key-only authentication. Configure a dedicated read-only role (`internal-sftp -R`) limited to the published WSL evidence directory. A separate report-drop role may write only a WSL staging inbox for host-generated reports; it cannot write source evidence, execute shell commands, forward ports or modify active rules. Scope the listening endpoint to host-only access and verify firewall/network behavior. Do not edit an unseen global `sshd_config`; use the supported local service configuration process and capture its actual configuration. [E4] [E5] [E21]

This second direction is necessary: if Hermes runs in WSL, Windows must publish its committed snapshot back to Hermes without a cross-OS mount. The read-only evidence account cannot also upload reports. Both transfers are Windows-initiated; neither is in the numerical critical path.

Example transfer **after** that configuration and out-of-band host-key verification. The paths and role below define the proposed transfer contract, not discovered host state:

```powershell
$RunId = 'reviewed-run-id'
$Stage = "C:\IPOS\exchange\staging\$RunId"
if (Test-Path $Stage) { throw 'Stage already exists; inspect replay state, do not overwrite.' }
New-Item -ItemType Directory -Path $Stage | Out-Null
$Batch = Join-Path $env:TEMP 'ipos-sftp-get.txt'
@"
get -r /published/$RunId $($Stage.Replace('\','/'))
"@ | Set-Content -Encoding ascii $Batch
sftp -b $Batch -P 2222 -o BatchMode=yes -o StrictHostKeyChecking=yes `
  -o "UserKnownHostsFile=$env:USERPROFILE/.ssh/ipos_known_hosts" `
  -i "$env:USERPROFILE/.ssh/ipos_export" ipos-export@127.0.0.1
if ($LASTEXITCODE -ne 0) { throw 'Transfer failed; staging is not accepted input.' }
```

Do not infer trust from `ssh-keyscan` alone. Provision and verify the actual server key. SFTP download completes transport only; receiver validation and local publication are still mandatory.

### 1D. Minimal artifact boundary

Reuse the existing R3 manifest model; do not add a parallel evidence catalog. Its published export must carry `run_id`, schema version, source-main commit, business `as_of`, creation time, account/subject coverage, and file entries with safe relative path, SHA-256, size and media type. An accepted numerical bundle additionally records rule/price/FX versions and allocation scope. [R5]

A receiver must reject partial files, wrong hashes, duplicate/conflicting IDs, future or expired business dates, path traversal, symlinks, Windows-reserved names and unexpected database files. Move validated staging into an immutable directory on the same native volume, then write the acceptance marker last. Replaying the same manifest does nothing; same ID with different bytes is quarantined. Never accept a file because it is named `snapshot.json` or has a recent mtime.

Correct the runner to resolve one holdings input and one parsed portfolio block for both persisted contradictions and snapshot output. Execute validation before any action publication; keep custody and narration outside the DuckDB writer lifetime. If malformed optional holdings are quarantined, macro output must explicitly say `portfolio_unavailable`, and old portfolio rows for the same run must not survive as current. Do not reinterpret an invalid portfolio as zero holdings.

Acceptance tests to add to the actual runner test suite: change inbox between stages and prove one input still governs both; kill transfer/export before final marker and prove no new run is accepted; replay twice and prove no duplicate action; keep external DuckDB connections out during writing; simulate research/AI outage and prove macro output remains available. These are future tests, not tests claimed to exist or pass now.

## Phase 2 - Broker reconciliation first, then C12

Owner: broker-data integrator. Recover C11/C12 runtime and tests before touching them. Use Portfolio Performance's supported local PDF import and CSV exports; retain its application version and document-type acceptance record. No parser reimplementation or headless CLI claim. [E12] [E13]

Build one bounded acceptance set from authorized local files: one original statement from each issuing-bank format actually held, one zero export, one buy/sell pair crossing lots, a fee/tax case, a transfer/corporate action and a foreign-currency case. No broad ingestion of the seminar archive is needed. Record unsupported variants explicitly.

Independent numeric controls:

| Control | Required invariant |
|---|---|
| Shares per account/instrument | Opening quantity + acquisitions + inbound transfers - disposals - outbound transfers, adjusted for documented corporate actions, equals statement holdings |
| Cash per account/currency | Opening cash + signed events = closing statement cash; paired trade legs counted once |
| Event idempotence | Same broker event/document can be reimported without changing balances |
| FIFO relief | Each sale consumes oldest eligible lots by declared policy; quantity cannot become negative absent an explicit short mandate |
| Cost basis | Native amounts, fees and historic FX remain auditable; FIFO realized basis and remaining weighted-average basis are separate fields |
| Valuation | Current prices/FX are not substituted for historic cost; value currency and instrument listing currency are separate |
| Missing history | Opening snapshot is marked incomplete-history, not converted into fictional buys or zero cost |

Select Wealthfolio's installed native holdings mode for opening snapshots, or transaction mode for complete verified events. First validate a duplicate-free disposable application account, not the only production ledger. Do not regard equality between IPOS output and a GUI fed by that output as independent truth; compare both to the broker control. [E16] [E22]

Native backup verification on Windows, after exporting through Wealthfolio's supported UI. Set `IPOS_WEALTHFOLIO_BACKUP` to that exported SQLite file, not the running app database:

```powershell
if (-not $env:IPOS_WEALTHFOLIO_BACKUP) { throw 'Set the exported backup path.' }
@'
import os, sqlite3
from pathlib import Path
p = Path(os.environ['IPOS_WEALTHFOLIO_BACKUP']).resolve(strict=True)
if os.name != 'nt' or str(p).startswith('\\\\'):
    raise SystemExit('Require a local Windows backup, never a UNC/WSL database')
with sqlite3.connect(p.as_uri() + '?mode=ro', uri=True) as con:
    result = con.execute('PRAGMA integrity_check').fetchall()
    if result != [('ok',)]:
        raise SystemExit(result)
    print(con.execute("SELECT type,name FROM sqlite_master WHERE type IN ('table','view') ORDER BY type,name").fetchall())
print('SQLite integrity verified; financial parity still requires schema-specific comparison.')
'@ | & $Py -
if ($LASTEXITCODE -ne 0) { throw 'Backup integrity failed.' }
```

Inspect the exported schema/version before writing a parity query; no table names were established in this audit. Fix tolerances to the imported precision, currency minor units and valuation timestamps. Distinguish expected market-price differences from quantity/cash/cost mismatches. Preserve original backup and checksums; never alter application tables directly. [E17]

## Phase 3 - Custody and externally implemented claim extraction

Owner: research integrator. Preserve R1/R3 choices. Bind the direct product interfaces in artifact 02 into the recovered M08/M09 implementation seam, not a new TTK engine. No whole-file replacement of recovered plans. [R4] [R5]

Verify installed tools before any dependency change:

```bash
python --version
python -m pip check
yt-dlp --version
ffmpeg -version
whisperx --help
scenedetect --help
python -c "from importlib.metadata import version; print({p: version(p) for p in ['whisperx','llama-index-core','llama-index-program-openai']})"
```

These commands belong in the chosen ext4 environment. Missing dependencies are a deployment task using pinned packages and model assets; do not execute a mass upgrade of the quantitative or community environment. The code blocks in artifact 02 are integration bindings, not proof that packages or models are installed.

Use a small source-grounded acceptance set covering a financial number, explicit negation, a retracted prediction and a claim split across segments. For every retained candidate, code must recover the exact quote using source hash, segment and offsets. Reject or queue ambiguous quotes; retain raw extraction for diagnosis. Include a quoted malicious instruction and verify it cannot call tools, change rules or populate numeric portfolio fields.

Custody acceptance: disconnect Karakeep and reconstruct a selected retained source from its neutral export; verify hashes and metadata, including pagination coverage. An image/PDF asset API must not be assumed to accept arbitrary video/audio MIME types. Keep media originals in native evidence storage and link receipts/bookmarks as supported. [E18]

One register writer applies approved transitions. Hermes/Activepieces can request updates, not overwrite shared JSON concurrently. A negative claim, an observation that falsifies an approved threshold and lack of current evidence are different event types. Notification retries never repeat promotion or generate a second action.

## Phase 4 - Macro policy, actual optimizer, views and manual-action closeout

Owner: quantitative integrator. Recover C13/M12P and its actual constraints before integration. The product smoke check below proves imports/signatures, not numerical correctness:

```powershell
& $Py -c 'import inspect,riskfolio as rp; from importlib.metadata import version; print(version("Riskfolio-Lib")); print(rp.__file__); print(inspect.signature(rp.plot_clusters)); print(inspect.signature(rp.plot_dendrogram)); print(inspect.signature(rp.Portfolio.rp_optimization))'
if ($LASTEXITCODE -ne 0) { throw 'Actual Riskfolio API unavailable.' }
```

Run the recovered tests only when the files really exist; missing tests must cause an explicit unresolved gate, not be replaced by a placeholder:

```powershell
$ModernTests = @('tests/test_m11_normalizer.py','tests/test_m13_optimizer.py')
foreach ($File in $ModernTests) {
    if (-not (Test-Path $File)) { throw "Required recovered test missing: $File" }
}
& $Py -m pytest -q @ModernTests
if ($LASTEXITCODE -ne 0) { throw 'Recovered quantitative tests failed.' }
```

Before target generation, require a reviewed instrument master, complete account coverage, adjusted EUR return universe, business-date-consistent valuation and versioned macro-to-sector constraints. A market-price-pattern label does not automatically identify a macro sector regime. Do not silently turn a stance score in [-1,1] into a capital percentage. [R11] [E9]

Preserve the actual solver's risk measure and constraints. Independently check finite weights, exact asset alignment, bound residuals, normalization and risk contributions; for volatility, `sum(RC_i)` equals `sqrt(w' Sigma w)`. An infeasible problem produces `BLOCKED`, never equal-weight fallback labelled optimal. Distinguish unconstrained risk-budget fit from constraints that legitimately prevent exact parity.

Compute order units using declared lot rules, then recalculate cash, exposure, costs, turnover and limits after rounding. Include instrument/account, held units, target units, delta, EUR price/FX timestamp, action, stop rule/level or unavailable reason, rule version and input run ID. Missing or stale inputs block action. The user places orders manually; later actual broker fills reconcile the next IBOR state. No order endpoint or broker credential is required.

Render the Riskfolio diagnostics and optional Plotly companion using the direct calls in artifact 02. Verify their displayed weights and aggregate totals against input tables, confirm cluster labels are not sector labels, and keep any unknown sector or excluded return sleeve visible. Do not rename a toy/synthetic graph as a portfolio result. [E8] [E10]

## Phase 5 - Operational acceptance across all stories

Run one end-to-end acceptance cycle with explicit run IDs, then a replay, then a controlled interruption. Capture native host runtime, pinned commit, package/model versions, accepted source/portfolio manifests, numerical output, C12 reconciliation outcome and delivery receipt. Never use pass counts alone as evidence of sensible investment policy.

| Check | Pass condition |
|---|---|
| Native host independence | No Docker/WSL/media/model start is required by the numerical calculation with already accepted inputs |
| Scheduling | Existing Task Scheduler definition uses the Windows interpreter, correct working directory, overlap prevention and meaningful exit status |
| Timing | Measure acquisition separately from warm numerical compute. The user-requested <15s target is tested, not inherited from prose |
| WF06 failure | Missing custody artifact or changed bytes produces a visible custody failure without corrupting last accepted evidence |
| Claim promotion | Unreviewed or unmatched claim cannot affect an active numeric rule; a reviewed deterministic trigger remains reproducible |
| Manual-action isolation | No broker order call exists; proposed quantities do not count as executed holdings |
| Narration | Snapshot numeric fields remain byte/semantic-identical before and after narration; model prose cannot overwrite them |
| Delivery | Retries resend the same run digest without re-optimizing or changing allocation |
| US10-12 | Community container IDs/configuration, reserved ports and volumes remain unchanged; no community PII enters IPOS/Telegram narrative |
| Recovery | Interrupted transfers/reports expose no partial new run; selected evidence and Wealthfolio backups restore locally |

**Definition of done:** targeted defects are corrected; the missing source generation is reconciled; full native tests pass; both OS handoffs and product imports run on real authorized inputs; independent broker/C12 controls close; deterministic policy explains every proposed action; community operations remain untouched. Until then, use the original supported comparison output where valid, and label prospective action integration as unverified.

## Audit validation already performed

`git apply --check` succeeded on the exact Git-blob-matched two-file baseline. Patched files compiled. Isolated execution of the 22 delivered regression cases produced 18 failures/4 passes before and 22 passes after; real pandas was used, FX lookup was explicitly stubbed, and unavailable DuckDB/configuration imports were excluded. This does not substitute for Phase 0 host pytest or later integration acceptance. Validation evidence is indexed in the manifest.

## Source links

[R8]: https://github.com/leela-spec/Investment/blob/cec42be2aaf922c74ea6b13dc44fe11adfdd618f/ipos/run.py "Live weekly runner"
[R9]: https://github.com/leela-spec/Investment/blob/cec42be2aaf922c74ea6b13dc44fe11adfdd618f/ipos/export/snapshot.py "Live snapshot builder and writer"
[E1]: https://duckdb.org/docs/current/connect/concurrency "DuckDB concurrency"
[E2]: https://learn.microsoft.com/en-us/windows/wsl/filesystems "Microsoft WSL filesystem guidance"
[E3]: https://docs.docker.com/desktop/features/wsl/best-practices/ "Docker Desktop WSL best practices"
[E4]: https://learn.microsoft.com/en-us/windows-server/administration/OpenSSH/openssh-overview "Windows OpenSSH"
[E5]: https://learn.microsoft.com/en-us/windows/wsl/networking "Microsoft WSL networking"
[E21]: https://man.openbsd.org/sftp-server.8 "OpenSSH read-only SFTP server"
[R5]: https://github.com/leela-spec/Investment/blob/cec42be2aaf922c74ea6b13dc44fe11adfdd618f/05_blueprint/research/2026-08-23-ipos-reuse-expansion-program/results/R3-evidence-kb/TOOL_LANDSCAPE.md "Existing evidence-KB landscape"
[E12]: https://help.portfolio-performance.info/en/reference/file/import/pdf-import/ "Portfolio Performance PDF import"
[E13]: https://help.portfolio-performance.info/en/reference/file/export/ "Portfolio Performance CSV export"
[E16]: https://wealthfolio.app/docs/guide/csv-import/ "Wealthfolio CSV and holdings-mode import"
[E22]: https://wealthfolio.app/docs/concepts/tracking-modes/ "Wealthfolio tracking modes"
[E17]: https://wealthfolio.app/docs/guide/data-export/ "Wealthfolio export and backup"
[R4]: https://github.com/leela-spec/Investment/blob/cec42be2aaf922c74ea6b13dc44fe11adfdd618f/05_blueprint/research/2026-08-23-ipos-reuse-expansion-program/results/R1-karakeep-ipos/CURRENT_IPOS_GAP_MAP.md "Existing Karakeep gap map"
[E18]: https://docs.karakeep.app/api/karakeep-api/ "Karakeep API"
[R11]: https://github.com/leela-spec/Investment/blob/cec42be2aaf922c74ea6b13dc44fe11adfdd618f/tests/test_regime.py "Existing regime tests"
[E9]: https://riskfolio-lib.readthedocs.io/en/latest/riskfoliolib/portfolio.html "Riskfolio convex portfolio API"
[E8]: https://riskfolio-lib.readthedocs.io/en/latest/riskfoliolib/plot.html "Riskfolio plotting API"
[E10]: https://plotly.com/python/treemaps/ "Plotly treemap API"
