import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

sys.path.append(str(ROOT_DIR))

import streamlit as st
import pandas as pd

from paper_trading.paper_trading_engine import (
    PaperTradingEngine
)

# =========================================================
# TITLE
# =========================================================

st.title(

    "Portfolio Monitor"
)

engine = PaperTradingEngine()

report = engine.report()

# =========================================================
# METRICS
# =========================================================

col1, col2 = st.columns(2)

with col1:

    st.metric(

        "Cash",

        f"${report['Cash']:,.2f}"
    )

with col2:

    st.metric(

        "Portfolio Value",

        f"${report['Portfolio Value']:,.2f}"
    )

# =========================================================
# POSITIONS
# =========================================================

positions = report["Positions"]

if positions:

    df = pd.DataFrame({

        "Symbol":

            list(positions.keys()),

        "Quantity":

            list(positions.values())
    })

    st.dataframe(

        df,

        use_container_width=True
    )