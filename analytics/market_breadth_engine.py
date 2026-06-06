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

universe = (
    universe
    .sort_values(
        "MULTI_FACTOR_SCORE",
        ascending=False
    )
)

print(
    f"\n📊 Total Universe Stocks: "
    f"{len(universe)}"
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


if len(symbols) == 0:

    raise ValueError(
        "No valid symbols found."
    )
print(
    f"\n📊 Stocks Selected: {len(symbols)}"
)
# =========================================================
# DOWNLOAD
# =========================================================

print(
    "\n📡 Downloading Market Breadth Data..."
)

all_closes = []

BATCH_SIZE = 100

for i in range(
    0,
    len(symbols),
    BATCH_SIZE
):

    batch = symbols[
        i:i+BATCH_SIZE
    ]

    print(
        f"Downloading batch "
        f"{i+1} "
        f"to "
        f"{min(i+BATCH_SIZE,len(symbols))}"
    )

    try:

        data = yf.download(
            batch,
            period="18mo",
            auto_adjust=True,
            progress=False,
            threads=True,
            group_by="ticker"
        )

        if data.empty:
            continue

        close_frames = []

        for symbol in batch:

            try:

                close = (
                    data[symbol]["Close"]
                )

                close.name = symbol

                close_frames.append(
                    close
                )

            except:
                pass

        if close_frames:

            all_closes.append(

                pd.concat(
                    close_frames,
                    axis=1
                )

            )

    except Exception as e:

        print(e)


if len(all_closes) == 0:

    raise ValueError(
        "No price data downloaded."
    )

close_df = pd.concat(
    all_closes,
    axis=1
)

close_df = close_df.ffill(limit=5)

valid_history = (

    close_df

    .count()

    >=

    200

)

close_df = close_df.loc[
    :,
    valid_history
]

print(
    f"\nStocks with 200d history: "
    f"{close_df.shape[1]}"
)

print("\nClose DF Shape:")
print(close_df.shape)

print("\nColumns:")
print(close_df.columns[:10])

print("\nLast Rows:")
print(close_df.tail())

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

print("\nMA50 Shape:")
print(ma50.shape)

print("\nMA200 Shape:")
print(ma200.shape)

print("\nLatest MA200:")
print(ma200.iloc[-1].head(20))
# =========================================================
# LATEST VALUES
# =========================================================

latest_close = close_df.iloc[-1]

if len(close_df) < 200:

    raise ValueError(
        "Insufficient history for breadth calculations."
    )

previous_close = close_df.iloc[-2]

advancers = (
    latest_close
    >
    previous_close
).sum()

decliners = (
    latest_close
    <
    previous_close
).sum()

ad_ratio = (
    advancers
    /
    max(
        advancers + decliners,
        1
    )
) * 100

latest_ma50 = ma50.iloc[-1]

latest_ma200 = ma200.iloc[-1]


# =========================================================
# 52 WEEK HIGH PARTICIPATION
# =========================================================

lookback_days = min(
    252,
    len(close_df)
)

high_52w = (

    close_df

    .rolling(
        lookback_days
    )

    .max()

)

valid_highs = (
    latest_close.notna()
    &
    high_52w.iloc[-1].notna()
)

pct_new_highs = (
    (
        latest_close[valid_highs]
        >=
        high_52w.iloc[-1][valid_highs]
    ).sum()
    /
    max(valid_highs.sum(), 1)
) * 100

# =========================================================
# BREADTH 50DMA
# =========================================================

valid_50 = (
    latest_close.notna()
    &
    latest_ma50.notna()
)

valid_200 = (
    latest_close.notna()
    &
    latest_ma200.notna()
)

pct_above_50 = (
    (
        latest_close[valid_50]
        >
        latest_ma50[valid_50]
    ).sum()
    /
    max(valid_50.sum(), 1)
) * 100

pct_above_200 = (
    (
        latest_close[valid_200]
        >
        latest_ma200[valid_200]
    ).sum()
    /
    max(valid_200.sum(), 1)
) * 100

# =========================================================
# BREADTH SCORE
# =========================================================

ad_score = ad_ratio

breadth_score = (

      pct_above_200 * 0.40

    + pct_above_50 * 0.30

    + ad_score * 0.20

    + pct_new_highs * 0.10

)

breadth_score = round(
    min(
        100,
        max(
            0,
            breadth_score
        )
    ),
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

    "ADVANCE_PERCENTAGE": [
        round(
            ad_ratio,
            2
        )
    ],

    "PCT_NEW_52W_HIGHS": [
        round(
            pct_new_highs,
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
        int(
            valid_200.sum()
        )
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
    f"Advance %      : {ad_ratio:.2f}"
)

print(
    f"52W Highs %   : {pct_new_highs:.2f}%"
)

print(
    f"Stocks Used   : {int(valid_200.sum())}"
)

print(
    f"Breadth Score: {breadth_score}"
)

print(
    f"Breadth Regime: {breadth_regime}"
)
