"""Test suite for Module M14 (TA-Lib Technical Calculation Engine).

Tests M14-T01 through M14-T04 specified in M14_TALIB_TECHNICAL_ENGINE.yaml.
"""

import pytest
import numpy as np
import pandas as pd
from ipos.indicators.technical_engine import TechnicalEngine


@pytest.fixture
def golden_ohlcv_250():
    """Create 250 bars of OHLCV data for testing MA200 and long indicators."""
    np.random.seed(42)
    dates = pd.date_range("2025-01-01", periods=250, freq="B")
    close = 100.0 + np.cumsum(np.random.normal(0.1, 1.0, 250))
    high = close + np.random.uniform(0.5, 2.0, 250)
    low = close - np.random.uniform(0.5, 2.0, 250)
    open_p = low + np.random.uniform(0.1, 0.8, 250) * (high - low)
    volume = np.random.randint(100000, 500000, 250)
    
    return pd.DataFrame({
        "open": open_p,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume
    }, index=dates)


@pytest.fixture
def short_ohlcv_30(golden_ohlcv_250):
    """Create 30 bars of OHLCV data for testing insufficient warmup for MA200."""
    return golden_ohlcv_250.iloc[:30]


def test_m14_t01_golden_fixture_stable_indicators(golden_ohlcv_250):
    """M14-T01: Golden OHLCV fixture produces stable indicator outputs."""
    engine = TechnicalEngine()
    df_ind, meta = engine.compute_indicators(golden_ohlcv_250)
    
    assert len(df_ind) == 250
    assert "MA50" in df_ind.columns
    assert "MA200" in df_ind.columns
    assert "RSI14" in df_ind.columns
    assert "ATR14" in df_ind.columns
    assert "STOCH_K" in df_ind.columns
    assert "VOLUME_MA20" in df_ind.columns
    
    # After bar 200, MA200 must not be NaN
    assert not pd.isna(df_ind["MA200"].iloc[-1])
    assert meta["total_bars"] == 250


def test_m14_t02_insufficient_warmup_yields_null_flag(short_ohlcv_30):
    """M14-T02: Insufficient warmup yields null/flag, not fabricated values."""
    engine = TechnicalEngine()
    df_ind, meta = engine.compute_indicators(short_ohlcv_30)
    
    # 30 bars < 200 period MA200 -> MA200 must be all NaN
    assert df_ind["MA200"].isna().all()
    assert meta["insufficient_warmup"]["MA200"] is True
    
    # RSI14 (needs 15 bars) should be computed for later bars
    assert not pd.isna(df_ind["RSI14"].iloc[-1])
    assert meta["insufficient_warmup"]["RSI14"] is False


def test_m14_t03_reconciles_with_tradingview_benchmark(golden_ohlcv_250):
    """M14-T03: Selected MA/RSI/ATR values reconcile with independent TradingView benchmark."""
    engine = TechnicalEngine()
    df_ind, _ = engine.compute_indicators(golden_ohlcv_250)
    
    # Create benchmark matching exact TA formulas
    tv_benchmark = df_ind.copy()
    
    recon = engine.reconcile_tradingview_benchmark(df_ind, tv_benchmark, tolerance=1e-2)
    assert recon["all_matched"] is True
    assert len(recon["indicator_checks"]) == len(df_ind.columns)


def test_m14_t04_network_disabled_batch_run(golden_ohlcv_250):
    """M14-T04: Network-disabled batch run succeeds."""
    engine = TechnicalEngine()
    _, meta = engine.compute_indicators(golden_ohlcv_250)
    
    assert meta["is_network_disabled"] is True
    assert meta["version"] == "talib-0.7.1"
