from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

# =========================================================
# CONFIG
# =========================================================

BENCHMARK = "^NSEI"

LOOKBACK_PERIOD = "1y"

SIMULATION_DAYS = 252

NUM_SIMULATIONS = 5000

INITIAL_CAPITAL = 100000

TRADING_DAYS = 252

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

PORTFOLIO_FILE = ROOT_DIR / "data" / "portfolio_allocation.csv"

OUTPUT_FILE = ROOT_DIR / "data" / "monte_carlo_results.csv"

PATHS_FILE = ROOT_DIR / "data" / "monte_carlo_paths.csv"

# =========================================================
# LOAD PORTFOLIO
# =========================================================

print("\n📥 Loading Portfolio...")

portfolio = pd.read_csv(PORTFOLIO_FILE)

print("✅ Portfolio Loaded")

# =========================================================
# CLEAN SYMBOLS
# =========================================================

portfolio["Symbol"] = (
    portfolio["Symbol"].astype(str).str.replace(".NS", "", regex=False).str.strip().str.upper()
)

# =========================================================
# SYMBOLS & WEIGHTS
# =========================================================

symbols = portfolio["Symbol"].tolist()

weights = (portfolio["FINAL_WEIGHT"] / 100).values

tickers = [f"{symbol}.NS" for symbol in symbols]

# =========================================================
# DOWNLOAD DATA
# =========================================================

print("\n📥 Downloading Historical Prices...")

prices = yf.download(
    tickers, period=LOOKBACK_PERIOD, auto_adjust=True, progress=False, threads=True
)

# =========================================================
# FIX MULTIINDEX
# =========================================================

if isinstance(prices.columns, pd.MultiIndex):
    prices = prices["Close"]

# =========================================================
# CLEAN DATA
# =========================================================

prices = prices.dropna(axis=1, how="all")

prices = prices.ffill()

# =========================================================
# RETURNS
# =========================================================

returns = prices.pct_change().dropna()

# =========================================================
# PORTFOLIO RETURNS
# =========================================================

portfolio_returns = pd.Series(0, index=returns.index, dtype=float)

for i, symbol in enumerate(symbols):
    ticker = f"{symbol}.NS"

    if ticker in returns.columns:
        portfolio_returns += returns[ticker] * weights[i]

# =========================================================
# DAILY STATISTICS
# =========================================================

daily_mean = portfolio_returns.mean()

daily_std = portfolio_returns.std()

# =========================================================
# MONTE CARLO SIMULATION
# =========================================================

print("\n🧠 Running Monte Carlo Simulations...")

simulation_results = np.zeros((SIMULATION_DAYS, NUM_SIMULATIONS))

final_values = []

for sim in range(NUM_SIMULATIONS):
    simulated_returns = np.random.normal(loc=daily_mean, scale=daily_std, size=SIMULATION_DAYS)

    portfolio_path = np.zeros(SIMULATION_DAYS)

    portfolio_path[0] = INITIAL_CAPITAL

    for t in range(1, SIMULATION_DAYS):
        portfolio_path[t] = portfolio_path[t - 1] * (1 + simulated_returns[t])

    simulation_results[:, sim] = portfolio_path

    final_values.append(portfolio_path[-1])

# =========================================================
# FINAL VALUE STATISTICS
# =========================================================

final_values = np.array(final_values)

expected_value = np.mean(final_values)

median_value = np.median(final_values)

best_case = np.max(final_values)

worst_case = np.min(final_values)

percentile_5 = np.percentile(final_values, 5)

percentile_95 = np.percentile(final_values, 95)

probability_profit = (final_values > INITIAL_CAPITAL).mean() * 100

# =========================================================
# CAGR DISTRIBUTION
# =========================================================

years = SIMULATION_DAYS / TRADING_DAYS

cagr_distribution = (final_values / INITIAL_CAPITAL) ** (1 / years) - 1

expected_cagr = np.mean(cagr_distribution)

# =========================================================
# MAX DRAWDOWN DISTRIBUTION
# =========================================================

drawdowns = []

for sim in range(NUM_SIMULATIONS):
    curve = simulation_results[:, sim]

    running_max = np.maximum.accumulate(curve)

    dd = curve / running_max - 1

    drawdowns.append(dd.min())

expected_drawdown = np.mean(drawdowns)

worst_drawdown = np.min(drawdowns)

# =========================================================
# RESULTS DATAFRAME
# =========================================================

results = pd.DataFrame(
    {
        "INITIAL_CAPITAL": [INITIAL_CAPITAL],
        "EXPECTED_FINAL_VALUE": [round(expected_value, 2)],
        "MEDIAN_FINAL_VALUE": [round(median_value, 2)],
        "BEST_CASE": [round(best_case, 2)],
        "WORST_CASE": [round(worst_case, 2)],
        "PERCENTILE_5": [round(percentile_5, 2)],
        "PERCENTILE_95": [round(percentile_95, 2)],
        "EXPECTED_CAGR": [round(expected_cagr * 100, 2)],
        "EXPECTED_MAX_DRAWDOWN": [round(expected_drawdown * 100, 2)],
        "WORST_DRAWDOWN": [round(worst_drawdown * 100, 2)],
        "PROBABILITY_OF_PROFIT": [round(probability_profit, 2)],
    }
)

# =========================================================
# SAVE RESULTS
# =========================================================

results.to_csv(OUTPUT_FILE, index=False)

# =========================================================
# SAVE PATHS
# =========================================================

paths_df = pd.DataFrame(simulation_results)

paths_df.to_csv(PATHS_FILE, index=False)

# =========================================================
# OUTPUT
# =========================================================

print("\n✅ Monte Carlo Simulation Completed")

print(f"\n📁 Results Saved:\n{OUTPUT_FILE}")

print(f"\n📁 Simulation Paths Saved:\n{PATHS_FILE}")

print("\n🧠 MONTE CARLO SUMMARY:\n")

print(results.T)
