# =========================================================
# EXPECTED RETURN ENGINE
# =========================================================

from pathlib import Path

import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "factor_model_rankings.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "expected_returns.csv"
)

# =========================================================
# LOAD
# =========================================================

print("\n📥 Loading Factor Model Rankings...")

df = pd.read_csv(INPUT_FILE)

print("✅ Data Loaded")

print("\n===== INPUT CHECK =====")

required_cols = [
    "Symbol",
    "Momentum",
    "Sharpe",
    "RS_30D",
    "RS_60D",
    "ALPHA_SCORE",
    "MULTI_FACTOR_SCORE",
]

missing = [
    c for c in required_cols
    if c not in df.columns
]

if missing:
    raise ValueError(
        f"Missing Columns: {missing}"
    )

print(
    df[
        [
            "Symbol",
            "Momentum",
            "Sharpe",
            "ALPHA_SCORE",
            "MULTI_FACTOR_SCORE",
        ]
    ].head(10)
)

# =========================================================
# NUMERIC CLEAN
# =========================================================

numeric_cols = [
    "Momentum",
    "Sharpe",
    "RS_30D",
    "RS_60D",
    "ALPHA_SCORE",
    "MULTI_FACTOR_SCORE",
]

for col in numeric_cols:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

    df[col] = df[col].fillna(0)

# =========================================================
# PREDICTION SCORE
# =========================================================

print(
    "\n🧠 Building Prediction Engine..."
)

df["PREDICTION_SCORE"] = (

      df["ALPHA_SCORE"] * 0.35

    + df["MULTI_FACTOR_SCORE"] * 0.35

    + df["RS_30D"] * 0.15

    + df["RS_60D"] * 0.10

    + df["Momentum"] * 0.05

)

# =========================================================
# NORMALIZATION
# =========================================================

scaler = MinMaxScaler()

df["PRED_SCORE_NORM"] = (
    scaler.fit_transform(
        df[["PREDICTION_SCORE"]]
    )
)

# =========================================================
# EXPECTED RETURNS
# =========================================================

print(
    "\n📈 Calculating Expected Returns..."
)

df["EXPECTED_RETURN_5D"] = (
    1
    + (
        df["PRED_SCORE_NORM"]
        * 4
    )
)

df["EXPECTED_RETURN_15D"] = (
    df["EXPECTED_RETURN_5D"]
    * 2.2
)

df["EXPECTED_RETURN_30D"] = (
    df["EXPECTED_RETURN_5D"]
    * 3.5
)

# =========================================================
# HOLDING PERIOD
# =========================================================

df["EST_HOLD_DAYS"] = (

    10

    +

    (
        df["PRED_SCORE_NORM"]
        * 25
    )

).round(0).astype(int)

# =========================================================
# SIGNAL ENGINE
# =========================================================

def signal(score):

    if score >= 0.90:
        return "STRONG BUY"

    elif score >= 0.75:
        return "BUY"

    elif score >= 0.55:
        return "HOLD"

    elif score >= 0.35:
        return "REDUCE"

    return "EXIT"


df["SIGNAL"] = (
    df["PRED_SCORE_NORM"]
    .apply(signal)
)

# =========================================================
# ROUNDING
# =========================================================

for col in [
    "EXPECTED_RETURN_5D",
    "EXPECTED_RETURN_15D",
    "EXPECTED_RETURN_30D",
]:
    df[col] = df[col].round(2)

df["PREDICTION_SCORE"] = (
    df["PREDICTION_SCORE"]
    .round(4)
)

df["PRED_SCORE_NORM"] = (
    df["PRED_SCORE_NORM"]
    .round(4)
)

# =========================================================
# SORT
# =========================================================

df = df.sort_values(
    by="PREDICTION_SCORE",
    ascending=False
)

df["PREDICTION_RANK"] = (
    range(
        1,
        len(df) + 1
    )
)

# =========================================================
# SAVE
# =========================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)

# =========================================================
# OUTPUT
# =========================================================

print(
    "\n✅ Expected Return Engine Complete"
)

print(
    f"\n📁 Saved To:\n{OUTPUT_FILE}"
)

print(
    "\n🏆 TOP PREDICTIONS:\n"
)

print(

    df[
        [
            "PREDICTION_RANK",
            "Symbol",
            "SIGNAL",
            "EXPECTED_RETURN_5D",
            "EXPECTED_RETURN_15D",
            "EXPECTED_RETURN_30D",
            "EST_HOLD_DAYS",
        ]
    ]
    .head(20)

)
