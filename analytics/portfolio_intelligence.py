import pandas as pd
import numpy as np

from pathlib import Path

# =========================================================
# CONFIG
# =========================================================

MAX_POSITION_SIZE = 0.10

MIN_POSITION_SIZE = 0.02

MAX_SECTOR_EXPOSURE = 0.30

TARGET_PORTFOLIO_VOL = 0.18

TOP_N = 20

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[1]

RANKINGS_FILE = (
    ROOT_DIR
    / "data"
    / "cross_sectional_rankings.csv"
)

SECTOR_FILE = (
    ROOT_DIR
    / "data"
    / "sector_relative_strength.csv"
)

REGIME_FILE = (
    ROOT_DIR
    / "data"
    / "market_regime_v2.csv"
)

OUTPUT_FILE = (
    ROOT_DIR
    / "data"
    / "portfolio_intelligence.csv"
)

# =========================================================
# LOAD DATA
# =========================================================

print("\n📥 Loading Data...")

rank_df = pd.read_csv(RANKINGS_FILE)

sector_df = pd.read_csv(SECTOR_FILE)

regime_df = pd.read_csv(REGIME_FILE)

print("✅ Data Loaded")

# =========================================================
# CLEAN COLUMN NAMES
# =========================================================

rank_df.columns = rank_df.columns.str.strip()

sector_df.columns = sector_df.columns.str.strip()

regime_df.columns = regime_df.columns.str.strip()

# =========================================================
# DETECT SCORE COLUMN
# =========================================================

score_candidates = [

    "ALPHA_SCORE",

    "FINAL_SCORE",

    "CROSS_SECTIONAL_SCORE",

    "COMPOSITE_SCORE",

    "RS_SCORE"

]

score_col = None

for col in score_candidates:

    if col in rank_df.columns:

        score_col = col

        break

if score_col is None:

    raise Exception(
        f"\n❌ No valid score column found\n"
        f"Available Columns:\n{rank_df.columns.tolist()}"
    )

print(f"\n✅ Using Score Column: {score_col}")

# =========================================================
# REQUIRED COLUMNS
# =========================================================

required_cols = [

    "Symbol",

    "Sector",

    "Momentum",

    "Sharpe"

]

for col in required_cols:

    if col not in rank_df.columns:

        raise Exception(
            f"\n❌ Missing Required Column: {col}"
        )

# =========================================================
# OPTIONAL LIQUIDITY COLUMN
# =========================================================

liquidity_col = None

liquidity_candidates = [

    "Avg Volume",

    "AVG_VOLUME",

    "Volume",

    "VOL_ADJ_RS"

]

for col in liquidity_candidates:

    if col in rank_df.columns:

        liquidity_col = col

        break

if liquidity_col:

    print(
        f"\n✅ Using Liquidity Column: "
        f"{liquidity_col}"
    )

else:

    print(
        "\n⚠️ No liquidity column found"
    )

# =========================================================
# CLEAN DATA
# =========================================================

rank_df = rank_df.replace(
    [np.inf, -np.inf],
    np.nan
)

drop_cols = [

    score_col,

    "Momentum",

    "Sharpe"

]

rank_df = rank_df.dropna(
    subset=drop_cols
)

# =========================================================
# EMPTY DATA CHECK
# =========================================================

if len(rank_df) == 0:

    raise Exception(
        "\n❌ No valid ranking data available"
    )

# =========================================================
# LIQUIDITY FILTER
# =========================================================

if liquidity_col:

    rank_df[liquidity_col] = pd.to_numeric(
        rank_df[liquidity_col],
        errors="coerce"
    )

    filtered_df = rank_df[
        rank_df[liquidity_col] > 0
    ]

    if len(filtered_df) > 0:

        rank_df = filtered_df

        print(
            f"\n✅ Stocks After Liquidity Filter: "
            f"{len(rank_df)}"
        )

    else:

        print(
            "\n⚠ Liquidity filter removed all stocks"
        )

        print(
            "⚠ Continuing with original universe"
        )

        print(
            f"⚠ Universe Size: {len(rank_df)}"
        )

# =========================================================
# MERGE SECTOR SCORES
# =========================================================

# Remove existing duplicate column first

if "SECTOR_SCORE" in rank_df.columns:

    rank_df = rank_df.drop(
        columns=["SECTOR_SCORE"]
    )

# Merge fresh sector scores

if (
    "Sector" in sector_df.columns
    and
    "SECTOR_SCORE" in sector_df.columns
):

    rank_df = pd.merge(

        rank_df,

        sector_df[
            [
                "Sector",
                "SECTOR_SCORE"
            ]
        ],

        on="Sector",

        how="left"
    )

else:

    rank_df["SECTOR_SCORE"] = 0

# Fill missing values

rank_df["SECTOR_SCORE"] = (

    rank_df["SECTOR_SCORE"]

    .fillna(0)

    .astype(float)
)

print(
    "\n✅ Sector Scores Integrated"
)
# =========================================================
# MARKET REGIME
# =========================================================

market_regime = "SIDEWAYS"

if len(regime_df) > 0:

    if "MARKET_REGIME" in regime_df.columns:

        market_regime = (
            regime_df.iloc[-1]["MARKET_REGIME"]
        )

print(
    f"\n🌍 Market Regime: "
    f"{market_regime}"
)

# =========================================================
# REGIME MULTIPLIER
# =========================================================

if market_regime == "BULL":

    regime_multiplier = 1.20

elif market_regime == "BEAR":

    regime_multiplier = 0.70

else:

    regime_multiplier = 1.00

# =========================================================
# AI SCORE ENGINE
# =========================================================

rank_df["AI_SCORE"] = (

    (
        rank_df[score_col] * 0.35
    )

    +

    (
        rank_df["Momentum"] * 100 * 0.20
    )

    +

    (
        rank_df["Sharpe"] * 10 * 0.20
    )

    +

    (
        rank_df["SECTOR_SCORE"] * 0.15
    )

)

# =========================================================
# OPTIONAL RS ENHANCEMENT
# =========================================================

optional_rs_cols = [

    "RS_30D",

    "RS_60D",

    "RS_ACCELERATION",

    "VOL_ADJ_RS"

]

for col in optional_rs_cols:

    if col in rank_df.columns:

        rank_df["AI_SCORE"] += (

            rank_df[col]
            .fillna(0)
            * 0.025
        )

# =========================================================
# REGIME ADJUSTMENT
# =========================================================

rank_df["AI_SCORE"] *= regime_multiplier

# =========================================================
# REMOVE NEGATIVE SCORES
# =========================================================

rank_df = rank_df[
    rank_df["AI_SCORE"] > 0
]

if len(rank_df) == 0:

    raise Exception(
        "\n❌ All AI scores invalid"
    )

# =========================================================
# SORT
# =========================================================

rank_df = rank_df.sort_values(

    by="AI_SCORE",

    ascending=False
)

# =========================================================
# SELECT TOP STOCKS
# =========================================================

portfolio = rank_df.head(TOP_N).copy()

# =========================================================
# RAW WEIGHTS
# =========================================================

portfolio["RAW_WEIGHT"] = (

    portfolio["AI_SCORE"]

    / portfolio["AI_SCORE"].sum()
)

# =========================================================
# POSITION CAPS
# =========================================================

portfolio["RAW_WEIGHT"] = np.clip(

    portfolio["RAW_WEIGHT"],

    MIN_POSITION_SIZE,

    MAX_POSITION_SIZE
)

# =========================================================
# SECTOR EXPOSURE CONTROL
# =========================================================

sector_exposure = (

    portfolio

    .groupby("Sector")["RAW_WEIGHT"]

    .sum()
)

for sector, exposure in sector_exposure.items():

    if exposure > MAX_SECTOR_EXPOSURE:

        reduction_factor = (

            MAX_SECTOR_EXPOSURE
            /
            exposure
        )

        mask = (
            portfolio["Sector"]
            == sector
        )

        portfolio.loc[
            mask,
            "RAW_WEIGHT"
        ] *= reduction_factor

# =========================================================
# FINAL NORMALIZATION
# =========================================================

portfolio["FINAL_WEIGHT"] = (

    portfolio["RAW_WEIGHT"]

    / portfolio["RAW_WEIGHT"].sum()
)

# =========================================================
# VOL TARGETING
# =========================================================

portfolio_vol = (

    portfolio["Sharpe"].std()
)

if (
    pd.notna(portfolio_vol)
    and portfolio_vol > 0
):

    vol_adjustment = (

        TARGET_PORTFOLIO_VOL
        /
        portfolio_vol
    )

else:

    vol_adjustment = 1

portfolio["TARGET_WEIGHT"] = (

    portfolio["FINAL_WEIGHT"]
    * vol_adjustment
)

portfolio["TARGET_WEIGHT"] = (

    portfolio["TARGET_WEIGHT"]

    / portfolio["TARGET_WEIGHT"].sum()
)

# =========================================================
# ROUNDING
# =========================================================

portfolio["TARGET_WEIGHT"] = (
    portfolio["TARGET_WEIGHT"]
    .round(4)
)

portfolio["AI_SCORE"] = (
    portfolio["AI_SCORE"]
    .round(2)
)

# =========================================================
# PORTFOLIO HEALTH
# =========================================================

portfolio_health = {

    "TOTAL_STOCKS":

        len(portfolio),

    "AVG_AI_SCORE":

        round(
            portfolio["AI_SCORE"].mean(),
            2
        ),

    "AVG_SHARPE":

        round(
            portfolio["Sharpe"].mean(),
            2
        ),

    "AVG_MOMENTUM":

        round(
            portfolio["Momentum"].mean(),
            4
        ),

    "TOP_SECTOR":

        portfolio["Sector"]

        .value_counts()

        .idxmax(),

    "MAX_WEIGHT":

        round(
            portfolio[
                "TARGET_WEIGHT"
            ].max()
            * 100,
            2
        )
}

# =========================================================
# SAVE
# =========================================================

portfolio.to_csv(

    OUTPUT_FILE,

    index=False
)

# =========================================================
# OUTPUT
# =========================================================

print(
    "\n✅ Portfolio Intelligence Generated"
)

print(
    f"\n📁 Saved To:\n"
    f"{OUTPUT_FILE}"
)

print("\n🏆 PORTFOLIO HEALTH:\n")

for k, v in portfolio_health.items():

    print(f"{k}: {v}")

print("\n🏆 TOP HOLDINGS:\n")

print(

    portfolio[

        [
            "Symbol",
            "Sector",
            "AI_SCORE",
            "TARGET_WEIGHT"
        ]

    ].head(15)
)