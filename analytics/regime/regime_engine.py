import pandas as pd
import numpy as np
import yfinance as yf
from pathlib import Path

import time

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT / "data"

OUTPUT_FILE = (
    DATA_DIR
    / "market_regime.csv"
)

BREADTH_FILE = (
    ROOT
    / "data"
    / "processed"
    / "market_breadth.csv"
)

breadth = pd.read_csv(
    BREADTH_FILE
)

breadth_score = float(
    breadth["BREADTH_SCORE"].iloc[0]
)

# =========================================================
# SETTINGS
# =========================================================

INDEX_SYMBOL = "^NSEI"

FAST_MA = 50
SLOW_MA = 200

VOL_LOOKBACK = 20

LOW_VOL_THRESHOLD = 0.15
HIGH_VOL_THRESHOLD = 0.25

MOM_1M = 21
MOM_3M = 63
MOM_6M = 126

# =========================================================
# DOWNLOAD DATA
# =========================================================

print("\n📡 Downloading NIFTY Data...")

data = pd.DataFrame()

for attempt in range(3):

    try:

        print(
            f"Attempt {attempt + 1}/3"
        )

        data = yf.download(
            INDEX_SYMBOL,
            period="3y",
            auto_adjust=True,
            progress=False,
            threads=False
        )

        if not data.empty:

            print(
                "✅ Download successful"
            )

            break

    except Exception as e:

        print(
            f"Attempt {attempt + 1} failed: {e}"
        )

    time.sleep(10)

if data.empty:

    print(
        "⚠ Yahoo Finance unavailable."
    )

    if OUTPUT_FILE.exists():

        print(
            "⚠ Using previous market regime."
        )

        raise SystemExit(0)

    raise ValueError(
        "Unable to download NIFTY data."
    )

# =========================================================
# CLOSE SERIES
# =========================================================

if isinstance(
    data.columns,
    pd.MultiIndex
):

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
# MOMENTUM
# =========================================================

mom_1m = (

    close.iloc[-1]

    /

    close.iloc[-MOM_1M]

    - 1

) * 100

mom_3m = (

    close.iloc[-1]

    /

    close.iloc[-MOM_3M]

    - 1

) * 100

mom_6m = (

    close.iloc[-1]

    /

    close.iloc[-MOM_6M]

    - 1

) * 100

momentum_score = (

      mom_1m * 0.40

    + mom_3m * 0.30

    + mom_6m * 0.30

)

# =========================================================
# DRAWDOWN
# =========================================================

rolling_high = (

    close

    .rolling(252)

    .max()

)

drawdown = (

    close

    /

    rolling_high

    - 1

) * 100

current_drawdown = (

    drawdown.iloc[-1]

)

# =========================================================
# LIQUIDITY
# =========================================================

liquidity_ratio = np.nan

liquidity_regime = "UNKNOWN"

try:

    if isinstance(
        data.columns,
        pd.MultiIndex
    ):

        volume = data["Volume"].iloc[:, 0]

    else:

        volume = data["Volume"]

    avg_volume = (

        volume

        .rolling(20)

        .mean()

    )

    liquidity_ratio = (

        volume.iloc[-1]

        /

        avg_volume.iloc[-1]

    )

    if liquidity_ratio > 1.20:

        liquidity_regime = "HIGH"

    elif liquidity_ratio > 0.80:

        liquidity_regime = "NORMAL"

    else:

        liquidity_regime = "LOW"

except:

    liquidity_ratio = np.nan

    liquidity_regime = "UNKNOWN"

# =========================================================
# VOL REGIME
# =========================================================

latest_vol = (

    df["VOLATILITY"]

    .iloc[-1]

)

if latest_vol < LOW_VOL_THRESHOLD:

    vol_regime = "LOW_VOL"

elif latest_vol < HIGH_VOL_THRESHOLD:

    vol_regime = "NORMAL_VOL"

else:

    vol_regime = "HIGH_VOL"

# =========================================================
# MARKET SCORE
# =========================================================

latest = df.iloc[-1]

# -----------------------------------------
# TREND COMPONENT (40%)
# -----------------------------------------

trend_component = np.clip(

    latest["TREND_STRENGTH"] * 2,

    -40,

    40

)

# -----------------------------------------
# BREADTH COMPONENT (25%)
# -----------------------------------------

breadth_component = (

    breadth_score

    * 0.25

)

# -----------------------------------------
# MOMENTUM COMPONENT (20%)
# -----------------------------------------

momentum_component = np.clip(

    momentum_score,

    -20,

    20

)

# -----------------------------------------
# VOLATILITY COMPONENT (15%)
# -----------------------------------------

vol_component = max(

    0,

    15

    -

    latest_vol * 50

)

# -----------------------------------------
# LIQUIDITY BONUS
# -----------------------------------------

liquidity_bonus = 0

if liquidity_regime == "HIGH":

    liquidity_bonus = 5

elif liquidity_regime == "LOW":

    liquidity_bonus = -5

# -----------------------------------------
# FINAL SCORE
# -----------------------------------------

market_score = 50

market_score += trend_component * 0.5
market_score += momentum_component * 0.5
market_score += (breadth_score - 50) * 0.5
market_score += (vol_component - 7.5)
market_score += liquidity_bonus

market_score = round(
    np.clip(
        market_score,
        0,
        100
    ),
    2
)

print("\n===== COMPONENTS =====")

print(
    f"Trend Component     : {trend_component:.2f}"
)

print(
    f"Breadth Component   : {breadth_component:.2f}"
)

print(
    f"Momentum Component  : {momentum_component:.2f}"
)

print(
    f"Volatility Component: {vol_component:.2f}"
)

print(
    f"Liquidity Bonus     : {liquidity_bonus:.2f}"
)

print(
    f"Market Score        : {market_score:.2f}"
)

# =========================================================
# MARKET REGIME
# =========================================================

if market_score >= 70:

    market_regime = "STRONG_BULL"

elif market_score >= 55:

    market_regime = "BULL"

elif market_score >= 35:

    market_regime = "SIDEWAYS"

elif market_score >= 20:

    market_regime = "BEAR"

else:

    market_regime = "STRONG_BEAR"

# =========================================================
# RISK REGIME
# =========================================================

if market_score >= 60:

    risk_regime = "RISK_ON"

elif market_score >= 30:

    risk_regime = "NEUTRAL"

else:

    risk_regime = "RISK_OFF"

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

    "TREND_STRENGTH_PCT": [
        round(
            latest["TREND_STRENGTH"],
            2
        )
    ],

    "VOLATILITY": [
        round(
            latest_vol,
            4
        )
    ],

    "VOL_REGIME": [
        vol_regime
    ],

    "BREADTH_SCORE": [
        round(
            breadth_score,
            2
        )
    ],

    "MOMENTUM_1M": [
        round(
            mom_1m,
            2
        )
    ],

    "MOMENTUM_3M": [
        round(
            mom_3m,
            2
        )
    ],

    "MOMENTUM_6M": [
        round(
            mom_6m,
            2
        )
    ],

    "TREND_COMPONENT": [
        round(
            trend_component,
            2
        )
    ],

    "BREADTH_COMPONENT": [
        round(
            breadth_component,
            2
        )
    ],

    "MOMENTUM_COMPONENT": [
        round(
            momentum_component,
            2
        )
    ],

    "VOLATILITY_COMPONENT": [
        round(
            vol_component,
            2
        )
    ],

    "MOMENTUM_SCORE": [
        round(
            momentum_score,
            2
        )
    ],

    "CURRENT_DRAWDOWN": [
        round(
            current_drawdown,
            2
        )
    ],

    "LIQUIDITY_RATIO": [
        round(
            liquidity_ratio,
            2
        )
        if pd.notna(liquidity_ratio)
        else np.nan
    ],

    "LIQUIDITY_REGIME": [
        liquidity_regime
    ],

    "MARKET_SCORE": [
        market_score
    ],

    "MARKET_REGIME": [
        market_regime
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

print("\n✅ Market Regime Engine Complete")

print(
    f"\n📁 Saved:\n{OUTPUT_FILE}"
)

print("\n🏆 CURRENT REGIME\n")

print(regime_df)

print(
    f"\nMarket Regime : {market_regime}"
)

print(
    f"Risk Regime   : {risk_regime}"
)

print(
    f"Breadth Score : {round(breadth_score,2)}"
)

print(
    f"Market Score  : {market_score}"
)
