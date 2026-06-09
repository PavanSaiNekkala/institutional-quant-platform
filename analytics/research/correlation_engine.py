import pandas as pd
import numpy as np
import yfinance as yf

from pathlib import Path

# =========================================================
# CONFIG
# =========================================================

TOP_N_STOCKS = 150

LOOKBACK_PERIOD = "1y"

CORRELATION_THRESHOLD = 0.75

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT_DIR / "data"

RANKINGS_FILE = (
    DATA_DIR
    / "conviction_scores.csv"
)

CORRELATION_FILE = (
    DATA_DIR
    / "correlation_matrix.csv"
)

DIVERSIFIED_FILE = (
    DATA_DIR
    / "diversified_candidates.csv"
)

# =========================================================
# LOAD RANKINGS
# =========================================================

print(
    "\n📥 Loading Rankings..."
)

rank_df = pd.read_csv(
    RANKINGS_FILE
)
print(
    f"Rows loaded: {len(rank_df)}"
)

print(
    rank_df.head()
)
high_df = rank_df[
    rank_df["CONVICTION"] == "HIGH"
]

if len(high_df) > 0:

    rank_df = high_df

else:

    print(
        "⚠️ No HIGH conviction stocks found."
    )

    print(
        "Using top ranked stocks instead."
    )
print(
    f"HIGH conviction rows: {len(rank_df)}"
)
rank_df = rank_df.sort_values(
    "MULTI_FACTOR_SCORE",
    ascending=False
)

rank_df = rank_df.head(
    TOP_N_STOCKS
)

symbols = (
    rank_df["Symbol"]
    .astype(str)
    .tolist()
)
if len(symbols) == 0:

    raise Exception(
        "❌ No symbols available for correlation analysis."
    )
# =========================================================
# DOWNLOAD DATA
# =========================================================

tickers = [
    f"{x}.NS"
    for x in symbols
]

print(
    f"\n📡 Downloading {len(tickers)} stocks..."
)

prices = yf.download(
    tickers,
    period=LOOKBACK_PERIOD,
    auto_adjust=True,
    progress=False,
    threads=True
)

if isinstance(
    prices.columns,
    pd.MultiIndex
):

    prices = prices["Close"]

# =========================================================
# RETURNS
# =========================================================

returns = (
    prices
    .pct_change()
    .dropna(how="all")
)

# =========================================================
# CORRELATION MATRIX
# =========================================================

corr_matrix = returns.corr()

corr_matrix.to_csv(
    CORRELATION_FILE
)

print(
    "\n✅ Correlation Matrix Saved"
)

# =========================================================
# DIVERSIFICATION FILTER
# =========================================================

selected = []

for symbol in symbols:

    keep = True

    for existing in selected:

        try:

            corr = corr_matrix.loc[
                f"{symbol}.NS",
                f"{existing}.NS"
            ]

            if corr > CORRELATION_THRESHOLD:

                keep = False

                break

        except Exception:

            continue

    if keep:

        selected.append(
            symbol
        )

# =========================================================
# OUTPUT
# =========================================================

diversified_df = rank_df[
    rank_df["Symbol"].isin(
        selected
    )
]

diversified_df.to_csv(
    DIVERSIFIED_FILE,
    index=False
)

print(
    "\n✅ Diversified Candidates Saved"
)

print(
    f"\nOriginal Stocks: {len(symbols)}"
)

print(
    f"Diversified Stocks: {len(selected)}"
)

print(
    "\n🏆 Top Diversified Picks:\n"
)

print(

    diversified_df[
        [
            "Symbol",
            "MULTI_FACTOR_SCORE"
        ]
    ]

    .head(20)
)
