import subprocess
from datetime import datetime
from pathlib import Path

import pandas as pd

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT / "data"

REGISTRY_FILE = DATA_DIR / "strategy_registry.csv"

STATS_FILE = DATA_DIR / "walk_forward_stats.csv"

REGIME_FILE = DATA_DIR / "market_regime.csv"

PORTFOLIO_FILE = DATA_DIR / "optimised_portfolio.csv"

# =========================================================
# HELPERS
# =========================================================


def safe_read(path):

    if not path.exists():
        return None

    try:
        return pd.read_csv(path)

    except Exception:
        return None


def get_git_commit():

    try:
        return (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT)
            .decode()
            .strip()
        )

    except Exception:
        return "UNKNOWN"


# =========================================================
# LOAD FILES
# =========================================================

print("\n📥 Loading Version Data...")

stats = safe_read(STATS_FILE)

regime_df = safe_read(REGIME_FILE)

portfolio = safe_read(PORTFOLIO_FILE)

# =========================================================
# DEFAULTS
# =========================================================

cagr = None
sharpe = None
max_dd = None
volatility = None
win_rate = None

regime = "UNKNOWN"

portfolio_size = 0

# =========================================================
# STATS
# =========================================================

if stats is not None:
    if "Metric" in stats.columns and "Value" in stats.columns:
        stats_map = dict(
            zip(
                stats["Metric"],
                stats["Value"],
                strict=False,
            )
        )

        cagr = stats_map.get("CAGR")

        sharpe = stats_map.get("Sharpe")

        max_dd = stats_map.get("Max Drawdown")

        volatility = stats_map.get("Volatility")

        win_rate = stats_map.get("Win Rate")

# =========================================================
# REGIME
# =========================================================

if regime_df is not None:
    for col in regime_df.columns:
        if "REGIME" in col.upper():
            regime = str(regime_df[col].iloc[0])

            break

# =========================================================
# PORTFOLIO SIZE
# =========================================================

if portfolio is not None:
    portfolio_size = len(portfolio)

# =========================================================
# VERSION
# =========================================================

version = 1

if REGISTRY_FILE.exists():
    old = pd.read_csv(REGISTRY_FILE)

    if len(old):
        version = old["VERSION"].max() + 1

# =========================================================
# RECORD
# =========================================================

record = pd.DataFrame(
    {
        "TIMESTAMP": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "VERSION": [version],
        "GIT_COMMIT": [get_git_commit()],
        "REGIME": [regime],
        "CAGR": [cagr],
        "SHARPE": [sharpe],
        "MAX_DRAWDOWN": [max_dd],
        "VOLATILITY": [volatility],
        "WIN_RATE": [win_rate],
        "PORTFOLIO_SIZE": [portfolio_size],
    }
)

# =========================================================
# APPEND
# =========================================================

if REGISTRY_FILE.exists():
    history = pd.read_csv(REGISTRY_FILE)

    history = pd.concat([history, record], ignore_index=True)

else:
    history = record

# =========================================================
# KEEP LAST 5000 RUNS
# =========================================================

history = history.tail(5000)

# =========================================================
# SAVE
# =========================================================

history.to_csv(REGISTRY_FILE, index=False)

# =========================================================
# REPORT
# =========================================================

print("\n✅ Strategy Registry Updated")

print(f"\n📁 Saved: {REGISTRY_FILE}")

print("\n🏆 Latest Version:\n")

print(record.T)
