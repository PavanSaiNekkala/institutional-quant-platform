import pandas as pd
import numpy as np

from pathlib import Path

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    ROOT_DIR
    / "data"
    / "cross_sectional_rankings.csv"
)

OUTPUT_FILE = (
    ROOT_DIR
    / "data"
    / "factor_model_rankings.csv"
)

# =========================================================
# LOAD DATA
# =========================================================

print("\n📥 Loading Ranking Data...")

df = pd.read_csv(INPUT_FILE)

print("✅ Ranking Data Loaded")
print("\n===== FACTOR MODEL INPUT =====")

print(
    df[
        [
            "Symbol",
            "Momentum",
            "Sharpe"
        ]
    ].head(10)
)

print()

print(
    df[
        [
            "Momentum",
            "Sharpe"
        ]
    ].describe()
)

# =========================================================
# CLEAN COLUMNS
# =========================================================

df.columns = df.columns.str.strip()

# =========================================================
# REQUIRED COLUMNS
# =========================================================

required_cols = [

    "Symbol",

    "Sector",

    "Momentum",

    "Sharpe",

    "ALPHA_SCORE"

]

for col in required_cols:

    if col not in df.columns:

        raise Exception(
            f"\n❌ Missing Required Column: {col}"
        )

# =========================================================
# CLEAN DATA
# =========================================================

df = df.replace(
    [np.inf, -np.inf],
    np.nan
)

df = df.dropna(
    subset=required_cols
)

# =========================================================
# FACTOR ENGINE
# =========================================================

print("\n🧠 Building Institutional Factors...")

# ---------------------------------------------------------
# MOMENTUM FACTOR
# ---------------------------------------------------------

df["FACTOR_MOMENTUM"] = (

    df["Momentum"]

    .rank(pct=True)

    * 100
)

# ---------------------------------------------------------
# SHARPE FACTOR
# ---------------------------------------------------------

df["FACTOR_SHARPE"] = (

    df["Sharpe"]

    .rank(pct=True)

    * 100
)

# ---------------------------------------------------------
# ALPHA FACTOR
# ---------------------------------------------------------

df["FACTOR_ALPHA"] = (

    df["ALPHA_SCORE"]

    .rank(pct=True)

    * 100
)

# ---------------------------------------------------------
# RS FACTOR
# ---------------------------------------------------------

rs_cols = [

    "RS_30D",

    "RS_60D",

    "RS_ACCELERATION"

]

existing_rs_cols = [

    col for col in rs_cols
    if col in df.columns
]

if len(existing_rs_cols) > 0:

    df["RS_COMPOSITE"] = (

        df[existing_rs_cols]

        .mean(axis=1)
    )

else:

    df["RS_COMPOSITE"] = 0

df["FACTOR_RS"] = (

    df["RS_COMPOSITE"]

    .rank(pct=True)

    * 100
)

# ---------------------------------------------------------
# LOW VOL FACTOR
# ---------------------------------------------------------

if "VOL_ADJ_RS" in df.columns:

    df["FACTOR_LOW_VOL"] = (

        (
            1 /
            (
                df["VOL_ADJ_RS"]
                + 1e-6
            )
        )

        .rank(pct=True)

        * 100
    )

else:

    df["FACTOR_LOW_VOL"] = 50

# ---------------------------------------------------------
# SECTOR FACTOR
# ---------------------------------------------------------

if "SECTOR_SCORE" in df.columns:

    df["FACTOR_SECTOR"] = (

        df["SECTOR_SCORE"]

        .rank(pct=True)

        * 100
    )

else:

    df["FACTOR_SECTOR"] = 50

# =========================================================
# FINAL FACTOR MODEL SCORE
# =========================================================

df["MULTI_FACTOR_SCORE"] = (

    (
        df["FACTOR_ALPHA"] * 0.25
    )

    +

    (
        df["FACTOR_MOMENTUM"] * 0.20
    )

    +

    (
        df["FACTOR_RS"] * 0.20
    )

    +

    (
        df["FACTOR_SHARPE"] * 0.15
    )

    +

    (
        df["FACTOR_LOW_VOL"] * 0.10
    )

    +

    (
        df["FACTOR_SECTOR"] * 0.10
    )

)

# =========================================================
# FINAL RANK
# =========================================================

df = df.sort_values(

    by="MULTI_FACTOR_SCORE",

    ascending=False
)

df["FACTOR_RANK"] = range(

    1,

    len(df) + 1
)

# =========================================================
# ROUNDING
# =========================================================

score_cols = [

    "FACTOR_ALPHA",

    "FACTOR_MOMENTUM",

    "FACTOR_RS",

    "FACTOR_SHARPE",

    "FACTOR_LOW_VOL",

    "FACTOR_SECTOR",

    "MULTI_FACTOR_SCORE"

]

df[score_cols] = (

    df[score_cols]

    .round(2)
)

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

print(
    "\n✅ Institutional Factor Model Complete"
)

print(
    f"\n📁 Saved To:\n"
    f"{OUTPUT_FILE}"
)

print("\n🏆 TOP FACTOR STOCKS:\n")

print(

    df[

        [
            "FACTOR_RANK",
            "Symbol",
            "Sector",
            "MULTI_FACTOR_SCORE"
        ]

    ].head(20)
)