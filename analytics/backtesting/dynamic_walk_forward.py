from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

# =========================================================
# SETTINGS
# =========================================================

START_DATE = "2020-01-01"

TOP_N = 20

MOMENTUM_LOOKBACK = 252

VOL_LOOKBACK = 126

# =========================================================
# FILES
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

UNIVERSE_FILE = ROOT / "data" / "raw" / "updated_stocks.xlsx"

EQUITY_FILE = ROOT / "data" / "dynamic_equity_curve.csv"

STATS_FILE = ROOT / "data" / "dynamic_backtest_stats.csv"

# =========================================================
# LOAD UNIVERSE
# =========================================================

print("\n📥 Loading Universe...")

universe = pd.read_excel(UNIVERSE_FILE)

symbols = []

for sym in universe["Symbol"]:
    sym = str(sym).upper().strip()

    if not sym.endswith(".NS"):
        sym += ".NS"

    symbols.append(sym)

symbols = list(set(symbols))

print(f"\nUniverse Size: {len(symbols)}")

# =========================================================
# DOWNLOAD
# =========================================================

print("\n📡 Downloading Historical Data...")

prices = yf.download(tickers=symbols, start=START_DATE, auto_adjust=True, progress=False)

if isinstance(prices.columns, pd.MultiIndex):
    prices = prices["Close"]

prices = prices.dropna(axis=1, how="all")

# =========================================================
# RETURNS
# =========================================================

returns = prices.pct_change(fill_method=None)

# =========================================================
# MONTH-END DATES
# =========================================================

month_ends = prices.resample("ME").last().index

# =========================================================
# WALK FORWARD
# =========================================================

portfolio_returns = []

portfolio_dates = []

for i in range(12, len(month_ends) - 1):
    formation_date = month_ends[i]

    next_date = month_ends[i + 1]

    hist_prices = prices.loc[:formation_date]

    if len(hist_prices) < MOMENTUM_LOOKBACK:
        continue

    # ============================================
    # MOMENTUM
    # ============================================

    momentum = hist_prices.iloc[-1] / hist_prices.iloc[-MOMENTUM_LOOKBACK] - 1

    momentum = momentum.dropna()

    if len(momentum) < TOP_N:
        continue

    # ============================================
    # TOP MOMENTUM
    # ============================================

    selected = momentum.sort_values(ascending=False).head(TOP_N).index

    # ============================================
    # VOLATILITY
    # ============================================

    hist_returns = returns[selected].loc[:formation_date].tail(VOL_LOOKBACK)

    vol = hist_returns.std() * np.sqrt(252)

    vol = vol.replace(0, np.nan)

    vol = vol.dropna()

    if len(vol) == 0:
        continue

    # ============================================
    # RISK PARITY
    # ============================================

    inv_vol = 1 / vol

    weights = inv_vol / inv_vol.sum()

    # ============================================
    # NEXT MONTH RETURN
    # ============================================

    forward_returns = returns[selected].loc[formation_date:next_date]

    if len(forward_returns) == 0:
        continue

    monthly_portfolio = forward_returns.mul(weights, axis=1).sum(axis=1)

    portfolio_returns.extend(monthly_portfolio.values)

    portfolio_dates.extend(monthly_portfolio.index)

# =========================================================
# EQUITY CURVE
# =========================================================

equity = (1 + pd.Series(portfolio_returns, index=portfolio_dates)).cumprod()

equity_df = pd.DataFrame({"Date": equity.index, "Portfolio_Value": equity.values})

# =========================================================
# STATS
# =========================================================

daily_returns = pd.Series(portfolio_returns)

total_return = equity.iloc[-1] - 1

years = (equity.index[-1] - equity.index[0]).days / 365.25

cagr = equity.iloc[-1] ** (1 / years) - 1

volatility = daily_returns.std() * np.sqrt(252)

sharpe = cagr / volatility

rolling_max = equity.cummax()

drawdown = equity / rolling_max - 1

max_dd = drawdown.min()

win_rate = (daily_returns > 0).mean() * 100

stats_df = pd.DataFrame(
    {
        "Metric": ["Total Return", "CAGR", "Volatility", "Sharpe", "Max Drawdown", "Win Rate"],
        "Value": [
            round(total_return * 100, 2),
            round(cagr * 100, 2),
            round(volatility * 100, 2),
            round(sharpe, 2),
            round(max_dd * 100, 2),
            round(win_rate, 2),
        ],
    }
)

# =========================================================
# SAVE
# =========================================================

equity_df.to_csv(EQUITY_FILE, index=False)

stats_df.to_csv(STATS_FILE, index=False)

# =========================================================
# REPORT
# =========================================================

print("\n✅ Dynamic Walk Forward Complete")

print("\n📁 Saved:")

print(EQUITY_FILE)

print(STATS_FILE)

print("\n🏆 Results:\n")

print(stats_df)
