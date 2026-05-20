import pandas as pd
import yfinance as yf
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[1]

NSE_FILE = ROOT_DIR / "data" / "valid_stocks.xlsx"

OUTPUT_FILE = ROOT_DIR / "data" / "market_caps.csv"

# =========================================================
# LOAD NSE STOCKS
# =========================================================

df = pd.read_excel(NSE_FILE)

# =========================================================
# AUTO DETECT SYMBOL COLUMN
# =========================================================

possible_cols = [
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

# =========================================================
# FORMAT SYMBOLS
# =========================================================

symbols = [

    s if s.endswith(".NS")
    else f"{s}.NS"

    for s in symbols
]

print(f"\n✅ Total NSE Stocks Loaded: {len(symbols)}")

# =========================================================
# FETCH MARKET CAP
# =========================================================

def fetch_market_cap(symbol):

    try:

        ticker = yf.Ticker(symbol)

        fast_info = ticker.fast_info

        market_cap = fast_info.get(
            "market_cap",
            0
        )

        return {

            "Symbol": symbol,

            "MarketCap": market_cap

        }

    except Exception as e:

        print(f"❌ Error: {symbol} -> {e}")

        return {

            "Symbol": symbol,

            "MarketCap": 0

        }

# =========================================================
# MULTITHREADED DOWNLOAD
# =========================================================

results = []

MAX_WORKERS = 20

with ThreadPoolExecutor(
    max_workers=MAX_WORKERS
) as executor:

    future_to_symbol = {

        executor.submit(
            fetch_market_cap,
            symbol
        ): symbol

        for symbol in symbols
    }

    for idx, future in enumerate(
        as_completed(future_to_symbol),
        start=1
    ):

        result = future.result()

        results.append(result)

        print(
            f"{idx}/{len(symbols)} | "
            f"{result['Symbol']} | "
            f"Market Cap: {result['MarketCap']}"
        )

# =========================================================
# CREATE DATAFRAME
# =========================================================

market_cap_df = pd.DataFrame(results)

# =========================================================
# REMOVE DUPLICATES
# =========================================================

market_cap_df = market_cap_df.drop_duplicates(
    subset=["Symbol"]
)

# =========================================================
# SORT BY MARKET CAP
# =========================================================

market_cap_df = market_cap_df.sort_values(
    by="MarketCap",
    ascending=False
)

# =========================================================
# SAVE CSV
# =========================================================

market_cap_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    f"\n✅ market_caps.csv saved successfully "
    f"at:\n{OUTPUT_FILE}"
)

print(
    f"\n✅ Total Stocks Saved: "
    f"{len(market_cap_df)}"
)
