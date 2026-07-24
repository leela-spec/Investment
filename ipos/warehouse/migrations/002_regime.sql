-- Migration 002: regime classifier outputs on the overall weekly row.
-- Adds the regime confidence and the policy-selectors JSON (position_size,
-- entry_style, trailing_stop, initial_stop) so the report can explain *why*
-- risk changed. regime_label + risk_scaler already exist from 001.

ALTER TABLE agg_regime ADD COLUMN IF NOT EXISTS regime_confidence DOUBLE;
ALTER TABLE agg_regime ADD COLUMN IF NOT EXISTS policy_json VARCHAR;
