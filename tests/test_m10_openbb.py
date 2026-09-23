"""Test suite for Module M10 (OpenBB ODP Data Layer).

Tests M10-T01 through M10-T05 specified in M10_OPENBB_ODP.yaml.
"""

import pytest
import pandas as pd
from ipos.data.openbb_adapter import OpenBBAdapter


def test_m10_t01_clean_environment_imports_openbb():
    """M10-T01: Clean environment imports OpenBB and completes build."""
    from openbb import obb
    assert obb is not None
    # Check that core routers exist
    assert hasattr(obb, "equity")
    assert hasattr(obb, "economy")


def test_m10_t02_representative_free_series_retrieve():
    """M10-T02: Representative free series retrieve reproducibly."""
    adapter = OpenBBAdapter()
    
    # Equity series (SPY)
    df_spy = adapter.fetch_equity_historical("SPY", provider="yfinance")
    assert not df_spy.empty
    assert "close" in df_spy.columns
    
    # FRED Fed balance sheet (WALCL)
    df_walcl = adapter.fetch_fred_series("WALCL")
    assert not df_walcl.empty
    assert "WALCL" in df_walcl.columns
    
    # FRED 10Y-2Y yield spread (T10Y2Y)
    df_t10y2y = adapter.fetch_fred_series("T10Y2Y")
    assert not df_t10y2y.empty
    assert "T10Y2Y" in df_t10y2y.columns
    
    # FRED HY OAS (BAMLH0A0HYM2)
    df_hy = adapter.fetch_fred_series("BAMLH0A0HYM2")
    assert not df_hy.empty
    assert "BAMLH0A0HYM2" in df_hy.columns


def test_m10_t03_three_point_spot_checks_match_upstream():
    """M10-T03: Three-point spot checks match upstream provider within expected transformations."""
    adapter = OpenBBAdapter()
    
    # Spot check FRED series WALCL
    df_walcl_adapter = adapter.fetch_fred_series("WALCL")
    df_walcl_direct = pd.read_csv("https://fred.stlouisfed.org/graph/fredgraph.csv?id=WALCL")
    df_walcl_direct["date"] = pd.to_datetime(df_walcl_direct["observation_date"])
    df_walcl_direct = df_walcl_direct.set_index("date").drop(columns=["observation_date"])
    df_walcl_direct["WALCL"] = pd.to_numeric(df_walcl_direct["WALCL"], errors="coerce")
    
    recent_dates = [str(d.date()) for d in df_walcl_adapter.index[-3:]]
    recon = adapter.reconcile_spot_check(df_walcl_adapter, df_walcl_direct, recent_dates, "WALCL")
    assert recon["all_matched"] is True, f"Reconciliation failed: {recon}"


def test_m10_t04_missing_credential_fails_explicitly():
    """M10-T04: Missing credential/provider outage fails explicitly rather than fabricating data."""
    adapter = OpenBBAdapter(fred_api_key=None)
    
    # Calling fetch_fred_series with require_official_credential=True and no API key must fail explicitly
    with pytest.raises(Exception) as exc_info:
        adapter.fetch_fred_series("WALCL", require_official_credential=True)
    
    err_msg = str(exc_info.value)
    assert "Missing credential" in err_msg or "fred_api_key" in err_msg or "OpenBBError" in type(exc_info.value).__name__


def test_m10_t05_no_openbb_workspace_required():
    """M10-T05: No OpenBB Workspace subscription is required."""
    adapter = OpenBBAdapter()
    meta_spy = adapter.get_series_metadata("SPY", "yfinance")
    meta_fred = adapter.get_series_metadata("WALCL", "fred")
    
    assert meta_spy["openbb_workspace_required"] is False
    assert meta_fred["openbb_workspace_required"] is False
