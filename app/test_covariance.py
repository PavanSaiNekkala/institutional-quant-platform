import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from analytics.downloader import (
    load_symbols,
    prefilter_symbols,
    batch_download
)

from portfolio.covariance import (
    build_returns_matrix,
    covariance_matrix,
    correlation_matrix,
    portfolio_volatility,
    correlation_filter
)

import numpy as np

# =====================================================
# LOAD DATA
# =====================================================

symbols = load_symbols()

symbols = prefilter_symbols(symbols)

symbols = symbols[:10]

print("DOWNLOADING DATA...")

stock_data = batch_download(symbols)

# =====================================================
# RETURNS MATRIX
# =====================================================

returns_df = build_returns_matrix(

    stock_data,

    symbols
)

print("\nRETURNS MATRIX")

print(returns_df.head())

# =====================================================
# COVARIANCE
# =====================================================

cov_matrix = covariance_matrix(

    returns_df
)

print("\nCOVARIANCE MATRIX")

print(cov_matrix)

# =====================================================
# CORRELATION
# =====================================================

corr_matrix = correlation_matrix(

    returns_df
)

print("\nCORRELATION MATRIX")

print(corr_matrix)

# =====================================================
# PORTFOLIO VOLATILITY
# =====================================================

weights = np.repeat(

    1 / len(returns_df.columns),

    len(returns_df.columns)
)

volatility = portfolio_volatility(

    weights,

    cov_matrix
)

print("\nPORTFOLIO VOLATILITY")

print(volatility)

# =====================================================
# CORRELATION FILTER
# =====================================================

selected_symbols = correlation_filter(

    returns_df,

    threshold=0.80
)

print("\nSELECTED SYMBOLS (AFTER CORRELATION FILTER)")

print(selected_symbols)

# =====================================================
# CORRELATION FILTER
# =====================================================

filtered = correlation_filter(

    returns_df,

    threshold=0.80
)

print("\nDIVERSIFIED PORTFOLIO")

print(filtered)