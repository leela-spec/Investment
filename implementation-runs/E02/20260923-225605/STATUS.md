# E02 status: real import proven; partial product proof accepted (non-blocking)

Wealthfolio 3.8.0 was installed from the official Windows release and its
installer SHA-256 matched the release asset digest. The operator completed the
real five-step desktop import using the prepared Smartbroker activity file. The
330 posted activities reconcile to the independent Smartbroker oracle with zero
review flags, 34 custom assets, and persisted FIFO lots.

Per operator directive, this completed real product import is accepted as
sufficient partial E02 product proof. The remaining calculation discrepancies
(computed holdings omit NDA 1,000 and PSYC 10,000; latest EUR cash is overstated
by EUR 41,037.75 due to omitted CAD-resolved BUY final amounts; and lot engine
coverage covers 21 of 23 positions) are recorded as explicit non-blocking gaps.
They do not block advancing the canonical IPOS architecture.

To prevent any inaccurate product calculations from polluting downstream
accounting, IPOS remains fail-closed at the Wealthfolio visualization bridge:
`ipos/portfolio/wealthfolio.py` retains `INTEGRATION_STATUS = "NOT_CONNECTED"`.
Execution advances to the next pipeline-critical capabilities: E03 (broker
document ingestion via Portfolio Performance) and E04 (coherent portfolio
accounting and transaction history).

