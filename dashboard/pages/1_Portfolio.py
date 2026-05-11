import sys

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

sys.path.append(str(ROOT_DIR))

import streamlit as st
import pandas as pd

from core.dashboard_data_loader import (
    load_portfolio_analytics
)

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(

    page_title="Portfolio Dashboard",

    layout="wide"
)

# =========================================================
# CACHED LOADER
# =========================================================

@st.cache_data(ttl=3600)

def get_portfolio_data():

    return load_portfolio_analytics()

# =========================================================
# TITLE
# =========================================================

st.title(

    "Institutional Portfolio Dashboard"
)

# =========================================================
# LOAD DATA
# =========================================================

portfolio_df = get_portfolio_data()

# =========================================================
# EMPTY CHECK
# =========================================================

if portfolio_df.empty:

    st.warning(

        "No portfolio analytics available."
    )

    st.stop()

# =========================================================
# DASHBOARD
# =========================================================

st.dataframe(

    portfolio_df,

    use_container_width=True
)

# =========================================================
# METRICS
# =========================================================

if "Portfolio Value" in portfolio_df.columns:

    latest_value = (

        portfolio_df[

            "Portfolio Value"
        ]

        .iloc[-1]
    )

    st.metric(

        "Portfolio Value",

        f"{latest_value:,.2f}"
    )
