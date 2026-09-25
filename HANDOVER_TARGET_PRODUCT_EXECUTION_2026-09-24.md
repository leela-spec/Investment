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

### Target-first communication discipline

Routine updates must lead with only: **target, intended value, current verdict, remaining material gap, and one next action**. Keep each item to one concise line. Put hashes, schemas, row calculations, command output, and other audit detail in the relevant `implementation-runs/` evidence files; surface them in conversation only when requested or required to explain a material failure.

Before continuing an investigation, ask whether its result can change the current product decision or next action. If not, stop. Do not let evidence production, debugging detail, or process ceremony displace the active value target.

## Current frontier

**E01 is complete. E02 partial product proof is accepted with non-blocking gaps. Active frontier: E03 & E04.**

The real Wealthfolio 3.8.0 desktop import of 330 activities is proven and accepted as sufficient partial E02 product proof. Remaining product calculation gaps (holdings omit NDA 1,000 and PSYC 10,000; EUR trade cash overstatement of EUR 41,037.75; and lot engine partial coverage) are recorded as explicit non-blocking limitations. `ipos/portfolio/wealthfolio.py` remains fail-closed (`INTEGRATION_STATUS = "NOT_CONNECTED"`). The active target is **E03: real broker-document ingestion through Portfolio Performance** followed by **E04: coherent portfolio accounting and transaction history**.


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
| Imported activity count is actually 330 | Native backup contains one applied 330-row import with zero review flags/errors | PASS |
| Activity-ledger quantities, fees, taxes, and 34 custom assets agree | Reconciled to the independent Smartbroker oracle | PASS |
| Computed holdings agree with broker control | NDA 1,000 and PSYC 10,000 are missing | FAIL |
| Computed EUR cash agrees | Overstated by EUR 41,037.75 | NON-BLOCKING GAP |
| Wealthfolio FIFO behavior is genuinely invoked | Persisted FIFO lots/disposals exist, but coverage omits NDA and PSYC | NON-BLOCKING GAP |
| Supported native export/read interface works | Native backup exported and inspected read-only | PASS |
| IPOS consumes real Wealthfolio output | No; code intentionally fails closed | FAIL-CLOSED / NON-BLOCKING |

## Exact next action

Advance to **E03 (broker-document ingestion via Portfolio Performance)** and **E04 (coherent portfolio accounting and history)**:

1. **Portfolio Performance Ingestion (E03)**:
   - Provide a typed adapter (`pp_adapter`) in `ipos/portfolio/` to parse standard Portfolio Performance CSV exports (`Buchungen` / transactions and `Vermögensaufstellung` / holdings).
   - Normalize PP exports into canonical IPOS activity records and holdings schemas with preserved provenance (ISIN, WKN, transaction type, fees, taxes, currency).
   - Ingest broker PDFs (DAB/BNP and Baader) through Portfolio Performance's native desktop document importer.

2. **Portfolio Accounting & Pipeline Integration (E04)**:
   - Wire normalized holdings and activity ledgers into `ipos/run.py` and DuckDB warehouse.
   - Reconcile multi-currency cash flows, weighted-average economic cost basis, and valuation timestamps.
   - Connect normalized actual holdings directly to the downstream quantitative engine: Riskfolio-Lib optimizer (E07), macro stance tilt (E08), and the Action Matrix (E09).


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

Report using five concise lines:

- target
- intended_value
- current_verdict
- remaining_material_gap
- next_action
