"""OpenBB ODP Data Layer Adapter for IPOS.

Provides an isolated local abstraction layer over OpenBB ODP for retrieving free market
and macroeconomic time series data without requiring paid OpenBB Workspace subscriptions.
"""

from typing import Dict, Any, List, Optional
import os
import pandas as pd
import requests


class OpenBBAdapter:
    """OpenBB Provider Abstraction Layer for IPOS local market & macro data."""

    def __init__(self, fred_api_key: Optional[str] = None):
        self.fred_api_key = fred_api_key or os.getenv("FRED_API_KEY")
        self._obb = None

    @property
    def obb(self):
        """Lazy-load OpenBB obb interface."""
        if self._obb is None:
            from openbb import obb
            self._obb = obb
            if self.fred_api_key:
                try:
                    self._obb.user_settings.credentials.fred_api_key = self.fred_api_key
                except Exception:
                    pass
        return self._obb

    def fetch_equity_historical(
        self, symbol: str, provider: str = "yfinance", start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """Fetch historical equity OHLCV series.
        
        Args:
            symbol: Ticker symbol (e.g. 'SPY')
            provider: OpenBB provider (default: 'yfinance')
            start_date: YYYY-MM-DD start date
            end_date: YYYY-MM-DD end date
            
        Returns:
            pd.DataFrame indexed by date
        """
        kwargs: Dict[str, Any] = {"symbol": symbol, "provider": provider}
        if start_date:
            kwargs["start_date"] = start_date
        if end_date:
            kwargs["end_date"] = end_date
            
        res = self.obb.equity.price.historical(**kwargs)
        df = res.to_df()
        if df.empty:
            raise ValueError(f"No equity data returned for symbol '{symbol}' from provider '{provider}'")
        return df

    def fetch_fred_series(
        self, symbol: str, require_official_credential: bool = False
    ) -> pd.DataFrame:
        """Fetch macroeconomic series from FRED.
        
        If official credentials are required and missing, explicit error is raised (for negative testing).
        Otherwise falls back to direct authoritative FRED CSV stream when key is unconfigured.
        """
        if require_official_credential and not self.fred_api_key:
            # Force call to obb.economy.fred_series without key to trigger explicit credential error
            res = self.obb.economy.fred_series(symbol=symbol, provider="fred")
            return res.to_df()

        if self.fred_api_key:
            try:
                res = self.obb.economy.fred_series(symbol=symbol, provider="fred")
                df = res.to_df()
                if not df.empty:
                    return df
            except Exception as e:
                if require_official_credential:
                    raise e

        # Free fallback: direct FRED CSV download (does not require API key)
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={symbol}"
        df = pd.read_csv(url)
        if "observation_date" in df.columns:
            df["date"] = pd.to_datetime(df["observation_date"])
            df = df.set_index("date").drop(columns=["observation_date"])
        # Rename column if symbol matches
        df.columns = [symbol if col == symbol else col for col in df.columns]
        # Coerce numeric
        df[symbol] = pd.to_numeric(df[symbol], errors="coerce")
        return df.dropna()

    def get_series_metadata(self, symbol: str, provider: str) -> Dict[str, Any]:
        """Record provider metadata, rate limit rules, licensing, and frequency notes."""
        return {
            "symbol": symbol,
            "provider": provider,
            "openbb_workspace_required": False,
            "licensing": "Free public domain / Yahoo Finance TOS / FRED TOS",
            "rate_limit": "Free tier standard (unthrottled for local usage)",
            "frequency": "Daily / Monthly / Quarterly depending on series",
            "missing_value_behavior": "Explicit NaN / dropna on NaN rows",
            "cache_notes": "Local in-memory / DataFrame caching"
        }

    def reconcile_spot_check(
        self, obb_df: pd.DataFrame, direct_df: pd.DataFrame, dates: List[str], val_col: str
    ) -> Dict[str, Any]:
        """Reconcile OpenBB ODP output against direct authoritative provider values across target dates."""
        check_results = []
        all_matched = True
        
        for d in dates:
            d_ts = pd.to_datetime(d)
            val_obb = None
            val_direct = None
            
            if d_ts in obb_df.index:
                val_obb = float(obb_df.loc[d_ts, val_col])
            elif d in obb_df.index:
                val_obb = float(obb_df.loc[d, val_col])
                
            if d_ts in direct_df.index:
                val_direct = float(direct_df.loc[d_ts, val_col])
            elif d in direct_df.index:
                val_direct = float(direct_df.loc[d, val_col])
                
            matched = False
            if val_obb is not None and val_direct is not None:
                diff = abs(val_obb - val_direct)
                matched = diff < 1e-3
            
            if not matched:
                all_matched = False
                
            check_results.append({
                "date": d,
                "obb_val": val_obb,
                "direct_val": val_direct,
                "matched": matched
            })
            
        return {
            "all_matched": all_matched,
            "checks": check_results
        }
