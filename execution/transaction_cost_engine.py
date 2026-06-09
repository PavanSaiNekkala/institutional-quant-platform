from pathlib import Path

import pandas as pd

# =========================================================
# FILES
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

BLOTTER_FILE = ROOT / "data" / "trade_blotter.csv"

OUTPUT_FILE = ROOT / "data" / "trade_blotter_costed.csv"

# =========================================================
# COST SETTINGS
# =========================================================

BROKERAGE = 0.0003
STT = 0.0010
SLIPPAGE = 0.0005
IMPACT_COST = 0.0005

# =========================================================
# LOAD
# =========================================================

print("\n📥 Loading Trade Blotter...")

df = pd.read_csv(BLOTTER_FILE)

# =========================================================
# TOTAL COST %
# =========================================================

TOTAL_COST_RATE = BROKERAGE + STT + SLIPPAGE + IMPACT_COST

# =========================================================
# COSTS
# =========================================================

df["TRANSACTION_COST"] = (df["ORDER_VALUE"] * TOTAL_COST_RATE).round(2)

# =========================================================
# NET TRADE VALUE
# =========================================================

df["NET_ORDER_VALUE"] = (df["ORDER_VALUE"] - df["TRANSACTION_COST"]).round(2)

# =========================================================
# PORTFOLIO TOTALS
# =========================================================

gross = df["ORDER_VALUE"].sum()

cost = df["TRANSACTION_COST"].sum()

net = df["NET_ORDER_VALUE"].sum()

# =========================================================
# SAVE
# =========================================================

df.to_csv(OUTPUT_FILE, index=False)

# =========================================================
# REPORT
# =========================================================

print("\n✅ Transaction Costs Applied")

print("\nGross Value :", round(gross, 2))
print("Cost Value  :", round(cost, 2))
print("Net Value   :", round(net, 2))

print("\nCost %")

print(round((cost / gross) * 100, 3))

print("\n📁 Saved:")

print(OUTPUT_FILE)

print("\n🏆 Highest Cost Trades:\n")

print(
    df[["Symbol", "ACTION", "ORDER_VALUE", "TRANSACTION_COST"]]
    .sort_values(by="TRANSACTION_COST", ascending=False)
    .head(20)
)
