"""Pre-DB validation and sanity checks.

Deliberately lightweight (plain pandas) for the Phase-1 golden-20 — see the
2026-07-23 note in ``05_blueprint/01_DECISION_ANALYSIS.md``: pandera (the D7
choice) is deferred to Phase 3 when many heterogeneous scrape sources arrive
and schema-as-code earns its dependency weight. The checks here cover the same
Phase-1 needs: shape, dtype, monotonic dates, and per-asset-class sanity
ranges. Failures raise ``ValidationError``; out-of-range outliers only warn.
"""

from __future__ import annotations

import pandas as pd

from ipos.config.models import RegistryEntry


class ValidationError(ValueError):
    pass


# Coarse plausibility ranges by asset_class (reject obviously corrupt pulls).
_SANITY: dict[str, tuple[float, float]] = {
    "Rates": (-20.0, 25.0),        # yields / spreads / index in %
    "Credit": (0.0, 60.0),         # OAS in %
    "Equity": (0.0, 100_000.0),    # index levels or VIX
    "FX": (0.0, 500.0),            # broad-USD index or a cross rate
    "Commodities": (0.0, 100_000.0),
}


def validate_observations(entry: RegistryEntry, df: pd.DataFrame) -> list[str]:
    """Validate a normalized [obs_date, value] frame. Returns a list of
    non-fatal warnings; raises ValidationError on structural problems."""
    warnings: list[str] = []

    if list(df.columns) != ["obs_date", "value"]:
        raise ValidationError(
            f"{entry.series_id}: expected columns [obs_date, value], got {list(df.columns)}"
        )
    if df.empty:
        raise ValidationError(f"{entry.series_id}: no rows")

    dates = pd.to_datetime(df["obs_date"])
    if not dates.is_monotonic_increasing:
        raise ValidationError(f"{entry.series_id}: obs_date not sorted ascending")
    if dates.duplicated().any():
        raise ValidationError(f"{entry.series_id}: duplicate obs_date rows")

    if df["value"].isna().any():
        raise ValidationError(f"{entry.series_id}: NaN values after normalization")

    lo, hi = _SANITY.get(entry.asset_class, (float("-inf"), float("inf")))
    out_of_range = df[(df["value"] < lo) | (df["value"] > hi)]
    if not out_of_range.empty:
        warnings.append(
            f"{entry.series_id}: {len(out_of_range)} value(s) outside sanity "
            f"range [{lo}, {hi}] for {entry.asset_class}"
        )
    return warnings
