-- Migration 003: daily OHLC bars for benchmark series (regime governor).
-- The Stooq CSV already returns Open/High/Low/Close; we previously kept only
-- Close. Capturing full bars lets the regime classifier use REAL weekly range
-- overlap + ATR (the MARKET_CONDITIONS definitions) instead of close-only
-- proxies. Populated only for the few benchmark series; revision-aware like
-- fact_observation.

CREATE TABLE IF NOT EXISTS fact_ohlc (
  series_id    VARCHAR NOT NULL,
  obs_date     DATE    NOT NULL,
  open         DOUBLE,
  high         DOUBLE,
  low          DOUBLE,
  close        DOUBLE  NOT NULL,
  vintage_id   VARCHAR NOT NULL,
  ingested_at  TIMESTAMP NOT NULL,
  PRIMARY KEY (series_id, obs_date, vintage_id)
);
