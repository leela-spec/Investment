# E02 CAD custom-asset remediation probe

This probe isolates the two Wealthfolio-computed holdings failures without
mutating or duplicating the proven imported account.

## Private probe file

- Path: `C:\Users\gehma\Downloads\wealthfolio-e02-cad-probe-2026-09-24.csv`
- SHA-256: `E2376B9EBE479DF0865D331E84BC0C2B42C3818D3BA0B6A97110295BABC64314`
- Rows: 28
- Git policy: keep outside Git.

The file contains only the 27 NDA rows and one PSYC row from the prepared v4
file. Their symbols were changed from resolved market tickers to their broker
ISINs so the native import review can create them as EUR custom assets. All
dates, types, quantities, settled-EUR prices, amounts, fees, taxes, and source
comments remain unchanged; the comment has an E02 probe suffix.

## Product-native procedure

1. Create a disposable EUR **Transactions** account named
   `IPOS E02 CAD Probe`.
2. Import the private probe through the normal five-step CSV workflow.
3. In **Review Assets**, explicitly keep both ISINs as custom assets with EUR
   quote/accounting currency; do not resolve them to the CAD market assets.
4. In **Review Activities**, confirm both `TRANSFER_IN` rows are external
   security transfers and that all 28 rows are valid.
5. Import, inspect holdings and cash, then create a new native backup.
6. Do not import this probe into the existing proven account.

## Independent acceptance oracle

| Control | Expected |
| --- | ---: |
| Activities | 28 |
| BUY | 16 |
| SELL | 10 |
| TRANSFER_IN | 2 |
| NDA / CA64073L1013 quantity | 1,000 |
| PSYC / CA74447P1009 quantity | 10,000 |
| BUY final amounts | EUR 41,037.75000050 |
| SELL final amounts | EUR 33,000.47002465 |
| Trade cash | EUR -8,037.27997585 |
| Buy fees | EUR 52.00 |
| Sell fees | EUR 18.00 |
| Taxes | EUR 0.00 |

Accept only if both holdings receive FIFO lots and Wealthfolio cash equals the
trade-cash oracle. If the custom-asset probe still drops the buys or holdings,
record the product limitation and keep E02 blocked rather than altering the live
database.
