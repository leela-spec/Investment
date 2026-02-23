---
module_id: TREND_BREAKS_TRANSITIONS
scope: module
tags: [trend, regime, transitions, confidence, risk_rules]
version: 0.1
source: seminar_pdf
cadence: weekly
---

## Purpose
Turn trend **breaks** and **timescale alignment** into a weekly governance layer:
- when to **cap risk** (trendless/uncertain),
- when to **add** (resumption + alignment),
- how to avoid false regime switches,
- enforce a **CRV floor** for any risk adds.

## Inputs (weekly)
- Swing points: `last_swing_low`, `last_swing_high` (pivot-based)
- Trend hierarchy labels (per market): `primary_trend_dir`, `secondary_trend_dir`, `tertiary_trend_dir`
- Derived flags:
  - `trend_break_flag`
  - `trendless_flag`
  - `correction_phase_flag`
  - `alignment_score` (0–3 aligned)

## Outputs (weekly)
- `transition_state` ∈ {STABLE_TREND, CORRECTION, BREAK, TRENDLESS, RESUME_OLD, COUNTERTREND, RANGE}
- `transition_confidence` ∈ [0,100]
- Governance actions:
  - `risk_cap_active` (bool)
  - `add_risk_allowed` (bool)
  - `contradiction_flags` (list)

---

## Trend Hierarchy Roles (short)
- **Primary trend**: strategic bias (stance prior)
- **Secondary trend**: timing signals inside primary
- **Tertiary trend**: execution refinement (entries/stops); should not override primary

---

## Trend Break Definitions (hard rules)
### Uptrend break
- If: in uptrend AND **break the last swing low**
- Then: uptrend is broken → transition to **TRENDLESS**

### Downtrend break
- If: in downtrend AND **break the last swing high**
- Then: downtrend is broken → transition to **TRENDLESS**

**Implementation note:** require weekly close confirmation if you want fewer false breaks.

---

## Post-Break State Machine (weekly governance)
1) **BREAK** (event)
2) **TRENDLESS** (default after break)
3) Next outcomes (don’t force prediction):
   - **RESUME_OLD** (old trend continues)
   - **COUNTERTREND** (new opposite trend develops)
   - **RANGE** (sideways)

### Core operating rule
- In **TRENDLESS / structure unclear**:
  - **Wait for clarity** (reduce activity)
  - **Cap risk budget**
  - Allow only **small probes** if other modules strongly agree

---

## Correction vs Resumption Logic (timescale-based)
### Correction starts (inside larger trend)
- If: **primary trend intact**
- AND: the **directly lower trend breaks against it**
- Then: `correction_phase_flag = true` (reduce aggressiveness, do not flip bias)

### Resumption starts
- If: in correction
- AND: **correction trend breaks back in primary direction**
- Then: **resumption signal** → tactical add is allowed *if* not CHOPPY and other modules confirm

---

## Multi-Timescale Alignment (confidence amplifier)
### Alignment score
- `alignment_score = count(primary==secondary==tertiary direction)`

**Rule**
- If alignment_score = 3:
  - Increase confidence
  - Allow stronger stance (bounded)
- If misaligned:
  - Reduce stance magnitude
  - Prefer “wait / smaller risk” until alignment improves

---

## Hard Risk Rule: CRV Floor (non-negotiable gate)
### CRV ≥ 1.3 for any risk adds
- If expected_reward / risk < **1.3**
- Then: do not enter / do not scale / reduce size or skip

**Apply this to:**
- new positions
- position adds
- leverage increases
- any risk budget expansion based on tactical setups

---

## Contradictions to Watch (trigger investigation)
- **TRENDLESS**, but macro/sentiment modules are strongly risk-on/off  
  → cap risk anyway; investigate why price structure is unclear.
- **Resumption signal**, but MARKET_CONDITIONS = CHOPPY  
  → likely false resumption; reduce confidence.
- High alignment, but yield curve inversion + tightening liquidity  
  → “technical vs macro” contradiction; reduce confidence, demand confirmation.

---

## Dashboard Hooks (what to visualize)
- Regime Map trail: show `transition_state` over time as a ribbon
- Mark BREAK events with vertical lines
- Overlay alignment_score and CRV gate triggers on the timeline
