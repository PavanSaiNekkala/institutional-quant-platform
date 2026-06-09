from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

# =========================================================
# CONFIG
# =========================================================

BENCHMARK = "^NSEI"

LOOKBACK_PERIOD = "1y"

TRADING_DAYS = 252

CONFIDENCE_LEVEL = 0.95

RISK_FREE_RATE = 0.06

PORTFOLIO_VALUE = 1000000

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[1]

PORTFOLIO_FILE = ROOT_DIR / "data" / "portfolio_allocation.csv"

RISK_REPORT_FILE = ROOT_DIR / "data" / "portfolio_risk_report.csv"

CORRELATION_FILE = ROOT_DIR / "data" / "correlation_matrix.csv"

RISK_METRICS_FILE = ROOT_DIR / "data" / "risk_metrics.csv"


# =========================================================
# LOAD PORTFOLIO
# =========================================================

print("\n📥 Loading Portfolio...")

portfolio = pd.read_csv(PORTFOLIO_FILE)

print("✅ Portfolio Loaded")

# =========================================================
# DETECT WEIGHT COLUMN
# =========================================================

portfolio.columns = portfolio.columns.astype(str).str.strip()

weight_candidates = ["FINAL_WEIGHT", "WEIGHT", "PORTFOLIO_WEIGHT", "OPTIMAL_WEIGHT", "ALLOC_WEIGHT"]

weight_col = None

for col in portfolio.columns:
    if col.strip().upper() in weight_candidates:
        weight_col = col

        break

if weight_col is None:
    raise Exception(
        f"\n❌ Weight column not found.\nAvailable columns:\n{portfolio.columns.tolist()}"
    )

print(f"\n✅ Using Weight Column: {weight_col}")

portfolio.columns = portfolio.columns.astype(str).str.strip()

print("\n📊 Portfolio Columns:")
print(portfolio.columns.tolist())

if portfolio.empty:
    raise Exception("\n❌ Portfolio file is empty")

print("✅ Portfolio Loaded")

if "Symbol" not in portfolio.columns:
    raise Exception(
        f"\n❌ Symbol column missing.\nAvailable columns:\n{portfolio.columns.tolist()}"
    )

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

portfolio.columns = [str(c).strip() for c in portfolio.columns]

if weight_col is None:
    raise Exception(
        f"\n❌ Weight column not found.\nAvailable columns:\n{portfolio.columns.tolist()}"
    )

print(f"\n✅ Using Weight Column: {weight_col}")

weights = portfolio[weight_col].astype(float)

if weights.max() > 1:
    weights = weights / 100

weights = weights.values

weight_sum = weights.sum()

if abs(weight_sum - 1) > 0.05:
    print(f"\n⚠️ WARNING: Portfolio weights sum to {weight_sum:.3f}")

tickers = [f"{symbol}.NS" for symbol in symbols]

tickers.append(BENCHMARK)

# =========================================================
# DOWNLOAD DATA
# =========================================================

print("\n📥 Downloading Market Data...")

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
# BENCHMARK RETURNS
# =========================================================

if BENCHMARK not in returns.columns:
    raise Exception(f"Benchmark {BENCHMARK} not downloaded")
benchmark_returns = returns[BENCHMARK]
# =========================================================
# PORTFOLIO RETURNS
# =========================================================

portfolio_returns = pd.Series(0, index=returns.index, dtype=float)

for i, symbol in enumerate(symbols):
    ticker = f"{symbol}.NS"

    if ticker in returns.columns:
        portfolio_returns += returns[ticker] * weights[i]

# =========================================================
# PORTFOLIO VOLATILITY
# =========================================================

portfolio_volatility = portfolio_returns.std() * np.sqrt(TRADING_DAYS)

# =========================================================
# PORTFOLIO CAGR
# =========================================================

equity_curve = (1 + portfolio_returns).cumprod()

years = len(portfolio_returns) / TRADING_DAYS

if len(portfolio_returns) < 20:
    raise Exception("Insufficient history for risk analysis")

portfolio_cagr = equity_curve.iloc[-1] ** (1 / years) - 1

# =========================================================
# SHARPE RATIO
# =========================================================

if portfolio_volatility > 0:
    sharpe_ratio = (portfolio_cagr - RISK_FREE_RATE) / portfolio_volatility

else:
    sharpe_ratio = 0

# =========================================================
# MAX DRAWDOWN
# =========================================================

rolling_max = equity_curve.cummax()

drawdown = equity_curve / rolling_max - 1

max_drawdown = drawdown.min()

# =========================================================
# VAR (95%)
# =========================================================

var_95 = np.percentile(portfolio_returns, (1 - CONFIDENCE_LEVEL) * 100)

# =========================================================
# CVAR (95%)
# =========================================================

cvar_95 = portfolio_returns[portfolio_returns <= var_95].mean()


common_idx = portfolio_returns.index.intersection(benchmark_returns.index)

portfolio_returns = portfolio_returns.loc[common_idx]
benchmark_returns = benchmark_returns.loc[common_idx]

# =========================================================
# BETA CALCULATION
# =========================================================

covariance = np.cov(portfolio_returns, benchmark_returns)[0][1]

benchmark_variance = np.var(benchmark_returns)

if benchmark_variance > 0:
    beta = covariance / benchmark_variance

else:
    beta = 0

# =========================================================
# CORRELATION MATRIX
# =========================================================

stock_returns = returns.drop(columns=[BENCHMARK], errors="ignore")

correlation_matrix = stock_returns.corr()

corr = correlation_matrix.copy()

np.fill_diagonal(corr.values, np.nan)

avg_correlation = np.nanmean(corr.values)

if np.isnan(avg_correlation):
    avg_correlation = 0

diversification_score = max(0, min(100, 100 * (1 - avg_correlation)))

var_rupees = PORTFOLIO_VALUE * abs(var_95)

# =========================================================
# SECTOR EXPOSURE
# =========================================================

if "Sector" in portfolio.columns:
    sector_exposure = portfolio.groupby("Sector")[weight_col].sum().sort_values(ascending=False)

else:
    sector_exposure = pd.Series({"UNKNOWN": portfolio[weight_col].sum()})

# =========================================================
# POSITION CONCENTRATION
# =========================================================

max_position = portfolio[weight_col].max()

top5_concentration = portfolio[weight_col].nlargest(5).sum()

if top5_concentration > 1:
    top5_concentration /= 100

# =========================================================
# WIN RATE
# =========================================================

win_rate = (portfolio_returns > 0).mean() * 100

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
concentration_check = top5_concentration

if concentration_check > 1:
    concentration_check /= 100

if concentration_check > 0.60:
    risk_score -= 15

risk_score = max(risk_score, 0)

if risk_score >= 90:
    risk_grade = "A"

elif risk_score >= 75:
    risk_grade = "B"

elif risk_score >= 60:
    risk_grade = "C"

else:
    risk_grade = "D"

# =========================================================
# SORTINO RATIO
# =========================================================

downside = portfolio_returns[portfolio_returns < 0]

downside_vol = downside.std() * np.sqrt(TRADING_DAYS)

sortino_ratio = (portfolio_cagr - RISK_FREE_RATE) / downside_vol if downside_vol > 0 else 0

active_returns = portfolio_returns - benchmark_returns

active_return = active_returns.mean() * TRADING_DAYS * 100

tracking_error = active_returns.std() * np.sqrt(TRADING_DAYS)

information_ratio = (active_returns.mean() * 252) / tracking_error if tracking_error > 0 else 0

# =========================================================
# RISK METRICS DATAFRAME
# =========================================================

risk_metrics = pd.DataFrame(
    {
        "PORTFOLIO_CAGR": [round(portfolio_cagr * 100, 2)],
        "PORTFOLIO_VOLATILITY": [round(portfolio_volatility * 100, 2)],
        "SHARPE_RATIO": [round(sharpe_ratio, 2)],
        "ACTIVE_RETURN": [round(active_return, 2)],
        "SORTINO_RATIO": [round(sortino_ratio, 2)],
        "DIVERSIFICATION_SCORE": [round(diversification_score, 2)],
        "RISK_GRADE": [risk_grade],
        "MAX_DRAWDOWN": [round(max_drawdown * 100, 2)],
        "BETA": [round(beta, 2)],
        "VAR_95": [round(var_95 * 100, 2)],
        "CVAR_95": [round(cvar_95 * 100, 2)],
        "WIN_RATE": [round(win_rate, 2)],
        "VAR_95_RS": [round(var_rupees, 0)],
        "TRACKING_ERROR": [round(tracking_error * 100, 2)],
        "INFORMATION_RATIO": [round(information_ratio, 2)],
        "AVG_CORRELATION": [round(avg_correlation, 2)],
        "TOP_5_CONCENTRATION": [round(top5_concentration, 2)],
        "MAX_SINGLE_POSITION": [round(max_position, 2)],
        "RISK_SCORE": [risk_score],
    }
)

# =========================================================
# PORTFOLIO RISK REPORT
# =========================================================

risk_report = portfolio.copy()

risk_report["WEIGHT_RANK"] = risk_report[weight_col].rank(ascending=False)

# =========================================================
# SAVE FILES
# =========================================================

EQUITY_CURVE_FILE = ROOT_DIR / "data" / "risk_equity_curve.csv"

equity_curve.to_csv(EQUITY_CURVE_FILE)

risk_metrics.to_csv(RISK_METRICS_FILE, index=False)

risk_report.to_csv(RISK_REPORT_FILE, index=False)

correlation_matrix.to_csv(CORRELATION_FILE)

# =========================================================
# OUTPUT
# =========================================================

print("\n✅ Risk Engine Completed")

print(f"\n📁 Risk Metrics:\n{RISK_METRICS_FILE}")

print(f"\n📁 Portfolio Risk Report:\n{RISK_REPORT_FILE}")

print(f"\n📁 Correlation Matrix:\n{CORRELATION_FILE}")

print("\n🧠 INSTITUTIONAL RISK SUMMARY:\n")

print(risk_metrics.T)

print("\n🏦 SECTOR EXPOSURE:\n")

print(sector_exposure)
