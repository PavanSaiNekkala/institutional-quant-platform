import pandas as pd
import numpy as np
import yfinance as yf

from pathlib import Path

# =========================================================
# CONFIG
# =========================================================

LOOKBACK_PERIOD = "3y"

TRAIN_WINDOW = 126

TEST_WINDOW = 21

TOP_N = 15

INITIAL_CAPITAL = 100000

TRADING_DAYS = 252

BENCHMARK = "^NSEI"

MIN_STOCKS_REQUIRED = 5

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    ROOT_DIR
    / "data"
    / "cross_sectional_rankings.csv"
)

OUTPUT_FILE = (
    ROOT_DIR
    / "data"
    / "walk_forward_results.csv"
)

EQUITY_CURVE_FILE = (
    ROOT_DIR
    / "data"
    / "walk_forward_equity_curve.csv"
)

# =========================================================
# LOAD RANKINGS
# =========================================================

print("\n📥 Loading Ranking Data...")

rank_df = pd.read_csv(INPUT_FILE)

print("✅ Ranking Data Loaded")

# =========================================================
# VALIDATE COLUMNS
# =========================================================

required_columns = [
    "Symbol"
]

for col in required_columns:

    if col not in rank_df.columns:

        raise Exception(
            f"\n❌ Missing Required Column: {col}"
        )

# =========================================================
# CLEAN SYMBOLS
# =========================================================

symbols = (

    rank_df["Symbol"]

    .astype(str)

    .str.replace(".NS", "", regex=False)

    .str.strip()

    .unique()

    .tolist()
)

symbols = [

    s for s in symbols

    if s not in ["", "nan", "None"]
]

tickers = [

    f"{symbol}.NS"

    for symbol in symbols
]

tickers.append(BENCHMARK)

# =========================================================
# DOWNLOAD PRICE DATA
# =========================================================

print("\n📥 Downloading Historical Prices...")

prices = yf.download(

    tickers=tickers,

    period=LOOKBACK_PERIOD,

    auto_adjust=True,

    progress=False,

    threads=True
)

# =========================================================
# FIX MULTIINDEX
# =========================================================

if isinstance(
    prices.columns,
    pd.MultiIndex
):

    prices = prices["Close"]

# =========================================================
# CLEAN DATA
# =========================================================

prices = prices.dropna(
    axis=1,
    how="all"
)

prices = prices.ffill()

prices = prices.dropna(
    how="all"
)

# =========================================================
# ENSURE BENCHMARK EXISTS
# =========================================================

if BENCHMARK not in prices.columns:

    raise Exception(
        "\n❌ Benchmark Data Missing"
    )

# =========================================================
# RETURNS
# =========================================================

returns = (

    prices

    .pct_change()

    .replace([np.inf, -np.inf], np.nan)

    .dropna(how="all")
)

returns = returns.dropna(
    axis=1,
    how="all"
)

benchmark_returns = returns[BENCHMARK]

# =========================================================
# WALK FORWARD
# =========================================================

portfolio_values = []

dates = []

capital = INITIAL_CAPITAL

print("\n🧠 Running Walk Forward Optimization...")

for start in range(

    TRAIN_WINDOW,

    len(returns) - TEST_WINDOW,

    TEST_WINDOW
):

    train_data = returns.iloc[
        start - TRAIN_WINDOW : start
    ]

    test_data = returns.iloc[
        start : start + TEST_WINDOW
    ]

    # =====================================================
    # VALIDATION
    # =====================================================

    if train_data.empty:

        continue

    if test_data.empty:

        continue

    # =====================================================
    # RELATIVE STRENGTH ENGINE
    # =====================================================

    rs_scores = {}

    for col in train_data.columns:

        if col == BENCHMARK:

            continue

        series = train_data[col].dropna()

        if len(series) < 30:

            continue

        volatility = series.std()

        if (
            pd.isna(volatility)
            or volatility == 0
        ):

            continue

        cumulative_return = (

            (
                1 + series
            )

            .prod()

            - 1
        )

        rs_score = (
            cumulative_return
            /
            volatility
        )

        if np.isfinite(rs_score):

            rs_scores[col] = rs_score

    # =====================================================
    # VALIDATE SCORES
    # =====================================================

    if len(rs_scores) < MIN_STOCKS_REQUIRED:

        continue

    # =====================================================
    # RANK STOCKS
    # =====================================================

    ranked = sorted(

        rs_scores.items(),

        key=lambda x: x[1],

        reverse=True
    )

    top_stocks = [

        x[0]

        for x in ranked[:TOP_N]
    ]

    if len(top_stocks) == 0:

        continue

    # =====================================================
    # EQUAL WEIGHT PORTFOLIO
    # =====================================================

    weight = 1 / len(top_stocks)

    portfolio_returns = pd.Series(

        0.0,

        index=test_data.index
    )

    valid_stock_count = 0

    for stock in top_stocks:

        if stock not in test_data.columns:

            continue

        stock_returns = (

            test_data[stock]

            .replace(
                [np.inf, -np.inf],
                np.nan
            )

            .fillna(0)
        )

        portfolio_returns += (
            stock_returns
            * weight
        )

        valid_stock_count += 1

    # =====================================================
    # VALIDATE PORTFOLIO
    # =====================================================

    if valid_stock_count == 0:

        continue

    if portfolio_returns.empty:

        continue

    # =====================================================
    # UPDATE CAPITAL
    # =====================================================

    cumulative_test_return = (

        (
            1 + portfolio_returns
        )

        .prod()

        - 1
    )

    if not np.isfinite(cumulative_test_return):

        continue

    capital *= (
        1 + cumulative_test_return
    )

    portfolio_values.append(
        capital
    )

    dates.append(
        test_data.index[-1]
    )

# =========================================================
# EQUITY CURVE
# =========================================================

equity_curve = pd.DataFrame({

    "Date": dates,

    "Portfolio_Value": portfolio_values
})

# =========================================================
# VALIDATION
# =========================================================

if equity_curve.empty:

    raise Exception(
        "\n❌ Equity Curve Empty\n"
        "No valid walk-forward windows generated.\n"
        "Possible reasons:\n"
        "- insufficient data\n"
        "- invalid symbols\n"
        "- benchmark mismatch\n"
        "- no valid portfolio periods"
    )

# =========================================================
# RETURNS
# =========================================================

equity_curve["Returns"] = (

    equity_curve["Portfolio_Value"]

    .pct_change()

    .fillna(0)
)

# =========================================================
# PERFORMANCE METRICS
# =========================================================

final_value = (
    equity_curve["Portfolio_Value"]
    .iloc[-1]
)

total_return = (
    final_value
    / INITIAL_CAPITAL
    - 1
)

years = max(

    (
        len(equity_curve)
        * TEST_WINDOW
        / TRADING_DAYS
    ),

    0.1
)

cagr = (

    (
        1 + total_return
    )

    ** (1 / years)

    - 1
)

volatility = (

    equity_curve["Returns"]

    .std()

    * np.sqrt(TRADING_DAYS)
)

if volatility == 0:

    sharpe = 0

else:

    sharpe = (
        cagr
        /
        volatility
    )

rolling_max = (

    equity_curve["Portfolio_Value"]

    .cummax()
)

drawdown = (

    equity_curve["Portfolio_Value"]

    / rolling_max

    - 1
)

max_drawdown = drawdown.min()

win_rate = (

    (
        equity_curve["Returns"] > 0
    )

    .mean()

    * 100
)

# =========================================================
# BENCHMARK METRICS
# =========================================================

benchmark_curve = (

    (
        1 + benchmark_returns
    )

    .cumprod()
)

benchmark_total_return = (

    benchmark_curve.iloc[-1]

    - 1
)

benchmark_cagr = (

    (
        1 + benchmark_total_return
    )

    ** (1 / years)

    - 1
)

alpha = (
    cagr
    -
    benchmark_cagr
)

# =========================================================
# RESULTS
# =========================================================

results = pd.DataFrame({

    "TOTAL_RETURN": [

        round(
            total_return * 100,
            2
        )
    ],

    "CAGR": [

        round(
            cagr * 100,
            2
        )
    ],

    "VOLATILITY": [

        round(
            volatility * 100,
            2
        )
    ],

    "SHARPE_RATIO": [

        round(
            sharpe,
            2
        )
    ],

    "MAX_DRAWDOWN": [

        round(
            max_drawdown * 100,
            2
        )
    ],

    "WIN_RATE": [

        round(
            win_rate,
            2
        )
    ],

    "BENCHMARK_CAGR": [

        round(
            benchmark_cagr * 100,
            2
        )
    ],

    "ALPHA": [

        round(
            alpha * 100,
            2
        )
    ]
})

# =========================================================
# SAVE
# =========================================================

results.to_csv(

    OUTPUT_FILE,

    index=False
)

equity_curve.to_csv(

    EQUITY_CURVE_FILE,

    index=False
)

# =========================================================
# OUTPUT
# =========================================================

print("\n✅ Walk Forward Optimization Completed")

print(
    f"\n📁 Results Saved:\n"
    f"{OUTPUT_FILE}"
)

print(
    f"\n📈 Equity Curve Saved:\n"
    f"{EQUITY_CURVE_FILE}"
)

print("\n🏆 WALK FORWARD RESULTS:\n")

print(results.T)