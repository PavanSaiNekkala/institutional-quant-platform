import pandas as pd

from pathlib import Path

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[1]

RANKINGS_FILE = (
    ROOT_DIR
    / "data"
    / "institutional_rankings.csv"
)

METADATA_FILE = (
    ROOT_DIR
    / "data"
    / "stock_metadata.csv"
)

OUTPUT_FILE = (
    ROOT_DIR
    / "data"
    / "sector_summary.csv"
)

# =========================================================
# LOAD DATA
# =========================================================

print("\n📥 Loading Data...")

rank_df = pd.read_csv(RANKINGS_FILE)

meta_df = pd.read_csv(METADATA_FILE)

# =========================================================
# CLEAN SYMBOLS
# =========================================================

rank_df["Symbol"] = (

    rank_df["Symbol"]

    .astype(str)

    .str.replace(".NS", "", regex=False)
)

meta_df["Symbol"] = (

    meta_df["Symbol"]

    .astype(str)

    .str.replace(".NS", "", regex=False)
)

# =========================================================
# MERGE
# =========================================================

df = pd.merge(

    rank_df,

    meta_df,

    on="Symbol",

    how="left"
)

# =========================================================
# FILL MISSING
# =========================================================

df["Sector"] = (
    df["Sector"]
    .fillna("Unknown")
)

df["Industry"] = (
    df["Industry"]
    .fillna("Unknown")
)

# =========================================================
# CREATE MOMENTUM
# =========================================================

df["Momentum"] = (

    (
        df["RS_5D"]

        +

        df["RS_15D"]

        +

        df["RS_30D"]

        +

        df["RS_60D"]
    )

    / 4
)

# =========================================================
# CREATE SHARPE PROXY
# =========================================================

df["Sharpe"] = (

    df["VOL_ADJ_RS"]

    / (

        df["VOLATILITY"]

        + 1e-9
    )
)

# =========================================================
# FINAL SCORE
# =========================================================

df["FINAL_SCORE"] = (

    df["ALPHA_SCORE"]

    * 20
)

# =========================================================
# CLASSIFICATION
# =========================================================

def classify(score):

    if score >= 80:

        return "STRONG_BUY"

    elif score >= 60:

        return "BUY"

    elif score >= 40:

        return "HOLD"

    else:

        return "SELL"

df["Classification"] = (

    df["FINAL_SCORE"]

    .apply(classify)
)

# =========================================================
# BUY COUNTS
# =========================================================

df["BUY_COUNT"] = (

    df["Classification"]

    .isin([
        "BUY",
        "STRONG_BUY"
    ])

    .astype(int)
)

df["STRONG_BUY_COUNT"] = (

    (
        df["Classification"]

        == "STRONG_BUY"
    )

    .astype(int)
)

# =========================================================
# SECTOR SUMMARY
# =========================================================

sector_summary = (

    df.groupby("Sector")

    .agg({

        "Momentum": "mean",

        "Sharpe": "mean",

        "FINAL_SCORE": "mean",

        "BUY_COUNT": "sum",

        "STRONG_BUY_COUNT": "sum",

        "Symbol": "count"
    })

    .reset_index()
)

# =========================================================
# RENAME COLUMNS
# =========================================================

sector_summary.columns = [

    "Sector",

    "AVG_MOMENTUM",

    "AVG_SHARPE",

    "AVG_INSTITUTIONAL_SCORE",

    "BUY_COUNT",

    "STRONG_BUY_COUNT",

    "TOTAL_STOCKS"
]

# =========================================================
# ROUNDING
# =========================================================

numeric_cols = [

    "AVG_MOMENTUM",

    "AVG_SHARPE",

    "AVG_INSTITUTIONAL_SCORE"
]

sector_summary[numeric_cols] = (

    sector_summary[numeric_cols]

    .round(2)
)

# =========================================================
# SECTOR SCORE
# =========================================================

sector_summary["SECTOR_SCORE"] = (

    (
        sector_summary["AVG_MOMENTUM"] * 0.4
    )

    +

    (
        sector_summary["AVG_SHARPE"] * 0.3
    )

    +

    (
        sector_summary["AVG_INSTITUTIONAL_SCORE"] * 0.3
    )

).round(2)

# =========================================================
# SORT
# =========================================================

sector_summary = sector_summary.sort_values(

    by="SECTOR_SCORE",

    ascending=False
)

# =========================================================
# SAVE
# =========================================================

sector_summary.to_csv(

    OUTPUT_FILE,

    index=False
)

# =========================================================
# OUTPUT
# =========================================================

print("\n✅ Sector Summary Generated")

print(
    f"\n📁 Saved to:\n"
    f"{OUTPUT_FILE}"
)

print("\n🏆 Top Sectors:\n")

print(
    sector_summary.head(10)
)
