from pathlib import Path

import numpy as np
import pandas as pd

# =====================================================
# CONFIG
# =====================================================

MIN_HISTORY_DAYS = 120
MIN_PRICE = 20

MAX_ANNUAL_VOL = 0.80  # 80%

TARGET_UNIVERSE_SIZE = 1500

MIN_MARKET_CAP = 0

# =====================================================
# PATHS
# =====================================================

ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = ROOT / "data" / "raw" / "valid_stocks.xlsx"

OUTPUT_FILE = ROOT / "data" / "raw" / "updated_stocks.xlsx"

PRICE_CACHE_FILE = ROOT / "data" / "cache" / "stock_prices.parquet"

METADATA_FILE = ROOT / "data" / "raw" / "stock_metadata.csv"

# =====================================================
# LOAD STOCK LIST
# =====================================================

print("\n📥 Loading Stock Universe...")

df = pd.read_excel(INPUT_FILE)

if "Stock" not in df.columns:
    raise ValueError("Stock column not found")

symbols = (
    df["Stock"]
    .dropna()
    .astype(str)
    .str.strip()
    .str.upper()
)

symbols = [
    s if s.endswith(".NS")
    else f"{s}.NS"
    for s in symbols
]

symbols = list(dict.fromkeys(symbols))

print(f"\nTotal Symbols : {len(symbols)}")

# =====================================================
# LOAD CACHE
# =====================================================

if not PRICE_CACHE_FILE.exists():
    raise FileNotFoundError(
        f"Missing cache:\n{PRICE_CACHE_FILE}"
    )

print("\n📥 Loading Price Cache...")

close_df = pd.read_parquet(PRICE_CACHE_FILE)

# =====================================================
# MULTIINDEX FIX
# =====================================================

if isinstance(close_df.columns, pd.MultiIndex):

    print("\n⚠ MultiIndex Detected")

    if "Close" in close_df.columns.get_level_values(-1):

        close_df = close_df.xs(
            "Close",
            axis=1,
            level=-1
        )

        print("✅ Close Prices Extracted")

close_df.index = pd.to_datetime(close_df.index)

print(
    f"\nCache Shape : "
    f"{close_df.shape[0]} x {close_df.shape[1]}"
)

# =====================================================
# CACHE AGE
# =====================================================

last_date = close_df.index.max()

days_old = (
    pd.Timestamp.today().normalize()
    - last_date.normalize()
).days

print(f"\n📅 Cache Age : {days_old} days")

# =====================================================
# FILTERS
# =====================================================

history_fail = 0
price_fail = 0
vol_fail = 0
missing_fail = 0

records = []

print("\n🔍 Screening Stocks...")

for symbol in symbols:

    try:

        if symbol not in close_df.columns:

            missing_fail += 1
            continue

        series = (
            close_df[symbol]
            .dropna()
            .astype(float)
        )

        if len(series) < MIN_HISTORY_DAYS:

            history_fail += 1
            continue

        latest_close = float(series.iloc[-1])

        if latest_close < MIN_PRICE:

            price_fail += 1
            continue

        returns = series.pct_change().dropna()

        annual_vol = (
            returns.std()
            * np.sqrt(252)
        )

        if pd.isna(annual_vol):

            continue

        if annual_vol > MAX_ANNUAL_VOL:

            vol_fail += 1
            continue

        records.append(
            {
                "Symbol": symbol,
                "Close": round(latest_close, 2),
                "History_Days": len(series),
                "Annual_Volatility": round(
                    annual_vol,
                    4
                ),
            }
        )

    except Exception:
        continue

# =====================================================
# REPORT
# =====================================================

print("\n======================")
print("FILTER STATISTICS")
print("======================")

print(f"Missing      : {missing_fail}")
print(f"History Fail : {history_fail}")
print(f"Price Fail   : {price_fail}")
print(f"Vol Fail     : {vol_fail}")
print(f"Passed       : {len(records)}")

if len(records) == 0:
    raise ValueError(
        "No stocks survived filtering."
    )

updated_df = pd.DataFrame(records)

# =====================================================
# METADATA
# =====================================================

if METADATA_FILE.exists():

    metadata = pd.read_csv(METADATA_FILE)

    metadata.columns = (
        metadata.columns
        .str.strip()
    )

    metadata["Symbol"] = (
        metadata["Symbol"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    if "Market_Cap" not in metadata.columns:

        if "MarketCap" in metadata.columns:

            metadata = metadata.rename(
                columns={
                    "MarketCap":
                    "Market_Cap"
                }
            )

        elif "Market Cap" in metadata.columns:

            metadata = metadata.rename(
                columns={
                    "Market Cap":
                    "Market_Cap"
                }
            )

    updated_df = updated_df.merge(
        metadata[
            ["Symbol", "Market_Cap"]
        ],
        on="Symbol",
        how="left",
    )

else:

    print(
        "\n⚠ Metadata file missing"
    )

    updated_df["Market_Cap"] = 0

updated_df["Market_Cap"] = (
    pd.to_numeric(
        updated_df["Market_Cap"],
        errors="coerce"
    )
    .fillna(0)
)

# =====================================================
# MARKET CAP FILTER
# =====================================================

updated_df = updated_df[
    updated_df["Market_Cap"]
    >= MIN_MARKET_CAP
]

# =====================================================
# QUALITY SCORE
# =====================================================

updated_df["MCAP_SCORE"] = (
    updated_df["Market_Cap"]
    .rank(pct=True)
)

updated_df["VOL_SCORE"] = (
    1
    - updated_df[
        "Annual_Volatility"
    ].rank(pct=True)
)

updated_df["QUALITY_SCORE"] = (
    updated_df["MCAP_SCORE"] * 0.70
    + updated_df["VOL_SCORE"] * 0.30
)

# =====================================================
# FINAL RANKING
# =====================================================

updated_df = updated_df.sort_values(
    "QUALITY_SCORE",
    ascending=False
)

updated_df = updated_df.head(
    TARGET_UNIVERSE_SIZE
)

# =====================================================
# SAVE
# =====================================================

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

print("\n🏆 Top Universe")

print(
    updated_df[
        [
            "Symbol",
            "Market_Cap",
            "Annual_Volatility",
            "QUALITY_SCORE",
        ]
    ].head(20)
)

print(
    f"\nFinal Universe : "
    f"{len(updated_df)}"
)

print(
    f"\nSaved:\n"
    f"{OUTPUT_FILE}"
)
