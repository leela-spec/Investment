"""Portfolio vs. Stance module tests (05_blueprint/03_PORTFOLIO_MODULE.md):
CSV parsing, module aggregation, and the fail-degraded "no file -> section
omitted" contract. No network."""

from __future__ import annotations

import datetime as dt
import os

import pandas as pd
import pytest

from ipos.aggregate.portfolio import (
    aggregate_portfolio,
    convert_to_eur,
    load_mapping,
    persist_portfolio_weights,
    portfolio_vs_stance,
    stance_alignment,
)
from ipos.config.load import load_registry
from ipos.etl import portfolio_csv
from ipos.etl.fixtures import SEED_ANCHOR
from ipos.export.snapshot import build_snapshot
from ipos.run import run_weekly
from ipos.warehouse.db import connect, init_db


# --- etl.portfolio_csv ------------------------------------------------------

def test_load_positions_none_when_no_inbox_file(tmp_path):
    assert portfolio_csv.latest_portfolio_file(tmp_path) is None


def test_load_positions_reads_value_eur_directly(tmp_path):
    p = tmp_path / "portfolio.csv"
    p.write_text("instrument,quantity,value_eur\nIE00B4L5Y983,120,18500.00\n", encoding="utf-8")
    df = portfolio_csv.load_positions(p)
    assert list(df.columns) == ["instrument", "quantity", "value_eur", "currency"]
    assert df.iloc[0]["value_eur"] == 18500.00
    assert df.iloc[0]["currency"] == "EUR"


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


# --- real-world German broker export (finanzen.net Zero shape, confirmed
#     against a real export 2026-07-27): semicolon delimiter, ISIN/Anzahl/
#     Wert columns, decimal-comma/thousands-dot numbers -----------------------

def test_load_positions_parses_german_semicolon_export(tmp_path):
    p = tmp_path / "portfolio.csv"
    p.write_text(
        "Name;ISIN;WKN;Art;Anzahl;Verfügbar;Kaufkurs;Kaufwert;Kurs;Kurszeit;"
        "Kursdatum;Wert;Erfolg [%];Erfolg [EUR];Notiz\n"
        "IREN LTD.;AU0000185993;A3C7R6;AKTIE;205;205;48,75;9.993,75;52,12;"
        "10:58:32;09.06.2026;10.684,60;6,91;690,85;\n"
        "SOFI TECHNOLOGIES;US83406F1021;A2QPMG;AKTIE;1.000;1.000;13,816;"
        "13.816,00;14,386;10:58:18;09.06.2026;14.386,00;4,13;570;\n",
        encoding="utf-8",
    )
    df = portfolio_csv.load_positions(p)
    assert list(df["instrument"]) == ["AU0000185993", "US83406F1021"]
    assert df.iloc[0]["quantity"] == pytest.approx(205)
    assert df.iloc[0]["value_eur"] == pytest.approx(10684.60)
    assert df.iloc[1]["quantity"] == pytest.approx(1000)  # "1.000" -> 1000, not 1.0
    assert df.iloc[1]["value_eur"] == pytest.approx(14386.00)
    assert list(df["currency"]) == ["EUR", "EUR"]  # no currency column -> default


# --- currency (05_blueprint/03_PORTFOLIO_MODULE.md §8 follow-up 3) ----------

def test_load_positions_defaults_currency_to_eur_when_absent(tmp_path):
    p = tmp_path / "portfolio.csv"
    p.write_text("instrument,quantity,value_eur\nX,10,100.0\n", encoding="utf-8")
    df = portfolio_csv.load_positions(p)
    assert df["currency"].unique().tolist() == ["EUR"]


def test_load_positions_reads_currency_column(tmp_path):
    p = tmp_path / "portfolio.csv"
    p.write_text("instrument,quantity,value_eur,currency\nX,10,100.0,usd\n", encoding="utf-8")
    df = portfolio_csv.load_positions(p)
    assert df.iloc[0]["currency"] == "USD"


def test_convert_to_eur_leaves_eur_positions_unchanged(populated_db, as_of):
    db, _ = populated_db
    positions = pd.DataFrame({
        "instrument": ["X"], "quantity": [1], "value_eur": [100.0], "currency": ["EUR"],
    })
    with connect(db, read_only=True) as con:
        converted, warnings = convert_to_eur(positions, con, as_of)
    assert converted.iloc[0]["value_eur"] == 100.0
    assert warnings == []


def test_convert_to_eur_converts_usd_using_latest_eurusd_rate(populated_db, as_of):
    db, _ = populated_db
    positions = pd.DataFrame({
        "instrument": ["X"], "quantity": [1], "value_eur": [1000.0], "currency": ["USD"],
    })
    with connect(db, read_only=True) as con:
        rate = con.execute(
            "SELECT value FROM fact_weekly WHERE series_id = 'EURUSD' AND as_of_date <= ? "
            "ORDER BY as_of_date DESC LIMIT 1",
            [as_of],
        ).fetchone()[0]
        converted, warnings = convert_to_eur(positions, con, as_of)
    assert converted.iloc[0]["value_eur"] == pytest.approx(1000.0 / rate)
    assert warnings == []


def test_convert_to_eur_warns_and_skips_unsupported_currency(populated_db, as_of):
    db, _ = populated_db
    positions = pd.DataFrame({
        "instrument": ["X"], "quantity": [1], "value_eur": [100.0], "currency": ["GBP"],
    })
    with connect(db, read_only=True) as con:
        converted, warnings = convert_to_eur(positions, con, as_of)
    assert converted.iloc[0]["value_eur"] == 100.0
    assert warnings == [{
        "currency": "GBP", "n_positions": 1,
        "reason": "no FX rate available; left unconverted",
    }]


def test_convert_to_eur_no_rate_available_warns_and_skips(tmp_path):
    reg = load_registry()
    db = tmp_path / "w.duckdb"
    init_db(reg, db)
    positions = pd.DataFrame({
        "instrument": ["X"], "quantity": [1], "value_eur": [100.0], "currency": ["USD"],
    })
    with connect(db) as con:
        converted, warnings = convert_to_eur(positions, con, dt.date(2026, 7, 17))
    assert converted.iloc[0]["value_eur"] == 100.0
    assert warnings[0]["currency"] == "USD"


# --- persist_portfolio_weights (feeds the contradictions engine; see
#     tests/test_contradictions.py for portfolio_weight()/tilt() predicates) -

def test_persist_portfolio_weights_writes_zero_for_unheld_modules(populated_db, as_of):
    db, _ = populated_db
    portfolio = {"modules": {"EquityRisk": {"weight_pct": 40.0, "value_eur": 4000.0}}}
    with connect(db) as con:
        n = persist_portfolio_weights(con, as_of, portfolio)
        rows = dict(con.execute(
            "SELECT module_id, weight_pct FROM fact_portfolio_weight WHERE as_of_date = ?",
            [as_of],
        ).fetchall())
    assert rows["EquityRisk"] == 40.0
    assert any(mid != "EquityRisk" and w == 0.0 for mid, w in rows.items())
    assert n == len(rows)


def test_persist_portfolio_weights_none_clears_and_returns_zero(populated_db, as_of):
    db, _ = populated_db
    with connect(db) as con:
        persist_portfolio_weights(con, as_of, {"modules": {"EquityRisk": {"weight_pct": 40.0, "value_eur": 1.0}}})
        n = persist_portfolio_weights(con, as_of, None)
        count = con.execute(
            "SELECT count(*) FROM fact_portfolio_weight WHERE as_of_date = ?", [as_of]
        ).fetchone()[0]
    assert n == 0
    assert count == 0


# --- run_log "portfolio" stage (05_blueprint/03_PORTFOLIO_MODULE.md §8
#     follow-up 4) ------------------------------------------------------------

def test_portfolio_stage_logged_when_no_csv(tmp_path, monkeypatch):
    import ipos.export.report as report_mod
    import ipos.export.snapshot as snap_mod

    monkeypatch.setattr(snap_mod, "EXPORTS_DIR", tmp_path / "exports")
    monkeypatch.setattr(report_mod, "EXPORTS_DIR", tmp_path / "exports")
    monkeypatch.setattr(portfolio_csv, "INBOX", tmp_path)  # empty dir, no portfolio*.csv

    reg = load_registry()
    db = tmp_path / "w.duckdb"
    run_weekly(as_of=SEED_ANCHOR, db_path=db, registry=reg, seed_offline=True,
               ingested_at=dt.datetime(2026, 7, 18, 8, 0, 0))
    with connect(db, read_only=True) as con:
        row = con.execute(
            "SELECT status, rows_out, detail FROM run_log WHERE stage = 'portfolio' AND as_of_date = ?",
            [SEED_ANCHOR],
        ).fetchone()
    assert row is not None
    status, rows_out, detail = row
    assert status == "OK"
    assert rows_out == 0
    assert "no portfolio CSV found" in detail


def test_portfolio_stage_logged_when_csv_present(tmp_path, monkeypatch):
    import ipos.aggregate.portfolio as portfolio_agg
    import ipos.export.report as report_mod
    import ipos.export.snapshot as snap_mod

    monkeypatch.setattr(snap_mod, "EXPORTS_DIR", tmp_path / "exports")
    monkeypatch.setattr(report_mod, "EXPORTS_DIR", tmp_path / "exports")

    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "portfolio.csv").write_text(
        "instrument,quantity,value_eur\nEQ_ETF,100,6200.00\n", encoding="utf-8",
    )
    mapping_path = tmp_path / "portfolio_mapping.yaml"
    mapping_path.write_text("mappings:\n  EQ_ETF: EquityRisk\nunmapped_policy: warn\n", encoding="utf-8")
    monkeypatch.setattr(portfolio_csv, "INBOX", inbox)
    monkeypatch.setattr(portfolio_agg, "MAPPING_PATH", mapping_path)

    reg = load_registry()
    db = tmp_path / "w.duckdb"
    run_weekly(as_of=SEED_ANCHOR, db_path=db, registry=reg, seed_offline=True,
               ingested_at=dt.datetime(2026, 7, 18, 8, 0, 0))
    with connect(db, read_only=True) as con:
        row = con.execute(
            "SELECT status, rows_out, detail FROM run_log WHERE stage = 'portfolio' AND as_of_date = ?",
            [SEED_ANCHOR],
        ).fetchone()
    assert row is not None
    status, rows_out, detail = row
    assert status == "OK"
    assert rows_out > 0
    assert "modules=1" in detail


# --- stale/aging portfolio CSV flag (05_blueprint/03_PORTFOLIO_MODULE.md §8
#     follow-up 5) ------------------------------------------------------------

def test_portfolio_freshness_none_without_file(as_of):
    assert portfolio_csv.portfolio_freshness(None, as_of) is None


def test_portfolio_freshness_fresh_file_not_flagged(tmp_path, as_of):
    p = tmp_path / "portfolio.csv"
    p.write_text("instrument,quantity,value_eur\nX,1,1\n", encoding="utf-8")
    now = dt.datetime.combine(as_of, dt.time()).timestamp()
    os.utime(p, (now, now))
    freshness = portfolio_csv.portfolio_freshness(p, as_of)
    assert freshness == {"age_days": 0, "stale": False}


def test_portfolio_freshness_flags_stale_file(tmp_path, as_of):
    p = tmp_path / "portfolio.csv"
    p.write_text("instrument,quantity,value_eur\nX,1,1\n", encoding="utf-8")
    old = dt.datetime.combine(as_of - dt.timedelta(days=30), dt.time()).timestamp()
    os.utime(p, (old, old))
    freshness = portfolio_csv.portfolio_freshness(p, as_of)
    assert freshness == {"age_days": 30, "stale": True}


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
    csv_path = inbox / "portfolio.csv"
    csv_path.write_text(
        "instrument,quantity,value_eur\nEQ_ETF,100,6200.00\nGOLD_ETC,50,930.00\n",
        encoding="utf-8",
    )
    now = dt.datetime.combine(as_of, dt.time()).timestamp()
    os.utime(csv_path, (now, now))  # just-dropped file -> never stale
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
    assert snap["portfolio"]["freshness"] == {"age_days": 0, "stale": False}
    rows = portfolio_vs_stance(snap)
    assert any(r["module"] == "EquityRisk" for r in rows)
