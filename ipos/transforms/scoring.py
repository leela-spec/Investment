"""Scoring math — the three Blueprint methods, as pure deterministic functions
plus a rolling engine over weekly history.

The math lives in Python (not window-function SQL) for the Phase-1 golden-20:
rolling *percentile-of-current-value-within-its-own-trailing-window* is awkward
to express in SQL, the data is tiny, and pure functions are trivially
hand-verifiable in tests. Determinism is preserved (no wall-clock, fixed
formulas). See the 2026-07-23 note in ``05_blueprint/01_DECISION_ANALYSIS.md``.

Standardized z-score mapping (correcting a Blueprint inconsistency, recorded in
the decision log): ``score = 50 * (tanh(z / k) + 1)`` — centered at 50, range
[0, 100], then inverted for ``higher_is_better = false``. The Blueprint's prose
``50 + 50*(z'+1)/2`` yields the range [50, 100] (not 0–100) and its pseudocode
``50 + 25z`` yields [25, 75]; neither is centered/range-safe, so we adopt the
clean centered form.
"""

from __future__ import annotations

import math
from typing import Sequence

from ipos.config.models import BandStep


def percentile_score(window: Sequence[float], higher_is_better: bool) -> float:
    """Percentile rank of the last value within its trailing window (inclusive),
    inverted per directionality. Returns 0–100."""
    vals = list(window)
    if not vals:
        return float("nan")
    current = vals[-1]
    pct = sum(1 for v in vals if v <= current) / len(vals) * 100.0
    return pct if higher_is_better else 100.0 - pct


def zscore_score(
    window: Sequence[float], higher_is_better: bool, k: float = 2.0
) -> float:
    """Tanh-damped rolling z-score mapped to 0–100 (centered at 50)."""
    vals = list(window)
    if not vals:
        return float("nan")
    current = vals[-1]
    n = len(vals)
    mu = sum(vals) / n
    var = sum((v - mu) ** 2 for v in vals) / n  # population std (ddof=0)
    sigma = math.sqrt(var)
    z = (current - mu) / sigma if sigma > 0 else 0.0
    zp = math.tanh(z / k)
    score = 50.0 * (zp + 1.0)
    score = min(100.0, max(0.0, score))
    return score if higher_is_better else 100.0 - score


def band_score(value: float, bands: list[BandStep]) -> float:
    """Map a value to the score of its band. Bands are ascending by `upper`
    (exclusive); the final band has `upper=None` (+inf). Directionality is
    encoded in the band scores themselves, so there is no inversion."""
    for step in bands:
        if step.upper is None or value < step.upper:
            return float(step.score)
    return float(bands[-1].score)  # unreachable (last upper is None), for safety
