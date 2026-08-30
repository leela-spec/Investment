"""Wealthfolio Local Visualization Bridge (Module M12).

Provides deterministic CSV export formatting, backup JSON generation, and read-only MCP representation
for local Wealthfolio portfolio visualization without live broker connect dependencies.
"""

from typing import Dict, Any, List
import json
import pandas as pd


WEALTHFOLIO_CSV_COLUMNS = ["Date", "Type", "Symbol", "Name", "Quantity", "Price", "Amount", "Fee", "Tax", "Currency"]


class WealthfolioAdapter:
    """Bridge converting canonical M11 portfolio data to Wealthfolio CSV & backup formats."""

    @staticmethod
    def to_wealthfolio_csv(df_activities: pd.DataFrame) -> pd.DataFrame:
        """Convert canonical activities dataframe to Wealthfolio CSV import format."""
        records = []
        for idx, row in df_activities.iterrows():
            # Map canonical type to Wealthfolio type
            act_type = str(row["type"]).upper()
            wf_type = act_type
            if act_type == "BUY":
                wf_type = "Buy"
            elif act_type == "SELL":
                wf_type = "Sell"
            elif act_type == "DIVIDEND":
                wf_type = "Dividend"
            elif act_type == "FEE":
                wf_type = "Fee"

            records.append({
                "Date": str(row["timestamp"]),
                "Type": wf_type,
                "Symbol": str(row["instrument_id"]),
                "Name": str(row["instrument_id"]),
                "Quantity": float(row["quantity"]),
                "Price": float(row["price"]),
                "Amount": float(row["gross"]),
                "Fee": float(row["fees"]),
                "Tax": float(row["taxes"]),
                "Currency": str(row["currency"])
            })

        df_wf = pd.DataFrame(records, columns=WEALTHFOLIO_CSV_COLUMNS)
        return df_wf

    @staticmethod
    def generate_backup_export(df_holdings: pd.DataFrame, df_activities: pd.DataFrame) -> Dict[str, Any]:
        """Generate local Wealthfolio JSON backup payload."""
        holdings_list = df_holdings.to_dict(orient="records")
        activities_list = df_activities.to_dict(orient="records")
        
        return {
            "version": "1.0",
            "app": "Wealthfolio",
            "backup_timestamp": "2026-08-30T21:45:30Z",
            "data": {
                "holdings": holdings_list,
                "activities": activities_list
            }
        }

    @staticmethod
    def mcp_read_holdings(df_holdings: pd.DataFrame) -> Dict[str, Any]:
        """Read-only MCP interface serving portfolio holdings and total market value."""
        total_val = float(df_holdings["market_value"].sum()) if "market_value" in df_holdings.columns else 0.0
        return {
            "status": "SUCCESS",
            "access_level": "READ_ONLY",
            "total_market_value": total_val,
            "holdings_count": len(df_holdings),
            "holdings": df_holdings.to_dict(orient="records")
        }

    @staticmethod
    def mcp_write_action(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Attempting a write action on initial scope read-only MCP token must be rejected."""
        raise PermissionError("Mutation/Write action rejected: Wealthfolio MCP token is READ_ONLY in initial scope")
