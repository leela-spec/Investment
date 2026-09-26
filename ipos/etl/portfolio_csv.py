"""Portfolio connector — the optional "actual holdings" input for the
Portfolio vs. Stance module (``05_blueprint/03_PORTFOLIO_MODULE.md``).

Matches ``data/inbox/portfolio*.csv`` (latest file wins, same convention as
``manual_csv.py``). Unlike a registry-driven series, this file is never
required: absent inbox file -> ``load_positions`` returns ``None`` and the
whole module is omitted downstream (fail-degraded, never a hard dependency).

Broker exports vary in locale: this parses both plain English/comma-decimal
CSVs and German-locale exports (semicolon-delimited, decimal-comma/
thousands-dot numbers, ISIN/Anzahl/Wert/Kurs columns — the shape of a real
finanzen.net Zero export, confirmed 2026-07-27) via delimiter sniffing.
"""

from __future__ import annotations

import datetime as dt
import io
import math
from pathlib import Path
import re
import zlib

import pandas as pd

from ipos.config.load import REPO_ROOT

INBOX = REPO_ROOT / "data" / "inbox"
GLOB = "portfolio*.csv"
PORTFOLIO_PATTERNS = (
    "portfolio*.csv",
    "ZERO-pos*.csv",
    "zero-pos*.csv",
    "3370191001*.pdf",
    "3370191001*.csv",
    "portfolio*.pdf",
    "*Depot*.pdf",
    "*depot*.pdf",
    "Buchungen*.csv",
    "buchungen*.csv",
    "Vermögensaufstellung*.csv",
    "vermoegensaufstellung*.csv",
    "Wertpapiere*.csv",
    "wertpapiere*.csv",
    "pp-*.csv",
    "PP-*.csv",
)

# Column-name candidates, English first, then the German broker-export names
# seen in the wild (finanzen.net Zero: ISIN/Anzahl/Wert/Kurs). ISIN is
# preferred over a free-text name since configs/portfolio_mapping.yaml maps
# by verbatim ISIN/ticker string. Deliberately NOT matching "kaufwert"/
# "kaufkurs" (purchase cost, not current market value/price) as value/price
# candidates — that would silently compute the wrong weight.
INSTRUMENT_COL_CANDIDATES = ("isin", "instrument", "ticker", "name")
QUANTITY_COL_CANDIDATES = ("quantity", "anzahl", "stück", "stueck", "stücke", "stuecke")
VALUE_COL_CANDIDATES = ("value_eur", "value", "market_value", "market_value_eur", "wert", "marktwert")
PRICE_COL_CANDIDATES = ("price_eur", "price", "unit_price", "kurs", "marktkurs pro stück", "marktkurs")
CURRENCY_COL_CANDIDATES = ("currency", "ccy", "währung", "waehrung")
DEFAULT_CURRENCY = "EUR"

STALE_AFTER_DAYS = 14  # mirrors configs/scoring_defaults.yaml's W-frequency
                        # staleness allowance -- the portfolio CSV has no
                        # registry frequency of its own to key off.


def latest_portfolio_file(inbox: Path | None = None) -> Path | None:
    matches = all_portfolio_files(inbox)
    return matches[-1] if matches else None


def _read_text(path: Path) -> str:
    """Decode UTF-8(-sig) first, cp1252 fallback -- German broker exports are
    sometimes Windows-1252 rather than UTF-8."""
    raw = path.read_bytes()
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw.decode("cp1252")


def _sniff_delimiter(header_line: str) -> str:
    return ";" if header_line.count(";") > header_line.count(",") else ","


def _detect_german_locale(header_line: str, raw_df: pd.DataFrame, sep: str) -> bool:
    """Detect whether file uses German numeric notation (dot thousands, comma decimal)."""
    if sep == ";":
        return True
    german_indicators = ("stück", "stücke", "stueck", "stuecke", "anzahl", "wert", "marktwert", "kurs", "währung", "waehrung")
    cols_clean = [str(c).replace('"', '').replace('\ufeff', '').strip().lower() for c in raw_df.columns]
    return any(any(ind in col for ind in german_indicators) for col in cols_clean)


def _parse_number(series: pd.Series, *, german_locale: bool) -> pd.Series:
    """German-locale exports use decimal-comma/thousands-dot (e.g.
    "10.684,60", "8.849" meaning 8849). Whether a file is German-locale is
    decided once, from the delimiter and headers (see ``load_positions``) --
    NOT by inspecting individual numbers, since a German thousands-only value
    like "8.849" contains no comma at all and would otherwise be silently
    misparsed as 8.849 by plain dot-decimal parsing."""
    s = series.astype(str).str.strip()
    if german_locale:
        s = s.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    return pd.to_numeric(s, errors="coerce")


def all_portfolio_files(inbox: Path | None = None) -> list[Path]:
    """Return all matching portfolio files (CSV and PDF) in the inbox, sorted by name."""
    box = inbox or INBOX
    files: list[Path] = []
    seen: set[Path] = set()
    for pat in PORTFOLIO_PATTERNS:
        for p in sorted(box.glob(pat)):
            resolved = p.resolve()
            if resolved not in seen and p.is_file():
                seen.add(resolved)
                files.append(p)
    return sorted(files, key=lambda p: p.name)


def _parse_smartbroker_pdf(src: Path) -> pd.DataFrame:
    """Parse Smartbroker+ Depotübersicht PDF export directly using standard library (re + zlib).
    Extracts table rows: instrument (ISIN), quantity, value_eur, currency (EUR)."""
    raw = src.read_bytes()
    streams = re.findall(b"stream\r?\n(.*?)endstream", raw, re.DOTALL)
    tokens: list[str] = []
    for s in streams:
        try:
            d = zlib.decompress(s).decode("latin1", errors="replace")
            matches = re.findall(r"\[(.*?)\]\s*TJ|\((.*?)\)\s*Tj", d)
            for m in matches:
                if m[0]:
                    parts = re.findall(r"\((.*?)\)", m[0])
                    tokens.append("".join(parts))
                elif m[1]:
                    tokens.append(m[1])
        except Exception:
            continue

    isin_pattern = re.compile(r"^[A-Z]{2}[A-Z0-9]{9}[0-9]$")
    isin_indices = [idx for idx, t in enumerate(tokens) if isin_pattern.match(t)]
    if not isin_indices:
        raise RuntimeError(f"{src.name}: no valid ISINs found in PDF depot overview")

    def _clean_eur_num(val_str: str) -> float:
        s = val_str.replace("\xa0", "").replace("\x80", "").replace("€", "").strip()
        s = s.replace(".", "").replace(",", ".")
        return float(s)

    records = []
    for k, idx in enumerate(isin_indices):
        isin = tokens[idx]
        next_idx = isin_indices[k + 1] if k + 1 < len(isin_indices) else len(tokens)
        row_tokens = tokens[idx + 1 : next_idx]
        if not row_tokens:
            continue
        try:
            qty = _clean_eur_num(row_tokens[0])
            val = _clean_eur_num(row_tokens[4]) if len(row_tokens) > 4 else 0.0
        except (ValueError, IndexError):
            continue

        records.append({
            "instrument": isin,
            "quantity": qty,
            "value_eur": val,
            "currency": DEFAULT_CURRENCY,
        })

    if not records:
        raise RuntimeError(f"{src.name}: failed to extract holdings rows from PDF")

    return pd.DataFrame(records)[["instrument", "quantity", "value_eur", "currency"]]


def _load_single_positions_file(src: Path) -> pd.DataFrame:
    """Parse one portfolio file (CSV or Smartbroker PDF) into DataFrame[instrument, quantity, value_eur, currency]."""
    if src.suffix.lower() == ".pdf":
        return _parse_smartbroker_pdf(src)
    text = _read_text(src)
    header_line = text.splitlines()[0] if text else ""
    header_clean = header_line.replace('"', '').replace('\ufeff', '').strip()

    # Check for Portfolio Performance export formats
    from ipos.portfolio.pp_adapter import PortfolioPerformanceAdapter
    if PortfolioPerformanceAdapter.is_buchungen_export(header_clean):
        from ipos.portfolio.accounting import PortfolioLedger
        adapter = PortfolioPerformanceAdapter()
        df_acts = adapter.parse_buchungen(src)
        ledger = PortfolioLedger()
        ledger.replay_activities(df_acts)
        df_pp = ledger.to_ipos_positions()
        if not df_pp.empty:
            return df_pp[["instrument", "quantity", "value_eur", "currency"]].reset_index(drop=True)

    if PortfolioPerformanceAdapter.is_holdings_export(header_clean):
        adapter = PortfolioPerformanceAdapter()
        df_pp = adapter.to_ipos_positions(src)
        if not df_pp.empty:
            return df_pp[["instrument", "quantity", "value_eur", "currency"]].reset_index(drop=True)

    if PortfolioPerformanceAdapter.is_smartbroker_activities_export(header_clean):
        from ipos.portfolio.accounting import PortfolioLedger
        adapter = PortfolioPerformanceAdapter()
        df_acts = adapter.parse_smartbroker_activities(src)
        ledger = PortfolioLedger(account_name="SMARTBROKER")
        ledger.replay_activities(df_acts)
        df_pp = ledger.to_ipos_positions()
        if not df_pp.empty:
            return df_pp[["instrument", "quantity", "value_eur", "currency"]].reset_index(drop=True)

    sep = _sniff_delimiter(header_line)
    raw = pd.read_csv(io.StringIO(text), sep=sep, dtype=str)
    german_locale = _detect_german_locale(header_line, raw, sep)
    cols = {c.replace('"', '').replace('\ufeff', '').strip().lower(): c for c in raw.columns}

    instrument_col = next((cols[c] for c in INSTRUMENT_COL_CANDIDATES if c in cols), None)
    quantity_col = next((cols[c] for c in QUANTITY_COL_CANDIDATES if c in cols), None)
    missing = [name for name, col in
               (("instrument", instrument_col), ("quantity", quantity_col)) if col is None]
    if missing:
        raise RuntimeError(f"{src.name}: missing required column(s) {sorted(missing)}")

    value_col = next((cols[c] for c in VALUE_COL_CANDIDATES if c in cols), None)
    price_col = next((cols[c] for c in PRICE_COL_CANDIDATES if c in cols), None)
    if value_col is None and price_col is None:
        raise RuntimeError(
            f"{src.name}: need a value column {VALUE_COL_CANDIDATES} or a "
            f"price column {PRICE_COL_CANDIDATES} to compute one"
        )

    df = pd.DataFrame()
    df["instrument"] = raw[instrument_col].fillna("").astype(str).str.strip()
    df["quantity"] = _parse_number(raw[quantity_col], german_locale=german_locale)
    if value_col is not None:
        df["value_eur"] = _parse_number(raw[value_col], german_locale=german_locale)
    else:
        df["value_eur"] = df["quantity"] * _parse_number(raw[price_col], german_locale=german_locale)

    currency_col = next((cols[c] for c in CURRENCY_COL_CANDIDATES if c in cols), None)
    if currency_col is not None:
        df["currency"] = raw[currency_col].fillna("").astype(str).str.strip().str.upper()
    else:
        df["currency"] = DEFAULT_CURRENCY

    invalid = (
        df["instrument"].eq("")
        | ~df["quantity"].map(math.isfinite)
        | ~df["value_eur"].map(math.isfinite)
        | ~df["currency"].str.fullmatch(r"[A-Z]{3}")
    )
    if invalid.any():
        rows = (df.index[invalid] + 2).tolist()
        raise RuntimeError(f"{src.name}: invalid portfolio rows {rows}; refusing partial holdings")
    return df[["instrument", "quantity", "value_eur", "currency"]].reset_index(drop=True)


def load_positions(path: Path | None = None, inbox: Path | None = None) -> pd.DataFrame | None:
    """Return consolidated columns [instrument, quantity, value_eur, currency], or ``None``
    if no portfolio file is present. When multiple portfolio files exist in inbox
    (e.g. across multiple brokers like Smartbroker and Zero), combines them."""
    if path is not None:
        sources = [path]
    else:
        sources = all_portfolio_files(inbox)
        if not sources:
            return None

    frames = []
    for src in sources:
        df_src = _load_single_positions_file(src)
        if df_src is not None and not df_src.empty:
            frames.append(df_src)

    if not frames:
        return None
    if len(frames) == 1:
        return frames[0]

    combined = pd.concat(frames, ignore_index=True)
    aggregated = (
        combined.groupby(["instrument", "currency"], as_index=False)
        .agg({"quantity": "sum", "value_eur": "sum"})
    )
    return aggregated[["instrument", "quantity", "value_eur", "currency"]].reset_index(drop=True)


def portfolio_freshness(
    path: Path | None, as_of: dt.date, *, stale_after_days: int = STALE_AFTER_DAYS,
) -> dict | None:
    """Age of the portfolio CSV via filesystem mtime, relative to ``as_of``
    (never wall-clock ``dt.date.today()`` -- ``build_snapshot``'s
    byte-identical-rerun-for-a-fixed-``as_of`` determinism contract depends
    on that). ``None`` when there is no file; otherwise
    {"age_days": int, "stale": bool}."""
    if path is None:
        return None
    mtime_date = dt.date.fromtimestamp(path.stat().st_mtime)
    age_days = (as_of - mtime_date).days
    return {"age_days": age_days, "stale": age_days > stale_after_days}

