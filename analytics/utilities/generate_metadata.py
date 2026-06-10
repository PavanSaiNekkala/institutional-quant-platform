from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import pandas as pd
import yfinance as yf

# =====================================================
# CONFIG
# =====================================================

MAX_WORKERS = 2

# =====================================================
# PATHS
# =====================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

MASTER_FILE = (
    ROOT_DIR
    / "data"
    / "master"
    / "security_master_source.csv"
)

OUTPUT_FILE = (
    ROOT_DIR
    / "data"
    / "raw"
    / "stock_metadata.csv"
)

DIAGNOSTIC_FILE = (
    ROOT_DIR
    / "data"
    / "logs"
    / "metadata_failures.csv"
)

TODAY = datetime.today().strftime("%Y-%m-%d")

# =====================================================
# LOAD MASTER
# =====================================================

print("\n📥 Loading Security Master Source...")

master = pd.read_csv(MASTER_FILE)

if "Symbol" not in master.columns:
    raise Exception(
        "Symbol column missing in security_master_source.csv"
    )

master["Symbol"] = (
    master["Symbol"]
    .astype(str)
    .str.upper()
    .str.strip()
)

symbols = (
    master["Symbol"]
    .drop_duplicates()
    .tolist()
)

print(f"Universe Size: {len(symbols):,}")

# =====================================================
# LOAD CACHE
# =====================================================

cache = {}

if OUTPUT_FILE.exists():

    old = pd.read_csv(OUTPUT_FILE)

    if (
        "Symbol" in old.columns
        and "Market_Cap" in old.columns
    ):

        old["Symbol"] = (
            old["Symbol"]
            .astype(str)
            .str.upper()
            .str.strip()
        )

        old["Market_Cap"] = pd.to_numeric(
            old["Market_Cap"],
            errors="coerce"
        ).fillna(0)

        cache = (
            old.set_index("Symbol")
            .to_dict("index")
        )

print(f"Cache Records: {len(cache):,}")

# =====================================================
# DIAGNOSTICS
# =====================================================

failures = []

cache_hits = 0
yahoo_downloads = 0

# =====================================================
# FETCH FUNCTION
# =====================================================

def get_market_cap(symbol):

    global cache_hits
    global yahoo_downloads

    # ---------------------------------------------
    # CACHE FIRST
    # ---------------------------------------------

    if symbol in cache:

        cached_cap = cache[symbol].get(
            "Market_Cap",
            0
        )

        if pd.notna(cached_cap) and cached_cap > 0:

            cache_hits += 1

            return {
                "Symbol": symbol,
                "Market_Cap": cached_cap,
                "Last_Updated": cache[symbol].get(
                    "Last_Updated",
                    TODAY
                ),
                "Source": "CACHE",
            }

    # ---------------------------------------------
    # YAHOO DOWNLOAD
    # ---------------------------------------------

    try:

        ticker = yf.Ticker(
            f"{symbol}.NS"
        )

        fast = dict(
            ticker.fast_info
        )

        market_cap = (
            fast.get("marketCap")
            or fast.get("market_cap")
            or 0
        )

        yahoo_downloads += 1

        return {
            "Symbol": symbol,
            "Market_Cap": market_cap,
            "Last_Updated": TODAY,
            "Source": "YAHOO",
        }

    except Exception as e:

        error_msg = str(e)

        reason = "DOWNLOAD_FAILED"

        if (
            "rate" in error_msg.lower()
            or "too many requests"
            in error_msg.lower()
        ):
            reason = "RATE_LIMIT"

        failures.append(
            {
                "Symbol": symbol,
                "Reason": reason,
                "Error": error_msg,
                "Timestamp": TODAY,
            }
        )

        # fallback to cache if available

        if symbol in cache:

            return {
                "Symbol": symbol,
                "Market_Cap": cache[symbol].get(
                    "Market_Cap",
                    0
                ),
                "Last_Updated": cache[symbol].get(
                    "Last_Updated",
                    TODAY
                ),
                "Source": "CACHE_FALLBACK",
            }

        return {
            "Symbol": symbol,
            "Market_Cap": 0,
            "Last_Updated": TODAY,
            "Source": reason,
        }

# =====================================================
# RUN
# =====================================================

print("\n🚀 Generating Metadata...")

results = []

with ThreadPoolExecutor(
    max_workers=MAX_WORKERS
) as executor:

    futures = {
        executor.submit(
            get_market_cap,
            symbol
        ): symbol
        for symbol in symbols
    }

    total = len(futures)

    for idx, future in enumerate(
        as_completed(futures),
        start=1,
    ):

        results.append(
            future.result()
        )

        if idx % 50 == 0:

            print(
                f"{idx:,}/{total:,}"
            )

# =====================================================
# BUILD OUTPUT
# =====================================================

metadata = pd.DataFrame(results)

metadata["Market_Cap"] = pd.to_numeric(
    metadata["Market_Cap"],
    errors="coerce"
).fillna(0)

metadata = (
    metadata
    .drop_duplicates("Symbol")
    .sort_values(
        "Market_Cap",
        ascending=False
    )
    .reset_index(drop=True)
)

# =====================================================
# SAVE
# =====================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

metadata.to_csv(
    OUTPUT_FILE,
    index=False
)

# =====================================================
# SAVE FAILURES
# =====================================================

if failures:

    DIAGNOSTIC_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    pd.DataFrame(
        failures
    ).to_csv(
        DIAGNOSTIC_FILE,
        index=False,
    )

# =====================================================
# SUMMARY
# =====================================================

missing = (
    metadata["Market_Cap"] == 0
).sum()

print("\n" + "=" * 70)

print("🏁 METADATA GENERATION COMPLETE")

print("=" * 70)

print(
    f"Stocks            : {len(metadata):,}"
)

print(
    f"Cache Hits        : {cache_hits:,}"
)

print(
    f"Yahoo Downloads   : {yahoo_downloads:,}"
)

print(
    f"Failures          : {len(failures):,}"
)

print(
    f"Missing MarketCap : {missing:,}"
)

if failures:

    rate_limits = sum(
        1
        for x in failures
        if x["Reason"] == "RATE_LIMIT"
    )

    print(
        f"Rate Limited      : {rate_limits:,}"
    )

    print(
        f"\nFailure Report:\n"
        f"{DIAGNOSTIC_FILE}"
    )

print(
    f"\nSaved:\n"
    f"{OUTPUT_FILE}"
)

print("=" * 70)
