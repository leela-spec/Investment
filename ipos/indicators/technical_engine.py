"""IPOS Local Technical Computation Engine (Module M14).

Provides reproducible local technical calculation over OHLCV series using TA-Lib
with explicit warmup period validation, period conventions, and TradingView reconciliation.
"""

from typing import Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
import talib


INDICATOR_REGISTRY = {
    "MA50": {"func": "SMA", "timeperiod": 50, "field": "close"},
    "MA200": {"func": "SMA", "timeperiod": 200, "field": "close"},
    "RSI14": {"func": "RSI", "timeperiod": 14, "field": "close"},
    "ATR14": {"func": "ATR", "timeperiod": 14, "field": "high_low_close"},
    "STOCH_K": {"func": "STOCH", "field": "high_low_close", "fastk_period": 14, "slowk_period": 3, "slowd_period": 3},
    "VOLUME_MA20": {"func": "SMA", "timeperiod": 20, "field": "volume"}
}


class TechnicalEngine:
    """TA-Lib Local Technical Calculation Engine for IPOS."""

    def __init__(self, registry: Optional[Dict[str, Any]] = None):
        self.registry = registry or INDICATOR_REGISTRY

    def compute_indicators(
        self, df_ohlcv: pd.DataFrame, timeframe: str = "daily"
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Compute TA-Lib indicators over OHLCV dataframe.
        
        Args:
            df_ohlcv: DataFrame containing 'open', 'high', 'low', 'close', 'volume'
            timeframe: 'daily' or 'weekly'
            
        Returns:
            Tuple of (DataFrame with indicator columns, metadata Dict)
        """
        required_cols = ["open", "high", "low", "close", "volume"]
        for col in required_cols:
            if col not in df_ohlcv.columns:
                # Case-insensitive column search
                lower_cols = {c.lower(): c for c in df_ohlcv.columns}
                if col in lower_cols:
                    df_ohlcv = df_ohlcv.rename(columns={lower_cols[col]: col})
                else:
                    raise ValueError(f"Missing required OHLCV column: '{col}'")

        n_bars = len(df_ohlcv)
        close = df_ohlcv["close"].astype(float).values
        high = df_ohlcv["high"].astype(float).values
        low = df_ohlcv["low"].astype(float).values
        volume = df_ohlcv["volume"].astype(float).values

        res_df = pd.DataFrame(index=df_ohlcv.index)
        insufficient_warmup = {}

        # Compute MA50
        res_df["MA50"] = talib.SMA(close, timeperiod=50)
        insufficient_warmup["MA50"] = bool(n_bars < 50)

        # Compute MA200
        res_df["MA200"] = talib.SMA(close, timeperiod=200)
        insufficient_warmup["MA200"] = bool(n_bars < 200)

        # Compute RSI14
        res_df["RSI14"] = talib.RSI(close, timeperiod=14)
        insufficient_warmup["RSI14"] = bool(n_bars < 15)

        # Compute ATR14
        res_df["ATR14"] = talib.ATR(high, low, close, timeperiod=14)
        insufficient_warmup["ATR14"] = bool(n_bars < 15)

        # Compute Slow Stochastic
        slowk, slowd = talib.STOCH(high, low, close, fastk_period=14, slowk_period=3, slowd_period=3)
        res_df["STOCH_K"] = slowk
        res_df["STOCH_D"] = slowd
        insufficient_warmup["STOCH"] = bool(n_bars < 17)

        # Compute Volume MA20
        res_df["VOLUME_MA20"] = talib.SMA(volume, timeperiod=20)
        insufficient_warmup["VOLUME_MA20"] = bool(n_bars < 20)

        metadata = {
            "total_bars": n_bars,
            "timeframe": timeframe,
            "insufficient_warmup": insufficient_warmup,
            "is_network_disabled": True,
            "version": "talib-0.7.1"
        }

        return res_df, metadata

    def reconcile_tradingview_benchmark(
        self, computed_df: pd.DataFrame, tv_benchmark_df: pd.DataFrame, tolerance: float = 1e-2
    ) -> Dict[str, Any]:
        """Reconcile TA-Lib indicator outputs against TradingView benchmark values."""
        results = []
        all_matched = True

        for col in computed_df.columns:
            if col in tv_benchmark_df.columns:
                valid_mask = computed_df[col].notna() & tv_benchmark_df[col].notna()
                if valid_mask.any():
                    comp_vals = computed_df.loc[valid_mask, col].values
                    tv_vals = tv_benchmark_df.loc[valid_mask, col].values
                    diff = np.abs(comp_vals - tv_vals)
                    max_diff = float(np.max(diff))
                    matched = bool(max_diff < tolerance)
                    if not matched:
                        all_matched = False
                    results.append({
                        "indicator": col,
                        "max_difference": max_diff,
                        "matched": matched
                    })

        return {
            "all_matched": all_matched,
            "indicator_checks": results
        }
