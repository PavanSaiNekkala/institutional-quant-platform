from pathlib import Path

import pandas as pd

# =========================================================
# CONFIG
# =========================================================

TOP_N = 150

MAX_PER_SECTOR = 5

MAX_PER_INDUSTRY = 2

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

FACTOR_FILE = (
    ROOT_DIR
    / "data"
    / "processed"
    / "factor_model_rankings.csv"
)

CONVICTION_FILE = (
    ROOT_DIR
    / "data"
    / "processed"
    / "conviction_scores.csv"
)

OUTPUT_FILE = (
    ROOT_DIR
    / "data"
    / "portfolio"
    / "diversified_candidates.csv"
)

# =========================================================
# LOAD
# =========================================================

print("\n📥 Loading Inputs...")

factor_df = pd.read_csv(FACTOR_FILE)

conviction_df = pd.read_csv(CONVICTION_FILE)

print("✅ Files Loaded")

# =========================================================
# CLEAN SYMBOLS
# =========================================================

for df in [factor_df, conviction_df]:

    df["Symbol"] = (
        df["Symbol"]
        .astype(str)
        .str.upper()
        .str.replace(".NS", "", regex=False)
        .str.strip()
    )

# =========================================================
# MERGE
# =========================================================

merge_cols = [
    c
    for c in [
        "Symbol",
        "CONVICTION_SCORE",
        "EXPECTED_RETURN",
    ]
    if c in conviction_df.columns
]

df = factor_df.merge(
    conviction_df[merge_cols],
    on="Symbol",
    how="left",
)

df["CONVICTION_SCORE"] = (
    df["CONVICTION_SCORE"]
    .fillna(0)
)

# =========================================================
# DIVERSIFICATION SCORE
# =========================================================

print("\n🧠 Building Diversification Score...")

df["DIVERSIFICATION_SCORE"] = (
    (df["MULTI_FACTOR_SCORE"] * 0.60)
    + (df["CONVICTION_SCORE"] * 0.40)
)

# =========================================================
# SORT
# =========================================================

df = df.sort_values(
    "DIVERSIFICATION_SCORE",
    ascending=False,
)

# =========================================================
# TOP UNIVERSE
# =========================================================

df = df.head(TOP_N)

# =========================================================
# SECTOR CONTROL
# =========================================================

selected = []

sector_count = {}

industry_count = {}

for _, row in df.iterrows():

    sector = str(
        row.get(
            "Sector",
            "Unknown"
        )
    )

    industry = str(
        row.get(
            "Industry",
            "Unknown"
        )
    )

    if sector_count.get(sector, 0) >= MAX_PER_SECTOR:
        continue

    if industry_count.get(industry, 0) >= MAX_PER_INDUSTRY:
        continue

    selected.append(row)

    sector_count[sector] = (
        sector_count.get(sector, 0) + 1
    )

    industry_count[industry] = (
        industry_count.get(industry, 0) + 1
    )

# =========================================================
# FINAL DATAFRAME
# =========================================================

final_df = pd.DataFrame(selected)

final_df = final_df.sort_values(
    "DIVERSIFICATION_SCORE",
    ascending=False,
)

final_df["DIVERSIFIED_RANK"] = range(
    1,
    len(final_df) + 1
)

# =========================================================
# SAVE
# =========================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

final_df.to_csv(
    OUTPUT_FILE,
    index=False,
)

# =========================================================
# OUTPUT
# =========================================================

print("\n✅ Diversification Complete")

print(
    f"\nCandidates Selected: "
    f"{len(final_df)}"
)

print(
    f"\nUnique Sectors: "
    f"{final_df['Sector'].nunique()}"
)

print(
    f"\nSaved:\n{OUTPUT_FILE}"
)

print("\n🏆 TOP DIVERSIFIED CANDIDATES\n")

cols = [
    c
    for c in [
        "DIVERSIFIED_RANK",
        "Symbol",
        "Sector",
        "Industry",
        "MULTI_FACTOR_SCORE",
        "CONVICTION_SCORE",
        "DIVERSIFICATION_SCORE",
    ]
    if c in final_df.columns
]

print(final_df[cols].head(20))
