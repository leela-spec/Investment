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

import pandas as pd

from ipos.config.load import REPO_ROOT

INBOX = REPO_ROOT / "data" / "inbox"
GLOB = "portfolio*.csv"

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
    matches = sorted((inbox or INBOX).glob(GLOB))
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
    """Return all matching portfolio CSV files in the inbox, sorted by name."""
    return sorted((inbox or INBOX).glob(GLOB))


def _load_single_positions_file(src: Path) -> pd.DataFrame:
    """Parse one portfolio file into DataFrame[instrument, quantity, value_eur, currency]."""
    text = _read_text(src)
    header_line = text.splitlines()[0] if text else ""
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

