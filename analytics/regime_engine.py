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
HIGH_VOL_THRESHOLD = 0.25

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
# VOLATILITY
# =========================================================

returns = df["Close"].pct_change()

df["VOLATILITY"] = (

    returns

    .rolling(VOL_LOOKBACK)

    .std()

    *

    np.sqrt(252)
)

# =========================================================
# REGIME CLASSIFICATION
# =========================================================

def classify(row):

    if pd.isna(row["MA200"]):
        return "UNKNOWN"

    bull = (

        row["Close"] > row["MA50"]

        and

        row["MA50"] > row["MA200"]
    )

    bear = (

        row["Close"] < row["MA50"]

        and

        row["MA50"] < row["MA200"]
    )

    high_vol = (
        row["VOLATILITY"]
        > HIGH_VOL_THRESHOLD
    )

    if high_vol:
        return "HIGH_VOLATILITY"

    if bull:
        return "BULL"

    if bear:
        return "BEAR"

    return "SIDEWAYS"


df["REGIME"] = df.apply(
    classify,
    axis=1
)

# =========================================================
# LATEST REGIME
# =========================================================

latest = df.iloc[-1]

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

    "VOLATILITY": [
        round(
            latest["VOLATILITY"],
            4
        )
    ],

    "REGIME": [
        latest["REGIME"]
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

print(
    OUTPUT_FILE
)

print("\n🏆 Current Market Regime:\n")

print(regime_df)

print(
    f"\nMarket State: {latest['REGIME']}"
)