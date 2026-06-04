import pandas as pd
import numpy as np
import yfinance as yf
from pathlib import Path

# =========================================================
# FILES
# =========================================================

ROOT = Path(__file__).resolve().parent.parent

OUTPUT_FILE = (
    ROOT
    / "data"
    / "market_regime.csv"
)

# =========================================================
# SETTINGS
# =========================================================

INDEX_SYMBOL = "^NSEI"

FAST_MA = 50
SLOW_MA = 200

VOL_LOOKBACK = 20

LOW_VOL_THRESHOLD = 0.15
HIGH_VOL_THRESHOLD = 0.20

# =========================================================
# DOWNLOAD INDEX
# =========================================================

print("\n📡 Downloading NIFTY Data...")

data = yf.download(
    INDEX_SYMBOL,
    period="3y",
    auto_adjust=True,
    progress=False
)

if data.empty:
    raise ValueError(
        "Unable to download NIFTY data."
    )

# =========================================================
# CLOSE SERIES
# =========================================================

if isinstance(data.columns, pd.MultiIndex):
    close = data["Close"].iloc[:, 0]
else:
    close = data["Close"]

df = pd.DataFrame()

df["Close"] = close

# =========================================================
# MOVING AVERAGES
# =========================================================

df["MA50"] = (
    df["Close"]
    .rolling(FAST_MA)
    .mean()
)

df["MA200"] = (
    df["Close"]
    .rolling(SLOW_MA)
    .mean()
)

# =========================================================
# RETURNS
# =========================================================

returns = df["Close"].pct_change()

# =========================================================
# VOLATILITY
# =========================================================

df["VOLATILITY"] = (
    returns
    .rolling(VOL_LOOKBACK)
    .std()
    * np.sqrt(252)
)

# =========================================================
# TREND STRENGTH
# =========================================================

df["TREND_STRENGTH"] = (
    (
        df["MA50"]
        - df["MA200"]
    )
    /
    df["MA200"]
) * 100

# =========================================================
# REGIME CLASSIFICATION
# =========================================================

def classify(row):

    if pd.isna(row["MA200"]):
        return "UNKNOWN"

    trend = row["TREND_STRENGTH"]

    high_vol = (
        row["VOLATILITY"]
        >= HIGH_VOL_THRESHOLD
    )

    if high_vol:
        return "HIGH_VOLATILITY"

    # Strong Bull

    if (
        row["Close"] > row["MA50"]
        and row["MA50"] > row["MA200"]
        and trend > 5
    ):
        return "STRONG_BULL"

    # Bull

    if (
        row["Close"] > row["MA50"]
        and row["MA50"] > row["MA200"]
    ):
        return "BULL"

    # Strong Bear

    if (
        row["Close"] < row["MA50"]
        and row["MA50"] < row["MA200"]
        and trend < -5
    ):
        return "STRONG_BEAR"

    # Bear

    if (
        row["Close"] < row["MA50"]
        and row["MA50"] < row["MA200"]
    ):
        return "BEAR"

    return "SIDEWAYS"


df["REGIME"] = df.apply(
    classify,
    axis=1
)

# =========================================================
# VOLATILITY REGIME
# =========================================================

def vol_bucket(vol):

    if vol < LOW_VOL_THRESHOLD:
        return "LOW_VOL"

    elif vol < HIGH_VOL_THRESHOLD:
        return "NORMAL_VOL"

    return "HIGH_VOL"


df["VOL_REGIME"] = (
    df["VOLATILITY"]
    .apply(vol_bucket)
)

# =========================================================
# LATEST
# =========================================================

latest = df.iloc[-1]

# =========================================================
# MARKET SCORE
# =========================================================

market_score = 0

# Price vs MA50

market_score += np.clip(

    (
        latest["Close"]
        /
        latest["MA50"]
        - 1
    ) * 100,

    -20,
    20
)

# MA50 vs MA200

market_score += np.clip(

    (
        latest["MA50"]
        /
        latest["MA200"]
        - 1
    ) * 100,

    -20,
    20
)

# Volatility penalty

market_score -= (
    latest["VOLATILITY"]
    * 50
)

market_score = round(
    market_score,
    2
)

# =========================================================
# RISK REGIME
# =========================================================

if market_score > 10:

    risk_regime = "RISK_ON"

elif market_score < -10:

    risk_regime = "RISK_OFF"

else:

    risk_regime = "NEUTRAL"

# =========================================================
# OUTPUT
# =========================================================

regime_df = pd.DataFrame({

    "DATE": [
        df.index[-1]
    ],

    "CLOSE": [
        round(
            latest["Close"],
            2
        )
    ],

    "MA50": [
        round(
            latest["MA50"],
            2
        )
    ],

    "MA200": [
        round(
            latest["MA200"],
            2
        )
    ],

    "TREND_STRENGTH_%": [
        round(
            latest["TREND_STRENGTH"],
            2
        )
    ],

    "VOLATILITY": [
        round(
            latest["VOLATILITY"],
            4
        )
    ],

    "VOL_REGIME": [
        latest["VOL_REGIME"]
    ],

    "REGIME": [
        latest["REGIME"]
    ],

    "MARKET_SCORE": [
        market_score
    ],

    "RISK_REGIME": [
        risk_regime
    ]
})

# =========================================================
# SAVE
# =========================================================

regime_df.to_csv(
    OUTPUT_FILE,
    index=False
)

# =========================================================
# REPORT
# =========================================================

print("\n✅ Regime Detection Complete")

print("\n📁 Saved:")

print(OUTPUT_FILE)

print("\n🏆 Current Market Regime:\n")

print(regime_df)

print(
    f"\nMarket State : {latest['REGIME']}"
)

print(
    f"Risk Regime  : {risk_regime}"
)

print(
    f"Market Score : {market_score}"
)
