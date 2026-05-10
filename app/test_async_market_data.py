import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from core.async_market_data import (
    fetch_market_data
)

# =====================================================
# TEST SYMBOLS
# =====================================================

symbols = [

    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS"
]

# =====================================================
# FETCH
# =====================================================

data = fetch_market_data(

    symbols,

    max_workers=5
)

# =====================================================
# OUTPUT
# =====================================================

print("\nASYNC MARKET DATA\n")

for symbol, df in data.items():

    print(

        symbol,

        len(df)
    )