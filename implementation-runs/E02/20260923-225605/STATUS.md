# E02 status: native acceptance pending

Wealthfolio 3.8.0 was installed from the official Windows release and its
installer SHA-256 matched the release asset digest. The native import/export
workflow has not yet been exercised because this task's computer-use bridge
does not expose Windows applications. The bridge advertises native-app support
but returns no applications and its runtime has no `getApp` function.

No Wealthfolio integration is claimed. IPOS remains fail-closed with
`INTEGRATION_STATUS = "NOT_CONNECTED"`. The representative fixture and
independent oracle in this directory are retained for a future native-product
acceptance run.

The fixture now follows Wealthfolio 3.8's documented native CSV semantics:
cash rows leave symbol, quantity, and unit price blank; `amount` is the final
cash total; and an omitted `fxRate` preserves the activity-currency cash
balance. The remaining step is deliberately product-native: import and inspect
the result in Wealthfolio, then use a supported export/read interface.
