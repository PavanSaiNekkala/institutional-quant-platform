from pathlib import Path

import pandas as pd
import yfinance as yf

# =========================================================
# FILES
# =========================================================

ROOT = Path(__file__).resolve().parents[2]
PORTFOLIO_FILE = ROOT / "data" / "optimised_portfolio.csv"

OUTPUT_FILE = ROOT / "data" / "execution_orders.csv"

# =========================================================
# SETTINGS
# =========================================================

TOTAL_CAPITAL = 1_000_000

CASH_BUFFER = 0.02

BROKERAGE_BPS = 5

SLIPPAGE_BPS = 10

# =========================================================
# LOAD
# =========================================================

print("\n📥 Loading Portfolio...")

df = pd.read_csv(PORTFOLIO_FILE)

# =========================================================
# WEIGHT DETECTION
# =========================================================

if "FINAL_WEIGHT" in df.columns:
    WEIGHT_COL = "FINAL_WEIGHT"

elif "TARGET_WEIGHT" in df.columns:
    WEIGHT_COL = "TARGET_WEIGHT"

elif "FINAL_WEIGHT_%" in df.columns:
    WEIGHT_COL = "FINAL_WEIGHT_%"

    df["FINAL_WEIGHT"] = df["FINAL_WEIGHT_%"] / 100

    WEIGHT_COL = "FINAL_WEIGHT"

elif "TARGET_WEIGHT_%" in df.columns:
    WEIGHT_COL = "TARGET_WEIGHT_%"

    df["TARGET_WEIGHT"] = df["TARGET_WEIGHT_%"] / 100

    WEIGHT_COL = "TARGET_WEIGHT"

else:
    raise ValueError("No portfolio weight column found.")

print(f"\nUsing Weight Column: {WEIGHT_COL}")

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
# DOWNLOAD LATEST PRICE
# =========================================================

print(f"\n📡 Downloading Prices ({len(symbols)} stocks)...")

price_df = yf.download(tickers=symbols, period="5d", auto_adjust=True, progress=False)

if price_df.empty:
    raise ValueError("Price download failed.")

# =========================================================
# EXTRACT LAST PRICE
# =========================================================

if isinstance(price_df.columns, pd.MultiIndex):
    close_prices = price_df["Close"].iloc[-1]

else:
    close_prices = price_df["Close"].iloc[-1]

price_map = {str(k): float(v) for k, v in close_prices.items()}

df["LAST_PRICE"] = df["YF_SYMBOL"].map(price_map)

# =========================================================
# HANDLE MISSING PRICES
# =========================================================

df = df.dropna(subset=["LAST_PRICE"])

# =========================================================
# CAPITAL ALLOCATION
# =========================================================

deployable_capital = TOTAL_CAPITAL * (1 - CASH_BUFFER)

df["ALLOCATED_CAPITAL"] = deployable_capital * df[WEIGHT_COL]

# =========================================================
# QUANTITY
# =========================================================

df["QUANTITY"] = (df["ALLOCATED_CAPITAL"] / df["LAST_PRICE"]).astype(int)

# =========================================================
# ACTUAL INVESTMENT
# =========================================================

df["INVESTED_AMOUNT"] = df["QUANTITY"] * df["LAST_PRICE"]

# =========================================================
# ACTUAL WEIGHT
# =========================================================

total_invested = df["INVESTED_AMOUNT"].sum()

df["ACTUAL_WEIGHT"] = df["INVESTED_AMOUNT"] / total_invested

df["ACTUAL_WEIGHT_%"] = (df["ACTUAL_WEIGHT"] * 100).round(2)

# =========================================================
# ORDER TYPE
# =========================================================

df["ACTION"] = "BUY"

# =========================================================
# CASH REPORT
# =========================================================

cash_used = df["INVESTED_AMOUNT"].sum()

cash_remaining = TOTAL_CAPITAL - cash_used

# =========================================================
# SORT
# =========================================================

df = df.sort_values(by="INVESTED_AMOUNT", ascending=False)

# =========================================================
# SAVE
# =========================================================

df.to_csv(OUTPUT_FILE, index=False)

# =========================================================
# REPORT
# =========================================================

print("\n✅ Execution Orders Generated")

print("\n📁 Saved:")

print(OUTPUT_FILE)

print(f"\n💰 Total Capital : ₹{TOTAL_CAPITAL:,.0f}")

print(f"💵 Invested      : ₹{cash_used:,.0f}")

print(f"🏦 Remaining     : ₹{cash_remaining:,.0f}")

print(f"💼 Utilization   : {(cash_used / TOTAL_CAPITAL) * 100:.2f}%")

print("\n🏆 Execution Sheet:\n")

print(
    df[["Symbol", "LAST_PRICE", "QUANTITY", "INVESTED_AMOUNT", "ACTUAL_WEIGHT_%", "ACTION"]].head(
        20
    )
)
