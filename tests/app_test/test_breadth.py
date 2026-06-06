import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import pandas as pd

from analytics.downloader import (
    load_symbols,
    prefilter_symbols,
    batch_download
)

from core.breadth import (
    advance_decline_ratio,
    breadth_momentum,
    percent_above_ma,
    breadth_score,
    breadth_regime
)

# =====================================================
# LOAD UNIVERSE
# =====================================================

symbols = load_symbols()

symbols = prefilter_symbols(symbols)

symbols = symbols[:30]

print("DOWNLOADING DATA...")

stock_data = batch_download(symbols)

# =====================================================
# BUILD PRICE MATRIX
# =====================================================

prices = pd.DataFrame()

for symbol, df in stock_data.items():

    prices[symbol] = df["close"]

prices = prices.dropna()

returns_df = prices.pct_change().dropna()

# =====================================================
# ADVANCE DECLINE
# =====================================================

ad_ratio = advance_decline_ratio(

    returns_df
)

print("\nADVANCE DECLINE RATIO")

print(ad_ratio.tail())

# =====================================================
# BREADTH MOMENTUM
# =====================================================

bm = breadth_momentum(

    returns_df
)

print("\nBREADTH MOMENTUM")

print(bm.tail())

# =====================================================
# PERCENT ABOVE MA
# =====================================================

pct_ma = percent_above_ma(

    prices
)

print("\nPERCENT ABOVE MA")

print(pct_ma.tail())

# =====================================================
# BREADTH SCORE
# =====================================================

bs = breadth_score(

    ad_ratio,

    pct_ma
)

print("\nBREADTH SCORE")

print(bs.tail())

# =====================================================
# MARKET REGIME
# =====================================================

regime = breadth_regime(

    bs
)

print("\nMARKET BREADTH REGIME")

print(regime)
