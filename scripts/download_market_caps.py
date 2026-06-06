import pandas as pd
import yfinance as yf
import time

from pathlib import Path

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[1]

NSE_FILE = ROOT_DIR / "data" / "updated_stocks.xlsx"

OUTPUT_FILE = ROOT_DIR / "data" / "market_caps.csv"

# =========================================================
# LOAD STOCKS
# =========================================================

df = pd.read_excel(NSE_FILE)

possible_cols = [
    "Stock",
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
    .str.strip()
    .unique()
    .tolist()
)

# =========================================================
# FORMAT NSE SYMBOLS
# =========================================================

symbols = [

    s.replace(".NS", "") + ".NS"

    for s in symbols
]

print(f"\n✅ Loaded Stocks: {len(symbols)}")

# =========================================================
# FETCH MARKET CAPS
# =========================================================

results = []

BATCH_SIZE = 50

for start in range(0, len(symbols), BATCH_SIZE):

    batch = symbols[start:start + BATCH_SIZE]

    print(
        f"\n🚀 Processing Batch "
        f"{start + 1} to "
        f"{start + len(batch)}"
    )

    try:

        tickers = yf.Tickers(
            " ".join(batch)
        )

        for symbol in batch:

            try:

                ticker = tickers.tickers[symbol]

                market_cap = 0

                # =========================================
                # FAST INFO
                # =========================================

                try:

                    market_cap = (
                        ticker.fast_info.get(
                            "market_cap",
                            0
                        )
                    )

                except Exception:

                    pass

                # =========================================
                # FALLBACK
                # =========================================

                if not market_cap:

                    try:

                        market_cap = (
                            ticker.info.get(
                                "marketCap",
                                0
                            )
                        )

                    except Exception:

                        pass

                print(
                    f"✅ {symbol} | "
                    f"{market_cap}"
                )

                results.append({

                    "Symbol": symbol.replace(
                        ".NS",
                        ""
                    ),

                    "MarketCap": market_cap

                })

            except Exception as e:

                print(
                    f"❌ {symbol} | ERROR"
                )

                results.append({

                    "Symbol": symbol.replace(
                        ".NS",
                        ""
                    ),

                    "MarketCap": 0

                })

        # =============================================
        # SAVE AFTER EACH BATCH
        # =============================================

        temp_df = pd.DataFrame(results)

        temp_df.to_csv(
            OUTPUT_FILE,
            index=False
        )

        print(
            f"💾 Auto Saved"
        )

        # =============================================
        # SMALL COOL DOWN
        # =============================================

        time.sleep(2)

    except Exception as e:

        print(
            f"❌ Batch Failed: {e}"
        )

# =========================================================
# FINAL DATAFRAME
# =========================================================

market_cap_df = pd.DataFrame(results)

market_cap_df = market_cap_df.drop_duplicates(
    subset=["Symbol"]
)

market_cap_df = market_cap_df.sort_values(
    by="MarketCap",
    ascending=False
)

# =========================================================
# SAVE FINAL CSV
# =========================================================

market_cap_df.to_csv(
    OUTPUT_FILE,
    index=False
)

# =========================================================
# SUMMARY
# =========================================================

success = len(
    market_cap_df[
        market_cap_df["MarketCap"] > 0
    ]
)

failed = len(
    market_cap_df[
        market_cap_df["MarketCap"] <= 0
    ]
)

print("\n================================")

print("✅ market_caps.csv saved")

print(f"✅ Success: {success}")

print(f"❌ Failed: {failed}")

print(
    f"📁 File: {OUTPUT_FILE}"
)

print("================================\n")
