from pathlib import Path

import pandas as pd

# =========================================================
# FILES
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

PORTFOLIO_FILE = ROOT / "data" / "processed" / "sector_controlled_portfolio.csv"

OUTPUT_FILE = ROOT / "data" / "portfolio" / "position_sized_portfolio.csv"

# =========================================================
# SETTINGS
# =========================================================

MAX_WEIGHT = 0.08
MIN_WEIGHT = 0.00

# =========================================================
# LOAD DATA
# =========================================================

print("\n📥 Loading Portfolio...")

portfolio_df = pd.read_csv(PORTFOLIO_FILE)

df = portfolio_df.copy()

# =========================================================
# POSITION SCORE
# =========================================================

df["ENTRY_SCORE"] = df["ENTRY_SCORE"].fillna(0)

df["POSITION_SCORE"] = (df["MULTI_FACTOR_SCORE"] ** 2) * (1 + df["ENTRY_SCORE"] / 10)

# =========================================================
# NORMALIZED WEIGHTS
# =========================================================

total_score = df["POSITION_SCORE"].sum()
if total_score <= 0:
    raise ValueError("POSITION_SCORE total is zero.")
df["TARGET_WEIGHT"] = df["POSITION_SCORE"] / total_score

# =========================================================
# APPLY LIMITS
# =========================================================

df["TARGET_WEIGHT"] = df["TARGET_WEIGHT"].clip(upper=MAX_WEIGHT)

df["TARGET_WEIGHT"] = df["TARGET_WEIGHT"] / df["TARGET_WEIGHT"].sum()

# =========================================================
# PERCENT FORMAT
# =========================================================

df["TARGET_WEIGHT_%"] = (df["TARGET_WEIGHT"] * 100).round(2)

# =========================================================
# SORT
# =========================================================

df = df.sort_values(by="TARGET_WEIGHT", ascending=False)

# =========================================================
# SAVE
# =========================================================

df.to_csv(OUTPUT_FILE, index=False)

print("\n✅ Position Sizing Complete")

print("\n📁 Saved:")

print(OUTPUT_FILE)

print("\n🏆 Portfolio Weights:\n")

print(df[["Symbol", "MULTI_FACTOR_SCORE", "ENTRY_SCORE", "TARGET_WEIGHT_%"]].head(20))
