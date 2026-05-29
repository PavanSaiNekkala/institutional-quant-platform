import pandas as pd
import numpy as np
import yfinance as yf

from pathlib import Path

from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed
)

# =========================================================
# CONFIG
# =========================================================

BENCHMARK = "^NSEI"

DOWNLOAD_PERIOD = "6mo"

MAX_WORKERS = 5

MIN_HISTORY = 70

# =========================================================
# RS WINDOWS
# =========================================================

RS_WINDOWS = {

    "RS_5D": 5,

    "RS_15D": 15,

    "RS_30D": 30,

    "RS_60D": 60
}

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT_DIR / "data"

INPUT_FILE = (
    DATA_DIR
    / "valid_stocks.xlsx"
)

# =========================================================
# IMPORTANT FIX
# =========================================================
# PIPELINE EXPECTS:
# institutional_rankings.csv
# =========================================================

OUTPUT_FILE = (
    DATA_DIR
    / "institutional_rankings.csv"
)

# =========================================================
# CREATE DATA DIRECTORY
# =========================================================

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# =========================================================
# LOAD STOCKS
# =========================================================

print("\n📥 Loading Stock Universe...")

if not INPUT_FILE.exists():

    raise FileNotFoundError(

        f"\n❌ Missing file:\n"
        f"{INPUT_FILE}"
    )

df = pd.read_excel(INPUT_FILE)

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

        f"\n❌ Symbol column not found.\n"

        f"Available columns:\n"

        f"{df.columns.tolist()}"
    )

symbols = (

    df[symbol_col]

    .dropna()

    .astype(str)

    .str.upper()

    .str.strip()

    .str.replace(".NS", "", regex=False)

    .unique()

    .tolist()
)

print(f"\n✅ Loaded {len(symbols)} symbols")

# =========================================================
# DOWNLOAD BENCHMARK
# =========================================================

print("\n📥 Downloading Benchmark...")

benchmark_df = yf.download(

    BENCHMARK,

    period=DOWNLOAD_PERIOD,

    auto_adjust=True,

    progress=False,

    threads=False
)

# =========================================================
# EMPTY CHECK
# =========================================================

if benchmark_df.empty:

    raise Exception(

        "\n❌ Failed to download benchmark data"
    )

# =========================================================
# FIX MULTIINDEX
# =========================================================

if isinstance(
    benchmark_df.columns,
    pd.MultiIndex
):

    benchmark_df.columns = (

        benchmark_df.columns
        .get_level_values(0)
    )

# =========================================================
# CLOSE SERIES
# =========================================================

if "Close" not in benchmark_df.columns:

    raise Exception(
        "\n❌ Benchmark Close column missing"
    )

benchmark_close = benchmark_df["Close"]

if isinstance(benchmark_close, pd.DataFrame):

    benchmark_close = benchmark_close.iloc[:, 0]

benchmark_close = benchmark_close.dropna()

# =========================================================
# BENCHMARK RETURNS
# =========================================================

benchmark_returns = (

    benchmark_close

    .pct_change()

    .dropna()
)

print("\n✅ Benchmark Ready")

# =========================================================
# RS CALCULATION
# =========================================================

def calculate_rs(symbol):

    try:

        # =================================================
        # SYMBOL NORMALIZATION
        # =================================================

        symbol = str(symbol).upper().strip()

        if not symbol.endswith(".NS"):

            symbol = f"{symbol}.NS"

        # =================================================
        # DOWNLOAD STOCK DATA
        # =================================================

        data = yf.download(

            symbol,

            period=DOWNLOAD_PERIOD,

            auto_adjust=True,

            progress=False,

            threads=False
        )

        # =================================================
        # EMPTY CHECK
        # =================================================

        if data.empty:

            print(f"❌ {symbol} -> Empty Data")

            return None

        # =================================================
        # FIX MULTIINDEX
        # =================================================

        if isinstance(
            data.columns,
            pd.MultiIndex
        ):

            data.columns = (

                data.columns
                .get_level_values(0)
            )

        # =================================================
        # CLOSE CHECK
        # =================================================

        if "Close" not in data.columns:

            print(f"❌ {symbol} -> No Close Column")

            return None

        close = data["Close"]

        if isinstance(close, pd.DataFrame):

            close = close.iloc[:, 0]

        close = close.dropna()

        # =================================================
        # HISTORY CHECK
        # =================================================

        if len(close) < MIN_HISTORY:

            print(

                f"❌ {symbol} -> "
                f"Insufficient History"
            )

            return None

        # =================================================
        # STOCK RETURNS
        # =================================================

        stock_returns = (

            close

            .pct_change()

            .dropna()
        )

        # =================================================
        # ALIGN RETURNS
        # =================================================

        combined = pd.concat(

            [
                stock_returns,
                benchmark_returns
            ],

            axis=1,

            join="inner"
        )
      
        combined.columns = [

            "STOCK",

            "BENCHMARK"
        ]

        combined = combined.dropna()

        # =================================================
        # ALIGNMENT CHECK
        # =================================================

        if len(combined) < MIN_HISTORY:

            print(

                f"❌ {symbol} -> "
                f"Alignment Failed"
            )

            return None

        # =================================================
        # RS CALCULATION
        # =================================================

        rs_data = {}

        for label, window in RS_WINDOWS.items():

            if len(combined) < window:

                rs_data[label] = None

                continue

            stock_perf = (

                (
                    1 + combined["STOCK"]
                )

                .tail(window)

                .prod()
            )

            benchmark_perf = (

                (
                    1 + combined["BENCHMARK"]
                )

                .tail(window)

                .prod()
            )

            rs_score = (

                (
                    stock_perf
                    /
                    benchmark_perf
                )

                - 1
            )

            rs_data[label] = round(

                rs_score * 100,

                2
            )

        # =================================================
        # RS ACCELERATION
        # =================================================

        try:

            rs_acceleration = round(

                rs_data["RS_5D"]

                -

                rs_data["RS_30D"],

                2
            )

        except:

            rs_acceleration = None

        # =================================================
        # VOLATILITY
        # =================================================

        volatility = round(

            combined["STOCK"]

            .std()

            * np.sqrt(252),

            4
        )

        # =================================================
        # VOL ADJUSTED RS
        # =================================================

        if (
            volatility is None
            or pd.isna(volatility)
            or volatility <= 0
        ):

            vol_adj_rs = 0

        else:

            vol_adj_rs = round(
                rs_data["RS_30D"] / volatility,
                2
            )
        # =================================================
        # RETURN OUTPUT
        # =================================================

        return {

            "Symbol": symbol,

            "RS_5D":
                rs_data.get("RS_5D"),

            "RS_15D":
                rs_data.get("RS_15D"),

            "RS_30D":
                rs_data.get("RS_30D"),

            "RS_60D":
                rs_data.get("RS_60D"),

            "RS_ACCELERATION":
                rs_acceleration,

            "VOLATILITY":
                volatility,

            "VOL_ADJ_RS":
                vol_adj_rs
        }

    except Exception as e:

        print(f"❌ {symbol} -> {e}")

        return None

# =========================================================
# MULTITHREAD EXECUTION
# =========================================================

print("\n🚀 Calculating Relative Strength...")

results = []

with ThreadPoolExecutor(
    max_workers=MAX_WORKERS
) as executor:

    futures = {

        executor.submit(
            calculate_rs,
            symbol
        ): symbol

        for symbol in symbols
    }

    total = len(futures)

    for idx, future in enumerate(

        as_completed(futures),

        start=1
    ):

        result = future.result()

        if result is not None:

            results.append(result)

            print(

                f"{idx}/{total} | "

                f"{result['Symbol']} | "

                f"RS_30D: "

                f"{result['RS_30D']}"
            )

# =========================================================
# DATAFRAME
# =========================================================

rs_df = pd.DataFrame(results)

print(
    "\n📊 Infinite VOL_ADJ_RS values:",
    np.isinf(rs_df["VOL_ADJ_RS"]).sum()
)

numeric_cols = [

    "RS_5D",
    "RS_15D",
    "RS_30D",
    "RS_60D",
    "RS_ACCELERATION",
    "VOLATILITY",
    "VOL_ADJ_RS"
]

for col in numeric_cols:

    if col in rs_df.columns:

        rs_df[col] = pd.to_numeric(
            rs_df[col],
            errors="coerce"
        )

        rs_df[col] = rs_df[col].replace(
            [np.inf, -np.inf],
            np.nan
        )

        rs_df[col] = rs_df[col].fillna(0)

# =========================================================
# EMPTY CHECK
# =========================================================

if rs_df.empty:

    raise Exception(
        "\n❌ No valid stocks processed"
    )

# =========================================================
# REMOVE DUPLICATES
# =========================================================

rs_df = rs_df.drop_duplicates(
    subset=["Symbol"]
)

# =========================================================
# INSTITUTIONAL SCORE
# =========================================================

rs_df["Institutional Score"] = (

    (
        rs_df["RS_30D"].rank(
            pct=True
        ) * 40
    )

    +

    (
        rs_df["RS_60D"].rank(
            pct=True
        ) * 30
    )

    +

    (
        rs_df["RS_ACCELERATION"].rank(
            pct=True
        ) * 20
    )

    +

    (
        rs_df["VOL_ADJ_RS"].rank(
            pct=True
        ) * 10
    )
)

rs_df["Institutional Score"] = (

    rs_df["Institutional Score"]

    .round(2)
)

rs_df["Institutional Score"] = (
    rs_df["Institutional Score"]
    .fillna(0)
    .round(2)
)

# =========================================================
# SORT
# =========================================================

rs_df = rs_df.sort_values(

    by=[
        "Institutional Score"
    ],

    ascending=False
)

# =========================================================
# SAVE OUTPUT
# =========================================================

rs_df.to_csv(

    OUTPUT_FILE,

    index=False
)

# =========================================================
# VALIDATION
# =========================================================

if not OUTPUT_FILE.exists():

    raise Exception(

        "\n❌ Output validation failed"
    )

# =========================================================
# OUTPUT
# =========================================================

print("\n✅ Relative Strength Generated")

print(

    f"\n📁 Saved to:\n"

    f"{OUTPUT_FILE}"
)

print("\n🏆 Top Institutional RS Stocks:\n")

print(

    rs_df.head(10)
)
