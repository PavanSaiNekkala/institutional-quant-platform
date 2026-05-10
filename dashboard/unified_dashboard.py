import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px

from core.universe_loader import (
    load_ranked_universe
)

from risk.regime_detection import (
    RegimeDetector
)

from strategy.dynamic_strategy_switcher import (
    DynamicStrategySwitcher
)

from portfolio.adaptive_allocation import (
    AdaptiveAllocation
)

from backtesting.institutional_backtester import (
    InstitutionalBacktester
)

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(

    page_title="Institutional Quant Command Center",

    layout="wide"
)

# =========================================================
# TITLE
# =========================================================

st.title(

    "Institutional Quant Command Center"
)

# =========================================================
# LOAD UNIVERSE
# =========================================================

symbols = load_ranked_universe(

    top_n=25
)

if len(symbols) == 0:

    st.error(

        "No symbols found in ranked_universe.xlsx"
    )

    st.stop()

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header(

    "Controls"
)

selected_symbol = st.sidebar.selectbox(

    "Select Symbol",

    symbols
)

# =========================================================
# SELECTED SYMBOL DISPLAY
# =========================================================

st.subheader(

    f"Selected Asset: {selected_symbol}"
)

# =========================================================
# REGIME DETECTION
# =========================================================

st.header(

    "Market Regime Intelligence"
)

regime_engine = RegimeDetector()

regime = regime_engine.detect(

    symbol=selected_symbol
)

if regime:

    regime_df = pd.DataFrame(

        regime.items(),

        columns=[

            "Metric",

            "Value"
        ]
    )

    st.dataframe(

        regime_df,

        use_container_width=True
    )

# =========================================================
# STRATEGY SWITCHING
# =========================================================

st.header(

    "Dynamic Strategy Switching"
)

strategy_engine = DynamicStrategySwitcher()

strategy = strategy_engine.select_strategy(

    symbol=selected_symbol
)

if strategy:

    strategy_df = pd.DataFrame(

        strategy.items(),

        columns=[

            "Metric",

            "Value"
        ]
    )

    st.dataframe(

        strategy_df,

        use_container_width=True
    )

# =========================================================
# ADAPTIVE ALLOCATION
# =========================================================

st.header(

    "Adaptive Allocation"
)

allocation_engine = AdaptiveAllocation()

allocation_symbols = symbols[:5]

returns_list = []

volatility_list = []

valid_symbols = []

# =========================================================
# FETCH MARKET DATA
# =========================================================

for sym in allocation_symbols:

    try:

        data = yf.download(

            sym,

            period="6mo",

            progress=False,

            auto_adjust=True
        )

        if data.empty:

            continue

        close = data["Close"]

        if isinstance(close, pd.DataFrame):

            close = close.iloc[:, 0]

        close = close.dropna()

        if len(close) < 30:

            continue

        returns = close.pct_change().dropna()

        expected_return = (

            returns.mean()

            * 252
        )

        volatility = (

            returns.std()

            * np.sqrt(252)
        )

        returns_list.append(

            float(expected_return)
        )

        volatility_list.append(

            float(volatility)
        )

        valid_symbols.append(sym)

    except Exception as e:

        st.warning(

            f"Allocation Error {sym}: {e}"
        )

# =========================================================
# ALLOCATION ENGINE
# =========================================================

if len(valid_symbols) > 1:

    allocation_df, allocation_summary = (

        allocation_engine.allocate(

            valid_symbols,

            returns_list,

            volatility_list
        )
    )

    st.dataframe(

        allocation_df,

        use_container_width=True
    )

    # =====================================================
    # ALLOCATION CHART
    # =====================================================

    fig = px.pie(

        allocation_df,

        names="Symbol",

        values="Adaptive Weight",

        title="Adaptive Portfolio Weights"
    )

    st.plotly_chart(

        fig,

        use_container_width=True
    )

    # =====================================================
    # SUMMARY
    # =====================================================

    summary_df = pd.DataFrame(

        allocation_summary.items(),

        columns=[

            "Metric",

            "Value"
        ]
    )

    st.dataframe(

        summary_df,

        use_container_width=True
    )

else:

    st.warning(

        "Not enough valid symbols for allocation analysis."
    )

# =========================================================
# BACKTESTING
# =========================================================

st.header(

    "Institutional Backtesting"
)

backtester = InstitutionalBacktester(

    initial_capital=100000
)

backtest = backtester.run_backtest(

    [selected_symbol],

    period="1y"
)

if backtest:

    metrics_df = pd.DataFrame(

        backtest["metrics"].items(),

        columns=[

            "Metric",

            "Value"
        ]
    )

    st.dataframe(

        metrics_df,

        use_container_width=True
    )

    # =====================================================
    # EQUITY CURVE
    # =====================================================

    equity_curve = backtest[

        "equity_curve"
    ]

    fig2 = px.line(

        equity_curve,

        title=f"{selected_symbol} Equity Curve"
    )

    st.plotly_chart(

        fig2,

        use_container_width=True
    )

else:

    st.warning(

        "Backtest failed for selected asset."
    )

# =========================================================
# SYSTEM STATUS
# =========================================================

st.success(

    "Institutional Quant Platform Operational"
)