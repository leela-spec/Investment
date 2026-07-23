# Phase 0 + Phase 1 Work Plan — Walking Skeleton (concrete build spec)

**Goal:** one command, `uv run ipos-weekly`, produces a correct `snapshot.json` + `report.md` for the current week from ~20 real indicators, idempotently, with green tests. This is the thinnest complete slice of the value loop. Widening (→60, regime, HTML, AI) is Phase 2+.

**Ground rule:** build ONLY what is listed here. Resist adding indicators, sources, or features — scope creep is failure mode #2 in `01_DECISION_ANALYSIS.md`. Meso plans C1–C3, C6, C8 are the authority for design; this file is the execution order.

---

## Step A — Scaffold (Phase 0)

Create exactly this (empty dirs get a `.gitkeep`):

```
pyproject.toml            # [project] name=ipos; entry points: ipos-init, ipos-pull, ipos-score, ipos-weekly, ipos-doctor
uv.lock                   # via `uv sync`
.env.example              # FRED_API_KEY=   (only key needed for Phase 1; Stooq needs none)
ipos/
  __init__.py
  cli.py                  # argparse dispatch to the entry points
  run.py                  # stage runner + run_log + fail-safe (C8)
  config/
    models.py             # pydantic: RegistryEntry, ModuleDef, Weights, ScoringDefaults
    load.py               # load+cross-validate all YAML -> typed Registry
  warehouse/
    db.py                 # connect (RW job / read_only helper), apply migrations, sync dim_series
    migrations/001_init.sql
  etl/
    base.py               # connector protocol + fallback executor + parquet archive writer
    fred.py
    stooq.py
    manual_csv.py
    validators.py         # pandera schemas + sanity ranges
  transforms/
    run.py
    sql/{canonical_weekly.sql,features.sql,scores_percentile.sql,scores_band.sql}
  aggregate/
    modules.py stance.py risk_budget.py     # regime.py + contradictions.py are Phase 2
  export/
    snapshot.py report.py
configs/
  registry.yaml           # the golden-20 below
  modules.yaml weights.yaml scoring_defaults.yaml
data/                     # gitignored except .gitkeep: warehouse.duckdb, archive/, inbox/, exports/
tests/
  fixtures/ test_config.py test_scoring.py test_snapshot.py test_failsafe.py
scripts/
  backfill_seed.py        # RUN EARLY (FRED OAS 3y window)
  seed_registry_from_extract.py
```

Add `data/` (except `.gitkeep`), `.env`, `*.duckdb`, `__pycache__`, `.venv` to `.gitignore`.

## Step B — The "golden 20" registry (`configs/registry.yaml`)

Highest-reliability first: 12 FRED (one key) + 8 Stooq (no key). Directionality is relative to "risk-on / supportive". Verify each locator on first pull; anything flaky drops to `status: deferred` and is replaced from the Phase-3 pool — do not block the skeleton on one bad ticker. Mark unverified tickers `needs_verification: true` (repo convention).

| # | series_id | name | source (locator) | module_id | asset_class | higher_is_better | scoring | notes |
|---|---|---|---|---|---|---|---|---|
| 1 | T10Y2Y | 10y–2y curve | fred:T10Y2Y | GrowthRisk | Rates | true | band | bands from rules.jsonl: <0→20 … ≥1.0→90 |
| 2 | T10Y3M | 10y–3m curve | fred:T10Y3M | GrowthRisk | Rates | true | band | confirmation pair to #1 |
| 3 | DGS10 | 10y yield | fred:DGS10 | RatesLiquidity | Rates | false | zscore | |
| 4 | NFCI | Chicago Fed fin. conditions | fred:NFCI | RatesLiquidity | Rates | false | zscore | negative = loose = supportive |
| 5 | DTWEXBGS | Trade-weighted USD | fred:DTWEXBGS | FX | FX | false | percentile | strong USD = risk-off (per module) |
| 6 | HY_OAS | US HY OAS | fred:BAMLH0A0HYM2 | Credit | Credit | false | percentile | ⚠ 3y window — archive from day 1 |
| 7 | IG_OAS | US IG OAS | fred:BAMLC0A0CM | Credit | Credit | false | percentile | ⚠ 3y window |
| 8 | VIXCLS | VIX | fred:VIXCLS | EquityRisk | Equity | false | percentile | |
| 9 | WALCL | Fed balance sheet | fred:WALCL | Liquidity | Rates | true | zscore | QE/QT proxy; extract_ref exists |
| 10 | UMCSENT | UMich consumer sentiment | fred:UMCSENT | Fundamentals | Equity | true | percentile | monthly → weekly ffill |
| 11 | WTI | WTI crude | fred:DCOILWTICO | Commodities | Commodities | true | percentile | growth/inflation proxy |
| 12 | DFF | Fed funds rate | fred:DFF | RatesLiquidity | Rates | false | zscore | policy tightness |
| 13 | SPX | S&P 500 | stooq:^spx | EquityRisk | Equity | true | percentile | benchmark + regime input (Phase 2) |
| 14 | NDX | Nasdaq 100 | stooq:^ndx | EquityRisk | Equity | true | percentile | |
| 15 | RUT | Russell 2000 | stooq:^rut | EquityRisk | Equity | true | percentile | small-cap risk appetite |
| 16 | DAX | DAX | stooq:^dax | EquityRisk | Equity | true | percentile | non-US breadth |
| 17 | GOLD | Gold | stooq:xauusd | Commodities | Commodities | true | percentile | |
| 18 | COPPER | Copper | stooq:hg.f | Commodities | Commodities | true | percentile | growth proxy (verify ticker) |
| 19 | EURUSD | EUR/USD | stooq:eurusd | FX | FX | true | percentile | USD inverse cross-check |
| 20 | US10Y_STOOQ | US 10y (mkt) | stooq:10usy.b | RatesLiquidity | Rates | false | zscore | cross-source check vs DGS10 (verify) |

Modules touched: EquityRisk, RatesLiquidity, GrowthRisk, Credit, Liquidity, FX, Commodities, Fundamentals → define these in `modules.yaml` with equal weights initially (tune in Phase 2), `playbook_refs` pointing at existing modules where they map (e.g. Credit/EquityRisk → `SENTIMENT_POSITIONING`, GrowthRisk → none yet, EquityRisk regime → `MARKET_CONDITIONS`).

## Step C — Build order (each step ends compilable + a test)

1. `config/models.py` + `load.py`; `configs/*.yaml` with golden-20 → `tests/test_config.py` (rejects dup id, unknown module, Σweights≠1, dangling playbook_ref). *DoD: `python -c "from ipos.config.load import load_registry; load_registry()"` succeeds.*
2. `warehouse/migrations/001_init.sql` = Blueprint DDL (`dim_series, fact_observation, fact_weekly, fact_feature, fact_score, agg_module, agg_regime, log_contradiction, run_log, meta`) with the C1 PK fix (`agg_module` keyed `(as_of_date, module_id, stance_dim)`); `warehouse/db.py`. → `ipos-init` creates DB, syncs `dim_series`, second run no-op.
3. `etl/base.py` (protocol + fallback + **parquet archive before transform**), `fred.py`, `stooq.py`, `manual_csv.py`, `validators.py`. → `ipos-pull` fills `fact_observation`; offline path uses archive + marks stale; no unhandled exception on a dead source. Tests use recorded fixtures, **no live calls**.
4. `transforms/sql/*` + `transforms/run.py`: canonical weekly (last obs ≤ Friday; monthly series ffill), features (delta_1w/4w/12w, pctile_156w, z_104w tanh-damped, trend), scoring (percentile + band; zscore may wait for Phase 2 if band+percentile cover the 20 — here #3/#4/#9/#12/#20 need zscore, so include it). → `test_scoring.py`: monotonicity, inversion, 0–100 bounds, hand-computed fixture, idempotency.
5. `aggregate/modules.py + stance.py + risk_budget.py`: weighted module scores, tilt = clip((score−50)/50), risk_budget = weighted blend (regime scaler = 1.0 placeholder until Phase 2). Write `agg_module`/`agg_regime`.
6. `export/snapshot.py`: build `snapshot.json` + `snapshot.min.json` (Blueprint schema + version stamps), archive under `data/exports/snapshots/YYYY-MM-DD/`; `export/report.py`: jinja2 deterministic `report.md` (no LLM in Phase 1). → `test_snapshot.py`: jsonschema valid, deterministic bytes on rerun.
7. `run.py` + `cli.py`: wire stages pull→canonical→features→scores→aggregate→export with run_log + fail-safe (critical-missing ⇒ keep last good, FAILED_ATTEMPT row). → `test_failsafe.py`.
8. `scripts/backfill_seed.py` — **run against live FRED immediately** to archive max OAS history; `scripts/seed_registry_from_extract.py` — provenance helper.

## Definition of Done (Phase 1)

- `uv run ipos-init && uv run ipos-weekly` on a clean checkout (with a FRED key) produces `data/exports/snapshots/<friday>/snapshot.json` + `report.md`.
- Re-running the same `--as-of` yields byte-identical `snapshot.json`.
- Pulling with the network off produces a degraded-but-valid snapshot (stale flags, lower confidence), not a crash.
- `uv run pytest -q` green in < 30 s; `python scripts/qa_repo.py` still exits 0.
- FRED OAS history archived to `data/archive/fred/BAMLH0A0HYM2/` (and IG).
- `PROJECT_STATE.md` §2/§3 updated to mark Phase 1 done and point at Phase 2.

## Explicitly deferred to Phase 2+ (do not build now)

z-score confidence composite · regime classifier + risk_scaler · contradictions engine · static HTML report · LLM narration · Task Scheduler registration · scrapes (CBOE/AAII/NAAIM/CNN/ISM) · indicators 21–60 · golden-snapshot regression harness. All are spec'd in `05_blueprint/meso/`.
