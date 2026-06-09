from pathlib import Path

import pandas as pd
import yfinance as yf

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

CACHE_DIR = ROOT / "data" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

CACHE_FILE = CACHE_DIR / "stock_prices.parquet"

UNIVERSE_FILE = ROOT / "data" / "raw" / "valid_stocks.xlsx"

# =========================================================
# LOAD UNIVERSE
# =========================================================

print("\n📥 Loading Universe...")

universe = pd.read_excel(UNIVERSE_FILE)

if "Stock" not in universe.columns:
    raise ValueError("Stock column missing")

symbols = universe["Stock"].dropna().astype(str).str.upper().str.strip()

symbols = [s if s.endswith(".NS") else f"{s}.NS" for s in symbols]

symbols = list(dict.fromkeys(symbols))

print(f"\n📊 Symbols: {len(symbols)}")

# =========================================================
# LOAD CACHE
# =========================================================

cache_df = None

if CACHE_FILE.exists():
    try:
        cache_df = pd.read_parquet(CACHE_FILE)

        cache_df.index = pd.to_datetime(cache_df.index)

        last_date = cache_df.index.max()

        print("\n✅ Cache Found")

        print(f"Last Date : {last_date.date()}")

    except Exception as e:
        print(f"\n⚠ Cache Read Failed: {e}")

        cache_df = None

# =========================================================
# DETERMINE DOWNLOAD PERIOD
# =========================================================

if cache_df is None:
    period = "18mo"

    start_date = None

    print("\n⚡ Full Historical Download")

else:
    last_date = cache_df.index.max()

    days_missing = (pd.Timestamp.today().normalize() - last_date.normalize()).days

    if days_missing <= 1:
        print("\n✅ Cache Already Current")

        print("\n💾 No Download Required")

        raise SystemExit

    start_date = (last_date - pd.Timedelta(days=5)).strftime("%Y-%m-%d")

    period = None

    print(f"\n⚡ Incremental Update ({days_missing} days)")

# =========================================================
# DOWNLOAD
# =========================================================

all_frames = []

BATCH_SIZE = 100

for i in range(0, len(symbols), BATCH_SIZE):
    batch = symbols[i : i + BATCH_SIZE]

    print(f"\nDownloading {i + 1}-{min(i + BATCH_SIZE, len(symbols))}")

    try:
        if start_date:
            data = yf.download(
                batch,
                start=start_date,
                auto_adjust=True,
                progress=False,
                threads=True,
                group_by="ticker",
            )

        else:
            data = yf.download(
                batch,
                period=period,
                auto_adjust=True,
                progress=False,
                threads=True,
                group_by="ticker",
            )

        if not data.empty:
            all_frames.append(data)

    except Exception as e:
        print(e)

# =========================================================
# VALIDATE
# =========================================================

if len(all_frames) == 0:
    raise ValueError("No price data downloaded.")

new_data = pd.concat(all_frames, axis=1)

# =========================================================
# MERGE CACHE
# =========================================================

if cache_df is not None:
    combined = pd.concat([cache_df, new_data])

    combined = combined[~combined.index.duplicated(keep="last")]

    combined = combined.sort_index()

else:
    combined = new_data

# =========================================================
# CLEAN
# =========================================================

combined = combined.ffill(limit=5)

# =========================================================
# SAVE
# =========================================================

combined.to_parquet(CACHE_FILE, index=True)

print("\n💾 Cache Updated")

print(f"\nRows: {combined.shape[0]}")

print(f"Symbols: {len(combined.columns.get_level_values(0).unique())}")

print(f"\nSaved:\n{CACHE_FILE}")
