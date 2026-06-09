from pathlib import Path

import numpy as np
import pandas as pd

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

PORTFOLIO_FILE = ROOT / "data" / "portfolio" / "optimised_portfolio.csv"
POSITIONS_FILE = ROOT / "data" / "processed" / "current_positions.csv"
CONVICTION_FILE = ROOT / "data" / "processed" / "conviction_scores.csv"
EXPECTED_FILE = ROOT / "data" / "processed" / "expected_returns.csv"
NEWS_FILE = ROOT / "data" / "processed" / "news_rankings.csv"

OUTPUT_FILE = ROOT / "data" / "portfolio" / "portfolio_monitor.csv"

# =========================================================
# LOAD
# =========================================================

print("\n📥 Loading Monitor Inputs...")

portfolio = pd.read_csv(PORTFOLIO_FILE)
positions = pd.read_csv(POSITIONS_FILE)

conviction = pd.read_csv(CONVICTION_FILE) if CONVICTION_FILE.exists() else pd.DataFrame()

expected = pd.read_csv(EXPECTED_FILE) if EXPECTED_FILE.exists() else pd.DataFrame()

news = pd.read_csv(NEWS_FILE) if NEWS_FILE.exists() else pd.DataFrame()

# =========================================================
# SYMBOL CLEAN
# =========================================================

for df in [portfolio, positions, conviction, expected, news]:
    if not df.empty and "Symbol" in df.columns:
        df["Symbol"] = (
            df["Symbol"].astype(str).str.replace(".NS", "", regex=False).str.upper().str.strip()
        )

# =========================================================
# BASE
# =========================================================

monitor = portfolio.copy()

# =========================================================
# POSITIONS
# =========================================================

if not positions.empty:
    monitor = monitor.merge(
        positions[["Symbol", "Entry_Date", "Holding_Days"]], on="Symbol", how="left"
    )

# =========================================================
# EST_HOLD_DAYS
# =========================================================

if "EST_HOLD_DAYS" not in monitor.columns:
    if not expected.empty and "EST_HOLD_DAYS" in expected.columns:
        monitor = monitor.merge(expected[["Symbol", "EST_HOLD_DAYS"]], on="Symbol", how="left")

# =========================================================
# CONVICTION
# =========================================================

if "CONVICTION" not in monitor.columns:
    if not conviction.empty and "CONVICTION" in conviction.columns:
        monitor = monitor.merge(
            conviction[["Symbol", "CONVICTION", "CONVICTION_SCORE"]], on="Symbol", how="left"
        )

# =========================================================
# EXPECTED RETURN
# =========================================================

if "EXPECTED_RETURN_30D" not in monitor.columns:
    if not expected.empty and "EXPECTED_RETURN_30D" in expected.columns:
        monitor = monitor.merge(
            expected[["Symbol", "EXPECTED_RETURN_30D"]], on="Symbol", how="left"
        )

# =========================================================
# NEWS FLAG
# =========================================================

if not conviction.empty and "NEWS_FLAG" in conviction.columns:
    monitor = monitor.merge(conviction[["Symbol", "NEWS_FLAG"]], on="Symbol", how="left")

# =========================================================
# NEWS ALPHA
# =========================================================

if not news.empty and "NEWS_ALPHA" in news.columns:
    monitor = monitor.merge(news[["Symbol", "NEWS_ALPHA"]], on="Symbol", how="left")

# =========================================================
# DEFAULTS
# =========================================================

for col in ["Holding_Days", "EST_HOLD_DAYS"]:
    if col not in monitor.columns:
        monitor[col] = 0

monitor["Holding_Days"] = pd.to_numeric(monitor["Holding_Days"], errors="coerce").fillna(0)

monitor["EST_HOLD_DAYS"] = pd.to_numeric(monitor["EST_HOLD_DAYS"], errors="coerce").fillna(0)

# =========================================================
# HOLD PROGRESS
# =========================================================

monitor["HOLD_PROGRESS"] = np.where(
    monitor["EST_HOLD_DAYS"] > 0, (monitor["Holding_Days"] / monitor["EST_HOLD_DAYS"] * 100), 0
)

monitor["HOLD_PROGRESS"] = monitor["HOLD_PROGRESS"].clip(0, 100).round(2)

# =========================================================
# ALERTS
# =========================================================

monitor["EXIT_WARNING"] = monitor["HOLD_PROGRESS"] >= 80

if "NEWS_FLAG" in monitor.columns:
    monitor["NEWS_ALERT"] = monitor["NEWS_FLAG"] != "NORMAL"

else:
    monitor["NEWS_ALERT"] = False

# =========================================================
# SAVE
# =========================================================

monitor.to_csv(OUTPUT_FILE, index=False)

# =========================================================
# REPORT
# =========================================================

print("\n✅ Portfolio Monitor Generated")

print(f"\n📁 Saved:\n{OUTPUT_FILE}")

print("\n🏆 Top Holdings:\n")

report_cols = [
    c
    for c in [
        "Symbol",
        "CONVICTION",
        "EXPECTED_RETURN_30D",
        "EST_HOLD_DAYS",
        "Holding_Days",
        "HOLD_PROGRESS",
    ]
    if c in monitor.columns
]

print(monitor[report_cols].head(20))
