"""Regime classifier (C4 decision 4) — a direct, light implementation of
`MARKET_CONDITIONS.md` v0.1, the Playbook's governor layer.

**Close-only MVP.** The module spec computes features from weekly OHLC bars
(ATR, range overlap). Phase 1 stores only weekly *closes* (`fact_weekly`), so
this MVP derives the same *concepts* from closes:
  * `overlap_index`  ← 1 − Kaufman efficiency ratio (net move / gross move);
    high overlap = choppy, the close-only analogue of "highs/lows overlap".
  * `swing_structure` ← HH/HL vs LH/LL from local pivots on weekly closes.
  * `atr_change_rate` ← ratio of recent to prior weekly-return volatility.
  * `retracement_ratio` ← pullback / prior impulse from the last two pivots.
When true weekly OHLC is added (Phase 3 registry work), swap the feature
functions; the rule/confidence/hysteresis layer stays. Recorded in the
decision-log amendment (2026-07-23).

Deterministic: pure functions of the close series; no wall-clock.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

RISK_SCALER = {"CHOPPY": 0.50, "TRENDY": 1.00, "MOMENTUM": 0.75, "UNCERTAIN": 0.40}

POLICY = {
    "CHOPPY": {"position_size": "small", "entry_style": "penalize_breakouts",
               "trailing_stop": "defensive_quick_exit", "initial_stop": "wide_buffer"},
    "TRENDY": {"position_size": "large", "entry_style": "retracements_and_breakouts",
               "trailing_stop": "swing_based", "initial_stop": "last_swing"},
    "MOMENTUM": {"position_size": "medium", "entry_style": "anticipate_continuation",
                 "trailing_stop": "volatility_aware", "initial_stop": "1_2_atr"},
    "UNCERTAIN": {"position_size": "small", "entry_style": "defensive",
                  "trailing_stop": "defensive_quick_exit", "initial_stop": "wide_buffer"},
}

LOOKBACK = 16       # weeks used for regime features
MIN_WEEKS = 8       # below this we cannot assess -> UNCERTAIN


@dataclass
class RegimeResult:
    label: str
    confidence: float
    risk_scaler: float
    policy: dict
    features: dict = field(default_factory=dict)


# --- features (close-only) --------------------------------------------------

def _pivots(p: np.ndarray) -> list[tuple[int, str]]:
    """Local extrema on the close series (k=1 neighbours). Returns (index, H|L)."""
    out = []
    for i in range(1, len(p) - 1):
        if p[i] > p[i - 1] and p[i] >= p[i + 1]:
            out.append((i, "H"))
        elif p[i] < p[i - 1] and p[i] <= p[i + 1]:
            out.append((i, "L"))
    return out


def _swing_structure(p: np.ndarray) -> tuple[str, int]:
    """Classify swing structure from the last few pivots. Returns
    (up|down|none, n_swings)."""
    pivots = _pivots(p)
    highs = [p[i] for i, kind in pivots if kind == "H"]
    lows = [p[i] for i, kind in pivots if kind == "L"]
    n = len(pivots)
    hh = sum(1 for a, b in zip(highs, highs[1:]) if b > a)
    hl = sum(1 for a, b in zip(lows, lows[1:]) if b > a)
    lh = sum(1 for a, b in zip(highs, highs[1:]) if b < a)
    ll = sum(1 for a, b in zip(lows, lows[1:]) if b < a)
    if hh >= 2 and hl >= 1:
        return "up", n
    if ll >= 2 and lh >= 1:
        return "down", n
    return "none", n


def _retracement_ratio(p: np.ndarray) -> float | None:
    """Pullback / prior impulse from the last two pivots to the current close."""
    pivots = _pivots(p)
    if len(pivots) < 2:
        return None
    (i1, _), (i2, _) = pivots[-2], pivots[-1]
    impulse = abs(p[i2] - p[i1])
    if impulse == 0:
        return None
    pullback = abs(p[-1] - p[i2])
    return float(pullback / impulse)


def _features(p: np.ndarray) -> dict:
    ret = np.diff(p)
    gross = float(np.sum(np.abs(ret)))
    net = float(abs(p[-1] - p[0]))
    er = net / gross if gross > 0 else 0.0          # Kaufman efficiency ratio
    overlap_index = 1.0 - er                         # high = choppy
    # volatility acceleration: recent vs prior *speed* (mean |weekly return|),
    # the close-only analogue of "ATR rising quickly".
    speed_recent = float(np.mean(np.abs(ret[-4:]))) if len(ret) >= 4 else float(np.mean(np.abs(ret)))
    speed_prev = float(np.mean(np.abs(ret[:-4]))) if len(ret) > 4 else speed_recent
    atr_change_rate = speed_recent / speed_prev if speed_prev > 0 else 1.0
    structure, n_swings = _swing_structure(p)
    return {
        "efficiency_ratio": round(er, 4),
        "overlap_index": round(overlap_index, 4),
        "atr_change_rate": round(atr_change_rate, 4),
        "swing_structure": structure,
        "n_swings": n_swings,
        "retracement_ratio": _retracement_ratio(p),
    }


# --- classification ---------------------------------------------------------

def _raw_label(f: dict) -> str:
    overlap = f["overlap_index"]
    accel = f["atr_change_rate"]
    structure = f["swing_structure"]
    established = f["n_swings"] >= 3 and structure != "none"
    rr = f["retracement_ratio"]

    # rule order per MARKET_CONDITIONS.md
    choppy_retrace = rr is not None and 0.8 <= rr <= 1.0
    if (choppy_retrace and overlap >= 0.6) or overlap >= 0.7:
        return "CHOPPY"
    if accel >= 1.5 and overlap <= 0.35:
        return "MOMENTUM"
    # TRENDY: strong directionality (low overlap / high efficiency ratio), or a
    # confirmed pivot swing structure in a moderately directional tape.
    if overlap <= 0.4 or (established and overlap <= 0.5):
        return "TRENDY"
    return "UNCERTAIN"


def _confidence(f: dict, label: str) -> float:
    c = 50.0
    established = f["n_swings"] >= 3 and f["swing_structure"] != "none"
    if established:
        c += 15
    # overlap + retracement agree with a directional regime
    if label in ("TRENDY", "CHOPPY") and f["retracement_ratio"] is not None:
        c += 10
    if label == "MOMENTUM" and f["atr_change_rate"] >= 1.5:
        c += 10
    # conflict: choppy overlap but volatility accelerating
    if f["overlap_index"] >= 0.6 and f["atr_change_rate"] >= 1.5:
        c -= 20
    if label == "UNCERTAIN":
        c -= 25
    return max(0.0, min(100.0, c))


def classify_history(closes: list[float]) -> RegimeResult:
    """Classify the latest week, applying the module's confidence heuristic and
    hysteresis (a flip needs 2 consecutive raw agreements unless confidence
    >= 80)."""
    if len(closes) < MIN_WEEKS:
        return RegimeResult("UNCERTAIN", 30.0, RISK_SCALER["UNCERTAIN"],
                            POLICY["UNCERTAIN"], {"reason": "insufficient_history"})

    p_all = np.asarray(closes, dtype=float)
    # raw label + confidence per week over a trailing span, for hysteresis
    span = min(len(p_all), LOOKBACK + 8)
    raws: list[tuple[str, float, dict]] = []
    for end in range(len(p_all) - span + 1, len(p_all) + 1):
        if end < MIN_WEEKS:
            continue
        window = p_all[max(0, end - LOOKBACK):end]
        f = _features(window)
        lbl = _raw_label(f)
        raws.append((lbl, _confidence(f, lbl), f))

    # hysteresis
    effective = raws[0][0]
    for i in range(1, len(raws)):
        lbl, conf, _ = raws[i]
        prev_lbl = raws[i - 1][0]
        if lbl != effective and (conf >= 80 or lbl == prev_lbl):
            effective = lbl

    _, last_conf, last_f = raws[-1]
    # if confidence is low, enforce UNCERTAIN -> defensive
    if last_conf < 40:
        effective = "UNCERTAIN"
    return RegimeResult(
        label=effective,
        confidence=round(last_conf, 4),
        risk_scaler=RISK_SCALER[effective],
        policy=POLICY[effective],
        features=last_f,
    )


def classify_from_db(con, benchmark: str, as_of) -> RegimeResult:
    rows = con.execute(
        "SELECT value FROM fact_weekly WHERE series_id = ? AND as_of_date <= ? "
        "ORDER BY as_of_date",
        [benchmark, as_of],
    ).fetchall()
    closes = [float(r[0]) for r in rows]
    return classify_history(closes)
