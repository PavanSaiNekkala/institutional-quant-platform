import pandas as pd

from pathlib import Path

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[1]

RS_FILE = (
    ROOT_DIR
    / "data"
    / "institutional_rankings.csv"
)

META_FILE = (
    ROOT_DIR
    / "data"
    / "stock_metadata.csv"
)

OUTPUT_FILE = (
    ROOT_DIR
    / "data"
    / "sector_relative_strength.csv"
)

# =========================================================
# LOAD DATA
# =========================================================

rs_df = pd.read_csv(RS_FILE)

meta_df = pd.read_csv(META_FILE)

# =========================================================
# CLEAN SYMBOLS
# =========================================================

rs_df["Symbol"] = (

    rs_df["Symbol"]

    .astype(str)

    .str.replace(".NS", "", regex=False)

    .str.upper()

    .str.strip()
)

meta_df["Symbol"] = (

    meta_df["Symbol"]

    .astype(str)

    .str.replace(".NS", "", regex=False)

    .str.upper()

    .str.strip()
)

# =========================================================
# MERGE
# =========================================================

df = pd.merge(

    rs_df,

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
# NUMERIC CLEAN
# =========================================================

numeric_cols = [

    "RS_5D",

    "RS_15D",

    "RS_30D",

    "RS_60D",

    "RS_ACCELERATION",

    "VOL_ADJ_RS"
]

for col in numeric_cols:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

# =========================================================
# SECTOR AGGREGATION
# =========================================================

sector_df = (

    df.groupby("Sector")

    .agg({

        "RS_5D": "mean",

        "RS_15D": "mean",

        "RS_30D": "mean",

        "RS_60D": "mean",

        "RS_ACCELERATION": "mean",

        "VOL_ADJ_RS": "mean",

        "Symbol": "count"

    })

    .reset_index()
)

# =========================================================
# RENAME
# =========================================================

sector_df.columns = [

    "Sector",

    "AVG_RS_5D",

    "AVG_RS_15D",

    "AVG_RS_30D",

    "AVG_RS_60D",

    "AVG_RS_ACCELERATION",

    "AVG_VOL_ADJ_RS",

    "TOTAL_STOCKS"
]

# =========================================================
# ROUNDING
# =========================================================

round_cols = [

    "AVG_RS_5D",

    "AVG_RS_15D",

    "AVG_RS_30D",

    "AVG_RS_60D",

    "AVG_RS_ACCELERATION",

    "AVG_VOL_ADJ_RS"
]

sector_df[round_cols] = (

    sector_df[round_cols]

    .round(2)
)

# =========================================================
# INSTITUTIONAL SECTOR SCORE
# =========================================================

sector_df["SECTOR_SCORE"] = (

    (

        sector_df["AVG_RS_30D"] * 0.4

    )

    +

    (

        sector_df["AVG_RS_60D"] * 0.4

    )

    +

    (

        sector_df["AVG_RS_ACCELERATION"] * 0.2

    )

).round(2)

# =========================================================
# RANK
# =========================================================

sector_df = sector_df.sort_values(

    by=[

        "SECTOR_SCORE",

        "AVG_RS_30D"

    ],

    ascending=False
)

# =========================================================
# SECTOR RANK
# =========================================================

sector_df["SECTOR_RANK"] = (

    range(

        1,

        len(sector_df) + 1
    )
)

# =========================================================
# SAVE
# =========================================================

sector_df.to_csv(

    OUTPUT_FILE,

    index=False
)

# =========================================================
# OUTPUT
# =========================================================

print("\n✅ Sector Relative Strength Generated")

print(
    f"\n📁 Saved to:\n"
    f"{OUTPUT_FILE}"
)

print("\n🏆 Strongest Sectors:\n")

print(

    sector_df.head(10)
)