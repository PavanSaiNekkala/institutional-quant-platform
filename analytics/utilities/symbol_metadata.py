import time

import pandas as pd
import yfinance as yf

# ============================================================
# CONFIG
# ============================================================

INPUT_FILE = "data/raw/valid_stocks.xlsx"
OUTPUT_FILE = "data/raw/symbol_metadata.csv"

DELAY_SECONDS = 2

# ============================================================
# LOAD SYMBOLS
# ============================================================

print("\nLoading Universe...")

source_df = pd.read_excel(INPUT_FILE)

symbols = (
    source_df["Stock"]
    .dropna()
    .astype(str)
    .str.strip()
    .unique()
)

TOTAL = len(symbols)

print(f"Total Symbols : {TOTAL}")

# ============================================================
# START FRESH
# ============================================================

results = []

print("\n" + "=" * 60)
print("GENERATING SYMBOL METADATA FROM SCRATCH")
print("=" * 60)

# ============================================================
# FETCH
# ============================================================

for idx, symbol in enumerate(symbols, start=1):

    try:

        print(
            f"[{idx}/{TOTAL}] "
            f"FETCHING -> {symbol}"
        )

        ticker = yf.Ticker(symbol)

        info = ticker.info

        row = {
            "symbol": symbol,
            "company_name": (
                info.get("longName")
                or info.get("shortName")
                or "Unknown"
            ),
            "sector": (
                info.get("sector")
                or "Unknown"
            ),
            "industry": (
                info.get("industry")
                or "Unknown"
            ),
        }

    except Exception as e:

        print(
            f"ERROR -> {symbol} -> {e}"
        )

        row = {
            "symbol": symbol,
            "company_name": "Unknown",
            "sector": "Unknown",
            "industry": "Unknown",
        }

    results.append(row)

    # Autosave every stock

    pd.DataFrame(results).to_csv(
        OUTPUT_FILE,
        index=False
    )

    time.sleep(DELAY_SECONDS)


# ============================================================
# FINAL SAVE
# ============================================================

metadata_df = pd.DataFrame(results)

metadata_df = (
    metadata_df
    .drop_duplicates(
        subset=["symbol"]
    )
    .reset_index(drop=True)
)

metadata_df.to_csv(
    OUTPUT_FILE,
    index=False
)

# ============================================================
# SUMMARY
# ============================================================

success = len(
    metadata_df[
        metadata_df["company_name"].notna()
    ]
)

failed = len(metadata_df) - success

print("\n" + "=" * 60)
print("COMPLETED")
print("=" * 60)

print(f"Total Symbols : {TOTAL}")
print(f"Success       : {success}")
print(f"Failed        : {failed}")

print(
    f"\nSaved : "
    f"{OUTPUT_FILE}"
)
