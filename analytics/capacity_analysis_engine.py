import pandas as pd
import numpy as np
from pathlib import Path

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parent.parent

PORTFOLIO_FILE = (
    ROOT
    / "data"
    / "optimised_portfolio.csv"
)

MASTER_FILE = (
    ROOT
    / "data"
    / "factor_model_rankings.csv"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "capacity_report.csv"
)

# =========================================================
# ASSUMPTIONS
# =========================================================

TEST_CAPITALS = [

    1_000_000,      # 10 Lakh
    5_000_000,      # 50 Lakh
    10_000_000,     # 1 Crore
    50_000_000,     # 5 Crore
    100_000_000     # 10 Crore

]

MAX_ADV_USAGE = 0.05

# =========================================================
# LOAD DATA
# =========================================================

print(
    "\n📥 Loading Portfolio..."
)

portfolio = pd.read_csv(
    PORTFOLIO_FILE
)

master = pd.read_csv(
    MASTER_FILE
)

# =========================================================
# VALIDATION
# =========================================================

required_portfolio = [
    "Symbol"
]

missing = [

    c for c in required_portfolio

    if c not in portfolio.columns

]

if missing:

    raise ValueError(
        f"Missing columns in portfolio: {missing}"
    )

# =========================================================
# FIND WEIGHT COLUMN
# =========================================================

weight_col = None

for col in [

    "FINAL_WEIGHT",
    "OPT_WEIGHT",
    "RISK_WEIGHT",
    "TARGET_WEIGHT",
    "WEIGHT"

]:

    if col in portfolio.columns:

        weight_col = col

        break

if weight_col is None:

    raise ValueError(
        "No portfolio weight column found."
    )

# =========================================================
# FIND LIQUIDITY COLUMN
# =========================================================

adv_col = None

for col in [

    "AVG_DAILY_VALUE",
    "AVG_DAILY_TURNOVER",
    "ADV",
    "LIQUIDITY_SCORE"

]:

    if col in master.columns:

        adv_col = col

        break

if adv_col is None:

    print(
        "\n⚠ No ADV column found."
    )

    print(
        "Using LIQUIDITY_SCORE proxy."
    )

# =========================================================
# MERGE
# =========================================================

merge_cols = ["Symbol"]

if adv_col:

    merge_cols.append(
        adv_col
    )

df = portfolio.merge(

    master[merge_cols],

    on="Symbol",

    how="left"

)

# =========================================================
# CREATE ADV IF MISSING
# =========================================================

if adv_col is None:

    df["ADV_PROXY"] = 1_00_00_000

    adv_col = "ADV_PROXY"

# =========================================================
# NORMALIZE WEIGHTS
# =========================================================

df[weight_col] = (

    df[weight_col]

    / df[weight_col].sum()

)

# =========================================================
# CAPACITY CALCULATIONS
# =========================================================

results = []

for capital in TEST_CAPITALS:

    temp = df.copy()

    temp["PORTFOLIO_CAPITAL"] = capital

    temp["POSITION_VALUE"] = (

        temp[weight_col]

        * capital

    )

    temp["ADV_USAGE"] = (

        temp["POSITION_VALUE"]

        / temp[adv_col]

    )

    temp["DAYS_TO_EXIT"] = (

        temp["POSITION_VALUE"]

        / (

            temp[adv_col]

            * MAX_ADV_USAGE

        )

    )

    max_adv = round(

        temp["ADV_USAGE"].max()
        * 100,

        2

    )

    avg_days = round(

        temp["DAYS_TO_EXIT"].mean(),

        2

    )

    results.append({

        "Capital": capital,

        "Max_ADV_Usage_%": max_adv,

        "Avg_Days_To_Exit": avg_days,

        "Pass_5pct_ADV_Rule":
            max_adv <= 5

    })

# =========================================================
# SUMMARY
# =========================================================

summary = pd.DataFrame(
    results
)

# =========================================================
# CAPACITY RATING
# =========================================================

largest_ok = summary[
    summary[
        "Pass_5pct_ADV_Rule"
    ]
]

if len(largest_ok) > 0:

    max_capital = int(

        largest_ok["Capital"]

        .max()

    )

else:

    max_capital = 0

if max_capital >= 100_000_000:

    rating = "HIGH"

elif max_capital >= 10_000_000:

    rating = "MEDIUM"

else:

    rating = "LOW"

summary["Capacity_Rating"] = rating

# =========================================================
# SAVE
# =========================================================

summary.to_csv(

    OUTPUT_FILE,

    index=False

)

# =========================================================
# REPORT
# =========================================================

print(
    "\n✅ Capacity Analysis Complete"
)

print(
    f"\n📁 Saved: {OUTPUT_FILE}"
)

print(
    "\n🏆 Capacity Summary:\n"
)

print(summary)

print(
    f"\nMaximum Deployable Capital: ₹{max_capital:,.0f}"
)

print(
    f"Capacity Rating: {rating}"
)
