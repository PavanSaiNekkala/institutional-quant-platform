import time
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf
from institutional_quant.utils.data_io import (
    save_parquet,
    load_parquet
)

# =========================================================
# CONFIG
# =========================================================

BENCHMARK = "^NSEI"

PERIOD = "1y"

SHORT_MA = 50

LONG_MA = 200

VOL_WINDOW = 20

MAX_RETRIES = 3

RETRY_DELAY = 5

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[1]

OUTPUT_DIR = ROOT_DIR / "data"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "market_regime.parquet"
)

# =========================================================
# DOWNLOAD MARKET DATA
# =========================================================

print("\n📥 Downloading Market Data...")

df = pd.DataFrame()

for attempt in range(MAX_RETRIES):

    try:

        df = yf.download(

            BENCHMARK,

            period=PERIOD,

            auto_adjust=True,

            progress=False,

            threads=False
        )

        # ---------------------------------------------
        # FIX MULTIINDEX
        # ---------------------------------------------

        if isinstance(
            df.columns,
            pd.MultiIndex
        ):

            df.columns = (
                df.columns.get_level_values(0)
            )

        # ---------------------------------------------
        # VALIDATE DATA
        # ---------------------------------------------

        if not df.empty:

            break

        print(
            f"\n⚠ Empty dataframe received "
            f"(Attempt {attempt + 1})"
        )

    except Exception as e:

        print(
            f"\n⚠ Download failed "
            f"(Attempt {attempt + 1})"
        )

        print(e)

    time.sleep(RETRY_DELAY)

# =========================================================
# FINAL VALIDATION
# =========================================================

if df.empty:

    raise ValueError(
        f"\n❌ Failed to download data for "
        f"{BENCHMARK}"
    )

if "Close" not in df.columns:

    raise ValueError(
        "\n❌ 'Close' column missing "
        "from downloaded data."
    )

# =========================================================
# CLOSE
# =========================================================

close = df["Close"].dropna()

if close.empty:

    raise ValueError(
        "\n❌ Close prices are empty."
    )

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
# HANDLE NaN VALUES
# =========================================================

if pd.isna(latest_short):

    latest_short = latest_close

if pd.isna(latest_long):

    latest_long = latest_close

if pd.isna(latest_vol):

    latest_vol = 0.20

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

    "NIFTY_CLOSE": [round(float(latest_close), 2)],

    "MA_50": [round(float(latest_short), 2)],

    "MA_200": [round(float(latest_long), 2)],

    "ANNUALIZED_VOL": [round(float(latest_vol), 4)],

    "MARKET_SCORE": [market_score]
})

# =========================================================
# SAVE
# =========================================================

save_parquet(
    output,
    OUTPUT_FILE
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
