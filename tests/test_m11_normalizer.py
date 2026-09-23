"""Test suite for Module M11 / Correction C11 (Deterministic Portfolio Normalizer).

Tests M11-T01 through M11-T12 against physically independent oracle fixtures.
"""

import pytest
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import pandas as pd
from ipos.portfolio.normalizer import PortfolioNormalizer, ValidationException


@pytest.fixture
def fixtures_dir():
    return os.path.join(os.path.dirname(__file__), "fixtures")


@pytest.fixture
def golden_fixture_path(fixtures_dir):
    return os.path.join(fixtures_dir, "golden_broker_export.csv")


@pytest.fixture
def golden_expected_path(fixtures_dir):
    return os.path.join(fixtures_dir, "golden_broker_expected.json")


@pytest.fixture
def corrupt_fixture_path(fixtures_dir):
    return os.path.join(fixtures_dir, "corrupt_broker_export.csv")


@pytest.fixture
def invalid_arithmetic_fixture_path(fixtures_dir):
    return os.path.join(fixtures_dir, "invalid_arithmetic_broker_export.csv")


@pytest.fixture
def mismatch_control_path(fixtures_dir):
    return os.path.join(fixtures_dir, "mismatch_control_expected.json")


@pytest.fixture
def multi_currency_fixture_path(fixtures_dir):
    return os.path.join(fixtures_dir, "multi_currency_broker_export.csv")


@pytest.fixture
def multi_currency_expected_path(fixtures_dir):
    return os.path.join(fixtures_dir, "multi_currency_broker_expected.json")


@pytest.fixture
def component_mismatch_path(fixtures_dir):
    return os.path.join(fixtures_dir, "component_mismatch_control_expected.json")


@pytest.fixture
def holding_mismatch_path(fixtures_dir):
    return os.path.join(fixtures_dir, "holding_mismatch_control_expected.json")


def test_m11_t01_golden_csv_fixture_mapping_vs_independent_oracle(golden_fixture_path, golden_expected_path):
    """M11-T01: Golden CSV fixture maps exactly to expected canonical rows matching independent JSON oracle."""
    with open(golden_expected_path, "r", encoding="utf-8-sig") as f:
        expected = json.load(f)

    normalizer = PortfolioNormalizer()
    df_holdings, df_activities, manifest, reconciliation = normalizer.normalize_csv_fixture(
        golden_fixture_path, control_input=golden_expected_path
    )

    assert len(df_activities) == expected["total_activities"]
    assert set(df_activities["type"]) == {"BUY", "SELL", "DIVIDEND"}
    assert manifest["total_source_rows"] == 4
    assert manifest["normalized_activities_count"] == 4

    # Reconciliation status must be BALANCED against independent oracle
    assert reconciliation["reconciliation_status"] == "BALANCED"
    assert reconciliation["reconciliation_difference"] == 0.0
    eur_totals = reconciliation["summary_totals_by_currency"]["EUR"]
    assert eur_totals["net_cash_flow"] == expected["summary_totals_by_currency"]["EUR"]["net_cash_flow"]


def test_m11_t02_text_fixture_preserves_values_and_cash_flow(golden_fixture_path, golden_expected_path):
    """M11-T02: Preserves transaction values and correctly derives directional net cash flow."""
    with open(golden_expected_path, "r", encoding="utf-8-sig") as f:
        expected = json.load(f)

    normalizer = PortfolioNormalizer()
    _, df_activities, _, reconciliation = normalizer.normalize_csv_fixture(golden_fixture_path, control_input=golden_expected_path)

    spy_buy = df_activities[df_activities["instrument_id"] == "US7846721097"].iloc[0]
    assert spy_buy["quantity"] == 10.0
    assert spy_buy["price"] == 500.0
    assert spy_buy["gross"] == 5000.0
    assert spy_buy["fees"] == 5.0

    totals = reconciliation["summary_totals_by_currency"]["EUR"]
    exp_eur = expected["summary_totals_by_currency"]["EUR"]
    assert totals["gross_buys"] == exp_eur["gross_buys"]
    assert totals["gross_sells"] == exp_eur["gross_sells"]
    assert totals["gross_dividends"] == exp_eur["gross_dividends"]
    assert totals["total_fees"] == exp_eur["total_fees"]
    assert totals["total_taxes"] == exp_eur["total_taxes"]
    assert totals["net_cash_flow"] == exp_eur["net_cash_flow"]


def test_m11_t03_standalone_fee_tax_semantics(tmp_path):
    """M11-T03: Non-overlapping standalone FEE and TAX rows are mapped and validated cleanly."""
    csv_content = (
        "source_row_id,timestamp,type,isin,symbol,name,quantity,price,gross,fees,taxes,currency\n"
        "501,2026-04-01T10:00:00Z,FEE,,CASH_FEE,Custody Fee,0,0.0,25.0,0.0,0.0,EUR\n"
        "502,2026-04-01T10:05:00Z,TAX,,CASH_TAX,Withholding Adjustment,0,0.0,10.0,0.0,0.0,EUR\n"
    )
    p = tmp_path / "standalone_fee_tax.csv"
    p.write_text(csv_content, encoding="utf-8")

    normalizer = PortfolioNormalizer()
    _, df_act, _, rec = normalizer.normalize_csv_fixture(str(p))

    assert len(df_act) == 2
    eur_totals = rec["summary_totals_by_currency"]["EUR"]
    assert eur_totals["total_fees"] == 25.0
    assert eur_totals["total_taxes"] == 10.0
    assert eur_totals["net_cash_flow"] == -35.0

    # Overlapping ambiguous configuration must be rejected
    bad_fee_content = (
        "source_row_id,timestamp,type,isin,symbol,name,quantity,price,gross,fees,taxes,currency\n"
        "503,2026-04-01T10:00:00Z,FEE,,CASH_FEE,Custody Fee,0,0.0,25.0,5.0,0.0,EUR\n"
    )
    p_bad = tmp_path / "bad_fee.csv"
    p_bad.write_text(bad_fee_content, encoding="utf-8")
    with pytest.raises(ValidationException, match="double-counting"):
        normalizer.normalize_csv_fixture(str(p_bad))


def test_m11_t04_reproducibility_determinism(golden_fixture_path):
    """M11-T04: Same fixture run twice yields identical canonical outputs and SHA-256 hashes."""
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


def test_m11_t05_row_arithmetic_invalid_causes_validation_exception(invalid_arithmetic_fixture_path, corrupt_fixture_path):
    """M11-T05: Negative test Case A - ROW_ARITHMETIC_INVALID raises ValidationException."""
    normalizer = PortfolioNormalizer()

    # Corrupt gross arithmetic (gross != qty * price)
    with pytest.raises(ValidationException, match="Row arithmetic error"):
        normalizer.normalize_csv_fixture(invalid_arithmetic_fixture_path)

    # Corrupt schema / types
    with pytest.raises(ValidationException):
        normalizer.normalize_csv_fixture(corrupt_fixture_path)


def test_m11_t06_source_control_mismatch_fails_reconciliation(golden_fixture_path, mismatch_control_path):
    """M11-T06: Negative test Case B - Valid rows with mismatched control yields MISMATCH."""
    normalizer = PortfolioNormalizer()
    _, _, _, reconciliation = normalizer.normalize_csv_fixture(golden_fixture_path, control_input=mismatch_control_path)

    assert reconciliation["reconciliation_status"] == "MISMATCH"
    assert reconciliation["reconciliation_difference"] == 520.25
    assert reconciliation["summary_totals_by_currency"]["EUR"]["net_cash_flow"] == -5520.25


def test_m11_t07_unverifiable_without_source_control(golden_fixture_path):
    """M11-T07: Normalization without control refuses to report BALANCED."""
    normalizer = PortfolioNormalizer()
    _, _, _, reconciliation = normalizer.normalize_csv_fixture(golden_fixture_path, control_input=None)

    assert reconciliation["reconciliation_status"] == "UNVERIFIABLE_NO_SOURCE_CONTROL"
    assert reconciliation["reconciliation_difference"] is None


def test_m11_t08_economic_book_cost_basis_relief_on_sales(golden_fixture_path, golden_expected_path):
    """M11-T08: Weighted average cost basis is relieved proportionally on sales."""
    with open(golden_expected_path, "r", encoding="utf-8-sig") as f:
        expected = json.load(f)

    normalizer = PortfolioNormalizer()
    df_holdings, _, _, _ = normalizer.normalize_csv_fixture(golden_fixture_path)

    aapl_holding = df_holdings[df_holdings["instrument_id"] == "US0378331005"].iloc[0]
    expected_aapl = expected["ending_holdings"]["US0378331005"]

    assert aapl_holding["quantity"] == expected_aapl["quantity"]
    assert round(aapl_holding["cost_basis"], 2) == expected_aapl["book_cost_basis"]
    assert round(aapl_holding["market_value"], 2) == expected_aapl["market_value"]

    spy_holding = df_holdings[df_holdings["instrument_id"] == "US7846721097"].iloc[0]
    expected_spy = expected["ending_holdings"]["US7846721097"]
    assert spy_holding["quantity"] == expected_spy["quantity"]
    assert round(spy_holding["cost_basis"], 2) == expected_spy["book_cost_basis"]


def test_m11_t09_valuation_timestamp_semantics(golden_fixture_path, golden_expected_path):
    """M11-T09: Holding as_of is NOT advanced on DIVIDEND when market value has not been revalued."""
    with open(golden_expected_path, "r", encoding="utf-8-sig") as f:
        expected = json.load(f)

    normalizer = PortfolioNormalizer()
    df_holdings, _, _, _ = normalizer.normalize_csv_fixture(golden_fixture_path)

    spy_holding = df_holdings[df_holdings["instrument_id"] == "US7846721097"].iloc[0]
    # SPY was bought on 2026-01-15. Dividend was received on 2026-03-01.
    # as_of must remain 2026-01-15T10:00:00Z (timestamp of valuation price 500.0)
    assert spy_holding["as_of"] == "2026-01-15T10:00:00Z"
    assert spy_holding["as_of"] == expected["ending_holdings"]["US7846721097"]["as_of"]

    # AAPL was sold on 2026-03-10 @ 190.0, so its valuation timestamp updated
    aapl_holding = df_holdings[df_holdings["instrument_id"] == "US0378331005"].iloc[0]
    assert aapl_holding["as_of"] == "2026-03-10T11:00:00Z"


def test_m11_t10_multi_currency_accounting(multi_currency_fixture_path, multi_currency_expected_path):
    """M11-T10: Multi-currency accounting aggregates per currency and never sums across EUR and USD."""
    with open(multi_currency_expected_path, "r", encoding="utf-8-sig") as f:
        expected = json.load(f)

    normalizer = PortfolioNormalizer()
    _, df_act, _, rec = normalizer.normalize_csv_fixture(multi_currency_fixture_path, control_input=multi_currency_expected_path)

    assert len(df_act) == 2
    assert "EUR" in rec["summary_totals_by_currency"]
    assert "USD" in rec["summary_totals_by_currency"]

    eur = rec["summary_totals_by_currency"]["EUR"]
    usd = rec["summary_totals_by_currency"]["USD"]

    assert eur["gross_buys"] == 600.00
    assert eur["net_cash_flow"] == -602.00
    assert usd["gross_buys"] == 5000.00
    assert usd["net_cash_flow"] == -5005.00

    # Ensure reconciliation passed per-currency check
    assert rec["reconciliation_status"] == "BALANCED"


def test_m11_t11_full_control_oracle_component_and_holding_mismatch(golden_fixture_path, component_mismatch_path, holding_mismatch_path):
    """M11-T11: Net cash flow matching alone is insufficient; component or holding discrepancy yields MISMATCH."""
    normalizer = PortfolioNormalizer()

    # 1. Component mismatch (net cash correct, but fees wrong)
    _, _, _, rec_comp = normalizer.normalize_csv_fixture(golden_fixture_path, control_input=component_mismatch_path)
    assert rec_comp["reconciliation_status"] == "MISMATCH"
    assert any(c["check"] == "summary_totals.EUR.total_fees" and c["status"] == "FAIL" for c in rec_comp["checks"])

    # 2. Ending holding quantity mismatch
    _, _, _, rec_hold = normalizer.normalize_csv_fixture(golden_fixture_path, control_input=holding_mismatch_path)
    assert rec_hold["reconciliation_status"] == "MISMATCH"
    assert any(c["check"] == "holding.US0378331005.quantity" and c["status"] == "FAIL" for c in rec_hold["checks"])


def test_m11_t12_cli_exit_code_semantics(golden_fixture_path, golden_expected_path, mismatch_control_path, tmp_path):
    """M11-T12: CLI exit codes conform to 0=BALANCED, 1=MISMATCH, 2=UNVERIFIABLE."""
    cli_py = os.path.join(os.path.dirname(__file__), "..", "ipos", "portfolio", "cli.py")

    # A. reconcile with BALANCED control -> exit code 0
    p_bal = subprocess.run([sys.executable, cli_py, "reconcile", "--input", golden_fixture_path, "--control", golden_expected_path], capture_output=True, text=True)
    assert p_bal.returncode == 0

    # B. reconcile with MISMATCH control -> exit code 1
    p_mis = subprocess.run([sys.executable, cli_py, "reconcile", "--input", golden_fixture_path, "--control", mismatch_control_path], capture_output=True, text=True)
    assert p_mis.returncode == 1

    # C. reconcile without control -> exit code 2
    p_unv = subprocess.run([sys.executable, cli_py, "reconcile", "--input", golden_fixture_path], capture_output=True, text=True)
    assert p_unv.returncode == 2

    # D. normalize without control -> exit code 0 (with explicit notice)
    out_dir = tmp_path / "out"
    p_norm_unv = subprocess.run([sys.executable, cli_py, "normalize", "--input", golden_fixture_path, "--outdir", str(out_dir)], capture_output=True, text=True)
    assert p_norm_unv.returncode == 0
    assert "UNVERIFIABLE" in p_norm_unv.stdout
