# IPOS target-product execution handover — 2026-09-24

This is the active handover for the target-oriented execution program supplied in:

`C:\Users\gehma\Downloads\IPOS_Process_Verification_Gap_Resolution_2026-09-23_V2\IPOS_Process_Verification_Gap_Resolution_2026-09-23`

It supplements `AGENTS.md`, `HANDOVER.md`, and `PROJECT_STATE.md`. Where their older next-step text conflicts with this file, use this file for the current execution frontier. Do not replace the target with proxy completion such as “a CSV exists” or “tests pass.”

## Mission and execution discipline

The governing order remains:

1. E01 — safe and truthful portfolio foundation
2. E02 — real Wealthfolio portfolio layer
3. E03 — real broker-document ingestion through Portfolio Performance
4. E04 — correct portfolio accounting and history
5. E05 — investment media understanding
6. E06 — source-grounded claim extraction
7. E07 — real Riskfolio portfolio intelligence
8. E08 — macro-to-portfolio connection
9. E09 — Action Matrix
10. E10 — operational automation

Target first, product second, real operator value third. Tests and generated files are evidence, not completion. Use product-native interfaces, preserve provenance, and do not invent local facades for external products.

## Current frontier

**E01 is complete. E02 is active and partially proven. Do not start E03 yet.**

E02 has now crossed the real-product boundary: the operator completed a real import in Wealthfolio 3.8.0 using a transformed Smartbroker transaction export. However, E02 is not complete because the resulting activities, holdings, cash, and cost basis have not yet been reconciled inside Wealthfolio or through a supported Wealthfolio export/read interface. IPOS must remain fail-closed until that proof exists.

## Completed and committed work

- Commit `ae8b465` completed E01 financial-boundary corrections:
  - unresolved FX cannot silently enter EUR totals;
  - M11 basis is explicitly weighted-average economic basis with currency semantics;
  - fake Wealthfolio backup/MCP behavior was removed;
  - Riskfolio-Lib 7.3.0 is declared, locked, genuinely invoked, and independently checked.
- Commit `e5c073c` added E02 native-product proof material and retained E05 evidence.
- Commit `ac7b660` aligned the controlled Wealthfolio acceptance fixture with Wealthfolio 3.8 semantics.
- E01 evidence: `implementation-runs/E01/20260923-222414/VERIFICATION_REPORT.md`.
- E02 baseline evidence and acceptance contract: `implementation-runs/E02/20260923-225605/`.
- `ipos/portfolio/wealthfolio.py` deliberately remains `INTEGRATION_STATUS = "NOT_CONNECTED"` and fails closed. Do not change that merely because an import completed.

## Real Wealthfolio use completed in this session

### Private source control

- Correct Smartbroker transaction export:
  - location: private local CSV in `C:\Users\gehma\Downloads`; identify it by the hash below rather than committing its account-number-bearing filename
  - SHA-256: `4FD36847B400B0E011078F7AEC290F5FDDE705AAAF551FD709F9C51298D6927A`
  - rows: 363
  - confirmed: 332
  - cancelled and excluded: 31
- Do not use the earlier `08-45-09.175Z.csv`; it was a holdings snapshot, not an activity ledger.
- Do not commit the broker export or any unredacted Wealthfolio backup. They contain private financial/account data.

### Imported file

- Final prepared import file:
  - path: `C:\Users\gehma\Downloads\wealthfolio-activities-2026-09-24-v4.csv`
  - SHA-256: `6191821561706043C577DBCAEF6A159CA0D75E684717EACC2AF5C429C9DAD76B`
  - candidate rows: 331
- The operator confirmed that the Wealthfolio import completed.
- Immediately before import, Wealthfolio reported **330 of 331 rows valid and ready**. Treat 330 as the expected imported count, but verify it in Wealthfolio rather than asserting it from the preview.
- The import used Wealthfolio's real five-step desktop CSV workflow: Upload, Mapping, Review Assets, Review Activities, Import.
- Wealthfolio resolved ordinary securities where possible. Thirty-four unsupported structured products/securities were explicitly marked as custom assets in the native UI.

### Intentional transformations and known exception

- Activity types were mapped as:
  - `BUY` -> `BUY`
  - `SELL` -> `SELL`
  - `ENTERINTOSECACCOUNT` -> `TRANSFER_IN`
  - `TAKEOFFSECACCOUNT` -> `TRANSFER_OUT`
- All imported trade monetary fields use the account/settlement currency EUR. Unit price is the settled EUR investment amount divided by quantity so the final amount, fees, and taxes reconcile.
- Eighteen verified ordinary-security ticker mappings were used; ISIN provenance was retained. Structured products remained ISIN/custom assets rather than being falsely mapped to their underlying stocks.
- Two genuine sells of `DE000MK4AL67` on 2026-04-24, each 750 units at EUR 2.73 with EUR 2,047.50 proceeds and executed 29 seconds apart, were combined into one 1,500-unit sell with EUR 4,095 proceeds. Wealthfolio treated the original pair as duplicates. Quantity and cash are preserved; per-fill granularity is not.
- One row remained invalid and was skipped by the product import:
  - timestamp: `2026-09-10T00:02:00`
  - ISIN/symbol: `XC000A42NLY5`
  - description: AtaiBeckley Inc. Contingent Value Rights
  - activity: `TRANSFER_IN`
  - quantity: 500
  - broker consideration/unit price: 0
- This single zero-consideration CVR transfer is an explicit residual gap. It is not important enough to block the other 330 activities. Do not redesign the pipeline around it. If later holdings reconciliation proves those rights still matter, add or document them manually in Wealthfolio with their unknown/zero economic basis.

## What is proven versus not proven

| Condition | Current evidence | Verdict |
|---|---|---|
| Official Wealthfolio installed | Version 3.8.0 and official installer verification recorded in E02 status | PASS |
| Real product import boundary crossed | Operator completed the native desktop import | PASS |
| Broker rows transformed with explicit provenance | Source and prepared-file hashes plus documented transformations | PASS |
| Imported activity count is actually 330 | Only the pre-import product preview and operator completion confirmation exist | VERIFY NOW |
| Holdings/quantities agree with broker control | Not yet inspected/reconciled | OPEN |
| EUR cash, fees, and taxes agree | Not yet inspected/reconciled | OPEN |
| Wealthfolio FIFO/cost-lot behavior is useful and correctly attributed | Not yet inspected/exported | OPEN |
| Supported native export/read interface works | Not yet exercised | OPEN |
| IPOS consumes real Wealthfolio output | No; code intentionally fails closed | OPEN |

## Exact next action

Finish E02 before advancing:

1. Open the imported Wealthfolio account and verify the actual activity count, holdings, and any review/draft flags. Record screenshots or a redacted receipt.
2. Use Wealthfolio's supported export or backup UI. Do not read or mutate the live application SQLite database directly, and do not invent a backup schema.
3. Keep the raw export/backup outside Git. Record only its path, SHA-256, application version, export timestamp, and redacted reconciliation results under `implementation-runs/E02/20260923-225605/`.
4. Build the independent oracle from the original Smartbroker export, not from the prepared Wealthfolio CSV. Reconcile at minimum:
   - expected imported activities: 330;
   - per-security net quantity after the documented combined sell and skipped CVR;
   - EUR trade cash totals, fees, and taxes;
   - the set of 34 custom assets;
   - review/draft/error count after import;
   - Wealthfolio FIFO/lot output, clearly distinguished from IPOS weighted-average basis.
5. Re-importing the same private file may be used to prove duplicate handling only after confirming it cannot mutate valid state unexpectedly. Expect zero new activities; cancel if the preview differs.
6. Only after the product-native state and export reconcile should `ipos/portfolio/wealthfolio.py` be connected to a supported read/export interface and `INTEGRATION_STATUS` be changed. Add tests that fail when the real product output is absent; do not restore local simulations.

If Wealthfolio cannot provide a supported export/read surface with enough provenance, record E02 as partially useful but blocked at the integration boundary. Do not compensate with direct live-database writes or fabricated MCP behavior.

## Next value target after E02

Proceed to **E03: real broker-document ingestion through Portfolio Performance**, using actual Smartbroker/DAB/Baader PDF documents and Portfolio Performance's supported desktop import/export workflow. This is for repeatable broker-document parsing; it is not a replacement for finishing the Wealthfolio result verification above.

E05 product-proof material already exists in `implementation-runs/E05/20260923-230911/`. Do not redo it merely because E05 appears later in the canonical order; inspect its receipts when that stage becomes active.

## Repository and operating constraints

- Repository: `C:\GitDev\Investment`
- Branch: `main`; commit directly, no feature branches or worktrees.
- Preserve the unrelated untracked file `Portfolio Status Quo/SomeRandomLastAnswersTOCOntinue.md`.
- Raw `Sources/` material is read-only.
- Code computes all numeric results; the LLM narrates only.
- Do not introduce new services, databases, abstraction layers, or orchestration unless the active target demonstrably requires them.
- Never claim success from a file, adapter, mock, schema, or test alone.

## Latest local verification

Run on 2026-09-24:

- `uv run pytest tests/test_m12_wealthfolio.py -q` -> 2 passed
- `uv run python scripts/qa_repo.py` -> all required checks passed; existing warnings remain informational
- Working tree contained only the unrelated untracked file noted above before this handover was created.

## Required reporting format for the next chat

Report using:

- target
- intended_value
- real_product_used
- what_now_works
- what_was_reused
- what_had_to_change
- evidence_from_real_use
- remaining_real_gap
- next_value_target
