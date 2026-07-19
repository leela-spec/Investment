# C1 — Registry & Warehouse (Meso Plan)

**Owns:** `configs/registry.yaml` (indicator definitions incl. data-source mapping), `configs/modules.yaml`, `configs/weights.yaml`, `configs/scoring_defaults.yaml`, DuckDB schema + init/migration.
**Depends on:** nothing. **Feeds:** everything.

## Options considered

| Option | Verdict |
|--------|---------|
| YAML registry + pydantic models (Blueprint) | ✅ **Chosen.** Human-diffable, git-versioned, typed at load time; adding indicator = adding rows (D2→D3 without refactor). |
| Registry inside DuckDB tables | ❌ Loses git diffability; config belongs in files, facts in DB. `dim_series` is *derived* from YAML at init. |
| Reuse `03_extract/indicators.jsonl` directly as registry | ❌ It's extraction output (raw definitions, page refs), not an ops config. But it **seeds** the registry: a one-time script converts active entries. |

## Decisions

1. **`registry.yaml` is the single source of truth.** Loader (pydantic) validates: unique `series_id`, known `module_id`, `scoring_method ∈ {percentile,zscore,band}`, `source` chain non-empty, `playbook_refs` resolve against `04_playbook/modules/`. Loader failure = run aborts before any pull.
2. **Registry entry schema** (superset of Blueprint example):
   ```yaml
   - series_id: HY_OAS
     name: "US High Yield OAS"
     asset_class: Credit
     module_id: Credit
     frequency: W            # canonical; source may be D
     unit: pct
     sources:                # ordered fallback chain (C2)
       - {type: fred, locator: BAMLH0A0HYM2}
       - {type: manual_csv, locator: "hy_oas*.csv"}
     higher_is_better: false
     scoring_method: percentile
     scoring_params: {lookback_weeks: 156}
     critical: true          # missing ⇒ keep last good snapshot
     playbook_refs: [SENTIMENT_POSITIONING]   # module_ids, not filenames
     extract_ref: rates_yield_curve_us_10y_minus_2y_t10y2y  # provenance → 03_extract
     status: active          # active | deferred
   ```
3. **DuckDB schema = Blueprint DDL verbatim** (`dim_series`, `fact_observation`, `fact_weekly`, `fact_feature`, `fact_score`, `agg_regime`, `log_contradiction`) plus `run_log` (structured run history) and `agg_module` (module-level rows; Blueprint folded these into `agg_regime` — separating module scores from regime rows is cleaner and costs nothing).
4. **Fix a Blueprint bug:** `agg_regime.as_of_date` as sole PK cannot hold multiple modules/stances → PK becomes `(as_of_date, module_id, stance_dim)` in `agg_module` / `(as_of_date)` only for the overall regime row.
5. **Migrations:** plain numbered SQL files (`warehouse/migrations/00X_*.sql`) applied by `ipos-init`; version stamp in a `meta` table. No migration framework.
6. **Indicator expansion protocol (34→60→120):** new indicators enter as `status: deferred` rows first; flipping to `active` requires: source chain tested by `ipos-doctor`, scoring params set, playbook_ref present. This keeps the ROI gate from the extraction runbook alive in ops.

## Implementation steps

1. `ipos/config/models.py` — pydantic models (RegistryEntry, ModuleDef, Weights, ScoringDefaults).
2. `ipos/config/load.py` — load + cross-validate all YAML; emit typed `Registry` object.
3. `scripts/seed_registry_from_extract.py` — one-time: `03_extract/indicators.jsonl` (active, verified) → `configs/registry.yaml` skeleton with `extract_ref` provenance; source locators filled from the C2 mapping table.
4. `warehouse/migrations/001_init.sql` — full DDL; `ipos/warehouse/db.py` — connect (RW for job, `read_only=True` helper for report), apply migrations, sync `dim_series` from registry (upsert, disable rows removed from YAML — never delete facts).
5. pytest: loader rejects bad YAML (dup id, unknown module, dangling playbook_ref); migration idempotency; dim_series sync.

## Definition of done
- `uv run ipos-init` creates `data/warehouse.duckdb` with all tables and syncs `dim_series` from a registry of ≥20 active indicators; second run is a no-op; tests green.

**Effort:** M (1–2 days). **Recurring tokens:** 0.
