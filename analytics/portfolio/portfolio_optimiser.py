from pathlib import Path

import pandas as pd

# =========================================================
# FILES
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = ROOT / "data" / "portfolio" / "risk_parity_portfolio.csv"

OUTPUT_FILE = ROOT / "data" / "portfolio" / "optimised_portfolio.csv"

# =========================================================
# SETTINGS
# =========================================================

MAX_WEIGHT = 0.10
MIN_WEIGHT = 0.02

# =========================================================
# LOAD
# =========================================================

print("\n📥 Loading Portfolio...")

df = pd.read_csv(INPUT_FILE)

# =========================================================
# VALIDATION
# =========================================================

required_cols = ["CONVICTION_SCORE", "EXPECTED_RETURN_30D", "VOLATILITY"]

for col in required_cols:
    if col not in df.columns:
        raise ValueError(f"Missing column: {col}")

# =========================================================
# FILL NA
# =========================================================

df["CONVICTION_SCORE"] = df["CONVICTION_SCORE"].fillna(df["CONVICTION_SCORE"].median())

df["EXPECTED_RETURN_30D"] = df["EXPECTED_RETURN_30D"].fillna(df["EXPECTED_RETURN_30D"].median())

df["VOLATILITY"] = df["VOLATILITY"].fillna(df["VOLATILITY"].median())

# =========================================================
# NORMALIZATION
# =========================================================

df["CONVICTION_NORM"] = df["CONVICTION_SCORE"] / df["CONVICTION_SCORE"].max()

df["RETURN_NORM"] = df["EXPECTED_RETURN_30D"] / df["EXPECTED_RETURN_30D"].max()

df["VOL_NORM"] = df["VOLATILITY"] / df["VOLATILITY"].max()

# =========================================================
# OPTIMISER SCORE
# =========================================================

df["OPTIMISER_SCORE"] = (
    df["CONVICTION_NORM"] * 0.40 + df["RETURN_NORM"] * 0.40 + (1 - df["VOL_NORM"]) * 0.20
)

# =========================================================
# INITIAL WEIGHTS
# =========================================================

df["OPT_WEIGHT"] = df["OPTIMISER_SCORE"] / df["OPTIMISER_SCORE"].sum()

# =========================================================
# POSITION LIMITS
# =========================================================

df["OPT_WEIGHT"] = df["OPT_WEIGHT"].clip(lower=MIN_WEIGHT, upper=MAX_WEIGHT)

df["OPT_WEIGHT"] = df["OPT_WEIGHT"] / df["OPT_WEIGHT"].sum()

# =========================================================
# PERCENT FORMAT
# =========================================================

df["OPT_WEIGHT_%"] = (df["OPT_WEIGHT"] * 100).round(2)

# =========================================================
# EXPECTED PORTFOLIO RETURN
# =========================================================

portfolio_return = (df["OPT_WEIGHT"] * df["EXPECTED_RETURN_30D"]).sum()

# =========================================================
# EXPECTED PORTFOLIO VOL
# =========================================================

portfolio_vol = (df["OPT_WEIGHT"] * df["VOLATILITY"]).sum()

# =========================================================
# SHARPE APPROXIMATION
# =========================================================

sharpe = portfolio_return / portfolio_vol

# =========================================================
# SORT
# =========================================================

df = df.sort_values(by="OPT_WEIGHT", ascending=False)

# =========================================================
# SAVE
# =========================================================

df.to_csv(OUTPUT_FILE, index=False)

# =========================================================
# REPORT
# =========================================================

print("\n✅ Portfolio Optimisation Complete")

print("\n📁 Saved:")

print(OUTPUT_FILE)

print("\n📈 Portfolio Statistics")

print(f"\nExpected Return : {portfolio_return:.2f}%")

print(f"Expected Volatility : {portfolio_vol:.2f}")

print(f"Sharpe Approx : {sharpe:.2f}")

print("\n🏆 Top Holdings:\n")

print(
    df[["Symbol", "OPT_WEIGHT_%", "CONVICTION_SCORE", "EXPECTED_RETURN_30D", "VOLATILITY"]].head(20)
)
