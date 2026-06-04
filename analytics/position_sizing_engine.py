import pandas as pd
from pathlib import Path

# =========================================================
# FILES
# =========================================================

ROOT = Path(__file__).resolve().parent.parent

PORTFOLIO_FILE = (
    ROOT
    / "data"
    / "sector_controlled_portfolio.csv"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "position_sized_portfolio.csv"
)

# =========================================================
# SETTINGS
# =========================================================

MAX_WEIGHT = 0.10
MIN_WEIGHT = 0.02

# =========================================================
# LOAD DATA
# =========================================================

print("\n📥 Loading Portfolio...")

portfolio_df = pd.read_csv(
    PORTFOLIO_FILE
)

df = portfolio_df.copy()

# =========================================================
# FILL MISSING
# =========================================================

df["CONVICTION_SCORE"] = (
    df["CONVICTION_SCORE"]
    .fillna(0)
)

df["EXPECTED_RETURN_30D"] = (
    df["EXPECTED_RETURN_30D"]
    .fillna(0)
)

df["ENTRY_SCORE"] = (
    df["ENTRY_SCORE"]
    .fillna(0)
)

# =========================================================
# POSITION SCORE
# =========================================================

df["POSITION_SCORE"] = (

    df["CONVICTION_SCORE"] * 0.50

    +

    df["EXPECTED_RETURN_30D"] * 3.00

    +

    df["ENTRY_SCORE"] * 2.00

)

# =========================================================
# NORMALIZED WEIGHTS
# =========================================================

total_score = (
    df["POSITION_SCORE"]
    .sum()
)
if total_score <= 0:

    raise ValueError(
        "POSITION_SCORE total is zero."
    )
df["TARGET_WEIGHT"] = (

    df["POSITION_SCORE"]

    /

    total_score
)

# =========================================================
# APPLY LIMITS
# =========================================================

df["TARGET_WEIGHT"] = (

    df["TARGET_WEIGHT"]

    .clip(
        lower=MIN_WEIGHT,
        upper=MAX_WEIGHT
    )
)

df["TARGET_WEIGHT"] = (

    df["TARGET_WEIGHT"]

    /

    df["TARGET_WEIGHT"].sum()
)

# =========================================================
# PERCENT FORMAT
# =========================================================

df["TARGET_WEIGHT_%"] = (

    df["TARGET_WEIGHT"]

    * 100

).round(2)

# =========================================================
# SORT
# =========================================================

df = df.sort_values(

    by="TARGET_WEIGHT",

    ascending=False
)

# =========================================================
# SAVE
# =========================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n✅ Position Sizing Complete")

print("\n📁 Saved:")

print(
    OUTPUT_FILE
)

print("\n🏆 Portfolio Weights:\n")

print(

    df[
        [
            "Symbol",
            "TARGET_WEIGHT_%",
            "CONVICTION_SCORE",
            "EXPECTED_RETURN_30D"
        ]
    ]

    .head(20)
)
