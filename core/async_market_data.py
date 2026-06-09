import concurrent.futures

import yfinance as yf

# =========================================================
# DOWNLOAD SINGLE SYMBOL
# =========================================================


def fetch_symbol_data(symbol, period="3mo"):

    try:
        data = yf.download(symbol, period=period, progress=False, auto_adjust=True, threads=False)

        if data.empty:
            return None

        return {"symbol": symbol, "data": data}

    except Exception:
        return None


# =========================================================
# CONCURRENT DOWNLOADS
# =========================================================


def fetch_market_data(symbols, max_workers=10):

    results = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_symbol_data, symbol): symbol for symbol in symbols}

        for future in concurrent.futures.as_completed(futures):
            result = future.result()

            if result:
                results[result["symbol"]] = result["data"]

    return results
