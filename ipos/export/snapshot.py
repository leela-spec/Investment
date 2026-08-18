"""Snapshot exporter: build the weekly ``snapshot.json`` (Blueprint schema plus
version stamps) and a minified ``snapshot.min.json`` for the AI layer, archived
under ``data/exports/snapshots/YYYY-MM-DD/``.

Determinism contract: the snapshot embeds NO wall-clock — only ``as_of`` and
config version stamps — and all floats are rounded and keys sorted, so a
re-run of the same week is byte-identical (Phase-1 Definition of Done).
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import duckdb
import jsonschema

from ipos.aggregate.portfolio import aggregate_portfolio, convert_to_eur, load_mapping
from ipos.config.load import REPO_ROOT
from ipos.config.models import Registry
from ipos.econ_calendar import events_for
from ipos.etl import portfolio_csv
from ipos.etl.portfolio_csv import load_positions

SCHEMA_VERSION = "1.0"
EXPORTS_DIR = REPO_ROOT / "data" / "exports" / "snapshots"

_ROUND = 4


def _r(x) -> float | None:
    return None if x is None else round(float(x), _ROUND)


def _trend_word(v: float | None) -> str:
    if v is None:
        return "flat"
    return "up" if v > 0 else ("down" if v < 0 else "flat")


SCORE_DELTA_HORIZONS = {"1w": 1, "4w": 4, "12w": 12, "52w": 52}

# How far back the contradiction-recurrence count looks. A contradiction firing
# for the first time and one that has fired 8 of the last 10 weeks are different
# situations, and the single-week query this replaces could not tell them apart.
RECURRENCE_WEEKS = 10


def _score_deltas(con: duckdb.DuckDBPyConnection, as_of: dt.date) -> dict[str, dict]:
    """Per-indicator change in the 0-100 SCORE over 1w / 4w / 12w / 52w.

    Score deltas rather than raw-value deltas because scores are the only
    cross-comparable quantity in the system: WALCL moving "+4,350" and COPPER
    moving "+0.14" cannot be ranked against each other, but "+12 score points"
    and "+3 score points" can. Horizons step back by *available scored weeks*,
    not calendar arithmetic, so a gap in history shifts the comparison week
    instead of silently returning None."""
    weeks = [r[0] for r in con.execute(
        "SELECT DISTINCT as_of_date FROM fact_score WHERE as_of_date <= ? "
        "ORDER BY as_of_date DESC LIMIT ?",
        [as_of, max(SCORE_DELTA_HORIZONS.values()) + 1],
    ).fetchall()]
    if not weeks:
        return {}
    current = dict(con.execute(
        "SELECT series_id, score_0_100 FROM fact_score WHERE as_of_date = ?", [weeks[0]]
    ).fetchall())
    out: dict[str, dict] = {sid: {} for sid in current}
    for key, back in SCORE_DELTA_HORIZONS.items():
        if back >= len(weeks):
            for sid in current:
                out[sid][key] = None
            continue
        past = dict(con.execute(
            "SELECT series_id, score_0_100 FROM fact_score WHERE as_of_date = ?",
            [weeks[back]],
        ).fetchall())
        for sid, score in current.items():
            out[sid][key] = _r(score - past[sid]) if sid in past else None
    return out


def _recurrence(
    con: duckdb.DuckDBPyConnection, as_of: dt.date, weeks: int = RECURRENCE_WEEKS
) -> tuple[dict[str, int], int]:
    """How many of the last `weeks` weeks each contradiction_id fired in.

    Returns (counts_by_id, weeks_observed). `weeks_observed` is the number of
    weeks that actually exist in ``log_contradiction`` — reporting "6 of 10"
    when only 3 weeks of history exist would overstate the record."""
    observed = [r[0] for r in con.execute(
        "SELECT DISTINCT as_of_date FROM log_contradiction WHERE as_of_date <= ? "
        "ORDER BY as_of_date DESC LIMIT ?",
        [as_of, weeks],
    ).fetchall()]
    if not observed:
        return {}, 0
    counts = dict(con.execute(
        "SELECT contradiction_id, count(DISTINCT as_of_date) FROM log_contradiction "
        "WHERE as_of_date >= ? AND as_of_date <= ? GROUP BY contradiction_id",
        [min(observed), as_of],
    ).fetchall())
    return counts, len(observed)


def _budget_attribution(con: duckdb.DuckDBPyConnection, as_of: dt.date) -> dict | None:
    """Decompose the week-on-week change in the *base* risk budget into one
    additive contribution per module.

    `aggregate.py` computes base_risk_budget = Σ(wₘ·sₘ)/Σw over the modules that
    have data ("covered"). So per module, contribution = its weighted share this
    week minus its weighted share last week:

        cₘ = (wₘ,t / Wt)·sₘ,t − (wₘ,p / Wp)·sₘ,p

    Summed over the *union* of both weeks' modules that telescopes to exactly
    base_t − base_p, with no residual term — a module that appeared or dropped
    out shows up as its own bar rather than as unexplained slack. Attributing
    the scaled budget instead would not decompose: the regime scaler multiplies
    the whole blend, so it is reported as its own separate step.

    Returns None when the prior week's aggregate layer is absent (the aggregate
    tables only hold what a run or `ipos-replay` wrote), so a short history
    omits the section rather than inventing a baseline."""
    def _week(day: dt.date):
        row = con.execute(
            "SELECT params_json FROM agg_regime WHERE as_of_date = ?", [day]
        ).fetchone()
        if row is None or not row[0]:
            return None
        weights = (json.loads(row[0]) or {}).get("risk_budget_weights") or {}
        scores = dict(con.execute(
            "SELECT module_id, module_score FROM agg_module WHERE as_of_date = ?", [day]
        ).fetchall())
        total = sum(weights.values())
        if total <= 0 or not scores:
            return None
        return {m: (w / total) * scores[m] for m, w in weights.items() if m in scores}

    prev_day = as_of - dt.timedelta(weeks=1)
    now, prev = _week(as_of), _week(prev_day)
    if now is None or prev is None:
        return None

    contributions = [
        {"module": m, "contribution": _r(now.get(m, 0.0) - prev.get(m, 0.0))}
        for m in sorted(set(now) | set(prev))
    ]
    contributions.sort(key=lambda c: (-abs(c["contribution"]), c["module"]))
    return {
        "prev_as_of": prev_day.isoformat(),
        "base_from": _r(sum(prev.values())),
        "base_to": _r(sum(now.values())),
        "delta": _r(sum(now.values()) - sum(prev.values())),
        "contributions": contributions,
    }


def build_snapshot(con: duckdb.DuckDBPyConnection, registry: Registry, as_of: dt.date) -> dict:
    defaults = registry.defaults

    overall = con.execute(
        "SELECT risk_budget_0_100, confidence_0_100, regime_label, risk_scaler, "
        "regime_confidence, policy_json, params_json FROM agg_regime WHERE as_of_date = ?",
        [as_of],
    ).fetchone()
    if overall is None:
        raise ValueError(f"no aggregate row for {as_of}; run aggregate first")
    regime_policy = json.loads(overall[5]) if overall[5] else None
    regime_params = json.loads(overall[6]) if overall[6] else {}
    # regime_features mixes numbers with a string (`atr_source`), so round only
    # what is numeric instead of coercing everything.
    regime_features = {
        k: (_r(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v)
        for k, v in sorted((regime_params.get("regime_features") or {}).items())
    }

    modules = con.execute(
        "SELECT module_id, stance_dim, module_score, module_confidence, stance_value "
        "FROM agg_module WHERE as_of_date = ? ORDER BY module_id",
        [as_of],
    ).fetchall()

    stance_vector = {dim: _r(val) for _, dim, _, _, val in modules}

    # indicator block: value + deltas + trend + score + confidence + stale
    feats = con.execute(
        "SELECT series_id, feature_id, value FROM fact_feature WHERE as_of_date = ?",
        [as_of],
    ).fetchall()
    feat_map: dict[str, dict[str, float]] = {}
    for sid, fid, val in feats:
        feat_map.setdefault(sid, {})[fid] = val

    score_deltas = _score_deltas(con, as_of)

    # Weeks of canonical history per series. Exported because `pctile_156w` is a
    # rolling percentile with min_periods=1, so it returns a number even from a
    # handful of observations; the renderer needs to know when that number rests
    # on too little history to be worth drawing (HY_OAS/IG_OAS are permanently
    # capped at ~157 weeks by FRED truncation, while SPX/US10Y reach back to 1970).
    history_weeks = dict(con.execute(
        "SELECT series_id, count(*) FROM fact_weekly WHERE as_of_date <= ? GROUP BY series_id",
        [as_of],
    ).fetchall())

    indicators = []
    rows = con.execute(
        """
        SELECT s.series_id, d.module_id, w.value, s.score_0_100, s.confidence_0_100, s.stale
        FROM fact_score s
        JOIN dim_series d USING (series_id)
        JOIN fact_weekly w ON w.series_id = s.series_id AND w.as_of_date = s.as_of_date
        WHERE s.as_of_date = ? AND d.enabled
        ORDER BY s.series_id
        """,
        [as_of],
    ).fetchall()
    for sid, module_id, value, score, conf, stale in rows:
        f = feat_map.get(sid, {})
        indicators.append({
            "id": sid,
            "module": module_id,
            "value": _r(value),
            "delta_1w": _r(f.get("delta_1w")),
            "delta_4w": _r(f.get("delta_4w")),
            "delta_12w": _r(f.get("delta_12w")),
            "trend": _trend_word(f.get("trend")),
            "score": _r(score),
            "confidence": _r(conf),
            "stale": bool(stale),
            # Where the RAW LEVEL sits in its own rolling history. NOT the same
            # quantity as `score` and NOT direction-adjusted: for an inverted
            # indicator (higher_is_better=false, e.g. VIXCLS, HY_OAS) a high
            # percentile means a LOW score. Both are exported because they answer
            # different questions — "is this reading historically extreme?" vs.
            # "is this reading supportive?".
            "pctile_156w": _r(f.get("pctile_156w")),
            "z_104w": _r(f.get("z_104w")),
            "history_weeks": history_weeks.get(sid, 0),
            # change in the 0-100 score, comparable across indicators (unlike
            # the raw-value deltas above)
            "score_deltas": score_deltas.get(sid, {}),
        })

    # top movers: change in score vs previous week
    prev = as_of - dt.timedelta(weeks=1)
    prev_scores = dict(con.execute(
        "SELECT series_id, score_0_100 FROM fact_score WHERE as_of_date = ?", [prev]
    ).fetchall())
    movers = []
    for ind in indicators:
        p = prev_scores.get(ind["id"])
        if p is not None:
            movers.append({"id": ind["id"], "delta_score_1w": _r(ind["score"] - p)})
    movers.sort(key=lambda m: (-abs(m["delta_score_1w"]), m["id"]))
    top_movers = movers[:8]

    # contradictions (written by the engine into log_contradiction)
    recurrence, recurrence_window = _recurrence(con, as_of)
    contradictions = []
    for cid, sev, summary, details in con.execute(
        "SELECT contradiction_id, severity, summary, details_json "
        "FROM log_contradiction WHERE as_of_date = ? ORDER BY "
        "CASE severity WHEN 'high' THEN 0 WHEN 'med' THEN 1 ELSE 2 END, contradiction_id",
        [as_of],
    ).fetchall():
        contradictions.append({
            "id": cid, "severity": sev, "summary": summary,
            "details": json.loads(details) if details else {},
            # fired in N of the last `recurrence_window` observed weeks
            "weeks_fired": recurrence.get(cid, 1),
            "weeks_observed": recurrence_window,
        })

    # synthetic-data detection: THIS week's canonical values backed by a
    # synthetic vintage means THIS run used --seed-offline demo data. Must be
    # `=`, not `<=`: an earlier week's legitimate demo run must never taint
    # every later real week's flag forever (2026-07-26 regression).
    synthetic_data = con.execute(
        "SELECT count(*) FROM fact_weekly WHERE as_of_date = ? "
        "AND vintage_id LIKE 'synthetic@%'",
        [as_of],
    ).fetchone()[0] > 0

    # Breadth: how WIDELY spread the signal is, which a weighted average hides.
    # A risk budget of 50 built from eight indicators all sitting at 50 is a very
    # different week from one built from four at 90 and four at 10. Derived from
    # the indicator list already in memory — no new table, no scoring change.
    n_scored = len(indicators)
    n_improving = sum(
        1 for i in indicators
        if (i["score_deltas"].get("1w") or 0) > 0
    )
    n_with_delta = sum(1 for i in indicators if i["score_deltas"].get("1w") is not None)
    breadth = {
        "n_scored": n_scored,
        "n_above_50": sum(1 for i in indicators if (i["score"] or 0) > 50),
        "pct_above_50": _r(
            100.0 * sum(1 for i in indicators if (i["score"] or 0) > 50) / n_scored
        ) if n_scored else None,
        "n_improving": n_improving,
        "pct_improving": _r(100.0 * n_improving / n_with_delta) if n_with_delta else None,
    }

    stale_series = sorted(i["id"] for i in indicators if i["stale"])
    missing_series = sorted(
        e.series_id for e in registry.active()
        if e.series_id not in {i["id"] for i in indicators}
    )

    # Portfolio vs. Stance (05_blueprint/03_PORTFOLIO_MODULE.md): entirely
    # optional — omitted whenever no portfolio CSV has been dropped in
    # data/inbox/, never a hard dependency for the rest of the report.
    portfolio_block = None
    positions = load_positions()
    if positions is not None and not positions.empty:
        positions, fx_warnings = convert_to_eur(positions, con, as_of)
        mapping, unmapped_policy = load_mapping()
        portfolio_block = aggregate_portfolio(positions, mapping, unmapped_policy)
        if fx_warnings:
            portfolio_block["fx_warnings"] = fx_warnings
        freshness = portfolio_csv.portfolio_freshness(portfolio_csv.latest_portfolio_file(), as_of)
        if freshness is not None:
            portfolio_block["freshness"] = freshness

    snapshot = {
        "schema_version": SCHEMA_VERSION,
        "scoring_version": defaults.scoring_version,
        "as_of": as_of.isoformat(),
        "overall": {
            "risk_budget": _r(overall[0]),
            "confidence": _r(overall[1]),
            "stance_vector": stance_vector,
        },
        "regime": {
            "label": overall[2],
            "confidence": _r(overall[4]),
            "risk_scaler": _r(overall[3]),
            "policy_selectors": regime_policy,
            # The budget before the regime scaler multiplied it, so the report can
            # show base -> x scaler -> headline instead of one unexplained number.
            "base_risk_budget": _r(regime_params.get("base_risk_budget")),
            # The measurements the classifier actually decided on (overlap_index,
            # atr_change_rate, range_overlap, atr_source). Computed since WS-B and
            # never surfaced, which left "why is this week CHOPPY?" unanswerable.
            "features": regime_features,
        },
        "modules": [
            {
                "module": m[0],
                "score": _r(m[2]),
                "confidence": _r(m[3]),
                "tilt": _r(m[4]),
            }
            for m in modules
        ],
        "contradictions": contradictions,
        "events": events_for(as_of),
        "top_movers": top_movers,
        "indicators": indicators,
        "breadth": breadth,
        "data_quality": {
            "n_indicators": len(indicators),
            "n_stale": len(stale_series),
            "n_missing": len(missing_series),
            "stale_series": stale_series,
            "missing_series": missing_series,
        },
        "flags": {
            "degraded": len(missing_series) > 0 or len(stale_series) > 0,
            "has_contradictions": len(contradictions) > 0,
            "n_high_severity": sum(1 for c in contradictions if c["severity"] == "high"),
            "synthetic_data": synthetic_data,
        },
    }
    attribution = _budget_attribution(con, as_of)
    if attribution is not None:
        snapshot["budget_attribution"] = attribution
    if portfolio_block is not None:
        snapshot["portfolio"] = portfolio_block
    return snapshot


def write_snapshot(snapshot: dict, as_of: dt.date, base_dir: Path | None = None) -> dict:
    out_dir = (base_dir or EXPORTS_DIR) / as_of.isoformat()
    out_dir.mkdir(parents=True, exist_ok=True)
    pretty = out_dir / "snapshot.json"
    minified = out_dir / "snapshot.min.json"
    pretty.write_text(
        json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    minified.write_text(
        json.dumps(snapshot, separators=(",", ":"), sort_keys=True), encoding="utf-8"
    )
    return {"snapshot": str(pretty), "snapshot_min": str(minified)}


# --- validation -------------------------------------------------------------

SNAPSHOT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": [
        "schema_version", "scoring_version", "as_of", "overall", "modules",
        "contradictions", "top_movers", "indicators", "data_quality", "flags",
    ],
    "properties": {
        "schema_version": {"type": "string"},
        "scoring_version": {"type": "string"},
        "as_of": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
        "overall": {
            "type": "object",
            "required": ["risk_budget", "confidence", "stance_vector"],
            "properties": {
                "risk_budget": {"type": "number", "minimum": 0, "maximum": 100},
                "confidence": {"type": "number", "minimum": 0, "maximum": 100},
                "stance_vector": {
                    "type": "object",
                    "additionalProperties": {"type": "number", "minimum": -1, "maximum": 1},
                },
            },
        },
        "modules": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["module", "score", "confidence", "tilt"],
                "properties": {
                    "module": {"type": "string"},
                    "score": {"type": "number", "minimum": 0, "maximum": 100},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 100},
                    "tilt": {"type": "number", "minimum": -1, "maximum": 1},
                },
            },
        },
        "contradictions": {"type": "array"},
        "top_movers": {"type": "array"},
        "indicators": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "module", "value", "score", "confidence", "trend", "stale"],
                "properties": {
                    "score": {"type": "number", "minimum": 0, "maximum": 100},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 100},
                    "trend": {"enum": ["up", "down", "flat"]},
                    "stale": {"type": "boolean"},
                },
            },
        },
        "data_quality": {"type": "object"},
        "flags": {"type": "object"},
        "breadth": {
            "type": "object",
            "description": "How widely spread the signal is, which the weighted average hides.",
        },
        "budget_attribution": {
            "type": "object",
            "description": (
                "Optional — additive per-module decomposition of the week-on-week change "
                "in the BASE risk budget (pre-scaler). Omitted when the prior week's "
                "aggregate layer is absent. `contributions` sums to `delta` by construction."
            ),
            "required": ["prev_as_of", "base_from", "base_to", "delta", "contributions"],
            "properties": {
                "prev_as_of": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
                "delta": {"type": "number"},
                "contributions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["module", "contribution"],
                        "properties": {
                            "module": {"type": "string"},
                            "contribution": {"type": "number"},
                        },
                    },
                },
            },
        },
        "portfolio": {
            "type": "object",
            "description": "Optional — present only when a portfolio CSV was found in data/inbox/.",
            "required": ["modules", "unmapped", "total_value_eur"],
            "properties": {
                "modules": {"type": "object"},
                "unmapped": {"type": "array"},
                "total_value_eur": {"type": "number"},
                "freshness": {
                    "type": "object",
                    "properties": {
                        "age_days": {"type": "integer"},
                        "stale": {"type": "boolean"},
                    },
                },
            },
        },
    },
}


def validate(snapshot: dict) -> None:
    jsonschema.validate(snapshot, SNAPSHOT_SCHEMA)
