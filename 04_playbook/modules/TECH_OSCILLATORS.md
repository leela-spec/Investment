---
module_id: TECH_OSCILLATORS
scope: module
tags: [technical, oscillators, rsi, stochastic, momentum, regime_gating]
version: 0.1
source: seminar_pdf
cadence: weekly
---

## Purpose
Use **Slow Stochastic** and **RSI** as a weekly oscillator layer that:
- adapts behavior by **market regime** (CHOPPY vs TRENDY vs MOMENTUM),
- supports **tactical timing** without overriding the governance modules,
- treats **RSI Power Zone** as **trend-following momentum**, not contrarian.

## Inputs (weekly)
- `tech_slow_stochastic_14_3_3` (K/D, 14,3,3)
- `tech_slow_stoch_crossover_signal` (K/D cross flags)
- `tech_rsi_14`
- `tech_rsi_power_zone_weekly` (Power Zone flag)
- Regime context from `MARKET_CONDITIONS`:
  - `regime_label`
  - `regime_confidence`

## Outputs (weekly)
- `oscillator_bias` ∈ {MEAN_REVERT, TREND_CONFIRM, NEUTRAL}
- `oscillator_score` (0–100, bounded)
- `oscillator_confidence` (0–100)
- `tactical_flags` (e.g., stoch_bull_cross, stoch_bear_cross, rsi_power_zone)

---

## Core Thresholds (explicit)
### Slow Stochastic
- Overbought: **>80**
- Oversold: **<20**
- Signals: **%K / %D crossovers** (use zone context when possible)

### RSI
- Overbought: **>70**
- Oversold: **<30**
- **Power Zone (weekly): RSI > 70 = momentum confirmation** (NOT contrarian)

---

## Regime Gating (how to interpret signals)
### CHOPPY (range / overlap)
- Oscillator bias: **MEAN_REVERT**
- Stochastic:
  - Oversold (<20) + bullish crossover → supportive bounce bias
  - Overbought (>80) + bearish crossover → caution / mean-reversion bias
- RSI:
  - <30 supports bounce bias (with confirmation)
  - >70 is *not* automatically bearish; treat cautiously but do not force sells

### TRENDY (directional HH/HL or LH/LL)
- Oscillator bias: **TREND_CONFIRM**
- Stochastic:
  - Overbought can persist; do not auto-sell
  - Use crossovers mainly as “tighten/loosen stops” not as trend reversal by itself
- RSI:
  - RSI >70 can be strength; use Power Zone as confirmation

### MOMENTUM (ATR expanding, fast moves)
- Oscillator bias: **TREND_CONFIRM** (but with higher noise)
- Stochastic/RSI extremes are less reliable contrarianly
- Power Zone is most useful here as a continuation confirmation
- Keep sizing rules from MARKET_CONDITIONS (momentum = medium size, wider stops)

---

## Operational Rules (compact)
1) **Stochastic zone awareness**
- >80 = overbought zone, <20 = oversold zone
- Don’t auto-trade zones without regime context

2) **Stochastic crossovers**
- Bull cross near/after oversold → supportive (tactical)
- Bear cross near/after overbought → caution (tactical)
- In CHOPPY: crossovers are more actionable
- In TRENDY/MOMENTUM: crossovers are mostly management (tighten/loosen), not reversal calls

3) **RSI classical zones**
- >70 / <30 are context flags, not standalone actions

4) **RSI Power Zone (weekly RSI > 70)**
- Treat as **momentum confirmation**
- Best used when regime ∈ {TRENDY, MOMENTUM}
- Explicit: **do not use as contrarian “overbought means sell”**

---

## Confidence Heuristic (0–100)
Start at 50, adjust:
- +15 if regime_confidence high AND regime ≠ UNCERTAIN
- +10 if RSI Power Zone active in TRENDY/MOMENTUM
- +5 if Stochastic crossover occurs with zone context (oversold/overbought)
- -20 if regime is UNCERTAIN (cap influence)
- -10 if oscillator signals conflict (e.g., stoch bear cross while Power Zone active)

---

## Contradictions (trigger investigation)
- RSI Power Zone active but price below 200 MA (long filter negative)
  - Treat as tactical rally in weak structure unless price/structure recovers.
- Strong oscillator signals while trend state is TRENDLESS after break
  - Cap risk; require structural reform (pivot break / alignment improvement).

---

## Implementation Notes (IPOS-friendly)
- Keep oscillator influence bounded: it should not override macro/rates risk governors.
- Store tactical flags in snapshot for explainability:
  - `rsi_power_zone_flag`
  - `stoch_cross_flag`
  - `stoch_zone`
- Default scoring approach:
  - CHOPPY → allow oscillator to tilt more (mean reversion)
  - TRENDY/MOMENTUM → oscillator mostly influences confidence/stops
