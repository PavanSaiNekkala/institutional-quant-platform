from pathlib import Path

import pandas as pd

# =========================================================
# FILES
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

MASTER_FILE = ROOT / "data" / "factor_model_rankings.csv"

OUTPUT_FILE = ROOT / "data" / "sector_controlled_portfolio.csv"

# =========================================================
# SETTINGS
# =========================================================

MAX_SECTOR_STOCKS = 3
TOP_STOCKS = 40

# =========================================================
# LOAD DATA
# =========================================================

print("\n📥 Loading Factor Rankings...")

df = pd.read_csv(MASTER_FILE)

# =========================================================
# SYMBOL CLEANUP
# =========================================================

df["Symbol"] = df["Symbol"].astype(str).str.upper().str.strip()

# =========================================================
# REMOVE DUPLICATES
# =========================================================

df = df.drop_duplicates(subset=["Symbol"], keep="first").reset_index(drop=True)

# =========================================================
# VALIDATION
# =========================================================

required_cols = ["Symbol", "Sector", "MULTI_FACTOR_SCORE"]

missing = [c for c in required_cols if c not in df.columns]

if missing:
    raise ValueError(f"Missing columns: {missing}")

# =========================================================
# CLEAN SECTOR
# =========================================================

df["Sector"] = df["Sector"].fillna("UNKNOWN").astype(str)

# =========================================================
# SORT BY FACTOR SCORE
# =========================================================

df = df.sort_values(by="MULTI_FACTOR_SCORE", ascending=False).reset_index(drop=True)

# =========================================================
# SECTOR CONTROL
# =========================================================

final_rows = []

sector_counter = {}

for _, row in df.iterrows():
    sector = str(row["Sector"]).upper()

    count = sector_counter.get(sector, 0)

    if count < MAX_SECTOR_STOCKS:
        final_rows.append(row)

        sector_counter[sector] = count + 1

# =========================================================
# CREATE FINAL DF
# =========================================================

final_df = pd.DataFrame(final_rows)

# =========================================================
# INITIAL WEIGHT
# =========================================================

score_sum = final_df["MULTI_FACTOR_SCORE"].sum()

final_df["INITIAL_WEIGHT"] = final_df["MULTI_FACTOR_SCORE"] / score_sum

final_df["INITIAL_WEIGHT_%"] = (final_df["INITIAL_WEIGHT"] * 100).round(2)

# =========================================================
# SORT
# =========================================================

final_df = final_df.sort_values(by="MULTI_FACTOR_SCORE", ascending=False)

# =========================================================
# SAVE
# =========================================================

final_df.to_csv(OUTPUT_FILE, index=False)

# =========================================================
# REPORT
# =========================================================

print("\n✅ Sector Exposure Control Complete")

print("\n📁 Saved:")

print(OUTPUT_FILE)

print("\n📊 Sector Allocation:\n")

print(final_df["Sector"].value_counts())

print("\n🏆 Top Holdings:\n")

print(final_df[["Symbol", "Sector", "MULTI_FACTOR_SCORE", "INITIAL_WEIGHT_%"]].head(20))

print("\nTotal Weight:", round(final_df["INITIAL_WEIGHT_%"].sum(), 2), "%")

print("\nTotal Holdings:", len(final_df))
