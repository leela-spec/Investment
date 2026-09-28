from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import pytest
import yaml

from ipos.etl.portfolio_csv import _parse_smartbroker_pdf, load_positions
from ipos.portfolio.accounting import PortfolioLedger
from ipos.portfolio.pp_adapter import PortfolioPerformanceAdapter


MANIFEST = Path("configs/fixture_acceptance.yaml")


def portfolio_fixture(fixture_id: str) -> Path:
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    fixture = next(item for item in manifest["portfolios"] if item["id"] == fixture_id)
    if fixture_id == "smartbroker-activities":
        return Path(os.environ.get("IPOS_SMARTBROKER_ACTIVITIES", fixture["evidence_file"]))
    return Path(fixture["evidence_file"])


def test_real_broker_fixtures_reconcile_and_consolidate():
    activities_path = portfolio_fixture("smartbroker-activities")
    statement_path = portfolio_fixture("smartbroker-statement")
    zero_path = portfolio_fixture("zero-positions")
    assert activities_path.is_file(), f"missing required fixture: {activities_path}"

    activities = PortfolioPerformanceAdapter(
        default_account="SMARTBROKER"
    ).parse_smartbroker_activities(activities_path)
    assert len(activities) == 332

    ledger = PortfolioLedger(account_name="SMARTBROKER")
    ledger.replay_activities(activities)
    ledger_positions = ledger.get_open_positions()
    assert len(ledger_positions) == 24
    assert ledger_positions["CA64073L1013"].quantity == 1000.0
    assert ledger_positions["CA74447P1009"].quantity == 10000.0

    statement = _parse_smartbroker_pdf(statement_path)
    report = ledger.reconciliation_report(
        external_holdings_control=dict(zip(statement.instrument, statement.quantity))
    )
    assert report["reconciliation_status"] == "MATCH"
    assert report["holdings_discrepancies"] == {}

    zero = load_positions(path=zero_path)
    assert zero is not None
    assert len(zero) == 8
    consolidated = pd.concat([statement, zero], ignore_index=True)
    assert len(consolidated) == 32


def test_market_values_are_controls_not_ledger_cost_basis():
    activities = PortfolioPerformanceAdapter(
        default_account="SMARTBROKER"
    ).parse_smartbroker_activities(portfolio_fixture("smartbroker-activities"))
    ledger = PortfolioLedger(account_name="SMARTBROKER")
    ledger.replay_activities(activities)
    statement = _parse_smartbroker_pdf(portfolio_fixture("smartbroker-statement"))
    zero = load_positions(path=portfolio_fixture("zero-positions"))

    assert statement["value_eur"].sum() == pytest.approx(36411.09, abs=0.01)
    assert zero is not None
    assert zero["value_eur"].sum() == pytest.approx(3837.21, abs=0.01)
    ledger_cost_value = ledger.to_ipos_positions()["value_eur"].sum()
    assert ledger_cost_value == pytest.approx(41508.65, abs=0.01)
    assert ledger_cost_value != pytest.approx(statement["value_eur"].sum(), abs=0.01)
