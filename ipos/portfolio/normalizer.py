"""IPOS Deterministic Portfolio & Activity Normalizer (Module M11 / Correction C11).

Converts broker exports into canonical portfolio snapshots, activity records,
source manifests, and multi-state reconciliation reports with zero silent transaction drops.
"""

from typing import Dict, Any, List, Tuple, Optional, Union
import hashlib
import json
import os
import pandas as pd


CANONICAL_INSTRUMENT_FIELDS = ["instrument_id", "isin", "symbol", "name", "currency"]
CANONICAL_HOLDING_FIELDS = ["account", "instrument_id", "quantity", "cost_basis", "market_value", "as_of"]
CANONICAL_ACTIVITY_FIELDS = ["account", "timestamp", "type", "instrument_id", "quantity", "price", "gross", "fees", "taxes", "currency", "source_row_id"]

VALID_ACTIVITY_TYPES = ["BUY", "SELL", "DIVIDEND", "FEE", "DEPOSIT", "WITHDRAWAL", "TAX"]
VALID_CURRENCIES = ["EUR", "USD", "GBP", "CHF"]


class ValidationException(Exception):
    """Raised when canonical schema or row arithmetic validation fails."""
    pass


class ReconciliationException(Exception):
    """Raised when reconciliation verification fails against independent control."""
    pass


class PortfolioNormalizer:
    """Normalizes broker transactions into canonical data structures with strict multi-currency accounting."""

    def __init__(self, account_name: str = "DEFAULT_ACCOUNT"):
        self.account_name = account_name

    @staticmethod
    def compute_file_sha256(filepath: str) -> str:
        """Compute SHA-256 hash of raw input file."""
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    def validate_holdings(self, df_holdings: pd.DataFrame) -> None:
        """Validate canonical holdings schema."""
        for field in CANONICAL_HOLDING_FIELDS:
            if field not in df_holdings.columns:
                raise ValidationException(f"Missing required holding field: '{field}'")

        for idx, row in df_holdings.iterrows():
            if row["quantity"] < 0:
                raise ValidationException(f"Invalid negative quantity {row['quantity']} for instrument '{row['instrument_id']}'")
            if pd.notna(row["cost_basis"]) and row["cost_basis"] < 0:
                raise ValidationException(f"Invalid negative cost basis {row['cost_basis']} for instrument '{row['instrument_id']}'")

    def validate_activities(self, df_activities: pd.DataFrame) -> None:
        """Validate canonical activities schema, signs, and row arithmetic."""
        for field in CANONICAL_ACTIVITY_FIELDS:
            if field not in df_activities.columns:
                raise ValidationException(f"Missing required activity field: '{field}'")

        # Check duplicate source_row_id
        if df_activities["source_row_id"].duplicated().any():
            dups = df_activities[df_activities["source_row_id"].duplicated()]["source_row_id"].tolist()
            raise ValidationException(f"Duplicate source_row_id detected: {dups}")

        for idx, row in df_activities.iterrows():
            act_type = row["type"]
            if act_type not in VALID_ACTIVITY_TYPES:
                raise ValidationException(f"Invalid activity type '{act_type}' at row {row['source_row_id']}")
            if row["currency"] not in VALID_CURRENCIES:
                raise ValidationException(f"Invalid currency '{row['currency']}' at row {row['source_row_id']}")

            qty = float(row["quantity"])
            price = float(row["price"])
            gross = float(row["gross"])
            fees = float(row["fees"])
            taxes = float(row["taxes"])

            if qty < 0 or price < 0 or gross < 0 or fees < 0 or taxes < 0:
                raise ValidationException(f"Negative value detected in row {row['source_row_id']}")

            # Row arithmetic checks for trade actions
            if act_type in ("BUY", "SELL"):
                expected_gross = qty * price
                if abs(gross - expected_gross) > 0.01:
                    raise ValidationException(
                        f"Row arithmetic error at source_row_id {row['source_row_id']}: "
                        f"gross {gross} != qty {qty} * price {price} ({expected_gross})"
                    )

            # Standalone FEE row checks: non-overlapping contract
            if act_type == "FEE":
                if fees != 0.0 or taxes != 0.0:
                    raise ValidationException(
                        f"Standalone FEE at source_row_id {row['source_row_id']} must have fees=0.0 and taxes=0.0 to prevent double-counting"
                    )
                if gross <= 0.0:
                    raise ValidationException(f"Standalone FEE at source_row_id {row['source_row_id']} must have positive gross amount")

            # Standalone TAX row checks: non-overlapping contract
            if act_type == "TAX":
                if fees != 0.0 or taxes != 0.0:
                    raise ValidationException(
                        f"Standalone TAX at source_row_id {row['source_row_id']} must have fees=0.0 and taxes=0.0 to prevent double-counting"
                    )
                if gross <= 0.0:
                    raise ValidationException(f"Standalone TAX at source_row_id {row['source_row_id']} must have positive gross amount")

            # DIVIDEND checks
            if act_type == "DIVIDEND":
                if qty != 0.0:
                    raise ValidationException(f"DIVIDEND at source_row_id {row['source_row_id']} must have quantity 0.0")

            # DEPOSIT / WITHDRAWAL checks
            if act_type in ("DEPOSIT", "WITHDRAWAL"):
                if fees != 0.0 or taxes != 0.0:
                    raise ValidationException(f"{act_type} at source_row_id {row['source_row_id']} must have fees=0.0 and taxes=0.0")

    def normalize_csv_fixture(
        self,
        filepath: str,
        control_input: Optional[Union[str, Dict[str, Any]]] = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any], Dict[str, Any]]:
        """Normalize raw CSV fixture into canonical holdings, activities, manifest, and multi-currency reconciliation report."""
        file_sha256 = self.compute_file_sha256(filepath)

        df_raw = pd.read_csv(filepath)
        required_raw_cols = ["source_row_id", "timestamp", "type", "isin", "symbol", "name", "quantity", "price", "gross", "fees", "taxes", "currency"]
        for col in required_raw_cols:
            if col not in df_raw.columns:
                raise ValidationException(f"Corrupt source file: missing raw column '{col}'")

        activities: List[Dict[str, Any]] = []
        holdings_map: Dict[str, Dict[str, Any]] = {}

        for idx, row in df_raw.iterrows():
            if pd.isna(row["type"]) or pd.isna(row["source_row_id"]) or pd.isna(row["quantity"]):
                raise ValidationException(f"Corrupt row at index {idx}")

            inst_id = str(row["isin"]).strip() if pd.notna(row["isin"]) else str(row["symbol"]).strip()
            act_type = str(row["type"]).strip().upper()
            qty = float(row["quantity"])
            price = float(row["price"])
            gross = float(row["gross"])
            fees = float(row["fees"])
            taxes = float(row["taxes"])
            curr = str(row["currency"]).strip().upper()

            act_record = {
                "account": self.account_name,
                "timestamp": str(row["timestamp"]),
                "type": act_type,
                "instrument_id": inst_id,
                "quantity": qty,
                "price": price,
                "gross": gross,
                "fees": fees,
                "taxes": taxes,
                "currency": curr,
                "source_row_id": int(row["source_row_id"])
            }
            activities.append(act_record)

            # Update holdings map with Economic/Book Cost Basis
            # Valuation Timestamp Semantics: as_of is updated ONLY on trade valuation events (BUY, SELL),
            # never advanced on cash events like DIVIDEND that do not revalue market_value.
            if act_type == "BUY":
                if inst_id not in holdings_map:
                    holdings_map[inst_id] = {
                        "account": self.account_name,
                        "instrument_id": inst_id,
                        "quantity": 0.0,
                        "cost_basis": 0.0,
                        "market_value": 0.0,
                        "as_of": str(row["timestamp"])
                    }
                holdings_map[inst_id]["quantity"] += qty
                holdings_map[inst_id]["cost_basis"] += (gross + fees + taxes)
                holdings_map[inst_id]["market_value"] = holdings_map[inst_id]["quantity"] * price
                holdings_map[inst_id]["as_of"] = str(row["timestamp"])

            elif act_type == "SELL":
                if inst_id not in holdings_map or holdings_map[inst_id]["quantity"] < qty:
                    raise ValidationException(f"Oversell condition for instrument '{inst_id}' at row {row['source_row_id']}")

                curr_qty = holdings_map[inst_id]["quantity"]
                curr_basis = holdings_map[inst_id]["cost_basis"]

                # Weighted-average economic cost relief on sale
                relief_basis = (qty / curr_qty) * curr_basis
                holdings_map[inst_id]["quantity"] -= qty
                holdings_map[inst_id]["cost_basis"] -= relief_basis

                if holdings_map[inst_id]["quantity"] == 0.0:
                    holdings_map[inst_id]["cost_basis"] = 0.0

                holdings_map[inst_id]["market_value"] = holdings_map[inst_id]["quantity"] * price
                holdings_map[inst_id]["as_of"] = str(row["timestamp"])

            elif act_type == "DIVIDEND":
                # Do NOT advance as_of on DIVIDEND because market_value is not revalued
                pass

        df_activities = pd.DataFrame(activities)
        if holdings_map:
            df_holdings = pd.DataFrame(list(holdings_map.values()))
        else:
            df_holdings = pd.DataFrame(columns=CANONICAL_HOLDING_FIELDS)

        # Validate frames
        self.validate_activities(df_activities)
        self.validate_holdings(df_holdings)

        # Source manifest
        manifest = {
            "source_file": os.path.basename(filepath),
            "source_sha256": file_sha256,
            "total_source_rows": len(df_raw),
            "normalized_activities_count": len(df_activities),
            "account": self.account_name
        }

        # Multi-currency accounting: calculate totals PER CURRENCY (never sum across currencies)
        currencies = sorted(list(set(df_activities["currency"].unique()))) if not df_activities.empty else []
        summary_totals_by_currency: Dict[str, Dict[str, float]] = {}

        for curr in currencies:
            curr_acts = df_activities[df_activities["currency"] == curr]
            gross_buys = 0.0
            gross_sells = 0.0
            gross_divs = 0.0
            total_fees = 0.0
            total_taxes = 0.0
            net_cash_flow = 0.0

            for _, act in curr_acts.iterrows():
                t = act["type"]
                g = float(act["gross"])
                f = float(act["fees"])
                tx = float(act["taxes"])

                if t == "BUY":
                    gross_buys += g
                    total_fees += f
                    total_taxes += tx
                    net_cash_flow -= (g + f + tx)
                elif t == "SELL":
                    gross_sells += g
                    total_fees += f
                    total_taxes += tx
                    net_cash_flow += (g - f - tx)
                elif t == "DIVIDEND":
                    gross_divs += g
                    total_fees += f
                    total_taxes += tx
                    net_cash_flow += (g - f - tx)
                elif t == "DEPOSIT":
                    net_cash_flow += g
                elif t == "WITHDRAWAL":
                    net_cash_flow -= g
                elif t == "FEE":
                    total_fees += g
                    net_cash_flow -= g
                elif t == "TAX":
                    total_taxes += g
                    net_cash_flow -= g

            summary_totals_by_currency[curr] = {
                "gross_buys": round(gross_buys, 2),
                "gross_sells": round(gross_sells, 2),
                "gross_dividends": round(gross_divs, 2),
                "total_fees": round(total_fees, 2),
                "total_taxes": round(total_taxes, 2),
                "net_cash_flow": round(net_cash_flow, 2)
            }

        # Comprehensive Multi-Field Reconciliation against Independent Control
        control_data: Optional[Dict[str, Any]] = None
        if isinstance(control_input, str) and os.path.exists(control_input):
            with open(control_input, "r", encoding="utf-8-sig") as cf:
                control_data = json.load(cf)
        elif isinstance(control_input, dict):
            control_data = control_input

        checks: List[Dict[str, Any]] = []

        if control_data is not None:
            # 1. Check summary totals per currency
            # Support both control["summary_totals_by_currency"] and legacy single-currency control["summary_totals"]
            ctrl_by_curr = control_data.get("summary_totals_by_currency", {})
            if not ctrl_by_curr and "summary_totals" in control_data and len(currencies) == 1:
                ctrl_by_curr = {currencies[0]: control_data["summary_totals"]}

            for curr, expected_totals in ctrl_by_curr.items():
                actual_totals = summary_totals_by_currency.get(curr, {})
                for field in ["gross_buys", "gross_sells", "gross_dividends", "total_fees", "total_taxes", "net_cash_flow"]:
                    if field in expected_totals:
                        exp_val = float(expected_totals[field])
                        act_val = float(actual_totals.get(field, 0.0))
                        diff = round(abs(act_val - exp_val), 4)
                        status = "PASS" if diff <= 1e-4 else "FAIL"
                        checks.append({
                            "check": f"summary_totals.{curr}.{field}",
                            "expected": exp_val,
                            "actual": act_val,
                            "difference": diff,
                            "status": status
                        })

            # Top-level net_cash_flow fallback if control only had top-level net_cash_flow
            if not checks and "net_cash_flow" in control_data and len(currencies) == 1:
                curr = currencies[0]
                exp_val = float(control_data["net_cash_flow"])
                act_val = float(summary_totals_by_currency[curr]["net_cash_flow"])
                diff = round(abs(act_val - exp_val), 4)
                status = "PASS" if diff <= 1e-4 else "FAIL"
                checks.append({
                    "check": f"summary_totals.{curr}.net_cash_flow",
                    "expected": exp_val,
                    "actual": act_val,
                    "difference": diff,
                    "status": status
                })

            # 2. Check ending holdings balances
            if "ending_holdings" in control_data and isinstance(control_data["ending_holdings"], dict):
                for inst_id, expected_h in control_data["ending_holdings"].items():
                    actual_h_rows = df_holdings[df_holdings["instrument_id"] == inst_id]
                    actual_qty = float(actual_h_rows.iloc[0]["quantity"]) if not actual_h_rows.empty else 0.0
                    actual_basis = float(actual_h_rows.iloc[0]["cost_basis"]) if not actual_h_rows.empty else 0.0
                    actual_as_of = str(actual_h_rows.iloc[0]["as_of"]) if not actual_h_rows.empty else ""

                    if "quantity" in expected_h:
                        exp_qty = float(expected_h["quantity"])
                        diff_qty = round(abs(actual_qty - exp_qty), 4)
                        checks.append({
                            "check": f"holding.{inst_id}.quantity",
                            "expected": exp_qty,
                            "actual": actual_qty,
                            "difference": diff_qty,
                            "status": "PASS" if diff_qty <= 1e-4 else "FAIL"
                        })

                    # Check cost basis (support book_cost_basis or cost_basis key)
                    basis_key = "book_cost_basis" if "book_cost_basis" in expected_h else ("cost_basis" if "cost_basis" in expected_h else None)
                    if basis_key:
                        exp_basis = float(expected_h[basis_key])
                        diff_basis = round(abs(actual_basis - exp_basis), 4)
                        checks.append({
                            "check": f"holding.{inst_id}.cost_basis",
                            "expected": exp_basis,
                            "actual": actual_basis,
                            "difference": diff_basis,
                            "status": "PASS" if diff_basis <= 1e-4 else "FAIL"
                        })

                    if "as_of" in expected_h:
                        exp_as_of = str(expected_h["as_of"])
                        as_of_match = (actual_as_of == exp_as_of)
                        checks.append({
                            "check": f"holding.{inst_id}.as_of",
                            "expected": exp_as_of,
                            "actual": actual_as_of,
                            "difference": 0.0 if as_of_match else 1.0,
                            "status": "PASS" if as_of_match else "FAIL"
                        })

        if checks:
            all_pass = all(c["status"] == "PASS" for c in checks)
            if all_pass:
                rec_status = "BALANCED"
                rec_diff = 0.0
            else:
                rec_status = "MISMATCH"
                failed_diffs = [c["difference"] for c in checks if c["status"] == "FAIL"]
                rec_diff = round(sum(failed_diffs), 4)
        else:
            rec_status = "UNVERIFIABLE_NO_SOURCE_CONTROL"
            rec_diff = None

        reconciliation = {
            "account": self.account_name,
            "total_activities": len(df_activities),
            "summary_totals_by_currency": summary_totals_by_currency,
            "checks": checks,
            "reconciliation_difference": rec_diff,
            "reconciliation_status": rec_status
        }

        return df_holdings, df_activities, manifest, reconciliation
