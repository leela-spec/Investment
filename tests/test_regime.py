"""Regime classifier tests (C4): constructed close paths land in the right
regime, low data => UNCERTAIN, hysteresis blocks single-week flips, and the
classifier is deterministic."""

from __future__ import annotations

import math

from ipos.aggregate.regime import RISK_SCALER, classify_history


def _trend(n=40):
    # clear uptrend with small wiggles -> HH/HL, high efficiency ratio
    return [100 + 2.0 * t + 3.0 * math.sin(t) for t in range(n)]


def _chop(n=40):
    # pure oscillation around a constant -> net move ~0, high overlap
    return [100 + 6.0 * math.sin(t / 1.4) for t in range(n)]


def _momentum(n=40):
    # steady trend that accelerates into a blow-off in the final weeks ->
    # recent speed >> prior speed (ATR-accel analogue), overlap stays low
    out = []
    for t in range(n):
        v = 100 + 1.0 * t
        if t >= n - 8:
            v += 0.7 * (t - (n - 9)) ** 2
        out.append(v)
    return out


def test_trend_is_trendy():
    r = classify_history(_trend())
    assert r.label == "TRENDY"
    assert r.risk_scaler == RISK_SCALER["TRENDY"]
    assert r.policy["position_size"] == "large"


def test_chop_is_choppy_or_uncertain():
    r = classify_history(_chop())
    # a range-bound series must not be called TRENDY/MOMENTUM
    assert r.label in ("CHOPPY", "UNCERTAIN")
    assert r.risk_scaler <= 0.5


def test_momentum_is_momentum():
    r = classify_history(_momentum())
    assert r.label == "MOMENTUM"
    assert r.risk_scaler == RISK_SCALER["MOMENTUM"]
    assert r.policy["initial_stop"] == "1_2_atr"


def test_insufficient_history_is_uncertain():
    r = classify_history([100, 101, 102])
    assert r.label == "UNCERTAIN"
    assert r.risk_scaler == RISK_SCALER["UNCERTAIN"]


def test_deterministic():
    p = _trend()
    assert classify_history(p).label == classify_history(p).label
    assert classify_history(p).confidence == classify_history(p).confidence


def test_hysteresis_blocks_single_week_flip():
    # a long clean trend with one aberrant last week should not immediately
    # flip the regime label (needs 2 consecutive confirmations unless conf>=80)
    trend = _trend(40)
    trend_then_spike = trend[:-1] + [trend[-2] * 0.7]  # one-week shock
    r = classify_history(trend_then_spike)
    # still governed by the established trend, not whipsawed to a new label
    assert r.label in ("TRENDY", "UNCERTAIN")
