# E02 status: real import proven; product reconciliation failed

Wealthfolio 3.8.0 was installed from the official Windows release and its
installer SHA-256 matched the release asset digest. The operator completed the
real five-step desktop import using the prepared Smartbroker activity file. The
last pre-import review showed 330 of 331 candidate rows valid; the product's
post-import state has now been inspected through a supported native backup.
The activity import itself reconciles, but Wealthfolio's computed holdings and
cash do not.

No Wealthfolio integration is claimed. IPOS remains fail-closed with
`INTEGRATION_STATUS = "NOT_CONNECTED"`. `SMARTBROKER_ORACLE.yaml` records the
redacted independent control derived directly from the original private broker
export. `WEALTHFOLIO_BACKUP_RECEIPT.yaml` and `RECONCILIATION_REPORT.md` record
the redacted native-product result. The broker file, prepared import, and
Wealthfolio backup remain outside Git.

The backup proves 330 posted activities, zero review flags, 34 custom assets,
and persisted FIFO lots. It also proves two material calculation gaps: the
computed holdings omit NDA 1,000 and PSYC 10,000, and the latest EUR cash is
overstated by EUR 41,037.75 because NDA buys did not enter the calculation while
NDA sell proceeds did. Resolve those two assets through a supported product-
native workflow and export a fresh backup before connecting IPOS. Direct live-
database mutation is not an acceptable fix.
