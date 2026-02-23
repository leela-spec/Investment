---
module_id: EXPECTANCY_CRV
scope: module
tags: [risk_management, expectancy, crv, r_multiple, governance]
version: 0.1
source: seminar_pdf
cadence: weekly
---

## Purpose
Anchor the IPOS risk discipline in **expectancy**:
- explain why **win rate alone is not enough**,
- enforce a hard **CRV floor** for entries and adds,
- connect management policies (e.g., trailing stops) to the payoff distribution.

## Inputs (weekly)
- For any proposed action (entry/add/scale):
  - `defined_risk_R` (usually 1R by construction; derived from stop distance × size)
  - `expected_reward_R` (target, trend path expectation, or conservative scenario)
  - `CRV = expected_reward_R / defined_risk_R`
- Optional strategy assumptions:
  - `assumed_win_rate` (p_win)
  - `avg_win_R`, `avg_loss_R` (loss ~ 1R)

## Outputs (weekly)
- `crv_gate_pass` (bool)
- `expectancy_note` (short explanation string for report)
- `expectancy_confidence` (0–100)

---

## Core Concepts
### CRV as R-multiple framing
- Express payoff and risk in **R**:
  - risk = 1R (your defined loss if stop is hit)
  - reward = expected multiple of R
- CRV is simply:
  - `CRV = reward / risk`

### Expectancy (intuition-level)
- Long-run profitability depends on:
  - **win rate** and **payoff size**
- Simple model:
  - `E ≈ p_win * avg_win_R - (1 - p_win) * avg_loss_R`
- Therefore:
  - higher CRV can offset lower win rate
  - high win rate with tiny CRV can still be fragile

---

## Hard Governance Rule (non-negotiable)
### CRV ≥ 1.3 gate (entries + adds)
- If `CRV < 1.3`:
  - do not enter
  - do not add/scale
  - reduce size or skip
- This is a **process gate**, not a “score”.

---

## Practical Use in Weekly IPOS
### What goes into the weekly report (short)
- For any tactical “add risk” recommendation:
  - show CRV estimate (conservative)
  - state whether the CRV gate passes
  - if it fails: explain why no add is recommended even if signals look good

### Avoid table overfitting
- The seminar’s win-rate × CRV tables are for intuition.
- IPOS should:
  - enforce the CRV floor
  - avoid quoting exact table outcomes
  - keep the explanation simple: “payoff quality matters”

---

## Link to Management (Trailing policies matter)
Trailing stops change your realized payoff distribution:
- tighter trailing:
  - tends to increase win rate but can compress winners (lower avg_win_R)
- wider trailing:
  - allows larger winners but can give back more and reduce win rate

**Governance implication**
- do not choose trailing policies that systematically compress winners so much that your effective CRV deteriorates.

---

## Contradictions (trigger investigation)
- Signals suggest adding risk, but CRV gate fails
  - override: no add; investigate whether target assumptions are unrealistic or stop too wide/tight
- Strategy claims “high win rate” but frequent drawdowns
  - likely poor payoff quality or correlation risk; review CRV and loss distribution

---

## Implementation Notes (IPOS-friendly)
- In macro-first IPOS, CRV is mainly applied to:
  - tactical adds (tilt increases, lever changes, adding exposures)
- Keep CRV estimation conservative:
  - reward scenarios should be plausible within the current regime/trend state
