import sys
from pathlib import Path

import streamlit as st

from core.dashboard_data_loader import load_pnl_analytics

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

sys.path.append(str(ROOT_DIR))

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(page_title="PnL Analytics", layout="wide")

# =========================================================
# CACHE
# =========================================================


@st.cache_data(ttl=3600)
def get_pnl_data():

    return load_pnl_analytics()


# =========================================================
# TITLE
# =========================================================

st.title("Institutional PnL Analytics")

# =========================================================
# LOAD
# =========================================================

pnl_df = get_pnl_data()

if pnl_df.empty:
    st.warning("No PnL analytics available.")

    st.stop()

# =========================================================
# DISPLAY
# =========================================================

st.dataframe(pnl_df, use_container_width=True)
