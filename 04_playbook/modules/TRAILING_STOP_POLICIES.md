---
module_id: TRAILING_STOP_POLICIES
scope: module
tags: [execution, trailing_stops, risk_management, donchian, swing_structure]
version: 0.1
source: seminar_pdf
cadence: weekly
---

## Purpose
Standardize **trade management** via trailing stop policies that are:
- explainable in weekly reports,
- compatible with weekly cadence,
- configurable but defaults are sensible.

This module does **not** backtest. It defines **policy selection** and **parameters**.

## Inputs (weekly)
- Market state:
  - `MARKET_CONDITIONS.regime_label` ∈ {CHOPPY, TRENDY, MOMENTUM, UNCERTAIN}
  - `MARKET_CONDITIONS.regime_confidence`
  - `TREND_BREAKS_TRANSITIONS.transition_state`
  - `MULTI_TIMESCALE_ALIGNMENT.alignment_score` (0–3)
- Price structure:
  - `last_swing_low`, `last_swing_high` (objective pivots)
- Price history for Donchian:
  - `N_week_high`, `N_week_low` for chosen period N

## Outputs (weekly)
- `trailing_policy` ∈ {REL_HILO, DONCHIAN, NONE}
- `trailing_params` (e.g., `{ "N": 14 }`)
- `stop_reference_level` (numeric)
- `stop_tightness` ∈ {TIGHT, MEDIUM, WIDE}
- `management_notes` (short string for report)

---

## Policy 1: Relative High/Low (REL_HILO)
### Definition (weekly)
- Long: stop = `last_swing_low`
- Short: stop = `last_swing_high`
Updated only when a new swing forms.

### When to prefer
- Regime: **TRENDY**
- Structure: swings are clean; transition_state not TRENDLESS
- Alignment: higher alignment_score supports wider, structure-based trailing

### Pros/Cons (practical)
- ✅ aligns with structure and keeps you in normal pullbacks
- ❌ can be wide; may give back more in fast momentum reversals

---

## Policy 2: Donchian Channel (DONCHIAN)
### Definition (weekly; default)
- Long: stop = **N-week low**
- Short: stop = **N-week high**
(N is configurable)

### Parameter guidance (from seminar examples)
- Smaller N (e.g., **10**) = **tighter** stop (more exits/churn)
- Larger N (e.g., **14**) = **wider** stop (fewer exits; more room)

### When to prefer
- If you want systematic trailing without pivots
- Regime: TRENDY/MOMENTUM (parameter changes with regime)

---

## Default regime mapping (MVP)
### TRENDY
- Default: `REL_HILO`
- Alternative: `DONCHIAN` with **N=14**
- Tightness: WIDE/MEDIUM

### MOMENTUM (ATR expanding; fast moves)
- Default: `DONCHIAN` with **N=10** (tighter control)
- Tightness: TIGHT/MEDIUM
- If you use REL_HILO here, reduce size (wide stops + fast reversals = giveback risk)

### CHOPPY / UNCERTAIN / TRENDLESS transition
- Default: `NONE` (management focuses on **risk reduction** not trailing optimization)
- If a position must be held: prefer tighter systematic management + smaller size

---

## Contradictions (investigate)
- High alignment_score (3) but very tight stop (Donchian N too small)
  - likely churn; consider wider stop or smaller noise sensitivity
- MOMENTUM regime but very wide stop
  - likely excessive giveback risk; consider tighter Donchian or smaller size
- TRENDLESS transition but trailing policy assumes stable trends
  - governance wins: cap risk, wait for structure

---

## Snapshot fields (AI-safe)
Include for each active position (or proposed add):
- `trailing_policy`, `trailing_params`
- `stop_reference_level_type` (swing_low / N_week_low / none)
- `stop_reference_level_value`
- any contradiction flags

---

## Implementation Notes
- Always use **objective pivots** (not drawn trendlines) for REL_HILO.
- Keep policy selection deterministic and explainable.
- Parameter N must be configurable in `config.yaml`.
---
# New Content from new Prompt
## Purpose  
Provide a **policy selector** for trailing stops (not a backtest system):  
- encode *which* trailing method is used  
- encode *why* (regime + structure)  
- encode *parameters* (e.g., Donchian N=10 vs N=14)  
- ensure the weekly snapshot logs enough to explain exits/de-risking  
  
## Where this fits (IPOS)  
- Depends on regime classification: `MARKET_CONDITIONS`  
- Works best with objective swing logic: `TREND_STRUCTURE` (pivot highs/lows)  
- Interacts with payoff distribution discipline: `EXPECTANCY_CRV`  
  
## Snapshot contract (what must be exported weekly)  
For each active position (or each “risk bucket”), include:  
- `trailing_policy`: `REL_HILO | DONCHIAN`  
- `trailing_params`: e.g. `{ "donchian_n": 14, "swing_pivot_rule": "weekly_fractal_3bar" }`  
- `stop_ref_type`: `swing_low | donchian_low | atr_band` (keep minimal)  
- `stop_level`: numeric (latest stop)  
- `stop_distance_pct`: optional, helps explain tight vs wide  
- `policy_rationale`: short string (<= 140 chars): “TRENDY + clean swings → REL_HILO”  
  
## Policy Catalog (MVP)  
  
### Policy A — Relative High/Low (REL_HILO)  
**Definition (weekly bars, long positions)**  
- Identify objective swing lows on weekly data (e.g., 3-bar fractal pivot).  
- Trailing stop follows structure:  
- `candidate_stop = last_confirmed_swing_low`  
- `stop_t = max(stop_{t-1}, candidate_stop)` (never loosen in normal trailing)  
  
**When to prefer**  
- TRENDY regime + well-defined swing structure  
- High multi-timescale alignment (if you track it): “3/3 alignment” makes trend capture more valuable  
  
**Operational notes**  
- Avoid subjective trendlines; use objective pivots (reduces drift between runs).  
- If regime shifts to CHOPPY / TRENDLESS / UNCERTAIN, do **not** widen further; tighten or cut exposure instead.  
  
**Source process notes**  
- `process_relative_hilo_stop_follows_swings` (p211–p212)  
- `process_relative_hilo_stop_is_simple_and_pattern_aligned` (p212)  
  
### Policy B — Donchian Channel Trailing (DONCHIAN)  
**Definition (weekly bars)**  
- Choose lookback `N` weeks.  
- For long positions (seminar-derived variant):  
- `stop_t = MIN(low_{t-N+1} ... low_t)` (lowest low over last N weeks)  
- Parameter `N` controls tightness (churn vs room).  
  
**When to prefer**  
- When you want systematic trailing that is less dependent on swing labeling.  
- TRENDY / MOMENTUM regimes where you want consistent mechanical trailing.  
  
**Parameter guidance (high-impact, keep simple)**  
- `N = 14` default for **TRENDY** (gives room; fewer exits)  
- `N = 10` default for **MOMENTUM** (tighter; risk-control in fast regimes)  
- In **CHOPPY**, avoid Donchian as a primary trailing method; reduce risk instead.  
  
**Source process notes**  
- `process_donchian_channel_stop_trails_by_channel` (p218–p219)  
- `process_donchian_period_controls_tightness` (p218–p219)  
  
## Policy Selection (minimal decision table)  
- If regime = TRENDY and swings are clean → **REL_HILO**  
- Else if regime = MOMENTUM → **DONCHIAN (N=10)** (tighter control)  
- Else if regime = TRENDY but swings are messy/ambiguous → **DONCHIAN (N=14)**  
- Else if regime = CHOPPY/UNCERTAIN → **de-risk first**, do not “solve” with wider stops  
  
## Rules (traceable IDs in `rules.jsonl`)  
Core:  
- `rule_trailing_stop_is_phase2_management` (p211)  
- `rule_policy_selector_relative_hilo` (p211–p212)  
- `rule_policy_selector_donchian_channel` (p218–p219)  
- `rule_donchian_period_tightness_tradeoff` (p218–p219)  
- `rule_default_donchian_by_regime` (p218–p219, p69)  
- `rule_trailing_policy_must_be_logged` (p211, p218)  
  
Governance + contradictions:  
- `rule_relative_hilo_requires_objective_swings` (p211–p212, p118) [needs_verification=true in extract]  
- `rule_relative_hilo_not_for_choppy_uncertain` (p59, p211) [needs_verification=true in extract]  
- `rule_contradiction_tight_trailing_in_trendy_alignment` (p102, p218) [needs_verification=true in extract]  
- `rule_contradiction_wide_trailing_in_momentum_spike` (p69, p218) [needs_verification=true in extract]  
- `rule_crv_and_trailing_are_linked` (p206–p209, p211) [needs_verification=true in extract]  
  
## Contradictions to Watch (what to log + investigate)  
1) **High alignment but tight trailing**  
- If: alignment_score high AND Donchian N is very small  
- Risk: churn undermines trend capture → consider widening N or lowering noise sensitivity  
  
2) **Momentum regime but very wide trailing**  
- If: MOMENTUM (ATR expanding) AND trailing is wide (e.g., N too large)  
- Risk: giveback too large → tighten trailing or reduce size  
  
3) **Trailing choice compresses winners (CRV impact)**  
- If: trailing systematically clips winners below your CRV floor logic  
- Action: treat trailing policy as a lever that changes realized payoff distribution (governance note; empirical tuning later)  
  
## Implementation Notes (MVP boundaries)  
- Implement as **metadata + deterministic calculations** on weekly bars.  
- Do not turn this into a full trade simulator in MVP.  
- Store policy + parameters every week so report generation can explain management decisions.  
---END FILE