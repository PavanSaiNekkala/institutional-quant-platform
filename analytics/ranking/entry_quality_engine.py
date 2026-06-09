from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
import yfinance as yf

# =========================================================
# CONFIG
# =========================================================

DOWNLOAD_PERIOD = "1y"

MAX_WORKERS = 5

MIN_HISTORY = 100

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT_DIR / "data"

INPUT_FILE = DATA_DIR / "raw" / "updated_stocks.xlsx"

OUTPUT_FILE = DATA_DIR / "processed" / "entry_quality_scores.csv"

CACHE_FILE = DATA_DIR / "cache" / "entry_quality_cache.parquet"
CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

DATA_DIR.mkdir(parents=True, exist_ok=True)

# =========================================================
# LOAD SYMBOLS
# =========================================================

print("\n📥 Loading Stock Universe...")

if not INPUT_FILE.exists():
    raise FileNotFoundError(f"\n❌ Missing file:\n{INPUT_FILE}")

df = pd.read_excel(INPUT_FILE)

possible_cols = ["Stock", "Symbol", "SYMBOL", "symbol"]

symbol_col = None

for col in possible_cols:
    if col in df.columns:
        symbol_col = col
        break

if symbol_col is None:
    raise Exception("\n❌ Symbol column not found")

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

print(f"\n✅ Loaded {len(symbols)} symbols")
print("\nSample symbols:")

print(symbols[:10])

# =========================================================
# RSI
# =========================================================


def calculate_rsi(series, period=14):

    delta = series.diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()

    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi


# =========================================================
# ENTRY QUALITY
# =========================================================


def calculate_entry_score(symbol):

    try:
        symbol = str(symbol).upper().strip()

        if not symbol.endswith(".NS"):
            symbol = f"{symbol}.NS"

        data = yf.download(
            symbol, period=DOWNLOAD_PERIOD, auto_adjust=True, progress=False, threads=False
        )

        if data.empty:
            print(f"❌ No Yahoo data: {symbol}")

            return None

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        required_cols = ["Close", "Volume"]

        for col in required_cols:
            if col not in data.columns:
                return None

        data = data.dropna()

        if len(data) < MIN_HISTORY:
            print(f"❌ Insufficient history: {symbol} | {len(data)} rows")

            return None

        close = data["Close"]

        volume = data["Volume"]

        latest_close = float(close.iloc[-1])

        ema20 = float(close.ewm(span=20, adjust=False).mean().iloc[-1])

        ema50 = float(close.ewm(span=50, adjust=False).mean().iloc[-1])

        rsi = float(calculate_rsi(close).iloc[-1])

        avg_volume = float(volume.rolling(20).mean().iloc[-1])

        volume_ratio = volume.iloc[-1] / avg_volume if avg_volume > 0 else 0

        high_52w = float(close.max())

        if high_52w > 0:
            distance_to_high = ((latest_close / high_52w) - 1) * 100

        else:
            distance_to_high = 0

        # =========================================
        # ENTRY SCORE
        # =========================================

        score = 0

        # Trend

        if latest_close > ema20:
            score += 2

        # EMA Alignment

        if ema20 > ema50:
            score += 2

        # RSI Strength

        if rsi > 60:
            score += 1

        # Volume Expansion

        if volume_ratio > 1.5:
            score += 2

        # Near 52W High

        if distance_to_high >= -5:
            score += 3

        return {
            "Symbol": symbol,
            "ENTRY_SCORE": score,
            "RSI": round(rsi, 2),
            "VOLUME_RATIO": round(volume_ratio, 2),
            "EMA20": round(ema20, 2),
            "EMA50": round(ema50, 2),
            "DISTANCE_TO_HIGH": round(distance_to_high * 100, 2),
        }

    except Exception as e:
        print(f"❌ {symbol}: {e}")

        return None


# =========================================================
# RUN
# =========================================================

# =========================================================
# CACHE
# =========================================================

if CACHE_FILE.exists():
    cache_df = pd.read_parquet(CACHE_FILE)

    cache_df["LAST_UPDATED"] = pd.to_datetime(cache_df["LAST_UPDATED"])

else:
    cache_df = pd.DataFrame()

symbols_to_refresh = []

cached_results = []

REFRESH_DAYS = 1

for symbol in symbols:
    if cache_df.empty:
        symbols_to_refresh.append(symbol)

        continue

    cached = cache_df[cache_df["Symbol"] == f"{symbol}.NS"]

    if cached.empty:
        symbols_to_refresh.append(symbol)

        continue

    age_days = (pd.Timestamp.now() - cached.iloc[0]["LAST_UPDATED"]).days

    if age_days >= REFRESH_DAYS:
        symbols_to_refresh.append(symbol)

    else:
        cached_results.append(cached.iloc[0].to_dict())

print(f"\nUsing Cache: {len(cached_results)}")

print(f"Refreshing: {len(symbols_to_refresh)}")

print("\n🚀 Calculating Entry Scores...")

results = []

print("\n🧪 Testing first symbol...")

print(calculate_entry_score(symbols[0]))

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = {
        executor.submit(calculate_entry_score, symbol): symbol for symbol in symbols_to_refresh
    }

    total = len(futures)

    for idx, future in enumerate(as_completed(futures), start=1):
        result = future.result()

        if result:
            results.append(result)

            print(f"{idx}/{total} | {result['Symbol']} | ENTRY_SCORE: {result['ENTRY_SCORE']}")

# =========================================================
# DATAFRAME
# =========================================================

new_df = pd.DataFrame(results)

if not new_df.empty:
    new_df["LAST_UPDATED"] = pd.Timestamp.now()

entry_df = pd.concat([pd.DataFrame(cached_results), new_df], ignore_index=True)

entry_df = entry_df.drop_duplicates(subset="Symbol", keep="last")

if entry_df.empty:
    raise Exception("\n❌ No stocks processed")

# Save Cache

entry_df.to_parquet(CACHE_FILE, index=False)

# =========================================================
# RANK
# =========================================================

entry_df["ENTRY_RANK"] = entry_df["ENTRY_SCORE"].rank(ascending=False, method="dense")

# =========================================================
# SAVE
# =========================================================

entry_df = entry_df.sort_values("ENTRY_SCORE", ascending=False)

entry_df.to_csv(OUTPUT_FILE, index=False)

print("\n✅ Entry Quality Scores Generated")

print(f"\n📁 Saved:\n{OUTPUT_FILE}")

print("\n🏆 Top Entry Candidates:\n")

print(entry_df.head(10))
