import time
from pathlib import Path

import pandas as pd
import yfinance as yf

# ============================================================
# CONFIG
# ============================================================

INPUT_FILE = "data/raw/valid_stocks.xlsx"
OUTPUT_FILE = "data/raw/symbol_metadata.csv"

DELAY_SECONDS = 1
MAX_RETRIES = 2

# ============================================================
# LOAD UNIVERSE
# ============================================================

print("\n📥 Loading Universe...")

symbols = (
    pd.read_excel(INPUT_FILE)["Stock"]
    .dropna()
    .astype(str)
    .str.upper()
    .str.strip()
    .unique()
)

print(f"Total Symbols : {len(symbols):,}")

# ============================================================
# LOAD EXISTING METADATA
# ============================================================

if Path(OUTPUT_FILE).exists():

    metadata_df = pd.read_csv(OUTPUT_FILE)

    metadata_df["symbol"] = (
        metadata_df["symbol"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

else:

    metadata_df = pd.DataFrame(
        columns=[
            "symbol",
            "company_name",
            "sector",
            "industry",
        ]
    )

# ============================================================
# IDENTIFY SYMBOLS REQUIRING UPDATE
# ============================================================

symbols_to_process = []

for symbol in symbols:

    row = metadata_df[
        metadata_df["symbol"] == symbol
    ]

    if row.empty:
        symbols_to_process.append(symbol)
        continue

    values = row.iloc[0][
        ["company_name", "sector", "industry"]
    ].astype(str)

    if any(
        str(v).strip().lower()
        in ["unknown", "nan", ""]
        for v in values
    ):
        symbols_to_process.append(symbol)

symbols_to_process = sorted(
    set(symbols_to_process)
)

print(
    f"Symbols To Fetch : "
    f"{len(symbols_to_process):,}"
)

if not symbols_to_process:

    print("\n✅ Metadata already complete.")
    raise SystemExit

# ============================================================
# FETCH FUNCTION
# ============================================================

def fetch_metadata(symbol):

    company_name = "Unknown"
    sector = "Unknown"
    industry = "Unknown"

    for _ in range(MAX_RETRIES):

        try:

            info = yf.Ticker(symbol).get_info()

            company_name = (
                info.get("longName")
                or info.get("shortName")
                or "Unknown"
            )

            sector = (
                info.get("sector")
                or "Unknown"
            )

            industry = (
                info.get("industry")
                or "Unknown"
            )

            if (
                company_name != "Unknown"
                and sector != "Unknown"
                and industry != "Unknown"
            ):
                break

        except Exception:
            pass

        time.sleep(2)

    return {
        "symbol": symbol,
        "company_name": company_name,
        "sector": sector,
        "industry": industry,
    }

# ============================================================
# UPDATE METADATA
# ============================================================

print("\n" + "=" * 60)
print("UPDATING SYMBOL METADATA")
print("=" * 60)

total = len(symbols_to_process)

for idx, symbol in enumerate(
    symbols_to_process,
    start=1,
):

    print(
        f"[{idx}/{total}] {symbol}"
    )

    row = fetch_metadata(symbol)

    metadata_df = metadata_df[
        metadata_df["symbol"] != symbol
    ]

    metadata_df = pd.concat(
        [
            metadata_df,
            pd.DataFrame([row]),
        ],
        ignore_index=True,
    )

    metadata_df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    time.sleep(DELAY_SECONDS)

# ============================================================
# FINAL CLEANUP
# ============================================================

metadata_df = (
    metadata_df
    .drop_duplicates(
        subset=["symbol"],
        keep="last",
    )
    .fillna("Unknown")
    .sort_values("symbol")
    .reset_index(drop=True)
)

metadata_df.to_csv(
    OUTPUT_FILE,
    index=False,
)

# ============================================================
# SUMMARY
# ============================================================

unknown_count = len(
    metadata_df[
        (metadata_df["company_name"] == "Unknown")
        | (metadata_df["sector"] == "Unknown")
        | (metadata_df["industry"] == "Unknown")
    ]
)

print("\n" + "=" * 60)
print("✅ COMPLETED")
print("=" * 60)

print(
    f"Total Records   : "
    f"{len(metadata_df):,}"
)

print(
    f"Unknown Records : "
    f"{unknown_count:,}"
)

print(
    f"\n💾 Saved : "
    f"{OUTPUT_FILE}"
)
