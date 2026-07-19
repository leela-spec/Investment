# C3 — Transform & Scoring Engine (Meso Plan)

**Owns:** weekly canonicalization, feature engineering, scoring 0–100, confidence 0–100. Lives in `ipos/transforms/` (SQL-first) + thin Python drivers.
**Depends on:** C1, C2. **Feeds:** C4, C6.

## Options considered

| Option | Verdict |
|--------|---------|
| SQL-in-DuckDB for all window math (Blueprint) | ✅ **Chosen.** Rolling percentiles/z-scores/deltas are single window-function statements; fast, testable, no dataframe churn. |
| pandas feature pipeline | ❌ More code, slower, harder to keep deterministic. pandas only at presentation edges. |
| Per-indicator custom Python scorers | ❌ Violates registry-driven principle; three parametrized methods cover the Playbook. |

## Decisions

1. **Canonical weekly alignment** (Blueprint policy, kept): `as_of_date` = Friday; canonical value = last observation ≤ `as_of_date` (per-series override e.g. AAII Wednesday). One SQL statement (`canonical_weekly.sql`) rebuilds `fact_weekly` from `fact_observation` for the affected window — recompute-over-patch keeps revisions trivial (revision = new vintage rows → window recompute).
2. **Feature set v1 (fixed, small):** `delta_1w/4w/12w`, `pct_change_*`, `z_104w` (tanh-damped, k=2.0), `pctile_156w` (registry can override lookbacks), `trend` = sign of 5-week slope, `sma_50w`, `sma_200w`, `atr_14w`, `hi_52w/lo_52w` (Donchian inputs for C4). All in `features.sql`; each feature = one window expression.
3. **Scoring (exactly the Blueprint's three methods):**
   - `percentile`: rolling rank in lookback window; invert if `higher_is_better = false`.
   - `zscore`: `50 + 50·(tanh(z/2)+1)/2` mapped, inverted as needed *(fixes the Blueprint's internal inconsistency: prose formula vs pseudocode `50+25z` — we standardize on the prose formula, range-safe 0–100)*.
   - `band`: thresholds from registry `scoring_params.bands` (seeds from `03_extract/rules.jsonl`: ISM 50, Put/Call 1.1, RSI 70/30, Stoch 80/20, curve <0 ⇒ 20, …).
   - Params frozen per run in `fact_score.params_json`; `scoring_version` global stamp.
4. **Confidence (Blueprint composite, kept, config-weighted):** `0.45·quality + 0.35·stability + 0.20·coherence` where quality = freshness/missingness/revision-instability, stability = 8-week score-change std (inverted), coherence = agreement with same-module neighbors. Staleness from C2 caps quality. Weights in `configs/scoring_defaults.yaml`.
5. **Determinism contract:** same DB state + same configs ⇒ byte-identical `fact_score` rows. No wall-clock reads inside transforms (`as_of_date` is an explicit parameter). This makes golden-snapshot tests (C9) possible.

## Implementation steps

1. `transforms/sql/canonical_weekly.sql`, `features.sql`, `scores_percentile.sql`, `scores_zscore.sql`, `scores_band.sql` — parametrized by `as_of_date` + registry-driven CTE (`dim_series` join).
2. `ipos/transforms/run.py` — executes SQL in order, applies band maps from registry (bands rendered into a DuckDB temp table, not string-built SQL).
3. `ipos/transforms/confidence.py` — the one place where Python beats SQL (multi-part composite); writes into `fact_score.confidence_0_100`.
4. `scripts/seed_bands_from_rules.py` — one-time: mine `03_extract/rules.jsonl` band/threshold rules into registry `scoring_params` (with `extract_ref` provenance).
5. pytest: monotonicity (percentile/band: higher input never lowers score when `higher_is_better`), inversion symmetry, damping bounds (score ∈ [0,100] for |z| → ∞), known-value fixtures (hand-computed 10-week series), idempotency (re-run same week ⇒ identical rows).

## Definition of done
- `uv run ipos-score --as-of 2026-07-17` populates `fact_feature` + `fact_score` for all active indicators; re-run identical; all scoring tests green; confidence present and sane (0–100, stale series visibly lower).

**Effort:** M–L (the "high" items 7–8 of the Blueprint milestone list). **Recurring tokens:** 0.
