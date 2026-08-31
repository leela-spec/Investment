"""IPOS Deterministic Portfolio & Activity Normalizer (Module M11 / Correction C11).

Converts broker exports into canonical portfolio snapshots, activity records,
source manifests, and multi-state reconciliation reports with zero silent transaction drops.
"""

from typing import Dict, Any, List, Tuple, Optional, Union
import hashlib
import json
import math
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
    """Normalizes broker transactions into canonical data structures with strict accounting."""

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
        """Normalize raw CSV fixture into canonical holdings, activities, manifest, and reconciliation report."""
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
            # Note: This is economic/book cost basis and does not claim to represent German tax-lot accounting.
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
                if inst_id in holdings_map:
                    holdings_map[inst_id]["as_of"] = str(row["timestamp"])

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

        # Calculate directional cash flow and summary totals
        gross_buys = 0.0
        gross_sells = 0.0
        gross_divs = 0.0
        total_fees = 0.0
        total_taxes = 0.0
        net_cash_flow = 0.0

        for act in activities:
            t = act["type"]
            g = act["gross"]
            f = act["fees"]
            tx = act["taxes"]

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

        summary_totals = {
            "gross_buys": round(gross_buys, 2),
            "gross_sells": round(gross_sells, 2),
            "gross_dividends": round(gross_divs, 2),
            "total_fees": round(total_fees, 2),
            "total_taxes": round(total_taxes, 2),
            "net_cash_flow": round(net_cash_flow, 2)
        }

        # Reconciliation against independent source control
        control_data: Optional[Dict[str, Any]] = None
        if isinstance(control_input, str) and os.path.exists(control_input):
            with open(control_input, "r", encoding="utf-8-sig") as cf:
                control_data = json.load(cf)
        elif isinstance(control_input, dict):
            control_data = control_input

        if control_data is not None:
            expected_net = None
            if "summary_totals" in control_data and "net_cash_flow" in control_data["summary_totals"]:
                expected_net = float(control_data["summary_totals"]["net_cash_flow"])
            elif "net_cash_flow" in control_data:
                expected_net = float(control_data["net_cash_flow"])

            if expected_net is not None:
                diff = abs(summary_totals["net_cash_flow"] - expected_net)
                if diff <= 1e-4:
                    rec_status = "BALANCED"
                    rec_diff = round(diff, 4)
                else:
                    rec_status = "MISMATCH"
                    rec_diff = round(diff, 4)
            else:
                rec_status = "UNVERIFIABLE_NO_SOURCE_CONTROL"
                rec_diff = None
        else:
            rec_status = "UNVERIFIABLE_NO_SOURCE_CONTROL"
            rec_diff = None

        reconciliation = {
            "account": self.account_name,
            "total_activities": len(df_activities),
            "summary_totals": summary_totals,
            "reconciliation_difference": rec_diff,
            "reconciliation_status": rec_status
        }

        return df_holdings, df_activities, manifest, reconciliation
