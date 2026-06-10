from pathlib import Path

import numpy as np
import pandas as pd

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

PORTFOLIO_FILE = (
    ROOT
    / "data"
    / "portfolio"
    / "portfolio_returns.csv"
)

BENCHMARK_FILE = (
    ROOT
    / "data"
    / "market"
    / "benchmark_returns.csv"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "portfolio"
    / "performance_analytics.csv"
)

# =========================================================
# SETTINGS
# =========================================================

RISK_FREE_RATE = 0.06
TRADING_DAYS = 252

# =========================================================
# LOAD PORTFOLIO
# =========================================================

print("\n📥 Loading Portfolio Returns...")

if not PORTFOLIO_FILE.exists():
    raise FileNotFoundError(
        f"Missing file:\n{PORTFOLIO_FILE}"
    )

portfolio = pd.read_csv(PORTFOLIO_FILE)

required_cols = ["Portfolio_Return"]

missing = [
    c
    for c in required_cols
    if c not in portfolio.columns
]

if missing:
    raise ValueError(
        f"Missing columns: {missing}"
    )

portfolio["Portfolio_Return"] = pd.to_numeric(
    portfolio["Portfolio_Return"],
    errors="coerce",
)

portfolio = portfolio.dropna(
    subset=["Portfolio_Return"]
)

# =========================================================
# DATE HANDLING
# =========================================================

if "Date" in portfolio.columns:
    portfolio["Date"] = pd.to_datetime(
        portfolio["Date"]
    )

returns = portfolio["Portfolio_Return"]

if len(returns) < 30:
    raise ValueError(
        "Need at least 30 return observations."
    )

# =========================================================
# PORTFOLIO METRICS
# =========================================================

equity_curve = (
    1 + returns
).cumprod()

total_return = (
    equity_curve.iloc[-1] - 1
)

years = max(
    len(returns) / TRADING_DAYS,
    1 / TRADING_DAYS,
)

cagr = (
    equity_curve.iloc[-1]
    ** (1 / years)
) - 1

volatility = (
    returns.std()
    * np.sqrt(TRADING_DAYS)
)

sharpe = (
    (cagr - RISK_FREE_RATE)
    / volatility
    if volatility > 0
    else np.nan
)

# =========================================================
# SORTINO
# =========================================================

downside = returns[returns < 0]

if len(downside) > 0:

    downside_vol = (
        downside.std()
        * np.sqrt(TRADING_DAYS)
    )

    sortino = (
        (cagr - RISK_FREE_RATE)
        / downside_vol
        if downside_vol > 0
        else np.nan
    )

else:
    sortino = np.nan

# =========================================================
# DRAWDOWN
# =========================================================

rolling_max = equity_curve.cummax()

drawdown = (
    equity_curve
    / rolling_max
) - 1

max_drawdown = drawdown.min()

calmar = (
    cagr / abs(max_drawdown)
    if max_drawdown != 0
    else np.nan
)

# =========================================================
# WIN RATE
# =========================================================

win_rate = (
    returns > 0
).mean() * 100

# =========================================================
# BENCHMARK DEFAULTS
# =========================================================

benchmark_cagr = np.nan
benchmark_volatility = np.nan
benchmark_drawdown = np.nan

beta = np.nan
alpha = np.nan
information_ratio = np.nan
treynor = np.nan

tracking_error = np.nan
excess_return = np.nan

upside_capture = np.nan
downside_capture = np.nan

# =========================================================
# BENCHMARK ANALYTICS
# =========================================================

if BENCHMARK_FILE.exists():

    benchmark_df = pd.read_csv(
        BENCHMARK_FILE
    )

    if (
        "Date" in benchmark_df.columns
        and "Benchmark_Return" in benchmark_df.columns
        and "Date" in portfolio.columns
    ):

        benchmark_df["Date"] = pd.to_datetime(
            benchmark_df["Date"]
        )

        benchmark_df["Benchmark_Return"] = pd.to_numeric(
            benchmark_df["Benchmark_Return"],
            errors="coerce",
        )

        merged = pd.merge(
            portfolio[
                ["Date", "Portfolio_Return"]
            ],
            benchmark_df[
                ["Date", "Benchmark_Return"]
            ],
            on="Date",
            how="inner",
        )

        merged = merged.dropna()

        print(
            f"\n✅ Benchmark merged ({len(merged)} observations)"
        )

        if len(merged) >= 30:

            r = merged["Portfolio_Return"]

            b = merged["Benchmark_Return"]

            # =====================================
            # Benchmark Metrics
            # =====================================

            benchmark_curve = (
                1 + b
            ).cumprod()

            benchmark_years = max(
                len(b) / TRADING_DAYS,
                1 / TRADING_DAYS,
            )

            benchmark_cagr = (
                benchmark_curve.iloc[-1]
                ** (1 / benchmark_years)
            ) - 1

            benchmark_volatility = (
                b.std()
                * np.sqrt(TRADING_DAYS)
            )

            benchmark_dd = (
                benchmark_curve
                / benchmark_curve.cummax()
            ) - 1

            benchmark_drawdown = (
                benchmark_dd.min()
            )

            # =====================================
            # Beta
            # =====================================

            benchmark_variance = b.var()

            if benchmark_variance > 0:

                beta = (
                    r.cov(b)
                    / benchmark_variance
                )

            # =====================================
            # Alpha
            # =====================================

            if pd.notna(beta):

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

            # =====================================
            # Active Return
            # =====================================

            active_return = (
                r - b
            )

            excess_return = (
                cagr
                - benchmark_cagr
            )

            tracking_error = (
                active_return.std()
                * np.sqrt(TRADING_DAYS)
            )

            if (
                pd.notna(tracking_error)
                and tracking_error > 0
            ):

                information_ratio = (
                    active_return.mean()
                    * TRADING_DAYS
                ) / tracking_error

            # =====================================
            # Treynor
            # =====================================

            if (
                pd.notna(beta)
                and abs(beta) > 1e-9
            ):

                treynor = (
                    cagr
                    - RISK_FREE_RATE
                ) / beta

            # =====================================
            # Upside Capture
            # =====================================

            up_market = b > 0

            if up_market.sum() > 0:

                benchmark_up = (
                    b[up_market]
                    .mean()
                )

                if benchmark_up != 0:

                    upside_capture = (
                        r[up_market].mean()
                        / benchmark_up
                    ) * 100

            # =====================================
            # Downside Capture
            # =====================================

            down_market = b < 0

            if down_market.sum() > 0:

                benchmark_down = (
                    b[down_market]
                    .mean()
                )

                if benchmark_down != 0:

                    downside_capture = (
                        r[down_market].mean()
                        / benchmark_down
                    ) * 100

# =========================================================
# OUTPUT
# =========================================================

metrics = [
    ("Total Return", total_return),
    ("CAGR", cagr),
    ("Volatility", volatility),
    ("Sharpe Ratio", sharpe),
    ("Sortino Ratio", sortino),
    ("Calmar Ratio", calmar),
    ("Max Drawdown", max_drawdown),
    ("Win Rate", win_rate),

    ("Benchmark CAGR", benchmark_cagr),
    ("Benchmark Volatility", benchmark_volatility),
    ("Benchmark Drawdown", benchmark_drawdown),

    ("Excess Return", excess_return),
    ("Tracking Error", tracking_error),

    ("Beta", beta),
    ("Alpha", alpha),
    ("Information Ratio", information_ratio),
    ("Treynor Ratio", treynor),

    ("Upside Capture", upside_capture),
    ("Downside Capture", downside_capture),
]

results = pd.DataFrame(
    metrics,
    columns=[
        "Metric",
        "Value",
    ],
)

results["Value"] = (
    results["Value"]
    .astype(float)
    .round(4)
)

# =========================================================
# SAVE
# =========================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

results.to_csv(
    OUTPUT_FILE,
    index=False,
)

# =========================================================
# REPORT
# =========================================================

print("\n✅ Performance Analytics Complete")

print(f"\n📁 Saved:\n{OUTPUT_FILE}")

print("\n📊 Metrics:\n")

print(results)
