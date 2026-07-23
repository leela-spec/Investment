-- IPOS warehouse schema (migration 001). Blueprint DDL, with the C1 fixes:
--   * agg_module split out from agg_regime and keyed
--     (as_of_date, module_id, stance_dim) so multiple modules/stances coexist
--     (the Blueprint's agg_regime.as_of_date-only PK could not);
--   * agg_regime keeps one overall row per as_of_date;
--   * run_log added for structured run history (C8 observability backend);
--   * meta table stamps the schema version.
-- Idempotent: every object uses IF NOT EXISTS so ipos-init re-runs are no-ops.

CREATE TABLE IF NOT EXISTS meta (
  key         VARCHAR PRIMARY KEY,
  value       VARCHAR NOT NULL,
  updated_at  TIMESTAMP NOT NULL DEFAULT now()
);

-- Series metadata (derived from configs/registry.yaml at init; never hand-edited).
CREATE TABLE IF NOT EXISTS dim_series (
  series_id         VARCHAR PRIMARY KEY,
  name              VARCHAR NOT NULL,
  asset_class       VARCHAR NOT NULL,
  region            VARCHAR,
  frequency         VARCHAR NOT NULL,   -- 'D','W','M'
  unit              VARCHAR,
  source_type       VARCHAR NOT NULL,   -- primary source type
  source_locator    VARCHAR,
  higher_is_better  BOOLEAN NOT NULL,
  scoring_method    VARCHAR NOT NULL,   -- percentile|zscore|band
  module_id         VARCHAR NOT NULL,
  critical          BOOLEAN NOT NULL DEFAULT FALSE,
  enabled           BOOLEAN NOT NULL DEFAULT TRUE,
  created_at        TIMESTAMP NOT NULL DEFAULT now()
);

-- Raw observations (revision-aware; append-only via upsert).
CREATE TABLE IF NOT EXISTS fact_observation (
  series_id    VARCHAR NOT NULL,
  obs_date     DATE    NOT NULL,
  value        DOUBLE  NOT NULL,
  vintage_id   VARCHAR NOT NULL,   -- pull timestamp (market) / provider version
  ingested_at  TIMESTAMP NOT NULL,
  source_hash  VARCHAR,
  PRIMARY KEY (series_id, obs_date, vintage_id)
);

-- Canonical weekly values (what scoring uses): last obs <= as_of_date.
CREATE TABLE IF NOT EXISTS fact_weekly (
  series_id    VARCHAR NOT NULL,
  as_of_date   DATE    NOT NULL,
  value        DOUBLE  NOT NULL,
  vintage_id   VARCHAR NOT NULL,
  obs_date     DATE    NOT NULL,   -- source obs date behind this canonical value
  ingested_at  TIMESTAMP NOT NULL,
  PRIMARY KEY (series_id, as_of_date)
);

-- Features (deltas, rolling stats, trend).
CREATE TABLE IF NOT EXISTS fact_feature (
  series_id    VARCHAR NOT NULL,
  as_of_date   DATE    NOT NULL,
  feature_id   VARCHAR NOT NULL,   -- delta_1w, delta_4w, delta_12w, pctile_156w, z_104w, trend, ...
  value        DOUBLE,
  PRIMARY KEY (series_id, as_of_date, feature_id)
);

-- Scores (0-100) with frozen params for reproducibility.
CREATE TABLE IF NOT EXISTS fact_score (
  series_id        VARCHAR NOT NULL,
  as_of_date       DATE    NOT NULL,
  score_0_100      DOUBLE  NOT NULL,
  scoring_method   VARCHAR NOT NULL,
  lookback_weeks   INTEGER,
  params_json      VARCHAR,
  confidence_0_100 DOUBLE  NOT NULL,
  stale            BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (series_id, as_of_date)
);

-- Module-level aggregates (C1 fix: keyed by as_of_date+module_id+stance_dim).
CREATE TABLE IF NOT EXISTS agg_module (
  as_of_date        DATE    NOT NULL,
  module_id         VARCHAR NOT NULL,
  stance_dim        VARCHAR NOT NULL,
  module_score      DOUBLE  NOT NULL,
  module_confidence DOUBLE  NOT NULL,
  stance_value      DOUBLE  NOT NULL,   -- tilt in [-1, +1]
  params_json       VARCHAR,
  PRIMARY KEY (as_of_date, module_id, stance_dim)
);

-- Overall regime / risk-budget row (one per week).
CREATE TABLE IF NOT EXISTS agg_regime (
  as_of_date        DATE    PRIMARY KEY,
  risk_budget_0_100 DOUBLE  NOT NULL,
  confidence_0_100  DOUBLE  NOT NULL,
  regime_label      VARCHAR,            -- Phase 2 classifier; NULL in Phase 1
  risk_scaler       DOUBLE  NOT NULL DEFAULT 1.0,
  params_json       VARCHAR
);

-- Contradictions (Phase 2 engine writes here; table exists from day 1).
CREATE TABLE IF NOT EXISTS log_contradiction (
  as_of_date       DATE    NOT NULL,
  contradiction_id VARCHAR NOT NULL,
  severity         VARCHAR NOT NULL,   -- low/med/high
  summary          VARCHAR NOT NULL,
  details_json     VARCHAR,
  created_at       TIMESTAMP NOT NULL DEFAULT now(),
  PRIMARY KEY (as_of_date, contradiction_id)
);

-- Structured run history (C8 observability).
CREATE TABLE IF NOT EXISTS run_log (
  run_id       VARCHAR NOT NULL,
  as_of_date   DATE    NOT NULL,
  stage        VARCHAR NOT NULL,
  status       VARCHAR NOT NULL,   -- OK | FAILED_ATTEMPT | SKIPPED
  started_at   TIMESTAMP NOT NULL,
  finished_at  TIMESTAMP,
  rows_in      INTEGER,
  rows_out     INTEGER,
  detail       VARCHAR,
  PRIMARY KEY (run_id, stage)
);
