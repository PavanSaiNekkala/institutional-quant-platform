import pandas as pd
from pathlib import Path
from datetime import datetime

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT / "data"

TRACKER_FILE = (
    DATA_DIR
    / "strategy_versions.csv"
)

# =========================================================
# INPUT FILES
# =========================================================

STATS_FILE = (
    DATA_DIR
    / "walk_forward_stats.csv"
)

REGIME_FILE = (
    DATA_DIR
    / "market_regime.csv"
)

PORTFOLIO_FILE = (
    DATA_DIR
    / "optimised_portfolio.csv"
)

# =========================================================
# HELPER
# =========================================================

def safe_read(path):

    if not path.exists():

        print(
            f"⚠ Missing: {path.name}"
        )

        return None

    try:

        return pd.read_csv(path)

    except Exception as e:

        print(
            f"⚠ Error reading {path.name}: {e}"
        )

        return None

# =========================================================
# LOAD FILES
# =========================================================

print(
    "\n📥 Loading Experiment Data..."
)

stats = safe_read(
    STATS_FILE
)

regime = safe_read(
    REGIME_FILE
)

portfolio = safe_read(
    PORTFOLIO_FILE
)

# =========================================================
# DEFAULT VALUES
# =========================================================

total_return = None
cagr = None
sharpe = None
volatility = None
max_dd = None
win_rate = None

current_regime = "UNKNOWN"

portfolio_size = 0

# =========================================================
# STATS EXTRACTION
# =========================================================

if stats is not None:

    if (
        "Metric" in stats.columns
        and
        "Value" in stats.columns
    ):

        stats_map = dict(

            zip(
                stats["Metric"],
                stats["Value"]
            )

        )

        total_return = stats_map.get(
            "Total Return"
        )

        cagr = stats_map.get(
            "CAGR"
        )

        sharpe = stats_map.get(
            "Sharpe"
        )

        volatility = stats_map.get(
            "Volatility"
        )

        max_dd = stats_map.get(
            "Max Drawdown"
        )

        win_rate = stats_map.get(
            "Win Rate"
        )

# =========================================================
# REGIME EXTRACTION
# =========================================================

if regime is not None:

    for col in regime.columns:

        if "REGIME" in col.upper():

            current_regime = str(

                regime[col].iloc[0]

            )

            break

# =========================================================
# PORTFOLIO SIZE
# =========================================================

if portfolio is not None:

    portfolio_size = len(
        portfolio
    )

# =========================================================
# VERSION NUMBER
# =========================================================

version = 1

if TRACKER_FILE.exists():

    old = pd.read_csv(
        TRACKER_FILE
    )

    if len(old) > 0:

        version = (
            old["VERSION"].max()
            + 1
        )

# =========================================================
# NEW RECORD
# =========================================================

new_row = pd.DataFrame({

    "DATE": [
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    ],

    "VERSION": [
        version
    ],

    "TOTAL_RETURN": [
        total_return
    ],

    "CAGR": [
        cagr
    ],

    "SHARPE": [
        sharpe
    ],

    "VOLATILITY": [
        volatility
    ],

    "MAX_DRAWDOWN": [
        max_dd
    ],

    "WIN_RATE": [
        win_rate
    ],

    "PORTFOLIO_SIZE": [
        portfolio_size
    ],

    "REGIME": [
        current_regime
    ],

    "NOTES": [
        ""
    ]

})

# =========================================================
# APPEND HISTORY
# =========================================================

if TRACKER_FILE.exists():

    history = pd.read_csv(
        TRACKER_FILE
    )

    history = pd.concat(

        [
            history,
            new_row
        ],

        ignore_index=True

    )

else:

    history = new_row

# =========================================================
# KEEP LAST 1000 RUNS
# =========================================================

history = history.tail(
    1000
)

# =========================================================
# SAVE
# =========================================================

history.to_csv(

    TRACKER_FILE,

    index=False

)

# =========================================================
# REPORT
# =========================================================

print(
    "\n✅ Experiment Tracker Updated"
)

print(
    f"\n📁 Saved: {TRACKER_FILE}"
)

print(
    "\n🏆 Latest Version:\n"
)

print(
    new_row.T
)
