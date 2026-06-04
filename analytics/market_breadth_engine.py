import pandas as pd
import numpy as np
import yfinance as yf
from pathlib import Path

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    ROOT
    / "data"
    / "factor_model_rankings.csv"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "market_breadth.csv"
)

# =========================================================
# LOAD UNIVERSE
# =========================================================

print("\n📥 Loading Universe...")

if not INPUT_FILE.exists():

    raise FileNotFoundError(
        f"Missing: {INPUT_FILE}"
    )

universe = pd.read_csv(
    INPUT_FILE
)

# =========================================================
# SYMBOL COLUMN
# =========================================================

if "YF_SYMBOL" in universe.columns:

    symbols = (
        universe["YF_SYMBOL"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

elif "Symbol" in universe.columns:

    symbols = (
        universe["Symbol"]
        .dropna()
        .astype(str)
        .str.upper()
        .str.replace(
            ".NS",
            "",
            regex=False
        )
        + ".NS"
    ).unique().tolist()

else:

    raise ValueError(
        "No Symbol column found."
    )

# =========================================================
# LIMIT CHECK
# =========================================================

symbols = [
    s
    for s in symbols
    if isinstance(s, str)
]

print(
    f"\n📊 Universe Size: {len(symbols)}"
)

if len(symbols) == 0:

    raise ValueError(
        "No valid symbols found."
    )

# =========================================================
# DOWNLOAD
# =========================================================

print(
    "\n📡 Downloading Market Breadth Data..."
)

try:

    prices = yf.download(

        tickers=symbols,

        period="1y",

        auto_adjust=True,

        progress=False,

        threads=True,

        group_by="ticker"

    )

except Exception as e:

    raise RuntimeError(
        f"Yahoo download failed: {e}"
    )

if prices.empty:

    raise ValueError(
        "No market data downloaded."
    )

# =========================================================
# EXTRACT CLOSES
# =========================================================

close_frames = []

for symbol in symbols:

    try:

        if symbol not in prices.columns.levels[0]:

            continue

        close = prices[
            symbol
        ]["Close"]

        close.name = symbol

        close_frames.append(
            close
        )

    except:

        continue

if len(close_frames) == 0:

    raise ValueError(
        "No valid close series found."
    )

close_df = pd.concat(
    close_frames,
    axis=1
)

# =========================================================
# MOVING AVERAGES
# =========================================================

ma50 = (
    close_df
    .rolling(50)
    .mean()
)

ma200 = (
    close_df
    .rolling(200)
    .mean()
)

# =========================================================
# LATEST VALUES
# =========================================================

latest_close = close_df.iloc[-1]

latest_ma50 = ma50.iloc[-1]

latest_ma200 = ma200.iloc[-1]

# =========================================================
# BREADTH 50DMA
# =========================================================

above_50 = (

    latest_close

    >

    latest_ma50

).sum()

pct_above_50 = (

    above_50

    /

    len(latest_close)

) * 100

# =========================================================
# BREADTH 200DMA
# =========================================================

above_200 = (

    latest_close

    >

    latest_ma200

).sum()

pct_above_200 = (

    above_200

    /

    len(latest_close)

) * 100

# =========================================================
# BREADTH SCORE
# =========================================================

breadth_score = (

      pct_above_50 * 0.40

    + pct_above_200 * 0.60

)

breadth_score = round(
    breadth_score,
    2
)

# =========================================================
# REGIME
# =========================================================

if breadth_score >= 70:

    breadth_regime = "STRONG"

elif breadth_score >= 50:

    breadth_regime = "HEALTHY"

elif breadth_score >= 30:

    breadth_regime = "WEAK"

else:

    breadth_regime = "VERY_WEAK"

# =========================================================
# OUTPUT
# =========================================================

output = pd.DataFrame({

    "PCT_ABOVE_50DMA": [
        round(
            pct_above_50,
            2
        )
    ],

    "PCT_ABOVE_200DMA": [
        round(
            pct_above_200,
            2
        )
    ],

    "BREADTH_SCORE": [
        breadth_score
    ],

    "BREADTH_REGIME": [
        breadth_regime
    ],

    "STOCKS_ANALYSED": [
        len(latest_close)
    ]

})

# =========================================================
# SAVE
# =========================================================

output.to_csv(
    OUTPUT_FILE,
    index=False
)

# =========================================================
# REPORT
# =========================================================

print(
    "\n✅ Market Breadth Engine Complete"
)

print(
    f"\n📁 Saved:\n{OUTPUT_FILE}"
)

print(
    "\n📊 Breadth Statistics\n"
)

print(output)

print(
    f"\nAbove 50DMA : {pct_above_50:.2f}%"
)

print(
    f"Above 200DMA: {pct_above_200:.2f}%"
)

print(
    f"Breadth Score: {breadth_score}"
)

print(
    f"Breadth Regime: {breadth_regime}"
)
