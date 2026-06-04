import plotly.graph_objects as go
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from analytics.downloader import (
    load_symbols,
    prefilter_symbols,
    batch_download
)

from backtest.engine import (
    run_backtest,
    simulate_portfolio
)

# =====================================================
# LOAD UNIVERSE
# =====================================================

symbols = load_symbols()

symbols = prefilter_symbols(symbols)

symbols = symbols[:50]

print("DOWNLOADING DATA...")

# =====================================================
# DOWNLOAD DATA
# =====================================================

stock_data = batch_download(symbols)

print("RUNNING BACKTEST ENGINE...")

# =====================================================
# RUN ENGINE
# =====================================================

scores_df, top_stocks = run_backtest(stock_data)

print("\nTOP STOCKS")

print(scores_df.head(10))

print("\nSELECTED PORTFOLIO")

print(top_stocks)

# =====================================================
# PORTFOLIO SIMULATION
# =====================================================

print("\nSIMULATING PORTFOLIO...")

portfolio_returns, equity_curve, benchmark_equity, results = (

    simulate_portfolio(

        stock_data,

        top_stocks
    )
)

print("\nPORTFOLIO RESULTS")

for k, v in results.items():

    print(f"{k}: {v}")

    # =====================================================
# EQUITY CURVE VISUALIZATION
# =====================================================

fig = go.Figure()

fig.add_trace(

    go.Scatter(

        x=benchmark_equity.index,

        y=benchmark_equity.values,

        mode="lines",

        name="NIFTY 50 Benchmark",

        line=dict(width=2)
    )
)

fig.update_layout(

    title="Institutional Portfolio Equity Curve",

    xaxis_title="Date",

    yaxis_title="Portfolio Value",

    template="plotly_dark",

    height=700
)

fig.show()