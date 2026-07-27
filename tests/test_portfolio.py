"""Portfolio vs. Stance module tests (05_blueprint/03_PORTFOLIO_MODULE.md):
CSV parsing, module aggregation, and the fail-degraded "no file -> section
omitted" contract. No network."""

from __future__ import annotations

import pandas as pd
import pytest

from ipos.aggregate.portfolio import (
    aggregate_portfolio,
    load_mapping,
    portfolio_vs_stance,
    stance_alignment,
)
from ipos.etl import portfolio_csv
from ipos.export.snapshot import build_snapshot
from ipos.warehouse.db import connect


# --- etl.portfolio_csv ------------------------------------------------------

def test_load_positions_none_when_no_inbox_file(tmp_path):
    assert portfolio_csv.latest_portfolio_file(tmp_path) is None


def test_load_positions_reads_value_eur_directly(tmp_path):
    p = tmp_path / "portfolio.csv"
    p.write_text("instrument,quantity,value_eur\nIE00B4L5Y983,120,18500.00\n", encoding="utf-8")
    df = portfolio_csv.load_positions(p)
    assert list(df.columns) == ["instrument", "quantity", "value_eur"]
    assert df.iloc[0]["value_eur"] == 18500.00


def test_load_positions_computes_value_from_price(tmp_path):
    p = tmp_path / "portfolio.csv"
    p.write_text("instrument,quantity,price_eur\nDE000A1EWWW0,10,50.0\n", encoding="utf-8")
    df = portfolio_csv.load_positions(p)
    assert df.iloc[0]["value_eur"] == 500.0


def test_load_positions_missing_required_column_raises(tmp_path):
    p = tmp_path / "portfolio.csv"
    p.write_text("instrument,value_eur\nX,100\n", encoding="utf-8")
    with pytest.raises(RuntimeError):
        portfolio_csv.load_positions(p)


def test_load_positions_no_value_or_price_raises(tmp_path):
    p = tmp_path / "portfolio.csv"
    p.write_text("instrument,quantity\nX,10\n", encoding="utf-8")
    with pytest.raises(RuntimeError):
        portfolio_csv.load_positions(p)


def test_latest_portfolio_file_picks_latest(tmp_path):
    (tmp_path / "portfolio_2026-07-01.csv").write_text("instrument,quantity,value_eur\nA,1,1\n")
    (tmp_path / "portfolio_2026-07-08.csv").write_text("instrument,quantity,value_eur\nB,1,2\n")
    latest = portfolio_csv.latest_portfolio_file(tmp_path)
    assert latest.name == "portfolio_2026-07-08.csv"


# --- aggregate.portfolio -----------------------------------------------------

def _positions():
    return pd.DataFrame({
        "instrument": ["EQ_ETF", "GOLD_ETC", "UNKNOWN"],
        "quantity": [100, 50, 10],
        "value_eur": [6200.0, 930.0, 200.0],
    })


def test_aggregate_portfolio_known_weights():
    mapping = {"EQ_ETF": "EquityRisk", "GOLD_ETC": "Commodities"}
    out = aggregate_portfolio(_positions(), mapping, "warn")
    assert out["total_value_eur"] == 7330.0
    assert out["modules"]["EquityRisk"]["value_eur"] == 6200.0
    assert out["modules"]["EquityRisk"]["weight_pct"] == pytest.approx(84.5771, rel=1e-3)
    assert out["modules"]["Commodities"]["weight_pct"] == pytest.approx(12.6876, rel=1e-3)
    assert out["unmapped"] == [{"instrument": "UNKNOWN", "value_eur": 200.0}]


def test_aggregate_portfolio_unmapped_ignore_hides_but_still_counts():
    mapping = {"EQ_ETF": "EquityRisk", "GOLD_ETC": "Commodities"}
    out = aggregate_portfolio(_positions(), mapping, "ignore")
    assert out["unmapped"] == []
    assert out["total_value_eur"] == 7330.0  # unknown's value still in the total


def test_aggregate_portfolio_unmapped_error_raises():
    mapping = {"EQ_ETF": "EquityRisk", "GOLD_ETC": "Commodities"}
    with pytest.raises(ValueError):
        aggregate_portfolio(_positions(), mapping, "error")


def test_load_mapping_missing_file_degrades_to_empty(tmp_path):
    mapping, policy = load_mapping(tmp_path / "does_not_exist.yaml")
    assert mapping == {}
    assert policy == "warn"


def test_load_mapping_reads_yaml(tmp_path):
    p = tmp_path / "portfolio_mapping.yaml"
    p.write_text("mappings:\n  EQ_ETF: EquityRisk\nunmapped_policy: ignore\n", encoding="utf-8")
    mapping, policy = load_mapping(p)
    assert mapping == {"EQ_ETF": "EquityRisk"}
    assert policy == "ignore"


def test_load_mapping_rejects_bad_policy(tmp_path):
    p = tmp_path / "portfolio_mapping.yaml"
    p.write_text("mappings: {}\nunmapped_policy: delete_everything\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_mapping(p)


# --- stance_alignment / portfolio_vs_stance ---------------------------------

def test_stance_alignment_examples_from_the_plan():
    # "Equity: you're 62% weighted; system suggests +0.60 tilt -> aligned"
    assert stance_alignment(62.0, 0.60) == "aligned"
    # "Commodities: you're 0% weighted; system suggests +0.93 -> not participating"
    assert stance_alignment(0.0, 0.93) == "not participating in a signal the system currently likes"


def test_stance_alignment_headwind_cases():
    assert stance_alignment(30.0, -0.5) == "exposed to a headwind the system currently flags"
    assert stance_alignment(0.0, -0.5) == "aligned (out of a signal the system currently dislikes)"
    assert stance_alignment(50.0, 0.05) == "aligned"  # near-neutral tilt


def test_portfolio_vs_stance_none_when_no_portfolio_block():
    assert portfolio_vs_stance({"modules": []}) is None


def test_portfolio_vs_stance_pairs_weight_with_tilt():
    snap = {
        "modules": [
            {"module": "EquityRisk", "score": 70, "confidence": 80, "tilt": 0.4},
            {"module": "Commodities", "score": 90, "confidence": 80, "tilt": 0.93},
        ],
        "portfolio": {
            "modules": {"EquityRisk": {"weight_pct": 62.0, "value_eur": 6200.0}},
            "unmapped": [],
            "total_value_eur": 10000.0,
        },
    }
    rows = portfolio_vs_stance(snap)
    by_module = {r["module"]: r for r in rows}
    assert by_module["EquityRisk"]["weight_pct"] == 62.0
    assert by_module["EquityRisk"]["read"] == "aligned"
    assert by_module["Commodities"]["weight_pct"] == 0.0
    assert by_module["Commodities"]["read"] == "not participating in a signal the system currently likes"


# --- integration: build_snapshot picks up an inbox file, and omits the
#     section entirely when absent --------------------------------------------

def test_snapshot_omits_portfolio_when_no_inbox_file(populated_db, as_of, monkeypatch, tmp_path):
    monkeypatch.setattr(portfolio_csv, "INBOX", tmp_path)  # empty dir, no portfolio*.csv
    db, reg = populated_db
    with connect(db, read_only=True) as con:
        snap = build_snapshot(con, reg, as_of)
    assert "portfolio" not in snap


def test_snapshot_includes_portfolio_when_inbox_file_present(populated_db, as_of, monkeypatch, tmp_path):
    import ipos.aggregate.portfolio as portfolio_agg

    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "portfolio.csv").write_text(
        "instrument,quantity,value_eur\nEQ_ETF,100,6200.00\nGOLD_ETC,50,930.00\n",
        encoding="utf-8",
    )
    mapping_path = tmp_path / "portfolio_mapping.yaml"
    mapping_path.write_text(
        "mappings:\n  EQ_ETF: EquityRisk\n  GOLD_ETC: Commodities\nunmapped_policy: warn\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(portfolio_csv, "INBOX", inbox)
    monkeypatch.setattr(portfolio_agg, "MAPPING_PATH", mapping_path)

    db, reg = populated_db
    with connect(db, read_only=True) as con:
        snap = build_snapshot(con, reg, as_of)

    assert "portfolio" in snap
    assert snap["portfolio"]["modules"]["EquityRisk"]["value_eur"] == 6200.0
    assert snap["portfolio"]["total_value_eur"] == 7130.0
    rows = portfolio_vs_stance(snap)
    assert any(r["module"] == "EquityRisk" for r in rows)
