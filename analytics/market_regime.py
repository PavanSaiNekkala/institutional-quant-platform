import pandas as pd
import numpy as np
import yfinance as yf

from pathlib import Path

# =========================================================
# CONFIG
# =========================================================

BENCHMARK = "^NSEI"

PERIOD = "1y"

SHORT_MA = 50

LONG_MA = 200

VOL_WINDOW = 20

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[1]

OUTPUT_FILE = (
    ROOT_DIR
    / "data"
    / "market_regime.csv"
)

# =========================================================
# DOWNLOAD MARKET DATA
# =========================================================

print("\n📥 Downloading Market Data...")

df = yf.download(

    BENCHMARK,

    period=PERIOD,

    auto_adjust=True,

    progress=False,

    threads=False
)

# =========================================================
# FIX MULTIINDEX
# =========================================================

if isinstance(
    df.columns,
    pd.MultiIndex
):

    df.columns = (
        df.columns.get_level_values(0)
    )

# =========================================================
# CLOSE
# =========================================================

close = df["Close"].dropna()

# =========================================================
# RETURNS
# =========================================================

returns = close.pct_change()

# =========================================================
# MOVING AVERAGES
# =========================================================

ma_short = (
    close
    .rolling(SHORT_MA)
    .mean()
)

ma_long = (
    close
    .rolling(LONG_MA)
    .mean()
)

# =========================================================
# VOLATILITY
# =========================================================

volatility = (

    returns

    .rolling(VOL_WINDOW)

    .std()

    * np.sqrt(252)
)

# =========================================================
# LATEST VALUES
# =========================================================

latest_close = close.iloc[-1]

latest_short = ma_short.iloc[-1]

latest_long = ma_long.iloc[-1]

latest_vol = volatility.iloc[-1]

# =========================================================
# TREND DETECTION
# =========================================================

if latest_short > latest_long:

    trend_regime = "BULLISH"

else:

    trend_regime = "BEARISH"

# =========================================================
# VOLATILITY REGIME
# =========================================================

if latest_vol < 0.20:

    vol_regime = "LOW_VOL"

elif latest_vol < 0.35:

    vol_regime = "NORMAL_VOL"

else:

    vol_regime = "HIGH_VOL"

# =========================================================
# FINAL MARKET REGIME
# =========================================================

if (

    trend_regime == "BULLISH"

    and

    vol_regime == "LOW_VOL"
):

    market_regime = "RISK_ON"

elif (

    trend_regime == "BULLISH"

    and

    vol_regime == "NORMAL_VOL"
):

    market_regime = "TRENDING_BULL"

elif (

    trend_regime == "BEARISH"

    and

    vol_regime == "HIGH_VOL"
):

    market_regime = "RISK_OFF"

else:

    market_regime = "NEUTRAL"

# =========================================================
# MARKET SCORE
# =========================================================

market_score = 0

# Trend Weight
if trend_regime == "BULLISH":

    market_score += 60

else:

    market_score -= 60

# Volatility Weight
if vol_regime == "LOW_VOL":

    market_score += 40

elif vol_regime == "NORMAL_VOL":

    market_score += 10

else:

    market_score -= 40

# =========================================================
# OUTPUT DATAFRAME
# =========================================================

output = pd.DataFrame({

    "MARKET_REGIME": [market_regime],

    "TREND_REGIME": [trend_regime],

    "VOLATILITY_REGIME": [vol_regime],

    "NIFTY_CLOSE": [round(latest_close, 2)],

    "MA_50": [round(latest_short, 2)],

    "MA_200": [round(latest_long, 2)],

    "ANNUALIZED_VOL": [round(latest_vol, 4)],

    "MARKET_SCORE": [market_score]
})

# =========================================================
# SAVE
# =========================================================

output.to_csv(

    OUTPUT_FILE,

    index=False
)

# =========================================================
# OUTPUT
# =========================================================

print("\n✅ Market Regime Generated")

print(
    f"\n📁 Saved to:\n"
    f"{OUTPUT_FILE}"
)

print("\n🧠 CURRENT MARKET REGIME:\n")

print(output)