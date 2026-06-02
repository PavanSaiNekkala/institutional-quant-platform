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

MASTER_FILE = (
    ROOT
    / "data"
    / "factor_model_rankings.csv"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "sector_controlled_portfolio.csv"
)

# =========================================================
# SETTINGS
# =========================================================

MAX_SECTOR_STOCKS = 5

# =========================================================
# LOAD DATA
# =========================================================

print("\n📥 Loading Portfolio...")

portfolio = pd.read_csv(
    PORTFOLIO_FILE
)

master = pd.read_csv(
    MASTER_FILE
)

# =========================================================
# SYMBOL CLEANUP
# =========================================================

portfolio["Symbol"] = (

    portfolio["Symbol"]

    .astype(str)

    .str.upper()

    .str.strip()

)

master["Symbol"] = (

    master["Symbol"]

    .astype(str)

    .str.upper()

    .str.strip()

)

# =========================================================
# ADD SECTOR DATA
# =========================================================

df = portfolio.merge(

    master[
        [
            "Symbol",
            "Sector",
            "Industry"
        ]
    ],

    on="Symbol",

    how="left"

)

# =========================================================
# VALIDATION
# =========================================================

required_cols = [

    "Symbol",

    "Sector",

    "FINAL_WEIGHT"

]

missing = [

    c for c in required_cols

    if c not in df.columns

]

if missing:

    raise ValueError(

        f"Missing columns: {missing}"

    )

# =========================================================
# SORT BY PORTFOLIO WEIGHT
# =========================================================

df = df.sort_values(

    by="FINAL_WEIGHT",

    ascending=False

).reset_index(drop=True)

# =========================================================
# SECTOR CONTROL
# =========================================================

final_rows = []

sector_counter = {}

for _, row in df.iterrows():

    sector = str(

        row["Sector"]

    ).upper()

    count = sector_counter.get(

        sector,

        0

    )

    if count < MAX_SECTOR_STOCKS:

        final_rows.append(

            row

        )

        sector_counter[sector] = (

            count + 1

        )

# =========================================================
# CREATE FINAL DF
# =========================================================

final_df = pd.DataFrame(

    final_rows

)

# =========================================================
# RENORMALIZE WEIGHTS
# =========================================================

final_df["FINAL_WEIGHT"] = (

    final_df["FINAL_WEIGHT"]

    /

    final_df["FINAL_WEIGHT"].sum()

)

final_df["FINAL_WEIGHT_%"] = (

    final_df["FINAL_WEIGHT"]

    * 100

).round(2)

# =========================================================
# SAVE
# =========================================================

final_df.to_csv(

    OUTPUT_FILE,

    index=False

)

# =========================================================
# REPORT
# =========================================================

print(

    "\n✅ Sector Exposure Control Complete"

)

print(

    "\n📁 Saved:"
)

print(

    OUTPUT_FILE

)

print(

    "\n📊 Sector Allocation:\n"

)

print(

    final_df["Sector"]

    .value_counts()

)

print(

    "\n🏆 Top Holdings:\n"

)

print(

    final_df[
        [
            "Symbol",
            "Sector",
            "FINAL_WEIGHT_%"
        ]
    ]

    .head(20)

)

print(

    "\nTotal Weight:",

    round(
        final_df["FINAL_WEIGHT_%"].sum(),
        2
    ),

    "%"
)