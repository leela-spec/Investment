# C4 — Regime & Aggregation (Meso Plan)

**Owns:** MARKET_CONDITIONS regime classifier, module aggregation, stance vector, risk budget, contradictions engine, top movers / key drivers.
**Depends on:** C3 (+ C1 configs). **Feeds:** C6, C7. Implements the Playbook's *governor* layer — the core "no traffic lights" value.

## Decisions

1. **Module scores** = weighted mean of member indicator scores (`configs/weights.yaml`, Σw=1 validated at load); module confidence = weight-averaged indicator confidence, degraded by intra-module dispersion. Written to `agg_module (as_of_date, module_id, …)`.
2. **Stance vector** (Blueprint mapping, kept): per stance dim (equity, duration, credit, usd, commodities): `tilt = clip((module_score−50)/50, −1, +1)` via a `modules→stance_dims` mapping in `configs/modules.yaml` (a dim may blend several modules with weights).
3. **Risk budget** = Σ W_m · module_score over risk-capacity modules, **then multiplied by the regime `risk_scaler`** and capped by governors:
   - regime scaler (Playbook defaults): CHOPPY 0.50, TRENDY 1.00, MOMENTUM 0.75, UNCERTAIN 0.40;
   - drawdown governor hook (DRAW_DOWN_AND_RECOVERY_GOVERNOR): risk-posture cap NORMAL 100 / CAUTION 70 / RECOVERY 40 / DEFENSIVE 25 — MVP takes posture from manual config (`configs/portfolio_state.yaml`), automation later;
   - final `risk_budget = min(base, caps…) · risk_scaler`, with all inputs stored in `params_json` (explainability: the report can show *why* risk changed).
4. **Regime classifier** — direct implementation of `MARKET_CONDITIONS.md` v0.1 (MVP rules, tune later):
   - features from C3 on the benchmark series: `overlap_index` (share of overlapping weekly ranges, 12w), `retracement_ratio` (pullback/impulse from pivot detection), `atr_change_rate`, `swing_structure` (HH/HL vs LH/LL counts, ≥3-swing minimum);
   - rule order exactly as the module: UNCERTAIN-priority → CHOPPY signature (retracement 0.8–1.0 ∧ overlap high) → MOMENTUM (ATR accel ∧ overlap very low) → TRENDY (HH/HL ∧ overlap low);
   - confidence heuristic verbatim (start 50; +15 swings, +10 agreement, +10 ATR clean, −20 conflict, −25 uncertain; <40 ⇒ UNCERTAIN cap);
   - **hysteresis** (transcript requirement): regime flips require 2 consecutive weekly confirmations unless confidence ≥ 80;
   - outputs `regime_label, regime_confidence, risk_scaler, policy_selectors{position_size, entry_style, trailing_stop, initial_stop}` → `agg_regime` + snapshot.
5. **Contradictions engine** (rank-3 feature): YAML predicates in `configs/contradictions.yaml`, evaluated over module scores + regime + indicator extremes; two classes per Blueprint (module-disagreement, intra-module conflict) **plus** the Playbook's regime contradictions (e.g. TRENDY ∧ retracement≈0.9; UNCERTAIN ∧ other modules risk-on ⇒ "process risk"). Seed set mined from the 10 modules' "Contradictions to Watch" sections + `rules.jsonl`. Each hit → `log_contradiction (id, severity, summary, details_json)` with triggering values captured.
   - Predicate DSL stays trivial: `when: "module('EquityRisk') >= 70 and module('Credit') <= 40"`, `severity: high` — evaluated with a small safe evaluator (no `eval`), ~50 lines.
6. **Top movers / key drivers:** movers = largest |Δscore_1w|; drivers = largest contributions W_m·Δmodule_score to Δrisk_budget. Pure SQL, feeds snapshot + report.

## Implementation steps

1. `ipos/aggregate/modules.py` (+ `regimes.sql` for coordinates), `stance.py`, `risk_budget.py` — thin, config-driven.
2. `ipos/aggregate/regime.py` — pivot/swing detection (scipy-free, simple local-extrema on weekly bars), features, rules, hysteresis.
3. `ipos/aggregate/contradictions.py` + `configs/contradictions.yaml` seed (~10–15 predicates from Playbook modules).
4. `scripts/seed_contradictions_from_playbook.py` — assistive one-time extraction with `extract_ref` provenance.
5. pytest: synthetic price paths with known regime (flat-chop, clean trend, parabolic momentum) classify correctly; hysteresis blocks single-week flips; contradiction predicates fire on constructed score fixtures; risk budget monotone in module scores and correctly capped by scaler/governors.

## Definition of done
- Weekly run writes `agg_module`, `agg_regime`, `log_contradiction`; snapshot contains stance vector, risk budget with decomposition, regime block with policy selectors; synthetic-regime tests green.

**Effort:** L (regime classifier is the hardest single component — schedule after the skeleton is green). **Recurring tokens:** 0.
