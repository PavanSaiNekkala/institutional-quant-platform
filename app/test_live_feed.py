import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from signals.live_feed import (
    live_stock_data,
    live_market_snapshot,
    market_timestamp
)

# =====================================================
# SINGLE STOCK
# =====================================================

reliance = live_stock_data(

    "RELIANCE.NS"
)

print("\nLIVE RELIANCE DATA")

print(reliance.tail())

# =====================================================
# MULTI STOCK
# =====================================================

symbols = [

    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS"
]

snapshot = live_market_snapshot(

    symbols
)

print("\nMARKET SNAPSHOT")

for symbol, data in snapshot.items():

    print(f"\n{symbol}")

    print(data.tail(2))

# =====================================================
# TIMESTAMP
# =====================================================

print("\nMARKET TIMESTAMP")

print(market_timestamp())