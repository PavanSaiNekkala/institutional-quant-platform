import pandas as pd
import yfinance as yf
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# =====================================================
# INPUT / OUTPUT
# =====================================================

ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT / "data"

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

INPUT_FILE = (
    ROOT
    / "data"
    / "valid_stocks.xlsx"
)

OUTPUT_FILE = (
    ROOT
    / "data"
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

updated_stocks = []

BATCH_SIZE = 100

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

        data = yf.download(

            batch,

            period="250d",

            auto_adjust=True,

            progress=False,

            threads=True,

            group_by="ticker"

        )

        if data.empty:

            continue

        for symbol in batch:

            try:

                close_series = data[
                    symbol
                ]["Close"].dropna()

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

def get_market_cap(symbol):

    try:

        ticker = yf.Ticker(symbol)

        info = ticker.fast_info

        return (

            info.get("marketCap")

            or

            info.get("market_cap")

            or

            0

        )

    except:

        return 0
            
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

print(
    f"\nFetching Market Caps for "
    f"{len(updated_df)} stocks..."
)

with ThreadPoolExecutor(
    max_workers=10
) as executor:

    market_caps = list(

        executor.map(
            get_market_cap,
            updated_df["Symbol"]
        )

    )

updated_df["Market_Cap"] = market_caps

print(
    f"\nMarket Cap Retrieved For: "
    f"{(updated_df['Market_Cap'] > 0).sum()}"
)

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

updated_df.to_excel(

    OUTPUT_FILE,

    index=False

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