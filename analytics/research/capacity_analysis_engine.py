from pathlib import Path

import pandas as pd

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

PORTFOLIO_FILE = ROOT / "data" / "portfolio" / "optimised_portfolio.csv"

MASTER_FILE = ROOT / "data" / "processed" / "factor_model_rankings.csv"

OUTPUT_FILE = ROOT / "data" / "processed" / "capacity_report.csv"

# =========================================================
# ASSUMPTIONS
# =========================================================

TEST_CAPITALS = [
    1_000_000,      # 10 lakh
    5_000_000,      # 50 lakh
    10_000_000,     # 1 crore
    25_000_000,     # 2.5 crore
    50_000_000,     # 5 crore
    100_000_000,    # 10 crore
]

MAX_ADV_USAGE = 0.05

# =========================================================
# LOAD DATA
# =========================================================

print("\n📥 Loading Portfolio...")

portfolio = pd.read_csv(PORTFOLIO_FILE)

master = pd.read_csv(MASTER_FILE)

# =========================================================
# VALIDATION
# =========================================================

required_portfolio = ["Symbol"]

missing = [c for c in required_portfolio if c not in portfolio.columns]

if missing:
    raise ValueError(f"Missing columns in portfolio: {missing}")

# =========================================================
# FIND WEIGHT COLUMN
# =========================================================

weight_col = None

for col in ["FINAL_WEIGHT", "OPT_WEIGHT", "RISK_WEIGHT", "TARGET_WEIGHT", "WEIGHT"]:
    if col in portfolio.columns:
        weight_col = col

        break

if weight_col is None:
    raise ValueError("No portfolio weight column found.")

# =========================================================
# FIND LIQUIDITY COLUMN
# =========================================================

adv_col = None

for col in [
    "ADV_RUPEES",
    "TRADED_VALUE",
    "AVG_DAILY_VALUE",
    "AVG_DAILY_TURNOVER",
    "ADV",
]:
    if col in master.columns:
        adv_col = col

        break

if adv_col is None:
    print("\nℹ No ADV column found in factor_model_rankings.csv")
    print("Loading TRADED_VALUE from liquidity_scores.csv")

# =========================================================
# MERGE
# =========================================================

merge_cols = ["Symbol"]

if adv_col:
    merge_cols.append(adv_col)

df = portfolio.merge(
    master[merge_cols],
    on="Symbol",
    how="left",
)

# =========================================================
# RESOLVE ADV COLUMN
# =========================================================

if adv_col:

    possible_cols = [
        adv_col,
        f"{adv_col}_x",
        f"{adv_col}_y",
    ]

    found = None

    for col in possible_cols:
        if col in df.columns:
            found = col
            break

    adv_col = found

# =========================================================
# LOAD LIQUIDITY FILE IF NEEDED
# =========================================================

if adv_col is None:

    liquidity_file = (
        ROOT
        / "data"
        / "processed"
        / "liquidity_scores.csv"
    )

    if not liquidity_file.exists():

        raise FileNotFoundError(
            f"Missing liquidity file:\n{liquidity_file}"
        )

    print("\n📥 Loading Liquidity Scores...")

    liquidity = pd.read_csv(liquidity_file)

    required = [
        "Symbol",
        "TRADED_VALUE",
    ]

    missing = [
        c
        for c in required
        if c not in liquidity.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns in liquidity file: {missing}"
        )

    df = df.merge(
        liquidity[
            [
                "Symbol",
                "TRADED_VALUE",
            ]
        ].rename(
            columns={
                "TRADED_VALUE": "ADV_RUPEES"
            }
        ),
        on="Symbol",
        how="left",
    )

adv_col = "ADV_RUPEES"

# =========================================================
# CLEAN ADV DATA
# =========================================================

df[adv_col] = pd.to_numeric(
    df[adv_col],
    errors="coerce",
)

df = df[
    df[adv_col] > 0
].copy()

if len(df) == 0:

    raise ValueError(
        "No securities with positive liquidity."
    )
# =========================================================
# NORMALIZE WEIGHTS
# =========================================================

df[weight_col] = df[weight_col] / df[weight_col].sum()

# =========================================================
# CAPACITY CALCULATIONS
# =========================================================

results = []

for capital in TEST_CAPITALS:
    temp = df.copy()

    temp["PORTFOLIO_CAPITAL"] = capital

    temp["POSITION_VALUE"] = temp[weight_col] * capital

    temp["ADV_USAGE"] = temp["POSITION_VALUE"] / temp[adv_col]

    temp["DAYS_TO_EXIT"] = temp["POSITION_VALUE"] / (temp[adv_col] * MAX_ADV_USAGE)

    max_adv = round(temp["ADV_USAGE"].max() * 100, 2)

    avg_days = round(temp["DAYS_TO_EXIT"].mean(), 2)

    bottleneck_stock = temp.loc[
        temp["ADV_USAGE"].idxmax(),
        "Symbol"
    ]

    portfolio_capacity = (
        temp[adv_col] * MAX_ADV_USAGE
    ) / temp[weight_col]

    max_capacity = portfolio_capacity.min()

    results.append(
        {
            "Capital": capital,
            "Max_ADV_Usage_%": max_adv,
            "Avg_Days_To_Exit": avg_days,
            "Bottleneck_Stock": bottleneck_stock,
            "Estimated_Max_Capacity": round(max_capacity, 0),
            "Pass_5pct_ADV_Rule": max_adv <= 5,
        }
    )

# =========================================================
# SUMMARY
# =========================================================

summary = pd.DataFrame(results)

# =========================================================
# CAPACITY RATING
# =========================================================

largest_ok = summary[summary["Pass_5pct_ADV_Rule"]]

if len(largest_ok) > 0:
    max_capital = int(largest_ok["Capital"].max())

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

summary.to_csv(OUTPUT_FILE, index=False)

# =========================================================
# REPORT
# =========================================================

print("\n✅ Capacity Analysis Complete")

print(f"\n📁 Saved: {OUTPUT_FILE}")

print("\n🏆 Capacity Summary:\n")

print(summary)

print(f"\nMaximum Deployable Capital: ₹{max_capital:,.0f}")

print(f"Capacity Rating: {rating}")
