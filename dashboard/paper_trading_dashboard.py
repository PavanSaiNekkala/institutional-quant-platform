import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from paper_trading.paper_trading_engine import PaperTradingEngine

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(page_title="Paper Trading Dashboard", layout="wide")

# =========================================================
# TITLE
# =========================================================

st.title("Institutional Paper Trading Dashboard")

# =========================================================
# ENGINE
# =========================================================

engine = PaperTradingEngine()

report = engine.report()

# =========================================================
# CASH
# =========================================================

st.header("Portfolio Overview")

col1, col2 = st.columns(2)

with col1:
    st.metric("Cash Balance", f"${report['Cash']:,.2f}")

with col2:
    st.metric("Portfolio Value", f"${report['Portfolio Value']:,.2f}")

# =========================================================
# POSITIONS
# =========================================================

st.header("Active Positions")

positions = report["Positions"]

if positions:
    positions_df = pd.DataFrame(
        {"Symbol": list(positions.keys()), "Quantity": list(positions.values())}
    )

    st.dataframe(positions_df, use_container_width=True)

    # =====================================================
    # POSITION CHART
    # =====================================================

    fig = px.pie(positions_df, names="Symbol", values="Quantity", title="Portfolio Allocation")

    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("No active positions.")

# =========================================================
# TRADE HISTORY
# =========================================================

st.header("Trade History")

trades = report["Trades"]

if trades:
    trades_df = pd.DataFrame(trades)

    st.dataframe(trades_df, use_container_width=True)

    # =====================================================
    # TRADE COUNTS
    # =====================================================

    if "Action" in trades_df.columns:
        trade_counts = trades_df["Action"].value_counts().reset_index()

        trade_counts.columns = ["Action", "Count"]

        fig2 = px.bar(trade_counts, x="Action", y="Count", title="Trade Activity")

        st.plotly_chart(fig2, use_container_width=True)

else:
    st.warning("No trades executed.")

# =========================================================
# SYSTEM STATUS
# =========================================================

st.success("Paper Trading System Operational")
