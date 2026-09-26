"""Test suite for Portfolio Performance Ingestion Adapter (E03) & Coherent Accounting (E04)."""

import io
from pathlib import Path
import pytest
import pandas as pd

from ipos.portfolio.pp_adapter import PortfolioPerformanceAdapter
from ipos.portfolio.accounting import PortfolioLedger
from ipos.etl.portfolio_csv import _load_single_positions_file


# Sample German PP Buchungen export
GERMAN_BUCHUNGEN_SAMPLE = """Datum;Typ;Wert;Buchungswährung;Bruttobetrag;Währung Bruttobetrag;Wechselkurs;Gebühren;Steuern;Stück;ISIN;WKN;Ticker-Symbol;Wertpapiername;Notiz
2026-01-10;Einlage;10.000,00;EUR;10.000,00;EUR;1,00;0,00;0,00;;;;;Barkonto;Einzahlung
2026-01-15;Kauf;2.500,00;EUR;2.490,00;EUR;1,00;10,00;0,00;50;US0378331005;865985;AAPL;Apple Inc.;Order 101
2026-02-01;Kauf;1.200,00;EUR;1.195,00;EUR;1,00;5,00;0,00;20;US0378331005;865985;AAPL;Apple Inc.;Order 102
2026-02-15;Dividende;75,00;EUR;100,00;EUR;1,00;0,00;25,00;;US0378331005;865985;AAPL;Apple Inc.;Quartalsdividende
2026-03-01;Verkauf;1.800,00;EUR;1.810,00;EUR;1,00;10,00;0,00;30;US0378331005;865985;AAPL;Apple Inc.;Gewinnmitnahme
2026-03-05;Gebühren;15,00;EUR;15,00;EUR;1,00;0,00;0,00;;;;;Depotführung;Q1 Gebuehr
"""

# Sample English PP Transactions export
ENGLISH_TRANSACTIONS_SAMPLE = """Date,Type,Value,Transaction Currency,Gross Amount,Currency Gross Amount,Exchange Rate,Fees,Taxes,Shares,ISIN,WKN,Ticker Symbol,Security Name,Note
2026-01-10,Deposit,5000.00,USD,5000.00,USD,1.00,0.00,0.00,,,,Cash Account,Initial Deposit
2026-01-20,Buy,3000.00,USD,2990.00,USD,1.00,10.00,0.00,100,US70450Y1038,,PYPL,PayPal Holdings,Market Order
2026-02-10,Sell,1600.00,USD,1605.00,USD,1.00,5.00,0.00,50,US70450Y1038,,PYPL,PayPal Holdings,Partial Sale
"""

# Sample German PP Vermögensaufstellung export
GERMAN_VERMOEGEN_SAMPLE = """Wertpapiername;ISIN;WKN;Ticker-Symbol;Aktueller Kurs;Aktueller Wert;Einstandskurs;Einstandswert;Performance;Gewinn / Verlust;Dividenden;Anzahl;Anteil in %;Notiz
Apple Inc.;US0378331005;865985;AAPL;185,50;7.420,00;150,00;6.000,00;23,67 %;1.420,00;75,00;40;65,50 %;Core holding
Microsoft Corp.;US5949181045;870747;MSFT;410,00;3.910,00;380,00;3.623,00;7,92 %;287,00;0,00;9,5366;34,50 %;Tech bet
"""


def test_01_german_buchungen_parsing():
    """Test 1: Parsing German-locale Portfolio Performance Buchungen.csv."""
    adapter = PortfolioPerformanceAdapter(default_account="TEST_PP")
    df_acts = adapter.parse_buchungen(io.StringIO(GERMAN_BUCHUNGEN_SAMPLE))

    assert len(df_acts) == 6
    assert list(df_acts["type"]) == ["DEPOSIT", "BUY", "BUY", "DIVIDEND", "SELL", "FEE"]
    assert df_acts.iloc[0]["gross"] == 10000.0
    assert df_acts.iloc[0]["currency"] == "EUR"

    # Buy 1: 50 shares Apple, gross=2490.0, fees=10.0
    assert df_acts.iloc[1]["instrument_id"] == "US0378331005"
    assert df_acts.iloc[1]["quantity"] == 50.0
    assert df_acts.iloc[1]["fees"] == 10.0
    assert df_acts.iloc[1]["gross"] == 2490.0

    # Dividend: 100.0 gross, 25.0 tax
    assert df_acts.iloc[3]["type"] == "DIVIDEND"
    assert df_acts.iloc[3]["gross"] == 100.0
    assert df_acts.iloc[3]["taxes"] == 25.0

    # Standalone Fee: 15.0 gross
    assert df_acts.iloc[5]["type"] == "FEE"
    assert df_acts.iloc[5]["gross"] == 15.0


def test_02_english_transactions_parsing():
    """Test 2: Parsing English-locale Portfolio Performance Transactions.csv."""
    adapter = PortfolioPerformanceAdapter(default_account="TEST_PP_EN")
    df_acts = adapter.parse_buchungen(io.StringIO(ENGLISH_TRANSACTIONS_SAMPLE))

    assert len(df_acts) == 3
    assert list(df_acts["type"]) == ["DEPOSIT", "BUY", "SELL"]
    assert df_acts.iloc[0]["gross"] == 5000.0
    assert df_acts.iloc[0]["currency"] == "USD"

    # Buy: 100 shares PayPal
    assert df_acts.iloc[1]["instrument_id"] == "US70450Y1038"
    assert df_acts.iloc[1]["quantity"] == 100.0
    assert df_acts.iloc[1]["fees"] == 10.0


def test_03_german_holdings_parsing():
    """Test 3: Parsing German PP Vermögensaufstellung / Holdings export."""
    adapter = PortfolioPerformanceAdapter(default_account="TEST_PP_HOLDINGS")
    df_holdings = adapter.parse_holdings(io.StringIO(GERMAN_VERMOEGEN_SAMPLE), as_of="2026-09-25")

    assert len(df_holdings) == 2
    assert df_holdings.iloc[0]["instrument_id"] == "US0378331005"
    assert df_holdings.iloc[0]["quantity"] == 40.0
    assert df_holdings.iloc[0]["market_value"] == 7420.0
    assert df_holdings.iloc[0]["weighted_average_cost_basis"] == 150.0

    assert df_holdings.iloc[1]["instrument_id"] == "US5949181045"
    assert df_holdings.iloc[1]["market_value"] == 3910.0

    # Convert to IPOS positions DataFrame
    df_ipos = adapter.to_ipos_positions(df_holdings)
    assert len(df_ipos) == 2
    assert "instrument" in df_ipos.columns
    assert "value_eur" in df_ipos.columns
    assert df_ipos.iloc[0]["value_eur"] == 7420.0


def test_04_accounting_ledger_multi_currency_and_cost_basis():
    """Test 4: Replaying activities through PortfolioLedger with exact cash & cost basis tracking."""
    adapter = PortfolioPerformanceAdapter(default_account="PP_ACCOUNT")
    df_acts = adapter.parse_buchungen(io.StringIO(GERMAN_BUCHUNGEN_SAMPLE))

    ledger = PortfolioLedger(account_name="PP_ACCOUNT")
    ledger.replay_activities(df_acts)

    assert ledger.processed_activities_count == 6

    # Apple Position:
    # Buy 1: 50 shares @ 2490 + 10 fees = 2500 total cost (cost basis = 50.00/share)
    # Buy 2: 20 shares @ 1195 + 5 fees = 1200 total cost
    # Combined before sale: 70 shares, 3700 total cost -> cost basis = 3700 / 70 = 52.85714/share
    # Sale: 30 shares sold. Gross 1810 - 10 fee = 1800 net proceeds.
    # Basis of sold portion = 30 * (3700 / 70) = 1585.714
    # Realized gain = 1800 - 1585.714 = 214.2857
    # Remaining: 40 shares, total cost = 40 * (3700 / 70) = 2114.2857, basis = 52.85714
    open_positions = ledger.get_open_positions()
    assert "US0378331005" in open_positions
    pos = open_positions["US0378331005"]
    assert pos.quantity == 40.0
    assert pos.weighted_average_cost_basis == pytest.approx(52.8571, rel=1e-3)
    assert pos.realized_pnl == pytest.approx(214.2857, rel=1e-3)

    # Cash Calculation (EUR):
    # + 10,000 (Deposit)
    # - 2,500 (Buy 1 outlay: 2490 + 10)
    # - 1,200 (Buy 2 outlay: 1195 + 5)
    # + 75 (Net Dividend: 100 gross - 25 tax)
    # + 1,800 (Net Sale Proceeds: 1810 - 10)
    # - 15 (Fee)
    # Expected Cash = 10,000 - 2,500 - 1,200 + 75 + 1,800 - 15 = 8,160.00 EUR
    assert ledger.cash_balances["EUR"] == pytest.approx(8160.0, rel=1e-3)


def test_05_reconciliation_report():
    """Test 5: Ledger reconciliation report against control figures."""
    adapter = PortfolioPerformanceAdapter()
    df_acts = adapter.parse_buchungen(io.StringIO(GERMAN_BUCHUNGEN_SAMPLE))
    ledger = PortfolioLedger()
    ledger.replay_activities(df_acts)

    # Reconcile against matching control figures
    control_cash = {"EUR": 8160.0}
    control_holdings = {"US0378331005": 40.0}
    rep_match = ledger.reconciliation_report(control_cash, control_holdings)
    assert rep_match["reconciliation_status"] == "MATCH"
    assert rep_match["cash_balances"]["EUR"]["variance"] == 0.0

    # Reconcile against mismatched control figures
    control_discrepancy = {"US0378331005": 50.0}  # Broker says 50, ledger has 40
    rep_disc = ledger.reconciliation_report(control_cash, control_discrepancy)
    assert rep_disc["reconciliation_status"] == "DISCREPANCY_DETECTED"
    assert "US0378331005" in rep_disc["holdings_discrepancies"]
    assert rep_disc["holdings_discrepancies"]["US0378331005"]["variance"] == -10.0


def test_06_inbox_auto_detection_of_pp_exports(tmp_path: Path):
    """Test 6: load_positions auto-detects Portfolio Performance CSV exports."""
    # 1. Test Vermögensaufstellung CSV
    pp_holdings_file = tmp_path / "Vermögensaufstellung_2026.csv"
    pp_holdings_file.write_text(GERMAN_VERMOEGEN_SAMPLE, encoding="utf-8")

    df_loaded = _load_single_positions_file(pp_holdings_file)
    assert len(df_loaded) == 2
    assert "US0378331005" in list(df_loaded["instrument"])
    assert df_loaded.loc[df_loaded["instrument"] == "US0378331005", "value_eur"].iloc[0] == 7420.0

    # 2. Test Buchungen CSV
    pp_buchungen_file = tmp_path / "Buchungen_2026.csv"
    pp_buchungen_file.write_text(GERMAN_BUCHUNGEN_SAMPLE, encoding="utf-8")

    df_from_acts = _load_single_positions_file(pp_buchungen_file)
    assert len(df_from_acts) == 1
    assert df_from_acts.iloc[0]["instrument"] == "US0378331005"
    assert df_from_acts.iloc[0]["quantity"] == 40.0


def test_07_real_smartbroker_activities_reconciliation():
    """Test 7: Replay real operator Smartbroker transactions export (332 confirmed rows)."""
    p = Path(r"C:\Users\gehma\Downloads\3370191001-2026-09-24T09-02-24.190Z.csv")
    if not p.exists():
        pytest.skip("Local Smartbroker export not present")

    adapter = PortfolioPerformanceAdapter(default_account="SMARTBROKER")
    df_acts = adapter.parse_smartbroker_activities(p)
    assert len(df_acts) == 332
    assert set(df_acts["type"]) == {"BUY", "SELL", "TRANSFER_IN", "TRANSFER_OUT"}

    ledger = PortfolioLedger(account_name="SMARTBROKER")
    ledger.replay_activities(df_acts)
    open_pos = ledger.get_open_positions()

    # Replaying all 332 confirmed activities in true chronological sequence
    # resolves exactly 24 open positions, matching the official broker PDF control.
    # It correctly preserves NDA (1,000) and PSYC (10,000) that Wealthfolio failed to reconstruct.
    assert len(open_pos) == 24
    assert "US88023B1035" in open_pos  # Tempus AI
    assert open_pos["US88023B1035"].quantity == 150.0
    assert "CA64073L1013" in open_pos  # Neptune Digital Assets (NDA)
    assert open_pos["CA64073L1013"].quantity == 1000.0
    assert "CA74447P1009" in open_pos  # Psyched Wellness (PSYC)
    assert open_pos["CA74447P1009"].quantity == 10000.0
    assert "DE000SH7NDN5" in open_pos  # Copper Turbo
    assert open_pos["DE000SH7NDN5"].quantity == 216.0

    # Verify positions with intraday trades have exact quantities matching the control
    assert open_pos["DE000MK6QKZ0"].quantity == 5.0
    assert open_pos["DE000MA5E683"].quantity == 1.0
    assert open_pos["DE000MN4NFQ8"].quantity == 800.0
    assert open_pos["DE000DN042H8"].quantity == 1.0
    assert open_pos["US49639K1016"].quantity == 10.0
    assert open_pos["DE000HM4PTX8"].quantity == 22.0

    # Verify fully sold out positions are not present in open positions
    for closed_isin in ["JE00BDD9Q840", "DE000MJ796Z6", "DE000FA5VTY7", "DE000MG2Z7N3", "DE000FD5E2J5", "DE000PH5KQZ4"]:
        assert closed_isin not in open_pos

    # If the control PDF exists, assert 100% MATCH reconciliation
    pdf_path = Path("data/inbox/3370191001-2026-09-25T15-15-35.459Z.pdf")
    if not pdf_path.exists():
        pdf_path = Path(r"C:\Users\gehma\Downloads\3370191001-2026-09-25T15-15-35.459Z.pdf")
    if pdf_path.exists():
        from ipos.etl.portfolio_csv import _parse_smartbroker_pdf
        df_pdf = _parse_smartbroker_pdf(pdf_path)
        pdf_dict = dict(zip(df_pdf["instrument"], df_pdf["quantity"]))
        report = ledger.reconciliation_report(external_holdings_control=pdf_dict)
        assert report["reconciliation_status"] == "MATCH"
        assert len(report["holdings_discrepancies"]) == 0

