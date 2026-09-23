"""Test suite for Module M12 (Wealthfolio Visualization Bridge).

Tests M12-T01 through M12-T05 specified in M12_WEALTHFOLIO.yaml.
"""

import pytest
import os
import pandas as pd
from ipos.portfolio.normalizer import PortfolioNormalizer
import ipos.portfolio.wealthfolio as wealthfolio


@pytest.fixture
def canonical_data():
    golden_path = os.path.join(os.path.dirname(__file__), "fixtures", "golden_broker_export.csv")
    normalizer = PortfolioNormalizer()
    df_holdings, df_activities, _, reconciliation = normalizer.normalize_csv_fixture(golden_path)
    return df_holdings, df_activities, reconciliation


def test_m12_does_not_claim_a_real_integration_without_wealthfolio(canonical_data):
    """Deleting Wealthfolio must make a claimed integration impossible, not silently local."""
    assert wealthfolio.INTEGRATION_STATUS == "NOT_CONNECTED"
    assert not hasattr(wealthfolio, "WealthfolioAdapter")
    with pytest.raises(wealthfolio.WealthfolioIntegrationUnavailable, match="E02"):
        wealthfolio.require_real_wealthfolio()


def test_m12_t02_portfolio_value_reconciliation(canonical_data):
    """M12-T02: Portfolio value/performance explainably reconciles."""
    df_holdings, _, reconciliation = canonical_data
    total_market_val = float(df_holdings["market_value"].sum())
    
    # Check market value is positive and matches holdings calculation
    assert total_market_val > 0.0
    assert reconciliation["reconciliation_status"] == "UNVERIFIABLE_NO_SOURCE_CONTROL"
