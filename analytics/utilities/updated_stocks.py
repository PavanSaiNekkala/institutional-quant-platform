from pathlib import Path

import pandas as pd

# =====================================================
# INPUT / OUTPUT
# =====================================================

ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT / "data"

DATA_DIR.mkdir(parents=True, exist_ok=True)


INPUT_FILE = ROOT / "data" / "raw" / "valid_stocks.xlsx"

OUTPUT_FILE = ROOT / "data" / "raw" / "updated_stocks.xlsx"

# =====================================================
# PRICE CACHE
# =====================================================

PRICE_CACHE_FILE = ROOT / "data" / "cache" / "stock_prices.parquet"

PRICE_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

SHEET_NAME = 0

# =====================================================
# LOAD
# =====================================================

print("\nLoading Excel...")

df = pd.read_excel(INPUT_FILE, sheet_name=SHEET_NAME)

# =====================================================
# SYMBOL COLUMN
# =====================================================

SYMBOL_COL = "Stock"

if SYMBOL_COL not in df.columns:
    raise ValueError(f"{SYMBOL_COL} column not found")

# =====================================================
# CLEAN SYMBOLS
# =====================================================

symbols = df[SYMBOL_COL].dropna().astype(str).str.strip().str.upper()

symbols = [s if s.endswith(".NS") else f"{s}.NS" for s in symbols]

symbols = list(dict.fromkeys(symbols))

symbols = [s for s in symbols if isinstance(s, str) and len(s) > 3]

print(f"\nTotal Stocks: {len(symbols)}")

updated_stocks = []

close_df = None

# =====================================================
# LOAD MASTER CACHE
# =====================================================

if not PRICE_CACHE_FILE.exists():
    raise FileNotFoundError(
        f"\nMissing cache:\n{PRICE_CACHE_FILE}\nRun update_price_cache.py first."
    )

close_df = pd.read_parquet(PRICE_CACHE_FILE)

if isinstance(close_df.columns, pd.MultiIndex):
    print("\n⚠ MultiIndex Columns Found")

    print(close_df.columns.names)

    if "Close" in close_df.columns.get_level_values(-1):
        close_df = close_df.xs("Close", axis=1, level=-1)

        print("\n✅ Extracted Close Prices")

close_df.index = pd.to_datetime(close_df.index)

last_date = close_df.index.max()

days_old = (pd.Timestamp.today().normalize() - last_date.normalize()).days

print(f"\n📅 Cache Age: {days_old} days")

if days_old > 3:
    print("\n⚠️ Cache older than 3 days.\nRun update_price_cache.py.")

print(f"\n✅ Loaded Price Cache ({close_df.shape[0]} rows x {close_df.shape[1]} columns)")

for symbol in symbols:
    try:
        if symbol not in close_df.columns:
            continue

        close_series = close_df[symbol].dropna()

        if len(close_series) < 200:
            continue

        latest_close = float(close_series.iloc[-1])

        returns = close_series.pct_change()

        volatility_pct = returns.abs().rolling(14).mean().iloc[-1] * 100

        if latest_close < 10:
            continue

        if volatility_pct > 6:
            continue

        updated_stocks.append(
            {
                "Symbol": symbol,
                "Close": round(latest_close, 2),
                "VOLATILITY_PCT": round(volatility_pct, 2),
                "History_Days": len(close_series),
            }
        )

    except Exception as e:
        print(f"{symbol} skipped: {e}")

print("\n======================")
print("FILTER STATISTICS")
print("======================")

history_fail = 0
price_fail = 0
vol_fail = 0
passed = 0

for symbol in symbols:
    if symbol not in close_df.columns:
        continue

    close_series = close_df[symbol].dropna()

    if len(close_series) < 200:
        history_fail += 1
        continue

    latest_close = float(close_series.iloc[-1])

    returns = close_series.pct_change()

    volatility_pct = returns.abs().rolling(14).mean().iloc[-1] * 100

    if latest_close < 10:
        price_fail += 1
        continue

    if volatility_pct > 12:
        vol_fail += 1
        continue

    passed += 1

print(f"History Fail : {history_fail}")
print(f"Price Fail   : {price_fail}")
print(f"Vol Fail     : {vol_fail}")
print(f"Passed       : {passed}")

if len(updated_stocks) == 0:
    raise ValueError("No stocks passed validation filters.")

updated_df = pd.DataFrame(updated_stocks)

metadata_file = ROOT / "data" / "raw" / "stock_metadata.csv"

if metadata_file.exists():
    metadata = pd.read_csv(metadata_file)

    metadata.columns = metadata.columns.str.strip()

    print("\nMetadata Columns:")
    print(metadata.columns.tolist())

    metadata["Symbol"] = metadata["Symbol"].astype(str).str.strip().str.upper()

    # Handle different naming conventions

    if "Market_Cap" not in metadata.columns:
        if "MarketCap" in metadata.columns:
            metadata = metadata.rename(columns={"MarketCap": "Market_Cap"})

        elif "Market Cap" in metadata.columns:
            metadata = metadata.rename(columns={"Market Cap": "Market_Cap"})

        else:
            raise ValueError(
                f"Market cap column not found. Available columns: {metadata.columns.tolist()}"
            )

    updated_df = updated_df.merge(metadata[["Symbol", "Market_Cap"]], on="Symbol", how="left")

    updated_df["Market_Cap"] = pd.to_numeric(updated_df["Market_Cap"], errors="coerce").fillna(0)

else:
    print("\nWARNING: stock_metadata.csv not found")

    updated_df["Market_Cap"] = 0

updated_df = updated_df[updated_df["Market_Cap"] >= 100_000_000]

if updated_df.empty:
    raise ValueError("No stocks survived market cap filter.")

updated_df = updated_df.sort_values(["Market_Cap"], ascending=False)

print("\nLargest Market Cap:")

print(updated_df.nlargest(10, "Market_Cap")[["Symbol", "Market_Cap"]])

temp_file = OUTPUT_FILE.parent / "updated_stocks_tmp.xlsx"

updated_df.to_excel(temp_file, index=False)

if OUTPUT_FILE.exists():
    OUTPUT_FILE.unlink()

temp_file.rename(OUTPUT_FILE)

# =====================================================
# REPORT
# =====================================================

print(f"\nupdated Stocks : {len(updated_df)}")

print(f"Removed Stocks : {len(symbols) - len(updated_df)}")

print(f"\nSaved:\n{OUTPUT_FILE}")
