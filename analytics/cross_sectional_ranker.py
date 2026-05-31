import pandas as pd
import numpy as np

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

RS_FILE = (
    ROOT_DIR
    / "data"
    / "institutional_rankings.csv"
)

SECTOR_RS_FILE = (
    ROOT_DIR
    / "data"
    / "sector_relative_strength.csv"
)

META_FILE = (
    ROOT_DIR
    / "data"
    / "stock_metadata.csv"
)

OUTPUT_FILE = (
    ROOT_DIR
    / "data"
    / "cross_sectional_rankings.csv"
)

# =========================================================
# LOAD DATA
# =========================================================

print("\n📥 Loading Files...")

rank_df = pd.read_csv(RANKINGS_FILE)

rs_df = pd.read_csv(RS_FILE)

sector_df = pd.read_csv(SECTOR_RS_FILE)

meta_df = pd.read_csv(META_FILE)

print("✅ Files Loaded")

print("\n===== RANK DF CHECK =====")
print(
    rank_df[
        ["Symbol","Momentum","Sharpe"]
    ].head(10)
)

print(
    rank_df[
        ["Momentum","Sharpe"]
    ].describe()
)

# =========================================================
# CLEAN SYMBOLS
# =========================================================

def clean_symbol(series):

    return (

        series

        .astype(str)

        .str.replace(".NS", "", regex=False)

        .str.upper()

        .str.strip()
    )

rank_df["Symbol"] = clean_symbol(
    rank_df["Symbol"]
)

rs_df["Symbol"] = clean_symbol(
    rs_df["Symbol"]
)

meta_df["Symbol"] = clean_symbol(
    meta_df["Symbol"]
)

# =========================================================
# MERGE DATA
# =========================================================

print("\n🔄 Merging Data...")

df = rank_df.copy()

print("\n===== AFTER COPY =====")

print(
    df[
        ["Symbol","Momentum","Sharpe"]
    ].head(10)
)

df = pd.merge(

    df,

    meta_df[
        [
            "Symbol",
            "Sector",
            "Industry",
            "MarketCap"
        ]
    ],

    on="Symbol",

    how="left"
)

print("\n===== AFTER META MERGE =====")

print(
    df[
        [
            "Symbol",
            "Momentum",
            "Sharpe"
        ]
    ].head(10)
)

print(
    df[
        [
            "Momentum",
            "Sharpe"
        ]
    ].describe()
)

sector_cols = [

    "Sector",

    "SECTOR_SCORE",

    "SECTOR_RANK"
]

df = pd.merge(

    df,

    sector_df[sector_cols],

    on="Sector",

    how="left"
)

print("✅ Merge Completed")

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
# NUMERIC COLUMNS
# =========================================================

numeric_cols = [

    "Momentum",

    "Sharpe",

    "RS_30D",

    "RS_60D",

    "RS_ACCELERATION",

    "VOL_ADJ_RS",

    "SECTOR_SCORE"
]

# =========================================================
# CONVERT TO NUMERIC
# =========================================================

for col in numeric_cols:

    if col not in df.columns:

        print(f"⚠️ Missing Column: {col}")

        df[col] = 0

    df[col] = pd.to_numeric(

        df[col],

        errors="coerce"
    )

# =========================================================
# FILL NaN
# =========================================================

df[numeric_cols] = (

    df[numeric_cols]

    .replace([np.inf, -np.inf], np.nan)

    .fillna(0)
)
print("\n===== AFTER NUMERIC CLEAN =====")

print(
    df[
        ["Momentum","Sharpe"]
    ].describe()
)

# =========================================================
# ZSCORE FUNCTION
# =========================================================

def zscore(series):

    std = series.std()

    if std == 0:

        return pd.Series(
            0,
            index=series.index
        )

    return (

        series - series.mean()

    ) / std

# =========================================================
# FACTOR NORMALIZATION
# =========================================================

print("\n📊 Calculating Factor Scores...")

df["MOMENTUM_Z"] = zscore(
    df["Momentum"]
)

df["SHARPE_Z"] = zscore(
    df["Sharpe"]
)

df["RS30_Z"] = zscore(
    df["RS_30D"]
)

df["RS60_Z"] = zscore(
    df["RS_60D"]
)

df["ACCEL_Z"] = zscore(
    df["RS_ACCELERATION"]
)

df["VOLADJ_Z"] = zscore(
    df["VOL_ADJ_RS"]
)

df["SECTOR_Z"] = zscore(
    df["SECTOR_SCORE"]
)

# =========================================================
# MASTER ALPHA SCORE
# =========================================================

print("\n🧠 Building Institutional Alpha Score...")

df["ALPHA_SCORE"] = (

    (

        df["MOMENTUM_Z"] * 0.20

    )

    +

    (

        df["SHARPE_Z"] * 0.20

    )

    +

    (

        df["RS30_Z"] * 0.20

    )

    +

    (

        df["RS60_Z"] * 0.15

    )

    +

    (

        df["ACCEL_Z"] * 0.10

    )

    +

    (

        df["VOLADJ_Z"] * 0.05

    )

    +

    (

        df["SECTOR_Z"] * 0.10

    )

)

# =========================================================
# ROUNDING
# =========================================================

df["ALPHA_SCORE"] = (

    df["ALPHA_SCORE"]

    .round(4)
)

# =========================================================
# SORTING
# =========================================================

print("\n📈 Ranking Stocks...")

df = df.sort_values(

    by=[

        "ALPHA_SCORE",

        "RS_30D",

        "RS_60D"

    ],

    ascending=False
)

# =========================================================
# FINAL RANK
# =========================================================

df["ALPHA_RANK"] = (

    range(

        1,

        len(df) + 1
    )
)

# =========================================================
# REMOVE DUPLICATES
# =========================================================

df = df.drop_duplicates(
    subset=["Symbol"]
)

# =========================================================
# FINAL COLUMN ORDER
# =========================================================

final_cols = [

    "ALPHA_RANK",

    "Symbol",

    "Sector",

    "Industry",

    "MarketCap",

    "ALPHA_SCORE",

    "Momentum",

    "Sharpe",

    "RS_30D",

    "RS_60D",

    "RS_ACCELERATION",

    "VOL_ADJ_RS",

    "SECTOR_SCORE",

    "SECTOR_RANK"
]

available_cols = [

    col for col in final_cols

    if col in df.columns
]

df = df[available_cols]

# =========================================================
# SAVE
# =========================================================

df.to_csv(

    OUTPUT_FILE,

    index=False
)

# =========================================================
# OUTPUT
# =========================================================

print("\n✅ Cross-Sectional Ranking Generated")

print(
    f"\n📁 Saved to:\n"
    f"{OUTPUT_FILE}"
)

print("\n🏆 TOP ALPHA STOCKS:\n")

print(

    df.head(20)
)
