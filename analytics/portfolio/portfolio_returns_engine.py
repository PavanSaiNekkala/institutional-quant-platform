from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

PORTFOLIO_FILE = ROOT / "data" / "portfolio" / "optimised_portfolio.csv"

RETURNS_FILE = ROOT / "data" / "portfolio" / "portfolio_returns.csv"

# =========================================================
# SETTINGS
# =========================================================

LOOKBACK_DAYS = 252

# =========================================================
# LOAD
# =========================================================

print("\n📥 Loading Portfolio...")

if not PORTFOLIO_FILE.exists():
    raise FileNotFoundError(f"Missing: {PORTFOLIO_FILE}")

portfolio = pd.read_csv(PORTFOLIO_FILE)

# =========================================================
# WEIGHT COLUMN
# =========================================================

if "OPTIMAL_WEIGHT" in portfolio.columns:
    weight_col = "OPTIMAL_WEIGHT"

elif "FINAL_WEIGHT" in portfolio.columns:
    weight_col = "FINAL_WEIGHT"

else:
    raise ValueError("No weight column found")

# =========================================================
# SYMBOLS
# =========================================================

portfolio["Symbol"] = (
    portfolio["Symbol"].astype(str).str.replace(".NS", "", regex=False).str.upper().str.strip()
)

symbols = [f"{x}.NS" for x in portfolio["Symbol"]]

weights = portfolio[weight_col].fillna(0).astype(float)

weights = weights / weights.sum()

# =========================================================
# DOWNLOAD PRICES
# =========================================================

print(f"\n📡 Downloading {len(symbols)} stocks...")

prices = yf.download(tickers=symbols, period="1y", auto_adjust=True, progress=False, threads=True)

if prices.empty:
    raise ValueError("No market data downloaded")

# =========================================================
# CLOSE PRICES
# =========================================================

if isinstance(prices.columns, pd.MultiIndex):
    close_prices = prices["Close"]

else:
    close_prices = prices

# =========================================================
# CLEAN
# =========================================================

close_prices = close_prices.dropna(axis=1, how="all")

available_symbols = list(close_prices.columns)

if len(available_symbols) == 0:
    raise ValueError("No valid price history")

# =========================================================
# ALIGN WEIGHTS
# =========================================================

weight_map = dict(
    zip(
        symbols,
        weights,
        strict=False,
    )
)

weights_vector = np.array([weight_map[s] for s in available_symbols])

weights_vector = weights_vector / weights_vector.sum()

# =========================================================
# RETURNS
# =========================================================

stock_returns = close_prices.pct_change(fill_method=None).dropna()

# =========================================================
# PORTFOLIO RETURNS
# =========================================================

portfolio_returns = stock_returns.mul(weights_vector, axis=1).sum(axis=1)

# =========================================================
# OUTPUT
# =========================================================

returns_df = pd.DataFrame(
    {"Date": portfolio_returns.index, "Portfolio_Return": portfolio_returns.values}
)

returns_df["Cumulative_Return"] = (1 + returns_df["Portfolio_Return"]).cumprod() - 1

# =========================================================
# SAVE
# =========================================================

returns_df.to_csv(RETURNS_FILE, index=False)

# =========================================================
# REPORT
# =========================================================

print("\n✅ Portfolio Returns Generated")

print(f"\n📁 Saved:\n{RETURNS_FILE}")

print(f"\n📊 Observations: {len(returns_df)}")

print("\nReturn Statistics:\n")

print(returns_df["Portfolio_Return"].describe())

print("\nUnique Daily Returns:", returns_df["Portfolio_Return"].nunique())
