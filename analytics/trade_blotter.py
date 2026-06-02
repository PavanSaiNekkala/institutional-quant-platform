import pandas as pd
from pathlib import Path

# =========================================================
# FILES
# =========================================================

ROOT = Path(__file__).resolve().parent.parent

PORTFOLIO_FILE = (
    ROOT
    / "data"
    / "risk_parity_portfolio.csv"
)

REBALANCE_FILE = (
    ROOT
    / "data"
    / "rebalance_plan.csv"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "trade_blotter.csv"
)

# =========================================================
# SETTINGS
# =========================================================

PORTFOLIO_VALUE = 1000000

# =========================================================
# LOAD
# =========================================================

print("\n📥 Loading Portfolio...")

portfolio = pd.read_csv(
    PORTFOLIO_FILE
)

rebalance = pd.read_csv(
    REBALANCE_FILE
)

# =========================================================
# TARGET WEIGHTS
# =========================================================

portfolio = portfolio[
    [
        "Symbol",
        "FINAL_WEIGHT"
    ]
]

# =========================================================
# TARGET VALUE
# =========================================================

portfolio["TARGET_VALUE"] = (

    portfolio["FINAL_WEIGHT"]

    *

    PORTFOLIO_VALUE

).round(0)

# =========================================================
# MERGE
# =========================================================

df = portfolio.merge(

    rebalance[
        [
            "Symbol",
            "ACTION"
        ]
    ],

    on="Symbol",

    how="left"
)

# =========================================================
# DEFAULT ACTION
# =========================================================

df["ACTION"] = (

    df["ACTION"]

    .fillna("BUY")
)

# =========================================================
# ORDER SIZE
# =========================================================

df["ORDER_VALUE"] = (

    df["TARGET_VALUE"]

).round(0)

# =========================================================
# SORT
# =========================================================

df = df.sort_values(

    by="ORDER_VALUE",

    ascending=False
)

# =========================================================
# SAVE
# =========================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)

# =========================================================
# REPORT
# =========================================================

print("\n✅ Trade Blotter Created")

print("\n📁 Saved:")

print(OUTPUT_FILE)

print("\n🏆 Orders:\n")

print(

    df[
        [
            "Symbol",
            "ACTION",
            "ORDER_VALUE"
        ]
    ]

    .head(20)
)