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
    / "optimised_portfolio.csv"
)

OUTPUT_SUMMARY = (
    ROOT
    / "data"
    / "portfolio_risk_summary.csv"
)

OUTPUT_ALERTS = (
    ROOT
    / "data"
    / "portfolio_alerts.csv"
)

# =========================================================
# SETTINGS
# =========================================================

LOOKBACK_DAYS = 252

MAX_POSITION = 0.10
MAX_TOP5 = 0.50
MAX_SECTOR = 0.25

# =========================================================
# LOAD
# =========================================================

print("\n📥 Loading Portfolio...")

df = pd.read_csv(PORTFOLIO_FILE)

# =========================================================
# VALIDATION
# =========================================================

required_cols = [
    "Symbol",
    "FINAL_WEIGHT"
]

missing = [
    c for c in required_cols
    if c not in df.columns
]

if missing:

    raise ValueError(
        f"Missing columns: {missing}"
    )

# =========================================================
# SYMBOLS
# =========================================================

symbols = []

for sym in df["Symbol"]:

    sym = str(sym).upper().strip()

    if not sym.endswith(".NS"):

        sym += ".NS"

    symbols.append(sym)

# =========================================================
# DOWNLOAD DATA
# =========================================================

print(
    f"\n📡 Downloading {len(symbols)} stocks..."
)

prices = yf.download(
    tickers=symbols,
    period="2y",
    auto_adjust=True,
    progress=False
)

if prices.empty:

    raise ValueError(
        "No market data downloaded."
    )

# =========================================================
# CLOSE PRICES
# =========================================================

if isinstance(
    prices.columns,
    pd.MultiIndex
):

    close_prices = prices["Close"]

else:

    close_prices = prices

# =========================================================
# RETURNS
# =========================================================

returns = close_prices.pct_change(
    fill_method=None
).dropna()

# =========================================================
# PORTFOLIO RETURNS
# =========================================================

weights = (
    df["FINAL_WEIGHT"]
    .values
)

portfolio_returns = (
    returns
    .dot(weights)
)

# =========================================================
# VOLATILITY
# =========================================================

annual_vol = (

    portfolio_returns.std()

    * np.sqrt(252)

    * 100
)

# =========================================================
# SHARPE
# =========================================================

sharpe = (

    portfolio_returns.mean()

    * 252

) / (

    portfolio_returns.std()

    * np.sqrt(252)

)

# =========================================================
# VAR
# =========================================================

var95 = (
    np.percentile(
        portfolio_returns,
        5
    )
    * 100
)

cvar95 = (

    portfolio_returns[
        portfolio_returns
        <= np.percentile(
            portfolio_returns,
            5
        )
    ]
    .mean()

    * 100
)

# =========================================================
# DRAWDOWN
# =========================================================

equity_curve = (

    1 + portfolio_returns

).cumprod()

rolling_max = (
    equity_curve.cummax()
)

drawdown = (

    equity_curve
    /
    rolling_max

    - 1

)

max_dd = (
    drawdown.min()
    * 100
)

current_dd = (
    drawdown.iloc[-1]
    * 100
)

# =========================================================
# CONCENTRATION
# =========================================================

largest_position = (
    df["FINAL_WEIGHT"]
    .max()
)

top5 = (

    df["FINAL_WEIGHT"]

    .nlargest(5)

    .sum()
)

top10 = (

    df["FINAL_WEIGHT"]

    .nlargest(10)

    .sum()
)

# =========================================================
# ALERTS
# =========================================================

alerts = []

if largest_position > MAX_POSITION:

    alerts.append(
        "POSITION_TOO_LARGE"
    )

if top5 > MAX_TOP5:

    alerts.append(
        "TOP5_CONCENTRATION"
    )

if annual_vol > 30:

    alerts.append(
        "HIGH_VOLATILITY"
    )

if max_dd < -25:

    alerts.append(
        "HIGH_DRAWDOWN"
    )

# =========================================================
# HEALTH SCORE
# =========================================================

health = 100

health -= max(
    0,
    annual_vol - 20
)

health -= abs(
    min(
        0,
        max_dd
    )
) * 0.5

health -= max(
    0,
    (largest_position * 100) - 10
)

health = max(
    0,
    round(
        health,
        2
    )
)

# =========================================================
# SUMMARY
# =========================================================

summary = pd.DataFrame({

    "Metric": [

        "Portfolio Volatility",

        "Sharpe",

        "VaR95",

        "CVaR95",

        "Current Drawdown",

        "Max Drawdown",

        "Largest Position",

        "Top5 Exposure",

        "Top10 Exposure",

        "Health Score"
    ],

    "Value": [

        round(annual_vol,2),

        round(sharpe,2),

        round(var95,2),

        round(cvar95,2),

        round(current_dd,2),

        round(max_dd,2),

        round(
            largest_position*100,
            2
        ),

        round(
            top5*100,
            2
        ),

        round(
            top10*100,
            2
        ),

        health
    ]
})

# =========================================================
# SAVE
# =========================================================

summary.to_csv(
    OUTPUT_SUMMARY,
    index=False
)

pd.DataFrame({

    "ALERT": alerts

}).to_csv(

    OUTPUT_ALERTS,
    index=False
)

# =========================================================
# REPORT
# =========================================================

print(
    "\n✅ Portfolio Monitor Complete"
)

print(
    "\n📁 Risk Summary:"
)

print(
    OUTPUT_SUMMARY
)

print(
    "\n📁 Alerts:"
)

print(
    OUTPUT_ALERTS
)

print(
    "\n🏆 Portfolio Health Score:",
    health
)

if len(alerts):

    print(
        "\n⚠ Alerts:"
    )

    for a in alerts:

        print(
            "-",
            a
        )

else:

    print(
        "\n✅ No Risk Alerts"
    )
