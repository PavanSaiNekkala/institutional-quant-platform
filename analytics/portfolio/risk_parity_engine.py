from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

# =========================================================
# FILES
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = ROOT / "data" / "position_sized_portfolio.csv"

OUTPUT_FILE = ROOT / "data" / "risk_parity_portfolio.csv"

# =========================================================
# SETTINGS
# =========================================================

LOOKBACK_DAYS = 252

# =========================================================
# LOAD
# =========================================================

print("\n📥 Loading Portfolio...")

df = pd.read_csv(INPUT_FILE)

# =========================================================
# SYMBOL CLEANUP
# =========================================================

symbols = []

for sym in df["Symbol"]:
    sym = str(sym).upper().strip()

    if not sym.endswith(".NS"):
        sym = sym + ".NS"

    symbols.append(sym)

df["YF_SYMBOL"] = symbols

# =========================================================
# DOWNLOAD PRICES
# =========================================================

print(f"\n📡 Downloading {len(symbols)} stocks...")

prices = yf.download(tickers=symbols, period="2y", auto_adjust=True, progress=False)

if prices.empty:
    raise ValueError("No price data downloaded.")

# =========================================================
# EXTRACT CLOSE
# =========================================================

if isinstance(prices.columns, pd.MultiIndex):
    close_prices = prices["Close"]

else:
    close_prices = prices

# =========================================================
# RETURNS
# =========================================================

returns = close_prices.pct_change(fill_method=None)

# =========================================================
# ANNUALIZED VOLATILITY
# =========================================================

volatility = returns.std() * np.sqrt(252)

vol_df = pd.DataFrame({"YF_SYMBOL": volatility.index, "VOLATILITY": volatility.values})

# =========================================================
# MERGE
# =========================================================

# =========================================================
# REMOVE OLD VOLATILITY
# =========================================================

df = df.drop(columns=["VOLATILITY"], errors="ignore")

df = df.drop(columns=["VOLATILITY_x", "VOLATILITY_y"], errors="ignore")

df = df.merge(vol_df, on="YF_SYMBOL", how="left")

df["VOLATILITY"] = df["VOLATILITY"].fillna(df["VOLATILITY"].median())

df["VOLATILITY"] = df["VOLATILITY"].replace(0, np.nan)

df["VOLATILITY"] = df["VOLATILITY"].fillna(df["VOLATILITY"].median())
# =========================================================
# RISK SCORE
# =========================================================
df["RISK_SCORE"] = df["MULTI_FACTOR_SCORE"] * (1 + df["ENTRY_SCORE"]) / df["VOLATILITY"]
# =========================================================
# NORMALIZE
# =========================================================

df["FINAL_WEIGHT"] = df["RISK_SCORE"] / df["RISK_SCORE"].sum()

df["FINAL_WEIGHT_%"] = (df["FINAL_WEIGHT"] * 100).round(2)

# =========================================================
# SORT
# =========================================================

df = df.sort_values(by="FINAL_WEIGHT", ascending=False)

# =========================================================
# SAVE
# =========================================================

df.to_csv(OUTPUT_FILE, index=False)

# =========================================================
# REPORT
# =========================================================

print("\n✅ Risk Parity Complete")

print("\n📁 Saved:")

print(OUTPUT_FILE)

print("\n🏆 Top Risk Adjusted Holdings:\n")

print(df[["Symbol", "MULTI_FACTOR_SCORE", "ENTRY_SCORE", "VOLATILITY", "FINAL_WEIGHT_%"]].head(20))
