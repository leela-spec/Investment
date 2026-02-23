---
module_id: TECH_VOLUME_CONFIRMATION
scope: module
tags: [technical, volume, confirmation, breakouts, confidence]
version: 0.1
source: seminar_pdf
cadence: weekly
---

## Purpose
Use **volume** as a **secondary confirmation** layer to:
- validate trend quality (impulse volume vs correction volume),
- validate breakouts (relative volume spikes),
- **adjust confidence** rather than force direction.

## Inputs (weekly)
- `tech_volume_raw`
- `tech_volume_trend_vs_correction_ratio`
- `tech_volume_breakout_confirmation` (relative volume vs baseline)
- Context from other modules:
  - `MARKET_CONDITIONS.regime_label` / `regime_confidence`
  - `TREND_BREAKS_TRANSITIONS.transition_state`

## Outputs (weekly)
- `volume_confirmation_score` (0–100, bounded)
- `volume_confidence_delta` (signed modifier)
- `breakout_quality_flag` ∈ {CONFIRMED, WEAK, NA}
- `contradiction_flags` (list)

---

## Core Principles (explicit)
- Volume is the **second signal** (confirmation), not the main signal.
- Candle color is irrelevant for volume interpretation.
- Typical behavior:
  - Higher volume in trend direction (impulses)
  - Lower volume during corrections/consolidation
  - Breakouts often show higher relative volume

---

## Rules (compact)
### 1) Trend quality confirmation
- If impulse/trend legs show higher volume than correction legs
  - increase confidence in trend-following posture

### 2) Consolidation volume
- Low volume during “waiting / consolidation” is normal
  - do not interpret as bearish alone

### 3) Breakout confirmation
- If breakout + relative volume high
  - classify breakout as **CONFIRMED**
  - increase confidence and allow bounded incremental adds (subject to governance)

- If breakout + relative volume low
  - classify breakout as **WEAK**
  - reduce confidence; higher false-break risk

---

## Confidence Heuristic
Start at 50:
- +15 if breakout CONFIRMED (high rel volume)
- -15 if breakout WEAK (low rel volume)
- +10 if trend_vs_correction_ratio strongly favors impulses
- -10 if volume data quality is low or missing (then neutralize volume effects)

---

## Contradictions (trigger investigation)
- Breakout volume confirms, but transition_state is TRENDLESS/UNCERTAIN after a break
  - governance wins: keep risk capped; require follow-through + structure reform
- Volume confirms breakouts, but regime_label is CHOPPY with high overlap/retracements
  - likely false breakout environment; treat as lower quality
- Volume weak during a supposed momentum breakout
  - momentum label questionable; re-check ATR expansion and overlap features

---

## Implementation Notes (IPOS-friendly)
- Use volume as a **confidence modifier** (affects confidence score, not core direction score).
- Store in snapshot:
  - `rel_volume`, `breakout_quality_flag`, `trend_vs_correction_ratio`, and contradiction flags.
- Default: if volume unavailable/unreliable for an asset class, set module to neutral.
