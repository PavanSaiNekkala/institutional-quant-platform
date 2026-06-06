import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from analytics.downloader import (
    load_symbols,
    prefilter_symbols,
    batch_download
)

from portfolio.risk_parity import (
    max_sharpe_allocation,
    min_volatility_allocation
)

import pandas as pd

# =====================================================
# LOAD DATA
# =====================================================

symbols = load_symbols()

symbols = prefilter_symbols(symbols)

symbols = symbols[:10]

print("DOWNLOADING DATA...")

stock_data = batch_download(symbols)

# =====================================================
# BUILD PRICE MATRIX
# =====================================================

prices = pd.DataFrame()

for symbol, df in stock_data.items():

    prices[symbol] = df["close"]

prices = prices.dropna()

print("\nPRICE MATRIX")

print(prices.head())

# =====================================================
# MAX SHARPE
# =====================================================

weights, performance = (

    max_sharpe_allocation(prices)
)

print("\nMAX SHARPE ALLOCATION")

print(weights)

print("\nPERFORMANCE")

print(performance)

# =====================================================
# MIN VOLATILITY
# =====================================================

weights2, performance2 = (

    min_volatility_allocation(prices)
)

print("\nMIN VOLATILITY ALLOCATION")

print(weights2)

print("\nPERFORMANCE")

print(performance2)
