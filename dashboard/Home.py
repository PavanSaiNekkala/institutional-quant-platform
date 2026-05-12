import sys

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import streamlit as st
import pandas as pd

from core.dashboard_data_loader import (
    load_ranked_universe
)

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(

    page_title="Institutional Quant Platform",

    page_icon="🏦",

    layout="wide"
)

# =========================================================
# CACHE
# =========================================================

@st.cache_data(

    ttl=3600,

    show_spinner=False
)

def get_rankings():

    df = load_ranked_universe()

    if df.empty:

        return df

    # =====================================================
    # CLEAN NUMERIC COLUMNS
    # =====================================================

    numeric_cols = [

        "Institutional Score",
        "Market Cap",
        "Current Price",
        "Momentum",
        "Sharpe",
        "Volatility"
    ]

    for col in numeric_cols:

        if col in df.columns:

            df[col] = pd.to_numeric(

                df[col],

                errors="coerce"
            )

    # =====================================================
    # REMOVE BAD ROWS
    # =====================================================

    if "Institutional Score" in df.columns:

        df = df.dropna(

            subset=["Institutional Score"]
        )

    # =====================================================
    # SORT
    # =====================================================

    df = df.sort_values(

        by="Institutional Score",

        ascending=False
    )

    df = df.reset_index(

        drop=True
    )

    return df

# =========================================================
# TITLE
# =========================================================

st.title(

    "🏦 Institutional Quant Research Platform"
)

# =========================================================
# LOAD DATA
# =========================================================

ranking_df = get_rankings()

# =========================================================
# EMPTY CHECK
# =========================================================

if ranking_df.empty:

    st.warning(

        "No ranked universe available."
    )

    st.stop()

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header(

    "Institutional Controls"
)

top_n = st.sidebar.slider(

    "Top Ranked Stocks",

    min_value=10,

    max_value=100,

    value=50,

    step=10
)

# =========================================================
# DISPLAY DATA
# =========================================================

display_df = ranking_df.head(top_n)

# =========================================================
# METRICS
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(

        "Universe Loaded",

        f"{len(ranking_df):,}"
    )

with col2:

    top_score = 0

    if "Institutional Score" in ranking_df.columns:

        top_score = ranking_df[
            "Institutional Score"
        ].max()

    st.metric(

        "Top Institutional Score",

        round(float(top_score), 2)
    )

with col3:

    avg_score = 0

    if "Institutional Score" in ranking_df.columns:

        avg_score = ranking_df[
            "Institutional Score"
        ].mean()

    st.metric(

        "Average Score",

        round(float(avg_score), 2)
    )

# =========================================================
# TOP STOCKS
# =========================================================

st.subheader(

    f"Top {top_n} Ranked Institutional Stocks"
)

# =========================================================
# SELECT DISPLAY COLUMNS
# =========================================================

preferred_cols = [

    "Symbol",
    "Sector",
    "Current Price",
    "Market Cap",
    "Momentum",
    "Sharpe",
    "Volatility",
    "Institutional Score"
]

available_cols = [

    col for col in preferred_cols

    if col in display_df.columns
]

display_df = display_df[available_cols]

# =========================================================
# ROUND NUMBERS
# =========================================================

display_df = display_df.round(2)

# =========================================================
# DATAFRAME
# =========================================================

st.dataframe(

    display_df,

    use_container_width=True,

    height=700
)

# =========================================================
# SYSTEM STATUS
# =========================================================

st.success(

    "Lightweight Institutional Dashboard Active"
)
