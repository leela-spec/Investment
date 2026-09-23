# IPOS process verification and gap analysis

**Audit date:** 2026-09-23. **Repository:** `leela-spec/Investment`. **Branch:** `main` only.
**Evidence pin:** `cec42be2aaf922c74ea6b13dc44fe11adfdd618f` (2026-08-26).
**Verdict:** safety defects confirmed in accessible code; the requested newer end-to-end system is **NOT CERTIFIED**. This package contains a verified-applicable safety patch and proposed integrations, not a claim that those integrations were deployed. [R0]

## 1. Authority and source-state mismatch

Five of the 21 distinct explicitly named paths are available: the original decision analysis, portfolio specification, visualization audit, R1 Karakeep gap map, and R3 tool landscape. Sixteen are absent at the inspected reference. The missing set comprises both root handovers, the ProThinking standard, WF05/WF06/WF07, the August-28 rebuild matrix and architecture, its M08/M09/M06/M12P plans, and both `ipos/portfolio/{normalizer,optimizer}.py` files and their named tests. Exact-file reads and narrowly scoped directory metadata establish this; an exact-name infrastructure-handover search found no result. This does **not** establish that later local work was lost or never completed.

Consequently, the pasted user contract governs the target, but cannot prove host configuration, C11/C12/C13 implementation, 22 active indicators, 126 executable rules, or a sub-15-second production run. The unseen revised decision matrix cannot honestly be declared reconciled line by line. No feature branch was substituted for `main`.

Directly linked live code was then inspected: portfolio CSV/aggregation, weekly runner, snapshot builder, portfolio tests and regime tests. Existing code establishes a deterministic macro/report pipeline and a holdings-exposure comparison, not the requested transaction IBOR or complete research-to-order-delta flow. [R2] [R6] [R7] [R8] [R9] [R10] [R11]

**Evidence labels:** OBSERVED = read live source; REPRODUCED = executed bounded tests; SPECIFIED = proposed correction; UNVERIFIED = required host/product acceptance remains. No raw `Sources/`, `data/`, `logs/`, or `tests/fixtures/` content was ingested.

## 2. Confirmed defects and consequential seams

| ID / priority | Finding and evidence | Correction / residual limitation |
|---|---|---|
| G01 / P0 | Required later sources are absent on visible `main`. [R0] | Reconcile the local and remote reference without reset, overwrite, branch switching, or fabricated replacement modules. |
| G02 / P0 | Failed FX conversions retain native amounts in `value_eur`; aggregation subsequently counts them as EUR. Some tests explicitly expect the unconverted helper result. [R7] [R10] | Patch rejects unresolved-currency aggregation; successful conversion relabels value currency EUR. Unknown FX is not zero exposure. |
| G03 / P0 | CSV parsing silently removes invalid values, can turn a missing instrument into the string `nan`, and accepts non-finite values/missing quantities. [R6] | Patch rejects incomplete input instead of shrinking the portfolio. Existing valid German and price-based inputs remain supported. |
| G04 / P1 | The runner computes holdings for persisted contradictions, but snapshot construction independently reads the inbox again. A changed file can produce two portfolios in one run. [R8] [R9] | Capture one immutable input receipt and reuse the resulting portfolio block throughout the run. Not fixed by the safety patch. |
| G05 / P1 | The writer connection spans provider pulls and narration; snapshots are written separately and non-atomically. [R8] [R9] | Separate acquisition/narration from the quantitative writer; publish a versioned bundle with a final commit manifest. No claim of whole-run database rollback. |
| G06 / P1 | Filename ordering chooses one CSV across the inbox; filesystem mtime supplies freshness. Neither proves complete multi-account holdings or business as-of. [R6] | Require account coverage and statement timestamps in the normalized input manifest; retain mtime only as operational metadata. |
| G07 / P1 | Holdings snapshots do not contain lot history, historic FX, fees, or corporate actions. Current portfolio code is exposure comparison only. [R2] [R7] | Keep opening holdings separate from transaction events; unknown FIFO basis stays unknown. |
| G08 / P1 | Price-pattern regime tests establish TRENDY/CHOPPY/MOMENTUM behavior, not a growth/inflation sector transmission model. [R11] | Name price regime, macro regime, sector mapping and optimizer constraints separately. Do not equate them. |
| G09 / P1 | Research-to-rule promotion is a documented existing gap; storage and extraction do not close it. [R4] [R5] | Exact quote gate, review status and versioned approved rules; no LLM-written portfolio weights or automatic thesis verdicts. |

**Patch behavior is deliberately fail-stop:** invalid holdings now raise before incorrect totals are produced. The inspected runner does not catch that exception, so that attempt can abort before report export; earlier database stages may already have written. Absence of a CSV remains optional. Graceful portfolio quarantine while continuing the macro report is a separate, explicitly tested follow-up, not a capability claimed for this patch.

## 3. End-to-end process and inter-OS contract

The coherent shape is **two asynchronous lanes meeting at a validated host input**, not one synchronous chain requiring Docker, WSL, AI and a GUI every Saturday:

```text
WSL/ext4: media -> aligned transcript -> candidate claims -> reviewed evidence bundle
                   |                                  |
Docker: Karakeep capture/review <--- supported API -----+
                   |
Windows-initiated OpenSSH SFTP pull: immutable files only, hash-checked on NTFS
                   |
Windows: accepted inputs + broker ledger + cached observations
         -> deterministic macro/policy -> Riskfolio -> manual Action Matrix
         -> committed snapshot bundle -> narration/delivery
         -> optional Wealthfolio visual and backup reconciliation
```

| Boundary / workflow | Owner and concrete transfer | Failure behavior / acceptance |
|---|---|---|
| M08 acquisition and slides | WSL ext4 owns original video, extracted audio, transcript and slide files; one source timeline. | Audio-only acquisition cannot supply slides. Preserve video; interrupted downloads never receive a completed receipt. |
| WF06 custody | Karakeep via API for capture/review; R3 immutable originals/manifests outside its application DB. [R4] [R5] [E18] | API failure queues export retry; a bookmark or HTTP 200 alone is not custody. Validate bytes, lineage and a restore sample. |
| M09/WF07 claims | WSL extraction publishes candidates referencing transcript hash, segment and exact quote offsets. | Unmatched/ambiguous quotes, missing context or falsifiers stay in review, never become numerical instructions. |
| Action/watch register | One designated writer on ext4; Activepieces/Hermes submit events, not concurrent file overwrites. | Deduplicate event IDs; transitions are proposed -> reviewed -> active -> triggered/closed. Host consumes a versioned export. |
| WF05 host sweep | Native Windows process exclusively owns host DuckDB/IBOR state; consumes previously accepted NTFS artifacts. | Missing optional research does not stop macro calculation. Stale/invalid holdings prohibit a new actionable matrix. |
| C13 and C12 | Riskfolio runs against host-owned returns; Wealthfolio receives CSV, then provides a native backup exported locally. | No open cross-OS database; no automatic broker API; no claim of independent parity from two views of the same faulty CSV. |

**Database correction:** for native in-process DuckDB, separate processes may all read only when none writes. "One writer plus other read-only processes" is not the intended file-sharing model. Narrators and GUIs consume exported artifacts, never the live warehouse. SQLite evidence, Wealthfolio and any IBOR each remain with their own native-filesystem owner. [E1] [E2]

**No 9P transfer:** use existing OpenSSH/SFTP over a host-reachable WSL endpoint, not `/mnt/c`, `\\wsl$`, `\\wsl.localhost` or a Docker bind mount for database access. Host initiates the pull to avoid assuming WSL-to-Windows localhost under NAT. Verify network mode and firewall; pin the host key. Only JSON/CSV/Parquet and selected documents cross; never working database files. [E4] [E5]

**Publication:** producer closes files, hashes them, then publishes an immutable directory. Receiver downloads into NTFS staging, rejects path traversal, symlinks, unexpected extensions, wrong sizes/hashes, stale timestamps and replay conflicts, then renames on the same volume and publishes its acceptance marker last. A hash proves byte identity, not source truth. Concurrent readers use one committed run ID, not a mutable collection of "latest" files.

## 4. Coverage of all 12 user stories

| Story | Assessment and acceptance condition |
|---|---|
| US-01 evidence custody | Prior research supports Karakeep plus neutral custody. Verify export pagination, originals, derivative lineage and restore without Karakeep. [R4] [R5] |
| US-02 media | External CLI chain is specified in 02. Verify audio/video timing, slide recall and missing/interpolated alignments on a bounded real sample. |
| US-03 claims/invalidation | Candidate extraction is allowed; deterministic predicates evaluate only reviewed typed conditions. Silence, stale evidence and contradiction are different states. |
| US-04 Saturday sweep | Existing native runner observed, scheduler/host not inspected. Separate warm compute latency from downloads, WSL startup, model loading and delivery; verify actual indicator/rule coverage. [R8] |
| US-05 broker/FIFO | Current code cannot certify IBOR/FIFO. Reconcile each account, trade/settlement dates, lot IDs, historic FX, fees and corporate actions; never fabricate historical buys from a snapshot. |
| US-06 sector allocation | Correlation clustering is not industry taxonomy or macro causality. Use explicit sector mappings plus separately approved constraints; do not substitute HRP for the unseen C13 solver. |
| US-07 manual actions | Numeric targets, feasible units, cash and stops; no execution credentials or order calls. Actual fills return through broker import before the next actionable matrix. |
| US-08 Wealthfolio | Native holdings and transaction modes are different contracts. Original broker control -> normalized input -> GUI/export parity, with matching dates and methods. [E16] |
| US-09 narrative/delivery | Narrator reads committed snapshot, cannot mutate numerical fields. Delivery retry must not rerun optimization; separate numerical run ID from message delivery ID. |
| US-10 community expenses | Out of IPOS implementation scope. OCR extracts fields; approved accounting rules and review determine categories. No automatic assumption of charitable tax status. |
| US-11 four-repository orchestration | Target-only: no other repositories inspected. Separate workspace identities, credentials, output paths and permissions; a global orchestrator is not a shared write authority. |
| US-12 untouched Docker community | Ports 8084/8082/8010/8086 are operator-supplied reservations, not observed host state. No restarts, pruning, shared secrets, volumes or migrations. Isolation under one Docker daemon is operational separation, not a hard security boundary. |

## 5. Numerical contract missing between research and orders

For a declared long-only allocation, code computes EUR NAV including cash, then target units from `target_weight * NAV / EUR_price`, rounds to each instrument's lot step, and rechecks cash, exposure and turnover after rounding. `delta_units = target_units - held_units`; positive means BUY, negative with remaining holdings TRIM, zero HOLD, and a zero target with holdings SELL. Missing data yields **BLOCKED**, not HOLD.

Risk contribution for covariance Sigma is `RC_i = w_i (Sigma w)_i / sqrt(w' Sigma w)`. Its sum must equal portfolio volatility. A budget such as 0.20 is a share of risk contribution, not automatically a 20% capital weight. Macro signals must affect an approved risk-budget/constraint mapping; a chart must never silently create that mapping.

FIFO lot relief and weighted-average remaining cost are distinct outputs. Preserve native-currency amounts and historical FX per transaction. An average acquisition cost cannot reconstruct the missing oldest lots. For policy-defined long trailing stops, code may use `max(previous_stop, high_water_mark - k * ATR)` only when the rule, k, prices, corporate-action adjustments and timestamps are approved and valid. This is a calculation contract, not a selected investment strategy.

## 6. Verification result and remaining gates

The two patched baseline files were reconstructed from connector content and matched their Git blob hashes exactly. Unified-diff applicability and Python compilation passed. **22 isolated regression cases: original functions 18 failed / 4 passed; patched functions 22 passed.** Real pandas was used; unavailable IPOS configuration/DuckDB imports were excluded for isolation, and FX lookup was explicitly stubbed in relevant tests. No SQL execution, complete repository pytest, Riskfolio optimization, WhisperX model run, Windows scheduler, WSL transport, GUI or broker-data acceptance was performed here.

The unresolved gates are source reconciliation, full host regression, same-input run consistency, transport/recovery, broker ledger completeness, approved macro-to-sector policy, and independent C12 parity. Until those pass, the deliverable is an actionable correction package, **not a production readiness certificate**.

## Source links

[R0]: https://github.com/leela-spec/Investment/commit/cec42be2aaf922c74ea6b13dc44fe11adfdd618f "Observed main reference"
[R2]: https://github.com/leela-spec/Investment/blob/cec42be2aaf922c74ea6b13dc44fe11adfdd618f/05_blueprint/03_PORTFOLIO_MODULE.md "Built portfolio comparison specification"
[R6]: https://github.com/leela-spec/Investment/blob/cec42be2aaf922c74ea6b13dc44fe11adfdd618f/ipos/etl/portfolio_csv.py "Live portfolio CSV reader"
[R7]: https://github.com/leela-spec/Investment/blob/cec42be2aaf922c74ea6b13dc44fe11adfdd618f/ipos/aggregate/portfolio.py "Live portfolio aggregation and FX"
[R8]: https://github.com/leela-spec/Investment/blob/cec42be2aaf922c74ea6b13dc44fe11adfdd618f/ipos/run.py "Live weekly runner"
[R9]: https://github.com/leela-spec/Investment/blob/cec42be2aaf922c74ea6b13dc44fe11adfdd618f/ipos/export/snapshot.py "Live snapshot builder and writer"
[R10]: https://github.com/leela-spec/Investment/blob/cec42be2aaf922c74ea6b13dc44fe11adfdd618f/tests/test_portfolio.py "Existing portfolio tests, inspected first 230 lines"
[R11]: https://github.com/leela-spec/Investment/blob/cec42be2aaf922c74ea6b13dc44fe11adfdd618f/tests/test_regime.py "Existing regime tests"
[R4]: https://github.com/leela-spec/Investment/blob/cec42be2aaf922c74ea6b13dc44fe11adfdd618f/05_blueprint/research/2026-08-23-ipos-reuse-expansion-program/results/R1-karakeep-ipos/CURRENT_IPOS_GAP_MAP.md "Existing Karakeep gap map"
[R5]: https://github.com/leela-spec/Investment/blob/cec42be2aaf922c74ea6b13dc44fe11adfdd618f/05_blueprint/research/2026-08-23-ipos-reuse-expansion-program/results/R3-evidence-kb/TOOL_LANDSCAPE.md "Existing evidence-KB landscape"
[E18]: https://docs.karakeep.app/api/karakeep-api/ "Karakeep API"
[E1]: https://duckdb.org/docs/current/connect/concurrency "DuckDB concurrency"
[E2]: https://learn.microsoft.com/en-us/windows/wsl/filesystems "Microsoft WSL filesystem guidance"
[E4]: https://learn.microsoft.com/en-us/windows-server/administration/OpenSSH/openssh-overview "Windows OpenSSH"
[E5]: https://learn.microsoft.com/en-us/windows/wsl/networking "Microsoft WSL networking"
[E16]: https://wealthfolio.app/docs/guide/csv-import/ "Wealthfolio CSV and holdings-mode import"
