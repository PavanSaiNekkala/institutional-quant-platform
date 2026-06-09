import pandas as pd
import numpy as np

from pathlib import Path

# =========================================================
# CONFIG
# =========================================================

INITIAL_CAPITAL = 10_000_000

MAX_POSITION_PCT = 0.10

SLIPPAGE_BPS = 15

BROKERAGE_BPS = 5

IMPACT_FACTOR = 0.000001

MIN_LIQUIDITY = 100000

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    ROOT_DIR
    / "data"
    / "reinforcement_portfolio.csv"
)

OUTPUT_FILE = (
    ROOT_DIR
    / "data"
    / "execution_simulation.csv"
)

# =========================================================
# LOAD DATA
# =========================================================

print("\n📥 Loading Reinforcement Portfolio...")

df = pd.read_csv(INPUT_FILE)

print("✅ Portfolio Loaded")

# =========================================================
# CLEAN COLUMNS
# =========================================================

df.columns = df.columns.str.strip()

# =========================================================
# REQUIRED COLUMNS
# =========================================================

required_cols = [

    "Symbol",

    "WEIGHT"

]

for col in required_cols:

    if col not in df.columns:

        raise Exception(
            f"\n❌ Missing Required Column: {col}"
        )

# =========================================================
# OPTIONAL LIQUIDITY
# =========================================================

if "AvgVolume" not in df.columns:

    df["AvgVolume"] = 500000

# =========================================================
# NORMALIZE WEIGHTS
# =========================================================

df["WEIGHT"] = (

    df["WEIGHT"]

    / df["WEIGHT"].sum()
)

# =========================================================
# POSITION SIZING
# =========================================================

df["TARGET_CAPITAL"] = (

    INITIAL_CAPITAL
    * df["WEIGHT"]
)

# =========================================================
# POSITION LIMITS
# =========================================================

max_position = (

    INITIAL_CAPITAL
    * MAX_POSITION_PCT
)

df["TARGET_CAPITAL"] = np.minimum(

    df["TARGET_CAPITAL"],

    max_position
)

# =========================================================
# EXECUTION COSTS
# =========================================================

df["SLIPPAGE_COST"] = (

    df["TARGET_CAPITAL"]

    * (SLIPPAGE_BPS / 10000)
)

df["BROKERAGE_COST"] = (

    df["TARGET_CAPITAL"]

    * (BROKERAGE_BPS / 10000)
)

# =========================================================
# MARKET IMPACT MODEL
# =========================================================

df["IMPACT_COST"] = (

    (
        df["TARGET_CAPITAL"] ** 1.10
    )

    * IMPACT_FACTOR
)

# =========================================================
# LIQUIDITY CHECK
# =========================================================

df["LIQUIDITY_RATIO"] = (

    df["TARGET_CAPITAL"]

    /

    (
        df["AvgVolume"]
        + 1
    )
)

df["LIQUIDITY_FLAG"] = np.where(

    df["AvgVolume"] < MIN_LIQUIDITY,

    "LOW_LIQUIDITY",

    "OK"
)

# =========================================================
# TOTAL EXECUTION COST
# =========================================================

df["TOTAL_COST"] = (

    df["SLIPPAGE_COST"]

    +

    df["BROKERAGE_COST"]

    +

    df["IMPACT_COST"]
)

# =========================================================
# NET INVESTED CAPITAL
# =========================================================

df["NET_CAPITAL"] = (

    df["TARGET_CAPITAL"]

    -

    df["TOTAL_COST"]
)

# =========================================================
# EXECUTION SCORE
# =========================================================

df["EXECUTION_SCORE"] = (

    100

    -

    (
        (
            df["TOTAL_COST"]
            /
            df["TARGET_CAPITAL"]
        )

        * 100
    )
)

# =========================================================
# ROUNDING
# =========================================================

numeric_cols = [

    "TARGET_CAPITAL",

    "SLIPPAGE_COST",

    "BROKERAGE_COST",

    "IMPACT_COST",

    "TOTAL_COST",

    "NET_CAPITAL",

    "EXECUTION_SCORE",

    "LIQUIDITY_RATIO"
]

df[numeric_cols] = (

    df[numeric_cols]

    .round(2)
)

# =========================================================
# SORT
# =========================================================

df = df.sort_values(

    by="EXECUTION_SCORE",

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
# PORTFOLIO METRICS
# =========================================================

total_cost = (

    df["TOTAL_COST"]

    .sum()
)

net_capital = (

    df["NET_CAPITAL"]

    .sum()
)

avg_execution = (

    df["EXECUTION_SCORE"]

    .mean()
)

# =========================================================
# OUTPUT
# =========================================================

print(
    "\n✅ Institutional Execution Simulation Complete"
)

print(
    f"\n📁 Saved To:\n"
    f"{OUTPUT_FILE}"
)

print("\n🏦 EXECUTION ANALYTICS:\n")

print(
    f"Initial Capital: "
    f"{INITIAL_CAPITAL:,.0f}"
)

print(
    f"Net Invested Capital: "
    f"{net_capital:,.0f}"
)

print(
    f"Total Execution Cost: "
    f"{total_cost:,.0f}"
)

print(
    f"Average Execution Score: "
    f"{avg_execution:.2f}"
)

print("\n🏆 EXECUTION TABLE:\n")

print(

    df[

        [
            "Symbol",
            "WEIGHT",
            "TARGET_CAPITAL",
            "TOTAL_COST",
            "NET_CAPITAL",
            "EXECUTION_SCORE",
            "LIQUIDITY_FLAG"
        ]

    ].head(20)
)
