from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

# =========================================================
# CONFIG
# =========================================================

BENCHMARK = "^NSEI"

BACKTEST_PERIOD = "1y"

TRADING_DAYS = 252

RISK_FREE_RATE = 0.06

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

PORTFOLIO_FILE = ROOT_DIR / "data" / "portfolio_allocation.csv"

OUTPUT_FILE = ROOT_DIR / "data" / "backtest_results.csv"

EQUITY_CURVE_FILE = ROOT_DIR / "data" / "portfolio_equity_curve.csv"

# =========================================================
# LOAD PORTFOLIO
# =========================================================

print("\n📥 Loading Portfolio...")

portfolio = pd.read_csv(PORTFOLIO_FILE)

print("✅ Portfolio Loaded")

# =========================================================
# SYMBOLS
# =========================================================

symbols = (
    portfolio["Symbol"]
    .astype(str)
    .str.replace(".NS", "", regex=False)
    .str.strip()
    .unique()
    .tolist()
)

weights = dict(
    zip(
        portfolio["Symbol"],
        portfolio["FINAL_WEIGHT"] / 100,
        strict=False,
    )
)

# =========================================================
# DOWNLOAD DATA
# =========================================================

tickers = [f"{symbol}.NS" for symbol in symbols]

tickers.append(BENCHMARK)

print("\n📥 Downloading Historical Prices...")

prices = yf.download(
    tickers, period=BACKTEST_PERIOD, auto_adjust=True, progress=False, threads=True
)

# =========================================================
# MULTIINDEX FIX
# =========================================================

if isinstance(prices.columns, pd.MultiIndex):
    close_prices = prices["Close"]

else:
    close_prices = prices

# =========================================================
# DROP NaN
# =========================================================

close_prices = close_prices.dropna(axis=1, how="all")

# =========================================================
# RETURNS
# =========================================================

returns = close_prices.pct_change().dropna()

# =========================================================
# BENCHMARK RETURNS
# =========================================================

benchmark_returns = returns[BENCHMARK]

# =========================================================
# PORTFOLIO RETURNS
# =========================================================

portfolio_returns = pd.Series(0, index=returns.index, dtype=float)

for symbol, weight in weights.items():
    ticker = f"{symbol}.NS"

    if ticker in returns.columns:
        portfolio_returns += returns[ticker] * weight

# =========================================================
# EQUITY CURVE
# =========================================================

equity_curve = (1 + portfolio_returns).cumprod()

benchmark_curve = (1 + benchmark_returns).cumprod()

# =========================================================
# CAGR
# =========================================================

years = len(portfolio_returns) / TRADING_DAYS

portfolio_cagr = equity_curve.iloc[-1] ** (1 / years) - 1

benchmark_cagr = benchmark_curve.iloc[-1] ** (1 / years) - 1

# =========================================================
# VOLATILITY
# =========================================================

portfolio_vol = portfolio_returns.std() * np.sqrt(TRADING_DAYS)

benchmark_vol = benchmark_returns.std() * np.sqrt(TRADING_DAYS)

# =========================================================
# SHARPE RATIO
# =========================================================

portfolio_sharpe = (portfolio_cagr - RISK_FREE_RATE) / portfolio_vol

benchmark_sharpe = (benchmark_cagr - RISK_FREE_RATE) / benchmark_vol

# =========================================================
# MAX DRAWDOWN
# =========================================================

rolling_max = equity_curve.cummax()

drawdown = equity_curve / rolling_max - 1

max_drawdown = drawdown.min()

# =========================================================
# WIN RATE
# =========================================================

win_rate = (portfolio_returns > 0).mean() * 100

# =========================================================
# ALPHA
# =========================================================

alpha = portfolio_cagr - benchmark_cagr

# =========================================================
# OUTPUT DATAFRAME
# =========================================================

results = pd.DataFrame(
    {
        "PORTFOLIO_CAGR": [round(portfolio_cagr * 100, 2)],
        "BENCHMARK_CAGR": [round(benchmark_cagr * 100, 2)],
        "ALPHA": [round(alpha * 100, 2)],
        "PORTFOLIO_VOLATILITY": [round(portfolio_vol * 100, 2)],
        "BENCHMARK_VOLATILITY": [round(benchmark_vol * 100, 2)],
        "PORTFOLIO_SHARPE": [round(portfolio_sharpe, 2)],
        "BENCHMARK_SHARPE": [round(benchmark_sharpe, 2)],
        "MAX_DRAWDOWN": [round(max_drawdown * 100, 2)],
        "WIN_RATE": [round(win_rate, 2)],
    }
)

# =========================================================
# SAVE RESULTS
# =========================================================

results.to_csv(OUTPUT_FILE, index=False)

# =========================================================
# SAVE EQUITY CURVE
# =========================================================

curve_df = pd.DataFrame(
    {
        "Date": equity_curve.index,
        "Portfolio": equity_curve.values,
        "Benchmark": benchmark_curve.values,
    }
)

curve_df.to_csv(EQUITY_CURVE_FILE, index=False)

# =========================================================
# OUTPUT
# =========================================================

print("\n✅ Backtest Completed")

print(f"\n📁 Results Saved:\n{OUTPUT_FILE}")

print(f"\n📈 Equity Curve Saved:\n{EQUITY_CURVE_FILE}")

print("\n🏆 PERFORMANCE SUMMARY:\n")

print(results.T)
