import pandas as pd
import numpy as np

from pathlib import Path

# =========================================================
# CONFIG
# =========================================================

TOP_N = 20

MAX_SECTOR_WEIGHT = 0.25

MAX_SINGLE_WEIGHT = 0.10

MIN_ALPHA_SCORE = 0

TARGET_PORTFOLIO_VOL = 0.20

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[1]

RANKINGS_FILE = (
    ROOT_DIR
    / "data"
    / "cross_sectional_rankings.csv"
)

REGIME_FILE = (
    ROOT_DIR
    / "data"
    / "market_regime.csv"
)

OUTPUT_FILE = (
    ROOT_DIR
    / "data"
    / "portfolio_allocation.csv"
)

# =========================================================
# LOAD DATA
# =========================================================

print("\n📥 Loading Data...")

df = pd.read_csv(RANKINGS_FILE)

regime_df = pd.read_csv(REGIME_FILE)

print("✅ Files Loaded")

# =========================================================
# MARKET REGIME
# =========================================================

market_regime = (
    regime_df["MARKET_REGIME"]
    .iloc[0]
)

print(
    f"\n🧠 Market Regime: "
    f"{market_regime}"
)

# =========================================================
# REGIME EXPOSURE
# =========================================================

if market_regime == "RISK_ON":

    gross_exposure = 1.00

elif market_regime == "TRENDING_BULL":

    gross_exposure = 0.80

elif market_regime == "NEUTRAL":

    gross_exposure = 0.50

else:

    gross_exposure = 0.25

# =========================================================
# FILTER STOCKS
# =========================================================

df = df[

    df["ALPHA_SCORE"]

    > MIN_ALPHA_SCORE
]

# =========================================================
# SORT
# =========================================================

df = df.sort_values(

    by="ALPHA_SCORE",

    ascending=False
)

# =========================================================
# TOP STOCKS
# =========================================================

portfolio = df.head(TOP_N).copy()

# =========================================================
# VOLATILITY PROXY
# =========================================================

portfolio["VOL_PROXY"] = (

    portfolio["VOL_ADJ_RS"]

    .abs()

    .replace(0, np.nan)
)

portfolio["VOL_PROXY"] = (

    portfolio["VOL_PROXY"]

    .fillna(
        portfolio["VOL_PROXY"].median()
    )
)

# =========================================================
# INVERSE VOL WEIGHTS
# =========================================================

portfolio["RAW_WEIGHT"] = (

    1
    /
    portfolio["VOL_PROXY"]
)

portfolio["RAW_WEIGHT"] = (

    portfolio["RAW_WEIGHT"]

    / portfolio["RAW_WEIGHT"].sum()
)

# =========================================================
# APPLY MAX SINGLE STOCK CAP
# =========================================================

portfolio["RAW_WEIGHT"] = (

    portfolio["RAW_WEIGHT"]

    .clip(
        upper=MAX_SINGLE_WEIGHT
    )
)

# =========================================================
# RE-NORMALIZE
# =========================================================

portfolio["RAW_WEIGHT"] = (

    portfolio["RAW_WEIGHT"]

    / portfolio["RAW_WEIGHT"].sum()
)

# =========================================================
# APPLY REGIME EXPOSURE
# =========================================================

portfolio["FINAL_WEIGHT"] = (

    portfolio["RAW_WEIGHT"]

    * gross_exposure
)

# =========================================================
# SECTOR CONTROL
# =========================================================

sector_weights = (

    portfolio

    .groupby("Sector")["FINAL_WEIGHT"]

    .sum()
)

overweight_sectors = sector_weights[

    sector_weights > MAX_SECTOR_WEIGHT
]

# =========================================================
# REDUCE OVERWEIGHT SECTORS
# =========================================================

for sector in overweight_sectors.index:

    current_weight = sector_weights[sector]

    reduction_factor = (

        MAX_SECTOR_WEIGHT
        /
        current_weight
    )

    portfolio.loc[

        portfolio["Sector"] == sector,

        "FINAL_WEIGHT"

    ] *= reduction_factor

# =========================================================
# FINAL RE-NORMALIZATION
# =========================================================

portfolio["FINAL_WEIGHT"] = (

    portfolio["FINAL_WEIGHT"]

    / portfolio["FINAL_WEIGHT"].sum()
)

# =========================================================
# PERCENT FORMAT
# =========================================================

portfolio["FINAL_WEIGHT"] = (

    portfolio["FINAL_WEIGHT"]

    * 100
).round(2)

# =========================================================
# EXPECTED PORTFOLIO SCORE
# =========================================================

portfolio_score = round(

    (

        portfolio["ALPHA_SCORE"]

        * portfolio["FINAL_WEIGHT"]

    ).sum()

    / 100,

    4
)

# =========================================================
# FINAL SORT
# =========================================================

portfolio = portfolio.sort_values(

    by="FINAL_WEIGHT",

    ascending=False
)

# =========================================================
# FINAL COLUMNS
# =========================================================

final_cols = [

    "Symbol",

    "Sector",

    "Industry",

    "ALPHA_SCORE",

    "RS_30D",

    "RS_60D",

    "FINAL_WEIGHT"
]

portfolio = portfolio[final_cols]

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

print("\n✅ Portfolio Allocation Generated")

print(
    f"\n📁 Saved to:\n"
    f"{OUTPUT_FILE}"
)

print(
    f"\n🧠 Portfolio Alpha Score: "
    f"{portfolio_score}"
)

print("\n🏆 FINAL PORTFOLIO:\n")

print(portfolio)