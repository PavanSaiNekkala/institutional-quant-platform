from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

# =========================================================
# FILES
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

PORTFOLIO_FILE = ROOT / "data" / "risk_parity_portfolio.csv"

OUTPUT_EQUITY = ROOT / "data" / "walk_forward_equity_curve.csv"

OUTPUT_STATS = ROOT / "data" / "walk_forward_stats.csv"

# =========================================================
# SETTINGS
# =========================================================

START_DATE = "2020-01-01"

REBALANCE_FREQ = "M"

# =========================================================
# LOAD PORTFOLIO
# =========================================================

print("\n📥 Loading Portfolio...")

portfolio = pd.read_csv(PORTFOLIO_FILE)

symbols = []

for sym in portfolio["Symbol"]:
    sym = str(sym).upper().strip()

    if not sym.endswith(".NS"):
        sym = sym + ".NS"

    symbols.append(sym)

portfolio["YF_SYMBOL"] = symbols

weights = dict(
    zip(
        portfolio["YF_SYMBOL"],
        portfolio["FINAL_WEIGHT"],
        strict=False,
    )
)

# =========================================================
# DOWNLOAD DATA
# =========================================================

print(f"\n📡 Downloading {len(symbols)} stocks...")

prices = yf.download(tickers=symbols, start=START_DATE, auto_adjust=True, progress=False)

if prices.empty:
    raise ValueError("No price data downloaded.")

# =========================================================
# CLOSE PRICES
# =========================================================

if isinstance(prices.columns, pd.MultiIndex):
    prices = prices["Close"]

# =========================================================
# RETURNS
# =========================================================

returns = prices.pct_change(fill_method=None)

returns = returns.dropna(how="all")

# =========================================================
# MONTHLY REBALANCE DATES
# =========================================================

rebalance_dates = returns.resample(REBALANCE_FREQ).last().index

# =========================================================
# WALK FORWARD
# =========================================================

portfolio_returns = []

current_weights = weights.copy()

for date in returns.index:
    daily_return = 0

    for stock in current_weights:
        if stock in returns.columns:
            r = returns.loc[date, stock]

            if pd.notna(r):
                daily_return += current_weights[stock] * r

    portfolio_returns.append(daily_return)

    if date in rebalance_dates:
        current_weights = weights.copy()

# =========================================================
# EQUITY CURVE
# =========================================================

equity = (1 + pd.Series(portfolio_returns, index=returns.index)).cumprod()

equity_df = pd.DataFrame({"Date": equity.index, "Portfolio_Value": equity.values})

# =========================================================
# PERFORMANCE
# =========================================================

total_return = equity.iloc[-1] - 1

years = (equity.index[-1] - equity.index[0]).days / 365.25

cagr = equity.iloc[-1] ** (1 / years) - 1

volatility = pd.Series(portfolio_returns).std() * np.sqrt(252)

sharpe = cagr / volatility

rolling_max = equity.cummax()

drawdown = equity / rolling_max - 1

max_drawdown = drawdown.min()

win_rate = np.mean(np.array(portfolio_returns) > 0) * 100

# =========================================================
# SAVE STATS
# =========================================================

stats_df = pd.DataFrame(
    {
        "Metric": ["Total Return", "CAGR", "Volatility", "Sharpe", "Max Drawdown", "Win Rate"],
        "Value": [
            round(total_return * 100, 2),
            round(cagr * 100, 2),
            round(volatility * 100, 2),
            round(sharpe, 2),
            round(max_drawdown * 100, 2),
            round(win_rate, 2),
        ],
    }
)

equity_df.to_csv(OUTPUT_EQUITY, index=False)

stats_df.to_csv(OUTPUT_STATS, index=False)

# =========================================================
# REPORT
# =========================================================

print("\n✅ Walk Forward Backtest Complete")

print("\n📁 Equity Curve Saved:")

print(OUTPUT_EQUITY)

print("\n📁 Statistics Saved:")

print(OUTPUT_STATS)

print("\n🏆 Results:\n")

print(stats_df)
