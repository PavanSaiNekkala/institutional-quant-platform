import pandas as pd
import numpy as np
from pathlib import Path

# =========================================================
# FILES
# =========================================================

ROOT = Path(__file__).resolve().parent.parent

CURRENT_FILE = (
    ROOT
    / "data"
    / "current_portfolio.csv"
)

TARGET_FILE = (
    ROOT
    / "data"
    / "risk_parity_portfolio.csv"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "rebalance_plan.csv"
)

# =========================================================
# SETTINGS
# =========================================================

REBALANCE_THRESHOLD = 0.02

# =========================================================
# LOAD
# =========================================================

print("\n📥 Loading Portfolios...")

target_df = pd.read_csv(
    TARGET_FILE
)

# =========================================================
# FIRST RUN
# =========================================================

if not CURRENT_FILE.exists():

    print(
        "\n⚠️ No current portfolio found."
    )

    first_portfolio = target_df[
        [
            "Symbol",
            "FINAL_WEIGHT"
        ]
    ].copy()

    first_portfolio.to_csv(
        CURRENT_FILE,
        index=False
    )

    print(
        "\n✅ Initial Portfolio Created"
    )

    raise SystemExit()

# =========================================================
# LOAD CURRENT
# =========================================================

current_df = pd.read_csv(
    CURRENT_FILE
)

# =========================================================
# CLEAN
# =========================================================

for df in [current_df, target_df]:

    df["Symbol"] = (
        df["Symbol"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

# =========================================================
# REDUCE COLUMNS
# =========================================================

if "FINAL_WEIGHT" not in current_df.columns:

    print(
        "\n⚠️ FINAL_WEIGHT not found in current portfolio."
    )

    print(
        "Creating equal weights..."
    )

    current_df["FINAL_WEIGHT"] = (

        1

        /

        len(current_df)
    )

current_df = current_df[
    [
        "Symbol",
        "FINAL_WEIGHT"
    ]
]
target_df = target_df[
    [
        "Symbol",
        "FINAL_WEIGHT"
    ]
]

# =========================================================
# MERGE
# =========================================================

merged = pd.merge(

    current_df,

    target_df,

    on="Symbol",

    how="outer",

    suffixes=(

        "_CURRENT",

        "_TARGET"
    )
)

merged = merged.fillna(0)

# =========================================================
# WEIGHT CHANGE
# =========================================================

merged["WEIGHT_CHANGE"] = (

    merged["FINAL_WEIGHT_TARGET"]

    -

    merged["FINAL_WEIGHT_CURRENT"]
)

# =========================================================
# ACTION LOGIC
# =========================================================

def get_action(change):

    if change > REBALANCE_THRESHOLD:

        return "BUY"

    elif change < -REBALANCE_THRESHOLD:

        return "SELL"

    else:

        return "HOLD"

merged["ACTION"] = (

    merged["WEIGHT_CHANGE"]

    .apply(get_action)
)

# =========================================================
# TURNOVER
# =========================================================

turnover = (

    merged["WEIGHT_CHANGE"]
    .abs()
    .sum()

    / 2
)

# =========================================================
# SORT
# =========================================================

merged = merged.sort_values(

    by="WEIGHT_CHANGE",

    ascending=False
)

# =========================================================
# SAVE
# =========================================================

merged.to_csv(

    OUTPUT_FILE,

    index=False
)

# =========================================================
# UPDATE CURRENT PORTFOLIO
# =========================================================

target_df.to_csv(

    CURRENT_FILE,

    index=False
)

# =========================================================
# REPORT
# =========================================================

print("\n✅ Rebalance Complete")

print("\n📁 Saved:")

print(
    OUTPUT_FILE
)

print(

    f"\n🔄 Portfolio Turnover: "
    f"{turnover*100:.2f}%"
)

print("\n🏆 Rebalance Actions:\n")

print(

    merged[
        [
            "Symbol",
            "FINAL_WEIGHT_CURRENT",
            "FINAL_WEIGHT_TARGET",
            "WEIGHT_CHANGE",
            "ACTION"
        ]
    ]

    .head(30)

)