from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

# =========================================================
# CONFIG
# =========================================================

DOWNLOAD_PERIOD = "6mo"

MAX_WORKERS = 3

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT_DIR / "data"

INPUT_FILE = DATA_DIR / "raw" / "updated_stocks.xlsx"

OUTPUT_FILE = DATA_DIR / "processed" / "liquidity_scores.csv"

# =========================================================
# LOAD STOCK UNIVERSE
# =========================================================

print("\n📥 Loading Stock Universe...")

df = pd.read_excel(INPUT_FILE)

possible_cols = ["Stock", "Symbol", "SYMBOL", "symbol"]

symbol_col = None

for col in possible_cols:
    if col in df.columns:
        symbol_col = col
        break

if symbol_col is None:
    raise Exception("❌ Symbol column not found")

symbols = (
    df[symbol_col]
    .dropna()
    .astype(str)
    .str.upper()
    .str.strip()
    .str.replace(".NS", "", regex=False)
    .unique()
    .tolist()
)

print(f"✅ Loaded {len(symbols)} symbols")
print("\nUnique Symbols Loaded:", len(symbols))

print("Original Rows:", len(df))

# =========================================================
# LIQUIDITY CALCULATION
# =========================================================


def calculate_liquidity(symbol):

    try:
        ticker = symbol

        if not ticker.endswith(".NS"):
            ticker = f"{ticker}.NS"

        data = yf.download(
            ticker, period=DOWNLOAD_PERIOD, auto_adjust=True, progress=False, threads=False
        )

        if data.empty:
            print(f"NO DATA -> {ticker}")
            return None

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        if "Close" not in data.columns or "Volume" not in data.columns:
            return None

        close = data["Close"].squeeze()

        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]

        volume = data["Volume"].squeeze()

        if isinstance(volume, pd.DataFrame):
            volume = volume.iloc[:, 0]

        latest_price = float(
            close.iloc[-1]
        )

        if pd.isna(latest_price):
            print(f"INVALID PRICE -> {ticker}")
            return None

        avg_volume_20d = float(
            volume.rolling(20).mean().iloc[-1]
        )

        if pd.isna(avg_volume_20d):
            print(f"INVALID VOLUME -> {ticker}")
            return None

        latest_price = float(latest_price)
        avg_volume_20d = float(avg_volume_20d)

        traded_value = latest_price * avg_volume_20d

        return {
            "Symbol": symbol,
            "Close": round(latest_price, 2),
            "AVG_20D_VOLUME": round(avg_volume_20d),
            "ADV_RUPEES": round(traded_value, 2),
        }
    except Exception as e:
        print(f"ERROR -> {ticker} -> {e}")
        return None


# =========================================================
# RUN
# =========================================================

print("\n🚀 Calculating Liquidity...")

results = []

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = {executor.submit(calculate_liquidity, symbol): symbol for symbol in symbols}

    total = len(futures)

    for idx, future in enumerate(as_completed(futures), start=1):
        result = future.result()

        if result:
            results.append(result)

            print(f"{idx}/{total} | {result['Symbol']}")

# =========================================================
# DATAFRAME
# =========================================================

liquidity_df = pd.DataFrame(results)

print("\n===== DOWNLOAD SUMMARY =====")

print("Universe:", len(symbols))
print("Downloaded:", len(liquidity_df))
print("Failed:", len(symbols) - len(liquidity_df))

if liquidity_df.empty:
    raise Exception("❌ No liquidity data generated")

# =========================================================
# LIQUIDITY SCORE
# =========================================================

liquidity_df["LIQUIDITY_SCORE"] = (
    liquidity_df["ADV_RUPEES"].rank(pct=True) * 100
)

liquidity_df["LIQUIDITY_RANK"] = liquidity_df["LIQUIDITY_SCORE"].rank(
    ascending=False, method="dense"
)

# =========================================================
# INSTITUTIONAL FILTER
# =========================================================

liquidity_df["LIQUIDITY_BUCKET"] = np.select(
    [
        liquidity_df["ADV_RUPEES"] >= 5e8,
        liquidity_df["ADV_RUPEES"] >= 1e8,
        liquidity_df["ADV_RUPEES"] >= 5e7
    ],
    ["HIGH", "MEDIUM", "LOW"],
    default="ILLIQUID",
)

# =========================================================
# SORT
# =========================================================

liquidity_df = liquidity_df.sort_values("LIQUIDITY_SCORE", ascending=False).reset_index(drop=True)

# =========================================================
# REMOVE DUPLICATE SYMBOLS
# =========================================================

before_rows = len(liquidity_df)

liquidity_df = (
    liquidity_df.sort_values("LIQUIDITY_SCORE", ascending=False)
    .drop_duplicates(subset=["Symbol"], keep="first")
    .reset_index(drop=True)
)

after_rows = len(liquidity_df)

print(f"\n🧹 Removed {before_rows - after_rows} duplicate rows")
print("\nLiquidity Rows:", len(liquidity_df))

print("Unique Symbols:", liquidity_df["Symbol"].nunique())
# =========================================================
# SAVE
# =========================================================

liquidity_df.to_csv(OUTPUT_FILE, index=False)

print("\n✅ Liquidity Scores Generated")

print(f"\n📁 Saved:\n{OUTPUT_FILE}")

print("\n🏆 Most Liquid Stocks:\n")

print(
    liquidity_df[
        [
            "Symbol",
            "ADV_RUPEES",
            "LIQUIDITY_SCORE",
            "LIQUIDITY_BUCKET",
        ]
    ].head(20)
)
