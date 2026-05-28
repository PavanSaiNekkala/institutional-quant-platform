import pandas as pd
import numpy as np
import yfinance as yf

from pathlib import Path

# =========================================================
# CONFIG
# =========================================================

LOOKBACK_DAYS = 252

TOP_N = 20

MAX_WEIGHT = 0.10

MIN_WEIGHT = 0.01

RISK_FREE_RATE = 0.06

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    ROOT_DIR
    / "data"
    / "factor_model_rankings.csv"
)

OUTPUT_FILE = (
    ROOT_DIR
    / "data"
    / "portfolio_allocation.csv"
)

# =========================================================
# LOAD DATA
# =========================================================

print("\n📥 Loading Factor Model Rankings...")

df = pd.read_csv(INPUT_FILE)

print("✅ Data Loaded")

# =========================================================
# CLEAN COLUMNS
# =========================================================

df.columns = df.columns.str.strip()

# =========================================================
# REQUIRED COLUMNS
# =========================================================

required_cols = [

    "Symbol",

    "MULTI_FACTOR_SCORE"

]

for col in required_cols:

    if col not in df.columns:

        raise Exception(
            f"\n❌ Missing Required Column: {col}"
        )

# =========================================================
# TOP STOCKS
# =========================================================

df = df.sort_values(

    by="MULTI_FACTOR_SCORE",

    ascending=False
)

portfolio = df.head(TOP_N).copy()

symbols = (

    portfolio["Symbol"]

    .astype(str)

    .str.replace(".NS", "", regex=False)

    .tolist()
)

yf_symbols = [

    f"{s}.NS"
    for s in symbols
]

# =========================================================
# DOWNLOAD PRICES
# =========================================================

print("\n📥 Downloading Historical Prices...")

prices = yf.download(

    yf_symbols,

    period="2y",

    auto_adjust=True,

    progress=False
)

if "Close" in prices.columns:

    prices = prices["Close"]

prices = prices.dropna(
    axis=1,
    how="all"
)

prices = prices.ffill()

# =========================================================
# RETURNS
# =========================================================

returns = prices.pct_change().dropna()

# =========================================================
# EXPECTED RETURNS
# =========================================================

expected_returns = (

    returns.mean()
    * 252
)

# =========================================================
# COVARIANCE MATRIX
# =========================================================

cov_matrix = (

    returns.cov()
    * 252
)

# =========================================================
# VOLATILITY
# =========================================================

volatility = np.sqrt(
    np.diag(cov_matrix)
)

# =========================================================
# RISK PARITY WEIGHTS
# =========================================================

inv_vol = 1 / volatility

risk_parity_weights = (

    inv_vol
    / inv_vol.sum()
)

# =========================================================
# WEIGHT CLEANUP
# =========================================================

weights = np.clip(

    risk_parity_weights,

    MIN_WEIGHT,

    MAX_WEIGHT
)

weights = (

    weights
    / weights.sum()
)

# =========================================================
# PORTFOLIO METRICS
# =========================================================

portfolio_return = np.dot(

    weights,

    expected_returns
)

portfolio_volatility = np.sqrt(

    np.dot(
        weights.T,
        np.dot(
            cov_matrix,
            weights
        )
    )
)

sharpe_ratio = (

    (
        portfolio_return
        - RISK_FREE_RATE
    )

    /

    portfolio_volatility
)

# =========================================================
# OUTPUT DATAFRAME
# =========================================================

optimized_portfolio = pd.DataFrame({

    "Symbol":

        prices.columns,

    "Weight":

        np.round(
            weights,
            4
        ),

    "Expected_Return":

        np.round(
            expected_returns.values,
            4
        ),

    "Volatility":

        np.round(
            volatility,
            4
        )

})

optimized_portfolio = (

    optimized_portfolio

    .sort_values(

        by="Weight",

        ascending=False
    )
)

# =========================================================
# SAVE
# =========================================================

optimized_portfolio.to_csv(

    OUTPUT_FILE,

    index=False
)

# =========================================================
# OUTPUT
# =========================================================

print(
    "\n✅ Portfolio Optimization Complete"
)

print(
    f"\n📁 Saved To:\n"
    f"{OUTPUT_FILE}"
)

print("\n🏆 PORTFOLIO METRICS:\n")

print(
    f"Expected Return: "
    f"{portfolio_return:.2%}"
)

print(
    f"Portfolio Volatility: "
    f"{portfolio_volatility:.2%}"
)

print(
    f"Sharpe Ratio: "
    f"{sharpe_ratio:.2f}"
)

print("\n🏆 OPTIMIZED PORTFOLIO:\n")

print(

    optimized_portfolio.head(15)
)
