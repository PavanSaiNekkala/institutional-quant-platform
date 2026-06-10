from pathlib import Path

import pandas as pd
import yfinance as yf

# =========================================================
# CONFIG
# =========================================================

BENCHMARK = "^NSEI"
PERIOD = "2y"

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

OUTPUT_FILE = (
    ROOT_DIR
    / "data"
    / "raw"
    / "benchmark.csv"
)

# =========================================================
# DOWNLOAD
# =========================================================

print("\n📥 Updating Benchmark...")

try:

    df = yf.download(
        BENCHMARK,
        period=PERIOD,
        auto_adjust=True,
        progress=False,
        threads=False,
    )

    if df.empty:
        raise Exception("Empty dataframe returned")

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.reset_index()

    df["Date"] = pd.to_datetime(df["Date"])

    df = df[
        [
            "Date",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
        ]
    ]

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("\n✅ Benchmark Downloaded")

    print(
        f"Rows: {len(df):,}"
    )

    print(
        f"Latest Close: "
        f"{df['Close'].iloc[-1]:,.2f}"
    )

except Exception as e:

    print("\n⚠ Yahoo Download Failed")
    print(f"Reason: {e}")

    if OUTPUT_FILE.exists():

        cached = pd.read_csv(OUTPUT_FILE)

        print("\n✅ Using Cached Benchmark")
        print(f"Rows: {len(cached):,}")
        print(
            f"Latest Close: "
            f"{cached['Close'].iloc[-1]:,.2f}"
        )

    else:

        raise RuntimeError(
            "\n❌ No benchmark available.\n"
            "Yahoo failed and benchmark.csv "
            "does not exist."
        ) from e

print(
    f"\nSaved:\n{OUTPUT_FILE}"
)
