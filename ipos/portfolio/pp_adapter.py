"""Portfolio Performance (PP) Ingestion Adapter (E03 / M11).

Provides typed parsing and canonical normalization of Portfolio Performance
desktop CSV exports:
1. Activities / Transactions: `Buchungen.csv`
2. Holdings / Securities snapshot: `Vermögensaufstellung.csv` / `Wertpapiere.csv`

Supports German and English header dialects, semicolon/comma delimiters, and
locale-aware numeric parsing (decimal-comma / thousands-dot).
"""

from __future__ import annotations

import io
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd

from ipos.portfolio.normalizer import (
    CANONICAL_ACTIVITY_FIELDS,
    CANONICAL_HOLDING_FIELDS,
    VALID_ACTIVITY_TYPES,
    VALID_CURRENCIES,
    PortfolioNormalizer,
    ValidationException,
)

# Activity type mapping from PP terms to canonical IPOS activities
PP_ACTIVITY_TYPE_MAP: Dict[str, str] = {
    # German
    "kauf": "BUY",
    "verkauf": "SELL",
    "einlage": "DEPOSIT",
    "entnahme": "WITHDRAWAL",
    "dividende": "DIVIDEND",
    "gebühren": "FEE",
    "gebuehren": "FEE",
    "steuern": "TAX",
    "umbuchung (eingang)": "TRANSFER_IN",
    "umbuchung (ausgang)": "TRANSFER_OUT",
    "transfer (inbound)": "TRANSFER_IN",
    "transfer (outbound)": "TRANSFER_OUT",
    # English
    "buy": "BUY",
    "sell": "SELL",
    "deposit": "DEPOSIT",
    "removal": "WITHDRAWAL",
    "withdrawal": "WITHDRAWAL",
    "dividend": "DIVIDEND",
    "fees": "FEE",
    "fee": "FEE",
    "taxes": "TAX",
    "tax": "TAX",
}


def _sniff_delimiter_and_locale(header_line: str) -> Tuple[str, bool]:
    """Determine CSV delimiter and whether German number formatting is used."""
    count_semicolon = header_line.count(";")
    count_comma = header_line.count(",")
    sep = ";" if count_semicolon >= count_comma else ","
    # German headers typically contain umlauts or distinct German keywords
    german_patterns = (
        r"\bdatum\b",
        r"\btyp\b",
        r"\bbuchungswährung\b",
        r"\bbruttobetrag\b",
        r"\bgebühren\b",
        r"\bgebuehren\b",
        r"\bsteuern\b",
        r"\bstück\b",
        r"\bstueck\b",
        r"\bstücke\b",
        r"\bstuecke\b",
        r"\banteile\b",
        r"\bkurs\b",
        r"\beinstandskurs\b",
        r"\beinstandswert\b",
        r"\baktueller wert\b",
    )
    english_patterns = (
        r"\bdate\b",
        r"\btype\b",
        r"\bshares\b",
        r"\bamount\b",
        r"\bsecurity name\b",
        r"\btransaction currency\b",
    )
    lower_header = header_line.lower()
    has_german = any(re.search(p, lower_header) for p in german_patterns)
    has_english = any(re.search(p, lower_header) for p in english_patterns)
    if has_german and not has_english:
        is_german = True
    elif has_english and not has_german:
        is_german = False
    else:
        is_german = sep == ";" or has_german
    return sep, is_german


def _parse_numeric(val: Any, is_german: bool) -> float:
    """Parse numeric string to float with locale awareness."""
    if pd.isna(val) or val is None or val == "":
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip().replace("€", "").replace("$", "").replace("£", "").strip()
    if is_german:
        # e.g., "1.234,56" -> "1234.56"
        s = s.replace(".", "").replace(",", ".")
    else:
        # e.g., "1,234.56" -> "1234.56"
        s = s.replace(",", "")
    try:
        return float(s)
    except ValueError:
        return 0.0


def _clean_str(val: Any) -> str:
    if pd.isna(val) or val is None:
        return ""
    return str(val).strip()


class PortfolioPerformanceAdapter:
    """Ingestion and normalization adapter for Portfolio Performance CSV exports."""

    def __init__(self, default_account: str = "PORTFOLIO_PERFORMANCE"):
        self.default_account = default_account
        self.normalizer = PortfolioNormalizer(account_name=default_account)

    @classmethod
    def is_buchungen_export(cls, header_line: str) -> bool:
        """Check if header line matches a Portfolio Performance Buchungen / Transactions CSV."""
        hl = header_line.lower()
        has_date = bool(re.search(r"\b(datum|date)\b", hl))
        has_type = bool(re.search(r"\b(typ|type)\b", hl))
        has_security = bool(re.search(r"\b(wertpapier|security|isin|ticker|wkn)\b", hl))
        return has_date and has_type and has_security

    @classmethod
    def is_holdings_export(cls, header_line: str) -> bool:
        """Check if header line matches a Portfolio Performance Vermögensaufstellung / Holdings CSV."""
        hl = header_line.lower()
        if cls.is_buchungen_export(header_line):
            return False
        # Do not mistake broker position exports (e.g. Smartbroker/Zero) for PP holdings
        if "depotnummer" in hl or "kundennummer" in hl or "assetklasse" in hl:
            return False
        has_security = bool(re.search(r"\b(wertpapiername|security name|wertpapier)\b", hl))
        has_value = bool(re.search(r"\b(aktueller wert|current value|marktwert|market value|einstandswert|purchase value)\b", hl))
        has_shares = bool(re.search(r"\b(anzahl|stück|stueck|stücke|stuecke|shares|bestand)\b", hl))
        return has_security and (has_value or has_shares)

    @classmethod
    def is_smartbroker_activities_export(cls, header_line: str) -> bool:
        """Check if header line matches a Smartbroker / DAB transaction CSV export."""
        hl = header_line.lower()
        return "transaktionstyp" in hl and "status der transaktion" in hl and "isin" in hl

    def parse_smartbroker_activities(
        self,
        filepath_or_buffer: Union[str, Path, io.StringIO],
        account_name: Optional[str] = None,
    ) -> pd.DataFrame:
        """Parse Smartbroker transaction export (e.g. 3370191001-*.csv) into canonical activities."""
        acct = account_name or "SMARTBROKER"
        if isinstance(filepath_or_buffer, (str, Path)):
            raw_bytes = Path(filepath_or_buffer).read_bytes()
            try:
                text = raw_bytes.decode("utf-8-sig")
            except UnicodeDecodeError:
                text = raw_bytes.decode("cp1252")
            stream = io.StringIO(text)
        else:
            stream = filepath_or_buffer

        df_raw = pd.read_csv(stream, sep=",", dtype=str)
        status_col = next((c for c in df_raw.columns if "STATUS" in c.upper()), None)
        if status_col:
            df_raw = df_raw[df_raw[status_col].str.upper() == "CONFIRMED"].copy()

        # Smartbroker exports are reverse-chronological (row 0 is latest trade).
        # Reverse the confirmed rows so that activities are ordered chronologically,
        # ensuring intraday buy/sell sequences replay in the exact order they occurred.
        df_raw = df_raw.iloc[::-1].reset_index(drop=True)

        activities: List[Dict[str, Any]] = []
        for idx, r in df_raw.iterrows():
            tt = str(r.get("TRANSAKTIONSTYP", "")).strip().upper()
            if tt == "BUY":
                act_type = "BUY"
            elif tt == "SELL":
                act_type = "SELL"
            elif tt == "ENTERINTOSECACCOUNT":
                act_type = "TRANSFER_IN"
            elif tt == "TAKEOFFSECACCOUNT":
                act_type = "TRANSFER_OUT"
            else:
                continue

            qty = abs(_parse_numeric(r.get("STÜCKE", 0.0), is_german=True))
            gross = abs(_parse_numeric(r.get("ANLAGEBETRAG IN KONTOWÄHRUNG", 0.0), is_german=True))
            fees = abs(_parse_numeric(r.get("GEBÜHREN IN KONTOWÄHRUNG", 0.0), is_german=True))
            taxes = abs(_parse_numeric(r.get("STEUERN IN KONTOWÄHRUNG", 0.0), is_german=True))
            isin = str(r.get("ISIN", "")).strip()
            ts = str(r.get("VALUTADATUM") or r.get("DATUM") or "")
            if "t" not in ts.lower() and len(ts) == 10:
                ts = f"{ts}T12:00:00"
            price = gross / qty if qty > 0 else 0.0

            activities.append({
                "account": acct,
                "timestamp": ts,
                "type": act_type,
                "instrument_id": isin,
                "quantity": qty,
                "price": price,
                "gross": gross,
                "fees": fees,
                "taxes": taxes,
                "currency": "EUR",
                "source_row_id": idx + 1,
            })

        return pd.DataFrame(activities, columns=CANONICAL_ACTIVITY_FIELDS)

    def parse_buchungen(
        self,
        filepath_or_buffer: Union[str, Path, io.StringIO],
        account_name: Optional[str] = None,
    ) -> pd.DataFrame:
        """Parse PP Buchungen.csv into canonical activities DataFrame.

        Columns produced:
        account, timestamp, type, instrument_id, quantity, price, gross, fees, taxes, currency, source_row_id
        """
        acct = account_name or self.default_account
        if isinstance(filepath_or_buffer, (str, Path)):
            raw_bytes = Path(filepath_or_buffer).read_bytes()
            try:
                text = raw_bytes.decode("utf-8-sig")
            except UnicodeDecodeError:
                text = raw_bytes.decode("cp1252")
            stream = io.StringIO(text)
        else:
            stream = filepath_or_buffer

        lines = [line for line in stream.read().splitlines() if line.strip()]
        if not lines:
            return pd.DataFrame(columns=CANONICAL_ACTIVITY_FIELDS)

        header = lines[0]
        sep, is_german = _sniff_delimiter_and_locale(header)

        df_raw = pd.read_csv(io.StringIO("\n".join(lines)), sep=sep, dtype=str)
        # Normalize column names
        col_map = {col: col.strip().lower() for col in df_raw.columns}
        df_raw.rename(columns=col_map, inplace=True)

        # Helper to find column from candidates
        def find_col(*candidates: str) -> Optional[str]:
            for c in candidates:
                if c in df_raw.columns:
                    return c
            return None

        col_date = find_col("datum", "date")
        col_type = find_col("typ", "type")
        col_value = find_col("wert", "value", "net amount", "nettobetrag")
        col_gross = find_col("bruttobetrag", "gross amount")
        col_curr = find_col("buchungswährung", "transaction currency", "währung", "currency")
        col_fees = find_col("gebühren", "gebuehren", "fees", "fee")
        col_taxes = find_col("steuern", "taxes", "tax")
        col_shares = find_col("stück", "stueck", "shares", "anzahl")
        col_isin = find_col("isin")
        col_wkn = find_col("wkn")
        col_ticker = find_col("ticker-symbol", "ticker symbol", "ticker")
        col_name = find_col("wertpapiername", "security name", "name")

        activities: List[Dict[str, Any]] = []

        for idx, row in df_raw.iterrows():
            raw_type = _clean_str(row.get(col_type) if col_type else "").lower()
            act_type = PP_ACTIVITY_TYPE_MAP.get(raw_type)
            if not act_type:
                # If unknown or notes-only row, skip
                continue

            raw_date = _clean_str(row.get(col_date) if col_date else "")
            # Ensure ISO-8601 formatting for date
            if "t" not in raw_date.lower() and len(raw_date) == 10:
                # e.g., "2026-09-24"
                timestamp = f"{raw_date}T12:00:00"
            else:
                timestamp = raw_date

            curr = _clean_str(row.get(col_curr) if col_curr else "EUR").upper()
            if curr not in VALID_CURRENCIES:
                curr = "EUR"

            qty = abs(_parse_numeric(row.get(col_shares) if col_shares else 0.0, is_german))
            fees = abs(_parse_numeric(row.get(col_fees) if col_fees else 0.0, is_german))
            taxes = abs(_parse_numeric(row.get(col_taxes) if col_taxes else 0.0, is_german))
            gross_val = abs(_parse_numeric(row.get(col_gross) if col_gross else 0.0, is_german))
            net_val = abs(_parse_numeric(row.get(col_value) if col_value else 0.0, is_german))

            if gross_val == 0.0:
                gross_val = net_val

            # Resolve instrument identifier: ISIN > Ticker > WKN > Name
            isin = _clean_str(row.get(col_isin) if col_isin else "")
            ticker = _clean_str(row.get(col_ticker) if col_ticker else "")
            wkn = _clean_str(row.get(col_wkn) if col_wkn else "")
            name = _clean_str(row.get(col_name) if col_name else "")

            inst_id = isin or ticker or wkn or name or "CASH"

            price = gross_val / qty if qty > 0 else 0.0

            # Standalone fee or tax activities: non-overlapping contract
            if act_type == "FEE":
                gross_val = fees if fees > 0 else gross_val
                fees = 0.0
                taxes = 0.0
                qty = 0.0
                price = 0.0
            elif act_type == "TAX":
                gross_val = taxes if taxes > 0 else gross_val
                fees = 0.0
                taxes = 0.0
                qty = 0.0
                price = 0.0
            elif act_type in ("DEPOSIT", "WITHDRAWAL", "DIVIDEND"):
                qty = 0.0
                price = 0.0

            act_record = {
                "account": acct,
                "timestamp": timestamp,
                "type": act_type,
                "instrument_id": inst_id,
                "quantity": qty,
                "price": price,
                "gross": gross_val,
                "fees": fees,
                "taxes": taxes,
                "currency": curr,
                "source_row_id": idx + 1,
            }
            activities.append(act_record)

        df_out = pd.DataFrame(activities, columns=CANONICAL_ACTIVITY_FIELDS)
        return df_out

    def parse_holdings(
        self,
        filepath_or_buffer: Union[str, Path, io.StringIO],
        account_name: Optional[str] = None,
        as_of: Optional[str] = None,
    ) -> pd.DataFrame:
        """Parse PP Vermögensaufstellung / Wertpapiere CSV into canonical holdings DataFrame."""
        acct = account_name or self.default_account
        as_of_date = as_of or pd.Timestamp.now().strftime("%Y-%m-%d")

        if isinstance(filepath_or_buffer, (str, Path)):
            raw_bytes = Path(filepath_or_buffer).read_bytes()
            try:
                text = raw_bytes.decode("utf-8-sig")
            except UnicodeDecodeError:
                text = raw_bytes.decode("cp1252")
            stream = io.StringIO(text)
        else:
            stream = filepath_or_buffer

        lines = [line for line in stream.read().splitlines() if line.strip()]
        if not lines:
            return pd.DataFrame(columns=CANONICAL_HOLDING_FIELDS)

        header = lines[0]
        sep, is_german = _sniff_delimiter_and_locale(header)

        df_raw = pd.read_csv(io.StringIO("\n".join(lines)), sep=sep, dtype=str)
        col_map = {col: col.strip().lower() for col in df_raw.columns}
        df_raw.rename(columns=col_map, inplace=True)

        def find_col(*candidates: str) -> Optional[str]:
            for c in candidates:
                if c in df_raw.columns:
                    return c
            return None

        col_isin = find_col("isin")
        col_wkn = find_col("wkn")
        col_ticker = find_col("ticker-symbol", "ticker symbol", "ticker")
        col_name = find_col("wertpapiername", "security name", "name")
        col_shares = find_col("anzahl", "stück", "stueck", "stücke", "stuecke", "shares", "bestand")
        col_val = find_col("aktueller wert", "current value", "marktwert", "market value", "wert")
        col_basis = find_col("einstandswert", "purchase value", "kaufwert", "cost basis", "einstandspreis")
        col_curr = find_col("währung", "waehrung", "currency")

        holdings: List[Dict[str, Any]] = []

        for _, row in df_raw.iterrows():
            isin = _clean_str(row.get(col_isin) if col_isin else "")
            ticker = _clean_str(row.get(col_ticker) if col_ticker else "")
            wkn = _clean_str(row.get(col_wkn) if col_wkn else "")
            name = _clean_str(row.get(col_name) if col_name else "")

            inst_id = isin or ticker or wkn or name
            if not inst_id:
                continue

            qty = _parse_numeric(row.get(col_shares) if col_shares else 0.0, is_german)
            market_val = _parse_numeric(row.get(col_val) if col_val else 0.0, is_german)
            cost_basis_val = _parse_numeric(row.get(col_basis) if col_basis else 0.0, is_german)
            curr = _clean_str(row.get(col_curr) if col_curr else "EUR").upper()
            if curr not in VALID_CURRENCIES:
                curr = "EUR"

            # Skip zero holdings
            if qty <= 0 and market_val <= 0:
                continue

            unit_cost = cost_basis_val / qty if qty > 0 else 0.0

            holdings.append({
                "account": acct,
                "instrument_id": inst_id,
                "quantity": qty,
                "weighted_average_cost_basis": unit_cost,
                "cost_basis_currency": curr,
                "market_value": market_val,
                "valuation_currency": curr,
                "as_of": as_of_date,
            })

        df_out = pd.DataFrame(holdings, columns=CANONICAL_HOLDING_FIELDS)
        return df_out

    def to_ipos_positions(self, df_holdings_or_path: Union[pd.DataFrame, str, Path]) -> pd.DataFrame:
        """Convert PP holdings into the DataFrame format expected by load_positions() / aggregate_portfolio.

        Columns: instrument, quantity, value_eur, price_eur, currency
        """
        if not isinstance(df_holdings_or_path, pd.DataFrame):
            df_holdings = self.parse_holdings(df_holdings_or_path)
        else:
            df_holdings = df_holdings_or_path

        rows: List[Dict[str, Any]] = []
        for _, r in df_holdings.iterrows():
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
