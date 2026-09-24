# E02 status: real import complete; product reconciliation pending

Wealthfolio 3.8.0 was installed from the official Windows release and its
installer SHA-256 matched the release asset digest. The operator completed the
real five-step desktop import using the prepared Smartbroker activity file. The
last pre-import review showed 330 of 331 candidate rows valid; the product's
post-import activity count, holdings, cash, review flags, and FIFO/lot output
still require native inspection or a supported Wealthfolio export.

No Wealthfolio integration is claimed. IPOS remains fail-closed with
`INTEGRATION_STATUS = "NOT_CONNECTED"`. `SMARTBROKER_ORACLE.yaml` records the
redacted independent control derived directly from the original private broker
export. The broker file and prepared import remain outside Git.

The current Codex desktop-control surface exposes no native Windows
applications, so this run could not inspect the imported Wealthfolio account or
operate its export/backup UI. The remaining step is deliberately product-native:
inspect the imported account and create a supported export/backup, then compare
that result to `SMARTBROKER_ORACLE.yaml`. Direct live-database access is not an
acceptable substitute.
