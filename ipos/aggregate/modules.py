"""Aggregation: indicator scores -> module scores -> stance vector ->
overall risk budget. Writes ``agg_module`` (one row per module/stance_dim) and
``agg_regime`` (one overall row per week).

Phase 1: risk_scaler is a fixed 1.0 placeholder (the regime classifier that
sets it is Phase 2). Everything here is a deterministic weighted blend.
"""

from __future__ import annotations

import datetime as dt
import json

import duckdb

from ipos.config.models import Registry


def _tilt(module_score: float) -> float:
    """Map a 0-100 module score to a [-1, +1] tilt (Blueprint)."""
    return max(-1.0, min(1.0, (module_score - 50.0) / 50.0))


def aggregate(con: duckdb.DuckDBPyConnection, registry: Registry, as_of: dt.date) -> dict:
    weights = registry.weights
    modules = registry.modules

    scores = con.execute(
        """
        SELECT s.series_id, s.score_0_100, s.confidence_0_100, d.module_id
        FROM fact_score s JOIN dim_series d USING (series_id)
        WHERE s.as_of_date = ? AND d.enabled
        """,
        [as_of],
    ).fetchall()
    if not scores:
        return {"modules": 0, "risk_budget": None}

    by_module: dict[str, list[tuple[str, float, float]]] = {}
    for series_id, score, conf, module_id in scores:
        by_module.setdefault(module_id, []).append((series_id, score, conf))

    # --- module scores + confidence + tilt ---
    con.execute("DELETE FROM agg_module WHERE as_of_date = ?", [as_of])
    module_scores: dict[str, float] = {}
    module_conf: dict[str, float] = {}
    for module_id, members in by_module.items():
        iw = weights.module_indicator_weights.get(module_id, {})
        total_w = sum(iw.get(sid, 0.0) for sid, _, _ in members)
        if total_w <= 0:  # equal-weight fallback
            iw = {sid: 1.0 / len(members) for sid, _, _ in members}
            total_w = 1.0
        mscore = sum(iw.get(sid, 0.0) * sc for sid, sc, _ in members) / total_w
        mconf = sum(iw.get(sid, 0.0) * cf for sid, _, cf in members) / total_w
        tilt = _tilt(mscore)
        module_scores[module_id] = mscore
        module_conf[module_id] = mconf
        stance_dim = modules[module_id].stance_dim if module_id in modules else module_id
        con.execute(
            """
            INSERT OR REPLACE INTO agg_module
              (as_of_date, module_id, stance_dim, module_score, module_confidence,
               stance_value, params_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                as_of, module_id, stance_dim, round(mscore, 6), round(mconf, 6),
                round(tilt, 6), json.dumps({"weights": iw}, sort_keys=True),
            ],
        )

    # --- overall risk budget + confidence ---
    rb_w = weights.risk_budget_weights
    covered = {m: w for m, w in rb_w.items() if m in module_scores}
    total_rb_w = sum(covered.values())
    risk_budget = (
        sum(w * module_scores[m] for m, w in covered.items()) / total_rb_w
        if total_rb_w > 0 else 0.0
    )
    overall_conf = (
        sum(w * module_conf[m] for m, w in covered.items()) / total_rb_w
        if total_rb_w > 0 else 0.0
    )
    risk_scaler = 1.0  # Phase 2 regime classifier sets this

    con.execute("DELETE FROM agg_regime WHERE as_of_date = ?", [as_of])
    con.execute(
        """
        INSERT OR REPLACE INTO agg_regime
          (as_of_date, risk_budget_0_100, confidence_0_100, regime_label,
           risk_scaler, params_json)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            as_of, round(risk_budget * risk_scaler, 6), round(overall_conf, 6),
            None, risk_scaler, json.dumps({"risk_budget_weights": covered}, sort_keys=True),
        ],
    )

    return {
        "modules": len(module_scores),
        "risk_budget": round(risk_budget, 6),
        "confidence": round(overall_conf, 6),
    }


def stance_vector(con: duckdb.DuckDBPyConnection, as_of: dt.date) -> dict[str, float]:
    rows = con.execute(
        "SELECT stance_dim, stance_value FROM agg_module WHERE as_of_date = ? ORDER BY stance_dim",
        [as_of],
    ).fetchall()
    return {dim: round(val, 6) for dim, val in rows}
