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

    layout="wide"
)

# =========================================================
# SIDEBAR WIDTH
# =========================================================

st.markdown(

    """
    <style>

    section[data-testid="stSidebar"] {

        width: 220px !important;
    }

    </style>
    """,

    unsafe_allow_html=True
)

# =========================================================
# CACHE
# =========================================================

@st.cache_data(ttl=3600)

def get_rankings():

    return load_ranked_universe()

# =========================================================
# TITLE
# =========================================================

st.title(

    "🏢 Institutional Quant Research Platform"
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

    "⚙ Controls"
)

top_n = st.sidebar.slider(

    "Top Ranked Stocks",

    min_value=10,

    max_value=100,

    value=50
)

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

    st.metric(

        "Top Institutional Score",

        round(

            ranking_df[
                "Institutional Score"
            ].max(),

            2
        )
    )

with col3:

    st.metric(

        "Average Score",

        round(

            ranking_df[
                "Institutional Score"
            ].mean(),

            2
        )
    )

# =========================================================
# TOP STOCKS
# =========================================================

st.subheader(

    "🚀 Top Institutional Stocks"
)

display_df = ranking_df.head(top_n)

st.dataframe(

    display_df,

    use_container_width=True
)

# =========================================================
# PENNY STOCKS SECTION
# =========================================================

st.subheader(

    "🪙 Penny Stocks"
)

# Penny stocks under ₹50

penny_df = ranking_df[

    ranking_df["Current Price"] < 50

].copy()

# Sort by institutional score

penny_df = penny_df.sort_values(

    by="Institutional Score",

    ascending=False
)

if penny_df.empty:

    st.info(

        "No penny stocks found."
    )

else:

    st.dataframe(

        penny_df.head(100),

        use_container_width=True
    )

# =========================================================
# FAILED STOCKS
# =========================================================

st.subheader(

    "❌ Failed Stocks"
)

try:

    failed_df = pd.read_excel(

        "failed_stocks.xlsx"
    )

    if failed_df.empty:

        st.success(

            "No failed stocks."
        )

    else:

        st.dataframe(

            failed_df,

            use_container_width=True
        )

except Exception:

    st.info(

        "No failed stock file available."
    )

# =========================================================
# SYSTEM STATUS
# =========================================================

st.success(

    "Institutional Dashboard Running Successfully"
)
