import pandas as pd
import numpy as np
import yfinance as yf

from pathlib import Path

# =========================================================
# CONFIG
# =========================================================

BENCHMARK = "^NSEI"

LOOKBACK_PERIOD = "1y"

TRADING_DAYS = 252

CONFIDENCE_LEVEL = 0.95

RISK_FREE_RATE = 0.06

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[1]

PORTFOLIO_FILE = (
    ROOT_DIR
    / "data"
    / "portfolio_allocation.csv"
)

RISK_REPORT_FILE = (
    ROOT_DIR
    / "data"
    / "portfolio_risk_report.csv"
)

CORRELATION_FILE = (
    ROOT_DIR
    / "data"
    / "correlation_matrix.csv"
)

RISK_METRICS_FILE = (
    ROOT_DIR
    / "data"
    / "risk_metrics.csv"
)

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

    portfolio["Symbol"]

    .astype(str)

    .str.replace(".NS", "", regex=False)

    .str.strip()

    .str.upper()
)

# =========================================================
# SYMBOLS & WEIGHTS
# =========================================================

symbols = portfolio["Symbol"].tolist()

weights = (

    portfolio["FINAL_WEIGHT"]

    / 100
).values

tickers = [

    f"{symbol}.NS"

    for symbol in symbols
]

tickers.append(BENCHMARK)

# =========================================================
# DOWNLOAD DATA
# =========================================================

print("\n📥 Downloading Market Data...")

prices = yf.download(

    tickers,

    period=LOOKBACK_PERIOD,

    auto_adjust=True,

    progress=False,

    threads=True
)

# =========================================================
# FIX MULTIINDEX
# =========================================================

if isinstance(
    prices.columns,
    pd.MultiIndex
):

    prices = prices["Close"]

# =========================================================
# CLEAN DATA
# =========================================================

prices = prices.dropna(
    axis=1,
    how="all"
)

prices = prices.ffill()

# =========================================================
# RETURNS
# =========================================================

returns = (

    prices

    .pct_change()

    .dropna()
)

# =========================================================
# BENCHMARK RETURNS
# =========================================================

benchmark_returns = returns[BENCHMARK]

# =========================================================
# PORTFOLIO RETURNS
# =========================================================

portfolio_returns = pd.Series(

    0,

    index=returns.index,

    dtype=float
)

for i, symbol in enumerate(symbols):

    ticker = f"{symbol}.NS"

    if ticker in returns.columns:

        portfolio_returns += (

            returns[ticker]

            * weights[i]
        )

# =========================================================
# PORTFOLIO VOLATILITY
# =========================================================

portfolio_volatility = (

    portfolio_returns.std()

    * np.sqrt(TRADING_DAYS)
)

# =========================================================
# PORTFOLIO CAGR
# =========================================================

equity_curve = (

    1 + portfolio_returns

).cumprod()

years = (

    len(portfolio_returns)

    / TRADING_DAYS
)

portfolio_cagr = (

    equity_curve.iloc[-1]

    ** (1 / years)

    - 1
)

# =========================================================
# SHARPE RATIO
# =========================================================

sharpe_ratio = (

    portfolio_cagr

    - RISK_FREE_RATE

) / portfolio_volatility

# =========================================================
# MAX DRAWDOWN
# =========================================================

rolling_max = equity_curve.cummax()

drawdown = (

    equity_curve

    / rolling_max

    - 1
)

max_drawdown = drawdown.min()

# =========================================================
# VAR (95%)
# =========================================================

var_95 = np.percentile(

    portfolio_returns,

    (1 - CONFIDENCE_LEVEL) * 100
)

# =========================================================
# CVAR (95%)
# =========================================================

cvar_95 = portfolio_returns[

    portfolio_returns <= var_95

].mean()

# =========================================================
# BETA CALCULATION
# =========================================================

covariance = np.cov(

    portfolio_returns,

    benchmark_returns
)[0][1]

benchmark_variance = np.var(
    benchmark_returns
)

beta = (

    covariance

    / benchmark_variance
)

# =========================================================
# CORRELATION MATRIX
# =========================================================

stock_returns = returns.drop(
    columns=[BENCHMARK],
    errors="ignore"
)

correlation_matrix = (
    stock_returns.corr()
)

avg_correlation = (

    correlation_matrix

    .mean()

    .mean()
)

# =========================================================
# SECTOR EXPOSURE
# =========================================================

sector_exposure = (

    portfolio

    .groupby("Sector")["FINAL_WEIGHT"]

    .sum()

    .sort_values(
        ascending=False
    )
)

# =========================================================
# POSITION CONCENTRATION
# =========================================================

max_position = (
    portfolio["FINAL_WEIGHT"].max()
)

top5_concentration = (

    portfolio["FINAL_WEIGHT"]

    .nlargest(5)

    .sum()
)

# =========================================================
# WIN RATE
# =========================================================

win_rate = (

    (
        portfolio_returns > 0
    )

    .mean()

    * 100
)

# =========================================================
# RISK SCORE
# =========================================================

risk_score = 100

# Volatility Penalty
if portfolio_volatility > 0.30:

    risk_score -= 25

elif portfolio_volatility > 0.20:

    risk_score -= 10

# Drawdown Penalty
if max_drawdown < -0.30:

    risk_score -= 25

elif max_drawdown < -0.20:

    risk_score -= 10

# Correlation Penalty
if avg_correlation > 0.70:

    risk_score -= 15

# Concentration Penalty
if top5_concentration > 60:

    risk_score -= 15

risk_score = max(
    risk_score,
    0
)

# =========================================================
# RISK METRICS DATAFRAME
# =========================================================

risk_metrics = pd.DataFrame({

    "PORTFOLIO_CAGR": [

        round(
            portfolio_cagr * 100,
            2
        )
    ],

    "PORTFOLIO_VOLATILITY": [

        round(
            portfolio_volatility * 100,
            2
        )
    ],

    "SHARPE_RATIO": [

        round(
            sharpe_ratio,
            2
        )
    ],

    "MAX_DRAWDOWN": [

        round(
            max_drawdown * 100,
            2
        )
    ],

    "BETA": [

        round(
            beta,
            2
        )
    ],

    "VAR_95": [

        round(
            var_95 * 100,
            2
        )
    ],

    "CVAR_95": [

        round(
            cvar_95 * 100,
            2
        )
    ],

    "WIN_RATE": [

        round(
            win_rate,
            2
        )
    ],

    "AVG_CORRELATION": [

        round(
            avg_correlation,
            2
        )
    ],

    "TOP_5_CONCENTRATION": [

        round(
            top5_concentration,
            2
        )
    ],

    "MAX_SINGLE_POSITION": [

        round(
            max_position,
            2
        )
    ],

    "RISK_SCORE": [
        risk_score
    ]
})

# =========================================================
# PORTFOLIO RISK REPORT
# =========================================================

risk_report = portfolio.copy()

risk_report["WEIGHT_RANK"] = (

    risk_report["FINAL_WEIGHT"]

    .rank(
        ascending=False
    )
)

# =========================================================
# SAVE FILES
# =========================================================

risk_metrics.to_csv(

    RISK_METRICS_FILE,

    index=False
)

risk_report.to_csv(

    RISK_REPORT_FILE,

    index=False
)

correlation_matrix.to_csv(
    CORRELATION_FILE
)

# =========================================================
# OUTPUT
# =========================================================

print("\n✅ Risk Engine Completed")

print(
    f"\n📁 Risk Metrics:\n"
    f"{RISK_METRICS_FILE}"
)

print(
    f"\n📁 Portfolio Risk Report:\n"
    f"{RISK_REPORT_FILE}"
)

print(
    f"\n📁 Correlation Matrix:\n"
    f"{CORRELATION_FILE}"
)

print("\n🧠 INSTITUTIONAL RISK SUMMARY:\n")

print(risk_metrics.T)

print("\n🏦 SECTOR EXPOSURE:\n")

print(sector_exposure)