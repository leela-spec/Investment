---
module_id: DRAW_DOWN_AND_RECOVERY_GOVERNOR
scope: module
tags: [risk_budget, drawdown, portfolio_caps, governance, diversification]
version: 0.1
source: seminar_pdf
cadence: weekly
---

## Purpose
Provide the **hard risk governors** that override tactical signals when needed:
- diversification & correlation checks,
- trading capital base + portfolio/position risk caps,
- drawdown cap logic (“loss pyramid”),
- derived max risk-per-trade example (30%/18 ≈ 1.67%),
- contradiction overrides for capital preservation.

## Inputs (weekly)
- Portfolio metadata (can be manual in MVP):
  - `trading_capital`
  - exposures by bucket (Equity/Rates/Credit/FX/Commodities)
  - exposures by region/sector (optional)
- Risk state:
  - `realized_drawdown_pct` (vs peak)
  - `max_drawdown_cap_pct` (default 30)
  - `max_portfolio_risk_pct` (policy)
  - `max_initial_position_risk_pct` or amount (policy)
  - `assumed_hit_rate` (optional) and `assumed_max_losing_streak` (policy)
- Signals context:
  - `risk_budget_suggested` (0–100)
  - `regime_confidence`

## Outputs (weekly)
- `risk_budget_cap` (0–100)
- `risk_mode` ∈ {NORMAL, CAUTION, RECOVERY, DEFENSIVE}
- `risk_per_trade_cap_pct` (if used)
- `diversification_score` (0–100, coarse)
- `correlation_risk_flag` (bool)
- `override_flags` (list)

---

## Core Principles
### Diversification
- Cross-asset diversification reduces volatility; rates stabilize; commodities can reduce volatility due to lower correlation.
- Regional diversification reduces concentration risk.
- Diversification may reduce performance → must be a configurable policy choice.

### Correlation risk
- Sector/driver clustering increases risk: many positions fall together.
- When environment is uncertain, concentration risk is especially dangerous.

### Loss pyramid (drawdown recovery)
- Drawdown recovery is **nonlinear**:
  - larger losses require disproportionately larger gains to recover.
- Therefore, risk must be reduced as drawdown grows.

---

## Default Governance (MVP)
### 1) Drawdown cap (hard)
- Default `max_drawdown_cap_pct = 30` (example; configurable)
- Define thresholds for progressive de-risking:
  - `CAUTION` when drawdown > 50% of cap
  - `RECOVERY` when drawdown > 80% of cap
  - `DEFENSIVE` when drawdown approaches cap

### 2) Derived max risk per trade (example policy)
- Seminar example (TQ=40%): max losing streak ≈ 18
- With DD cap 30% → max risk/trade ≈ `30% / 18 ≈ 1.67%`
- Treat as a **default** until you set your own hit-rate/streak assumptions.

### 3) Portfolio and position caps
- `max_portfolio_risk_pct`: hard cap for total portfolio risk (config)
- `max_initial_position_risk_pct/amount`: hard cap per position (config)
- Use trading capital as base (not total wealth).

---

## Overrides (how this module caps risk)
### Risk budget cap logic (simple)
- Start with `risk_budget_cap = risk_budget_suggested`
- Apply hard constraints:
  - If drawdown in RECOVERY/DEFENSIVE → cap risk_budget_cap lower
  - If concentration/correlation risk high → cap risk_budget_cap lower
  - If regime_confidence low + concentration high → cap further

**Rule of thumb caps (MVP defaults)**
- NORMAL: cap = 100
- CAUTION: cap = 70
- RECOVERY: cap = 40
- DEFENSIVE: cap = 25

---

## Contradictions (override wins)
- Risk budget signals risk-on while drawdown is high/near cap
  - override: RECOVERY/DEFENSIVE caps apply
- High concentration (sector/driver) while regime uncertain
  - override: reduce risk budget; require diversification
- Strong tactical setups but portfolio caps would be exceeded
  - override: size down or skip

---

## Snapshot Requirements (AI-safe)
Include:
- trading capital base
- drawdown %, drawdown cap %, risk mode
- portfolio/position caps
- risk-per-trade cap (if used)
- diversification score + correlation flags
- overrides applied (why)

---

## Implementation Notes (IPOS-friendly)
- Start with manual entry for exposures and drawdown in MVP.
- Later automate using broker exports or portfolio CSV.
- Keep all caps configurable, but ship sensible defaults.
