import pandas as pd
import numpy as np

from pathlib import Path

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[1]

FACTOR_FILE = (
    ROOT_DIR
    / "data"
    / "factor_model_rankings.csv"
)

REGIME_FILE = (
    ROOT_DIR
    / "data"
    / "market_regime_v2.csv"
)

OUTPUT_FILE = (
    ROOT_DIR
    / "data"
    / "meta_strategy_portfolio.csv"
)

# =========================================================
# LOAD DATA
# =========================================================

print("\n📥 Loading Data...")

df = pd.read_csv(FACTOR_FILE)

regime_df = pd.read_csv(REGIME_FILE)

print("✅ Data Loaded")

# =========================================================
# CLEAN COLUMNS
# =========================================================

df.columns = df.columns.str.strip()

regime_df.columns = regime_df.columns.str.strip()

# =========================================================
# CURRENT REGIME
# =========================================================

market_regime = (

    regime_df.iloc[0]["MARKET_REGIME"]
)

print(
    f"\n🌍 Current Regime: "
    f"{market_regime}"
)

# =========================================================
# REQUIRED COLUMNS
# =========================================================

required_cols = [

    "Symbol",

    "Sector",

    "MULTI_FACTOR_SCORE",

    "Momentum",

    "Sharpe"

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
# STRATEGY ENGINES
# =========================================================

print(
    "\n🧠 Running Meta-Strategy Models..."
)

# ---------------------------------------------------------
# MOMENTUM STRATEGY
# ---------------------------------------------------------

df["STRATEGY_MOMENTUM"] = (

    df["Momentum"]

    .rank(pct=True)

    * 100
)

# ---------------------------------------------------------
# QUALITY STRATEGY
# ---------------------------------------------------------

df["STRATEGY_QUALITY"] = (

    df["Sharpe"]

    .rank(pct=True)

    * 100
)

# ---------------------------------------------------------
# FACTOR STRATEGY
# ---------------------------------------------------------

df["STRATEGY_FACTOR"] = (

    df["MULTI_FACTOR_SCORE"]

    .rank(pct=True)

    * 100
)

# ---------------------------------------------------------
# LOW VOL STRATEGY
# ---------------------------------------------------------

if "VOL_ADJ_RS" in df.columns:

    df["STRATEGY_LOW_VOL"] = (

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

    df["STRATEGY_LOW_VOL"] = 50

# ---------------------------------------------------------
# RELATIVE STRENGTH STRATEGY
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

df["STRATEGY_RS"] = (

    df["RS_COMPOSITE"]

    .rank(pct=True)

    * 100
)

# =========================================================
# REGIME-ADAPTIVE WEIGHTS
# =========================================================

if market_regime == "BULL_EXPANSION":

    weights = {

        "momentum": 0.30,

        "factor": 0.30,

        "rs": 0.20,

        "quality": 0.10,

        "low_vol": 0.10
    }

elif market_regime == "PANIC":

    weights = {

        "momentum": 0.05,

        "factor": 0.10,

        "rs": 0.10,

        "quality": 0.35,

        "low_vol": 0.40
    }

elif market_regime == "BEAR_DISTRIBUTION":

    weights = {

        "momentum": 0.10,

        "factor": 0.15,

        "rs": 0.15,

        "quality": 0.30,

        "low_vol": 0.30
    }

else:

    weights = {

        "momentum": 0.20,

        "factor": 0.25,

        "rs": 0.20,

        "quality": 0.20,

        "low_vol": 0.15
    }

# =========================================================
# META STRATEGY SCORE
# =========================================================

df["META_SCORE"] = (

    (
        df["STRATEGY_MOMENTUM"]

        * weights["momentum"]
    )

    +

    (
        df["STRATEGY_FACTOR"]

        * weights["factor"]
    )

    +

    (
        df["STRATEGY_RS"]

        * weights["rs"]
    )

    +

    (
        df["STRATEGY_QUALITY"]

        * weights["quality"]
    )

    +

    (
        df["STRATEGY_LOW_VOL"]

        * weights["low_vol"]
    )

)

# =========================================================
# FINAL RANKING
# =========================================================

df = df.sort_values(

    by="META_SCORE",

    ascending=False
)

df["META_RANK"] = range(

    1,

    len(df) + 1
)

# =========================================================
# POSITION WEIGHTS
# =========================================================

TOP_N = 25

portfolio = df.head(TOP_N).copy()

portfolio["RAW_WEIGHT"] = (

    portfolio["META_SCORE"]

    / portfolio["META_SCORE"].sum()
)

portfolio["FINAL_WEIGHT"] = (

    portfolio["RAW_WEIGHT"]

    / portfolio["RAW_WEIGHT"].sum()
)

portfolio["FINAL_WEIGHT"] = (

    portfolio["FINAL_WEIGHT"]

    .round(4)
)

# =========================================================
# ROUNDING
# =========================================================

portfolio["META_SCORE"] = (

    portfolio["META_SCORE"]

    .round(2)
)

# =========================================================
# SAVE
# =========================================================

portfolio.to_csv(

    OUTPUT_FILE,

    index=False
)

# =========================================================
# PORTFOLIO ANALYTICS
# =========================================================

top_sector = (

    portfolio["Sector"]

    .value_counts()

    .idxmax()
)

avg_meta_score = (

    portfolio["META_SCORE"]

    .mean()
)

avg_sharpe = (

    portfolio["Sharpe"]

    .mean()
)

# =========================================================
# OUTPUT
# =========================================================

print(
    "\n✅ AI Meta-Strategy Portfolio Generated"
)

print(
    f"\n📁 Saved To:\n"
    f"{OUTPUT_FILE}"
)

print("\n🏆 META STRATEGY ANALYTICS:\n")

print(
    f"Top Sector: {top_sector}"
)

print(
    f"Average Meta Score: "
    f"{avg_meta_score:.2f}"
)

print(
    f"Average Sharpe: "
    f"{avg_sharpe:.2f}"
)

print("\n🏆 TOP META STRATEGY HOLDINGS:\n")

print(

    portfolio[

        [
            "META_RANK",
            "Symbol",
            "Sector",
            "META_SCORE",
            "FINAL_WEIGHT"
        ]

    ].head(20)
)