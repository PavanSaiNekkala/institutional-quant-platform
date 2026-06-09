import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

from research.experiment_db import load_experiments

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(page_title="Institutional Research Dashboard", layout="wide")

# =========================================================
# TITLE
# =========================================================

st.title("Institutional Research Analytics")

# =========================================================
# LOAD EXPERIMENTS
# =========================================================

experiments = load_experiments()

# =========================================================
# METRICS
# =========================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric("Experiments", len(experiments))

col2.metric("Completed", len(experiments[experiments["status"] == "COMPLETED"]))

col3.metric("Average Metric", round(experiments["metric"].mean(), 2))

col4.metric("Best Metric", round(experiments["metric"].max(), 2))

# =========================================================
# EXPERIMENT TABLE
# =========================================================

st.subheader("Experiment Database")

st.dataframe(experiments, use_container_width=True)

# =========================================================
# METRIC VISUALIZATION
# =========================================================

st.subheader("Experiment Performance")

fig = go.Figure()

fig.add_trace(go.Bar(x=experiments["experiment_name"], y=experiments["metric"]))

st.plotly_chart(fig, use_container_width=True)

# =========================================================
# STATUS DISTRIBUTION
# =========================================================

st.subheader("Experiment Status")

status_counts = experiments["status"].value_counts()

status_fig = go.Figure()

status_fig.add_trace(go.Pie(labels=status_counts.index, values=status_counts.values))

st.plotly_chart(status_fig, use_container_width=True)

# =========================================================
# RESEARCH HEALTH
# =========================================================

st.success("Institutional Research Systems Operational")
