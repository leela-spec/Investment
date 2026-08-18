-- Migration 005: the forecast log — the prerequisite for ever answering
-- "does this system work?" (01_DECISION_ANALYSIS.md amendment 2026-07-29, item 17).
--
-- Scoring a forecast only counts as evidence if the forecast was recorded
-- BEFORE its outcome window opened. That cannot be reconstructed after the
-- fact: grading the system on history it has already seen is marking your own
-- homework. So this table exists purely to write the week's calls down now,
-- with a resolution rule frozen at write time, and settle them later.
--
-- Deliberately append-only in behaviour: ipos/forecast.py inserts with
-- ON CONFLICT DO NOTHING, so re-running a past week (the pipeline is
-- idempotent) can never rewrite a call that was already made. A row here is a
-- claim with a date on it, not a cache.
--
-- `baseline_value` and `hurdle` are frozen copies, not references. Resolution
-- therefore needs only the benchmark's value on `resolve_on`. This is
-- deliberate: this project has twice had stored history change underneath it
-- (the synthetic purge of 2026-07-27 moved 24 of 26 weeks of Credit scores),
-- and a claim whose own goalposts move with the warehouse is not a claim.
--
-- No display layer reads this yet. That is the point: the logging is
-- time-gated and cannot be back-filled, the report section is not.

CREATE TABLE IF NOT EXISTS log_forecast (
  as_of_date       DATE    NOT NULL,   -- the week the call was made
  stance_dim       VARCHAR NOT NULL,   -- which stance dimension made it
  horizon_weeks    INTEGER NOT NULL,   -- 4 / 13 / 26, frozen set
  benchmark_series VARCHAR NOT NULL,   -- the series the claim resolves against
  direction        INTEGER NOT NULL,   -- +1 = benchmark should rise, -1 = fall
  tilt             DOUBLE  NOT NULL,   -- the tilt the call came from
  probability      DOUBLE  NOT NULL,   -- P(claim true), 0-1, for the Brier score
  baseline_value   DOUBLE  NOT NULL,   -- benchmark level at as_of_date (frozen)
  hurdle           DOUBLE  NOT NULL,   -- median horizon-change to beat (frozen)
  resolve_on       DATE    NOT NULL,   -- as_of_date + horizon_weeks
  criterion        VARCHAR NOT NULL,   -- human-readable rule, frozen at write time
  scoring_version  VARCHAR NOT NULL,   -- calls are not comparable across a bump
  PRIMARY KEY (as_of_date, stance_dim, horizon_weeks)
);
