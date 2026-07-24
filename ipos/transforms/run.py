"""Transform driver: canonical weekly -> features -> scores -> confidence.

Reads ``fact_observation``, writes ``fact_weekly``, ``fact_feature``,
``fact_score``. Deterministic: ``as_of_date`` is an explicit parameter, no
wall-clock is read, and re-running the same week yields byte-identical rows.
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from ipos.config.models import Registry
from ipos.transforms.scoring import band_score

SQL_DIR = Path(__file__).resolve().parent / "sql"


# --- weekly Friday grid -----------------------------------------------------

def _friday_grid(con: duckdb.DuckDBPyConnection, as_of: dt.date) -> list[dt.date]:
    row = con.execute("SELECT min(obs_date), max(obs_date) FROM fact_observation").fetchone()
    if not row or row[0] is None:
        return []
    first_obs = row[0]
    if isinstance(first_obs, dt.datetime):
        first_obs = first_obs.date()
    n_weeks = (as_of - first_obs).days // 7 + 1
    return [as_of - dt.timedelta(weeks=i) for i in range(n_weeks - 1, -1, -1)]


def build_canonical(con: duckdb.DuckDBPyConnection, as_of: dt.date) -> int:
    weeks = _friday_grid(con, as_of)
    if not weeks:
        return 0
    wk = pd.DataFrame({"as_of_date": [pd.Timestamp(w) for w in weeks]})
    con.register("week_keys_df", wk)
    con.execute("CREATE OR REPLACE TEMP TABLE week_keys AS SELECT as_of_date::DATE AS as_of_date FROM week_keys_df")
    sql = (SQL_DIR / "canonical_weekly.sql").read_text(encoding="utf-8")
    con.execute(sql)
    con.unregister("week_keys_df")
    return con.execute(
        "SELECT count(*) FROM fact_weekly WHERE as_of_date <= ?", [as_of]
    ).fetchone()[0]


# --- features + scores ------------------------------------------------------

def compute(
    con: duckdb.DuckDBPyConnection,
    registry: Registry,
    as_of: dt.date,
    forced_stale: set[str] | None = None,
) -> dict:
    """Compute features, scores and confidence for every week <= as_of and
    write them. Returns a small summary.

    ``forced_stale`` marks the *current* week's rows for those series stale
    regardless of obs age — used when the pull layer served archived data
    because live sources were unreachable (offline degraded run)."""
    forced_stale = forced_stale or set()
    defaults = registry.defaults
    weekly = con.execute(
        """
        SELECT series_id, as_of_date, value, obs_date
        FROM fact_weekly WHERE as_of_date <= ?
        ORDER BY series_id, as_of_date
        """,
        [as_of],
    ).df()
    if weekly.empty:
        return {"scored_series": 0, "weeks": 0}

    entries = {e.series_id: e for e in registry.active()}
    stale_lag = defaults.staleness_days
    weekly["as_of_date"] = pd.to_datetime(weekly["as_of_date"])
    weekly["obs_date"] = pd.to_datetime(weekly["obs_date"])

    score_frames: list[pd.DataFrame] = []
    feat_frames: list[pd.DataFrame] = []

    for series_id, g in weekly.groupby("series_id", sort=True):
        entry = entries.get(series_id)
        if entry is None:
            continue
        g = g.sort_values("as_of_date").reset_index(drop=True)
        v = g["value"].astype(float)
        weeks = g["as_of_date"].dt.date
        lag_allow = stale_lag.get(entry.frequency, 14)

        pct_lb = entry.scoring_params.lookback_weeks or defaults.percentile_lookback_weeks
        z_lb = entry.scoring_params.z_lookback_weeks or defaults.zscore_lookback_weeks
        k = entry.scoring_params.z_k or defaults.zscore_k
        tw = defaults.trend_slope_weeks

        # --- vectorized features (identical math to ipos.transforms.scoring) ---
        d1, d4, d12 = v.diff(1), v.diff(4), v.diff(12)
        raw_pct = v.rolling(pct_lb, min_periods=1).apply(
            lambda w: float(np.mean(w <= w[-1]) * 100.0), raw=True
        )
        rmean = v.rolling(z_lb, min_periods=1).mean()
        rstd = v.rolling(z_lb, min_periods=1).std(ddof=0)
        raw_z = ((v - rmean) / rstd).where(rstd > 0, 0.0)
        trend = pd.Series(np.sign(v.diff(tw).to_numpy()), index=v.index).fillna(0.0)

        # --- vectorized score by method ---
        if entry.scoring_method == "percentile":
            score = raw_pct if entry.higher_is_better else 100.0 - raw_pct
            lookback = pct_lb
        elif entry.scoring_method == "zscore":
            s = (50.0 * (np.tanh(raw_z / k) + 1.0)).clip(0, 100)
            score = s if entry.higher_is_better else 100.0 - s
            lookback = z_lb
        else:  # band
            bands = entry.scoring_params.bands or []
            score = v.apply(lambda x: band_score(x, bands))
            lookback = None

        # --- staleness (ratio drives graded confidence quality) ---
        age = (g["as_of_date"] - g["obs_date"]).dt.days
        staleness_ratio = (age / lag_allow).clip(lower=0.0)
        stale = age > lag_allow
        if series_id in forced_stale:
            forced = weeks == as_of
            stale = stale | forced
            staleness_ratio = staleness_ratio.where(~forced, staleness_ratio.clip(lower=2.0))

        score_frames.append(pd.DataFrame({
            "series_id": series_id,
            "as_of_date": weeks,
            "score": score.round(6),
            "method": entry.scoring_method,
            "lookback": lookback,
            "stale": stale,
            "staleness_ratio": staleness_ratio.round(4),
            "module_id": entry.module_id,
        }))

        feat_long = pd.DataFrame({
            "as_of_date": weeks, "delta_1w": d1, "delta_4w": d4, "delta_12w": d12,
            "pctile_156w": raw_pct, "z_104w": raw_z, "trend": trend,
        }).melt(id_vars="as_of_date", var_name="feature_id", value_name="value").dropna(subset=["value"])
        feat_long.insert(0, "series_id", series_id)
        feat_frames.append(feat_long)

    scores_df = pd.concat(score_frames, ignore_index=True)
    scores_df = _confidence(scores_df, defaults)

    # --- write fact_feature ---
    con.execute("DELETE FROM fact_feature WHERE as_of_date <= ?", [as_of])
    feats_df = pd.concat(feat_frames, ignore_index=True)
    if not feats_df.empty:
        con.register("fdf", feats_df)
        con.execute(
            "INSERT OR REPLACE INTO fact_feature SELECT series_id, as_of_date::DATE, feature_id, value FROM fdf"
        )
        con.unregister("fdf")

    # --- write fact_score ---
    con.execute("DELETE FROM fact_score WHERE as_of_date <= ?", [as_of])
    params = json.dumps({
        "scoring_version": defaults.scoring_version,
        "zscore_k": defaults.zscore_k,
        "percentile_lookback_weeks": defaults.percentile_lookback_weeks,
        "zscore_lookback_weeks": defaults.zscore_lookback_weeks,
    }, sort_keys=True)
    out = scores_df.copy()
    out["params_json"] = params
    con.register("sdf", out)
    con.execute(
        """
        INSERT OR REPLACE INTO fact_score
          (series_id, as_of_date, score_0_100, scoring_method, lookback_weeks,
           params_json, confidence_0_100, stale)
        SELECT series_id, as_of_date::DATE, score, method, lookback,
               params_json, confidence, stale
        FROM sdf
        """
    )
    con.unregister("sdf")

    return {
        "scored_series": scores_df["series_id"].nunique(),
        "weeks": int(scores_df["as_of_date"].nunique()),
        "rows": len(scores_df),
    }


def _confidence(scores_df: pd.DataFrame, defaults) -> pd.DataFrame:
    """Confidence = quality + stability (coherence off by default — see
    ConfidenceWeights). quality is a GRADED staleness score; stability rewards
    low recent score-volatility with a configurable scale."""
    w = defaults.confidence_weights
    scale = defaults.stability_scale
    df = scores_df.sort_values(["series_id", "as_of_date"]).copy()

    # quality: 100 while fresh (staleness_ratio <= 1), degrading as data ages
    # past its allowed lag; floored at 20 (never zero — the value still exists).
    df["quality"] = (100.0 - 55.0 * (df["staleness_ratio"] - 1.0).clip(lower=0.0)).clip(20.0, 100.0)

    # stability: low volatility of recent score changes => high stability.
    def _stab(group: pd.Series) -> pd.Series:
        vol = group.diff().rolling(window=8, min_periods=2).std().fillna(0.0)
        return (100.0 * np.exp(-vol / scale)).clip(0, 100)
    df["stability"] = df.groupby("series_id")["score"].transform(_stab)

    # coherence: retained for optional use but weighted 0 by default (would
    # double-count the contradictions engine). Only computed if it has weight.
    if w.coherence > 0:
        module_mean = df.groupby(["as_of_date", "module_id"])["score"].transform("mean")
        module_size = df.groupby(["as_of_date", "module_id"])["score"].transform("size")
        coherence = (100.0 - (df["score"] - module_mean).abs()).clip(0, 100)
        df["coherence"] = coherence.where(module_size > 1, 50.0)
    else:
        df["coherence"] = 0.0

    total_w = w.quality + w.stability + w.coherence
    df["confidence"] = (
        (w.quality * df["quality"] + w.stability * df["stability"]
         + w.coherence * df["coherence"]) / total_w
    ).clip(0, 100).round(6)
    return df
