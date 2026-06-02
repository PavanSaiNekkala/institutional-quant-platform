import pandas as pd
import numpy as np
from pathlib import Path

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parent.parent

RETURNS_FILE = (
    ROOT
    / "data"
    / "portfolio_returns.csv"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "performance_analytics.csv"
)

# =========================================================
# SETTINGS
# =========================================================

RISK_FREE_RATE = 0.06
TRADING_DAYS = 252

# =========================================================
# LOAD
# =========================================================

print("\n📥 Loading Returns...")

if not RETURNS_FILE.exists():

    raise FileNotFoundError(
        f"Missing: {RETURNS_FILE}"
    )

df = pd.read_csv(
    RETURNS_FILE
)

# =========================================================
# VALIDATION
# =========================================================

required = [
    "Portfolio_Return"
]

missing = [
    c for c in required
    if c not in df.columns
]

if missing:

    raise ValueError(
        f"Missing columns: {missing}"
    )

# =========================================================
# RETURNS
# =========================================================

returns = df[
    "Portfolio_Return"
].dropna()

if len(returns) < 30:

    raise ValueError(
        "Need at least 30 return observations."
    )

# =========================================================
# BASIC METRICS
# =========================================================

cumulative = (
    1 + returns
).cumprod()

total_return = (
    cumulative.iloc[-1] - 1
)

years = len(
    returns
) / TRADING_DAYS

cagr = (
    cumulative.iloc[-1]
    ** (1 / years)
) - 1

volatility = (

    returns.std()

    * np.sqrt(
        TRADING_DAYS
    )

)

sharpe = (

    cagr
    - RISK_FREE_RATE

) / volatility

# =========================================================
# SORTINO
# =========================================================

downside = returns[
    returns < 0
]

if len(downside) > 0:

    downside_vol = (

        downside.std()

        * np.sqrt(
            TRADING_DAYS
        )

    )

    sortino = (

        cagr
        - RISK_FREE_RATE

    ) / downside_vol

else:

    sortino = np.nan

# =========================================================
# DRAWDOWN
# =========================================================

rolling_max = (
    cumulative.cummax()
)

drawdown = (

    cumulative
    / rolling_max

) - 1

max_drawdown = (
    drawdown.min()
)

# =========================================================
# CALMAR
# =========================================================

if max_drawdown != 0:

    calmar = (

        cagr

        / abs(
            max_drawdown
        )

    )

else:

    calmar = np.nan

# =========================================================
# WIN RATE
# =========================================================

win_rate = (

    (returns > 0)

    .mean()

    * 100

)

# =========================================================
# BENCHMARK
# =========================================================

beta = np.nan
alpha = np.nan
information_ratio = np.nan
treynor = np.nan

if "Benchmark_Return" in df.columns:

    benchmark = df[
        "Benchmark_Return"
    ].dropna()

    common = min(
        len(returns),
        len(benchmark)
    )

    r = returns.tail(
        common
    )

    b = benchmark.tail(
        common
    )

    covariance = np.cov(
        r,
        b
    )[0, 1]

    variance = np.var(
        b
    )

    if variance != 0:

        beta = (
            covariance
            / variance
        )

    benchmark_cagr = (

        (
            1 + b
        )

        .prod()

        ** (
            TRADING_DAYS
            / len(b)
        )

    ) - 1

    alpha = (

        cagr

        - (
            RISK_FREE_RATE

            + beta

            * (
                benchmark_cagr
                - RISK_FREE_RATE
            )
        )

    )

    active_return = (
        r - b
    )

    tracking_error = (

        active_return.std()

        * np.sqrt(
            TRADING_DAYS
        )

    )

    if tracking_error != 0:

        information_ratio = (

            active_return.mean()

            * TRADING_DAYS

        ) / tracking_error

    if beta not in [

        0,
        np.nan

    ]:

        treynor = (

            cagr
            - RISK_FREE_RATE

        ) / beta

# =========================================================
# OUTPUT
# =========================================================

results = pd.DataFrame({

    "Metric": [

        "Total Return",
        "CAGR",
        "Volatility",
        "Sharpe Ratio",
        "Sortino Ratio",
        "Calmar Ratio",
        "Max Drawdown",
        "Win Rate",
        "Beta",
        "Alpha",
        "Information Ratio",
        "Treynor Ratio"

    ],

    "Value": [

        round(
            total_return,
            4
        ),

        round(
            cagr,
            4
        ),

        round(
            volatility,
            4
        ),

        round(
            sharpe,
            4
        ),

        round(
            sortino,
            4
        ),

        round(
            calmar,
            4
        ),

        round(
            max_drawdown,
            4
        ),

        round(
            win_rate,
            2
        ),

        round(
            beta,
            4
        ) if pd.notna(beta) else np.nan,

        round(
            alpha,
            4
        ) if pd.notna(alpha) else np.nan,

        round(
            information_ratio,
            4
        ) if pd.notna(information_ratio) else np.nan,

        round(
            treynor,
            4
        ) if pd.notna(treynor) else np.nan

    ]

})

# =========================================================
# SAVE
# =========================================================

results.to_csv(
    OUTPUT_FILE,
    index=False
)

# =========================================================
# REPORT
# =========================================================

print(
    "\n✅ Performance Analytics Complete"
)

print(
    f"\n📁 Saved: {OUTPUT_FILE}"
)

print(
    "\n📊 Metrics:\n"
)

print(results)
