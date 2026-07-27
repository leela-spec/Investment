"""Portfolio connector — the optional "actual holdings" input for the
Portfolio vs. Stance module (``05_blueprint/03_PORTFOLIO_MODULE.md``).

Matches ``data/inbox/portfolio*.csv`` (latest file wins, same convention as
``manual_csv.py``). Unlike a registry-driven series, this file is never
required: absent inbox file -> ``load_positions`` returns ``None`` and the
whole module is omitted downstream (fail-degraded, never a hard dependency).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ipos.config.load import REPO_ROOT

INBOX = REPO_ROOT / "data" / "inbox"
GLOB = "portfolio*.csv"

REQUIRED = {"instrument", "quantity"}
VALUE_COL_CANDIDATES = ("value_eur", "value", "market_value", "market_value_eur")
PRICE_COL_CANDIDATES = ("price_eur", "price", "unit_price")


def latest_portfolio_file(inbox: Path | None = None) -> Path | None:
    matches = sorted((inbox or INBOX).glob(GLOB))
    return matches[-1] if matches else None


def load_positions(path: Path | None = None) -> pd.DataFrame | None:
    """Return columns [instrument, quantity, value_eur], or ``None`` if no
    portfolio file is present. Computes ``value_eur`` from quantity * price
    at import time when the export only gives a price, so the operator never
    has to hand-compute it."""
    src = path or latest_portfolio_file()
    if src is None:
        return None

    raw = pd.read_csv(src)
    cols = {c.lower(): c for c in raw.columns}
    missing = REQUIRED - cols.keys()
    if missing:
        raise RuntimeError(f"{src.name}: missing required column(s) {sorted(missing)}")

    value_col = next((cols[c] for c in VALUE_COL_CANDIDATES if c in cols), None)
    price_col = next((cols[c] for c in PRICE_COL_CANDIDATES if c in cols), None)
    if value_col is None and price_col is None:
        raise RuntimeError(
            f"{src.name}: need a value column {VALUE_COL_CANDIDATES} or a "
            f"price column {PRICE_COL_CANDIDATES} to compute one"
        )

    df = raw.rename(columns={cols["instrument"]: "instrument", cols["quantity"]: "quantity"})
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    if value_col is not None:
        df["value_eur"] = pd.to_numeric(df[value_col], errors="coerce")
    else:
        df["value_eur"] = df["quantity"] * pd.to_numeric(df[price_col], errors="coerce")

    df["instrument"] = df["instrument"].astype(str).str.strip()
    df = df.dropna(subset=["instrument", "value_eur"])
    df = df[df["instrument"] != ""]
    return df[["instrument", "quantity", "value_eur"]].reset_index(drop=True)
