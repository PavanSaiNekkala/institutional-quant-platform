import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import yfinance as yf

from core.regime import (
    trend_regime,
    volatility_regime,
    combined_regime,
    regime_allocation
)

# =====================================================
# DOWNLOAD MARKET DATA
# =====================================================

data = yf.download(

    "^NSEI",

    period="2y",

    progress=False
)

close = data["Close"].squeeze()

returns = close.pct_change()

# =====================================================
# TREND REGIME
# =====================================================

trend = trend_regime(

    close
)

print("\nTREND REGIME")

print(trend.tail())

# =====================================================
# VOLATILITY REGIME
# =====================================================

vol = volatility_regime(

    returns
)

print("\nVOLATILITY REGIME")

print(vol.tail())

# =====================================================
# COMBINED REGIME
# =====================================================

combined = combined_regime(

    close,

    returns
)

print("\nCOMBINED REGIME")

print(combined.tail())

# =====================================================
# CURRENT ALLOCATION
# =====================================================

latest_regime = combined.iloc[-1]

allocation = regime_allocation(

    latest_regime
)

print("\nCURRENT REGIME")

print(latest_regime)

print("\nRECOMMENDED EXPOSURE")

print(allocation)
