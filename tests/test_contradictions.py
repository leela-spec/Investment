"""Contradictions engine tests (C4 decision 5): the seed predicates compile,
predicates fire on constructed score fixtures, the safe evaluator rejects
unsafe expressions, and results are deterministic."""

from __future__ import annotations

import datetime as dt

import pytest

from ipos.aggregate.contradictions import (
    ContradictionConfigError,
    _build_context,
    _compile,
    _eval,
    evaluate,
    load_predicates,
)
from ipos.warehouse.db import connect, init_db
from ipos.config.load import load_registry

AS_OF = dt.date(2026, 7, 17)


def test_seed_predicates_compile():
    preds = load_predicates()
    assert len(preds) >= 8
    assert {p.severity for p in preds} <= {"low", "med", "high"}


# --- safe evaluator ---------------------------------------------------------

def test_evaluator_basic_logic():
    funcs = {"module": lambda k: {"A": 80.0, "B": 30.0}[k], "abs": abs,
             "min": min, "max": max}
    assert _eval(_compile("module('A') >= 70 and module('B') <= 40"), funcs) is True
    assert _eval(_compile("module('A') <= 70"), funcs) is False


def test_evaluator_rejects_unsafe():
    # attribute access, imports, arbitrary calls must be refused at compile time
    for bad in [
        "__import__('os').system('ls')",
        "module.__class__",
        "open('x')",
        "1 + 2",            # arithmetic BinOp not in whitelist
    ]:
        with pytest.raises(ContradictionConfigError):
            _compile(bad)


def test_missing_data_does_not_fire():
    # a comparison against a None (e.g. regime() in Phase 1) is False, not a crash
    funcs = {"regime": lambda: None, "module": lambda k: 50.0,
             "abs": abs, "min": min, "max": max}
    assert _eval(_compile("regime() == 'CHOPPY'"), funcs) is False


# --- engine over constructed DB fixtures ------------------------------------

def _seed_scores(db, module_scores, indicator_scores=None):
    """Write minimal agg_module + fact_score rows so the engine has a context."""
    reg = load_registry()
    init_db(reg, db)
    with connect(db) as con:
        for mid, score in module_scores.items():
            con.execute(
                "INSERT OR REPLACE INTO agg_module (as_of_date, module_id, stance_dim, "
                "module_score, module_confidence, stance_value) VALUES (?,?,?,?,?,?)",
                [AS_OF, mid, mid.lower(), score, 80.0, (score - 50) / 50],
            )
        for sid, score in (indicator_scores or {}).items():
            con.execute(
                "INSERT OR REPLACE INTO fact_score (series_id, as_of_date, score_0_100, "
                "scoring_method, confidence_0_100) VALUES (?,?,?,?,?)",
                [sid, AS_OF, score, "percentile", 80.0],
            )


def test_eq_vs_credit_fires_high(tmp_path):
    db = tmp_path / "w.duckdb"
    _seed_scores(db, {"EquityRisk": 75.0, "Credit": 35.0})
    with connect(db) as con:
        hits = evaluate(con, AS_OF)
    ids = {h["id"] for h in hits}
    assert "EQ_vs_CREDIT" in ids
    hit = next(h for h in hits if h["id"] == "EQ_vs_CREDIT")
    assert hit["severity"] == "high"
    # triggering values captured
    assert hit["details"]["module(EquityRisk)"] == pytest.approx(75.0)
    assert hit["details"]["module(Credit)"] == pytest.approx(35.0)


def test_no_contradiction_when_aligned(tmp_path):
    db = tmp_path / "w.duckdb"
    # everything mid/high and coherent -> no macro contradiction
    _seed_scores(db, {
        "EquityRisk": 60.0, "Credit": 58.0, "RatesLiquidity": 55.0,
        "GrowthRisk": 60.0, "Commodities": 50.0, "Liquidity": 55.0,
        "Fundamentals": 52.0, "FX": 50.0,
    })
    with connect(db) as con:
        hits = evaluate(con, AS_OF)
    assert all(h["id"] not in {"EQ_vs_CREDIT", "EQ_vs_RATES", "EQ_vs_GROWTH"} for h in hits)


def test_engine_deterministic_and_ordered(tmp_path):
    db = tmp_path / "w.duckdb"
    _seed_scores(db, {"EquityRisk": 80.0, "Credit": 30.0, "RatesLiquidity": 30.0,
                      "GrowthRisk": 25.0, "Commodities": 65.0, "Liquidity": 50.0,
                      "Fundamentals": 25.0, "FX": 50.0})
    with connect(db) as con:
        first = evaluate(con, AS_OF)
    with connect(db) as con:
        second = evaluate(con, AS_OF)
    assert [h["id"] for h in first] == [h["id"] for h in second]
    # high severity sorts first
    severities = [h["severity"] for h in first]
    rank = {"high": 0, "med": 1, "low": 2}
    assert severities == sorted(severities, key=lambda s: rank[s])
