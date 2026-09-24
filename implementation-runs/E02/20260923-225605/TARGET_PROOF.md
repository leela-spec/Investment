target_product: Wealthfolio
expected_version: "3.8.0"
official_interface_to_use: "Native Windows desktop CSV import wizard plus Settings -> Backup & Export -> Backup"
proof_action: "Import the transformed real Smartbroker transaction ledger and reconcile the product-computed state from a native Wealthfolio backup"
independent_oracle: "Quantities, EUR trade cash, fees, taxes, and custom-asset identities computed from the original hash-identified Smartbroker export, not from Wealthfolio output"
facade_failure_example: "Generating a local CSV/JSON/SQLite file with Wealthfolio-like fields without a native product import receipt, persisted FIFO lots, and product-computed snapshots"
