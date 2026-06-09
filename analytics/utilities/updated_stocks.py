import pandas as pd
import yfinance as yf
import time
import logging

from pathlib import Path

# =====================================================
# INPUT / OUTPUT
# =====================================================

ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT / "data"

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

CACHE_DIR = ROOT / "cache"

CACHE_DIR.mkdir(
    parents=True,
    exist_ok=True
)

yf.set_tz_cache_location(
    str(CACHE_DIR)
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

INPUT_FILE = (
    ROOT
    / "data"
    / "raw"
    / "valid_stocks.xlsx"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "raw"
    / "updated_stocks.xlsx"
)

SHEET_NAME = 0

# =====================================================
# LOAD
# =====================================================

print("\nLoading Excel...")

df = pd.read_excel(
    INPUT_FILE,
    sheet_name=SHEET_NAME
)

# =====================================================
# SYMBOL COLUMN
# =====================================================

SYMBOL_COL = "Stock"

if SYMBOL_COL not in df.columns:

    raise ValueError(
        f"{SYMBOL_COL} column not found"
    )

# =====================================================
# CLEAN SYMBOLS
# =====================================================

symbols = (

    df[SYMBOL_COL]

    .dropna()

    .astype(str)

    .str.strip()

    .str.upper()

)

symbols = [

    s

    if s.endswith(".NS")

    else f"{s}.NS"

    for s in symbols

]

symbols = list(
    dict.fromkeys(symbols)
)

symbols = [
    s for s in symbols
    if isinstance(s, str)
    and len(s) > 3
]

print(
    f"\nTotal Stocks: {len(symbols)}"
)

# =====================================================
# BATCH PROCESSING
# =====================================================

def download_batch(batch):

    for attempt in range(2):

        try:

            data = yf.download(
                batch,
                period="250d",
                auto_adjust=True,
                progress=False,
                threads=True,
                group_by="ticker"
            )

            if not data.empty:

                return data

        except Exception as e:

            logging.warning(
                f"Attempt {attempt + 1}/2 failed: {e}"
            )

        time.sleep(5)

    return pd.DataFrame()

updated_stocks = []

BATCH_SIZE = 200

for i in range(

    0,

    len(symbols),

    BATCH_SIZE

):

    batch = symbols[
        i:i+BATCH_SIZE
    ]

    print(

        f"\nBatch "

        f"{i+1}"

        f" - "

        f"{min(i+BATCH_SIZE,len(symbols))}"

    )

    try:

        data = download_batch(batch)

        if data.empty:

            continue

        for symbol in batch:

            try:

                if symbol not in data.columns.get_level_values(0):
                    continue

                close_series = data[symbol]["Close"].dropna()

                volume_series = data[
                    symbol
                ]["Volume"].dropna()

                high_series = data[
                    symbol
                ]["High"].dropna()

                low_series = data[
                    symbol
                ]["Low"].dropna()

                if len(close_series) < 200:

                    continue

                latest_close = float(
                    close_series.iloc[-1]
                )

                avg_volume = int(
                    volume_series.mean()
                )

                atr_pct = (

                    (
                        high_series
                        - low_series
                    )
                    /
                    close_series

                ).mean() * 100

                if latest_close < 10:

                    continue

                if avg_volume < 10000:

                    continue

                if atr_pct > 6:

                    continue

                updated_stocks.append({

                    "Symbol": symbol,

                    "Close": round(
                        latest_close,
                        2
                    ),

                    "Avg_Volume": avg_volume,

                    "ATR_PCT": round(
                        atr_pct,
                        2
                    ),

                    "History_Days": len(
                        close_series
                    )

                })

            except Exception as e:

                print(
                    f"{symbol} skipped: {e}"
                )

    except Exception as e:

        print(e)

    time.sleep(0.5)


# =====================================================
# OUTPUT
# =====================================================

if len(updated_stocks) == 0:

    raise ValueError(
        "No stocks passed validation filters."
    )

updated_df = pd.DataFrame(
    updated_stocks
)

metadata_file = (
    ROOT
    / "data"
    / "raw"
    / "stock_metadata.csv"
)

if metadata_file.exists():

    metadata = pd.read_csv(
        metadata_file
    )

    metadata["Symbol"] = (
        metadata["Symbol"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    updated_df = updated_df.merge(
        metadata[
            ["Symbol", "Market_Cap"]
        ],
        on="Symbol",
        how="left"
    )

    updated_df["Market_Cap"] = (
        updated_df["Market_Cap"]
        .fillna(0)
    )

else:

    print(
        "\nWARNING: stock_metadata.csv not found"
    )

    updated_df["Market_Cap"] = 0

updated_df = updated_df[

    updated_df["Market_Cap"]

    >=

    100_000_000

]

if updated_df.empty:

    raise ValueError(
        "No stocks survived market cap filter."
    )

updated_df = updated_df.sort_values(
    [
        "Market_Cap",
        "Avg_Volume"
    ],
    ascending=False
)

print(
    f"\nLargest Market Cap:"
)

print(
    updated_df.nlargest(
        10,
        "Market_Cap"
    )[[
        "Symbol",
        "Market_Cap"
    ]]
)

temp_file = (

    OUTPUT_FILE.parent

    / "updated_stocks_tmp.xlsx"

)

updated_df.to_excel(

    temp_file,

    index=False

)

if OUTPUT_FILE.exists():
    OUTPUT_FILE.unlink()

temp_file.rename(
    OUTPUT_FILE
)

# =====================================================
# REPORT
# =====================================================

print(
    f"\nupdated Stocks : {len(updated_df)}"
)

print(
    f"Removed Stocks : {len(symbols)-len(updated_df)}"
)

print(
    f"\nSaved:\n{OUTPUT_FILE}"
)
