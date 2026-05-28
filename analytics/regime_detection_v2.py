import pandas as pd
import numpy as np

from pathlib import Path

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    ROOT_DIR
    / "data"
    / "factor_model_rankings.csv"
)

OUTPUT_FILE = (
    ROOT_DIR
    / "data"
    / "market_regime_v2.csv"
)

# =========================================================
# LOAD DATA
# =========================================================

print("\n📥 Loading Factor Model Data...")

df = pd.read_csv(INPUT_FILE)

print("✅ Data Loaded")

# =========================================================
# CLEAN COLUMNS
# =========================================================

df.columns = df.columns.str.strip()

# =========================================================
# REQUIRED COLUMNS
# =========================================================

required_cols = [

    "Momentum",

    "Sharpe",

    "MULTI_FACTOR_SCORE"

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
# MARKET BREADTH
# =========================================================

breadth = (

    (
        df["Momentum"] > 0
    )

    .mean()
)

# =========================================================
# AVERAGE FACTOR STRENGTH
# =========================================================

avg_factor_score = (

    df["MULTI_FACTOR_SCORE"]

    .mean()
)

# =========================================================
# SHARPE ENVIRONMENT
# =========================================================

avg_sharpe = (

    df["Sharpe"]

    .mean()
)

# =========================================================
# VOLATILITY REGIME
# =========================================================

if "VOL_ADJ_RS" in df.columns:

    avg_volatility = (

        df["VOL_ADJ_RS"]

        .mean()
    )

else:

    avg_volatility = 1

# =========================================================
# RS ENVIRONMENT
# =========================================================

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

    rs_strength = (

        df[existing_rs_cols]

        .mean()

        .mean()
    )

else:

    rs_strength = 0

# =========================================================
# REGIME CLASSIFICATION
# =========================================================

if (

    breadth > 0.70
    and
    avg_factor_score > 75
    and
    avg_sharpe > 1

):

    regime = "BULL_EXPANSION"

elif (

    breadth > 0.60
    and
    avg_factor_score > 65

):

    regime = "BULL_WEAKENING"

elif (

    breadth < 0.30
    and
    avg_sharpe < 0

):

    regime = "PANIC"

elif (

    breadth < 0.40
    and
    avg_factor_score < 40

):

    regime = "BEAR_DISTRIBUTION"

elif (

    avg_volatility > 2

):

    regime = "SIDEWAYS_HIGH_VOL"

elif (

    avg_volatility <= 2
    and
    breadth >= 0.40
    and
    breadth <= 0.60

):

    regime = "SIDEWAYS_LOW_VOL"

else:

    regime = "RECOVERY"

# =========================================================
# REGIME SCORE
# =========================================================

regime_score = (

    (
        breadth * 30
    )

    +

    (
        avg_factor_score * 0.40
    )

    +

    (
        avg_sharpe * 10
    )

)

# =========================================================
# OUTPUT DATAFRAME
# =========================================================

regime_df = pd.DataFrame({

    "MARKET_REGIME": [regime],

    "REGIME_SCORE": [

        round(regime_score, 2)
    ],

    "MARKET_BREADTH": [

        round(breadth, 4)
    ],

    "AVG_FACTOR_SCORE": [

        round(avg_factor_score, 2)
    ],

    "AVG_SHARPE": [

        round(avg_sharpe, 2)
    ],

    "AVG_VOLATILITY": [

        round(avg_volatility, 4)
    ],

    "RS_ENVIRONMENT": [

        round(rs_strength, 4)
    ]

})

# =========================================================
# SAVE
# =========================================================

regime_df.to_csv(

    OUTPUT_FILE,

    index=False
)

# =========================================================
# OUTPUT
# =========================================================

print(
    "\n✅ Institutional Regime Detection Complete"
)

print(
    f"\n📁 Saved To:\n"
    f"{OUTPUT_FILE}"
)

print("\n🌍 CURRENT MARKET REGIME:\n")

print(regime_df)