-- Rebuild fact_weekly from fact_observation for every enabled series across
-- the weekly Friday grid (temp table `week_keys(as_of_date)` is created by the
-- driver). Canonical rule (Blueprint): the weekly value is the last observation
-- at or before the week's Friday. Implemented with a DuckDB ASOF JOIN, which
-- picks the greatest obs_date <= as_of_date per series. Revision-safe: if a
-- series gets a new vintage, re-running recomputes the affected weeks.
--
-- Determinism: when a single obs_date carries multiple vintages we keep the
-- lexicographically greatest vintage_id (stable), so re-runs are byte-identical.
-- A real observation always outranks a synthetic one for the same obs_date
-- regardless of vintage-string ordering ("synthetic@..." sorts after a real
-- vintage's series-id prefix, so without this a synthetic seed row could
-- silently outrank a later real pull that landed on the same calendar date --
-- the exact "synthetic served as real" leak D5 amendment 12 exists to close).
-- On a real (non---seed-offline) run, synthetic rows are excluded from the
-- candidate set entirely (bound param $1 = include_synthetic) -- otherwise a
-- fabricated *later* obs_date (the synthetic seed's own multi-year history)
-- would legitimately out-ASOF a real but older observation, which the
-- same-date tie-break above cannot catch.

INSERT OR REPLACE INTO fact_weekly
  (series_id, as_of_date, value, vintage_id, obs_date, ingested_at)
WITH latest_obs AS (
  SELECT series_id, obs_date, value, vintage_id, ingested_at
  FROM (
    SELECT *,
           row_number() OVER (
             PARTITION BY series_id, obs_date
             ORDER BY (vintage_id LIKE 'synthetic@%') ASC, vintage_id DESC, ingested_at DESC
           ) AS rn
    FROM fact_observation
    WHERE ($1 OR vintage_id NOT LIKE 'synthetic@%')
  )
  WHERE rn = 1
),
grid AS (
  SELECT s.series_id, w.as_of_date
  FROM (SELECT series_id FROM dim_series WHERE enabled) s
  CROSS JOIN week_keys w
)
SELECT g.series_id, g.as_of_date, o.value, o.vintage_id, o.obs_date, o.ingested_at
FROM grid g
ASOF JOIN latest_obs o
  ON o.series_id = g.series_id
 AND g.as_of_date >= o.obs_date;
