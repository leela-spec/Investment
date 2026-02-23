---
module_id: EXECUTION_LIQUIDITY_FILTERS
scope: module
tags: [execution, liquidity, slippage, tradability, risk_controls]
version: 0.1
source: seminar_pdf
cadence: weekly
---

## Purpose
Reduce operational risk by enforcing **tradability gates**:
- avoid instruments where **slippage/spreads** dominate,
- improve reliability of technical levels (support/resistance),
- make liquidity constraints explicit in the weekly snapshot.

## Inputs (weekly)
- For equities/ETFs:
  - `adtv_shares` (avg daily shares) and/or `avg_dollar_volume`
  - `last_price`
- For other assets (rates/fx/commodities):
  - use appropriate proxies (open interest, bid-ask, turnover) — configuration-driven

## Outputs (weekly)
- `liquidity_tier` ∈ {LOW, MED, HIGH}
- `liquidity_gate_pass` (bool)
- `price_gate_pass` (bool)  // equities only
- `execution_confidence_modifier` (signed)
- `execution_size_cap` (multiplier)
- `contradiction_flags` (list)

---

## Core Principles (explicit)
- Higher liquidity:
  - lowers slippage
  - increases reliability of technical levels
  - reflects stronger institutional participation (better price discovery)

---

## Default Gates (MVP)
### 1) Liquidity gate (equities)
- Default: **ADTV ≥ 400k shares/day** (example threshold)
- If ETF: prefer **avg $ volume** (price × shares) as more comparable.

### 2) Minimum price gate (equities)
- Default: **price ≥ $10** (example threshold)

**Note:** These are defaults; keep configurable per market/instrument.

---

## Governance Effects (how gates impact IPOS)
### If gates pass (HIGH liquidity)
- Increase confidence in technical signals slightly (MA, breakouts, volume behavior)
- Allow normal sizing under the global risk budget

### If liquidity gate fails / LOW tier
- Reduce confidence in technical signals
- Increase expected slippage assumption
- Enforce **position size reduction** or exclude instrument

### If price gate fails (equities)
- Treat as higher noise/spread risk (microcap/low-price effects)
- Exclude or cap size strongly

---

## Contradictions (trigger investigation)
- Strong technical signals but liquidity gate fails / LOW tier
  - contradiction: “signal quality vs execution risk”
  - require manual review; do not scale aggressively
- Breakout confirmations in illiquid names
  - treat as higher false breakout risk due to slippage + thin order books

---

## Snapshot Requirements (AI + auditability)
Always include:
- ADTV (or avg $ volume)
- liquidity_tier
- gate pass/fail flags
- size cap applied
- any contradiction flags

This keeps weekly reports explainable and prevents “invisible” execution risk.

---

## Implementation Notes (IPOS-friendly)
- Encode as a **pre-trade governor** (applies before scoring/stance execution).
- If you keep instruments in the DB but fail gates:
  - still compute scores (for learning),
  - but enforce the size cap and label as “non-tradable” for action.
