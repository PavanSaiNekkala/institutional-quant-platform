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
# CACHE
# =========================================================

@st.cache_data(ttl=3600)

def get_rankings():

    return load_ranked_universe()

# =========================================================
# TITLE
# =========================================================

st.title(

    "Institutional Quant Research Platform"
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

    "Top Stocks",

    min_value=10,

    max_value=min(

        500,

        len(ranking_df)
    ),

    value=50
)

# =========================================================
# METRICS
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(

        "Universe Loaded",

        len(ranking_df)
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

    "Top Ranked Institutional Stocks"
)

display_df = ranking_df.head(top_n)

st.dataframe(

    display_df,

    use_container_width=True
)

# =========================================================
# SYSTEM STATUS
# =========================================================

st.success(

    "Lightweight Institutional Dashboard Active"
)
