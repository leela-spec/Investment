"""Coherent Portfolio Accounting & Multi-Currency Ledger (E04 / M11).

Provides double-entry cash and position tracking, weighted-average economic
cost basis, realized/unrealized capital gains, fee and tax auditing, and
reconciliation against independent broker control figures.
"""

from __future__ import annotations

import datetime as dt
from typing import Any, Dict, List, Optional, Tuple, Union
import pandas as pd

from ipos.portfolio.normalizer import (
    CANONICAL_ACTIVITY_FIELDS,
    CANONICAL_HOLDING_FIELDS,
    VALID_ACTIVITY_TYPES,
    VALID_CURRENCIES,
)


class HoldingPosition:
    """State of an individual asset holding."""

    def __init__(self, instrument_id: str, currency: str = "EUR"):
        self.instrument_id = instrument_id
        self.currency = currency
        self.quantity: float = 0.0
        self.total_cost: float = 0.0  # Total economic acquisition cost
        self.weighted_average_cost_basis: float = 0.0
        self.realized_pnl: float = 0.0
        self.total_bought_qty: float = 0.0
        self.total_sold_qty: float = 0.0
        self.last_trade_date: Optional[str] = None

    def apply_buy(self, quantity: float, gross: float, fees: float = 0.0, taxes: float = 0.0, timestamp: str = "") -> None:
        """Apply a BUY event, incorporating transaction fees into economic cost basis."""
        if quantity <= 0:
            return
        incidental_cost = gross + fees + taxes
        self.total_cost += incidental_cost
        self.quantity += quantity
        self.total_bought_qty += quantity
        self.weighted_average_cost_basis = self.total_cost / self.quantity if self.quantity > 0 else 0.0
        self.last_trade_date = timestamp

    def apply_sell(self, quantity: float, gross: float, fees: float = 0.0, taxes: float = 0.0, timestamp: str = "") -> float:
        """Apply a SELL event, reducing cost basis proportionally and calculating realized gain/loss."""
        if quantity <= 0:
            return 0.0
        if quantity > self.quantity + 1e-9:
            import logging
            logging.getLogger(__name__).warning(
                "SELL deficit for %s: selling %.4f with only %.4f in holding at %s",
                self.instrument_id, quantity, self.quantity, timestamp
            )
        # Basis of sold portion
        cost_of_sold = self.weighted_average_cost_basis * quantity
        net_proceeds = gross - fees - taxes
        gain_loss = net_proceeds - cost_of_sold

        self.realized_pnl += gain_loss
        self.total_cost -= cost_of_sold
        self.quantity -= quantity
        self.total_sold_qty += quantity

        if self.quantity <= 1e-9:
            # Position fully closed
            self.quantity = 0.0
            self.total_cost = 0.0
            self.weighted_average_cost_basis = 0.0
        else:
            self.weighted_average_cost_basis = self.total_cost / self.quantity

        self.last_trade_date = timestamp
        return gain_loss

    def apply_transfer_in(self, quantity: float, unit_cost: float = 0.0, timestamp: str = "") -> None:
        """Apply an incoming securities transfer."""
        if quantity <= 0:
            return
        cost = quantity * unit_cost
        self.total_cost += cost
        self.quantity += quantity
        self.total_bought_qty += quantity
        self.weighted_average_cost_basis = self.total_cost / self.quantity if self.quantity > 0 else 0.0
        self.last_trade_date = timestamp

    def apply_transfer_out(self, quantity: float, timestamp: str = "") -> None:
        """Apply an outgoing securities transfer."""
        if quantity <= 0:
            return
        if quantity > self.quantity + 1e-9:
            import logging
            logging.getLogger(__name__).warning(
                "TRANSFER_OUT deficit for %s: transferring %.4f with only %.4f in holding at %s",
                self.instrument_id, quantity, self.quantity, timestamp
            )
        cost_of_transferred = self.weighted_average_cost_basis * quantity
        self.total_cost -= cost_of_transferred
        self.quantity -= quantity
        self.total_sold_qty += quantity
        if self.quantity <= 1e-9:
            self.quantity = 0.0
            self.total_cost = 0.0
            self.weighted_average_cost_basis = 0.0
        self.last_trade_date = timestamp


class PortfolioLedger:
    """Multi-currency portfolio ledger and activity replay engine."""

    def __init__(self, account_name: str = "DEFAULT"):
        self.account_name = account_name
        self.cash_balances: Dict[str, float] = {c: 0.0 for c in VALID_CURRENCIES}
        self.positions: Dict[str, HoldingPosition] = {}
        self.cumulative_fees: Dict[str, float] = {c: 0.0 for c in VALID_CURRENCIES}
        self.cumulative_taxes: Dict[str, float] = {c: 0.0 for c in VALID_CURRENCIES}
        self.cumulative_dividends: Dict[str, float] = {c: 0.0 for c in VALID_CURRENCIES}
        self.cumulative_deposits: Dict[str, float] = {c: 0.0 for c in VALID_CURRENCIES}
        self.cumulative_withdrawals: Dict[str, float] = {c: 0.0 for c in VALID_CURRENCIES}
        self.total_realized_pnl: Dict[str, float] = {c: 0.0 for c in VALID_CURRENCIES}
        self.processed_activities_count: int = 0
        self.earliest_activity_date: Optional[str] = None
        self.latest_activity_date: Optional[str] = None

    def replay_activities(self, df_activities: pd.DataFrame) -> None:
        """Replay an activities DataFrame chronologically to build accurate portfolio state."""
        if df_activities.empty:
            return

        df_copy = df_activities.copy()
        # Inflows/buys execute before sales/withdrawals when timestamps are identical
        type_priority = {
            "DEPOSIT": 1,
            "TRANSFER_IN": 1,
            "BUY": 2,
            "DIVIDEND": 3,
            "SELL": 4,
            "TRANSFER_OUT": 4,
            "FEE": 5,
            "TAX": 5,
            "WITHDRAWAL": 6,
        }
        df_copy["_order"] = df_copy["type"].map(lambda t: type_priority.get(str(t).upper(), 9))

        # Sort by timestamp, execution type priority, and row id
        df_sorted = df_copy.sort_values(
            by=["timestamp", "_order", "source_row_id"], ascending=[True, True, True]
        ).reset_index(drop=True)

        for _, row in df_sorted.iterrows():
            self._process_single_activity(row)

    def _process_single_activity(self, row: pd.Series) -> None:
        act_type = str(row["type"]).upper()
        curr = str(row["currency"]).upper()
        if curr not in self.cash_balances:
            self.cash_balances[curr] = 0.0
            self.cumulative_fees[curr] = 0.0
            self.cumulative_taxes[curr] = 0.0
            self.cumulative_dividends[curr] = 0.0
            self.cumulative_deposits[curr] = 0.0
            self.cumulative_withdrawals[curr] = 0.0
            self.total_realized_pnl[curr] = 0.0

        ts = str(row["timestamp"])
        if not self.earliest_activity_date:
            self.earliest_activity_date = ts
        self.latest_activity_date = ts

        qty = float(row.get("quantity", 0.0))
        gross = float(row.get("gross", 0.0))
        fees = float(row.get("fees", 0.0))
        taxes = float(row.get("taxes", 0.0))
        inst_id = str(row.get("instrument_id", "")).strip()

        # Track fees and taxes
        self.cumulative_fees[curr] += fees
        self.cumulative_taxes[curr] += taxes

        if act_type == "DEPOSIT":
            self.cash_balances[curr] += gross
            self.cumulative_deposits[curr] += gross

        elif act_type == "WITHDRAWAL":
            self.cash_balances[curr] -= gross
            self.cumulative_withdrawals[curr] += gross

        elif act_type == "BUY":
            total_cash_outflow = gross + fees + taxes
            self.cash_balances[curr] -= total_cash_outflow

            if inst_id not in self.positions:
                self.positions[inst_id] = HoldingPosition(inst_id, currency=curr)
            self.positions[inst_id].apply_buy(qty, gross, fees, taxes, timestamp=ts)

        elif act_type == "SELL":
            net_cash_inflow = gross - fees - taxes
            self.cash_balances[curr] += net_cash_inflow

            if inst_id not in self.positions:
                self.positions[inst_id] = HoldingPosition(inst_id, currency=curr)
            gain_loss = self.positions[inst_id].apply_sell(qty, gross, fees, taxes, timestamp=ts)
            self.total_realized_pnl[curr] += gain_loss

        elif act_type == "DIVIDEND":
            net_div = gross - taxes - fees
            self.cash_balances[curr] += net_div
            self.cumulative_dividends[curr] += net_div

        elif act_type == "FEE":
            self.cash_balances[curr] -= gross
            self.cumulative_fees[curr] += gross

        elif act_type == "TAX":
            self.cash_balances[curr] -= gross
            self.cumulative_taxes[curr] += gross

        elif act_type == "TRANSFER_IN":
            if inst_id not in self.positions:
                self.positions[inst_id] = HoldingPosition(inst_id, currency=curr)
            price = float(row.get("price", 0.0))
            self.positions[inst_id].apply_transfer_in(qty, unit_cost=price, timestamp=ts)

        elif act_type == "TRANSFER_OUT":
            if inst_id in self.positions:
                self.positions[inst_id].apply_transfer_out(qty, timestamp=ts)

        self.processed_activities_count += 1

    def get_open_positions(self) -> Dict[str, HoldingPosition]:
        """Return all positions with non-zero open quantity."""
        return {k: pos for k, pos in self.positions.items() if pos.quantity > 1e-9}

    def to_canonical_holdings(
        self,
        valuation_prices: Optional[Dict[str, float]] = None,
        as_of: Optional[str] = None,
    ) -> pd.DataFrame:
        """Generate canonical holdings DataFrame from open ledger positions."""
        as_of_str = as_of or (self.latest_activity_date[:10] if self.latest_activity_date else dt.date.today().isoformat())
        prices = valuation_prices or {}

        records: List[Dict[str, Any]] = []
        for inst_id, pos in self.get_open_positions().items():
            market_price = prices.get(inst_id, pos.weighted_average_cost_basis)
            market_value = pos.quantity * market_price

            records.append({
                "account": self.account_name,
                "instrument_id": inst_id,
                "quantity": pos.quantity,
                "weighted_average_cost_basis": pos.weighted_average_cost_basis,
                "cost_basis_currency": pos.currency,
                "market_value": market_value,
                "valuation_currency": pos.currency,
                "as_of": as_of_str,
            })

        return pd.DataFrame(records, columns=CANONICAL_HOLDING_FIELDS)

    def to_ipos_positions(
        self,
        valuation_prices: Optional[Dict[str, float]] = None,
    ) -> pd.DataFrame:
        """Export open positions in the format expected by load_positions() / aggregate_portfolio."""
        holdings_df = self.to_canonical_holdings(valuation_prices)
        rows: List[Dict[str, Any]] = []
        for _, r in holdings_df.iterrows():
            qty = float(r["quantity"])
            val = float(r["market_value"])
            curr = str(r["valuation_currency"])
            price = val / qty if qty > 0 else 0.0
            rows.append({
                "instrument": str(r["instrument_id"]),
                "quantity": qty,
                "value_eur": val,
                "price_eur": price,
                "currency": curr,
            })
        return pd.DataFrame(rows, columns=["instrument", "quantity", "value_eur", "price_eur", "currency"])

    def reconciliation_report(
        self,
        external_cash_control: Optional[Dict[str, float]] = None,
        external_holdings_control: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """Produce an audit reconciliation summary comparing ledger state to independent controls."""
        open_pos = self.get_open_positions()
        holdings_summary = {
            k: {
                "quantity": pos.quantity,
                "weighted_average_cost_basis": pos.weighted_average_cost_basis,
                "currency": pos.currency,
                "realized_pnl": pos.realized_pnl,
            }
            for k, pos in open_pos.items()
        }

        cash_reconciliation = {}
        for curr, bal in self.cash_balances.items():
            ctrl = (external_cash_control or {}).get(curr)
            delta = (bal - ctrl) if ctrl is not None else None
            cash_reconciliation[curr] = {
                "ledger_balance": round(bal, 2),
                "control_balance": round(ctrl, 2) if ctrl is not None else None,
                "variance": round(delta, 2) if delta is not None else None,
            }

        holdings_variance = {}
        if external_holdings_control:
            all_keys = set(open_pos.keys()).union(external_holdings_control.keys())
            for k in all_keys:
                ledger_qty = open_pos[k].quantity if k in open_pos else 0.0
                ctrl_qty = external_holdings_control.get(k, 0.0)
                diff = ledger_qty - ctrl_qty
                if abs(diff) > 1e-4:
                    holdings_variance[k] = {
                        "ledger_quantity": ledger_qty,
                        "control_quantity": ctrl_qty,
                        "variance": diff,
                    }

        return {
            "account": self.account_name,
            "activities_replayed": self.processed_activities_count,
            "date_range": {
                "start": self.earliest_activity_date,
                "end": self.latest_activity_date,
            },
            "cash_balances": cash_reconciliation,
            "cumulative_totals": {
                "fees": {c: round(v, 2) for c, v in self.cumulative_fees.items() if v > 0},
                "taxes": {c: round(v, 2) for c, v in self.cumulative_taxes.items() if v > 0},
                "dividends": {c: round(v, 2) for c, v in self.cumulative_dividends.items() if v > 0},
                "deposits": {c: round(v, 2) for c, v in self.cumulative_deposits.items() if v > 0},
                "withdrawals": {c: round(v, 2) for c, v in self.cumulative_withdrawals.items() if v > 0},
                "realized_pnl": {c: round(v, 2) for c, v in self.total_realized_pnl.items() if abs(v) > 0},
            },
            "open_holdings_count": len(open_pos),
            "holdings_discrepancies": holdings_variance,
            "reconciliation_status": "MATCH" if not holdings_variance else "DISCREPANCY_DETECTED",
        }
