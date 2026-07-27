-- Migration 004: actual portfolio weights per module, so the contradictions
-- engine (ipos/aggregate/contradictions.py) can compare holdings against
-- stance the same way it reads every other DB-backed signal (an as_of_date-
-- scoped query), instead of needing snapshot-dict access it doesn't have.
-- One row per module SCORED that week (agg_module), even when weight is 0 --
-- this distinguishes "you hold 0% of this module" (a real, known 0) from
-- "no portfolio CSV at all this week" (no rows -> portfolio_weight() is None).

CREATE TABLE IF NOT EXISTS fact_portfolio_weight (
  as_of_date  DATE    NOT NULL,
  module_id   VARCHAR NOT NULL,
  weight_pct  DOUBLE  NOT NULL,
  value_eur   DOUBLE  NOT NULL,
  PRIMARY KEY (as_of_date, module_id)
);
