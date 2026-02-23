---
module_id: TECH_MOVING_AVERAGES
scope: module
tags: [technical, moving_averages, trend_filter, risk_budget_governor]
version: 0.1
source: seminar_pdf
cadence: weekly
---

## Purpose
Use moving averages as **lagging trend filters** and **risk governors**:
- emphasize **50** and **200** (per seminar),
- apply a simple **“below 200 = negative filter”** rule,
- treat MA contraction as a **setup context**, not a signal.

## Inputs (weekly)
- `tech_ma_50w`
- `tech_ma_200w`
- `tech_ma_50_200_cross`
- `tech_ma_contraction_index`
- Market context: `equity_sp500_index` (or chosen benchmark)

## Outputs (weekly)
- `ma_trend_filter` ∈ {STRONG_POSITIVE, POSITIVE, NEUTRAL, NEGATIVE}
- `ma_confidence` (0–100)
- `risk_governor_flag` (bool)  // used in risk budget computation
- `contradiction_flags` (list)

---

## Core Principles (explicit)
- Moving averages **smooth** prices and are **lagging** → use as filters, not early timing.
- Focus lengths: **50** and **200**.
- For “investment style” (fund-like), **price below 200 MA is a negative filter**.

---

## Filter Logic (MVP)
### 1) 200 MA investment filter (governor)
- If `price < MA200`:
  - `ma_trend_filter = NEGATIVE`
  - set `risk_governor_flag = true`
  - apply equity risk budget cap / underweight bias

- If `price >= MA200`:
  - `ma_trend_filter = POSITIVE` (subject to other context)

### 2) 50 vs 200 cross (secondary confirmation)
- If `MA50 > MA200`: trend supportive confirmation (but lagging)
- If `MA50 < MA200`: trend weaker confirmation

### 3) Price distance and slope (optional refinement)
- `price_minus_ma200` (distance) and MA slope can add confidence but should not dominate.

---

## MA Contraction (setup context)
### What it means
- MA and price action can go sideways / contract (flat slope + compressed range).
- After a contraction ends, a **new trend may form**.

### How to use (efficient)
- Contraction does **not** change stance by itself.
- It adds a “setup” tag:
  - *Watch for breakout + volume confirmation + regime suitability*

---

## Confidence Heuristic (0–100)
Start at 50:
- +20 if price is clearly above MA200 (and MA200 slope not deteriorating)
- +10 if MA50 > MA200
- -25 if price below MA200 (governor active)
- -10 if whipsaw zone (price near MA200; frequent crossings)
- +5 if contraction_flag true (setup awareness, not direction)

---

## Contradictions (trigger investigation)
- **Price below MA200** but **RSI Power Zone active**
  - interpret as tactical rally inside structurally weak trend unless price reclaims MA200 and trend structure reforms.
- **MA50 > MA200** but **trend-break / TRENDLESS** state active
  - lagging MA confirms old regime; do not ignore structure break.
- **Contraction setup** but MARKET_CONDITIONS = CHOPPY and no volume confirmation
  - likely continued chop; reduce expectation of clean breakout.

---

## Implementation Notes (IPOS-friendly)
- Treat MA200 filter as a **risk budget governor** (hard bias), not a trading trigger.
- Keep changes slow:
  - optionally require 2 weekly closes to confirm “below/above MA200” to reduce whipsaws.
- Store in snapshot:
  - `price_vs_ma200_flag`, `ma50_vs_ma200_flag`, `contraction_flag`, and any contradiction flags.
