import streamlit as st

# ============import sys

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import streamlit as st

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

    "Institutional Quant Operating Platform"
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
# METRICS
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(

        "Universe Size",

        len(ranking_df)
    )

with col2:

    st.metric(

        "Top Score",

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

    "Top Ranked Stocks"
)

st.dataframe(

    ranking_df.head(50),

    use_container_width=True
)=============================================
# PAGE CONFIG
# =========================================================

st.set_page_config(

    page_title="Institutional Quant Platform",

    layout="wide"
)

# =========================================================
# TITLE
# =========================================================

st.title(

    "Institutional Quant Operating Platform"
)

st.success(

    "Platform Operational"
)

# =========================================================
# OVERVIEW
# =========================================================

st.header(

    "Platform Overview"
)

st.markdown(

    """
    This platform includes:

    - Portfolio Analytics
    - Paper Trading
    - Adaptive Allocation
    - Regime Detection
    - Backtesting
    - Risk Analytics
    - Reporting Infrastructure
    - Automated Refresh Systems
    - Institutional Monitoring
    """
)

# =========================================================
# STATUS
# =========================================================

st.header(

    "System Status"
)

st.info(

    "All core institutional systems online."
)
