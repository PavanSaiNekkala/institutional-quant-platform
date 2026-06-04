import pandas as pd
from pathlib import Path
from datetime import datetime

# =========================================================
# FILES
# =========================================================

ROOT = Path(__file__).resolve().parent.parent

PORTFOLIO_FILE = (
    ROOT
    / "data"
    / "optimised_portfolio.csv"
)

TRADE_HISTORY_FILE = (
    ROOT
    / "data"
    / "trade_history.csv"
)

CURRENT_POSITIONS_FILE = (
    ROOT
    / "data"
    / "current_positions.csv"
)

EXITED_POSITIONS_FILE = (
    ROOT
    / "data"
    / "exited_positions.csv"
)

LIFECYCLE_FILE = (
    ROOT
    / "data"
    / "portfolio_lifecycle.csv"
)

# =========================================================
# LOAD PORTFOLIO
# =========================================================

print("\n📥 Loading Portfolio...")

portfolio = pd.read_csv(
    PORTFOLIO_FILE
)

portfolio["Symbol"] = (
    portfolio["Symbol"]
    .astype(str)
    .str.upper()
    .str.strip()
)

# =========================================================
# LOAD TRADE HISTORY
# =========================================================

if Path(
    TRADE_HISTORY_FILE
).exists():

    trades = pd.read_csv(
        TRADE_HISTORY_FILE
    )

else:

    trades = pd.DataFrame(
        columns=[
            "DATE",
            "Symbol",
            "ACTION",
            "PRICE"
        ]
    )
    
print("\nTRADE HISTORY ROWS")
print(len(trades))

print("\nTRADE ACTIONS")
print(
    trades["ACTION"]
    .value_counts(dropna=False)
)
print("\nTRADE SYMBOLS SAMPLE")
print(
    trades["Symbol"]
    .head(20)
)
# =========================================================
# CLEAN
# =========================================================

if not trades.empty:

    trades["Symbol"] = (

        trades["Symbol"]

        .astype(str)

        .str.replace(
            ".NS",
            "",
            regex=False
        )

        .str.upper()

        .str.strip()

    )

    trades["DATE"] = pd.to_datetime(
        trades["DATE"],
        errors="coerce"
    )

# =========================================================
# CURRENT POSITIONS
# =========================================================

current_symbols = set(
    portfolio["Symbol"]
)

# =========================================================
# ENTRY DATES
# =========================================================

if not trades.empty:

    entries = trades[

        trades["ACTION"]

        .astype(str)

        .str.upper()

        .str.contains(
            "BUY",
            na=False
        )

    ]

else:

    entries = pd.DataFrame()

entry_dates = {}

if not entries.empty:

    entries = entries.sort_values(
        "DATE"
    )

    for symbol in current_symbols:

        subset = entries[
            entries["Symbol"]
            == symbol
        ]

        if len(subset):

            entry_dates[symbol] = (
                subset.iloc[0]["DATE"]
            )

# =========================================================
# CURRENT POSITIONS TABLE
# =========================================================

current_rows = []

today = pd.Timestamp.today()

for _, row in portfolio.iterrows():

    symbol = row["Symbol"]

    entry_date = entry_dates.get(
        symbol,
        pd.Nat
    )
        
    if pd.notna(entry_date):

        holding_days = (
            today - entry_date
        ).days

    else:

        holding_days = None

    current_rows.append({

        "Symbol":
            symbol,

        "Entry_Date":
            entry_date,

        "Holding_Days":
            holding_days,

        "Portfolio_Weight":
            row.get(
                "OPTIMAL_WEIGHT",
                row.get(
                    "FINAL_WEIGHT",
                    None
                )
            ),

        "Status":
            "ACTIVE"
    })

current_df = pd.DataFrame(
    current_rows
)

# =========================================================
# EXITED POSITIONS
# =========================================================

historical_symbols = set()

if not trades.empty:

    historical_symbols = set(
        trades["Symbol"]
    )

exited_symbols = list(

    historical_symbols

    -

    current_symbols

)

exit_rows = []

for symbol in exited_symbols:

    subset = trades[
        trades["Symbol"]
        == symbol
    ]

    last_trade = (

        subset

        .sort_values("DATE")

        .iloc[-1]

    )

    exit_rows.append({

        "Symbol":
            symbol,

        "Last_Trade_Date":
            last_trade["DATE"],

        "Last_Action":
            last_trade["ACTION"],

        "Status":
            "EXITED"
    })

exited_df = pd.DataFrame(
    exit_rows
)

# =========================================================
# LIFECYCLE TABLE
# =========================================================

lifecycle_rows = []

for _, row in current_df.iterrows():

    lifecycle_rows.append({

        "Symbol":
            row["Symbol"],

        "Lifecycle_Stage":
            "HELD",

        "Holding_Days":
            row["Holding_Days"]
    })

for _, row in exited_df.iterrows():

    lifecycle_rows.append({

        "Symbol":
            row["Symbol"],

        "Lifecycle_Stage":
            "EXITED",

        "Holding_Days":
            None
    })

lifecycle_df = pd.DataFrame(
    lifecycle_rows
)

# =========================================================
# SAVE
# =========================================================

current_df.to_csv(

    CURRENT_POSITIONS_FILE,

    index=False

)

exited_df.to_csv(

    EXITED_POSITIONS_FILE,

    index=False

)

lifecycle_df.to_csv(

    LIFECYCLE_FILE,

    index=False

)

# =========================================================
# REPORT
# =========================================================

print(
    "\n✅ Portfolio Lifecycle Complete"
)

print("\n📁 Files Saved:")

print(
    CURRENT_POSITIONS_FILE
)

print(
    EXITED_POSITIONS_FILE
)

print(
    LIFECYCLE_FILE
)

print(
    f"\n📊 Active Positions: "
    f"{len(current_df)}"
)

print(
    f"📊 Exited Positions: "
    f"{len(exited_df)}"
)

print("\n🏆 Current Holdings:\n")

print(

    current_df.head(20)

)
