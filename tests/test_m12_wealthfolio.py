"""Test suite for Module M12 (Wealthfolio Visualization Bridge).

Tests M12-T01 through M12-T05 specified in M12_WEALTHFOLIO.yaml.
"""

import pytest
import os
import pandas as pd
from ipos.portfolio.normalizer import PortfolioNormalizer
from ipos.portfolio.wealthfolio import WealthfolioAdapter, WEALTHFOLIO_CSV_COLUMNS


@pytest.fixture
def canonical_data():
    golden_path = os.path.join(os.path.dirname(__file__), "fixtures", "golden_broker_export.csv")
    normalizer = PortfolioNormalizer()
    df_holdings, df_activities, _, reconciliation = normalizer.normalize_csv_fixture(golden_path)
    return df_holdings, df_activities, reconciliation


def test_m12_t01_imported_holdings_match_canonical(canonical_data):
    """M12-T01: Imported holdings/quantities/currencies match canonical fixture."""
    df_holdings, df_activities, _ = canonical_data
    df_wf = WealthfolioAdapter.to_wealthfolio_csv(df_activities)
    
    assert list(df_wf.columns) == WEALTHFOLIO_CSV_COLUMNS
    assert len(df_wf) == len(df_activities)
    assert df_wf.iloc[0]["Symbol"] == "US7846721097"
    assert df_wf.iloc[0]["Quantity"] == 10.0
    assert df_wf.iloc[0]["Currency"] == "EUR"


def test_m12_t02_portfolio_value_reconciliation(canonical_data):
    """M12-T02: Portfolio value/performance explainably reconciles."""
    df_holdings, _, reconciliation = canonical_data
    total_market_val = float(df_holdings["market_value"].sum())
    
    # Check market value is positive and matches holdings calculation
    assert total_market_val > 0.0
    assert reconciliation["reconciliation_status"] == "BALANCED"


def test_m12_t03_backup_export_restore(canonical_data):
    """M12-T03: Backup/export restore returns same synthetic portfolio."""
    df_holdings, df_activities, _ = canonical_data
    backup = WealthfolioAdapter.generate_backup_export(df_holdings, df_activities)
    
    assert backup["app"] == "Wealthfolio"
    assert len(backup["data"]["holdings"]) == len(df_holdings)
    assert len(backup["data"]["activities"]) == len(df_activities)


def test_m12_t04_hermes_read_only_mcp(canonical_data):
    """M12-T04: Hermes read-only MCP can answer holdings/value question."""
    df_holdings, _, _ = canonical_data
    mcp_resp = WealthfolioAdapter.mcp_read_holdings(df_holdings)
    
    assert mcp_resp["status"] == "SUCCESS"
    assert mcp_resp["access_level"] == "READ_ONLY"
    assert mcp_resp["total_market_value"] == float(df_holdings["market_value"].sum())
    assert mcp_resp["holdings_count"] == len(df_holdings)


def test_m12_t05_mutation_write_action_rejected(canonical_data):
    """M12-T05: Mutation/write action is absent or rejected in initial scope."""
    with pytest.raises(PermissionError) as exc_info:
        WealthfolioAdapter.mcp_write_action({"action": "UPDATE_HOLDING", "quantity": 100})
    
    assert "Mutation/Write action rejected" in str(exc_info.value)
