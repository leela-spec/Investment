# Wealthfolio 3.8 native acceptance

Official product references:

- [CSV import](https://wealthfolio.app/docs/guide/csv-import/)
- [Activity fields and currency behavior](https://wealthfolio.app/docs/concepts/activity-fields/)
- [Cost basis and lots](https://wealthfolio.app/docs/concepts/cost-basis-and-lots/)
- [Export and backup](https://wealthfolio.app/docs/guide/data-export/)
- [MCP server](https://wealthfolio.app/docs/guide/mcp-server/)

Use a disposable **Transactions** account named `IPOS E02 Disposable` with
account currency EUR. Import `representative_activities.csv` through
Activities → Import CSV. The v3.8 wizard should show six rows and guide the
operator through Upload, Mapping, Review Assets, Review Activities, and Import.

Accept only when the product itself shows:

1. Six posted activities with no unresolved review flags.
2. SAP.DE quantity 9 and SPY quantity 4.
3. EUR cash 1129 and USD cash 197.
4. Charges preserved as EUR fees 9/tax 2 and USD fee 2/tax 1.
5. Wealthfolio's lot/cost view distinguishes its FIFO result from IPOS's
   weighted-average economic basis.
6. Re-importing the identical file reports all six rows as duplicates and
   imports zero new activities.
7. A supported product export/read interface exposes enough activity and lot
   provenance for IPOS without direct SQLite access or invented backup JSON.

Market values may move with quotes; they are not part of this acceptance
oracle. If asset resolution, FX, or review status is unresolved, stop at the
review step and record the product's actual message instead of forcing import.
