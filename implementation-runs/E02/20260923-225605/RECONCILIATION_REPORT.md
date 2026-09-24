# E02 Wealthfolio native-backup reconciliation

## Verdict

**FAIL-CLOSED.** The real Wealthfolio 3.8.0 import and supported backup are
proven, but the product-computed portfolio does not reconcile to the original
Smartbroker export. IPOS must not consume this state yet.

The private native backup remains outside Git. Only its hash, product receipts,
and redacted aggregate results are recorded here.

## Product boundary proof

- Supported interface: Wealthfolio **Settings -> Backup & Export -> Backup**.
- Export: `C:\Users\gehma\Downloads\wealthfolio_backup_20260924_140842.db`.
- SHA-256: `92001DC95B88C20108EA2A9C9762B7998C9251A717145904046D75AA35233CE6`.
- Export timestamp: 2026-09-24 14:08:42 Europe/Berlin.
- SQLite `quick_check`: `ok`.
- The product-native `import_runs` receipt says `APPLIED`, 330 fetched and
  inserted, zero skipped, zero warnings, and zero errors.

This is a supported exported backup, not the live application database. The
inspection was read-only.

## Reconciliation matrix

| Pass condition | Real Wealthfolio proof | Independent broker oracle | Verdict |
| --- | --- | --- | --- |
| Imported activity count | 330 persisted activities; import receipt inserted 330 | 332 confirmed rows minus one combined sell and one rejected CVR = 330 | PASS |
| Review/draft/error state | 330 POSTED; zero `needs_review`; import warnings/errors zero | Expected zero after completed review | PASS |
| Activity-type counts | BUY 149, SELL 155, TRANSFER_IN 20, TRANSFER_OUT 6 | Source-derived transformed counts | PASS |
| Per-security activity-ledger quantity | 23 non-zero net quantities after resolving four product-normalized ticker suffixes | 23 non-zero quantities in `SMARTBROKER_ORACLE.yaml` | PASS |
| Computed holdings | Latest snapshot/open lots contain 21 non-zero positions | 23 expected | **FAIL** |
| EUR trade cash | Latest Wealthfolio snapshot: EUR 45,560.75002311 | Sells EUR 683,332.68 minus buys EUR 678,809.68 = EUR 4,523.00 | **FAIL** |
| Fees and taxes | Buy fees EUR 240.72; sell fees EUR 217.55; taxes EUR 0 | Same values from original broker export | PASS |
| Custom assets | Exact 34-ISIN set uses manual quote mode | Prepared-file custom set after rejected CVR and natively resolved JE00BDD9Q840 are excluded | PASS |
| FIFO attribution | Account configuration and all persisted lots/disposals say FIFO | Must remain distinct from IPOS weighted-average basis | PASS WITH INCOMPLETE COVERAGE |
| Supported export/read surface | Native backup contains typed product tables and import receipts | Official Wealthfolio export/backup contract | PASS |

## Material discrepancies

Two valid broker positions exist in the posted activity ledger but are absent
from Wealthfolio's computed holdings and lots:

- `CA64073L1013` / product code `NDA`: expected 1,000 units, computed holding 0.
- `CA74447P1009` / product code `PSYC`: expected 10,000 units, computed holding 0.

Both are CAD-quoted resolved assets whose imported activities use the correct
EUR settlement currency. Their external `TRANSFER_IN` activities are posted
and carry `metadata.flow.is_external = true`, but neither transfer created a
lot. All 16 NDA BUY activities also failed to create lots. Wealthfolio still
included all ten NDA SELL proceeds in cash.

This failure is isolated by product quote currency in this dataset: the two CAD
assets are the only activity-linked assets without any persisted lot, while all
38 EUR assets and all 13 USD assets have persisted lots. This correlation does
not by itself prove the internal cause, but it gives a narrow product-native
remediation test without changing the broker accounting.

The resulting cash defect is exact:

- expected net trade cash: EUR 4,523.00002261 (EUR 4,523.00 rounded);
- latest Wealthfolio cash: EUR 45,560.75002311;
- overstatement: EUR 41,037.75000050;
- sum of the 16 NDA BUY final amounts omitted by the product calculation:
  EUR 41,037.75000050.

This is not a market-price difference. It changes holdings, cash, cost basis,
and portfolio value.

## Wealthfolio FIFO evidence

The account explicitly stores `costBasisMethod = FIFO`. The backup contains
151 FIFO lots and 235 FIFO disposal records. For the 21 positions that reached
the lot engine, the latest snapshot contains EUR 39,456.43166667 account-
currency cost basis. The persisted native-currency remaining basis is EUR/
asset-currency 42,740.88 in aggregate and must not be treated as one clean EUR
number.

FIFO is therefore genuinely invoked and attributable to Wealthfolio, but its
portfolio result is incomplete because NDA and PSYC never reached the lot
engine. IPOS weighted-average economic basis remains a separate concept.

## Required resolution

Do not change `ipos/portfolio/wealthfolio.py` or
`INTEGRATION_STATUS = "NOT_CONNECTED"` yet. Resolve the two affected assets in
Wealthfolio through a product-native workflow, then create a new backup and
rerun this reconciliation. A plausible next controlled attempt is a disposable
account where `NDA` and `PSYC` are kept as EUR-denominated custom assets rather
than resolved CAD market assets; do not mutate the proven account until that
behavior is confirmed.

Official semantics used for interpretation:

- https://wealthfolio.app/docs/guide/data-export/
- https://wealthfolio.app/docs/concepts/activity-types/
- https://wealthfolio.app/docs/concepts/activity-fields/
- https://wealthfolio.app/docs/concepts/cost-basis-and-lots/
