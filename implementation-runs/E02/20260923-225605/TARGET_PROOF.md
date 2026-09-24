target_product: Wealthfolio
expected_version: "3.8.0"
official_interface_to_use: "Native Windows desktop CSV import wizard, product UI inspection, and product-native export"
proof_action: "Import a controlled transaction portfolio with buys, partial sells, multiple currencies, fees, and taxes, then export Wealthfolio-computed state"
independent_oracle: "Hand-calculated transaction quantities and cash totals from an immutable representative fixture, reconciled to Wealthfolio UI/export"
facade_failure_example: "Generating a local CSV/JSON with Wealthfolio-like fields without the desktop product importing and exporting it"
