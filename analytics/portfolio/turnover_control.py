import pandas as pd

from pathlib import Path

# =========================================================
# CONFIG
# =========================================================

MAX_PORTFOLIO_SIZE = None

REPLACEMENT_THRESHOLD = 10

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT_DIR / "data"

CURRENT_PORTFOLIO_FILE = (
    DATA_DIR
    / "current_portfolio.csv"
)

CANDIDATES_FILE = (
    DATA_DIR
    / "diversified_candidates.csv"
)

OUTPUT_FILE = (
    DATA_DIR
    / "target_portfolio.csv"
)

# =========================================================
# LOAD DATA
# =========================================================

print(
    "\n📥 Loading Portfolio Data..."
)

candidates_df = pd.read_csv(
    CANDIDATES_FILE
)

candidates_df = candidates_df.sort_values(
    "MULTI_FACTOR_SCORE",
    ascending=False
)

# =========================================================
# FIRST RUN
# =========================================================

if not CURRENT_PORTFOLIO_FILE.exists():

    print(
        "\n⚠️ No current portfolio found."
    )

    target_df = candidates_df.head(
        MAX_PORTFOLIO_SIZE
    ).copy()

    target_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        "\n✅ Initial Portfolio Created"
    )

    raise SystemExit

# =========================================================
# LOAD CURRENT PORTFOLIO
# =========================================================

current_df = pd.read_csv(
    CURRENT_PORTFOLIO_FILE
)

current_symbols = set(
    current_df["Symbol"]
)

candidate_symbols = set(
    candidates_df["Symbol"]
)

# =========================================================
# MARKET
# =========================================================

_FILE = (
    DATA_DIR
    / "market_.csv"
)

if _FILE.exists():

    _df = pd.read_csv(
        _FILE
    )

    market_ = str(
        _df["MARKET_"].iloc[0]
    ).upper()

else:

    market_ = "SIDEWAYS"

print(
    f"\n📊 Market : {market_}"
)

if market_ == "BULL":

    MAX_PORTFOLIO_SIZE = 30

elif market_ == "SIDEWAYS":

    MAX_PORTFOLIO_SIZE = 20

elif market_ == "BEAR":

    MAX_PORTFOLIO_SIZE = 10

else:

    MAX_PORTFOLIO_SIZE = 20

print(
    f"📈 Portfolio Size: {MAX_PORTFOLIO_SIZE}"
)

# =========================================================
# KEEP EXISTING HOLDINGS
# =========================================================

portfolio = []

for symbol in current_symbols:

    row = candidates_df[
        candidates_df["Symbol"] == symbol
    ]

    if not row.empty:

        portfolio.append(
            row.iloc[0]
        )

# =========================================================
# FILL EMPTY SLOTS
# =========================================================

for _, candidate in candidates_df.iterrows():

    if len(portfolio) >= MAX_PORTFOLIO_SIZE:

        break

    symbol = candidate["Symbol"]

    existing_symbols = {

        x["Symbol"]

        for x in portfolio
    }

    if symbol in existing_symbols:

        continue

    portfolio.append(
        candidate
    )

# =========================================================
# SCORE BASED REPLACEMENT
# =========================================================

portfolio_df = pd.DataFrame(
    portfolio
)

portfolio_df = portfolio_df.sort_values(
    "MULTI_FACTOR_SCORE"
)

for _, candidate in candidates_df.iterrows():

    weakest = portfolio_df.iloc[0]

    score_gap = (

        candidate[
            "MULTI_FACTOR_SCORE"
        ]

        -

        weakest[
            "MULTI_FACTOR_SCORE"
        ]
    )

    if score_gap < REPLACEMENT_THRESHOLD:

        continue

    if candidate["Symbol"] in list(

        portfolio_df["Symbol"]

    ):

        continue

    portfolio_df = portfolio_df.iloc[1:]

    portfolio_df = pd.concat(

        [
            portfolio_df,
            candidate.to_frame().T
        ],

        ignore_index=True
    )

    portfolio_df = portfolio_df.sort_values(
        "MULTI_FACTOR_SCORE"
    )

# =========================================================
# METRICS
# =========================================================

old_symbols = set(
    current_df["Symbol"]
)

new_symbols = set(
    portfolio_df["Symbol"]
)

added = len(
    new_symbols
    -
    old_symbols
)

removed = len(
    old_symbols
    -
    new_symbols
)

turnover_pct = round(

    (
        max(
            added,
            removed
        )

        /

        max(
            len(old_symbols),
            1
        )
    )

    * 100,

    2
)

retention_pct = round(

    (
        len(
            old_symbols
            &
            new_symbols
        )

        /

        max(
            len(old_symbols),
            1
        )
    )

    * 100,

    2
)

# =========================================================
# SAVE
# =========================================================

portfolio_df = portfolio_df.sort_values(
    "MULTI_FACTOR_SCORE",
    ascending=False
)

portfolio_df.to_csv(
    OUTPUT_FILE,
    index=False
)

# =========================================================
# SUMMARY
# =========================================================

print(
    "\n✅ Turnover Control Complete"
)

print(
    f"\nTurnover % : {turnover_pct}"
)

print(
    f"Retention % : {retention_pct}"
)

print(
    f"\n📁 Saved:\n{OUTPUT_FILE}"
)

print(
    "\n🏆 Final Portfolio:\n"
)

print(

    portfolio_df[
        [
            "Symbol",
            "MULTI_FACTOR_SCORE"
        ]
    ]

    .head(20)
)
