import pandas as pd
from pathlib import Path
from datetime import datetime

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

PORTFOLIO_FILE = (
    ROOT
    / "data"
    / "optimised_portfolio.csv"
)

REGIME_FILE = (
    ROOT
    / "data"
    / "market_regime.csv"
)

PARQUET_FILE = (
    ROOT
    / "data"
    / "historical_signals.parquet"
)

CSV_FILE = (
    ROOT
    / "data"
    / "historical_signals.csv"
)

# =========================================================
# LOAD DATA
# =========================================================

print("\n📥 Loading Signals...")

portfolio = pd.read_csv(
    PORTFOLIO_FILE
)

# =========================================================
# REGIME
# =========================================================

regime = "UNKNOWN"

if REGIME_FILE.exists():

    try:

        regime_df = pd.read_csv(
            REGIME_FILE
        )

        for col in regime_df.columns:

            if "REGIME" in col.upper():

                regime = str(
                    regime_df[col].iloc[0]
                )

                break

    except Exception:

        pass

# =========================================================
# FIND COLUMNS
# =========================================================

def get_col(options):

    for col in options:

        if col in portfolio.columns:

            return col

    return None


rank_col = get_col([
    "FACTOR_RANK",
    "PREDICTION_RANK",
    "ALPHA_RANK",
    "RANK"
])

score_col = get_col([
    "MULTI_FACTOR_SCORE",
    "CONVICTION_SCORE",
    "PREDICTION_SCORE"
])

return_col = get_col([
    "EXPECTED_RETURN_30D",
    "EXPECTED_RETURN_15D",
    "EXPECTED_RETURN_5D"
])

weight_col = get_col([
    "FINAL_WEIGHT",
    "OPT_WEIGHT",
    "RISK_WEIGHT",
    "TARGET_WEIGHT",
    "WEIGHT"
])

# =========================================================
# BUILD SIGNAL TABLE
# =========================================================

signals = pd.DataFrame()

signals["DATE"] = [
    datetime.now().strftime(
        "%Y-%m-%d"
    )
] * len(portfolio)

signals["TIMESTAMP"] = [
    datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )
] * len(portfolio)

signals["REGIME"] = [
    regime
] * len(portfolio)

signals["SYMBOL"] = portfolio["Symbol"]

# Optional fields

if rank_col:

    signals["RANK"] = (
        portfolio[rank_col]
    )

if score_col:

    signals["SCORE"] = (
        portfolio[score_col]
    )

if return_col:

    signals["EXPECTED_RETURN"] = (
        portfolio[return_col]
    )

if weight_col:

    signals["WEIGHT"] = (
        portfolio[weight_col]
    )

# =========================================================
# APPEND HISTORY
# =========================================================

if PARQUET_FILE.exists():

    try:

        history = pd.read_parquet(
            PARQUET_FILE
        )

        history = pd.concat(

            [
                history,
                signals
            ],

            ignore_index=True

        )

    except Exception:

        history = signals

else:

    history = signals

# =========================================================
# REMOVE DUPLICATES
# =========================================================

history = history.drop_duplicates(

    subset=[
        "DATE",
        "SYMBOL"
    ],

    keep="last"

)

# =========================================================
# SORT
# =========================================================

history = history.sort_values(

    by=[
        "DATE",
        "SYMBOL"
    ]

)

# =========================================================
# SAVE
# =========================================================

history.to_parquet(

    PARQUET_FILE,

    index=False

)

history.to_csv(

    CSV_FILE,

    index=False

)

# =========================================================
# REPORT
# =========================================================

print(
    "\n✅ Signal Database Updated"
)

print(
    f"\n📁 Saved: {PARQUET_FILE}"
)

print(
    f"\n📁 Backup: {CSV_FILE}"
)

print(
    f"\n📊 Total Signals Stored: {len(history):,}"
)

print(
    f"\n🆕 Signals Added: {len(signals)}"
)
