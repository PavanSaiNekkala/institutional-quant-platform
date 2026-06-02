import pandas as pd
from pathlib import Path

# =========================================================
# FILES
# =========================================================

ROOT = Path(__file__).resolve().parent.parent

PORTFOLIO_FILE = (
    ROOT
    / "data"
    / "optimised_portfolio.csv"
)

FACTOR_FILE = (
    ROOT
    / "data"
    / "factor_model_rankings.csv"
)

EXPECTED_FILE = (
    ROOT
    / "data"
    / "expected_returns.csv"
)

OUTPUT_ATTRIBUTION = (
    ROOT
    / "data"
    / "factor_attribution.csv"
)

OUTPUT_STOCK_ATTRIBUTION = (
    ROOT
    / "data"
    / "factor_attribution_by_stock.csv"
)

# =========================================================
# LOAD
# =========================================================

print("\n📥 Loading Data...")

portfolio = pd.read_csv(
    PORTFOLIO_FILE
)

factor_df = pd.read_csv(
    FACTOR_FILE
)

expected_df = pd.read_csv(
    EXPECTED_FILE
)

# =========================================================
# SYMBOL CLEANUP
# =========================================================

for df in [
    portfolio,
    factor_df,
    expected_df
]:

    df["Symbol"] = (
        df["Symbol"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

# =========================================================
# MERGE
# =========================================================

df = portfolio.merge(

    factor_df[
        [
            "Symbol",
            "FACTOR_MOMENTUM",
            "FACTOR_SHARPE",
            "FACTOR_ALPHA",
            "FACTOR_RS",
            "FACTOR_SECTOR",
            "FACTOR_ENTRY",
            "FACTOR_LIQUIDITY"
        ]
    ],

    on="Symbol",

    how="left"
)

# =========================================================
# ADD EXPECTED RETURN ONLY IF MISSING
# =========================================================

if "EXPECTED_RETURN_30D" not in df.columns:

    df = df.merge(

        expected_df[
            [
                "Symbol",
                "EXPECTED_RETURN_30D"
            ]
        ],

        on="Symbol",

        how="left"
    )

else:

    print(
        "\n✅ EXPECTED_RETURN_30D already available"
    )
# =========================================================
# FILL NA
# =========================================================

factor_cols = [

    "FACTOR_MOMENTUM",
    "FACTOR_SHARPE",
    "FACTOR_ALPHA",
    "FACTOR_RS",
    "FACTOR_SECTOR",
    "FACTOR_ENTRY",
    "FACTOR_LIQUIDITY",
    "EXPECTED_RETURN_30D"
]

for col in factor_cols:

    df[col] = (
        df[col]
        .fillna(0)
    )

# =========================================================
# DETECT WEIGHT COLUMN
# =========================================================

if "FINAL_WEIGHT" in df.columns:

    weight_col = "FINAL_WEIGHT"

elif "TARGET_WEIGHT" in df.columns:

    weight_col = "TARGET_WEIGHT"

else:

    raise ValueError(
        "No portfolio weight column found."
    )

print(
    f"\nUsing weight column: {weight_col}"
)

# =========================================================
# STOCK LEVEL ATTRIBUTION
# =========================================================

df["MOMENTUM_ATTR"] = (
    df[weight_col]
    *
    df["FACTOR_MOMENTUM"]
)

df["SHARPE_ATTR"] = (
    df[weight_col]
    *
    df["FACTOR_SHARPE"]
)

df["ALPHA_ATTR"] = (
    df[weight_col]
    *
    df["FACTOR_ALPHA"]
)

df["RS_ATTR"] = (
    df[weight_col]
    *
    df["FACTOR_RS"]
)

df["SECTOR_ATTR"] = (
    df[weight_col]
    *
    df["FACTOR_SECTOR"]
)

df["ENTRY_ATTR"] = (
    df[weight_col]
    *
    df["FACTOR_ENTRY"]
)

df["LIQUIDITY_ATTR"] = (
    df[weight_col]
    *
    df["FACTOR_LIQUIDITY"]
)

df["EXPECTED_RETURN_ATTR"] = (
    df[weight_col]
    *
    df["EXPECTED_RETURN_30D"]
)

# =========================================================
# PORTFOLIO LEVEL ATTRIBUTION
# =========================================================

summary = pd.DataFrame({

    "Factor": [

        "Momentum",
        "Sharpe",
        "Alpha",
        "Relative Strength",
        "Sector",
        "Entry Quality",
        "Liquidity",
        "Expected Return"
    ],

    "Contribution": [

        df["MOMENTUM_ATTR"].sum(),
        df["SHARPE_ATTR"].sum(),
        df["ALPHA_ATTR"].sum(),
        df["RS_ATTR"].sum(),
        df["SECTOR_ATTR"].sum(),
        df["ENTRY_ATTR"].sum(),
        df["LIQUIDITY_ATTR"].sum(),
        df["EXPECTED_RETURN_ATTR"].sum()
    ]
})

summary["Contribution"] = (
    summary["Contribution"]
    .round(4)
)

summary = summary.sort_values(

    by="Contribution",

    ascending=False

).reset_index(drop=True)

# =========================================================
# SAVE SUMMARY
# =========================================================

summary.to_csv(

    OUTPUT_ATTRIBUTION,

    index=False
)

# =========================================================
# SAVE STOCK ATTRIBUTION
# =========================================================

stock_output = df[

    [
        "Symbol",

        "MOMENTUM_ATTR",
        "SHARPE_ATTR",
        "ALPHA_ATTR",
        "RS_ATTR",
        "SECTOR_ATTR",
        "ENTRY_ATTR",
        "LIQUIDITY_ATTR",
        "EXPECTED_RETURN_ATTR"
    ]

].copy()

stock_output.to_csv(

    OUTPUT_STOCK_ATTRIBUTION,

    index=False
)

# =========================================================
# REPORT
# =========================================================

print(
    "\n✅ Factor Attribution Complete"
)

print(
    "\n📁 Saved:"
)

print(
    OUTPUT_ATTRIBUTION
)

print(
    OUTPUT_STOCK_ATTRIBUTION
)

print(
    "\n🏆 Factor Contribution:\n"
)

print(
    summary
)