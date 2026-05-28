import pandas as pd
import yfinance as yf
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT_DIR / "data" / "valid_stocks.xlsx"

OUTPUT_FILE = ROOT_DIR / "data" / "stock_metadata.csv"

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
    .unique()
    .tolist()
)

print(f"\n✅ Loaded {len(symbols)} stocks")

# =========================================================
# FETCH METADATA
# =========================================================

def fetch_metadata(symbol):

    try:

        ticker = yf.Ticker(f"{symbol}.NS")

        info = ticker.info

        return {

            "Symbol": symbol,

            "Sector": info.get(
                "sector",
                "Unknown"
            ),

            "Industry": info.get(
                "industry",
                "Unknown"
            ),

            "MarketCap": info.get(
                "marketCap",
                0
            ),

            "Beta": info.get(
                "beta",
                None
            ),

            "AvgVolume": info.get(
                "averageVolume",
                0
            )
        }

    except Exception as e:

        print(f"❌ {symbol} -> {e}")

        return {

            "Symbol": symbol,

            "Sector": "Unknown",

            "Industry": "Unknown",

            "MarketCap": 0,

            "Beta": None,

            "AvgVolume": 0
        }

# =========================================================
# MULTITHREAD DOWNLOAD
# =========================================================

results = []

MAX_WORKERS = 10

with ThreadPoolExecutor(
    max_workers=MAX_WORKERS
) as executor:

    futures = {

        executor.submit(
            fetch_metadata,
            symbol
        ): symbol

        for symbol in symbols
    }

    for idx, future in enumerate(
        as_completed(futures),
        start=1
    ):

        result = future.result()

        results.append(result)

        print(
            f"{idx}/{len(symbols)} | "
            f"{result['Symbol']} | "
            f"{result['Sector']}"
        )

        time.sleep(0.05)

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
# SORT
# =========================================================

metadata_df = metadata_df.sort_values(
    by="MarketCap",
    ascending=False
)

# =========================================================
# SAVE
# =========================================================

metadata_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    f"\n✅ stock_metadata.csv saved successfully"
)

print(
    f"\n✅ Total Stocks Saved: "
    f"{len(metadata_df)}"
)
