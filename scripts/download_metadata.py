import pandas as pd
import yfinance as yf
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT_DIR / "data" / "updated_stocks.xlsx"

OUTPUT_FILE = ROOT_DIR / "data" / "stock_metadata.csv"

# =========================================================
# CONFIG
# =========================================================

MAX_WORKERS = 5
REQUEST_DELAY = 0.5
BATCH_SIZE = 50
BATCH_COOLDOWN = 5
MAX_RETRIES = 3

# =========================================================
# LOAD STOCKS
# =========================================================

df = pd.read_excel(INPUT_FILE)

possible_cols = [
        "Stock",
        "Symbol",
        "SYMBOL",
        "symbol"
]

symbol_col = None

for col in possible_cols:

        if col in df.columns:

                symbol_col = col
                break

if symbol_col is None:

        raise Exception(
                f"Symbol column not found. "
                f"Available columns: {df.columns.tolist()}"
        )

symbols = (
        df[symbol_col]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
)

# =========================================================
# REMOVE .NS IF ALREADY EXISTS
# =========================================================

symbols = [

        symbol.replace(".NS", "")

        for symbol in symbols
]

print(f"\n✅ Loaded {len(symbols)} stocks")

# =========================================================
# FETCH METADATA
# =========================================================

def fetch_metadata(symbol):

        yahoo_symbol = f"{symbol}.NS"

        for attempt in range(MAX_RETRIES):

                try:

                        time.sleep(REQUEST_DELAY)

                        ticker = yf.Ticker(yahoo_symbol)

                        info = ticker.info

                        if not info:

                                raise Exception("Empty response")

                        market_cap = info.get(
                                "marketCap",
                                0
                        )

                        sector = info.get(
                                "sector",
                                "Unknown"
                        )

                        industry = info.get(
                                "industry",
                                "Unknown"
                        )

                        beta = info.get(
                                "beta",
                                None
                        )

                        avg_volume = info.get(
                                "averageVolume",
                                0
                        )

                        return {

                                "Symbol": symbol,

                                "Sector": sector,

                                "Industry": industry,

                                "MarketCap": market_cap,

                                "Beta": beta,

                                "AvgVolume": avg_volume
                        }

                except Exception as e:

                        error_msg = str(e)

                        # =================================================
                        # RATE LIMIT HANDLING
                        # =================================================

                        if (
                                "Too Many Requests" in error_msg
                                or "Rate limited" in error_msg
                                or "401" in error_msg
                        ):

                                wait_time = (
                                        5 * (attempt + 1)
                                )

                                print(
                                        f"⏳ {symbol} "
                                        f"Rate Limited "
                                        f"Retrying in "
                                        f"{wait_time}s..."
                                )

                                time.sleep(wait_time)

                        else:

                                print(
                                        f"❌ {symbol} -> {e}"
                                )

                                break

        return {

                "Symbol": symbol,

                "Sector": "Unknown",

                "Industry": "Unknown",

                "MarketCap": 0,

                "Beta": None,

                "AvgVolume": 0
        }

# =========================================================
# DOWNLOAD METADATA
# =========================================================

results = []

TOTAL = len(symbols)

for batch_start in range(
        0,
        TOTAL,
        BATCH_SIZE
):

        batch_symbols = symbols[
                batch_start:
                batch_start + BATCH_SIZE
        ]

        batch_number = (
                batch_start // BATCH_SIZE
        ) + 1

        print(
                f"\n🚀 Processing Batch "
                f"{batch_number}"
        )

        with ThreadPoolExecutor(
                max_workers=MAX_WORKERS
        ) as executor:

                futures = {

                        executor.submit(
                                fetch_metadata,
                                symbol
                        ): symbol

                        for symbol in batch_symbols
                }

                for idx, future in enumerate(
                        as_completed(futures),
                        start=batch_start + 1
                ):

                        result = future.result()

                        results.append(result)

                        print(
                                f"{idx}/{TOTAL} | "
                                f"{result['Symbol']} | "
                                f"{result['Sector']} | "
                                f"MCAP: {result['MarketCap']}"
                        )

        # =================================================
        # COOL DOWN BETWEEN BATCHES
        # =================================================

        if batch_start + BATCH_SIZE < TOTAL:

                print(
                        f"\n⏳ Cooling Down "
                        f"{BATCH_COOLDOWN}s..."
                )

                time.sleep(BATCH_COOLDOWN)

# =========================================================
# DATAFRAME
# =========================================================

metadata_df = pd.DataFrame(results)

# =========================================================
# REMOVE DUPLICATES
# =========================================================

metadata_df = metadata_df.drop_duplicates(
        subset=["Symbol"]
)

# =========================================================
# MARKET CAP CATEGORY
# =========================================================

def classify_market_cap(mcap):

        if mcap >= 200000000000:

                return "Large Cap"

        elif mcap >= 50000000000:

                return "Mid Cap"

        elif mcap > 0:

                return "Small Cap"

        return "Unknown"

metadata_df["MARKET_CAP_CATEGORY"] = (
        metadata_df["MarketCap"]
        .apply(classify_market_cap)
)

# =========================================================
# SORT
# =========================================================

metadata_df = metadata_df.sort_values(
        by="MarketCap",
        ascending=False
)

# =========================================================
# RESET INDEX
# =========================================================

metadata_df = metadata_df.reset_index(
        drop=True
)

# =========================================================
# SAVE CSV
# =========================================================

metadata_df.to_csv(
        OUTPUT_FILE,
        index=False
)

# =========================================================
# SUMMARY
# =========================================================

SUCCESS = len(
        metadata_df[
                metadata_df["MarketCap"] > 0
        ]
)

FAILED = len(
        metadata_df[
                metadata_df["MarketCap"] == 0
        ]
)

print("\n====================================")

print(
        f"✅ stock_metadata.csv saved successfully"
)

print(
        f"\n📁 Location:\n{OUTPUT_FILE}"
)

print(
        f"\n✅ Success: {SUCCESS}"
)

print(
        f"❌ Failed: {FAILED}"
)

print(
        f"📊 Total Stocks: {len(metadata_df)}"
)

print("====================================\n")
