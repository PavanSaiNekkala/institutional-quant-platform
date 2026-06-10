from pathlib import Path

import pandas as pd
import yfinance as yf

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

OUTPUT_FILE = (
    ROOT
    / "data"
    / "market"
    / "benchmark_returns.csv"
)

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

# =========================================================
# CONFIG
# =========================================================

BENCHMARK = "^CRSLDX"  # Nifty 500 Total Return Index
LOOKBACK = "10y"

# =========================================================
# DOWNLOAD
# =========================================================

print("\n📡 Downloading Benchmark...")

benchmark = yf.download(
    BENCHMARK,
    period=LOOKBACK,
    auto_adjust=True,
    progress=False,
)

if benchmark.empty:
    raise ValueError(
        f"❌ Benchmark download failed: {BENCHMARK}"
    )

# =========================================================
# HANDLE YFINANCE MULTIINDEX
# =========================================================

if isinstance(benchmark.columns, pd.MultiIndex):

    if "Close" not in benchmark.columns.get_level_values(0):
        raise ValueError("❌ Close column not found")

    close_prices = benchmark["Close"].iloc[:, 0]

else:
    close_prices = benchmark["Close"]

# =========================================================
# RETURNS
# =========================================================

returns = close_prices.pct_change().dropna()

# =========================================================
# OUTPUT DATAFRAME
# =========================================================

df = returns.reset_index()

df.columns = [
    "Date",
    "Benchmark_Return",
]

df["Date"] = pd.to_datetime(df["Date"])

# =========================================================
# SAVE
# =========================================================

df.to_csv(
    OUTPUT_FILE,
    index=False,
)

# =========================================================
# SUMMARY
# =========================================================

print("\n✅ Benchmark Returns Generated")

print(f"\n📁 Saved:\n{OUTPUT_FILE}")

print("\n📊 Dataset Summary")

print(f"Rows      : {len(df):,}")

print(f"Start Date: {df['Date'].min().date()}")

print(f"End Date  : {df['Date'].max().date()}")

print("\nLast 5 Records")

print(df.tail())
