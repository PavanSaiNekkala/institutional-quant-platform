import pandas as pd
import yfinance as yf
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[1]

NSE_FILE = ROOT_DIR / "data" / "nse_universe.csv"

OUTPUT_FILE = ROOT_DIR / "data" / "market_caps.csv"

# =========================================================
# LOAD NSE STOCKS
# =========================================================

df = pd.read_csv(NSE_FILE)

symbols = df["Symbol"].dropna().unique().tolist()

# =========================================================
# DOWNLOAD MARKET CAP
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

    except Exception:

        return {

            "Symbol": symbol,

            "MarketCap": 0

        }

# =========================================================
# MULTITHREADED DOWNLOAD
# =========================================================

results = []

with ThreadPoolExecutor(max_workers=20) as executor:

    futures = executor.map(
        fetch_market_cap,
        symbols
    )

    for idx, result in enumerate(futures, start=1):

        results.append(result)

        print(
            f"{idx}/{len(symbols)} "
            f"{result['Symbol']} "
            f"{result['MarketCap']}"
        )

# =========================================================
# SAVE CSV
# =========================================================

market_cap_df = pd.DataFrame(results)

market_cap_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n✅ market_caps.csv saved successfully")
