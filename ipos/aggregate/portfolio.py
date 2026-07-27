"""Portfolio aggregation: actual holdings (``ipos/etl/portfolio_csv.py``) ->
per-module exposure, for the "Portfolio vs. Stance" report section
(``05_blueprint/03_PORTFOLIO_MODULE.md``).

Deliberately does only two things: turn raw positions into module weights
(this file), and pair those weights against the existing stance vector for
display (``portfolio_vs_stance``, used by both report renderers). No trade or
rebalancing suggestions are produced anywhere in this module — a read-only
comparison only, matching the rest of the system's "no trade calls" stance.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import duckdb
import pandas as pd
import yaml

from ipos.config.load import REPO_ROOT

MAPPING_PATH = REPO_ROOT / "configs" / "portfolio_mapping.yaml"

DEFAULT_UNMAPPED_POLICY = "warn"
_VALID_POLICIES = {"warn", "ignore", "error"}

# Currency code -> registry series_id whose value is USD-per-1-EUR (verified
# against configs/registry.yaml's EURUSD entry + its synthetic fixture
# baseline of 1.08, consistent only under USD-per-EUR quoting). Only USD is
# wired up today since no other FX series exists in the registry yet.
SUPPORTED_FX = {"USD": "EURUSD"}


def load_mapping(path: Path | None = None) -> tuple[dict[str, str], str]:
    """Returns (instrument -> module_id, unmapped_policy). A missing or empty
    mapping file degrades to an empty mapping (everything unmapped) rather
    than failing the run — the operator hasn't finished setup yet, not an
    error."""
    p = path or MAPPING_PATH
    if not p.exists():
        return {}, DEFAULT_UNMAPPED_POLICY
    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    policy = raw.get("unmapped_policy", DEFAULT_UNMAPPED_POLICY)
    if policy not in _VALID_POLICIES:
        raise ValueError(f"{p}: unmapped_policy must be one of {sorted(_VALID_POLICIES)}, got {policy!r}")
    return dict(raw.get("mappings") or {}), policy


def aggregate_portfolio(
    positions: pd.DataFrame,
    mapping: dict[str, str],
    unmapped_policy: str = DEFAULT_UNMAPPED_POLICY,
) -> dict:
    """positions: DataFrame[instrument, quantity, value_eur]. Returns
    {"modules": {module_id: {"value_eur", "weight_pct"}}, "unmapped": [...],
    "total_value_eur": ...}. Total always includes every position's value,
    mapped or not."""
    total = float(positions["value_eur"].sum())
    by_module: dict[str, float] = {}
    unmapped: list[dict] = []
    for row in positions.itertuples(index=False):
        module_id = mapping.get(row.instrument)
        if module_id is None:
            if unmapped_policy == "error":
                raise ValueError(
                    f"portfolio: unmapped instrument '{row.instrument}' "
                    f"(add it to configs/portfolio_mapping.yaml)"
                )
            if unmapped_policy == "warn":
                unmapped.append({
                    "instrument": row.instrument,
                    "value_eur": round(float(row.value_eur), 2),
                })
            continue
        by_module[module_id] = by_module.get(module_id, 0.0) + float(row.value_eur)

    modules = {
        module_id: {
            "value_eur": round(value, 2),
            "weight_pct": round(value / total * 100.0, 4) if total else 0.0,
        }
        for module_id, value in sorted(by_module.items())
    }
    return {
        "modules": modules,
        "unmapped": sorted(unmapped, key=lambda u: u["instrument"]),
        "total_value_eur": round(total, 2),
    }


def _latest_fx_value(con: duckdb.DuckDBPyConnection, series_id: str, as_of: dt.date) -> float | None:
    """Most recent canonical value at or before ``as_of`` -- nearest, not
    exact-match, since an FX pull may lag a portfolio CSV drop by a day or
    two. ``None`` when no row exists yet."""
    row = con.execute(
        "SELECT value FROM fact_weekly WHERE series_id = ? AND as_of_date <= ? "
        "ORDER BY as_of_date DESC LIMIT 1",
        [series_id, as_of],
    ).fetchone()
    return float(row[0]) if row else None


def convert_to_eur(
    positions: pd.DataFrame, con: duckdb.DuckDBPyConnection, as_of: dt.date,
) -> tuple[pd.DataFrame, list[dict]]:
    """Convert non-EUR position values to EUR using that week's FX rate
    (``fact_weekly``, nearest at-or-before ``as_of``). EUR rows (the default
    when no currency column exists -- fully backward compatible) pass
    through unchanged. A currency with no known rate or no ``SUPPORTED_FX``
    mapping is left UNCONVERTED and reported in the returned warnings list --
    warn-over-crash, matching ``unmapped_policy``'s philosophy, rather than
    aborting the whole portfolio section over one bad currency code. Returns
    (converted_positions, warnings)."""
    df = positions.copy()
    if "currency" not in df.columns:
        return df, []
    warnings: list[dict] = []
    for ccy in sorted(set(df["currency"]) - {"EUR"}):
        mask = df["currency"] == ccy
        series_id = SUPPORTED_FX.get(ccy)
        rate = _latest_fx_value(con, series_id, as_of) if series_id else None
        if not rate or rate <= 0:
            warnings.append({
                "currency": ccy, "n_positions": int(mask.sum()),
                "reason": "no FX rate available; left unconverted",
            })
            continue
        df.loc[mask, "value_eur"] = df.loc[mask, "value_eur"] / rate
    return df, warnings


def persist_portfolio_weights(
    con: duckdb.DuckDBPyConnection, as_of: dt.date, portfolio: dict | None,
) -> int:
    """Write this week's actual module weights to ``fact_portfolio_weight``
    so ``ipos.aggregate.contradictions``'s ``portfolio_weight()`` can read
    them like any other as_of_date-scoped signal. One row per module scored
    this week (``agg_module``), using 0.0 for modules the operator holds
    nothing in -- so "0% weight" and "no portfolio data this week" are never
    confused. Deletes any existing rows for this ``as_of`` first (same
    idempotent-rerun pattern as ``contradictions.evaluate()``). Writes ZERO
    rows when ``portfolio`` is ``None`` (no CSV this week) -- so
    ``portfolio_weight()`` then correctly returns ``None`` for every module,
    and no portfolio-mismatch rule can misfire on a no-CSV week. Returns the
    row count written."""
    con.execute("DELETE FROM fact_portfolio_weight WHERE as_of_date = ?", [as_of])
    if portfolio is None:
        return 0
    known_modules = [r[0] for r in con.execute(
        "SELECT DISTINCT module_id FROM agg_module WHERE as_of_date = ?", [as_of]
    ).fetchall()]
    weights = portfolio.get("modules", {})
    for module_id in known_modules:
        w = weights.get(module_id, {})
        con.execute(
            "INSERT INTO fact_portfolio_weight (as_of_date, module_id, weight_pct, value_eur) "
            "VALUES (?, ?, ?, ?)",
            [as_of, module_id, w.get("weight_pct", 0.0), w.get("value_eur", 0.0)],
        )
    return len(known_modules)


def stance_alignment(
    weight_pct: float, tilt: float,
    *, weight_threshold: float = 10.0, tilt_threshold: float = 0.2,
) -> str:
    """Plain-language read of actual exposure vs. this week's suggested
    tilt. Purely descriptive, never a trade call."""
    has_weight = weight_pct >= weight_threshold
    if tilt >= tilt_threshold:
        return "aligned" if has_weight else "not participating in a signal the system currently likes"
    if tilt <= -tilt_threshold:
        return "exposed to a headwind the system currently flags" if has_weight else "aligned (out of a signal the system currently dislikes)"
    return "aligned"


def portfolio_vs_stance(snapshot: dict) -> list[dict] | None:
    """Pair each module's actual portfolio weight against this week's tilt.
    Returns ``None`` when the snapshot has no ``portfolio`` block (no CSV was
    dropped this run) — the whole section is then omitted by the report
    renderers, never a hard dependency."""
    portfolio = snapshot.get("portfolio")
    if portfolio is None:
        return None
    weights = portfolio.get("modules", {})
    rows = []
    for m in snapshot.get("modules", []):
        module_id = m["module"]
        w = weights.get(module_id, {})
        weight_pct = w.get("weight_pct", 0.0)
        value_eur = w.get("value_eur", 0.0)
        rows.append({
            "module": module_id,
            "tilt": m["tilt"],
            "weight_pct": weight_pct,
            "value_eur": value_eur,
            "read": stance_alignment(weight_pct, m["tilt"]),
        })
    rows.sort(key=lambda r: r["module"])
    return rows
