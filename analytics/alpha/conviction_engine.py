from pathlib import Path

import pandas as pd

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT_DIR / "data"

FACTOR_FILE = DATA_DIR / "processed" / "factor_model_rankings.csv"

ENTRY_FILE = DATA_DIR / "processed" / "entry_quality_scores.csv"

OUTPUT_FILE = DATA_DIR / "processed" / "conviction_scores.csv"

NEWS_FILE = DATA_DIR / "processed" / "news_rankings.csv"

if NEWS_FILE.exists():
    news_df = pd.read_csv(NEWS_FILE)

else:
    print("⚠ News file missing")

    news_df = pd.DataFrame(
        columns=["Symbol", "NEWS_ALPHA", "NEWS_SCORE", "NEWS_BIAS", "NEWS_IMPACT"]
    )

if news_df.empty:
    print("⚠ Empty news file detected")
# =========================================================
# LOAD FILES
# =========================================================

print("\n📥 Loading Data...")

factor_df = pd.read_csv(FACTOR_FILE)

entry_df = pd.read_csv(ENTRY_FILE)

# =========================================================
# NORMALIZE SYMBOLS
# =========================================================

for df_ in [factor_df, entry_df]:
    df_["Symbol"] = (
        df_["Symbol"].astype(str).str.replace(".NS", "", regex=False).str.strip().str.upper()
    )

print("\nFACTOR SYMBOLS")
print(factor_df["Symbol"].head())

print("\nENTRY SYMBOLS")
print(entry_df["Symbol"].head())

# =========================================================
# VALIDATION
# =========================================================
required_news_cols = ["Symbol", "NEWS_ALPHA", "NEWS_SCORE", "NEWS_BIAS", "NEWS_IMPACT"]

missing_news = [c for c in required_news_cols if c not in news_df.columns]

if missing_news:
    raise ValueError(f"Missing News Columns: {missing_news}")

required_factor_cols = ["Symbol", "MULTI_FACTOR_SCORE"]

required_entry_cols = ["Symbol", "ENTRY_SCORE"]

for col in required_factor_cols:
    if col not in factor_df.columns:
        raise Exception(f"❌ Missing column: {col}")

for col in required_entry_cols:
    if col not in entry_df.columns:
        raise Exception(f"❌ Missing column: {col}")

news_df["Symbol"] = (
    news_df["Symbol"].astype(str).str.replace(".NS", "", regex=False).str.strip().str.upper()
)
news_df = news_df.sort_values("NEWS_ALPHA", ascending=False).drop_duplicates("Symbol")
# =========================================================
# MERGE
# =========================================================

factor_df = factor_df.drop(columns=["ENTRY_SCORE"], errors="ignore")

df = factor_df.merge(entry_df[["Symbol", "ENTRY_SCORE"]], on="Symbol", how="left")
df = df.merge(
    news_df[["Symbol", "NEWS_ALPHA", "NEWS_SCORE", "NEWS_BIAS", "NEWS_IMPACT"]],
    on="Symbol",
    how="left",
)
print("\nAFTER ENTRY MERGE")
print(df.columns.tolist())

print("\nMatched ENTRY_SCORE:", df["ENTRY_SCORE"].notna().sum())

print("Total Rows:", len(df))

print("\nDF COLUMNS AFTER EXPECTED RETURN MERGE")

print(df.columns.tolist())

df["ENTRY_SCORE"] = df["ENTRY_SCORE"].fillna(0)

df["NEWS_ALPHA"] = df["NEWS_ALPHA"].fillna(50)

df["NEWS_SCORE"] = df["NEWS_SCORE"].fillna(0)

df["NEWS_BIAS"] = df["NEWS_BIAS"].fillna("NEUTRAL")

df["NEWS_IMPACT"] = df["NEWS_IMPACT"].fillna("LOW")

print("\nENTRY SCORE STATS")

print(df["ENTRY_SCORE"].describe())

print("\nEXPECTED RETURN 30D STATS")

print("\nTOP 20")

print(df[["Symbol", "MULTI_FACTOR_SCORE", "ENTRY_SCORE"]].head(20))


def catalyst(row):

    if row["NEWS_BIAS"] == "POSITIVE" and row["NEWS_IMPACT"] == "HIGH":
        return "NEWS CATALYST"

    if row["NEWS_BIAS"] == "NEGATIVE" and row["NEWS_IMPACT"] == "HIGH":
        return "NEWS RISK"

    if row["NEWS_BIAS"] == "POSITIVE" and row["NEWS_IMPACT"] == "MEDIUM":
        return "POSITIVE NEWS"

    if row["NEWS_BIAS"] == "NEGATIVE" and row["NEWS_IMPACT"] == "MEDIUM":
        return "NEGATIVE NEWS"

    return "NORMAL"


df["NEWS_FLAG"] = df.apply(catalyst, axis=1)

# =========================================================
# CONTINUOUS CONVICTION SCORE
# =========================================================

factor_max = max(df["MULTI_FACTOR_SCORE"].max(), 1)

df["FACTOR_NORM"] = df["MULTI_FACTOR_SCORE"] / factor_max

entry_max = max(df["ENTRY_SCORE"].max(), 1)

df["ENTRY_NORM"] = df["ENTRY_SCORE"] / entry_max

df["NEWS_NORM"] = df["NEWS_ALPHA"].clip(0, 100) / 100

df["CONVICTION_SCORE"] = df["FACTOR_NORM"] * 55 + df["ENTRY_NORM"] * 25 + df["NEWS_NORM"] * 20

df["CONVICTION_SCORE"] = df["CONVICTION_SCORE"].round(2)

df["CONVICTION"] = "LOW"

df.loc[df["CONVICTION_SCORE"] >= 80, "CONVICTION"] = "HIGH"

df.loc[(df["CONVICTION_SCORE"] >= 60) & (df["CONVICTION_SCORE"] < 80), "CONVICTION"] = "MEDIUM"

print("\nENTRY SCORE VALUE COUNTS")

print(df["ENTRY_SCORE"].value_counts().sort_index())

# =========================================================
# RANK
# =========================================================

df = df.sort_values(["CONVICTION_SCORE", "MULTI_FACTOR_SCORE"], ascending=False)

df["CONVICTION_RANK"] = range(1, len(df) + 1)

# =========================================================
# SAVE
# =========================================================

output_cols = [
    "Symbol",
    "MULTI_FACTOR_SCORE",
    "LIQUIDITY_SCORE",
    "FACTOR_MOMENTUM",
    "FACTOR_SHARPE",
    "FACTOR_ALPHA",
    "RS_COMPOSITE",
    "NEWS_ALPHA",
    "NEWS_SCORE",
    "NEWS_BIAS",
    "NEWS_IMPACT",
    "NEWS_FLAG",
    "ENTRY_SCORE",
    "CONVICTION",
    "CONVICTION_SCORE",
    "CONVICTION_RANK",
]

df[output_cols].to_csv(OUTPUT_FILE, index=False)

# =========================================================
# SUMMARY
# =========================================================

print("\n✅ Conviction Scores Generated")

print(f"\n📁 Saved:\n{OUTPUT_FILE}")

print("\n📊 Conviction Distribution:\n")

print(df["CONVICTION"].value_counts())

print("\n🏆 Top Conviction Stocks:\n")

print(df[output_cols].head(20))
