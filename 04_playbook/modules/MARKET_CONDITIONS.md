---
module_id: MARKET_CONDITIONS
scope: module
tags: [regime, trend, volatility, execution, risk_budget]
version: 0.1
source: seminar_pdf
cadence: weekly
---

## Purpose
Classify the market into **CHOPPY / TRENDY / MOMENTUM** and translate that into **risk posture + position sizing + entry style + stop policy**. This module is a *governor* for the whole IPOS.

## Inputs (minimal)
- **Market price series (context)**: e.g., `equity_sp500_index` (or your chosen benchmark per asset bucket)
- **Derived features (computed weekly)**:
  - `overlap_index` (how often weekly ranges overlap)
  - `retracement_ratio` (pullback size / prior impulse size)
  - `atr_weekly` and `atr_change_rate` (ATR level + acceleration)
  - `swing_structure` (HH/HL vs LH/LL counts; pivot-based)

## Outputs (stored weekly)
- `regime_label` ∈ {CHOPPY, TRENDY, MOMENTUM}
- `regime_confidence` ∈ [0,100]
- `risk_scaler` (multiplier applied to risk budget + stance magnitude)
- `policy_selectors`: {position_size, entry_style, trailing_stop, initial_stop}

---

## Core Definitions (from seminar)
### CHOPPY
- Sideways / range-like (or weak trend)
- Many **false breakouts**
- High overlap of highs/lows
- Retracements often **80–100%** of the prior move

### TRENDY
- Clear direction
- Uptrend: higher highs + higher lows (HH/HL)
- Downtrend: lower highs + lower lows (LH/LL)
- Few overlaps of highs/lows

### MOMENTUM
- Very high dynamics
- **ATR rises quickly**
- No overlap of highs/lows
- Can run with or against the prevailing trend (treat as “fast conditions”)

---

## Classification Rules (simple, efficient)
Use these as a first MVP classifier (tune later):

1) **Uncertain → Defensive (priority rule)**
- If: regime_confidence is low / signals mixed / swings not established
- Then: label = `UNCERTAIN` (internally) → act like CHOPPY for risk

2) **CHOPPY signature**
- If: `retracement_ratio ∈ [0.8, 1.0]` AND `overlap_index` high
- Then: regime_label = CHOPPY

3) **MOMENTUM signature**
- If: `atr_change_rate` high AND `overlap_index` very low
- Then: regime_label = MOMENTUM

4) **TRENDY signature**
- If: `swing_structure` indicates HH/HL (or LH/LL) AND overlap low
- Then: regime_label = TRENDY

### Trend Structure Minimum (for confidence)
- A trend exists after **3 consecutive moves** produce visible swing highs/lows.
- Uptrend formed with **≥1 higher low and ≥2 higher highs**.
- Downtrend formed with **≥1 lower high and ≥2 lower lows**.

---

## Regime → Portfolio Policies (direct seminar mapping)
### Position sizing
- CHOPPY: **small**
- TRENDY: **large**
- MOMENTUM: **medium**
- If unsure: **defensive + small** (cap risk)

**Recommended risk_scaler (MVP default)**
- CHOPPY: `0.50x`
- TRENDY: `1.00x`
- MOMENTUM: `0.75x`
- UNCERTAIN: `0.40x`

### Entry style
- CHOPPY: **penalize breakouts** (don’t rely on them)
- TRENDY: **retracements + breakouts** both allowed (prefer confirmation)
- MOMENTUM: **anticipate continuation**; do not expect big retracements

### Trailing stops (policy selector, not numbers)
- CHOPPY: none / defensive (quick exit mindset)
- TRENDY: relative highs/lows (swing-based trailing)
- MOMENTUM: Supertrend-like (volatility-aware trailing)

### Initial stops
- CHOPPY: far away (translate as wider volatility buffer in implementation)
- TRENDY: last swing low/high
- MOMENTUM: **1–2 ATR** (explicit)

---

## Confidence Heuristic (0–100)
Start at 50, then adjust:
- +15 if swing structure satisfies “trend exists” criteria (≥3 swings)
- +10 if overlap + retracement agree strongly with a regime
- +10 if ATR acceleration cleanly signals momentum
- -20 if signals conflict (e.g., overlap high but ATR accelerating)
- -25 if “uncertain / cannot assess” condition is met

If `regime_confidence < 40`: enforce **UNCERTAIN → defensive cap**.

---

## Contradictions to Watch (trigger investigation)
- **TRENDY label but retracement_ratio ~ 0.9** → trend may be illusory; likely CHOPPY.
- **MOMENTUM label while overlap remains high** → volatility spike inside range; reduce confidence.
- **Regime = UNCERTAIN** but other modules scream risk-on/off → flag “process risk”: environment unclear, so cap risk budget anyway.

---

## Implementation Notes (IPOS-friendly)
- Compute all regime features weekly from daily bars (or weekly OHLC if you have it).
- Store `policy_selectors` in the weekly snapshot so your report can explain *why* risk changed.
- Keep this module “light”: it’s a governor, not a full technical system.
