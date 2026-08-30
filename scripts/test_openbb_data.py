import sys
import os
import time

print("Testing OpenBB imports...")
t0 = time.time()
from openbb import obb
print(f"Imported obb in {time.time() - t0:.2f}s")

# Test yfinance equity historical
try:
    print("Fetching SPY from yfinance...")
    res = obb.equity.price.historical(symbol="SPY", provider="yfinance")
    df = res.to_df()
    print("SPY data shape:", df.shape)
    print("SPY tail:\n", df.tail(2))
except Exception as e:
    print("SPY fetch error:", e)

# Test FRED series
try:
    print("Fetching FRED WALCL (Fed balance sheet)...")
    res = obb.economy.fred_series(symbol="WALCL", provider="fred")
    df = res.to_df()
    print("WALCL shape:", df.shape)
    print("WALCL tail:\n", df.tail(2))
except Exception as e:
    print("FRED WALCL fetch error:", e)

# Test FRED T10Y2Y
try:
    print("Fetching FRED T10Y2Y...")
    res = obb.economy.fred_series(symbol="T10Y2Y", provider="fred")
    df = res.to_df()
    print("T10Y2Y shape:", df.shape)
    print("T10Y2Y tail:\n", df.tail(2))
except Exception as e:
    print("FRED T10Y2Y fetch error:", e)
