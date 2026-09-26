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

**E01, E03, E04, E05, E06, E07, E08, E09, and E10 are complete and verified. Active frontier: Phase 3 indicator expansion (from `configs/registry_120.yaml` to expand active 22 indicators to 60/120) and research evidence ingestion expansion.**

WF-07 Stage 4 / E08 (Macro-to-Portfolio Decision Connection) is fully implemented and verified. Pure-numeric deterministic sector tilt engine maps all portfolio holdings into 6 core sector clusters, dynamically cascades macro stance vector into bounded multipliers [0.20, 1.80], penalizes research-invalidated sectors (0.80x), executes systematic asymmetric gating (Confidence Gate < 50% or UNCERTAIN regime gates BUY -> HOLD (GATED) while preserving defensive TRIM/SELL), and runs Riskfolio-Lib Hierarchical Risk Parity (rp.HCPortfolio). Independent adversarial proof verifier confirmed PASS.

E03 (Portfolio Performance adapter) and E04 (Multi-Currency Portfolio Ledger accounting) are fully implemented and verified. Real operator transaction activities (`3370191001-2026-09-24T09-02-24.190Z.csv`, 332 confirmed trades) replayed chronologically produce exactly 24 open holdings matching the official broker statement PDF (`3370191001-2026-09-25T15-15-35.459Z.pdf`) with 0 discrepancies (100% MATCH reconciliation), preserving NDA (1,000) and PSYC (10,000). Independent adversarial proof verifier confirmed PASS.


## Completed and committed work

- Commit `ae8b465` completed E01 financial-boundary corrections:
  - unresolved FX cannot silently enter EUR totals;
  - M11 basis is explicitly weighted-average economic basis with currency semantics;
  - fake Wealthfolio backup/MCP behavior was removed;
  - Riskfolio-Lib 7.3.0 is declared, locked, genuinely invoked, and independently checked.
- Commit `b80e082` completed E09 Action Matrix engine & WF-07 Stage 5:
  - Full portfolio mapping of 27 holdings across Zero and Smartbroker (€269,227.11 capital);
  - Deterministic Action Matrix (`ipos/portfolio/action_matrix.py`) computing macro-reconciled target weights, deltas, actions (TRIM/BUY/HOLD/SELL), and stop rules;
  - Integrated into weekly pipeline, DuckDB warehouse, `snapshot.json`, `report.md`, and interactive `report.html`.
- E07 Real Riskfolio-Lib Portfolio Intelligence & Risk Parity completed (2026-09-25):
  - Euler marginal & percentage risk contributions ($MRC$, $RC$, $RC\%$) mathematically calculated across all 32 operator broker holdings;
  - Native convex Risk Parity (`rp.Portfolio.rp_optimization`) and Hierarchical Risk Parity (`rp.HCPortfolio.optimization`) executed offline with zero network leaks and zero LLM arithmetic;
  - Risk Parity target sizing directly controls the Action Matrix rebalancing recommendations and stop policies;
  - Rendered in executive `report.md` and interactive `report.html`;
  - Verified by independent adversarial proof verifier (`PASS`).
- E10 Operational Automation completed (2026-09-26):
  - Registered Windows Task Scheduler task `IPOS Weekly Pipeline` (Saturdays 06:00, Ready state);
  - Headless runner (`scripts/run_pipeline_automated.ps1`) capturing logs to `logs/scheduled/` and writing BOM-free JSON status records (`data/exports/automation_status.json`);
  - Operator quick launcher script `scripts/open_latest_report.ps1`;
  - Verified by independent adversarial proof verifier (`PASS`).
- E05 & E06 Source-Grounded Claim Extraction & Action/Watch Register completed (2026-09-26):
  - WhisperX ASR transcript resolution & cryptographic verification (`audio.json`, SHA256 `6c4d790d...`);
  - Word-level mathematical quote grounding against time intervals;
  - Defanged prompt injection protection;
  - Single-writer atomic register (`data/action_watch_register.json`) with deterministic state machine transitions (`OPEN` -> `TRIGGERED` -> `RESOLVED`);
  - Verified by independent adversarial proof verifier (`PASS`).
- E03 & E04 Portfolio Performance Ingestion & Multi-Currency Ledger Accounting completed (2026-09-26):
  - `PortfolioPerformanceAdapter` (`ipos/portfolio/pp_adapter.py`) ingesting PP Buchungen and Vermögensaufstellung (German and English locales) and raw Smartbroker/DAB transaction exports;
  - `PortfolioLedger` (`ipos/portfolio/accounting.py`) executing genuine chronological activity replay with type priority tiebreakers, multi-currency cash tracking (`EUR`, `USD`, `CAD`, `CHF`), weighted-average economic cost basis tracking across partial sales, and realized capital gains attribution;
  - Replayed 332 confirmed activities from `3370191001-2026-09-24T09-02-24.190Z.csv`, achieving exact 100% MATCH against official broker control PDF (`3370191001-2026-09-25T15-15-35.459Z.pdf`) with 0 discrepancies across all 24 open holdings;
  - Verified by independent adversarial proof verifier (`PASS`).
- WF-07 Stage 4 / E08 Macro-to-Portfolio Decision Connection completed (2026-09-26):
  - Deterministic pure-numeric sector tilt engine (`ipos/portfolio/decision.py`) mapping portfolio holdings to 6 core sector clusters (`TECHNOLOGY_AI`, `CRYPTO_DIGITAL_ASSETS`, `HEALTHCARE_BIOTECH`, `ENERGY_COMMODITIES`, `DEFENSE_INDUSTRIALS`, `FINANCIALS_VALUE`);
  - Dynamic cascading of macro stance vector (`equity`, `duration`, `credit`, `usd`, `commodities`, `growth`) into sector tilts bounded strictly to `[0.20, 1.80]`;
  - Active research thesis-invalidation penalty (0.80x) applying directly to target sectors from `data/action_watch_register.json`;
  - Systematic asymmetric rebalancing gating (Confidence Gate < 50% or `UNCERTAIN` regime converts `BUY` -> `HOLD (GATED)` while preserving defensive `TRIM` and `SELL`);
  - Riskfolio-Lib Hierarchical Risk Parity (`rp.HCPortfolio`) optimization running alongside classic Risk Parity;
  - Full end-to-end integration into `ipos/run.py`, `snapshot.json`, `report.md`, and interactive `report.html`;
  - Verified by independent adversarial proof verifier (`PASS`).
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

Advance to **Phase 3 Indicator Expansion (60/120 Indicators)**:

1. **Indicator Expansion (`configs/registry_120.yaml`)**:
   - Systematically expand the active 22-indicator registry (`configs/registry.yaml`) to the 60-indicator core set from `configs/registry_120.yaml`.
   - Implement missing macro and market series feeds (e.g. real yields, breakeven inflation, credit spreads, commodity breadth, liquidity indexes).
   - Wire expanded indicators into `ipos/macro/engine.py` to enrich macro regime confidence scoring, stance vector determination, and anomaly detection.

2. **Research & Pipeline Deepening**:
   - Deepen automated evidence ingestion from research transcripts directly into `data/action_watch_register.json`.
   - Maintain strict asymmetric gating and Riskfolio-Lib portfolio intelligence downstream.

## Repository and operating constraints

- Repository: `C:\GitDev\Investment`
- Branch: `main`; commit directly, no feature branches or worktrees.
- Preserve the unrelated untracked file `Portfolio Status Quo/SomeRandomLastAnswersTOCOntinue.md`.
- Raw `Sources/` material is read-only.
- Code computes all numeric results; the LLM narrates only.
- Do not introduce new services, databases, abstraction layers, or orchestration unless the active target demonstrably requires them.
- Never claim success from a file, adapter, mock, schema, or test alone.

## Latest local verification

Run on 2026-09-26:

- `uv run pytest` -> 259 passed, 0 failures across the test suite
- `uv run pytest tests/test_macro_decision.py -v` -> 6 passed
- `uv run python scripts/qa_repo.py` -> all required checks passed
- `uv run python -m ipos.cli weekly --seed-offline --as-of 2026-09-25 --provider none` -> completed with `status=OK`
- Independent adversarial proof verifier confirmed PASS for WF-07 Stage 4 / E08.

## Required reporting format for the next chat

Report using five concise lines:

- target
- intended_value
- current_verdict
- remaining_material_gap
- next_action
