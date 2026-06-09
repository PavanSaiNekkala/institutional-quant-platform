from pathlib import Path

import pandas as pd

# =========================================================
# FILES
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = ROOT / "data" / "risk_parity_portfolio.csv"

OUTPUT_FILE = ROOT / "data" / "performance_attribution.csv"

# =========================================================
# LOAD
# =========================================================

print("\n📥 Loading Portfolio...")

df = pd.read_csv(INPUT_FILE)

# =========================================================
# COLUMN VALIDATION
# =========================================================

required_cols = ["Symbol", "FINAL_WEIGHT", "EXPECTED_RETURN_30D"]

missing = [col for col in required_cols if col not in df.columns]

if len(missing) > 0:
    raise ValueError(f"Missing columns: {missing}")

# =========================================================
# CLEAN
# =========================================================

df["FINAL_WEIGHT"] = pd.to_numeric(df["FINAL_WEIGHT"], errors="coerce").fillna(0)

df["EXPECTED_RETURN_30D"] = pd.to_numeric(df["EXPECTED_RETURN_30D"], errors="coerce").fillna(0)

# =========================================================
# CONTRIBUTION
# =========================================================

df["CONTRIBUTION"] = df["FINAL_WEIGHT"] * df["EXPECTED_RETURN_30D"]

# =========================================================
# PORTFOLIO EXPECTED RETURN
# =========================================================

portfolio_expected_return = df["CONTRIBUTION"].sum()

# =========================================================
# CONTRIBUTION %
# =========================================================

df["CONTRIBUTION_%"] = (df["CONTRIBUTION"] / portfolio_expected_return * 100).round(2)

# =========================================================
# ALPHA CONTRIBUTION
# =========================================================

df["ALPHA_CONTRIBUTION"] = (df["EXPECTED_RETURN_30D"] - portfolio_expected_return) * df[
    "FINAL_WEIGHT"
]

# =========================================================
# RISK ADJUSTED CONTRIBUTION
# =========================================================

if "VOLATILITY" in df.columns:
    df["RISK_ADJ_CONTRIBUTION"] = df["CONTRIBUTION"] / df["VOLATILITY"]

else:
    df["RISK_ADJ_CONTRIBUTION"] = df["CONTRIBUTION"]

# =========================================================
# RANKING
# =========================================================

df = df.sort_values(by="CONTRIBUTION", ascending=False)

df["ATTRIBUTION_RANK"] = range(1, len(df) + 1)

# =========================================================
# SAVE
# =========================================================

df.to_csv(OUTPUT_FILE, index=False)

# =========================================================
# SUMMARY
# =========================================================

print("\n✅ Performance Attribution Complete")

print("\n📁 Saved:")

print(OUTPUT_FILE)

print(f"\n📈 Portfolio Expected Return: {portfolio_expected_return:.2f}%")

print("\n🏆 Top Contributors:\n")

print(
    df[
        [
            "Symbol",
            "FINAL_WEIGHT",
            "EXPECTED_RETURN_30D",
            "CONTRIBUTION",
            "CONTRIBUTION_%",
            "ATTRIBUTION_RANK",
        ]
    ].head(20)
)

# =========================================================
# ATTRIBUTION SUMMARY
# =========================================================

print("\n📊 Attribution Summary")

print(df[["CONTRIBUTION", "ALPHA_CONTRIBUTION", "RISK_ADJ_CONTRIBUTION"]].describe())
