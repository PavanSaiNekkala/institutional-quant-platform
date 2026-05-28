import pandas as pd
import numpy as np

from pathlib import Path

# =========================================================
# CONFIG
# =========================================================

EPISODES = 200

LEARNING_RATE = 0.10

DISCOUNT_FACTOR = 0.90

EXPLORATION_RATE = 0.20

TOP_N = 20

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    ROOT_DIR
    / "data"
    / "ml_alpha_predictions.csv"
)

REGIME_FILE = (
    ROOT_DIR
    / "data"
    / "market_regime_v2.csv"
)

OUTPUT_FILE = (
    ROOT_DIR
    / "data"
    / "reinforcement_portfolio.csv"
)

QTABLE_FILE = (
    ROOT_DIR
    / "data"
    / "reinforcement_q_table.csv"
)

# =========================================================
# LOAD DATA
# =========================================================

print("\n📥 Loading ML Alpha Predictions...")

df = pd.read_csv(INPUT_FILE)

regime_df = pd.read_csv(REGIME_FILE)

print("✅ Data Loaded")

# =========================================================
# CLEAN COLUMNS
# =========================================================

df.columns = df.columns.str.strip()

regime_df.columns = regime_df.columns.str.strip()

# =========================================================
# REQUIRED COLUMNS
# =========================================================

required_cols = [

    "Symbol",

    "Sector",

    "ML_PREDICTED_ALPHA",

    "Momentum",

    "Sharpe"

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
# CURRENT REGIME
# =========================================================

market_regime = (

    regime_df.iloc[0]["MARKET_REGIME"]
)

print(
    f"\n🌍 Market Regime: "
    f"{market_regime}"
)

# =========================================================
# STATES & ACTIONS
# =========================================================

states = [

    "BULL_EXPANSION",

    "BULL_WEAKENING",

    "SIDEWAYS_LOW_VOL",

    "SIDEWAYS_HIGH_VOL",

    "BEAR_DISTRIBUTION",

    "PANIC",

    "RECOVERY"
]

actions = [

    "MOMENTUM",

    "LOW_VOL",

    "QUALITY",

    "RS",

    "FACTOR"
]

# =========================================================
# INITIALIZE Q TABLE
# =========================================================

q_table = pd.DataFrame(

    0,

    index=states,

    columns=actions,

    dtype=float
)

# =========================================================
# REWARD FUNCTION
# =========================================================

def calculate_reward(action, stock):

    reward = 0

    if action == "MOMENTUM":

        reward += stock["Momentum"] * 100

    elif action == "LOW_VOL":

        if "VOL_ADJ_RS" in stock:

            reward += (
                1 /
                (
                    stock["VOL_ADJ_RS"]
                    + 1e-6
                )
            ) * 10

    elif action == "QUALITY":

        reward += stock["Sharpe"] * 20

    elif action == "RS":

        rs_cols = [

            "RS_30D",

            "RS_60D",

            "RS_ACCELERATION"

        ]

        existing_cols = [

            c for c in rs_cols
            if c in stock.index
        ]

        if len(existing_cols) > 0:

            reward += (

                stock[existing_cols]

                .mean()
            )

    elif action == "FACTOR":

        if "MULTI_FACTOR_SCORE" in stock:

            reward += (

                stock["MULTI_FACTOR_SCORE"]
            )

    reward += (

        stock["ML_PREDICTED_ALPHA"]
        * 0.50
    )

    return reward

# =========================================================
# Q LEARNING TRAINING
# =========================================================

print(
    "\n🧠 Training Reinforcement Allocation Agent..."
)

for episode in range(EPISODES):

    current_state = market_regime

    sample_stock = df.sample(1).iloc[0]

    # -----------------------------------------------------
    # EXPLORE VS EXPLOIT
    # -----------------------------------------------------

    if np.random.rand() < EXPLORATION_RATE:

        action = np.random.choice(actions)

    else:

        action = (

            q_table.loc[current_state]

            .idxmax()
        )

    # -----------------------------------------------------
    # REWARD
    # -----------------------------------------------------

    reward = calculate_reward(
        action,
        sample_stock
    )

    # -----------------------------------------------------
    # Q UPDATE
    # -----------------------------------------------------

    old_q = q_table.loc[
        current_state,
        action
    ]

    next_max = (

        q_table.loc[current_state]

        .max()
    )

    new_q = (

        old_q

        +

        LEARNING_RATE
        *
        (
            reward
            +
            DISCOUNT_FACTOR
            * next_max
            -
            old_q
        )
    )

    q_table.loc[
        current_state,
        action
    ] = new_q

# =========================================================
# BEST ACTIONS
# =========================================================

best_action = (

    q_table.loc[market_regime]

    .idxmax()
)

print(
    f"\n🤖 Learned Optimal Strategy: "
    f"{best_action}"
)

# =========================================================
# STRATEGY SCORING
# =========================================================

if best_action == "MOMENTUM":

    df["RL_SCORE"] = (

        df["Momentum"] * 100
    )

elif best_action == "LOW_VOL":

    if "VOL_ADJ_RS" in df.columns:

        df["RL_SCORE"] = (

            1 /
            (
                df["VOL_ADJ_RS"]
                + 1e-6
            )
        )

    else:

        df["RL_SCORE"] = 0

elif best_action == "QUALITY":

    df["RL_SCORE"] = (

        df["Sharpe"] * 10
    )

elif best_action == "RS":

    rs_cols = [

        "RS_30D",

        "RS_60D",

        "RS_ACCELERATION"

    ]

    existing_cols = [

        c for c in rs_cols
        if c in df.columns
    ]

    if len(existing_cols) > 0:

        df["RL_SCORE"] = (

            df[existing_cols]

            .mean(axis=1)
        )

    else:

        df["RL_SCORE"] = 0

else:

    if "MULTI_FACTOR_SCORE" in df.columns:

        df["RL_SCORE"] = (

            df["MULTI_FACTOR_SCORE"]
        )

    else:

        df["RL_SCORE"] = 0

# =========================================================
# FINAL ENSEMBLE SCORE
# =========================================================

df["FINAL_RL_SCORE"] = (

    (
        df["RL_SCORE"] * 0.50
    )

    +

    (
        df["ML_PREDICTED_ALPHA"] * 0.50
    )

)

# =========================================================
# FINAL PORTFOLIO
# =========================================================

df = df.sort_values(

    by="FINAL_RL_SCORE",

    ascending=False
)

portfolio = df.head(TOP_N).copy()

portfolio["WEIGHT"] = (

    portfolio["FINAL_RL_SCORE"]

    / portfolio["FINAL_RL_SCORE"].sum()
)

portfolio["WEIGHT"] = (

    portfolio["WEIGHT"]

    .round(4)
)

portfolio["FINAL_RL_SCORE"] = (

    portfolio["FINAL_RL_SCORE"]

    .round(4)
)

portfolio["RL_RANK"] = range(

    1,

    len(portfolio) + 1
)

# =========================================================
# SAVE
# =========================================================

portfolio.to_csv(

    OUTPUT_FILE,

    index=False
)

q_table.to_csv(

    QTABLE_FILE
)

# =========================================================
# OUTPUT
# =========================================================

print(
    "\n✅ Reinforcement Learning Portfolio Complete"
)

print(
    f"\n📁 Portfolio Saved To:\n"
    f"{OUTPUT_FILE}"
)

print(
    f"\n📁 Q-Table Saved To:\n"
    f"{QTABLE_FILE}"
)

print("\n🏆 LEARNED POLICY:\n")

print(q_table)

print("\n🏆 TOP RL HOLDINGS:\n")

print(

    portfolio[

        [
            "RL_RANK",
            "Symbol",
            "Sector",
            "FINAL_RL_SCORE",
            "WEIGHT"
        ]

    ]
)