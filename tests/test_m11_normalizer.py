"""Test suite for Module M11 (Deterministic Portfolio Normalizer).

Tests M11-T01 through M11-T06 specified in M11_PORTFOLIO_NORMALIZER.yaml.
"""

import pytest
import hashlib
import os
import tempfile
import pandas as pd
from ipos.portfolio.normalizer import PortfolioNormalizer, ValidationException


@pytest.fixture
def golden_fixture_path():
    return os.path.join(os.path.dirname(__file__), "fixtures", "golden_broker_export.csv")


@pytest.fixture
def corrupt_fixture_path():
    return os.path.join(os.path.dirname(__file__), "fixtures", "corrupt_broker_export.csv")


def test_m11_t01_golden_csv_fixture_mapping(golden_fixture_path):
    """M11-T01: Golden CSV fixture maps exactly to expected canonical rows."""
    normalizer = PortfolioNormalizer()
    df_holdings, df_activities, manifest, reconciliation = normalizer.normalize_csv_fixture(golden_fixture_path)
    
    assert len(df_activities) == 4
    assert set(df_activities["type"]) == {"BUY", "SELL", "DIVIDEND"}
    assert manifest["total_source_rows"] == 4
    assert manifest["normalized_activities_count"] == 4


def test_m11_t02_text_fixture_preserves_values(golden_fixture_path):
    """M11-T02: Text/CSV fixture extraction preserves expected transaction values."""
    normalizer = PortfolioNormalizer()
    _, df_activities, _, _ = normalizer.normalize_csv_fixture(golden_fixture_path)
    
    spy_buy = df_activities[df_activities["instrument_id"] == "US7846721097"].iloc[0]
    assert spy_buy["quantity"] == 10.0
    assert spy_buy["price"] == 500.0
    assert spy_buy["gross"] == 5000.0
    assert spy_buy["fees"] == 5.0


def test_m11_t03_dividends_fees_currency_mapping(golden_fixture_path):
    """M11-T03: Dividends, fees, and currency attributes map cleanly."""
    normalizer = PortfolioNormalizer()
    _, df_activities, _, _ = normalizer.normalize_csv_fixture(golden_fixture_path)
    
    div_act = df_activities[df_activities["type"] == "DIVIDEND"].iloc[0]
    assert div_act["gross"] == 15.0
    assert div_act["taxes"] == 2.25
    assert div_act["currency"] == "EUR"


def test_m11_t04_reproducibility_determinism(golden_fixture_path):
    """M11-T04: Same fixture run twice yields identical canonical outputs and hashes."""
    normalizer = PortfolioNormalizer()
    
    with tempfile.TemporaryDirectory() as tmp1, tempfile.TemporaryDirectory() as tmp2:
        df_h1, df_a1, _, _ = normalizer.normalize_csv_fixture(golden_fixture_path)
        df_h2, df_a2, _, _ = normalizer.normalize_csv_fixture(golden_fixture_path)
        
        path1 = os.path.join(tmp1, "act.csv")
        path2 = os.path.join(tmp2, "act.csv")
        df_a1.to_csv(path1, index=False)
        df_a2.to_csv(path2, index=False)
        
        hash1 = hashlib.sha256(open(path1, "rb").read()).hexdigest()
        hash2 = hashlib.sha256(open(path2, "rb").read()).hexdigest()
        assert hash1 == hash2


def test_m11_t05_corrupt_row_causes_validation_failure(corrupt_fixture_path):
    """M11-T05: Corrupt/ambiguous source row causes validation failure, not silent drop."""
    normalizer = PortfolioNormalizer()
    with pytest.raises(ValidationException):
        normalizer.normalize_csv_fixture(corrupt_fixture_path)


def test_m11_t06_reconciliation_zero_difference(golden_fixture_path):
    """M11-T06: Reconciliation difference is zero or explicitly explained."""
    normalizer = PortfolioNormalizer()
    _, _, _, reconciliation = normalizer.normalize_csv_fixture(golden_fixture_path)
    
    assert reconciliation["reconciliation_difference"] == 0.0
    assert reconciliation["reconciliation_status"] == "BALANCED"
