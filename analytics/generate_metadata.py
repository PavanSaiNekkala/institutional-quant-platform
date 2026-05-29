import pandas as pd
import yfinance as yf
import time

from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed
)

# =====================================================
# CONFIG
# =====================================================

INPUT_FILE = "data/valid_stocks.xlsx"
OUTPUT_FILE = "data/stock_metadata.csv"

MAX_WORKERS = 3
BATCH_SIZE = 20
BATCH_DELAY = 10

# =====================================================
# LOAD STOCKS
# =====================================================

print("\n📥 Loading stocks...")

df = pd.read_excel(INPUT_FILE)

if "Symbol" in df.columns:

    symbol_col = "Symbol"

elif "Stock" in df.columns:

    symbol_col = "Stock"

else:

    raise ValueError(
        f"❌ Expected Symbol or Stock column. Found: {list(df.columns)}"
    )

symbols = (
    df[symbol_col]
    .dropna()
    .astype(str)
    .str.strip()
    .unique()
    .tolist()
)

symbols = [

    s if s.endswith(".NS")

    else f"{s}.NS"

    for s in symbols
]

TOTAL = len(symbols)

print(f"✅ Column Used : {symbol_col}")
print(f"✅ Total Stocks: {TOTAL}")

# =====================================================
# FETCH FUNCTION
# =====================================================

def fetch_metadata(symbol):

    try:

        ticker = yf.Ticker(symbol)

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
            )
        }

    except Exception:

        return {

            "Symbol": symbol,

            "Sector": "Unknown",

            "Industry": "Unknown",

            "MarketCap": 0
        }

# =====================================================
# PROCESS IN BATCHES
# =====================================================

results = []

completed = 0

print("\n" + "=" * 70)
print("🚀 GENERATING STOCK METADATA")
print("=" * 70)

for batch_start in range(
    0,
    TOTAL,
    BATCH_SIZE
):

    batch = symbols[
        batch_start:
        batch_start + BATCH_SIZE
    ]

    batch_no = (
        batch_start // BATCH_SIZE
    ) + 1

    print(
        f"\n📦 Batch {batch_no}"
        f" | {len(batch)} Stocks"
    )

    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        futures = {

            executor.submit(
                fetch_metadata,
                symbol
            ): symbol

            for symbol in batch
        }

        for future in as_completed(
            futures
        ):

            row = future.result()

            results.append(row)

            completed += 1

            print(

                f"[{completed}/{TOTAL}] "

                f"{row['Symbol']} "

                f"| "

                f"{row['Sector']} "

                f"| "

                f"{row['Industry']}"
            )

    # ==========================================
    # AUTOSAVE
    # ==========================================

    pd.DataFrame(
        results
    ).to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"\n💾 Autosaved "
        f"{completed} records"
    )

    # ==========================================
    # COOL DOWN
    # ==========================================

    if batch_start + BATCH_SIZE < TOTAL:

        print(
            f"\n⏳ Cooling down "
            f"{BATCH_DELAY}s..."
        )

        time.sleep(
            BATCH_DELAY
        )

# =====================================================
# FINAL SAVE
# =====================================================

metadata = pd.DataFrame(results)

metadata.to_csv(
    OUTPUT_FILE,
    index=False
)

# =====================================================
# SUMMARY
# =====================================================

success = len(

    metadata[
        metadata["Sector"]
        != "Unknown"
    ]
)

failed = len(

    metadata[
        metadata["Sector"]
        == "Unknown"
    ]
)

print("\n" + "=" * 70)

print("🏁 METADATA GENERATION COMPLETE")

print("=" * 70)

print(f"📊 Total Stocks : {TOTAL}")
print(f"✅ Success      : {success}")
print(f"❌ Unknown      : {failed}")

if TOTAL > 0:

    print(
        f"📈 Success Rate : "
        f"{round(success/TOTAL*100,2)}%"
    )

print(
    f"\n💾 Saved: "
    f"{OUTPUT_FILE}"
)

print("=" * 70)