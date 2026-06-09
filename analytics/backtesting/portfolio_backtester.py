import pandas as pd
import numpy as np
import yfinance as yf
from pathlib import Path

# =========================================================
# FILES
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

PORTFOLIO_FILE = (
    ROOT
    / "data"
    / "risk_parity_portfolio.csv"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "backtest_results.csv"
)

# =========================================================
# SETTINGS
# =========================================================

LOOKBACK_YEARS = 3

BENCHMARK = "^NSEI"

RISK_FREE_RATE = 0.06

# =========================================================
# LOAD PORTFOLIO
# =========================================================

print("\n📥 Loading Portfolio...")

portfolio = pd.read_csv(
    PORTFOLIO_FILE
)

if "FINAL_WEIGHT" not in portfolio.columns:

    raise ValueError(
        "FINAL_WEIGHT column missing."
    )

# =========================================================
# SYMBOLS
# =========================================================

symbols = []

for s in portfolio["Symbol"]:

    s = str(s).upper().strip()

    if not s.endswith(".NS"):

        s = s + ".NS"

    symbols.append(s)

weights = (
    portfolio["FINAL_WEIGHT"]
    .values
)

# =========================================================
# DOWNLOAD DATA
# =========================================================

print(
    f"\n📡 Downloading {len(symbols)} stocks..."
)

prices = yf.download(
    tickers=symbols,
    period=f"{LOOKBACK_YEARS}y",
    auto_adjust=True,
    progress=False
)

if isinstance(prices.columns, pd.MultiIndex):

    prices = prices["Close"]

# =========================================================
# CLEAN
# =========================================================

prices = prices.dropna(
    axis=1,
    how="all"
)

valid_cols = prices.columns.tolist()

valid_weights = []

for sym in valid_cols:

    idx = symbols.index(sym)

    valid_weights.append(
        weights[idx]
    )

weights = np.array(
    valid_weights
)

weights = (
    weights
    /
    weights.sum()
)

# =========================================================
# RETURNS
# =========================================================

returns = prices.pct_change(
    fill_method=None
)

returns = returns.dropna()

# =========================================================
# PORTFOLIO RETURNS
# =========================================================

portfolio_returns = (

    returns

    * weights

).sum(axis=1)

# =========================================================
# EQUITY CURVE
# =========================================================

equity_curve = (

    1

    + portfolio_returns

).cumprod()

# =========================================================
# CAGR
# =========================================================

years = (

    len(equity_curve)

    / 252
)

cagr = (

    equity_curve.iloc[-1]

    **

    (1 / years)

    - 1
)

# =========================================================
# VOLATILITY
# =========================================================

volatility = (

    portfolio_returns.std()

    *

    np.sqrt(252)
)

# =========================================================
# SHARPE
# =========================================================

sharpe = (

    cagr

    - RISK_FREE_RATE

) / volatility

# =========================================================
# MAX DRAWDOWN
# =========================================================

rolling_max = (

    equity_curve.cummax()
)

drawdown = (

    equity_curve

    /

    rolling_max

    - 1
)

max_drawdown = (
    drawdown.min()
)

# =========================================================
# BENCHMARK
# =========================================================

print(
    "\n📡 Downloading Benchmark..."
)

benchmark = yf.download(
    BENCHMARK,
    period=f"{LOOKBACK_YEARS}y",
    auto_adjust=True,
    progress=False
)

benchmark = benchmark["Close"]

benchmark_returns = (

    benchmark

    .pct_change()

    .dropna()
)

benchmark_curve = (

    1

    + benchmark_returns

).cumprod()

benchmark_cagr = (

    benchmark_curve.iloc[-1]

    **

    (1 / years)

    - 1
)

alpha = (
    cagr
    -
    benchmark_cagr
)

# =========================================================
# REPORT
# =========================================================

report = pd.DataFrame({

    "Metric": [

        "CAGR",

        "Annual Volatility",

        "Sharpe Ratio",

        "Max Drawdown",

        "Benchmark CAGR",

        "Alpha"
    ],

    "Value": [

        round(cagr * 100, 2),

        round(volatility * 100, 2),

        round(sharpe, 2),

        round(max_drawdown * 100, 2),

        round(
            benchmark_cagr * 100,
            2
        ),

        round(alpha * 100, 2)
    ]
})

report.to_csv(
    OUTPUT_FILE,
    index=False
)

# =========================================================
# OUTPUT
# =========================================================

print("\n✅ Backtest Complete")

print("\n📁 Saved:")

print(
    OUTPUT_FILE
)

print("\n🏆 Performance Summary:\n")

print(report)
