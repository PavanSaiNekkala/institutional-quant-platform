import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ai.orchestrator import orchestrate_ai

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(page_title="Institutional AI Dashboard", layout="wide")

# =========================================================
# TITLE
# =========================================================

st.title("Institutional AI Monitoring Dashboard")

# =========================================================
# SAMPLE DATA
# =========================================================

np.random.seed(42)

prices = pd.Series(100 + np.cumsum(np.random.normal(0, 1, 500)))

# =========================================================
# RUN AI
# =========================================================

result = orchestrate_ai(prices)

# =========================================================
# METRICS
# =========================================================

col1, col2, col3 = st.columns(3)

col1.metric("Final Signal", result["Final Signal"])

col2.metric("Decision", result["Decision"])

col3.metric("Ensemble Signal", result["Ensemble Signal"])

# =========================================================
# SIGNAL TABLE
# =========================================================

st.subheader("AI Signal Breakdown")

signal_df = pd.DataFrame({"Metric": list(result.keys()), "Value": list(result.values())})

st.dataframe(signal_df, use_container_width=True)

# =========================================================
# PRICE CHART
# =========================================================

st.subheader("Price Series")

fig = go.Figure()

fig.add_trace(go.Scatter(y=prices, mode="lines", name="Price"))

st.plotly_chart(fig, use_container_width=True)

# =========================================================
# SIGNAL VISUALIZATION
# =========================================================

st.subheader("AI Signal Strength")

signals = {k: v for k, v in result.items() if "Signal" in k}

signal_fig = go.Figure()

signal_fig.add_trace(go.Bar(x=list(signals.keys()), y=list(signals.values())))

st.plotly_chart(signal_fig, use_container_width=True)

# =========================================================
# FOOTER
# =========================================================

st.success("Institutional AI orchestration active")
