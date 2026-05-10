import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from core.orchestrator import (
    orchestrate_portfolio
)

from core.regime import (
    regime_allocation
)

# =========================================================
# STREAMLIT CONFIG
# =========================================================

st.set_page_config(

    page_title="Institutional Quant Platform",

    layout="wide"
)

# =========================================================
# TITLE
# =========================================================

st.title(

    "🏦 Institutional Quant Research Platform"
)

st.markdown("---")

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header(

    "Institutional Controls"
)

regime = st.sidebar.selectbox(

    "Market Regime",

    [

        "BULL_LOW_VOL",
        "BULL_NORMAL_VOL",
        "BULL_HIGH_VOL",
        "BEAR_LOW_VOL",
        "BEAR_NORMAL_VOL",
        "BEAR_HIGH_VOL"
    ]
)

top_n = st.sidebar.slider(

    "Top Stocks",

    5,

    50,

    10
)
# =========================================================
# LOAD DYNAMIC UNIVERSE
# =========================================================

universe_path = (
    ROOT_DIR
    / "data"
    / "valid_stocks.xlsx"
)

try:

    universe_df = pd.read_excel(
        universe_path
    )

    stocks = (

        universe_df.iloc[:, 0]

        .dropna()

        .astype(str)

        .unique()

        .tolist()
    )

    # =====================================================
    # NSE FILTER
    # =====================================================

    stocks = [

        stock for stock in stocks

        if ".NS" in stock
    ]

except Exception as e:

    st.error(
        f"Universe load failed: {e}"
    )

    st.stop()
# =========================================================
# RUN ORCHESTRATOR
# =========================================================

results = orchestrate_portfolio(

    stocks,

    regime=regime
)

results = results.head(top_n)

# =========================================================
# REGIME EXPOSURE
# =========================================================

recommended_exposure = regime_allocation(

    regime
)

# =========================================================
# DASHBOARD METRICS
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(

        "Selected Regime",

        regime
    )

with col2:

    st.metric(

        "Recommended Exposure",

        round(

            recommended_exposure,

            2
        )
    )

with col3:

    st.metric(

        "Stocks Ranked",

        len(results)
    )

# =========================================================
# RANKINGS TABLE
# =========================================================

st.subheader(

    "Institutional Alpha Rankings"
)

st.dataframe(

    results,

    use_container_width=True
)

# =========================================================
# SCORE VISUALIZATION
# =========================================================

fig = px.bar(

    results.reset_index(),

    x="index",

    y="Final Score",

    color="Classification",

    title="Institutional Alpha Scores"
)

st.plotly_chart(

    fig,

    use_container_width=True
)

# =========================================================
# FACTOR SCORE BREAKDOWN
# =========================================================

factor_fig = px.scatter(

    results.reset_index(),

    x="Alpha Score",

    y="Ensemble Score",

    size="Adaptive Score",

    color="Classification",

    hover_name="index",

    title="Institutional Factor Intelligence"
)

st.plotly_chart(

    factor_fig,

    use_container_width=True
)

# =========================================================
# PERCENTILE DISTRIBUTION
# =========================================================

hist_fig = px.histogram(

    results,

    x="Percentile",

    nbins=10,

    title="Alpha Percentile Distribution"
)

st.plotly_chart(

    hist_fig,

    use_container_width=True
)

# =========================================================
# TOP PICKS
# =========================================================

st.subheader(

    "Institutional Long Candidates"
)

top_picks = results[

    results["Classification"]

    == "INSTITUTIONAL_LONG"
]

st.dataframe(

    top_picks,

    use_container_width=True
)

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(

    "Institutional Quantamental Intelligence Platform"
)
