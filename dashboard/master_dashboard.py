import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from signals.live_signals import (
    generate_live_signal
)

from portfolio.live_monitor import (
    live_portfolio_report
)

from monitoring.alerts import (
    AlertManager
)

# =========================================================
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

    "Institutional Quantitative Intelligence Platform"
)

# =========================================================
# SYMBOLS
# =========================================================

symbols = [

    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS"
]

weights = np.array([

    0.30,
    0.25,
    0.25,
    0.20
])

# =========================================================
# LIVE SIGNALS
# =========================================================

st.subheader(

    "Live AI Signals"
)

signal_reports = []

for symbol in symbols:

    try:

        report = generate_live_signal(

            symbol
        )

        signal_reports.append(

            report
        )

    except Exception as e:

        st.warning(

            f"Signal error for {symbol}: {e}"
        )

signal_df = pd.DataFrame(

    signal_reports
)

st.dataframe(

    signal_df,

    use_container_width=True
)

# =========================================================
# SIGNAL VISUALIZATION
# =========================================================

fig = go.Figure()

fig.add_trace(

    go.Bar(

        x=signal_df["Symbol"],

        y=signal_df["Signal Score"]
    )
)

st.plotly_chart(

    fig,

    use_container_width=True
)

# =========================================================
# PORTFOLIO MONITOR
# =========================================================

st.subheader(

    "Live Portfolio Analytics"
)

portfolio = live_portfolio_report(

    symbols,

    weights
)

portfolio_df = pd.DataFrame({

    "Metric":

        portfolio.keys(),

    "Value":

        portfolio.values()
})

st.dataframe(

    portfolio_df,

    use_container_width=True
)

# =========================================================
# ALERTS
# =========================================================

st.subheader(

    "Institutional Alerts"
)

alerts = AlertManager()

alerts.risk_alert(

    drawdown=-0.12
)

alerts.volatility_alert(

    volatility=0.35
)

alerts.signal_alert(

    symbol="RELIANCE.NS",

    decision="BUY"
)

alert_df = pd.DataFrame(

    alerts.get_alerts()
)

st.dataframe(

    alert_df,

    use_container_width=True
)

# =========================================================
# SYSTEM HEALTH
# =========================================================

st.success(

    "Institutional Quant Platform Operational"
)